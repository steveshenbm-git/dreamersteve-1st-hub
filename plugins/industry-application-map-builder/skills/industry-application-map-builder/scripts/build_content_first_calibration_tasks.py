#!/usr/bin/env python3
"""Build isolated truth-blind task pairs from a final frozen content-first contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from typing import Any
import unicodedata
from urllib.parse import unquote

from validate_semantic_research_workspace import frozen_contract_completeness_errors, load_jsonl


VISIBLE_CASE_KEYS = {
    "case_id",
    "taxonomy_node",
    "product_neutral_research_theme",
    "risk_flags",
}
VISIBLE_NODE_KEYS = {
    "taxonomy_node_id",
    "code",
    "level",
    "name_zh",
    "breadcrumb",
    "official_definition_or_null",
    "included_activities_or_null",
    "excluded_or_adjacent_activities_or_null",
    "official_source_reference",
    "official_source_sha256",
}
FORBIDDEN_TRUTH_KEYS = {
    "truth_label",
    "expected_screening_result",
    "expected_semantic_work_state",
    "expected_evidence_state_before_B",
    "known_positive",
    "truth_disposition",
    "evidence_quality",
    "adjudication_state",
    "adjudication_version",
    "reopen_reason",
    "supersedes_truth_sha256",
    "selection_reason",
    "source_refs",
    "truth_boundary",
    "primary_category",
    "sampling_category",
}
FORBIDDEN_VISIBLE_MARKERS = FORBIDDEN_TRUTH_KEYS | {
    "receiver_snapshot_sha256",
    "other_arm_output",
    "receiver", "accepted_answer", "accepted_answers", "scorecard", "score_card",
}
THREE_LINK_GATE = [
    "taxonomy_membership_basis",
    "output_or_subprocess_basis",
    "mechanism_or_use_point_basis",
]
ARMS = ("baseline_full_depth_v1", "screen_then_expand_v2")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PAIRED_EXECUTION_KEYS = {
    "declared_model_and_configuration", "tools", "source_permissions", "observation_window",
    "budgets", "frozen_artifact_references_and_hashes", "fresh_context_required",
    "truth_isolation_required", "other_arm_isolation_required", "prior_case_isolation_required",
    "append_only_outputs_required", "model_execution_authorized",
}
ARTIFACT_GROUPS = ("prompt", "schema", "config", "rubric")
PAIRED_ARTIFACT_KEYS = set(ARTIFACT_GROUPS)
ARTIFACT_ROW_KEYS = {"reference", "sha256"}
MODEL_CONFIGURATION_KEYS = {"model", "configuration_reference", "configuration_sha256"}
BUDGET_KEYS = {"query_budget", "source_open_budget", "elapsed_seconds_budget", "output_token_budget"}
RECEIPT_KEYS = {
    "authorization_id", "authorized_at", "permitted_action", "final_contract_sha256",
    "formal_case_set_sha256", "visible_case_set_sha256", "output_scope",
    "model_execution_authorized", "full_screening_authorized",
}
VISIBLE_HEADER_KEYS = {
    "record_type", "visible_case_set_id", "research_contract_id", "visible_case_set_state",
    "visible_only", "truth_data_allowed", "frozen_before_truth_preparation", "freeze_authorization_reference",
    "frozen_at", "case_count", "actual_case_record_count", "formal_case_ids",
}
VISIBLE_RECORD_KEYS = {"record_type", "research_contract_id", *VISIBLE_CASE_KEYS}


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 1


def canonical_json_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative_path(root: Path, reference: object) -> Path | None:
    if not isinstance(reference, str) or not reference or not reference.strip():
        return None
    normalized = PurePosixPath(reference).as_posix()
    if reference != normalized or normalized == "." or "\\" in reference:
        return None
    candidate = PurePosixPath(reference)
    if candidate.is_absolute() or any(part in {".", ".."} for part in candidate.parts):
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def normalized_marker_text(value: str) -> str:
    decoded = value
    for _ in range(3):
        next_value = unquote(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    normalized = unicodedata.normalize("NFKC", decoded).casefold()
    return "".join(character for character in normalized if character.isalnum())


FORBIDDEN_NORMALIZED_MARKERS = {
    normalized_marker_text(marker) for marker in FORBIDDEN_VISIBLE_MARKERS
}


def contains_forbidden_marker(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            contains_forbidden_marker(key) or contains_forbidden_marker(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(contains_forbidden_marker(item) for item in value)
    if isinstance(value, str):
        normalized = normalized_marker_text(value)
        return any(marker in normalized for marker in FORBIDDEN_NORMALIZED_MARKERS)
    return False


def safe_case_id(case_id: object) -> bool:
    if not nonempty_text(case_id) or not isinstance(case_id, str):
        return False
    return (
        unicodedata.normalize("NFKC", case_id) == case_id
        and "/" not in case_id and "\\" not in case_id and "." not in case_id
        and not any(character.isspace() or ord(character) < 32 for character in case_id)
    )


def formal_case_ids_from_rows(rows: list[dict[str, Any]], research_contract_id: object) -> list[str] | None:
    headers = [row for row in rows if row.get("record_type") == "visible_case_set_contract"]
    cases = [row for row in rows if row.get("record_type") == "visible_calibration_case"]
    if len(headers) != 1 or len(cases) != 40 or set(headers[0]) != VISIBLE_HEADER_KEYS or headers[0].get("research_contract_id") != research_contract_id:
        return None
    header = headers[0]
    if header.get("visible_case_set_state") != "frozen_visible_only" or header.get("visible_only") is not True or header.get("truth_data_allowed") is not False or header.get("frozen_before_truth_preparation") is not True or not nonempty_text(header.get("freeze_authorization_reference")) or not nonempty_text(header.get("frozen_at")) or header.get("case_count") != 40 or header.get("actual_case_record_count") != 40 or not nonempty_text(header.get("visible_case_set_id")):
        return None
    declared = headers[0].get("formal_case_ids")
    observed = [case.get("case_id") for case in cases]
    if not isinstance(declared, list) or declared != observed or len(declared) != 40:
        return None
    if not all(safe_case_id(case_id) for case_id in declared):
        return None
    normalized = [unicodedata.normalize("NFKC", case_id).casefold() for case_id in declared]
    return list(declared) if len(set(normalized)) == 40 else None


def iso8601_before(starts_at: object, ends_at: object) -> bool:
    if not nonempty_text(starts_at) or not nonempty_text(ends_at):
        return False
    try:
        start = datetime.fromisoformat(str(starts_at).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(ends_at).replace("Z", "+00:00"))
    except ValueError:
        return False
    return start.tzinfo is not None and end.tzinfo is not None and start < end


def load_source_observation_schema(root: Path, paired: dict[str, Any]) -> list[dict[str, Any]]:
    rows = paired["frozen_artifact_references_and_hashes"]["schema"]
    if len(rows) != 1:
        raise ValueError("exactly one source-observation schema artifact is required")
    path = safe_relative_path(root, rows[0]["reference"])
    if path is None or not path.is_file() or file_sha256(path) != rows[0]["sha256"]:
        raise ValueError("contract-local source-observation schema hash mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    observation_body = payload["content_source_observation"]
    if set(payload) != {"schema_version", "content_source_observation"} or payload.get("schema_version") != "1.0" or not isinstance(observation_body, dict) or set(observation_body) != {"case_id", "method_arm", "source_observations", "unknown_items"} or observation_body.get("case_id") is not None or observation_body.get("method_arm") is not None or observation_body.get("unknown_items") != []:
        raise ValueError("source observation schema exact envelope invalid")
    observations = observation_body["source_observations"]
    item_keys = {"source_url_or_null", "publisher_or_null", "title_or_null", "original_location_or_null", "bounded_summary_or_null", "access_state", "conditions", "limitations", "counterevidence"}
    if not isinstance(observations, list) or len(observations) != 1 or not isinstance(observations[0], dict) or set(observations[0]) != item_keys or any(observations[0][key] is not None for key in ("source_url_or_null", "publisher_or_null", "title_or_null", "original_location_or_null", "bounded_summary_or_null")) or observations[0].get("access_state") != "UNVERIFIED" or any(observations[0][key] != [] for key in ("conditions", "limitations", "counterevidence")):
        raise ValueError("source observation schema must own a non-empty array")
    return observations


def paired_execution_contract_errors(contract: dict[str, Any]) -> list[str]:
    paired = contract.get("paired_execution_contract")
    if not isinstance(paired, dict):
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    if set(paired) != PAIRED_EXECUTION_KEYS:
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    required_truth_blind_flags = (
        "fresh_context_required",
        "truth_isolation_required",
        "other_arm_isolation_required",
        "prior_case_isolation_required",
        "append_only_outputs_required",
    )
    if any(paired.get(name) is not True for name in required_truth_blind_flags) or paired.get("model_execution_authorized") is not False:
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    model = paired.get("declared_model_and_configuration")
    if not isinstance(model, dict) or set(model) != MODEL_CONFIGURATION_KEYS or not nonempty_text(model.get("model")) or not nonempty_text(model.get("configuration_reference")) or not SHA256.fullmatch(str(model.get("configuration_sha256", ""))):
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    if not isinstance(paired.get("tools"), list) or not paired["tools"] or not all(nonempty_text(item) for item in paired["tools"]) or len(set(paired["tools"])) != len(paired["tools"]):
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    if not isinstance(paired.get("source_permissions"), list) or not paired["source_permissions"] or not all(nonempty_text(item) for item in paired["source_permissions"]) or len(set(paired["source_permissions"])) != len(paired["source_permissions"]):
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    window = paired.get("observation_window")
    budget = paired.get("budgets")
    if not isinstance(window, dict) or set(window) != {"starts_at", "ends_at"} or not iso8601_before(window.get("starts_at"), window.get("ends_at")):
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    if not isinstance(budget, dict) or set(budget) != BUDGET_KEYS or any(type(value) is not int or value <= 0 for value in budget.values()):
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    artifacts = paired.get("frozen_artifact_references_and_hashes")
    if not isinstance(artifacts, dict) or set(artifacts) != PAIRED_ARTIFACT_KEYS:
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    references: list[str] = []
    config_rows: list[dict[str, Any]] = []
    for group in ARTIFACT_GROUPS:
        rows = artifacts.get(group)
        if not isinstance(rows, list) or not rows:
            return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
        for row in rows:
            if not isinstance(row, dict) or set(row) != ARTIFACT_ROW_KEYS or not nonempty_text(row.get("reference")) or not SHA256.fullmatch(str(row.get("sha256", ""))):
                return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
            references.append(row["reference"])
            if group == "config":
                config_rows.append(row)
    if len(references) != len(set(references)) or len(config_rows) != 1:
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    if model["configuration_reference"] != config_rows[0]["reference"] or model["configuration_sha256"] != config_rows[0]["sha256"]:
        return ["PAIRED_EXECUTION_CONTRACT_INVALID"]
    return []


def verify_contract_local_references(contract: dict[str, Any], root: Path) -> tuple[dict[str, str] | None, str | None]:
    expected: list[tuple[str, object, object]] = []
    architecture = contract.get("terminology_architecture")
    if not isinstance(architecture, dict):
        return None, "TERMINOLOGY_BRIDGE_REFERENCE_INVALID"
    expected.append(("terminology", architecture.get("term_pack_reference"), architecture.get("term_pack_sha256")))
    expected.append(("taxonomy", contract.get("taxonomy_snapshot_reference"), contract.get("taxonomy_snapshot_sha256")))
    prompt_rows = contract.get("prompt_template_references_and_hashes")
    if not isinstance(prompt_rows, list) or not prompt_rows:
        return None, "PROMPT_TEMPLATE_REFERENCE_INVALID"
    expected.extend(("prompt", row.get("reference"), row.get("sha256")) for row in prompt_rows if isinstance(row, dict))
    paired = contract.get("paired_execution_contract")
    artifacts = paired.get("frozen_artifact_references_and_hashes") if isinstance(paired, dict) else None
    if not isinstance(artifacts, dict):
        return None, "PAIRED_EXECUTION_CONTRACT_INVALID"
    for group in ("prompt", "schema", "config", "rubric"):
        rows = artifacts.get(group)
        if not isinstance(rows, list):
            return None, "PAIRED_EXECUTION_CONTRACT_INVALID"
        expected.extend((group, row.get("reference"), row.get("sha256")) for row in rows if isinstance(row, dict))
    protected_hashes = {
        contract.get("calibration_case_set_reference_and_hash", {}).get("sha256"),
        contract.get("visible_case_set_reference_and_hash", {}).get("sha256"),
        contract.get("visible_case_freeze_receipt_reference_and_hash", {}).get("sha256"),
        contract.get("source_truth_package_sha256"),
    }
    forbidden_references = {
        contract.get("calibration_case_set_reference_and_hash", {}).get("reference"),
        contract.get("visible_case_set_reference_and_hash", {}).get("reference"),
        contract.get("visible_case_freeze_receipt_reference_and_hash", {}).get("reference"),
        contract.get("source_truth_package_reference"),
    }
    protected_parent_roots = {
        PurePosixPath(reference).parent
        for reference in (
            contract.get("calibration_case_set_reference_and_hash", {}).get("reference"),
            contract.get("source_truth_package_reference"),
        )
        if isinstance(reference, str) and PurePosixPath(reference).parent != PurePosixPath(".")
    }
    snapshots: dict[str, str] = {}
    identities: set[tuple[int, int]] = set()
    for label, reference, expected_sha in expected:
        path = safe_relative_path(root, reference)
        if path is None:
            return None, f"{label.upper()}_REFERENCE_INVALID"
        if expected_sha in protected_hashes:
            return None, "TASK_VISIBLE_ARTIFACT_HASH_COLLISION"
        if reference in forbidden_references:
            return None, "TASK_VISIBLE_ARTIFACT_ROLE_COLLISION"
        candidate = PurePosixPath(reference)
        if any(candidate.parts[:len(parent.parts)] == parent.parts for parent in protected_parent_roots):
            return None, "TASK_VISIBLE_ARTIFACT_ROOT_COLLISION"
        if not path.is_file():
            return None, f"{label.upper()}_MISSING"
        actual = file_sha256(path)
        if actual != expected_sha:
            return None, f"{label.upper()}_HASH_MISMATCH"
        if actual in protected_hashes:
            return None, "TASK_VISIBLE_ARTIFACT_HASH_COLLISION"
        if reference in forbidden_references:
            return None, "TASK_VISIBLE_ARTIFACT_ROLE_COLLISION"
        stat = path.stat()
        identity = (stat.st_dev, stat.st_ino)
        if identity in identities:
            return None, "TASK_VISIBLE_ARTIFACT_IDENTITY_COLLISION"
        identities.add(identity)
        snapshots[path.relative_to(root.resolve()).as_posix()] = actual
    return snapshots, None


def nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_final_contract(payload: object, visible_case_set_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(payload, dict) or not isinstance(payload.get("semantic_research_contract"), dict):
        return None, "CONTRACT_INVALID"
    contract = payload["semantic_research_contract"]
    if contract.get("contract_state") != "frozen" or contract.get("execution_mode") != "content_first":
        return None, "FINAL_CONTENT_CONTRACT_REQUIRED"
    if contract.get("execution_authorized") is not False:
        return None, "MODEL_EXECUTION_AUTHORIZATION_INVALID"
    problems = frozen_contract_completeness_errors(contract)
    if problems:
        return None, "FINAL_CONTRACT_INCOMPLETE"
    formal_reference = contract.get("calibration_case_set_reference_and_hash")
    visible_reference = contract.get("visible_case_set_reference_and_hash")
    if not isinstance(formal_reference, dict) or not SHA256.fullmatch(str(formal_reference.get("sha256", ""))):
        return None, "FORMAL_CASE_SET_HASH_INVALID"
    if not isinstance(visible_reference, dict) or not SHA256.fullmatch(str(visible_reference.get("sha256", ""))):
        return None, "VISIBLE_CASE_SET_HASH_INVALID"
    if file_sha256(visible_case_set_path) != visible_reference["sha256"]:
        return None, "VISIBLE_CASE_SET_HASH_MISMATCH"
    if paired_execution_contract_errors(contract):
        return None, "PAIRED_EXECUTION_CONTRACT_INVALID"
    return contract, None


def exact_official_node(node: object) -> dict[str, Any] | None:
    if not isinstance(node, dict) or set(node) != VISIBLE_NODE_KEYS:
        return None
    if not (
        nonempty_text(node.get("taxonomy_node_id"))
        and nonempty_text(node.get("code"))
        and type(node.get("level")) is int
        and nonempty_text(node.get("name_zh"))
        and isinstance(node.get("breadcrumb"), list)
        and node["breadcrumb"]
        and all(nonempty_text(item) for item in node["breadcrumb"])
        and nonempty_text(node.get("official_source_reference"))
        and SHA256.fullmatch(str(node.get("official_source_sha256", "")))
    ):
        return None
    for name in (
        "official_definition_or_null",
        "included_activities_or_null",
        "excluded_or_adjacent_activities_or_null",
    ):
        if node[name] is not None and not nonempty_text(node[name]):
            return None
    return {key: node[key] for key in sorted(VISIBLE_NODE_KEYS)}


def visible_input_from_case(case: object) -> dict[str, Any] | None:
    if not isinstance(case, dict) or set(case) != VISIBLE_RECORD_KEYS or case.get("record_type") != "visible_calibration_case":
        return None
    # The case can contain sealed truth and selection data; only these exact
    # visible fields are copied.  Nested case structures never pass through.
    visible = {key: case.get(key) for key in VISIBLE_CASE_KEYS}
    if not nonempty_text(visible["case_id"]) or not nonempty_text(visible["product_neutral_research_theme"]):
        return None
    if not isinstance(visible["risk_flags"], list) or not all(nonempty_text(item) for item in visible["risk_flags"]):
        return None
    node = exact_official_node(visible["taxonomy_node"])
    if node is None:
        return None
    projection = {
        "case_id": visible["case_id"],
        "taxonomy_node": node,
        "product_neutral_research_theme": visible["product_neutral_research_theme"],
        "risk_flags": list(visible["risk_flags"]),
    }
    return None if contains_forbidden_marker(projection) else projection


def visible_case_set_errors(rows: list[dict[str, Any]], research_contract_id: object) -> tuple[list[str], list[str]]:
    ids = formal_case_ids_from_rows(rows, research_contract_id)
    cases = [row for row in rows if row.get("record_type") == "visible_calibration_case"]
    if ids is None or any(row.get("record_type") not in {"visible_case_set_contract", "visible_calibration_case"} for row in rows):
        return ["VISIBLE_CASE_SET_INVALID"], []
    if [case.get("case_id") for case in cases] != ids or any(
        case.get("research_contract_id") != research_contract_id or visible_input_from_case(case) is None
        for case in cases
    ):
        return ["VISIBLE_CASE_PROJECTION_INVALID"], []
    return [], ids


def method_fields(arm: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if arm == "baseline_full_depth_v1":
        return (
            {
                "method_arm": arm,
                "full_depth_required": True,
                "broad_node_output_family_decomposition_required": False,
                "deep_expansion_policy": "all_cases",
            },
            {
                "enabled": False,
                "trigger": "not_available_in_baseline",
                "case_local": True,
                "mutates_frozen_term_pack": False,
                "allowed_use": "retrieval_only",
            },
        )
    return (
        {
            "method_arm": arm,
            "full_depth_required": False,
            "broad_node_output_family_decomposition_required": True,
            "deep_expansion_policy": "three_link_hypothesis_ambiguous_conflict_or_high_risk_broad_node",
        },
        {
            "enabled": True,
            "trigger": "core_search_complete_without_three_link_bridge",
            "case_local": True,
            "mutates_frozen_term_pack": False,
            "allowed_use": "retrieval_only",
        },
    )


def task_for(contract: dict[str, Any], visible_input: dict[str, Any], arm: str, observations: list[dict[str, Any]]) -> dict[str, Any]:
    method_contract, dynamic_discovery = method_fields(arm)
    term_architecture = contract["terminology_architecture"]
    return {
        "schema_version": "1.0",
        "content_first_calibration_task": {
            "task_id": f"{visible_input['case_id']}--{arm}",
            "research_contract_id": contract["research_contract_id"],
            "contract_version": contract["contract_version"],
            "method_arm": arm,
            "execution_authorized": False,
            "paired_execution_contract": contract["paired_execution_contract"],
            "taxonomy_snapshot": {
                "reference": contract["taxonomy_snapshot_reference"],
                "sha256": contract["taxonomy_snapshot_sha256"],
            },
            "visible_input": visible_input,
            "input_hash_algorithm": "sha256_canonical_json_v1",
            "visible_input_sha256": canonical_json_sha256(visible_input),
            "frozen_terminology_pack": {
                "reference": term_architecture["term_pack_reference"],
                "sha256": term_architecture["term_pack_sha256"],
                "allowed_use": "retrieval_only",
                "mutates_frozen_term_pack": False,
            },
            "method_contract": method_contract,
            "output_family_decomposition": {
                "required_before_dynamic_term_discovery": arm == "screen_then_expand_v2",
                "official_basis_required": True,
                "model_generated_families_are_hypotheses_only": True,
            },
            "dynamic_term_discovery": dynamic_discovery,
            "three_link_gate": THREE_LINK_GATE,
            "expected_return_schema": {
                "source_observations": observations,
                "unknown_items": "array",
            },
        },
    }


def authorization_receipt_error(
    receipt_path: Path, expected_sha256: object, final_contract_sha256: str, formal_case_set_sha256: str,
    visible_case_set_sha256: str,
    expected_output_scope: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    if not SHA256.fullmatch(str(expected_sha256)):
        return None, "EXPECTED_AUTHORIZATION_RECEIPT_SHA256_INVALID"
    if not receipt_path.is_file():
        return None, "AUTHORIZATION_RECEIPT_MISSING"
    if file_sha256(receipt_path) != expected_sha256:
        return None, "AUTHORIZATION_RECEIPT_HASH_MISMATCH"
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        if set(payload) != {"schema_version", "package_generation_authorization_receipt"} or payload["schema_version"] != "1.0":
            return None, "AUTHORIZATION_RECEIPT_INVALID"
        receipt = payload["package_generation_authorization_receipt"]
    except (OSError, ValueError, TypeError):
        return None, "AUTHORIZATION_RECEIPT_INVALID"
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_KEYS:
        return None, "AUTHORIZATION_RECEIPT_INVALID"
    if (
        not nonempty_text(receipt.get("authorization_id"))
        or not iso8601_before(receipt.get("authorized_at"), "9999-12-31T23:59:59+00:00")
        or receipt.get("permitted_action") != "package_generation_only"
        or receipt.get("final_contract_sha256") != final_contract_sha256
        or receipt.get("formal_case_set_sha256") != formal_case_set_sha256
        or receipt.get("visible_case_set_sha256") != visible_case_set_sha256
        or receipt.get("output_scope") != str(expected_output_scope.resolve())
        or receipt.get("model_execution_authorized") is not False
        or receipt.get("full_screening_authorized") is not False
    ):
        return None, "AUTHORIZATION_RECEIPT_INVALID"
    return receipt, None


def exact_task_errors(task: object, contract: dict[str, Any], visible: dict[str, Any], arm: str, observations: list[dict[str, Any]]) -> list[str]:
    if contains_forbidden_marker(task):
        return ["TASK_FORBIDDEN_LEAKAGE"]
    if not isinstance(task, dict) or set(task) != {"schema_version", "content_first_calibration_task"} or task.get("schema_version") != "1.0":
        return ["TASK_SCHEMA_INVALID"]
    body = task["content_first_calibration_task"]
    required = {
        "task_id", "research_contract_id", "contract_version", "method_arm", "execution_authorized",
        "paired_execution_contract", "taxonomy_snapshot", "visible_input", "input_hash_algorithm",
        "visible_input_sha256", "frozen_terminology_pack", "method_contract", "output_family_decomposition",
        "dynamic_term_discovery", "three_link_gate", "expected_return_schema",
    }
    if not isinstance(body, dict) or set(body) != required or body.get("task_id") != f"{visible['case_id']}--{arm}" or body.get("research_contract_id") != contract["research_contract_id"] or body.get("contract_version") != contract["contract_version"] or body.get("method_arm") != arm or body.get("execution_authorized") is not False:
        return ["TASK_SCHEMA_INVALID"]
    if body.get("paired_execution_contract") != contract["paired_execution_contract"] or paired_execution_contract_errors(contract):
        return ["TASK_SCHEMA_INVALID"]
    if body.get("visible_input") != visible or body.get("visible_input_sha256") != canonical_json_sha256(visible) or body.get("input_hash_algorithm") != "sha256_canonical_json_v1":
        return ["TASK_SCHEMA_INVALID"]
    if set(body.get("taxonomy_snapshot", {})) != {"reference", "sha256"} or body["taxonomy_snapshot"] != {"reference": contract["taxonomy_snapshot_reference"], "sha256": contract["taxonomy_snapshot_sha256"]}:
        return ["TASK_SCHEMA_INVALID"]
    architecture = contract["terminology_architecture"]
    if set(body.get("frozen_terminology_pack", {})) != {"reference", "sha256", "allowed_use", "mutates_frozen_term_pack"} or body["frozen_terminology_pack"] != {"reference": architecture["term_pack_reference"], "sha256": architecture["term_pack_sha256"], "allowed_use": "retrieval_only", "mutates_frozen_term_pack": False}:
        return ["TASK_SCHEMA_INVALID"]
    expected_method, expected_dynamic = method_fields(arm)
    if body.get("method_contract") != expected_method or body.get("dynamic_term_discovery") != expected_dynamic or body.get("three_link_gate") != THREE_LINK_GATE:
        return ["TASK_SCHEMA_INVALID"]
    if body.get("output_family_decomposition") != {"required_before_dynamic_term_discovery": arm == "screen_then_expand_v2", "official_basis_required": True, "model_generated_families_are_hypotheses_only": True}:
        return ["TASK_SCHEMA_INVALID"]
    if body.get("expected_return_schema") != {"source_observations": observations, "unknown_items": "array"}:
        return ["TASK_SCHEMA_INVALID"]
    return []


def validated_inputs(args: argparse.Namespace, expected_output_scope: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]] | None, list[dict[str, Any]] | None, dict[str, str] | None, list[dict[str, Any]] | None, str | None]:
    contract_path = args.contract.resolve()
    visible_case_set_path = args.visible_case_set.resolve()
    contract_root = args.contract_local_root.resolve()
    if not contract_path.is_file():
        return None, None, None, None, None, "CONTRACT_MISSING"
    if not visible_case_set_path.is_file():
        return None, None, None, None, None, "VISIBLE_CASE_SET_MISSING"
    if not SHA256.fullmatch(args.expected_final_contract_sha256):
        return None, None, None, None, None, "EXPECTED_FINAL_CONTRACT_SHA256_INVALID"
    if not contract_root.is_dir():
        return None, None, None, None, None, "CONTRACT_LOCAL_ROOT_MISSING"
    try:
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
        contract, contract_error = validate_final_contract(payload, visible_case_set_path)
        if contract_error:
            return None, None, None, None, None, contract_error
        assert contract is not None
        if file_sha256(contract_path) != args.expected_final_contract_sha256:
            return None, None, None, None, None, "EXPECTED_FINAL_CONTRACT_SHA256_MISMATCH"
        reference_hashes, reference_error = verify_contract_local_references(contract, contract_root)
        if reference_error:
            return None, None, None, None, None, reference_error
        assert reference_hashes is not None
        rows = load_jsonl(visible_case_set_path)
        observations = load_source_observation_schema(contract_root, contract["paired_execution_contract"])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return None, None, None, None, None, "BUILDER_INPUT_INVALID"
    case_problems, case_ids = visible_case_set_errors(rows, contract["research_contract_id"])
    if case_problems:
        return None, None, None, None, None, case_problems[0]
    formal_case_ids = formal_case_ids_from_rows(rows, contract["research_contract_id"])
    if formal_case_ids is None or case_ids != formal_case_ids:
        return None, None, None, None, None, "FORMAL_CASE_IDS_INVALID"
    receipt, receipt_error = authorization_receipt_error(
        args.package_generation_authorization_receipt.resolve(),
        args.expected_package_generation_authorization_receipt_sha256,
        file_sha256(contract_path), contract["calibration_case_set_reference_and_hash"]["sha256"], file_sha256(visible_case_set_path),
        expected_output_scope,
    )
    if receipt_error:
        return None, None, None, None, None, receipt_error
    if set(reference_hashes.values()).intersection({
        file_sha256(contract_path), args.expected_package_generation_authorization_receipt_sha256,
    }):
        return None, None, None, None, None, "TASK_VISIBLE_ARTIFACT_HASH_COLLISION"
    cases = [row for row in rows if row.get("record_type") == "visible_calibration_case"]
    visible_by_case: dict[str, dict[str, Any]] = {}
    for case in cases:
        visible = visible_input_from_case(case)
        if visible is None:
            return None, None, None, None, None, "VISIBLE_CASE_PROJECTION_INVALID"
        visible_by_case[visible["case_id"]] = visible
    if len(visible_by_case) != 40 or list(visible_by_case) != formal_case_ids:
        return None, None, None, None, None, "VISIBLE_CASE_PROJECTION_INVALID"
    return contract, rows, observations, reference_hashes, receipt, None


def build_package(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists():
        return fail("OUTPUT_EXISTS", str(output))
    contract, rows, observations, reference_hashes, receipt, input_error = validated_inputs(args, output)
    if input_error:
        return fail(input_error, str(args.contract))
    assert contract is not None and rows is not None and observations is not None and reference_hashes is not None and receipt is not None
    contract_path, visible_case_set_path, contract_root = args.contract.resolve(), args.visible_case_set.resolve(), args.contract_local_root.resolve()
    formal_case_ids = formal_case_ids_from_rows(rows, contract["research_contract_id"])
    assert formal_case_ids is not None
    visible_by_case = {case["case_id"]: visible_input_from_case(case) for case in rows if case.get("record_type") == "visible_calibration_case"}

    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.tmp-", dir=output.parent))
    try:
        pairs = []
        task_count = 0
        for case_id in formal_case_ids:
            visible = visible_by_case[case_id]
            assert visible is not None
            arm_paths: dict[str, str] = {}
            for arm in ARMS:
                relative = Path(arm) / f"{case_id}.task.json"
                target = staging / relative
                try:
                    target.resolve().relative_to((staging / arm).resolve())
                except ValueError:
                    return fail("TASK_PATH_ESCAPE", relative.as_posix())
                target.parent.mkdir(parents=True, exist_ok=True)
                task = task_for(contract, visible, arm, observations)
                target.write_bytes(canonical_json_bytes(task))
                task_count += 1
                if args.test_fail_after_task_count is not None and task_count >= args.test_fail_after_task_count:
                    raise OSError("deterministic requested mid-build failure")
                arm_paths[arm] = {
                    "path": relative.as_posix(),
                    "task_file_sha256": file_sha256(target),
                }
            pairs.append(
                {
                    "case_id": case_id,
                    "visible_input_sha256": canonical_json_sha256(visible),
                    "task_files": arm_paths,
                }
            )
        manifest = {
            "schema_version": "1.0",
            "content_first_paired_task_manifest": {
                "research_contract_id": contract["research_contract_id"],
                "contract_version": contract["contract_version"],
                "final_contract_sha256": file_sha256(contract_path),
                "formal_case_set_sha256": contract["calibration_case_set_reference_and_hash"]["sha256"],
                "visible_case_set_sha256": file_sha256(visible_case_set_path),
                "pair_count": 40,
                "task_count": 80,
                "execution_authorized": False,
                "package_generation_authorization_receipt_sha256": args.expected_package_generation_authorization_receipt_sha256,
                "package_generation_authorization_id": receipt["authorization_id"],
                "paired_execution_contract": contract["paired_execution_contract"],
                "paired_execution_contract_sha256": canonical_json_sha256(contract["paired_execution_contract"]),
                "contract_local_reference_hashes": reference_hashes,
                "pairs": pairs,
            },
        }
        manifest_path = staging / "paired-task-manifest.json"
        manifest_path.write_bytes(canonical_json_bytes(manifest))
        entries = [entry for pair in pairs for entry in pair["task_files"].values()]
        if len(entries) != 80 or len({entry["path"] for entry in entries}) != 80:
            return fail("TASK_MANIFEST_INVALID", "80 unique task paths required")
        for pair in pairs:
            for arm, entry in pair["task_files"].items():
                task_path = safe_relative_path(staging, entry["path"])
                if (
                    task_path is None
                    or not task_path.is_file()
                    or file_sha256(task_path) != entry["task_file_sha256"]
                ):
                    return fail("TASK_MANIFEST_HASH_MISMATCH", entry["path"])
                task_errors = exact_task_errors(
                    json.loads(task_path.read_text(encoding="utf-8")),
                    contract,
                    visible_by_case[pair["case_id"]],
                    arm,
                    observations,
                )
                if task_errors:
                    return fail(task_errors[0], entry["path"])
        if file_sha256(contract_path) != args.expected_final_contract_sha256 or file_sha256(visible_case_set_path) != contract["visible_case_set_reference_and_hash"]["sha256"]:
            return fail("SOURCE_INPUT_DRIFT", "contract or visible case set changed during build")
        reread_hashes, reference_error = verify_contract_local_references(contract, contract_root)
        if reference_error or reread_hashes != reference_hashes:
            return fail("SOURCE_INPUT_DRIFT", reference_error or "contract-local frozen reference changed during build")
        if output.exists():
            return fail("OUTPUT_EXISTS", str(output))
        staging.replace(output)
    except OSError as exc:
        return fail("TASK_BUILD_FAILED", str(exc))
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    manifest_hash = file_sha256(output / "paired-task-manifest.json")
    print(json.dumps({"status": "PASS", "output": str(output), "pair_count": 40, "task_count": 80, "manifest_file_sha256": manifest_hash, "model_execution_authorized": False}, ensure_ascii=False))
    return 0


def verify_package(args: argparse.Namespace) -> int:
    package = args.verify_package.resolve()
    if not package.is_dir():
        return fail("PACKAGE_MISSING", str(package))
    contract, rows, observations, reference_hashes, receipt, input_error = validated_inputs(args, package)
    if input_error:
        return fail(input_error, str(args.contract))
    assert contract is not None and rows is not None and observations is not None and reference_hashes is not None and receipt is not None
    manifest_path = package / "paired-task-manifest.json"
    if not SHA256.fullmatch(args.expected_manifest_file_sha256) or not manifest_path.is_file() or file_sha256(manifest_path) != args.expected_manifest_file_sha256:
        return fail("MANIFEST_FILE_SHA256_MISMATCH", str(manifest_path))
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fail("MANIFEST_INVALID", str(manifest_path))
    required = {"research_contract_id", "contract_version", "final_contract_sha256", "formal_case_set_sha256", "visible_case_set_sha256", "pair_count", "task_count", "execution_authorized", "package_generation_authorization_receipt_sha256", "package_generation_authorization_id", "paired_execution_contract", "paired_execution_contract_sha256", "contract_local_reference_hashes", "pairs"}
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "content_first_paired_task_manifest"} or manifest.get("schema_version") != "1.0":
        return fail("MANIFEST_INVALID", "top-level")
    body = manifest["content_first_paired_task_manifest"]
    if not isinstance(body, dict) or set(body) != required or body.get("research_contract_id") != contract["research_contract_id"] or body.get("contract_version") != contract["contract_version"] or body.get("final_contract_sha256") != file_sha256(args.contract.resolve()) or body.get("formal_case_set_sha256") != contract["calibration_case_set_reference_and_hash"]["sha256"] or body.get("visible_case_set_sha256") != file_sha256(args.visible_case_set.resolve()) or body.get("pair_count") != 40 or body.get("task_count") != 80 or body.get("execution_authorized") is not False or body.get("package_generation_authorization_receipt_sha256") != args.expected_package_generation_authorization_receipt_sha256 or body.get("package_generation_authorization_id") != receipt["authorization_id"] or body.get("paired_execution_contract") != contract["paired_execution_contract"] or body.get("paired_execution_contract_sha256") != canonical_json_sha256(contract["paired_execution_contract"]) or body.get("contract_local_reference_hashes") != reference_hashes:
        return fail("MANIFEST_INVALID", "contract binding")
    formal_case_ids = formal_case_ids_from_rows(rows, contract["research_contract_id"])
    pairs = body.get("pairs")
    if formal_case_ids is None or not isinstance(pairs, list) or len(pairs) != 40:
        return fail("MANIFEST_INVALID", "pairs")
    visible_by_case = {case["case_id"]: visible_input_from_case(case) for case in rows if case.get("record_type") == "visible_calibration_case"}
    paths: set[str] = set()
    for expected_case_id, pair in zip(formal_case_ids, pairs):
        if not isinstance(pair, dict) or set(pair) != {"case_id", "visible_input_sha256", "task_files"} or pair.get("case_id") != expected_case_id:
            return fail("MANIFEST_INVALID", "pair schema")
        visible = visible_by_case.get(expected_case_id)
        if visible is None or pair.get("visible_input_sha256") != canonical_json_sha256(visible) or not isinstance(pair.get("task_files"), dict) or set(pair["task_files"]) != set(ARMS):
            return fail("MANIFEST_INVALID", "pair binding")
        for arm in ARMS:
            entry = pair["task_files"][arm]
            if not isinstance(entry, dict) or set(entry) != {"path", "task_file_sha256"} or not SHA256.fullmatch(str(entry.get("task_file_sha256", ""))):
                return fail("MANIFEST_INVALID", "task entry")
            path = safe_relative_path(package, entry["path"])
            if path is None or path.suffix != ".json" or path.parent != (package / arm).resolve() or path.name != f"{expected_case_id}.task.json" or not path.is_file() or entry["path"] in paths:
                return fail("MANIFEST_INVALID", "task path")
            paths.add(entry["path"])
            if file_sha256(path) != entry["task_file_sha256"]:
                return fail("TASK_FILE_SHA256_MISMATCH", entry["path"])
            try:
                task = json.loads(path.read_text(encoding="utf-8"))
            except ValueError:
                return fail("TASK_SCHEMA_INVALID", entry["path"])
            errors = exact_task_errors(task, contract, visible, arm, observations)
            if errors:
                return fail(errors[0], entry["path"])
    allowed_paths = paths | {"paired-task-manifest.json", *ARMS}
    actual_paths = {path.relative_to(package).as_posix() for path in package.rglob("*")}
    if len(paths) != 80 or {p.relative_to(package).as_posix() for p in package.rglob("*.task.json")} != paths or actual_paths != allowed_paths:
        return fail("MANIFEST_INVALID", "task inventory")
    print(json.dumps({"status": "PASS", "package": str(package), "manifest_file_sha256": file_sha256(manifest_path), "model_execution_authorized": False}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify paired, truth-blind content-first calibration tasks.")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--visible-case-set", required=True, type=Path)
    parser.add_argument("--contract-local-root", required=True, type=Path)
    parser.add_argument("--expected-final-contract-sha256", required=True)
    parser.add_argument("--package-generation-authorization-receipt", required=True, type=Path)
    parser.add_argument("--expected-package-generation-authorization-receipt-sha256", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-package", type=Path)
    parser.add_argument("--expected-manifest-file-sha256")
    parser.add_argument("--test-fail-after-task-count", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if (args.output is None) == (args.verify_package is None):
        return fail("MODE_INVALID", "choose exactly one of --output or --verify-package")
    if args.verify_package is not None:
        if args.expected_manifest_file_sha256 is None:
            return fail("EXPECTED_MANIFEST_FILE_SHA256_REQUIRED", "verification requires a trusted manifest file sha256")
        return verify_package(args)
    return build_package(args)


if __name__ == "__main__":
    raise SystemExit(main())
