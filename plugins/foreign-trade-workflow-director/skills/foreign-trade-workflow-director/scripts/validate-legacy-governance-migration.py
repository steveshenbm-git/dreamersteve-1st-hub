#!/usr/bin/env python3
"""Read-only validator for bounded legacy governance migration batches."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Optional


PASS = 0
FAIL = 2
UNVERIFIED = 3
MIGRATION_CONTRACT_ID = "FTWG-LEGACY-GOVERNANCE-MIGRATION"
MIGRATION_CONTRACT_VERSION = "1.0.0-draft.2"
AUTHORIZATION_CLASS = "governance_registry_write"
PHASES = ("inventory", "mapping", "dry-run", "activation-preflight", "post-activation")
SOURCE_ROLES = {
    "authoritative_history", "supporting_evidence", "context_only", "generated_view",
}
GOVERNANCE_SCOPES = {"framework", "company", "task"}
MAPPING_DECISIONS = {
    "create_new_finding", "link_existing_finding", "create_or_link_improvement",
    "context_only", "duplicate_excluded", "invalid_excluded", "unresolved_conflict",
}
CANDIDATE_LOGS = {
    "finding": "migrated-finding-events.jsonl",
    "improvement": "migrated-improvement-events.jsonl",
    "validation": "migrated-validation-events.jsonl",
    "evidence": "migrated-evidence-events.jsonl",
}
TARGET_LOGS = {
    "finding": "findings.jsonl",
    "improvement": "improvement-events.jsonl",
    "validation": "validation-events.jsonl",
    "evidence": "evidence-index.jsonl",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_event_hash(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "event_sha256"}
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def result_payload(
    code: int,
    phase: str,
    *,
    issues: list[str],
    unverified: list[str],
    actual_counts: Optional[dict[str, int]] = None,
    missing_source_ids: Optional[list[str]] = None,
    undeclared_paths: Optional[list[str]] = None,
    mapping_closure: Optional[dict[str, int]] = None,
    one_next_action: Optional[str] = None,
) -> tuple[int, dict[str, Any]]:
    state = "PASS" if code == PASS else "UNVERIFIED" if code == UNVERIFIED else "FAIL"
    return code, {
        "result": state,
        "phase": phase,
        "issues": issues,
        "unverified": unverified,
        "actual_counts": actual_counts or {
            "discovered": 0, "included": 0, "excluded": 0, "duplicate": 0, "failed": 0,
        },
        "missing_source_ids": missing_source_ids or [],
        "undeclared_paths": undeclared_paths or [],
        "mapping_closure": mapping_closure or {"eligible_records": 0, "mapped_records": 0},
        "one_next_action": one_next_action,
    }


def finish(
    phase: str,
    issues: list[str],
    unverified: list[str],
    **fields: Any,
) -> tuple[int, dict[str, Any]]:
    if issues:
        action = "Correct the reported migration contract failures in a new or still-unfrozen batch."
        return result_payload(FAIL, phase, issues=issues, unverified=unverified, one_next_action=action, **fields)
    if unverified:
        action = "Provide the missing evidence or authorization without changing historical sources."
        return result_payload(UNVERIFIED, phase, issues=[], unverified=unverified, one_next_action=action, **fields)
    return result_payload(PASS, phase, issues=[], unverified=[], one_next_action=None, **fields)


def safe_existing_root(value: str, label: str) -> tuple[Optional[Path], list[str]]:
    path = Path(value)
    if not path.exists():
        return None, [f"{label} does not exist"]
    if path.is_symlink():
        return None, [f"{label} must not be a symlink"]
    if not path.is_dir():
        return None, [f"{label} is not a directory"]
    return path.resolve(), []


def safe_file(root: Path, name: str) -> tuple[Optional[Path], Optional[str]]:
    if Path(name).name != name:
        return None, f"unsafe batch file reference: {name}"
    path = root / name
    if path.is_symlink():
        return None, f"symlink batch file is prohibited: {name}"
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError:
        return None, f"required batch file is missing: {name}"
    if resolved.parent != root or not resolved.is_file():
        return None, f"batch file escapes authorized batch root: {name}"
    return resolved, None


def matches_any(relative: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(relative, pattern) for pattern in patterns)


def path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def discover_sources(manifest: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    unverified: list[str] = []
    include_patterns = manifest.get("include_patterns")
    exclude_patterns = manifest.get("exclude_patterns")
    if not isinstance(include_patterns, list) or not include_patterns:
        issues.append("include patterns are not frozen")
        include_patterns = []
    if not isinstance(exclude_patterns, list):
        issues.append("exclude patterns are not frozen")
        exclude_patterns = []
    if manifest.get("follow_symlinks") is not False:
        issues.append("follow_symlinks must be false")

    roots: dict[str, Path] = {}
    for entry in manifest.get("discovery_roots", []):
        if not isinstance(entry, dict) or not entry.get("root_id") or not entry.get("path"):
            issues.append("invalid discovery root entry")
            continue
        root_id = entry["root_id"]
        if root_id in roots:
            issues.append(f"duplicate discovery root id: {root_id}")
            continue
        root, root_issues = safe_existing_root(entry["path"], f"discovery root {root_id}")
        issues.extend(root_issues)
        if root:
            roots[root_id] = root
    if not roots:
        issues.append("no authorized discovery roots are available")

    exclude_roots: list[Path] = []
    for raw in manifest.get("exclude_roots", []):
        try:
            candidate = Path(raw).resolve(strict=True)
        except (OSError, TypeError):
            unverified.append(f"excluded root is unreadable: {raw}")
            continue
        if not any(path_within(candidate, root) for root in roots.values()):
            issues.append(f"excluded root is outside authorized discovery roots: {candidate}")
        else:
            exclude_roots.append(candidate)

    included: dict[tuple[str, str], Path] = {}
    discovered_paths: dict[tuple[str, str], Path] = {}
    excluded: set[tuple[str, str]] = set()
    duplicate: set[tuple[str, str]] = set()
    failed: set[tuple[str, str]] = set()
    seen_hashes: dict[str, tuple[str, str]] = {}
    discovered = 0
    for root_id, root in roots.items():
        for directory, dirnames, filenames in os.walk(root, followlinks=False):
            current = Path(directory)
            kept_dirs = []
            for dirname in dirnames:
                child = current / dirname
                relative = child.relative_to(root).as_posix()
                if child.is_symlink():
                    issues.append(f"symlink escape candidate is prohibited: {root_id}:{relative}")
                    continue
                resolved = child.resolve()
                if any(path_within(resolved, excluded_root) for excluded_root in exclude_roots):
                    continue
                kept_dirs.append(dirname)
            dirnames[:] = kept_dirs
            for filename in filenames:
                path = current / filename
                relative = path.relative_to(root).as_posix()
                if path.is_symlink():
                    issues.append(f"symlink escape candidate is prohibited: {root_id}:{relative}")
                    continue
                if not matches_any(relative, include_patterns):
                    continue
                discovered += 1
                key = (root_id, relative)
                discovered_paths[key] = path.resolve()
                resolved = path.resolve()
                if not path_within(resolved, root):
                    issues.append(f"discovered file escaped authorized root: {root_id}:{relative}")
                    failed.add(key)
                    continue
                if any(path_within(resolved, excluded_root) for excluded_root in exclude_roots) or matches_any(relative, exclude_patterns):
                    excluded.add(key)
                    continue
                try:
                    digest = sha256_file(resolved)
                except OSError as exc:
                    issues.append(f"failed to read discovered file {root_id}:{relative}: {exc}")
                    failed.add(key)
                    continue
                if digest in seen_hashes:
                    duplicate.add(key)
                    continue
                seen_hashes[digest] = key
                included[key] = resolved

    counts = {
        "discovered": discovered,
        "included": len(included),
        "excluded": len(excluded),
        "duplicate": len(duplicate),
        "failed": len(failed),
    }
    if counts["included"] + counts["excluded"] + counts["duplicate"] + counts["failed"] != counts["discovered"]:
        issues.append("actual discovery counts do not close")
    expected = manifest.get("expected_counts")
    if expected != counts:
        issues.append(f"expected counts do not match actual discovery counts: expected={expected} actual={counts}")

    declared_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    source_ids: set[str] = set()
    invalid_declared_ids: list[str] = []
    for source in manifest.get("declared_sources", []):
        if not isinstance(source, dict):
            issues.append("declared source must be an object")
            continue
        source_id = source.get("source_id")
        root_id = source.get("root_id")
        relative = source.get("relative_path")
        if not isinstance(source_id, str) or not source_id:
            issues.append("declared source is missing source_id")
            continue
        if source_id in source_ids:
            issues.append(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        if root_id not in roots or not isinstance(relative, str):
            issues.append(f"declared source {source_id} has an unknown root or path")
            invalid_declared_ids.append(source_id)
            continue
        candidate = roots[root_id] / relative
        lexical_resolved = candidate.resolve()
        if not path_within(lexical_resolved, roots[root_id]):
            issues.append(f"declared source {source_id} is outside authorized discovery root")
            invalid_declared_ids.append(source_id)
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            issues.append(f"declared source {source_id} is unreadable")
            invalid_declared_ids.append(source_id)
            continue
        key = (root_id, Path(relative).as_posix())
        if key in declared_by_key:
            issues.append(f"multiple declarations for source path {root_id}:{relative}")
        declared_by_key[key] = source
        if source.get("source_role") not in SOURCE_ROLES:
            issues.append(f"declared source {source_id} has invalid source role")
        if source.get("governance_scope") not in GOVERNANCE_SCOPES:
            issues.append(f"declared source {source_id} has invalid governance scope")
        if source.get("sha256") != sha256_file(resolved):
            issues.append(f"declared source hash mismatch: {source_id}")
        if source.get("byte_count") != resolved.stat().st_size:
            issues.append(f"declared source byte count mismatch: {source_id}")
        if not isinstance(source.get("record_count"), int) or source.get("record_count", 0) < 0:
            issues.append(f"declared source record count is invalid: {source_id}")
        if key in included and source.get("migration_eligible") is not True:
            issues.append(f"included source must be migration eligible: {source_id}")
        if key in excluded | duplicate:
            if source.get("migration_eligible") is not False:
                issues.append(f"excluded or duplicate source must not be migration eligible: {source_id}")
            if not source.get("exclusion_reason"):
                issues.append(f"excluded or duplicate source lacks exclusion reason: {source_id}")

    actual_keys = set(discovered_paths)
    declared_keys = set(declared_by_key)
    undeclared = sorted(f"{root_id}:{relative}" for root_id, relative in actual_keys - declared_keys)
    missing_ids = sorted(
        [declared_by_key[key].get("source_id") for key in declared_keys - actual_keys]
        + invalid_declared_ids
    )
    for path in undeclared:
        issues.append(f"eligible discovered file omitted from manifest: {path}")
    for source_id in missing_ids:
        issues.append(f"declared source is not an included eligible file: {source_id}")

    return {
        "issues": issues,
        "unverified": unverified,
        "roots": roots,
        "included": included,
        "discovered_paths": discovered_paths,
        "declared_by_key": declared_by_key,
        "counts": counts,
        "missing_source_ids": missing_ids,
        "undeclared_paths": undeclared,
    }


def read_mapping(batch: Path, manifest: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    issues: list[str] = []
    path, error = safe_file(batch, "legacy-finding-mapping.jsonl")
    if error or path is None:
        return {"issues": [error or "mapping file is missing"], "records": [], "closure": {"eligible_records": 0, "mapped_records": 0}}
    records: list[dict[str, Any]] = []
    seen_mapping_ids: set[str] = set()
    seen_locators: set[tuple[str, str]] = set()
    manifest_sha = sha256_file(manifest_path)
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            issues.append(f"mapping line {line_number} is invalid JSON: {exc.msg}")
            continue
        if not isinstance(record, dict):
            issues.append(f"mapping line {line_number} must be an object")
            continue
        if record.get("template_record") is not False:
            issues.append(f"mapping line {line_number} is still a template")
        mapping_id = record.get("mapping_id")
        if not mapping_id or mapping_id in seen_mapping_ids:
            issues.append(f"duplicate mapping id or missing mapping id at line {line_number}")
        else:
            seen_mapping_ids.add(mapping_id)
        locator = (record.get("source_id"), record.get("source_record_locator"))
        if locator in seen_locators:
            issues.append(f"duplicate mapping for source record {locator}")
        else:
            seen_locators.add(locator)
        if record.get("source_manifest_sha256") != manifest_sha:
            issues.append(f"mapping line {line_number} source manifest sha256 mismatch")
        decision = record.get("mapping_decision")
        if decision not in MAPPING_DECISIONS:
            issues.append(f"mapping line {line_number} has invalid mapping decision")
        if decision == "unresolved_conflict":
            issues.append(f"mapping line {line_number} has an unresolved conflict")
        if decision in {"link_existing_finding", "duplicate_excluded"} and not record.get("canonical_target_id"):
            issues.append(f"mapping line {line_number} lacks a canonical target")
        if record.get("requires_revalidation") is not True:
            issues.append(f"mapping line {line_number} must require revalidation")
        if not record.get("reviewed_by") or not record.get("authorization_reference"):
            issues.append(f"mapping line {line_number} lacks review or authorization reference")
        records.append(record)

    eligible_counts = {
        source.get("source_id"): source.get("record_count", 0)
        for source in manifest.get("declared_sources", [])
        if isinstance(source, dict) and source.get("migration_eligible") is True
    }
    mapped_by_source: dict[str, int] = {}
    for record in records:
        source_id = record.get("source_id")
        mapped_by_source[source_id] = mapped_by_source.get(source_id, 0) + 1
        if source_id not in eligible_counts:
            issues.append(f"mapping references an undeclared or ineligible source: {source_id}")
    for source_id, count in eligible_counts.items():
        if mapped_by_source.get(source_id, 0) != count:
            issues.append(
                f"source record mapping closure failed for {source_id}: expected {count}, got {mapped_by_source.get(source_id, 0)}"
            )
    closure = {
        "eligible_records": sum(eligible_counts.values()),
        "mapped_records": sum(mapped_by_source.get(source_id, 0) for source_id in eligible_counts),
    }
    return {"issues": issues, "records": records, "closure": closure, "path": path}


def validate_candidate_package(
    batch: Path, manifest: dict[str, Any], manifest_path: Path, mapping: dict[str, Any], target: Path
) -> list[str]:
    issues: list[str] = []
    target_registry = target / "governance-registry.yaml"
    if not target_registry.is_file() or target_registry.is_symlink():
        issues.append("target governance registry is missing or unsafe")
    elif manifest.get("target_registry_sha256") != sha256_file(target_registry):
        issues.append("target registry hash changed after the manifest was frozen")

    counts: dict[str, int] = {}
    mapping_ids = {record.get("mapping_id") for record in mapping["records"]}
    for kind, filename in CANDIDATE_LOGS.items():
        path, error = safe_file(batch, filename)
        if error or path is None:
            issues.append(error or f"missing candidate {kind} log")
            counts[kind] = 0
            continue
        count = 0
        expected_previous = None
        seen_ids: set[str] = set()
        id_field = {
            "finding": "event_id",
            "improvement": "improvement_event_id",
            "validation": "validation_event_id",
            "evidence": "evidence_event_id",
        }[kind]
        for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                issues.append(f"{filename}:{line_number}: invalid JSON: {exc.msg}")
                continue
            count += 1
            if not isinstance(event, dict) or event.get("template_record") is True:
                issues.append(f"{filename}:{line_number}: template or invalid candidate event")
                continue
            event_id = event.get(id_field)
            if not isinstance(event_id, str) or not event_id or event_id in seen_ids:
                issues.append(f"{filename}:{line_number}: missing or duplicate candidate event id")
            else:
                seen_ids.add(event_id)
            if event.get("sequence") != line_number:
                issues.append(f"{filename}:{line_number}: candidate event sequence mismatch")
            if event.get("previous_event_sha256") != expected_previous:
                issues.append(f"{filename}:{line_number}: candidate previous event hash mismatch")
            actual_event_hash = canonical_event_hash(event)
            if event.get("event_sha256") != actual_event_hash:
                issues.append(f"{filename}:{line_number}: candidate event hash mismatch")
            expected_previous = event.get("event_sha256")
            provenance = event.get("migration_provenance")
            if not isinstance(provenance, dict) or provenance.get("migration_batch_id") != manifest.get("migration_batch_id"):
                issues.append(f"{filename}:{line_number}: missing migration provenance")
            elif not set(provenance.get("mapping_ids", [])).issubset(mapping_ids):
                issues.append(f"{filename}:{line_number}: provenance references an unknown mapping")
            if event.get("lifecycle_state") == "verified_closed":
                issues.append(f"{filename}:{line_number}: historical verified_closed promotion is prohibited")
            if event.get("to_state") == "accepted_effective":
                issues.append(f"{filename}:{line_number}: historical accepted_effective promotion is prohibited")
            if any(key in event for key in ("rewrite_source", "relocate_source", "delete_source")):
                issues.append(f"{filename}:{line_number}: historical source mutation is prohibited")
        counts[kind] = count

    report_path, error = safe_file(batch, "migration-validation-report.json")
    if error or report_path is None:
        issues.append(error or "migration validation report is missing")
        return issues
    try:
        report = load_json(report_path)
    except json.JSONDecodeError as exc:
        issues.append(f"migration validation report is invalid JSON: {exc.msg}")
        return issues
    if report.get("template_record") is not False or report.get("result") != "PASS":
        issues.append("migration validation report is not a real PASS report")
    if report.get("migration_batch_id") != manifest.get("migration_batch_id"):
        issues.append("migration validation report batch id mismatch")
    if report.get("manifest_sha256") != sha256_file(manifest_path):
        issues.append("migration validation report manifest hash mismatch")
    if report.get("mapping_sha256") != sha256_file(mapping["path"]):
        issues.append("migration validation report mapping hash mismatch")
    if report.get("target_registry_sha256") != manifest.get("target_registry_sha256"):
        issues.append("migration validation report target hash mismatch")
    if report.get("candidate_event_counts") != counts:
        issues.append("migration validation report candidate event counts do not close")
    return issues


def validate_receipt(batch: Path, target: Path, manifest: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    receipt_path, error = safe_file(batch, "migration-activation-receipt.json")
    if error or receipt_path is None:
        return [error or "activation receipt is missing"]
    try:
        receipt = load_json(receipt_path)
    except json.JSONDecodeError as exc:
        return [f"activation receipt is invalid JSON: {exc.msg}"]
    required = (
        "schema_version", "migration_batch_id", "migration_contract_id",
        "migration_contract_version", "target_registry_id", "authorization_class",
        "user_authorization_reference", "single_editor_id", "target_before", "target_after",
        "appended_counts", "post_activation_rebuild_result", "activation_state",
    )
    missing = [field for field in required if field not in receipt]
    if missing:
        issues.append(f"activation receipt is incomplete: {missing}")
        return issues
    if receipt.get("migration_batch_id") != manifest.get("migration_batch_id"):
        issues.append("activation receipt batch id mismatch")
    if receipt.get("migration_contract_id") != MIGRATION_CONTRACT_ID:
        issues.append("activation receipt contract id mismatch")
    if receipt.get("authorization_class") != AUTHORIZATION_CLASS or not receipt.get("user_authorization_reference"):
        issues.append("activation receipt lacks governance_registry_write authorization")
    if receipt.get("activation_state") != "ACTIVE" or receipt.get("post_activation_rebuild_result") != "PASS":
        issues.append("activation receipt does not prove active rebuilt state")
    try:
        registry = load_json(target / "governance-registry.yaml")
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(f"target registry is unreadable after activation: {exc}")
        return issues
    if registry.get("registry_id") != receipt.get("target_registry_id"):
        issues.append("activation receipt target registry id mismatch")
    after = receipt.get("target_after", {})
    if after.get("registry_sha256") != sha256_file(target / "governance-registry.yaml"):
        issues.append("append-only target hash mismatch for governance registry")
    hash_fields = {
        "finding": "findings_file_sha256",
        "improvement": "improvements_file_sha256",
        "validation": "validations_file_sha256",
        "evidence": "evidence_file_sha256",
    }
    count_fields = {
        "finding": "finding_events",
        "improvement": "improvement_events",
        "validation": "validation_events",
        "evidence": "evidence_events",
    }
    appended = receipt.get("appended_counts", {})
    for kind, filename in TARGET_LOGS.items():
        path = target / filename
        if not path.is_file() or path.is_symlink():
            issues.append(f"append-only target log is missing or unsafe: {filename}")
            continue
        if after.get(hash_fields[kind]) != sha256_file(path):
            issues.append(f"append-only target hash mismatch for {filename}")
        candidate_path = batch / CANDIDATE_LOGS[kind]
        candidate_lines = candidate_path.read_text(encoding="utf-8").splitlines()
        expected_appended = len(candidate_lines)
        if appended.get(count_fields[kind]) != expected_appended:
            issues.append(f"activation receipt appended count mismatch for {filename}")
        if expected_appended:
            target_lines = path.read_text(encoding="utf-8").splitlines()
            if len(target_lines) < expected_appended or target_lines[-expected_appended:] != candidate_lines:
                issues.append(f"append-only target tail does not match candidate events for {filename}")
    return issues


def validate(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    batch, issues = safe_existing_root(args.batch_root, "batch root")
    target, target_issues = safe_existing_root(args.target_governance_root, "target governance root")
    issues.extend(target_issues)
    if batch is None or target is None:
        return finish(args.phase, issues, [])
    manifest_path, error = safe_file(batch, "legacy-governance-source-manifest.yaml")
    if error or manifest_path is None:
        return finish(args.phase, [error or "source manifest is missing"], [])
    try:
        manifest = load_json(manifest_path)
    except json.JSONDecodeError as exc:
        return finish(args.phase, [f"source manifest is not JSON-compatible YAML: {exc.msg}"], [])
    if not isinstance(manifest, dict):
        return finish(args.phase, ["source manifest must be an object"], [])
    if manifest.get("template_record") is not False:
        issues.append("source manifest is still a template")
    if manifest.get("migration_contract_id") != MIGRATION_CONTRACT_ID or manifest.get("migration_contract_version") != MIGRATION_CONTRACT_VERSION:
        issues.append("migration contract identity mismatch")
    if manifest.get("target_governance_root") != str(target):
        issues.append("target governance root does not match the frozen manifest")
    if not manifest.get("inventory_frozen_at"):
        issues.append("inventory freeze time is missing")

    inventory = discover_sources(manifest)
    issues.extend(inventory["issues"])
    unverified = list(inventory["unverified"])
    common = {
        "actual_counts": inventory["counts"],
        "missing_source_ids": inventory["missing_source_ids"],
        "undeclared_paths": inventory["undeclared_paths"],
    }
    if args.phase == "inventory":
        return finish(args.phase, issues, unverified, **common)

    mapping = read_mapping(batch, manifest, manifest_path)
    issues.extend(mapping["issues"])
    common["mapping_closure"] = mapping["closure"]
    if args.phase == "mapping":
        return finish(args.phase, issues, unverified, **common)

    if args.phase in {"dry-run", "activation-preflight"}:
        issues.extend(validate_candidate_package(batch, manifest, manifest_path, mapping, target))
        if args.phase == "activation-preflight" and not issues:
            authorization = manifest.get("activation_authorization")
            if not isinstance(authorization, dict):
                unverified.append("governance_registry_write authorization is missing")
            else:
                if authorization.get("authorization_class") != AUTHORIZATION_CLASS:
                    issues.append("activation authorization class is invalid")
                if not authorization.get("user_authorization_reference"):
                    unverified.append("governance_registry_write authorization reference is missing")
                try:
                    target_registry = load_json(target / "governance-registry.yaml")
                except (OSError, json.JSONDecodeError) as exc:
                    issues.append(f"target registry cannot confirm single editor: {exc}")
                    target_registry = {}
                if authorization.get("single_editor_id") != target_registry.get("single_editor_id"):
                    issues.append("activation single editor identity mismatch")
                report = load_json(batch / "migration-validation-report.json")
                if report.get("activation_authorized") is not True or report.get("authorization_reference") != authorization.get("user_authorization_reference"):
                    issues.append("migration report is not bound to the activation authorization")
        return finish(args.phase, issues, unverified, **common)

    issues.extend(validate_receipt(batch, target, manifest))
    return finish(args.phase, issues, unverified, **common)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--batch-root", required=True)
    result.add_argument("--target-governance-root", required=True)
    result.add_argument("--phase", choices=PHASES, required=True)
    return result


def main(argv: Optional[list[str]] = None) -> int:
    args = parser().parse_args(argv)
    code, payload = validate(args)
    sys.stdout.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
