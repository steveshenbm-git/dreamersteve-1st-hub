from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import unicodedata

from r4_adjudicated_truth_contract import (
    BETA5_CASE_PACKAGE_CONTRACT_VERSION as CASE_PACKAGE_CONTRACT_VERSION,
    MAP_BUILDER_PLUGIN_VERSION,
    BETA5_TRUTH_CONTRACT_VERSION as TRUTH_CONTRACT_VERSION,
    TRUTH_ROW_FIELDS,
    validate_adjudicated_truth_rows,
)

TRUTH_BASIS_ROLES = (
    "taxonomy_membership_basis",
    "output_or_subprocess_basis",
    "mechanism_or_use_point_basis",
)
RAW_CAPTURE_METHODS = {
    "http_response_body_v1",
    "file_snapshot_v1",
    "document_export_v1",
}
PROJECTION_ALGORITHM = "canonical_json_node_projection_v1"


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value).rstrip(b"\n")).hexdigest()


def aware_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def valid_prep_to_final_version(preparation: object, final: object) -> bool:
    if not isinstance(preparation, str) or not isinstance(final, str):
        return False
    match = re.fullmatch(r"(.+)\.prep\.(\d+)", preparation)
    return bool(match and final == f"{match.group(1)}.final.{match.group(2)}")


def taxonomy_identifier_key(value: object) -> str | None:
    """Normalize an official taxonomy identifier without treating it as a path."""
    if not isinstance(value, str) or not value or value.strip() != value:
        return None
    if unicodedata.normalize("NFKC", value) != value or "\\" in value:
        return None
    if any(character.isspace() or ord(character) < 32 for character in value):
        return None
    if value.startswith("/") or value.endswith("/") or "//" in value:
        return None
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return value.casefold()


def taxonomy_level_number(value: object) -> int | None:
    if type(value) is int and value in {1, 2, 3, 4}:
        return value
    return {
        "section": 1,
        "division": 2,
        "group": 3,
        "class": 4,
    }.get(value)


def canonical_local_reference(reference: object) -> str | None:
    if not isinstance(reference, str) or not reference:
        return None
    candidate = PurePosixPath(reference)
    if (
        candidate.as_posix() != reference
        or candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or "\\" in reference
        or unicodedata.normalize("NFKC", reference) != reference
    ):
        return None
    return reference


def declared_input_path_error(
    root: Path, actual_path: Path, reference: object
) -> str | None:
    canonical = canonical_local_reference(reference)
    if canonical is None:
        return "DECLARED_INPUT_PATH_MISMATCH"
    unresolved = root.resolve() / PurePosixPath(canonical)
    current = root.resolve()
    for part in PurePosixPath(canonical).parts:
        current = current / part
        if current.is_symlink():
            return "DECLARED_INPUT_PATH_MISMATCH"
    try:
        expected = unresolved.resolve(strict=True)
        actual = actual_path.resolve(strict=True)
        expected.relative_to(root.resolve())
    except (FileNotFoundError, OSError, ValueError):
        return "DECLARED_INPUT_PATH_MISMATCH"
    return None if actual == expected else "DECLARED_INPUT_PATH_MISMATCH"


def publish_create_only_atomic(
    output: Path, body: bytes, *, fail_after_temp_write: bool = False
) -> str | None:
    if output.exists():
        return "OUTPUT_EXISTS"
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{output.name}.tmp-", dir=output.parent
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        if fail_after_temp_write:
            return "LOCK_PUBLISH_FAILED"
        try:
            os.link(temp_path, output)
        except FileExistsError:
            return "OUTPUT_EXISTS"
        return None
    except OSError:
        return "LOCK_PUBLISH_FAILED"
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _secure_file(
    root: Path, reference: object, expected_hash: object
) -> tuple[Path | None, bytes | None, tuple[int, int] | None, str | None]:
    canonical = canonical_local_reference(reference)
    if canonical is None:
        return None, None, None, "TRUTH_SOURCE_REFERENCE_INVALID"
    unresolved = root.resolve() / PurePosixPath(canonical)
    current = root.resolve()
    for part in PurePosixPath(canonical).parts:
        current = current / part
        if current.is_symlink():
            return None, None, None, "TRUTH_SOURCE_REFERENCE_INVALID"
    try:
        path = unresolved.resolve(strict=True)
        path.relative_to(root.resolve())
        body = path.read_bytes()
        stat = path.stat()
    except (FileNotFoundError, OSError, ValueError):
        return None, None, None, "TRUTH_SOURCE_MISSING"
    if (
        not isinstance(expected_hash, str)
        or len(expected_hash) != 64
        or expected_hash.lower() != expected_hash
        or any(ch not in "0123456789abcdef" for ch in expected_hash)
        or hashlib.sha256(body).hexdigest() != expected_hash
    ):
        return path, body, (stat.st_dev, stat.st_ino), "TRUTH_SOURCE_HASH_MISMATCH"
    return path, body, (stat.st_dev, stat.st_ino), None


