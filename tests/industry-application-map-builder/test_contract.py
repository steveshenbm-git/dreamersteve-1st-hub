from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "industry-application-map-builder"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "industry-application-map-builder"


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


class IndustryApplicationMapContractTests(unittest.TestCase):
    def test_plugin_identity_and_marketplace_entry(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(manifest["name"], "industry-application-map-builder")
        self.assertEqual(manifest["interface"]["displayName"], "行业应用地图构建")
        self.assertTrue(
            any(
                entry["name"] == "industry-application-map-builder"
                and entry["source"]["path"]
                == "./plugins/industry-application-map-builder"
                for entry in marketplace["plugins"]
            )
        )

    def test_skill_owns_map_work_but_not_customer_search_or_salesperson_status(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertEqual(frontmatter_keys(skill_text), ["name", "description"])
        for required in (
            "base_bootstrap",
            "application_knowledge_update",
            "company_map_build",
            "company_map_review",
            "route_pool_handoff",
            "company_route_pool_packet",
            "不得搜索具体客户",
            "不得写入 `direction_status = 已确认可扫描`",
        ):
            self.assertIn(required, skill_text)

    def test_derivation_contract_exposes_real_chain_and_four_state_logic(self):
        schema = (SKILL_ROOT / "references" / "industry-application-schema.md").read_text(
            encoding="utf-8"
        )
        derivation = (SKILL_ROOT / "references" / "evidence-and-derivation.md").read_text(
            encoding="utf-8"
        )
        combined = schema + derivation

        for required in (
            "industry_node",
            "output_product",
            "use_point_or_process",
            "application_node",
            "requirement_atom",
            "company_id + product_scope + application_node_id",
            "satisfied",
            "violated",
            "unknown",
            "conflicted",
            "geography_evidence_ids",
            "禁止综合评分",
            "AI常识",
        ):
            self.assertIn(required, combined)

    def test_upstream_hands_to_map_builder_and_downstream_consumes_route_pool(self):
        product_skill = (
            ROOT
            / "plugins"
            / "company-product-knowledge-builder"
            / "skills"
            / "company-product-knowledge-builder"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        customer_skill = (
            ROOT
            / "plugins"
            / "foreign-trade-customer-development"
            / "skills"
            / "foreign-trade-customer-development"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("industry-application-map-builder", product_skill)
        self.assertIn("company_route_pool_packet", customer_skill)
        self.assertIn("source_route_candidate_id", customer_skill)
        self.assertIn("命名公司", customer_skill)

    def test_readme_describes_three_skill_workflow(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("industry-application-map-builder", readme)
        self.assertIn(
            "company-product-knowledge-builder → industry-application-map-builder → foreign-trade-customer-development",
            readme,
        )


if __name__ == "__main__":
    unittest.main()
