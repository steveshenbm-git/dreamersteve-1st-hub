#!/usr/bin/env python3
from __future__ import annotations

import argparse
from functools import lru_cache
import json
from math import comb
from pathlib import Path
import random
import sys


STRATA = (
    "signal_conflict",
    "nec_or_miscellaneous",
    "source_scarce",
    "semantic_ambiguity",
    "ordinary",
)


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 1


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"line {number} is not an object")
        records.append(value)
    return records


def risk_stratum(record: dict) -> str:
    flags = record.get("risk_layer_inputs") or {}
    if flags.get("signal_conflict"):
        return "signal_conflict"
    if record.get("is_nec_or_miscellaneous_node") or flags.get("is_nec_or_miscellaneous_node"):
        return "nec_or_miscellaneous"
    if flags.get("source_scarce"):
        return "source_scarce"
    if flags.get("semantic_ambiguity"):
        return "semantic_ambiguity"
    return "ordinary"


@lru_cache(maxsize=None)
def zero_miss_upper_rate(population: int, sample: int, alpha_scaled: int) -> float:
    alpha = alpha_scaled / 1_000_000_000
    if population == 0:
        return 0.0
    if sample == 0:
        return 1.0
    denominator = comb(population, sample)

    def probability_zero(misses: int) -> float:
        available_non_misses = population - misses
        if available_non_misses < sample:
            return 0.0
        return comb(available_non_misses, sample) / denominator

    low, high = 0, population
    while low < high:
        middle = (low + high + 1) // 2
        if probability_zero(middle) >= alpha:
            low = middle
        else:
            high = middle - 1
    return low / population


