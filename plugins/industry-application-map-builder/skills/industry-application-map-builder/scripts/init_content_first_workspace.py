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


def valid_contract(contract: Any) -> bool:
    if not isinstance(contract, dict):
        return False
    policy = contract.get("content_first_policy")
    case_set = contract.get("calibration_case_set_reference_and_hash")
    return (
        contract.get("contract_state") == "frozen"
        and contract.get("execution_mode") == "content_first"
        and nonempty(contract.get("research_contract_id"))
        and nonempty(contract.get("contract_version"))
        and nonempty(contract.get("taxonomy_snapshot_sha256"))
        and type(contract.get("terminal_node_count")) is int
        and contract.get("terminal_node_count") > 0
        and nonempty(contract.get("terminal_node_manifest_reference"))
        and nonempty(contract.get("terminal_node_manifest_sha256"))
        and isinstance(case_set, dict)
        and nonempty(case_set.get("reference"))
        and nonempty(case_set.get("sha256"))
        and nonempty(contract.get("source_truth_package_reference"))
        and nonempty(contract.get("source_truth_package_sha256"))
        and isinstance(policy, dict)
        and policy.get("raw_response_must_be_unchanged") is True
        and policy.get("platform_audit_required_for_content_pass") is False
        and policy.get("downstream_release_state") == "RESEARCH_ONLY_BLOCKED"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an isolated append-only RC2 content-first research workspace."
    )
    parser.add_argument("--map-root", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()
    map_root = args.map_root.resolve()
    if not map_root.is_dir():
        return fail("MAP_ROOT_MISSING", str(map_root))
    try:
        payload = json.loads(args.contract.read_text(encoding="utf-8"))
        contract = payload.get("semantic_research_contract", {}) if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError) as exc:
        return fail("CONTRACT_INVALID", str(exc))
    if not valid_contract(contract):
        return fail("CONTENT_CONTRACT_INCOMPLETE", str(args.contract))
    workspace = (
        map_root
        / "05-工作区"
        / "行业语义研究"
        / str(contract["research_contract_id"])
    )
    if workspace.exists():
        return fail("DESTINATION_EXISTS", str(workspace))
    directories = (
        "00-合同",
        "01-节点快照",
        "02-校准案例",
        "02-来源真值",
        "03-内容原始回答/baseline_full_depth",
        "03-内容原始回答/candidate_screen_then_expand",
        "04-平台审计",
        "05-证据包",
        "06-反向审计",
        "07-报告/content-scorecards",
        "08-隔离失败返回",
    )
    try:
        for relative in directories:
            (workspace / relative).mkdir(parents=True, exist_ok=False)
        (workspace / "00-合同" / "semantic-research-contract.json").write_bytes(
            args.contract.read_bytes()
        )
    except OSError as exc:
        return fail("WORKSPACE_CREATE_FAILED", str(exc))
    print(json.dumps({"status": "PASS", "workspace": str(workspace), "runs_nodes": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
