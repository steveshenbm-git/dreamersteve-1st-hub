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
SCRIPT = (
    ROOT
    / "plugins"
    / "foreign-trade-customer-development"
    / "skills"
    / "foreign-trade-customer-development"
    / "scripts"
    / "verify_route_pool_packet.py"
)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RoutePacketPreflightTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> tuple[Path, Path, dict]:
        map_root = root / "map-root"
        company_root = map_root / "04-公司地图" / "ACME-001"
        company_root.mkdir(parents=True)
        snapshot: dict[str, str] = {"company_id": "ACME-001"}
        for path_field, hash_field in (
            ("product_packet_path", "product_packet_sha256"),
            ("facts_path", "facts_sha256"),
            ("shared_taxonomy_path", "taxonomy_sha256"),
            ("shared_application_base_path", "application_base_sha256"),
        ):
            source = root / f"{path_field}.bin"
            source.write_bytes(path_field.encode("utf-8"))
            snapshot[path_field] = str(source.resolve())
            snapshot[hash_field] = sha256(source)

        export_id = "ACME-001-EXPORT-2026-07-29-0001"
        registry_path = company_root / "route-pool-export-registry.json"
        packet_path = company_root / "company-route-pool-packet.json"
        company_map_path = company_root / "company-industry-application-map.xlsx"
        company_map_path.write_bytes(b"synthetic company map")
        producer_snapshot = {
            "company_map_path": str(company_map_path.relative_to(map_root)),
            "company_map_sha256": sha256(company_map_path),
        }
        packet = {
            "schema_version": "1.0",
            "company_route_pool_packet": {
                "export_id": export_id,
                "company_id": "ACME-001",
                "product_scope": "demo-product",
                "input_snapshot": snapshot,
                "producer_snapshot": deepcopy(producer_snapshot),
                "route_candidates": [
                    {
                        "route_candidate_id": "ACME-001-R-0001",
                        "company_id": "ACME-001",
                        "map_route_status": "路线候选",
                    }
                ],
                "route_leads": [
                    {
                        "route_candidate_id": "ACME-001-R-0002",
                        "company_id": "ACME-001",
                        "map_route_status": "路线线索",
                    }
                ],
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
        registry = {
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
                    "route_candidate_ids": ["ACME-001-R-0001", "ACME-001-R-0002"],
                    "validator_version": "1.1",
                    "validated_at": "2026-07-29",
                    "state": "current",
                    "invalidation_reason": None,
                }
            ],
        }
        write_json(registry_path, registry)
        return map_root, packet_path, registry

    def run_verify(
        self,
        map_root: Path,
        packet_path: Path,
        route_id: str = "ACME-001-R-0001",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(packet_path),
                "--map-root",
                str(map_root),
                "--company-id",
                "ACME-001",
                "--route-candidate-id",
                route_id,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_current_registered_packet_and_selected_candidate_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, _ = self.build_fixture(Path(tmp))

            result = self.run_verify(map_root, packet_path)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                report["selected_route"]["route_candidate_id"],
                "ACME-001-R-0001",
            )

    def test_tampered_packet_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, _ = self.build_fixture(Path(tmp))
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            packet["company_route_pool_packet"]["product_scope"] = "tampered"
            write_json(packet_path, packet)

            result = self.run_verify(map_root, packet_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ROUTE_PACKET_HASH_MISMATCH", result.stdout)

    def test_stale_registry_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, registry = self.build_fixture(Path(tmp))
            registry["exports"][0]["state"] = "stale"
            registry_path = map_root / "04-公司地图/ACME-001/route-pool-export-registry.json"
            write_json(registry_path, registry)

            result = self.run_verify(map_root, packet_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ROUTE_EXPORT_NOT_CURRENT", result.stdout)

    def test_route_lead_cannot_be_selected_for_direction_compilation(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, _ = self.build_fixture(Path(tmp))

            result = self.run_verify(map_root, packet_path, "ACME-001-R-0002")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SELECTED_ROUTE_NOT_ELIGIBLE", result.stdout)

    def test_changed_snapshot_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, _ = self.build_fixture(Path(tmp))
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            source_path = Path(
                packet["company_route_pool_packet"]["input_snapshot"][
                    "facts_path"
                ]
            )
            source_path.write_bytes(b"changed")

            result = self.run_verify(map_root, packet_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("INPUT_SNAPSHOT_HASH_MISMATCH", result.stdout)

    def test_changed_source_company_map_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, _ = self.build_fixture(Path(tmp))
            company_map = (
                map_root
                / "04-公司地图/ACME-001/company-industry-application-map.xlsx"
            )
            company_map.write_bytes(b"changed company map")

            result = self.run_verify(map_root, packet_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ROUTE_EXPORT_SOURCE_MAP_STALE", result.stdout)

    def test_copied_packet_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, _ = self.build_fixture(Path(tmp))
            copied = packet_path.with_name("copied-route-packet.json")
            copied.write_bytes(packet_path.read_bytes())

            result = self.run_verify(map_root, copied)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ROUTE_PACKET_PATH_MISMATCH", result.stdout)

    def test_cross_company_packet_is_rejected_even_when_registry_hash_is_updated(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, registry = self.build_fixture(Path(tmp))
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            packet["company_route_pool_packet"]["company_id"] = "OTHER-CO"
            write_json(packet_path, packet)
            registry["exports"][0]["packet_sha256"] = sha256(packet_path)
            registry_path = map_root / "04-公司地图/ACME-001/route-pool-export-registry.json"
            write_json(registry_path, registry)

            result = self.run_verify(map_root, packet_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CROSS_COMPANY_ROUTE_PACKET", result.stdout)

    def test_missing_producer_registry_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            map_root, packet_path, _ = self.build_fixture(Path(tmp))
            registry_path = map_root / "04-公司地图/ACME-001/route-pool-export-registry.json"
            registry_path.unlink()

            result = self.run_verify(map_root, packet_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ROUTE_EXPORT_REGISTRY_MISSING", result.stdout)


if __name__ == "__main__":
    unittest.main()
