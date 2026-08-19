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
        self.assertEqual(manifest["version"], "0.3.0-beta.2")
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
            "init_semantic_research_workspace.py",
            "freeze_semantic_taxonomy_snapshot.py",
            "validate_semantic_research_workspace.py",
            "sample_semantic_reverse_audit.py",
            "evaluate_semantic_calibration.py",
        ):
            self.assertTrue((SKILL_ROOT / "scripts" / script).is_file(), script)

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
            "baseline_full_depth",
            "candidate_screen_then_expand",
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


if __name__ == "__main__":
    unittest.main()
