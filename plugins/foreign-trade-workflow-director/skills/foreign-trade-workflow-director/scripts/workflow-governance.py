#!/usr/bin/env python3
"""Validate and perform one authorized append/rebuild in an existing governance root."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Optional


PASS = 0
FAIL = 2
UNVERIFIED = 3
CONTRACT_ID = "FTWG-INSPECTOR-GOVERNANCE"
CONTRACT_VERSION = "1.0.0-draft.3"
AUTHORIZATION_CLASS = "governance_registry_write"

LOG_SPECS = {
    "finding": ("findings_log", "findings.jsonl", "event_id", "event_count"),
    "improvement": (
        "improvement_log",
        "improvement-events.jsonl",
        "improvement_event_id",
        "event_count",
    ),
    "validation": (
        "validation_log",
        "validation-events.jsonl",
        "validation_event_id",
        "event_count",
    ),
    "evidence": (
        "evidence_index",
        "evidence-index.jsonl",
        "evidence_event_id",
        "record_count",
    ),
}

DISPOSITIONS = {
    "continue": 0,
    "continue_with_correction": 1,
    "rehearsal_only": 2,
    "stop": 3,
}
TERMINAL_FINDING_STATES = {"verified_closed", "not_a_defect", "superseded"}
FINDING_STATES = {
    "open", "contained", "source_fix_pending", "source_fixed_unreleased",
    "released_unverified", "installed_unverified", "forward_validation_pending",
    "verified_closed", "not_a_defect", "superseded", "reopened",
}
VALIDATION_LAYERS = {
    "contract_consistency", "deterministic_regression", "full_test_suite",
    "source_release", "installed_artifact_identity", "task_forward_validation",
    "cross_company_validation", "real_effectiveness",
}
VALIDATION_STATES = {
    "NOT_STARTED", "PASS", "FAIL", "UNVERIFIED", "STALE", "NOT_APPLICABLE",
}
IMPROVEMENT_STATES = {
    "proposed", "design_accepted", "baseline_captured", "implementation_authorized",
    "source_changed", "tests_passed", "published", "installed_verified",
    "forward_validation_in_progress", "forward_validation_passed",
    "accepted_effective", "superseded", "reopened",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_event_hash(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "event_sha256"}
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return sha256_bytes(encoded)


def json_result(code: int, operation: str, **fields: Any) -> tuple[int, dict[str, Any]]:
    result = "PASS" if code == PASS else "UNVERIFIED" if code == UNVERIFIED else "FAIL"
    return code, {"result": result, "operation": operation, **fields}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_root(value: str) -> tuple[Optional[Path], list[str]]:
    path = Path(value)
    issues: list[str] = []
    if not path.exists():
        return None, ["governance root does not exist; initialization is not supported"]
    if path.is_symlink():
        return None, ["governance root must not be a symlink"]
    if not path.is_dir():
        return None, ["governance root is not a directory"]
    return path.resolve(), issues


def safe_child(root: Path, name: str) -> tuple[Optional[Path], Optional[str]]:
    if Path(name).name != name or name in {"", ".", ".."}:
        return None, f"unsafe governance file reference: {name!r}"
    path = root / name
    if path.is_symlink():
        return None, f"symlink is not allowed in governance root: {name}"
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError:
        return None, f"required governance file is missing: {name}"
    if resolved.parent != root or not resolved.is_file():
        return None, f"governance file escapes approved root or is not a file: {name}"
    return resolved, None


def read_log(
    path: Path, *, id_field: str, kind: str
) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    issues: list[str] = []
    seen_ids: set[str] = set()
    expected_previous = None
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            issues.append(f"{path.name}:{line_number}: blank JSONL line")
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            issues.append(f"{path.name}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(event, dict):
            issues.append(f"{path.name}:{line_number}: event must be an object")
            continue
        event_id = event.get(id_field)
        if not isinstance(event_id, str) or not event_id:
            issues.append(f"{path.name}:{line_number}: missing {id_field}")
        elif event_id in seen_ids:
            issues.append(f"{path.name}:{line_number}: duplicate event id {event_id}")
        else:
            seen_ids.add(event_id)
        if event.get("sequence") != line_number:
            issues.append(f"{path.name}:{line_number}: sequence is not strictly increasing")
        if event.get("previous_event_sha256") != expected_previous:
            issues.append(f"{path.name}:{line_number}: previous event hash mismatch")
        actual_hash = canonical_event_hash(event)
        if event.get("event_sha256") != actual_hash:
            issues.append(f"{path.name}:{line_number}: event hash mismatch")
        validate_event(event, kind, issues, f"{path.name}:{line_number}")
        expected_previous = event.get("event_sha256")
        events.append(event)
    return events, issues


def validate_event(
    event: dict[str, Any], kind: str, issues: list[str], location: str
) -> None:
    if event.get("authorization_class") not in {None, AUTHORIZATION_CLASS}:
        issues.append(f"{location}: unsupported authorization class")
    if event.get("specialist_truth_override") is True:
        issues.append(f"{location}: specialist truth override is prohibited")
    if kind == "finding":
        for field in ("event_id", "finding_id", "title", "affected_skill_id"):
            if not isinstance(event.get(field), str) or not event.get(field):
                issues.append(f"{location}: missing stable {field}")
        if not isinstance(event.get("affected_scope"), list) or not event.get("affected_scope"):
            issues.append(f"{location}: affected_scope must be a non-empty list")
        if not isinstance(event.get("evidence"), list) or not event.get("evidence"):
            issues.append(f"{location}: finding evidence must be a non-empty list")
        if event.get("severity") not in {"record", "corrective", "acceptance_blocker", "severe_blocker"}:
            issues.append(f"{location}: invalid severity")
        if event.get("flow_disposition") not in DISPOSITIONS:
            issues.append(f"{location}: invalid flow disposition")
        state = event.get("lifecycle_state")
        if state not in FINDING_STATES:
            issues.append(f"{location}: invalid finding lifecycle state")
        required = event.get("required_validation_layers", [])
        completed = event.get("completed_validation_layers", [])
        if not isinstance(required, list) or not set(required).issubset(VALIDATION_LAYERS):
            issues.append(f"{location}: invalid required validation layers")
        if not isinstance(completed, list) or not set(completed).issubset(VALIDATION_LAYERS):
            issues.append(f"{location}: invalid completed validation layers")
        if state == "verified_closed" and not set(required).issubset(set(completed)):
            issues.append(f"{location}: verified_closed lacks required validation layers")
        if state == "verified_closed" and event.get("recorder_role") == "specialist_candidate":
            issues.append(f"{location}: specialist candidate cannot close a finding")
    elif kind == "validation":
        for field in ("validation_event_id", "skill_id", "skill_version"):
            if not isinstance(event.get(field), str) or not event.get(field):
                issues.append(f"{location}: missing stable {field}")
        if event.get("validation_layer") not in VALIDATION_LAYERS:
            issues.append(f"{location}: invalid validation layer")
        if event.get("result") not in VALIDATION_STATES:
            issues.append(f"{location}: invalid validation result")
        if not event.get("skill_version"):
            issues.append(f"{location}: validation event is not bound to a skill version")
    elif kind == "improvement":
        for field in ("improvement_event_id", "improvement_id", "target_skill_id"):
            if not isinstance(event.get(field), str) or not event.get(field):
                issues.append(f"{location}: missing stable {field}")
        state = event.get("to_state")
        if state not in IMPROVEMENT_STATES:
            issues.append(f"{location}: invalid improvement lifecycle state")
        if state == "accepted_effective" and not event.get("user_authorization_reference"):
            issues.append(f"{location}: accepted_effective lacks user acceptance")
    elif kind == "evidence":
        for field in ("evidence_event_id", "evidence_id", "reference"):
            if not isinstance(event.get(field), str) or not event.get(field):
                issues.append(f"{location}: missing stable {field}")
        if event.get("integrity_state") not in VALIDATION_STATES:
            issues.append(f"{location}: invalid evidence integrity state")
        if event.get("integrity_state") == "PASS" and not event.get("sha256"):
            issues.append(f"{location}: PASS evidence lacks sha256")


def derive_state(logs: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    latest_findings: dict[str, dict[str, Any]] = {}
    latest_improvements: dict[str, dict[str, Any]] = {}
    for event in logs["finding"]:
        finding_id = event.get("finding_id")
        if isinstance(finding_id, str):
            latest_findings[finding_id] = event
    for event in logs["improvement"]:
        improvement_id = event.get("improvement_id")
        if isinstance(improvement_id, str):
            latest_improvements[improvement_id] = event

    open_events = [
        event
        for event in latest_findings.values()
        if event.get("lifecycle_state") not in TERMINAL_FINDING_STATES
    ]
    disposition = "continue"
    if open_events:
        disposition = max(
            (event.get("flow_disposition", "continue") for event in open_events),
            key=lambda item: DISPOSITIONS.get(item, -1),
        )
    actions = {
        event.get("one_next_action")
        for event in open_events
        if isinstance(event.get("one_next_action"), str) and event.get("one_next_action")
    }
    owners = {
        event.get("next_action_owner") for event in open_events
        if event.get("one_next_action") in actions and event.get("next_action_owner")
    }
    authorizations = {
        event.get("next_authorization_required") for event in open_events
        if event.get("one_next_action") in actions and event.get("next_authorization_required")
    }
    blocking = sorted(
        event["finding_id"]
        for event in open_events
        if event.get("flow_disposition") == "stop" and isinstance(event.get("finding_id"), str)
    )
    cycles = []
    for improvement_id, event in sorted(latest_improvements.items()):
        cycles.append({
            "improvement_id": improvement_id,
            "target_skill_id": event.get("target_skill_id"),
            "target_version_or_candidate": event.get("target_version_or_candidate"),
            "trigger_finding_ids": event.get("trigger_finding_ids", []),
            "lifecycle_state": event.get("to_state"),
            "design_reference": event.get("design_reference"),
            "design_sha256": event.get("design_sha256"),
            "latest_improvement_event_id": event.get("improvement_event_id"),
            "remaining_gates": event.get("remaining_gates", []),
        })
    return {
        "highest_open_disposition": disposition,
        "active_blocking_finding_ids": blocking,
        "one_next_action": next(iter(actions)) if len(actions) == 1 else None,
        "next_action_owner": next(iter(owners)) if len(owners) == 1 else None,
        "next_authorization_required": (
            next(iter(authorizations)) if len(authorizations) == 1 else None
        ),
        "action_count": len(actions),
        "improvement_cycles": cycles,
    }


def inspect_root(
    root: Path, *, check_snapshot: bool, parent_registry: Optional[str] = None
) -> dict[str, Any]:
    issues: list[str] = []
    unverified: list[str] = []
    registry_path, error = safe_child(root, "governance-registry.yaml")
    if error:
        return {"issues": [error], "unverified": [], "registry": None, "logs": {}}
    summary_path, error = safe_child(root, "governance-summary.md")
    if error and check_snapshot:
        issues.append(error)
    try:
        registry = load_json(registry_path) if registry_path else None
    except (OSError, json.JSONDecodeError) as exc:
        return {"issues": [f"governance registry is not JSON-compatible YAML: {exc}"], "unverified": [], "registry": None, "logs": {}}
    if not isinstance(registry, dict):
        return {"issues": ["governance registry must be an object"], "unverified": [], "registry": None, "logs": {}}

    if registry.get("contract_id") != CONTRACT_ID or registry.get("contract_version") != CONTRACT_VERSION:
        issues.append("governance contract identity mismatch")
    identities = [registry.get("company_id"), registry.get("framework_id")]
    if sum(value is not None for value in identities) != 1:
        issues.append("exactly one company_id or framework_id is required")
    if registry.get("governance_root") != str(root):
        issues.append("governance_root does not match the approved root")
    if not isinstance(registry.get("single_editor_id"), str) or not registry.get("single_editor_id"):
        issues.append("single_editor_id is missing")

    logs: dict[str, list[dict[str, Any]]] = {}
    all_ids: set[str] = set()
    metadata: dict[str, dict[str, Any]] = {}
    for kind, (registry_key, default_name, id_field, count_key) in LOG_SPECS.items():
        current = registry.get(registry_key)
        if not isinstance(current, dict):
            issues.append(f"missing registry log metadata: {registry_key}")
            logs[kind] = []
            continue
        reference = current.get("reference", default_name)
        if reference != default_name:
            issues.append(f"unexpected log reference for {kind}: {reference}")
        log_path, path_error = safe_child(root, default_name)
        if path_error:
            issues.append(path_error)
            logs[kind] = []
            continue
        events, log_issues = read_log(log_path, id_field=id_field, kind=kind)
        issues.extend(log_issues)
        for event in events:
            event_id = event.get(id_field)
            if isinstance(event_id, str):
                if event_id in all_ids:
                    issues.append(f"duplicate event id across logs: {event_id}")
                all_ids.add(event_id)
        logs[kind] = events
        metadata[kind] = {
            "reference": default_name,
            count_key: len(events),
            "terminal_event_sha256": events[-1].get("event_sha256") if events else None,
            "file_sha256": sha256_file(log_path),
        }

    derived = derive_state(logs)
    if derived["action_count"] > 1:
        issues.append("more than one next action is active")

    current_versions = {
        item.get("skill_id"): item.get("observed_version")
        for item in registry.get("registered_skills", [])
        if isinstance(item, dict)
    }
    for event in logs.get("validation", []):
        current = current_versions.get(event.get("skill_id"))
        if current and event.get("skill_version") != current:
            issues.append("validation event version does not match current registered skill")

    latest_findings: dict[str, dict[str, Any]] = {}
    for event in logs.get("finding", []):
        if isinstance(event.get("finding_id"), str):
            latest_findings[event["finding_id"]] = event
    for finding_id, event in latest_findings.items():
        if event.get("lifecycle_state") != "verified_closed":
            continue
        for layer in event.get("required_validation_layers", []):
            matching = [
                validation
                for validation in logs.get("validation", [])
                if finding_id in validation.get("finding_ids", [])
                and validation.get("validation_layer") == layer
                and validation.get("result") in {"PASS", "NOT_APPLICABLE"}
                and validation.get("skill_id") == event.get("affected_skill_id")
                and validation.get("skill_version") == event.get("affected_skill_version")
            ]
            if not matching:
                issues.append(
                    f"verified_closed finding {finding_id} lacks a matching current-version validation event for {layer}"
                )

    parent_ref = registry.get("parent_framework_registry_reference")
    parent_hash = registry.get("parent_framework_registry_sha256")
    inherited = registry.get("inherited_finding_ids", [])
    if parent_ref is not None:
        if not parent_registry:
            unverified.append("parent framework registry was not provided")
        else:
            parent = Path(parent_registry)
            try:
                if str(parent.resolve(strict=True)) != str(Path(parent_ref).resolve(strict=True)):
                    issues.append("parent framework registry reference mismatch")
                elif sha256_file(parent) != parent_hash:
                    issues.append("parent framework registry hash mismatch")
                else:
                    parent_data = load_json(parent)
                    available = set(parent_data.get("open_finding_ids", [])) | set(
                        parent_data.get("active_blocking_finding_ids", [])
                    )
                    if not set(inherited).issubset(available):
                        issues.append("inherited finding id is absent from parent registry")
            except (OSError, json.JSONDecodeError) as exc:
                unverified.append(f"parent framework registry is unreadable: {exc}")

    if check_snapshot:
        for kind, (registry_key, _name, _id_field, _count_key) in LOG_SPECS.items():
            if registry.get(registry_key) != metadata.get(kind):
                issues.append(f"stale snapshot metadata for {kind} log")
        for key in (
            "highest_open_disposition", "active_blocking_finding_ids", "one_next_action",
            "next_action_owner", "next_authorization_required", "improvement_cycles",
        ):
            if registry.get(key) != derived.get(key):
                issues.append(f"stale derived registry field: {key}")
        if summary_path:
            summary = summary_path.read_text(encoding="utf-8")
            if not summary.startswith("# Workflow Governance Summary\n"):
                issues.append("governance summary is not a generated summary")
            if str(registry.get("registry_id")) not in summary:
                issues.append("governance summary registry identity mismatch")

    return {
        "issues": issues,
        "unverified": unverified,
        "registry": registry,
        "logs": logs,
        "metadata": metadata,
        "derived": derived,
    }


def build_registry(state: dict[str, Any]) -> dict[str, Any]:
    registry = copy.deepcopy(state["registry"])
    for kind, (registry_key, _name, _id_field, _count_key) in LOG_SPECS.items():
        registry[registry_key] = state["metadata"][kind]
    for key in (
        "highest_open_disposition", "active_blocking_finding_ids", "one_next_action",
        "next_action_owner", "next_authorization_required", "improvement_cycles",
    ):
        registry[key] = state["derived"][key]
    registry["snapshot_sequence"] = max(
        (event.get("sequence", 0) for events in state["logs"].values() for event in events),
        default=0,
    )
    registry["rebuilt_from_logs"] = True
    registry["last_rebuilt_at"] = None
    return registry


def summary_text(registry: dict[str, Any]) -> str:
    action = registry.get("one_next_action")
    return (
        "# Workflow Governance Summary\n\n"
        f"- registry_id: {registry.get('registry_id')}\n"
        f"- highest_open_disposition: {registry.get('highest_open_disposition')}\n"
        f"- open_stop_findings: {len(registry.get('active_blocking_finding_ids', []))}\n"
        f"- one_next_action: {json.dumps(action, ensure_ascii=False) if action is not None else 'null'}\n"
        "\nThis file is derived from the append-only governance logs.\n"
    )


def atomic_write_text(path: Path, text: str) -> None:
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def rebuild_files(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    registry = build_registry(state)
    registry_text = json.dumps(registry, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    atomic_write_text(root / "governance-registry.yaml", registry_text)
    atomic_write_text(root / "governance-summary.md", summary_text(registry))
    return registry


def validate_operation(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root, root_issues = resolve_root(args.governance_root)
    if root_issues or root is None:
        return json_result(FAIL, "validate", issues=root_issues, one_next_action=None)
    state = inspect_root(root, check_snapshot=True, parent_registry=args.parent_registry)
    if state["issues"]:
        return json_result(FAIL, "validate", issues=state["issues"], unverified=state["unverified"], one_next_action=None)
    if state["unverified"]:
        return json_result(UNVERIFIED, "validate", issues=[], unverified=state["unverified"], one_next_action=None)
    return json_result(
        PASS,
        "validate",
        governance_root=str(root),
        registry_sha256=sha256_file(root / "governance-registry.yaml"),
        issues=[],
        unverified=[],
        one_next_action=state["registry"].get("one_next_action"),
    )


def authorization_checks(
    root: Path, registry: dict[str, Any], args: argparse.Namespace
) -> list[str]:
    issues: list[str] = []
    actual_hash = sha256_file(root / "governance-registry.yaml")
    if args.expected_registry_sha256 != actual_hash:
        issues.append("expected registry sha256 does not match current registry")
    if args.single_editor_id != registry.get("single_editor_id"):
        issues.append("single editor identity mismatch")
    if not isinstance(args.authorization_reference, str) or not args.authorization_reference.strip():
        issues.append("authorization reference is required")
    return issues


def append_operation(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root, root_issues = resolve_root(args.governance_root)
    if root_issues or root is None:
        return json_result(FAIL, "append", issues=root_issues, event_appended=False, one_next_action=None)
    state = inspect_root(root, check_snapshot=True)
    if state["issues"]:
        return json_result(FAIL, "append", issues=state["issues"], event_appended=False, one_next_action=None)
    if state["unverified"]:
        return json_result(UNVERIFIED, "append", issues=[], unverified=state["unverified"], event_appended=False, one_next_action=None)
    issues = authorization_checks(root, state["registry"], args)
    try:
        candidate = load_json(Path(args.event_file))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(f"candidate event is unreadable: {exc}")
        candidate = None
    if not isinstance(candidate, dict):
        issues.append("candidate event must contain exactly one JSON object")
    else:
        for protected in ("sequence", "previous_event_sha256", "event_sha256"):
            if protected in candidate:
                issues.append(f"caller must not supply computed field: {protected}")
        if candidate.get("authorization_class") != AUTHORIZATION_CLASS:
            issues.append("candidate authorization class must be governance_registry_write")
        if candidate.get("user_authorization_reference") != args.authorization_reference:
            issues.append("candidate authorization reference does not match the command")
        for identity_key in ("company_id", "framework_id"):
            if candidate.get(identity_key) != state["registry"].get(identity_key):
                issues.append(f"candidate {identity_key} does not match registry")
        validate_event(candidate, args.event_kind, issues, "candidate")
    if issues:
        return json_result(FAIL, "append", issues=issues, event_appended=False, one_next_action=None)

    _registry_key, filename, id_field, _count_key = LOG_SPECS[args.event_kind]
    existing = state["logs"][args.event_kind]
    all_ids = {
        event.get(spec[2])
        for kind, events in state["logs"].items()
        for event in events
        for spec in (LOG_SPECS[kind],)
    }
    if candidate.get(id_field) in all_ids:
        return json_result(FAIL, "append", issues=["candidate event id already exists"], event_appended=False, one_next_action=None)
    event = copy.deepcopy(candidate)
    event["sequence"] = len(existing) + 1
    event["previous_event_sha256"] = existing[-1].get("event_sha256") if existing else None
    event["event_sha256"] = canonical_event_hash(event)
    encoded = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    log_path = root / filename
    old_bytes = log_path.read_bytes()
    with log_path.open("ab") as handle:
        handle.write(encoded.encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    if not log_path.read_bytes().startswith(old_bytes):
        return json_result(FAIL, "append", issues=["append-only prefix check failed"], event_appended=True, derived_files_stale=True, one_next_action="Run explicit rebuild after preserving the log.")

    post_state = inspect_root(root, check_snapshot=False)
    if post_state["issues"] or post_state["unverified"]:
        return json_result(
            FAIL,
            "append",
            issues=post_state["issues"] + post_state["unverified"],
            event_appended=True,
            derived_files_stale=True,
            event_id=event.get(id_field),
            sequence=event["sequence"],
            one_next_action="Run explicit rebuild after preserving the accepted event.",
        )
    try:
        registry = rebuild_files(root, post_state)
    except OSError as exc:
        return json_result(
            FAIL,
            "append",
            issues=[f"derived rebuild failed after append: {exc}"],
            event_appended=True,
            derived_files_stale=True,
            event_id=event.get(id_field),
            sequence=event["sequence"],
            one_next_action="Run explicit rebuild after preserving the accepted event.",
        )
    return json_result(
        PASS,
        "append",
        governance_root=str(root),
        event_appended=True,
        derived_files_stale=False,
        event_id=event.get(id_field),
        sequence=event["sequence"],
        previous_event_sha256=event["previous_event_sha256"],
        event_sha256=event["event_sha256"],
        registry_sha256_before=args.expected_registry_sha256,
        registry_sha256_after=sha256_file(root / "governance-registry.yaml"),
        one_next_action=registry.get("one_next_action"),
    )


def rebuild_operation(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    root, root_issues = resolve_root(args.governance_root)
    if root_issues or root is None:
        return json_result(FAIL, "rebuild", issues=root_issues, one_next_action=None)
    state = inspect_root(root, check_snapshot=False)
    if state["issues"]:
        return json_result(FAIL, "rebuild", issues=state["issues"], one_next_action=None)
    if state["unverified"]:
        return json_result(UNVERIFIED, "rebuild", issues=[], unverified=state["unverified"], one_next_action=None)
    issues = authorization_checks(root, state["registry"], args)
    if issues:
        return json_result(FAIL, "rebuild", issues=issues, one_next_action=None)
    before = sha256_file(root / "governance-registry.yaml")
    try:
        registry = rebuild_files(root, state)
    except OSError as exc:
        return json_result(FAIL, "rebuild", issues=[f"derived rebuild failed: {exc}"], one_next_action="Resolve the filesystem failure and retry explicit rebuild.")
    return json_result(
        PASS,
        "rebuild",
        governance_root=str(root),
        registry_sha256_before=before,
        registry_sha256_after=sha256_file(root / "governance-registry.yaml"),
        one_next_action=registry.get("one_next_action"),
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="operation", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--governance-root", required=True)
    validate.add_argument("--parent-registry")

    append = subparsers.add_parser("append")
    append.add_argument("--governance-root", required=True)
    append.add_argument("--event-kind", choices=sorted(LOG_SPECS), required=True)
    append.add_argument("--event-file", required=True)
    append.add_argument("--authorization-reference", required=True)
    append.add_argument("--single-editor-id", required=True)
    append.add_argument("--expected-registry-sha256", required=True)

    rebuild = subparsers.add_parser("rebuild")
    rebuild.add_argument("--governance-root", required=True)
    rebuild.add_argument("--authorization-reference", required=True)
    rebuild.add_argument("--single-editor-id", required=True)
    rebuild.add_argument("--expected-registry-sha256", required=True)
    return result


def main(argv: Optional[list[str]] = None) -> int:
    args = parser().parse_args(argv)
    if args.operation == "validate":
        code, payload = validate_operation(args)
    elif args.operation == "append":
        code, payload = append_operation(args)
    else:
        code, payload = rebuild_operation(args)
    sys.stdout.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
