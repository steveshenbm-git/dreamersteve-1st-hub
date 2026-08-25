#!/usr/bin/env python3
"""Freeze a truth-free visible case set before any sealed truth is prepared."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

from content_first_visible_case_schema import nonempty_text, valid_timezone_iso8601, visible_case_draft_errors


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fail(code: str, detail: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "detail": detail}, ensure_ascii=False), file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze a draft visible-only RC2 case set before sealed truth preparation.")
    parser.add_argument("--visible-case-draft", required=True, type=Path)
    parser.add_argument("--visible-case-set-reference", required=True)
    parser.add_argument("--freeze-authorization-reference", required=True)
    parser.add_argument("--frozen-at", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt-output", required=True, type=Path)
    parser.add_argument("--test-fail-after-visible-publish", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    draft, output, receipt_output = args.visible_case_draft.resolve(), args.output.resolve(), args.receipt_output.resolve()
    if not draft.is_file():
        return fail("VISIBLE_CASE_DRAFT_MISSING", str(draft))
    if output.exists() or receipt_output.exists():
        return fail("OUTPUT_EXISTS", str(output if output.exists() else receipt_output))
    if output == receipt_output or not all(nonempty_text(value) for value in (args.visible_case_set_reference, args.freeze_authorization_reference)) or not valid_timezone_iso8601(args.frozen_at):
        return fail("VISIBLE_CASE_FREEZE_ARGUMENT_INVALID", "reference, authorization, frozen_at, and distinct outputs are required")
    created: list[Path] = []
    try:
        rows = [json.loads(line) for line in draft.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, ValueError) as exc:
        return fail("VISIBLE_CASE_DRAFT_INVALID", str(exc))
    if not rows or not all(isinstance(row, dict) for row in rows):
        return fail("VISIBLE_CASE_DRAFT_INVALID", "rows must be JSON objects")
    header = next((row for row in rows if row.get("record_type") == "visible_case_set_draft"), {})
    errors = visible_case_draft_errors(rows, header.get("research_contract_id"))
    if errors:
        return fail("VISIBLE_CASE_DRAFT_INVALID", ";".join(errors))
    frozen_rows = [
        {
            "record_type": "visible_case_set_contract",
            "visible_case_set_id": header["visible_case_set_id"],
            "research_contract_id": header["research_contract_id"],
            "visible_case_set_state": "frozen_visible_only",
            "visible_only": True,
            "truth_data_allowed": False,
            "frozen_before_truth_preparation": True,
            "freeze_authorization_reference": args.freeze_authorization_reference,
            "frozen_at": args.frozen_at,
            "case_count": 40,
            "actual_case_record_count": 40,
            "formal_case_ids": header["formal_case_ids"],
        },
        *[
            {
                "record_type": "visible_calibration_case",
                "research_contract_id": row["research_contract_id"],
                "case_id": row["case_id"],
                "taxonomy_node": row["taxonomy_node"],
                "product_neutral_research_theme": row["product_neutral_research_theme"],
                "risk_flags": row["risk_flags"],
            }
            for row in rows
            if row.get("record_type") == "visible_calibration_case_draft"
        ],
    ]
    frozen_bytes = b"".join(canonical_bytes(row) for row in frozen_rows)
    ordered_ids = frozen_rows[0]["formal_case_ids"]
    receipt = {
        "schema_version": "1.0",
        "visible_case_freeze_receipt": {
            "receipt_id": "visible-case-freeze-" + sha256_bytes(frozen_bytes)[:16],
            "action": "visible_case_freeze_only",
            "research_contract_id": header["research_contract_id"],
            "visible_case_set_reference": args.visible_case_set_reference,
            "output_scope": args.visible_case_set_reference,
            "visible_case_set_sha256": sha256_bytes(frozen_bytes),
            "ordered_case_ids_sha256": sha256_bytes(canonical_bytes(ordered_ids)),
            "freeze_authorization_reference": args.freeze_authorization_reference,
            "frozen_at": args.frozen_at,
            "truth_authorized": False,
            "model_execution_authorized": False,
            "full_screening_authorized": False,
        },
    }
    receipt_bytes = canonical_bytes(receipt)
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt_output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix=".visible-freeze-", dir=output.parent) as staging:
            stage = Path(staging)
            frozen_stage, receipt_stage = stage / "visible.jsonl", stage / "receipt.json"
            frozen_stage.write_bytes(frozen_bytes)
            receipt_stage.write_bytes(receipt_bytes)
            frozen_stage.replace(output)
            created.append(output)
            if args.test_fail_after_visible_publish:
                raise OSError("deterministic requested second publish failure")
            receipt_stage.replace(receipt_output)
            created.append(receipt_output)
    except OSError as exc:
        for created_path in reversed(created):
            try:
                created_path.unlink()
            except OSError:
                pass
        return fail("VISIBLE_CASE_FREEZE_WRITE_FAILED", str(exc))
    print(json.dumps({"status": "PASS", "output": str(output), "receipt": str(receipt_output), "visible_case_set_sha256": sha256_bytes(frozen_bytes)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
