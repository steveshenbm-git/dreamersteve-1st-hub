#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
from typing import Any

from r4_adjudicated_truth_contract import BETA5_TRUTH_SCORECARD_CONTRACT_VERSION

R4_MARKER = BETA5_TRUTH_SCORECARD_CONTRACT_VERSION
R4_ARMS = ("baseline_full_depth_v1", "screen_then_expand_v2")
GATE_ORDER = [
    "safety",
    "accepted_positive_recall",
    "receiver_evidence_completeness",
    "stability",
    "efficiency",
]
REPORT_FIELDS = {
    "schema_version",
    "evaluation_result",
    "content_method_state",
    "gate_order",
    "critical_content_rules_applied_before_efficiency",
    "platform_audit_used_as_content_gate",
    "not_beta3_effectiveness",
    "research_contract_id",
    "contract_version",
    "final_contract_sha256",
    "paired_task_manifest_sha256",
    "case_count",
    "stability_repeat_count",
    "efficiency_gate_state",
    "baseline_query_count",
    "candidate_query_count",
    "baseline_source_open_count",
    "candidate_source_open_count",
    "baseline_deep_expansion_count",
    "candidate_deep_expansion_count",
    "deep_expansion_reduction",
    "minimum_required_reduction",
    "maximum_allowed_query_count_increase",
    "maximum_allowed_source_open_count_increase",
    "safety_failures",
    "downstream_authorized",
    "reasons",
}
MANIFEST_FIELDS = {
    "manifest_type",
    "research_contract_id",
    "schema_version",
    "taxonomy_snapshot_reference",
    "taxonomy_snapshot_sha256",
    "terminal_node_count",
    "terminal_node_ids",
}
RECEIPT_FIELDS = {
    "authorization_receipt_id",
    "research_contract_id",
    "contract_version",
    "user_authorization_reference",
    "authorized_at",
    "final_contract_reference",
    "final_contract_sha256",
    "calibration_report_reference",
    "calibration_report_sha256",
    "terminal_node_manifest_reference",
    "terminal_node_manifest_sha256",
    "authorization_scope",
    "runs_nodes",
    "downstream_release_state",
    "receipt_sha256",
}
NODE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9./:_-]{0,255}$")


