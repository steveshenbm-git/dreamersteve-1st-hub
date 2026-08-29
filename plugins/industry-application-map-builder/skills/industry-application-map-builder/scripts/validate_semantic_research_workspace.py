#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from pathlib import PurePosixPath

from validate_terminology_bridge import load_rows as load_terminology_rows
from validate_terminology_bridge import validate_rows as validate_terminology_rows
from content_first_visible_case_schema import frozen_visible_case_errors, visible_case_projection
from r4_adjudicated_truth_contract import (
    BETA5_CASE_PACKAGE_CONTRACT_VERSION as CASE_PACKAGE_CONTRACT_VERSION,
    BETA5_MAP_BUILDER_PLUGIN_VERSION as MAP_BUILDER_PLUGIN_VERSION,
    BETA5_TRUTH_SCORECARD_CONTRACT_VERSION as TRUTH_SCORECARD_CONTRACT_VERSION,
    DIRECTOR_PLUGIN_VERSION,
    MINIMUM_NEW_UNSEEN_ACCEPTED_POSITIVES,
    SAMPLING_CATEGORY_COUNTS,
    SELECTION_ORIGIN_COUNTS,
    derive_truth_summary,
    validate_adjudicated_truth_rows,
    validate_beta5_case_rows,
    validate_positive_holdout_floor,
    validate_truth_summary_integrity,
)
from r4_case_package_contract import (
    aware_datetime,
    taxonomy_identifier_key,
    taxonomy_level_number,
    validate_complete_truth_rows,
)


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
    "case_preparation_gate",
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
CONTENT_FIRST_REQUIRED = {
    "created_at",
    "owner_authorization_reference",
    "skill_git_commit",
    "workflow_director_plugin_version",
    "execution_mode",
    "terminology_architecture",
    "calibration_case_policy",
    "retrieval_efficiency_gates",
    "content_first_policy",
    "source_truth_package_reference",
    "source_truth_package_sha256",
    "adjudicated_truth_summary",
    "visible_case_set_reference_and_hash",
    "visible_case_freeze_receipt_reference_and_hash",
    "execution_authorized",
    "paired_execution_contract",
    "r3_case_source_manifest_reference_and_hash",
    "full_screening_authorization",
    "full_screening_authorization_reference",
    "prohibited_actions",
    "map_builder_plugin_version",
    "case_package_contract_version",
}
R4_BASELINE_METHOD = "baseline_full_depth_v1"
R4_CANDIDATE_METHOD = "screen_then_expand_v2"
CONTENT_FIRST_CONCEPT_ROLES = {
    "industry_output",
    "material_form",
    "phase_relation",
    "process_action",
    "use_point",
    "exclusion",
}
CONTENT_FIRST_CATEGORY_COUNTS = SAMPLING_CATEGORY_COUNTS
CONTENT_FIRST_SELECTION_ORIGIN_COUNTS = SELECTION_ORIGIN_COUNTS
RETAINED_PROVENANCE_KEYS = {
    "development_regression_only",
    "selection_origin",
    "r3_source_case_id",
    "source_snapshot_reference",
    "source_snapshot_sha256",
}
NEW_PROVENANCE_KEYS = {
    "development_regression_only",
    "selection_origin",
    "selection_receipt_reference",
    "selection_receipt_sha256",
}
RETAINED_SNAPSHOT_KEYS = {
    "snapshot_id",
    "r3_source_case_id",
    "execution_state",
    "captured_at",
}
NEW_SELECTION_RECEIPT_KEYS = {
    "receipt_id",
    "research_contract_id",
    "case_id",
    "source_node_id",
    "selected_at",
    "preparation_contract_version",
    "locked_input_sha256",
    "terminology_bridge_reference",
    "terminology_bridge_sha256",
    "official_terminal_node_snapshot_reference",
    "official_terminal_node_snapshot_sha256",
    "prior_method_exposure_state",
    "selection_basis",
}
R3_SOURCE_MANIFEST_KEYS = {
    "manifest_id", "research_contract_id", "source_round", "accepted_state",
    "accepted_at", "acceptance_reference", "case_count",
    "development_case_count", "unexecuted_case_count", "cases",
}
R3_SOURCE_MANIFEST_ENTRY_KEYS = {
    "r3_source_case_id", "source_case_role", "execution_state",
    "source_snapshot_reference", "source_snapshot_sha256",
}
def visible_case_set_workspace_errors(visible_rows: list[dict], formal_rows: list[dict], research_contract_id: object) -> list[str]:
    visible_cases = [row for row in visible_rows if row.get("record_type") == "visible_calibration_case"]
    formal_cases = [row for row in formal_rows if row.get("record_type") == "calibration_case"]
    if frozen_visible_case_errors(visible_rows, research_contract_id):
        return ["VISIBLE_CASE_SET_INVALID"]
    visible_ids = [row.get("case_id") for row in visible_cases]
    formal_ids = [row.get("case_id") for row in formal_cases]
    if visible_ids != formal_ids:
        return ["VISIBLE_CASE_SET_INVALID"]
    for visible, formal in zip(visible_cases, formal_cases):
        if visible_case_projection(visible) != visible_case_projection(formal):
            return ["VISIBLE_CASE_SET_INVALID"]
    return []
SCREENING_RESULTS = {"hypothesis_formed", "ambiguous", "no_hypothesis_formed"}
WORK_STATES = {"not_screened", "screened", "evidence_expansion_required", "evidence_expanded", "audit_reopened"}
EVIDENCE_STATES = {"supported", "hypothesis", "unknown", "conflicted"}
FORMAL_MODEL_RECORD_KEYS = (
    "semantic_model_task",
    "semantic_model_return",
    "semantic_model_receipt",
)
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


def real_lowercase_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value) is not None
        and len(set(value)) > 1
    )


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


def case_preparation_input_projection(contract: dict) -> dict:
    """Return the immutable case-preparation input projection.

    Finalization is allowed to change only the normalized fields below. The
    returned projection is never serialized as a contract and therefore does
    not create placeholder case evidence.
    """
    projection = json.loads(json.dumps(contract))
    gate = projection.get("case_preparation_gate")
    if not isinstance(gate, dict):
        gate = {}
        projection["case_preparation_gate"] = gate
    preparation_version = gate.get("preparation_contract_version")
    projection["contract_version"] = preparation_version
    projection["contract_state"] = "case_preparation_locked"
    projection["frozen_at"] = None
    projection["calibration_case_set_reference_and_hash"] = {
        "reference": None,
        "sha256": None,
    }
    if projection.get("execution_mode") == "content_first":
        projection["visible_case_set_reference_and_hash"] = {"reference": None, "sha256": None}
        projection["visible_case_freeze_receipt_reference_and_hash"] = {"reference": None, "sha256": None}
        projection["source_truth_package_reference"] = None
        projection["source_truth_package_sha256"] = None
        projection["adjudicated_truth_summary"] = None
    batch = projection.get("batch_rule")
    if isinstance(batch, dict):
        batch["batch_size"] = None
    controls = projection.get("control_case_rule")
    if isinstance(controls, dict):
        controls["case_ids"] = []
    gate["locked_input_sha256"] = None
    return projection


def case_preparation_input_sha256(contract: dict) -> str:
    return canonical_json_sha256(case_preparation_input_projection(contract))


def case_preparation_outputs_are_empty(contract: dict) -> bool:
    case_set = contract.get("calibration_case_set_reference_and_hash")
    visible_case_set = contract.get("visible_case_set_reference_and_hash")
    visible_freeze_receipt = contract.get("visible_case_freeze_receipt_reference_and_hash")
    batch = contract.get("batch_rule")
    controls = contract.get("control_case_rule")
    return (
        isinstance(case_set, dict)
        and case_set.get("reference") is None
        and case_set.get("sha256") is None
        and (
            contract.get("execution_mode") != "content_first"
            or (
                isinstance(visible_case_set, dict)
                and visible_case_set.get("reference") is None
                and visible_case_set.get("sha256") is None
                and isinstance(visible_freeze_receipt, dict)
                and visible_freeze_receipt.get("reference") is None
                and visible_freeze_receipt.get("sha256") is None
                and contract.get("adjudicated_truth_summary") is None
            )
        )
        and isinstance(batch, dict)
        and batch.get("batch_size") is None
        and isinstance(controls, dict)
        and controls.get("case_ids") == []
        and contract.get("frozen_at") is None
    )