def _raw_source_rejection(body: bytes, content_type: object) -> str | None:
    del content_type  # sniff the bytes; a self-reported MIME type is not evidence
    try:
        decoded = body.decode("utf-8").strip()
    except UnicodeDecodeError:
        decoded = ""
    if re.fullmatch(r"https?://\S+", decoded, flags=re.IGNORECASE):
        return "SELF_REPORTED_URL_CANNOT_BE_RAW_SOURCE"
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        return None
    if isinstance(payload, str) and re.fullmatch(
        r"https?://\S+", payload.strip(), flags=re.IGNORECASE
    ):
        return "SELF_REPORTED_URL_CANNOT_BE_RAW_SOURCE"
    summary_keys = {
        "summary",
        "source_summary",
        "conclusion",
        "screening_result",
        "semantic_decision",
        "supported",
    }
    stack: list[tuple[object, int]] = [(payload, 0)]
    inspected = 0
    while stack:
        value, depth = stack.pop()
        inspected += 1
        if inspected > 10000 or depth > 12:
            return "RAW_SOURCE_STRUCTURE_LIMIT_EXCEEDED"
        if isinstance(value, dict):
            if any(
                isinstance(key, str)
                and unicodedata.normalize("NFKC", key).casefold() in summary_keys
                for key in value
            ):
                return "DERIVED_SUMMARY_CANNOT_BE_RAW_SOURCE"
            stack.extend((item, depth + 1) for item in value.values())
        elif isinstance(value, list):
            stack.extend((item, depth + 1) for item in value)
    return None


def _projection_binding_error(
    basis: dict,
    contract: dict,
    root: Path,
    case: dict | None,
    source_body: bytes | None,
) -> str | None:
    taxonomy_reference = contract.get("taxonomy_snapshot_reference")
    taxonomy_sha256 = contract.get("taxonomy_snapshot_sha256")
    taxonomy_node = (case or {}).get("taxonomy_node") or {}
    official_reference = taxonomy_node.get("official_source_reference")
    expected_node_id = taxonomy_node.get("taxonomy_node_id")
    pointer = basis.get("upstream_json_pointer")
    if (
        not isinstance(case, dict)
        or canonical_local_reference(taxonomy_reference) is None
        or basis.get("upstream_snapshot_reference") != taxonomy_reference
        or basis.get("upstream_snapshot_sha256") != taxonomy_sha256
        or basis.get("upstream_node_id") != expected_node_id
        or not isinstance(pointer, str)
        or official_reference != f"{taxonomy_reference}{pointer}"
        or not re.fullmatch(r"#/terminal_nodes/(0|[1-9][0-9]*)", pointer)
        or basis.get("projection_algorithm") != PROJECTION_ALGORITHM
        or basis.get("projection_sha256") != basis.get("source_sha256")
        or source_body is None
    ):
        return "OFFICIAL_TAXONOMY_PROJECTION_BINDING_INVALID"
    _, snapshot_body, _, snapshot_error = _secure_file(
        root, taxonomy_reference, taxonomy_sha256
    )
    if snapshot_error or snapshot_body is None:
        return "OFFICIAL_TAXONOMY_PROJECTION_BINDING_INVALID"
    try:
        snapshot = json.loads(snapshot_body)
        index = int(pointer.rsplit("/", 1)[1])
        node = snapshot["terminal_nodes"][index]
    except (ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError):
        return "OFFICIAL_TAXONOMY_PROJECTION_BINDING_INVALID"
    if (
        not isinstance(node, dict)
        or node.get("taxonomy_node_id") != expected_node_id
        or canonical_bytes(node) != source_body
    ):
        return "OFFICIAL_TAXONOMY_PROJECTION_BINDING_INVALID"
    return None


