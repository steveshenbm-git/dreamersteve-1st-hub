#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
from pathlib import PurePosixPath

from content_source_observation_schema import (
    SNAPSHOT_RECEIPT_KEYS,
    contains_receiver_owned_field,
    valid_model_observation,
)
from content_first_r4_scorecard_schema import (
    R4_MARKER,
    R4_SCORECARD_FIELDS,
    TRUTH_FIELDS,
    validate_r4_scorecard,
)
from r4_adjudicated_truth_contract import (
    EVIDENCE_QUALITIES,
    EVIDENCE_STATES as ADJUDICATION_EVIDENCE_STATES,
    TRUTH_DISPOSITIONS,
)


LEGACY_ARMS = {
    "baseline_full_depth",
    "candidate_screen_then_expand",
}
LEGACY_RESEARCH_CONTRACT_VERSIONS = {"1.0.0-content.1"}
PLATFORM_AUDIT_STATES = {"PASS", "FAIL", "UNVERIFIED", "NOT_COLLECTED"}
LEGACY_SCORE_ITEMS = {
    "scope_taxonomy_grounding",
    "three_axis_handling",
    "source_truth_alignment",
    "safety_boundary",
    "unknown_disclosure",
}
LEGACY_SCORECARD_FIELDS = R4_SCORECARD_FIELDS - {
    "equivalent_source_dimensions",
    "equivalent_source_result",
}
SCREENING_RESULTS = {"hypothesis_formed", "ambiguous", "no_hypothesis_formed"}
SEMANTIC_WORK_STATES = {
    "not_screened",
    "screened",
    "evidence_expansion_required",
    "evidence_expanded",
    "audit_reopened",
}
EVIDENCE_STATES = {"supported", "hypothesis", "unknown", "conflicted"}
PRIVATE_INPUT_KEYS = {
    "company_id",
    "company_name",
    "company_product",
    "product_fact_id",
    "route_id",
    "customer_id",
}
OBSERVATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_inside(workspace: Path, reference: Any) -> Path | None:
    if not nonempty(reference):
        return None
    candidate = Path(reference)
    if not candidate.is_absolute():
        candidate = workspace / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(workspace.resolve())
    except ValueError:
        return None
    return resolved


def canonical_reference_target(
    workspace: Path, reference: Any
) -> tuple[Path, str | None] | None:
    """Resolve one canonical workspace-relative POSIX reference and optional JSON pointer."""
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
        or has_symlink_component(workspace, base)
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
        current: Any = load_json(path)
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
    except (OSError, json.JSONDecodeError):
        return None
    return path.resolve(), fragment


def artifact_identity(path: Path) -> tuple[int, int] | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    return stat.st_dev, stat.st_ino


def register_artifact_role(
    registry: dict[tuple[int, int], str],
    errors: list[dict[str, str]],
    path: Path,
    role: str,
) -> None:
    identity = artifact_identity(path)
    if identity is None:
        return
    prior_role = registry.get(identity)
    if prior_role is not None and prior_role != role:
        add(
            errors,
            "ARTIFACT_ROLE_INODE_COLLISION",
            f"{path}: {prior_role} vs {role}",
        )
    else:
        registry[identity] = role


def has_symlink_component(workspace: Path, reference: str) -> bool:
    candidate = workspace / Path(reference)
    try:
        relative = candidate.absolute().relative_to(workspace.absolute())
    except ValueError:
        return True
    current = workspace
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def contains_private_input(value: Any) -> bool:
    if isinstance(value, dict):
        return any(key in PRIVATE_INPUT_KEYS or contains_private_input(item) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_private_input(item) for item in value)
    return False


