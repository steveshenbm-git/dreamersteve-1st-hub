#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
from typing import Any

from content_first_r4_scorecard_schema import validate_r4_scorecard
from r4_adjudicated_truth_contract import (
    BETA5_TRUTH_SCORECARD_CONTRACT_VERSION,
    derive_truth_summary,
)


R4_MARKER = BETA5_TRUTH_SCORECARD_CONTRACT_VERSION
LEGACY_MARKER = "1.0-legacy"
R4_ARMS = ("baseline_full_depth_v1", "screen_then_expand_v2")
LEGACY_ARMS = ("baseline_full_depth", "candidate_screen_then_expand")
RESOURCE_QUERY_FIELDS = {
    "query_id",
    "query_text",
    "role",
    "language",
    "region",
    "observed_result_references",
    "inspected_result_count",
    "opened_source_references",
    "access_outcomes",
}
RESOURCE_FIELDS = {
    "observation_id",
    "research_contract_id",
    "contract_version",
    "case_id",
    "method_arm",
    "task_reference",
    "task_sha256",
    "deep_expansion_disposition",
    "queries",
    "query_count",
    "source_open_count",
    "observation_sha256",
}
RESOURCE_PREAUTH_FIELDS = {
    "authorization_id",
    "permitted_action",
    "research_contract_id",
    "contract_version",
    "case_id",
    "method_arm",
    "original_candidate_task_reference",
    "task_sha256",
    "fresh_context_id",
    "authorized_at",
    "model_execution_authorized",
    "downstream_authorized",
}
RAW_ENVELOPE_FIELDS = {
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
SUMMARY_CASE_FIELDS = {
    "case_id",
    "visible_input_sha256",
    "task_id",
    "task_reference",
    "task_sha256",
    "raw_envelope_reference",
    "raw_envelope_sha256",
    "raw_response_reference",
    "raw_response_sha256",
    "scorecard_reference",
    "scorecard_sha256",
    "resource_observation_reference",
    "resource_observation_sha256",
    "resource_observation_receipt_reference",
    "resource_observation_receipt_sha256",
    "content_score_result",
    "unknown_items_present",
    "critical_dispositions",
}
STABILITY_RECEIPT_FIELDS = {
    "receipt_id",
    "repeat_id",
    "case_id",
    "method_arm",
    "visible_input_sha256",
    "repeat_task_reference",
    "repeat_task_sha256",
    "preauthorization_reference",
    "preauthorization_sha256",
    "original_candidate_task_reference",
    "original_candidate_task_sha256",
    "raw_envelope_reference",
    "raw_envelope_sha256",
    "raw_response_reference",
    "raw_response_sha256",
    "scorecard_reference",
    "scorecard_sha256",
    "resource_observation_reference",
    "resource_observation_sha256",
    "resource_observation_receipt_reference",
    "resource_observation_receipt_sha256",
    "receipt_sha256",
}


class Incomplete(ValueError):
    pass


class Failed(ValueError):
    pass


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}), file=sys.stderr)
    return 2


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonnegative_int(value: Any) -> bool:
    return type(value) is int and value >= 0


