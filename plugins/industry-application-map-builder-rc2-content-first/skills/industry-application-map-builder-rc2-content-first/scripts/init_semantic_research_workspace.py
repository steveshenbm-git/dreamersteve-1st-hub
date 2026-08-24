#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from validate_semantic_research_workspace import frozen_contract_completeness_errors


DIRECTORIES = (
    "00-合同",
    "01-节点快照",
    "02-校准案例",
    "03-运行原始记录/baseline",
    "03-运行原始记录/candidate",
    "04-模型交接",
    "05-证据包",
    "06-反向审计",
    "07-报告",
    "08-隔离失败返回",
)


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 1


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize one isolated RC2 semantic research workspace.")
    parser.add_argument("--map-root", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()

    map_root = args.map_root.resolve()
    contract_source = args.contract.resolve()
    if not map_root.is_dir():
        return fail("MAP_ROOT_MISSING", str(map_root))
    if not contract_source.is_file():
        return fail("CONTRACT_MISSING", str(contract_source))
    try:
        payload = json.loads(contract_source.read_text(encoding="utf-8"))
        contract = payload["semantic_research_contract"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return fail("CONTRACT_INVALID", str(exc))

    contract_id = contract.get("research_contract_id")
    if not isinstance(contract_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", contract_id):
        return fail("CONTRACT_ID_INVALID", repr(contract_id))
    if contract.get("contract_state") != "frozen":
        return fail("CONTRACT_NOT_FROZEN", str(contract.get("contract_state")))
    completeness = frozen_contract_completeness_errors(contract)
    if completeness:
        return fail("CONTRACT_INCOMPLETE", ";".join(completeness))

    destination = map_root / "05-工作区" / "行业语义研究" / contract_id
    if destination.exists():
        return fail("DESTINATION_EXISTS", str(destination))

    for relative in DIRECTORIES:
        (destination / relative).mkdir(parents=True, exist_ok=False)

    contract_bytes = canonical_bytes(payload)
    contract_target = destination / "00-合同" / "semantic-research-contract.json"
    contract_target.write_bytes(contract_bytes)
    manifest = {
        "schema_version": "1.0",
        "research_contract_id": contract_id,
        "contract_version": contract.get("contract_version"),
        "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "append_only_runtime_records": True,
        "allowed_writes": contract.get("allowed_writes", []),
        "shared_application_base_write_authorized": bool(contract.get("application_base_write_authorization")),
    }
    (destination / "00-合同" / "workspace-manifest.json").write_bytes(canonical_bytes(manifest))
    print(json.dumps({"status": "PASS", "workspace": str(destination), "research_contract_id": contract_id}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
