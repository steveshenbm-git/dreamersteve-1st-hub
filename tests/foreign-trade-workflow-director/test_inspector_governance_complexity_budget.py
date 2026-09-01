from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "foreign-trade-workflow-director"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "foreign-trade-workflow-director"


class InspectorGovernanceComplexityBudgetTests(unittest.TestCase):
    def test_candidate_identity_and_two_governance_runtime_entrypoints(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["version"], "0.5.0-beta.1")
        scripts = {path.name for path in (SKILL_ROOT / "scripts").glob("*.py")}
        governance_entrypoints = {
            "validate-legacy-governance-migration.py",
            "workflow-governance.py",
        }
        self.assertEqual(scripts & governance_entrypoints, governance_entrypoints)
        self.assertEqual(
            scripts - governance_entrypoints,
            {
                "validate_handoff_envelope.py",
                "validate_customer_flow_transition.py",
                "bind_customer_flow_transition.py",
            },
        )

    def test_runtime_scripts_use_standard_library_and_no_service_stack(self):
        allowed_roots = {
            "__future__", "argparse", "copy", "datetime", "fnmatch", "hashlib", "json", "os",
            "pathlib", "re", "sys", "tempfile", "typing", "uuid",
            "validate_customer_flow_transition",
        }
        forbidden_calls = {"socket", "serve_forever", "Popen", "urlopen", "requests"}
        for script in sorted((SKILL_ROOT / "scripts").glob("*.py")):
            tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
            imported = set()
            names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".", 1)[0])
                elif isinstance(node, ast.Name):
                    names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    names.add(node.attr)
            self.assertFalse(imported - allowed_roots, (script.name, imported - allowed_roots))
            self.assertFalse(names & forbidden_calls, (script.name, names & forbidden_calls))

    def test_portable_resources_do_not_embed_company_or_incident_facts(self):
        portable = [
            path
            for path in SKILL_ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".json", ".jsonl", ".py"}
        ]
        forbidden = re.compile(
            r"(?:雅洋|江月|Jiangyue|Yayang|Task[ -]?12|RC2-40-SOURCE-TRUTH|prosecutor-ledger)",
            re.IGNORECASE,
        )
        hits = []
        for path in portable:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if forbidden.search(line):
                    hits.append(f"{path.relative_to(SKILL_ROOT)}:{number}")
        self.assertEqual(hits, [])

    def test_skill_entrypoint_stays_a_router(self):
        current_lines = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(current_lines), 319)
        skill = "\n".join(current_lines)
        self.assertNotIn("legacy-finding-mapping.jsonl:", skill)
        self.assertNotIn("finding_event:\n  schema_version", skill)
        migration_section = skill.split("## 历史治理迁移", 1)
        if len(migration_section) == 2:
            self.assertIn("仅在用户明确要求迁移", migration_section[1])


if __name__ == "__main__":
    unittest.main()
