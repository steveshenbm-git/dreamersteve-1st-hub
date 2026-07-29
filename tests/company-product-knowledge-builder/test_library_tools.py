from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = (
    ROOT
    / "plugins"
    / "company-product-knowledge-builder"
    / "skills"
    / "company-product-knowledge-builder"
)
INIT_SCRIPT = SKILL_ROOT / "scripts" / "init_company_library.py"
VALIDATE_SCRIPT = SKILL_ROOT / "scripts" / "validate_company_library.py"
EXPORT_FACT_PACKET_SCRIPT = (
    SKILL_ROOT / "scripts" / "export_product_development_fact_packet.py"
)
EXPORT_READINESS_VIEW_SCRIPT = (
    SKILL_ROOT / "scripts" / "export_development_readiness_view.py"
)


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class CompanyLibraryToolTests(unittest.TestCase):
    def initialize(self, parent: Path, company_id: str = "ACME-001") -> Path:
        destination = parent / company_id
        result = run_script(
            INIT_SCRIPT,
            "--company-id",
            company_id,
            "--company-name",
            "Acme Materials",
            "--destination",
            str(destination),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return destination

    def validate(self, library: Path) -> subprocess.CompletedProcess[str]:
        return run_script(VALIDATE_SCRIPT, str(library), "--format", "json")

    def add_source(self, library: Path, source_id: str = "ACME-001-S-0001") -> None:
        archive = library / "01-源文件封存" / "datasheet.txt"
        archive.write_text("controlled source", encoding="utf-8")
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        registry_path = library / "00-管理" / "源文件清单.json"
        registry = load_json(registry_path)
        registry["sources"].append(
            {
                "source_id": source_id,
                "company_id": "ACME-001",
                "archived_path": "01-源文件封存/datasheet.txt",
                "sha256": digest,
                "actual_subject": "own_company",
                "intake_date": "2026-07-29",
                "notes": "Controlled fixture",
            }
        )
        write_json(registry_path, registry)

    def valid_fact(
        self,
        *,
        fact_id: str = "ACME-001-K-0001",
        evidence_level: str = "E3",
        subject_scope: str = "own_company",
    ) -> dict:
        allowed_use = {
            "E3": ["internal", "external"],
            "E2": ["internal"],
            "E1": ["verification"],
            "E0": ["risk_review"],
        }[evidence_level]
        review_status = "approved" if evidence_level in {"E2", "E3"} else "pending"
        return {
            "fact_id": fact_id,
            "company_id": "ACME-001",
            "product_family": "Effect pigments",
            "product_series": None,
            "product_model": None,
            "fact_type": "parameter",
            "fact_value": {"value": 25},
            "statement_kind": "source_fact",
            "unit": "micrometre",
            "unit_status": "provided",
            "test_method": "laser diffraction",
            "test_method_status": "provided",
            "applicable_conditions": ["dry powder"],
            "known_limits": ["No wet-dispersion result established"],
            "subject_scope": subject_scope,
            "source_id": "ACME-001-S-0001",
            "source_location": "page 1, table 2",
            "evidence_level": evidence_level,
            "review_status": review_status,
            "reviewed_by": "owner" if review_status == "approved" else None,
            "reviewed_at": "2026-07-29" if review_status == "approved" else None,
            "allowed_use": allowed_use,
            "conflict_status": "none",
            "conflicts_with": [],
            "updated_at": "2026-07-29",
        }

    def put_facts(self, library: Path, *facts: dict) -> None:
        facts_path = library / "02-事实库" / "facts.json"
        payload = load_json(facts_path)
        payload["facts"] = list(facts)
        write_json(facts_path, payload)

    def put_product_family(self, library: Path, *fact_ids: str) -> None:
        product_path = library / "03-产品体系" / "product-system.json"
        payload = load_json(product_path)
        payload["product_families"] = [
            {
                "product_family_id": "ACME-001-PF-001",
                "name": "Effect pigments",
                "alias_terms": [],
                "fact_ids": list(fact_ids),
                "series": [],
                "unresolved_structure": [],
            }
        ]
        write_json(product_path, payload)

    def commercial_fact(
        self,
        *,
        fact_id: str,
        evidence_level: str = "E3",
        dimension: str = "minimum_order_quantity",
        operator: str = "minimum",
        value=25,
        unit: str | None = "kg",
        valid_until: str | None = "2026-12-31",
    ) -> dict:
        fact = self.valid_fact(fact_id=fact_id, evidence_level=evidence_level)
        fact.update(
            {
                "fact_type": "commercial_condition",
                "fact_value": {
                    "dimension": dimension,
                    "operator": operator,
                    "value": value,
                    "unit": unit,
                },
                "unit": unit,
                "unit_status": "provided" if unit else "not_applicable",
                "test_method": None,
                "test_method_status": "not_applicable",
                "observed_at": "2026-07-01",
                "valid_until": valid_until,
                "review_due": valid_until,
                "sensitivity": "commercial_internal",
                "geographic_scope": [],
                "customer_type_scope": [],
                "application_scope": [],
            }
        )
        return fact

    def test_initializer_creates_an_empty_isolated_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))

            self.assertEqual(load_json(library / "company.json")["company_id"], "ACME-001")
            expected_paths = (
                "00-管理/源文件清单.json",
                "01-源文件封存",
                "02-事实库/facts.json",
                "03-产品体系/product-system.json",
                "04-开发交接/product-development-fact-packet.json",
                "05-复核/review-log.json",
                "06-工作区",
                "07-风险隔离",
            )
            for relative in expected_paths:
                self.assertTrue((library / relative).exists(), relative)

            combined = "\n".join(
                path.read_text(encoding="utf-8", errors="ignore")
                for path in library.rglob("*")
                if path.is_file()
            )
            self.assertNotIn("雅洋", combined)
            self.assertNotIn("Yayang", combined)

    def test_initializer_refuses_to_overwrite_an_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "ACME-001"
            destination.mkdir()
            marker = destination / "keep.txt"
            marker.write_text("do not overwrite", encoding="utf-8")

            result = run_script(
                INIT_SCRIPT,
                "--company-id",
                "ACME-001",
                "--company-name",
                "Acme Materials",
                "--destination",
                str(destination),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("DESTINATION_EXISTS", result.stderr + result.stdout)
            self.assertEqual(marker.read_text(encoding="utf-8"), "do not overwrite")

    def test_valid_empty_library_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            result = self.validate(library)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["errors"], [])

    def test_cross_company_fact_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            fact = self.valid_fact()
            fact["company_id"] = "OTHER-CO"
            self.put_facts(library, fact)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CROSS_COMPANY_FACT", result.stdout)

    def test_unapproved_or_non_company_fact_cannot_be_e3(self):
        cases = (
            ("pending", "own_company", "E3_REQUIRES_APPROVAL"),
            ("approved", "supplier", "E3_SUBJECT_MISMATCH"),
            ("approved", "general_industry", "E3_SUBJECT_MISMATCH"),
            ("approved", "unknown", "E3_SUBJECT_MISMATCH"),
        )
        for review_status, subject_scope, error_code in cases:
            with self.subTest(review_status=review_status, subject_scope=subject_scope):
                with tempfile.TemporaryDirectory() as tmp:
                    library = self.initialize(Path(tmp))
                    self.add_source(library)
                    fact = self.valid_fact(subject_scope=subject_scope)
                    fact["review_status"] = review_status
                    if review_status != "approved":
                        fact["reviewed_by"] = None
                        fact["reviewed_at"] = None
                    self.put_facts(library, fact)

                    result = self.validate(library)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error_code, result.stdout)

    def test_inference_or_unknown_statement_cannot_be_promoted_to_e3(self):
        for statement_kind in ("inference", "unknown"):
            with self.subTest(statement_kind=statement_kind):
                with tempfile.TemporaryDirectory() as tmp:
                    library = self.initialize(Path(tmp))
                    self.add_source(library)
                    fact = self.valid_fact()
                    fact["statement_kind"] = statement_kind
                    self.put_facts(library, fact)

                    result = self.validate(library)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("E3_STATEMENT_KIND_MISMATCH", result.stdout)

    def test_evidence_level_controls_allowed_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            fact = self.valid_fact(evidence_level="E1")
            fact["allowed_use"] = ["external"]
            self.put_facts(library, fact)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ALLOWED_USE_EXCEEDS_EVIDENCE", result.stdout)

    def test_parameter_without_unit_or_test_context_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            fact = self.valid_fact()
            fact["unit"] = None
            fact["unit_status"] = "missing"
            fact["test_method"] = None
            fact["test_method_status"] = "missing"
            self.put_facts(library, fact)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PARAMETER_UNIT_UNRESOLVED", result.stdout)
            self.assertIn("PARAMETER_TEST_METHOD_UNRESOLVED", result.stdout)

    def test_one_source_may_support_fact_scoped_e3_e1_and_e0(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            registry_path = library / "00-管理" / "源文件清单.json"
            registry = load_json(registry_path)
            registry["sources"][0]["actual_subject"] = "mixed"
            write_json(registry_path, registry)
            e3 = self.valid_fact(fact_id="ACME-001-K-0001")
            e1 = self.valid_fact(
                fact_id="ACME-001-K-0002",
                evidence_level="E1",
                subject_scope="supplier",
            )
            e0 = self.valid_fact(
                fact_id="ACME-001-K-0003",
                evidence_level="E0",
                subject_scope="general_industry",
            )
            self.put_facts(library, e3, e1, e0)

            result = self.validate(library)

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_source_registry_rejects_blanket_evidence_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            registry_path = library / "00-管理" / "源文件清单.json"
            registry = load_json(registry_path)
            registry["sources"][0]["evidence_level"] = "E3"
            write_json(registry_path, registry)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCE_BLANKET_EVIDENCE_FORBIDDEN", result.stdout)

    def test_changed_source_hash_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            archive = library / "01-源文件封存" / "datasheet.txt"
            archive.write_text("source changed after intake", encoding="utf-8")

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCE_HASH_MISMATCH", result.stdout)

    def test_handoff_confirmed_fields_accept_only_approved_e3_fact_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            e1 = self.valid_fact(evidence_level="E1")
            self.put_facts(library, e1)
            packet_path = library / "04-开发交接" / "product-development-fact-packet.json"
            packet = load_json(packet_path)
            packet["product_development_fact_packet"]["confirmed_parameters"] = [
                "ACME-001-K-0001"
            ]
            write_json(packet_path, packet)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("HANDOFF_CONFIRMED_FACT_NOT_E3", result.stdout)

    def test_handoff_is_scoped_to_industry_application_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            packet_path = library / "04-开发交接" / "product-development-fact-packet.json"
            packet = load_json(packet_path)["product_development_fact_packet"]

            self.assertEqual(
                packet["allowed_use"], ["internal_industry_application_mapping"]
            )
            self.assertTrue(
                any("contains no industry routes" in item for item in packet["prohibited_inference"])
            )

    def test_handoff_conditions_and_limits_also_require_e3(self):
        for field in ("required_conditions", "known_limits"):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as tmp:
                    library = self.initialize(Path(tmp))
                    self.add_source(library)
                    e1 = self.valid_fact(evidence_level="E1")
                    self.put_facts(library, e1)
                    packet_path = library / "04-开发交接" / "product-development-fact-packet.json"
                    packet = load_json(packet_path)
                    packet["product_development_fact_packet"][field] = ["ACME-001-K-0001"]
                    write_json(packet_path, packet)

                    result = self.validate(library)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("HANDOFF_CONFIRMED_FACT_NOT_E3", result.stdout)

    def test_handoff_rejects_unregistered_approved_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            packet_path = library / "04-开发交接" / "product-development-fact-packet.json"
            packet = load_json(packet_path)
            packet["product_development_fact_packet"]["approved_references"] = [
                "ACME-001-S-9999"
            ]
            write_json(packet_path, packet)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("HANDOFF_UNKNOWN_SOURCE", result.stdout)

    def test_product_tree_rejects_unknown_fact_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            product_path = library / "03-产品体系" / "product-system.json"
            product = load_json(product_path)
            product["product_families"] = [
                {
                    "product_family_id": "ACME-001-PF-001",
                    "name": "Effect pigments",
                    "alias_terms": [],
                    "fact_ids": ["ACME-001-K-9999"],
                    "series": [],
                    "unresolved_structure": [],
                }
            ]
            write_json(product_path, product)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PRODUCT_TREE_UNKNOWN_FACT", result.stdout)

    def test_product_tree_rejects_another_company_identifier(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            product_path = library / "03-产品体系" / "product-system.json"
            product = load_json(product_path)
            product["product_families"] = [
                {
                    "product_family_id": "OTHER-CO-PF-001",
                    "name": "Effect pigments",
                    "alias_terms": [],
                    "fact_ids": [],
                    "series": [],
                    "unresolved_structure": [],
                }
            ]
            write_json(product_path, product)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CROSS_COMPANY_PRODUCT_ID", result.stdout)

    def test_change_log_is_company_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            changes_path = library / "00-管理" / "变更记录.json"
            changes = load_json(changes_path)
            changes["company_id"] = "OTHER-CO"
            write_json(changes_path, changes)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CROSS_COMPANY_FILE", result.stdout)

    def test_fact_packet_exporter_selects_only_approved_e3_scope_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = self.initialize(root)
            self.add_source(library)
            e3 = self.valid_fact(fact_id="ACME-001-K-0001")
            e2 = self.valid_fact(
                fact_id="ACME-001-K-0002",
                evidence_level="E2",
            )
            e2["fact_type"] = "property"
            self.put_facts(library, e3, e2)
            self.put_product_family(
                library,
                "ACME-001-K-0001",
                "ACME-001-K-0002",
            )
            output = root / "packet.json"

            result = run_script(
                EXPORT_FACT_PACKET_SCRIPT,
                str(library),
                "--product-family-id",
                "ACME-001-PF-001",
                "--output",
                str(output),
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = load_json(output)
            packet = payload["product_development_fact_packet"]
            self.assertEqual(payload["schema_version"], "1.2")
            self.assertEqual(packet["confirmed_parameters"], ["ACME-001-K-0001"])
            self.assertEqual(packet["confirmed_properties"], [])
            self.assertEqual(packet["approved_references"], ["ACME-001-S-0001"])
            self.assertEqual(
                set(packet["knowledge_snapshot"]),
                {"facts_sha256", "product_system_sha256", "source_registry_sha256"},
            )

    def test_readiness_view_rejects_cross_company_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = self.initialize(root)
            request_path = root / "request.json"
            write_json(
                request_path,
                {
                    "development_readiness_request": {
                        "request_id": "READY-001",
                        "company_id": "OTHER-CO",
                        "product_scope": "Effect pigments",
                        "route_candidate_id": "OTHER-CO-R-001",
                        "requested_dimensions": ["minimum_order_quantity"],
                        "declared_conditions": [],
                        "requested_at": "2026-07-29",
                    }
                },
            )

            result = run_script(
                EXPORT_READINESS_VIEW_SCRIPT,
                str(library),
                "--request",
                str(request_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CROSS_COMPANY_READINESS_REQUEST", result.stderr + result.stdout)

    def test_readiness_view_distinguishes_ready_conflict_unknown_and_stale(self):
        cases = (
            (50, "minimum_order_quantity", "2026-12-31", True, "可承接"),
            (10, "minimum_order_quantity", "2026-12-31", True, "已确认冲突"),
            (50, "minimum_order_quantity", "2026-12-31", False, "有条件"),
            (50, "lead_time", "2026-12-31", True, "未知"),
            (50, "minimum_order_quantity", "2026-01-01", True, "未知"),
        )
        for declared_value, dimension, valid_until, include_declared, expected in cases:
            with self.subTest(expected=expected, dimension=dimension):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    library = self.initialize(root)
                    self.add_source(library)
                    fact = self.commercial_fact(
                        fact_id="ACME-001-K-0001",
                        valid_until=valid_until,
                    )
                    self.put_facts(library, fact)
                    request_path = root / "request.json"
                    output = root / "view.json"
                    write_json(
                        request_path,
                        {
                            "development_readiness_request": {
                                "request_id": "READY-001",
                                "company_id": "ACME-001",
                                "product_scope": "Effect pigments",
                                "route_candidate_id": "ACME-001-R-001",
                                "intended_use_scope": ["industrial coatings"],
                                "geography_scope": ["DE"],
                                "customer_type_scope": ["manufacturer"],
                                "requested_dimensions": [dimension],
                                "declared_conditions": (
                                    [
                                        {
                                            "dimension": dimension,
                                            "value": declared_value,
                                            "unit": "kg",
                                        }
                                    ]
                                    if include_declared
                                    else []
                                ),
                                "requested_at": "2026-07-29",
                                "return_to": {
                                    "skill": "foreign-trade-customer-development",
                                    "task_route": "route_portfolio_review",
                                },
                            }
                        },
                    )

                    result = run_script(
                        EXPORT_READINESS_VIEW_SCRIPT,
                        str(library),
                        "--request",
                        str(request_path),
                        "--output",
                        str(output),
                    )

                    self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                    view = load_json(output)["development_readiness_view"]
                    self.assertEqual(view["readiness_state"], expected)
                    self.assertEqual(view["company_id"], "ACME-001")
                    self.assertEqual(view["request_id"], "READY-001")

    def test_e2_readiness_items_are_annex_only_and_never_change_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = self.initialize(root)
            self.add_source(library)
            fact = self.commercial_fact(
                fact_id="ACME-001-K-0001",
                evidence_level="E2",
            )
            self.put_facts(library, fact)
            request_path = root / "request.json"
            output = root / "view.json"
            write_json(
                request_path,
                {
                    "development_readiness_request": {
                        "request_id": "READY-001",
                        "company_id": "ACME-001",
                        "product_scope": "Effect pigments",
                        "route_candidate_id": "ACME-001-R-001",
                        "requested_dimensions": ["minimum_order_quantity"],
                        "declared_conditions": [
                            {
                                "dimension": "minimum_order_quantity",
                                "value": 50,
                                "unit": "kg",
                            }
                        ],
                        "requested_at": "2026-07-29",
                    }
                },
            )

            result = run_script(
                EXPORT_READINESS_VIEW_SCRIPT,
                str(library),
                "--request",
                str(request_path),
                "--output",
                str(output),
                "--include-e2-annex",
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            view = load_json(output)["development_readiness_view"]
            self.assertEqual(view["readiness_state"], "未知")
            self.assertEqual(view["confirmed_items"], [])
            self.assertEqual(
                [item["fact_id"] for item in view["internal_reference_annex"]],
                ["ACME-001-K-0001"],
            )

    def test_commercial_condition_requires_structured_dimension_and_review_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            fact = self.commercial_fact(fact_id="ACME-001-K-0001")
            fact["fact_value"] = {"value": 25}
            fact["review_due"] = "not-a-date"
            self.put_facts(library, fact)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("COMMERCIAL_CONDITION_INVALID", result.stdout)
            self.assertIn("COMMERCIAL_REVIEW_DATE_INVALID", result.stdout)

    def test_commercial_numeric_operator_rejects_non_numeric_fact_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            self.add_source(library)
            fact = self.commercial_fact(fact_id="ACME-001-K-0001")
            fact["fact_value"]["value"] = "twenty-five"
            self.put_facts(library, fact)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("COMMERCIAL_CONDITION_INVALID", result.stdout)

    def test_incomparable_declared_condition_becomes_conditional_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = self.initialize(root)
            self.add_source(library)
            fact = self.commercial_fact(fact_id="ACME-001-K-0001")
            self.put_facts(library, fact)
            request_path = root / "request.json"
            write_json(
                request_path,
                {
                    "development_readiness_request": {
                        "request_id": "READY-001",
                        "company_id": "ACME-001",
                        "product_scope": "Effect pigments",
                        "route_candidate_id": "ACME-001-R-001",
                        "requested_dimensions": ["minimum_order_quantity"],
                        "declared_conditions": [
                            {
                                "dimension": "minimum_order_quantity",
                                "value": "not-a-number",
                                "unit": "kg",
                            }
                        ],
                        "requested_at": "2026-07-29",
                    }
                },
            )

            result = run_script(
                EXPORT_READINESS_VIEW_SCRIPT,
                str(library),
                "--request",
                str(request_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            view = json.loads(result.stdout)["development_readiness_view"]
            self.assertEqual(view["readiness_state"], "有条件")

    def test_generated_handoff_requires_valid_knowledge_snapshot_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = self.initialize(Path(tmp))
            packet_path = library / "04-开发交接" / "product-development-fact-packet.json"
            payload = load_json(packet_path)
            packet = payload["product_development_fact_packet"]
            packet["generated_at"] = "2026-07-29"
            packet["product_family_id"] = "ACME-001-PF-001"
            packet["knowledge_snapshot"] = {
                "facts_sha256": "bad",
                "product_system_sha256": "bad",
                "source_registry_sha256": "bad",
            }
            write_json(packet_path, payload)

            result = self.validate(library)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("HANDOFF_SNAPSHOT_HASH_INVALID", result.stdout)


if __name__ == "__main__":
    unittest.main()
