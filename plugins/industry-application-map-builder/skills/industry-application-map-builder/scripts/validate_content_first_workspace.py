#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ARMS = {"baseline_full_depth", "candidate_screen_then_expand"}
PLATFORM_AUDIT_STATES = {"PASS", "FAIL", "UNVERIFIED", "NOT_COLLECTED"}
SCORE_ITEMS = {
    "scope_taxonomy_grounding",
    "three_axis_handling",
    "source_truth_alignment",
    "safety_boundary",
    "unknown_disclosure",
}
PRIVATE_INPUT_KEYS = {
    "company_id",
    "company_name",
    "company_product",
    "product_fact_id",
    "route_id",
    "customer_id",
}


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


def contains_private_input(value: Any) -> bool:
    if isinstance(value, dict):
        return any(key in PRIVATE_INPUT_KEYS or contains_private_input(item) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_private_input(item) for item in value)
    return False


def add(errors: list[dict[str, str]], code: str, detail: str) -> None:
    errors.append({"code": code, "detail": detail})


def score_result(items: dict[str, Any]) -> str:
    if any(items[name]["critical"] and items[name]["score"] == 0 for name in SCORE_ITEMS):
        return "FAIL"
    if all(items[name]["score"] == 2 for name in SCORE_ITEMS):
        return "PASS"
    return "UNVERIFIED"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate append-only RC2 content-first raw-answer and scorecard evidence."
    )
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    errors: list[dict[str, str]] = []
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
    if not envelopes:
        add(errors, "RAW_ENVELOPE_MISSING", str(raw_root))

    expected_scorecards: dict[Path, dict[str, Any]] = {}
    for envelope_path, body in envelopes.items():
        subject = body.get("subject")
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
            "source_truth_comparison_reference",
            "source_truth_comparison_sha256",
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
            and body.get("method_arm") in ARMS
            and body.get("visible_input") is not None
            and body.get("visible_input_sha256") == canonical_sha256(body.get("visible_input"))
            and body.get("platform_audit_state") in PLATFORM_AUDIT_STATES
        ):
            add(errors, "RAW_ENVELOPE_SEMANTICS_INVALID", str(envelope_path))
        if contains_private_input(body.get("visible_input")):
            add(errors, "CROSS_COMPANY_INPUT_FORBIDDEN", str(envelope_path))
        raw_path = resolve_inside(workspace, body.get("raw_response_reference"))
        if raw_path is None or not raw_path.is_file():
            add(errors, "RAW_RESPONSE_MISSING", str(envelope_path))
        elif not is_sha256(body.get("raw_response_sha256")) or sha256_file(raw_path) != body.get(
            "raw_response_sha256"
        ):
            add(errors, "RAW_RESPONSE_HASH_MISMATCH", str(envelope_path))
        source_path = resolve_inside(workspace, body.get("source_truth_comparison_reference"))
        if source_path is None or not source_path.is_file():
            add(errors, "SOURCE_TRUTH_COMPARISON_MISSING", str(envelope_path))
        elif source_path.stat().st_size == 0:
            add(errors, "SOURCE_TRUTH_COMPARISON_EMPTY", str(envelope_path))
        elif not is_sha256(body.get("source_truth_comparison_sha256")) or sha256_file(source_path) != body.get(
            "source_truth_comparison_sha256"
        ):
            add(errors, "SOURCE_TRUTH_COMPARISON_HASH_MISMATCH", str(envelope_path))
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
            body = payload.get("semantic_content_scorecard", {}) if isinstance(payload, dict) else {}
            if body:
                scorecards[path.resolve()] = body
    if not scorecards:
        add(errors, "SCORECARD_MISSING", str(score_root))

    matched_envelopes: set[Path] = set()
    for score_path, body in scorecards.items():
        envelope_path = resolve_inside(workspace, body.get("raw_answer_reference"))
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
        items = body.get("scoring_items")
        items_valid = isinstance(items, dict) and set(items) == SCORE_ITEMS
        if items_valid:
            for name in SCORE_ITEMS:
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
        expected_result = score_result(items)
        if body.get("content_score_result") != expected_result:
            add(errors, "SCORECARD_RESULT_INVALID", str(score_path))
        if expected_result != "PASS":
            add(errors, "CONTENT_SCORE_NOT_PASS", str(score_path))
        if body.get("scorecard_sha256") != canonical_sha256({**body, "scorecard_sha256": None}):
            add(errors, "SCORECARD_HASH_MISMATCH", str(score_path))
    for envelope_path in expected_scorecards:
        if envelope_path not in matched_envelopes:
            add(errors, "SCORECARD_FOR_RAW_ENVELOPE_MISSING", str(envelope_path))

    report = {"status": "FAIL" if errors else "PASS", "workspace": str(workspace), "errors": errors}
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(report["status"])
        for error in errors:
            print(f"{error['code']}: {error['detail']}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
