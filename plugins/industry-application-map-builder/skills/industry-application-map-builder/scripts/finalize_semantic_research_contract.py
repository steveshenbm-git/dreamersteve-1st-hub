#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from typing import Any
from urllib.parse import unquote

from content_first_visible_case_schema import (
    SHA256,
    frozen_visible_case_errors,
    valid_case_id as shared_valid_case_id,
    visible_case_projection,
)
from r4_case_package_contract import (
    CASE_PACKAGE_CONTRACT_VERSION,
    MAP_BUILDER_PLUGIN_VERSION,
    aware_datetime,
    declared_input_path_error,
    valid_prep_to_final_version,
)
from r4_adjudicated_truth_contract import derive_truth_summary

from validate_semantic_research_workspace import (
    case_preparation_contract_completeness_errors,
    content_first_local_frozen_reference_errors,
    frozen_contract_completeness_errors,
    load_jsonl,
    nonempty_text,
    validate_content_first_case_truth_rows,
)


VISIBLE_FREEZE_RECEIPT_KEYS = {
    "receipt_id", "action", "research_contract_id", "visible_case_set_reference",
    "output_scope", "visible_case_set_sha256", "ordered_case_ids_sha256",
    "freeze_authorization_reference", "frozen_at", "truth_authorized",
    "model_execution_authorized", "full_screening_authorized",
}


def valid_case_id(value: object) -> bool:
    return shared_valid_case_id(value)


def collect_text_values(value: object) -> set[str]:
    if isinstance(value, str):
        return {unicodedata.normalize("NFKC", value).casefold()}
    if isinstance(value, dict):
        return set().union(*(collect_text_values(item) for item in value.values())) if value else set()
    if isinstance(value, list):
        return set().union(*(collect_text_values(item) for item in value)) if value else set()
    return set()


def normalized_laundering_values(value: object) -> set[str]:
    if isinstance(value, str):
        decoded = value
        for _ in range(6):
            next_value = unquote(decoded)
            if next_value == decoded:
                break
            decoded = next_value
        normalized = "".join(character for character in unicodedata.normalize("NFKC", decoded).casefold() if character.isalnum())
        return {normalized} if normalized else set()
    if isinstance(value, dict):
        return set().union(*(normalized_laundering_values(item) for item in value.values())) if value else set()
    if isinstance(value, list):
        return set().union(*(normalized_laundering_values(item) for item in value)) if value else set()
    return set()


def sealed_truth_view(truth: dict) -> dict:
    """Exclude only taxonomy facts already present in the visible case projection."""
    sealed = {
        key: value for key, value in truth.items() if key not in {"record_type", "case_id"}
    }
    bases = sealed.get("evidence_bases")
    if not isinstance(bases, dict):
        return sealed
    copied_bases = dict(bases)
    taxonomy = copied_bases.get("taxonomy_membership_basis")
    if isinstance(taxonomy, dict):
        copied_taxonomy = dict(taxonomy)
        for key in (
            "upstream_snapshot_reference",
            "upstream_snapshot_sha256",
            "upstream_node_id",
            "upstream_json_pointer",
            "original_location",
        ):
            copied_taxonomy.pop(key, None)
        copied_bases["taxonomy_membership_basis"] = copied_taxonomy
    sealed["evidence_bases"] = copied_bases
    return sealed


