#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import sys
import tempfile
from typing import Any


PREPARATION_DIRECTORIES = (
    "00-合同准备",
    "01-节点快照",
    "01-术语桥",
    "02-校准案例候选",
    "02-校准案例候选/r3-source-snapshots",
    "03-来源真值准备",
    "07-报告",
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
TERM_TEMPLATE = SKILL_ROOT / "assets/content-first/terminology-bridge.template.jsonl"
R4_BASELINE_METHOD = "baseline_full_depth_v1"
R4_CANDIDATE_METHOD = "screen_then_expand_v2"


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 2


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_research_contract_id(value: Any) -> bool:
    return nonempty(value) and Path(value).name == value and value not in {".", ".."}


def load_contract(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    contract = payload.get("semantic_research_contract") if isinstance(payload, dict) else None
    return contract if isinstance(contract, dict) else None, None


def load_empty_term_pack(contract: dict[str, Any]) -> bytes:
    rows = [
        json.loads(line)
        for line in TERM_TEMPLATE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 1 or rows[0].get("record_type") != "terminology_bridge_contract":
        raise ValueError("terminology bridge template is invalid")
    header = rows[0]
    header["research_contract_id"] = contract["research_contract_id"]
    header["contract_version"] = contract.get("contract_version")
    return (json.dumps(header, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a refusal-safe content-first preparation directory."
    )
    parser.add_argument("--map-root", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()
    map_root = args.map_root.resolve()
    if not map_root.is_dir():
        return fail("MAP_ROOT_MISSING", str(map_root))
    contract, error = load_contract(args.contract)
    if error is not None or contract is None:
        return fail("CONTRACT_INVALID", error or str(args.contract))
    if contract.get("contract_state") != "draft":
        return fail("CONTRACT_STATE_INVALID", str(contract.get("contract_state")))
    if contract.get("execution_mode") != "content_first":
        return fail("EXECUTION_MODE_INVALID", str(contract.get("execution_mode")))
    if (
        contract.get("baseline_method_contract") != R4_BASELINE_METHOD
        or contract.get("candidate_method_contract") != R4_CANDIDATE_METHOD
    ):
        return fail(
            "METHOD_ARMS_INVALID",
            "content-first preparation requires the exact frozen R4 method arms",
        )
    if not valid_research_contract_id(contract.get("research_contract_id")):
        return fail("RESEARCH_CONTRACT_ID_INVALID", str(contract.get("research_contract_id")))
    if not nonempty(contract.get("contract_version")):
        return fail("CONTRACT_VERSION_INVALID", str(contract.get("contract_version")))
    workspace = (
        map_root
        / "05-工作区"
        / "行业语义研究"
        / str(contract["research_contract_id"])
    )
    if workspace.exists():
        return fail("DESTINATION_EXISTS", str(workspace))
    staging_workspace: Path | None = None
    try:
        workspace.parent.mkdir(parents=True, exist_ok=True)
        staging_workspace = Path(
            tempfile.mkdtemp(
                prefix=f".{contract['research_contract_id']}.tmp-",
                dir=workspace.parent,
            )
        )
        for relative in PREPARATION_DIRECTORIES:
            (staging_workspace / relative).mkdir(parents=True, exist_ok=False)
        contract_copy = (
            staging_workspace / "00-合同准备" / "semantic-research-contract.draft.json"
        )
        shutil.copyfile(args.contract, contract_copy)
        contract_copy.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        term_pack = staging_workspace / "01-术语桥" / "terminology-bridge.jsonl"
        term_pack_bytes = load_empty_term_pack(contract)
        term_pack.write_bytes(term_pack_bytes)
        term_pack_sha256 = hashlib.sha256(term_pack_bytes).hexdigest()
        manifest = staging_workspace / "01-术语桥" / "terminology-bridge.manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "research_contract_id": contract["research_contract_id"],
                    "contract_version": contract["contract_version"],
                    "terminology_bridge": term_pack.name,
                    "terminology_bridge_sha256": term_pack_sha256,
                    "term_pack_state": "frozen_empty_cold_start",
                    "accepted_term_count": 0,
                    "company_data_allowed": False,
                },
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        staging_workspace.rename(workspace)
    except (OSError, ValueError) as exc:
        if staging_workspace is not None and staging_workspace.exists():
            shutil.rmtree(staging_workspace)
        return fail("PREPARATION_CREATE_FAILED", str(exc))
    term_pack = workspace / "01-术语桥" / "terminology-bridge.jsonl"
    manifest = workspace / "01-术语桥" / "terminology-bridge.manifest.json"
    print(
        json.dumps(
            {
                "status": "PASS",
                "preparation_workspace": str(workspace),
                "terminology_bridge": str(term_pack),
                "terminology_bridge_sha256": term_pack_sha256,
                "manifest": str(manifest),
                "model_tasks_created": False,
                "r3_source_manifest_required_before_lock": True,
                "r3_source_manifest_created": False,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
