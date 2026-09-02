#!/usr/bin/env python3
"""Validate direction evidence independence without authorizing customer scanning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


PACKET_FIELDS = {
    "contract_version",
    "validation_id",
    "company_id",
    "route_id",
    "business_route_closure_id",
    "validation_state",
    "salesperson_scan_authorization",
    "evidence",
}
EVIDENCE_FIELDS = {
    "evidence_id",
    "evidence_role",
    "source_dependency_group",
    "source_reference",
    "observed_company_id",
}
ROLES = {"application_seed", "direction_holdout", "counterevidence"}


def failure(code: str) -> dict[str, Any]:
    return {"result": "FAIL", "reason_codes": [code]}


def validate_document(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict) or set(document) != {"direction_validation_packet_v1"}:
        return failure("DIRECTION_VALIDATION_SCHEMA_INVALID")
    packet = document["direction_validation_packet_v1"]
    if not isinstance(packet, dict) or set(packet) != PACKET_FIELDS:
        return failure("DIRECTION_VALIDATION_SCHEMA_INVALID")
    if packet["contract_version"] != "1.0" or packet["validation_state"] != "PASS":
        return failure("DIRECTION_VALIDATION_STATE_INVALID")
    if packet["salesperson_scan_authorization"] != "blocked":
        return failure("DIRECTION_VALIDATION_EXCEEDS_AUTHORITY")
    for field in ("validation_id", "company_id", "route_id", "business_route_closure_id"):
        if not isinstance(packet[field], str) or not packet[field].strip():
            return failure("DIRECTION_VALIDATION_SCHEMA_INVALID")
    evidence = packet["evidence"]
    if not isinstance(evidence, list) or not evidence:
        return failure("DIRECTION_EVIDENCE_REQUIRED")
    ids: set[str] = set()
    by_role: dict[str, list[dict[str, str]]] = {role: [] for role in ROLES}
    for item in evidence:
        if not isinstance(item, dict) or set(item) != EVIDENCE_FIELDS:
            return failure("DIRECTION_EVIDENCE_SCHEMA_INVALID")
        if item["evidence_role"] not in ROLES:
            return failure("DIRECTION_EVIDENCE_ROLE_INVALID")
        if any(not isinstance(item[field], str) or not item[field].strip() for field in EVIDENCE_FIELDS):
            return failure("DIRECTION_EVIDENCE_SCHEMA_INVALID")
        if item["evidence_id"] in ids:
            return failure("DIRECTION_EVIDENCE_ID_DUPLICATE")
        ids.add(item["evidence_id"])
        by_role[item["evidence_role"]].append(item)
    if not by_role["application_seed"] or not by_role["direction_holdout"]:
        return failure("SEED_AND_HOLDOUT_REQUIRED")
    seed_groups = {item["source_dependency_group"] for item in by_role["application_seed"]}
    holdout_groups = {item["source_dependency_group"] for item in by_role["direction_holdout"]}
    if seed_groups & holdout_groups:
        return failure("SEED_HOLDOUT_DEPENDENCY_OVERLAP")
    seed_refs = {item["source_reference"] for item in by_role["application_seed"]}
    holdout_refs = {item["source_reference"] for item in by_role["direction_holdout"]}
    if seed_refs & holdout_refs:
        return failure("SEED_HOLDOUT_SOURCE_OVERLAP")
    seed_companies = {item["observed_company_id"] for item in by_role["application_seed"]}
    holdout_companies = {item["observed_company_id"] for item in by_role["direction_holdout"]}
    if seed_companies & holdout_companies:
        return failure("SEED_HOLDOUT_COMPANY_OVERLAP")
    return {
        "result": "PASS",
        "reason_codes": [],
        "validation_id": packet["validation_id"],
        "company_id": packet["company_id"],
        "route_id": packet["route_id"],
        "business_route_closure_id": packet["business_route_closure_id"],
        "salesperson_scan_authorization": "blocked",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.packet.read_text(encoding="utf-8"))
        result = validate_document(document)
    except (OSError, UnicodeError, json.JSONDecodeError):
        result = failure("DIRECTION_VALIDATION_NOT_READABLE")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