def validate_visible_case_set(
    visible_rows: list[dict], formal_rows: list[dict], truth_rows: list[dict], research_contract_id: object,
) -> list[str]:
    """Validate the separately frozen task-visible projection before final truth binding."""
    problems: list[str] = []
    cases = [row for row in visible_rows if row.get("record_type") == "visible_calibration_case"]
    formal_cases = [row for row in formal_rows if row.get("record_type") == "calibration_case"]
    if frozen_visible_case_errors(visible_rows, research_contract_id):
        return ["VISIBLE_CASE_SET_INVALID"]
    visible_ids = [row.get("case_id") for row in cases]
    formal_ids = [row.get("case_id") for row in formal_cases]
    if visible_ids != formal_ids:
        problems.append("VISIBLE_CASE_SET_INVALID")
    for visible, formal in zip(cases, formal_cases):
        if visible_case_projection(visible) != visible_case_projection(formal):
            problems.append("VISIBLE_CASE_SET_INVALID")
            break
    # Exact value comparison catches a truth-bearing string copied through an otherwise allowed field.
    forbidden_values: set[str] = set()
    for formal in formal_cases:
        # Treat every non-projection formal field as sealed.  Field names are
        # not a security boundary: a neutral-looking key can still carry truth.
        forbidden_values.update(collect_text_values({
            key: value for key, value in formal.items()
            if key not in {"record_type", "research_contract_id", "case_id", "taxonomy_node", "product_neutral_research_theme", "risk_flags"}
        }))
    for truth in truth_rows:
        forbidden_values.update(collect_text_values(sealed_truth_view(truth)))
    sealed_normalized: set[str] = set()
    for formal in formal_cases:
        sealed_normalized.update(normalized_laundering_values({
            key: value for key, value in formal.items()
            if key not in {"record_type", "research_contract_id", "case_id", "taxonomy_node", "product_neutral_research_theme", "risk_flags"}
        }))
    for truth in truth_rows:
        sealed_normalized.update(normalized_laundering_values(sealed_truth_view(truth)))
    sealed_normalized = {value for value in sealed_normalized if len(value) >= 6}
    for visible in cases:
        strings = collect_text_values(visible_case_projection(visible)) - {unicodedata.normalize("NFKC", str(visible.get("case_id", ""))).casefold()}
        normalized_strings = normalized_laundering_values(visible_case_projection(visible)) - normalized_laundering_values(visible.get("case_id"))
        if forbidden_values.intersection(strings) or any(sealed in candidate for sealed in sealed_normalized for candidate in normalized_strings):
            problems.append("VISIBLE_CASE_VALUE_LAUNDERING")
            break
    return problems


def fail(code: str, detail: str) -> int:
    print(
        json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False),
        file=sys.stderr,
    )
    return 1


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def publish_create_only_atomic(output: Path, body: bytes, *, fail_after_temp_write: bool) -> str | None:
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.tmp-", dir=output.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        if fail_after_temp_write:
            raise OSError("injected publish failure after complete temporary write")
        os.link(temporary, output)
        temporary.unlink()
        return None
    except FileExistsError:
        temporary.unlink(missing_ok=True)
        return "OUTPUT_EXISTS"
    except OSError:
        temporary.unlink(missing_ok=True)
        return "FINAL_CONTRACT_PUBLISH_FAILED"


def visible_freeze_receipt_error(
    receipt_path: Path, expected_sha256: object, expected_reference: object,
    visible_reference: object, visible_bytes: bytes, visible_rows: list[dict], research_contract_id: object,
) -> str | None:
    """Verify the independent pre-truth freeze receipt before truth bytes are opened."""
    if not SHA256.fullmatch(str(expected_sha256)):
        return "VISIBLE_CASE_FREEZE_RECEIPT_SHA256_INVALID"
    if not nonempty_text(expected_reference) or not receipt_path.is_file():
        return "VISIBLE_CASE_FREEZE_RECEIPT_INVALID"
    if hashlib.sha256(receipt_path.read_bytes()).hexdigest() != expected_sha256:
        return "VISIBLE_CASE_FREEZE_RECEIPT_HASH_MISMATCH"
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt = payload["visible_case_freeze_receipt"]
    except (OSError, ValueError, KeyError, TypeError):
        return "VISIBLE_CASE_FREEZE_RECEIPT_INVALID"
    header = next((row for row in visible_rows if row.get("record_type") == "visible_case_set_contract"), {})
    ordered_ids = header.get("formal_case_ids")
    if (
        not isinstance(payload, dict) or set(payload) != {"schema_version", "visible_case_freeze_receipt"}
        or payload.get("schema_version") != "1.0" or not isinstance(receipt, dict)
        or set(receipt) != VISIBLE_FREEZE_RECEIPT_KEYS
        or not nonempty_text(receipt.get("receipt_id"))
        or receipt.get("action") != "visible_case_freeze_only"
        or receipt.get("research_contract_id") != research_contract_id
        or receipt.get("visible_case_set_reference") != visible_reference
        or receipt.get("output_scope") != visible_reference
        or receipt.get("visible_case_set_sha256") != hashlib.sha256(visible_bytes).hexdigest()
        or receipt.get("ordered_case_ids_sha256") != hashlib.sha256(canonical_bytes(ordered_ids)).hexdigest()
        or receipt.get("freeze_authorization_reference") != header.get("freeze_authorization_reference")
        or receipt.get("frozen_at") != header.get("frozen_at")
        or receipt.get("truth_authorized") is not False
        or receipt.get("model_execution_authorized") is not False
        or receipt.get("full_screening_authorized") is not False
    ):
        return "VISIBLE_CASE_FREEZE_RECEIPT_INVALID"
    return None


