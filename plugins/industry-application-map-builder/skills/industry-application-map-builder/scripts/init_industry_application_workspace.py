from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import shutil
import sys

from xlsx_contract import replace_xlsx_tokens, sha256_file


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"
ROOT_TEMPLATE = ASSETS / "empty-industry-application-map-root"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def fail(code: str, message: str) -> int:
    print(f"{code}: {message}", file=sys.stderr)
    return 1


def init_root(args: argparse.Namespace) -> int:
    destination = args.destination.resolve()
    if destination.exists():
        return fail("DESTINATION_EXISTS", str(destination))

    shutil.copytree(ROOT_TEMPLATE, destination)
    for relative in (
        "01-共享行业骨架",
        "02-共享应用知识",
        "03-共享来源封存",
        "04-公司地图",
        "05-工作区",
        "06-风险隔离",
    ):
        (destination / relative).mkdir(parents=True, exist_ok=True)

    taxonomy = destination / "01-共享行业骨架" / "industry-taxonomy.xlsx"
    application = destination / "02-共享应用知识" / "industry-application-base.xlsx"
    shutil.copy2(ASSETS / "empty-industry-taxonomy.xlsx", taxonomy)
    shutil.copy2(ASSETS / "empty-industry-application-base.xlsx", application)
    today = date.today().isoformat()
    shared = {
        "[[TAXONOMY_SYSTEM]]": args.taxonomy_system,
        "[[TAXONOMY_VERSION]]": args.taxonomy_version,
        "[[TAXONOMY_SOURCE_URL]]": args.taxonomy_source_url,
        "[[OBSERVED_AT]]": today,
        "[[DECLARED_SCOPE]]": args.declared_scope,
    }
    replace_xlsx_tokens(taxonomy, shared)
    replace_xlsx_tokens(
        application,
        {
            **shared,
            "[[APPLICATION_BASE_VERSION]]": args.application_base_version,
            "[[SOURCE_SCOPE]]": args.source_scope,
        },
    )

    registry_path = destination / "00-管理" / "map-registry.json"
    registry = read_json(registry_path)
    registry.update(
        {
            "map_root_id": destination.name,
            "shared_taxonomy": {
                "path": "01-共享行业骨架/industry-taxonomy.xlsx",
                "taxonomy_system": args.taxonomy_system,
                "taxonomy_version": args.taxonomy_version,
                "sha256": sha256_file(taxonomy),
            },
            "shared_application_base": {
                "path": "02-共享应用知识/industry-application-base.xlsx",
                "application_base_version": args.application_base_version,
                "sha256": sha256_file(application),
            },
            "companies": [],
            "initialized_at": today,
        }
    )
    write_json(registry_path, registry)
    change_path = destination / "00-管理" / "change-log.json"
    changes = read_json(change_path)
    changes["changes"].append(
        {
            "change_id": "MAP-INIT-0001",
            "changed_at": today,
            "actor": "initializer",
            "reason": "initialize shared industry application map root",
            "affected_ids": [destination.name],
            "authorization_basis": "explicit user-authorized creation",
        }
    )
    write_json(change_path, changes)
    print(destination)
    return 0


