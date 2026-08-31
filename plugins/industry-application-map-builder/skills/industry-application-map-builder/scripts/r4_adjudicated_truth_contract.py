from __future__ import annotations

import hashlib
import json
import re
from typing import Any


MAP_BUILDER_PLUGIN_VERSION = "0.4.0-beta.6"
DIRECTOR_PLUGIN_VERSION = "0.4.0-beta.1"
BETA5_CASE_PACKAGE_CONTRACT_VERSION = "1.0-beta5"
BETA5_TRUTH_CONTRACT_VERSION = "2.1-r4-adjudicated"
BETA5_TRUTH_SCORECARD_CONTRACT_VERSION = "2.1-r4"

SELECTION_ORIGIN_COUNTS = {
    "retained_r3_unexecuted": 30,
    "new_unseen": 10,
}
SAMPLING_CATEGORY_COUNTS = {
    "direct_evidence_candidate": 8,
    "terminology_mismatch_candidate": 6,
    "misleading_name_control": 6,
    "source_scarce": 5,
    "incomplete_conditions": 5,
    "source_independence_risk": 4,
    "vacuous_hypothesis_control": 3,
    "contamination_or_structure_control": 3,
}
MINIMUM_NEW_UNSEEN_ACCEPTED_POSITIVES = 10

TRUTH_DISPOSITIONS = {
    "positive_confirmed",
    "positive_bounded",
    "negative_confirmed",
    "unresolved",
}
EVIDENCE_STATES = {"supported", "hypothesis", "unknown", "conflicted"}
EVIDENCE_QUALITIES = {
    "direct_complete",
    "direct_bounded",
    "insufficient",
    "inaccessible",
    "incomplete_conditions",
    "conflicting",
}
ADJUDICATION_STATES = {
    "draft",
    "pending_independent_review",
    "accepted",
    "reopened",
    "superseded",
}

TRUTH_ROW_FIELDS = {
    "record_type",
    "truth_contract_version",
    "research_contract_id",
    "preparation_contract_version",
    "locked_input_sha256",
    "case_id",
    "truth_disposition",
    "evidence_state",
    "evidence_quality",
    "adjudication_state",
    "adjudication_version",
    "counterevidence",
    "reopen_reason",
    "supersedes_truth_sha256",
    "evidence_bases",
    "conditions",
    "limitations",
    "unknowns",
    "exclusion_boundary",
    "truth_sha256",
}
FORBIDDEN_CASE_TRUTH_FIELDS = {
    "known_positive",
    "truth_label",
    "truth_disposition",
    "evidence_state",
    "evidence_quality",
    "adjudication_state",
    "expected_screening_result",
    "counts_toward_known_positive_recall",
}

_ALLOWED_TRUTH_EVIDENCE_COMBINATIONS = {
    ("positive_confirmed", "supported", "direct_complete"),
    ("positive_bounded", "supported", "direct_bounded"),
    ("negative_confirmed", "supported", "direct_complete"),
    ("negative_confirmed", "supported", "direct_bounded"),
    ("unresolved", "supported", "incomplete_conditions"),
    ("unresolved", "hypothesis", "insufficient"),
    ("unresolved", "hypothesis", "incomplete_conditions"),
    ("unresolved", "unknown", "insufficient"),
    ("unresolved", "unknown", "inaccessible"),
    ("unresolved", "unknown", "incomplete_conditions"),
    ("unresolved", "conflicted", "conflicting"),
}


def _unique(errors: list[str]) -> list[str]:
    return list(dict.fromkeys(errors))


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_nonempty(item) for item in value)


