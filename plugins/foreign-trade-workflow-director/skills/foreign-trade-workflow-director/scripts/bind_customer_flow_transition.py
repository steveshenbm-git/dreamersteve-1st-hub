#!/usr/bin/env python3
"""Create a new bound customer-flow payload and envelope without overwriting files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import validate_customer_flow_transition as contract


class BindFailure(Exception):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise BindFailure("INPUT_NOT_READABLE") from error


def package_reference(path: Path, package_dir: Path) -> str:
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise BindFailure("INPUT_NOT_READABLE") from error
    if path.is_symlink() or not resolved.is_file():
        raise BindFailure("INPUT_REFERENCE_INVALID")
    try:
        relative = resolved.relative_to(package_dir)
    except ValueError as error:
        raise BindFailure("INPUT_REFERENCE_OUTSIDE_PACKAGE") from error
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise BindFailure("INPUT_REFERENCE_INVALID")
    return relative.as_posix()


def parse_binding(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise BindFailure("BINDING_ARGUMENT_INVALID")
    role, raw_path = value.split("=", 1)
    if not role or role != role.strip() or not raw_path:
        raise BindFailure("BINDING_ARGUMENT_INVALID")
    return role, Path(raw_path)


def write_new_json(path: Path, document: dict[str, Any]) -> None:
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(document, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except FileExistsError as error:
        raise BindFailure("OUTPUT_ALREADY_EXISTS") from error
    except OSError as error:
        raise BindFailure("OUTPUT_NOT_WRITABLE") from error


def build(args: argparse.Namespace) -> dict[str, Any]:
    registry = contract.load_transition_contract()
    transitions = registry["transitions"]
    binding_contracts = registry["binding_contracts"]
    transition = transitions.get(args.transition_id)
    if transition is None:
        raise BindFailure("FLOW_TRANSITION_UNSUPPORTED")

    output_payload = Path(args.output_payload)
    output_envelope = Path(args.output_envelope)
    if output_payload.exists() or output_envelope.exists():
        raise BindFailure("OUTPUT_ALREADY_EXISTS")
    try:
        payload_parent = output_payload.parent.resolve(strict=True)
        envelope_parent = output_envelope.parent.resolve(strict=True)
    except OSError as error:
        raise BindFailure("OUTPUT_DIRECTORY_NOT_READABLE") from error
    if payload_parent != envelope_parent:
        raise BindFailure("OUTPUT_DIRECTORY_MISMATCH")
    package_dir = envelope_parent

    payload_path = Path(args.payload)
    package_reference(payload_path, package_dir)
    try:
        payload_raw = payload_path.read_bytes()
    except OSError as error:
        raise BindFailure("INPUT_NOT_READABLE") from error
    try:
        payload = contract.parse_json_bytes(payload_raw, "PAYLOAD_NOT_READABLE")
    except contract.ContractFailure as error:
        raise BindFailure(error.reason_code) from error
    payload_root = transition["payload_root"]
    if not isinstance(payload, dict) or set(payload) != {payload_root}:
        raise BindFailure("PAYLOAD_CONTRACT_MISMATCH")
    inner = payload[payload_root]
    if not isinstance(inner, dict) or "customer_flow_link_v1" in inner:
        raise BindFailure("PAYLOAD_SCHEMA_INVALID")
    try:
        company_id = contract.require_text(
            inner.get("company_id"), "PAYLOAD_SCHEMA_INVALID"
        )
        customer_id = contract.require_text(
            inner.get("customer_id"), "PAYLOAD_SCHEMA_INVALID"
        )
    except contract.ContractFailure as error:
        raise BindFailure(error.reason_code) from error

    source_packet = Path(args.source_packet)
    source_reference = package_reference(source_packet, package_dir)
    try:
        source_raw = source_packet.read_bytes()
    except OSError as error:
        raise BindFailure("INPUT_NOT_READABLE") from error
    source_record = contract.validate_source_packet(
        source_raw,
        company_id=company_id,
        customer_id=customer_id,
        transition=transition,
    )
    source_packet_sha256 = hashlib.sha256(source_raw).hexdigest()
    if transition["source_acceptance_receipt_required"]:
        contract.read_bound_bytes(
            output_envelope,
            source_record["accepted_input_payload_reference"],
            source_record["accepted_input_payload_sha256"],
            invalid_reason="SOURCE_ACCEPTED_INPUT_REFERENCE_INVALID",
            unreadable_reason="SOURCE_ACCEPTED_INPUT_NOT_READABLE",
            hash_reason="SOURCE_ACCEPTED_INPUT_HASH_MISMATCH",
        )

    parsed_bindings = [parse_binding(value) for value in args.binding]
    binding_map: dict[str, Path] = {}
    for role, path in parsed_bindings:
        if role in binding_map:
            raise BindFailure("BINDING_ARGUMENT_INVALID")
        binding_map[role] = path
    expected_roles = transition["required_binding_roles"]
    if set(binding_map) != set(expected_roles):
        raise BindFailure("FLOW_REQUIRED_BINDING_MISMATCH")
    bindings: list[dict[str, str]] = []
    for role in expected_roles:
        binding_path = binding_map[role]
        binding_reference = package_reference(binding_path, package_dir)
        try:
            binding_raw = binding_path.read_bytes()
        except OSError as error:
            raise BindFailure("INPUT_NOT_READABLE") from error
        contract.validate_binding_record(
            binding_raw,
            expected_root=binding_contracts[role],
            company_id=company_id,
            customer_id=customer_id,
        )
        bindings.append(
            {
                "role": role,
                "reference": binding_reference,
                "sha256": hashlib.sha256(binding_raw).hexdigest(),
            }
        )

    acceptance_reference: str | None = None
    acceptance_sha256: str | None = None
    if transition["source_acceptance_receipt_required"]:
        if args.source_acceptance_receipt is None:
            raise BindFailure("SOURCE_ACCEPTANCE_RECEIPT_REQUIRED")
        acceptance_path = Path(args.source_acceptance_receipt)
        acceptance_reference = package_reference(acceptance_path, package_dir)
        try:
            acceptance_raw = acceptance_path.read_bytes()
        except OSError as error:
            raise BindFailure("INPUT_NOT_READABLE") from error
        contract.validate_acceptance_receipt(
            acceptance_raw,
            company_id=company_id,
            customer_id=customer_id,
            transition=transition,
            expected_handoff_id=source_record["accepted_input_handoff_id"],
            expected_payload_sha256=source_record[
                "accepted_input_payload_sha256"
            ],
        )
        acceptance_sha256 = hashlib.sha256(acceptance_raw).hexdigest()
    elif args.source_acceptance_receipt is not None:
        raise BindFailure("SOURCE_ACCEPTANCE_RECEIPT_UNEXPECTED")

    human_reference: str | None = None
    human_sha256: str | None = None
    if transition["human_decision_receipt_required"]:
        if args.human_decision_receipt is None:
            raise BindFailure("HUMAN_DECISION_RECEIPT_REQUIRED")
        human_path = Path(args.human_decision_receipt)
        human_reference = package_reference(human_path, package_dir)
        try:
            human_raw = human_path.read_bytes()
        except OSError as error:
            raise BindFailure("INPUT_NOT_READABLE") from error
        contract.validate_human_decision_receipt(
            human_raw,
            company_id=company_id,
            customer_id=customer_id,
            transition=transition,
        )
        human_sha256 = hashlib.sha256(human_raw).hexdigest()
    elif args.human_decision_receipt is not None:
        raise BindFailure("HUMAN_DECISION_RECEIPT_UNEXPECTED")

    inner["customer_flow_link_v1"] = {
        "contract_version": "1.0",
        "transition_id": args.transition_id,
        "company_id": company_id,
        "customer_id": customer_id,
        "source_skill": transition["source_skill"],
        "source_route": transition["source_route"],
        "source_state": transition["source_state"],
        "target_state": transition["target_state"],
        "source_packet_reference": source_reference,
        "source_packet_sha256": source_packet_sha256,
        "source_acceptance_receipt_reference": acceptance_reference,
        "source_acceptance_receipt_sha256": acceptance_sha256,
        "required_bindings": bindings,
        "human_decision_receipt_reference": human_reference,
        "human_decision_receipt_sha256": human_sha256,
        "target_skill": transition["target_skill"],
        "target_route": transition["target_route"],
        "allowed_next_actions": transition["allowed_next_actions"],
    }

    payload_created = False
    try:
        write_new_json(output_payload, payload)
        payload_created = True
        payload_reference = package_reference(output_payload, package_dir)
        envelope = {
            "handoff_envelope_v1": {
                "contract_version": "1.0",
                "handoff_id": args.handoff_id,
                "company_id": company_id,
                "target_skill": transition["target_skill"],
                "target_route": transition["target_route"],
                "payload_reference": payload_reference,
                "payload_sha256": sha256(output_payload),
                "allowed_writes": [],
            }
        }
        write_new_json(output_envelope, envelope)
    except Exception:
        if payload_created and not output_envelope.exists():
            try:
                output_payload.unlink()
            except OSError:
                pass
        raise

    return {
        "result": "PASS",
        "reason_codes": [],
        "handoff_id": args.handoff_id,
        "transition_id": args.transition_id,
        "payload_reference": output_payload.name,
        "envelope_reference": output_envelope.name,
        "write_status": "new_files_written",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transition-id", required=True)
    parser.add_argument("--handoff-id", required=True)
    parser.add_argument("--payload", required=True)
    parser.add_argument("--source-packet", required=True)
    parser.add_argument("--binding", action="append", default=[])
    parser.add_argument("--source-acceptance-receipt")
    parser.add_argument("--human-decision-receipt")
    parser.add_argument("--output-payload", required=True)
    parser.add_argument("--output-envelope", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = build(args)
        exit_code = 0
    except (BindFailure, contract.ContractFailure) as failure:
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
