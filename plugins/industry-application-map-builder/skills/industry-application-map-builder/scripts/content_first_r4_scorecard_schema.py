from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any


R4_MARKER = "2.0-r4"
PLATFORM_AUDIT_STATES = {"PASS", "FAIL", "UNVERIFIED", "NOT_COLLECTED"}
R4_SCORE_ITEMS = {
    "taxonomy_and_scope_grounding": ("taxonomy_truth_reviewer", True),
    "semantic_decision_correctness": ("semantic_truth_reviewer", True),
    "source_retrieval_equivalence": ("source_equivalence_reviewer", True),
    "receiver_evidence_integrity": ("receiver_evidence_reviewer", True),
    "safety_boundary": ("safety_boundary_reviewer", True),
    "unknown_and_challenge_handling": ("challenge_and_unknown_reviewer", False),
}
R4_EQUIVALENCE_DIMENSIONS = {
    "taxonomy_membership": "taxonomy_membership_basis",
    "output_or_use_point": "output_or_subprocess_basis",
    "mechanism": "mechanism_basis",
    "conditions": "conditions",
    "boundary": "truth_boundary",
}
EQUIVALENCE_RESULTS = {"PASS", "FAIL", "UNVERIFIED"}
R4_SCORECARD_FIELDS = {
    "scorecard_id",
    "raw_answer_reference",
    "raw_answer_sha256",
    "subject",
    "method_arm",
    "visible_input_sha256",
    "source_truth_comparison_reference",
    "source_truth_comparison_sha256",
    "scoring_rubric_version",
    "scoring_items",
    "equivalent_source_dimensions",
    "equivalent_source_result",
    "unknown_items",
    "content_score_result",
    "platform_audit_state",
    "platform_audit_reference_or_null",
    "scorecard_sha256",
}
TRUTH_FIELDS = {
    "truth_id",
    "research_contract_id",
    "contract_version",
    "case_id",
    "taxonomy_membership_basis",
    "output_or_subprocess_basis",
    "mechanism_basis",
    "expected_semantic_axes",
    "conditions",
    "limitations",
    "unknowns",
    "truth_boundary",
    "counts_toward_known_positive_recall",
    "truth_sha256",
}


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_text_list(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty(item) for item in value)


def _has_symlink_component(workspace: Path, reference: str) -> bool:
    current = workspace
    for part in PurePosixPath(reference).parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def canonical_reference_target(
    workspace: Path, reference: Any
) -> tuple[Path, str | None] | None:
    if not nonempty(reference) or "\\" in reference:
        return None
    base, separator, fragment = reference.partition("#")
    if "#" in fragment or (separator and not fragment.startswith("/")):
        return None
    candidate = PurePosixPath(base)
    if (
        candidate.is_absolute()
        or not base
        or "//" in base
        or candidate.as_posix() != base
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or _has_symlink_component(workspace, base)
    ):
        return None
    path = workspace.joinpath(*candidate.parts)
    if not path.is_file():
        return None
    try:
        if path.resolve().relative_to(workspace.resolve()).as_posix() != base:
            return None
    except (OSError, ValueError):
        return None
    if not separator:
        return path.resolve(), None
    try:
        current: Any = json.loads(path.read_text(encoding="utf-8"))
        for raw_token in fragment[1:].split("/"):
            if re.search(r"~(?![01])", raw_token):
                return None
            token = raw_token.replace("~1", "/").replace("~0", "~")
            if isinstance(current, dict) and token in current:
                current = current[token]
            elif (
                isinstance(current, list)
                and token.isdigit()
                and (token == "0" or not token.startswith("0"))
                and int(token) < len(current)
            ):
                current = current[int(token)]
            else:
                return None
    except (OSError, ValueError):
        return None
    return path.resolve(), fragment


def _identity(path: Path) -> tuple[int, int] | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    return stat.st_dev, stat.st_ino


def _score_result(items: dict[str, Any]) -> str:
    if any(
        items[name]["critical"] and items[name]["score"] == 0
        for name in R4_SCORE_ITEMS
    ):
        return "FAIL"
    if all(items[name]["score"] == 2 for name in R4_SCORE_ITEMS):
        return "PASS"
    return "UNVERIFIED"


def _equivalence_result(dimensions: dict[str, Any]) -> str:
    results = [dimensions[name]["result"] for name in R4_EQUIVALENCE_DIMENSIONS]
    if any(result == "FAIL" for result in results):
        return "FAIL"
    if all(result == "PASS" for result in results):
        return "PASS"
    return "UNVERIFIED"


