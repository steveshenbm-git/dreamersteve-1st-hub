from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "foreign-trade-workflow-director"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "foreign-trade-workflow-director"


def load_yaml(path: Path) -> dict:
    result = subprocess.run(
        [
            "ruby", "-ryaml", "-rjson", "-e",
            "puts JSON.generate(YAML.safe_load(File.read(ARGV.fetch(0)), permitted_classes: [], permitted_symbols: [], aliases: false))",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class InspectorGovernanceContractTests(unittest.TestCase):
    def test_candidate_identity_and_contract_versions(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["version"], "0.5.0-beta.2")
        self.assertIn("inspector-governance", manifest["keywords"])
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---", 2)[1]
        self.assertIn("cross-skill inspector governance", frontmatter)
        self.assertIn("validation progress", frontmatter)
        inspector = (SKILL_ROOT / "references" / "inspector-governance-contract.md").read_text(encoding="utf-8")
        migration = (SKILL_ROOT / "references" / "legacy-governance-migration-contract.md").read_text(encoding="utf-8")
        self.assertIn("FTWG-INSPECTOR-GOVERNANCE", inspector)
        self.assertIn("1.0.0-draft.3", inspector)
        self.assertIn("FTWG-LEGACY-GOVERNANCE-MIGRATION", migration)
        self.assertIn("1.0.0-draft.2", migration)
        self.assertIn("no automatic activation", migration)

    def test_four_templates_are_empty_and_safe(self):
        assets = SKILL_ROOT / "assets"
        registry = load_yaml(assets / "workflow-governance-registry.template.yaml")
        manifest = load_yaml(assets / "legacy-governance-source-manifest.template.yaml")
        mapping_lines = [
            json.loads(line)
            for line in (assets / "legacy-finding-mapping.template.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        report = json.loads((assets / "migration-validation-report.template.json").read_text(encoding="utf-8"))

        for document in (registry, manifest, report, mapping_lines[0]):
            self.assertIs(document["template_record"], True)
        self.assertEqual(registry["template_state"], "UNVERIFIED")
        self.assertFalse(registry["write_authorized"])
        self.assertIsNone(registry["workflow_governance_registry"]["registry_id"])
        self.assertEqual(manifest["discovery_roots"], [])
        self.assertEqual(manifest["declared_sources"], [])
        self.assertIsNone(mapping_lines[0]["mapping_id"])
        self.assertEqual(report["result"], "UNVERIFIED")
        self.assertFalse(report["activation_authorized"])

    def test_runtime_yaml_templates_are_json_compatible_without_third_party_yaml(self):
        assets = SKILL_ROOT / "assets"
        for name in (
            "workflow-governance-registry.template.yaml",
            "legacy-governance-source-manifest.template.yaml",
        ):
            parsed = json.loads((assets / name).read_text(encoding="utf-8"))
            self.assertIs(parsed["template_record"], True)

    def test_existing_templates_bind_null_governance_references(self):
        state = load_yaml(SKILL_ROOT / "assets" / "company-workflow-state.template.yaml")["company_workflow_state"]
        replication = load_yaml(SKILL_ROOT / "assets" / "workflow-replication-manifest.template.yaml")["workflow_replication_manifest"]
        self.assertEqual(state["blueprint_version"], "0.5.0-beta.2")
        self.assertIsNone(state["workflow_governance_registry_reference"])
        self.assertIsNone(state["workflow_governance_registry_sha256"])
        self.assertIsNone(state["latest_inspector_preflight_reference"])
        self.assertEqual(replication["blueprint_version"], "0.5.0-beta.2")
        self.assertIsNone(replication["workflow_governance_registry_reference"])
        self.assertIsNone(replication["workflow_governance_registry_sha256"])

    def test_skill_routes_governance_without_loading_migration_by_default(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("inspector-governance-contract.md", skill)
        self.assertIn("workflow-governance.py", skill)
        self.assertIn("仅在用户明确要求迁移", skill)
        self.assertIn("legacy-governance-migration-contract.md", skill)
        self.assertIn("一个处置和一项下一动作", skill)
        self.assertIn("专业事实和真值仍由专业技能拥有", skill)

    def test_disposition_contract_sequences_correction_and_scopes_stop(self):
        inspector = (SKILL_ROOT / "references" / "inspector-governance-contract.md").read_text(encoding="utf-8")
        for required in (
            "先把失败证据写入不可覆盖的记录",
            "完成保留后才执行纠偏",
            "当前公司和当前任务",
            "不得提升为便携规则或第二家公司事实",
            "目标动作本身是正式激活或正式治理写入",
            "缺少 `governance_registry_write`",
            "对该目标动作返回 `stop`",
            "只读诊断仍可继续",
            "用户请求的目标动作本身只是隔离演练",
        ):
            self.assertIn(required, inspector)

    def test_legacy_activation_without_write_authorization_is_stop(self):
        migration = (SKILL_ROOT / "references" / "legacy-governance-migration-contract.md").read_text(encoding="utf-8")
        self.assertIn("正式激活", migration)
        self.assertIn("缺少 `governance_registry_write`", migration)
        self.assertIn("处置必须是 `stop`", migration)
        self.assertIn("只读盘点、映射复核或诊断不因此被禁止", migration)


if __name__ == "__main__":
    unittest.main()
