from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = (
    ROOT / "plugins" / "foreign-trade-workflow-director" / "skills" / "foreign-trade-workflow-director"
)
FIXTURE = ROOT / "tests" / "foreign-trade-workflow-director" / "fixtures" / "inspector-governance-pressure-cases.json"


class InspectorGovernanceLeakageTests(unittest.TestCase):
    def test_portable_candidate_contains_no_company_task_or_local_path_facts(self):
        forbidden = re.compile(
            r"(?:雅洋|江月|Jiangyue|Yayang|Task[ -]?12|RC2-40-SOURCE-TRUTH|prosecutor-ledger|/Users/|传统外贸)",
            re.IGNORECASE,
        )
        files = [
            path
            for path in SKILL_ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".json", ".jsonl", ".py"}
        ] + [FIXTURE]
        hits = []
        for path in files:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if forbidden.search(line):
                    hits.append(f"{path}:{number}")
        self.assertEqual(hits, [])

    def test_templates_are_fact_empty_not_preaccepted_instances(self):
        for path in (
            SKILL_ROOT / "assets" / "workflow-governance-registry.template.yaml",
            SKILL_ROOT / "assets" / "legacy-governance-source-manifest.template.yaml",
            SKILL_ROOT / "assets" / "legacy-finding-mapping.template.jsonl",
            SKILL_ROOT / "assets" / "migration-validation-report.template.json",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIn("template_record", text)
            self.assertNotRegex(text, re.compile(r"(?:accepted_effective|verified_closed|activation_state:\s*ACTIVE)"))


if __name__ == "__main__":
    unittest.main()