def declared_task_visible_collision(
    contract: dict, protected_references: set[object], protected_hashes: set[object]
) -> str | None:
    """Reject declared sealed collisions before opening any task-visible artifact."""
    entries: list[tuple[object, object]] = []
    architecture = contract.get("terminology_architecture")
    if isinstance(architecture, dict):
        entries.append((architecture.get("term_pack_reference"), architecture.get("term_pack_sha256")))
    entries.append((contract.get("taxonomy_snapshot_reference"), contract.get("taxonomy_snapshot_sha256")))
    prompts = contract.get("prompt_template_references_and_hashes")
    if isinstance(prompts, list):
        entries.extend((row.get("reference"), row.get("sha256")) for row in prompts if isinstance(row, dict))
    paired = contract.get("paired_execution_contract")
    artifacts = paired.get("frozen_artifact_references_and_hashes") if isinstance(paired, dict) else None
    if isinstance(artifacts, dict):
        for rows in artifacts.values():
            if isinstance(rows, list):
                entries.extend((row.get("reference"), row.get("sha256")) for row in rows if isinstance(row, dict))
    if any(reference in protected_references for reference, _ in entries):
        return "TASK_VISIBLE_ARTIFACT_ROLE_COLLISION"
    if any(expected_hash in protected_hashes for _, expected_hash in entries):
        return "TASK_VISIBLE_ARTIFACT_HASH_COLLISION"
    protected_parents = {
        Path(str(reference)).parent.as_posix()
        for reference in protected_references
        if isinstance(reference, str) and Path(reference).parent.as_posix() != "."
    }
    for reference, _ in entries:
        if isinstance(reference, str) and any(
            Path(reference).as_posix().startswith(parent + "/") for parent in protected_parents
        ):
            return "TASK_VISIBLE_ARTIFACT_ROOT_COLLISION"
    return None