def execution_mode_errors(contract: dict) -> list[str]:
    if "execution_mode" in contract and contract.get("execution_mode") != "content_first":
        return ["execution_mode:invalid"]
    return []


def content_first_default_deny_errors(contract: dict) -> list[str]:
    policy = contract.get("content_first_policy")
    expected_prohibitions = {
        "full_screening_without_explicit_authorization",
        "write_shared_application_base",
        "company_matching",
        "route_generation",
        "customer_research",
    }
    if (
        contract.get("execution_authorized") is not False
        or contract.get("full_screening_authorization") is not False
        or contract.get("full_screening_authorization_reference") is not None
        or contract.get("application_base_write_authorization") is not False
        or not isinstance(policy, dict)
        or policy.get("content_method_state") != "CONTENT_CALIBRATION_INCOMPLETE"
        or policy.get("content_full_screening_state") != "NOT_AUTHORIZED"
        or policy.get("downstream_release_state") != "RESEARCH_ONLY_BLOCKED"
        or not expected_prohibitions.issubset(set(contract.get("prohibited_actions") or []))
        or content_first_allowed_write_errors(contract)
    ):
        return ["content_first_default_deny:invalid"]
    return []


def content_first_allowed_write_errors(contract: dict) -> list[str]:
    allowed_writes = contract.get("allowed_writes")
    contract_id = contract.get("research_contract_id")
    if not isinstance(allowed_writes, list) or not isinstance(contract_id, str):
        return ["allowed_writes:invalid"]
    marker = f"05-工作区/行业语义研究/{contract_id}"
    forbidden_markers = ("02-共享应用知识", "company", "brand", "product", "route", "customer")
    for item in allowed_writes:
        if not nonempty_text(item):
            return ["allowed_writes:invalid"]
        normalized = item.replace("\\", "/")
        if (
            Path(normalized).is_absolute()
            or ".." in Path(normalized).parts
            or (normalized != marker and not normalized.startswith(marker + "/"))
            or any(marker_text in normalized.lower() for marker_text in forbidden_markers)
        ):
            return ["allowed_writes:out_of_scope"]
    return []


def strict_paired_execution_contract_errors(paired: object) -> list[str]:
    """Validate the frozen, task-visible paired-run contract without defaults."""
    keys = {
        "declared_model_and_configuration", "tools", "source_permissions", "observation_window",
        "budgets", "frozen_artifact_references_and_hashes", "fresh_context_required",
        "truth_isolation_required", "other_arm_isolation_required", "prior_case_isolation_required",
        "append_only_outputs_required", "model_execution_authorized",
    }
    if not isinstance(paired, dict) or set(paired) != keys:
        return ["paired_execution_contract:exact_schema_invalid"]
    model = paired["declared_model_and_configuration"]
    if not isinstance(model, dict) or set(model) != {"model", "configuration_reference", "configuration_sha256"} or not nonempty_text(model.get("model")) or not nonempty_text(model.get("configuration_reference")) or not real_lowercase_sha256(model.get("configuration_sha256")):
        return ["paired_execution_contract.model:invalid"]
    for field in ("tools", "source_permissions"):
        values = paired[field]
        if not isinstance(values, list) or not values or not all(nonempty_text(value) for value in values) or len(set(values)) != len(values):
            return [f"paired_execution_contract.{field}:invalid"]
    window = paired["observation_window"]
    try:
        starts = datetime.fromisoformat(str(window.get("starts_at")).replace("Z", "+00:00")) if isinstance(window, dict) and set(window) == {"starts_at", "ends_at"} else None
        ends = datetime.fromisoformat(str(window.get("ends_at")).replace("Z", "+00:00")) if isinstance(window, dict) and set(window) == {"starts_at", "ends_at"} else None
    except ValueError:
        starts = ends = None
    if starts is None or ends is None or starts.tzinfo is None or ends.tzinfo is None or starts >= ends:
        return ["paired_execution_contract.observation_window:invalid"]
    budgets = paired["budgets"]
    if not isinstance(budgets, dict) or set(budgets) != {"query_budget", "source_open_budget", "elapsed_seconds_budget", "output_token_budget"} or any(type(value) is not int or value <= 0 for value in budgets.values()):
        return ["paired_execution_contract.budgets:invalid"]
    artifacts = paired["frozen_artifact_references_and_hashes"]
    if not isinstance(artifacts, dict) or set(artifacts) != {"prompt", "schema", "config", "rubric"}:
        return ["paired_execution_contract.artifacts:invalid"]
    references: list[str] = []
    config_rows: list[dict] = []
    for group in ("prompt", "schema", "config", "rubric"):
        rows = artifacts[group]
        if not isinstance(rows, list) or not rows:
            return [f"paired_execution_contract.artifacts.{group}:invalid"]
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"reference", "sha256"} or not nonempty_text(row.get("reference")) or not real_lowercase_sha256(row.get("sha256")):
                return [f"paired_execution_contract.artifacts.{group}:invalid"]
            references.append(row["reference"])
            if group == "config":
                config_rows.append(row)
    if len(references) != len(set(references)) or len(config_rows) != 1 or model["configuration_reference"] != config_rows[0]["reference"] or model["configuration_sha256"] != config_rows[0]["sha256"]:
        return ["paired_execution_contract.artifact_identity:invalid"]
    flags = ("fresh_context_required", "truth_isolation_required", "other_arm_isolation_required", "prior_case_isolation_required", "append_only_outputs_required")
    if any(paired[field] is not True for field in flags) or paired["model_execution_authorized"] is not False:
        return ["paired_execution_contract.isolation_or_authorization:invalid"]
    return []


