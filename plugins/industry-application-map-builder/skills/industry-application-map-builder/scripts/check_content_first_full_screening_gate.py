#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 2


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the explicit RC2 content-first full-screening authorization gate without running any node."
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--calibration-report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        return fail("OUTPUT_EXISTS", str(args.output))
    try:
        payload = json.loads(args.contract.read_text(encoding="utf-8"))
        contract = payload.get("semantic_research_contract", {}) if isinstance(payload, dict) else {}
        report = json.loads(args.calibration_report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail("FULL_SCOPE_INPUT_INVALID", str(exc))
    policy = contract.get("content_first_policy", {}) if isinstance(contract, dict) else {}
    shared_fields = ("research_contract_id", "contract_version", "taxonomy_snapshot_sha256")
    contract_ready = (
        contract.get("execution_mode") == "content_first"
        and contract.get("contract_state") == "frozen"
        and isinstance(policy, dict)
        and policy.get("downstream_release_state") == "RESEARCH_ONLY_BLOCKED"
    )
    report_matches = all(contract.get(field) == report.get(field) and nonempty(contract.get(field)) for field in shared_fields)
    calibration_passes = (
        report.get("content_method_state") == "CONTENT_CALIBRATION_PASS"
        and report.get("not_beta3_effectiveness") is True
        and report.get("safety_failures") == []
    )
    explicit_authorization = (
        contract.get("full_screening_authorization") is True
        and nonempty(contract.get("full_screening_authorization_reference"))
    )
    reasons: list[str] = []
    if not contract_ready:
        state = "BLOCKED"
        reasons.append("content-first contract or research-only boundary is invalid")
    elif not report_matches:
        state = "BLOCKED"
        reasons.append("calibration report does not match frozen contract")
    elif not calibration_passes:
        state = "BLOCKED"
        reasons.append("content calibration has not passed with zero safety failures")
    elif not explicit_authorization:
        state = "NOT_AUTHORIZED"
        reasons.append("explicit full-screening authorization reference is missing")
    else:
        state = "AUTHORIZED_NOT_STARTED"
    output = {
        "schema_version": "1.0",
        "research_contract_id": contract.get("research_contract_id"),
        "contract_version": contract.get("contract_version"),
        "taxonomy_snapshot_sha256": contract.get("taxonomy_snapshot_sha256"),
        "content_full_screening_state": state,
        "authorization_reference": contract.get("full_screening_authorization_reference"),
        "runs_nodes": False,
        "downstream_release_state": "RESEARCH_ONLY_BLOCKED",
        "reasons": reasons,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS" if state == "AUTHORIZED_NOT_STARTED" else "FAIL", "content_full_screening_state": state, "output": str(args.output)}, ensure_ascii=False))
    return 0 if state == "AUTHORIZED_NOT_STARTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
