#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


CONTRACT_REQUIRED = {
    "research_contract_id",
    "contract_version",
    "contract_state",
    "created_at",
    "frozen_at",
    "owner_authorization_reference",
    "skill_git_commit",
    "map_builder_plugin_version",
    "workflow_director_plugin_version",
    "taxonomy_snapshot_reference",
    "taxonomy_snapshot_sha256",
    "terminal_node_count",
    "research_theme",
    "model_profile_id",
    "model_roles",
    "model_identity_evidence_policy",
    "prompt_template_references_and_hashes",
    "source_scope",
    "search_tool_and_locale",
    "minimum_retrieval_rule",
    "evidence_rule",
    "baseline_method_contract",
    "candidate_method_contract",
    "calibration_case_set_reference_and_hash",
    "batch_rule",
    "control_case_rule",
    "budget_rule",
    "sampling_strata_rule",
    "sampling_seed_rule",
    "confidence_bound_method",
    "hard_gates",
    "allowed_writes",
    "prohibited_actions",
    "full_screening_authorization",
    "application_base_write_authorization",
}
SCREENING_RESULTS = {"hypothesis_formed", "ambiguous", "no_hypothesis_formed"}
WORK_STATES = {"not_screened", "screened", "evidence_expansion_required", "evidence_expanded", "audit_reopened"}
EVIDENCE_STATES = {"supported", "hypothesis", "unknown", "conflicted"}
QUERY_GROUPS = {"industry_output_or_process", "mechanism_use_point_and_cross_domain_synonyms"}
PROMPT_ROLES = {
    "baseline",
    "A_screening",
    "A_evidence",
    "B_review",
    "C_dispute",
    "C_reverse_audit",
}
REQUIRED_HARD_GATES = {
    "known_positive_recall_100_percent",
    "unsupported_supported_count_zero",
    "circular_source_supported_count_zero",
    "cross_company_contamination_zero",
    "claim_inflation_zero",
    "status_axis_mixing_zero",
    "deep_expansion_reduction_at_least_20_percent",
    "reproducible_run",
}
REQUIRED_PROHIBITIONS = {
    "write_shared_application_base_during_calibration",
    "company_matching_before_semantic_stage_pass",
    "customer_search_before_semantic_stage_pass",
    "silent_model_substitution",
    "automatic_external_model_claim_without_connector",
}
FORBIDDEN_B_KEYS = {
    "full_reasoning",
    "chain_of_thought",
    "model_a_confidence",
    "business_recommendation",
    "company_name",
    "company_product",
    "vote_count",
}
MODEL_C_TRIGGERS = {
    "a_b_dispute",
    "source_conflict",
    "claim_inflation_risk",
    "systematic_term_bias",
    "independent_counterevidence",
    "reverse_audit_sample",
}
MODEL_TRANSPORTS = {"manual_external_handoff", "codex_task", "authorized_api"}
IDENTITY_LEVEL_RANK = {
    "unverified": 0,
    "operator_attested": 1,
    "ui_observed": 2,
    "platform_verified": 3,
    "connector_verified": 4,
}
IDENTITY_TYPE_LEVEL = {
    "unknown": "unverified",
    "self_reported": "unverified",
    "user_attested": "operator_attested",
    "ui_observed": "ui_observed",
    "platform_export": "platform_verified",
    "connector_verified": "connector_verified",
}
MODEL_REQUIRED_FIELDS = {
    "task_id",
    "research_contract_id",
    "contract_version",
    "input_sha256",
    "declared_model_name",
    "result_state",
    "reason_codes",
    "source_access_results",
    "structured_findings",
    "unknowns",
}
MODEL_OPTIONAL_OR_UNKNOWN_FIELDS = {
    "actual_model_id_or_unknown",
    "provider_or_unknown",
    "model_reported_run_id",
    "model_reported_started_at",
    "model_reported_returned_at",
}
RECEIVER_OWNED_FIELDS = {
    "receipt_id",
    "received_at",
    "raw_return_reference",
    "raw_return_sha256",
    "identity_evidence",
    "executor_metadata",
    "acceptance_state",
}
MODEL_RETURN_FIELDS = MODEL_REQUIRED_FIELDS | MODEL_OPTIONAL_OR_UNKNOWN_FIELDS
MODEL_RECEIPT_FIELDS = {
    "receipt_id",
    "task_id",
    "research_contract_id",
    "contract_version",
    "transport",
    "raw_return_reference",
    "raw_return_sha256",
    "received_at",
    "identity_evidence",
    "executor_metadata",
    "acceptance_state",
    "reason_codes",
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{number}: record is not an object")
        rows.append(value)
    return rows


def nested_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        result = set(value)
        for item in value.values():
            result.update(nested_keys(item))
        return result
    if isinstance(value, list):
        result: set[str] = set()
        for item in value:
            result.update(nested_keys(item))
        return result
    return set()


def add(errors: list[dict], code: str, detail: str) -> None:
    errors.append({"code": code, "detail": detail})


def nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def sha256_text(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def canonical_json_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def positive_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def frozen_contract_completeness_errors(contract: object) -> list[str]:
    if not isinstance(contract, dict):
        return ["semantic_research_contract must be an object"]
    problems: list[str] = []
    missing = sorted(CONTRACT_REQUIRED - set(contract))
    if missing:
        problems.append("missing:" + ",".join(missing))

    for field in (
        "research_contract_id",
        "contract_version",
        "created_at",
        "frozen_at",
        "owner_authorization_reference",
        "skill_git_commit",
        "map_builder_plugin_version",
        "workflow_director_plugin_version",
        "taxonomy_snapshot_reference",
        "model_profile_id",
    ):
        if not nonempty_text(contract.get(field)):
            problems.append(f"{field}:empty")
    if contract.get("contract_state") != "frozen":
        problems.append("contract_state:not_frozen")
    if not sha256_text(contract.get("taxonomy_snapshot_sha256")):
        problems.append("taxonomy_snapshot_sha256:invalid")
    if not isinstance(contract.get("terminal_node_count"), int) or contract.get("terminal_node_count", 0) <= 0:
        problems.append("terminal_node_count:invalid")

    identity_policy = contract.get("model_identity_evidence_policy")
    if not isinstance(identity_policy, dict) or set(identity_policy) != {"A", "B", "C"}:
        problems.append("model_identity_evidence_policy:invalid")
    else:
        for role, policy in identity_policy.items():
            if (
                not isinstance(policy, dict)
                or policy.get("minimum_level") not in IDENTITY_LEVEL_RANK
                or not isinstance(policy.get("accepted_types"), list)
                or not policy.get("accepted_types")
                or not all(item in IDENTITY_TYPE_LEVEL for item in policy.get("accepted_types", []))
            ):
                problems.append(f"model_identity_evidence_policy.{role}:invalid")

    theme = contract.get("research_theme")
    if not isinstance(theme, dict):
        problems.append("research_theme:invalid")
    else:
        for field in ("theme_id", "mechanism", "form_or_use_point"):
            if not nonempty_text(theme.get(field)):
                problems.append(f"research_theme.{field}:empty")
        exclusions = theme.get("exclusions")
        if not isinstance(exclusions, list) or not exclusions or not all(nonempty_text(item) for item in exclusions):
            problems.append("research_theme.exclusions:empty_or_invalid")
        if theme.get("product_neutrality_review") != "PASS":
            problems.append("research_theme.product_neutrality_review:not_PASS")

    roles = contract.get("model_roles")
    expected_roles = {
        "A": "generate_search_and_package",
        "B": "blind_source_review",
        "C": "dispute_and_reverse_audit",
    }
    if roles != expected_roles:
        problems.append("model_roles:invalid")

    prompt_rows = contract.get("prompt_template_references_and_hashes")
    if not isinstance(prompt_rows, list):
        problems.append("prompt_template_references_and_hashes:invalid")
    else:
        prompt_roles = set()
        for row in prompt_rows:
            if not isinstance(row, dict):
                problems.append("prompt_template_reference:not_object")
                continue
            prompt_roles.add(row.get("role"))
            if not nonempty_text(row.get("reference")) or not sha256_text(row.get("sha256")):
                problems.append(f"prompt_template_reference:invalid:{row.get('role')}")
        if prompt_roles != PROMPT_ROLES:
            problems.append("prompt_template_roles:incomplete")

    source_scope = contract.get("source_scope")
    if not isinstance(source_scope, list) or not source_scope or not all(nonempty_text(item) for item in source_scope):
        problems.append("source_scope:empty_or_invalid")
    locale = contract.get("search_tool_and_locale")
    if not isinstance(locale, dict) or not nonempty_text(locale.get("tool")):
        problems.append("search_tool_and_locale.tool:empty")
    else:
        for field in ("languages", "regions"):
            values = locale.get(field)
            if not isinstance(values, list) or not values or not all(nonempty_text(item) for item in values):
                problems.append(f"search_tool_and_locale.{field}:empty_or_invalid")

    retrieval = contract.get("minimum_retrieval_rule")
    if not isinstance(retrieval, dict) or set(retrieval.get("query_groups") or []) != QUERY_GROUPS:
        problems.append("minimum_retrieval_rule.query_groups:invalid")
    elif any(
        not positive_number(retrieval.get(field))
        for field in (
            "inspect_top_distinct_results_per_group",
            "open_potential_clues_per_group_max",
            "source_scarce_distinct_accessible_node_specific_results_below",
        )
    ):
        problems.append("minimum_retrieval_rule:invalid_limits")

    evidence_rule = contract.get("evidence_rule")
    if not isinstance(evidence_rule, dict) or any(
        evidence_rule.get(field) is not True
        for field in (
            "supported_requires_direct_source",
            "supported_requires_model_b_pass",
            "model_consensus_is_not_evidence",
        )
    ):
        problems.append("evidence_rule:invalid")
    if contract.get("baseline_method_contract") != "baseline_full_depth":
        problems.append("baseline_method_contract:invalid")
    if contract.get("candidate_method_contract") != "candidate_screen_then_expand":
        problems.append("candidate_method_contract:invalid")

    case_set = contract.get("calibration_case_set_reference_and_hash")
    if not isinstance(case_set, dict) or not nonempty_text(case_set.get("reference")) or not sha256_text(case_set.get("sha256")):
        problems.append("calibration_case_set_reference_and_hash:invalid")
    batch = contract.get("batch_rule")
    if not isinstance(batch, dict) or not isinstance(batch.get("batch_size"), int) or batch.get("batch_size", 0) <= 0:
        problems.append("batch_rule.batch_size:invalid")
    elif batch.get("stop_after_each_batch") is not True or batch.get("trigger_rate_is_diagnostic_not_pass_gate") is not True:
        problems.append("batch_rule:invalid")
    controls = contract.get("control_case_rule")
    if not isinstance(controls, dict) or not controls.get("case_ids") or controls.get("drift_requires_pause") is not True:
        problems.append("control_case_rule:invalid")
    budget = contract.get("budget_rule")
    if not isinstance(budget, dict) or any(
        not positive_number(budget.get(field))
        for field in ("token_limit", "search_limit", "time_limit_minutes")
    ) or budget.get("budget_stop_keeps_unprocessed_nodes_not_screened") is not True:
        problems.append("budget_rule:invalid")

    strata = contract.get("sampling_strata_rule")
    if not isinstance(strata, list) or set(strata) != {
        "signal_conflict",
        "nec_or_miscellaneous",
        "source_scarce",
        "semantic_ambiguity",
        "ordinary",
    }:
        problems.append("sampling_strata_rule:invalid")
    seed = contract.get("sampling_seed_rule")
    if not isinstance(seed, dict) or not nonempty_text(seed.get("seed")) or seed.get("algorithm") != "python_random_v1_srswor":
        problems.append("sampling_seed_rule:invalid")
    confidence = contract.get("confidence_bound_method")
    if not isinstance(confidence, dict) or confidence.get("stratum_method") != "exact_one_sided_hypergeometric_inversion" or confidence.get("multiple_strata_correction") != "Bonferroni" or confidence.get("required_weighted_upper_bound") != 0.05 or confidence.get("family_alpha") != 0.05:
        problems.append("confidence_bound_method:invalid")

    if set(contract.get("hard_gates") or []) != REQUIRED_HARD_GATES:
        problems.append("hard_gates:invalid")
    writes = contract.get("allowed_writes")
    if not isinstance(writes, list) or not writes or not all(nonempty_text(item) for item in writes):
        problems.append("allowed_writes:empty_or_invalid")
    if not REQUIRED_PROHIBITIONS.issubset(set(contract.get("prohibited_actions") or [])):
        problems.append("prohibited_actions:incomplete")
    for field in ("full_screening_authorization", "application_base_write_authorization"):
        if not isinstance(contract.get(field), bool):
            problems.append(f"{field}:not_boolean")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an RC2 semantic research workspace without mutating it.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    errors: list[dict] = []

    contract_path = workspace / "00-合同" / "semantic-research-contract.json"
    manifest_path = workspace / "00-合同" / "workspace-manifest.json"
    if not contract_path.is_file():
        add(errors, "CONTRACT_MISSING", str(contract_path))
        contract = {}
    else:
        try:
            contract = load_json(contract_path)["semantic_research_contract"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            add(errors, "CONTRACT_INVALID", str(exc))
            contract = {}

    if not manifest_path.is_file():
        add(errors, "WORKSPACE_MANIFEST_MISSING", str(manifest_path))
    elif contract_path.is_file():
        try:
            manifest = load_json(manifest_path)
            actual_contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
            if not isinstance(manifest, dict) or manifest.get("contract_sha256") != actual_contract_hash:
                add(errors, "CONTRACT_HASH_MISMATCH", actual_contract_hash)
        except (json.JSONDecodeError, OSError) as exc:
            add(errors, "WORKSPACE_MANIFEST_INVALID", str(exc))

    completeness = frozen_contract_completeness_errors(contract)
    if completeness:
        add(errors, "CONTRACT_INCOMPLETE", ";".join(completeness))
    contract_id = contract.get("research_contract_id")
    contract_version = contract.get("contract_version")

    def verify_reference(reference: object, expected_hash: object, code_prefix: str) -> Path | None:
        if not nonempty_text(reference) or not sha256_text(expected_hash):
            add(errors, f"{code_prefix}_REFERENCE_INVALID", repr(reference))
            return None
        path = Path(reference)
        if not path.is_absolute():
            path = workspace / path
        path = path.resolve()
        if not path.is_file():
            add(errors, f"{code_prefix}_MISSING", str(path))
            return None
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            add(errors, f"{code_prefix}_HASH_MISMATCH", str(path))
        return path

    taxonomy_path = verify_reference(
        contract.get("taxonomy_snapshot_reference"),
        contract.get("taxonomy_snapshot_sha256"),
        "TAXONOMY_SNAPSHOT",
    )
    if taxonomy_path:
        try:
            taxonomy_payload = load_json(taxonomy_path)
            if not isinstance(taxonomy_payload, dict) or taxonomy_payload.get("terminal_node_count") != contract.get("terminal_node_count"):
                add(errors, "TAXONOMY_SNAPSHOT_COUNT_MISMATCH", str(taxonomy_path))
        except (json.JSONDecodeError, OSError) as exc:
            add(errors, "TAXONOMY_SNAPSHOT_INVALID", str(exc))

    case_set = contract.get("calibration_case_set_reference_and_hash")
    if isinstance(case_set, dict):
        case_path = verify_reference(
            case_set.get("reference"), case_set.get("sha256"), "CALIBRATION_CASE_SET"
        )
        if case_path:
            try:
                first_record = next((row for row in load_jsonl(case_path) if row.get("record_type") == "case_set_contract"), None)
                if not first_record or first_record.get("case_count") != 40:
                    add(errors, "CALIBRATION_CASE_SET_INVALID", str(case_path))
            except (json.JSONDecodeError, OSError, ValueError) as exc:
                add(errors, "CALIBRATION_CASE_SET_INVALID", str(exc))

    prompt_rows = contract.get("prompt_template_references_and_hashes")
    if isinstance(prompt_rows, list):
        for row in prompt_rows:
            if isinstance(row, dict):
                verify_reference(row.get("reference"), row.get("sha256"), "PROMPT_TEMPLATE")

    allowed_writes = contract.get("allowed_writes", []) if isinstance(contract, dict) else []
    shared_write = any("02-共享应用知识" in str(item) or "industry-application-base.xlsx" in str(item) for item in allowed_writes)
    if shared_write and not contract.get("application_base_write_authorization", False):
        add(errors, "CALIBRATION_WRITE_SCOPE_VIOLATION", "shared application base appears in allowed_writes without authorization")
    if contract.get("application_base_write_authorization") is True and contract.get("full_screening_authorization") is not True:
        add(errors, "AUTHORIZATION_ORDER_VIOLATION", "application base write cannot precede full screening authorization")
    research_marker = f"05-工作区/行业语义研究/{contract_id}"
    for item in allowed_writes if isinstance(allowed_writes, list) else []:
        normalized = str(item).replace("\\", "/")
        is_research_path = research_marker in normalized
        is_authorized_shared_path = (
            contract.get("application_base_write_authorization") is True
            and contract.get("full_screening_authorization") is True
            and ("02-共享应用知识" in normalized or normalized.endswith("industry-application-base.xlsx"))
        )
        if not is_research_path and not is_authorized_shared_path:
            add(errors, "WRITE_SCOPE_VIOLATION", normalized)

    screening_path = workspace / "03-运行原始记录" / "candidate" / "screening-records.jsonl"
    if screening_path.is_file():
        try:
            screening_records = load_jsonl(screening_path)
        except (json.JSONDecodeError, ValueError) as exc:
            add(errors, "SCREENING_RECORDS_INVALID", str(exc))
            screening_records = []
        for record in screening_records:
            node_id = str(record.get("industry_node_id"))
            if record.get("research_contract_id") != contract_id or record.get("contract_version") != contract_version:
                add(errors, "CONTRACT_VERSION_MISMATCH", node_id)
            if record.get("screening_result") not in SCREENING_RESULTS:
                add(errors, "SCREENING_RESULT_INVALID", node_id)
            if record.get("semantic_work_state") not in WORK_STATES:
                add(errors, "SEMANTIC_WORK_STATE_INVALID", node_id)
            if record.get("evidence_state") not in EVIDENCE_STATES:
                add(errors, "EVIDENCE_STATE_INVALID", node_id)
            if record.get("stop_reason") == "budget_stop" and record.get("semantic_work_state") != "not_screened":
                add(errors, "BUDGET_STOP_STATE_INFLATION", node_id)
            if record.get("screening_result") == "no_hypothesis_formed":
                queries = record.get("search_queries") or []
                groups = {item.get("group") for item in queries if isinstance(item, dict)}
                inspected = record.get("inspected_result_references") or []
                inspected_groups = {item.get("group") for item in inspected if isinstance(item, dict)}
                counts_ok = True
                actual_references: dict[str, set[str]] = {group: set() for group in QUERY_GROUPS}
                for item in inspected:
                    if not isinstance(item, dict):
                        counts_ok = False
                        continue
                    group = item.get("group")
                    reference = item.get("reference")
                    if group in QUERY_GROUPS and nonempty_text(reference):
                        actual_references[group].add(reference.strip())
                    else:
                        counts_ok = False
                for query in queries:
                    if not isinstance(query, dict):
                        counts_ok = False
                        continue
                    group = query.get("group")
                    if group not in QUERY_GROUPS or not nonempty_text(query.get("query")):
                        counts_ok = False
                        continue
                    available = query.get("available_distinct_result_count")
                    checked = query.get("inspected_distinct_result_count")
                    actual_count = len(actual_references[group])
                    if (
                        not isinstance(available, int)
                        or isinstance(available, bool)
                        or available < 0
                        or not isinstance(checked, int)
                        or isinstance(checked, bool)
                        or checked < min(5, available)
                        or checked > available
                        or checked > actual_count
                        or actual_count < min(5, available)
                    ):
                        counts_ok = False
                if groups != QUERY_GROUPS or inspected_groups != QUERY_GROUPS or not counts_ok:
                    add(errors, "SCREENING_MINIMUM_RETRIEVAL_NOT_MET", node_id)

    evidence_path = workspace / "05-证据包" / "evidence-records.jsonl"
    if evidence_path.is_file():
        try:
            evidence_records = load_jsonl(evidence_path)
        except (json.JSONDecodeError, ValueError) as exc:
            add(errors, "EVIDENCE_RECORDS_INVALID", str(exc))
            evidence_records = []
        for record in evidence_records:
            if record.get("research_contract_id") != contract_id or record.get("contract_version") != contract_version:
                add(errors, "CONTRACT_VERSION_MISMATCH", str(record.get("claim_id")))
            if record.get("evidence_state") == "supported":
                gate = (
                    record.get("direct_source_support") is True
                    and record.get("source_location_present") is True
                    and record.get("snapshot_or_live_source_verified") is True
                    and record.get("model_b_review") == "PASS"
                    and record.get("claim_scope_within_source") is True
                    and record.get("circular_source") is False
                    and record.get("unresolved_counterevidence") is False
                )
                if not gate:
                    add(errors, "SUPPORTED_EVIDENCE_GATE_FAILED", str(record.get("claim_id")))

    handoff_root = workspace / "04-模型交接"
    model_tasks: dict[str, dict] = {}
    if handoff_root.is_dir():
        for path in sorted(handoff_root.rglob("*.json")):
            try:
                payload = load_json(path)
            except json.JSONDecodeError as exc:
                add(errors, "MODEL_PACKET_INVALID", f"{path.name}: {exc}")
                continue
            task = payload.get("semantic_model_task", {}) if isinstance(payload, dict) else {}
            if not task:
                continue
            task_id = task.get("task_id")
            if not nonempty_text(task_id):
                add(errors, "MODEL_TASK_INVALID", f"{path.relative_to(handoff_root)}: missing task_id")
                continue
            if task_id in model_tasks:
                add(errors, "MODEL_TASK_DUPLICATE", str(task_id))
            else:
                model_tasks[task_id] = task
            role = task.get("role")
            allowed_modes = {
                "A": {"baseline_full_depth", "screening", "evidence_expansion"},
                "B": {"blind_source_review"},
                "C": {"dispute", "reverse_audit"},
            }
            identity_policy = task.get("identity_evidence_policy")
            expected_return_schema = task.get("expected_return_schema")
            field_ownership = task.get("field_ownership")
            manual_rules = task.get("manual_transport_rules")
            visible_input = task.get("visible_input")
            input_hash_ok = (
                task.get("input_hash_algorithm") == "sha256_canonical_json_v1"
                and visible_input is not None
                and task.get("input_sha256") == canonical_json_sha256(visible_input)
            )
            if not input_hash_ok:
                add(
                    errors,
                    "MODEL_TASK_INPUT_HASH_MISMATCH",
                    f"{path.relative_to(handoff_root)}: {task_id}",
                )
            task_ok = (
                payload.get("schema_version") == "1.1"
                and
                task.get("research_contract_id") == contract_id
                and task.get("contract_version") == contract_version
                and sha256_text(task.get("input_sha256"))
                and input_hash_ok
                and role in allowed_modes
                and task.get("mode") in allowed_modes.get(role, set())
                and nonempty_text(task.get("declared_model_name"))
                and task.get("output_contract") == "semantic_model_return"
                and task.get("transport") in MODEL_TRANSPORTS
                and nonempty_text(task.get("issued_at"))
                and isinstance(identity_policy, dict)
                and identity_policy
                == contract.get("model_identity_evidence_policy", {}).get(role)
                and identity_policy.get("minimum_level") in IDENTITY_LEVEL_RANK
                and isinstance(identity_policy.get("accepted_types"), list)
                and bool(identity_policy.get("accepted_types"))
                and all(
                    item in IDENTITY_TYPE_LEVEL
                    for item in identity_policy.get("accepted_types", [])
                )
                and isinstance(expected_return_schema, dict)
                and expected_return_schema.get("schema_version") == "1.1"
                and isinstance(expected_return_schema.get("semantic_model_return"), dict)
                and set(expected_return_schema.get("semantic_model_return", {}))
                == MODEL_RETURN_FIELDS
                and isinstance(field_ownership, dict)
                and set(field_ownership) == {
                    "model_required_fields",
                    "model_optional_or_unknown_fields",
                    "receiver_owned_fields",
                }
                and set(field_ownership.get("model_required_fields", []))
                == MODEL_REQUIRED_FIELDS
                and set(field_ownership.get("model_optional_or_unknown_fields", []))
                == MODEL_OPTIONAL_OR_UNKNOWN_FIELDS
                and set(field_ownership.get("receiver_owned_fields", []))
                == RECEIVER_OWNED_FIELDS
                and isinstance(manual_rules, dict)
                and manual_rules.get("return_raw_json_only") is True
                and manual_rules.get("unknown_runtime_metadata_must_be_null") is True
                and manual_rules.get("receiver_must_not_backfill_model_reported_fields") is True
                and isinstance(task.get("prohibited_inputs"), list)
                and isinstance(task.get("prohibited_actions"), list)
                and isinstance(task.get("source_permissions"), list)
                and nonempty_text(task.get("stop_condition"))
            )
            if not task_ok:
                add(errors, "MODEL_TASK_INVALID", f"{path.relative_to(handoff_root)}: {task_id}")
            if role == "C":
                trigger = task.get("trigger_reason")
                trigger_ok = trigger in MODEL_C_TRIGGERS and (
                    (task.get("mode") == "reverse_audit" and trigger == "reverse_audit_sample")
                    or (task.get("mode") == "dispute" and trigger != "reverse_audit_sample")
                )
                if not trigger_ok:
                    add(errors, "MODEL_C_TRIGGER_INVALID", f"{path.relative_to(handoff_root)}: {trigger}")
            if task.get("role") == "B":
                leaked = sorted(FORBIDDEN_B_KEYS & nested_keys(task))
                if leaked:
                    add(errors, "MODEL_B_BLINDING_VIOLATION", f"{path.relative_to(handoff_root)}: {','.join(leaked)}")

    receipts: dict[str, dict] = {}
    receipt_return_paths: dict[str, Path] = {}
    receipt_validity: dict[str, bool] = {}
    if handoff_root.is_dir():
        for path in sorted(handoff_root.rglob("*.json")):
            try:
                payload = load_json(path)
            except json.JSONDecodeError:
                continue
            receipt = payload.get("semantic_model_receipt", {}) if isinstance(payload, dict) else {}
            if not receipt:
                continue
            task_id = receipt.get("task_id")
            if not nonempty_text(task_id):
                add(errors, "MODEL_RECEIPT_INVALID", f"{path.relative_to(handoff_root)}: missing task_id")
                continue
            if task_id in receipts:
                add(errors, "MODEL_RECEIPT_DUPLICATE", str(task_id))
                continue
            receipts[task_id] = receipt
            task = model_tasks.get(task_id)
            valid = True
            if payload.get("schema_version") != "1.1" or set(receipt) != MODEL_RECEIPT_FIELDS:
                add(errors, "MODEL_RECEIPT_INVALID", f"{path.name}: schema or fields")
                valid = False
            if task is None:
                add(errors, "MODEL_RECEIPT_TASK_MISSING", f"{path.name}: {task_id}")
                receipt_validity[task_id] = False
                continue
            for field in ("research_contract_id", "contract_version", "transport"):
                if receipt.get(field) != task.get(field):
                    add(errors, "MODEL_RECEIPT_MISMATCH", f"{task_id}: {field}")
                    valid = False
            if not nonempty_text(receipt.get("receipt_id")) or not nonempty_text(receipt.get("received_at")):
                add(errors, "MODEL_RECEIPT_INVALID", f"{path.name}: {task_id}")
                valid = False

            raw_reference = receipt.get("raw_return_reference")
            raw_path: Path | None = None
            if nonempty_text(raw_reference):
                raw_path = Path(raw_reference)
                if not raw_path.is_absolute():
                    raw_path = workspace / raw_path
                raw_path = raw_path.resolve()
                try:
                    raw_path.relative_to(workspace)
                except ValueError:
                    add(errors, "MODEL_RECEIPT_RETURN_REFERENCE_OUTSIDE_WORKSPACE", str(raw_path))
                    raw_path = None
                    valid = False
            else:
                add(errors, "MODEL_RECEIPT_INVALID", f"{path.name}: missing raw_return_reference")
                valid = False
            if raw_path is None or not raw_path.is_file():
                add(errors, "MODEL_RECEIPT_RETURN_MISSING", str(raw_path))
                valid = False
            else:
                receipt_return_paths[task_id] = raw_path
                actual_return_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
                if receipt.get("raw_return_sha256") != actual_return_hash:
                    add(errors, "MODEL_RECEIPT_RETURN_HASH_MISMATCH", f"{task_id}: {raw_path}")
                    valid = False

            identity = receipt.get("identity_evidence")
            policy = task.get("identity_evidence_policy", {})
            if not isinstance(identity, dict):
                add(errors, "MODEL_RECEIPT_IDENTITY_INVALID", str(task_id))
                valid = False
            else:
                evidence_type = identity.get("evidence_type")
                verification_level = identity.get("verification_level")
                expected_level = IDENTITY_TYPE_LEVEL.get(evidence_type)
                minimum_level = policy.get("minimum_level")
                identity_ok = (
                    evidence_type in policy.get("accepted_types", [])
                    and expected_level == verification_level
                    and verification_level in IDENTITY_LEVEL_RANK
                    and minimum_level in IDENTITY_LEVEL_RANK
                    and IDENTITY_LEVEL_RANK.get(verification_level, 0)
                    >= IDENTITY_LEVEL_RANK.get(minimum_level, 99)
                    and nonempty_text(identity.get("observed_model_label_or_unknown"))
                    and identity.get("observed_model_label_or_unknown") != "unknown"
                    and identity.get("observed_model_label_or_unknown")
                    == task.get("declared_model_name")
                    and nonempty_text(identity.get("evidence_reference_or_null"))
                )
                if not identity_ok:
                    add(errors, "MODEL_RECEIPT_IDENTITY_UNVERIFIED", str(task_id))
                    valid = False

            executor = receipt.get("executor_metadata")
            if not isinstance(executor, dict):
                add(errors, "MODEL_RECEIPT_EXECUTOR_METADATA_INVALID", str(task_id))
                valid = False
            elif task.get("transport") == "manual_external_handoff":
                manual_executor_ok = (
                    executor.get("executor_run_id_or_null") is None
                    and executor.get("executor_started_at_or_null") is None
                    and executor.get("executor_returned_at_or_null") is None
                    and executor.get("provenance") == "none"
                )
                if not manual_executor_ok:
                    add(errors, "MODEL_RECEIPT_MANUAL_EXECUTOR_METADATA_INVALID", str(task_id))
                    valid = False
            else:
                connected_executor_ok = (
                    nonempty_text(executor.get("executor_run_id_or_null"))
                    and nonempty_text(executor.get("executor_started_at_or_null"))
                    and nonempty_text(executor.get("executor_returned_at_or_null"))
                    and executor.get("provenance") == task.get("transport")
                )
                if not connected_executor_ok:
                    add(errors, "MODEL_RECEIPT_CONNECTED_EXECUTOR_METADATA_INVALID", str(task_id))
                    valid = False
            if (
                receipt.get("acceptance_state") not in {"PASS", "FAIL", "UNVERIFIED"}
                or not isinstance(receipt.get("reason_codes"), list)
                or not receipt.get("reason_codes")
            ):
                add(errors, "MODEL_RECEIPT_INVALID", f"{path.name}: {task_id}")
                valid = False
            if receipt.get("acceptance_state") != "PASS":
                add(errors, "MODEL_RETURN_NOT_ADMISSIBLE", str(task_id))
                valid = False
            receipt_validity[task_id] = valid

    return_paths: list[Path] = []
    for root in (workspace / "03-运行原始记录", handoff_root):
        if root.is_dir():
            return_paths.extend(sorted(root.rglob("*.json")))
    seen_return_task_ids: set[str] = set()
    for path in return_paths:
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        returned = payload.get("semantic_model_return", {}) if isinstance(payload, dict) else {}
        if not returned:
            continue
        task_id = returned.get("task_id")
        return_key = str(task_id)
        if return_key in seen_return_task_ids:
            add(errors, "MODEL_RETURN_DUPLICATE", return_key)
        seen_return_task_ids.add(return_key)
        task = model_tasks.get(task_id)
        if task is None:
            add(errors, "MODEL_RETURN_TASK_MISSING", f"{path.name}: {task_id}")
            continue
        mismatch_fields = []
        for field in ("research_contract_id", "contract_version", "input_sha256", "declared_model_name"):
            if returned.get(field) != task.get(field):
                mismatch_fields.append(field)
        if mismatch_fields:
            add(errors, "MODEL_RETURN_MISMATCH", f"{task_id}: {','.join(mismatch_fields)}")
        return_state = returned.get("result_state")
        optional_runtime_fields = (
            "model_reported_run_id",
            "model_reported_started_at",
            "model_reported_returned_at",
        )
        optional_runtime_ok = all(
            returned.get(field) is None or nonempty_text(returned.get(field))
            for field in optional_runtime_fields
        )
        return_shape_ok = (
            payload.get("schema_version") == "1.1"
            and set(returned) == MODEL_RETURN_FIELDS
            and return_state in {"PASS", "FAIL", "UNVERIFIED"}
            and nonempty_text(returned.get("actual_model_id_or_unknown"))
            and nonempty_text(returned.get("provider_or_unknown"))
            and optional_runtime_ok
            and isinstance(returned.get("reason_codes"), list)
            and bool(returned.get("reason_codes"))
            and isinstance(returned.get("source_access_results"), list)
            and isinstance(returned.get("structured_findings"), list)
            and isinstance(returned.get("unknowns"), list)
        )
        if not return_shape_ok:
            add(errors, "MODEL_RETURN_INVALID", f"{path.name}: {task_id}")
        receiver_owned_fields = set(task.get("field_ownership", {}).get("receiver_owned_fields", []))
        receiver_field_leaks = sorted(receiver_owned_fields & set(returned))
        if receiver_field_leaks:
            add(errors, "MODEL_RETURN_RECEIVER_FIELD_VIOLATION", f"{path.name}: {','.join(receiver_field_leaks)}")
        receipt = receipts.get(task_id)
        if receipt is None:
            add(errors, "MODEL_RECEIPT_MISSING", f"{path.name}: {task_id}")
        else:
            expected_return_path = receipt_return_paths.get(task_id)
            if expected_return_path != path.resolve():
                add(errors, "MODEL_RECEIPT_RETURN_REFERENCE_MISMATCH", f"{task_id}: {path}")
            if not receipt_validity.get(task_id, False):
                add(errors, "MODEL_RETURN_NOT_ADMISSIBLE", str(task_id))
        if task.get("role") == "B":
            leaked = sorted(FORBIDDEN_B_KEYS & nested_keys(returned))
            if leaked:
                add(errors, "MODEL_B_BLINDING_VIOLATION", f"{path.name}: {','.join(leaked)}")

    report = {"status": "FAIL" if errors else "PASS", "errors": errors, "workspace": str(workspace)}
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(report["status"])
        for error in errors:
            print(f"{error['code']}: {error['detail']}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
