#!/usr/bin/env python3
"""Export one deterministic E3 product-fact packet for industry mapping."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from validate_company_library import validate


FACT_FIELD = {
    "form": "confirmed_form",
    "parameter": "confirmed_parameters",
    "property": "confirmed_properties",
    "mechanism": "confirmed_mechanisms",
    "function": "confirmed_functions",
    "effect": "confirmed_effects",
    "application": "confirmed_applications",
    "required_condition": "required_conditions",
    "known_limit": "known_limits",
}


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


def find_product_node(nodes: list[Any], product_family_id: str) -> dict[str, Any] | None:
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if node.get("product_family_id") == product_family_id:
            return node
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("--product-family-id", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    library = args.library.expanduser().resolve()
    report = validate(library)
    if report["status"] != "PASS":
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    company = read_json(library / "company.json")
    facts_path = library / "02-事实库" / "facts.json"
    product_path = library / "03-产品体系" / "product-system.json"
    source_registry_path = library / "00-管理" / "源文件清单.json"
    facts_payload = read_json(facts_path)
    product_payload = read_json(product_path)
    node = find_product_node(
        product_payload.get("product_families", []),
        args.product_family_id,
    )
    if node is None:
        return fail("PRODUCT_FAMILY_NOT_FOUND", args.product_family_id)

    facts = {
        fact["fact_id"]: fact
        for fact in facts_payload.get("facts", [])
        if isinstance(fact, dict) and isinstance(fact.get("fact_id"), str)
    }
    fields: dict[str, list[str]] = {field: [] for field in FACT_FIELD.values()}
    source_ids: set[str] = set()
    for fact_id in node.get("fact_ids", []):
        fact = facts.get(fact_id)
        if not fact:
            continue
        if not (
            fact.get("evidence_level") == "E3"
            and fact.get("review_status") == "approved"
            and fact.get("subject_scope") == "own_company"
            and fact.get("statement_kind") == "source_fact"
        ):
            continue
        field = FACT_FIELD.get(fact.get("fact_type"))
        if field:
            fields[field].append(fact_id)
            source_ids.add(fact["source_id"])

    packet = {
        "schema_version": "1.2",
        "product_development_fact_packet": {
            "company_id": company["company_id"],
            "product_family_id": args.product_family_id,
            "product_family": node.get("name"),
            "product_series_or_model": None,
            **{key: sorted(value) for key, value in fields.items()},
            "unresolved_conditions": list(node.get("unresolved_structure", [])),
            "approved_references": sorted(source_ids),
            "knowledge_snapshot": {
                "facts_sha256": sha256(facts_path),
                "product_system_sha256": sha256(product_path),
                "source_registry_sha256": sha256(source_registry_path),
            },
            "allowed_use": ["internal_industry_application_mapping"],
            "prohibited_inference": [
                "Do not infer price, inventory, MOQ, lead time, certificates, regulations, HS/customs, production capacity, or customer cases.",
                "This packet itself contains no industry routes; downstream route hypotheses must remain separate from company facts.",
                "Do not emit country priorities, customer candidates, customer selection, or outreach content.",
            ],
            "generated_at": date.today().isoformat(),
            "generator_version": "1.0",
        },
    }
    output = (
        args.output.expanduser().resolve()
        if args.output
        else library / "04-开发交接" / "product-development-fact-packet.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
