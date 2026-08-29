#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import unicodedata

from r4_case_package_contract import (
    CASE_PACKAGE_CONTRACT_VERSION,
    MAP_BUILDER_PLUGIN_VERSION,
    canonical_bytes,
    canonical_local_reference,
)
from r4_adjudicated_truth_contract import (
    SELECTION_ORIGIN_COUNTS,
    derive_truth_summary,
)


FINALIZER = Path(__file__).with_name("finalize_semantic_research_contract.py")
MANIFEST_NAME = "case-package-manifest.json"
RECEIPT_NAME = "case-package-freeze-receipt.json"
MANIFEST_KEYS = {
    "manifest_id",
    "research_contract_id",
    "map_builder_plugin_version",
    "case_package_contract_version",
    "preparation_contract_version",
    "locked_input_sha256",
    "final_contract_version",
    "final_contract_sha256",
    "formal_case_count",
    "adjudicated_truth_summary",
    "selection_origin_counts",
    "formal_case_ids",
    "control_case_ids",
    "stability_repeat_case_ids",
    "package_authorization_reference",
    "frozen_at",
    "model_execution_authorized",
    "full_screening_authorized",
    "downstream_release_state",
    "artifacts",
}
RECEIPT_KEYS = {
    "receipt_id",
    "research_contract_id",
    "final_contract_version",
    "manifest_reference",
    "manifest_sha256",
    "output_scope",
    "package_authorization_reference",
    "frozen_at",
    "model_execution_authorized",
    "full_screening_authorized",
    "downstream_release_state",
}


def fail(code: str, detail: str) -> int:
    print(
        json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False),
        file=sys.stderr,
    )
    return 1


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("object required")
    return payload


def artifact_role(reference: str) -> str:
    if reference == "00-合同/final-contract.json":
        return "final_contract"
    if reference == "00-合同准备/case-preparation-contract.locked.json":
        return "locked_preparation_contract"
    if reference.startswith("02-校准案例/"):
        return "formal_case_material"
    if reference.startswith("03-来源真值/raw/"):
        return "raw_truth_source"
    if reference.startswith("03-来源真值/receipts/"):
        return "truth_source_capture_receipt"
    if reference.startswith("03-来源真值/"):
        return "source_truth_package"
    if reference.startswith("01-节点快照/"):
        return "taxonomy_snapshot"
    if reference.startswith("01-术语桥/"):
        return "terminology_bridge"
    if reference.startswith("02-校准案例候选/"):
        return "holdout_provenance"
    return "frozen_contract_input"


def package_artifacts(
    root: Path, *, reject_duplicate_content: bool = False
) -> list[dict]:
    artifacts = []
    identities: set[tuple[int, int]] = set()
    content_hashes: set[str] = set()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("CASE_PACKAGE_SYMLINK_FORBIDDEN")
        if not path.is_file():
            continue
        stat = path.stat()
        if stat.st_nlink != 1:
            raise ValueError("CASE_PACKAGE_HARDLINK_FORBIDDEN")
        identity = (stat.st_dev, stat.st_ino)
        if identity in identities:
            raise ValueError("CASE_PACKAGE_HARDLINK_FORBIDDEN")
        identities.add(identity)
        if path in {root / MANIFEST_NAME, root / RECEIPT_NAME}:
            continue
        reference = path.relative_to(root).as_posix()
        if canonical_local_reference(reference) is None:
            raise ValueError("CASE_PACKAGE_REFERENCE_INVALID")
        body = path.read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        if reject_duplicate_content and digest in content_hashes:
            raise ValueError("CASE_PACKAGE_DUPLICATE_CONTENT_FORBIDDEN")
        content_hashes.add(digest)
        artifacts.append(
            {
                "reference": reference,
                "role": artifact_role(reference),
                "sha256": digest,
                "byte_length": len(body),
            }
        )
    return artifacts


def canonical_absolute_input(raw: object) -> Path | None:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        return None
    if unicodedata.normalize("NFKC", raw) != raw or not raw.startswith("/"):
        return None
    parts = raw.split("/")
    if parts[0] != "" or any(part in {"", ".", ".."} for part in parts[1:]):
        return None
    return Path(raw)


