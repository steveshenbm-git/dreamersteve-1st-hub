from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from xlsx_contract import (
    parse_json_list,
    read_headers,
    read_sheet_records,
    sha256_file,
    workbook_sheet_names,
)


TAXONOMY_SHEETS = ["版本与范围", "行业骨架", "证据来源", "变更记录"]
TAXONOMY_HEADERS = {
    "版本与范围": ["schema_version", "taxonomy_system", "taxonomy_version", "effective_status", "source_url", "observed_at", "declared_scope", "notes"],
    "行业骨架": ["taxonomy_node_id", "taxonomy_system", "taxonomy_version", "code", "name_zh", "name_en", "level", "parent_node_id", "valid_from", "valid_to", "status", "source_id"],
    "证据来源": ["source_id", "source_type", "title", "publisher", "source_url_or_local_reference", "published_at", "observed_at", "access_scope", "notes"],
    "变更记录": ["change_id", "changed_at", "actor", "reason", "affected_ids", "prior_state", "new_state", "authorization_basis"],
}
APPLICATION_SHEETS = [
    "版本与范围",
    "产出产品",
    "应用节点",
    "需求原子",
    "关系边",
    "证据来源",
    "覆盖台账",
    "变更记录",
]
APPLICATION_HEADERS = {
    "版本与范围": ["schema_version", "application_base_version", "taxonomy_system", "taxonomy_version", "declared_scope", "source_scope", "observed_at", "notes"],
    "产出产品": ["output_product_id", "name_zh", "name_en", "aliases", "taxonomy_node_ids", "description", "evidence_state", "evidence_ids", "limitations"],
    "应用节点": ["application_node_id", "name_zh", "name_en", "application_type", "use_point_type", "process_step", "output_product_ids", "description", "evidence_state", "evidence_ids", "limitations"],
    "需求原子": ["requirement_atom_id", "application_node_id", "dimension", "operator", "value", "unit", "conditions", "hardness", "evidence_state", "evidence_ids", "limitations"],
    "关系边": ["edge_id", "from_type", "from_id", "relation_type", "to_type", "to_id", "evidence_state", "evidence_ids", "source_dependency_group", "limitations"],
    "证据来源": ["evidence_id", "source_type", "title", "publisher", "source_url_or_local_reference", "published_at", "observed_at", "source_subject", "source_dependency_group", "original_location", "zh_summary", "evidence_state", "access_scope", "conflict_note"],
    "覆盖台账": ["coverage_id", "taxonomy_node_id", "output_product_id", "application_node_id", "coverage_state", "disposition_reason", "last_reviewed_at"],
    "变更记录": ["change_id", "changed_at", "actor", "reason", "affected_ids", "prior_state", "new_state", "authorization_basis"],
}
COMPANY_SHEETS = [
    "公司与输入",
    "产品能力",
    "路线候选",
    "匹配明细",
    "排除暂缓",
    "覆盖台账",
    "路线交接",
    "变更记录",
]

COMPANY_HEADERS = {
    "公司与输入": ["company_id", "company_library_root", "product_packet_path", "product_packet_sha256", "facts_path", "facts_sha256", "shared_taxonomy_path", "taxonomy_sha256", "shared_application_base_path", "application_base_sha256", "product_scope", "declared_taxonomy_scope", "declared_application_scope", "allowed_source_scope", "initialized_at"],
    "产品能力": ["capability_id", "company_id", "product_scope", "product_fact_ids", "product_source_ids", "dimension", "operator", "value", "unit", "conditions", "known_limits", "evidence_state"],
    "路线候选": ["route_candidate_id", "company_id", "product_scope", "application_node_id", "taxonomy_node_ids", "output_product_ids", "use_point_or_process", "target_enterprise_activity", "product_fact_ids", "product_source_ids", "application_evidence_ids", "application_source_groups", "evidence_state", "technical_match_state", "known_limit_conflict", "research_disposition", "map_route_status", "geography_hypotheses", "geography_evidence_ids", "unresolved_conditions", "derivation_trace"],
    "匹配明细": ["match_id", "route_candidate_id", "requirement_atom_id", "capability_id", "match_state", "condition_compatibility", "process_interface_compatibility", "limit_conflict", "product_fact_ids", "application_evidence_ids", "rationale"],
    "排除暂缓": ["disposition_id", "route_candidate_id", "application_node_id", "disposition", "reason", "evidence_ids", "reviewed_at"],
    "覆盖台账": ["coverage_id", "company_id", "product_scope", "coverage_object_type", "coverage_object_id", "coverage_state", "disposition", "route_candidate_ids", "gap", "reviewed_at"],
    "路线交接": ["handoff_id", "route_candidate_id", "target_skill", "handoff_state", "exported_at", "packet_path", "salesperson_decision_required"],
    "变更记录": ["change_id", "changed_at", "actor", "reason", "affected_ids", "prior_state", "new_state", "authorization_basis"],
}

