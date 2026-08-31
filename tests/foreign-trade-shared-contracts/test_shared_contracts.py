from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
DIRECTOR_ROOT = ROOT / "plugins" / "foreign-trade-workflow-director"
INDUSTRY_ROOT = ROOT / "plugins" / "industry-application-map-builder"
DEVELOPMENT_ROOT = ROOT / "plugins" / "foreign-trade-customer-development"
OPERATIONS_ROOT = ROOT / "plugins" / "foreign-trade-customer-operations"
VALIDATOR = (
    DIRECTOR_ROOT
    / "skills"
    / "foreign-trade-workflow-director"
    / "scripts"
    / "validate_handoff_envelope.py"
)

EXPECTED_PLUGIN_VERSIONS = {
    "company-product-knowledge-builder": "0.1.0",
    "industry-application-map-builder": "0.4.0-beta.6",
    "foreign-trade-customer-development": "0.2.0-beta.2",
    "foreign-trade-customer-operations": "0.2.0-beta.2",
    "foreign-trade-workflow-director": "0.3.0-beta.4",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(read(path))


def schema_fields(markdown: str, schema_name: str) -> tuple[str, ...]:
    pattern = re.compile(
        rf"```text\n{re.escape(schema_name)}:\n(?P<body>.*?)\n```",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        raise AssertionError(f"schema not found: {schema_name}")
    fields: list[str] = []
    for line in match.group("body").splitlines():
        if not line.startswith("  ") or line.startswith("    "):
            continue
        fields.append(line.strip().split(":", 1)[0])
    return tuple(fields)


class MarketplaceAndSchemaTests(unittest.TestCase):
    def test_marketplace_exposes_the_complete_workflow_candidate_set(self):
        marketplace = load_json(MARKETPLACE_PATH)
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}

        self.assertEqual(set(EXPECTED_PLUGIN_VERSIONS), set(entries))
        for plugin_name, expected_version in EXPECTED_PLUGIN_VERSIONS.items():
            plugin_root = ROOT / "plugins" / plugin_name
            self.assertEqual(
                entries[plugin_name]["source"]["path"],
                f"./plugins/{plugin_name}",
            )
            manifest = load_json(plugin_root / ".codex-plugin" / "plugin.json")
            self.assertEqual(manifest["version"], expected_version)

    def test_readme_lists_install_commands_for_every_required_plugin(self):
        readme = read(ROOT / "README.md")
        for plugin_name in EXPECTED_PLUGIN_VERSIONS:
            self.assertIn(
                f"codex plugin add {plugin_name}@foreign-trade-team",
                readme,
            )

    def test_industry_semantic_return_matches_the_director_schema(self):
        director_contract = read(
            DIRECTOR_ROOT
            / "skills"
            / "foreign-trade-workflow-director"
            / "references"
            / "workflow-and-packet-contracts.md"
        )
        industry_contract = read(
            INDUSTRY_ROOT
            / "skills"
            / "industry-application-map-builder"
            / "references"
            / "handoff-contracts.md"
        )

        self.assertEqual(
            schema_fields(industry_contract, "semantic_specialist_return_packet"),
            schema_fields(director_contract, "semantic_specialist_return_packet"),
        )

    def test_development_and_operations_share_the_bound_payload_fields(self):
        development_outreach = read(
            DEVELOPMENT_ROOT
            / "skills"
            / "foreign-trade-customer-development"
            / "references"
            / "opportunity-and-outreach.md"
        )
        development_reply = read(
            DEVELOPMENT_ROOT
            / "skills"
            / "foreign-trade-customer-development"
            / "references"
            / "workbook-and-handoff.md"
        )
        operations_routing = read(
            OPERATIONS_ROOT
            / "skills"
            / "foreign-trade-customer-operations"
            / "references"
            / "routing-and-account-state.md"
        )

        outreach_fields = schema_fields(
            development_outreach, "outreach_handoff_packet"
        )
        development_reply_fields = schema_fields(
            development_reply, "customer_operations_handoff"
        )
        operations_reply_fields = schema_fields(
            operations_routing, "customer_operations_handoff"
        )

        self.assertIn("company_id", outreach_fields)
        self.assertIn("company_id", development_reply_fields)
        self.assertEqual(development_reply_fields, operations_reply_fields)
        self.assertNotIn("handoff_id", outreach_fields)
        self.assertNotIn("handoff_id", development_reply_fields)

    def test_each_optimizing_skill_has_an_independent_validation_contract(self):
        contracts = {
            INDUSTRY_ROOT: (
                "formal 40 pairs",
                "6 repeats",
                "RESEARCH_ONLY_BLOCKED",
            ),
            DEVELOPMENT_ROOT: (
                "0 unsupported PASS",
                "no ranking",
                "no drafting or sending",
            ),
            OPERATIONS_ROOT: (
                "0 invented claims",
                "0 false actual state",
                "reply_communication",
            ),
        }

        for plugin_root, required_phrases in contracts.items():
            skill_name = plugin_root.name
            skill_root = plugin_root / "skills" / skill_name
            skill_text = read(skill_root / "SKILL.md")
            contract_path = skill_root / "references" / "optimization-validation.md"
            self.assertTrue(contract_path.is_file(), skill_name)
            self.assertIn(
                "[optimization-validation.md](references/optimization-validation.md)",
                skill_text,
            )
            contract_text = read(contract_path)
            for phrase in required_phrases:
                self.assertIn(phrase, contract_text, skill_name)


class HandoffEnvelopeValidatorTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.payload_path = self.root / "outreach-payload.json"
        self.payload_path.write_text(
            json.dumps(
                {
                    "outreach_handoff_packet": {
                        "company_id": "COMP-001",
                        "customer_id": "CUST-001",
                        "salesperson_request": "prepare cold outreach",
                    }
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.registry_path = self.root / "accepted-handoffs.json"
        self.registry_path.write_text(
            json.dumps({"accepted_handoff_ids": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        self.envelope_path = self.root / "handoff-envelope.json"
        self.write_envelope()

    def tearDown(self):
        self.temp_dir.cleanup()

    def payload_sha256(self) -> str:
        return hashlib.sha256(self.payload_path.read_bytes()).hexdigest()

    def write_envelope(self, **overrides):
        envelope = {
            "contract_version": "1.0",
            "handoff_id": "HANDOFF-001",
            "company_id": "COMP-001",
            "target_skill": "foreign-trade-customer-operations",
            "target_route": "cold_outreach",
            "payload_reference": self.payload_path.name,
            "payload_sha256": self.payload_sha256(),
            "allowed_writes": [],
        }
        envelope.update(overrides)
        self.envelope_path.write_text(
            json.dumps({"handoff_envelope_v1": envelope}, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_validator(
        self,
        *,
        expected_route: str = "cold_outreach",
    ) -> subprocess.CompletedProcess[str]:
        self.assertTrue(VALIDATOR.is_file(), f"missing validator: {VALIDATOR}")
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--envelope",
                str(self.envelope_path),
                "--expected-company-id",
                "COMP-001",
                "--expected-target-skill",
                "foreign-trade-customer-operations",
                "--expected-target-route",
                expected_route,
                "--accepted-handoff-registry",
                str(self.registry_path),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_result(
        self,
        expected_result: str,
        expected_reason: str | None = None,
        *,
        expected_route: str = "cold_outreach",
    ):
        result = self.run_validator(expected_route=expected_route)
        output = json.loads(result.stdout)
        self.assertEqual(output["result"], expected_result, result.stderr)
        if expected_reason is not None:
            self.assertIn(expected_reason, output["reason_codes"])
            self.assertNotEqual(result.returncode, 0)
        else:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output["reason_codes"], [])

    def test_valid_bound_envelope_passes_without_writing(self):
        self.assert_result("PASS")
        self.assertEqual(
            load_json(self.registry_path),
            {"accepted_handoff_ids": []},
        )

    def test_changed_payload_is_rejected(self):
        self.payload_path.write_text("{}\n", encoding="utf-8")
        self.assert_result("FAIL", "PAYLOAD_HASH_MISMATCH")

    def test_cross_company_payload_is_rejected(self):
        payload = load_json(self.payload_path)
        payload["outreach_handoff_packet"]["company_id"] = "COMP-OTHER"
        self.payload_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        self.write_envelope()
        self.assert_result("FAIL", "PAYLOAD_COMPANY_ID_MISMATCH")

    def test_payload_wrapper_must_match_the_target_route(self):
        payload = load_json(self.payload_path)
        inner = payload.pop("outreach_handoff_packet")
        payload["customer_operations_handoff"] = inner
        self.payload_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        self.write_envelope()
        self.assert_result("FAIL", "PAYLOAD_CONTRACT_MISMATCH")

    def test_duplicate_json_key_is_rejected(self):
        self.envelope_path.write_text(
            "{\"handoff_envelope_v1\":{"
            "\"contract_version\":\"1.0\","
            "\"handoff_id\":\"HANDOFF-001\","
            "\"company_id\":\"COMP-OTHER\","
            "\"company_id\":\"COMP-001\","
            "\"target_skill\":\"foreign-trade-customer-operations\","
            "\"target_route\":\"cold_outreach\","
            f"\"payload_reference\":\"{self.payload_path.name}\","
            f"\"payload_sha256\":\"{self.payload_sha256()}\","
            "\"allowed_writes\":[]}}\n",
            encoding="utf-8",
        )
        self.assert_result("FAIL", "JSON_DUPLICATE_KEY")

    def test_wrong_target_is_rejected(self):
        self.write_envelope(target_route="reply_communication")
        self.assert_result("FAIL", "TARGET_ROUTE_MISMATCH")

    def test_unregistered_target_contract_is_rejected(self):
        self.write_envelope(target_route="account_operation")
        self.assert_result(
            "FAIL",
            "TARGET_CONTRACT_UNSUPPORTED",
            expected_route="account_operation",
        )

    def test_duplicate_handoff_is_rejected(self):
        self.registry_path.write_text(
            json.dumps({"accepted_handoff_ids": ["HANDOFF-001"]}) + "\n",
            encoding="utf-8",
        )
        self.assert_result("FAIL", "HANDOFF_ID_ALREADY_ACCEPTED")

    def test_nonempty_write_scope_is_rejected(self):
        self.write_envelope(allowed_writes=["salesperson-workbench.xlsx"])
        self.assert_result("FAIL", "ALLOWED_WRITES_NOT_AUTHORIZED")

    def test_escaping_payload_reference_is_rejected(self):
        self.write_envelope(payload_reference="../outreach-payload.json")
        self.assert_result("FAIL", "PAYLOAD_REFERENCE_INVALID")


if __name__ == "__main__":
    unittest.main()
