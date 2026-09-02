#!/usr/bin/env python3
"""Validate a route-scoped business/application closure receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any


RECEIPT_FIELDS = {
    "contract_version",
    "closure_receipt_id",
    "company_id",
    "route_id",
    "business_industry_id",
    "route_packet_reference",
    "route_packet_sha256",
    "direction_validation_reference",
    "direction_validation_sha256",
    "route_scoped_application_closure_state",
    "global_semantic_stage_effect",
    "customer_discovery_readiness",
    "salesperson_scan_authorization",
    "allowed_next_actions",
    "prohibited_next_actions",
    "validated_at",
}
REQUIRED_PROHIBITIONS = {"scan_candidates", "claim_product_fit", "claim_regulatory_compliance"}
DIRECTION_PACKET_FIELDS = {
    "contract_version",
    "validation_id",
    "company_id",
    "route_id",
    "business_route_closure_id",
    "validation_state",
    "salesperson_scan_authorization",
    "evidence",
}
DIRECTION_EVIDENCE_FIELDS = {
    "evidence_id",
    "evidence_role",
    "source_dependency_group",
    "source_reference",
    "observed_company_id",
}
DIRECTION_EVIDENCE_ROLES = {"application_seed", "direction_holdout", "counterevidence"}


class ClosureFailure(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def bound_json(receipt_path: Path, reference: Any, expected_hash: Any, role: str) -> dict[str, Any]:
    if not isinstance(reference, str) or not reference or "\\" in reference:
        raise ClosureFailure(f"{role}_REFERENCE_INVALID")
    pure = PurePosixPath(reference)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ClosureFailure(f"{role}_REFERENCE_INVALID")
    candidate = receipt_path.parent.joinpath(*pure.parts)
    if candidate.is_symlink():
        raise ClosureFailure(f"{role}_REFERENCE_INVALID")
    try:
        path = candidate.resolve(strict=True)
        path.relative_to(receipt_path.parent.resolve())
        raw = path.read_bytes()
    except (OSError, ValueError) as error:
        raise ClosureFailure(f"{role}_NOT_READABLE") from error
    if not isinstance(expected_hash, str) or sha256(raw) != expected_hash:
        raise ClosureFailure(f"{role}_HASH_MISMATCH")
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ClosureFailure(f"{role}_INVALID") from error
    if not isinstance(document, dict):
        raise ClosureFailure(f"{role}_INVALID")
    return document


def validate_direction(
    document: dict[str, Any], receipt: dict[str, Any], expected_closure_id: str
) -> None:
    if set(document) != {"direction_validation_packet_v1"}:
        raise ClosureFailure("DIRECTION_VALIDATION_INVALID")
    packet = document.get("direction_validation_packet_v1")
    if not isinstance(packet, dict) or set(packet) != DIRECTION_PACKET_FIELDS:
        raise ClosureFailure("DIRECTION_VALIDATION_INVALID")
    if (
        packet.get("contract_version") != "1.0"
        or packet.get("company_id") != receipt["company_id"]
        or packet.get("route_id") != receipt["route_id"]
        or packet.get("business_route_closure_id") != expected_closure_id
        or packet.get("validation_state") != "PASS"
        or packet.get("salesperson_scan_authorization") != "blocked"
    ):
        raise ClosureFailure("DIRECTION_VALIDATION_MISMATCH")
    for field in ("validation_id", "company_id", "route_id", "business_route_closure_id"):
        if not isinstance(packet[field], str) or not packet[field].strip():
            raise ClosureFailure("DIRECTION_VALIDATION_INVALID")
    evidence = packet.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ClosureFailure("DIRECTION_VALIDATION_INVALID")
    evidence_ids: set[str] = set()
    for item in evidence:
        if (
            not isinstance(item, dict)
            or set(item) != DIRECTION_EVIDENCE_FIELDS
            or item.get("evidence_role") not in DIRECTION_EVIDENCE_ROLES
            or any(not isinstance(item.get(field), str) or not item[field].strip() for field in DIRECTION_EVIDENCE_FIELDS)
            or item["evidence_id"] in evidence_ids
        ):
            raise ClosureFailure("DIRECTION_VALIDATION_INVALID")
        evidence_ids.add(item["evidence_id"])
    seeds = [item for item in evidence if isinstance(item, dict) and item.get("evidence_role") == "application_seed"]
    holdouts = [item for item in evidence if isinstance(item, dict) and item.get("evidence_role") == "direction_holdout"]
    if not seeds or not holdouts:
        raise ClosureFailure("DIRECTION_VALIDATION_INDEPENDENCE_MISSING")
    if {item.get("source_dependency_group") for item in seeds} & {item.get("source_dependency_group") for item in holdouts}:
        raise ClosureFailure("DIRECTION_VALIDATION_DEPENDENCY_OVERLAP")
    if {item.get("source_reference") for item in seeds} & {item.get("source_reference") for item in holdouts}:
        raise ClosureFailure("DIRECTION_VALIDATION_SOURCE_OVERLAP")
    if {item.get("observed_company_id") for item in seeds} & {item.get("observed_company_id") for item in holdouts}:
        raise ClosureFailure("DIRECTION_VALIDATION_COMPANY_OVERLAP")


def validate_route(document: dict[str, Any], receipt: dict[str, Any]) -> str:
    packet = document.get("company_route_pool_packet")
    if not isinstance(packet, dict) or packet.get("company_id") != receipt["company_id"]:
        raise ClosureFailure("ROUTE_PACKET_MISMATCH")
    routes = []
    for field in ("route_candidates", "route_leads"):
        value = packet.get(field, [])
        if isinstance(value, list):
            routes.extend(item for item in value if isinstance(item, dict))
    matches = [item for item in routes if item.get("route_candidate_id") == receipt["route_id"]]
    if len(matches) != 1:
        raise ClosureFailure("ROUTE_NOT_UNIQUE")
    route = matches[0]
    if (
        route.get("business_industry_id") != receipt["business_industry_id"]
        or route.get("customer_discovery_readiness") != receipt["customer_discovery_readiness"]
    ):
        raise ClosureFailure("ROUTE_CLOSURE_IDENTITY_MISMATCH")
    closures = packet.get("route_closures")
    if not isinstance(closures, list):
        raise ClosureFailure("ROUTE_CLOSURE_MISSING")
    closure_matches = [
        item for item in closures
        if isinstance(item, dict)
        and item.get("closure_id") == route.get("business_route_closure_id")
        and item.get("route_candidate_id") == receipt["route_id"]
    ]
    if len(closure_matches) != 1 or closure_matches[0].get("review_result") != "PASS":
        raise ClosureFailure("ROUTE_CLOSURE_NOT_ACCEPTED")
    closure_id = route.get("business_route_closure_id")
    if not isinstance(closure_id, str) or not closure_id:
        raise ClosureFailure("ROUTE_CLOSURE_NOT_ACCEPTED")
    return closure_id


def validate(receipt_path: Path) -> dict[str, Any]:
    try:
        document = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ClosureFailure("CLOSURE_RECEIPT_NOT_READABLE") from error
    if not isinstance(document, dict) or set(document) != {"business_route_closure_receipt_v1"}:
        raise ClosureFailure("CLOSURE_RECEIPT_SCHEMA_INVALID")
    receipt = document["business_route_closure_receipt_v1"]
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
        raise ClosureFailure("CLOSURE_RECEIPT_SCHEMA_INVALID")
    if (
        receipt["contract_version"] != "1.0"
        or receipt["route_scoped_application_closure_state"] != "PASS"
        or receipt["global_semantic_stage_effect"] != "none"
        or receipt["salesperson_scan_authorization"] != "blocked"
    ):
        raise ClosureFailure("CLOSURE_RECEIPT_STATE_INVALID")
    if receipt["allowed_next_actions"] != ["present_direction_for_salesperson_scan_decision"]:
        raise ClosureFailure("CLOSURE_NEXT_ACTION_INVALID")
    prohibited = receipt["prohibited_next_actions"]
    if not isinstance(prohibited, list) or not REQUIRED_PROHIBITIONS.issubset(set(prohibited)):
        raise ClosureFailure("CLOSURE_PROHIBITIONS_INCOMPLETE")
    route_document = bound_json(receipt_path, receipt["route_packet_reference"], receipt["route_packet_sha256"], "ROUTE_PACKET")
    direction_document = bound_json(receipt_path, receipt["direction_validation_reference"], receipt["direction_validation_sha256"], "DIRECTION_VALIDATION")
    expected_closure_id = validate_route(route_document, receipt)
    validate_direction(direction_document, receipt, expected_closure_id)
    return {
        "result": "PASS",
        "reason_codes": [],
        "closure_receipt_id": receipt["closure_receipt_id"],
        "company_id": receipt["company_id"],
        "route_id": receipt["route_id"],
        "global_semantic_stage_effect": "none",
        "salesperson_scan_authorization": "blocked",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.receipt.expanduser().resolve())
        code = 0
    except ClosureFailure as failure:
        result = {"result": "FAIL", "reason_codes": [failure.code]}
        code = 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
