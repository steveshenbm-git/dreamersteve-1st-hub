#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


CONCEPT_ROLES = {
    "industry_output",
    "material_form",
    "phase_relation",
    "process_action",
    "use_point",
    "exclusion",
}
TERM_STATES = {"proposed", "source_observed", "accepted_for_retrieval", "rejected"}
LANGUAGES = {"zh", "en", "other"}
ORIGINS = {"official_taxonomy", "public_source", "model_query_candidate"}
PRIVATE_KEYS = {
    "company_id",
    "company_name",
    "company_product",
    "brand_id",
    "brand_name",
    "product_fact_id",
    "product_id",
    "product_name",
    "route_id",
    "customer_id",
    "customer_name",
}
PERMITTED_COMPANY_GUARD_KEYS = {"company_data_allowed", "company_data_present"}
HEADER_FIELDS = {
    "record_type",
    "research_contract_id",
    "contract_version",
    "term_pack_state",
    "accepted_term_count",
    "company_data_allowed",
}
TERM_FIELDS = {
    "record_type",
    "term_id",
    "research_contract_id",
    "concept_role",
    "language",
    "surface_form",
    "term_state",
    "origin",
    "source_reference",
    "source_snapshot_sha256",
    "applicable_scope",
    "exclusions",
    "company_data_present",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_lowercase_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
        and len(set(value)) > 1
    )


def add(errors: list[dict[str, str]], code: str, detail: str) -> None:
    errors.append({"code": code, "detail": detail})


def private_keys_in(value: Any) -> set[str]:
    if isinstance(value, dict):
        found = {
            key
            for key in value
            if key in PRIVATE_KEYS
            or (
                key not in PERMITTED_COMPANY_GUARD_KEYS
                and any(
                    marker in key.lower()
                    for marker in ("company", "brand", "product", "route", "customer")
                )
            )
        }
        for item in value.values():
            found.update(private_keys_in(item))
        return found
    if isinstance(value, list):
        return set().union(*(private_keys_in(item) for item in value)) if value else set()
    return set()


def validate_rows(
    rows: list[dict[str, Any]], expected_contract_id: str | None = None
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            add(errors, "TERM_ROW_INVALID", str(index))
            continue
        private_keys = private_keys_in(row)
        if private_keys:
            add(errors, "COMPANY_TERM_FORBIDDEN", ",".join(sorted(private_keys)))
        if row.get("record_type") not in {
            "terminology_bridge_contract",
            "terminology_term",
        }:
            add(errors, "TERM_RECORD_TYPE_INVALID", str(index))

    headers = [row for row in rows if row.get("record_type") == "terminology_bridge_contract"]
    terms = [row for row in rows if row.get("record_type") == "terminology_term"]
    if len(headers) != 1:
        add(errors, "TERM_HEADER_COUNT_INVALID", str(len(headers)))
        return errors

    header = headers[0]
    if set(header) != HEADER_FIELDS:
        add(errors, "TERM_HEADER_FIELDS_INVALID", "terminology_bridge_contract")
    contract_id = header.get("research_contract_id")
    if not nonempty(contract_id):
        add(errors, "TERM_CONTRACT_ID_INVALID", "header")
    if expected_contract_id is not None and contract_id != expected_contract_id:
        add(errors, "TERM_CONTRACT_ID_MISMATCH", str(contract_id))
    if not nonempty(header.get("contract_version")):
        add(errors, "TERM_CONTRACT_VERSION_INVALID", "header")
    if header.get("term_pack_state") not in {"frozen_empty_cold_start", "frozen"}:
        add(errors, "TERM_PACK_STATE_INVALID", str(header.get("term_pack_state")))
    if header.get("term_pack_state") == "frozen_empty_cold_start" and terms:
        add(errors, "TERM_COLD_START_NOT_EMPTY", str(len(terms)))
    if type(header.get("accepted_term_count")) is not int or header.get(
        "accepted_term_count"
    ) < 0:
        add(errors, "TERM_ACCEPTED_COUNT_INVALID", str(header.get("accepted_term_count")))
    elif header.get("accepted_term_count") != sum(
        term.get("term_state") == "accepted_for_retrieval" for term in terms
    ):
        add(errors, "TERM_ACCEPTED_COUNT_MISMATCH", str(header.get("accepted_term_count")))
    if header.get("company_data_allowed") is not False:
        add(errors, "COMPANY_TERM_FORBIDDEN", "company_data_allowed")

    term_ids = [term.get("term_id") for term in terms]
    if len(set(term_ids)) != len(terms):
        add(errors, "TERM_ID_DUPLICATE", "term_id")
    for index, term in enumerate(terms):
        if set(term) != TERM_FIELDS:
            add(errors, "TERM_FIELDS_INVALID", str(index))
        if not nonempty(term.get("term_id")):
            add(errors, "TERM_ID_INVALID", str(index))
        if term.get("research_contract_id") != contract_id:
            add(errors, "TERM_CONTRACT_ID_MISMATCH", str(index))
        if term.get("concept_role") not in CONCEPT_ROLES:
            add(errors, "TERM_CONCEPT_ROLE_INVALID", str(term.get("concept_role")))
        state = term.get("term_state")
        if state not in TERM_STATES:
            add(errors, "TERM_STATE_INVALID", str(state))
        if state in {"source_observed", "accepted_for_retrieval"} and not nonempty(
            term.get("source_reference")
        ):
            add(errors, "TERM_SOURCE_REFERENCE_REQUIRED", str(index))
        if state in {"source_observed", "accepted_for_retrieval"} and not is_lowercase_sha256(
            term.get("source_snapshot_sha256")
        ):
            add(errors, "TERM_SOURCE_SNAPSHOT_SHA256_INVALID", str(index))
        if term.get("language") not in LANGUAGES:
            add(errors, "TERM_LANGUAGE_INVALID", str(term.get("language")))
        if term.get("origin") not in ORIGINS:
            add(errors, "TERM_ORIGIN_INVALID", str(term.get("origin")))
        if not (
            nonempty(term.get("surface_form"))
            and isinstance(term.get("applicable_scope"), list)
            and isinstance(term.get("exclusions"), list)
        ):
            add(errors, "TERM_SEMANTICS_INVALID", str(index))
        if term.get("company_data_present") is not False:
            add(errors, "COMPANY_TERM_FORBIDDEN", f"company_data_present:{index}")
    return errors


def load_rows(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows, [{"code": "TERM_PACK_MISSING", "detail": str(path)}]
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                add(errors, "TERM_JSONL_BLANK_LINE", str(line_number))
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                add(errors, "TERM_ROW_INVALID", str(line_number))
                continue
            rows.append(value)
    except (OSError, json.JSONDecodeError) as exc:
        add(errors, "TERM_PACK_INVALID", str(exc))
    return rows, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a contract-local terminology bridge.")
    parser.add_argument("terminology_bridge", type=Path)
    parser.add_argument("--expected-contract-id")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    rows, errors = load_rows(args.terminology_bridge)
    errors.extend(validate_rows(rows, args.expected_contract_id))
    term_count = sum(row.get("record_type") == "terminology_term" for row in rows)
    report = {"status": "FAIL" if errors else "PASS", "errors": errors, "term_count": term_count}
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(report["status"])
        print(f"term_count: {term_count}")
        for error in errors:
            print(f"{error['code']}: {error['detail']}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