def _sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def validate_beta5_case_rows(case_rows: list[dict]) -> list[str]:
    errors: list[str] = []
    origin_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    case_ids: list[str] = []
    for row in case_rows:
        if not isinstance(row, dict) or row.get("record_type") != "calibration_case":
            errors.append("CASE_SCHEMA_INVALID")
            continue
        if FORBIDDEN_CASE_TRUTH_FIELDS.intersection(row):
            errors.append("CASE_TRUTH_FIELD_FORBIDDEN")
        if "primary_category" in row:
            errors.append("LEGACY_TRUTH_BEARING_CATEGORY_FORBIDDEN")
        case_id = row.get("case_id")
        if not _nonempty(case_id):
            errors.append("CASE_ID_INVALID")
        else:
            case_ids.append(case_id)
        category = row.get("sampling_category")
        if category not in SAMPLING_CATEGORY_COUNTS:
            errors.append("SAMPLING_CATEGORY_INVALID")
        else:
            category_counts[category] = category_counts.get(category, 0) + 1
        provenance = row.get("provenance")
        origin = provenance.get("selection_origin") if isinstance(provenance, dict) else None
        if (
            isinstance(provenance, dict)
            and provenance.get("development_regression_only") is True
        ):
            errors.append("DEVELOPMENT_CASE_IN_FORMAL_SET")
        if (
            not isinstance(provenance, dict)
            or provenance.get("development_regression_only") is not False
            or origin not in SELECTION_ORIGIN_COUNTS
        ):
            errors.append("CASE_PROVENANCE_INVALID")
        else:
            origin_counts[origin] = origin_counts.get(origin, 0) + 1
    if len(case_rows) != 40 or len(case_ids) != 40 or len(set(case_ids)) != 40:
        errors.append("FORTY_UNIQUE_CASES_REQUIRED")
    if origin_counts != SELECTION_ORIGIN_COUNTS:
        errors.append("SELECTION_ORIGIN_COUNTS_INVALID")
    if category_counts != SAMPLING_CATEGORY_COUNTS:
        errors.append("SAMPLING_CATEGORY_COUNTS_INVALID")
    return _unique(errors)


def validate_adjudicated_truth_rows(
    truth_rows: list[dict],
    *,
    expected_case_ids: list[str],
    expected_contract_id: str,
    expected_preparation_contract_version: str,
    expected_locked_input_sha256: str,
    require_accepted: bool = True,
) -> list[str]:
    errors: list[str] = []
    seen_case_ids: set[str] = set()
    for row in truth_rows:
        if not isinstance(row, dict) or set(row) != TRUTH_ROW_FIELDS:
            errors.append("SOURCE_TRUTH_SCHEMA_INVALID")
            continue
        case_id = row.get("case_id")
        if not _nonempty(case_id) or case_id in seen_case_ids:
            errors.append("SOURCE_TRUTH_CASE_ID_INVALID")
        elif isinstance(case_id, str):
            seen_case_ids.add(case_id)
        if (
            row.get("record_type") != "source_truth"
            or row.get("truth_contract_version") != BETA5_TRUTH_CONTRACT_VERSION
            or row.get("research_contract_id") != expected_contract_id
            or row.get("preparation_contract_version")
            != expected_preparation_contract_version
            or row.get("locked_input_sha256") != expected_locked_input_sha256
            or not _nonempty(row.get("adjudication_version"))
            or not _string_list(row.get("counterevidence"))
            or not isinstance(row.get("evidence_bases"), dict)
            or not _string_list(row.get("conditions"))
            or not _string_list(row.get("limitations"))
            or not _string_list(row.get("unknowns"))
            or not _nonempty(row.get("exclusion_boundary"))
        ):
            errors.append("SOURCE_TRUTH_SCHEMA_INVALID")
        combination = (
            row.get("truth_disposition"),
            row.get("evidence_state"),
            row.get("evidence_quality"),
        )
        if combination not in _ALLOWED_TRUTH_EVIDENCE_COMBINATIONS:
            errors.append("TRUTH_EVIDENCE_COMBINATION_INVALID")
        adjudication_state = row.get("adjudication_state")
        if adjudication_state not in ADJUDICATION_STATES:
            errors.append("ADJUDICATION_STATE_INVALID")
        if require_accepted and adjudication_state != "accepted":
            errors.append("CURRENT_TRUTH_ROW_NOT_ACCEPTED")
        reopen_reason = row.get("reopen_reason")
        if (adjudication_state == "reopened") != _nonempty(reopen_reason):
            errors.append("REOPEN_REASON_STATE_MISMATCH")
        supersedes = row.get("supersedes_truth_sha256")
        if supersedes is not None and not _is_sha256(supersedes):
            errors.append("SUPERSEDES_TRUTH_HASH_INVALID")
    if seen_case_ids != set(expected_case_ids) or len(truth_rows) != len(expected_case_ids):
        errors.append("SOURCE_TRUTH_CASE_COVERAGE_INVALID")
    return _unique(errors)


