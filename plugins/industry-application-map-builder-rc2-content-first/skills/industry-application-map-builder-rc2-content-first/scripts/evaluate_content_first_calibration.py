#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 2


def sha256_text(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def load_arm(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    arm = payload.get("semantic_content_calibration_arm", {}) if isinstance(payload, dict) else {}
    if not isinstance(arm, dict):
        raise ValueError("semantic_content_calibration_arm is missing")
    return arm


def evidence_map(arm: dict[str, Any]) -> dict[str, dict[str, Any]] | None:
    rows = arm.get("case_evidence")
    if not isinstance(rows, list) or len(rows) != 40:
        return None
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            return None
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in result:
            return None
        if not (
            sha256_text(row.get("visible_input_sha256"))
            and sha256_text(row.get("raw_response_sha256"))
            and sha256_text(row.get("scorecard_sha256"))
            and row.get("content_score_result") == "PASS"
            and row.get("unknown_items_present") is True
        ):
            return None
        result[case_id] = row
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate paired RC2 content-first calibration evidence without using platform audit as a content gate."
    )
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--minimum-reduction", type=float, default=0.20)
    args = parser.parse_args()
    if args.output.exists():
        return fail("OUTPUT_EXISTS", str(args.output))
    if not 0 <= args.minimum_reduction < 1:
        return fail("MINIMUM_REDUCTION_INVALID", str(args.minimum_reduction))
    try:
        baseline = load_arm(args.baseline)
        candidate = load_arm(args.candidate)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail("CALIBRATION_INPUT_INVALID", str(exc))

    reasons: list[str] = []
    paired_fields = (
        "research_contract_id",
        "contract_version",
        "taxonomy_snapshot_sha256",
        "calibration_case_set_sha256",
        "source_truth_package_sha256",
    )
    paired = all(
        isinstance(baseline.get(field), str)
        and baseline.get(field)
        and baseline.get(field) == candidate.get(field)
        for field in paired_fields
    )
    baseline_evidence = evidence_map(baseline)
    candidate_evidence = evidence_map(candidate)
    evidence_ready = baseline_evidence is not None and candidate_evidence is not None
    visible_inputs_paired = (
        evidence_ready
        and set(baseline_evidence) == set(candidate_evidence)
        and all(
            baseline_evidence[case_id]["visible_input_sha256"]
            == candidate_evidence[case_id]["visible_input_sha256"]
            for case_id in baseline_evidence
        )
    )
    controls_ready = (
        baseline.get("run_complete") is True
        and candidate.get("run_complete") is True
        and baseline.get("method_arm") == "baseline_full_depth"
        and candidate.get("method_arm") == "candidate_screen_then_expand"
        and baseline.get("content_reproducible") is True
        and candidate.get("content_reproducible") is True
    )
    numeric_ready = all(
        type(value) is int and 0 <= value <= 40
        for value in (
            baseline.get("deep_expansion_count"),
            candidate.get("deep_expansion_count"),
        )
    ) and baseline.get("deep_expansion_count") == 40
    if not paired:
        state = "CONTENT_CALIBRATION_INCOMPLETE"
        reasons.append("paired content contract or frozen inputs mismatch")
    elif not evidence_ready or not visible_inputs_paired:
        state = "CONTENT_CALIBRATION_INCOMPLETE"
        reasons.append("40-case raw-answer, scorecard, unknown, or visible-input evidence is incomplete")
    elif not controls_ready or not numeric_ready:
        state = "CONTENT_CALIBRATION_INCOMPLETE"
        reasons.append("paired content-run controls or counts are incomplete")
    else:
        baseline_positives = baseline.get("known_positive_case_ids")
        candidate_positives = candidate.get("known_positive_case_ids")
        candidate_entered = candidate.get("known_positive_entered_expansion_case_ids")
        safety_failures = candidate.get("safety_failures")
        positives_ready = (
            isinstance(baseline_positives, list)
            and isinstance(candidate_positives, list)
            and isinstance(candidate_entered, list)
            and baseline_positives
            and len(set(baseline_positives)) == len(baseline_positives)
            and set(baseline_positives) == set(candidate_positives)
            and set(baseline_positives) == set(candidate_entered)
        )
        if not isinstance(safety_failures, list):
            state = "CONTENT_CALIBRATION_INCOMPLETE"
            reasons.append("safety_failures is missing or malformed")
        elif safety_failures:
            state = "CONTENT_CALIBRATION_FAIL"
            reasons.extend(str(item) for item in safety_failures)
        elif not positives_ready:
            state = "CONTENT_CALIBRATION_FAIL"
            reasons.append("known-positive content recall is below 100 percent")
        else:
            reduction = (
                (baseline["deep_expansion_count"] - candidate["deep_expansion_count"])
                / baseline["deep_expansion_count"]
            )
            if reduction + 1e-12 < args.minimum_reduction:
                state = "CONTENT_CALIBRATION_FAIL"
                reasons.append("deep expansion reduction is below the frozen threshold")
            else:
                state = "CONTENT_CALIBRATION_PASS"
    baseline_count = baseline.get("deep_expansion_count")
    candidate_count = candidate.get("deep_expansion_count")
    reduction = (
        (baseline_count - candidate_count) / baseline_count
        if isinstance(baseline_count, int) and baseline_count > 0 and isinstance(candidate_count, int)
        else None
    )
    report = {
        "schema_version": "1.0",
        "content_method_state": state,
        "critical_content_rules_applied_before_efficiency": True,
        "platform_audit_used_as_content_gate": False,
        "not_beta3_effectiveness": True,
        "research_contract_id": baseline.get("research_contract_id"),
        "contract_version": baseline.get("contract_version"),
        "taxonomy_snapshot_sha256": baseline.get("taxonomy_snapshot_sha256"),
        "calibration_case_set_sha256": baseline.get("calibration_case_set_sha256"),
        "source_truth_package_sha256": baseline.get("source_truth_package_sha256"),
        "case_count": len(baseline_evidence) if baseline_evidence is not None else None,
        "baseline_deep_expansion_count": baseline_count,
        "candidate_deep_expansion_count": candidate_count,
        "deep_expansion_reduction": reduction,
        "minimum_required_reduction": args.minimum_reduction,
        "safety_failures": candidate.get("safety_failures") if isinstance(candidate.get("safety_failures"), list) else [],
        "reasons": reasons,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS" if state == "CONTENT_CALIBRATION_PASS" else "FAIL", "content_method_state": state, "output": str(args.output)}, ensure_ascii=False))
    return 0 if state == "CONTENT_CALIBRATION_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
