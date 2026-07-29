from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_TEST_PATH = (
    ROOT / "tests/company-product-knowledge-builder/test_library_tools.py"
)
MAP_TEST_PATH = (
    ROOT / "tests/industry-application-map-builder/test_workspace_tools.py"
)
CUSTOMER_VERIFY = (
    ROOT
    / "plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development"
    / "scripts/verify_route_pool_packet.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRODUCT = load_module("product_builder_tests", PRODUCT_TEST_PATH)
MAP = load_module("industry_map_tests", MAP_TEST_PATH)


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class ProductMapCustomerIntegrationTests(unittest.TestCase):
    def test_registered_route_and_readiness_view_remain_traceable_end_to_end(self):
        product = PRODUCT.CompanyLibraryToolTests()
        industry_map = MAP.WorkspaceToolTests()
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            library = product.initialize(parent)
            product.add_source(library)
            technical_fact = product.valid_fact(fact_id="ACME-001-K-0001")
            commercial_fact = product.commercial_fact(
                fact_id="ACME-001-K-0002",
                dimension="minimum_order_quantity",
                operator="minimum",
                value=25,
                unit="kg",
            )
            product.put_facts(library, technical_fact, commercial_fact)
            product.put_product_family(
                library,
                "ACME-001-K-0001",
                "ACME-001-K-0002",
            )
            product_packet = library / "04-开发交接/product-development-fact-packet.json"
            fact_export = run(
                PRODUCT.EXPORT_FACT_PACKET_SCRIPT,
                str(library),
                "--product-family-id",
                "ACME-001-PF-001",
            )
            self.assertEqual(
                fact_export.returncode,
                0,
                fact_export.stdout + fact_export.stderr,
            )

            map_root = industry_map.initialize_root(parent)
            industry_map.populate_shared_base(map_root)
            company_root = industry_map.initialize_company(
                map_root,
                library,
                product_packet,
                product_scope="Effect pigments",
            )
            industry_map.populate_company_route(company_root)
            company_workbook = company_root / "company-industry-application-map.xlsx"
            for sheet_name in ("产品能力", "路线候选", "覆盖台账"):
                MAP.change_first_record(
                    company_workbook,
                    sheet_name,
                    "product_scope",
                    "Effect pigments",
                )
            map_validation = industry_map.validate(map_root)
            self.assertEqual(
                map_validation.returncode,
                0,
                map_validation.stdout + map_validation.stderr,
            )

            route_packet = company_root / "company-route-pool-packet.json"
            route_export = run(
                MAP.EXPORT_SCRIPT,
                str(map_root),
                "--company-id",
                "ACME-001",
                "--output",
                str(route_packet),
            )
            self.assertEqual(
                route_export.returncode,
                0,
                route_export.stdout + route_export.stderr,
            )
            preflight = run(
                CUSTOMER_VERIFY,
                str(route_packet),
                "--map-root",
                str(map_root),
                "--company-id",
                "ACME-001",
                "--route-candidate-id",
                "ACME-001-R-0001",
            )
            self.assertEqual(preflight.returncode, 0, preflight.stdout + preflight.stderr)
            preflight_report = json.loads(preflight.stdout)

            request_path = parent / "development-readiness-request.json"
            PRODUCT.write_json(
                request_path,
                {
                    "development_readiness_request": {
                        "request_id": "READY-001",
                        "company_id": "ACME-001",
                        "product_scope": "Effect pigments",
                        "route_candidate_id": "ACME-001-R-0001",
                        "intended_use_scope": ["Synthetic application"],
                        "geography_scope": ["DE"],
                        "customer_type_scope": ["manufacturer"],
                        "requested_dimensions": ["minimum_order_quantity"],
                        "declared_conditions": [
                            {
                                "dimension": "minimum_order_quantity",
                                "value": 30,
                                "unit": "kg",
                            }
                        ],
                        "requested_at": "2026-07-29",
                        "return_to": {
                            "skill": "foreign-trade-customer-development",
                            "task_route": "route_portfolio_review",
                        },
                    }
                },
            )
            readiness = run(
                PRODUCT.EXPORT_READINESS_VIEW_SCRIPT,
                str(library),
                "--request",
                str(request_path),
            )
            self.assertEqual(
                readiness.returncode,
                0,
                readiness.stdout + readiness.stderr,
            )
            readiness_view = json.loads(readiness.stdout)["development_readiness_view"]

            self.assertEqual(preflight_report["company_id"], readiness_view["company_id"])
            self.assertEqual(
                preflight_report["selected_route"]["route_candidate_id"],
                readiness_view["route_candidate_id"],
            )
            self.assertEqual(readiness_view["readiness_state"], "可承接")
            self.assertEqual(
                readiness_view["next_owner"],
                "foreign-trade-customer-development",
            )
            self.assertEqual(
                preflight_report["selected_route"]["map_route_status"],
                "路线候选",
            )
            preflight_again = run(
                CUSTOMER_VERIFY,
                str(route_packet),
                "--map-root",
                str(map_root),
                "--company-id",
                "ACME-001",
                "--route-candidate-id",
                "ACME-001-R-0001",
            )
            self.assertEqual(
                preflight_again.returncode,
                0,
                preflight_again.stdout + preflight_again.stderr,
            )


if __name__ == "__main__":
    unittest.main()
