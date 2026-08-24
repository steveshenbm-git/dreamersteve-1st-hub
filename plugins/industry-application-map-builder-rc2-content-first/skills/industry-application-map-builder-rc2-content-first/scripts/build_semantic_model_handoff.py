#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ALLOWED_MODES = {
    "A": {"baseline_full_depth", "screening", "evidence_expansion"},
    "B": {"blind_source_review"},
    "C": {"dispute", "reverse_audit"},
}
MODEL_RETURN_FIELDS = {
    "task_id",
    "research_contract_id",
    "contract_version",
    "input_sha256",
    "declared_model_name",
    "actual_model_id_or_unknown",
    "provider_or_unknown",
    "model_reported_run_id",
    "model_reported_started_at",
    "result_state",
    "reason_codes",
    "source_access_results",
    "structured_findings",
    "unknowns",
    "model_reported_returned_at",
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fail(code: str, detail: str) -> int:
    print(f"{code}: {detail}", file=sys.stderr)
    return 1


def nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build one self-contained semantic-model handoff packet."
    )
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.output.exists():
        return fail("DESTINATION_EXISTS", str(args.output))
    try:
        task_payload = load_json(args.task)
        visible_input = load_json(args.input)
        task = task_payload["semantic_model_task"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return fail("HANDOFF_INPUT_INVALID", str(exc))
    if not isinstance(task, dict):
        return fail("MODEL_TASK_INVALID", "semantic_model_task must be an object")

    required_structures = (
        "expected_return_schema",
        "field_ownership",
        "manual_transport_rules",
        "identity_evidence_policy",
    )
    missing = [name for name in required_structures if not isinstance(task.get(name), dict)]
    if missing:
        return fail("MODEL_TASK_INCOMPLETE", ",".join(missing))
    if task.get("transport") != "manual_external_handoff":
        return fail("MODEL_TASK_TRANSPORT_UNSUPPORTED", repr(task.get("transport")))
    role = task.get("role")
    required_text = (
        "task_id",
        "research_contract_id",
        "contract_version",
        "declared_model_name",
        "issued_at",
        "stop_condition",
    )
    incomplete = [name for name in required_text if not nonempty_text(task.get(name))]
    if role not in ALLOWED_MODES or task.get("mode") not in ALLOWED_MODES.get(role, set()):
        incomplete.append("role_or_mode")
    for name in (
        "source_references",
        "source_permissions",
        "prohibited_inputs",
        "prohibited_actions",
    ):
        if not isinstance(task.get(name), list):
            incomplete.append(name)
    expected_return = task.get("expected_return_schema", {})
    if (
        expected_return.get("schema_version") != "1.1"
        or set(expected_return.get("semantic_model_return", {})) != MODEL_RETURN_FIELDS
    ):
        incomplete.append("expected_return_schema")
    if incomplete:
        return fail("MODEL_TASK_INCOMPLETE", ",".join(sorted(set(incomplete))))

    task["visible_input"] = visible_input
    task["input_hash_algorithm"] = "sha256_canonical_json_v1"
    task["input_sha256"] = canonical_json_sha256(visible_input)
    output = {"schema_version": "1.1", "semantic_model_task": task}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