def timezone_aware_iso8601(value: Any) -> bool:
    if not nonempty(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def string_list(value: Any, *, count: int | None = None) -> bool:
    return (
        isinstance(value, list)
        and (count is None or len(value) == count)
        and all(nonempty(item) for item in value)
        and len(set(value)) == len(value)
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[Any]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_arm(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    arm = payload.get("semantic_content_calibration_arm") if isinstance(payload, dict) else None
    if not isinstance(arm, dict):
        raise Incomplete("semantic_content_calibration_arm is missing")
    return arm


def canonical_workspace_reference(workspace: Path, reference: Any) -> Path:
    if not nonempty(reference) or "\\" in reference or "//" in reference or "#" in reference:
        raise Incomplete("artifact reference is not canonical")
    pure = PurePosixPath(reference)
    if pure.is_absolute() or pure.as_posix() != reference or any(
        part in {"", ".", ".."} for part in pure.parts
    ):
        raise Incomplete("artifact reference is not canonical")
    current = workspace.resolve()
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise Incomplete("artifact reference uses a symlink")
    if not current.is_file():
        raise Incomplete("artifact reference is missing")
    try:
        resolved = current.resolve()
        if resolved.relative_to(workspace.resolve()).as_posix() != reference:
            raise Incomplete("artifact reference is aliased")
    except (OSError, ValueError) as exc:
        raise Incomplete("artifact reference escapes workspace") from exc
    return resolved


def trusted_workspace_file(workspace: Path, path: Path, expected_hash: Any) -> Path:
    if not is_sha256(expected_hash):
        raise Incomplete("trusted expected SHA-256 is invalid")
    try:
        resolved = path.resolve()
        reference = resolved.relative_to(workspace.resolve()).as_posix()
    except (OSError, ValueError) as exc:
        raise Incomplete("trusted artifact is outside workspace") from exc
    canonical = canonical_workspace_reference(workspace, reference)
    if file_sha256(canonical) != expected_hash:
        raise Incomplete("trusted artifact hash mismatch")
    return canonical


def reference_and_hash(workspace: Path, value: Any) -> tuple[Path, str]:
    if not (
        isinstance(value, dict)
        and set(value) == {"reference", "sha256"}
        and is_sha256(value.get("sha256"))
    ):
        raise Incomplete("reference-and-hash binding is malformed")
    path = canonical_workspace_reference(workspace, value["reference"])
    if file_sha256(path) != value["sha256"]:
        raise Incomplete("reference-and-hash binding drifted")
    return path, value["sha256"]


class ArtifactRegistry:
    def __init__(self) -> None:
        self.identities: dict[tuple[int, int], str] = {}
        self.unique_hashes: dict[str, str] = {}

    def add(self, path: Path, role: str, *, bytes_must_be_unique: bool) -> None:
        stat = path.stat()
        identity = (stat.st_dev, stat.st_ino)
        previous = self.identities.get(identity)
        if previous is not None:
            raise Incomplete(f"artifact inode reused across {previous} and {role}")
        self.identities[identity] = role
        if bytes_must_be_unique:
            digest = file_sha256(path)
            previous_hash_role = self.unique_hashes.get(digest)
            if previous_hash_role is not None:
                raise Incomplete(
                    f"artifact bytes reused across {previous_hash_role} and {role}"
                )
            self.unique_hashes[digest] = role


def read_bound_json(
    workspace: Path,
    reference: Any,
    expected_hash: Any,
    registry: ArtifactRegistry,
    role: str,
    *,
    bytes_must_be_unique: bool,
) -> tuple[Path, Any]:
    if not is_sha256(expected_hash):
        raise Incomplete(f"{role} SHA-256 is malformed")
    path = canonical_workspace_reference(workspace, reference)
    if file_sha256(path) != expected_hash:
        raise Incomplete(f"{role} SHA-256 mismatch")
    registry.add(path, role, bytes_must_be_unique=bytes_must_be_unique)
    try:
        return path, load_json(path)
    except (OSError, ValueError) as exc:
        raise Incomplete(f"{role} JSON is invalid") from exc


def load_frozen_inputs(
    workspace: Path,
    contract_path: Path,
    contract_hash: str,
    manifest_path: Path,
    manifest_hash: str,
) -> tuple[dict[str, Any], list[str], set[str], list[str], dict[tuple[str, str], dict[str, Any]], dict[str, str]]:
    contract_payload = load_json(contract_path)
    contract = (
        contract_payload.get("semantic_research_contract")
        if isinstance(contract_payload, dict)
        else None
    )
    if not isinstance(contract, dict):
        raise Incomplete("final frozen research contract is malformed")
    gates = contract.get("retrieval_efficiency_gates")
    policy = contract.get("content_first_policy")
    if (
        contract.get("contract_state") != "frozen"
        or contract.get("execution_mode") != "content_first"
        or contract.get("baseline_method_contract") != R4_ARMS[0]
        or contract.get("candidate_method_contract") != R4_ARMS[1]
        or not isinstance(policy, dict)
        or policy.get("truth_scorecard_contract_version") != R4_MARKER
        or not isinstance(gates, dict)
        or set(gates)
        != {
            "minimum_deep_expansion_reduction",
            "maximum_query_count_increase",
            "maximum_source_open_count_increase",
            "stability_repeat_case_count",
        }
        or type(gates.get("minimum_deep_expansion_reduction")) not in {int, float}
        or gates.get("minimum_deep_expansion_reduction") != 0.2
        or type(gates.get("maximum_query_count_increase")) not in {int, float}
        or gates.get("maximum_query_count_increase") != 0.1
        or type(gates.get("maximum_source_open_count_increase")) not in {int, float}
        or gates.get("maximum_source_open_count_increase") != 0.0
        or type(gates.get("stability_repeat_case_count")) is not int
        or gates.get("stability_repeat_case_count") != 6
    ):
        raise Incomplete("frozen R4 efficiency gates or method contract are invalid")
    case_binding = contract.get("calibration_case_set_reference_and_hash")
    truth_binding = {
        "reference": contract.get("source_truth_package_reference"),
        "sha256": contract.get("source_truth_package_sha256"),
    }
    case_path, _ = reference_and_hash(workspace, case_binding)
    truth_path, _ = reference_and_hash(workspace, truth_binding)
    case_rows = load_jsonl(case_path)
    truth_rows = load_jsonl(truth_path)
    header = case_rows[0] if case_rows else None
    formal_ids = header.get("formal_case_ids") if isinstance(header, dict) else None
    repeat_ids = header.get("stability_repeat_case_ids") if isinstance(header, dict) else None
    cases = [row for row in case_rows if isinstance(row, dict) and row.get("record_type") == "calibration_case"]
    if (
        not string_list(formal_ids, count=40)
        or not string_list(repeat_ids, count=6)
        or not set(repeat_ids).issubset(set(formal_ids))
        or len(cases) != 40
        or [row.get("case_id") for row in cases] != formal_ids
    ):
        raise Incomplete("formal case-set IDs or six repeat selections are invalid")
    truth_by_case: dict[str, dict[str, Any]] = {}
    for row in truth_rows:
        if not isinstance(row, dict) or not nonempty(row.get("case_id")) or row["case_id"] in truth_by_case:
            raise Incomplete("source-truth case binding is malformed")
        truth_by_case[row["case_id"]] = row
    if set(truth_by_case) != set(formal_ids):
        raise Incomplete("source-truth does not cover the formal case set")
    truth_summary = derive_truth_summary(truth_rows)
    if contract.get("adjudicated_truth_summary") != truth_summary:
        raise Incomplete("adjudicated truth summary does not match frozen source truth")
    positives = set(truth_summary["accepted_positive_case_ids"])
    if not positives:
        raise Incomplete("accepted-positive denominator must not be empty")

    manifest_payload = load_json(manifest_path)
    manifest = (
        manifest_payload.get("content_first_paired_task_manifest")
        if isinstance(manifest_payload, dict)
        else None
    )
    pairs = manifest.get("pairs") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or manifest.get("research_contract_id") != contract.get("research_contract_id")
        or manifest.get("contract_version") != contract.get("contract_version")
        or manifest.get("final_contract_sha256") != contract_hash
        or manifest.get("formal_case_set_sha256") != case_binding.get("sha256")
        or manifest.get("pair_count") != 40
        or manifest.get("task_count") != 80
        or manifest.get("execution_authorized") is not False
        or not isinstance(pairs, list)
        or len(pairs) != 40
    ):
        raise Incomplete("paired Task 4 manifest is not bound to the final contract")
    task_map: dict[tuple[str, str], dict[str, Any]] = {}
    visible_hashes: dict[str, str] = {}
    task_identities: set[tuple[int, int]] = set()
    task_hashes: set[str] = set()
    for expected_case_id, pair in zip(formal_ids, pairs):
        if (
            not isinstance(pair, dict)
            or pair.get("case_id") != expected_case_id
            or not is_sha256(pair.get("visible_input_sha256"))
            or not isinstance(pair.get("task_files"), dict)
            or set(pair["task_files"]) != set(R4_ARMS)
        ):
            raise Incomplete("paired Task 4 manifest case binding is invalid")
        visible_hashes[expected_case_id] = pair["visible_input_sha256"]
        for arm in R4_ARMS:
            entry = pair["task_files"][arm]
            if not (
                isinstance(entry, dict)
                and set(entry) == {"path", "task_file_sha256"}
                and is_sha256(entry.get("task_file_sha256"))
            ):
                raise Incomplete("paired Task 4 task entry is invalid")
            try:
                task_reference = (manifest_path.parent / entry["path"]).relative_to(
                    workspace
                ).as_posix()
            except ValueError as exc:
                raise Incomplete("Task 4 task path escapes workspace") from exc
            task_path = canonical_workspace_reference(workspace, task_reference)
            if file_sha256(task_path) != entry["task_file_sha256"]:
                raise Incomplete("Task 4 task hash mismatch")
            stat = task_path.stat()
            identity = (stat.st_dev, stat.st_ino)
            if identity in task_identities or entry["task_file_sha256"] in task_hashes:
                raise Incomplete("Task 4 task artifact is reused across case or arm")
            task_identities.add(identity)
            task_hashes.add(entry["task_file_sha256"])
            task = load_json(task_path)
            body = task.get("content_first_calibration_task") if isinstance(task, dict) else None
            if (
                not isinstance(body, dict)
                or body.get("task_id") != f"{expected_case_id}--{arm}"
                or body.get("research_contract_id") != contract.get("research_contract_id")
                or body.get("contract_version") != contract.get("contract_version")
                or body.get("method_arm") != arm
                or body.get("execution_authorized") is not False
                or body.get("visible_input_sha256") != pair["visible_input_sha256"]
                or not isinstance(body.get("visible_input"), dict)
                or body["visible_input"].get("case_id") != expected_case_id
                or canonical_sha256(body["visible_input"]) != pair["visible_input_sha256"]
            ):
                raise Incomplete("Task 4 task content is misbound")
            task_map[(expected_case_id, arm)] = {
                "reference": task_reference,
                "sha256": entry["task_file_sha256"],
                "task_id": body["task_id"],
            }
    return contract, formal_ids, positives, repeat_ids, task_map, visible_hashes


def validate_snapshot_receipts(
    workspace: Path,
    references: Any,
    registry: ArtifactRegistry,
    role_prefix: str,
) -> tuple[set[str], dict[str, str], set[str]]:
    if not isinstance(references, list) or not all(nonempty(item) for item in references):
        raise Incomplete("receiver snapshot receipt references are malformed")
    result: set[str] = set()
    states: dict[str, str] = {}
    snapshots: set[str] = set()
    for index, reference in enumerate(references):
        path = canonical_workspace_reference(workspace, reference)
        registry.add(path, f"{role_prefix}:snapshot-receipt:{index}", bytes_must_be_unique=True)
        payload = load_json(path)
        body = payload.get("content_source_snapshot_receipt") if isinstance(payload, dict) else None
        if not isinstance(body, dict):
            raise Incomplete("receiver snapshot receipt is malformed")
        claimed = body.get("receipt_sha256")
        snapshot_reference = body.get("receiver_snapshot_reference")
        snapshot_hash = body.get("receiver_snapshot_sha256")
        if (
            not is_sha256(claimed)
            or canonical_sha256({**body, "receipt_sha256": None}) != claimed
            or body.get("snapshot_capture_state") != "captured"
            or not is_sha256(snapshot_hash)
        ):
            raise Incomplete("receiver snapshot receipt integrity is incomplete")
        snapshot = canonical_workspace_reference(workspace, snapshot_reference)
        if file_sha256(snapshot) != snapshot_hash:
            raise Incomplete("receiver snapshot bytes do not match receipt")
        registry.add(snapshot, f"{role_prefix}:snapshot:{index}", bytes_must_be_unique=False)
        result.add(reference)
        states[reference] = body["snapshot_capture_state"]
        snapshots.add(snapshot_reference)
    return result, states, snapshots


def validate_resource_record(
    workspace: Path,
    observation_payload: Any,
    receipt_payload: Any,
    *,
    observation_reference: str,
    observation_hash: str,
    case_id: str,
    arm: str,
    task_reference: str,
    task_hash: str,
    snapshot_receipts: set[str],
    research_contract_id: str,
    contract_version: str,
    preauthorization_task_reference: str | None = None,
    preauthorization_task_hash: str | None = None,
    required_preauthorization_reference: str | None = None,
    required_preauthorization_hash: str | None = None,
) -> tuple[int, int, int]:
    body = (
        observation_payload.get("content_resource_observation")
        if isinstance(observation_payload, dict)
        else None
    )
    if (
        not isinstance(observation_payload, dict)
        or set(observation_payload) != {"schema_version", "content_resource_observation"}
        or observation_payload.get("schema_version") != "1.0"
        or not isinstance(body, dict)
        or set(body) != RESOURCE_FIELDS
    ):
        raise Incomplete("receiver resource observation schema is invalid")
    expected_preauth_reference = preauthorization_task_reference or task_reference
    expected_preauth_hash = preauthorization_task_hash or task_hash
    if (
        not nonempty(body.get("observation_id"))
        or body.get("research_contract_id") != research_contract_id
        or body.get("contract_version") != contract_version
        or body.get("case_id") != case_id
        or body.get("method_arm") != arm
        or body.get("task_reference") != task_reference
        or body.get("task_sha256") != task_hash
        or body.get("deep_expansion_disposition") not in {"expanded", "screen_only"}
        or not isinstance(body.get("queries"), list)
        or not nonnegative_int(body.get("query_count"))
        or not nonnegative_int(body.get("source_open_count"))
        or not is_sha256(body.get("observation_sha256"))
        or canonical_sha256({**body, "observation_sha256": None})
        != body.get("observation_sha256")
    ):
        raise Incomplete("receiver resource observation binding is invalid")
    query_ids: set[str] = set()
    observed_references: set[str] = set()
    opened_references: set[str] = set()
    opened_count = 0
    for query in body["queries"]:
        if not isinstance(query, dict) or set(query) != RESOURCE_QUERY_FIELDS:
            raise Incomplete("receiver resource query schema is invalid")
        query_id = query.get("query_id")
        observed = query.get("observed_result_references")
        opened = query.get("opened_source_references")
        outcomes = query.get("access_outcomes")
        if (
            not nonempty(query_id)
            or query_id in query_ids
            or not all(nonempty(query.get(field)) for field in ("query_text", "role", "language", "region"))
            or not nonnegative_int(query.get("inspected_result_count"))
            or not isinstance(observed, list)
            or not isinstance(opened, list)
            or not all(nonempty(item) for item in [*observed, *opened])
            or len(set(observed)) != len(observed)
            or len(set(opened)) != len(opened)
            or not set(observed).issubset(snapshot_receipts)
            or not set(opened).issubset(snapshot_receipts)
            or not isinstance(outcomes, list)
            or len(outcomes) != len(opened)
        ):
            raise Incomplete("receiver resource query binding is invalid")
        if query["inspected_result_count"] != len(observed):
            raise Incomplete(
                "receiver resource inspected-result count does not match exact records"
            )
        outcome_refs: list[str] = []
        for outcome in outcomes:
            if (
                not isinstance(outcome, dict)
                or set(outcome) != {"source_reference", "access_state"}
                or outcome.get("source_reference") not in opened
                or outcome.get("access_state") not in {"opened", "unavailable", "failed"}
            ):
                raise Incomplete("receiver resource access outcome is invalid")
            outcome_refs.append(outcome["source_reference"])
        if set(outcome_refs) != set(opened):
            raise Incomplete("receiver resource access outcomes do not cover opens")
        if observed_references.intersection(observed):
            raise Incomplete("receiver resource observed-result record is reused")
        if opened_references.intersection(opened):
            raise Incomplete("receiver resource source-open record is reused")
        observed_references.update(observed)
        opened_references.update(opened)
        query_ids.add(query_id)
        opened_count += len(opened)
    if body["query_count"] != len(body["queries"]) or body["source_open_count"] != opened_count:
        raise Incomplete("receiver resource counts do not match exact query records")

    receipt = (
        receipt_payload.get("content_resource_observation_receipt")
        if isinstance(receipt_payload, dict)
        else None
    )
    if not isinstance(receipt, dict):
        raise Incomplete("receiver resource observation receipt is missing")
    receipt_hash = receipt.get("receipt_sha256")
    if (
        receipt.get("receiver_owned") is not True
        or receipt.get("resource_observation_reference") != observation_reference
        or receipt.get("resource_observation_sha256") != observation_hash
        or not is_sha256(receipt_hash)
        or canonical_sha256({**receipt, "receipt_sha256": None}) != receipt_hash
        or not is_sha256(receipt.get("preauthorization_sha256"))
        or (
            required_preauthorization_reference is not None
            and receipt.get("preauthorization_reference")
            != required_preauthorization_reference
        )
        or (
            required_preauthorization_hash is not None
            and receipt.get("preauthorization_sha256") != required_preauthorization_hash
        )
    ):
        raise Incomplete("receiver resource receipt binding is invalid")
    preauth_path = canonical_workspace_reference(
        workspace, receipt.get("preauthorization_reference")
    )
    if file_sha256(preauth_path) != receipt["preauthorization_sha256"]:
        raise Incomplete("receiver resource preauthorization hash mismatch")
    preauth_payload = load_json(preauth_path)
    preauth = (
        preauth_payload.get("receiver_resource_observation_preauthorization")
        if isinstance(preauth_payload, dict)
        else None
    )
    if (
        not isinstance(preauth_payload, dict)
        or set(preauth_payload)
        != {"schema_version", "receiver_resource_observation_preauthorization"}
        or preauth_payload.get("schema_version") != "1.0"
        or not isinstance(preauth, dict)
        or set(preauth) != RESOURCE_PREAUTH_FIELDS
        or not nonempty(preauth.get("authorization_id"))
        or preauth.get("permitted_action")
        != "capture_content_resource_observation_only"
        or preauth.get("research_contract_id") != research_contract_id
        or preauth.get("contract_version") != contract_version
        or preauth.get("case_id") != case_id
        or preauth.get("method_arm") != arm
        or preauth.get("original_candidate_task_reference") != expected_preauth_reference
        or preauth.get("task_sha256") != expected_preauth_hash
        or not nonempty(preauth.get("fresh_context_id"))
        or not timezone_aware_iso8601(preauth.get("authorized_at"))
        or preauth.get("model_execution_authorized") is not False
        or preauth.get("downstream_authorized") is not False
    ):
        raise Incomplete("receiver resource preauthorization is misbound")
    return body["query_count"], body["source_open_count"], (
        1 if body["deep_expansion_disposition"] == "expanded" else 0
    )


def validate_run_artifacts(
    workspace: Path,
    row: dict[str, Any],
    *,
    case_id: str,
    arm: str,
    visible_hash: str,
    task_reference: str,
    task_hash: str,
    research_contract_id: str,
    contract_version: str,
    registry: ArtifactRegistry,
    role_prefix: str,
    preauthorization_task_reference: str | None = None,
    preauthorization_task_hash: str | None = None,
    required_preauthorization_reference: str | None = None,
    required_preauthorization_hash: str | None = None,
    preauthorization_already_registered: bool = False,
) -> tuple[dict[str, str], str, tuple[int, int, int]]:
    for field in (
        "raw_envelope_sha256",
        "raw_response_sha256",
        "scorecard_sha256",
        "resource_observation_sha256",
        "resource_observation_receipt_sha256",
    ):
        if not is_sha256(row.get(field)):
            raise Incomplete(f"{role_prefix} summary hash is malformed")
    envelope_path, envelope_payload = read_bound_json(
        workspace,
        row.get("raw_envelope_reference"),
        row.get("raw_envelope_sha256"),
        registry,
        f"{role_prefix}:raw-envelope",
        bytes_must_be_unique=True,
    )
    envelope_body = (
        envelope_payload.get("semantic_content_raw_answer")
        if isinstance(envelope_payload, dict)
        else None
    )
    if (
        not isinstance(envelope_payload, dict)
        or set(envelope_payload) != {"schema_version", "semantic_content_raw_answer"}
        or envelope_payload.get("schema_version") != "1.0"
        or not isinstance(envelope_body, dict)
        or set(envelope_body) != RAW_ENVELOPE_FIELDS
    ):
        raise Incomplete("raw envelope schema is invalid")
    if (
        not nonempty(envelope_body.get("raw_answer_id"))
        or envelope_body.get("research_contract_id") != research_contract_id
        or envelope_body.get("contract_version") != contract_version
        or envelope_body.get("subject") != {"kind": "calibration_case", "id": case_id}
        or envelope_body.get("method_arm") != arm
        or not isinstance(envelope_body.get("visible_input"), dict)
        or canonical_sha256(envelope_body.get("visible_input")) != visible_hash
        or envelope_body.get("visible_input_sha256") != visible_hash
        or envelope_body.get("raw_response_reference") != row.get("raw_response_reference")
        or envelope_body.get("raw_response_sha256") != row.get("raw_response_sha256")
        or not isinstance(envelope_body.get("unknown_items"), list)
        or not nonempty(envelope_body.get("raw_response_format"))
        or not isinstance(envelope_body.get("source_observations"), list)
        or not isinstance(envelope_body.get("source_snapshot_receipt_references"), list)
        or len(envelope_body["source_observations"])
        != len(envelope_body["source_snapshot_receipt_references"])
        or envelope_body.get("platform_audit_state")
        not in {"PASS", "FAIL", "UNVERIFIED", "NOT_COLLECTED"}
        or (
            envelope_body.get("platform_audit_state") == "NOT_COLLECTED"
            and envelope_body.get("platform_audit_reference_or_null") is not None
        )
    ):
        raise Incomplete("raw envelope is misbound to case, arm, or task input")
    envelope_internal_hash = envelope_body.get("envelope_sha256")
    if not is_sha256(envelope_internal_hash) or canonical_sha256(
        {**envelope_body, "envelope_sha256": None}
    ) != envelope_internal_hash:
        raise Incomplete("raw envelope internal hash is invalid")
    raw_path = canonical_workspace_reference(workspace, row["raw_response_reference"])
    if file_sha256(raw_path) != row["raw_response_sha256"]:
        raise Incomplete("raw response hash mismatch")
    registry.add(raw_path, f"{role_prefix}:raw-response", bytes_must_be_unique=False)
    snapshot_receipts, receipt_states, snapshot_references = validate_snapshot_receipts(
        workspace,
        envelope_body.get("source_snapshot_receipt_references"),
        registry,
        role_prefix,
    )
    score_path, score_payload = read_bound_json(
        workspace,
        row.get("scorecard_reference"),
        row.get("scorecard_sha256"),
        registry,
        f"{role_prefix}:scorecard",
        bytes_must_be_unique=True,
    )
    truth_path = canonical_workspace_reference(
        workspace, envelope_body.get("source_truth_comparison_reference")
    )
    if file_sha256(truth_path) != envelope_body.get("source_truth_comparison_sha256"):
        raise Incomplete("raw envelope source-truth binding is invalid")
    score_validation = validate_r4_scorecard(
        workspace=workspace,
        scorecard_path=score_path,
        payload=score_payload,
        envelope_path=envelope_path,
        envelope=envelope_body,
        truth_path=truth_path,
        receipt_states=receipt_states,
        snapshot_references=snapshot_references,
        expected_contract_id=research_contract_id,
        expected_contract_version=contract_version,
        expected_file_sha256=row.get("scorecard_sha256"),
    )
    if score_validation["issues"]:
        raise Incomplete(
            "Task 6 scorecard invalid: "
            + ", ".join(issue["code"] for issue in score_validation["issues"])
        )
    dispositions = score_validation["dispositions"]
    score_result = score_validation["content_score_result"]
    observation_path, observation_payload = read_bound_json(
        workspace,
        row.get("resource_observation_reference"),
        row.get("resource_observation_sha256"),
        registry,
        f"{role_prefix}:resource-observation",
        bytes_must_be_unique=True,
    )
    receipt_path, receipt_payload = read_bound_json(
        workspace,
        row.get("resource_observation_receipt_reference"),
        row.get("resource_observation_receipt_sha256"),
        registry,
        f"{role_prefix}:resource-receipt",
        bytes_must_be_unique=True,
    )
    receipt_body = receipt_payload.get("content_resource_observation_receipt")
    if not isinstance(receipt_body, dict):
        raise Incomplete("receiver resource receipt schema is invalid")
    preauth_path = canonical_workspace_reference(
        workspace, receipt_body.get("preauthorization_reference")
    )
    if not preauthorization_already_registered:
        registry.add(
            preauth_path,
            f"{role_prefix}:resource-preauthorization",
            bytes_must_be_unique=True,
        )
    metrics = validate_resource_record(
        workspace,
        observation_payload,
        receipt_payload,
        observation_reference=observation_path.relative_to(workspace).as_posix(),
        observation_hash=file_sha256(observation_path),
        case_id=case_id,
        arm=arm,
        task_reference=task_reference,
        task_hash=task_hash,
        snapshot_receipts=snapshot_receipts,
        research_contract_id=research_contract_id,
        contract_version=contract_version,
        preauthorization_task_reference=preauthorization_task_reference,
        preauthorization_task_hash=preauthorization_task_hash,
        required_preauthorization_reference=required_preauthorization_reference,
        required_preauthorization_hash=required_preauthorization_hash,
    )
    # The receipt and score files are read for their bytes; keep variables explicit for role audit.
    _ = score_path, receipt_path
    return dispositions, score_result, metrics


def validate_arm(
    workspace: Path,
    arm: dict[str, Any],
    *,
    expected_arm: str,
    contract: dict[str, Any],
    contract_reference: str,
    contract_hash: str,
    manifest_reference: str,
    manifest_hash: str,
    formal_ids: list[str],
    positives: set[str],
    task_map: dict[tuple[str, str], dict[str, Any]],
    visible_hashes: dict[str, str],
    registry: ArtifactRegistry,
) -> tuple[
    dict[str, dict[str, str]],
    tuple[int, int, int],
    dict[str, dict[str, Any]],
    set[str],
]:
    if (
        arm.get("calibration_contract_marker") != R4_MARKER
        or arm.get("research_contract_id") != contract.get("research_contract_id")
        or arm.get("contract_version") != contract.get("contract_version")
        or arm.get("taxonomy_snapshot_sha256") != contract.get("taxonomy_snapshot_sha256")
        or arm.get("calibration_case_set_sha256")
        != contract.get("calibration_case_set_reference_and_hash", {}).get("sha256")
        or arm.get("source_truth_package_sha256")
        != contract.get("source_truth_package_sha256")
        or arm.get("method_arm") != expected_arm
        or arm.get("run_complete") is not True
        or arm.get("content_reproducible") is not True
        or arm.get("final_contract_reference_and_hash")
        != {"reference": contract_reference, "sha256": contract_hash}
        or arm.get("paired_task_manifest_reference_and_hash")
        != {"reference": manifest_reference, "sha256": manifest_hash}
        or not isinstance(arm.get("safety_failures"), list)
    ):
        raise Incomplete("R4 arm summary is not bound to frozen inputs")
    rows = arm.get("case_evidence")
    if not isinstance(rows, list) or len(rows) != 40:
        raise Incomplete("R4 arm summary must contain exactly 40 cases")
    positive_summary = arm.get("accepted_positive_case_ids")
    entered_summary = arm.get("accepted_positive_entered_expansion_case_ids")
    if (
        not string_list(positive_summary)
        or len(positive_summary) != len(positives)
        or set(positive_summary) != positives
    ):
        raise Incomplete("summary accepted-positive IDs do not match frozen source truth")
    if not string_list(entered_summary):
        raise Incomplete("candidate expansion IDs are malformed")
    row_by_case: dict[str, dict[str, Any]] = {}
    dispositions_by_case: dict[str, dict[str, str]] = {}
    expanded_case_ids: set[str] = set()
    query_total = source_total = deep_total = 0
    for expected_case_id, row in zip(formal_ids, rows):
        if not isinstance(row, dict) or set(row) != SUMMARY_CASE_FIELDS:
            raise Incomplete("R4 case summary schema is invalid")
        task = task_map[(expected_case_id, expected_arm)]
        if (
            row.get("case_id") != expected_case_id
            or row.get("visible_input_sha256") != visible_hashes[expected_case_id]
            or row.get("task_id") != task["task_id"]
            or row.get("task_reference") != task["reference"]
            or row.get("task_sha256") != task["sha256"]
            or row.get("unknown_items_present") is not True
        ):
            raise Incomplete("R4 case summary is misbound to the Task 4 task")
        dispositions, score_result, metrics = validate_run_artifacts(
            workspace,
            row,
            case_id=expected_case_id,
            arm=expected_arm,
            visible_hash=visible_hashes[expected_case_id],
            task_reference=task["reference"],
            task_hash=task["sha256"],
            research_contract_id=contract["research_contract_id"],
            contract_version=contract["contract_version"],
            registry=registry,
            role_prefix=f"{expected_arm}:{expected_case_id}",
        )
        if row.get("critical_dispositions") != dispositions or row.get(
            "content_score_result"
        ) != score_result:
            raise Incomplete("summary score dispositions do not match Task 6 scorecard")
        dispositions_by_case[expected_case_id] = dispositions
        query_total += metrics[0]
        source_total += metrics[1]
        deep_total += metrics[2]
        if metrics[2] == 1:
            expanded_case_ids.add(expected_case_id)
        row_by_case[expected_case_id] = row
    if any(
        not nonnegative_int(arm.get(field))
        for field in ("query_count", "source_open_count", "deep_expansion_count")
    ) or (
        arm["query_count"], arm["source_open_count"], arm["deep_expansion_count"]
    ) != (query_total, source_total, deep_total):
        raise Incomplete("resource totals do not match receiver-owned observations")
    return (
        dispositions_by_case,
        (query_total, source_total, deep_total),
        row_by_case,
        expanded_case_ids,
    )


def validate_stability(
    workspace: Path,
    candidate: dict[str, Any],
    *,
    contract: dict[str, Any],
    contract_hash: str,
    manifest_hash: str,
    repeat_ids: list[str],
    task_map: dict[tuple[str, str], dict[str, Any]],
    visible_hashes: dict[str, str],
    original_dispositions: dict[str, dict[str, str]],
    registry: ArtifactRegistry,
    stability_manifest_path: Path,
    stability_manifest_hash: str,
) -> None:
    declared = candidate.get("stability_task_manifest_reference_and_hash")
    expected_stability_ref = stability_manifest_path.relative_to(workspace).as_posix()
    if declared != {"reference": expected_stability_ref, "sha256": stability_manifest_hash}:
        raise Incomplete("stability task manifest summary binding is invalid")
    payload = load_json(stability_manifest_path)
    body = payload.get("content_first_stability_task_manifest") if isinstance(payload, dict) else None
    entries = body.get("entries") if isinstance(body, dict) else None
    if (
        not isinstance(body, dict)
        or body.get("research_contract_id") != contract.get("research_contract_id")
        or body.get("contract_version") != contract.get("contract_version")
        or body.get("final_contract_sha256") != contract_hash
        or body.get("formal_case_set_sha256")
        != contract.get("calibration_case_set_reference_and_hash", {}).get("sha256")
        or body.get("paired_task_manifest_sha256") != manifest_hash
        or body.get("method_arm") != R4_ARMS[1]
        or body.get("repeat_case_count") != 6
        or body.get("repeat_case_ids") != repeat_ids
        or body.get("created_before_repeat_execution") is not True
        or body.get("model_execution_authorized") is not False
        or body.get("downstream_authorized") is not False
        or not isinstance(entries, list)
        or len(entries) != 6
    ):
        raise Incomplete("frozen stability task manifest is invalid")
    task_by_case: dict[str, dict[str, Any]] = {}
    seen_authorization_ids: set[str] = set()
    seen_fresh_context_ids: set[str] = set()
    package_root = stability_manifest_path.parent
    for expected_case_id, entry in zip(repeat_ids, entries):
        if not isinstance(entry, dict) or entry.get("case_id") != expected_case_id:
            raise Incomplete("stability task entry case binding is invalid")
        try:
            task_ref = (package_root / entry["repeat_task_reference"]).relative_to(
                workspace
            ).as_posix()
            preauth_ref = (package_root / entry["preauthorization_reference"]).relative_to(
                workspace
            ).as_posix()
        except (KeyError, ValueError) as exc:
            raise Incomplete("stability task path is invalid") from exc
        task_path = canonical_workspace_reference(workspace, task_ref)
        preauth_path = canonical_workspace_reference(workspace, preauth_ref)
        if (
            file_sha256(task_path) != entry.get("repeat_task_sha256")
            or file_sha256(preauth_path) != entry.get("preauthorization_sha256")
        ):
            raise Incomplete("stability task or preauthorization hash mismatch")
        registry.add(task_path, f"stability-task:{expected_case_id}", bytes_must_be_unique=True)
        registry.add(preauth_path, f"stability-preauth:{expected_case_id}", bytes_must_be_unique=True)
        task_payload = load_json(task_path)
        task = (
            task_payload.get("content_first_stability_repeat_task")
            if isinstance(task_payload, dict)
            else None
        )
        preauth_payload = load_json(preauth_path)
        preauth = (
            preauth_payload.get("receiver_resource_observation_preauthorization")
            if isinstance(preauth_payload, dict)
            else None
        )
        original = task_map[(expected_case_id, R4_ARMS[1])]
        if (
            not isinstance(task, dict)
            or task.get("repeat_id") != entry.get("repeat_id")
            or task.get("case_id") != expected_case_id
            or task.get("method_arm") != R4_ARMS[1]
            or task.get("visible_input_sha256") != visible_hashes[expected_case_id]
            or task.get("original_candidate_task_reference") != original["reference"]
            or task.get("original_candidate_task_sha256") != original["sha256"]
            or task.get("preauthorization_reference") != entry["preauthorization_reference"]
            or task.get("preauthorization_sha256") != entry["preauthorization_sha256"]
            or not nonempty(task.get("fresh_context_id"))
            or task.get("counts_toward_formal_case_score") is not False
            or task.get("execution_authorized") is not False
        ):
            raise Incomplete("stability repeat task is misbound")
        authorization_id = preauth.get("authorization_id") if isinstance(preauth, dict) else None
        fresh_context_id = preauth.get("fresh_context_id") if isinstance(preauth, dict) else None
        if (
            not isinstance(preauth_payload, dict)
            or set(preauth_payload)
            != {"schema_version", "receiver_resource_observation_preauthorization"}
            or preauth_payload.get("schema_version") != "1.0"
            or not isinstance(preauth, dict)
            or set(preauth) != RESOURCE_PREAUTH_FIELDS
            or not nonempty(authorization_id)
            or authorization_id in seen_authorization_ids
            or not nonempty(fresh_context_id)
            or fresh_context_id in seen_fresh_context_ids
            or preauth.get("permitted_action")
            != "capture_content_resource_observation_only"
            or preauth.get("research_contract_id") != contract.get("research_contract_id")
            or preauth.get("contract_version") != contract.get("contract_version")
            or preauth.get("case_id") != expected_case_id
            or preauth.get("method_arm") != R4_ARMS[1]
            or preauth.get("original_candidate_task_reference") != original["reference"]
            or preauth.get("task_sha256") != original["sha256"]
            or fresh_context_id != task["fresh_context_id"]
            or not nonempty(preauth.get("authorized_at"))
            or preauth.get("model_execution_authorized") is not False
            or preauth.get("downstream_authorized") is not False
            or not timezone_aware_iso8601(preauth.get("authorized_at"))
        ):
            raise Incomplete(
                "stability repeats require independent preauthorization and fresh context"
            )
        seen_authorization_ids.add(authorization_id)
        seen_fresh_context_ids.add(fresh_context_id)
        task_by_case[expected_case_id] = {
            "repeat_id": task["repeat_id"],
            "fresh_context_id": task["fresh_context_id"],
            "reference": task_ref,
            "sha256": entry["repeat_task_sha256"],
            "preauthorization_reference": preauth_ref,
            "preauthorization_sha256": entry["preauthorization_sha256"],
        }
    receipt_refs = candidate.get("stability_repeat_receipts")
    if not isinstance(receipt_refs, list) or len(receipt_refs) != 6:
        raise Incomplete("six stability repeats are incomplete")
    seen_receipt_ids: set[str] = set()
    seen_cases: set[str] = set()
    for ref_record in receipt_refs:
        receipt_path, receipt_hash = reference_and_hash(workspace, ref_record)
        registry.add(receipt_path, "stability-execution-receipt", bytes_must_be_unique=True)
        payload = load_json(receipt_path)
        receipt = payload.get("content_first_stability_repeat_receipt") if isinstance(payload, dict) else None
        if not isinstance(receipt, dict) or set(receipt) != STABILITY_RECEIPT_FIELDS:
            raise Incomplete("six stability repeats are incomplete")
        case_id = receipt.get("case_id")
        repeat_task = task_by_case.get(case_id)
        internal_hash = receipt.get("receipt_sha256")
        if (
            repeat_task is None
            or not nonempty(receipt.get("receipt_id"))
            or receipt["receipt_id"] in seen_receipt_ids
            or case_id in seen_cases
            or receipt.get("repeat_id") != repeat_task["repeat_id"]
            or receipt.get("method_arm") != R4_ARMS[1]
            or receipt.get("visible_input_sha256") != visible_hashes[case_id]
            or receipt.get("repeat_task_reference") != repeat_task["reference"]
            or receipt.get("repeat_task_sha256") != repeat_task["sha256"]
            or receipt.get("preauthorization_reference")
            != repeat_task["preauthorization_reference"]
            or receipt.get("preauthorization_sha256")
            != repeat_task["preauthorization_sha256"]
            or receipt.get("original_candidate_task_reference")
            != task_map[(case_id, R4_ARMS[1])]["reference"]
            or receipt.get("original_candidate_task_sha256")
            != task_map[(case_id, R4_ARMS[1])]["sha256"]
            or not is_sha256(internal_hash)
            or canonical_sha256({**receipt, "receipt_sha256": None}) != internal_hash
            or receipt_hash != file_sha256(receipt_path)
        ):
            raise Incomplete("six stability repeats are incomplete")
        run_row = {
            key: receipt[key]
            for key in (
                "raw_envelope_reference",
                "raw_envelope_sha256",
                "raw_response_reference",
                "raw_response_sha256",
                "scorecard_reference",
                "scorecard_sha256",
                "resource_observation_reference",
                "resource_observation_sha256",
                "resource_observation_receipt_reference",
                "resource_observation_receipt_sha256",
            )
        }
        dispositions, _, _ = validate_run_artifacts(
            workspace,
            run_row,
            case_id=case_id,
            arm=R4_ARMS[1],
            visible_hash=visible_hashes[case_id],
            task_reference=repeat_task["reference"],
            task_hash=repeat_task["sha256"],
            research_contract_id=contract["research_contract_id"],
            contract_version=contract["contract_version"],
            registry=registry,
            role_prefix=f"stability:{case_id}",
            preauthorization_task_reference=task_map[(case_id, R4_ARMS[1])]["reference"],
            preauthorization_task_hash=task_map[(case_id, R4_ARMS[1])]["sha256"],
            required_preauthorization_reference=repeat_task["preauthorization_reference"],
            required_preauthorization_hash=repeat_task["preauthorization_sha256"],
            preauthorization_already_registered=True,
        )
        if dispositions != original_dispositions[case_id]:
            raise Failed("stability critical dispositions are inconsistent")
        seen_receipt_ids.add(receipt["receipt_id"])
        seen_cases.add(case_id)
    if seen_cases != set(repeat_ids):
        raise Incomplete("six stability repeats do not cover the frozen selection")


def legacy_evidence_map(arm: dict[str, Any]) -> dict[str, dict[str, Any]] | None:
    rows = arm.get("case_evidence")
    if not isinstance(rows, list) or len(rows) != 40:
        return None
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            return None
        case_id = row.get("case_id")
        if not nonempty(case_id) or case_id in result:
            return None
        if not (
            is_sha256(row.get("visible_input_sha256"))
            and is_sha256(row.get("raw_response_sha256"))
            and is_sha256(row.get("scorecard_sha256"))
            and row.get("content_score_result") == "PASS"
            and row.get("unknown_items_present") is True
        ):
            return None
        result[case_id] = row
    return result


def evaluate_legacy(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    minimum_reduction: float,
) -> tuple[str, list[str], bool, dict[str, Any]]:
    evidence_a = legacy_evidence_map(baseline)
    evidence_b = legacy_evidence_map(candidate)
    if evidence_a is None or evidence_b is None or set(evidence_a) != set(evidence_b):
        return "INCOMPLETE", ["legacy 40-case evidence is incomplete"], False, {}
    if baseline.get("method_arm") != LEGACY_ARMS[0] or candidate.get("method_arm") != LEGACY_ARMS[1]:
        return "INCOMPLETE", ["legacy method arms are invalid"], False, {}
    baseline_count = baseline.get("deep_expansion_count")
    candidate_count = candidate.get("deep_expansion_count")
    if not all(type(value) is int and 0 <= value <= 40 for value in (baseline_count, candidate_count)):
        return "INCOMPLETE", ["legacy counts are invalid"], False, {}
    reasons: list[str] = []
    if (baseline_count - candidate_count) / baseline_count + 1e-12 < minimum_reduction:
        reasons.append("deep expansion reduction is below the frozen threshold")
    return ("FAIL" if reasons else "PASS"), reasons, True, {
        "baseline_deep_expansion_count": baseline_count,
        "candidate_deep_expansion_count": candidate_count,
        "deep_expansion_reduction": (baseline_count - candidate_count) / baseline_count,
    }


def empty_efficiency() -> dict[str, Any]:
    return {
        "efficiency_gate_state": "NOT_EVALUATED",
        "baseline_query_count": None,
        "candidate_query_count": None,
        "baseline_source_open_count": None,
        "candidate_source_open_count": None,
        "baseline_deep_expansion_count": None,
        "candidate_deep_expansion_count": None,
        "deep_expansion_reduction": None,
    }


def atomic_publish(path: Path, report: dict[str, Any], inject_failure: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(report, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if inject_failure:
            raise OSError("injected failure before publication")
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate real paired R4 artifacts with critical gates before frozen efficiency gates."
    )
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--expected-final-contract-sha256")
    parser.add_argument("--paired-task-manifest", type=Path)
    parser.add_argument("--expected-paired-task-manifest-sha256")
    parser.add_argument("--stability-task-manifest", type=Path)
    parser.add_argument("--expected-stability-task-manifest-sha256")
    parser.add_argument("--minimum-reduction", type=float, default=None)
    parser.add_argument("--maximum-query-increase", type=float, default=None)
    parser.add_argument("--test-fail-before-publish", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.output.exists():
        return fail("OUTPUT_EXISTS", str(args.output))
    try:
        baseline = load_arm(args.baseline)
        candidate = load_arm(args.candidate)
    except (OSError, ValueError, TypeError) as exc:
        return fail("CALIBRATION_INPUT_INVALID", str(exc))
    marker_a = baseline.get("calibration_contract_marker")
    marker_b = candidate.get("calibration_contract_marker")
    result = "INCOMPLETE"
    reasons: list[str] = []
    efficiency = empty_efficiency()
    contract: dict[str, Any] = {}
    contract_hash: str | None = None
    manifest_hash: str | None = None
    case_count: int | None = None
    stability_count: int | None = None
    try:
        if marker_a == marker_b == R4_MARKER:
            if args.minimum_reduction is not None or args.maximum_query_increase is not None:
                raise Incomplete("R4 efficiency thresholds cannot be overridden from CLI")
            if any(
                value is None
                for value in (
                    args.workspace,
                    args.contract,
                    args.expected_final_contract_sha256,
                    args.paired_task_manifest,
                    args.expected_paired_task_manifest_sha256,
                    args.stability_task_manifest,
                    args.expected_stability_task_manifest_sha256,
                )
            ):
                raise Incomplete("trusted R4 workspace, contract, task, and stability inputs are required")
            workspace = args.workspace.resolve()
            if not workspace.is_dir():
                raise Incomplete("trusted R4 workspace is missing")
            contract_path = trusted_workspace_file(
                workspace, args.contract, args.expected_final_contract_sha256
            )
            manifest_path = trusted_workspace_file(
                workspace,
                args.paired_task_manifest,
                args.expected_paired_task_manifest_sha256,
            )
            stability_manifest_path = trusted_workspace_file(
                workspace,
                args.stability_task_manifest,
                args.expected_stability_task_manifest_sha256,
            )
            contract_hash = args.expected_final_contract_sha256
            manifest_hash = args.expected_paired_task_manifest_sha256
            (
                contract,
                formal_ids,
                positives,
                repeat_ids,
                task_map,
                visible_hashes,
            ) = load_frozen_inputs(
                workspace,
                contract_path,
                contract_hash,
                manifest_path,
                manifest_hash,
            )
            contract_reference = contract_path.relative_to(workspace).as_posix()
            manifest_reference = manifest_path.relative_to(workspace).as_posix()
            registry = ArtifactRegistry()
            baseline_dispositions, baseline_metrics, _, _ = validate_arm(
                workspace,
                baseline,
                expected_arm=R4_ARMS[0],
                contract=contract,
                contract_reference=contract_reference,
                contract_hash=contract_hash,
                manifest_reference=manifest_reference,
                manifest_hash=manifest_hash,
                formal_ids=formal_ids,
                positives=positives,
                task_map=task_map,
                visible_hashes=visible_hashes,
                registry=registry,
            )
            (
                candidate_dispositions,
                candidate_metrics,
                _,
                candidate_expanded_case_ids,
            ) = validate_arm(
                workspace,
                candidate,
                expected_arm=R4_ARMS[1],
                contract=contract,
                contract_reference=contract_reference,
                contract_hash=contract_hash,
                manifest_reference=manifest_reference,
                manifest_hash=manifest_hash,
                formal_ids=formal_ids,
                positives=positives,
                task_map=task_map,
                visible_hashes=visible_hashes,
                registry=registry,
            )
            case_count = 40
            # Gate 1: safety across both arms.
            if baseline.get("safety_failures") or candidate.get("safety_failures") or any(
                dispositions["safety_boundary"] == "FAIL"
                for dispositions in [
                    *baseline_dispositions.values(),
                    *candidate_dispositions.values(),
                ]
            ):
                raise Failed("critical safety gate failed")
            if any(
                dispositions["safety_boundary"] == "UNVERIFIED"
                for dispositions in [
                    *baseline_dispositions.values(),
                    *candidate_dispositions.values(),
                ]
            ):
                raise Incomplete("critical safety gate is unverified")
            # Gate 2: frozen truth and actual receiver-owned expansion dispositions.
            if (
                set(candidate["accepted_positive_entered_expansion_case_ids"])
                != positives
                or not positives.issubset(candidate_expanded_case_ids)
            ):
                raise Failed("accepted-positive content recall is below 100 percent")
            # Gate 3: every Task 6 critical disposition must be closed before stability.
            flattened = [
                disposition
                for case in [*baseline_dispositions.values(), *candidate_dispositions.values()]
                for disposition in case.values()
            ]
            if "FAIL" in flattened:
                raise Failed("critical receiver or scorecard evidence failed")
            if "UNVERIFIED" in flattened:
                raise Incomplete("critical receiver or scorecard evidence is incomplete")
            # Gate 4: six predeclared high-risk candidate cases, each one fresh repeat.
            validate_stability(
                workspace,
                candidate,
                contract=contract,
                contract_hash=contract_hash,
                manifest_hash=manifest_hash,
                repeat_ids=repeat_ids,
                task_map=task_map,
                visible_hashes=visible_hashes,
                original_dispositions=candidate_dispositions,
                registry=registry,
                stability_manifest_path=stability_manifest_path,
                stability_manifest_hash=args.expected_stability_task_manifest_sha256,
            )
            stability_count = 6
            # Gate 5: frozen integer thresholds; no float arithmetic or CLI override.
            bq, bo, bd = baseline_metrics
            cq, co, cd = candidate_metrics
            efficiency_reasons: list[str] = []
            if bd != 40:
                raise Incomplete("baseline full-depth observations do not cover all 40 cases")
            if cd * 5 > bd * 4:
                efficiency_reasons.append("deep expansion reduction is below the frozen threshold")
            if cq * 10 > bq * 11:
                efficiency_reasons.append("query count increase exceeds 10 percent")
            if co > bo:
                efficiency_reasons.append("source-open count exceeds baseline")
            efficiency = {
                "efficiency_gate_state": "FAIL" if efficiency_reasons else "PASS",
                "baseline_query_count": bq,
                "candidate_query_count": cq,
                "baseline_source_open_count": bo,
                "candidate_source_open_count": co,
                "baseline_deep_expansion_count": bd,
                "candidate_deep_expansion_count": cd,
                "deep_expansion_reduction": (bd - cd) / bd,
            }
            reasons.extend(efficiency_reasons)
            result = "FAIL" if reasons else "PASS"
        elif marker_a == marker_b == LEGACY_MARKER:
            minimum = 0.2 if args.minimum_reduction is None else args.minimum_reduction
            if not 0 <= minimum < 1:
                raise Incomplete("legacy minimum reduction is invalid")
            result, reasons, evaluated, legacy_metrics = evaluate_legacy(
                baseline, candidate, minimum
            )
            if evaluated:
                efficiency.update(legacy_metrics)
                efficiency["efficiency_gate_state"] = result
        else:
            raise Incomplete("explicit matching calibration contract marker is required")
    except Failed as exc:
        result = "FAIL"
        reasons = [str(exc)]
        efficiency = empty_efficiency()
    except (Incomplete, OSError, ValueError, TypeError, KeyError) as exc:
        result = "INCOMPLETE"
        reasons = [str(exc) or "R4 evaluation input is incomplete"]
        efficiency = empty_efficiency()

    report = {
        "schema_version": R4_MARKER if marker_a == R4_MARKER else "1.0",
        "evaluation_result": result,
        "content_method_state": f"CONTENT_CALIBRATION_{result}",
        "gate_order": [
            "safety",
            "accepted_positive_recall",
            "receiver_evidence_completeness",
            "stability",
            "efficiency",
        ],
        "critical_content_rules_applied_before_efficiency": True,
        "platform_audit_used_as_content_gate": False,
        "not_beta3_effectiveness": True,
        "research_contract_id": contract.get("research_contract_id", baseline.get("research_contract_id")),
        "contract_version": contract.get("contract_version", baseline.get("contract_version")),
        "final_contract_sha256": contract_hash,
        "paired_task_manifest_sha256": manifest_hash,
        "case_count": case_count,
        "stability_repeat_count": stability_count,
        **efficiency,
        "minimum_required_reduction": 0.2 if marker_a == R4_MARKER else args.minimum_reduction,
        "maximum_allowed_query_count_increase": 0.1 if marker_a == R4_MARKER else None,
        "maximum_allowed_source_open_count_increase": 0.0 if marker_a == R4_MARKER else None,
        "safety_failures": [
            *(baseline.get("safety_failures") if isinstance(baseline.get("safety_failures"), list) else []),
            *(candidate.get("safety_failures") if isinstance(candidate.get("safety_failures"), list) else []),
        ],
        "downstream_authorized": False,
        "reasons": reasons,
    }
    try:
        atomic_publish(args.output, report, args.test_fail_before_publish)
    except FileExistsError:
        return fail("OUTPUT_EXISTS", str(args.output))
    except OSError as exc:
        return fail("OUTPUT_PUBLICATION_FAILED", str(exc))
    print(
        json.dumps(
            {
                "status": result,
                "content_method_state": report["content_method_state"],
                "output": str(args.output),
            }
        )
    )
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