def content_first_local_frozen_reference_errors(contract: object, root: Path) -> list[str]:
    """Verify only task-visible frozen inputs under one explicit local root."""
    if not isinstance(contract, dict) or not root.is_dir():
        return ["CONTRACT_LOCAL_ROOT_INVALID"]
    entries: list[tuple[str, object, object]] = []
    architecture = contract.get("terminology_architecture")
    if isinstance(architecture, dict) and architecture.get("term_pack_reference") is not None:
        entries.append(("TERMINOLOGY_BRIDGE", architecture.get("term_pack_reference"), architecture.get("term_pack_sha256")))
    if contract.get("taxonomy_snapshot_reference") is not None:
        entries.append(("TAXONOMY_SNAPSHOT", contract.get("taxonomy_snapshot_reference"), contract.get("taxonomy_snapshot_sha256")))
    prompts = contract.get("prompt_template_references_and_hashes")
    if isinstance(prompts, list):
        entries.extend(("PROMPT_TEMPLATE", row.get("reference"), row.get("sha256")) for row in prompts if isinstance(row, dict))
    paired = contract.get("paired_execution_contract")
    strict_errors = strict_paired_execution_contract_errors(paired)
    if strict_errors:
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    artifacts = paired.get("frozen_artifact_references_and_hashes") if isinstance(paired, dict) else None
    if not isinstance(artifacts, dict):
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    for group in ("prompt", "schema", "config", "rubric"):
        rows = artifacts.get(group)
        if not isinstance(rows, list):
            return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
        entries.extend((f"PAIRED_{group.upper()}", row.get("reference"), row.get("sha256")) for row in rows if isinstance(row, dict))
    errors: list[str] = []
    root = root.resolve()
    protected_hashes = {
        (contract.get("calibration_case_set_reference_and_hash") or {}).get("sha256"),
        (contract.get("visible_case_set_reference_and_hash") or {}).get("sha256"),
        (contract.get("visible_case_freeze_receipt_reference_and_hash") or {}).get("sha256"),
        contract.get("source_truth_package_sha256"),
    }
    protected_references = {
        (contract.get("calibration_case_set_reference_and_hash") or {}).get("reference"),
        (contract.get("visible_case_set_reference_and_hash") or {}).get("reference"),
        (contract.get("visible_case_freeze_receipt_reference_and_hash") or {}).get("reference"),
        contract.get("source_truth_package_reference"),
    }
    protected_parent_roots = {
        PurePosixPath(reference).parent
        for reference in (
            (contract.get("calibration_case_set_reference_and_hash") or {}).get("reference"),
            contract.get("source_truth_package_reference"),
        )
        if isinstance(reference, str) and PurePosixPath(reference).parent != PurePosixPath(".")
    }
    identities: set[tuple[int, int]] = set()
    for label, reference, expected_hash in entries:
        normalized = PurePosixPath(reference).as_posix() if isinstance(reference, str) else None
        candidate = PurePosixPath(reference) if isinstance(reference, str) and normalized == reference and normalized != "." else None
        if candidate is None or candidate.is_absolute() or any(part in {".", ".."} for part in candidate.parts) or "\\" in str(reference):
            errors.append(f"{label}_REFERENCE_INVALID")
            continue
        if expected_hash in protected_hashes:
            errors.append("TASK_VISIBLE_ARTIFACT_HASH_COLLISION")
            continue
        if reference in protected_references:
            errors.append("TASK_VISIBLE_ARTIFACT_ROLE_COLLISION")
            continue
        if any(candidate.parts[:len(parent.parts)] == parent.parts for parent in protected_parent_roots):
            errors.append("TASK_VISIBLE_ARTIFACT_ROOT_COLLISION")
            continue
        path = (root / candidate).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"{label}_PATH_ESCAPE")
            continue
        if not path.is_file():
            errors.append(f"{label}_MISSING")
        elif not real_lowercase_sha256(expected_hash) or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            errors.append(f"{label}_HASH_MISMATCH")
        else:
            if expected_hash in protected_hashes:
                errors.append("TASK_VISIBLE_ARTIFACT_HASH_COLLISION")
            if reference in protected_references:
                errors.append("TASK_VISIBLE_ARTIFACT_ROLE_COLLISION")
            stat = path.stat()
            identity = (stat.st_dev, stat.st_ino)
            if identity in identities:
                errors.append("TASK_VISIBLE_ARTIFACT_IDENTITY_COLLISION")
            identities.add(identity)
    if not errors and isinstance(artifacts, dict):
        schema_rows = artifacts.get("schema")
        if not isinstance(schema_rows, list) or len(schema_rows) != 1:
            errors.append("PAIRED_SCHEMA_INVALID")
        else:
            schema_path = root / schema_rows[0]["reference"]
            try:
                payload = json.loads(schema_path.read_text(encoding="utf-8"))
                body = payload.get("content_source_observation") if isinstance(payload, dict) else None
                item_keys = {"source_url_or_null", "publisher_or_null", "title_or_null", "original_location_or_null", "bounded_summary_or_null", "access_state", "conditions", "limitations", "counterevidence"}
                item = body.get("source_observations", [None])[0] if isinstance(body, dict) and isinstance(body.get("source_observations"), list) and len(body["source_observations"]) == 1 else None
                if set(payload) != {"schema_version", "content_source_observation"} or payload.get("schema_version") != "1.0" or not isinstance(body, dict) or set(body) != {"case_id", "method_arm", "source_observations", "unknown_items"} or body.get("case_id") is not None or body.get("method_arm") is not None or body.get("unknown_items") != [] or not isinstance(item, dict) or set(item) != item_keys or any(item[key] is not None for key in ("source_url_or_null", "publisher_or_null", "title_or_null", "original_location_or_null", "bounded_summary_or_null")) or item.get("access_state") != "UNVERIFIED" or any(item[key] != [] for key in ("conditions", "limitations", "counterevidence")):
                    errors.append("PAIRED_SCHEMA_INVALID")
            except (OSError, ValueError, TypeError, KeyError):
                errors.append("PAIRED_SCHEMA_INVALID")
    return errors


def parse_aware_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def normalized_identifier_key(value: object) -> str | None:
    if (
        not nonempty_text(value)
        or not isinstance(value, str)
        or "/" in value
        or "\\" in value
        or any(character.isspace() or ord(character) < 32 for character in value)
    ):
        return None
    return unicodedata.normalize("NFKC", value).casefold()


def secure_contract_local_file(
    root: Path, reference: object, expected_hash: object
) -> tuple[Path | None, bytes | None, tuple[int, int] | None, str | None]:
    """Open a canonical regular file without accepting aliases or path escapes."""
    if not isinstance(reference, str):
        return None, None, None, "PROVENANCE_REFERENCE_INVALID"
    candidate = PurePosixPath(reference)
    if (
        candidate.as_posix() != reference
        or candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or "\\" in reference
    ):
        return None, None, None, "PROVENANCE_REFERENCE_INVALID"
    root = root.resolve()
    unresolved = root
    for part in candidate.parts:
        unresolved = unresolved / part
        if unresolved.is_symlink():
            return None, None, None, "PROVENANCE_SYMLINK_FORBIDDEN"
    try:
        resolved = unresolved.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, OSError, ValueError):
        return None, None, None, "PROVENANCE_ASSET_MISSING"
    if not resolved.is_file():
        return None, None, None, "PROVENANCE_ASSET_MISSING"
    try:
        body = resolved.read_bytes()
        stat = resolved.stat()
    except OSError:
        return None, None, None, "PROVENANCE_ASSET_MISSING"
    if (
        not real_lowercase_sha256(expected_hash)
        or hashlib.sha256(body).hexdigest() != expected_hash
    ):
        return resolved, body, (stat.st_dev, stat.st_ino), "PROVENANCE_ASSET_HASH_MISMATCH"
    return resolved, body, (stat.st_dev, stat.st_ino), None


def validate_r3_source_manifest(
    contract: object, contract_local_root: Path | None
) -> tuple[list[str], dict[str, dict]]:
    if not isinstance(contract, dict) or contract_local_root is None or not contract_local_root.is_dir():
        return ["R3_SOURCE_MANIFEST_ROOT_INVALID"], {}
    binding = contract.get("r3_case_source_manifest_reference_and_hash")
    if (
        not isinstance(binding, dict)
        or set(binding) != {"reference", "sha256"}
        or not nonempty_text(binding.get("reference"))
    ):
        return ["R3_SOURCE_MANIFEST_BINDING_INVALID"], {}
    _, manifest_bytes, _, error = secure_contract_local_file(
        contract_local_root, binding.get("reference"), binding.get("sha256")
    )
    if error:
        return [error], {}
    try:
        payload = json.loads(manifest_bytes)
        manifest = payload["r3_case_source_manifest"]
    except (ValueError, TypeError, KeyError):
        return ["R3_SOURCE_MANIFEST_SCHEMA_INVALID"], {}
    if (
        not isinstance(payload, dict)
        or set(payload) != {"schema_version", "r3_case_source_manifest"}
        or payload.get("schema_version") != "1.0"
        or not isinstance(manifest, dict)
        or set(manifest) != R3_SOURCE_MANIFEST_KEYS
        or not nonempty_text(manifest.get("manifest_id"))
        or manifest.get("research_contract_id") != contract.get("research_contract_id")
        or manifest.get("source_round") != "R3"
        or manifest.get("accepted_state") != "accepted_source_truth"
        or parse_aware_datetime(manifest.get("accepted_at")) is None
        or not nonempty_text(manifest.get("acceptance_reference"))
        or manifest.get("case_count") != 40
        or manifest.get("development_case_count") != 10
        or manifest.get("unexecuted_case_count") != 30
        or not isinstance(manifest.get("cases"), list)
        or len(manifest["cases"]) != 40
    ):
        return ["R3_SOURCE_MANIFEST_COMPOSITION_INVALID"], {}
    errors: list[str] = []
    accepted_at = parse_aware_datetime(manifest.get("accepted_at"))
    locked_at = parse_aware_datetime(
        (contract.get("case_preparation_gate") or {}).get("locked_at")
    )
    if locked_at is not None and accepted_at is not None and accepted_at >= locked_at:
        errors.append("R3_SOURCE_MANIFEST_NOT_ACCEPTED_BEFORE_LOCK")
    source_ids: set[str] = set()
    snapshot_ids: set[str] = set()
    references: set[str] = set()
    hashes: set[str] = set()
    identities: set[tuple[int, int]] = set()
    by_id: dict[str, dict] = {}
    role_counts = {"development_regression_only": 0, "formal_holdout_eligible": 0}
    for entry in manifest["cases"]:
        if not isinstance(entry, dict) or set(entry) != R3_SOURCE_MANIFEST_ENTRY_KEYS:
            errors.append("R3_SOURCE_MANIFEST_ENTRY_INVALID")
            continue
        source_id = entry.get("r3_source_case_id")
        source_key = normalized_identifier_key(source_id)
        if source_key is None or source_key in source_ids:
            errors.append("R3_SOURCE_CASE_ID_REUSE")
        else:
            source_ids.add(source_key)
            by_id[source_key] = entry
        role = entry.get("source_case_role")
        expected_state = (
            "executed_development"
            if role == "development_regression_only"
            else "unexecuted" if role == "formal_holdout_eligible" else None
        )
        if expected_state is None or entry.get("execution_state") != expected_state:
            errors.append("R3_SOURCE_MANIFEST_ENTRY_INVALID")
        else:
            role_counts[role] += 1
        reference = entry.get("source_snapshot_reference")
        expected_hash = entry.get("source_snapshot_sha256")
        if isinstance(reference, str) and reference in references:
            errors.append("PROVENANCE_ASSET_REFERENCE_REUSE")
        elif isinstance(reference, str):
            references.add(reference)
        if isinstance(expected_hash, str) and expected_hash in hashes:
            errors.append("PROVENANCE_ASSET_HASH_REUSE")
        elif isinstance(expected_hash, str):
            hashes.add(expected_hash)
        _, snapshot_bytes, identity, snapshot_error = secure_contract_local_file(
            contract_local_root, reference, expected_hash
        )
        if snapshot_error:
            errors.append(snapshot_error)
            continue
        if identity in identities:
            errors.append("PROVENANCE_ASSET_IDENTITY_REUSE")
        elif identity is not None:
            identities.add(identity)
        try:
            snapshot_payload = json.loads(snapshot_bytes)
            snapshot = snapshot_payload["retained_r3_case_snapshot"]
        except (ValueError, TypeError, KeyError):
            errors.append("R3_SOURCE_SNAPSHOT_INVALID")
            continue
        snapshot_key = normalized_identifier_key(snapshot.get("snapshot_id")) if isinstance(snapshot, dict) else None
        if snapshot_key is None or snapshot_key in snapshot_ids:
            errors.append("R3_SOURCE_SNAPSHOT_ID_REUSE")
        else:
            snapshot_ids.add(snapshot_key)
        if (
            not isinstance(snapshot_payload, dict)
            or set(snapshot_payload) != {"schema_version", "retained_r3_case_snapshot"}
            or snapshot_payload.get("schema_version") != "1.0"
            or not isinstance(snapshot, dict)
            or set(snapshot) != RETAINED_SNAPSHOT_KEYS
            or snapshot.get("r3_source_case_id") != source_id
            or snapshot.get("execution_state") != expected_state
            or parse_aware_datetime(snapshot.get("captured_at")) is None
        ):
            errors.append("R3_SOURCE_SNAPSHOT_INVALID")
    if role_counts != {"development_regression_only": 10, "formal_holdout_eligible": 30}:
        errors.append("R3_SOURCE_MANIFEST_COMPOSITION_INVALID")
    return list(dict.fromkeys(errors)), by_id


