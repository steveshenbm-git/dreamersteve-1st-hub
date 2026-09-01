from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "foreign-trade-customer-operations"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "foreign-trade-customer-operations"
REFERENCE_ROOT = SKILL_ROOT / "references"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class CustomerOperationsContractTests(unittest.TestCase):
    def test_identity_version_and_operations_only_routes(self):
        manifest = json.loads(read(PLUGIN_ROOT / ".codex-plugin" / "plugin.json"))
        skill = read(SKILL_ROOT / "SKILL.md")

        self.assertEqual("foreign-trade-customer-operations", manifest["name"])
        self.assertEqual("0.3.0-beta.1", manifest["version"])
        for route in (
            "outreach_activation",
            "interaction_intake",
            "account_operation",
            "serious_case_operation",
        ):
            self.assertIn(route, skill)
        for old_route in (
            "| `cold_outreach` |",
            "| `unanswered_follow_up` |",
            "| `reply_communication` |",
        ):
            self.assertNotIn(old_route, skill)

    def test_only_operations_authority_references_remain(self):
        skill = read(SKILL_ROOT / "SKILL.md")
        for filename in (
            "routing-and-account-state.md",
            "communication-brief-production.md",
            "serious-case-operation.md",
            "workbook-and-automation.md",
            "optimization-validation.md",
        ):
            self.assertTrue((REFERENCE_ROOT / filename).is_file(), filename)
            self.assertIn(filename, skill)

        for obsolete in (
            "cold-outreach-and-follow-up.md",
            "reply-communication.md",
            "reply-evidence-and-contract.md",
            "special-handling.md",
        ):
            self.assertFalse((REFERENCE_ROOT / obsolete).exists(), obsolete)

    def test_intake_requires_registered_predecessor_and_pauses_on_reply(self):
        skill = read(SKILL_ROOT / "SKILL.md")
        routing = read(REFERENCE_ROOT / "routing-and-account-state.md")
        for required in (
            "validate_customer_flow_transition.py",
            "development_outreach_to_operations_activation",
            "development_reply_to_operations_intake",
            "director_actual_interaction_to_operations_intake",
            "outreach_handoff_packet",
            "customer_operations_handoff",
            "interaction_evidence_packet",
            "A suspected reply is sufficient to pause cold outreach",
        ):
            self.assertIn(required, skill + routing)

    def test_operations_owns_decision_and_brief_but_no_external_body(self):
        skill = read(SKILL_ROOT / "SKILL.md")
        routing = read(REFERENCE_ROOT / "routing-and-account-state.md")
        brief = read(REFERENCE_ROOT / "communication-brief-production.md")
        combined = skill + routing + brief
        for required in (
            "operations_decision_packet",
            "OPERATION_DECISION_READY",
            "communication_brief_packet",
            "customer_thread_snapshot_v1",
            "confirmed salesperson draft-request receipt",
            "foreign-trade-customer-communication",
            "不生成任何对外正文",
            "not external copy and not a send authorization",
        ):
            self.assertIn(required, combined)

    def test_actual_state_and_due_review_cannot_jump_to_drafting(self):
        skill = read(SKILL_ROOT / "SKILL.md")
        workbook = read(REFERENCE_ROOT / "workbook-and-automation.md")
        combined = skill + workbook
        for required in (
            "Only `interaction_evidence_packet` may support actual send or actual reply state",
            "A candidate, approval, planned send",
            "daily_due_draft_review",
            "read-only eligibility reviewer",
            "does not create a communication brief, candidate, workbook write, or send action",
        ):
            self.assertIn(required, combined)

    def test_serious_case_requires_responsible_person_decision(self):
        serious = read(REFERENCE_ROOT / "serious-case-operation.md")
        for required in (
            "Do not admit liability",
            "Do not waive rights",
            "Compensation, refund, discount, replacement",
            "bound responsible-person decision",
            "decision_state = BLOCKED",
        ):
            self.assertIn(required, serious)

    def test_email_assistant_is_a_router_not_a_second_drafting_owner(self):
        readme = read(ROOT / "README.md")
        email_skill = read(
            ROOT
            / "plugins"
            / "foreign-trade-email-assistant"
            / "skills"
            / "foreign-trade-email-assistant"
            / "SKILL.md"
        )
        self.assertIn("optional compatibility router", readme)
        self.assertIn("not an independent email-writing workflow", email_skill)
        self.assertIn("不再独立起草完整线程回复", email_skill)
        self.assertIn("bounded_revision", email_skill)


if __name__ == "__main__":
    unittest.main()