def validate_case_set(rows: list[dict], research_contract_id: object) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    headers = [row for row in rows if row.get("record_type") == "case_set_contract"]
    cases = [row for row in rows if row.get("record_type") == "calibration_case"]
    if len(headers) != 1:
        problems.append("exactly_one_case_set_contract_required")
        header: dict = {}
    else:
        header = headers[0]
    if any(row.get("record_type") not in {"case_set_contract", "calibration_case"} for row in rows):
        problems.append("unknown_record_type")
    if (
        header.get("case_count") != 40
        or header.get("actual_case_record_count") != 40
        or header.get("case_set_state") != "frozen"
        or not nonempty_text(header.get("case_set_id"))
        or header.get("research_contract_id") != research_contract_id
    ):
        problems.append("case_set_contract_invalid")
    case_ids = [row.get("case_id") for row in cases]
    if (
        len(cases) != 40
        or not all(nonempty_text(case_id) for case_id in case_ids)
        or len(set(case_ids)) != 40
        or any(row.get("research_contract_id") != research_contract_id for row in cases)
    ):
        problems.append("forty_unique_contract_bound_cases_required")
    formal_case_ids = header.get("formal_case_ids")
    if (
        not isinstance(formal_case_ids, list)
        or formal_case_ids != case_ids
        or len(formal_case_ids) != 40
        or not all(
            isinstance(case_id, str)
            and bool(case_id.strip())
            and unicodedata.normalize("NFKC", case_id) == case_id
            and "/" not in case_id
            and "\\" not in case_id
            and "." not in case_id
            and not any(character.isspace() or ord(character) < 32 for character in case_id)
            for case_id in formal_case_ids
        )
        or len({unicodedata.normalize("NFKC", case_id).casefold() for case_id in formal_case_ids if isinstance(case_id, str)}) != 40
    ):
        problems.append("formal_case_ids_invalid")
    return problems, [str(case_id) for case_id in case_ids if nonempty_text(case_id)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bind a real frozen 40-case set to a new final RC2 research-contract version."
    )
    parser.add_argument("--preparation-contract", required=True, type=Path)
    parser.add_argument("--case-set", required=True, type=Path)
    parser.add_argument("--case-set-reference", required=True)
    parser.add_argument("--visible-case-set", type=Path)
    parser.add_argument("--visible-case-set-reference")
    parser.add_argument("--visible-case-freeze-receipt", type=Path)
    parser.add_argument("--visible-case-freeze-receipt-reference")
    parser.add_argument("--expected-visible-case-freeze-receipt-sha256")
    parser.add_argument("--source-truth-package", type=Path)
    parser.add_argument("--source-truth-reference")
    parser.add_argument("--final-contract-version", required=True)
    parser.add_argument("--batch-size", required=True, type=int)
    parser.add_argument("--control-case-id", required=True, action="append")
    parser.add_argument("--frozen-at", required=True)
    parser.add_argument("--contract-local-root", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--test-fail-after-temp-write", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    preparation_path = args.preparation_contract.resolve()
    case_set_path = args.case_set.resolve()
    visible_case_set_path = args.visible_case_set.resolve() if args.visible_case_set is not None else None
    visible_freeze_receipt_path = args.visible_case_freeze_receipt.resolve() if args.visible_case_freeze_receipt is not None else None
    output = args.output.resolve()
    contract_local_root = args.contract_local_root.resolve() if args.contract_local_root is not None else None
    if not preparation_path.is_file():
        return fail("PREPARATION_CONTRACT_MISSING", str(preparation_path))
    if not case_set_path.is_file():
        return fail("CASE_SET_MISSING", str(case_set_path))
    if output.exists():
        return fail("OUTPUT_EXISTS", str(output))
    if (
        not nonempty_text(args.case_set_reference)
        or not nonempty_text(args.final_contract_version)
        or not nonempty_text(args.frozen_at)
        or args.batch_size <= 0
    ):
        return fail("FINALIZATION_ARGUMENT_INVALID", "reference, version, frozen_at, and positive batch size are required")
    if len(set(args.control_case_id)) != len(args.control_case_id):
        return fail("CONTROL_CASE_IDS_INVALID", "control case IDs must be unique")

    try:
        payload = json.loads(preparation_path.read_text(encoding="utf-8"))
        contract = payload["semantic_research_contract"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return fail("PREPARATION_CONTRACT_INVALID", str(exc))
    if "execution_mode" in contract and contract.get("execution_mode") != "content_first":
        return fail("EXECUTION_MODE_INVALID", str(contract.get("execution_mode")))
    preparation_problems = case_preparation_contract_completeness_errors(contract)
    if preparation_problems:
        code = (
            "PREPARATION_LOCK_HASH_MISMATCH"
            if "case_preparation_gate.locked_input_sha256:mismatch" in preparation_problems
            else "PREPARATION_CONTRACT_INCOMPLETE"
        )
        return fail(code, ";".join(preparation_problems))
    content_first = contract.get("execution_mode") == "content_first"
    truth_path: Path | None = None
    visible_bytes: bytes | None = None
    visible_rows: list[dict] | None = None
    truth_rows: list[dict] | None = None
    sealed_references: set[object] = set()
    sealed_hashes: set[object] = set()
    if content_first:
        if contract.get("map_builder_plugin_version") != MAP_BUILDER_PLUGIN_VERSION:
            return fail(
                "MAP_BUILDER_PLUGIN_VERSION_INVALID",
                repr(contract.get("map_builder_plugin_version")),
            )
        if (
            contract.get("case_package_contract_version")
            != CASE_PACKAGE_CONTRACT_VERSION
        ):
            return fail(
                "CASE_PACKAGE_CONTRACT_VERSION_INVALID",
                repr(contract.get("case_package_contract_version")),
            )
        if contract_local_root is None or not contract_local_root.is_dir():
            return fail("CONTRACT_LOCAL_ROOT_REQUIRED", "content_first finalization requires an explicit local frozen-input root")
        if args.source_truth_package is None or not nonempty_text(args.source_truth_reference):
            return fail("SOURCE_TRUTH_PACKAGE_REQUIRED", "content_first finalization requires a source truth package and reference")
        if visible_case_set_path is None or not nonempty_text(args.visible_case_set_reference):
            return fail("VISIBLE_CASE_SET_REQUIRED", "content_first finalization requires a pre-frozen visible-only case set and reference")
        if (
            visible_freeze_receipt_path is None
            or not nonempty_text(args.visible_case_freeze_receipt_reference)
            or not nonempty_text(args.expected_visible_case_freeze_receipt_sha256)
        ):
            return fail("VISIBLE_CASE_FREEZE_RECEIPT_REQUIRED", "content_first finalization requires an independently hashed visible-case freeze receipt")
        if not visible_case_set_path.is_file():
            return fail("VISIBLE_CASE_SET_MISSING", str(visible_case_set_path))
        truth_path = args.source_truth_package.resolve()
        if not truth_path.is_file():
            return fail("SOURCE_TRUTH_PACKAGE_MISSING", str(truth_path))
        declared_inputs = (
            (case_set_path, args.case_set_reference),
            (visible_case_set_path, args.visible_case_set_reference),
            (visible_freeze_receipt_path, args.visible_case_freeze_receipt_reference),
            (truth_path, args.source_truth_reference),
        )
        if any(
            declared_input_path_error(contract_local_root, actual, reference)
            for actual, reference in declared_inputs
            if actual is not None
        ):
            return fail(
                "DECLARED_INPUT_PATH_MISMATCH",
                "actual case, visible, receipt, and truth files must equal their contract-local references",
            )
        try:
            visible_bytes = visible_case_set_path.read_bytes()
            visible_rows = load_jsonl(visible_case_set_path)
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            return fail("VISIBLE_CASE_SET_INVALID", str(exc))
        receipt_error = visible_freeze_receipt_error(
            visible_freeze_receipt_path,
            args.expected_visible_case_freeze_receipt_sha256,
            args.visible_case_freeze_receipt_reference,
            args.visible_case_set_reference,
            visible_bytes,
            visible_rows,
            contract.get("research_contract_id"),
        )
        if receipt_error:
            return fail(receipt_error, str(visible_freeze_receipt_path))

    preparation_version = contract["contract_version"]
    if content_first and not valid_prep_to_final_version(
        preparation_version, args.final_contract_version
    ):
        return fail(
            "FINAL_CONTRACT_VERSION_INVALID",
            "final contract version must be the exact prep-to-final transition",
        )
    if not content_first and args.final_contract_version == preparation_version:
        return fail(
            "FINAL_CONTRACT_VERSION_NOT_NEW",
            "final contract version must differ from the locked preparation contract version",
        )
    locked_at = aware_datetime(
        (contract.get("case_preparation_gate") or {}).get("locked_at")
    )
    frozen_at = aware_datetime(args.frozen_at)
    if locked_at is None or frozen_at is None or frozen_at <= locked_at:
        return fail(
            "FROZEN_AT_INVALID",
            "frozen_at must be timezone-aware and strictly later than locked_at",
        )
    try:
        case_set_bytes = case_set_path.read_bytes()
        rows = load_jsonl(case_set_path)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return fail("CASE_SET_INVALID", str(exc))
    case_problems, case_ids = validate_case_set(rows, contract.get("research_contract_id"))
    missing_controls = sorted(set(args.control_case_id) - set(case_ids))
    if missing_controls:
        case_problems.append("control_case_ids_not_in_case_set:" + ",".join(missing_controls))
    if case_problems:
        return fail("CASE_SET_INVALID", ";".join(case_problems))
    if truth_path is not None:
        try:
            truth_bytes = truth_path.read_bytes()
            truth_rows = load_jsonl(truth_path)
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            return fail("SOURCE_TRUTH_PACKAGE_INVALID", str(exc))
        assert visible_case_set_path is not None and visible_freeze_receipt_path is not None
        assert visible_bytes is not None and visible_rows is not None and truth_rows is not None
        sealed_references = {
            args.case_set_reference,
            args.visible_case_set_reference,
            args.visible_case_freeze_receipt_reference,
            args.source_truth_reference,
        }
        sealed_hashes = {
            hashlib.sha256(case_set_bytes).hexdigest(),
            hashlib.sha256(visible_bytes).hexdigest(),
            hashlib.sha256(truth_bytes).hexdigest(),
            args.expected_visible_case_freeze_receipt_sha256,
        }
        collision = declared_task_visible_collision(contract, sealed_references, sealed_hashes)
        if collision:
            return fail(collision, "declared task-visible input aliases a sealed role before validation opens it")
        reference_problems = content_first_local_frozen_reference_errors(contract, contract_local_root)
        if reference_problems:
            return fail("FROZEN_REFERENCE_INVALID", ";".join(reference_problems))
        post_read_sealed_hashes = {
            hashlib.sha256(case_set_path.read_bytes()).hexdigest(),
            hashlib.sha256(visible_case_set_path.read_bytes()).hexdigest(),
            hashlib.sha256(visible_freeze_receipt_path.read_bytes()).hexdigest(),
            hashlib.sha256(truth_path.read_bytes()).hexdigest(),
        }
        if post_read_sealed_hashes != sealed_hashes:
            return fail("SEALED_INPUT_CHANGED_DURING_VALIDATION", "sealed content-first input changed while task-visible references were checked")
        collision = declared_task_visible_collision(contract, sealed_references, post_read_sealed_hashes)
        if collision:
            return fail(collision, "declared task-visible input aliases a sealed role after validation")
        content_problems = validate_content_first_case_truth_rows(
            rows,
            truth_rows,
            contract.get("research_contract_id"),
            contract.get("calibration_case_policy"),
            args.control_case_id,
            (contract.get("retrieval_efficiency_gates") or {}).get("stability_repeat_case_count"),
            contract=contract,
            contract_local_root=contract_local_root,
            frozen_at=args.frozen_at,
        )
        if content_problems:
            return fail("FORMAL_CONTENT_SET_INVALID", ";".join(content_problems))
        visible_problems = validate_visible_case_set(
            visible_rows, rows, truth_rows, contract.get("research_contract_id")
        )
        if visible_problems:
            return fail(visible_problems[0], ";".join(visible_problems))

    payload["schema_version"] = "1.2"
    contract["contract_version"] = args.final_contract_version
    contract["contract_state"] = "frozen"
    contract["frozen_at"] = args.frozen_at
    contract["calibration_case_set_reference_and_hash"] = {
        "reference": args.case_set_reference,
        "sha256": hashlib.sha256(case_set_bytes).hexdigest(),
    }
    if truth_path is not None:
        assert visible_case_set_path is not None and visible_freeze_receipt_path is not None and visible_bytes is not None
        contract["visible_case_set_reference_and_hash"] = {
            "reference": args.visible_case_set_reference,
            "sha256": hashlib.sha256(visible_bytes).hexdigest(),
        }
        contract["visible_case_freeze_receipt_reference_and_hash"] = {
            "reference": args.visible_case_freeze_receipt_reference,
            "sha256": args.expected_visible_case_freeze_receipt_sha256,
        }
    if truth_path is not None:
        contract["source_truth_package_reference"] = args.source_truth_reference
        contract["source_truth_package_sha256"] = hashlib.sha256(truth_bytes).hexdigest()
        contract["adjudicated_truth_summary"] = derive_truth_summary(truth_rows)
    contract["batch_rule"]["batch_size"] = args.batch_size
    contract["control_case_rule"]["case_ids"] = list(args.control_case_id)
    final_problems = frozen_contract_completeness_errors(contract)
    if final_problems:
        return fail("FINAL_CONTRACT_INCOMPLETE", ";".join(final_problems))

    final_bytes = canonical_bytes(payload)
    visible_hashes = {
        contract["terminology_architecture"]["term_pack_sha256"],
        contract["taxonomy_snapshot_sha256"],
        *(row["sha256"] for row in contract["prompt_template_references_and_hashes"]),
        *(row["sha256"] for rows in contract["paired_execution_contract"]["frozen_artifact_references_and_hashes"].values() for row in rows),
    }
    protected_hashes = {
        hashlib.sha256(final_bytes).hexdigest(),
        contract["calibration_case_set_reference_and_hash"]["sha256"],
    }
    if truth_path is not None:
        protected_hashes.update({
            contract["visible_case_set_reference_and_hash"]["sha256"],
            contract["visible_case_freeze_receipt_reference_and_hash"]["sha256"],
            contract["source_truth_package_sha256"],
        })
    if visible_hashes.intersection(protected_hashes):
        return fail("TASK_VISIBLE_ARTIFACT_HASH_COLLISION", "frozen task-visible artifacts must be hash-disjoint from sealed inputs")
    publish_error = publish_create_only_atomic(
        output, final_bytes, fail_after_temp_write=args.test_fail_after_temp_write
    )
    if publish_error:
        return fail(publish_error, str(output))
    print(
        json.dumps(
            {
                "status": "PASS",
                "contract_state": "frozen",
                "output": str(output),
                "case_set_sha256": contract["calibration_case_set_reference_and_hash"]["sha256"],
                "final_contract_completeness": "PASS",
                "workspace_reference_validation_required": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
