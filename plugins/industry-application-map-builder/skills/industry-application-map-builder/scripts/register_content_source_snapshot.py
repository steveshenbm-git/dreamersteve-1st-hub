#!/usr/bin/env python3
"""Register receiver-owned source bytes without trusting model hash claims."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

from content_source_observation_schema import valid_model_observation


OBSERVATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
OBSERVATION_POINTER = re.compile(
    r"^/semantic_content_raw_answer/source_observations/(0|[1-9][0-9]*)$"
)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def fail(code: str, detail: str) -> int:
    print(
        json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False),
        file=sys.stderr,
    )
    return 2


def timezone_aware_iso8601(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def workspace_file_identity_collision(workspace: Path, source: Path) -> bool:
    source_stat = source.stat()
    for candidate in workspace.rglob("*"):
        if candidate.is_symlink():
            continue
        try:
            if candidate.is_file():
                candidate_stat = candidate.stat()
                if (candidate_stat.st_dev, candidate_stat.st_ino) == (
                    source_stat.st_dev,
                    source_stat.st_ino,
                ):
                    return True
        except OSError as exc:
            raise RuntimeError(str(exc)) from exc
    return False


def inside(workspace: Path, path: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(workspace)
    except (OSError, ValueError):
        return False
    return True


def has_symlink_component(workspace: Path, path: Path) -> bool:
    try:
        relative = path.absolute().relative_to(workspace.absolute())
    except ValueError:
        return True
    current = workspace
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def stage_bytes(parent: Path, payload: bytes) -> Path:
    handle = tempfile.NamedTemporaryFile(prefix=".source-snapshot-", dir=parent, delete=False)
    try:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    finally:
        handle.close()
    return Path(handle.name)


def publish_without_overwrite(staged: Path, destination: Path) -> None:
    os.link(staged, destination)
    staged.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy one receiver-captured public source and issue an immutable receipt."
    )
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--source-file", required=True, type=Path)
    parser.add_argument("--observation-id", required=True)
    parser.add_argument("--source-observation-reference", required=True)
    parser.add_argument("--captured-at", required=True)
    parser.add_argument("--test-fail-after-snapshot-publish", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        return fail("WORKSPACE_MISSING", str(workspace))
    if (
        not OBSERVATION_ID.fullmatch(args.observation_id)
        or args.observation_id in {".", ".."}
    ):
        return fail("OBSERVATION_ID_INVALID", args.observation_id)
    if not isinstance(args.source_observation_reference, str) or not args.source_observation_reference.strip():
        return fail("SOURCE_OBSERVATION_REFERENCE_INVALID", str(args.source_observation_reference))
    if not timezone_aware_iso8601(args.captured_at):
        return fail("SNAPSHOT_CAPTURED_AT_INVALID", args.captured_at)

    try:
        source = args.source_file.resolve(strict=True)
    except OSError as exc:
        return fail("SOURCE_FILE_MISSING", str(exc))
    if not source.is_file():
        return fail("SOURCE_FILE_INVALID", str(source))
    if inside(workspace, source):
        return fail("SOURCE_FILE_NOT_EXTERNAL", str(source))
    try:
        if workspace_file_identity_collision(workspace, source):
            return fail("SOURCE_FILE_NOT_EXTERNAL", str(source))
    except (OSError, RuntimeError) as exc:
        return fail("SOURCE_IDENTITY_SCAN_FAILED", str(exc))

    observation_path_text, separator, observation_fragment = args.source_observation_reference.partition("#")
    observation_relative = Path(observation_path_text)
    pointer_match = OBSERVATION_POINTER.fullmatch(observation_fragment)
    if (
        not separator
        or pointer_match is None
        or observation_relative.is_absolute()
        or observation_relative.as_posix() != observation_path_text
        or any(part in {".", ".."} for part in observation_relative.parts)
    ):
        return fail("SOURCE_OBSERVATION_REFERENCE_INVALID", args.source_observation_reference)
    observation_path = (workspace / observation_relative).resolve(strict=False)
    if not inside(workspace, observation_path) or not observation_path.is_file():
        return fail("SOURCE_OBSERVATION_REFERENCE_INVALID", args.source_observation_reference)
    try:
        observation_payload = json.loads(observation_path.read_text(encoding="utf-8"))
        observation_body = observation_payload.get("semantic_content_raw_answer")
        observations = observation_body.get("source_observations")
        observation_index = int(pointer_match.group(1))
        target_observation = observations[observation_index]
    except (OSError, ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError):
        return fail("SOURCE_OBSERVATION_REFERENCE_INVALID", args.source_observation_reference)
    if not valid_model_observation(target_observation):
        return fail("SOURCE_OBSERVATION_INVALID", args.source_observation_reference)
    try:
        if source.samefile(observation_path):
            return fail("SOURCE_SNAPSHOT_IDENTITY_COLLISION", str(source))
    except OSError as exc:
        return fail("SOURCE_OBSERVATION_REFERENCE_INVALID", str(exc))

    snapshot_relative = Path("05-证据包") / "receiver-source-snapshots" / f"{args.observation_id}.snapshot"
    receipt_relative = Path("05-证据包") / "source-snapshot-receipts" / f"{args.observation_id}.receipt.json"
    snapshot = workspace / snapshot_relative
    receipt_path = workspace / receipt_relative
    if not inside(workspace, snapshot):
        return fail("SNAPSHOT_DESTINATION_OUTSIDE_WORKSPACE", str(snapshot))
    if not inside(workspace, receipt_path):
        return fail("RECEIPT_DESTINATION_OUTSIDE_WORKSPACE", str(receipt_path))
    if has_symlink_component(workspace, snapshot):
        return fail("SNAPSHOT_DESTINATION_SYMLINK_FORBIDDEN", str(snapshot))
    if has_symlink_component(workspace, receipt_path):
        return fail("RECEIPT_DESTINATION_SYMLINK_FORBIDDEN", str(receipt_path))
    if snapshot.exists() or snapshot.is_symlink():
        return fail("SNAPSHOT_EXISTS", str(snapshot))
    if receipt_path.exists() or receipt_path.is_symlink():
        return fail("RECEIPT_EXISTS", str(receipt_path))

    try:
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return fail("SNAPSHOT_DESTINATION_INVALID", str(exc))
    if not inside(workspace, snapshot):
        return fail("SNAPSHOT_DESTINATION_OUTSIDE_WORKSPACE", str(snapshot))
    if not inside(workspace, receipt_path):
        return fail("RECEIPT_DESTINATION_OUTSIDE_WORKSPACE", str(receipt_path))
    if has_symlink_component(workspace, snapshot):
        return fail("SNAPSHOT_DESTINATION_SYMLINK_FORBIDDEN", str(snapshot))
    if has_symlink_component(workspace, receipt_path):
        return fail("RECEIPT_DESTINATION_SYMLINK_FORBIDDEN", str(receipt_path))

    snapshot_resolved = snapshot.resolve(strict=False)
    receipt_resolved = receipt_path.resolve(strict=False)
    if len({source, observation_path, snapshot_resolved, receipt_resolved}) != 4:
        return fail("SOURCE_SNAPSHOT_PATH_COLLISION", str(source))

    try:
        source_bytes = source.read_bytes()
    except OSError as exc:
        return fail("SOURCE_READ_FAILED", str(exc))
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    receipt_body = {
        "receipt_id": f"SNAPSHOT-{args.observation_id}",
        "observation_id": args.observation_id,
        "source_observation_reference": args.source_observation_reference,
        "receiver_snapshot_reference": snapshot_relative.as_posix(),
        "receiver_snapshot_sha256": source_sha256,
        "snapshot_capture_state": "captured",
        "snapshot_captured_at": args.captured_at,
        "receipt_sha256": None,
    }
    receipt_body["receipt_sha256"] = canonical_sha256(receipt_body)
    receipt_payload = {
        "schema_version": "1.0",
        "content_source_snapshot_receipt": receipt_body,
    }
    receipt_bytes = (
        json.dumps(receipt_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")

    staged_snapshot: Path | None = None
    staged_receipt: Path | None = None
    created: list[Path] = []
    try:
        staged_snapshot = stage_bytes(snapshot.parent, source_bytes)
        staged_receipt = stage_bytes(receipt_path.parent, receipt_bytes)
        publish_without_overwrite(staged_snapshot, snapshot)
        staged_snapshot = None
        created.append(snapshot)
        if args.test_fail_after_snapshot_publish:
            raise OSError("deterministic requested receipt publication failure")
        publish_without_overwrite(staged_receipt, receipt_path)
        staged_receipt = None
        created.append(receipt_path)
    except FileExistsError as exc:
        for created_path in reversed(created):
            try:
                created_path.unlink()
            except OSError:
                pass
        code = "SNAPSHOT_EXISTS" if snapshot.exists() else "RECEIPT_EXISTS"
        return fail(code, str(exc))
    except OSError as exc:
        for created_path in reversed(created):
            try:
                created_path.unlink()
            except OSError:
                pass
        return fail("SNAPSHOT_WRITE_FAILED", str(exc))
    finally:
        for staged in (staged_snapshot, staged_receipt):
            if staged is not None:
                try:
                    staged.unlink()
                except OSError:
                    pass

    print(
        json.dumps(
            {
                "status": "PASS",
                "observation_id": args.observation_id,
                "source_observation_reference": args.source_observation_reference,
                "receiver_snapshot_reference": snapshot_relative.as_posix(),
                "receiver_snapshot_sha256": source_sha256,
                "receipt_reference": receipt_relative.as_posix(),
                "receipt_sha256": receipt_body["receipt_sha256"],
                "snapshot_capture_state": "captured",
                "snapshot_captured_at": args.captured_at,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