def validate_content_first_case_provenance(
    cases: list[dict], contract: object, contract_local_root: Path | None
) -> list[str]:
    """Validate the receiver-only 30 retained + 10 newly selected provenance chain."""
    if not isinstance(contract, dict) or contract_local_root is None or not contract_local_root.is_dir():
        return ["CONTRACT_LOCAL_ROOT_INVALID"]
    policy = contract.get("calibration_case_policy")
    if not isinstance(policy, dict):
        return ["CALIBRATION_CASE_POLICY_INVALID"]
    problems: list[str] = []
    origin_counts: dict[str, int] = {}
    asset_references: set[str] = set()
    asset_hashes: set[str] = set()
    asset_identities: set[tuple[int, int]] = set()
    r3_source_ids: set[str] = set()
    receipt_ids: set[str] = set()
    new_source_node_ids: set[str] = set()
    retained_manifest_ids: set[str] = set()
    locked_at = parse_aware_datetime((contract.get("case_preparation_gate") or {}).get("locked_at"))
    gate = contract.get("case_preparation_gate") if isinstance(contract.get("case_preparation_gate"), dict) else {}
    architecture = contract.get("terminology_architecture") if isinstance(contract.get("terminology_architecture"), dict) else {}
    manifest_errors, manifest_by_id = validate_r3_source_manifest(
        contract, contract_local_root
    )
    problems.extend(manifest_errors)
    eligible_manifest_ids = {
        key for key, entry in manifest_by_id.items()
        if entry.get("source_case_role") == "formal_holdout_eligible"
        and entry.get("execution_state") == "unexecuted"
    }

    taxonomy_reference = contract.get("taxonomy_snapshot_reference")
    taxonomy_sha256 = contract.get("taxonomy_snapshot_sha256")
    _, taxonomy_bytes, _, taxonomy_error = secure_contract_local_file(
        contract_local_root, taxonomy_reference, taxonomy_sha256
    )
    if taxonomy_error:
        problems.append(taxonomy_error)
        terminal_node_ids: set[str] = set()
        terminal_node_by_id: dict[str, dict] = {}
    else:
        try:
            taxonomy_payload = json.loads(taxonomy_bytes)
            terminal_nodes = taxonomy_payload.get("terminal_nodes")
            terminal_node_by_id = {
                taxonomy_identifier_key(row.get("taxonomy_node_id")): (index, row)
                for index, row in enumerate(terminal_nodes)
                if isinstance(row, dict)
                and taxonomy_identifier_key(row.get("taxonomy_node_id")) is not None
                and nonempty_text(row.get("code"))
                and nonempty_text(row.get("name_zh"))
            } if isinstance(terminal_nodes, list) else {}
            terminal_node_ids = set(terminal_node_by_id)
            if (
                not isinstance(terminal_nodes, list)
                or len(terminal_node_ids) != len(terminal_nodes)
                or taxonomy_payload.get("terminal_node_count") != len(terminal_nodes)
            ):
                terminal_node_ids = set()
                terminal_node_by_id = {}
                problems.append("OFFICIAL_TERMINAL_NODE_SNAPSHOT_INVALID")
        except (ValueError, TypeError, AttributeError):
            terminal_node_ids = set()
            terminal_node_by_id = {}
            problems.append("OFFICIAL_TERMINAL_NODE_SNAPSHOT_INVALID")

    # Receipts bind this shared terminology input; it remains one deliberate
    # contract role and is not counted as 40 independent provenance assets.
    _, _, _, terminology_error = secure_contract_local_file(
        contract_local_root,
        architecture.get("term_pack_reference"),
        architecture.get("term_pack_sha256"),
    )
    if terminology_error:
        problems.append(terminology_error)

    for case in cases:
        provenance = case.get("provenance")
        if not isinstance(provenance, dict) or provenance.get("development_regression_only") is not False:
            problems.append("CASE_PROVENANCE_INVALID")
            continue
        origin = provenance.get("selection_origin")
        if origin not in CONTENT_FIRST_SELECTION_ORIGIN_COUNTS:
            problems.append("CASE_PROVENANCE_INVALID")
            continue
        origin_counts[origin] = origin_counts.get(origin, 0) + 1
        if origin == "retained_r3_unexecuted":
            if set(provenance) != RETAINED_PROVENANCE_KEYS:
                problems.append("CASE_PROVENANCE_INVALID")
                continue
            reference = provenance.get("source_snapshot_reference")
            expected_hash = provenance.get("source_snapshot_sha256")
            r3_case_id = provenance.get("r3_source_case_id")
            r3_key = normalized_identifier_key(r3_case_id)
            if r3_key is None or r3_key in r3_source_ids:
                problems.append("R3_SOURCE_CASE_ID_REUSE")
            else:
                r3_source_ids.add(r3_key)
                retained_manifest_ids.add(r3_key)
                manifest_entry = manifest_by_id.get(r3_key)
                if (
                    manifest_entry is None
                    or manifest_entry.get("source_case_role") != "formal_holdout_eligible"
                    or manifest_entry.get("execution_state") != "unexecuted"
                    or manifest_entry.get("source_snapshot_reference")
                    != provenance.get("source_snapshot_reference")
                    or manifest_entry.get("source_snapshot_sha256")
                    != provenance.get("source_snapshot_sha256")
                ):
                    problems.append("R3_RETAINED_MEMBERSHIP_MISMATCH")
            payload_key = "retained_r3_case_snapshot"
        else:
            if set(provenance) != NEW_PROVENANCE_KEYS:
                problems.append("CASE_PROVENANCE_INVALID")
                continue
            reference = provenance.get("selection_receipt_reference")
            expected_hash = provenance.get("selection_receipt_sha256")
            payload_key = "new_unseen_selection_receipt"

        if isinstance(reference, str) and reference in asset_references:
            problems.append("PROVENANCE_ASSET_REFERENCE_REUSE")
        elif isinstance(reference, str):
            asset_references.add(reference)
        if isinstance(expected_hash, str) and expected_hash in asset_hashes:
            problems.append("PROVENANCE_ASSET_HASH_REUSE")
        elif isinstance(expected_hash, str):
            asset_hashes.add(expected_hash)
        _, body, identity, asset_error = secure_contract_local_file(
            contract_local_root, reference, expected_hash
        )
        if asset_error:
            problems.append(asset_error)
            continue
        if identity in asset_identities:
            problems.append("PROVENANCE_ASSET_IDENTITY_REUSE")
        elif identity is not None:
            asset_identities.add(identity)
        try:
            payload = json.loads(body)
            record = payload[payload_key]
        except (ValueError, TypeError, KeyError):
            problems.append("PROVENANCE_ASSET_SCHEMA_INVALID")
            continue
        if (
            not isinstance(payload, dict)
            or set(payload) != {"schema_version", payload_key}
            or payload.get("schema_version") != "1.0"
            or not isinstance(record, dict)
        ):
            problems.append("PROVENANCE_ASSET_SCHEMA_INVALID")
            continue
        if origin == "retained_r3_unexecuted":
            if set(record) != RETAINED_SNAPSHOT_KEYS:
                problems.append("PROVENANCE_ASSET_SCHEMA_INVALID")
                continue
            if (
                not nonempty_text(record.get("snapshot_id"))
                or record.get("r3_source_case_id") != provenance.get("r3_source_case_id")
                or parse_aware_datetime(record.get("captured_at")) is None
            ):
                problems.append("R3_SOURCE_SNAPSHOT_INVALID")
            if record.get("execution_state") != "unexecuted":
                problems.append("R3_SOURCE_NOT_UNEXECUTED")
        else:
            if set(record) != NEW_SELECTION_RECEIPT_KEYS:
                problems.append("PROVENANCE_ASSET_SCHEMA_INVALID")
                continue
            receipt_id = record.get("receipt_id")
            receipt_key = normalized_identifier_key(receipt_id)
            if receipt_key is None or receipt_key in receipt_ids:
                problems.append("NEW_SELECTION_RECEIPT_ID_REUSE")
            else:
                receipt_ids.add(receipt_key)
            selected_at = parse_aware_datetime(record.get("selected_at"))
            case_node = case.get("taxonomy_node") if isinstance(case.get("taxonomy_node"), dict) else {}
            source_node_key = taxonomy_identifier_key(record.get("source_node_id"))
            if source_node_key is None or source_node_key in new_source_node_ids:
                problems.append("NEW_SELECTION_SOURCE_NODE_REUSE")
            else:
                new_source_node_ids.add(source_node_key)
            case_node_key = taxonomy_identifier_key(case_node.get("taxonomy_node_id"))
            if (
                record.get("research_contract_id") != contract.get("research_contract_id")
                or record.get("case_id") != case.get("case_id")
                or source_node_key != case_node_key
                or source_node_key not in terminal_node_ids
            ):
                problems.append("NEW_SELECTION_SOURCE_NODE_INVALID")
            official_entry = terminal_node_by_id.get(source_node_key)
            official_node = official_entry[1] if isinstance(official_entry, tuple) else None
            if isinstance(official_node, dict) and any(
                key in official_node and official_node.get(key) != case_node.get(key)
                for key in ("code", "name_zh")
            ):
                problems.append("NEW_SELECTION_OFFICIAL_NODE_MISMATCH")
            if locked_at is None or selected_at is None or selected_at <= locked_at:
                problems.append("NEW_SELECTION_BEFORE_PREPARATION_LOCK")
            if record.get("prior_method_exposure_state") != "unseen":
                problems.append("NEW_SELECTION_NOT_UNSEEN")
            if (
                record.get("preparation_contract_version") != gate.get("preparation_contract_version")
                or record.get("locked_input_sha256") != gate.get("locked_input_sha256")
                or record.get("terminology_bridge_reference") != architecture.get("term_pack_reference")
                or record.get("terminology_bridge_sha256") != architecture.get("term_pack_sha256")
                or record.get("official_terminal_node_snapshot_reference") != taxonomy_reference
                or record.get("official_terminal_node_snapshot_sha256") != taxonomy_sha256
                or record.get("selection_basis")
                != "official_terminal_node_after_method_and_terminology_lock"
            ):
                problems.append("NEW_SELECTION_LOCK_BINDING_INVALID")

    if origin_counts != CONTENT_FIRST_SELECTION_ORIGIN_COUNTS:
        problems.append("SELECTION_ORIGIN_COMPOSITION_INVALID")
    if retained_manifest_ids != eligible_manifest_ids:
        problems.append("R3_RETAINED_MEMBERSHIP_MISMATCH")
    if len(new_source_node_ids) != 10:
        problems.append("NEW_SELECTION_SOURCE_NODE_REUSE")
    for case in cases:
        case_node = case.get("taxonomy_node") if isinstance(case.get("taxonomy_node"), dict) else {}
        node_key = taxonomy_identifier_key(case_node.get("taxonomy_node_id"))
        official_entry = terminal_node_by_id.get(node_key)
        if not isinstance(official_entry, tuple):
            problems.append("FORMAL_CASE_OFFICIAL_NODE_INVALID")
            continue
        node_index, official_node = official_entry
        official_level = taxonomy_level_number(official_node.get("level"))
        if (
            case_node.get("code") != official_node.get("code")
            or case_node.get("name_zh") != official_node.get("name_zh")
            or (
                official_level is not None
                and case_node.get("level") != official_level
            )
        ):
            problems.append("FORMAL_CASE_OFFICIAL_NODE_INVALID")
        expected_reference = f"{taxonomy_reference}#/terminal_nodes/{node_index}"
        if (
            case_node.get("official_source_reference") != expected_reference
            or case_node.get("official_source_sha256") != taxonomy_sha256
        ):
            problems.append("FORMAL_CASE_OFFICIAL_SOURCE_INVALID")
    return list(dict.fromkeys(problems))


