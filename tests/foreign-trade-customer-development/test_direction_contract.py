from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = (
    ROOT
    / "plugins"
    / "foreign-trade-customer-development"
    / "skills"
    / "foreign-trade-customer-development"
)


class DirectionDiscoveryContractTests(unittest.TestCase):
    def test_route_portfolio_review_precedes_direction_compilation(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        research_text = (
            SKILL_ROOT / "references" / "research-and-sources.md"
        ).read_text(encoding="utf-8")
        combined = skill_text + research_text

        for required in (
            "route_portfolio_review",
            "route_portfolio_review_packet",
            "direction_compilation",
            "direction_discovery",
            "compatibility alias",
            "salesperson_route_decision",
        ):
            self.assertIn(required, combined)

    def test_route_preflight_and_readiness_are_explicit_handoffs(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        research_text = (
            SKILL_ROOT / "references" / "research-and-sources.md"
        ).read_text(encoding="utf-8")
        combined = skill_text + research_text

        for required in (
            "producer_registry_reference",
            "route_packet_sha256",
            "development_readiness_request",
            "development_readiness_view",
            "next_owner: company-product-knowledge-builder",
            "可承接",
            "有条件",
            "未知",
            "已确认冲突",
            "不得反写 map_route_status",
        ):
            self.assertIn(required, combined)

    def test_businessperson_owns_route_selection_without_composite_score(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        research_text = (
            SKILL_ROOT / "references" / "research-and-sources.md"
        ).read_text(encoding="utf-8")
        combined = skill_text + research_text

        for required in (
            "选择编译",
            "继续核实",
            "暂缓",
            "淘汰",
            "不得生成综合路线评分",
            "国家或地区假设不得直接变成最终市场优先级",
        ):
            self.assertIn(required, combined)

    def test_route_led_direction_discovery_has_a_decision_gate(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        research_text = (
            SKILL_ROOT / "references" / "research-and-sources.md"
        ).read_text(encoding="utf-8")

        for required in (
            "direction_discovery",
            "direction_validation",
            "development_direction_packet",
            "已确认可扫描",
            "确认可扫描",
            "继续核实",
            "暂缓",
            "淘汰",
            "公司或品牌特定的直接产品证据",
        ):
            self.assertIn(required, skill_text + research_text)

    def test_development_hands_off_communication_without_drafting_email(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        opportunity_text = (
            SKILL_ROOT / "references" / "opportunity-and-outreach.md"
        ).read_text(encoding="utf-8")

        self.assertIn("outreach_handoff", skill_text)
        self.assertIn("不再准备首封邮件", skill_text + opportunity_text)
        self.assertIn("foreign-trade-customer-operations", skill_text)

    def test_direction_discovery_exposes_the_full_product_to_enterprise_derivation_chain(self):
        research_text = (
            SKILL_ROOT / "references" / "research-and-sources.md"
        ).read_text(encoding="utf-8")

        for required in (
            "company_route_pool_packet",
            "source_route_candidate_id",
            "direction_derivation_chain",
            "approved_product_fact",
            "effect_or_function_boundary",
            "application_conditions",
            "observable_product_signal",
            "target_enterprise_rule",
            "counterevidence_or_unknown",
            "事实、推断和未知",
            "不能仅凭外观、行业惯例或“可能需要”",
        ):
            self.assertIn(required, research_text)

    def test_direction_discovery_consumes_map_route_instead_of_rebuilding_industries(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        research_text = (
            SKILL_ROOT / "references" / "research-and-sources.md"
        ).read_text(encoding="utf-8")
        combined = skill_text + research_text

        for required in (
            "industry-application-map-builder",
            "validated `company_route_pool_packet`",
            "does not independently infer an industry from product facts",
            "命名公司初查",
        ):
            self.assertIn(required, combined)

    def test_direction_lifecycle_includes_scan_feedback_without_ai_reclassification(self):
        research_text = (
            SKILL_ROOT / "references" / "research-and-sources.md"
        ).read_text(encoding="utf-8")

        for required in (
            "direction_feedback_packet",
            "保留",
            "调整",
            "暂缓",
            "淘汰",
            "不得自动改写 direction_status",
        ):
            self.assertIn(required, research_text)


if __name__ == "__main__":
    unittest.main()
