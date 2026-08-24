from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MAP_PLUGIN = ROOT / "plugins" / "industry-application-map-builder-rc2-content-first"
WORKFLOW_PLUGIN = ROOT / "plugins" / "foreign-trade-workflow-director-rc2-content-first"
MAP_SKILL = (
    MAP_PLUGIN
    / "skills"
    / "industry-application-map-builder-rc2-content-first"
)
WORKFLOW_SKILL = (
    WORKFLOW_PLUGIN
    / "skills"
    / "foreign-trade-workflow-director-rc2-content-first"
)


class ContentFirstCandidateContractTests(unittest.TestCase):
    def test_candidates_have_distinct_names_and_versions(self):
        map_manifest = json.loads(
            (MAP_PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        workflow_manifest = json.loads(
            (WORKFLOW_PLUGIN / ".codex-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            map_manifest["name"], "industry-application-map-builder-rc2-content-first"
        )
        self.assertEqual(map_manifest["version"], "0.4.0-rc2-content-first.1")
        self.assertEqual(
            workflow_manifest["name"], "foreign-trade-workflow-director-rc2-content-first"
        )
        self.assertEqual(workflow_manifest["version"], "0.3.0-rc2-content-first.1")

    def test_content_first_contract_keeps_raw_content_and_separates_platform_audit(self):
        map_skill = (MAP_SKILL / "SKILL.md").read_text(encoding="utf-8")
        workflow_skill = (WORKFLOW_SKILL / "SKILL.md").read_text(encoding="utf-8")
        mode_contract = (
            MAP_SKILL / "references" / "content-first-mode-contract.md"
        ).read_text(encoding="utf-8")
        raw_template = json.loads(
            (MAP_SKILL / "assets" / "content-first" / "content-raw-answer.template.json").read_text(
                encoding="utf-8"
            )
        )["semantic_content_raw_answer"]
        scorecard_template = json.loads(
            (MAP_SKILL / "assets" / "content-first" / "content-scorecard.template.json").read_text(
                encoding="utf-8"
            )
        )["semantic_content_scorecard"]

        self.assertIn("name: industry-application-map-builder-rc2-content-first", map_skill)
        self.assertIn("name: foreign-trade-workflow-director-rc2-content-first", workflow_skill)
        for required in (
            "strict_audit",
            "content_first",
            "raw_response_reference",
            "raw_response_sha256",
            "source_truth_comparison_reference",
            "source_truth_comparison_sha256",
            "method_arm",
            "unknown_items",
            "platform_audit_state",
            "CONTENT_CALIBRATION_PASS",
            "RESEARCH_ONLY_BLOCKED",
        ):
            self.assertIn(required, mode_contract)
        for required in (
            "subject",
            "method_arm",
            "visible_input",
            "visible_input_sha256",
            "raw_response_reference",
            "raw_response_sha256",
            "source_truth_comparison_reference",
        ):
            self.assertIn(required, raw_template)
        self.assertIn("unknown_items", scorecard_template)
        self.assertIn("platform_audit_state", scorecard_template)
        self.assertNotIn("style", "\n".join(scorecard_template["scoring_items"].keys()).lower())
        self.assertIn("RESEARCH_ONLY_BLOCKED", workflow_skill)

    def test_workflow_candidate_keeps_content_first_research_out_of_downstream_stages(self):
        blueprint = (WORKFLOW_SKILL / "references" / "workflow-blueprint.md").read_text(
            encoding="utf-8"
        )
        packet_contract = (
            WORKFLOW_SKILL / "references" / "workflow-and-packet-contracts.md"
        ).read_text(encoding="utf-8")
        state_template = (
            WORKFLOW_SKILL / "assets" / "company-workflow-state.template.yaml"
        ).read_text(encoding="utf-8")
        compatibility = (MAP_SKILL / "references" / "compatibility-matrix.md").read_text(
            encoding="utf-8"
        )

        for text in (blueprint, packet_contract, state_template):
            self.assertIn("semantic_evaluation_mode", text)
            self.assertIn("content_first", text)
            self.assertIn("CONTENT_CALIBRATION_PASS", text)
            self.assertIn("RESEARCH_ONLY_BLOCKED", text)
        self.assertIn("strict_audit", state_template)
        self.assertIn("Content-first full-scope research", compatibility)
        self.assertIn("BLOCKED", compatibility)

    def test_content_first_pressure_scenarios_cover_the_new_failure_modes(self):
        scenarios = (MAP_SKILL / "references" / "pressure-scenarios.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "平台元数据缺失",
            "原始回答",
            "默认授权全量",
            "跨公司污染",
            "文风",
            "RESEARCH_ONLY_BLOCKED",
        ):
            self.assertIn(required, scenarios)


if __name__ == "__main__":
    unittest.main()