def validate_r4_scorecard(
    *,
    workspace: Path,
    scorecard_path: Path,
    payload: Any,
    envelope_path: Path,
    envelope: dict[str, Any],
    truth_path: Path,
    receipt_states: dict[str, str],
    snapshot_references: set[str],
    expected_contract_id: str,
    expected_contract_version: str,
    expected_file_sha256: str | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []

    def issue(code: str, detail: str | None = None) -> None:
        issues.append({"code": code, "detail": detail or str(scorecard_path)})

    body = payload.get("semantic_content_scorecard") if isinstance(payload, dict) else None
    if (
        not isinstance(payload, dict)
        or set(payload) != {"schema_version", "semantic_content_scorecard"}
        or payload.get("schema_version") != "1.0"
        or not isinstance(body, dict)
        or set(body) != R4_SCORECARD_FIELDS
    ):
        issue("SCORECARD_FIELDS_INVALID")
        return {"issues": issues, "dispositions": {}, "content_score_result": None}
    if expected_file_sha256 is not None and file_sha256(scorecard_path) != expected_file_sha256:
        issue("SCORECARD_FILE_HASH_MISMATCH")
    envelope_reference = envelope_path.relative_to(workspace).as_posix()
    truth_reference = truth_path.relative_to(workspace).as_posix()
    if not (
        nonempty(body.get("scorecard_id"))
        and body.get("raw_answer_reference") == envelope_reference
        and body.get("raw_answer_sha256") == file_sha256(envelope_path)
        and body.get("subject") == envelope.get("subject")
        and body.get("method_arm") == envelope.get("method_arm")
        and body.get("visible_input_sha256") == envelope.get("visible_input_sha256")
        and body.get("source_truth_comparison_reference") == truth_reference
        and body.get("source_truth_comparison_reference")
        == envelope.get("source_truth_comparison_reference")
        and body.get("source_truth_comparison_sha256") == file_sha256(truth_path)
        and body.get("source_truth_comparison_sha256")
        == envelope.get("source_truth_comparison_sha256")
        and body.get("scoring_rubric_version") == R4_MARKER
    ):
        issue("SCORECARD_BINDING_INVALID")
    if _identity(scorecard_path) == _identity(truth_path):
        issue("TRUTH_SCORECARD_ARTIFACT_COLLISION")
    try:
        truth_payload = json.loads(truth_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        truth_payload = None
    truth = (
        truth_payload.get("semantic_content_case_truth")
        if isinstance(truth_payload, dict)
        else None
    )
    if (
        not isinstance(truth_payload, dict)
        or set(truth_payload) != {"schema_version", "semantic_content_case_truth"}
        or truth_payload.get("schema_version") != "1.0"
        or not isinstance(truth, dict)
        or set(truth) != TRUTH_FIELDS
        or not nonempty(truth.get("truth_id"))
        or truth.get("research_contract_id") != expected_contract_id
        or truth.get("contract_version") != expected_contract_version
        or truth.get("case_id") != envelope.get("subject", {}).get("id")
        or type(truth.get("counts_toward_known_positive_recall")) is not bool
        or truth.get("truth_sha256")
        != canonical_sha256({**truth, "truth_sha256": None})
    ):
        issue("CONTENT_CASE_TRUTH_BINDING_INVALID")

    items = body.get("scoring_items")
    items_valid = isinstance(items, dict) and set(items) == set(R4_SCORE_ITEMS)
    evidence_seen: set[tuple[int, int, str | None]] = set()
    if items_valid:
        current_truth = envelope.get("source_truth_comparison_reference")
        truth_prefix = f"{current_truth}#/semantic_content_case_truth/"
        current_receipts = set(receipt_states)
        evidence_by_role = {
            "taxonomy_and_scope_grounding": {truth_prefix + "taxonomy_membership_basis"},
            "semantic_decision_correctness": {
                truth_prefix + "expected_semantic_axes",
                truth_prefix + "output_or_subprocess_basis",
                truth_prefix + "mechanism_basis",
                truth_prefix + "conditions",
            },
            "source_retrieval_equivalence": {
                envelope_reference + "#/semantic_content_raw_answer/source_observations",
                *{
                    envelope_reference
                    + f"#/semantic_content_raw_answer/source_observations/{index}"
                    for index in range(len(envelope.get("source_observations") or []))
                },
                *current_receipts,
                *snapshot_references,
            },
            "receiver_evidence_integrity": {*current_receipts, *snapshot_references},
            "safety_boundary": {
                envelope.get("raw_response_reference"),
                envelope_reference + "#/semantic_content_raw_answer/unknown_items",
                truth_prefix + "truth_boundary",
                truth_prefix + "limitations",
            },
            "unknown_and_challenge_handling": {
                envelope.get("raw_response_reference"),
                envelope_reference + "#/semantic_content_raw_answer/unknown_items",
                truth_prefix + "unknowns",
                truth_prefix + "limitations",
            },
        }
        for name, (responsibility, critical) in R4_SCORE_ITEMS.items():
            item = items.get(name)
            references = item.get("evidence_references") if isinstance(item, dict) else None
            targets = (
                [canonical_reference_target(workspace, reference) for reference in references]
                if isinstance(references, list)
                else []
            )
            if not (
                isinstance(item, dict)
                and set(item)
                == {"responsibility", "critical", "score", "reason", "evidence_references"}
                and item.get("responsibility") == responsibility
                and item.get("critical") is critical
                and type(item.get("score")) is int
                and item.get("score") in {0, 1, 2}
                and nonempty(item.get("reason"))
                and valid_text_list(references)
                and bool(references)
                and len(set(references)) == len(references)
                and all(target is not None for target in targets)
            ):
                items_valid = False
                continue
            if any(reference not in evidence_by_role[name] for reference in references):
                issue("SCORECARD_EVIDENCE_ROLE_INVALID", f"{scorecard_path}: {name}")
                items_valid = False
            score_identity = _identity(scorecard_path)
            for target in targets:
                assert target is not None
                identity = _identity(target[0])
                if identity is None:
                    items_valid = False
                    continue
                if identity == score_identity:
                    issue("SCORECARD_EVIDENCE_SELF_REFERENCE")
                    items_valid = False
                    continue
                key = (identity[0], identity[1], target[1])
                if key in evidence_seen:
                    issue("SCORECARD_EVIDENCE_REFERENCE_REUSED")
                    items_valid = False
                evidence_seen.add(key)
    if not items_valid:
        issue("SCORECARD_ITEMS_INVALID")

    dimensions = body.get("equivalent_source_dimensions")
    dimensions_valid = isinstance(dimensions, dict) and set(dimensions) == set(
        R4_EQUIVALENCE_DIMENSIONS
    )
    if dimensions_valid:
        truth_reference = envelope.get("source_truth_comparison_reference")
        for name, truth_field in R4_EQUIVALENCE_DIMENSIONS.items():
            dimension = dimensions.get(name)
            truth_refs = (
                dimension.get("truth_evidence_references")
                if isinstance(dimension, dict)
                else None
            )
            receiver_refs = (
                dimension.get("receiver_evidence_references")
                if isinstance(dimension, dict)
                else None
            )
            expected_truth = (
                f"{truth_reference}#/semantic_content_case_truth/{truth_field}"
            )
            if not (
                isinstance(dimension, dict)
                and set(dimension)
                == {
                    "result",
                    "reason",
                    "truth_evidence_references",
                    "receiver_evidence_references",
                }
                and dimension.get("result") in EQUIVALENCE_RESULTS
                and nonempty(dimension.get("reason"))
                and truth_refs == [expected_truth]
                and canonical_reference_target(workspace, expected_truth) is not None
                and valid_text_list(receiver_refs)
                and bool(receiver_refs)
                and len(set(receiver_refs)) == len(receiver_refs)
                and all(reference in receipt_states for reference in receiver_refs)
                and all(
                    canonical_reference_target(workspace, reference) is not None
                    for reference in receiver_refs
                )
                and (
                    dimension.get("result") != "PASS"
                    or all(receipt_states[reference] == "captured" for reference in receiver_refs)
                )
            ):
                dimensions_valid = False
    if not dimensions_valid:
        issue("EQUIVALENT_SOURCE_DIMENSIONS_INVALID")
        expected_equivalent = None
    else:
        expected_equivalent = _equivalence_result(dimensions)
        if body.get("equivalent_source_result") != expected_equivalent:
            issue("EQUIVALENT_SOURCE_RESULT_INVALID")
        expected_source_score = {"PASS": 2, "UNVERIFIED": 1, "FAIL": 0}[
            expected_equivalent
        ]
        if items_valid and items["source_retrieval_equivalence"]["score"] != expected_source_score:
            issue("EQUIVALENT_SOURCE_SCORE_INCONSISTENT")

    if not isinstance(body.get("unknown_items"), list):
        issue("SCORECARD_UNKNOWNS_MISSING")
    if body.get("platform_audit_state") not in PLATFORM_AUDIT_STATES or (
        body.get("platform_audit_state") == "NOT_COLLECTED"
        and body.get("platform_audit_reference_or_null") is not None
    ):
        issue("SCORECARD_PLATFORM_AUDIT_INVALID")
    elif body.get("platform_audit_state") != "NOT_COLLECTED" and canonical_reference_target(
        workspace, body.get("platform_audit_reference_or_null")
    ) is None:
        issue("SCORECARD_PLATFORM_AUDIT_INVALID")

    dispositions: dict[str, str] = {}
    expected_result = None
    if items_valid:
        expected_result = _score_result(items)
        dispositions = {
            name: {0: "FAIL", 1: "UNVERIFIED", 2: "PASS"}[items[name]["score"]]
            for name, (_, critical) in R4_SCORE_ITEMS.items()
            if critical
        }
        if body.get("content_score_result") != expected_result:
            issue("SCORECARD_RESULT_INVALID")
    if body.get("scorecard_sha256") != canonical_sha256(
        {**body, "scorecard_sha256": None}
    ):
        issue("SCORECARD_HASH_MISMATCH")
    return {
        "issues": issues,
        "dispositions": dispositions,
        "content_score_result": expected_result,
    }
