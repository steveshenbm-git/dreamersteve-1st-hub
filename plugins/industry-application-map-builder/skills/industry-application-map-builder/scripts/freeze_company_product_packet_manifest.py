#!/usr/bin/env python3
"""Freeze multiple product fact packets into one company-scoped input manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


class ManifestFailure(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ManifestFailure("INPUT_NOT_READABLE") from error


def sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise ManifestFailure("INPUT_NOT_READABLE") from error


def parse_packet_argument(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ManifestFailure("PRODUCT_PACKET_ARGUMENT_INVALID")
    scope, raw_path = value.split("=", 1)
    scope = scope.strip()
    if not scope or not raw_path:
        raise ManifestFailure("PRODUCT_PACKET_ARGUMENT_INVALID")
    return scope, Path(raw_path).expanduser().resolve()


def packet_fact_ids(packet: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for field, value in packet.items():
        if field.startswith("confirmed_") or field in {"required_conditions", "known_limits"}:
            if isinstance(value, list):
                result.update(item for item in value if isinstance(item, str) and item)
    return result


def build(args: argparse.Namespace) -> dict[str, Any]:
    library = args.company_library_root.expanduser().resolve()
    company_path = library / "company.json"
    facts_path = library / "02-事实库/facts.json"
    company = read_json(company_path)
    facts_payload = read_json(facts_path)
    if company.get("company_id") != args.company_id or facts_payload.get("company_id") != args.company_id:
        raise ManifestFailure("CROSS_COMPANY_INPUT")
    facts = {
        item.get("fact_id"): item
        for item in facts_payload.get("facts", [])
        if isinstance(item, dict) and item.get("fact_id")
    }
    parsed = [parse_packet_argument(value) for value in args.product_packet]
    if not parsed:
        raise ManifestFailure("PRODUCT_PACKET_REQUIRED")
    scopes = [scope for scope, _ in parsed]
    if len(scopes) != len(set(scopes)):
        raise ManifestFailure("DUPLICATE_PRODUCT_SCOPE")
    packets: list[dict[str, Any]] = []
    for scope, path in parsed:
        document = read_json(path)
        packet = document.get("product_development_fact_packet") if isinstance(document, dict) else None
        if not isinstance(packet, dict):
            raise ManifestFailure("PRODUCT_PACKET_CONTRACT_INVALID")
        if packet.get("company_id") != args.company_id:
            raise ManifestFailure("CROSS_COMPANY_INPUT")
        if packet.get("product_family") != scope:
            raise ManifestFailure("PRODUCT_SCOPE_PACKET_MISMATCH")
        if "internal_industry_application_mapping" not in packet.get("allowed_use", []):
            raise ManifestFailure("PRODUCT_PACKET_USE_NOT_ALLOWED")
        fact_ids = sorted(packet_fact_ids(packet))
        for fact_id in fact_ids:
            fact = facts.get(fact_id)
            if not fact:
                raise ManifestFailure("UNRESOLVED_PACKET_FACT")
            if not (
                fact.get("company_id") == args.company_id
                and fact.get("subject_scope") == "own_company"
                and fact.get("statement_kind") == "source_fact"
                and fact.get("evidence_level") == "E3"
                and fact.get("review_status") == "approved"
            ):
                raise ManifestFailure("PRODUCT_FACT_NOT_APPROVED_E3")
        packets.append(
            {
                "product_scope": scope,
                "product_packet_path": str(path),
                "product_packet_sha256": sha256(path),
                "product_fact_ids": fact_ids,
            }
        )
    return {
        "schema_version": "1.0",
        "company_product_packet_manifest": {
            "manifest_id": f"{args.company_id}-PRODUCT-MANIFEST-{args.frozen_at}",
            "company_id": args.company_id,
            "company_library_root": str(library),
            "facts_path": str(facts_path.resolve()),
            "facts_sha256": sha256(facts_path),
            "product_scopes": scopes,
            "packets": packets,
            "allowed_use": ["internal_industry_application_mapping"],
            "frozen_at": args.frozen_at,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company-id", required=True)
    parser.add_argument("--company-library-root", type=Path, required=True)
    parser.add_argument("--product-packet", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frozen-at", required=True)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    try:
        if output.exists():
            raise ManifestFailure("OUTPUT_EXISTS")
        document = build(args)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except ManifestFailure as failure:
        print(json.dumps({"status": "FAIL", "errors": [{"code": failure.code}]}, ensure_ascii=False))
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
