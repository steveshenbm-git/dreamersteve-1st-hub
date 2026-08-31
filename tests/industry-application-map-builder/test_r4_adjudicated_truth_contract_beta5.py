from __future__ import annotations

import json
import os
import re
import sys
import unittest
from pathlib import Path


DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = Path(
    os.environ.get("R4_CONTRACT_REPOSITORY_ROOT", DEFAULT_REPOSITORY_ROOT)
)
SCRIPT_ROOT = (
    REPOSITORY_ROOT
    / "plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts"
)
CALIBRATION_REFERENCE = (
    REPOSITORY_ROOT
    / "plugins/industry-application-map-builder/skills/industry-application-map-builder/references/industry-semantic-calibration-and-audit.md"
)
sys.path.insert(0, str(SCRIPT_ROOT))

from r4_adjudicated_truth_contract import (  # noqa: E402
    BETA5_CASE_PACKAGE_CONTRACT_VERSION,
    MAP_BUILDER_PLUGIN_VERSION,
    BETA5_TRUTH_CONTRACT_VERSION,
    BETA5_TRUTH_SCORECARD_CONTRACT_VERSION,
    DIRECTOR_PLUGIN_VERSION,
    SAMPLING_CATEGORY_COUNTS,
    SELECTION_ORIGIN_COUNTS,
    derive_truth_summary,
    validate_adjudicated_truth_rows,
    validate_beta5_case_rows,
    validate_positive_holdout_floor,
    validate_truth_summary_integrity,
)


def case_rows() -> list[dict]:
    categories = [
        category
        for category, count in SAMPLING_CATEGORY_COUNTS.items()
        for _ in range(count)
    ]
    rows = []
    for index, category in enumerate(categories, 1):
        rows.append(
            {
                "record_type": "calibration_case",
                "case_id": f"R4-CASE-{index:03d}",
                "research_contract_id": "R4-BETA5-TEST",
                "sampling_category": category,
                "provenance": {
                    "development_regression_only": False,
                    "selection_origin": (
                        "new_unseen" if index <= 10 else "retained_r3_unexecuted"
                    ),
                },
            }
        )
    return rows


def truth_rows(positive_count: int = 15) -> list[dict]:
    rows = []
    for index in range(1, 41):
        positive = index <= positive_count
        row = {
            "record_type": "source_truth",
            "truth_contract_version": BETA5_TRUTH_CONTRACT_VERSION,
            "research_contract_id": "R4-BETA5-TEST",
            "preparation_contract_version": "R4-BETA5.prep.1",
            "locked_input_sha256": "a" * 64,
            "case_id": f"R4-CASE-{index:03d}",
            "truth_disposition": "positive_confirmed" if positive else "negative_confirmed",
            "evidence_state": "supported",
            "evidence_quality": "direct_complete",
            "adjudication_state": "accepted",
            "adjudication_version": "R4-TRUTH-ADJ-001",
            "counterevidence": [],
            "reopen_reason": None,
            "supersedes_truth_sha256": None,
            "evidence_bases": {},
            "conditions": [],
            "limitations": [],
            "unknowns": [],
            "exclusion_boundary": "product-neutral boundary",
            "truth_sha256": None,
        }
        rows.append(row)
    return rows


