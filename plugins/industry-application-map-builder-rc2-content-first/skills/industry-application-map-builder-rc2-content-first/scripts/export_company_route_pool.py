from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys

from validate_industry_application_workspace import validate_workspace
from xlsx_contract import parse_json_list, read_sheet_records


LIST_FIELDS = {
    "taxonomy_node_ids",
    "output_product_ids",
    "product_fact_ids",
    "product_source_ids",
    "application_evidence_ids",
    "application_source_groups",
    "geography_hypotheses",
    "geography_evidence_ids",
    "unresolved_conditions",
    "route_candidate_ids",
    "evidence_ids",
}


def normalize(record: dict[str, str]) -> dict:
    result = dict(record)
    for field in LIST_FIELDS:
        if field in result:
            result[field] = parse_json_list(result[field], field)
    for field in ("known_limit_conflict", "limit_conflict"):
        if field in result:
            result[field] = str(result[field]).lower() == "true"
    return result


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(code: str, message: str) -> int:
    print(f"{code}: {message}", file=sys.stderr)
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("map_root", type=Path)
    parser.add_argument("--company-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    map_root = args.map_root.resolve()
    report = validate_workspace(map_root, args.company_id)
    if report["status"] != "PASS":
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    registry = json.loads(
        (map_root / "00-管理" / "map-registry.json").read_text(encoding="utf-8")
    )
    company = next(
        item for item in registry["companies"] if item["company_id"] == args.company_id
    )
    workbook = map_root / company["company_map_path"]
    company_root = workbook.parent.resolve()
    output = args.output.expanduser().resolve()
    try:
        output.relative_to(company_root)
    except ValueError:
        return fail("ROUTE_PACKET_OUTSIDE_COMPANY_MAP", str(output))
    if output.exists():
        return fail("ROUTE_PACKET_OUTPUT_EXISTS", str(output))
    export_registry_path = company_root / "route-pool-export-registry.json"
    if not export_registry_path.is_file():
        return fail("ROUTE_EXPORT_REGISTRY_MISSING", str(export_registry_path))
    export_registry = json.loads(export_registry_path.read_text(encoding="utf-8"))
    if export_registry.get("company_id") != args.company_id or not isinstance(
        export_registry.get("exports"), list
    ):
        return fail("ROUTE_EXPORT_REGISTRY_INVALID", str(export_registry_path))
    sequence = len(export_registry["exports"]) + 1
    export_id = f"{args.company_id}-EXPORT-{date.today().isoformat()}-{sequence:04d}"
    routes = [normalize(row) for row in read_sheet_records(workbook, "路线候选")]
    dispositions = [normalize(row) for row in read_sheet_records(workbook, "排除暂缓")]
    coverage = [normalize(row) for row in read_sheet_records(workbook, "覆盖台账")]
    input_snapshot = read_sheet_records(workbook, "公司与输入")[0]
    producer_snapshot = {
        "company_map_path": str(workbook.resolve().relative_to(map_root)),
        "company_map_sha256": sha256(workbook),
    }
    packet = {
        "schema_version": "1.0",
        "company_route_pool_packet": {
            "export_id": export_id,
            "company_id": args.company_id,
            "product_scope": company["product_scope"],
            "input_snapshot": input_snapshot,
            "producer_snapshot": producer_snapshot,
            "declared_scope": {
                "taxonomy": company["declared_taxonomy_scope"],
                "application": company["declared_application_scope"],
                "sources": company["allowed_source_scope"],
            },
            "route_candidates": [
                row for row in routes if row.get("map_route_status") in {"路线候选", "待外部核实"}
            ],
            "route_leads": [row for row in routes if row.get("map_route_status") == "路线线索"],
            "deferred_routes": [row for row in routes if row.get("map_route_status") == "暂缓"],
            "excluded_routes": [row for row in routes if row.get("map_route_status") == "排除"] + dispositions,
            "coverage_summary": coverage,
            "prohibited_inference": [
                "Do not treat map routes as approved company product facts.",
                "Do not infer country priority, customer priority, purchasing role, or product adoption.",
                "Do not scan companies until the salesperson records direction_status = 已确认可扫描, except for the named-company initial-check route.",
            ],
            "target_skill": "foreign-trade-customer-development",
            "producer_registry_reference": {
                "map_root": str(map_root),
                "path": str(export_registry_path.relative_to(map_root)),
                "export_id": export_id,
            },
            "exported_at": date.today().isoformat(),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, packet)
    route_ids: list[str] = []
    packet_body = packet["company_route_pool_packet"]
    for key in (
        "route_candidates",
        "route_leads",
        "deferred_routes",
        "excluded_routes",
    ):
        for row in packet_body[key]:
            route_id = row.get("route_candidate_id")
            if route_id and route_id not in route_ids:
                route_ids.append(route_id)
    export_registry["exports"].append(
        {
            "export_id": export_id,
            "company_id": args.company_id,
            "packet_path": str(output.relative_to(map_root)),
            "packet_sha256": sha256(output),
            "input_snapshot": input_snapshot,
            "producer_snapshot": producer_snapshot,
            "route_candidate_ids": route_ids,
            "validator_version": "1.1",
            "validated_at": date.today().isoformat(),
            "state": "current",
            "invalidation_reason": None,
        }
    )
    write_json(export_registry_path, export_registry)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