def has_symlink_component(path: Path) -> bool:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def rename_directory_no_replace(stage: Path, output: Path) -> str | None:
    if sys.platform != "darwin":
        return "CASE_PACKAGE_NO_REPLACE_UNAVAILABLE"
    libc = ctypes.CDLL(None, use_errno=True)
    renamex_np = libc.renamex_np
    renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    renamex_np.restype = ctypes.c_int
    result = renamex_np(
        os.fsencode(stage),
        os.fsencode(output),
        0x00000004,  # RENAME_EXCL from macOS sys/stdio.h
    )
    if result == 0:
        return None
    error_number = ctypes.get_errno()
    if error_number in {errno.EEXIST, errno.ENOTEMPTY}:
        return "OUTPUT_EXISTS"
    return "CASE_PACKAGE_PUBLISH_FAILED"


def publish_directory_create_only(
    stage: Path, output: Path, *, create_collision: bool = False
) -> str | None:
    descriptor = os.open(output.parent, os.O_RDONLY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        if create_collision:
            output.mkdir()
        return rename_directory_no_replace(stage, output)
    except OSError:
        return "CASE_PACKAGE_PUBLISH_FAILED"
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def verify_package(package: Path, expected_manifest_sha256: str) -> int:
    if not package.is_dir() or package.is_symlink():
        return fail("CASE_PACKAGE_INVALID", str(package))
    manifest_path = package / MANIFEST_NAME
    receipt_path = package / RECEIPT_NAME
    if not manifest_path.is_file() or not receipt_path.is_file():
        return fail("CASE_PACKAGE_INVALID", "manifest and receipt are required")
    if sha256_file(manifest_path) != expected_manifest_sha256:
        return fail("CASE_PACKAGE_MANIFEST_HASH_MISMATCH", str(manifest_path))
    try:
        payload = load_json(manifest_path)
        manifest = payload["content_first_case_package_manifest"]
        receipt_payload = load_json(receipt_path)
        receipt = receipt_payload["content_first_case_package_freeze_receipt"]
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return fail("CASE_PACKAGE_INVALID", str(exc))
    if (
        set(payload) != {"schema_version", "content_first_case_package_manifest"}
        or payload.get("schema_version") != "1.0-beta5"
        or not isinstance(manifest, dict)
        or set(manifest) != MANIFEST_KEYS
        or manifest.get("map_builder_plugin_version") != MAP_BUILDER_PLUGIN_VERSION
        or manifest.get("case_package_contract_version")
        != CASE_PACKAGE_CONTRACT_VERSION
        or not isinstance(manifest.get("artifacts"), list)
        or receipt_payload.get("schema_version") != "1.0-beta5"
        or set(receipt_payload)
        != {"schema_version", "content_first_case_package_freeze_receipt"}
        or not isinstance(receipt, dict)
        or set(receipt) != RECEIPT_KEYS
        or receipt.get("manifest_sha256") != expected_manifest_sha256
        or receipt.get("output_scope") != str(package.resolve())
        or receipt.get("model_execution_authorized") is not False
        or receipt.get("full_screening_authorized") is not False
        or receipt.get("downstream_release_state") != "RESEARCH_ONLY_BLOCKED"
    ):
        return fail("CASE_PACKAGE_INVALID", "manifest or receipt schema invalid")
    try:
        actual = package_artifacts(package, reject_duplicate_content=True)
    except ValueError as exc:
        return fail(str(exc), str(package))
    if actual != manifest["artifacts"]:
        return fail("CASE_PACKAGE_CLOSED_SET_INVALID", str(package))
    references = [row.get("reference") for row in actual]
    hashes = [row.get("sha256") for row in actual]
    if len(references) != len(set(references)):
        return fail("CASE_PACKAGE_CLOSED_SET_INVALID", "duplicate artifact reference")
    if not all(isinstance(value, str) and len(value) == 64 for value in hashes):
        return fail("CASE_PACKAGE_CLOSED_SET_INVALID", "invalid artifact hash")
    final_contract_path = package / "00-合同/final-contract.json"
    try:
        contract = load_json(final_contract_path)["semantic_research_contract"]
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return fail("CASE_PACKAGE_INVALID", str(exc))
    if (
        contract.get("map_builder_plugin_version") != MAP_BUILDER_PLUGIN_VERSION
        or contract.get("case_package_contract_version")
        != CASE_PACKAGE_CONTRACT_VERSION
        or contract.get("contract_state") != "frozen"
        or manifest.get("final_contract_sha256") != sha256_file(final_contract_path)
        or manifest.get("research_contract_id") != contract.get("research_contract_id")
        or manifest.get("final_contract_version") != contract.get("contract_version")
        or manifest.get("manifest_id")
        != f"{contract.get('research_contract_id')}-CASE-PACKAGE"
        or manifest.get("frozen_at") != contract.get("frozen_at")
        or not isinstance(manifest.get("package_authorization_reference"), str)
        or not manifest["package_authorization_reference"].strip()
    ):
        return fail("CASE_PACKAGE_FINAL_CONTRACT_INVALID", str(final_contract_path))
    try:
        case_binding = contract["calibration_case_set_reference_and_hash"]
        formal_reference = case_binding["reference"]
        formal_path = package / PurePosixPath(formal_reference)
        formal_hash = sha256_file(formal_path)
        formal_rows = [
            json.loads(line)
            for line in formal_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        header = next(
            row for row in formal_rows if row.get("record_type") == "case_set_contract"
        )
        cases = [
            row for row in formal_rows if row.get("record_type") == "calibration_case"
        ]
        truth_reference = contract["source_truth_package_reference"]
        truth_path = package / PurePosixPath(truth_reference)
        truth_rows = [
            json.loads(line)
            for line in truth_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        return fail("CASE_PACKAGE_MANIFEST_FACT_MISMATCH", str(exc))
    recomputed_origins = {
        origin: sum(
            (row.get("provenance") or {}).get("selection_origin") == origin
            for row in cases
        )
        for origin in SELECTION_ORIGIN_COUNTS
    }
    recomputed_truth_summary = derive_truth_summary(truth_rows)
    gate = contract.get("case_preparation_gate") or {}
    if (
        canonical_local_reference(formal_reference) is None
        or formal_hash != case_binding.get("sha256")
        or manifest.get("formal_case_count") != len(cases)
        or manifest.get("adjudicated_truth_summary") != recomputed_truth_summary
        or manifest.get("selection_origin_counts") != recomputed_origins
        or manifest.get("formal_case_ids") != header.get("formal_case_ids")
        or manifest.get("control_case_ids")
        != (contract.get("control_case_rule") or {}).get("case_ids")
        or manifest.get("stability_repeat_case_ids")
        != header.get("stability_repeat_case_ids")
        or manifest.get("preparation_contract_version")
        != gate.get("preparation_contract_version")
        or manifest.get("locked_input_sha256") != gate.get("locked_input_sha256")
        or manifest.get("model_execution_authorized") is not False
        or manifest.get("full_screening_authorized") is not False
        or manifest.get("downstream_release_state") != "RESEARCH_ONLY_BLOCKED"
        or receipt.get("research_contract_id") != contract.get("research_contract_id")
        or receipt.get("receipt_id")
        != f"{contract.get('research_contract_id')}-CASE-PACKAGE-FREEZE"
        or receipt.get("final_contract_version") != contract.get("contract_version")
        or receipt.get("manifest_reference") != MANIFEST_NAME
        or receipt.get("package_authorization_reference")
        != manifest.get("package_authorization_reference")
        or receipt.get("frozen_at") != manifest.get("frozen_at")
    ):
        return fail("CASE_PACKAGE_MANIFEST_FACT_MISMATCH", str(package))
    print(
        json.dumps(
            {
                "status": "PASS",
                "package": str(package),
                "manifest_sha256": expected_manifest_sha256,
                "artifact_count": len(actual),
            },
            ensure_ascii=False,
        )
    )
    return 0


def build(args: argparse.Namespace) -> int:
    output_argument = args.output.absolute()
    output = output_argument.parent.resolve() / output_argument.name
    if os.path.lexists(output):
        return fail("OUTPUT_EXISTS", str(output))
    source_argument = canonical_absolute_input(args.contract_local_root)
    if source_argument is None or has_symlink_component(source_argument):
        return fail("CONTRACT_LOCAL_ROOT_INVALID", str(args.contract_local_root))
    try:
        source_root = source_argument.resolve(strict=True)
    except (OSError, ValueError):
        return fail("CONTRACT_LOCAL_ROOT_INVALID", str(source_argument))
    if not source_root.is_dir():
        return fail("CONTRACT_LOCAL_ROOT_INVALID", str(source_root))
    try:
        package_artifacts(source_root, reject_duplicate_content=True)
    except ValueError as exc:
        return fail(str(exc), str(source_root))
    declared = (
        (args.case_set, args.case_set_reference),
        (args.visible_case_set, args.visible_case_set_reference),
        (
            args.visible_case_freeze_receipt,
            args.visible_case_freeze_receipt_reference,
        ),
        (args.source_truth_package, args.source_truth_reference),
    )
    for raw_actual, reference in declared:
        if canonical_local_reference(reference) is None:
            return fail("DECLARED_INPUT_PATH_MISMATCH", str(reference))
        actual = canonical_absolute_input(raw_actual)
        expected = source_root / PurePosixPath(reference)
        if (
            actual is None
            or actual != expected
            or has_symlink_component(actual)
        ):
            return fail("DECLARED_INPUT_PATH_MISMATCH", str(raw_actual))
        try:
            resolved_actual = actual.resolve(strict=True)
        except (OSError, ValueError):
            return fail("DECLARED_INPUT_PATH_MISMATCH", str(reference))
        if resolved_actual != expected:
            return fail("DECLARED_INPUT_PATH_MISMATCH", str(raw_actual))
    if not args.package_authorization_reference.strip():
        return fail("PACKAGE_AUTHORIZATION_INVALID", "authorization reference required")

    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent)
    )
    try:
        shutil.copytree(source_root, stage, dirs_exist_ok=True)
        locked_target = stage / "00-合同准备/case-preparation-contract.locked.json"
        locked_target.parent.mkdir(parents=True, exist_ok=True)
        locked_target.write_bytes(args.preparation_contract.resolve().read_bytes())
        final_contract = stage / "00-合同/final-contract.json"
        final_contract.parent.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            str(FINALIZER),
            "--preparation-contract",
            str(locked_target),
            "--case-set",
            str(stage / PurePosixPath(args.case_set_reference)),
            "--case-set-reference",
            args.case_set_reference,
            "--visible-case-set",
            str(stage / PurePosixPath(args.visible_case_set_reference)),
            "--visible-case-set-reference",
            args.visible_case_set_reference,
            "--visible-case-freeze-receipt",
            str(stage / PurePosixPath(args.visible_case_freeze_receipt_reference)),
            "--visible-case-freeze-receipt-reference",
            args.visible_case_freeze_receipt_reference,
            "--expected-visible-case-freeze-receipt-sha256",
            args.expected_visible_case_freeze_receipt_sha256,
            "--source-truth-package",
            str(stage / PurePosixPath(args.source_truth_reference)),
            "--source-truth-reference",
            args.source_truth_reference,
            "--final-contract-version",
            args.final_contract_version,
            "--batch-size",
            str(args.batch_size),
            "--frozen-at",
            args.frozen_at,
            "--contract-local-root",
            str(stage),
            "--output",
            str(final_contract),
        ]
        for control_id in args.control_case_id:
            command.extend(["--control-case-id", control_id])
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            return fail(
                "CASE_PACKAGE_BUILD_FAILED",
                (result.stderr or result.stdout).strip(),
            )
        if args.test_fail_after_phase == "final-contract":
            return fail("CASE_PACKAGE_BUILD_FAILED", "injected after final contract")
        final_payload = load_json(final_contract)
        contract = final_payload["semantic_research_contract"]
        formal_rows = [
            json.loads(line)
            for line in (stage / PurePosixPath(args.case_set_reference))
            .read_text(encoding="utf-8")
            .splitlines()
            if line
        ]
        cases = [row for row in formal_rows if row.get("record_type") == "calibration_case"]
        header = next(
            row for row in formal_rows if row.get("record_type") == "case_set_contract"
        )
        artifacts = package_artifacts(stage, reject_duplicate_content=True)
        manifest = {
            "schema_version": "1.0-beta5",
            "content_first_case_package_manifest": {
                "manifest_id": f"{contract['research_contract_id']}-CASE-PACKAGE",
                "research_contract_id": contract["research_contract_id"],
                "map_builder_plugin_version": MAP_BUILDER_PLUGIN_VERSION,
                "case_package_contract_version": CASE_PACKAGE_CONTRACT_VERSION,
                "preparation_contract_version": contract["case_preparation_gate"][
                    "preparation_contract_version"
                ],
                "locked_input_sha256": contract["case_preparation_gate"][
                    "locked_input_sha256"
                ],
                "final_contract_version": contract["contract_version"],
                "final_contract_sha256": sha256_file(final_contract),
                "formal_case_count": len(cases),
                "adjudicated_truth_summary": derive_truth_summary(
                    [
                        json.loads(line)
                        for line in (
                            stage
                            / PurePosixPath(contract["source_truth_package_reference"])
                        )
                        .read_text(encoding="utf-8")
                        .splitlines()
                        if line
                    ]
                ),
                "selection_origin_counts": {
                    origin: sum(
                        (row.get("provenance") or {}).get("selection_origin") == origin
                        for row in cases
                    )
                    for origin in SELECTION_ORIGIN_COUNTS
                },
                "formal_case_ids": header["formal_case_ids"],
                "control_case_ids": list(args.control_case_id),
                "stability_repeat_case_ids": header["stability_repeat_case_ids"],
                "package_authorization_reference": args.package_authorization_reference,
                "frozen_at": args.frozen_at,
                "model_execution_authorized": False,
                "full_screening_authorized": False,
                "downstream_release_state": "RESEARCH_ONLY_BLOCKED",
                "artifacts": artifacts,
            },
        }
        manifest_path = stage / MANIFEST_NAME
        manifest_path.write_bytes(canonical_bytes(manifest))
        manifest_sha = sha256_file(manifest_path)
        receipt = {
            "schema_version": "1.0-beta5",
            "content_first_case_package_freeze_receipt": {
                "receipt_id": f"{contract['research_contract_id']}-CASE-PACKAGE-FREEZE",
                "research_contract_id": contract["research_contract_id"],
                "final_contract_version": contract["contract_version"],
                "manifest_reference": MANIFEST_NAME,
                "manifest_sha256": manifest_sha,
                "output_scope": str(output),
                "package_authorization_reference": args.package_authorization_reference,
                "frozen_at": args.frozen_at,
                "model_execution_authorized": False,
                "full_screening_authorized": False,
                "downstream_release_state": "RESEARCH_ONLY_BLOCKED",
            },
        }
        (stage / RECEIPT_NAME).write_bytes(canonical_bytes(receipt))
        publish_error = publish_directory_create_only(
            stage,
            output,
            create_collision=args.test_create_output_before_publish,
        )
        if publish_error:
            return fail(publish_error, str(output))
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "package": str(output),
                    "manifest_sha256": manifest_sha,
                    "artifact_count": len(artifacts),
                    "model_execution_authorized": False,
                },
                ensure_ascii=False,
            )
        )
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return fail("CASE_PACKAGE_BUILD_FAILED", str(exc))
    finally:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Atomically freeze or verify one closed-set R4 beta.4 case package."
    )
    parser.add_argument("--verify-package", type=Path)
    parser.add_argument("--expected-manifest-sha256")
    parser.add_argument("--preparation-contract", type=Path)
    parser.add_argument("--contract-local-root")
    parser.add_argument("--case-set")
    parser.add_argument("--case-set-reference")
    parser.add_argument("--visible-case-set")
    parser.add_argument("--visible-case-set-reference")
    parser.add_argument("--visible-case-freeze-receipt")
    parser.add_argument("--visible-case-freeze-receipt-reference")
    parser.add_argument("--expected-visible-case-freeze-receipt-sha256")
    parser.add_argument("--source-truth-package")
    parser.add_argument("--source-truth-reference")
    parser.add_argument("--final-contract-version")
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--control-case-id", action="append", default=[])
    parser.add_argument("--frozen-at")
    parser.add_argument("--package-authorization-reference")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--test-fail-after-phase", choices=("final-contract",)
    )
    parser.add_argument("--test-create-output-before-publish", action="store_true")
    args = parser.parse_args()
    if args.verify_package is not None:
        if not isinstance(args.expected_manifest_sha256, str):
            return fail("EXPECTED_MANIFEST_HASH_REQUIRED", "verification requires trusted hash")
        return verify_package(
            args.verify_package.absolute(), args.expected_manifest_sha256
        )
    required = (
        args.preparation_contract,
        args.contract_local_root,
        args.case_set,
        args.case_set_reference,
        args.visible_case_set,
        args.visible_case_set_reference,
        args.visible_case_freeze_receipt,
        args.visible_case_freeze_receipt_reference,
        args.expected_visible_case_freeze_receipt_sha256,
        args.source_truth_package,
        args.source_truth_reference,
        args.final_contract_version,
        args.batch_size,
        args.control_case_id,
        args.frozen_at,
        args.package_authorization_reference,
        args.output,
    )
    if any(value in (None, "", []) for value in required):
        return fail("CASE_PACKAGE_ARGUMENT_INVALID", "all build arguments are required")
    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
