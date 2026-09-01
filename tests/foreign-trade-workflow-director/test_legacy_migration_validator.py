from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = (
    ROOT
    / "plugins"
    / "foreign-trade-workflow-director"
    / "skills"
    / "foreign-trade-workflow-director"
    / "scripts"
    / "validate-legacy-governance-migration.py"
)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_fingerprint(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def run_validator(batch: Path, target: Path, phase: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3", str(VALIDATOR), "--batch-root", str(batch),
            "--target-governance-root", str(target), "--phase", phase,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def create_fixture(parent: Path) -> tuple[Path, Path, Path]:
    source = parent / "legacy-source"
    source.mkdir()
    (source / "ledger.md").write_text("finding-one\n", encoding="utf-8")
    (source / "skip-note.md").write_text("context\n", encoding="utf-8")

    target = parent / "governance"
    target.mkdir()
    (target / "governance-registry.yaml").write_text(
        json.dumps({
            "registry_id": "FTWG-REG-framework-fixture",
            "contract_id": "FTWG-INSPECTOR-GOVERNANCE",
            "contract_version": "1.0.0-draft.3",
            "single_editor_id": "editor-a",
            "activated_migration_batches": [],
        }, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for name in ("findings.jsonl", "improvement-events.jsonl", "validation-events.jsonl", "evidence-index.jsonl"):
        (target / name).write_bytes(b"")

    batch = parent / "migration-batch"
    batch.mkdir()
    manifest = {
        "template_record": False,
        "schema_version": "1.0.0-draft.1",
        "migration_batch_id": "FTWG-MIG-FIXTURE-0001",
        "migration_contract_id": "FTWG-LEGACY-GOVERNANCE-MIGRATION",
        "migration_contract_version": "1.0.0-draft.2",
        "phase_state": "mapping_reviewed",
        "discovery_roots": [{"root_id": "legacy-a", "path": str(source.resolve())}],
        "include_patterns": ["*.md"],
        "exclude_roots": [],
        "exclude_patterns": ["skip-*.md"],
        "follow_symlinks": False,
        "declared_sources": [{
            "source_id": "SRC-0001",
            "root_id": "legacy-a",
            "relative_path": "ledger.md",
            "sha256": sha_file(source / "ledger.md"),
            "byte_count": (source / "ledger.md").stat().st_size,
            "record_count": 1,
            "source_role": "authoritative_history",
            "governance_scope": "framework",
            "migration_eligible": True,
        }, {
            "source_id": "SRC-EXCLUDED-0001",
            "root_id": "legacy-a",
            "relative_path": "skip-note.md",
            "sha256": sha_file(source / "skip-note.md"),
            "byte_count": (source / "skip-note.md").stat().st_size,
            "record_count": 1,
            "source_role": "context_only",
            "governance_scope": "framework",
            "migration_eligible": False,
            "exclusion_reason": "Matched the frozen exclusion rule.",
        }],
        "expected_counts": {
            "discovered": 2, "included": 1, "excluded": 1, "duplicate": 0, "failed": 0,
        },
        "target_governance_root": str(target.resolve()),
        "target_registry_sha256": sha_file(target / "governance-registry.yaml"),
        "inventory_frozen_at": "2026-08-31T00:00:00Z",
        "activation_authorization": None,
    }
    manifest_path = batch / "legacy-governance-source-manifest.yaml"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    mapping = {
        "template_record": False,
        "schema_version": "1.0.0-draft.1",
        "mapping_id": "MAP-0001",
        "migration_batch_id": "FTWG-MIG-FIXTURE-0001",
        "source_id": "SRC-0001",
        "source_manifest_sha256": sha_file(manifest_path),
        "source_record_locator": "line:1",
        "mapping_decision": "context_only",
        "canonical_target_id": None,
        "evidence_references_and_hashes": [{"reference": "ledger.md#line:1", "sha256": sha_file(source / "ledger.md")}],
        "requires_revalidation": True,
        "reviewed_by": "reviewer-a",
        "authorization_reference": "AUTH-MAP-1",
    }
    (batch / "legacy-finding-mapping.jsonl").write_text(
        json.dumps(mapping, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    for name in (
        "migrated-finding-events.jsonl", "migrated-improvement-events.jsonl",
        "migrated-validation-events.jsonl", "migrated-evidence-events.jsonl",
    ):
        (batch / name).write_bytes(b"")
    report = {
        "template_record": False,
        "schema_version": "1.0.0-draft.1",
        "migration_batch_id": "FTWG-MIG-FIXTURE-0001",
        "phase": "dry-run",
        "result": "PASS",
        "manifest_sha256": sha_file(manifest_path),
        "mapping_sha256": sha_file(batch / "legacy-finding-mapping.jsonl"),
        "target_registry_sha256": sha_file(target / "governance-registry.yaml"),
        "candidate_event_counts": {"finding": 0, "improvement": 0, "validation": 0, "evidence": 0},
        "activation_authorized": False,
        "authorization_reference": None,
        "one_next_action": "Request governance_registry_write authorization.",
        "remaining_unverified": ["activation"],
    }
    (batch / "migration-validation-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return source, batch, target


class LegacyMigrationValidatorTests(unittest.TestCase):
    def test_inventory_proves_bounded_closure_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            source, batch, target = create_fixture(Path(temp))
            before = (tree_fingerprint(source), tree_fingerprint(batch), tree_fingerprint(target))
            result = run_validator(batch, target, "inventory")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "PASS")
            self.assertEqual(payload["actual_counts"], {
                "discovered": 2, "included": 1, "excluded": 1, "duplicate": 0, "failed": 0,
            })
            self.assertEqual(payload["missing_source_ids"], [])
            self.assertEqual(payload["undeclared_paths"], [])
            self.assertEqual(
                (tree_fingerprint(source), tree_fingerprint(batch), tree_fingerprint(target)),
                before,
            )

    def test_inventory_rejects_omitted_eligible_file_undeclared_source_and_count_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            source, batch, target = create_fixture(Path(temp))
            (source / "omitted.md").write_text("finding-two\n", encoding="utf-8")
            manifest_path = batch / "legacy-governance-source-manifest.yaml"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["declared_sources"].append({
                "source_id": "SRC-OUTSIDE",
                "root_id": "legacy-a",
                "relative_path": "../outside.md",
                "sha256": "0" * 64,
                "byte_count": 0,
                "record_count": 1,
                "source_role": "authoritative_history",
                "governance_scope": "framework",
                "migration_eligible": True,
            })
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result = run_validator(batch, target, "inventory")
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            issues = " ".join(payload["issues"])
            self.assertIn("omitted.md", issues)
            self.assertIn("outside authorized discovery root", issues)
            self.assertIn("expected counts", issues)

    def test_inventory_requires_manifest_records_for_excluded_files(self):
        with tempfile.TemporaryDirectory() as temp:
            _source, batch, target = create_fixture(Path(temp))
            manifest_path = batch / "legacy-governance-source-manifest.yaml"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["declared_sources"] = [
                source for source in manifest["declared_sources"]
                if source["source_id"] != "SRC-EXCLUDED-0001"
            ]
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result = run_validator(batch, target, "inventory")
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "skip-note.md",
                " ".join(json.loads(result.stdout)["issues"]),
            )

    def test_inventory_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            source, batch, target = create_fixture(parent)
            outside = parent / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            os.symlink(outside, source / "linked.md")
            result = run_validator(batch, target, "inventory")
            self.assertEqual(result.returncode, 2)
            self.assertIn("symlink", " ".join(json.loads(result.stdout)["issues"]))

    def test_mapping_rejects_duplicate_mapping_missing_source_hash_and_conflict(self):
        with tempfile.TemporaryDirectory() as temp:
            _source, batch, target = create_fixture(Path(temp))
            mapping_path = batch / "legacy-finding-mapping.jsonl"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping["source_manifest_sha256"] = None
            mapping["mapping_decision"] = "unresolved_conflict"
            mapping_path.write_text(
                json.dumps(mapping, separators=(",", ":")) + "\n"
                + json.dumps(mapping, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            result = run_validator(batch, target, "mapping")
            self.assertEqual(result.returncode, 2)
            issues = " ".join(json.loads(result.stdout)["issues"])
            self.assertIn("duplicate mapping", issues)
            self.assertIn("source manifest sha256", issues)
            self.assertIn("unresolved conflict", issues)

    def test_valid_dry_run_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            source, batch, target = create_fixture(Path(temp))
            before = (tree_fingerprint(source), tree_fingerprint(batch), tree_fingerprint(target))
            result = run_validator(batch, target, "dry-run")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "PASS")
            self.assertEqual(payload["mapping_closure"], {"eligible_records": 1, "mapped_records": 1})
            self.assertEqual(
                (tree_fingerprint(source), tree_fingerprint(batch), tree_fingerprint(target)),
                before,
            )

    def test_dry_run_rejects_stale_target_hash_and_historical_state_promotion(self):
        with tempfile.TemporaryDirectory() as temp:
            _source, batch, target = create_fixture(Path(temp))
            (target / "governance-registry.yaml").write_text("{}\n", encoding="utf-8")
            promoted = {
                "event_id": "EVT-MIG-1",
                "finding_id": "FND-MIG-1",
                "lifecycle_state": "verified_closed",
                "migration_provenance": {"migration_batch_id": "FTWG-MIG-FIXTURE-0001", "mapping_ids": ["MAP-0001"]},
            }
            (batch / "migrated-finding-events.jsonl").write_text(
                json.dumps(promoted) + "\n", encoding="utf-8"
            )
            result = run_validator(batch, target, "dry-run")
            self.assertEqual(result.returncode, 2)
            issues = " ".join(json.loads(result.stdout)["issues"])
            self.assertIn("target registry hash", issues)
            self.assertIn("verified_closed", issues)
            self.assertIn("event hash", issues)

    def test_activation_preflight_requires_explicit_authorization(self):
        with tempfile.TemporaryDirectory() as temp:
            _source, batch, target = create_fixture(Path(temp))
            missing = run_validator(batch, target, "activation-preflight")
            self.assertEqual(missing.returncode, 3)
            self.assertIn("governance_registry_write", " ".join(json.loads(missing.stdout)["unverified"]))

            manifest_path = batch / "legacy-governance-source-manifest.yaml"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["activation_authorization"] = {
                "authorization_class": "governance_registry_write",
                "user_authorization_reference": "AUTH-ACTIVATE-1",
                "single_editor_id": "editor-a",
            }
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            mapping_path = batch / "legacy-finding-mapping.jsonl"
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            mapping["source_manifest_sha256"] = sha_file(manifest_path)
            mapping_path.write_text(json.dumps(mapping, separators=(",", ":")) + "\n", encoding="utf-8")
            report_path = batch / "migration-validation-report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["manifest_sha256"] = sha_file(manifest_path)
            report["mapping_sha256"] = sha_file(mapping_path)
            report["activation_authorized"] = True
            report["authorization_reference"] = "AUTH-ACTIVATE-1"
            report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            passed = run_validator(batch, target, "activation-preflight")
            self.assertEqual(passed.returncode, 0, passed.stderr + passed.stdout)

    def test_post_activation_validates_receipt_and_append_only_target(self):
        with tempfile.TemporaryDirectory() as temp:
            _source, batch, target = create_fixture(Path(temp))
            receipt_path = batch / "migration-activation-receipt.json"
            receipt_path.write_text(json.dumps({"activation_state": "ACTIVE"}), encoding="utf-8")
            invalid = run_validator(batch, target, "post-activation")
            self.assertEqual(invalid.returncode, 2)
            self.assertIn("receipt", " ".join(json.loads(invalid.stdout)["issues"]))

            registry_sha = sha_file(target / "governance-registry.yaml")
            empty_sha = hashlib.sha256(b"").hexdigest()
            receipt = {
                "schema_version": "1.0.0-draft.1",
                "migration_batch_id": "FTWG-MIG-FIXTURE-0001",
                "migration_contract_id": "FTWG-LEGACY-GOVERNANCE-MIGRATION",
                "migration_contract_version": "1.0.0-draft.2",
                "target_registry_id": "FTWG-REG-framework-fixture",
                "authorization_class": "governance_registry_write",
                "user_authorization_reference": "AUTH-ACTIVATE-1",
                "single_editor_id": "editor-a",
                "target_before": {"registry_sha256": registry_sha},
                "target_after": {
                    "registry_sha256": registry_sha,
                    "findings_file_sha256": empty_sha,
                    "improvements_file_sha256": empty_sha,
                    "validations_file_sha256": empty_sha,
                    "evidence_file_sha256": empty_sha,
                },
                "appended_counts": {"finding_events": 0, "improvement_events": 0, "validation_events": 0, "evidence_events": 0},
                "post_activation_rebuild_result": "PASS",
                "activation_state": "ACTIVE",
                "remaining_unverified": [],
            }
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            valid = run_validator(batch, target, "post-activation")
            self.assertEqual(valid.returncode, 0, valid.stderr + valid.stdout)

            (target / "findings.jsonl").write_text('{"event_sha256":"historic"}\n', encoding="utf-8")
            receipt["target_after"]["findings_file_sha256"] = sha_file(target / "findings.jsonl")
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            preexisting_history = run_validator(batch, target, "post-activation")
            self.assertEqual(preexisting_history.returncode, 0, preexisting_history.stderr + preexisting_history.stdout)

            (target / "findings.jsonl").write_text('{"event_sha256":"rewritten"}\n', encoding="utf-8")
            invalidated = run_validator(batch, target, "post-activation")
            self.assertEqual(invalidated.returncode, 2)
            self.assertIn("append-only target hash", " ".join(json.loads(invalidated.stdout)["issues"]))


if __name__ == "__main__":
    unittest.main()