def validate_complete_truth_rows(
    truth_rows: list[dict],
    contract: dict,
    root: Path,
    *,
    case_by_id: dict[str, dict] | None = None,
    frozen_at: object = None,
) -> list[str]:
    errors: list[str] = []
    seen_refs: set[str] = set()
    seen_hashes: set[str] = set()
    seen_inodes: set[tuple[int, int]] = set()
    expected_contract_id = contract.get("research_contract_id")
    locked_hash = (contract.get("case_preparation_gate") or {}).get(
        "locked_input_sha256"
    )
    locked_at = aware_datetime(
        (contract.get("case_preparation_gate") or {}).get("locked_at")
    )
    freeze_time = aware_datetime(frozen_at or contract.get("frozen_at"))
    seen_receipt_ids: set[str] = set()
    errors.extend(
        validate_adjudicated_truth_rows(
            truth_rows,
            expected_case_ids=list((case_by_id or {}).keys()),
            expected_contract_id=expected_contract_id,
            expected_preparation_contract_version=(
                (contract.get("case_preparation_gate") or {}).get(
                    "preparation_contract_version"
                )
            ),
            expected_locked_input_sha256=locked_hash,
        )
    )
    for row in truth_rows:
        if not isinstance(row, dict) or set(row) != TRUTH_ROW_FIELDS:
            errors.append("SOURCE_TRUTH_SCHEMA_INVALID")
            continue
        if (
            row.get("record_type") != "source_truth"
            or row.get("truth_contract_version") != TRUTH_CONTRACT_VERSION
            or row.get("research_contract_id") != expected_contract_id
            or row.get("preparation_contract_version")
            != (contract.get("case_preparation_gate") or {}).get(
                "preparation_contract_version"
            )
            or row.get("locked_input_sha256") != locked_hash
            or not isinstance(row.get("conditions"), list)
            or not isinstance(row.get("limitations"), list)
            or not isinstance(row.get("unknowns"), list)
            or not isinstance(row.get("exclusion_boundary"), str)
            or not row["exclusion_boundary"].strip()
        ):
            errors.append("SOURCE_TRUTH_SCHEMA_INVALID")
            continue
        claimed_truth_hash = row.get("truth_sha256")
        projection = dict(row)
        projection["truth_sha256"] = None
        if claimed_truth_hash != canonical_sha256(projection):
            errors.append("SOURCE_TRUTH_SELF_HASH_MISMATCH")
        bases = row.get("evidence_bases")
        if not isinstance(bases, dict) or set(bases) != set(TRUTH_BASIS_ROLES):
            errors.append("SOURCE_TRUTH_BASIS_INVALID")
            continue
        for role in TRUTH_BASIS_ROLES:
            basis = bases[role]
            required_basis = {
                "source_kind",
                "source_reference",
                "source_sha256",
                "capture_receipt_reference",
                "capture_receipt_sha256",
                "original_location",
                "claim",
                "upstream_snapshot_reference",
                "upstream_snapshot_sha256",
                "upstream_node_id",
                "upstream_json_pointer",
                "projection_algorithm",
                "projection_sha256",
            }
            if not isinstance(basis, dict) or set(basis) != required_basis:
                errors.append("SOURCE_TRUTH_BASIS_INVALID")
                continue
            source_kind = basis.get("source_kind")
            if role != "taxonomy_membership_basis" and source_kind != "receiver_captured_raw":
                errors.append("RAW_SOURCE_CAPTURE_REQUIRED")
                continue
            if source_kind not in {"receiver_captured_raw", "official_taxonomy_projection"}:
                errors.append("RAW_SOURCE_CAPTURE_REQUIRED")
                continue
            projection_fields = (
                "upstream_snapshot_reference",
                "upstream_snapshot_sha256",
                "upstream_node_id",
                "upstream_json_pointer",
                "projection_algorithm",
                "projection_sha256",
            )
            if source_kind == "receiver_captured_raw" and any(
                basis.get(field) is not None for field in projection_fields
            ):
                errors.append("SOURCE_TRUTH_BASIS_INVALID")
            if (
                not isinstance(basis.get("original_location"), str)
                or not basis["original_location"].strip()
                or not isinstance(basis.get("claim"), str)
                or not basis["claim"].strip()
            ):
                errors.append("SOURCE_TRUTH_BASIS_INVALID")
            source_body: bytes | None = None
            for ref_key, hash_key in (
                ("source_reference", "source_sha256"),
                ("capture_receipt_reference", "capture_receipt_sha256"),
            ):
                reference = basis.get(ref_key)
                expected_hash = basis.get(hash_key)
                if reference in seen_refs:
                    errors.append("TRUTH_SOURCE_REFERENCE_REUSED")
                elif isinstance(reference, str):
                    seen_refs.add(reference)
                if expected_hash in seen_hashes:
                    errors.append("TRUTH_SOURCE_HASH_REUSED")
                elif isinstance(expected_hash, str):
                    seen_hashes.add(expected_hash)
                _, body, identity, source_error = _secure_file(
                    root, reference, expected_hash
                )
                if source_error:
                    errors.append(source_error)
                    continue
                if identity in seen_inodes:
                    errors.append("TRUTH_SOURCE_INODE_REUSED")
                elif identity is not None:
                    seen_inodes.add(identity)
                if ref_key == "source_reference":
                    source_body = body
                if ref_key == "capture_receipt_reference":
                    try:
                        payload = json.loads(body)
                        receipt = payload["source_capture_receipt"]
                    except (ValueError, TypeError, KeyError):
                        errors.append("TRUTH_SOURCE_RECEIPT_INVALID")
                        continue
                    if (
                        not isinstance(payload, dict)
                        or set(payload) != {
                            "schema_version",
                            "source_capture_receipt",
                        }
                        or payload.get("schema_version") != "1.0"
                        or not isinstance(receipt, dict)
                        or set(receipt)
                        != {
                            "receipt_id",
                            "capture_contract_version",
                            "receiver_owner",
                            "capture_method",
                            "upstream_response_reference",
                            "upstream_response_sha256",
                            "research_contract_id",
                            "case_id",
                            "basis_role",
                            "source_reference",
                            "source_sha256",
                            "content_type",
                            "byte_length",
                            "final_url",
                            "captured_at",
                        }
                        or not isinstance(receipt.get("receipt_id"), str)
                        or not receipt["receipt_id"].strip()
                        or receipt.get("capture_contract_version")
                        != "1.0-receiver-owned"
                        or receipt.get("receiver_owner") != "content_source_receiver"
                        or receipt.get("research_contract_id")
                        != expected_contract_id
                        or receipt.get("case_id") != row.get("case_id")
                        or receipt.get("basis_role") != role
                        or receipt.get("source_reference")
                        != basis.get("source_reference")
                        or receipt.get("source_sha256")
                        != basis.get("source_sha256")
                        or not isinstance(receipt.get("content_type"), str)
                        or not receipt["content_type"].strip()
                        or not isinstance(receipt.get("byte_length"), int)
                        or source_body is None
                        or receipt.get("byte_length") != len(source_body)
                        or receipt.get("final_url")
                        != basis.get("original_location")
                    ):
                        errors.append("TRUTH_SOURCE_RECEIPT_INVALID")
                        continue
                    receipt_id = receipt["receipt_id"]
                    if receipt_id in seen_receipt_ids:
                        errors.append("TRUTH_SOURCE_RECEIPT_INVALID")
                    else:
                        seen_receipt_ids.add(receipt_id)
                    captured_at = aware_datetime(receipt.get("captured_at"))
                    if (
                        locked_at is None
                        or freeze_time is None
                        or captured_at is None
                        or captured_at <= locked_at
                        or captured_at > freeze_time
                    ):
                        errors.append("TRUTH_SOURCE_RECEIPT_TIME_INVALID")
                    if source_kind == "receiver_captured_raw":
                        if (
                            receipt.get("capture_method") not in RAW_CAPTURE_METHODS
                            or receipt.get("upstream_response_reference")
                            != basis.get("original_location")
                            or receipt.get("upstream_response_sha256")
                            != basis.get("source_sha256")
                        ):
                            errors.append("TRUTH_SOURCE_RECEIPT_INVALID")
                        raw_rejection = _raw_source_rejection(
                            source_body, receipt.get("content_type")
                        )
                        if raw_rejection:
                            errors.append(raw_rejection)
                    else:
                        if (
                            receipt.get("capture_method")
                            != "official_taxonomy_projection_v1"
                            or receipt.get("upstream_response_reference")
                            != f"{basis.get('upstream_snapshot_reference')}{basis.get('upstream_json_pointer')}"
                            or receipt.get("upstream_response_sha256")
                            != basis.get("upstream_snapshot_sha256")
                        ):
                            errors.append("TRUTH_SOURCE_RECEIPT_INVALID")
            if source_kind == "official_taxonomy_projection":
                projection_error = _projection_binding_error(
                    basis,
                    contract,
                    root,
                    (case_by_id or {}).get(row.get("case_id")),
                    source_body,
                )
                if projection_error:
                    errors.append(projection_error)
    return list(dict.fromkeys(errors))