class Invalid(ValueError):
    pass


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}), file=sys.stderr)
    return 2


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def nonnegative_int(value: Any) -> bool:
    return type(value) is int and value >= 0


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def aware_time(value: Any) -> bool:
    if not nonempty(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def canonical_workspace_file(workspace: Path, path: Path, expected_hash: Any) -> Path:
    if not is_sha256(expected_hash):
        raise Invalid("expected SHA-256 is malformed")
    try:
        resolved = path.resolve(strict=True)
        reference = resolved.relative_to(workspace.resolve()).as_posix()
    except (OSError, ValueError) as exc:
        raise Invalid("trusted file is outside the workspace or missing") from exc
    pure = PurePosixPath(reference)
    if pure.as_posix() != reference or any(part in {"", ".", ".."} for part in pure.parts):
        raise Invalid("trusted file reference is not canonical")
    current = workspace.resolve()
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise Invalid("trusted file reference uses a symlink")
    if not resolved.is_file() or file_sha256(resolved) != expected_hash:
        raise Invalid("trusted file hash mismatch")
    return resolved


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_contract(payload: Any, contract_hash: str) -> dict[str, Any]:
    contract = (
        payload.get("semantic_research_contract") if isinstance(payload, dict) else None
    )
    policy = contract.get("content_first_policy") if isinstance(contract, dict) else None
    gates = contract.get("retrieval_efficiency_gates") if isinstance(contract, dict) else None
    if (
        not isinstance(payload, dict)
        or set(payload) != {"schema_version", "semantic_research_contract"}
        or not nonempty(payload.get("schema_version"))
        or not isinstance(contract, dict)
        or not nonempty(contract.get("research_contract_id"))
        or not nonempty(contract.get("contract_version"))
        or contract.get("contract_state") != "frozen"
        or contract.get("execution_mode") != "content_first"
        or contract.get("baseline_method_contract") != R4_ARMS[0]
        or contract.get("candidate_method_contract") != R4_ARMS[1]
        or not is_sha256(contract.get("taxonomy_snapshot_sha256"))
        or not nonnegative_int(contract.get("terminal_node_count"))
        or contract.get("terminal_node_count") == 0
        or not nonempty(contract.get("terminal_node_manifest_reference"))
        or not is_sha256(contract.get("terminal_node_manifest_sha256"))
        or contract.get("full_screening_authorization") is not False
        or contract.get("full_screening_authorization_reference") is not None
        or not isinstance(policy, dict)
        or policy.get("truth_scorecard_contract_version") != R4_MARKER
        or policy.get("platform_audit_required_for_content_pass") is not False
        or policy.get("content_full_screening_state") != "NOT_AUTHORIZED"
        or policy.get("downstream_release_state") != "RESEARCH_ONLY_BLOCKED"
        or not isinstance(gates, dict)
        or set(gates)
        != {
            "minimum_deep_expansion_reduction",
            "maximum_query_count_increase",
            "maximum_source_open_count_increase",
            "stability_repeat_case_count",
        }
        or type(gates.get("minimum_deep_expansion_reduction")) not in {int, float}
        or gates.get("minimum_deep_expansion_reduction") != 0.2
        or type(gates.get("maximum_query_count_increase")) not in {int, float}
        or gates.get("maximum_query_count_increase") != 0.1
        or type(gates.get("maximum_source_open_count_increase")) not in {int, float}
        or gates.get("maximum_source_open_count_increase") != 0.0
        or type(gates.get("stability_repeat_case_count")) is not int
        or gates.get("stability_repeat_case_count") != 6
        or not is_sha256(contract_hash)
    ):
        raise Invalid("final frozen R4 contract is invalid")
    return contract


def validate_report(report: Any, contract: dict[str, Any], contract_hash: str) -> None:
    if not isinstance(report, dict) or set(report) != REPORT_FIELDS:
        raise Invalid("R4 evaluator report schema is invalid")
    integer_fields = (
        "baseline_query_count",
        "candidate_query_count",
        "baseline_source_open_count",
        "candidate_source_open_count",
        "baseline_deep_expansion_count",
        "candidate_deep_expansion_count",
    )
    if not all(nonnegative_int(report.get(field)) for field in integer_fields):
        raise Invalid("R4 evaluator resource metrics are invalid")
    bq = report["baseline_query_count"]
    cq = report["candidate_query_count"]
    bo = report["baseline_source_open_count"]
    co = report["candidate_source_open_count"]
    bd = report["baseline_deep_expansion_count"]
    cd = report["candidate_deep_expansion_count"]
    reduction = report.get("deep_expansion_reduction")
    if (
        report.get("schema_version") != R4_MARKER
        or report.get("evaluation_result") != "PASS"
        or report.get("content_method_state") != "CONTENT_CALIBRATION_PASS"
        or report.get("gate_order") != GATE_ORDER
        or report.get("critical_content_rules_applied_before_efficiency") is not True
        or report.get("platform_audit_used_as_content_gate") is not False
        or report.get("not_beta3_effectiveness") is not True
        or report.get("research_contract_id") != contract["research_contract_id"]
        or report.get("contract_version") != contract["contract_version"]
        or report.get("final_contract_sha256") != contract_hash
        or not is_sha256(report.get("paired_task_manifest_sha256"))
        or type(report.get("case_count")) is not int
        or report.get("case_count") != 40
        or type(report.get("stability_repeat_count")) is not int
        or report.get("stability_repeat_count") != 6
        or report.get("efficiency_gate_state") != "PASS"
        or bd != 40
        or bd == 0
        or cd * 5 > bd * 4
        or cq * 10 > bq * 11
        or co > bo
        or type(reduction) not in {int, float}
        or reduction != (bd - cd) / bd
        or type(report.get("minimum_required_reduction")) not in {int, float}
        or report.get("minimum_required_reduction") != 0.2
        or type(report.get("maximum_allowed_query_count_increase")) not in {int, float}
        or report.get("maximum_allowed_query_count_increase") != 0.1
        or type(report.get("maximum_allowed_source_open_count_increase")) not in {int, float}
        or report.get("maximum_allowed_source_open_count_increase") != 0.0
        or report.get("safety_failures") != []
        or report.get("downstream_authorized") is not False
        or report.get("reasons") != []
    ):
        raise Invalid("R4 evaluator report is not a closed PASS result")


def validate_manifest(
    manifest: Any,
    contract: dict[str, Any],
    manifest_reference: str,
    manifest_hash: str,
) -> list[str]:
    node_ids = manifest.get("terminal_node_ids") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or set(manifest) != MANIFEST_FIELDS
        or manifest.get("manifest_type") != "content_first_terminal_node_manifest"
        or manifest.get("schema_version") != "1.0"
        or manifest.get("research_contract_id") != contract["research_contract_id"]
        or manifest.get("taxonomy_snapshot_sha256")
        != contract["taxonomy_snapshot_sha256"]
        or not nonempty(manifest.get("taxonomy_snapshot_reference"))
        or type(manifest.get("terminal_node_count")) is not int
        or manifest.get("terminal_node_count") != contract["terminal_node_count"]
        or not isinstance(node_ids, list)
        or len(node_ids) != contract["terminal_node_count"]
        or not node_ids
        or not all(nonempty(node_id) and NODE_ID.fullmatch(node_id) for node_id in node_ids)
        or len(set(node_ids)) != len(node_ids)
        or contract.get("terminal_node_manifest_reference") != manifest_reference
        or contract.get("terminal_node_manifest_sha256") != manifest_hash
    ):
        raise Invalid("frozen terminal-node manifest is invalid or mismatched")
    return node_ids


