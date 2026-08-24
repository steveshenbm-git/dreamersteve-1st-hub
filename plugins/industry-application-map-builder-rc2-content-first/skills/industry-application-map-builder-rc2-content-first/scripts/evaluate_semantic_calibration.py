#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate paired RC2 calibration arms with safety gates before efficiency.")
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
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail("CALIBRATION_INPUT_INVALID", str(exc))

    reasons: list[str] = []
    controls_ready = baseline.get("run_complete") is True and candidate.get("run_complete") is True
    paired_identity_fields = (
        "research_contract_id",
        "contract_version",
        "taxonomy_snapshot_sha256",
        "calibration_case_set_sha256",
        "model_profile_id",
    )
    case_ids = baseline.get("case_ids")
    candidate_case_ids = candidate.get("case_ids")
    identity_ready = (
        all(isinstance(baseline.get(field), str) and baseline.get(field) for field in paired_identity_fields)
        and all(baseline.get(field) == candidate.get(field) for field in paired_identity_fields)
        and isinstance(case_ids, list)
        and isinstance(candidate_case_ids, list)
        and len(case_ids) == 40
        and len(set(case_ids)) == 40
        and case_ids == candidate_case_ids
        and baseline.get("method_arm") == "baseline_full_depth"
        and candidate.get("method_arm") == "candidate_screen_then_expand"
    )
    required_numeric = all(
        type(value) is int and value >= 0
        for value in (
            baseline.get("deep_expansion_count"),
            baseline.get("known_positive_count"),
            candidate.get("deep_expansion_count"),
            candidate.get("known_positive_count"),
            candidate.get("known_positive_entered_expansion"),
        )
    )
    counts_ready = (
        required_numeric
        and baseline.get("deep_expansion_count") == 40
        and 0 < baseline.get("known_positive_count", 0) <= 40
        and 0 <= candidate.get("deep_expansion_count", 41) <= 40
        and 0 < candidate.get("known_positive_count", 0) <= 40
        and 0 <= candidate.get("known_positive_entered_expansion", 41) <= candidate.get("known_positive_count", 0)
    )
    if not identity_ready:
        state = "INCONCLUSIVE"
        reasons.append("paired calibration identity mismatch")
    elif not controls_ready or not counts_ready:
        state = "INCONCLUSIVE"
        reasons.append("paired run controls or required counts are incomplete")
    else:
        safety_failures = candidate.get("safety_failures")
        if not isinstance(safety_failures, list):
            state = "INCONCLUSIVE"
            reasons.append("safety_failures is missing or malformed")
        else:
            positive_recall_ok = (
                candidate["known_positive_count"] == baseline["known_positive_count"]
                and candidate["known_positive_entered_expansion"] == candidate["known_positive_count"]
            )
            baseline_count = baseline["deep_expansion_count"]
            reduction = None if baseline_count == 0 else (baseline_count - candidate["deep_expansion_count"]) / baseline_count
            if safety_failures:
                state = "NOT_EFFECTIVE"
                reasons.extend(str(item) for item in safety_failures)
            elif not positive_recall_ok:
                state = "NOT_EFFECTIVE"
                reasons.append("known positive recall is below 100 percent")
            elif candidate.get("reproducible") is not True:
                state = "NOT_EFFECTIVE"
                reasons.append("candidate run is not reproducible")
            elif reduction is None:
                state = "INCONCLUSIVE"
                reasons.append("baseline deep expansion count is zero")
            elif reduction + 1e-12 < args.minimum_reduction:
                state = "NOT_EFFECTIVE"
                reasons.append("deep expansion reduction is below the frozen threshold")
            else:
                state = "EFFECTIVE"
    baseline_count = baseline.get("deep_expansion_count")
    candidate_count = candidate.get("deep_expansion_count")
    reduction = (
        (baseline_count - candidate_count) / baseline_count
        if isinstance(baseline_count, int) and baseline_count > 0 and isinstance(candidate_count, int)
        else None
    )
    report = {
        "schema_version": "1.0",
        "method_validation_state": state,
        "critical_rules_applied_before_efficiency": True,
        "baseline_deep_expansion_count": baseline_count,
        "candidate_deep_expansion_count": candidate_count,
        "deep_expansion_reduction": reduction,
        "minimum_required_reduction": args.minimum_reduction,
        "paired_identity_verified": identity_ready,
        "research_contract_id": baseline.get("research_contract_id"),
        "contract_version": baseline.get("contract_version"),
        "calibration_case_set_sha256": baseline.get("calibration_case_set_sha256"),
        "case_count": len(case_ids) if isinstance(case_ids, list) else None,
        "reasons": reasons,
        "does_not_prove_population_miss_rate": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS" if state == "EFFECTIVE" else "FAIL", "method_validation_state": state, "output": str(args.output)}, ensure_ascii=False))
    return 0 if state == "EFFECTIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