def validate_content_first_case_truth_rows(
    case_rows: list[dict],
    truth_rows: list[dict],
    research_contract_id: object,
    calibration_policy: object,
    control_case_ids: object,
    stability_repeat_case_count: object,
    *,
    contract: object | None = None,
    contract_local_root: Path | None = None,
    frozen_at: object = None,
) -> list[str]:
    problems: list[str] = []
    if not isinstance(calibration_policy, dict):
        return ["CALIBRATION_CASE_POLICY_INVALID"]
    headers = [row for row in case_rows if row.get("record_type") == "case_set_contract"]
    cases = [row for row in case_rows if row.get("record_type") == "calibration_case"]
    if len(headers) != 1:
        problems.append("CASE_SET_HEADER_INVALID")
        header: dict = {}
    else:
        header = headers[0]
    if any(row.get("record_type") not in {"case_set_contract", "calibration_case"} for row in case_rows):
        problems.append("CASE_SET_RECORD_TYPE_INVALID")
    case_ids = [row.get("case_id") for row in cases]
    if (
        header.get("case_count") != 40
        or header.get("actual_case_record_count") != 40
        or header.get("case_set_state") != "frozen"
        or header.get("research_contract_id") != research_contract_id
        or len(cases) != 40
        or not all(nonempty_text(case_id) for case_id in case_ids)
        or len(set(case_ids)) != 40
        or any(row.get("research_contract_id") != research_contract_id for row in cases)
    ):
        problems.append("FORTY_UNIQUE_CONTRACT_BOUND_CASES_REQUIRED")
    formal_case_ids = header.get("formal_case_ids")
    if (
        not isinstance(formal_case_ids, list)
        or formal_case_ids != case_ids
        or len(formal_case_ids) != 40
        or not all(
            isinstance(case_id, str)
            and bool(case_id.strip())
            and unicodedata.normalize("NFKC", case_id) == case_id
            and "/" not in case_id and "\\" not in case_id and "." not in case_id
            and not any(character.isspace() or ord(character) < 32 for character in case_id)
            for case_id in formal_case_ids
        )
        or len({unicodedata.normalize("NFKC", case_id).casefold() for case_id in formal_case_ids if isinstance(case_id, str)}) != 40
    ):
        problems.append("FORMAL_CASE_IDS_INVALID")
    expected_counts = calibration_policy.get("required_sampling_category_counts")
    actual_counts: dict[object, int] = {}
    for case in cases:
        category = case.get("sampling_category")
        actual_counts[category] = actual_counts.get(category, 0) + 1
    if (
        header.get("sampling_category_counts") != expected_counts
        or actual_counts != expected_counts
    ):
        problems.append("SAMPLING_CATEGORY_COUNT_DRIFT")
    excluded_case_ids = calibration_policy.get("development_case_ids_excluded_from_formal")
    if not isinstance(excluded_case_ids, list):
        problems.append("DEVELOPMENT_CASE_EXCLUSION_POLICY_INVALID")
    else:
        excluded_keys = [normalized_identifier_key(value) for value in excluded_case_ids]
        case_keys = {normalized_identifier_key(value) for value in case_ids}
        if any(key is None for key in excluded_keys) or len(set(excluded_keys)) != len(excluded_keys):
            problems.append("DEVELOPMENT_CASE_EXCLUSION_POLICY_INVALID")
        elif set(excluded_keys).intersection(case_keys):
            problems.append("DEVELOPMENT_CASE_ID_IN_FORMAL_SET")
    problems.extend(validate_beta5_case_rows(cases))
    problems.extend(
        validate_content_first_case_provenance(
            cases, contract, contract_local_root
        )
    )
    repeats = header.get("stability_repeat_case_ids")
    if (
        not isinstance(repeats, list)
        or len(repeats) != stability_repeat_case_count
        or len(set(repeats)) != len(repeats)
        or not set(repeats).issubset(set(case_ids))
    ):
        problems.append("STABILITY_REPEAT_CASES_INVALID")
    if (
        not isinstance(control_case_ids, list)
        or not control_case_ids
        or len(set(control_case_ids)) != len(control_case_ids)
        or not set(control_case_ids).issubset(set(case_ids))
    ):
        problems.append("CONTROL_CASE_IDS_INVALID")
    if len(truth_rows) != 40:
        problems.append("SOURCE_TRUTH_ROW_COUNT_INVALID")
        return problems
    case_by_id = {case["case_id"]: case for case in cases if nonempty_text(case.get("case_id"))}
    truth_ids = [row.get("case_id") for row in truth_rows]
    if (
        any(row.get("record_type") != "source_truth" for row in truth_rows)
        or not all(nonempty_text(case_id) for case_id in truth_ids)
        or len(set(truth_ids)) != 40
        or set(truth_ids) != set(case_by_id)
    ):
        problems.append("SOURCE_TRUTH_CASE_IDS_INVALID")
    else:
        gate = contract.get("case_preparation_gate") if isinstance(contract, dict) else {}
        problems.extend(
            validate_adjudicated_truth_rows(
                truth_rows,
                expected_case_ids=case_ids,
                expected_contract_id=research_contract_id,
                expected_preparation_contract_version=gate.get(
                    "preparation_contract_version"
                ),
                expected_locked_input_sha256=gate.get("locked_input_sha256"),
            )
        )
        truth_summary = derive_truth_summary(truth_rows)
        problems.extend(validate_positive_holdout_floor(cases, truth_summary))
    if (
        isinstance(contract, dict)
        and contract.get("map_builder_plugin_version") == MAP_BUILDER_PLUGIN_VERSION
        and contract.get("case_package_contract_version")
        == CASE_PACKAGE_CONTRACT_VERSION
        and contract_local_root is not None
    ):
        problems.extend(
            validate_complete_truth_rows(
                truth_rows,
                contract,
                contract_local_root,
                case_by_id=case_by_id,
                frozen_at=frozen_at or contract.get("frozen_at"),
            )
        )
    return problems


