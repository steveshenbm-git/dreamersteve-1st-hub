#!/usr/bin/env python3
"""Create one isolated company product-knowledge library from the bundled template."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import shutil
import sys


COMPANY_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,63}$")
TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "assets" / "empty-company-library"


def fail(code: str, message: str) -> int:
    print(json.dumps({"status": "FAIL", "code": code, "message": message}, ensure_ascii=False), file=sys.stderr)
    return 2


def replace_placeholders(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = original
        for placeholder, value in replacements.items():
            updated = updated.replace(placeholder, value)
        if updated != original:
            path.write_text(updated, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new isolated company product-knowledge library."
    )
    parser.add_argument("--company-id", required=True)
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--destination", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    company_id = args.company_id.strip()
    company_name = args.company_name.strip()
    destination = args.destination.expanduser().resolve()

    if not COMPANY_ID_PATTERN.fullmatch(company_id):
        return fail(
            "INVALID_COMPANY_ID",
            "company_id must be 2-64 characters using letters, numbers, dot, underscore, or hyphen.",
        )
    if not company_name:
        return fail("INVALID_COMPANY_NAME", "company_name must not be empty.")
    if destination.exists():
        return fail("DESTINATION_EXISTS", f"Refusing to overwrite existing path: {destination}")
    if not TEMPLATE_ROOT.is_dir():
        return fail("TEMPLATE_MISSING", f"Bundled template not found: {TEMPLATE_ROOT}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_ROOT, destination)
    replace_placeholders(
        destination,
        {
            "[COMPANY_ID]": company_id,
            "[COMPANY_NAME]": company_name,
            "[TODAY]": date.today().isoformat(),
        },
    )

    print(
        json.dumps(
            {
                "status": "PASS",
                "company_id": company_id,
                "destination": str(destination),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
