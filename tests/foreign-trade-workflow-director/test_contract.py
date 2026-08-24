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
    def test_plugin_identity_marketplace_and_next_beta_version(self):
        manifest = json.loads(read(PLUGIN_ROOT / ".codex-plugin" / "plugin.json"))
        marketplace = json.loads(read(ROOT / ".agents" / "plugins" / "marketplace.json"))

        self.assertEqual(manifest["name"], "foreign-trade-workflow-director")
        self.assertEqual(manifest["version"], "0.3.0-beta.1")
        self.assertRegex(
            manifest["version"],
            r"^0\.3\.0-beta\.1$",
        )
        self.assertTrue(
            any(
                entry["name"] == "foreign-trade-workflow-director"
                and entry["source"]["path"]
                == "./plugins/foreign-trade-workflow-director"
                for entry in marketplace["plugins"]
            )
        )

    def test_skill_is_portable_workflow_controller(self):
        skill = read(SKILL_ROOT / "SKILL.md")

        self.assertEqual(frontmatter_keys(skill), ["name", "description"])
        for required in (
            "portable_workflow_blueprint_beta",
            "framework_audit",
            "company_framework_bootstrap",
            "framework_resume",
            "specialist_handoff",
            "framework_replication_plan",
            "business_decision_record",
            "environment_audit",
            "company_identity",
            "product_knowledge",
            "industry_taxonomy",
            "industry_semantic_expansion",
            "company_industry_match",
            "route_pool_handoff",
            "direction_decision",
            "candidate_development",
            "customer_operations",
            "framework_review",
            "最早未完成",
            "foreign-trade-customer-development",
            "foreign-trade-customer-operations",
            "industry-application-map-builder",
            "salesperson_workbench",
            "不搜索具体客户",
            "不得发送",
            "未写入",
            "待授权",
            "已重开验证",
        ):
            self.assertIn(required, skill)

    def test_blueprint_orders_stages_and_blocks_semantic_gap(self):
        blueprint = read(SKILL_ROOT / "references" / "workflow-blueprint.md")
        stages = (
            "environment_audit",
            "company_identity",
            "product_knowledge",
            "industry_taxonomy",
            "industry_semantic_expansion",
            "company_industry_match",
            "route_pool_handoff",
            "direction_decision",
            "candidate_development",
            "customer_operations",
            "framework_review",
        )

        positions = [blueprint.index(stage) for stage in stages]
        self.assertEqual(positions, sorted(positions))
        for required in (
            "first_incomplete_stage",
            "not_expanded",
            "full registered terminal-node scope",
            "pilot",
            "company_foundation",
            "route_instance",
            "direction_instance",
            "customer_thread",
            "workflow_blueprint",
            "company_workflow_state",
            "workflow_replication_manifest",
            "company_id",
            "private company data",
            "separate authorization",
            "PASS | FAIL | UNVERIFIED",
        ):
            self.assertIn(required, blueprint)

    def test_portable_templates_are_empty_and_complete(self):
        state = read(SKILL_ROOT / "assets" / "company-workflow-state.template.yaml")
        replication = read(
            SKILL_ROOT / "assets" / "workflow-replication-manifest.template.yaml"
        )

        self.assertIn("company_id: null", state)
        self.assertIn("blueprint_version: 0.3.0-beta.1", state)
        self.assertIn("blueprint_version: 0.3.0-beta.1", replication)
        self.assertIn("semantic_evaluation_mode: content_first", state)
        self.assertIn("strict_audit", state)
        self.assertIn("RESEARCH_ONLY_BLOCKED", state)
        self.assertIn("first_incomplete_stage: environment_audit", state)
        self.assertIn("active_work_unit: null", state)
        self.assertIn("latest_semantic_receipt_reference: null", state)
        self.assertIn("latest_review_result: UNVERIFIED", state)
        self.assertIn("latest_admissibility_state: UNVERIFIED", state)
        self.assertIn("work_units: []", state)
        self.assertIn("company_foundation:", state)
        for stage in (
            "environment_audit",
            "company_identity",
            "product_knowledge",
            "industry_taxonomy",
            "industry_semantic_expansion",
            "company_industry_match",
            "route_pool_handoff",
        ):
            self.assertIn(f"stage_id: {stage}", state)
        for recurring_stage in (
            "stage_id: direction_decision",
            "stage_id: candidate_development",
            "stage_id: customer_operations",
            "stage_id: framework_review",
        ):
            self.assertNotIn(recurring_stage, state)

        for required in (
            "required_plugins_and_compatible_versions",
            "company-product-knowledge-builder",
            "industry-application-map-builder",
            "foreign-trade-customer-development",
            "foreign-trade-customer-operations",
            "excluded_company_data_classes",
            "target_environment_write_authorization: false",
        ):
            self.assertIn(required, replication)

    def test_packet_contract_separates_front_back_and_collector(self):
        contract = read(SKILL_ROOT / "references" / "workflow-and-packet-contracts.md")

        for required in (
            "framework_audit_packet",
            "company_framework_bootstrap_packet",
            "workflow_replication_manifest",
            "operator_task_card",
            "first_incomplete_stage",
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
        self.assertIn("完整外贸流程", agent)
        self.assertIn("最早未完成", agent)
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

    def test_stage_five_routes_rc2_without_crossing_human_authorization_gates(self):
        skill = read(SKILL_ROOT / "SKILL.md")
        blueprint = read(SKILL_ROOT / "references" / "workflow-blueprint.md")
        contract = read(SKILL_ROOT / "references" / "workflow-and-packet-contracts.md")
        state = read(SKILL_ROOT / "assets" / "company-workflow-state.template.yaml")
        combined = "\n".join((skill, blueprint, contract, state))

        for required in (
            "semantic_contract_prepare",
            "semantic_calibration_case_prepare",
            "semantic_method_calibration",
            "semantic_full_screening",
            "semantic_evidence_expansion",
            "semantic_reverse_audit",
            "semantic_stage_review",
            "semantic_method_validation_state",
            "active_research_contract_id",
            "active_semantic_work_unit",
            "full_screening_authorization",
            "application_base_write_authorization",
            "semantic_model_handoff_packet",
            "semantic_model_receipt",
            "review_result",
            "admissibility_state",
            "raw_return_sha256",
            "receiver-owned",
            "manual_external_handoff",
        ):
            self.assertIn(required, combined)

        self.assertIn("40例", combined)
        self.assertIn("case_preparation_locked", combined)
        self.assertIn("实际案例集哈希", combined)
        self.assertIn("新版本最终冻结合同", combined)
        self.assertIn("未最终冻结", combined)
        self.assertIn("不能把 `industry_semantic_expansion` 记为 PASS", combined)
        self.assertIn("不自动调用", combined)


if __name__ == "__main__":
    unittest.main()
