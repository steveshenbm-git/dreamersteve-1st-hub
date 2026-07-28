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
    def test_product_led_direction_discovery_has_a_decision_gate(self):
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
