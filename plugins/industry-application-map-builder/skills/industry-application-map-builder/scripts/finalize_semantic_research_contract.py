#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from validate_semantic_research_workspace import (
    case_preparation_contract_completeness_errors,
    frozen_contract_completeness_errors,
    load_jsonl,
    nonempty_text,
)


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


def validate_case_set(rows: list[dict], research_contract_id: object) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    headers = [row for row in rows if row.get("record_type") == "case_set_contract"]
    cases = [row for row in rows if row.get("record_type") == "calibration_case"]
    if len(headers) != 1:
        problems.append("exactly_one_case_set_contract_required")
        header: dict = {}
    else:
        header = headers[0]
    if any(row.get("record_type") not in {"case_set_contract", "calibration_case"} for row in rows):
        problems.append("unknown_record_type")
    if (
        header.get("case_count") != 40
        or header.get("actual_case_record_count") != 40
        or header.get("case_set_state") != "frozen"
        or not nonempty_text(header.get("case_set_id"))
        or header.get("research_contract_id") != research_contract_id
    ):
        problems.append("case_set_contract_invalid")
    case_ids = [row.get("case_id") for row in cases]
    if (
        len(cases) != 40
        or not all(nonempty_text(case_id) for case_id in case_ids)
        or len(set(case_ids)) != 40
        or any(row.get("research_contract_id") != research_contract_id for row in cases)
    ):
        problems.append("forty_unique_contract_bound_cases_required")
    return problems, [str(case_id) for case_id in case_ids if nonempty_text(case_id)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bind a real frozen 40-case set to a new final RC2 research-contract version."
    )
    parser.add_argument("--preparation-contract", required=True, type=Path)
    parser.add_argument("--case-set", required=True, type=Path)
    parser.add_argument("--case-set-reference", required=True)
    parser.add_argument("--final-contract-version", required=True)
    parser.add_argument("--batch-size", required=True, type=int)
    parser.add_argument("--control-case-id", required=True, action="append")
    parser.add_argument("--frozen-at", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    preparation_path = args.preparation_contract.resolve()
    case_set_path = args.case_set.resolve()
    output = args.output.resolve()
    if not preparation_path.is_file():
        return fail("PREPARATION_CONTRACT_MISSING", str(preparation_path))
    if not case_set_path.is_file():
        return fail("CASE_SET_MISSING", str(case_set_path))
    if output.exists():
        return fail("OUTPUT_EXISTS", str(output))
    if (
        not nonempty_text(args.case_set_reference)
        or not nonempty_text(args.final_contract_version)
        or not nonempty_text(args.frozen_at)
        or args.batch_size <= 0
    ):
        return fail("FINALIZATION_ARGUMENT_INVALID", "reference, version, frozen_at, and positive batch size are required")
    if len(set(args.control_case_id)) != len(args.control_case_id):
        return fail("CONTROL_CASE_IDS_INVALID", "control case IDs must be unique")

    try:
        payload = json.loads(preparation_path.read_text(encoding="utf-8"))
        contract = payload["semantic_research_contract"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return fail("PREPARATION_CONTRACT_INVALID", str(exc))
    preparation_problems = case_preparation_contract_completeness_errors(contract)
    if preparation_problems:
        code = (
            "PREPARATION_LOCK_HASH_MISMATCH"
            if "case_preparation_gate.locked_input_sha256:mismatch" in preparation_problems
            else "PREPARATION_CONTRACT_INCOMPLETE"
        )
        return fail(code, ";".join(preparation_problems))

    preparation_version = contract["contract_version"]
    if args.final_contract_version == preparation_version:
        return fail(
            "FINAL_CONTRACT_VERSION_NOT_NEW",
            "final contract version must differ from the locked preparation contract version",
        )
    try:
        rows = load_jsonl(case_set_path)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return fail("CASE_SET_INVALID", str(exc))
    case_problems, case_ids = validate_case_set(rows, contract.get("research_contract_id"))
    missing_controls = sorted(set(args.control_case_id) - set(case_ids))
    if missing_controls:
        case_problems.append("control_case_ids_not_in_case_set:" + ",".join(missing_controls))
    if case_problems:
        return fail("CASE_SET_INVALID", ";".join(case_problems))

    payload["schema_version"] = "1.2"
    contract["contract_version"] = args.final_contract_version
    contract["contract_state"] = "frozen"
    contract["frozen_at"] = args.frozen_at
    contract["calibration_case_set_reference_and_hash"] = {
        "reference": args.case_set_reference,
        "sha256": hashlib.sha256(case_set_path.read_bytes()).hexdigest(),
    }
    contract["batch_rule"]["batch_size"] = args.batch_size
    contract["control_case_rule"]["case_ids"] = list(args.control_case_id)
    final_problems = frozen_contract_completeness_errors(contract)
    if final_problems:
        return fail("FINAL_CONTRACT_INCOMPLETE", ";".join(final_problems))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_bytes(payload))
    print(
        json.dumps(
            {
                "status": "PASS",
                "contract_state": "frozen",
                "output": str(output),
                "case_set_sha256": contract["calibration_case_set_reference_and_hash"]["sha256"],
                "final_contract_completeness": "PASS",
                "workspace_reference_validation_required": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
