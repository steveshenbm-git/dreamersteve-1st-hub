from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "foreign-trade-workflow-director"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "foreign-trade-workflow-director"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> dict:
    result = subprocess.run(
        [
            "ruby",
            "-ryaml",
            "-rjson",
            "-e",
            "puts JSON.generate(YAML.safe_load(File.read(ARGV.fetch(0)), permitted_classes: [], permitted_symbols: [], aliases: false))",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


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
        self.assertEqual(manifest["version"], "0.5.0-beta.2")
        self.assertRegex(
            manifest["version"],
            r"^0\.5\.0-beta\.2$",
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
            "business_route_closure_review",
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
            "foreign-trade-customer-communication",
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
        self.assertIn("blueprint_version: 0.5.0-beta.2", state)
        self.assertIn("blueprint_version: 0.5.0-beta.2", replication)
        self.assertIn("semantic_evaluation_mode: content_first", state)
        self.assertIn("strict_audit", state)
        self.assertIn("RESEARCH_ONLY_BLOCKED", state)
        self.assertIn("first_incomplete_stage: environment_audit", state)
        self.assertIn("active_work_unit: null", state)
        self.assertIn("latest_semantic_receipt_reference: null", state)
        self.assertIn("latest_review_result: UNVERIFIED", state)
        self.assertIn("latest_admissibility_state: UNVERIFIED", state)
        self.assertIn("work_units: []", state)
        self.assertIn("route_scoped_business_closures: []", state)
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
        self.assertTrue(
            (SKILL_ROOT / "references" / "business-validated-route-closure-contract.md").is_file()
        )
        self.assertTrue(
            (SKILL_ROOT / "assets" / "business-route-closure-receipt.template.json").is_file()
        )
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
            "foreign-trade-customer-communication",
            "excluded_company_data_classes",
            "target_environment_write_authorization: false",
        ):
            self.assertIn(required, replication)

    def test_r4_state_templates_are_closed_hash_gated_and_keep_bootstrap_routing(self):
        state_path = SKILL_ROOT / "assets" / "company-workflow-state.template.yaml"
        replication_path = (
            SKILL_ROOT / "assets" / "workflow-replication-manifest.template.yaml"
        )
        state = load_yaml(state_path)["company_workflow_state"]
        semantic = state["semantic_method"]
        expected_semantic_keys = {
            "semantic_evaluation_mode",
            "allowed_semantic_evaluation_modes",
            "semantic_method_validation_state",
            "terminology_bridge_reference",
            "terminology_bridge_sha256",
            "terminology_bridge_state",
            "allowed_terminology_bridge_states",
            "development_regression_case_count",
            "development_regression_only",
            "development_regression_state",
            "allowed_development_regression_states",
            "case_package_contract_version",
            "truth_contract_version",
            "truth_scorecard_contract_version",
            "formal_holdout_case_count",
            "retained_r3_unexecuted_case_count",
            "new_unseen_case_count",
            "formal_holdout_selection_origin_counts",
            "formal_holdout_provenance_state",
            "allowed_formal_holdout_provenance_states",
            "formal_holdout_case_set_sha256",
            "truth_adjudication_state",
            "allowed_truth_adjudication_states",
            "accepted_positive_case_ids_sha256",
            "accepted_positive_count",
            "accepted_negative_case_ids_sha256",
            "accepted_negative_count",
            "unresolved_case_ids_sha256",
            "unresolved_count",
            "truth_revision_invalidates_prior_scoring",
            "inspector_preflight_required",
            "inspector_memory_reference",
            "inspector_preflight_state",
            "allowed_inspector_preflight_states",
            "deferred_findings_reference",
            "formal_paired_task_expected_count",
            "paired_task_manifest_reference",
            "paired_task_manifest_sha256",
            "formal_paired_task_chain_state",
            "allowed_formal_paired_task_chain_states",
            "source_truth_package_sha256",
            "scorecard_package_sha256",
            "receiver_evidence_manifest_sha256",
            "stability_repeat_expected_count",
            "stability_task_manifest_reference",
            "stability_task_manifest_sha256",
            "stability_repeat_state",
            "allowed_stability_repeat_states",
            "content_method_state",
            "allowed_content_method_states",
            "content_full_screening_state",
            "content_full_screening_authorization_reference",
            "content_full_screening_authorization_receipt_reference",
            "content_full_screening_authorization_receipt_sha256",
            "content_terminal_scope_sha256",
            "downstream_release_state",
            "active_research_contract_id",
            "active_research_contract_version",
            "active_semantic_work_unit",
            "full_screening_authorization",
            "application_base_write_authorization",
            "latest_semantic_return_reference",
            "latest_semantic_receipt_reference",
            "latest_review_result",
            "latest_admissibility_state",
        }
        self.assertEqual(set(semantic), expected_semantic_keys)
        self.assertEqual(state["first_incomplete_stage"], "environment_audit")
        self.assertEqual(semantic["active_semantic_work_unit"], "content_first_contract_prepare")
        self.assertEqual(semantic["terminology_bridge_state"], "not_prepared")
        self.assertIsNone(semantic["terminology_bridge_reference"])
        self.assertIsNone(semantic["terminology_bridge_sha256"])
        self.assertEqual(semantic["development_regression_case_count"], 10)
        self.assertTrue(semantic["development_regression_only"])
        self.assertEqual(semantic["development_regression_state"], "not_started")
        self.assertEqual(semantic["formal_holdout_case_count"], 40)
        self.assertEqual(semantic["retained_r3_unexecuted_case_count"], 30)
        self.assertEqual(semantic["new_unseen_case_count"], 10)
        self.assertEqual(
            semantic["formal_holdout_selection_origin_counts"],
            {"retained_r3_unexecuted": 30, "new_unseen": 10},
        )
        self.assertEqual(semantic["case_package_contract_version"], "1.0-beta5")
        self.assertEqual(semantic["truth_contract_version"], "2.1-r4-adjudicated")
        self.assertEqual(semantic["truth_scorecard_contract_version"], "2.1-r4")
        self.assertEqual(semantic["truth_adjudication_state"], "not_prepared")
        self.assertIsNone(semantic["accepted_positive_case_ids_sha256"])
        self.assertIsNone(semantic["accepted_positive_count"])
        self.assertTrue(semantic["truth_revision_invalidates_prior_scoring"])
        self.assertTrue(semantic["inspector_preflight_required"])
        self.assertEqual(semantic["inspector_preflight_state"], "not_checked")
        self.assertIsNone(semantic["formal_holdout_case_set_sha256"])
        self.assertEqual(semantic["formal_paired_task_expected_count"], 80)
        self.assertIsNone(semantic["paired_task_manifest_reference"])
        self.assertIsNone(semantic["paired_task_manifest_sha256"])
        self.assertEqual(semantic["formal_paired_task_chain_state"], "not_started")
        self.assertEqual(semantic["stability_repeat_expected_count"], 6)
        self.assertIsNone(semantic["stability_task_manifest_reference"])
        self.assertIsNone(semantic["stability_task_manifest_sha256"])
        self.assertEqual(semantic["stability_repeat_state"], "not_started")
        self.assertEqual(semantic["content_method_state"], "CONTENT_CALIBRATION_INCOMPLETE")
        self.assertIsNone(semantic["content_full_screening_authorization_reference"])
        self.assertIsNone(semantic["content_full_screening_authorization_receipt_reference"])
        self.assertIsNone(semantic["content_full_screening_authorization_receipt_sha256"])
        self.assertIsNone(semantic["content_terminal_scope_sha256"])
        self.assertEqual(semantic["downstream_release_state"], "RESEARCH_ONLY_BLOCKED")

        replication = load_yaml(replication_path)["workflow_replication_manifest"]
        dependencies = replication["r4_semantic_contract_dependencies"]
        self.assertEqual(
            set(dependencies),
            {
                "semantic_evaluation_mode",
                "terminology_bridge_reference",
                "terminology_bridge_sha256",
                "terminology_bridge_state",
                "development_regression_state",
                "development_regression_only",
                "case_package_contract_version",
                "truth_contract_version",
                "truth_scorecard_contract_version",
                "formal_holdout_case_set_sha256",
                "formal_holdout_case_count",
                "retained_r3_unexecuted_case_count",
                "new_unseen_case_count",
                "formal_holdout_provenance_state",
                "truth_adjudication_state",
                "accepted_positive_case_ids_sha256",
                "accepted_positive_count",
                "accepted_negative_case_ids_sha256",
                "accepted_negative_count",
                "unresolved_case_ids_sha256",
                "unresolved_count",
                "truth_revision_invalidates_prior_scoring",
                "inspector_preflight_required",
                "formal_paired_task_expected_count",
                "paired_task_manifest_reference",
                "paired_task_manifest_sha256",
                "formal_paired_task_chain_state",
                "source_truth_package_sha256",
                "scorecard_package_sha256",
                "receiver_evidence_manifest_sha256",
                "stability_repeat_expected_count",
                "stability_task_manifest_reference",
                "stability_task_manifest_sha256",
                "stability_repeat_state",
                "content_method_state",
                "content_full_screening_state",
                "content_full_screening_authorization_reference",
                "content_full_screening_authorization_receipt_reference",
                "content_full_screening_authorization_receipt_sha256",
                "content_terminal_scope_sha256",
                "downstream_release_state",
            },
        )
        self.assertEqual(dependencies["semantic_evaluation_mode"], "content_first")
        self.assertTrue(dependencies["development_regression_only"])
        self.assertEqual(dependencies["formal_holdout_case_count"], 40)
        self.assertEqual(dependencies["retained_r3_unexecuted_case_count"], 30)
        self.assertEqual(dependencies["new_unseen_case_count"], 10)
        self.assertEqual(dependencies["case_package_contract_version"], "1.0-beta5")
        self.assertEqual(dependencies["truth_contract_version"], "2.1-r4-adjudicated")
        self.assertEqual(dependencies["truth_scorecard_contract_version"], "2.1-r4")
        self.assertTrue(dependencies["truth_revision_invalidates_prior_scoring"])
        self.assertTrue(dependencies["inspector_preflight_required"])
        self.assertEqual(dependencies["formal_paired_task_expected_count"], 80)
        self.assertIsNone(dependencies["paired_task_manifest_reference"])
        self.assertIsNone(dependencies["paired_task_manifest_sha256"])
        self.assertEqual(dependencies["stability_repeat_expected_count"], 6)
        self.assertIsNone(dependencies["stability_task_manifest_reference"])
        self.assertIsNone(dependencies["stability_task_manifest_sha256"])
        self.assertIsNone(dependencies["content_full_screening_authorization_reference"])
        self.assertIsNone(
            dependencies["content_full_screening_authorization_receipt_reference"]
        )
        self.assertIsNone(dependencies["content_full_screening_authorization_receipt_sha256"])
        self.assertIsNone(dependencies["content_terminal_scope_sha256"])
        self.assertEqual(dependencies["downstream_release_state"], "RESEARCH_ONLY_BLOCKED")

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
            "communication": ROOT
            / "plugins/foreign-trade-customer-communication/skills/foreign-trade-customer-communication/SKILL.md",
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

    def test_director_routes_r4_without_downstream_release_or_legacy_downgrade(self):
        skill = read(SKILL_ROOT / "SKILL.md")
        blueprint = read(SKILL_ROOT / "references" / "workflow-blueprint.md")
        contract = read(SKILL_ROOT / "references" / "workflow-and-packet-contracts.md")
        pressures = read(ROOT / "tests" / "foreign-trade-workflow-director" / "pressure-prompts.md")
        scorecard = read(ROOT / "tests" / "foreign-trade-workflow-director" / "scorecard.md")
        combined = "\n".join((skill, blueprint, contract, pressures, scorecard))

        for required in (
            "first_incomplete_stage: industry_semantic_expansion",
            "terminology_bridge_reference",
            "terminology_bridge_sha256",
            "terminology_bridge_state",
            "development_regression_only",
            "development_regression_state",
            "formal_holdout_case_set_sha256",
            "retained_r3_unexecuted",
            "new_unseen",
            "accepted_positive_case_ids_sha256",
            "accepted_negative_case_ids_sha256",
            "unresolved_case_ids_sha256",
            "truth_revision_invalidates_prior_scoring",
            "inspector_preflight",
            "formal_holdout_provenance_state",
            "paired_task_manifest_sha256",
            "formal_paired_task_chain_state",
            "stability_repeat_state",
            "stability_task_manifest_sha256",
            "source_truth_package_sha256",
            "scorecard_package_sha256",
            "receiver_evidence_manifest_sha256",
            "content_first_contract_prepare",
            "semantic_calibration_case_prepare",
            "content_first_calibration_review",
            "CONTENT_CALIBRATION_INCOMPLETE",
            "CONTENT_CALIBRATION_PASS",
            "content_first_full_screening_gate",
            "content_full_screening_authorization_reference",
            "content_full_screening_authorization_receipt_reference",
            "content_full_screening_authorization_receipt_sha256",
            "content_terminal_scope_sha256",
            "RESEARCH_ONLY_BLOCKED",
            "platform_audit_state",
        ):
            self.assertIn(required, combined)
        self.assertIn("30 + 10", combined)
        self.assertIn("80", combined)
        self.assertIn("6", combined)
        self.assertIn("strict_audit", combined)
        self.assertIn(
            "not_started / in_progress / UNVERIFIED → content_first_calibration_review (development-only)",
            combined,
        )
        self.assertIn("FAIL → content_first_contract_prepare", combined)
        self.assertIn(
            "授权引用、Task 8 gate绑定、独立receipt引用与真实SHA-256、冻结末端范围SHA-256任一缺失或错配 → content_first_full_screening_gate (NOT_AUTHORIZED)",
            combined,
        )
        self.assertIn("strict_audit 的40例 `EFFECTIVE`", skill)
        self.assertIn("content_first 的 `CONTENT_CALIBRATION_PASS`", skill)
        self.assertNotIn("40例结果即使 `EFFECTIVE`", skill)
        self.assertIn(
            "semantic_method_validation_state: null | INCONCLUSIVE | EFFECTIVE | NOT_EFFECTIVE (strict_audit only; content_first = null)",
            contract,
        )
        content_return = contract.split("content_first_semantic_return:", 1)[1].split(
            "```", 1
        )[0]
        specialist_return = contract.split(
            "semantic_specialist_return_packet:", 1
        )[1].split("```", 1)[0]
        for return_schema in (content_return, specialist_return):
            for required in (
                "content_full_screening_state",
                "content_full_screening_authorization_reference",
                "content_full_screening_authorization_receipt_reference",
                "content_full_screening_authorization_receipt_sha256",
                "content_terminal_scope_sha256",
            ):
                self.assertIn(required, return_schema)
        self.assertNotRegex(skill, re.compile(r"(?m)^\s*方法未EFFECTIVE\s*→"))

    def test_r4_pressure_suite_covers_machine_gate_failures(self):
        pressures = read(ROOT / "tests" / "foreign-trade-workflow-director" / "pressure-prompts.md")
        for required in (
            "terminology_bridge_sha256",
            "development_regression_only",
            "30 + 10",
            "stability_repeat_state",
            "strict_audit",
            "platform_audit_state",
            "content_full_screening_authorization_receipt_reference",
            "content_full_screening_authorization_receipt_sha256",
            "Task 8 gate绑定",
            "RESEARCH_ONLY_BLOCKED",
        ):
            self.assertIn(required, pressures)

    def test_legacy_method_result_vocabulary_is_locally_scoped_in_every_director_surface(self):
        surfaces = (
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "references" / "workflow-blueprint.md",
            SKILL_ROOT / "references" / "workflow-and-packet-contracts.md",
            ROOT / "tests" / "foreign-trade-workflow-director" / "pressure-prompts.md",
            ROOT / "tests" / "foreign-trade-workflow-director" / "scorecard.md",
        )
        legacy_result = re.compile(r"(?:NOT_EFFECTIVE|INCONCLUSIVE|EFFECTIVE)")
        explicit_legacy_scope = re.compile(r"strict_audit|legacy|严格审计|历史")
        unscoped = []
        for path in surfaces:
            for line_number, line in enumerate(read(path).splitlines(), start=1):
                if legacy_result.search(line) and not explicit_legacy_scope.search(line):
                    unscoped.append(f"{path.relative_to(ROOT)}:{line_number}: {line}")
        self.assertEqual(unscoped, [])

    def test_content_first_state_never_uses_legacy_method_result_state(self):
        state = load_yaml(
            SKILL_ROOT / "assets" / "company-workflow-state.template.yaml"
        )["company_workflow_state"]["semantic_method"]
        self.assertEqual(state["semantic_evaluation_mode"], "content_first")
        self.assertIsNone(state["semantic_method_validation_state"])
        self.assertRegex(state["content_method_state"], r"^CONTENT_CALIBRATION_")


if __name__ == "__main__":
    unittest.main()
