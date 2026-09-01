from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MAP_PLUGIN = ROOT / "plugins" / "industry-application-map-builder"
WORKFLOW_PLUGIN = ROOT / "plugins" / "foreign-trade-workflow-director"
MAP_SKILL = MAP_PLUGIN / "skills" / "industry-application-map-builder"
WORKFLOW_SKILL = WORKFLOW_PLUGIN / "skills" / "foreign-trade-workflow-director"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"


class UnifiedContentFirstUpgradeTests(unittest.TestCase):
    def test_existing_plugin_names_receive_the_next_versions(self):
        map_manifest = json.loads(
            (MAP_PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        workflow_manifest = json.loads(
            (WORKFLOW_PLUGIN / ".codex-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(map_manifest["name"], "industry-application-map-builder")
        self.assertEqual(map_manifest["version"], "0.4.0-beta.6")
        self.assertEqual(workflow_manifest["name"], "foreign-trade-workflow-director")
        self.assertEqual(workflow_manifest["version"], "0.4.0-beta.2")

    def test_content_first_is_in_the_original_skill_and_strict_is_legacy_compatible(self):
        map_skill = (MAP_SKILL / "SKILL.md").read_text(encoding="utf-8")
        workflow_skill = (WORKFLOW_SKILL / "SKILL.md").read_text(encoding="utf-8")
        mode_contract = (MAP_SKILL / "references" / "content-first-mode-contract.md").read_text(
            encoding="utf-8"
        )
        raw_template = MAP_SKILL / "assets" / "content-first" / "content-raw-answer.template.json"

        self.assertIn("name: industry-application-map-builder", map_skill)
        self.assertIn("name: foreign-trade-workflow-director", workflow_skill)
        self.assertIn("content_first", map_skill)
        self.assertIn("strict_audit", map_skill)
        self.assertIn("legacy", map_skill.lower())
        self.assertIn("content_first", workflow_skill)
        self.assertTrue(raw_template.is_file())
        for required in (
            "raw_response_reference",
            "raw_response_sha256",
            "source_truth_comparison_reference",
            "source_truth_comparison_sha256",
            "unknown_items",
            "platform_audit_state",
            "CONTENT_CALIBRATION_PASS",
            "RESEARCH_ONLY_BLOCKED",
        ):
            self.assertIn(required, mode_contract)

    def test_new_workflow_template_defaults_to_content_first_without_releasing_downstream(self):
        state = (
            WORKFLOW_SKILL / "assets" / "company-workflow-state.template.yaml"
        ).read_text(encoding="utf-8")
        blueprint = (WORKFLOW_SKILL / "references" / "workflow-blueprint.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("blueprint_id: foreign-trade-complete-workflow", state)
        self.assertIn("blueprint_version: 0.4.0-beta.2", state)
        self.assertIn("semantic_evaluation_mode: content_first", state)
        self.assertIn("strict_audit", state)
        self.assertIn("RESEARCH_ONLY_BLOCKED", state)
        self.assertIn("CONTENT_CALIBRATION_PASS", blueprint)

    def test_marketplace_has_no_duplicate_candidate_plugin_entry(self):
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        names = {plugin["name"] for plugin in marketplace["plugins"]}

        self.assertEqual(marketplace["name"], "foreign-trade-team")
        self.assertIn("industry-application-map-builder", names)
        self.assertIn("foreign-trade-workflow-director", names)
        self.assertNotIn("industry-application-map-builder-rc2-content-first", names)
        self.assertNotIn("foreign-trade-workflow-director-rc2-content-first", names)
        self.assertFalse(
            (ROOT / "plugins" / "industry-application-map-builder-rc2-content-first").exists()
        )
        self.assertFalse(
            (ROOT / "plugins" / "foreign-trade-workflow-director-rc2-content-first").exists()
        )


if __name__ == "__main__":
    unittest.main()