def content_first_contract_errors(
    contract: dict, *, final_outputs_required: bool
) -> list[str]:
    problems: list[str] = []
    missing = sorted(CONTENT_FIRST_REQUIRED - set(contract))
    if missing:
        problems.append("content_first_missing:" + ",".join(missing))
    if contract.get("execution_mode") != "content_first":
        problems.append("execution_mode:not_content_first")
    if contract.get("map_builder_plugin_version") != MAP_BUILDER_PLUGIN_VERSION:
        problems.append("MAP_BUILDER_PLUGIN_VERSION_INVALID")
    if aware_datetime(contract.get("created_at")) is None:
        problems.append("CONTRACT_CREATED_AT_INVALID")
    if not nonempty_text(contract.get("owner_authorization_reference")):
        problems.append("OWNER_AUTHORIZATION_REFERENCE_INVALID")
    if not (
        isinstance(contract.get("skill_git_commit"), str)
        and re.fullmatch(r"[0-9a-f]{40}", contract["skill_git_commit"])
    ):
        problems.append("SKILL_GIT_COMMIT_INVALID")
    if contract.get("workflow_director_plugin_version") != DIRECTOR_PLUGIN_VERSION:
        problems.append("WORKFLOW_DIRECTOR_PLUGIN_VERSION_INVALID")
    locked_at = aware_datetime((contract.get("case_preparation_gate") or {}).get("locked_at"))
    created_at = aware_datetime(contract.get("created_at"))
    if locked_at is not None and created_at is not None and created_at >= locked_at:
        problems.append("CONTRACT_CREATED_AT_INVALID")
    if (
        contract.get("case_package_contract_version")
        != CASE_PACKAGE_CONTRACT_VERSION
    ):
        problems.append("CASE_PACKAGE_CONTRACT_VERSION_INVALID")
    if (
        contract.get("baseline_method_contract") != R4_BASELINE_METHOD
        or contract.get("candidate_method_contract") != R4_CANDIDATE_METHOD
    ):
        problems.append("METHOD_ARMS_INVALID")
    problems.extend(content_first_default_deny_errors(contract))

    architecture = contract.get("terminology_architecture")
    if not isinstance(architecture, dict):
        problems.append("terminology_architecture:invalid")
    else:
        for field in (
            "global_skill_fixed_domain_terms_allowed",
            "case_specific_answer_terms_allowed_in_skill",
            "company_terms_allowed_in_semantic_screening",
        ):
            if architecture.get(field) is not False:
                problems.append(f"terminology_architecture.{field}:not_false")
        if set(architecture.get("concept_roles") or []) != CONTENT_FIRST_CONCEPT_ROLES:
            problems.append("terminology_architecture.concept_roles:invalid")
        if architecture.get("term_pack_state") not in {
            "frozen_empty_cold_start",
            "frozen_reviewed",
        }:
            problems.append("terminology_architecture.term_pack_state:invalid")
        if not nonempty_text(architecture.get("term_pack_reference")):
            problems.append("terminology_architecture.term_pack_reference:empty")
        if not real_lowercase_sha256(architecture.get("term_pack_sha256")):
            problems.append("terminology_architecture.term_pack_sha256:invalid")

    policy = contract.get("calibration_case_policy")
    if not isinstance(policy, dict):
        problems.append("calibration_case_policy:invalid")
    else:
        if policy.get("formal_case_count") != 40:
            problems.append("calibration_case_policy.formal_case_count:invalid")
        if (
            policy.get("minimum_new_unseen_accepted_positive_count")
            != MINIMUM_NEW_UNSEEN_ACCEPTED_POSITIVES
        ):
            problems.append(
                "calibration_case_policy.minimum_new_unseen_accepted_positive_count:invalid"
            )
        if policy.get("positive_denominator_source") != "accepted_adjudicated_truth_rows":
            problems.append(
                "calibration_case_policy.positive_denominator_source:invalid"
            )
        if policy.get("unresolved_counts_as_negative") is not False:
            problems.append(
                "calibration_case_policy.unresolved_counts_as_negative:not_false"
            )
        counts = policy.get("required_sampling_category_counts")
        if counts != CONTENT_FIRST_CATEGORY_COUNTS or sum(
            counts.values() if isinstance(counts, dict) else []
        ) != 40:
            problems.append(
                "calibration_case_policy.required_sampling_category_counts:invalid"
            )
        excluded_ids = policy.get("development_case_ids_excluded_from_formal")
        excluded_keys = (
            [normalized_identifier_key(value) for value in excluded_ids]
            if isinstance(excluded_ids, list) else []
        )
        if (
            not isinstance(excluded_ids, list)
            or any(key is None for key in excluded_keys)
            or len(set(excluded_keys)) != len(excluded_keys)
        ):
            problems.append("calibration_case_policy.development_case_ids_excluded_from_formal:invalid")
        if policy.get("selection_origin_counts") != CONTENT_FIRST_SELECTION_ORIGIN_COUNTS:
            problems.append("calibration_case_policy.selection_origin_counts:invalid")

    gates = contract.get("retrieval_efficiency_gates")
    if not isinstance(gates, dict) or gates.get("stability_repeat_case_count") != 6:
        problems.append("retrieval_efficiency_gates.stability_repeat_case_count:invalid")
    content_policy = contract.get("content_first_policy")
    if not isinstance(content_policy, dict):
        problems.append("content_first_policy:invalid")
    elif (
        content_policy.get("truth_scorecard_contract_version")
        != TRUTH_SCORECARD_CONTRACT_VERSION
    ):
        problems.append("content_first_policy.truth_scorecard_contract_version:invalid")

    problems.extend(strict_paired_execution_contract_errors(contract.get("paired_execution_contract")))

    r3_binding = contract.get("r3_case_source_manifest_reference_and_hash")
    if (
        not isinstance(r3_binding, dict)
        or set(r3_binding) != {"reference", "sha256"}
        or not nonempty_text(r3_binding.get("reference"))
        or not real_lowercase_sha256(r3_binding.get("sha256"))
    ):
        problems.append("r3_case_source_manifest_reference_and_hash:invalid")

    truth_reference = contract.get("source_truth_package_reference")
    truth_sha256 = contract.get("source_truth_package_sha256")
    if final_outputs_required:
        if not nonempty_text(truth_reference) or not real_lowercase_sha256(truth_sha256):
            problems.append("source_truth_package:invalid")
        summary = contract.get("adjudicated_truth_summary")
        if validate_truth_summary_integrity(summary):
            problems.append("adjudicated_truth_summary:invalid")
        visible_case_set = contract.get("visible_case_set_reference_and_hash")
        if not isinstance(visible_case_set, dict) or not nonempty_text(visible_case_set.get("reference")) or not real_lowercase_sha256(visible_case_set.get("sha256")):
            problems.append("visible_case_set_reference_and_hash:invalid")
        visible_freeze_receipt = contract.get("visible_case_freeze_receipt_reference_and_hash")
        if not isinstance(visible_freeze_receipt, dict) or not nonempty_text(visible_freeze_receipt.get("reference")) or not real_lowercase_sha256(visible_freeze_receipt.get("sha256")):
            problems.append("visible_case_freeze_receipt_reference_and_hash:invalid")
    elif truth_reference is not None or truth_sha256 is not None:
        problems.append("source_truth_package:not_empty_before_finalization")
    return problems