def timezone_aware_iso8601(value: Any) -> bool:
    if not nonempty(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def add(errors: list[dict[str, str]], code: str, detail: str) -> None:
    errors.append({"code": code, "detail": detail})


def score_result(items: dict[str, Any], names: set[str]) -> str:
    if any(items[name]["critical"] and items[name]["score"] == 0 for name in names):
        return "FAIL"
    if all(items[name]["score"] == 2 for name in names):
        return "PASS"
    return "UNVERIFIED"


def valid_text_list(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty(item) for item in value)


def valid_truth_source_reference(
    workspace: Path, truth_path: Path, value: Any
) -> tuple[str, str, int, int] | None:
    if not (
        isinstance(value, dict)
        and set(value) == {"reference", "sha256"}
        and nonempty(value.get("reference"))
        and is_sha256(value.get("sha256"))
    ):
        return None
    reference = value["reference"]
    candidate = Path(reference)
    required_root = Path("02-来源真值") / "truth-source-snapshots"
    if (
        candidate.is_absolute()
        or candidate.as_posix() != reference
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or not candidate.is_relative_to(required_root)
        or has_symlink_component(workspace, reference)
    ):
        return None
    source_path = resolve_inside(workspace, reference)
    if source_path is None or not source_path.is_file():
        return None
    try:
        source_stat = source_path.stat()
        truth_stat = truth_path.stat()
    except OSError:
        return None
    if (
        source_path == truth_path
        or (source_stat.st_dev, source_stat.st_ino)
        == (truth_stat.st_dev, truth_stat.st_ino)
        or sha256_file(source_path) != value["sha256"]
    ):
        return None
    return reference, value["sha256"], source_stat.st_dev, source_stat.st_ino


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate append-only RC2 content-first raw-answer and scorecard evidence."
    )
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    errors: list[dict[str, str]] = []
    unverified_source_observation_ids: list[str] = []
    unverified_scorecard_ids: list[str] = []
    seen_receipt_paths: set[Path] = set()
    seen_observation_ids: set[str] = set()
    seen_receipt_ids: set[str] = set()
    artifact_roles: dict[tuple[int, int], str] = {}
    if not workspace.is_dir():
        add(errors, "WORKSPACE_MISSING", str(workspace))
    contract: dict[str, Any] = {}
    contract_path = workspace / "00-合同" / "semantic-research-contract.json"
    if contract_path.is_file():
        try:
            payload = load_json(contract_path)
            contract = payload.get("semantic_research_contract", {}) if isinstance(payload, dict) else {}
        except (OSError, json.JSONDecodeError) as exc:
            add(errors, "CONTENT_CONTRACT_INVALID", str(exc))
    else:
        add(errors, "CONTENT_CONTRACT_MISSING", str(contract_path))
    policy = contract.get("content_first_policy", {}) if isinstance(contract, dict) else {}
    declared_baseline_arm = contract.get("baseline_method_contract")
    declared_candidate_arm = contract.get("candidate_method_contract")
    scorecard_contract_version = (
        policy.get("truth_scorecard_contract_version")
        if isinstance(policy, dict)
        else None
    )
    if scorecard_contract_version == "1.0-legacy" and (
        declared_baseline_arm is None and declared_candidate_arm is None
        and contract.get("contract_version") in LEGACY_RESEARCH_CONTRACT_VERSIONS
    ):
        allowed_arms = LEGACY_ARMS
        r4_scoring_required = False
    elif scorecard_contract_version == R4_MARKER and (
        declared_baseline_arm == "baseline_full_depth_v1"
        and declared_candidate_arm == "screen_then_expand_v2"
    ):
        allowed_arms = {"baseline_full_depth_v1", "screen_then_expand_v2"}
        r4_scoring_required = True
    else:
        allowed_arms = set()
        r4_scoring_required = scorecard_contract_version != "1.0-legacy"
        if scorecard_contract_version not in {"1.0-legacy", R4_MARKER}:
            add(
                errors,
                "TRUTH_SCORECARD_CONTRACT_VERSION_INVALID",
                str(scorecard_contract_version),
            )
        add(errors, "CONTENT_CONTRACT_METHOD_ARMS_INVALID", str(contract_path))
    if not (
        contract.get("execution_mode") == "content_first"
        and contract.get("contract_state") == "frozen"
        and isinstance(policy, dict)
        and policy.get("raw_response_must_be_unchanged") is True
        and policy.get("platform_audit_required_for_content_pass") is False
        and policy.get("downstream_release_state") == "RESEARCH_ONLY_BLOCKED"
    ):
        add(errors, "CONTENT_CONTRACT_MODE_INVALID", str(contract_path))

    raw_root = workspace / "03-内容原始回答"
    score_root = workspace / "07-报告" / "content-scorecards"
    envelopes: dict[Path, dict[str, Any]] = {}
    envelope_receipt_states: dict[Path, dict[str, str]] = {}
    envelope_snapshot_references: dict[Path, set[str]] = {}
    envelope_truth_paths: dict[Path, Path] = {}
    if raw_root.is_dir():
        for path in sorted(raw_root.rglob("*.json")):
            try:
                payload = load_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                add(errors, "RAW_ENVELOPE_INVALID", f"{path}: {exc}")
                continue
            body = payload.get("semantic_content_raw_answer", {}) if isinstance(payload, dict) else {}
            if body:
                envelopes[path.resolve()] = body
                envelope_subject = body.get("subject")
                envelope_owner = (
                    f"{body.get('method_arm')}:{envelope_subject.get('id')}"
                    if isinstance(envelope_subject, dict)
                    else str(body.get("method_arm"))
                )
                register_artifact_role(
                    artifact_roles,
                    errors,
                    path.resolve(),
                    f"envelope:{envelope_owner}",
                )
    if not envelopes:
        add(errors, "RAW_ENVELOPE_MISSING", str(raw_root))

    expected_scorecards: dict[Path, dict[str, Any]] = {}
    for envelope_path, body in envelopes.items():
        subject = body.get("subject")
        envelope_owner = (
            f"{body.get('method_arm')}:{subject.get('id')}"
            if isinstance(subject, dict)
            else str(body.get("method_arm"))
        )
        expected = {
            "raw_answer_id",
            "research_contract_id",
            "contract_version",
            "subject",
            "method_arm",
            "visible_input",
            "visible_input_sha256",
            "raw_response_reference",
            "raw_response_sha256",
            "raw_response_format",
            "source_observations",
            "source_snapshot_receipt_references",
            "source_truth_comparison_reference",
            "source_truth_comparison_sha256",
            "unknown_items",
            "platform_audit_state",
            "platform_audit_reference_or_null",
            "envelope_sha256",
        }
        if set(body) != expected:
            add(errors, "RAW_ENVELOPE_FIELDS_INVALID", str(envelope_path))
            continue
        if not (
            nonempty(body.get("raw_answer_id"))
            and body.get("research_contract_id") == contract.get("research_contract_id")
            and body.get("contract_version") == contract.get("contract_version")
            and isinstance(subject, dict)
            and subject.get("kind") in {"calibration_case", "terminal_node"}
            and nonempty(subject.get("id"))
            and body.get("method_arm") in allowed_arms
            and body.get("visible_input") is not None
            and body.get("visible_input_sha256") == canonical_sha256(body.get("visible_input"))
            and body.get("platform_audit_state") in PLATFORM_AUDIT_STATES
        ):
            add(errors, "RAW_ENVELOPE_SEMANTICS_INVALID", str(envelope_path))
        if contains_private_input(body.get("visible_input")):
            add(errors, "CROSS_COMPANY_INPUT_FORBIDDEN", str(envelope_path))
        observations = body.get("source_observations")
        receipt_references = body.get("source_snapshot_receipt_references")
        if not isinstance(observations, list) or not isinstance(receipt_references, list):
            add(errors, "SOURCE_OBSERVATION_LINKS_INVALID", str(envelope_path))
            observations = []
            receipt_references = []
        if len(observations) != len(receipt_references):
            add(errors, "SOURCE_OBSERVATION_RECEIPT_COUNT_MISMATCH", str(envelope_path))
        if not isinstance(body.get("unknown_items"), list):
            add(errors, "RAW_ANSWER_UNKNOWNS_INVALID", str(envelope_path))
        receipt_states: dict[str, str] = {}
        snapshot_references: set[str] = set()
        for index, observation in enumerate(observations):
            if contains_receiver_owned_field(observation):
                add(
                    errors,
                    "MODEL_OBSERVATION_RECEIVER_FIELD_FORBIDDEN",
                    f"{envelope_path}: source_observations/{index}",
                )
            if not valid_model_observation(observation):
                add(
                    errors,
                    "MODEL_SOURCE_OBSERVATION_INVALID",
                    f"{envelope_path}: source_observations/{index}",
                )
            if index >= len(receipt_references):
                continue
            receipt_error_count = len(errors)
            receipt_path = resolve_inside(workspace, receipt_references[index])
            if receipt_path is None:
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_OUTSIDE_WORKSPACE", str(receipt_references[index]))
                continue
            if receipt_path in seen_receipt_paths:
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_REUSED", str(receipt_path))
                continue
            seen_receipt_paths.add(receipt_path)
            if not receipt_path.is_file():
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_MISSING", str(receipt_path))
                continue
            register_artifact_role(
                artifact_roles,
                errors,
                receipt_path,
                f"receipt:{envelope_owner}",
            )
            try:
                receipt_payload = load_json(receipt_path)
            except (OSError, json.JSONDecodeError) as exc:
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_INVALID", f"{receipt_path}: {exc}")
                continue
            receipt = (
                receipt_payload.get("content_source_snapshot_receipt")
                if isinstance(receipt_payload, dict)
                else None
            )
            if (
                not isinstance(receipt_payload, dict)
                or set(receipt_payload) != {"schema_version", "content_source_snapshot_receipt"}
                or receipt_payload.get("schema_version") != "1.0"
                or not isinstance(receipt, dict)
                or set(receipt) != SNAPSHOT_RECEIPT_KEYS
            ):
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_INVALID", str(receipt_path))
                continue
            observation_id = receipt.get("observation_id")
            expected_receipt_reference = (
                f"05-证据包/source-snapshot-receipts/{observation_id}.receipt.json"
            )
            expected_snapshot_reference = (
                f"05-证据包/receiver-source-snapshots/{observation_id}.snapshot"
            )
            expected_source_reference = (
                f"{envelope_path.relative_to(workspace).as_posix()}"
                f"#/semantic_content_raw_answer/source_observations/{index}"
            )
            receipt_id = receipt.get("receipt_id")
            if (
                not nonempty(receipt_id)
                or not isinstance(observation_id, str)
                or not OBSERVATION_ID.fullmatch(observation_id)
                or observation_id in {".", ".."}
                or receipt.get("source_observation_reference") != expected_source_reference
                or not timezone_aware_iso8601(receipt.get("snapshot_captured_at"))
            ):
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_SEMANTICS_INVALID", str(receipt_path))
            if receipt_id != f"SNAPSHOT-{observation_id}":
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_ID_INVALID", str(receipt_path))
            if receipt_id in seen_receipt_ids:
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_ID_REUSED", str(receipt_id))
            elif isinstance(receipt_id, str):
                seen_receipt_ids.add(receipt_id)
            if (
                receipt_references[index] != expected_receipt_reference
                or has_symlink_component(workspace, expected_receipt_reference)
            ):
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_REFERENCE_INVALID", str(receipt_path))
            if observation_id in seen_observation_ids:
                add(errors, "SOURCE_OBSERVATION_ID_REUSED", str(observation_id))
            elif isinstance(observation_id, str):
                seen_observation_ids.add(observation_id)
            if receipt.get("receipt_sha256") != canonical_sha256(
                {**receipt, "receipt_sha256": None}
            ):
                add(errors, "SOURCE_SNAPSHOT_RECEIPT_HASH_MISMATCH", str(receipt_path))
            capture_state = receipt.get("snapshot_capture_state")
            if capture_state == "captured":
                if (
                    receipt.get("receiver_snapshot_reference") != expected_snapshot_reference
                    or has_symlink_component(workspace, expected_snapshot_reference)
                ):
                    add(errors, "RECEIVER_SNAPSHOT_REFERENCE_INVALID", str(receipt_path))
                if not is_sha256(receipt.get("receiver_snapshot_sha256")):
                    add(errors, "RECEIVER_SNAPSHOT_SHA256_INVALID", str(receipt_path))
                snapshot_path = resolve_inside(workspace, receipt.get("receiver_snapshot_reference"))
                if snapshot_path is None:
                    add(errors, "RECEIVER_SNAPSHOT_OUTSIDE_WORKSPACE", str(receipt_path))
                elif not snapshot_path.is_file():
                    add(errors, "RECEIVER_SNAPSHOT_MISSING", str(snapshot_path))
                elif is_sha256(receipt.get("receiver_snapshot_sha256")) and sha256_file(
                    snapshot_path
                ) != receipt.get("receiver_snapshot_sha256"):
                    add(errors, "RECEIVER_SNAPSHOT_HASH_MISMATCH", str(snapshot_path))
                else:
                    register_artifact_role(
                        artifact_roles,
                        errors,
                        snapshot_path,
                        f"receiver_snapshot:{envelope_owner}",
                    )
                    snapshot_references.add(expected_snapshot_reference)
            elif capture_state in {"unavailable", "failed"}:
                if (
                    receipt.get("receiver_snapshot_reference") is not None
                    or receipt.get("receiver_snapshot_sha256") is not None
                ):
                    add(errors, "UNVERIFIED_SNAPSHOT_FIELDS_MUST_BE_NULL", str(receipt_path))
                if not isinstance(observation, dict) or observation.get("access_state") != "UNVERIFIED":
                    add(errors, "UNVERIFIED_CAPTURE_EVIDENCE_STATE_INVALID", str(receipt_path))
                elif isinstance(observation_id, str):
                    unverified_source_observation_ids.append(observation_id)
            else:
                add(errors, "SNAPSHOT_CAPTURE_STATE_INVALID", str(receipt_path))
            if len(errors) == receipt_error_count and isinstance(capture_state, str):
                receipt_states[receipt_references[index]] = capture_state
        envelope_receipt_states[envelope_path] = receipt_states
        envelope_snapshot_references[envelope_path] = snapshot_references
        raw_target = canonical_reference_target(
            workspace, body.get("raw_response_reference")
        )
        raw_path = raw_target[0] if raw_target is not None and raw_target[1] is None else None
        if raw_path is None or not raw_path.is_file():
            add(errors, "RAW_RESPONSE_MISSING", str(envelope_path))
        elif not is_sha256(body.get("raw_response_sha256")) or sha256_file(raw_path) != body.get(
            "raw_response_sha256"
        ):
            add(errors, "RAW_RESPONSE_HASH_MISMATCH", str(envelope_path))
        else:
            register_artifact_role(
                artifact_roles,
                errors,
                raw_path,
                f"raw_response:{envelope_owner}",
            )
        source_target = canonical_reference_target(
            workspace, body.get("source_truth_comparison_reference")
        )
        source_path = (
            source_target[0]
            if source_target is not None and source_target[1] is None
            else None
        )
        if source_path is None:
            add(errors, "SOURCE_TRUTH_COMPARISON_REFERENCE_INVALID", str(envelope_path))
        elif source_path.stat().st_size == 0:
            add(errors, "SOURCE_TRUTH_COMPARISON_EMPTY", str(envelope_path))
        elif not is_sha256(body.get("source_truth_comparison_sha256")) or sha256_file(source_path) != body.get(
            "source_truth_comparison_sha256"
        ):
            add(errors, "SOURCE_TRUTH_COMPARISON_HASH_MISMATCH", str(envelope_path))
        elif r4_scoring_required:
            try:
                truth_payload = load_json(source_path)
            except (OSError, json.JSONDecodeError) as exc:
                add(errors, "CONTENT_CASE_TRUTH_INVALID", f"{source_path}: {exc}")
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
            ):
                add(errors, "CONTENT_CASE_TRUTH_INVALID", str(source_path))
            else:
                envelope_truth_paths[envelope_path] = source_path
                register_artifact_role(artifact_roles, errors, source_path, "truth_file")
                if not (
                    nonempty(truth.get("truth_id"))
                    and truth.get("research_contract_id") == contract.get("research_contract_id")
                    and truth.get("contract_version") == contract.get("contract_version")
                    and truth.get("case_id")
                    == (subject.get("id") if isinstance(subject, dict) else None)
                ):
                    add(errors, "CONTENT_CASE_TRUTH_BINDING_MISMATCH", str(source_path))
                all_truth_source_identities: list[tuple[int, int]] = []
                all_truth_source_hashes: list[str] = []
                basis_valid = True
                truth_source_reference_invalid = False
                for basis_name in (
                    "taxonomy_membership_basis",
                    "output_or_subprocess_basis",
                    "mechanism_basis",
                ):
                    basis = truth.get(basis_name)
                    source_references = (
                        basis.get("source_references") if isinstance(basis, dict) else None
                    )
                    verified_source_references = (
                        [
                            valid_truth_source_reference(workspace, source_path, reference)
                            for reference in source_references
                        ]
                        if isinstance(source_references, list)
                        else []
                    )
                    if isinstance(source_references, list) and any(
                        reference is None for reference in verified_source_references
                    ):
                        truth_source_reference_invalid = True
                    verified_source_identities = [
                        (reference[2], reference[3])
                        for reference in verified_source_references
                        if reference is not None
                    ]
                    verified_source_hashes = [
                        reference[1]
                        for reference in verified_source_references
                        if reference is not None
                    ]
                    if not (
                        isinstance(basis, dict)
                        and set(basis) == {"basis_text", "source_references"}
                        and nonempty(basis.get("basis_text"))
                        and isinstance(source_references, list)
                        and bool(source_references)
                        and all(reference is not None for reference in verified_source_references)
                        and len(set(verified_source_identities))
                        == len(verified_source_identities)
                    ):
                        basis_valid = False
                        continue
                    all_truth_source_identities.extend(verified_source_identities)
                    all_truth_source_hashes.extend(verified_source_hashes)
                    for verified_reference in verified_source_references:
                        if verified_reference is not None:
                            source_artifact = canonical_reference_target(
                                workspace, verified_reference[0]
                            )
                            if source_artifact is not None:
                                register_artifact_role(
                                    artifact_roles,
                                    errors,
                                    source_artifact[0],
                                    "truth_source",
                                )
                if not basis_valid:
                    add(errors, "CONTENT_CASE_TRUTH_INVALID", str(source_path))
                if truth_source_reference_invalid:
                    add(errors, "TRUTH_SOURCE_REFERENCE_INVALID", str(source_path))
                elif (
                    len(set(all_truth_source_identities)) != len(all_truth_source_identities)
                    or len(set(all_truth_source_hashes)) != len(all_truth_source_hashes)
                ):
                    add(errors, "TRUTH_SOURCE_REFERENCE_REUSED", str(source_path))
                expected_axes = truth.get("expected_semantic_axes")
                if not (
                    isinstance(expected_axes, dict)
                    and set(expected_axes)
                    == {
                        "screening_result",
                        "semantic_work_state",
                        "expected_output_evidence_state",
                    }
                    and expected_axes.get("screening_result") in SCREENING_RESULTS
                    and expected_axes.get("semantic_work_state") in SEMANTIC_WORK_STATES
                    and expected_axes.get("expected_output_evidence_state")
                    in EVIDENCE_STATES
                    and truth.get("truth_disposition") in TRUTH_DISPOSITIONS
                    and truth.get("evidence_state")
                    in ADJUDICATION_EVIDENCE_STATES
                    and truth.get("evidence_quality") in EVIDENCE_QUALITIES
                    and truth.get("adjudication_state") == "accepted"
                    and nonempty(truth.get("adjudication_version"))
                    and valid_text_list(truth.get("conditions"))
                    and valid_text_list(truth.get("limitations"))
                    and valid_text_list(truth.get("unknowns"))
                    and nonempty(truth.get("truth_boundary"))
                    and truth.get("truth_sha256")
                    == canonical_sha256({**truth, "truth_sha256": None})
                ):
                    add(errors, "CONTENT_CASE_TRUTH_INVALID", str(source_path))
        expected_envelope_hash = canonical_sha256({**body, "envelope_sha256": None})
        if body.get("envelope_sha256") != expected_envelope_hash:
            add(errors, "RAW_ENVELOPE_HASH_MISMATCH", str(envelope_path))
        expected_scorecards[envelope_path] = body

    scorecards: dict[Path, dict[str, Any]] = {}
    if score_root.is_dir():
        for path in sorted(score_root.rglob("*.json")):
            try:
                payload = load_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                add(errors, "SCORECARD_INVALID", f"{path}: {exc}")
                continue
            body = payload.get("semantic_content_scorecard") if isinstance(payload, dict) else None
            if (
                not isinstance(payload, dict)
                or set(payload) != {"schema_version", "semantic_content_scorecard"}
                or payload.get("schema_version") != "1.0"
                or not isinstance(body, dict)
            ):
                add(errors, "SCORECARD_INVALID", str(path))
                continue
            scorecards[path.resolve()] = body
            score_subject = body.get("subject")
            score_owner = (
                f"{body.get('method_arm')}:{score_subject.get('id')}"
                if isinstance(score_subject, dict)
                else str(body.get("method_arm"))
            )
            register_artifact_role(
                artifact_roles,
                errors,
                path.resolve(),
                f"scorecard:{score_owner}",
            )
    if not scorecards:
        add(errors, "SCORECARD_MISSING", str(score_root))

    matched_envelopes: set[Path] = set()
    for score_path, body in scorecards.items():
        expected_scorecard_fields = (
            R4_SCORECARD_FIELDS if r4_scoring_required else LEGACY_SCORECARD_FIELDS
        )
        if set(body) != expected_scorecard_fields:
            add(errors, "SCORECARD_FIELDS_INVALID", str(score_path))
            continue
        envelope_target = canonical_reference_target(
            workspace, body.get("raw_answer_reference")
        )
        envelope_path = (
            envelope_target[0]
            if envelope_target is not None and envelope_target[1] is None
            else None
        )
        envelope = envelopes.get(envelope_path) if envelope_path is not None else None
        if envelope is None:
            add(errors, "SCORECARD_RAW_ENVELOPE_MISSING", str(score_path))
            continue
        matched_envelopes.add(envelope_path)
        if body.get("raw_answer_sha256") != sha256_file(envelope_path):
            add(errors, "SCORECARD_RAW_ENVELOPE_HASH_MISMATCH", str(score_path))
        for field in (
            "subject",
            "method_arm",
            "visible_input_sha256",
            "source_truth_comparison_reference",
            "source_truth_comparison_sha256",
        ):
            if body.get(field) != envelope.get(field):
                add(errors, "SCORECARD_ENVELOPE_MISMATCH", f"{score_path}: {field}")
        if r4_scoring_required:
            truth_path = envelope_truth_paths.get(envelope_path)
            if truth_path is None:
                add(errors, "CONTENT_CASE_TRUTH_INVALID", str(score_path))
                continue
            validation = validate_r4_scorecard(
                workspace=workspace,
                scorecard_path=score_path,
                payload={"schema_version": "1.0", "semantic_content_scorecard": body},
                envelope_path=envelope_path,
                envelope=envelope,
                truth_path=truth_path,
                receipt_states=envelope_receipt_states.get(envelope_path, {}),
                snapshot_references=envelope_snapshot_references.get(envelope_path, set()),
                expected_contract_id=contract.get("research_contract_id"),
                expected_contract_version=contract.get("contract_version"),
                expected_file_sha256=sha256_file(score_path),
            )
            for issue in validation["issues"]:
                add(errors, issue["code"], issue["detail"])
            expected_result = validation["content_score_result"]
            if expected_result == "FAIL":
                add(errors, "CONTENT_SCORE_FAIL", str(score_path))
            elif expected_result == "UNVERIFIED":
                unverified_scorecard_ids.append(str(body.get("scorecard_id")))
            continue
        items = body.get("scoring_items")
        score_item_names = LEGACY_SCORE_ITEMS
        items_valid = isinstance(items, dict) and set(items) == score_item_names
        if items_valid and isinstance(items, dict):
            for name in score_item_names:
                item = items[name]
                if not (
                    isinstance(item, dict)
                    and type(item.get("score")) is int
                    and item.get("score") in {0, 1, 2}
                    and type(item.get("critical")) is bool
                    and nonempty(item.get("reason"))
                ):
                    items_valid = False
        if not items_valid:
            add(errors, "SCORECARD_ITEMS_INVALID", str(score_path))
            continue
        if not isinstance(body.get("unknown_items"), list):
            add(errors, "SCORECARD_UNKNOWNS_MISSING", str(score_path))
        if body.get("platform_audit_state") not in PLATFORM_AUDIT_STATES:
            add(errors, "SCORECARD_PLATFORM_AUDIT_INVALID", str(score_path))
        expected_result = score_result(items, score_item_names)
        if body.get("content_score_result") != expected_result:
            add(errors, "SCORECARD_RESULT_INVALID", str(score_path))
        if expected_result != "PASS":
            add(errors, "CONTENT_SCORE_NOT_PASS", str(score_path))
        if body.get("scorecard_sha256") != canonical_sha256({**body, "scorecard_sha256": None}):
            add(errors, "SCORECARD_HASH_MISMATCH", str(score_path))
    for envelope_path in expected_scorecards:
        if envelope_path not in matched_envelopes:
            add(errors, "SCORECARD_FOR_RAW_ENVELOPE_MISSING", str(envelope_path))

    has_unverified = bool(
        unverified_source_observation_ids
        or unverified_scorecard_ids
    )
    report = {
        "status": "FAIL" if errors else ("UNVERIFIED" if has_unverified else "PASS"),
        "workspace": str(workspace),
        "errors": errors,
        "unverified_source_observation_ids": sorted(set(unverified_source_observation_ids)),
        "unverified_scorecard_ids": sorted(set(unverified_scorecard_ids)),
    }
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(report["status"])
        for error in errors:
            print(f"{error['code']}: {error['detail']}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
