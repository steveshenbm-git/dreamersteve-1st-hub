#!/usr/bin/env python3
"""Read-only validation for one bound customer-flow transition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
TRANSITION_REGISTRY_PATH = (
    SKILL_ROOT / "assets" / "customer-flow-transition-registry.v1.json"
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ENVELOPE_FIELDS = {
    "contract_version",
    "handoff_id",
    "company_id",
    "target_skill",
    "target_route",
    "payload_reference",
    "payload_sha256",
    "allowed_writes",
}
FLOW_LINK_FIELDS = {
    "contract_version",
    "transition_id",
    "company_id",
    "customer_id",
    "source_skill",
    "source_route",
    "source_state",
    "target_state",
    "source_packet_reference",
    "source_packet_sha256",
    "source_acceptance_receipt_reference",
    "source_acceptance_receipt_sha256",
    "required_bindings",
    "human_decision_receipt_reference",
    "human_decision_receipt_sha256",
    "target_skill",
    "target_route",
    "allowed_next_actions",
}
BINDING_FIELDS = {"role", "reference", "sha256"}
ACCEPTANCE_RECEIPT_FIELDS = {
    "contract_version",
    "handoff_id",
    "company_id",
    "customer_id",
    "receiver_skill",
    "receiver_route",
    "accepted_payload_sha256",
    "result",
    "accepted_at",
}
HUMAN_DECISION_FIELDS = {
    "contract_version",
    "decision_id",
    "company_id",
    "customer_id",
    "decision_type",
    "decision_state",
    "recorded_at",
}
REGISTRY_FIELDS = {
    "contract_name",
    "contract_version",
    "binding_contracts",
    "transitions",
}
TRANSITION_FIELDS = {
    "source_skill",
    "source_route",
    "source_state",
    "source_packet_root",
    "source_state_field",
    "target_skill",
    "target_route",
    "target_state",
    "payload_root",
    "required_binding_roles",
    "source_acceptance_receipt_required",
    "human_decision_receipt_required",
    "human_decision_types",
    "allowed_next_actions",
}


class ContractFailure(Exception):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractFailure("JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def parse_json_bytes(raw: bytes, reason_code: str) -> Any:
    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except ContractFailure:
        raise
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ContractFailure(reason_code) from error


def read_json(path: Path, reason_code: str) -> Any:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise ContractFailure(reason_code) from error
    return parse_json_bytes(raw, reason_code)


def require_text(value: Any, reason_code: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ContractFailure(reason_code)
    return value


def require_sha256(value: Any, reason_code: str) -> str:
    value = require_text(value, reason_code)
    if not SHA256_PATTERN.fullmatch(value):
        raise ContractFailure(reason_code)
    return value


def resolve_bound_file(
    envelope_path: Path,
    reference: Any,
    *,
    invalid_reason: str,
    unreadable_reason: str,
) -> Path:
    reference = require_text(reference, invalid_reason)
    if "\\" in reference:
        raise ContractFailure(invalid_reason)
    pure_reference = PurePosixPath(reference)
    if pure_reference.is_absolute() or any(
        part in {"", ".", ".."} for part in pure_reference.parts
    ):
        raise ContractFailure(invalid_reason)

    envelope_dir = envelope_path.parent.resolve()
    candidate = envelope_dir.joinpath(*pure_reference.parts)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise ContractFailure(unreadable_reason) from error
    if not resolved.is_relative_to(envelope_dir):
        raise ContractFailure(invalid_reason)

    current = envelope_dir
    for part in pure_reference.parts:
        current = current / part
        if current.is_symlink():
            raise ContractFailure(invalid_reason)
    if not resolved.is_file():
        raise ContractFailure(unreadable_reason)
    return resolved


def read_bound_bytes(
    envelope_path: Path,
    reference: Any,
    expected_sha256: Any,
    *,
    invalid_reason: str,
    unreadable_reason: str,
    hash_reason: str,
) -> tuple[Path, bytes]:
    path = resolve_bound_file(
        envelope_path,
        reference,
        invalid_reason=invalid_reason,
        unreadable_reason=unreadable_reason,
    )
    expected_sha256 = require_sha256(expected_sha256, invalid_reason)
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise ContractFailure(unreadable_reason) from error
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ContractFailure(hash_reason)
    return path, raw


def load_transition_contract() -> dict[str, Any]:
    registry = read_json(TRANSITION_REGISTRY_PATH, "FLOW_REGISTRY_NOT_READABLE")
    if (
        not isinstance(registry, dict)
        or set(registry) != REGISTRY_FIELDS
        or registry["contract_name"] != "customer_flow_transition_registry"
        or registry["contract_version"] != "1.0"
        or not isinstance(registry["binding_contracts"], dict)
        or not isinstance(registry["transitions"], dict)
    ):
        raise ContractFailure("FLOW_REGISTRY_INVALID")
    binding_contracts = registry["binding_contracts"]
    if not binding_contracts or any(
        not isinstance(role, str)
        or not role
        or not isinstance(root, str)
        or not root
        for role, root in binding_contracts.items()
    ):
        raise ContractFailure("FLOW_REGISTRY_INVALID")
    transitions = registry["transitions"]
    if not transitions:
        raise ContractFailure("FLOW_REGISTRY_INVALID")
    for transition_id, transition in transitions.items():
        if (
            not isinstance(transition_id, str)
            or not transition_id
            or not isinstance(transition, dict)
            or set(transition) != TRANSITION_FIELDS
        ):
            raise ContractFailure("FLOW_REGISTRY_INVALID")
        text_fields = (
            "source_skill",
            "source_route",
            "source_state",
            "source_packet_root",
            "source_state_field",
            "target_skill",
            "target_route",
            "target_state",
            "payload_root",
        )
        if any(
            not isinstance(transition[field], str) or not transition[field]
            for field in text_fields
        ):
            raise ContractFailure("FLOW_REGISTRY_INVALID")
        roles = transition["required_binding_roles"]
        actions = transition["allowed_next_actions"]
        decision_types = transition["human_decision_types"]
        if (
            not isinstance(roles, list)
            or len(roles) != len(set(roles))
            or any(role not in binding_contracts for role in roles)
            or not isinstance(actions, list)
            or not actions
            or len(actions) != len(set(actions))
            or any(not isinstance(action, str) or not action for action in actions)
            or not isinstance(decision_types, list)
            or len(decision_types) != len(set(decision_types))
            or any(
                not isinstance(decision_type, str) or not decision_type
                for decision_type in decision_types
            )
            or not isinstance(
                transition["source_acceptance_receipt_required"], bool
            )
            or not isinstance(
                transition["human_decision_receipt_required"], bool
            )
            or transition["human_decision_receipt_required"]
            != bool(decision_types)
        ):
            raise ContractFailure("FLOW_REGISTRY_INVALID")
    return registry


def load_transition_registry() -> dict[str, dict[str, Any]]:
    return load_transition_contract()["transitions"]


def route_payload_contracts(
    transitions: dict[str, dict[str, Any]],
) -> dict[tuple[str, str], set[str]]:
    contracts: dict[tuple[str, str], set[str]] = {}
    for transition in transitions.values():
        if not isinstance(transition, dict):
            raise ContractFailure("FLOW_REGISTRY_INVALID")
        try:
            key = (transition["target_skill"], transition["target_route"])
            payload_root = transition["payload_root"]
        except KeyError as error:
            raise ContractFailure("FLOW_REGISTRY_INVALID") from error
        if not all(isinstance(value, str) and value for value in (*key, payload_root)):
            raise ContractFailure("FLOW_REGISTRY_INVALID")
        contracts.setdefault(key, set()).add(payload_root)
    return contracts


def validate_acceptance_receipt(
    raw: bytes,
    *,
    company_id: str,
    customer_id: str,
    transition: dict[str, Any],
    expected_handoff_id: str,
    expected_payload_sha256: str,
) -> None:
    document = parse_json_bytes(raw, "SOURCE_ACCEPTANCE_RECEIPT_INVALID")
    if not isinstance(document, dict) or set(document) != {
        "handoff_acceptance_receipt_v1"
    }:
        raise ContractFailure("SOURCE_ACCEPTANCE_RECEIPT_INVALID")
    receipt = document["handoff_acceptance_receipt_v1"]
    if not isinstance(receipt, dict) or set(receipt) != ACCEPTANCE_RECEIPT_FIELDS:
        raise ContractFailure("SOURCE_ACCEPTANCE_RECEIPT_INVALID")
    if (
        receipt["contract_version"] != "1.0"
        or receipt["company_id"] != company_id
        or receipt["customer_id"] != customer_id
        or receipt["receiver_skill"] != transition["source_skill"]
        or receipt["receiver_route"] != transition["source_route"]
        or receipt["result"] != "PASS"
    ):
        raise ContractFailure("SOURCE_ACCEPTANCE_RECEIPT_MISMATCH")
    handoff_id = require_text(
        receipt["handoff_id"], "SOURCE_ACCEPTANCE_RECEIPT_INVALID"
    )
    if handoff_id != expected_handoff_id:
        raise ContractFailure("SOURCE_ACCEPTANCE_HANDOFF_MISMATCH")
    accepted_payload_sha256 = require_sha256(
        receipt["accepted_payload_sha256"],
        "SOURCE_ACCEPTANCE_RECEIPT_INVALID",
    )
    if accepted_payload_sha256 != expected_payload_sha256:
        raise ContractFailure("SOURCE_ACCEPTANCE_PAYLOAD_MISMATCH")
    require_text(receipt["accepted_at"], "SOURCE_ACCEPTANCE_RECEIPT_INVALID")


def validate_human_decision_receipt(
    raw: bytes,
    *,
    company_id: str,
    customer_id: str,
    transition: dict[str, Any],
) -> None:
    document = parse_json_bytes(raw, "HUMAN_DECISION_RECEIPT_INVALID")
    if not isinstance(document, dict) or set(document) != {
        "human_decision_receipt_v1"
    }:
        raise ContractFailure("HUMAN_DECISION_RECEIPT_INVALID")
    receipt = document["human_decision_receipt_v1"]
    if not isinstance(receipt, dict) or set(receipt) != HUMAN_DECISION_FIELDS:
        raise ContractFailure("HUMAN_DECISION_RECEIPT_INVALID")
    if (
        receipt["contract_version"] != "1.0"
        or receipt["company_id"] != company_id
        or receipt["customer_id"] != customer_id
        or receipt["decision_state"] != "CONFIRMED"
    ):
        raise ContractFailure("HUMAN_DECISION_RECEIPT_MISMATCH")
    for field in ("decision_id", "decision_type", "recorded_at"):
        require_text(receipt[field], "HUMAN_DECISION_RECEIPT_INVALID")
    if receipt["decision_type"] not in transition["human_decision_types"]:
        raise ContractFailure("HUMAN_DECISION_TYPE_MISMATCH")


def validate_source_packet(
    raw: bytes,
    *,
    company_id: str,
    customer_id: str,
    transition: dict[str, Any],
) -> dict[str, Any]:
    document = parse_json_bytes(raw, "FLOW_SOURCE_PACKET_INVALID")
    expected_root = transition["source_packet_root"]
    if not isinstance(document, dict) or set(document) != {expected_root}:
        raise ContractFailure("FLOW_SOURCE_CONTRACT_MISMATCH")
    source = document[expected_root]
    if not isinstance(source, dict):
        raise ContractFailure("FLOW_SOURCE_PACKET_INVALID")
    if source.get("company_id") != company_id or source.get("customer_id") != customer_id:
        raise ContractFailure("FLOW_SOURCE_IDENTITY_MISMATCH")
    if source.get(transition["source_state_field"]) != transition["source_state"]:
        raise ContractFailure("FLOW_SOURCE_STATE_MISMATCH")
    if transition["source_acceptance_receipt_required"]:
        require_text(
            source.get("accepted_input_handoff_id"),
            "FLOW_SOURCE_PACKET_INVALID",
        )
        require_text(
            source.get("accepted_input_payload_reference"),
            "FLOW_SOURCE_PACKET_INVALID",
        )
        require_sha256(
            source.get("accepted_input_payload_sha256"),
            "FLOW_SOURCE_PACKET_INVALID",
        )
    return source


def validate_binding_record(
    raw: bytes,
    *,
    expected_root: str,
    company_id: str,
    customer_id: str,
) -> None:
    document = parse_json_bytes(raw, "FLOW_BINDING_CONTRACT_MISMATCH")
    if not isinstance(document, dict) or set(document) != {expected_root}:
        raise ContractFailure("FLOW_BINDING_CONTRACT_MISMATCH")
    record = document[expected_root]
    if not isinstance(record, dict):
        raise ContractFailure("FLOW_BINDING_CONTRACT_MISMATCH")
    if record.get("company_id") != company_id or record.get("customer_id") != customer_id:
        raise ContractFailure("FLOW_BINDING_IDENTITY_MISMATCH")


def validate(args: argparse.Namespace) -> dict[str, Any]:
    envelope_path = Path(args.envelope).resolve()
    document = read_json(envelope_path, "ENVELOPE_NOT_READABLE")
    if not isinstance(document, dict) or set(document) != {"handoff_envelope_v1"}:
        raise ContractFailure("ENVELOPE_SCHEMA_INVALID")
    envelope = document["handoff_envelope_v1"]
    if not isinstance(envelope, dict) or set(envelope) != ENVELOPE_FIELDS:
        raise ContractFailure("ENVELOPE_SCHEMA_INVALID")
    if envelope["contract_version"] != "1.0":
        raise ContractFailure("CONTRACT_VERSION_UNSUPPORTED")

    handoff_id = require_text(envelope["handoff_id"], "ENVELOPE_SCHEMA_INVALID")
    company_id = require_text(envelope["company_id"], "ENVELOPE_SCHEMA_INVALID")
    target_skill = require_text(
        envelope["target_skill"], "ENVELOPE_SCHEMA_INVALID"
    )
    target_route = require_text(
        envelope["target_route"], "ENVELOPE_SCHEMA_INVALID"
    )
    if company_id != args.expected_company_id:
        raise ContractFailure("COMPANY_ID_MISMATCH")
    if target_skill != args.expected_target_skill:
        raise ContractFailure("TARGET_SKILL_MISMATCH")
    if target_route != args.expected_target_route:
        raise ContractFailure("TARGET_ROUTE_MISMATCH")
    if not isinstance(envelope["allowed_writes"], list):
        raise ContractFailure("ENVELOPE_SCHEMA_INVALID")
    if envelope["allowed_writes"]:
        raise ContractFailure("ALLOWED_WRITES_NOT_AUTHORIZED")

    registry = load_transition_contract()
    transitions = registry["transitions"]
    binding_contracts = registry["binding_contracts"]
    allowed_payload_roots = route_payload_contracts(transitions).get(
        (target_skill, target_route)
    )
    if allowed_payload_roots is None:
        raise ContractFailure("TARGET_CONTRACT_UNSUPPORTED")

    _, payload_raw = read_bound_bytes(
        envelope_path,
        envelope["payload_reference"],
        envelope["payload_sha256"],
        invalid_reason="PAYLOAD_REFERENCE_INVALID",
        unreadable_reason="PAYLOAD_NOT_READABLE",
        hash_reason="PAYLOAD_HASH_MISMATCH",
    )
    payload = parse_json_bytes(payload_raw, "PAYLOAD_NOT_READABLE")
    if not isinstance(payload, dict) or len(payload) != 1:
        raise ContractFailure("PAYLOAD_CONTRACT_MISMATCH")
    payload_root = next(iter(payload))
    if payload_root not in allowed_payload_roots:
        raise ContractFailure("PAYLOAD_CONTRACT_MISMATCH")
    inner = payload[payload_root]
    if not isinstance(inner, dict):
        raise ContractFailure("PAYLOAD_SCHEMA_INVALID")
    if inner.get("company_id") != company_id:
        raise ContractFailure("PAYLOAD_COMPANY_ID_MISMATCH")
    customer_id = require_text(inner.get("customer_id"), "PAYLOAD_SCHEMA_INVALID")

    flow = inner.get("customer_flow_link_v1")
    if not isinstance(flow, dict) or set(flow) != FLOW_LINK_FIELDS:
        raise ContractFailure("FLOW_LINK_SCHEMA_INVALID")
    if flow["contract_version"] != "1.0":
        raise ContractFailure("FLOW_CONTRACT_VERSION_UNSUPPORTED")
    transition_id = require_text(
        flow["transition_id"], "FLOW_LINK_SCHEMA_INVALID"
    )
    transition = transitions.get(transition_id)
    if transition is None:
        raise ContractFailure("FLOW_TRANSITION_UNSUPPORTED")
    if flow["company_id"] != company_id or flow["customer_id"] != customer_id:
        raise ContractFailure("FLOW_IDENTITY_MISMATCH")

    expected_source = (
        transition["source_skill"],
        transition["source_route"],
        transition["source_state"],
    )
    actual_source = (
        flow["source_skill"],
        flow["source_route"],
        flow["source_state"],
    )
    if actual_source != expected_source:
        raise ContractFailure("FLOW_SOURCE_MISMATCH")
    if (
        flow["target_skill"] != transition["target_skill"]
        or flow["target_route"] != transition["target_route"]
        or flow["target_state"] != transition["target_state"]
        or flow["target_skill"] != target_skill
        or flow["target_route"] != target_route
        or payload_root != transition["payload_root"]
    ):
        raise ContractFailure("FLOW_TARGET_MISMATCH")
    if flow["allowed_next_actions"] != transition["allowed_next_actions"]:
        raise ContractFailure("FLOW_ACTION_SCOPE_MISMATCH")

    _, source_raw = read_bound_bytes(
        envelope_path,
        flow["source_packet_reference"],
        flow["source_packet_sha256"],
        invalid_reason="FLOW_SOURCE_REFERENCE_INVALID",
        unreadable_reason="FLOW_SOURCE_NOT_READABLE",
        hash_reason="FLOW_SOURCE_HASH_MISMATCH",
    )
    source_packet = validate_source_packet(
        source_raw,
        company_id=company_id,
        customer_id=customer_id,
        transition=transition,
    )

    if transition["source_acceptance_receipt_required"]:
        read_bound_bytes(
            envelope_path,
            source_packet["accepted_input_payload_reference"],
            source_packet["accepted_input_payload_sha256"],
            invalid_reason="SOURCE_ACCEPTED_INPUT_REFERENCE_INVALID",
            unreadable_reason="SOURCE_ACCEPTED_INPUT_NOT_READABLE",
            hash_reason="SOURCE_ACCEPTED_INPUT_HASH_MISMATCH",
        )

    acceptance_required = transition["source_acceptance_receipt_required"]
    acceptance_reference = flow["source_acceptance_receipt_reference"]
    acceptance_sha256 = flow["source_acceptance_receipt_sha256"]
    if acceptance_required:
        if acceptance_reference is None or acceptance_sha256 is None:
            raise ContractFailure("SOURCE_ACCEPTANCE_RECEIPT_REQUIRED")
        _, acceptance_raw = read_bound_bytes(
            envelope_path,
            acceptance_reference,
            acceptance_sha256,
            invalid_reason="SOURCE_ACCEPTANCE_RECEIPT_INVALID",
            unreadable_reason="SOURCE_ACCEPTANCE_RECEIPT_NOT_READABLE",
            hash_reason="SOURCE_ACCEPTANCE_RECEIPT_HASH_MISMATCH",
        )
        validate_acceptance_receipt(
            acceptance_raw,
            company_id=company_id,
            customer_id=customer_id,
            transition=transition,
            expected_handoff_id=source_packet["accepted_input_handoff_id"],
            expected_payload_sha256=source_packet[
                "accepted_input_payload_sha256"
            ],
        )
    elif acceptance_reference is not None or acceptance_sha256 is not None:
        raise ContractFailure("SOURCE_ACCEPTANCE_RECEIPT_UNEXPECTED")

    bindings = flow["required_bindings"]
    if not isinstance(bindings, list):
        raise ContractFailure("FLOW_BINDING_SCHEMA_INVALID")
    binding_roles: list[str] = []
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != BINDING_FIELDS:
            raise ContractFailure("FLOW_BINDING_SCHEMA_INVALID")
        role = require_text(binding["role"], "FLOW_BINDING_SCHEMA_INVALID")
        binding_roles.append(role)
        _, binding_raw = read_bound_bytes(
            envelope_path,
            binding["reference"],
            binding["sha256"],
            invalid_reason="FLOW_BINDING_REFERENCE_INVALID",
            unreadable_reason="FLOW_BINDING_NOT_READABLE",
            hash_reason="FLOW_BINDING_HASH_MISMATCH",
        )
        validate_binding_record(
            binding_raw,
            expected_root=binding_contracts[role],
            company_id=company_id,
            customer_id=customer_id,
        )
    if len(binding_roles) != len(set(binding_roles)):
        raise ContractFailure("FLOW_BINDING_SCHEMA_INVALID")
    if set(binding_roles) != set(transition["required_binding_roles"]):
        raise ContractFailure("FLOW_REQUIRED_BINDING_MISMATCH")

    human_required = transition["human_decision_receipt_required"]
    human_reference = flow["human_decision_receipt_reference"]
    human_sha256 = flow["human_decision_receipt_sha256"]
    if human_required:
        if human_reference is None or human_sha256 is None:
            raise ContractFailure("HUMAN_DECISION_RECEIPT_REQUIRED")
        _, human_raw = read_bound_bytes(
            envelope_path,
            human_reference,
            human_sha256,
            invalid_reason="HUMAN_DECISION_RECEIPT_INVALID",
            unreadable_reason="HUMAN_DECISION_RECEIPT_NOT_READABLE",
            hash_reason="HUMAN_DECISION_RECEIPT_HASH_MISMATCH",
        )
        validate_human_decision_receipt(
            human_raw,
            company_id=company_id,
            customer_id=customer_id,
            transition=transition,
        )
    elif human_reference is not None or human_sha256 is not None:
        raise ContractFailure("HUMAN_DECISION_RECEIPT_UNEXPECTED")

    acceptance_registry = read_json(
        Path(args.accepted_handoff_registry).resolve(),
        "ACCEPTANCE_REGISTRY_NOT_READABLE",
    )
    if (
        not isinstance(acceptance_registry, dict)
        or set(acceptance_registry) != {"accepted_handoff_ids"}
        or not isinstance(acceptance_registry["accepted_handoff_ids"], list)
        or any(
            not isinstance(item, str) or not item
            for item in acceptance_registry["accepted_handoff_ids"]
        )
        or len(acceptance_registry["accepted_handoff_ids"])
        != len(set(acceptance_registry["accepted_handoff_ids"]))
    ):
        raise ContractFailure("ACCEPTANCE_REGISTRY_INVALID")
    if handoff_id in acceptance_registry["accepted_handoff_ids"]:
        raise ContractFailure("HANDOFF_ID_ALREADY_ACCEPTED")

    return {
        "result": "PASS",
        "reason_codes": [],
        "handoff_id": handoff_id,
        "company_id": company_id,
        "customer_id": customer_id,
        "transition_id": transition_id,
        "target_skill": target_skill,
        "target_route": target_route,
        "payload_reference": envelope["payload_reference"],
        "payload_sha256": envelope["payload_sha256"],
        "write_status": "not_written",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", required=True)
    parser.add_argument("--expected-company-id", required=True)
    parser.add_argument("--expected-target-skill", required=True)
    parser.add_argument("--expected-target-route", required=True)
    parser.add_argument("--accepted-handoff-registry", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = validate(args)
        exit_code = 0
    except ContractFailure as failure:
        result = {
            "result": "FAIL",
            "reason_codes": [failure.reason_code],
            "write_status": "not_written",
        }
        exit_code = 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
