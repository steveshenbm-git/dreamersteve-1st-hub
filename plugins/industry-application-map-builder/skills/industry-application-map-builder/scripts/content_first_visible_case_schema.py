"""Exact, truth-free content-first visible-case schemas shared by every gate."""
from __future__ import annotations

import re
from datetime import datetime
import unicodedata
from typing import Any


SHA256 = re.compile(r"^[0-9a-f]{64}$")
VISIBLE_NODE_KEYS = {
    "taxonomy_node_id", "code", "level", "name_zh", "breadcrumb",
    "official_definition_or_null", "included_activities_or_null",
    "excluded_or_adjacent_activities_or_null", "official_source_reference",
    "official_source_sha256",
}
VISIBLE_DRAFT_HEADER_KEYS = {
    "record_type", "visible_case_set_id", "research_contract_id", "visible_case_set_state",
    "visible_only", "truth_data_allowed", "case_count", "actual_case_record_count",
    "formal_case_ids",
}
VISIBLE_FROZEN_HEADER_KEYS = VISIBLE_DRAFT_HEADER_KEYS | {
    "frozen_before_truth_preparation", "freeze_authorization_reference", "frozen_at",
}
VISIBLE_DRAFT_RECORD_KEYS = {
    "record_type", "research_contract_id", "case_id", "taxonomy_node",
    "product_neutral_research_theme", "risk_flags",
}
VISIBLE_FROZEN_RECORD_KEYS = {
    "record_type", "research_contract_id", "case_id", "taxonomy_node",
    "product_neutral_research_theme", "risk_flags",
}


def nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_timezone_iso8601(value: object) -> bool:
    if not nonempty_text(value):
        return False
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def valid_case_id(value: object) -> bool:
    return (
        isinstance(value, str) and bool(value.strip())
        and unicodedata.normalize("NFKC", value) == value
        and "/" not in value and "\\" not in value and "." not in value
        and not any(character.isspace() or ord(character) < 32 for character in value)
    )


def valid_visible_node(node: object) -> bool:
    if not isinstance(node, dict) or set(node) != VISIBLE_NODE_KEYS:
        return False
    if not (
        nonempty_text(node.get("taxonomy_node_id"))
        and nonempty_text(node.get("code"))
        and type(node.get("level")) is int
        and nonempty_text(node.get("name_zh"))
        and isinstance(node.get("breadcrumb"), list)
        and bool(node["breadcrumb"])
        and all(nonempty_text(item) for item in node["breadcrumb"])
        and nonempty_text(node.get("official_source_reference"))
        and isinstance(node.get("official_source_sha256"), str)
        and SHA256.fullmatch(node["official_source_sha256"]) is not None
    ):
        return False
    return all(
        node[key] is None or nonempty_text(node[key])
        for key in (
            "official_definition_or_null", "included_activities_or_null",
            "excluded_or_adjacent_activities_or_null",
        )
    )


def visible_case_projection(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case.get("case_id"),
        "taxonomy_node": case.get("taxonomy_node"),
        "product_neutral_research_theme": case.get("product_neutral_research_theme"),
        "risk_flags": case.get("risk_flags"),
    }


def _valid_cases(cases: list[dict], research_contract_id: object, record_type: str, expected_keys: set[str]) -> bool:
    ids = [row.get("case_id") for row in cases]
    return (
        len(cases) == 40
        and len(set(ids)) == 40
        and len({unicodedata.normalize("NFKC", value).casefold() for value in ids if isinstance(value, str)}) == 40
        and all(
            set(row) == expected_keys
            and row.get("record_type") == record_type
            and row.get("research_contract_id") == research_contract_id
            and valid_case_id(row.get("case_id"))
            and valid_visible_node(row.get("taxonomy_node"))
            and nonempty_text(row.get("product_neutral_research_theme"))
            and isinstance(row.get("risk_flags"), list)
            and all(nonempty_text(flag) for flag in row["risk_flags"])
            for row in cases
        )
    )


def _validate_rows(rows: list[dict], research_contract_id: object, *, frozen: bool) -> list[str]:
    header_type = "visible_case_set_contract" if frozen else "visible_case_set_draft"
    record_type = "visible_calibration_case" if frozen else "visible_calibration_case_draft"
    header_keys = VISIBLE_FROZEN_HEADER_KEYS if frozen else VISIBLE_DRAFT_HEADER_KEYS
    headers = [row for row in rows if row.get("record_type") == header_type]
    cases = [row for row in rows if row.get("record_type") == record_type]
    if len(headers) != 1 or any(row.get("record_type") not in {header_type, record_type} for row in rows):
        return ["VISIBLE_CASE_SET_INVALID"]
    header = headers[0]
    ids = [row.get("case_id") for row in cases]
    if (
        set(header) != header_keys
        or header.get("research_contract_id") != research_contract_id
        or not nonempty_text(header.get("visible_case_set_id"))
        or header.get("visible_case_set_state") != ("frozen_visible_only" if frozen else "draft_visible_only")
        or header.get("visible_only") is not True
        or header.get("truth_data_allowed") is not False
        or header.get("case_count") != 40
        or header.get("actual_case_record_count") != 40
        or header.get("formal_case_ids") != ids
        or not _valid_cases(cases, research_contract_id, record_type, VISIBLE_FROZEN_RECORD_KEYS if frozen else VISIBLE_DRAFT_RECORD_KEYS)
    ):
        return ["VISIBLE_CASE_SET_INVALID"]
    if frozen and (
        header.get("frozen_before_truth_preparation") is not True
        or not nonempty_text(header.get("freeze_authorization_reference"))
        or not valid_timezone_iso8601(header.get("frozen_at"))
    ):
        return ["VISIBLE_CASE_SET_INVALID"]
    return []


def visible_case_draft_errors(rows: list[dict], research_contract_id: object) -> list[str]:
    return _validate_rows(rows, research_contract_id, frozen=False)


def frozen_visible_case_errors(rows: list[dict], research_contract_id: object) -> list[str]:
    return _validate_rows(rows, research_contract_id, frozen=True)