def frozen_contract_completeness_errors(
    contract: object, *, validate_case_preparation_gate: bool = True
) -> list[str]:
    if not isinstance(contract, dict):
        return ["semantic_research_contract must be an object"]
    mode_problems = execution_mode_errors(contract)
    if mode_problems:
        return mode_problems
    if contract.get("execution_mode") == "content_first":
        problems = content_first_contract_errors(contract, final_outputs_required=True)
        if contract.get("contract_state") != "frozen":
            problems.append("contract_state:not_frozen")
        case_set = contract.get("calibration_case_set_reference_and_hash")
        if (
            not isinstance(case_set, dict)
            or not nonempty_text(case_set.get("reference"))
            or not real_lowercase_sha256(case_set.get("sha256"))
        ):
            problems.append("calibration_case_set_reference_and_hash:invalid")
        batch = contract.get("batch_rule")
        if not isinstance(batch, dict) or not isinstance(batch.get("batch_size"), int) or batch["batch_size"] <= 0:
            problems.append("batch_rule.batch_size:invalid")
        controls = contract.get("control_case_rule")
        if not isinstance(controls, dict) or not controls.get("case_ids"):
            problems.append("control_case_rule:invalid")
        if validate_case_preparation_gate:
            gate = contract.get("case_preparation_gate")
            if not isinstance(gate, dict) or gate.get("state") != "locked" or gate.get("authorization") is not True:
                problems.append("case_preparation_gate:invalid")
            elif (
                not nonempty_text(gate.get("authorization_reference"))
                or not nonempty_text(gate.get("preparation_contract_version"))
                or not nonempty_text(gate.get("locked_at"))
                or not real_lowercase_sha256(gate.get("locked_input_sha256"))
            ):
                problems.append("case_preparation_gate:incomplete")
            elif gate.get("preparation_contract_version") == contract.get("contract_version"):
                problems.append("contract_version:not_new_after_case_preparation")
            elif gate.get("locked_input_sha256") != case_preparation_input_sha256(contract):
                problems.append("case_preparation_gate.locked_input_sha256:mismatch")
        return problems
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
    if validate_case_preparation_gate:
        gate = contract.get("case_preparation_gate")
        if not isinstance(gate, dict):
            problems.append("case_preparation_gate:invalid")
        else:
            for field in (
                "authorization_reference",
                "preparation_contract_version",
                "locked_at",
            ):
                if not nonempty_text(gate.get(field)):
                    problems.append(f"case_preparation_gate.{field}:empty")
            if gate.get("authorization") is not True:
                problems.append("case_preparation_gate.authorization:not_true")
            if gate.get("state") != "locked":
                problems.append("case_preparation_gate.state:not_locked")
            if not sha256_text(gate.get("locked_input_sha256")):
                problems.append("case_preparation_gate.locked_input_sha256:invalid")
            elif gate.get("locked_input_sha256") != case_preparation_input_sha256(contract):
                problems.append("case_preparation_gate.locked_input_sha256:mismatch")
            if gate.get("preparation_contract_version") == contract.get("contract_version"):
                problems.append("contract_version:not_new_after_case_preparation")
    return problems