def validate_receipt(
    payload: Any,
    contract: dict[str, Any],
    *,
    contract_reference: str,
    contract_hash: str,
    report_reference: str,
    report_hash: str,
    manifest_reference: str,
    manifest_hash: str,
) -> dict[str, Any]:
    receipt = (
        payload.get("content_first_full_screening_authorization_receipt")
        if isinstance(payload, dict)
        else None
    )
    if (
        not isinstance(payload, dict)
        or set(payload)
        != {"schema_version", "content_first_full_screening_authorization_receipt"}
        or payload.get("schema_version") != "1.0"
        or not isinstance(receipt, dict)
        or set(receipt) != RECEIPT_FIELDS
        or not nonempty(receipt.get("authorization_receipt_id"))
        or receipt.get("research_contract_id") != contract["research_contract_id"]
        or receipt.get("contract_version") != contract["contract_version"]
        or not nonempty(receipt.get("user_authorization_reference"))
        or not aware_time(receipt.get("authorized_at"))
        or receipt.get("final_contract_reference") != contract_reference
        or receipt.get("final_contract_sha256") != contract_hash
        or receipt.get("calibration_report_reference") != report_reference
        or receipt.get("calibration_report_sha256") != report_hash
        or receipt.get("terminal_node_manifest_reference") != manifest_reference
        or receipt.get("terminal_node_manifest_sha256") != manifest_hash
        or receipt.get("authorization_scope")
        != "content_first_full_screening_research_only"
        or receipt.get("runs_nodes") is not False
        or receipt.get("downstream_release_state") != "RESEARCH_ONLY_BLOCKED"
        or not is_sha256(receipt.get("receipt_sha256"))
        or receipt.get("receipt_sha256")
        != canonical_sha256({**receipt, "receipt_sha256": None})
    ):
        raise Invalid("full-screen authorization receipt is invalid or misbound")
    return receipt