EVIDENCE_STATES = {"supported", "hypothesis", "unknown", "conflicted"}
TECHNICAL_STATES = {"satisfied", "violated", "unknown", "conflicted"}
MAP_ROUTE_STATUSES = {"路线线索", "路线候选", "待外部核实", "暂缓", "排除"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def diagnostic(code: str, message: str, path: Path | None = None) -> dict[str, str]:
    item = {"code": code, "message": message}
    if path:
        item["path"] = str(path)
    return item


def safe_list(errors: list[dict[str, str]], value: Any, field: str, path: Path) -> list[str]:
    try:
        return parse_json_list(value, field)
    except ValueError as exc:
        errors.append(diagnostic("INVALID_JSON_LIST", str(exc), path))
        return []


def check_sheet_contract(
    errors: list[dict[str, str]], path: Path, expected_sheets: list[str], headers: dict[str, list[str]] | None = None
) -> None:
    try:
        actual = workbook_sheet_names(path)
    except Exception as exc:
        errors.append(diagnostic("WORKBOOK_UNREADABLE", str(exc), path))
        return
    if actual != expected_sheets:
        errors.append(diagnostic("WORKBOOK_SHEET_ORDER", f"expected {expected_sheets!r}, got {actual!r}", path))
    if headers:
        for sheet, expected in headers.items():
            try:
                actual_headers = read_headers(path, sheet)
            except Exception as exc:
                errors.append(diagnostic("WORKBOOK_HEADER_UNREADABLE", f"{sheet}: {exc}", path))
                continue
            if actual_headers != expected:
                errors.append(diagnostic("WORKBOOK_HEADER_MISMATCH", sheet, path))


def validate_workspace(map_root: Path, company_id: str | None = None) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    registry_path = map_root / "00-管理" / "map-registry.json"
    taxonomy_path = map_root / "01-共享行业骨架" / "industry-taxonomy.xlsx"
    application_path = map_root / "02-共享应用知识" / "industry-application-base.xlsx"
    for required in (registry_path, taxonomy_path, application_path):
        if not required.is_file():
            errors.append(diagnostic("REQUIRED_FILE_MISSING", str(required), required))
    if errors:
        return {"status": "FAIL", "errors": errors}

    try:
        registry = read_json(registry_path)
    except Exception as exc:
        return {"status": "FAIL", "errors": [diagnostic("REGISTRY_INVALID", str(exc), registry_path)]}

    check_sheet_contract(errors, taxonomy_path, TAXONOMY_SHEETS, TAXONOMY_HEADERS)
    check_sheet_contract(errors, application_path, APPLICATION_SHEETS, APPLICATION_HEADERS)
    taxonomy_version = registry.get("shared_taxonomy", {}).get("taxonomy_version")
    if not taxonomy_version or taxonomy_version == "UNASSIGNED":
        errors.append(diagnostic("TAXONOMY_VERSION_MISSING", "taxonomy version is not frozen", registry_path))
    for key, path in (("shared_taxonomy", taxonomy_path), ("shared_application_base", application_path)):
        recorded = registry.get(key, {}).get("sha256")
        if recorded != sha256_file(path):
            errors.append(diagnostic("SHARED_BASE_HASH_MISMATCH", key, path))

    if not company_id:
        return {"status": "PASS" if not errors else "FAIL", "errors": errors}

    companies = [item for item in registry.get("companies", []) if item.get("company_id") == company_id]
    if len(companies) != 1:
        errors.append(diagnostic("COMPANY_MAP_NOT_REGISTERED", company_id, registry_path))
        return {"status": "FAIL", "errors": errors}
    company = companies[0]
    workbook = map_root / company["company_map_path"]
    if not workbook.is_file():
        errors.append(diagnostic("COMPANY_WORKBOOK_MISSING", company_id, workbook))
        return {"status": "FAIL", "errors": errors}
    check_sheet_contract(errors, workbook, COMPANY_SHEETS, COMPANY_HEADERS)
    company_root = workbook.parent.resolve()
    export_registry_path = company_root / "route-pool-export-registry.json"
    export_registry = None
    if not export_registry_path.is_file():
        errors.append(
            diagnostic(
                "ROUTE_EXPORT_REGISTRY_MISSING",
                company_id,
                export_registry_path,
            )
        )
    else:
        try:
            export_registry = read_json(export_registry_path)
        except Exception as exc:
            errors.append(
                diagnostic(
                    "ROUTE_EXPORT_REGISTRY_INVALID",
                    str(exc),
                    export_registry_path,
                )
            )

    packet_path = Path(company["product_packet_path"])
    facts_path = Path(company["facts_path"])
    for required in (packet_path, facts_path):
        if not required.is_file():
            errors.append(diagnostic("COMPANY_INPUT_MISSING", str(required), required))
    if errors and any(item["code"] == "COMPANY_INPUT_MISSING" for item in errors):
        return {"status": "FAIL", "errors": errors}
    if company.get("product_packet_sha256") != sha256_file(packet_path):
        errors.append(diagnostic("PRODUCT_PACKET_HASH_MISMATCH", company_id, packet_path))
    if company.get("facts_sha256") != sha256_file(facts_path):
        errors.append(diagnostic("FACTS_HASH_MISMATCH", company_id, facts_path))
    if company.get("taxonomy_sha256") != sha256_file(taxonomy_path):
        errors.append(diagnostic("COMPANY_TAXONOMY_SNAPSHOT_STALE", company_id, taxonomy_path))
    if company.get("application_base_sha256") != sha256_file(application_path):
        errors.append(diagnostic("COMPANY_APPLICATION_SNAPSHOT_STALE", company_id, application_path))

    input_rows = read_sheet_records(workbook, "公司与输入")
    if len(input_rows) != 1:
        errors.append(diagnostic("COMPANY_INPUT_SNAPSHOT_COUNT", company_id, workbook))
    else:
        input_snapshot = input_rows[0]
        expected_snapshot = {
            "company_id": company_id,
            "company_library_root": str(Path(company["company_library_root"]).resolve()),
            "product_packet_path": str(packet_path.resolve()),
            "product_packet_sha256": company.get("product_packet_sha256", ""),
            "facts_path": str(facts_path.resolve()),
            "facts_sha256": company.get("facts_sha256", ""),
            "shared_taxonomy_path": str(taxonomy_path.resolve()),
            "taxonomy_sha256": company.get("taxonomy_sha256", ""),
            "shared_application_base_path": str(application_path.resolve()),
            "application_base_sha256": company.get("application_base_sha256", ""),
            "product_scope": company.get("product_scope", ""),
            "declared_taxonomy_scope": company.get("declared_taxonomy_scope", ""),
            "declared_application_scope": company.get("declared_application_scope", ""),
            "allowed_source_scope": company.get("allowed_source_scope", ""),
        }
        mismatches = [
            field
            for field, expected in expected_snapshot.items()
            if input_snapshot.get(field, "") != expected
        ]
        if mismatches:
            errors.append(
                diagnostic(
                    "COMPANY_INPUT_SNAPSHOT_MISMATCH",
                    f"{company_id}: {mismatches}",
                    workbook,
                )
            )

    if export_registry is not None:
        if export_registry.get("company_id") != company_id or not isinstance(
            export_registry.get("exports"), list
        ):
            errors.append(
                diagnostic(
                    "ROUTE_EXPORT_REGISTRY_INVALID",
                    company_id,
                    export_registry_path,
                )
            )
        else:
            seen_export_ids: set[str] = set()
            for export in export_registry["exports"]:
                export_id = export.get("export_id") if isinstance(export, dict) else None
                if not isinstance(export_id, str) or not export_id:
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_ID_INVALID",
                            str(export_id),
                            export_registry_path,
                        )
                    )
                    continue
                if export_id in seen_export_ids:
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_ID_DUPLICATE",
                            export_id,
                            export_registry_path,
                        )
                    )
                seen_export_ids.add(export_id)
                if export.get("company_id") != company_id:
                    errors.append(
                        diagnostic(
                            "CROSS_COMPANY_ROUTE_EXPORT",
                            export_id,
                            export_registry_path,
                        )
                    )
                if export.get("state") not in {"current", "stale", "superseded"}:
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_STATE_INVALID",
                            export_id,
                            export_registry_path,
                        )
                    )
                packet_relative = export.get("packet_path")
                if not isinstance(packet_relative, str) or not packet_relative:
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_PACKET_PATH_INVALID",
                            export_id,
                            export_registry_path,
                        )
                    )
                    continue
                route_packet_path = (map_root / packet_relative).resolve()
                try:
                    route_packet_path.relative_to(company_root)
                except ValueError:
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_PACKET_OUTSIDE_COMPANY_MAP",
                            export_id,
                            route_packet_path,
                        )
                    )
                    continue
                if not route_packet_path.is_file():
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_PACKET_MISSING",
                            export_id,
                            route_packet_path,
                        )
                    )
                    continue
                recorded_hash = export.get("packet_sha256")
                if recorded_hash != sha256_file(route_packet_path):
                    errors.append(
                        diagnostic(
                            "ROUTE_PACKET_HASH_MISMATCH",
                            export_id,
                            route_packet_path,
                        )
                    )
                try:
                    route_packet = read_json(route_packet_path).get(
                        "company_route_pool_packet", {}
                    )
                except Exception as exc:
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_PACKET_INVALID",
                            str(exc),
                            route_packet_path,
                        )
                    )
                    continue
                reference = route_packet.get("producer_registry_reference", {})
                if (
                    route_packet.get("export_id") != export_id
                    or route_packet.get("company_id") != company_id
                    or reference.get("export_id") != export_id
                    or reference.get("path")
                    != str(export_registry_path.relative_to(map_root))
                    or Path(reference.get("map_root", "")).resolve() != map_root
                ):
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_REFERENCE_MISMATCH",
                            export_id,
                            route_packet_path,
                        )
                    )
                if route_packet.get("input_snapshot") != export.get("input_snapshot"):
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_SNAPSHOT_MISMATCH",
                            export_id,
                            route_packet_path,
                        )
                    )
                producer_snapshot = export.get("producer_snapshot")
                if (
                    not isinstance(producer_snapshot, dict)
                    or route_packet.get("producer_snapshot") != producer_snapshot
                ):
                    errors.append(
                        diagnostic(
                            "ROUTE_EXPORT_PRODUCER_SNAPSHOT_MISMATCH",
                            export_id,
                            route_packet_path,
                        )
                    )
                else:
                    snapshot_map_path = (map_root / str(
                        producer_snapshot.get("company_map_path", "")
                    )).resolve()
                    if snapshot_map_path != workbook.resolve():
                        errors.append(
                            diagnostic(
                                "ROUTE_EXPORT_SOURCE_MAP_PATH_MISMATCH",
                                export_id,
                                route_packet_path,
                            )
                        )
                    elif (
                        export.get("state") == "current"
                        and producer_snapshot.get("company_map_sha256")
                        != sha256_file(workbook)
                    ):
                        errors.append(
                            diagnostic(
                                "ROUTE_EXPORT_SOURCE_MAP_STALE",
                                export_id,
                                workbook,
                            )
                        )

    facts_payload = read_json(facts_path)
    packet = read_json(packet_path).get("product_development_fact_packet", {})
    if facts_payload.get("company_id") != company_id or packet.get("company_id") != company_id:
        errors.append(diagnostic("CROSS_COMPANY_INPUT", company_id, packet_path))
    if "internal_industry_application_mapping" not in packet.get("allowed_use", []):
        errors.append(diagnostic("PRODUCT_PACKET_USE_NOT_ALLOWED", company_id, packet_path))
    facts = {fact.get("fact_id"): fact for fact in facts_payload.get("facts", [])}
    packet_fact_ids: set[str] = set()
    for field, value in packet.items():
        if field.startswith("confirmed_") or field in {"required_conditions", "known_limits"}:
            if isinstance(value, list):
                packet_fact_ids.update(item for item in value if isinstance(item, str))

    for fact_id in packet_fact_ids:
        fact = facts.get(fact_id)
        if not fact:
            errors.append(diagnostic("UNRESOLVED_PACKET_FACT", fact_id, packet_path))
        elif not (
            fact.get("company_id") == company_id
            and fact.get("subject_scope") == "own_company"
            and fact.get("statement_kind") == "source_fact"
            and fact.get("evidence_level") == "E3"
            and fact.get("review_status") == "approved"
        ):
            errors.append(diagnostic("PRODUCT_FACT_NOT_APPROVED_E3", fact_id, facts_path))

    taxonomy_rows = read_sheet_records(taxonomy_path, "行业骨架")
    taxonomy_source_rows = read_sheet_records(taxonomy_path, "证据来源")
    taxonomy_source_by_id = {row.get("source_id"): row for row in taxonomy_source_rows}
    taxonomy_sources = set(taxonomy_source_by_id)
    taxonomy_ids = {row.get("taxonomy_node_id") for row in taxonomy_rows}
    if len(taxonomy_ids) != len(taxonomy_rows):
        errors.append(diagnostic("DUPLICATE_TAXONOMY_NODE_ID", "industry taxonomy", taxonomy_path))
    for row in taxonomy_rows:
        if row.get("source_id") not in taxonomy_sources:
            errors.append(
                diagnostic(
                    "TAXONOMY_SOURCE_UNRESOLVED",
                    row.get("taxonomy_node_id", ""),
                    taxonomy_path,
                )
            )
        elif not str(taxonomy_source_by_id[row.get("source_id")].get("source_type", "")).startswith("official"):
            errors.append(diagnostic("TAXONOMY_SOURCE_NOT_OFFICIAL", row.get("taxonomy_node_id", ""), taxonomy_path))
        if row.get("taxonomy_system") != registry.get("shared_taxonomy", {}).get("taxonomy_system"):
            errors.append(diagnostic("TAXONOMY_SYSTEM_MISMATCH", row.get("taxonomy_node_id", ""), taxonomy_path))
        if row.get("taxonomy_version") != taxonomy_version:
            errors.append(diagnostic("TAXONOMY_VERSION_MISMATCH", row.get("taxonomy_node_id", ""), taxonomy_path))
    output_rows = read_sheet_records(application_path, "产出产品")
    outputs = {row.get("output_product_id"): row for row in output_rows}
    output_ids = set(outputs)
    application_rows = read_sheet_records(application_path, "应用节点")
    applications = {row.get("application_node_id"): row for row in application_rows}
    application_ids = {row.get("application_node_id") for row in application_rows}
    requirement_rows = read_sheet_records(application_path, "需求原子")
    requirements = {row.get("requirement_atom_id"): row for row in requirement_rows}
    evidence_rows = read_sheet_records(application_path, "证据来源")
    evidence = {row.get("evidence_id"): row for row in evidence_rows}
    evidence_ids = set(evidence)
    if len(evidence_ids) != len(evidence_rows):
        errors.append(diagnostic("DUPLICATE_APPLICATION_EVIDENCE_ID", "application evidence", application_path))

    for collection_name, rows, id_field in (
        ("output", output_rows, "output_product_id"),
        ("application", application_rows, "application_node_id"),
        ("requirement", requirement_rows, "requirement_atom_id"),
    ):
        identifiers = [row.get(id_field) for row in rows]
        if len(set(identifiers)) != len(identifiers):
            errors.append(diagnostic(f"DUPLICATE_{collection_name.upper()}_ID", collection_name, application_path))

    for row in output_rows:
        output_id = row.get("output_product_id", "")
        for taxonomy_id in safe_list(errors, row.get("taxonomy_node_ids"), "output.taxonomy_node_ids", application_path):
            if taxonomy_id not in taxonomy_ids:
                errors.append(diagnostic("OUTPUT_UNKNOWN_TAXONOMY_NODE", f"{output_id}: {taxonomy_id}", application_path))
        output_evidence = safe_list(errors, row.get("evidence_ids"), "output.evidence_ids", application_path)
        if row.get("evidence_state") == "supported" and not output_evidence:
            errors.append(diagnostic("SUPPORTED_OUTPUT_EVIDENCE_MISSING", output_id, application_path))
        for evidence_id in output_evidence:
            if evidence_id not in evidence_ids:
                errors.append(diagnostic("OUTPUT_UNKNOWN_EVIDENCE", f"{output_id}: {evidence_id}", application_path))

    for row in application_rows:
        application_id = row.get("application_node_id", "")
        for output_id in safe_list(errors, row.get("output_product_ids"), "application.output_product_ids", application_path):
            if output_id not in output_ids:
                errors.append(diagnostic("APPLICATION_UNKNOWN_OUTPUT", f"{application_id}: {output_id}", application_path))
        application_evidence = safe_list(errors, row.get("evidence_ids"), "application.evidence_ids", application_path)
        if row.get("evidence_state") == "supported" and not application_evidence:
            errors.append(diagnostic("SUPPORTED_APPLICATION_EVIDENCE_MISSING", application_id, application_path))
        for evidence_id in application_evidence:
            if evidence_id not in evidence_ids:
                errors.append(diagnostic("APPLICATION_UNKNOWN_EVIDENCE", f"{application_id}: {evidence_id}", application_path))

    for row in requirement_rows:
        requirement_id = row.get("requirement_atom_id", "")
        if row.get("application_node_id") not in application_ids:
            errors.append(diagnostic("REQUIREMENT_UNKNOWN_APPLICATION", requirement_id, application_path))
        requirement_evidence = safe_list(errors, row.get("evidence_ids"), "requirement.evidence_ids", application_path)
        if row.get("evidence_state") == "supported" and not requirement_evidence:
            errors.append(diagnostic("SUPPORTED_REQUIREMENT_EVIDENCE_MISSING", requirement_id, application_path))
        for evidence_id in requirement_evidence:
            if evidence_id not in evidence_ids:
                errors.append(diagnostic("REQUIREMENT_UNKNOWN_EVIDENCE", f"{requirement_id}: {evidence_id}", application_path))

    capabilities = read_sheet_records(workbook, "产品能力")
    capability_by_id = {row.get("capability_id"): row for row in capabilities}
    capability_ids = set(capability_by_id)
    if len(capability_ids) != len(capabilities):
        errors.append(diagnostic("DUPLICATE_CAPABILITY_ID", company_id, workbook))
    for capability in capabilities:
        if capability.get("company_id") != company_id:
            errors.append(diagnostic("CROSS_COMPANY_CAPABILITY", capability.get("capability_id", ""), workbook))
        for fact_id in safe_list(errors, capability.get("product_fact_ids"), "product_fact_ids", workbook):
            fact = facts.get(fact_id)
            if fact_id not in packet_fact_ids or not fact:
                errors.append(diagnostic("UNRESOLVED_PRODUCT_FACT", fact_id, workbook))
            elif not (
                fact.get("company_id") == company_id
                and fact.get("subject_scope") == "own_company"
                and fact.get("statement_kind") == "source_fact"
                and fact.get("evidence_level") == "E3"
                and fact.get("review_status") == "approved"
            ):
                errors.append(diagnostic("PRODUCT_FACT_NOT_APPROVED_E3", fact_id, workbook))

    route_rows = read_sheet_records(workbook, "路线候选")
    route_ids = {row.get("route_candidate_id") for row in route_rows}
    if len(route_ids) != len(route_rows):
        errors.append(diagnostic("DUPLICATE_ROUTE_ID", company_id, workbook))
    route_keys: set[tuple[str, str, str]] = set()
    match_rows = read_sheet_records(workbook, "匹配明细")
    matches_by_route: dict[str, list[dict[str, str]]] = {}
    for match in match_rows:
        match_route_id = match.get("route_candidate_id", "")
        matches_by_route.setdefault(match_route_id, []).append(match)
        if match_route_id not in route_ids:
            errors.append(diagnostic("MATCH_UNKNOWN_ROUTE", match.get("match_id", ""), workbook))
        if match.get("capability_id") not in capability_ids:
            errors.append(diagnostic("MATCH_UNKNOWN_CAPABILITY", match.get("match_id", ""), workbook))
        if match.get("requirement_atom_id") not in requirements:
            errors.append(diagnostic("MATCH_UNKNOWN_REQUIREMENT", match.get("match_id", ""), workbook))
        for field in ("match_state", "condition_compatibility", "process_interface_compatibility"):
            if match.get(field) not in TECHNICAL_STATES:
                errors.append(diagnostic("MATCH_STATE_INVALID", f"{match.get('match_id')}: {field}", workbook))

    for route in route_rows:
        route_id = route.get("route_candidate_id", "")
        route_key = (
            route.get("company_id", ""),
            route.get("product_scope", ""),
            route.get("application_node_id", ""),
        )
        if route_key in route_keys:
            errors.append(diagnostic("DUPLICATE_ROUTE_KEY", " + ".join(route_key), workbook))
        route_keys.add(route_key)
        if route.get("company_id") != company_id:
            errors.append(diagnostic("CROSS_COMPANY_ROUTE", route_id, workbook))
        if route.get("product_scope") != company.get("product_scope"):
            errors.append(diagnostic("ROUTE_PRODUCT_SCOPE_MISMATCH", route_id, workbook))
        status = route.get("map_route_status")
        if status == "已确认可扫描":
            errors.append(diagnostic("ROUTE_STATUS_EXCEEDS_AUTHORITY", route_id, workbook))
        elif status not in MAP_ROUTE_STATUSES:
            errors.append(diagnostic("ROUTE_STATUS_INVALID", route_id, workbook))
        if route.get("evidence_state") not in EVIDENCE_STATES:
            errors.append(diagnostic("ROUTE_EVIDENCE_STATE_INVALID", route_id, workbook))
        if route.get("technical_match_state") not in TECHNICAL_STATES:
            errors.append(diagnostic("ROUTE_TECHNICAL_STATE_INVALID", route_id, workbook))

        product_fact_ids = safe_list(errors, route.get("product_fact_ids"), "product_fact_ids", workbook)
        product_sources = set(safe_list(errors, route.get("product_source_ids"), "product_source_ids", workbook))
        application_sources = set(safe_list(errors, route.get("application_source_groups"), "application_source_groups", workbook))
        if product_sources & application_sources:
            errors.append(diagnostic("CIRCULAR_SOURCE_DEPENDENCY", route_id, workbook))
        for fact_id in product_fact_ids:
            fact = facts.get(fact_id)
            if fact_id not in packet_fact_ids or not fact:
                errors.append(diagnostic("UNRESOLVED_PRODUCT_FACT", fact_id, workbook))
            elif not (
                fact.get("company_id") == company_id
                and fact.get("subject_scope") == "own_company"
                and fact.get("statement_kind") == "source_fact"
                and fact.get("evidence_level") == "E3"
                and fact.get("review_status") == "approved"
            ):
                errors.append(diagnostic("PRODUCT_FACT_NOT_APPROVED_E3", fact_id, workbook))
        application_id = route.get("application_node_id")
        application = applications.get(application_id)
        if application_id not in application_ids:
            errors.append(diagnostic("UNKNOWN_APPLICATION_NODE", route_id, workbook))
        route_taxonomy_ids = safe_list(errors, route.get("taxonomy_node_ids"), "taxonomy_node_ids", workbook)
        for taxonomy_id in route_taxonomy_ids:
            if taxonomy_id not in taxonomy_ids:
                errors.append(diagnostic("UNKNOWN_TAXONOMY_NODE", taxonomy_id, workbook))
        route_output_ids = safe_list(errors, route.get("output_product_ids"), "output_product_ids", workbook)
        for output_id in route_output_ids:
            if output_id not in output_ids:
                errors.append(diagnostic("UNKNOWN_OUTPUT_PRODUCT", output_id, workbook))
        app_evidence = safe_list(errors, route.get("application_evidence_ids"), "application_evidence_ids", workbook)
        for evidence_id in app_evidence:
            if evidence_id not in evidence_ids:
                errors.append(diagnostic("UNKNOWN_APPLICATION_EVIDENCE", evidence_id, workbook))

        if application:
            linked_evidence = set(
                safe_list(errors, application.get("evidence_ids"), "application.evidence_ids", application_path)
            )
            if not set(app_evidence).issubset(linked_evidence):
                errors.append(diagnostic("ROUTE_EVIDENCE_NOT_LINKED_TO_APPLICATION", route_id, workbook))
            linked_outputs = set(
                safe_list(errors, application.get("output_product_ids"), "application.output_product_ids", application_path)
            )
            if not set(route_output_ids).issubset(linked_outputs):
                errors.append(diagnostic("ROUTE_OUTPUT_NOT_LINKED_TO_APPLICATION", route_id, workbook))

        linked_taxonomy: set[str] = set()
        for output_id in route_output_ids:
            output = outputs.get(output_id)
            if output:
                linked_taxonomy.update(
                    safe_list(errors, output.get("taxonomy_node_ids"), "output.taxonomy_node_ids", application_path)
                )
        if not set(route_taxonomy_ids).issubset(linked_taxonomy):
            errors.append(diagnostic("ROUTE_TAXONOMY_NOT_LINKED_TO_OUTPUT", route_id, workbook))

        resolved_source_groups = {
            evidence[evidence_id].get("source_dependency_group", "")
            for evidence_id in app_evidence
            if evidence_id in evidence and evidence[evidence_id].get("source_dependency_group")
        }
        recorded_source_groups = set(
            safe_list(errors, route.get("application_source_groups"), "application_source_groups", workbook)
        )
        if recorded_source_groups != resolved_source_groups:
            errors.append(diagnostic("APPLICATION_SOURCE_GROUP_MISMATCH", route_id, workbook))
        if product_sources & resolved_source_groups:
            errors.append(diagnostic("CIRCULAR_SOURCE_DEPENDENCY", route_id, workbook))

        geography = safe_list(errors, route.get("geography_hypotheses"), "geography_hypotheses", workbook)
        geography_evidence = safe_list(
            errors, route.get("geography_evidence_ids"), "geography_evidence_ids", workbook
        )
        if geography and not geography_evidence:
            errors.append(diagnostic("GEOGRAPHY_HYPOTHESIS_EVIDENCE_REQUIRED", route_id, workbook))
        for evidence_id in geography_evidence:
            item = evidence.get(evidence_id)
            if not item:
                errors.append(diagnostic("UNKNOWN_GEOGRAPHY_EVIDENCE", evidence_id, workbook))
            elif item.get("evidence_state") != "supported":
                errors.append(diagnostic("GEOGRAPHY_EVIDENCE_NOT_SUPPORTED", evidence_id, workbook))

        if status in {"路线候选", "待外部核实"}:
            if not application or not route_output_ids or not route_taxonomy_ids:
                errors.append(diagnostic("ROUTE_CHAIN_INCOMPLETE", route_id, workbook))
            elif application.get("evidence_state") != "supported":
                errors.append(diagnostic("APPLICATION_NODE_NOT_SUPPORTED", route_id, workbook))
            if any(
                evidence.get(evidence_id, {}).get("evidence_state") != "supported"
                for evidence_id in app_evidence
            ):
                errors.append(diagnostic("ROUTE_APPLICATION_EVIDENCE_NOT_SUPPORTED", route_id, workbook))
            if any(
                evidence.get(evidence_id, {}).get("source_subject") == "own_company"
                for evidence_id in app_evidence
            ):
                errors.append(diagnostic("ROUTE_APPLICATION_EVIDENCE_NOT_PRODUCT_NEUTRAL", route_id, workbook))
            for output_id in route_output_ids:
                output = outputs.get(output_id)
                if not output:
                    continue
                output_evidence_ids = safe_list(
                    errors, output.get("evidence_ids"), "output.evidence_ids", application_path
                )
                if output.get("evidence_state") != "supported" or any(
                    evidence.get(evidence_id, {}).get("evidence_state") != "supported"
                    for evidence_id in output_evidence_ids
                ):
                    errors.append(diagnostic("ROUTE_OUTPUT_NOT_SUPPORTED", output_id, workbook))
            if not route.get("use_point_or_process") or not route.get("target_enterprise_activity"):
                errors.append(diagnostic("ROUTE_ENTERPRISE_CHAIN_INCOMPLETE", route_id, workbook))
            if route.get("technical_match_state") != "satisfied":
                errors.append(diagnostic("ROUTE_CANDIDATE_NOT_TECHNICALLY_SATISFIED", route_id, workbook))
            if route.get("evidence_state") != "supported" or not app_evidence:
                errors.append(diagnostic("ROUTE_CANDIDATE_APPLICATION_EVIDENCE_INSUFFICIENT", route_id, workbook))
            if str(route.get("known_limit_conflict", "")).lower() != "false":
                errors.append(diagnostic("ROUTE_CANDIDATE_LIMIT_CONFLICT", route_id, workbook))
            matches = matches_by_route.get(route_id, [])
            hard_requirement_ids = {
                item.get("requirement_atom_id")
                for item in requirement_rows
                if item.get("application_node_id") == application_id
                and item.get("hardness") == "hard"
            }
            matched_requirement_ids = {
                item.get("requirement_atom_id") for item in matches
            }
            if not hard_requirement_ids:
                errors.append(diagnostic("ROUTE_HARD_REQUIREMENT_MISSING", route_id, workbook))
            if not hard_requirement_ids.issubset(matched_requirement_ids):
                missing = sorted(hard_requirement_ids - matched_requirement_ids)
                errors.append(diagnostic("ROUTE_HARD_REQUIREMENT_UNMATCHED", f"{route_id}: {missing}", workbook))
            if not matches:
                errors.append(diagnostic("ROUTE_CANDIDATE_MATCH_DETAIL_MISSING", route_id, workbook))
            elif any(
                match.get("match_state") != "satisfied"
                or match.get("condition_compatibility") != "satisfied"
                or match.get("process_interface_compatibility") != "satisfied"
                or str(match.get("limit_conflict", "")).lower() != "false"
                for match in matches
            ):
                errors.append(diagnostic("ROUTE_CANDIDATE_MATCH_DETAIL_NOT_SATISFIED", route_id, workbook))
            for match in matches:
                requirement = requirements.get(match.get("requirement_atom_id"))
                capability = capability_by_id.get(match.get("capability_id"))
                if requirement and requirement.get("application_node_id") != application_id:
                    errors.append(diagnostic("MATCH_REQUIREMENT_WRONG_APPLICATION", match.get("match_id", ""), workbook))
                if capability and capability.get("product_scope") != route.get("product_scope"):
                    errors.append(diagnostic("MATCH_CAPABILITY_WRONG_PRODUCT_SCOPE", match.get("match_id", ""), workbook))
                match_product_facts = set(
                    safe_list(errors, match.get("product_fact_ids"), "match.product_fact_ids", workbook)
                )
                if not match_product_facts or not match_product_facts.issubset(set(product_fact_ids)):
                    errors.append(diagnostic("MATCH_PRODUCT_FACT_TRACE_INVALID", match.get("match_id", ""), workbook))
                match_application_evidence = set(
                    safe_list(errors, match.get("application_evidence_ids"), "match.application_evidence_ids", workbook)
                )
                if not match_application_evidence or not match_application_evidence.issubset(set(app_evidence)):
                    errors.append(diagnostic("MATCH_APPLICATION_EVIDENCE_TRACE_INVALID", match.get("match_id", ""), workbook))

    for row in read_sheet_records(workbook, "排除暂缓"):
        if not row.get("route_candidate_id") and not row.get("application_node_id"):
            errors.append(diagnostic("ROUTE_EDGE_DISPOSITION_REQUIRED", row.get("disposition_id", ""), workbook))
    coverage_rows = read_sheet_records(workbook, "覆盖台账")
    covered_capability_ids = {
        row.get("coverage_object_id")
        for row in coverage_rows
        if row.get("coverage_object_type") == "capability"
        and row.get("coverage_state") in {"mapped", "deferred", "excluded", "unknown"}
    }
    for capability_id in capability_ids - covered_capability_ids:
        errors.append(diagnostic("CAPABILITY_COVERAGE_MISSING", capability_id, workbook))
    for row in coverage_rows:
        if row.get("company_id") != company_id:
            errors.append(diagnostic("CROSS_COMPANY_COVERAGE", row.get("coverage_id", ""), workbook))
        if row.get("coverage_object_type") == "taxonomy_branch" and row.get("coverage_state") == "excluded":
            errors.append(diagnostic("INDUSTRY_WIDE_EXCLUSION_FORBIDDEN", row.get("coverage_id", ""), workbook))
    for row in read_sheet_records(workbook, "路线交接"):
        if row.get("route_candidate_id") not in route_ids:
            errors.append(diagnostic("HANDOFF_UNKNOWN_ROUTE", row.get("handoff_id", ""), workbook))
        if row.get("target_skill") not in ("", "foreign-trade-customer-development"):
            errors.append(diagnostic("HANDOFF_TARGET_INVALID", row.get("handoff_id", ""), workbook))

    unique = []
    seen = set()
    for item in errors:
        key = (item["code"], item["message"], item.get("path"))
        if key not in seen:
            unique.append(item)
            seen.add(key)
    return {"status": "PASS" if not unique else "FAIL", "errors": unique}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("map_root", type=Path)
    parser.add_argument("--company-id")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    report = validate_workspace(args.map_root.resolve(), args.company_id)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{report['status']}: {len(report['errors'])} diagnostics")
        for item in report["errors"]:
            print(f"{item['code']}: {item['message']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
