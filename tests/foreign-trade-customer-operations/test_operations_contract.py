from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "foreign-trade-customer-operations"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "foreign-trade-customer-operations"


class CustomerOperationsContractTests(unittest.TestCase):
    def test_plugin_and_routes_exist(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertEqual("foreign-trade-customer-operations", manifest["name"])
        for route in (
            "cold_outreach",
            "unanswered_follow_up",
            "reply_communication",
            "account_operation",
        ):
            self.assertIn(route, skill_text)

    def test_cold_drafts_never_become_actual_sends(self):
        workbook_text = (
            SKILL_ROOT / "references" / "workbook-and-automation.md"
        ).read_text(encoding="utf-8")

        for required in (
            "draft_content_or_local_reference",
            "draft_generated_at",
            "draft_for_touch_stage",
            "automation_run_id",
            "actual_sent_at = 空",
            "不得自动发送",
        ):
            self.assertIn(required, workbook_text)

    def test_reply_stops_cold_follow_up(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("收到或疑似收到回复", skill_text)
        self.assertIn("停止新的冷开发触达草稿", skill_text)

    def test_reply_handoff_has_a_named_receiving_contract(self):
        routing_text = (
            SKILL_ROOT / "references" / "routing-and-account-state.md"
        ).read_text(encoding="utf-8")

        for required in (
            "customer_operations_handoff",
            "trigger_channel",
            "trigger_touch_id",
            "response_reference",
            "sender_identity_status",
            "actual_send_history",
            "reply_return_packet",
        ):
            self.assertIn(required, routing_text)

    def test_first_touch_channel_exceptions_preserve_the_exact_decision_gates(self):
        cold_text = (
            SKILL_ROOT / "references" / "cold-outreach-and-follow-up.md"
        ).read_text(encoding="utf-8")

        for required in (
            "email_channel_gap_packet",
            "继续研究可正常使用的邮箱",
            "明确批准一个合格的其他渠道首次触达例外",
            "经业务员明确批准的其他渠道首次触达例外实际发送后仍无回复",
            "另行逐项批准一个明确的下一受控动作",
            "不得增加、合并、重命名或扩展选项",
        ):
            self.assertIn(required, cold_text)

    def test_regular_and_event_cadence_keep_a_complete_decision_contract(self):
        cold_text = (
            SKILL_ROOT / "references" / "cold-outreach-and-follow-up.md"
        ).read_text(encoding="utf-8")

        for required in (
            "cadence_decision_packet",
            "initial_email_sequence_completed",
            "alternate_channel_step_completed",
            "return_email_actually_sent",
            "unadjusted_next_date",
            "event_touch_candidate",
            "recorded_validation_question",
            "ai_suggested_validation_question",
            "风险硬门优先于有效事件",
        ):
            self.assertIn(required, cold_text)

    def test_reply_route_preserves_output_revision_and_serious_issue_contracts(self):
        reply_text = (
            SKILL_ROOT / "references" / "reply-communication.md"
        ).read_text(encoding="utf-8")
        evidence_text = (
            SKILL_ROOT / "references" / "reply-evidence-and-contract.md"
        ).read_text(encoding="utf-8")
        special_text = (
            SKILL_ROOT / "references" / "special-handling.md"
        ).read_text(encoding="utf-8")

        for required in (
            "中文回复建议",
            "客户语言邮件预稿",
            "逐意一致的中文译文",
            "一个关键问题只能索取一个缺失事实",
            "自然语言修订",
        ):
            self.assertIn(required, reply_text + evidence_text)
        for required in (
            "时间线",
            "两至三种可选策略",
            "不得承认责任",
            "不得放弃合同权利",
            "未经公司责任人明确批准",
        ):
            self.assertIn(required, special_text)

    def test_legacy_email_assistant_is_explicitly_optional_compatibility(self):
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        legacy_skill_text = (
            ROOT
            / "plugins"
            / "foreign-trade-email-assistant"
            / "skills"
            / "foreign-trade-email-assistant"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("optional compatibility plugin", readme_text)
        self.assertIn("standalone compatibility email workflow", legacy_skill_text)


if __name__ == "__main__":
    unittest.main()
