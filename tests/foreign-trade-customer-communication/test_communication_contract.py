from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
COMMUNICATION_PLUGIN = ROOT / "plugins" / "foreign-trade-customer-communication"
COMMUNICATION_SKILL = (
    COMMUNICATION_PLUGIN / "skills" / "foreign-trade-customer-communication"
)
OPERATIONS_SKILL = (
    ROOT
    / "plugins"
    / "foreign-trade-customer-operations"
    / "skills"
    / "foreign-trade-customer-operations"
)
DEVELOPMENT_SKILL = (
    ROOT
    / "plugins"
    / "foreign-trade-customer-development"
    / "skills"
    / "foreign-trade-customer-development"
)
DIRECTOR_SKILL = (
    ROOT
    / "plugins"
    / "foreign-trade-workflow-director"
    / "skills"
    / "foreign-trade-workflow-director"
)
EMAIL_SKILL = (
    ROOT
    / "plugins"
    / "foreign-trade-email-assistant"
    / "skills"
    / "foreign-trade-email-assistant"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class CustomerCommunicationContractTests(unittest.TestCase):
    def test_plugin_has_the_required_structure_and_initial_version(self):
        manifest_path = COMMUNICATION_PLUGIN / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(read(manifest_path))
        self.assertEqual("foreign-trade-customer-communication", manifest["name"])
        self.assertEqual("0.1.0-beta.1", manifest["version"])
        self.assertTrue((COMMUNICATION_SKILL / "SKILL.md").is_file())
        self.assertTrue((COMMUNICATION_SKILL / "agents" / "openai.yaml").is_file())

    def test_routes_cover_execution_without_customer_operation_ownership(self):
        skill_text = read(COMMUNICATION_SKILL / "SKILL.md")
        for route in (
            "cold_outreach",
            "unanswered_follow_up",
            "reply_communication",
            "account_communication",
            "sensitive_communication",
            "bounded_revision",
        ):
            self.assertIn(route, skill_text)
        for required in (
            "communication_brief_packet",
            "validate_customer_flow_transition.py",
            "communication_candidate_packet",
            "CANDIDATE_FOR_REVIEW",
            "send_authorization = not_granted",
            "不得直接接受 `outreach_handoff_packet`",
            "不得直接接受原始客户线程",
        ):
            self.assertIn(required, skill_text)

    def test_route_references_are_progressively_loaded(self):
        skill_text = read(COMMUNICATION_SKILL / "SKILL.md")
        for filename in (
            "brief-and-routing.md",
            "cold-outreach-and-follow-up.md",
            "reply-and-sensitive-communication.md",
            "candidate-and-revision-contract.md",
            "optimization-validation.md",
        ):
            path = COMMUNICATION_SKILL / "references" / filename
            self.assertTrue(path.is_file(), filename)
            self.assertIn(filename, skill_text)

    def test_bounded_revision_returns_business_scope_changes_to_operations(self):
        revision_text = read(
            COMMUNICATION_SKILL
            / "references"
            / "candidate-and-revision-contract.md"
        )
        for required in (
            "prior_candidate_reference",
            "prior_candidate_sha256",
            "revision_request_receipt",
            "价格",
            "交期",
            "责任",
            "赔偿",
            "return_scope_change_to_operations",
        ):
            self.assertIn(required, revision_text)

    def test_operations_owns_state_and_brief_but_not_external_copy(self):
        operations_text = read(OPERATIONS_SKILL / "SKILL.md")
        for route in (
            "outreach_activation",
            "interaction_intake",
            "account_operation",
            "serious_case_operation",
        ):
            self.assertIn(route, operations_text)
        for required in (
            "communication_brief_packet",
            "foreign-trade-customer-communication",
            "不生成任何对外正文",
        ):
            self.assertIn(required, operations_text)

    def test_development_routes_to_operations_before_communication(self):
        development_text = read(DEVELOPMENT_SKILL / "SKILL.md")
        self.assertIn("target_route = outreach_activation", development_text)
        self.assertIn("target_route = interaction_intake", development_text)
        self.assertIn("不得直接交给 `foreign-trade-customer-communication`", development_text)

    def test_director_keeps_one_business_stage_and_enforces_internal_substates(self):
        blueprint = read(DIRECTOR_SKILL / "references" / "workflow-blueprint.md")
        contract = read(
            DIRECTOR_SKILL / "references" / "customer-flow-transition-contract.md"
        )
        self.assertIn("customer_operations", blueprint)
        self.assertIn("foreign-trade-customer-communication", blueprint)
        for state in (
            "DEVELOPMENT_READY",
            "THREAD_ACCEPTED",
            "OPERATION_DECISION_READY",
            "COMMUNICATION_BRIEF_ACCEPTED",
            "COMMUNICATION_CANDIDATE_READY",
            "CANDIDATE_REVIEW_PENDING",
        ):
            self.assertIn(state, contract)

    def test_legacy_email_assistant_redirects_complete_threads_to_director(self):
        email_text = read(EMAIL_SKILL / "SKILL.md")
        email_agent = read(EMAIL_SKILL / "agents" / "openai.yaml")
        self.assertIn("foreign-trade-workflow-director", email_text)
        self.assertIn("不再独立起草完整线程回复", email_text)
        self.assertIn("bounded_revision", email_text)
        self.assertIn("完整线程先进入客户运营", email_agent)
        self.assertNotIn("双语预稿", email_agent)
        for obsolete in (
            "evidence-and-sources.md",
            "records-and-integration.md",
            "reply-contract.md",
            "special-handling.md",
        ):
            self.assertFalse((EMAIL_SKILL / "references" / obsolete).exists())


if __name__ == "__main__":
    unittest.main()
