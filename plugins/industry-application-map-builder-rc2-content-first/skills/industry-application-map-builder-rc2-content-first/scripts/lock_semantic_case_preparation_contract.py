#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from validate_semantic_research_workspace import (
    case_preparation_contract_completeness_errors,
    case_preparation_input_sha256,
    case_preparation_outputs_are_empty,
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lock complete RC2 inputs for candidate/case preparation without freezing a model-run contract."
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--authorization-reference", required=True)
    parser.add_argument("--locked-at", required=True)
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
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
        contract = payload["semantic_research_contract"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return fail("CONTRACT_INVALID", str(exc))
    if not isinstance(payload, dict) or not isinstance(contract, dict):
        return fail("CONTRACT_INVALID", "semantic_research_contract must be an object")
    if contract.get("contract_state") != "draft":
        return fail("CONTRACT_NOT_DRAFT", str(contract.get("contract_state")))
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

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_bytes(payload))
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
