#!/usr/bin/env python3
"""Generate an on-demand, read-only commercial readiness view."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from validate_company_library import validate


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(code: str, message: str) -> int:
    print(
        json.dumps({"status": "FAIL", "code": code, "message": message}, ensure_ascii=False),
        file=sys.stderr,
    )
    return 2


def scope_applies(fact: dict[str, Any], request: dict[str, Any]) -> bool:
    pairs = (
        ("geographic_scope", "geography_scope"),
        ("customer_type_scope", "customer_type_scope"),
        ("application_scope", "intended_use_scope"),
    )
    for fact_key, request_key in pairs:
        fact_values = fact.get(fact_key, [])
        request_values = request.get(request_key, [])
        if fact_values and request_values and not set(fact_values).intersection(request_values):
            return False
    return True


def stale_state(fact: dict[str, Any], requested_at: date) -> str:
    boundary = fact.get("valid_until") or fact.get("review_due")
    if not boundary:
        return "无法判断"
    try:
        return "已过期" if date.fromisoformat(boundary) < requested_at else "当前"
    except (TypeError, ValueError):
        return "无法判断"


def condition_satisfied(fact_value: dict[str, Any], declared: dict[str, Any]) -> bool | None:
    operator = fact_value.get("operator")
    expected = fact_value.get("value")
    actual = declared.get("value")
    expected_unit = fact_value.get("unit")
    actual_unit = declared.get("unit")
    if (expected_unit or actual_unit) and expected_unit != actual_unit:
        return None
    if operator == "minimum":
        if (
            not isinstance(expected, (int, float))
            or isinstance(expected, bool)
            or not isinstance(actual, (int, float))
            or isinstance(actual, bool)
        ):
            return None
        return actual >= expected
    if operator == "maximum":
        if (
            not isinstance(expected, (int, float))
            or isinstance(expected, bool)
            or not isinstance(actual, (int, float))
            or isinstance(actual, bool)
        ):
            return None
        return actual <= expected
    if operator == "equals":
        return actual == expected
    if operator == "one_of":
        return actual in expected if isinstance(expected, list) else None
    if operator == "not_one_of":
        return actual not in expected if isinstance(expected, list) else None
    if operator == "required_boolean":
        if not isinstance(actual, bool) or not isinstance(expected, bool):
            return None
        return actual is expected
    return None


def compact_item(fact: dict[str, Any], stale: str) -> dict[str, Any]:
    return {
        "fact_id": fact["fact_id"],
        "dimension": fact["fact_value"].get("dimension"),
        "condition": fact["fact_value"],
        "source_id": fact["source_id"],
        "reviewed_at": fact.get("reviewed_at"),
        "valid_until": fact.get("valid_until"),
        "review_due": fact.get("review_due"),
        "stale_status": stale,
        "sensitivity": fact.get("sensitivity", "commercial_internal"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--include-e2-annex", action="store_true")
    args = parser.parse_args()

    library = args.library.expanduser().resolve()
    report = validate(library)
    if report["status"] != "PASS":
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    company = read_json(library / "company.json")
    request_payload = read_json(args.request.expanduser().resolve())
    request = request_payload.get("development_readiness_request")
    if not isinstance(request, dict):
        return fail("INVALID_READINESS_REQUEST", "development_readiness_request is required")
    if request.get("company_id") != company.get("company_id"):
        return fail("CROSS_COMPANY_READINESS_REQUEST", str(request.get("company_id")))
    dimensions = request.get("requested_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        return fail("READINESS_DIMENSIONS_REQUIRED", "requested_dimensions must be non-empty")
    try:
        requested_at = date.fromisoformat(request["requested_at"])
    except (KeyError, TypeError, ValueError):
        return fail("READINESS_REQUEST_DATE_INVALID", str(request.get("requested_at")))

    facts_path = library / "02-事实库" / "facts.json"
    product_path = library / "03-产品体系" / "product-system.json"
    source_registry_path = library / "00-管理" / "源文件清单.json"
    facts = read_json(facts_path).get("facts", [])
    declared = {
        item.get("dimension"): item
        for item in request.get("declared_conditions", [])
        if isinstance(item, dict) and item.get("dimension")
    }
    confirmed_items: list[dict[str, Any]] = []
    annex: list[dict[str, Any]] = []
    stale_items: list[dict[str, Any]] = []
    current_by_dimension: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}

    for fact in facts:
        if not isinstance(fact, dict) or fact.get("fact_type") != "commercial_condition":
            continue
        if fact.get("product_family") != request.get("product_scope"):
            continue
        if not scope_applies(fact, request):
            continue
        value = fact.get("fact_value")
        dimension = value.get("dimension") if isinstance(value, dict) else None
        if dimension not in dimensions:
            continue
        stale = stale_state(fact, requested_at)
        item = compact_item(fact, stale)
        if fact.get("evidence_level") == "E2":
            if args.include_e2_annex:
                annex.append(item)
            continue
        if not (
            fact.get("evidence_level") == "E3"
            and fact.get("review_status") == "approved"
            and fact.get("subject_scope") == "own_company"
            and fact.get("statement_kind") == "source_fact"
        ):
            continue
        confirmed_items.append(item)
        if stale != "当前":
            stale_items.append(item)
            continue
        current_by_dimension.setdefault(dimension, []).append((fact, item))

    missing_dimensions: list[str] = []
    conflicting_items: list[dict[str, Any]] = []
    conditional_items: list[dict[str, Any]] = []
    for dimension in dimensions:
        current = current_by_dimension.get(dimension, [])
        if not current:
            missing_dimensions.append(dimension)
            continue
        declared_item = declared.get(dimension)
        if not declared_item:
            conditional_items.extend(item for _, item in current)
            continue
        for fact, item in current:
            result = condition_satisfied(fact["fact_value"], declared_item)
            if result is False:
                conflicting_items.append(item)
            elif result is None:
                conditional_items.append(item)

    if conflicting_items:
        readiness_state = "已确认冲突"
    elif conditional_items:
        readiness_state = "有条件"
    elif missing_dimensions or stale_items:
        readiness_state = "未知"
    else:
        readiness_state = "可承接"

    view = {
        "schema_version": "1.0",
        "development_readiness_view": {
            "request_id": request.get("request_id"),
            "company_id": company["company_id"],
            "product_scope": request.get("product_scope"),
            "route_candidate_id": request.get("route_candidate_id"),
            "request_context": {
                key: request.get(key, [])
                for key in (
                    "intended_use_scope",
                    "geography_scope",
                    "customer_type_scope",
                    "requested_dimensions",
                    "declared_conditions",
                )
            },
            "knowledge_snapshot": {
                "facts_sha256": sha256(facts_path),
                "product_system_sha256": sha256(product_path),
                "source_registry_sha256": sha256(source_registry_path),
            },
            "confirmed_items": sorted(confirmed_items, key=lambda item: item["fact_id"]),
            "internal_reference_annex": sorted(annex, key=lambda item: item["fact_id"]),
            "stale_items": sorted(stale_items, key=lambda item: item["fact_id"]),
            "missing_dimensions": sorted(missing_dimensions),
            "conflicting_items": sorted(conflicting_items, key=lambda item: item["fact_id"]),
            "conditional_items": sorted(conditional_items, key=lambda item: item["fact_id"]),
            "readiness_state": readiness_state,
            "status_basis": "Only current approved E3 own-company commercial facts affect readiness_state.",
            "prohibited_inference": [
                "未知 does not mean blocked or commercially unsuitable.",
                "E2 annex items are internal references and never determine readiness_state.",
                "This view does not change map_route_status, select a market, rank a route, or authorize customer scanning.",
            ],
            "generated_at": date.today().isoformat(),
            "next_owner": request.get("return_to", {}).get(
                "skill", "foreign-trade-customer-development"
            ),
            "decision_owner": "salesperson",
        },
    }
    rendered = json.dumps(view, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(output)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
