#!/usr/bin/env python3
"""Verify a route-pool packet against its trusted producer registry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BASE_SNAPSHOT_FIELDS = (
    ("facts_path", "facts_sha256"),
    ("shared_taxonomy_path", "taxonomy_sha256"),
    ("shared_application_base_path", "application_base_sha256"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def diagnostic(code: str, message: str, path: Path | None = None) -> dict[str, str]:
    item = {"code": code, "message": message}
    if path is not None:
        item["path"] = str(path)
    return item


def within(root: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative:
        return None
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def verify(
    packet_path: Path,
    map_root: Path,
    company_id: str,
    route_candidate_id: str | None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    packet_path = packet_path.expanduser().resolve()
    map_root = map_root.expanduser().resolve()
    try:
        packet_path.relative_to(map_root)
    except ValueError:
        errors.append(
            diagnostic("ROUTE_PACKET_OUTSIDE_MAP_ROOT", company_id, packet_path)
        )
    if not packet_path.is_file():
        errors.append(diagnostic("ROUTE_PACKET_MISSING", company_id, packet_path))
        return {"status": "FAIL", "errors": errors}
    try:
        payload = read_json(packet_path)
    except Exception as exc:
        errors.append(diagnostic("ROUTE_PACKET_INVALID", str(exc), packet_path))
        return {"status": "FAIL", "errors": errors}
    packet = payload.get("company_route_pool_packet")
    if not isinstance(packet, dict):
        errors.append(
            diagnostic(
                "ROUTE_PACKET_CONTRACT_INVALID",
                "company_route_pool_packet is required",
                packet_path,
            )
        )
        return {"status": "FAIL", "errors": errors}
    if packet.get("company_id") != company_id:
        errors.append(diagnostic("CROSS_COMPANY_ROUTE_PACKET", company_id, packet_path))
    if packet.get("target_skill") != "foreign-trade-customer-development":
        errors.append(
            diagnostic("ROUTE_PACKET_TARGET_MISMATCH", company_id, packet_path)
        )

    reference = packet.get("producer_registry_reference")
    if not isinstance(reference, dict):
        errors.append(
            diagnostic("PRODUCER_REGISTRY_REFERENCE_INVALID", company_id, packet_path)
        )
        return {"status": "FAIL", "errors": errors}
    try:
        referenced_root = Path(reference.get("map_root", "")).expanduser().resolve()
    except (TypeError, ValueError):
        referenced_root = Path()
    if referenced_root != map_root:
        errors.append(diagnostic("PRODUCER_MAP_ROOT_MISMATCH", company_id, packet_path))
    registry_path = within(map_root, reference.get("path"))
    if registry_path is None:
        errors.append(
            diagnostic("PRODUCER_REGISTRY_PATH_INVALID", company_id, packet_path)
        )
        return {"status": "FAIL", "errors": errors}
    if not registry_path.is_file():
        errors.append(
            diagnostic("ROUTE_EXPORT_REGISTRY_MISSING", company_id, registry_path)
        )
        return {"status": "FAIL", "errors": errors}
    try:
        registry = read_json(registry_path)
    except Exception as exc:
        errors.append(
            diagnostic("ROUTE_EXPORT_REGISTRY_INVALID", str(exc), registry_path)
        )
        return {"status": "FAIL", "errors": errors}
    if registry.get("company_id") != company_id or not isinstance(
        registry.get("exports"), list
    ):
        errors.append(
            diagnostic("ROUTE_EXPORT_REGISTRY_INVALID", company_id, registry_path)
        )
        return {"status": "FAIL", "errors": errors}

    export_id = packet.get("export_id")
    if not isinstance(export_id, str) or reference.get("export_id") != export_id:
        errors.append(diagnostic("ROUTE_EXPORT_ID_MISMATCH", str(export_id), packet_path))
        return {"status": "FAIL", "errors": errors}
    records = [
        item
        for item in registry["exports"]
        if isinstance(item, dict) and item.get("export_id") == export_id
    ]
    if len(records) != 1:
        errors.append(
            diagnostic("ROUTE_EXPORT_RECORD_NOT_UNIQUE", export_id, registry_path)
        )
        return {"status": "FAIL", "errors": errors}
    record = records[0]
    if record.get("company_id") != company_id:
        errors.append(diagnostic("CROSS_COMPANY_ROUTE_EXPORT", export_id, registry_path))
    if record.get("state") != "current":
        errors.append(
            diagnostic("ROUTE_EXPORT_NOT_CURRENT", str(record.get("state")), registry_path)
        )
    if record.get("validator_version") not in {"1.1", "1.2"}:
        errors.append(
            diagnostic(
                "ROUTE_EXPORT_VALIDATOR_VERSION_UNSUPPORTED",
                str(record.get("validator_version")),
                registry_path,
            )
        )
    registered_packet = within(map_root, record.get("packet_path"))
    if registered_packet is None or registered_packet != packet_path:
        errors.append(
            diagnostic("ROUTE_PACKET_PATH_MISMATCH", export_id, packet_path)
        )
    packet_hash = sha256(packet_path)
    if record.get("packet_sha256") != packet_hash:
        errors.append(diagnostic("ROUTE_PACKET_HASH_MISMATCH", export_id, packet_path))
    snapshot = packet.get("input_snapshot")
    if not isinstance(snapshot, dict) or snapshot != record.get("input_snapshot"):
        errors.append(diagnostic("ROUTE_INPUT_SNAPSHOT_MISMATCH", export_id, packet_path))
        snapshot = snapshot if isinstance(snapshot, dict) else {}
    if snapshot.get("company_id") != company_id:
        errors.append(diagnostic("CROSS_COMPANY_INPUT_SNAPSHOT", company_id, packet_path))
    product_input_mode = snapshot.get("product_input_mode") or "single_packet_legacy"
    if product_input_mode == "single_packet_legacy":
        snapshot_fields = (("product_packet_path", "product_packet_sha256"),) + BASE_SNAPSHOT_FIELDS
    elif product_input_mode == "multi_packet_manifest_v1":
        snapshot_fields = (
            ("product_packet_manifest_path", "product_packet_manifest_sha256"),
        ) + BASE_SNAPSHOT_FIELDS
        product_scopes = packet.get("product_scopes")
        if (
            not isinstance(product_scopes, list)
            or not product_scopes
            or any(not isinstance(item, str) or not item for item in product_scopes)
            or len(product_scopes) != len(set(product_scopes))
        ):
            errors.append(diagnostic("ROUTE_PACKET_PRODUCT_SCOPES_INVALID", export_id, packet_path))
    else:
        snapshot_fields = BASE_SNAPSHOT_FIELDS
        errors.append(diagnostic("PRODUCT_INPUT_MODE_UNSUPPORTED", str(product_input_mode), packet_path))
    for path_field, hash_field in snapshot_fields:
        source_value = snapshot.get(path_field)
        expected_hash = snapshot.get(hash_field)
        if not isinstance(source_value, str) or not source_value:
            errors.append(
                diagnostic("INPUT_SNAPSHOT_PATH_MISSING", path_field, packet_path)
            )
            continue
        source_path = Path(source_value).expanduser().resolve()
        if not source_path.is_file():
            errors.append(
                diagnostic("INPUT_SNAPSHOT_FILE_MISSING", path_field, source_path)
            )
        elif not isinstance(expected_hash, str) or sha256(source_path) != expected_hash:
            errors.append(
                diagnostic("INPUT_SNAPSHOT_HASH_MISMATCH", path_field, source_path)
            )

    producer_snapshot = packet.get("producer_snapshot")
    if not isinstance(producer_snapshot, dict) or producer_snapshot != record.get(
        "producer_snapshot"
    ):
        errors.append(
            diagnostic("ROUTE_EXPORT_PRODUCER_SNAPSHOT_MISMATCH", export_id, packet_path)
        )
    else:
        company_map_path = within(map_root, producer_snapshot.get("company_map_path"))
        expected_company_map = (
            registry_path.parent / "company-industry-application-map.xlsx"
        ).resolve()
        if company_map_path is not None and company_map_path != expected_company_map:
            errors.append(
                diagnostic(
                    "ROUTE_EXPORT_SOURCE_MAP_PATH_MISMATCH",
                    export_id,
                    company_map_path,
                )
            )
        elif company_map_path is None or not company_map_path.is_file():
            errors.append(
                diagnostic("ROUTE_EXPORT_SOURCE_MAP_MISSING", export_id, packet_path)
            )
        elif producer_snapshot.get("company_map_sha256") != sha256(company_map_path):
            errors.append(
                diagnostic(
                    "ROUTE_EXPORT_SOURCE_MAP_STALE",
                    export_id,
                    company_map_path,
                )
            )

    selected_route = None
    selected_route_mode = None
    allowed_downstream_actions: list[str] = []
    prohibited_claims: list[str] = []
    if route_candidate_id:
        route_candidates = packet.get("route_candidates")
        if not isinstance(route_candidates, list):
            route_candidates = []
        route_leads = packet.get("route_leads")
        if not isinstance(route_leads, list):
            route_leads = []
        candidate_matches = [
            route
            for route in route_candidates
            if isinstance(route, dict)
            and route.get("route_candidate_id") == route_candidate_id
        ]
        lead_matches = [
            route
            for route in route_leads
            if isinstance(route, dict)
            and route.get("route_candidate_id") == route_candidate_id
        ]
        if len(candidate_matches) == 1 and not lead_matches and candidate_matches[0].get("map_route_status") == "路线候选":
            selected_route = candidate_matches[0]
            selected_route_mode = "full_direction_compilation"
            allowed_downstream_actions = ["compile_direction"]
            prohibited_claims = ["scan_candidates_without_salesperson_decision"]
        elif len(lead_matches) == 1 and not candidate_matches:
            lead = lead_matches[0]
            if lead.get("customer_discovery_readiness") != "ready_for_limited_direction_validation":
                errors.append(diagnostic("SELECTED_ROUTE_NOT_ELIGIBLE", route_candidate_id, packet_path))
            elif (
                lead.get("technical_match_state") in {"violated", "conflicted"}
                or lead.get("regulatory_qualification_state") in {"violated", "conflicted"}
                or bool(lead.get("known_limit_conflict"))
            ):
                errors.append(diagnostic("LIMITED_ROUTE_QUALIFICATION_BLOCKED", route_candidate_id, packet_path))
            elif lead.get("evidence_state") != "supported":
                errors.append(diagnostic("LIMITED_ROUTE_APPLICATION_EVIDENCE_INSUFFICIENT", route_candidate_id, packet_path))
            else:
                closures = packet.get("route_closures")
                if not isinstance(closures, list):
                    closures = []
                closure_matches = [
                    item for item in closures
                    if isinstance(item, dict)
                    and item.get("closure_id") == lead.get("business_route_closure_id")
                    and item.get("route_candidate_id") == route_candidate_id
                ]
                if len(closure_matches) != 1 or closure_matches[0].get("review_result") != "PASS":
                    errors.append(diagnostic("LIMITED_ROUTE_CLOSURE_NOT_ACCEPTED", route_candidate_id, packet_path))
                else:
                    closure = closure_matches[0]
                    actions = closure.get("allowed_downstream_actions")
                    prohibitions = closure.get("prohibited_downstream_actions")
                    if not isinstance(actions, list) or "compile_and_validate_direction" not in actions:
                        errors.append(diagnostic("LIMITED_ROUTE_ACTION_NOT_ALLOWED", route_candidate_id, packet_path))
                    elif not isinstance(prohibitions, list) or not {
                        "recommend_product",
                        "claim_product_fit",
                        "claim_regulatory_compliance",
                        "scan_candidates",
                    }.issubset(set(prohibitions)):
                        errors.append(diagnostic("LIMITED_ROUTE_PROHIBITIONS_INCOMPLETE", route_candidate_id, packet_path))
                    else:
                        selected_route = lead
                        selected_route_mode = "limited_direction_validation"
                        allowed_downstream_actions = list(actions)
                        prohibited_claims = list(prohibitions)
        else:
            errors.append(
                diagnostic("SELECTED_ROUTE_NOT_ELIGIBLE", route_candidate_id, packet_path)
            )
        if selected_route is not None:
            if selected_route.get("company_id") != company_id:
                errors.append(
                    diagnostic("CROSS_COMPANY_SELECTED_ROUTE", route_candidate_id, packet_path)
                )
            route_ids = record.get("route_candidate_ids")
            if not isinstance(route_ids, list) or route_candidate_id not in route_ids:
                errors.append(
                    diagnostic(
                        "SELECTED_ROUTE_NOT_IN_PRODUCER_RECORD",
                        route_candidate_id,
                        registry_path,
                    )
                )

    if errors:
        return {"status": "FAIL", "errors": errors}
    return {
        "status": "PASS",
        "company_id": company_id,
        "export_id": export_id,
        "route_packet_reference": str(packet_path),
        "route_packet_sha256": packet_hash,
        "producer_registry_reference": str(registry_path),
        "input_snapshot": snapshot,
        "producer_snapshot": producer_snapshot,
        "selected_route": selected_route,
        "selected_route_mode": selected_route_mode,
        "allowed_downstream_actions": allowed_downstream_actions,
        "prohibited_claims": prohibited_claims,
        "salesperson_scan_authorization": "blocked",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--map-root", type=Path, required=True)
    parser.add_argument("--company-id", required=True)
    parser.add_argument("--route-id")
    parser.add_argument("--route-candidate-id")
    args = parser.parse_args()
    if (
        args.route_id
        and args.route_candidate_id
        and args.route_id != args.route_candidate_id
    ):
        parser.error("--route-id and --route-candidate-id must identify the same route")
    report = verify(
        args.packet,
        args.map_root,
        args.company_id,
        args.route_id or args.route_candidate_id,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