def derive_truth_summary(truth_rows: list[dict]) -> dict[str, Any]:
    accepted_positive_ids = sorted(
        row["case_id"]
        for row in truth_rows
        if row.get("adjudication_state") == "accepted"
        and row.get("truth_disposition")
        in {"positive_confirmed", "positive_bounded"}
        and row.get("evidence_state") == "supported"
        and row.get("evidence_quality") in {"direct_complete", "direct_bounded"}
    )
    accepted_negative_ids = sorted(
        row["case_id"]
        for row in truth_rows
        if row.get("adjudication_state") == "accepted"
        and row.get("truth_disposition") == "negative_confirmed"
        and row.get("evidence_state") == "supported"
        and row.get("evidence_quality") in {"direct_complete", "direct_bounded"}
    )
    unresolved_ids = sorted(
        row["case_id"]
        for row in truth_rows
        if row.get("adjudication_state") == "accepted"
        and row.get("truth_disposition") == "unresolved"
    )
    return {
        "accepted_positive_case_ids": accepted_positive_ids,
        "accepted_positive_case_ids_sha256": _sha256(accepted_positive_ids),
        "accepted_positive_count": len(accepted_positive_ids),
        "accepted_negative_case_ids": accepted_negative_ids,
        "accepted_negative_case_ids_sha256": _sha256(accepted_negative_ids),
        "accepted_negative_count": len(accepted_negative_ids),
        "unresolved_case_ids": unresolved_ids,
        "unresolved_case_ids_sha256": _sha256(unresolved_ids),
        "unresolved_count": len(unresolved_ids),
    }


def validate_truth_summary_integrity(
    summary: Any, *, expected_case_ids: list[str] | None = None
) -> list[str]:
    errors: list[str] = []
    fields = (
        ("accepted_positive_case_ids", "accepted_positive_case_ids_sha256", "accepted_positive_count"),
        ("accepted_negative_case_ids", "accepted_negative_case_ids_sha256", "accepted_negative_count"),
        ("unresolved_case_ids", "unresolved_case_ids_sha256", "unresolved_count"),
    )
    expected_keys = {field for group in fields for field in group}
    if not isinstance(summary, dict) or set(summary) != expected_keys:
        return ["TRUTH_SUMMARY_SCHEMA_INVALID"]

    partitions: list[list[str]] = []
    for ids_field, hash_field, count_field in fields:
        case_ids = summary.get(ids_field)
        if (
            not isinstance(case_ids, list)
            or not all(_nonempty(case_id) for case_id in case_ids)
            or case_ids != sorted(case_ids)
            or len(case_ids) != len(set(case_ids))
            or summary.get(count_field) != len(case_ids)
        ):
            errors.append("TRUTH_SUMMARY_CASE_IDS_INVALID")
            continue
        partitions.append(case_ids)
        if summary.get(hash_field) != _sha256(case_ids):
            errors.append("TRUTH_SUMMARY_HASH_MISMATCH")

    if len(partitions) == len(fields):
        combined_ids = [case_id for partition in partitions for case_id in partition]
        if (
            len(combined_ids) != 40
            or len(combined_ids) != len(set(combined_ids))
            or (
                expected_case_ids is not None
                and (
                    len(expected_case_ids) != 40
                    or len(expected_case_ids) != len(set(expected_case_ids))
                    or set(combined_ids) != set(expected_case_ids)
                )
            )
        ):
            errors.append("TRUTH_SUMMARY_CASE_PARTITION_INVALID")
    if not summary.get("accepted_positive_case_ids"):
        errors.append("ACCEPTED_POSITIVE_DENOMINATOR_EMPTY")
    return _unique(errors)


def validate_positive_holdout_floor(
    case_rows: list[dict], truth_summary: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    positive_ids = truth_summary.get("accepted_positive_case_ids")
    if not isinstance(positive_ids, list) or not all(
        _nonempty(case_id) for case_id in positive_ids
    ):
        return ["ACCEPTED_POSITIVE_CASE_IDS_INVALID"]
    if not positive_ids:
        errors.append("ACCEPTED_POSITIVE_DENOMINATOR_EMPTY")
    new_unseen_ids = {
        row.get("case_id")
        for row in case_rows
        if isinstance(row.get("provenance"), dict)
        and row["provenance"].get("selection_origin") == "new_unseen"
    }
    if len(set(positive_ids).intersection(new_unseen_ids)) < MINIMUM_NEW_UNSEEN_ACCEPTED_POSITIVES:
        errors.append("MINIMUM_NEW_UNSEEN_ACCEPTED_POSITIVES_NOT_MET")
    return errors
