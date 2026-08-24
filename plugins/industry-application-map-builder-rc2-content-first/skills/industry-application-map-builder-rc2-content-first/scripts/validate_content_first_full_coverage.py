#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


SCREENING_RESULTS = {"hypothesis_formed", "ambiguous", "no_hypothesis_formed"}
WORK_STATES = {
    "screened",
    "evidence_expansion_required",
    "evidence_expanded",
    "audit_reopened",
}
EVIDENCE_STATES = {"supported", "hypothesis", "unknown", "conflicted"}


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 2


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check frozen RC2 content-first terminal-node coverage without releasing downstream work."
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--terminal-node-manifest", required=True, type=Path)
    parser.add_argument("--screening-index", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        return fail("OUTPUT_EXISTS", str(args.output))
    try:
        contract_payload = json.loads(args.contract.read_text(encoding="utf-8"))
        contract = (
            contract_payload.get("semantic_research_contract", {})
            if isinstance(contract_payload, dict)
            else {}
        )
        manifest = json.loads(args.terminal_node_manifest.read_text(encoding="utf-8"))
        index_payload = json.loads(args.screening_index.read_text(encoding="utf-8"))
        index = (
            index_payload.get("semantic_content_full_screening_index", {})
            if isinstance(index_payload, dict)
            else {}
        )
    except (OSError, json.JSONDecodeError) as exc:
        return fail("FULL_COVERAGE_INPUT_INVALID", str(exc))

    reasons: list[str] = []
    policy = contract.get("content_first_policy", {}) if isinstance(contract, dict) else {}
    node_ids = manifest.get("terminal_node_ids") if isinstance(manifest, dict) else None
    manifest_valid = (
        isinstance(node_ids, list)
        and bool(node_ids)
        and all(nonempty(node_id) for node_id in node_ids)
        and len(set(node_ids)) == len(node_ids)
        and contract.get("terminal_node_count") == len(node_ids)
        and contract.get("terminal_node_manifest_sha256") == sha256_file(args.terminal_node_manifest)
    )
    contract_valid = (
        contract.get("execution_mode") == "content_first"
        and contract.get("contract_state") == "frozen"
        and contract.get("full_screening_authorization") is True
        and nonempty(contract.get("full_screening_authorization_reference"))
        and isinstance(policy, dict)
        and policy.get("content_method_state") == "CONTENT_CALIBRATION_PASS"
        and policy.get("content_full_screening_state")
        in {"AUTHORIZED_NOT_STARTED", "IN_PROGRESS", "COVERAGE_INCOMPLETE"}
        and policy.get("downstream_release_state") == "RESEARCH_ONLY_BLOCKED"
    )
    shared_fields = ("research_contract_id", "contract_version", "terminal_node_manifest_sha256")
    index_matches = all(index.get(field) == contract.get(field) for field in shared_fields)
    rows = index.get("node_evidence") if isinstance(index, dict) else None
    indexed: dict[str, dict[str, Any]] = {}
    rows_valid = isinstance(rows, list) and index.get("method_arm") == "candidate_screen_then_expand"
    required_row_fields = {
        "industry_node_id",
        "visible_input_sha256",
        "raw_response_sha256",
        "scorecard_sha256",
        "screening_result",
        "semantic_work_state",
        "evidence_state",
        "unknown_items_present",
    }
    if rows_valid:
        for row in rows:
            if not isinstance(row, dict) or set(row) != required_row_fields:
                rows_valid = False
                break
            node_id = row.get("industry_node_id")
            if (
                not nonempty(node_id)
                or node_id in indexed
                or not all(sha256_text(row.get(field)) for field in ("visible_input_sha256", "raw_response_sha256", "scorecard_sha256"))
                or row.get("screening_result") not in SCREENING_RESULTS
                or row.get("semantic_work_state") not in WORK_STATES
                or row.get("evidence_state") not in EVIDENCE_STATES
                or row.get("unknown_items_present") is not True
            ):
                rows_valid = False
                break
            indexed[node_id] = row
    if not contract_valid:
        state = "BLOCKED"
        reasons.append("content calibration, authorization, or research-only boundary is not valid")
    elif not manifest_valid:
        state = "BLOCKED"
        reasons.append("frozen terminal-node manifest is invalid or mismatched")
    elif not index_matches or not rows_valid:
        state = "BLOCKED"
        reasons.append("screening index is malformed or does not match the frozen contract")
    else:
        expected = set(node_ids)
        actual = set(indexed)
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        if missing or unexpected:
            state = "COVERAGE_INCOMPLETE"
            if missing:
                reasons.append(f"missing terminal nodes: {','.join(missing[:10])}")
            if unexpected:
                reasons.append(f"unexpected terminal nodes: {','.join(unexpected[:10])}")
        else:
            state = "READY_FOR_REVERSE_AUDIT"
    report = {
        "schema_version": "1.0",
        "research_contract_id": contract.get("research_contract_id"),
        "contract_version": contract.get("contract_version"),
        "terminal_node_manifest_sha256": contract.get("terminal_node_manifest_sha256"),
        "expected_terminal_node_count": len(node_ids) if isinstance(node_ids, list) else None,
        "indexed_terminal_node_count": len(indexed),
        "content_full_screening_state": state,
        "requires_content_workspace_validation": True,
        "requires_evidence_expansion": True,
        "requires_reverse_audit": True,
        "downstream_release_state": "RESEARCH_ONLY_BLOCKED",
        "reasons": reasons,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS" if state == "READY_FOR_REVERSE_AUDIT" else "FAIL", "content_full_screening_state": state, "output": str(args.output)}, ensure_ascii=False))
    return 0 if state == "READY_FOR_REVERSE_AUDIT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
