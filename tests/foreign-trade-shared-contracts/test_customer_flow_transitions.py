from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
DIRECTOR_SKILL = (
    ROOT
    / "plugins"
    / "foreign-trade-workflow-director"
    / "skills"
    / "foreign-trade-workflow-director"
)
VALIDATOR = DIRECTOR_SKILL / "scripts" / "validate_customer_flow_transition.py"
BINDER = DIRECTOR_SKILL / "scripts" / "bind_customer_flow_transition.py"
TRANSITION_REGISTRY = (
    DIRECTOR_SKILL / "assets" / "customer-flow-transition-registry.v1.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CustomerFlowTransitionValidatorTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source_packet = self.write_json(
            "development-snapshot.json",
            {
                "development_snapshot_v1": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "state": "DEVELOPMENT_READY",
                }
            },
        )
        self.selection_receipt = self.write_json(
            "customer-selection.json",
            {
                "customer_selection_receipt_v1": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "selection_state": "CONFIRMED",
                }
            },
        )
        self.human_receipt = self.write_json(
            "outreach-request.json",
            {
                "human_decision_receipt_v1": {
                    "contract_version": "1.0",
                    "decision_id": "DECISION-001",
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "decision_type": "outreach_request",
                    "decision_state": "CONFIRMED",
                    "recorded_at": "2026-09-01T10:00:00+08:00",
                }
            },
        )
        self.accepted_registry = self.write_json(
            "accepted-handoffs.json", {"accepted_handoff_ids": []}
        )
        self.payload_path = self.root / "outreach-payload.json"
        self.envelope_path = self.root / "handoff-envelope.json"
        self.write_valid_development_transition()

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_json(self, filename: str, document: dict) -> Path:
        path = self.root / filename
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def write_envelope(
        self,
        *,
        target_skill: str = "foreign-trade-customer-operations",
        target_route: str = "outreach_activation",
    ) -> None:
        self.write_json(
            self.envelope_path.name,
            {
                "handoff_envelope_v1": {
                    "contract_version": "1.0",
                    "handoff_id": "HANDOFF-001",
                    "company_id": "COMP-001",
                    "target_skill": target_skill,
                    "target_route": target_route,
                    "payload_reference": self.payload_path.name,
                    "payload_sha256": sha256(self.payload_path),
                    "allowed_writes": [],
                }
            },
        )

    def valid_flow_link(self) -> dict:
        return {
            "contract_version": "1.0",
            "transition_id": "development_outreach_to_operations_activation",
            "company_id": "COMP-001",
            "customer_id": "CUST-001",
            "source_skill": "foreign-trade-customer-development",
            "source_route": "outreach_handoff",
            "source_state": "DEVELOPMENT_READY",
            "target_state": "THREAD_ACCEPTED",
            "source_packet_reference": self.source_packet.name,
            "source_packet_sha256": sha256(self.source_packet),
            "source_acceptance_receipt_reference": None,
            "source_acceptance_receipt_sha256": None,
            "required_bindings": [
                {
                    "role": "customer_selection_receipt",
                    "reference": self.selection_receipt.name,
                    "sha256": sha256(self.selection_receipt),
                }
            ],
            "human_decision_receipt_reference": self.human_receipt.name,
            "human_decision_receipt_sha256": sha256(self.human_receipt),
            "target_skill": "foreign-trade-customer-operations",
            "target_route": "outreach_activation",
            "allowed_next_actions": [
                "establish_customer_thread",
                "return_missing_development_fact",
            ],
        }

    def write_valid_development_transition(self) -> None:
        self.write_json(
            self.payload_path.name,
            {
                "outreach_handoff_packet": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "salesperson_request": "prepare controlled outreach",
                    "customer_flow_link_v1": self.valid_flow_link(),
                }
            },
        )
        self.write_envelope()

    def run_validator(
        self,
        *,
        expected_skill: str = "foreign-trade-customer-operations",
        expected_route: str = "outreach_activation",
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
                expected_skill,
                "--expected-target-route",
                expected_route,
                "--accepted-handoff-registry",
                str(self.accepted_registry),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_failure(self, reason_code: str, **run_kwargs) -> None:
        result = self.run_validator(**run_kwargs)
        self.assertNotEqual(0, result.returncode)
        output = json.loads(result.stdout)
        self.assertEqual("FAIL", output["result"])
        self.assertIn(reason_code, output["reason_codes"])

    def test_registry_and_valid_development_transition_pass_without_writing(self):
        self.assertTrue(TRANSITION_REGISTRY.is_file())
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("PASS", json.loads(result.stdout)["result"])
        self.assertEqual(
            {"accepted_handoff_ids": []},
            json.loads(self.accepted_registry.read_text(encoding="utf-8")),
        )

    def test_direct_development_to_communication_is_rejected(self):
        payload = json.loads(self.payload_path.read_text(encoding="utf-8"))
        inner = payload.pop("outreach_handoff_packet")
        flow_link = inner["customer_flow_link_v1"]
        flow_link["target_skill"] = "foreign-trade-customer-communication"
        flow_link["target_route"] = "cold_outreach"
        payload["communication_brief_packet"] = inner
        self.write_json(self.payload_path.name, payload)
        self.write_envelope(
            target_skill="foreign-trade-customer-communication",
            target_route="cold_outreach",
        )

        self.assert_failure(
            "FLOW_TARGET_MISMATCH",
            expected_skill="foreign-trade-customer-communication",
            expected_route="cold_outreach",
        )

    def test_missing_human_decision_receipt_is_rejected(self):
        payload = json.loads(self.payload_path.read_text(encoding="utf-8"))
        flow_link = payload["outreach_handoff_packet"]["customer_flow_link_v1"]
        flow_link["human_decision_receipt_reference"] = None
        flow_link["human_decision_receipt_sha256"] = None
        self.write_json(self.payload_path.name, payload)
        self.write_envelope()

        self.assert_failure("HUMAN_DECISION_RECEIPT_REQUIRED")

    def test_changed_required_binding_is_rejected(self):
        self.selection_receipt.write_text("{}\n", encoding="utf-8")
        self.assert_failure("FLOW_BINDING_HASH_MISMATCH")

    def test_hash_valid_source_packet_with_wrong_state_is_rejected(self):
        source = json.loads(self.source_packet.read_text(encoding="utf-8"))
        source["development_snapshot_v1"]["state"] = "NOT_READY"
        self.write_json(self.source_packet.name, source)
        payload = json.loads(self.payload_path.read_text(encoding="utf-8"))
        flow_link = payload["outreach_handoff_packet"]["customer_flow_link_v1"]
        flow_link["source_packet_sha256"] = sha256(self.source_packet)
        self.write_json(self.payload_path.name, payload)
        self.write_envelope()

        self.assert_failure("FLOW_SOURCE_STATE_MISMATCH")

    def test_hash_valid_binding_with_wrong_contract_is_rejected(self):
        self.write_json(
            self.selection_receipt.name,
            {
                "unrelated_receipt_v1": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                }
            },
        )
        payload = json.loads(self.payload_path.read_text(encoding="utf-8"))
        flow_link = payload["outreach_handoff_packet"]["customer_flow_link_v1"]
        flow_link["required_bindings"][0]["sha256"] = sha256(
            self.selection_receipt
        )
        self.write_json(self.payload_path.name, payload)
        self.write_envelope()

        self.assert_failure("FLOW_BINDING_CONTRACT_MISMATCH")

    def test_wrong_human_decision_type_is_rejected(self):
        receipt = json.loads(self.human_receipt.read_text(encoding="utf-8"))
        receipt["human_decision_receipt_v1"]["decision_type"] = "send_approval"
        self.write_json(self.human_receipt.name, receipt)
        payload = json.loads(self.payload_path.read_text(encoding="utf-8"))
        flow_link = payload["outreach_handoff_packet"]["customer_flow_link_v1"]
        flow_link["human_decision_receipt_sha256"] = sha256(self.human_receipt)
        self.write_json(self.payload_path.name, payload)
        self.write_envelope()

        self.assert_failure("HUMAN_DECISION_TYPE_MISMATCH")

    def test_operations_to_communication_requires_prior_acceptance(self):
        accepted_input = self.write_json(
            "operations-input.json",
            {
                "outreach_handoff_packet": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                }
            },
        )
        operations_decision = self.write_json(
            "operations-decision.json",
            {
                "operations_decision_packet": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "decision_state": "OPERATION_DECISION_READY",
                    "accepted_input_handoff_id": "HANDOFF-OPS-001",
                    "accepted_input_payload_reference": accepted_input.name,
                    "accepted_input_payload_sha256": sha256(accepted_input),
                }
            },
        )
        thread_snapshot = self.write_json(
            "customer-thread.json",
            {
                "customer_thread_snapshot_v1": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "freshness": "current",
                }
            },
        )
        draft_request = self.write_json(
            "draft-request.json",
            {
                "human_decision_receipt_v1": {
                    "contract_version": "1.0",
                    "decision_id": "DECISION-002",
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "decision_type": "draft_request",
                    "decision_state": "CONFIRMED",
                    "recorded_at": "2026-09-01T10:05:00+08:00",
                }
            },
        )
        flow_link = {
            "contract_version": "1.0",
            "transition_id": "operations_outreach_to_communication_cold",
            "company_id": "COMP-001",
            "customer_id": "CUST-001",
            "source_skill": "foreign-trade-customer-operations",
            "source_route": "outreach_activation",
            "source_state": "OPERATION_DECISION_READY",
            "target_state": "COMMUNICATION_BRIEF_ACCEPTED",
            "source_packet_reference": operations_decision.name,
            "source_packet_sha256": sha256(operations_decision),
            "source_acceptance_receipt_reference": None,
            "source_acceptance_receipt_sha256": None,
            "required_bindings": [
                {
                    "role": "customer_thread_snapshot",
                    "reference": thread_snapshot.name,
                    "sha256": sha256(thread_snapshot),
                }
            ],
            "human_decision_receipt_reference": draft_request.name,
            "human_decision_receipt_sha256": sha256(draft_request),
            "target_skill": "foreign-trade-customer-communication",
            "target_route": "cold_outreach",
            "allowed_next_actions": [
                "prepare_communication_candidate",
                "return_invalid_brief",
            ],
        }
        self.write_json(
            self.payload_path.name,
            {
                "communication_brief_packet": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "communication_purpose": "first controlled contact",
                    "customer_flow_link_v1": flow_link,
                }
            },
        )
        self.write_envelope(
            target_skill="foreign-trade-customer-communication",
            target_route="cold_outreach",
        )

        self.assert_failure(
            "SOURCE_ACCEPTANCE_RECEIPT_REQUIRED",
            expected_skill="foreign-trade-customer-communication",
            expected_route="cold_outreach",
        )

    def test_source_acceptance_receipt_and_prior_input_are_both_bound(self):
        accepted_input = self.write_json(
            "operations-input.json",
            {
                "outreach_handoff_packet": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                }
            },
        )
        operations_decision = self.write_json(
            "operations-decision.json",
            {
                "operations_decision_packet": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "decision_state": "OPERATION_DECISION_READY",
                    "accepted_input_handoff_id": "HANDOFF-OPS-001",
                    "accepted_input_payload_reference": accepted_input.name,
                    "accepted_input_payload_sha256": sha256(accepted_input),
                }
            },
        )
        thread_snapshot = self.write_json(
            "customer-thread.json",
            {
                "customer_thread_snapshot_v1": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "freshness": "current",
                }
            },
        )
        acceptance = self.write_json(
            "operations-acceptance.json",
            {
                "handoff_acceptance_receipt_v1": {
                    "contract_version": "1.0",
                    "handoff_id": "HANDOFF-OPS-001",
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "receiver_skill": "foreign-trade-customer-operations",
                    "receiver_route": "outreach_activation",
                    "accepted_payload_sha256": "0" * 64,
                    "result": "PASS",
                    "accepted_at": "2026-09-01T10:02:00+08:00",
                }
            },
        )
        draft_request = self.write_json(
            "draft-request.json",
            {
                "human_decision_receipt_v1": {
                    "contract_version": "1.0",
                    "decision_id": "DECISION-002",
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "decision_type": "draft_request",
                    "decision_state": "CONFIRMED",
                    "recorded_at": "2026-09-01T10:05:00+08:00",
                }
            },
        )
        self.write_json(
            self.payload_path.name,
            {
                "communication_brief_packet": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "communication_purpose": "first controlled contact",
                    "customer_flow_link_v1": {
                        "contract_version": "1.0",
                        "transition_id": "operations_outreach_to_communication_cold",
                        "company_id": "COMP-001",
                        "customer_id": "CUST-001",
                        "source_skill": "foreign-trade-customer-operations",
                        "source_route": "outreach_activation",
                        "source_state": "OPERATION_DECISION_READY",
                        "target_state": "COMMUNICATION_BRIEF_ACCEPTED",
                        "source_packet_reference": operations_decision.name,
                        "source_packet_sha256": sha256(operations_decision),
                        "source_acceptance_receipt_reference": acceptance.name,
                        "source_acceptance_receipt_sha256": sha256(acceptance),
                        "required_bindings": [
                            {
                                "role": "customer_thread_snapshot",
                                "reference": thread_snapshot.name,
                                "sha256": sha256(thread_snapshot),
                            }
                        ],
                        "human_decision_receipt_reference": draft_request.name,
                        "human_decision_receipt_sha256": sha256(draft_request),
                        "target_skill": "foreign-trade-customer-communication",
                        "target_route": "cold_outreach",
                        "allowed_next_actions": [
                            "prepare_communication_candidate",
                            "return_invalid_brief",
                        ],
                    },
                }
            },
        )
        self.write_envelope(
            target_skill="foreign-trade-customer-communication",
            target_route="cold_outreach",
        )

        self.assert_failure(
            "SOURCE_ACCEPTANCE_PAYLOAD_MISMATCH",
            expected_skill="foreign-trade-customer-communication",
            expected_route="cold_outreach",
        )

        acceptance_document = json.loads(acceptance.read_text(encoding="utf-8"))
        acceptance_document["handoff_acceptance_receipt_v1"][
            "accepted_payload_sha256"
        ] = sha256(accepted_input)
        self.write_json(acceptance.name, acceptance_document)
        payload_document = json.loads(self.payload_path.read_text(encoding="utf-8"))
        payload_document["communication_brief_packet"]["customer_flow_link_v1"][
            "source_acceptance_receipt_sha256"
        ] = sha256(acceptance)
        self.write_json(self.payload_path.name, payload_document)
        self.write_envelope(
            target_skill="foreign-trade-customer-communication",
            target_route="cold_outreach",
        )
        accepted_input.write_text("{}\n", encoding="utf-8")

        self.assert_failure(
            "SOURCE_ACCEPTED_INPUT_HASH_MISMATCH",
            expected_skill="foreign-trade-customer-communication",
            expected_route="cold_outreach",
        )


class CustomerFlowTransitionBinderTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source_packet = self.write_json(
            "development-snapshot.json",
            {
                "development_snapshot_v1": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "state": "DEVELOPMENT_READY",
                }
            },
        )
        self.selection_receipt = self.write_json(
            "customer-selection.json",
            {
                "customer_selection_receipt_v1": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "selection_state": "CONFIRMED",
                }
            },
        )
        self.human_receipt = self.write_json(
            "outreach-request.json",
            {
                "human_decision_receipt_v1": {
                    "contract_version": "1.0",
                    "decision_id": "DECISION-001",
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "decision_type": "outreach_request",
                    "decision_state": "CONFIRMED",
                    "recorded_at": "2026-09-01T10:00:00+08:00",
                }
            },
        )
        self.unbound_payload = self.write_json(
            "outreach-unbound.json",
            {
                "outreach_handoff_packet": {
                    "company_id": "COMP-001",
                    "customer_id": "CUST-001",
                    "salesperson_request": "prepare controlled outreach",
                }
            },
        )
        self.bound_payload = self.root / "outreach-bound.json"
        self.envelope = self.root / "handoff-envelope.json"
        self.accepted_registry = self.write_json(
            "accepted-handoffs.json", {"accepted_handoff_ids": []}
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_json(self, filename: str, document: dict) -> Path:
        path = self.root / filename
        path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def binder_command(self) -> list[str]:
        return [
            sys.executable,
            str(BINDER),
            "--transition-id",
            "development_outreach_to_operations_activation",
            "--handoff-id",
            "HANDOFF-BUILT-001",
            "--payload",
            str(self.unbound_payload),
            "--source-packet",
            str(self.source_packet),
            "--binding",
            f"customer_selection_receipt={self.selection_receipt}",
            "--human-decision-receipt",
            str(self.human_receipt),
            "--output-payload",
            str(self.bound_payload),
            "--output-envelope",
            str(self.envelope),
        ]

    def test_binder_creates_a_transition_that_the_validator_accepts(self):
        self.assertTrue(BINDER.is_file(), f"missing binder: {BINDER}")
        bound = subprocess.run(
            self.binder_command(), text=True, capture_output=True, check=False
        )
        self.assertEqual(0, bound.returncode, bound.stderr)

        validated = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--envelope",
                str(self.envelope),
                "--expected-company-id",
                "COMP-001",
                "--expected-target-skill",
                "foreign-trade-customer-operations",
                "--expected-target-route",
                "outreach_activation",
                "--accepted-handoff-registry",
                str(self.accepted_registry),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, validated.returncode, validated.stderr)
        self.assertEqual("PASS", json.loads(validated.stdout)["result"])

    def test_binder_refuses_to_overwrite_an_existing_output(self):
        self.bound_payload.write_text("preserve\n", encoding="utf-8")
        self.assertTrue(BINDER.is_file(), f"missing binder: {BINDER}")

        result = subprocess.run(
            self.binder_command(), text=True, capture_output=True, check=False
        )

        self.assertNotEqual(0, result.returncode)
        self.assertEqual("preserve\n", self.bound_payload.read_text(encoding="utf-8"))
        self.assertIn("OUTPUT_ALREADY_EXISTS", result.stdout)

    def test_binder_rejects_semantically_wrong_source_before_writing(self):
        source = json.loads(self.source_packet.read_text(encoding="utf-8"))
        source["development_snapshot_v1"]["state"] = "NOT_READY"
        self.write_json(self.source_packet.name, source)

        result = subprocess.run(
            self.binder_command(), text=True, capture_output=True, check=False
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("FLOW_SOURCE_STATE_MISMATCH", result.stdout)
        self.assertFalse(self.bound_payload.exists())
        self.assertFalse(self.envelope.exists())


class CustomerFlowRegistryCoverageTests(unittest.TestCase):
    def test_every_registered_transition_builds_a_validator_accepted_chain(self):
        registry = json.loads(TRANSITION_REGISTRY.read_text(encoding="utf-8"))
        binding_contracts = registry["binding_contracts"]

        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            for index, (transition_id, transition) in enumerate(
                registry["transitions"].items(), start=1
            ):
                with self.subTest(transition_id=transition_id):
                    package = base / f"case-{index:02d}"
                    package.mkdir()

                    def write(filename: str, document: dict) -> Path:
                        path = package / filename
                        path.write_text(
                            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8",
                        )
                        return path

                    company_id = "COMP-001"
                    customer_id = f"CUST-{index:03d}"
                    source_inner = {
                        "company_id": company_id,
                        "customer_id": customer_id,
                        transition["source_state_field"]: transition["source_state"],
                    }
                    accepted_input_handoff_id = f"INPUT-{index:03d}"
                    accepted_input_payload_sha256 = None
                    if transition["source_acceptance_receipt_required"]:
                        accepted_input = write(
                            "accepted-input.json",
                            {
                                "prior_input_packet": {
                                    "company_id": company_id,
                                    "customer_id": customer_id,
                                }
                            },
                        )
                        accepted_input_payload_sha256 = sha256(accepted_input)
                        source_inner.update(
                            {
                                "accepted_input_handoff_id": accepted_input_handoff_id,
                                "accepted_input_payload_reference": accepted_input.name,
                                "accepted_input_payload_sha256": accepted_input_payload_sha256,
                            }
                        )
                    source_packet = write(
                        "source.json",
                        {transition["source_packet_root"]: source_inner},
                    )

                    bindings = []
                    for binding_index, role in enumerate(
                        transition["required_binding_roles"], start=1
                    ):
                        binding = write(
                            f"binding-{binding_index}.json",
                            {
                                binding_contracts[role]: {
                                    "company_id": company_id,
                                    "customer_id": customer_id,
                                }
                            },
                        )
                        bindings.append(
                            {
                                "role": role,
                                "reference": binding.name,
                                "sha256": sha256(binding),
                            }
                        )

                    acceptance_reference = None
                    acceptance_sha256 = None
                    if transition["source_acceptance_receipt_required"]:
                        acceptance = write(
                            "acceptance.json",
                            {
                                "handoff_acceptance_receipt_v1": {
                                    "contract_version": "1.0",
                                    "handoff_id": accepted_input_handoff_id,
                                    "company_id": company_id,
                                    "customer_id": customer_id,
                                    "receiver_skill": transition["source_skill"],
                                    "receiver_route": transition["source_route"],
                                    "accepted_payload_sha256": accepted_input_payload_sha256,
                                    "result": "PASS",
                                    "accepted_at": "2026-09-01T12:00:00+08:00",
                                }
                            },
                        )
                        acceptance_reference = acceptance.name
                        acceptance_sha256 = sha256(acceptance)

                    human_reference = None
                    human_sha256 = None
                    if transition["human_decision_receipt_required"]:
                        human = write(
                            "human.json",
                            {
                                "human_decision_receipt_v1": {
                                    "contract_version": "1.0",
                                    "decision_id": f"DECISION-{index:03d}",
                                    "company_id": company_id,
                                    "customer_id": customer_id,
                                    "decision_type": transition[
                                        "human_decision_types"
                                    ][0],
                                    "decision_state": "CONFIRMED",
                                    "recorded_at": "2026-09-01T12:01:00+08:00",
                                }
                            },
                        )
                        human_reference = human.name
                        human_sha256 = sha256(human)

                    flow_link = {
                        "contract_version": "1.0",
                        "transition_id": transition_id,
                        "company_id": company_id,
                        "customer_id": customer_id,
                        "source_skill": transition["source_skill"],
                        "source_route": transition["source_route"],
                        "source_state": transition["source_state"],
                        "target_state": transition["target_state"],
                        "source_packet_reference": source_packet.name,
                        "source_packet_sha256": sha256(source_packet),
                        "source_acceptance_receipt_reference": acceptance_reference,
                        "source_acceptance_receipt_sha256": acceptance_sha256,
                        "required_bindings": bindings,
                        "human_decision_receipt_reference": human_reference,
                        "human_decision_receipt_sha256": human_sha256,
                        "target_skill": transition["target_skill"],
                        "target_route": transition["target_route"],
                        "allowed_next_actions": transition["allowed_next_actions"],
                    }
                    payload = write(
                        "payload.json",
                        {
                            transition["payload_root"]: {
                                "company_id": company_id,
                                "customer_id": customer_id,
                                "customer_flow_link_v1": flow_link,
                            }
                        },
                    )
                    envelope = write(
                        "envelope.json",
                        {
                            "handoff_envelope_v1": {
                                "contract_version": "1.0",
                                "handoff_id": f"HANDOFF-{index:03d}",
                                "company_id": company_id,
                                "target_skill": transition["target_skill"],
                                "target_route": transition["target_route"],
                                "payload_reference": payload.name,
                                "payload_sha256": sha256(payload),
                                "allowed_writes": [],
                            }
                        },
                    )
                    accepted = write(
                        "accepted.json", {"accepted_handoff_ids": []}
                    )

                    result = subprocess.run(
                        [
                            sys.executable,
                            str(VALIDATOR),
                            "--envelope",
                            str(envelope),
                            "--expected-company-id",
                            company_id,
                            "--expected-target-skill",
                            transition["target_skill"],
                            "--expected-target-route",
                            transition["target_route"],
                            "--accepted-handoff-registry",
                            str(accepted),
                        ],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(0, result.returncode, result.stdout)

    def test_registry_has_no_skip_edge_or_duplicate_signature(self):
        transitions = json.loads(
            TRANSITION_REGISTRY.read_text(encoding="utf-8")
        )["transitions"]
        signatures = []
        for transition in transitions.values():
            signature = (
                transition["source_skill"],
                transition["source_route"],
                transition["source_state"],
                transition["target_skill"],
                transition["target_route"],
                transition["target_state"],
            )
            signatures.append(signature)
            self.assertFalse(
                transition["source_skill"]
                == "foreign-trade-customer-development"
                and transition["target_skill"]
                == "foreign-trade-customer-communication"
            )
        self.assertEqual(len(signatures), len(set(signatures)))


if __name__ == "__main__":
    unittest.main()
