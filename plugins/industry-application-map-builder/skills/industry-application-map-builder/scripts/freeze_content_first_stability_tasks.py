#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any


SHA256 = re.compile(r"^[0-9a-f]{64}$")
CANDIDATE_ARM = "screen_then_expand_v2"


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}), file=sys.stderr)
    return 2


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def aware_time(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def inside(workspace: Path, path: Path) -> Path | None:
    try:
        resolved = path.resolve()
        resolved.relative_to(workspace.resolve())
    except (OSError, ValueError):
        return None
    current = workspace.resolve()
    relative = resolved.relative_to(current)
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return None
    return resolved


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze six predeclared R4 stability repeat tasks before any repeat execution."
    )
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--expected-final-contract-sha256", required=True)
    parser.add_argument("--formal-case-set", required=True, type=Path)
    parser.add_argument("--expected-formal-case-set-sha256", required=True)
    parser.add_argument("--paired-task-manifest", required=True, type=Path)
    parser.add_argument("--expected-paired-task-manifest-sha256", required=True)
    parser.add_argument("--authorization-id-prefix", required=True)
    parser.add_argument("--authorized-at", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--test-fail-after-file-count", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        return fail("WORKSPACE_INVALID", str(workspace))
    output = inside(workspace, args.output)
    if output is None:
        try:
            args.output.resolve().parent.relative_to(workspace)
            output = args.output.resolve()
        except (OSError, ValueError):
            return fail("OUTPUT_OUTSIDE_WORKSPACE", str(args.output))
    if output.exists():
        return fail("OUTPUT_EXISTS", str(output))
    if not args.authorization_id_prefix or not aware_time(args.authorized_at):
        return fail("FREEZE_AUTHORIZATION_INVALID", args.authorization_id_prefix)
    inputs = (args.contract, args.formal_case_set, args.paired_task_manifest)
    resolved_inputs = [inside(workspace, path) for path in inputs]
    if any(path is None or not path.is_file() for path in resolved_inputs):
        return fail("FREEZE_INPUT_INVALID", "all inputs must be regular workspace files")
    contract_path, case_path, manifest_path = resolved_inputs
    expected_hashes = (
        args.expected_final_contract_sha256,
        args.expected_formal_case_set_sha256,
        args.expected_paired_task_manifest_sha256,
    )
    if any(not SHA256.fullmatch(value) for value in expected_hashes) or any(
        file_sha256(path) != expected
        for path, expected in zip(resolved_inputs, expected_hashes)
    ):
        return fail("FREEZE_INPUT_HASH_MISMATCH", "contract, cases, or task manifest")
    try:
        contract = load_json(contract_path)["semantic_research_contract"]
        case_rows = [
            json.loads(line)
            for line in case_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        manifest = load_json(manifest_path)["content_first_paired_task_manifest"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return fail("FREEZE_INPUT_INVALID", str(exc))
    case_header = case_rows[0] if case_rows else None
    repeat_ids = case_header.get("stability_repeat_case_ids") if isinstance(case_header, dict) else None
    formal_ids = case_header.get("formal_case_ids") if isinstance(case_header, dict) else None
    pairs = manifest.get("pairs") if isinstance(manifest, dict) else None
    if (
        contract.get("contract_state") != "frozen"
        or contract.get("candidate_method_contract") != CANDIDATE_ARM
        or contract.get("retrieval_efficiency_gates", {}).get("stability_repeat_case_count") != 6
        or contract.get("calibration_case_set_reference_and_hash", {}).get("sha256")
        != args.expected_formal_case_set_sha256
        or not isinstance(formal_ids, list)
        or len(formal_ids) != 40
        or not isinstance(repeat_ids, list)
        or len(repeat_ids) != 6
        or len(set(repeat_ids)) != 6
        or not all(isinstance(case_id, str) and case_id in formal_ids for case_id in repeat_ids)
        or not isinstance(pairs, list)
        or len(pairs) != 40
        or manifest.get("final_contract_sha256") != args.expected_final_contract_sha256
    ):
        return fail("STABILITY_FREEZE_CONTRACT_INVALID", "frozen selection or manifest binding")
    pair_by_case = {
        pair.get("case_id"): pair
        for pair in pairs
        if isinstance(pair, dict) and isinstance(pair.get("case_id"), str)
    }
    staging = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output.parent)
    )
    written = 0
    entries: list[dict[str, Any]] = []
    try:
        for index, case_id in enumerate(repeat_ids, 1):
            pair = pair_by_case.get(case_id)
            entry = pair.get("task_files", {}).get(CANDIDATE_ARM) if isinstance(pair, dict) else None
            if not isinstance(entry, dict) or set(entry) != {"path", "task_file_sha256"}:
                raise ValueError(f"candidate task missing for {case_id}")
            candidate_task = inside(workspace, manifest_path.parent / entry["path"])
            if (
                candidate_task is None
                or not candidate_task.is_file()
                or file_sha256(candidate_task) != entry["task_file_sha256"]
                or not SHA256.fullmatch(entry["task_file_sha256"])
            ):
                raise ValueError(f"candidate task hash mismatch for {case_id}")
            visible_hash = pair.get("visible_input_sha256")
            if not SHA256.fullmatch(str(visible_hash)):
                raise ValueError(f"visible input hash missing for {case_id}")
            repeat_id = f"R4-STABILITY-{index:02d}-{case_id}"
            fresh_context_id = f"R4-FRESH-{index:02d}-{case_id}"
            candidate_reference = candidate_task.relative_to(workspace).as_posix()
            preauth_reference = f"preauthorizations/{case_id}.preauthorization.json"
            preauth = {
                "schema_version": "1.0",
                "receiver_resource_observation_preauthorization": {
                    "authorization_id": f"{args.authorization_id_prefix}-{index:02d}",
                    "permitted_action": "capture_content_resource_observation_only",
                    "research_contract_id": contract["research_contract_id"],
                    "contract_version": contract["contract_version"],
                    "case_id": case_id,
                    "method_arm": CANDIDATE_ARM,
                    "original_candidate_task_reference": candidate_reference,
                    "task_sha256": entry["task_file_sha256"],
                    "fresh_context_id": fresh_context_id,
                    "authorized_at": args.authorized_at,
                    "model_execution_authorized": False,
                    "downstream_authorized": False,
                },
            }
            preauth_path = staging / preauth_reference
            preauth_path.parent.mkdir(parents=True, exist_ok=True)
            preauth_path.write_bytes(canonical_bytes(preauth))
            written += 1
            if args.test_fail_after_file_count is not None and written >= args.test_fail_after_file_count:
                raise OSError("deterministic requested stability freeze failure")
            task_reference = f"tasks/{case_id}.repeat-task.json"
            task = {
                "schema_version": "1.0",
                "content_first_stability_repeat_task": {
                    "repeat_id": repeat_id,
                    "research_contract_id": contract["research_contract_id"],
                    "contract_version": contract["contract_version"],
                    "case_id": case_id,
                    "method_arm": CANDIDATE_ARM,
                    "visible_input_sha256": visible_hash,
                    "original_candidate_task_reference": candidate_reference,
                    "original_candidate_task_sha256": entry["task_file_sha256"],
                    "preauthorization_reference": preauth_reference,
                    "preauthorization_sha256": file_sha256(preauth_path),
                    "fresh_context_id": fresh_context_id,
                    "counts_toward_formal_case_score": False,
                    "execution_authorized": False,
                },
            }
            task_path = staging / task_reference
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_bytes(canonical_bytes(task))
            written += 1
            if args.test_fail_after_file_count is not None and written >= args.test_fail_after_file_count:
                raise OSError("deterministic requested stability freeze failure")
            entries.append(
                {
                    "repeat_id": repeat_id,
                    "case_id": case_id,
                    "visible_input_sha256": visible_hash,
                    "preauthorization_reference": preauth_reference,
                    "preauthorization_sha256": file_sha256(preauth_path),
                    "repeat_task_reference": task_reference,
                    "repeat_task_sha256": file_sha256(task_path),
                }
            )
        manifest_out = {
            "schema_version": "1.0",
            "content_first_stability_task_manifest": {
                "research_contract_id": contract["research_contract_id"],
                "contract_version": contract["contract_version"],
                "final_contract_sha256": args.expected_final_contract_sha256,
                "formal_case_set_sha256": args.expected_formal_case_set_sha256,
                "paired_task_manifest_sha256": args.expected_paired_task_manifest_sha256,
                "method_arm": CANDIDATE_ARM,
                "repeat_case_count": 6,
                "repeat_case_ids": repeat_ids,
                "created_before_repeat_execution": True,
                "model_execution_authorized": False,
                "downstream_authorized": False,
                "entries": entries,
            },
        }
        (staging / "stability-task-manifest.json").write_bytes(canonical_bytes(manifest_out))
        if output.exists():
            raise FileExistsError(str(output))
        staging.replace(output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return fail("STABILITY_FREEZE_FAILED", str(exc))
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": str(output),
                "repeat_case_count": 6,
                "manifest_file_sha256": file_sha256(output / "stability-task-manifest.json"),
                "model_execution_authorized": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