def allocate_samples(populations: dict[str, int], family_alpha: float, target: float) -> tuple[dict[str, int], dict[str, float], float]:
    nonempty = [name for name in STRATA if populations.get(name, 0) > 0]
    if not nonempty:
        return {name: 0 for name in STRATA}, {name: 0.0 for name in STRATA}, 0.0
    stratum_alpha = family_alpha / len(nonempty)
    alpha_scaled = round(stratum_alpha * 1_000_000_000)
    samples = {name: 0 for name in STRATA}
    total = sum(populations.values())

    def bounds() -> dict[str, float]:
        return {
            name: zero_miss_upper_rate(populations.get(name, 0), samples[name], alpha_scaled)
            for name in STRATA
        }

    def overall(current: dict[str, float]) -> float:
        return sum((populations.get(name, 0) / total) * current[name] for name in STRATA)

    current = bounds()
    while overall(current) > target + 1e-15:
        best_name = None
        best_drop = -1.0
        for name in nonempty:
            if samples[name] >= populations[name]:
                continue
            candidate_bound = zero_miss_upper_rate(populations[name], samples[name] + 1, alpha_scaled)
            drop = (populations[name] / total) * (current[name] - candidate_bound)
            if drop > best_drop + 1e-18 or (abs(drop - best_drop) <= 1e-18 and (best_name is None or STRATA.index(name) < STRATA.index(best_name))):
                best_name = name
                best_drop = drop
        if best_name is None:
            break
        samples[best_name] += 1
        current[best_name] = zero_miss_upper_rate(populations[best_name], samples[best_name], alpha_scaled)
    return samples, current, overall(current)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a reproducible stratified reverse-audit sample.")
    parser.add_argument("--screening-records", required=True, type=Path)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--family-alpha", type=float, default=0.05)
    parser.add_argument("--target-upper-bound", type=float, default=0.05)
    parser.add_argument("--audit-results", type=Path)
    args = parser.parse_args()
    source = args.screening_records.resolve()
    output = args.output.resolve()
    if not source.is_file():
        return fail("SCREENING_RECORDS_MISSING", str(source))
    if output.exists():
        return fail("OUTPUT_EXISTS", str(output))
    if not 0 < args.family_alpha < 1 or not 0 <= args.target_upper_bound < 1:
        return fail("STATISTICAL_PARAMETER_INVALID", "alpha and target must be within their probability ranges")
    try:
        population = [record for record in read_jsonl(source) if record.get("screening_result") == "no_hypothesis_formed"]
    except (json.JSONDecodeError, ValueError) as exc:
        return fail("SCREENING_RECORDS_INVALID", str(exc))
    ids = [str(record.get("industry_node_id")) for record in population]
    if any(node_id in {"", "None"} for node_id in ids) or len(ids) != len(set(ids)):
        return fail("POPULATION_ID_INVALID", "industry_node_id must be present and unique")

    grouped: dict[str, list[dict]] = {name: [] for name in STRATA}
    assignments: list[dict] = []
    for record in sorted(population, key=lambda item: str(item["industry_node_id"])):
        name = risk_stratum(record)
        grouped[name].append(record)
        assignments.append({"industry_node_id": str(record["industry_node_id"]), "risk_stratum": name})
    populations = {name: len(grouped[name]) for name in STRATA}
    sample_sizes, upper_bounds, overall_upper = allocate_samples(populations, args.family_alpha, args.target_upper_bound)

    statistical_sample: list[dict] = []
    sampled_ids: set[str] = set()
    for name in STRATA:
        candidates = [str(record["industry_node_id"]) for record in grouped[name]]
        rng = random.Random(f"{args.seed}|{name}")
        selected = sorted(rng.sample(candidates, sample_sizes[name])) if sample_sizes[name] else []
        sampled_ids.update(selected)
        statistical_sample.extend({"industry_node_id": node_id, "risk_stratum": name} for node_id in selected)

    top_levels: dict[str, list[str]] = {}
    for record in population:
        top = str(record.get("top_level_node_id") or "unknown")
        top_levels.setdefault(top, []).append(str(record["industry_node_id"]))
    covered_top = {
        str(record.get("top_level_node_id") or "unknown")
        for record in population
        if str(record["industry_node_id"]) in sampled_ids
    }
    supplements: list[dict] = []
    for top in sorted(set(top_levels) - covered_top):
        candidates = sorted(node_id for node_id in top_levels[top] if node_id not in sampled_ids)
        if candidates:
            rng = random.Random(f"{args.seed}|coverage|{top}")
            supplements.append({"industry_node_id": rng.choice(candidates), "top_level_node_id": top})

    required_audit_ids = sampled_ids | {item["industry_node_id"] for item in supplements}
    confirmed_misses: list[str] = []
    audit_issues: list[str] = []
    audit_state = "PLANNED"
    if args.audit_results:
        try:
            audit_records = read_jsonl(args.audit_results.resolve())
            result_ids = [str(record.get("industry_node_id")) for record in audit_records]
            if any(node_id in {"", "None"} for node_id in result_ids) or len(result_ids) != len(set(result_ids)):
                audit_issues.append("audit result IDs must be present and unique")
            missing_ids = sorted(required_audit_ids - set(result_ids))
            extra_ids = sorted(set(result_ids) - required_audit_ids)
            if missing_ids:
                audit_issues.append("missing audit results:" + ",".join(missing_ids))
            if extra_ids:
                audit_issues.append("out-of-scope audit results:" + ",".join(extra_ids))
            for record in audit_records:
                node_id = str(record.get("industry_node_id"))
                result = record.get("audit_result")
                confirmed_miss = record.get("confirmed_miss")
                if result not in {"PASS", "FAIL", "UNVERIFIED"} or not isinstance(confirmed_miss, bool):
                    audit_issues.append(f"invalid audit result:{node_id}")
                    continue
                if record.get("confirmed_miss") is True:
                    confirmed_misses.append(node_id)
                    if result != "FAIL":
                        audit_issues.append(f"confirmed miss must be FAIL:{node_id}")
                elif result == "FAIL":
                    audit_issues.append(f"FAIL must declare confirmed_miss:{node_id}")
                elif result == "UNVERIFIED":
                    audit_issues.append(f"unverified audit result:{node_id}")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            return fail("AUDIT_RESULTS_INVALID", str(exc))
        if confirmed_misses:
            audit_state = "FAIL"
        elif audit_issues:
            audit_state = "INCONCLUSIVE"
        else:
            audit_state = "PASS"

    result = {
        "schema_version": "1.0",
        "sampling_method": "stratified_srswor",
        "seed": args.seed,
        "family_alpha": args.family_alpha,
        "multiple_strata_correction": "Bonferroni",
        "population_count": len(population),
        "population_assignments": assignments,
        "stratum_population_counts": populations,
        "stratum_sample_sizes": sample_sizes,
        "stratum_zero_miss_upper_bounds": upper_bounds,
        "zero_miss_overall_upper_bound": overall_upper,
        "statistical_sample": statistical_sample,
        "industry_coverage_supplement": supplements,
        "industry_coverage_supplement_in_statistical_denominator": False,
        "required_audit_node_ids": sorted(required_audit_ids),
        "confirmed_misses": sorted(set(confirmed_misses)),
        "audit_issues": audit_issues,
        "audit_state": audit_state,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    command_status = "PASS" if audit_state in {"PLANNED", "PASS"} else "FAIL"
    print(json.dumps({"status": command_status, "audit_state": audit_state, "output": str(output), "sample_count": len(statistical_sample), "upper_bound": overall_upper}, ensure_ascii=False))
    return 0 if command_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