def init_company(args: argparse.Namespace) -> int:
    map_root = args.map_root.resolve()
    registry_path = map_root / "00-管理" / "map-registry.json"
    if not registry_path.is_file():
        return fail("MAP_ROOT_INVALID", str(map_root))
    if not args.company_id:
        return fail("COMPANY_ID_REQUIRED", "--company-id is required")
    if not args.company_library_root or not args.product_packet or not args.product_scope:
        return fail(
            "COMPANY_INPUT_REQUIRED",
            "--company-library-root, --product-packet, and --product-scope are required",
        )

    company_library = args.company_library_root.resolve()
    packet_path = args.product_packet.resolve()
    facts_path = company_library / "02-事实库" / "facts.json"
    company_file = company_library / "company.json"
    for required in (company_file, packet_path, facts_path):
        if not required.is_file():
            return fail("COMPANY_INPUT_MISSING", str(required))

    company = read_json(company_file)
    packet = read_json(packet_path).get("product_development_fact_packet", {})
    facts = read_json(facts_path)
    if any(
        value != args.company_id
        for value in (
            company.get("company_id"),
            packet.get("company_id"),
            facts.get("company_id"),
        )
    ):
        return fail("CROSS_COMPANY_INPUT", args.company_id)
    if "internal_industry_application_mapping" not in packet.get("allowed_use", []):
        return fail("PRODUCT_PACKET_USE_NOT_ALLOWED", str(packet_path))

    company_root = map_root / "04-公司地图" / args.company_id
    if company_root.exists():
        return fail("COMPANY_MAP_EXISTS", str(company_root))

    registry = read_json(registry_path)
    taxonomy = map_root / registry["shared_taxonomy"]["path"]
    application = map_root / registry["shared_application_base"]["path"]
    today = date.today().isoformat()
    company_root.mkdir(parents=True)
    workbook = company_root / "company-industry-application-map.xlsx"
    shutil.copy2(ASSETS / "empty-company-industry-application-map.xlsx", workbook)
    replacements = {
        "[[COMPANY_ID]]": args.company_id,
        "[[COMPANY_LIBRARY_ROOT]]": str(company_library),
        "[[PRODUCT_PACKET_PATH]]": str(packet_path),
        "[[PRODUCT_PACKET_SHA256]]": sha256_file(packet_path),
        "[[FACTS_PATH]]": str(facts_path),
        "[[FACTS_SHA256]]": sha256_file(facts_path),
        "[[SHARED_TAXONOMY_PATH]]": str(taxonomy),
        "[[TAXONOMY_SHA256]]": sha256_file(taxonomy),
        "[[SHARED_APPLICATION_BASE_PATH]]": str(application),
        "[[APPLICATION_BASE_SHA256]]": sha256_file(application),
        "[[PRODUCT_SCOPE]]": args.product_scope,
        "[[DECLARED_TAXONOMY_SCOPE]]": args.declared_taxonomy_scope,
        "[[DECLARED_APPLICATION_SCOPE]]": args.declared_application_scope,
        "[[ALLOWED_SOURCE_SCOPE]]": args.allowed_source_scope,
        "[[INITIALIZED_AT]]": today,
    }
    replace_xlsx_tokens(workbook, replacements)
    write_json(company_root / "review-log.json", {"schema_version": "1.0", "reviews": []})
    write_json(
        company_root / "route-pool-export-registry.json",
        {
            "schema_version": "1.0",
            "company_id": args.company_id,
            "exports": [],
        },
    )

    registry["companies"].append(
        {
            "company_id": args.company_id,
            "company_map_path": str(workbook.relative_to(map_root)),
            "company_library_root": str(company_library),
            "product_packet_path": str(packet_path),
            "product_packet_sha256": sha256_file(packet_path),
            "facts_path": str(facts_path),
            "facts_sha256": sha256_file(facts_path),
            "taxonomy_sha256": sha256_file(taxonomy),
            "application_base_sha256": sha256_file(application),
            "product_scope": args.product_scope,
            "declared_taxonomy_scope": args.declared_taxonomy_scope,
            "declared_application_scope": args.declared_application_scope,
            "allowed_source_scope": args.allowed_source_scope,
            "initialized_at": today,
        }
    )
    write_json(registry_path, registry)
    print(company_root)
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--mode", choices=("root", "company"), required=True)
    result.add_argument("--destination", type=Path)
    result.add_argument("--map-root", type=Path)
    result.add_argument("--company-id")
    result.add_argument("--company-library-root", type=Path)
    result.add_argument("--product-packet", type=Path)
    result.add_argument("--product-scope")
    result.add_argument("--taxonomy-system", default="UNASSIGNED")
    result.add_argument("--taxonomy-version", default="UNASSIGNED")
    result.add_argument("--taxonomy-source-url", default="")
    result.add_argument("--declared-scope", default="framework_only")
    result.add_argument("--application-base-version", default="1.0.0")
    result.add_argument("--source-scope", default="public_sources_only")
    result.add_argument("--declared-taxonomy-scope", default="not_declared")
    result.add_argument("--declared-application-scope", default="not_declared")
    result.add_argument("--allowed-source-scope", default="public_sources_only")
    return result


def main() -> int:
    args = parser().parse_args()
    if args.mode == "root":
        if not args.destination:
            return fail("DESTINATION_REQUIRED", "--destination is required")
        return init_root(args)
    if not args.map_root:
        return fail("MAP_ROOT_REQUIRED", "--map-root is required")
    return init_company(args)


if __name__ == "__main__":
    raise SystemExit(main())