class R4AdjudicatedTruthContractBeta5Tests(unittest.TestCase):
    def test_calibration_reference_uses_neutral_sampling_and_dynamic_truth_denominator(self):
        reference = CALIBRATION_REFERENCE.read_text(encoding="utf-8")
        sampling_rows = {
            category: int(count)
            for category, count in re.findall(
                r"^\| `([^`]+)` \| (\d+) \|", reference, flags=re.MULTILINE
            )
        }

        self.assertEqual(sampling_rows, SAMPLING_CATEGORY_COUNTS)
        for truth_bearing_fragment in (
            "new unseen positives",
            "直接来源支持的明确正例",
            "术语不同但实际相关的正例",
            "14个已知正例100%进入展开",
        ):
            with self.subTest(fragment=truth_bearing_fragment):
                self.assertNotIn(truth_bearing_fragment, reference)
        for dynamic_truth_binding in (
            "truth_contract_version = 2.1-r4-adjudicated",
            "accepted_positive_case_ids",
            "accepted_positive_count",
            "accepted_positive_case_ids_sha256",
            "动态召回分母",
        ):
            with self.subTest(binding=dynamic_truth_binding):
                self.assertIn(dynamic_truth_binding, reference)

    def test_versions_and_neutral_sampling_contract_are_exact(self):
        self.assertEqual(MAP_BUILDER_PLUGIN_VERSION, "0.4.0-beta.6")
        self.assertEqual(DIRECTOR_PLUGIN_VERSION, "0.4.0-beta.1")
        self.assertEqual(BETA5_CASE_PACKAGE_CONTRACT_VERSION, "1.0-beta5")
        self.assertEqual(BETA5_TRUTH_CONTRACT_VERSION, "2.1-r4-adjudicated")
        self.assertEqual(BETA5_TRUTH_SCORECARD_CONTRACT_VERSION, "2.1-r4")
        self.assertEqual(
            SELECTION_ORIGIN_COUNTS,
            {"retained_r3_unexecuted": 30, "new_unseen": 10},
        )
        self.assertEqual(sum(SAMPLING_CATEGORY_COUNTS.values()), 40)
        self.assertFalse(
            any("positive" in category for category in SAMPLING_CATEGORY_COUNTS)
        )

    def test_case_rows_are_truth_free_and_sampling_does_not_define_truth(self):
        cases = case_rows()
        self.assertEqual(validate_beta5_case_rows(cases), [])

        cases[0]["known_positive"] = True
        self.assertIn("CASE_TRUTH_FIELD_FORBIDDEN", validate_beta5_case_rows(cases))
        cases[0].pop("known_positive")
        cases[0]["primary_category"] = cases[0]["sampling_category"]
        self.assertIn("LEGACY_TRUTH_BEARING_CATEGORY_FORBIDDEN", validate_beta5_case_rows(cases))

    def test_truth_sets_are_derived_from_accepted_adjudication_and_denominator_is_dynamic(self):
        cases = case_rows()
        truths = truth_rows(positive_count=15)
        self.assertEqual(
            validate_adjudicated_truth_rows(
                truths,
                expected_case_ids=[row["case_id"] for row in cases],
                expected_contract_id="R4-BETA5-TEST",
                expected_preparation_contract_version="R4-BETA5.prep.1",
                expected_locked_input_sha256="a" * 64,
            ),
            [],
        )
        summary = derive_truth_summary(truths)
        self.assertEqual(summary["accepted_positive_count"], 15)
        self.assertEqual(summary["accepted_negative_count"], 25)
        self.assertEqual(summary["unresolved_count"], 0)
        self.assertEqual(len(summary["accepted_positive_case_ids_sha256"]), 64)
        self.assertEqual(validate_positive_holdout_floor(cases, summary), [])

        cases[0]["sampling_category"], cases[20]["sampling_category"] = (
            cases[20]["sampling_category"],
            cases[0]["sampling_category"],
        )
        self.assertEqual(derive_truth_summary(truths), summary)

    def test_unresolved_is_neither_positive_nor_negative(self):
        truths = truth_rows(positive_count=15)
        unresolved = truths[-1]
        unresolved.update(
            {
                "truth_disposition": "unresolved",
                "evidence_state": "conflicted",
                "evidence_quality": "conflicting",
                "counterevidence": ["credible contrary evidence remains"],
            }
        )
        summary = derive_truth_summary(truths)
        self.assertEqual(summary["accepted_positive_count"], 15)
        self.assertEqual(summary["accepted_negative_count"], 24)
        self.assertEqual(summary["unresolved_case_ids"], ["R4-CASE-040"])

    def test_reopened_or_contradictory_truth_cannot_enter_a_frozen_package(self):
        truths = truth_rows(positive_count=15)
        truths[0]["adjudication_state"] = "reopened"
        truths[0]["reopen_reason"] = "new direct counterevidence"
        errors = validate_adjudicated_truth_rows(
            truths,
            expected_case_ids=[f"R4-CASE-{index:03d}" for index in range(1, 41)],
            expected_contract_id="R4-BETA5-TEST",
            expected_preparation_contract_version="R4-BETA5.prep.1",
            expected_locked_input_sha256="a" * 64,
        )
        self.assertIn("CURRENT_TRUTH_ROW_NOT_ACCEPTED", errors)

        truths = truth_rows(positive_count=15)
        truths[0]["evidence_state"] = "hypothesis"
        self.assertIn(
            "TRUTH_EVIDENCE_COMBINATION_INVALID",
            validate_adjudicated_truth_rows(
                truths,
                expected_case_ids=[f"R4-CASE-{index:03d}" for index in range(1, 41)],
                expected_contract_id="R4-BETA5-TEST",
                expected_preparation_contract_version="R4-BETA5.prep.1",
                expected_locked_input_sha256="a" * 64,
            ),
        )

    def test_new_unseen_positive_floor_is_a_freeze_gate_not_a_truth_assignment(self):
        cases = case_rows()
        truths = truth_rows(positive_count=15)
        truths[9].update(
            {
                "truth_disposition": "negative_confirmed",
                "evidence_state": "supported",
                "evidence_quality": "direct_complete",
            }
        )
        summary = derive_truth_summary(truths)
        self.assertEqual(summary["accepted_positive_count"], 14)
        self.assertIn(
            "MINIMUM_NEW_UNSEEN_ACCEPTED_POSITIVES_NOT_MET",
            validate_positive_holdout_floor(cases, summary),
        )

    def test_truth_summary_hashes_sorted_ids_not_sampling_order(self):
        truths = truth_rows(positive_count=15)
        forward = derive_truth_summary(truths)
        reverse = derive_truth_summary(list(reversed(truths)))
        self.assertEqual(forward, reverse)
        self.assertEqual(
            json.dumps(forward["accepted_positive_case_ids"], ensure_ascii=False),
            json.dumps(sorted(forward["accepted_positive_case_ids"]), ensure_ascii=False),
        )

    def test_truth_summary_rejects_forged_hash_overlap_duplicate_and_missing_case(self):
        summary = derive_truth_summary(truth_rows(positive_count=15))
        self.assertEqual(
            validate_truth_summary_integrity(
                summary,
                expected_case_ids=[f"R4-CASE-{index:03d}" for index in range(1, 41)],
            ),
            [],
        )

        forged = dict(summary)
        forged["accepted_positive_case_ids_sha256"] = "f" * 64
        self.assertIn(
            "TRUTH_SUMMARY_HASH_MISMATCH",
            validate_truth_summary_integrity(
                forged,
                expected_case_ids=[f"R4-CASE-{index:03d}" for index in range(1, 41)],
            ),
        )

        overlap = json.loads(json.dumps(summary))
        overlap["accepted_negative_case_ids"][0] = overlap["accepted_positive_case_ids"][0]
        self.assertIn(
            "TRUTH_SUMMARY_CASE_PARTITION_INVALID",
            validate_truth_summary_integrity(
                overlap,
                expected_case_ids=[f"R4-CASE-{index:03d}" for index in range(1, 41)],
            ),
        )

        duplicate = json.loads(json.dumps(summary))
        duplicate["accepted_positive_case_ids"][1] = duplicate["accepted_positive_case_ids"][0]
        self.assertIn(
            "TRUTH_SUMMARY_CASE_IDS_INVALID",
            validate_truth_summary_integrity(
                duplicate,
                expected_case_ids=[f"R4-CASE-{index:03d}" for index in range(1, 41)],
            ),
        )


if __name__ == "__main__":
    unittest.main()
