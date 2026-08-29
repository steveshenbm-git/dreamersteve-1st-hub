#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from validate_semantic_research_workspace import (
    case_preparation_contract_completeness_errors,
    case_preparation_input_sha256,
    case_preparation_outputs_are_empty,
    content_first_default_deny_errors,
    content_first_local_frozen_reference_errors,
    nonempty_text,
    validate_r3_source_manifest,
)
from validate_terminology_bridge import load_rows, validate_rows
from r4_case_package_contract import (
    CASE_PACKAGE_CONTRACT_VERSION,
    MAP_BUILDER_PLUGIN_VERSION,
    aware_datetime,
    publish_create_only_atomic,
)
from r4_adjudicated_truth_contract import DIRECTOR_PLUGIN_VERSION


def fail(code: str, detail: str) -> int:
    print(
        json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False),
        file=sys.stderr,
    )
    return 1


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lock complete RC2 inputs for candidate/case preparation without freezing a model-run contract."
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--terminology-bridge", type=Path)
    parser.add_argument("--terminology-bridge-reference")
    parser.add_argument("--r3-source-manifest", type=Path)
    parser.add_argument("--r3-source-manifest-reference")
    parser.add_argument("--authorization-reference", required=True)
    parser.add_argument("--expected-skill-git-commit")
    parser.add_argument("--locked-at", required=True)
    parser.add_argument("--test-fail-after-temp-write", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = args.contract.resolve()
    output = args.output.resolve()
    if not source.is_file():
        return fail("CONTRACT_MISSING", str(source))
    if output.exists():
        return fail("OUTPUT_EXISTS", str(output))
    if not nonempty_text(args.authorization_reference) or not nonempty_text(args.locked_at):
        return fail("AUTHORIZATION_INVALID", "authorization reference and locked_at are required")
    if aware_datetime(args.locked_at) is None:
        return fail("LOCKED_AT_INVALID", "locked_at must be timezone-aware ISO-8601")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
        contract = payload["semantic_research_contract"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return fail("CONTRACT_INVALID", str(exc))
    if not isinstance(payload, dict) or not isinstance(contract, dict):
        return fail("CONTRACT_INVALID", "semantic_research_contract must be an object")
    if contract.get("contract_state") != "draft":
        return fail("CONTRACT_NOT_DRAFT", str(contract.get("contract_state")))
    if "execution_mode" in contract and contract.get("execution_mode") != "content_first":
        return fail("EXECUTION_MODE_INVALID", str(contract.get("execution_mode")))
    content_first = contract.get("execution_mode") == "content_first"
    if content_first:
        created_at = aware_datetime(contract.get("created_at"))
        locked_at = aware_datetime(args.locked_at)
        if created_at is None or locked_at is None or created_at >= locked_at:
            return fail(
                "CONTRACT_CREATED_AT_INVALID",
                "created_at must be timezone-aware and strictly earlier than locked_at",
            )
        if (
            not nonempty_text(contract.get("owner_authorization_reference"))
            or contract.get("owner_authorization_reference")
            != args.authorization_reference
        ):
            return fail(
                "OWNER_AUTHORIZATION_REFERENCE_INVALID",
                "contract owner authorization must match the lock authorization",
            )
        skill_git_commit = contract.get("skill_git_commit")
        if (
            not isinstance(skill_git_commit, str)
            or len(skill_git_commit) != 40
            or any(character not in "0123456789abcdef" for character in skill_git_commit)
        ):
            return fail("SKILL_GIT_COMMIT_INVALID", repr(skill_git_commit))
        expected_skill_git_commit = args.expected_skill_git_commit
        if (
            not isinstance(expected_skill_git_commit, str)
            or len(expected_skill_git_commit) != 40
            or any(
                character not in "0123456789abcdef"
                for character in expected_skill_git_commit
            )
        ):
            return fail(
                "EXPECTED_SKILL_GIT_COMMIT_REQUIRED",
                repr(expected_skill_git_commit),
            )
        if skill_git_commit != expected_skill_git_commit:
            return fail(
                "SKILL_GIT_COMMIT_MISMATCH",
                f"contract={skill_git_commit} expected={expected_skill_git_commit}",
            )
        if contract.get("workflow_director_plugin_version") != DIRECTOR_PLUGIN_VERSION:
            return fail(
                "WORKFLOW_DIRECTOR_PLUGIN_VERSION_INVALID",
                repr(contract.get("workflow_director_plugin_version")),
            )
        if contract.get("map_builder_plugin_version") != MAP_BUILDER_PLUGIN_VERSION:
            return fail(
                "MAP_BUILDER_PLUGIN_VERSION_INVALID",
                repr(contract.get("map_builder_plugin_version")),
            )
        if (
            contract.get("case_package_contract_version")
            != CASE_PACKAGE_CONTRACT_VERSION
        ):
            return fail(
                "CASE_PACKAGE_CONTRACT_VERSION_INVALID",
                repr(contract.get("case_package_contract_version")),
            )
        if content_first_default_deny_errors(contract):
            return fail("CONTENT_FIRST_DEFAULT_DENY_REQUIRED", "execution and downstream authorization must remain default-deny")
        if args.terminology_bridge is None or not nonempty_text(args.terminology_bridge_reference):
            return fail("TERMINOLOGY_BRIDGE_REQUIRED", "content_first preparation requires a terminology bridge and reference")
        preparation_root = source.parent.parent
        if source.parent != preparation_root / "00-合同准备":
            return fail("PREPARATION_CONTRACT_NOT_LOCAL", str(source))
        term_path = args.terminology_bridge.resolve()
        expected_term_path = preparation_root / "01-术语桥" / term_path.name
        if term_path != expected_term_path:
            return fail("TERMINOLOGY_BRIDGE_NOT_CONTRACT_LOCAL", str(term_path))
        reference = Path(args.terminology_bridge_reference)
        if reference.is_absolute() or ".." in reference.parts or reference.as_posix() != term_path.relative_to(preparation_root).as_posix():
            return fail("TERMINOLOGY_BRIDGE_REFERENCE_INVALID", args.terminology_bridge_reference)
        term_rows, term_errors = load_rows(term_path)
        header = next(
            (row for row in term_rows if row.get("record_type") == "terminology_bridge_contract"),
            {},
        )
        if header.get("research_contract_id") != contract.get("research_contract_id"):
            return fail("TERMINOLOGY_BRIDGE_CONTRACT_ID_MISMATCH", str(header.get("research_contract_id")))
        if header.get("contract_version") != contract.get("contract_version"):
            return fail("TERMINOLOGY_BRIDGE_VERSION_MISMATCH", str(header.get("contract_version")))
        term_errors.extend(validate_rows(term_rows, contract.get("research_contract_id")))
        if term_errors:
            return fail("TERMINOLOGY_BRIDGE_INVALID", ";".join(error["code"] for error in term_errors))
        architecture = contract.get("terminology_architecture")
        if not isinstance(architecture, dict):
            return fail("TERMINOLOGY_ARCHITECTURE_INVALID", "missing terminology_architecture")
        architecture.update(
            {
                "term_pack_reference": args.terminology_bridge_reference,
                "term_pack_sha256": hashlib.sha256(term_path.read_bytes()).hexdigest(),
                "term_pack_state": (
                    "frozen_reviewed"
                    if header.get("term_pack_state") == "frozen"
                    else header.get("term_pack_state")
                ),
            }
        )
        if args.r3_source_manifest is None or not nonempty_text(args.r3_source_manifest_reference):
            return fail("R3_SOURCE_MANIFEST_REQUIRED", "content_first preparation requires an accepted R3 source manifest")
        manifest_path = args.r3_source_manifest.resolve()
        if not manifest_path.is_file():
            return fail("R3_SOURCE_MANIFEST_MISSING", str(manifest_path))
        expected_manifest_parent = preparation_root / "02-校准案例候选"
        if manifest_path.parent != expected_manifest_parent:
            return fail("R3_SOURCE_MANIFEST_NOT_CONTRACT_LOCAL", str(manifest_path))
        manifest_reference = Path(args.r3_source_manifest_reference)
        if (
            manifest_reference.is_absolute()
            or ".." in manifest_reference.parts
            or manifest_reference.as_posix()
            != manifest_path.relative_to(preparation_root).as_posix()
        ):
            return fail("R3_SOURCE_MANIFEST_REFERENCE_INVALID", args.r3_source_manifest_reference)
        contract["r3_case_source_manifest_reference_and_hash"] = {
            "reference": args.r3_source_manifest_reference,
            "sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        }
        manifest_errors, _ = validate_r3_source_manifest(contract, preparation_root)
        if manifest_errors:
            return fail("R3_SOURCE_MANIFEST_INVALID", ";".join(manifest_errors))
        contract.setdefault(
            "calibration_case_set_reference_and_hash", {"reference": None, "sha256": None}
        )
        contract.setdefault(
            "visible_case_set_reference_and_hash", {"reference": None, "sha256": None}
        )
        contract.setdefault(
            "visible_case_freeze_receipt_reference_and_hash", {"reference": None, "sha256": None}
        )
        contract.setdefault(
            "batch_rule",
            {"batch_size": None, "stop_after_each_batch": True, "trigger_rate_is_diagnostic_not_pass_gate": True},
        )
        contract.setdefault(
            "control_case_rule", {"case_ids": [], "drift_requires_pause": True}
        )
        contract.setdefault(
            "case_preparation_gate",
            {"authorization": False, "authorization_reference": None, "preparation_contract_version": None, "state": "draft", "locked_at": None, "locked_input_sha256": None},
        )
    if not case_preparation_outputs_are_empty(contract):
        return fail(
            "PREPARATION_OUTPUTS_NOT_EMPTY",
            "case-set reference/hash, batch size, control IDs, and frozen_at must remain empty before case preparation",
        )
    gate = contract.get("case_preparation_gate")
    if not isinstance(gate, dict):
        return fail("CASE_PREPARATION_GATE_INVALID", "missing case_preparation_gate object")

    preparation_version = contract.get("contract_version")
    if not nonempty_text(preparation_version):
        return fail("CONTRACT_VERSION_INVALID", repr(preparation_version))
    payload["schema_version"] = "1.2"
    contract["contract_state"] = "case_preparation_locked"
    gate.update(
        {
            "authorization": True,
            "authorization_reference": args.authorization_reference,
            "preparation_contract_version": preparation_version,
            "state": "locked",
            "locked_at": args.locked_at,
            "locked_input_sha256": None,
        }
    )
    gate["locked_input_sha256"] = case_preparation_input_sha256(contract)
    problems = case_preparation_contract_completeness_errors(contract)
    if problems:
        return fail("CASE_PREPARATION_CONTRACT_INCOMPLETE", ";".join(problems))
    if content_first:
        manifest_errors, _ = validate_r3_source_manifest(contract, preparation_root)
        if manifest_errors:
            return fail("R3_SOURCE_MANIFEST_INVALID", ";".join(manifest_errors))
        reference_problems = content_first_local_frozen_reference_errors(contract, preparation_root)
        if reference_problems:
            return fail("FROZEN_REFERENCE_INVALID", ";".join(reference_problems))

    publish_error = publish_create_only_atomic(
        output,
        canonical_bytes(payload),
        fail_after_temp_write=args.test_fail_after_temp_write,
    )
    if publish_error:
        return fail(publish_error, str(output))
    print(
        json.dumps(
            {
                "status": "PASS",
                "contract_state": "case_preparation_locked",
                "output": str(output),
                "locked_input_sha256": gate["locked_input_sha256"],
                "model_run_authorized": False,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
