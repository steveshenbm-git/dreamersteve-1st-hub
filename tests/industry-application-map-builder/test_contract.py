from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "industry-application-map-builder"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "industry-application-map-builder"
R4_PRODUCTION_TEXT_FILES = (
    SKILL_ROOT / "SKILL.md",
    SKILL_ROOT / "agents" / "openai.yaml",
    PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
    SKILL_ROOT / "references" / "content-first-mode-contract.md",
    SKILL_ROOT / "references" / "industry-semantic-research-contract.md",
    SKILL_ROOT / "references" / "industry-semantic-model-protocol.md",
    SKILL_ROOT / "references" / "industry-semantic-calibration-and-audit.md",
    SKILL_ROOT / "references" / "compatibility-matrix.md",
    SKILL_ROOT / "references" / "pressure-scenarios.md",
)


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
        self.assertEqual(manifest["version"], "0.4.0-beta.2")
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

    def test_rc2_semantic_routes_and_resources_are_owned_by_map_builder(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for route in (
            "semantic_contract_prepare",
            "semantic_calibration_case_prepare",
            "semantic_method_calibration",
            "semantic_full_screening",
            "semantic_evidence_expansion",
            "semantic_reverse_audit",
            "semantic_stage_review",
        ):
            self.assertIn(route, skill_text)

        for reference in (
            "industry-semantic-research-contract.md",
            "industry-semantic-model-protocol.md",
            "industry-semantic-calibration-and-audit.md",
        ):
            self.assertTrue((SKILL_ROOT / "references" / reference).is_file(), reference)
            self.assertIn(reference, skill_text)

        for script in (
            "build_semantic_model_handoff.py",
            "lock_semantic_case_preparation_contract.py",
            "finalize_semantic_research_contract.py",
            "init_semantic_research_workspace.py",
            "freeze_semantic_taxonomy_snapshot.py",
            "validate_semantic_research_workspace.py",
            "sample_semantic_reverse_audit.py",
            "evaluate_semantic_calibration.py",
        ):
            self.assertTrue((SKILL_ROOT / "scripts" / script).is_file(), script)

    def test_rc2_case_preparation_has_a_non_circular_gate_before_final_freeze(self):
        combined = "\n".join(
            (SKILL_ROOT / path).read_text(encoding="utf-8")
            for path in (
                "SKILL.md",
                "references/industry-semantic-research-contract.md",
                "references/industry-semantic-calibration-and-audit.md",
                "references/coverage-and-lifecycle.md",
                "references/pressure-scenarios.md",
            )
        )
        for required in (
            "case_preparation_locked",
            "locked_input_sha256",
            "案例集哈希和控制案例必须保持为空",
            "新合同版本",
            "实际案例集哈希",
            "lock_semantic_case_preparation_contract.py",
            "finalize_semantic_research_contract.py",
            "模型运行",
        ):
            self.assertIn(required, combined)
        self.assertIn("占位案例集哈希", combined)

    def test_rc2_contract_separates_status_axes_models_and_authorizations(self):
        for name in (
            "industry-semantic-research-contract.md",
            "industry-semantic-model-protocol.md",
            "industry-semantic-calibration-and-audit.md",
        ):
            self.assertTrue((SKILL_ROOT / "references" / name).is_file(), name)
        references = "\n".join(
            (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
            for name in (
                "industry-semantic-research-contract.md",
                "industry-semantic-model-protocol.md",
                "industry-semantic-calibration-and-audit.md",
            )
        )
        for required in (
            "screening_result",
            "semantic_work_state",
            "evidence_state",
            "no_hypothesis_formed",
            "GPT-5.6 Terra",
            "Claude Sonnet 5",
            "Grok 4.5",
            "manual_external_handoff",
            "application_base_write_authorization",
            "INCONCLUSIVE",
            "baseline_full_depth_v1",
            "screen_then_expand_v2",
            "Bonferroni",
            "超几何",
        ):
            self.assertIn(required, references)
        for forbidden in (
            "logically_unrelated",
            "confirmed_irrelevant",
            "excluded_by_screening",
        ):
            self.assertNotIn(forbidden, references)

    def test_rc2_assets_are_machine_readable_and_do_not_contain_credentials(self):
        asset_root = SKILL_ROOT / "assets" / "semantic-method"
        json_assets = (
            "research-contract.template.json",
            "model-profile.rc2-pilot.template.json",
            "model-task.template.json",
            "model-return.template.json",
            "model-receipt.template.json",
            "screening-record.template.json",
            "audit-plan.template.json",
        )
        combined = ""
        for name in json_assets:
            path = asset_root / name
            self.assertTrue(path.is_file(), name)
            json.loads(path.read_text(encoding="utf-8"))
            combined += path.read_text(encoding="utf-8")
        case_path = asset_root / "calibration-case-set.template.jsonl"
        self.assertTrue(case_path.is_file())
        for line in case_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                json.loads(line)
        for secret_name in ("api_key", "access_token", "password", "private_key"):
            self.assertNotIn(secret_name, combined.lower())

    def test_manual_handoff_assets_define_self_contained_output_and_receiver_receipt(self):
        asset_root = SKILL_ROOT / "assets" / "semantic-method"
        task = json.loads(
            (asset_root / "model-task.template.json").read_text(encoding="utf-8")
        )["semantic_model_task"]
        returned = json.loads(
            (asset_root / "model-return.template.json").read_text(encoding="utf-8")
        )["semantic_model_return"]
        receipt = json.loads(
            (asset_root / "model-receipt.template.json").read_text(encoding="utf-8")
        )["semantic_model_receipt"]
        research_contract = json.loads(
            (asset_root / "research-contract.template.json").read_text(encoding="utf-8")
        )["semantic_research_contract"]

        for required in (
            "visible_input",
            "input_hash_algorithm",
            "expected_return_schema",
            "field_ownership",
            "manual_transport_rules",
            "identity_evidence_policy",
            "source_permissions",
            "stop_condition",
        ):
            self.assertIn(required, task)
        for optional_runtime_field in (
            "model_reported_run_id",
            "model_reported_started_at",
            "model_reported_returned_at",
        ):
            self.assertIn(optional_runtime_field, returned)
            self.assertIsNone(returned[optional_runtime_field])
        for receiver_owned in (
            "receipt_id",
            "received_at",
            "raw_return_reference",
            "raw_return_sha256",
            "identity_evidence",
            "executor_metadata",
            "acceptance_state",
        ):
            self.assertIn(receiver_owned, receipt)
        self.assertIn("model_identity_evidence_policy", research_contract)
        self.assertEqual(
            research_contract["model_identity_evidence_policy"]["B"]["minimum_level"],
            "operator_attested",
        )

    def test_skill_documents_generalized_r4_gates_across_production_contracts(self):
        texts = {
            path.relative_to(PLUGIN_ROOT).as_posix(): path.read_text(encoding="utf-8")
            for path in R4_PRODUCTION_TEXT_FILES
        }
        combined = "\n".join(texts.values())

        requirements_by_file = {
            "skills/industry-application-map-builder/SKILL.md": (
                "content_first_r4",
                "contract-local terminology",
                "output-family",
                "40 pairs",
                "6 predeclared high-risk single-case repeats",
                "CONTENT_CALIBRATION_PASS",
                "RESEARCH_ONLY_BLOCKED",
                "first_incomplete_stage = industry_semantic_expansion",
            ),
            "skills/industry-application-map-builder/references/content-first-mode-contract.md": (
                "visible-only",
                "receiver_snapshot_sha256",
                "truth_scorecard_contract_version",
                "safety -> recall -> receiver evidence -> stability -> efficiency",
                "real 80-task",
            ),
            "skills/industry-application-map-builder/references/industry-semantic-research-contract.md": (
                "global skill terminology schema",
                "contract-local terminology",
                "company-local terminology pack",
                "cold start may be empty",
                "output-family",
            ),
            "skills/industry-application-map-builder/references/industry-semantic-model-protocol.md": (
                "taxonomy membership basis",
                "output or subprocess basis",
                "mechanism or use-point basis",
                "receiver-owned",
                "wrong contract IDs",
            ),
            "skills/industry-application-map-builder/references/industry-semantic-calibration-and-audit.md": (
                "30 unexecuted",
                "10 new unseen positives",
                "development_regression_only",
                "40 pairs",
                "6 predeclared high-risk single-case repeats",
                "20 percent",
                "10 percent",
                "zero source-open increase",
            ),
            "skills/industry-application-map-builder/references/compatibility-matrix.md": (
                "0.4.0-beta.2",
                "legacy downgrade",
                "1.0-legacy",
            ),
        }
        for relative, required_values in requirements_by_file.items():
            with self.subTest(production_file=relative):
                for required in required_values:
                    self.assertIn(required, texts[relative])

        self.assertNotIn("fixed_domain_terms", combined)
        self.assertNotIn("雅洋", combined)
        self.assertNotIn("Yayang", combined)

    def test_r4_pressure_contract_covers_failures_and_recovery_in_production_text(self):
        pressure = (
            SKILL_ROOT / "references" / "pressure-scenarios.md"
        ).read_text(encoding="utf-8")
        for scenario_id in range(59, 81):
            marker = f"R4-P{scenario_id}"
            with self.subTest(scenario=marker):
                matching = [line for line in pressure.splitlines() if marker in line]
                self.assertEqual(len(matching), 1)
                self.assertRegex(matching[0], r"\| (?:FAIL|UNVERIFIED) \|")
                self.assertGreaterEqual(matching[0].count("|"), 5)

        for required in (
            "fixed production vocabulary",
            "company-A leakage",
            "term-pack mutation",
            "model terms treated as evidence",
            "class-name-only broad search",
            "incomplete link chains",
            "prose hashes",
            "formal-truth leakage",
            "development cases counted formally",
            "sentinel-driven method changes",
            "shifted query/open work",
            "missing repeats",
            "value laundering",
            "path aliases",
            "hardlinks",
            "receiver fields",
            "workspace-file laundering",
            "wrong contract IDs",
            "scorecard weakening",
            "CLI threshold override",
            "summary self-report",
            "repeat ID-only copy",
            "legacy downgrade",
        ):
            self.assertIn(required, pressure)

    def test_r4_docs_use_exact_arm_ids_and_quarantine_legacy_arm_names(self):
        calibration = (
            SKILL_ROOT
            / "references"
            / "industry-semantic-calibration-and-audit.md"
        ).read_text(encoding="utf-8")
        r4_text, legacy_text = calibration.split("### legacy strict_audit", 1)

        self.assertIn("baseline_full_depth_v1", r4_text)
        self.assertIn("screen_then_expand_v2", r4_text)
        self.assertNotRegex(r4_text, r"(?<!_)baseline_full_depth(?!_)")
        self.assertNotRegex(r4_text, r"(?<!_)candidate_screen_then_expand(?!_)")
        self.assertIn("EFFECTIVE", legacy_text)

        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        r4_skill, legacy_skill = skill.split("## Legacy strict_audit semantic method", 1)
        self.assertIn("baseline_full_depth_v1", r4_skill)
        self.assertIn("screen_then_expand_v2", r4_skill)
        self.assertNotRegex(r4_skill, r"(?<!_)baseline_full_depth(?!_)")
        self.assertNotRegex(r4_skill, r"(?<!_)candidate_screen_then_expand(?!_)")
        self.assertIn("EFFECTIVE", legacy_skill)

    def test_content_first_and_legacy_acceptance_gates_are_explicitly_separate(self):
        content = (
            SKILL_ROOT / "references" / "content-first-mode-contract.md"
        ).read_text(encoding="utf-8")
        protocol = (
            SKILL_ROOT / "references" / "industry-semantic-model-protocol.md"
        ).read_text(encoding="utf-8")
        calibration = (
            SKILL_ROOT
            / "references"
            / "industry-semantic-calibration-and-audit.md"
        ).read_text(encoding="utf-8")
        compatibility = (
            SKILL_ROOT / "references" / "compatibility-matrix.md"
        ).read_text(encoding="utf-8")

        for required in (
            "platform audit is separate and is not a content PASS gate",
            "CONTENT_CALIBRATION_*",
            "CONTENT_CALIBRATION_PASS",
            "explicit human full-screen authorization",
            "unchanged scope",
            "AUTHORIZED_NOT_STARTED",
            "never emits strict-audit `EFFECTIVE`",
        ):
            self.assertIn(required, content)
        self.assertIn("## content_first R4 return acceptance", protocol)
        self.assertIn("## Legacy strict_audit return acceptance", protocol)
        self.assertIn("identity/admissibility", protocol)
        self.assertIn("### content_first R4 full-screen gate", calibration)
        self.assertIn("### legacy strict_audit", calibration)
        self.assertIn("missing platform audit alone", compatibility)

        pressure = (
            SKILL_ROOT / "references" / "pressure-scenarios.md"
        ).read_text(encoding="utf-8")
        self.assertIn("contract/policy violation", pressure)
        self.assertIn("CONTENT_CALIBRATION_INCOMPLETE", pressure)
        p80 = next(line for line in pressure.splitlines() if "R4-P80" in line)
        self.assertNotIn("重延", p80)

    def test_scorecard_limits_effective_calibration_vocabulary_to_legacy_strict_audit(self):
        scorecard = (
            ROOT / "tests" / "industry-application-map-builder" / "scorecard.md"
        ).read_text(encoding="utf-8")
        calibration_line = next(
            line for line in scorecard.splitlines() if "| CALIBRATION-1 |" in line
        )
        self.assertIn("For legacy `strict_audit` only", calibration_line)
        self.assertIn("EFFECTIVE, NOT_EFFECTIVE, or INCONCLUSIVE", calibration_line)

    def test_remaining_effective_routes_are_explicitly_legacy_only(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        route_line = next(
            line for line in skill.splitlines() if "| `semantic_method_calibration` |" in line
        )
        self.assertIn("legacy `strict_audit` only", route_line)

        research_contract = (
            SKILL_ROOT / "references" / "industry-semantic-research-contract.md"
        ).read_text(encoding="utf-8")
        state_line = next(
            line for line in research_contract.splitlines() if "method_validation_state:" in line
        )
        self.assertIn("legacy_strict_audit_only", state_line)

        pressure = (
            SKILL_ROOT / "references" / "pressure-scenarios.md"
        ).read_text(encoding="utf-8")
        p35 = next(line for line in pressure.splitlines() if line.startswith("35."))
        self.assertIn("legacy strict_audit", p35)


if __name__ == "__main__":
    unittest.main()
