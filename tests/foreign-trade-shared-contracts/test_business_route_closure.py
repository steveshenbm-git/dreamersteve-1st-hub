from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
MAP_SKILL = ROOT / "plugins/industry-application-map-builder/skills/industry-application-map-builder"
DEVELOPMENT_SKILL = ROOT / "plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development"
DIRECTOR_SKILL = ROOT / "plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director"
FREEZE_MANIFEST = MAP_SKILL / "scripts/freeze_company_product_packet_manifest.py"
VERIFY_ROUTE = DEVELOPMENT_SKILL / "scripts/verify_route_pool_packet.py"
VALIDATE_DIRECTION = DEVELOPMENT_SKILL / "scripts/validate_direction_validation.py"
VALIDATE_CLOSURE = DIRECTOR_SKILL / "scripts/validate_business_route_closure.py"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class BusinessRouteClosureContractTests(unittest.TestCase):
    def make_product_inputs(self, root: Path) -> tuple[Path, Path, Path]:
        library = root / "company-library"
        facts = library / "02-事实库/facts.json"
        write_json(library / "company.json", {"company_id": "ACME-001"})
        write_json(
            facts,
            {
                "schema_version": "1.0",
                "company_id": "ACME-001",
                "facts": [
                    {
                        "fact_id": "ACME-001-GLITTER-001",
                        "company_id": "ACME-001",
                        "subject_scope": "own_company",
                        "statement_kind": "source_fact",
                        "evidence_level": "E3",
                        "review_status": "approved",
                    },
                    {
                        "fact_id": "ACME-001-PEARL-001",
                        "company_id": "ACME-001",
                        "subject_scope": "own_company",
                        "statement_kind": "source_fact",
                        "evidence_level": "E3",
                        "review_status": "approved",
                    },
                ],
            },
        )
        packets = []
        for scope, fact_id, filename in (
            ("Glitter powder", "ACME-001-GLITTER-001", "glitter.json"),
            ("Pearlescent pigment", "ACME-001-PEARL-001", "pearl.json"),
        ):
            path = library / "04-开发交接" / filename
            write_json(
                path,
                {
                    "schema_version": "1.1",
                    "product_development_fact_packet": {
                        "company_id": "ACME-001",
                        "product_family": scope,
                        "confirmed_functions": [fact_id],
                        "required_conditions": [],
                        "known_limits": [],
                        "allowed_use": ["internal_industry_application_mapping"],
                    },
                },
            )
            packets.append(path)
        return library, packets[0], packets[1]

    def make_route_packet(
        self, root: Path, *, limited_state: str = "unknown", multi_product_input: bool = False
    ) -> tuple[Path, Path]:
        map_root = root / "map-root"
        company_root = map_root / "04-公司地图/ACME-001"
        company_root.mkdir(parents=True)
        snapshot: dict[str, str] = {"company_id": "ACME-001", "product_input_mode": "single_packet_legacy"}
        snapshot["product_input_mode"] = (
            "multi_packet_manifest_v1" if multi_product_input else "single_packet_legacy"
        )
        input_fields = [
            ("facts_path", "facts_sha256"),
            ("shared_taxonomy_path", "taxonomy_sha256"),
            ("shared_application_base_path", "application_base_sha256"),
        ]
        input_fields.insert(
            0,
            (
                "product_packet_manifest_path",
                "product_packet_manifest_sha256",
            )
            if multi_product_input
            else ("product_packet_path", "product_packet_sha256"),
        )
        for path_field, hash_field in input_fields:
            source = root / f"{path_field}.bin"
            source.write_bytes(path_field.encode("utf-8"))
            snapshot[path_field] = str(source.resolve())
            snapshot[hash_field] = sha256(source)
        company_map = company_root / "company-industry-application-map.xlsx"
        company_map.write_bytes(b"synthetic company map")
        producer_snapshot = {
            "company_map_path": str(company_map.relative_to(map_root)),
            "company_map_sha256": sha256(company_map),
        }
        route = {
            "route_candidate_id": "ACME-001-R-LEAD",
            "company_id": "ACME-001",
            "product_scope": "Pearlescent pigment",
            "business_industry_id": "BVI-010",
            "business_route_closure_id": "CLOSE-001",
            "map_route_status": "路线线索",
            "evidence_state": "supported",
            "technical_match_state": limited_state,
            "regulatory_qualification_state": "unknown",
            "known_limit_conflict": False,
            "customer_discovery_readiness": "ready_for_limited_direction_validation",
        }
        closure = {
            "closure_id": "CLOSE-001",
            "route_candidate_id": route["route_candidate_id"],
            "business_industry_id": "BVI-010",
            "application_closure_state": "supported",
            "application_evidence_ids": ["APP-E-001"],
            "application_source_groups": ["APP-SEED-GROUP"],
            "customer_discovery_readiness": "ready_for_limited_direction_validation",
            "regulatory_qualification_state": "unknown",
            "allowed_downstream_actions": ["compile_and_validate_direction"],
            "prohibited_downstream_actions": [
                "recommend_product",
                "claim_product_fit",
                "claim_regulatory_compliance",
                "scan_candidates",
            ],
            "review_result": "PASS",
        }
        export_id = "ACME-001-EXPORT-2026-09-01-0001"
        registry_path = company_root / "route-pool-export-registry.json"
        packet_path = company_root / "company-route-pool-packet.json"
        packet = {
            "schema_version": "1.1",
            "company_route_pool_packet": {
                "export_id": export_id,
                "company_id": "ACME-001",
                "product_scope": "",
                "product_scopes": ["Glitter powder", "Pearlescent pigment"],
                "input_snapshot": snapshot,
                "producer_snapshot": deepcopy(producer_snapshot),
                "route_candidates": [],
                "route_leads": [route],
                "route_closures": [closure],
                "deferred_routes": [],
                "excluded_routes": [],
                "target_skill": "foreign-trade-customer-development",
                "producer_registry_reference": {
                    "map_root": str(map_root.resolve()),
                    "path": str(registry_path.relative_to(map_root)),
                    "export_id": export_id,
                },
            },
        }
        write_json(packet_path, packet)
        write_json(
            registry_path,
            {
                "schema_version": "1.0",
                "company_id": "ACME-001",
                "exports": [
                    {
                        "export_id": export_id,
                        "company_id": "ACME-001",
                        "packet_path": str(packet_path.relative_to(map_root)),
                        "packet_sha256": sha256(packet_path),
                        "input_snapshot": deepcopy(snapshot),
                        "producer_snapshot": deepcopy(producer_snapshot),
                        "route_candidate_ids": [route["route_candidate_id"]],
                        "validator_version": "1.2",
                        "validated_at": "2026-09-01",
                        "state": "current",
                        "invalidation_reason": None,
                    }
                ],
            },
        )
        return map_root, packet_path

    def resign_packet(self, map_root: Path, packet_path: Path) -> None:
        registry_path = map_root / "04-公司地图/ACME-001/route-pool-export-registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["exports"][0]["packet_sha256"] = sha256(packet_path)
        write_json(registry_path, registry)

    def test_manifest_freezer_keeps_two_product_fact_scopes_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library, glitter, pearl = self.make_product_inputs(root)
            output = root / "company-product-packet-manifest.json"
            result = run(
                FREEZE_MANIFEST,
                "--company-id", "ACME-001",
                "--company-library-root", str(library),
                "--product-packet", f"Glitter powder={glitter}",
                "--product-packet", f"Pearlescent pigment={pearl}",
                "--output", str(output),
                "--frozen-at", "2026-09-01T00:00:00Z",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            body = json.loads(output.read_text(encoding="utf-8"))["company_product_packet_manifest"]
            self.assertEqual(body["company_id"], "ACME-001")
            self.assertEqual([item["product_scope"] for item in body["packets"]], ["Glitter powder", "Pearlescent pigment"])
            self.assertEqual(body["facts_sha256"], sha256(library / "02-事实库/facts.json"))
            self.assertNotEqual(body["packets"][0]["product_packet_sha256"], body["packets"][1]["product_packet_sha256"])

    def test_supported_route_lead_with_unknown_qualification_enters_limited_validation_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path = self.make_route_packet(Path(tmp))
            result = run(
                VERIFY_ROUTE,
                str(packet_path),
                "--map-root", str(map_root),
                "--company-id", "ACME-001",
                "--route-id", "ACME-001-R-LEAD",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["selected_route_mode"], "limited_direction_validation")
            self.assertEqual(report["salesperson_scan_authorization"], "blocked")
            self.assertIn("claim_product_fit", report["prohibited_claims"])

    def test_multi_product_input_snapshot_is_verified_without_legacy_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path = self.make_route_packet(
                Path(tmp), multi_product_input=True
            )
            result = run(
                VERIFY_ROUTE,
                str(packet_path),
                "--map-root", str(map_root),
                "--company-id", "ACME-001",
                "--route-id", "ACME-001-R-LEAD",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_violated_technical_state_cannot_use_limited_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path = self.make_route_packet(Path(tmp), limited_state="violated")
            result = run(
                VERIFY_ROUTE,
                str(packet_path),
                "--map-root", str(map_root),
                "--company-id", "ACME-001",
                "--route-id", "ACME-001-R-LEAD",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("LIMITED_ROUTE_QUALIFICATION_BLOCKED", result.stdout)

    def test_direction_validation_rejects_seed_holdout_dependency_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "direction-validation.json"
            write_json(
                path,
                {
                    "direction_validation_packet_v1": {
                        "contract_version": "1.0",
                        "validation_id": "DV-001",
                        "company_id": "ACME-001",
                        "route_id": "ACME-001-R-LEAD",
                        "business_route_closure_id": "CLOSE-001",
                        "validation_state": "PASS",
                        "salesperson_scan_authorization": "blocked",
                        "evidence": [
                            {"evidence_id": "E-SEED", "evidence_role": "application_seed", "source_dependency_group": "GROUP-1", "source_reference": "https://seed.example", "observed_company_id": "SEED-CO"},
                            {"evidence_id": "E-HOLD", "evidence_role": "direction_holdout", "source_dependency_group": "GROUP-1", "source_reference": "https://holdout.example", "observed_company_id": "HOLD-CO"},
                        ],
                    }
                },
            )
            result = run(VALIDATE_DIRECTION, str(path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SEED_HOLDOUT_DEPENDENCY_OVERLAP", result.stdout)

    def test_cross_skill_receipt_preserves_global_semantic_block_and_scan_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            map_root, route_packet = self.make_route_packet(root)
            direction = route_packet.parent / "direction-validation.json"
            write_json(
                direction,
                {
                    "direction_validation_packet_v1": {
                        "contract_version": "1.0",
                        "validation_id": "DV-001",
                        "company_id": "ACME-001",
                        "route_id": "ACME-001-R-LEAD",
                        "business_route_closure_id": "CLOSE-001",
                        "validation_state": "PASS",
                        "salesperson_scan_authorization": "blocked",
                        "evidence": [
                            {"evidence_id": "E-SEED", "evidence_role": "application_seed", "source_dependency_group": "SEED-GROUP", "source_reference": "https://seed.example", "observed_company_id": "SEED-CO"},
                            {"evidence_id": "E-HOLD", "evidence_role": "direction_holdout", "source_dependency_group": "HOLD-GROUP", "source_reference": "https://holdout.example", "observed_company_id": "HOLD-CO"},
                        ],
                    }
                },
            )
            receipt = route_packet.parent / "business-route-closure-receipt.json"
            write_json(
                receipt,
                {
                    "business_route_closure_receipt_v1": {
                        "contract_version": "1.0",
                        "closure_receipt_id": "BRC-001",
                        "company_id": "ACME-001",
                        "route_id": "ACME-001-R-LEAD",
                        "business_industry_id": "BVI-010",
                        "route_packet_reference": route_packet.name,
                        "route_packet_sha256": sha256(route_packet),
                        "direction_validation_reference": direction.name,
                        "direction_validation_sha256": sha256(direction),
                        "route_scoped_application_closure_state": "PASS",
                        "global_semantic_stage_effect": "none",
                        "customer_discovery_readiness": "ready_for_limited_direction_validation",
                        "salesperson_scan_authorization": "blocked",
                        "allowed_next_actions": ["present_direction_for_salesperson_scan_decision"],
                        "prohibited_next_actions": ["scan_candidates", "claim_product_fit", "claim_regulatory_compliance"],
                        "validated_at": "2026-09-01T00:00:00Z",
                    }
                },
            )
            result = run(VALIDATE_CLOSURE, str(receipt))
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["result"], "PASS")
            self.assertEqual(report["global_semantic_stage_effect"], "none")
            self.assertEqual(report["salesperson_scan_authorization"], "blocked")

    def test_cross_skill_receipt_rechecks_holdout_company_independence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, route_packet = self.make_route_packet(root)
            direction = route_packet.parent / "direction-validation.json"
            write_json(
                direction,
                {
                    "direction_validation_packet_v1": {
                        "contract_version": "1.0",
                        "validation_id": "DV-OVERLAP",
                        "company_id": "ACME-001",
                        "route_id": "ACME-001-R-LEAD",
                        "business_route_closure_id": "CLOSE-001",
                        "validation_state": "PASS",
                        "salesperson_scan_authorization": "blocked",
                        "evidence": [
                            {"evidence_id": "E-SEED", "evidence_role": "application_seed", "source_dependency_group": "SEED-GROUP", "source_reference": "https://seed.example", "observed_company_id": "SAME-CO"},
                            {"evidence_id": "E-HOLD", "evidence_role": "direction_holdout", "source_dependency_group": "HOLD-GROUP", "source_reference": "https://holdout.example", "observed_company_id": "SAME-CO"},
                        ],
                    }
                },
            )
            standalone = run(VALIDATE_DIRECTION, str(direction))
            self.assertNotEqual(standalone.returncode, 0)
            self.assertIn("SEED_HOLDOUT_COMPANY_OVERLAP", standalone.stdout)

            receipt = route_packet.parent / "business-route-closure-receipt.json"
            write_json(
                receipt,
                {
                    "business_route_closure_receipt_v1": {
                        "contract_version": "1.0",
                        "closure_receipt_id": "BRC-OVERLAP",
                        "company_id": "ACME-001",
                        "route_id": "ACME-001-R-LEAD",
                        "business_industry_id": "BVI-010",
                        "route_packet_reference": route_packet.name,
                        "route_packet_sha256": sha256(route_packet),
                        "direction_validation_reference": direction.name,
                        "direction_validation_sha256": sha256(direction),
                        "route_scoped_application_closure_state": "PASS",
                        "global_semantic_stage_effect": "none",
                        "customer_discovery_readiness": "ready_for_limited_direction_validation",
                        "salesperson_scan_authorization": "blocked",
                        "allowed_next_actions": ["present_direction_for_salesperson_scan_decision"],
                        "prohibited_next_actions": ["scan_candidates", "claim_product_fit", "claim_regulatory_compliance"],
                        "validated_at": "2026-09-01T00:00:00Z",
                    }
                },
            )
            receipt_result = run(VALIDATE_CLOSURE, str(receipt))
            self.assertNotEqual(receipt_result.returncode, 0)
            self.assertIn("DIRECTION_VALIDATION_COMPANY_OVERLAP", receipt_result.stdout)


if __name__ == "__main__":
    unittest.main()
