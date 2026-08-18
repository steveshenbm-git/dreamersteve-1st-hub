from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "foreign-trade-workflow-director"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "foreign-trade-workflow-director"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter_keys(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    return [
        line.split(":", 1)[0].strip()
        for line in parts[1].splitlines()
        if line and not line.startswith((" ", "\t")) and ":" in line
    ]


class WorkflowDirectorContractTests(unittest.TestCase):
    def test_plugin_identity_marketplace_and_beta_version(self):
        manifest = json.loads(read(PLUGIN_ROOT / ".codex-plugin" / "plugin.json"))
        marketplace = json.loads(read(ROOT / ".agents" / "plugins" / "marketplace.json"))

        self.assertEqual(manifest["name"], "foreign-trade-workflow-director")
        self.assertRegex(manifest["version"], r"^0\.1\.0-beta\.\d+$")
        self.assertTrue(
            any(
                entry["name"] == "foreign-trade-workflow-director"
                and entry["source"]["path"]
                == "./plugins/foreign-trade-workflow-director"
                for entry in marketplace["plugins"]
            )
        )

    def test_skill_is_single_salesperson_front_door(self):
        skill = read(SKILL_ROOT / "SKILL.md")

        self.assertEqual(frontmatter_keys(skill), ["name", "description"])
        for required in (
            "single_salesperson_beta",
            "workbench_bootstrap",
            "workbench_resume",
            "specialist_handoff",
            "business_decision_record",
            "foreign-trade-customer-development",
            "foreign-trade-customer-operations",
            "industry-application-map-builder",
            "不搜索具体客户",
            "不得发送",
            "未写入",
            "待授权",
            "已重开验证",
        ):
            self.assertIn(required, skill)

    def test_packet_contract_separates_front_back_and_collector(self):
        contract = read(SKILL_ROOT / "references" / "workflow-and-packet-contracts.md")

        for required in (
            "salesperson_workbench",
            "specialist_handoff_packet",
            "workbench_update_packet",
            "candidate_collection_task",
            "raw_candidate_batch",
            "append_only",
            "source_record_id",
            "source_packet_reference",
            "evidence_reference",
            "PASS / FAIL / UNVERIFIED",
            "不得生成综合分",
            "共享输入过期",
        ):
            self.assertIn(required, contract)

    def test_agent_prompt_explicitly_invokes_skill(self):
        agent = read(SKILL_ROOT / "agents" / "openai.yaml")
        self.assertIn("$foreign-trade-workflow-director", agent)
        for key in ("display_name", "short_description", "default_prompt"):
            self.assertRegex(agent, re.compile(rf"(?m)^\s+{key}:\s+[\"']"))

    def test_specialists_expose_coordinator_boundaries(self):
        paths = {
            "map": ROOT
            / "plugins/industry-application-map-builder/skills/industry-application-map-builder/SKILL.md",
            "development": ROOT
            / "plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/SKILL.md",
            "operations": ROOT
            / "plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/SKILL.md",
        }
        texts = {name: read(path) for name, path in paths.items()}

        for text in texts.values():
            self.assertIn("foreign-trade-workflow-director", text)
            self.assertIn("salesperson_workbench", text)
        for required in (
            "candidate_task_export",
            "candidate_batch_intake",
            "candidate_review",
            "raw_candidate_batch",
            "追加",
        ):
            self.assertIn(required, texts["development"])


if __name__ == "__main__":
    unittest.main()