def case_preparation_contract_completeness_errors(contract: object) -> list[str]:
    if not isinstance(contract, dict):
        return ["semantic_research_contract must be an object"]
    mode_problems = execution_mode_errors(contract)
    if mode_problems:
        return mode_problems
    if contract.get("execution_mode") == "content_first":
        problems = content_first_contract_errors(contract, final_outputs_required=False)
        if contract.get("contract_state") != "case_preparation_locked":
            problems.append("contract_state:not_case_preparation_locked")
        if not case_preparation_outputs_are_empty(contract):
            problems.append("case_preparation_outputs:not_empty")
        gate = contract.get("case_preparation_gate")
        if not isinstance(gate, dict) or gate.get("authorization") is not True or gate.get("state") != "locked":
            problems.append("case_preparation_gate:invalid")
        elif (
            not nonempty_text(gate.get("authorization_reference"))
            or gate.get("preparation_contract_version") != contract.get("contract_version")
            or not nonempty_text(gate.get("locked_at"))
            or not real_lowercase_sha256(gate.get("locked_input_sha256"))
        ):
            problems.append("case_preparation_gate:incomplete")
        elif gate.get("locked_input_sha256") != case_preparation_input_sha256(contract):
            problems.append("case_preparation_gate.locked_input_sha256:mismatch")
        return problems
    problems: list[str] = []
    if contract.get("contract_state") != "case_preparation_locked":
        problems.append("contract_state:not_case_preparation_locked")
    if not case_preparation_outputs_are_empty(contract):
        problems.append("case_preparation_outputs:not_empty")

    # Reuse every final-contract rule except the fields that case preparation
    # must genuinely produce. These internal sentinels are not returned or
    # written to disk.
    common_candidate = json.loads(json.dumps(contract))
    common_candidate["contract_state"] = "frozen"
    common_candidate["frozen_at"] = "INTERNAL-COMMON-VALIDATION"
    common_candidate["calibration_case_set_reference_and_hash"] = {
        "reference": "INTERNAL-NOT-SERIALIZED.jsonl",
        "sha256": "0" * 64,
    }
    if isinstance(common_candidate.get("batch_rule"), dict):
        common_candidate["batch_rule"]["batch_size"] = 1
    if isinstance(common_candidate.get("control_case_rule"), dict):
        common_candidate["control_case_rule"]["case_ids"] = ["INTERNAL-NOT-SERIALIZED"]
    problems.extend(
        frozen_contract_completeness_errors(
            common_candidate, validate_case_preparation_gate=False
        )
    )

    gate = contract.get("case_preparation_gate")
    if not isinstance(gate, dict):
        problems.append("case_preparation_gate:invalid")
    else:
        for field in (
            "authorization_reference",
            "preparation_contract_version",
            "locked_at",
        ):
            if not nonempty_text(gate.get(field)):
                problems.append(f"case_preparation_gate.{field}:empty")
        if gate.get("authorization") is not True:
            problems.append("case_preparation_gate.authorization:not_true")
        if gate.get("preparation_contract_version") != contract.get("contract_version"):
            problems.append("case_preparation_gate.preparation_contract_version:mismatch")
        if gate.get("state") != "locked":
            problems.append("case_preparation_gate.state:not_locked")
        if not sha256_text(gate.get("locked_input_sha256")):
            problems.append("case_preparation_gate.locked_input_sha256:invalid")
        elif gate.get("locked_input_sha256") != case_preparation_input_sha256(contract):
            problems.append("case_preparation_gate.locked_input_sha256:mismatch")
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

    if isinstance(contract, dict) and contract.get("execution_mode") == "content_first":
        for reference_problem in content_first_local_frozen_reference_errors(contract, workspace):
            add(errors, reference_problem, str(workspace))
        def verify_content_reference(reference: object, expected_hash: object, prefix: str) -> Path | None:
            if (
                not nonempty_text(reference)
                or not real_lowercase_sha256(expected_hash)
                or Path(reference).is_absolute()
                or ".." in Path(reference).parts
            ):
                add(errors, f"{prefix}_REFERENCE_INVALID", repr(reference))
                return None
            path = (workspace / Path(reference)).resolve()
            try:
                path.relative_to(workspace)
            except ValueError:
                add(errors, f"{prefix}_PATH_ESCAPE", str(path))
                return None
            if not path.is_file():
                add(errors, f"{prefix}_MISSING", str(path))
                return None
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                add(errors, f"{prefix}_HASH_MISMATCH", str(path))
            return path

        architecture = contract.get("terminology_architecture")
        term_path = None
        if isinstance(architecture, dict):
            term_reference = architecture.get("term_pack_reference")
            if not isinstance(term_reference, str) or not term_reference.startswith("01-术语桥/"):
                add(errors, "TERMINOLOGY_BRIDGE_REFERENCE_INVALID", repr(term_reference))
            else:
                term_path = verify_content_reference(
                    term_reference, architecture.get("term_pack_sha256"), "TERMINOLOGY_BRIDGE"
                )
        case_set = contract.get("calibration_case_set_reference_and_hash")
        case_path = None
        if isinstance(case_set, dict):
            case_path = verify_content_reference(
                case_set.get("reference"), case_set.get("sha256"), "CALIBRATION_CASE_SET"
            )
        visible_case_set = contract.get("visible_case_set_reference_and_hash")
        visible_case_path = None
        if isinstance(visible_case_set, dict):
            visible_case_path = verify_content_reference(
                visible_case_set.get("reference"), visible_case_set.get("sha256"), "VISIBLE_CASE_SET"
            )
        truth_path = verify_content_reference(
            contract.get("source_truth_package_reference"),
            contract.get("source_truth_package_sha256"),
            "SOURCE_TRUTH_PACKAGE",
        )
        taxonomy_path = verify_content_reference(
            contract.get("taxonomy_snapshot_reference"),
            contract.get("taxonomy_snapshot_sha256"),
            "TAXONOMY_SNAPSHOT",
        )
        if taxonomy_path is not None:
            try:
                taxonomy_payload = load_json(taxonomy_path)
                if taxonomy_payload.get("terminal_node_count") != contract.get("terminal_node_count"):
                    add(errors, "TAXONOMY_SNAPSHOT_COUNT_MISMATCH", str(taxonomy_path))
            except (json.JSONDecodeError, OSError, AttributeError) as exc:
                add(errors, "TAXONOMY_SNAPSHOT_INVALID", str(exc))
        prompt_rows = contract.get("prompt_template_references_and_hashes")
        if not isinstance(prompt_rows, list) or not prompt_rows:
            add(errors, "PROMPT_TEMPLATE_REFERENCES_INVALID", "at least one frozen prompt is required")
        else:
            for row in prompt_rows:
                if not isinstance(row, dict):
                    add(errors, "PROMPT_TEMPLATE_REFERENCES_INVALID", repr(row))
                    continue
                verify_content_reference(
                    row.get("reference"), row.get("sha256"), "PROMPT_TEMPLATE"
                )
        if term_path is not None:
            term_rows, term_errors = load_terminology_rows(term_path)
            term_errors.extend(validate_terminology_rows(term_rows, contract_id))
            header = next(
                (row for row in term_rows if row.get("record_type") == "terminology_bridge_contract"),
                {},
            )
            gate = contract.get("case_preparation_gate")
            if not isinstance(gate, dict) or header.get("contract_version") != gate.get("preparation_contract_version"):
                add(errors, "TERMINOLOGY_BRIDGE_VERSION_MISMATCH", str(header.get("contract_version")))
            if term_errors:
                add(errors, "TERMINOLOGY_BRIDGE_INVALID", ";".join(error["code"] for error in term_errors))
        if case_path is not None and truth_path is not None:
            try:
                content_problems = validate_content_first_case_truth_rows(
                    load_jsonl(case_path),
                    load_jsonl(truth_path),
                    contract_id,
                    contract.get("calibration_case_policy"),
                    (contract.get("control_case_rule") or {}).get("case_ids"),
                    (contract.get("retrieval_efficiency_gates") or {}).get("stability_repeat_case_count"),
                    contract=contract,
                    contract_local_root=workspace,
                )
                if content_problems:
                    add(errors, "FORMAL_CONTENT_SET_INVALID", ";".join(content_problems))
            except (json.JSONDecodeError, OSError, ValueError) as exc:
                add(errors, "FORMAL_CONTENT_SET_INVALID", str(exc))
        if case_path is not None and visible_case_path is not None:
            try:
                visible_problems = visible_case_set_workspace_errors(
                    load_jsonl(visible_case_path), load_jsonl(case_path), contract_id
                )
                if visible_problems:
                    add(errors, visible_problems[0], str(visible_case_path))
            except (json.JSONDecodeError, OSError, ValueError) as exc:
                add(errors, "VISIBLE_CASE_SET_INVALID", str(exc))
        for relative, record_type, states in (
            ("03-运行原始记录/candidate/screening-records.jsonl", "SCREENING", SCREENING_RESULTS),
            ("05-证据包/evidence-records.jsonl", "EVIDENCE", EVIDENCE_STATES),
        ):
            record_path = workspace / relative
            if not record_path.is_file():
                continue
            try:
                for record in load_jsonl(record_path):
                    if record.get("research_contract_id") != contract_id or record.get("contract_version") != contract_version:
                        add(errors, f"{record_type}_CONTRACT_VERSION_MISMATCH", str(record_path))
                    state_field = "screening_result" if record_type == "SCREENING" else "evidence_state"
                    if record.get(state_field) not in states:
                        add(errors, f"{record_type}_STATE_INVALID", str(record_path))
            except (json.JSONDecodeError, OSError, ValueError) as exc:
                add(errors, f"{record_type}_RECORDS_INVALID", str(exc))
        handoff_root = workspace / "04-模型交接"
        if handoff_root.is_dir():
            for packet_path in handoff_root.rglob("*.json"):
                try:
                    packet = load_json(packet_path)
                except (json.JSONDecodeError, OSError) as exc:
                    add(errors, "MODEL_PACKET_INVALID", str(exc))
                    continue
                if not isinstance(packet, dict):
                    add(errors, "MODEL_PACKET_FORMAL_RECORD_INVALID", str(packet_path))
                    continue
                selected_formal_keys = [
                    key for key in FORMAL_MODEL_RECORD_KEYS if key in packet
                ]
                if len(selected_formal_keys) != 1:
                    add(errors, "MODEL_PACKET_FORMAL_RECORD_INVALID", str(packet_path))
                    continue
                formal_record_key = selected_formal_keys[0]
                packet_body = packet[formal_record_key]
                if not isinstance(packet_body, dict):
                    add(errors, "MODEL_PACKET_FORMAL_RECORD_INVALID", str(packet_path))
                    continue
                if packet_body.get("research_contract_id") != contract_id or packet_body.get("contract_version") != contract_version:
                    add(errors, "MODEL_PACKET_CONTRACT_VERSION_MISMATCH", str(packet_path))
                    continue
                if formal_record_key == "semantic_model_return" and not nonempty_text(packet_body.get("result_state")):
                    add(errors, "MODEL_RETURN_STATE_INVALID", str(packet_path))
                if formal_record_key == "semantic_model_receipt" and not nonempty_text(packet_body.get("acceptance_state")):
                    add(errors, "MODEL_RECEIPT_STATE_INVALID", str(packet_path))
        report = {"status": "FAIL" if errors else "PASS", "errors": errors}
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        else:
            print(report["status"])
            for error in errors:
                print(f"{error['code']}: {error['detail']}")
        return 1 if errors else 0

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
