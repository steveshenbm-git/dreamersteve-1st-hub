#!/usr/bin/env python3
"""Validate company isolation, traceability, evidence, and handoff boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


EVIDENCE_ALLOWED_USE = {
    "E3": {"internal", "external"},
    "E2": {"internal"},
    "E1": {"verification"},
    "E0": {"risk_review"},
}
SUBJECT_SCOPES = {"own_company", "supplier", "customer", "general_industry", "unknown"}
SOURCE_SUBJECTS = SUBJECT_SCOPES | {"mixed"}
STATEMENT_KINDS = {"source_fact", "inference", "unknown"}
FACT_TYPES = {
    "identity",
    "form",
    "material",
    "parameter",
    "property",
    "mechanism",
    "function",
    "effect",
    "required_condition",
    "known_limit",
    "application",
    "technical_document",
    "commercial_condition",
    "company_fact",
}
CONFIRMED_HANDOFF_FIELDS = {
    "confirmed_form",
    "confirmed_parameters",
    "confirmed_properties",
    "confirmed_mechanisms",
    "confirmed_functions",
    "confirmed_effects",
    "confirmed_applications",
    "required_conditions",
    "known_limits",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def read_json(path: Path, issues: list[dict[str, str]]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(issue("REQUIRED_FILE_MISSING", path, "Required JSON file is missing."))
    except json.JSONDecodeError as exc:
        issues.append(issue("INVALID_JSON", path, f"Invalid JSON: {exc}"))
    return None


def issue(code: str, path: Path | str, message: str) -> dict[str, str]:
    return {"code": code, "path": str(path), "message": message}


def require_keys(
    record: dict[str, Any],
    keys: set[str],
    record_path: str,
    issues: list[dict[str, str]],
) -> None:
    for key in sorted(keys - set(record)):
        issues.append(issue("REQUIRED_FIELD_MISSING", record_path, f"Missing field: {key}"))


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_sources(
    root: Path,
    company_id: str,
    payload: Any,
    issues: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        issues.append(issue("INVALID_SOURCE_REGISTRY", "00-管理/源文件清单.json", "sources must be a list."))
        return {}
    if payload.get("company_id") != company_id:
        issues.append(issue("CROSS_COMPANY_SOURCE_REGISTRY", "00-管理/源文件清单.json", "Registry company_id does not match library."))

    by_id: dict[str, dict[str, Any]] = {}
    required = {
        "source_id",
        "company_id",
        "archived_path",
        "sha256",
        "actual_subject",
        "intake_date",
        "notes",
    }
    for index, source in enumerate(payload["sources"]):
        record_path = f"sources[{index}]"
        if not isinstance(source, dict):
            issues.append(issue("INVALID_SOURCE_RECORD", record_path, "Source record must be an object."))
            continue
        require_keys(source, required, record_path, issues)
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            issues.append(issue("INVALID_SOURCE_ID", record_path, "source_id must be non-empty."))
            continue
        if source_id in by_id:
            issues.append(issue("DUPLICATE_SOURCE_ID", record_path, source_id))
        by_id[source_id] = source
        if source.get("company_id") != company_id:
            issues.append(issue("CROSS_COMPANY_SOURCE", record_path, source_id))
        if "evidence_level" in source:
            issues.append(
                issue(
                    "SOURCE_BLANKET_EVIDENCE_FORBIDDEN",
                    record_path,
                    "Assign evidence at fact level, never to the entire source.",
                )
            )
        if source.get("actual_subject") not in SOURCE_SUBJECTS:
            issues.append(issue("INVALID_SOURCE_SUBJECT", record_path, str(source.get("actual_subject"))))

        archived_path = source.get("archived_path")
        if not isinstance(archived_path, str) or not archived_path:
            issues.append(issue("INVALID_ARCHIVED_PATH", record_path, "archived_path must be non-empty."))
            continue
        candidate = (root / archived_path).resolve()
        archive_root = (root / "01-源文件封存").resolve()
        if not is_inside(candidate, archive_root):
            issues.append(issue("SOURCE_PATH_OUTSIDE_ARCHIVE", record_path, archived_path))
            continue
        if not candidate.is_file():
            issues.append(issue("SOURCE_FILE_MISSING", record_path, archived_path))
            continue
        expected_hash = source.get("sha256")
        if not isinstance(expected_hash, str) or not SHA256_PATTERN.fullmatch(expected_hash):
            issues.append(issue("INVALID_SOURCE_HASH", record_path, str(expected_hash)))
            continue
        actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            issues.append(issue("SOURCE_HASH_MISMATCH", record_path, archived_path))
    return by_id


def validate_facts(
    company_id: str,
    payload: Any,
    sources: dict[str, dict[str, Any]],
    issues: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("facts"), list):
        issues.append(issue("INVALID_FACT_LIBRARY", "02-事实库/facts.json", "facts must be a list."))
        return {}
    if payload.get("company_id") != company_id:
        issues.append(issue("CROSS_COMPANY_FACT_LIBRARY", "02-事实库/facts.json", "Fact library company_id does not match."))

    required = {
        "fact_id",
        "company_id",
        "product_family",
        "product_series",
        "product_model",
        "fact_type",
        "fact_value",
        "statement_kind",
        "unit",
        "unit_status",
        "test_method",
        "test_method_status",
        "applicable_conditions",
        "known_limits",
        "subject_scope",
        "source_id",
        "source_location",
        "evidence_level",
        "review_status",
        "reviewed_by",
        "reviewed_at",
        "allowed_use",
        "conflict_status",
        "conflicts_with",
        "updated_at",
    }
    by_id: dict[str, dict[str, Any]] = {}
    for index, fact in enumerate(payload["facts"]):
        record_path = f"facts[{index}]"
        if not isinstance(fact, dict):
            issues.append(issue("INVALID_FACT_RECORD", record_path, "Fact record must be an object."))
            continue
        require_keys(fact, required, record_path, issues)
        fact_id = fact.get("fact_id")
        if not isinstance(fact_id, str) or not fact_id:
            issues.append(issue("INVALID_FACT_ID", record_path, "fact_id must be non-empty."))
            continue
        if fact_id in by_id:
            issues.append(issue("DUPLICATE_FACT_ID", record_path, fact_id))
        by_id[fact_id] = fact

        if fact.get("company_id") != company_id:
            issues.append(issue("CROSS_COMPANY_FACT", record_path, fact_id))
        if fact.get("fact_type") not in FACT_TYPES:
            issues.append(issue("INVALID_FACT_TYPE", record_path, str(fact.get("fact_type"))))
        statement_kind = fact.get("statement_kind")
        if statement_kind not in STATEMENT_KINDS:
            issues.append(issue("INVALID_STATEMENT_KIND", record_path, str(statement_kind)))
        subject_scope = fact.get("subject_scope")
        if subject_scope not in SUBJECT_SCOPES:
            issues.append(issue("INVALID_FACT_SUBJECT", record_path, str(subject_scope)))
        source_id = fact.get("source_id")
        if source_id not in sources:
            issues.append(issue("UNKNOWN_FACT_SOURCE", record_path, str(source_id)))
        if not isinstance(fact.get("source_location"), str) or not fact.get("source_location", "").strip():
            issues.append(issue("SOURCE_LOCATION_REQUIRED", record_path, fact_id))

        evidence = fact.get("evidence_level")
        allowed_use = fact.get("allowed_use")
        if evidence not in EVIDENCE_ALLOWED_USE:
            issues.append(issue("INVALID_EVIDENCE_LEVEL", record_path, str(evidence)))
        elif not isinstance(allowed_use, list) or not allowed_use or not set(allowed_use).issubset(EVIDENCE_ALLOWED_USE[evidence]):
            issues.append(issue("ALLOWED_USE_EXCEEDS_EVIDENCE", record_path, fact_id))

        if evidence in {"E2", "E3"}:
            if fact.get("review_status") != "approved" or not fact.get("reviewed_by") or not fact.get("reviewed_at"):
                issues.append(issue(f"{evidence}_REQUIRES_APPROVAL", record_path, fact_id))
        if evidence == "E3" and subject_scope != "own_company":
            issues.append(issue("E3_SUBJECT_MISMATCH", record_path, fact_id))
        if evidence == "E3" and statement_kind != "source_fact":
            issues.append(issue("E3_STATEMENT_KIND_MISMATCH", record_path, fact_id))

        if fact.get("fact_type") == "parameter":
            if not fact.get("unit") and fact.get("unit_status") != "not_applicable":
                issues.append(issue("PARAMETER_UNIT_UNRESOLVED", record_path, fact_id))
            if not fact.get("test_method") and fact.get("test_method_status") != "not_applicable":
                issues.append(issue("PARAMETER_TEST_METHOD_UNRESOLVED", record_path, fact_id))
            if not isinstance(fact.get("applicable_conditions"), list):
                issues.append(issue("PARAMETER_CONDITIONS_INVALID", record_path, fact_id))

        conflict_status = fact.get("conflict_status")
        conflicts_with = fact.get("conflicts_with")
        if conflict_status not in {"none", "open", "resolved", "superseded"}:
            issues.append(issue("INVALID_CONFLICT_STATUS", record_path, str(conflict_status)))
        if not isinstance(conflicts_with, list):
            issues.append(issue("INVALID_CONFLICT_LINKS", record_path, fact_id))
        elif conflict_status == "open" and not conflicts_with:
            issues.append(issue("OPEN_CONFLICT_WITHOUT_LINK", record_path, fact_id))
    return by_id


def validate_company_scoped_file(
    payload: Any,
    company_id: str,
    path: str,
    collection_key: str,
    issues: list[dict[str, str]],
) -> None:
    if not isinstance(payload, dict):
        return
    if payload.get("company_id") != company_id:
        issues.append(issue("CROSS_COMPANY_FILE", path, "company_id does not match library."))
    if not isinstance(payload.get(collection_key), list):
        issues.append(issue("INVALID_COLLECTION", path, f"{collection_key} must be a list."))


def validate_product_system(
    payload: Any,
    company_id: str,
    facts: dict[str, dict[str, Any]],
    issues: list[dict[str, str]],
) -> None:
    validate_company_scoped_file(
        payload,
        company_id,
        "03-产品体系/product-system.json",
        "product_families",
        issues,
    )
    if not isinstance(payload, dict) or not isinstance(payload.get("product_families"), list):
        return

    def inspect_node(node: Any, node_path: str) -> None:
        if isinstance(node, dict):
            for identifier_key in (
                "product_family_id",
                "product_series_id",
                "product_model_id",
                "specification_id",
            ):
                identifier = node.get(identifier_key)
                if identifier is not None and (
                    not isinstance(identifier, str)
                    or not identifier.startswith(f"{company_id}-")
                ):
                    issues.append(
                        issue(
                            "CROSS_COMPANY_PRODUCT_ID",
                            f"{node_path}.{identifier_key}",
                            str(identifier),
                        )
                    )
            fact_ids = node.get("fact_ids", [])
            if not isinstance(fact_ids, list):
                issues.append(issue("PRODUCT_TREE_FACT_IDS_INVALID", node_path, "fact_ids must be a list."))
            else:
                for fact_id in fact_ids:
                    if fact_id not in facts:
                        issues.append(issue("PRODUCT_TREE_UNKNOWN_FACT", node_path, str(fact_id)))
            for key in ("series", "models", "specifications"):
                if key in node:
                    inspect_node(node[key], f"{node_path}.{key}")
        elif isinstance(node, list):
            for index, child in enumerate(node):
                inspect_node(child, f"{node_path}[{index}]")

    inspect_node(payload["product_families"], "product_families")


def validate_handoff(
    payload: Any,
    company_id: str,
    facts: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    issues: list[dict[str, str]],
) -> None:
    packet = payload.get("product_development_fact_packet") if isinstance(payload, dict) else None
    if not isinstance(packet, dict):
        issues.append(issue("INVALID_HANDOFF_PACKET", "04-开发交接/product-development-fact-packet.json", "Packet object missing."))
        return
    if packet.get("company_id") != company_id:
        issues.append(issue("CROSS_COMPANY_HANDOFF", "product_development_fact_packet", "company_id does not match."))
    for field in CONFIRMED_HANDOFF_FIELDS:
        fact_ids = packet.get(field)
        if not isinstance(fact_ids, list):
            issues.append(issue("INVALID_HANDOFF_FIELD", field, "Confirmed field must be a list of fact IDs."))
            continue
        for fact_id in fact_ids:
            fact = facts.get(fact_id)
            if fact is None:
                issues.append(issue("HANDOFF_UNKNOWN_FACT", field, str(fact_id)))
            elif not (
                fact.get("evidence_level") == "E3"
                and fact.get("review_status") == "approved"
                and fact.get("subject_scope") == "own_company"
            ):
                issues.append(issue("HANDOFF_CONFIRMED_FACT_NOT_E3", field, str(fact_id)))
    for field in ("unresolved_conditions", "approved_references", "allowed_use", "prohibited_inference"):
        if not isinstance(packet.get(field), list):
            issues.append(issue("INVALID_HANDOFF_FIELD", field, "Field must be a list."))
    references = packet.get("approved_references")
    if isinstance(references, list):
        for source_id in references:
            if source_id not in sources:
                issues.append(issue("HANDOFF_UNKNOWN_SOURCE", "approved_references", str(source_id)))


def validate(root: Path) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    required_directories = (
        "00-管理",
        "01-源文件封存",
        "02-事实库",
        "03-产品体系",
        "04-开发交接",
        "05-复核",
        "06-工作区",
        "07-风险隔离",
    )
    for relative in required_directories:
        if not (root / relative).is_dir():
            issues.append(issue("REQUIRED_DIRECTORY_MISSING", relative, "Required directory is missing."))

    company = read_json(root / "company.json", issues)
    company_id = company.get("company_id") if isinstance(company, dict) else None
    if not isinstance(company_id, str) or not company_id:
        issues.append(issue("COMPANY_ID_REQUIRED", "company.json", "company_id must be non-empty."))
        company_id = ""

    source_payload = read_json(root / "00-管理" / "源文件清单.json", issues)
    sources = validate_sources(root, company_id, source_payload, issues)
    fact_payload = read_json(root / "02-事实库" / "facts.json", issues)
    facts = validate_facts(company_id, fact_payload, sources, issues)
    product_payload = read_json(root / "03-产品体系" / "product-system.json", issues)
    validate_product_system(product_payload, company_id, facts, issues)
    change_payload = read_json(root / "00-管理" / "变更记录.json", issues)
    validate_company_scoped_file(
        change_payload,
        company_id,
        "00-管理/变更记录.json",
        "changes",
        issues,
    )
    review_payload = read_json(root / "05-复核" / "review-log.json", issues)
    validate_company_scoped_file(
        review_payload,
        company_id,
        "05-复核/review-log.json",
        "reviews",
        issues,
    )
    handoff_payload = read_json(root / "04-开发交接" / "product-development-fact-packet.json", issues)
    validate_handoff(handoff_payload, company_id, facts, sources, issues)

    return {
        "status": "PASS" if not issues else "FAIL",
        "company_id": company_id or None,
        "source_count": len(sources),
        "fact_count": len(facts),
        "errors": issues,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("library", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.library.expanduser().resolve()
    report = validate(root)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['status']}: company_id={report['company_id']} sources={report['source_count']} facts={report['fact_count']}")
        for item in report["errors"]:
            print(f"- {item['code']} | {item['path']} | {item['message']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
