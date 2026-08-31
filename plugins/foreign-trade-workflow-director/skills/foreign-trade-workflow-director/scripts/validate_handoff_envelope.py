#!/usr/bin/env python3
"""Read-only validation for a bound cross-skill handoff envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


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
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ROUTE_PAYLOAD_CONTRACTS = {
    (
        "foreign-trade-customer-operations",
        "cold_outreach",
    ): "outreach_handoff_packet",
    (
        "foreign-trade-customer-operations",
        "reply_communication",
    ): "customer_operations_handoff",
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


def load_json(path: Path, reason_code: str) -> Any:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise ContractFailure(reason_code) from error
    return parse_json_bytes(raw, reason_code)


def require_nonempty_text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ContractFailure("ENVELOPE_SCHEMA_INVALID")
    return value


def resolve_payload_path(envelope_path: Path, reference: Any) -> Path:
    reference = require_nonempty_text(reference)
    if "\\" in reference:
        raise ContractFailure("PAYLOAD_REFERENCE_INVALID")
    pure_reference = PurePosixPath(reference)
    if pure_reference.is_absolute() or any(
        part in {"", ".", ".."} for part in pure_reference.parts
    ):
        raise ContractFailure("PAYLOAD_REFERENCE_INVALID")

    envelope_dir = envelope_path.parent.resolve()
    payload_path = envelope_dir.joinpath(*pure_reference.parts)
    try:
        resolved_payload = payload_path.resolve(strict=True)
    except OSError as error:
        raise ContractFailure("PAYLOAD_NOT_READABLE") from error
    if not resolved_payload.is_relative_to(envelope_dir):
        raise ContractFailure("PAYLOAD_REFERENCE_INVALID")

    current = envelope_dir
    for part in pure_reference.parts:
        current = current / part
        if current.is_symlink():
            raise ContractFailure("PAYLOAD_REFERENCE_INVALID")
    if not resolved_payload.is_file():
        raise ContractFailure("PAYLOAD_NOT_READABLE")
    return resolved_payload


def extract_payload_company_id(payload: Any, expected_root: str) -> str:
    if not isinstance(payload, dict) or set(payload) != {expected_root}:
        raise ContractFailure("PAYLOAD_CONTRACT_MISMATCH")
    inner = payload[expected_root]
    if not isinstance(inner, dict) or "company_id" not in inner:
        raise ContractFailure("PAYLOAD_SCHEMA_INVALID")
    return require_nonempty_text(inner["company_id"])


def validate(args: argparse.Namespace) -> dict[str, Any]:
    envelope_path = Path(args.envelope).resolve()
    document = load_json(envelope_path, "ENVELOPE_NOT_READABLE")
    if not isinstance(document, dict) or set(document) != {"handoff_envelope_v1"}:
        raise ContractFailure("ENVELOPE_SCHEMA_INVALID")
    envelope = document["handoff_envelope_v1"]
    if not isinstance(envelope, dict) or set(envelope) != ENVELOPE_FIELDS:
        raise ContractFailure("ENVELOPE_SCHEMA_INVALID")

    if envelope["contract_version"] != "1.0":
        raise ContractFailure("CONTRACT_VERSION_UNSUPPORTED")
    handoff_id = require_nonempty_text(envelope["handoff_id"])
    company_id = require_nonempty_text(envelope["company_id"])
    target_skill = require_nonempty_text(envelope["target_skill"])
    target_route = require_nonempty_text(envelope["target_route"])
    payload_sha256 = require_nonempty_text(envelope["payload_sha256"])
    if not SHA256_PATTERN.fullmatch(payload_sha256):
        raise ContractFailure("ENVELOPE_SCHEMA_INVALID")
    if company_id != args.expected_company_id:
        raise ContractFailure("COMPANY_ID_MISMATCH")
    if target_skill != args.expected_target_skill:
        raise ContractFailure("TARGET_SKILL_MISMATCH")
    if target_route != args.expected_target_route:
        raise ContractFailure("TARGET_ROUTE_MISMATCH")
    expected_payload_root = ROUTE_PAYLOAD_CONTRACTS.get((target_skill, target_route))
    if expected_payload_root is None:
        raise ContractFailure("TARGET_CONTRACT_UNSUPPORTED")
    if not isinstance(envelope["allowed_writes"], list):
        raise ContractFailure("ENVELOPE_SCHEMA_INVALID")
    if envelope["allowed_writes"]:
        raise ContractFailure("ALLOWED_WRITES_NOT_AUTHORIZED")

    payload_path = resolve_payload_path(envelope_path, envelope["payload_reference"])
    try:
        payload_bytes = payload_path.read_bytes()
    except OSError as error:
        raise ContractFailure("PAYLOAD_NOT_READABLE") from error
    actual_payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()
    if actual_payload_sha256 != payload_sha256:
        raise ContractFailure("PAYLOAD_HASH_MISMATCH")
    payload = parse_json_bytes(payload_bytes, "PAYLOAD_NOT_READABLE")
    if extract_payload_company_id(payload, expected_payload_root) != company_id:
        raise ContractFailure("PAYLOAD_COMPANY_ID_MISMATCH")

    registry = load_json(
        Path(args.accepted_handoff_registry).resolve(),
        "ACCEPTANCE_REGISTRY_NOT_READABLE",
    )
    if not isinstance(registry, dict) or set(registry) != {"accepted_handoff_ids"}:
        raise ContractFailure("ACCEPTANCE_REGISTRY_INVALID")
    accepted_ids = registry["accepted_handoff_ids"]
    if not isinstance(accepted_ids, list) or any(
        not isinstance(item, str) or not item for item in accepted_ids
    ):
        raise ContractFailure("ACCEPTANCE_REGISTRY_INVALID")
    if len(accepted_ids) != len(set(accepted_ids)):
        raise ContractFailure("ACCEPTANCE_REGISTRY_INVALID")
    if handoff_id in accepted_ids:
        raise ContractFailure("HANDOFF_ID_ALREADY_ACCEPTED")

    return {
        "result": "PASS",
        "reason_codes": [],
        "handoff_id": handoff_id,
        "company_id": company_id,
        "target_skill": target_skill,
        "target_route": target_route,
        "payload_reference": envelope["payload_reference"],
        "payload_sha256": payload_sha256,
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
