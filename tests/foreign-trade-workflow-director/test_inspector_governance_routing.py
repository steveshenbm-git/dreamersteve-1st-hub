from __future__ import annotations

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = (
    ROOT / "plugins" / "foreign-trade-workflow-director" / "skills" / "foreign-trade-workflow-director"
)


class InspectorGovernanceRoutingTests(unittest.TestCase):
    def test_governance_is_horizontal_and_business_stage_order_is_unchanged(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        blueprint = (SKILL_ROOT / "references" / "workflow-blueprint.md").read_text(encoding="utf-8")
        self.assertIn("blueprint_version: 0.5.0-beta.1", blueprint)
        expected = (
            "environment_audit → company_identity → product_knowledge → industry_taxonomy → "
            "industry_semantic_expansion → company_industry_match → route_pool_handoff → "
            "direction_decision → candidate_development → customer_operations → framework_review"
        )
        self.assertIn(expected, skill)
        self.assertNotRegex(expected, re.compile(r"governance|inspector"))
        self.assertIn("RESEARCH_ONLY_BLOCKED", skill)

    def test_normal_route_loads_governance_but_not_migration_detail(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        governance = skill.split("## 跨技能检察治理", 1)[1].split("## 历史治理迁移", 1)[0]
        migration = skill.split("## 历史治理迁移", 1)[1].split("## ", 1)[0]
        self.assertIn("inspector-governance-contract.md", governance)
        self.assertNotIn("legacy-governance-migration-contract.md", governance)
        self.assertIn("仅在用户明确要求迁移", migration)
        self.assertIn("正常审计和续作不加载迁移字段", migration)
        self.assertIn("不自动激活", migration)

    def test_packaged_candidate_has_exact_governance_surface_once(self):
        expected = {
            "references/inspector-governance-contract.md",
            "references/legacy-governance-migration-contract.md",
            "assets/workflow-governance-registry.template.yaml",
            "assets/legacy-governance-source-manifest.template.yaml",
            "assets/legacy-finding-mapping.template.jsonl",
            "assets/migration-validation-report.template.json",
            "scripts/workflow-governance.py",
            "scripts/validate-legacy-governance-migration.py",
        }
        actual = {
            str(path.relative_to(SKILL_ROOT))
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertTrue(expected.issubset(actual))
        for relative in expected:
            self.assertTrue((SKILL_ROOT / relative).is_file())


if __name__ == "__main__":
    unittest.main()