def atomic_publish(path: Path, report: dict[str, Any], inject_failure: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(report, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if inject_failure:
            raise OSError("injected failure before publication")
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the immutable R4 full-screen authorization chain without running nodes."
    )
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--expected-final-contract-sha256", required=True)
    parser.add_argument("--calibration-report", required=True, type=Path)
    parser.add_argument("--expected-calibration-report-sha256", required=True)
    parser.add_argument("--terminal-node-manifest", required=True, type=Path)
    parser.add_argument("--expected-terminal-node-manifest-sha256", required=True)
    parser.add_argument("--authorization-receipt", required=True, type=Path)
    parser.add_argument("--expected-authorization-receipt-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--test-fail-before-publish", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.output.exists():
        return fail("OUTPUT_EXISTS", str(args.output))

    workspace = args.workspace.resolve()
    state = "BLOCKED"
    reasons: list[str] = []
    contract: dict[str, Any] = {}
    receipt: dict[str, Any] = {}
    node_count: int | None = None
    try:
        if not workspace.is_dir():
            raise Invalid("trusted workspace is missing")
        contract_path = canonical_workspace_file(
            workspace, args.contract, args.expected_final_contract_sha256
        )
        report_path = canonical_workspace_file(
            workspace, args.calibration_report, args.expected_calibration_report_sha256
        )
        manifest_path = canonical_workspace_file(
            workspace,
            args.terminal_node_manifest,
            args.expected_terminal_node_manifest_sha256,
        )
        contract = validate_contract(
            load_json(contract_path), args.expected_final_contract_sha256
        )
        validate_report(
            load_json(report_path), contract, args.expected_final_contract_sha256
        )
        manifest_reference = manifest_path.relative_to(workspace).as_posix()
        node_ids = validate_manifest(
            load_json(manifest_path),
            contract,
            manifest_reference,
            args.expected_terminal_node_manifest_sha256,
        )
        node_count = len(node_ids)
        try:
            receipt_path = canonical_workspace_file(
                workspace,
                args.authorization_receipt,
                args.expected_authorization_receipt_sha256,
            )
            receipt = validate_receipt(
                load_json(receipt_path),
                contract,
                contract_reference=contract_path.relative_to(workspace).as_posix(),
                contract_hash=args.expected_final_contract_sha256,
                report_reference=report_path.relative_to(workspace).as_posix(),
                report_hash=args.expected_calibration_report_sha256,
                manifest_reference=manifest_reference,
                manifest_hash=args.expected_terminal_node_manifest_sha256,
            )
        except (Invalid, OSError, ValueError, TypeError, KeyError) as exc:
            state = "NOT_AUTHORIZED"
            reasons = [str(exc) or "full-screen authorization receipt is missing"]
        else:
            state = "AUTHORIZED_NOT_STARTED"
    except (Invalid, OSError, ValueError, TypeError, KeyError) as exc:
        state = "BLOCKED"
        reasons = [str(exc) or "R4 full-screen evidence chain is invalid"]

    output = {
        "schema_version": R4_MARKER,
        "research_contract_id": contract.get("research_contract_id"),
        "contract_version": contract.get("contract_version"),
        "final_contract_sha256": (
            args.expected_final_contract_sha256 if contract else None
        ),
        "calibration_report_sha256": (
            args.expected_calibration_report_sha256 if contract else None
        ),
        "terminal_node_manifest_sha256": contract.get(
            "terminal_node_manifest_sha256"
        ),
        "terminal_node_count": node_count,
        "content_full_screening_state": state,
        "authorization_reference": receipt.get("user_authorization_reference"),
        "authorization_receipt_sha256": (
            args.expected_authorization_receipt_sha256 if receipt else None
        ),
        "runs_nodes": False,
        "downstream_release_state": "RESEARCH_ONLY_BLOCKED",
        "reasons": reasons,
    }
    try:
        atomic_publish(args.output, output, args.test_fail_before_publish)
    except FileExistsError:
        return fail("OUTPUT_EXISTS", str(args.output))
    except OSError as exc:
        return fail("OUTPUT_PUBLICATION_FAILED", str(exc))
    print(
        json.dumps(
            {
                "status": "PASS" if state == "AUTHORIZED_NOT_STARTED" else "FAIL",
                "content_full_screening_state": state,
                "output": str(args.output),
                "runs_nodes": False,
            }
        )
    )
    return 0 if state == "AUTHORIZED_NOT_STARTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
