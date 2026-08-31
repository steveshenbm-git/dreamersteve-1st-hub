from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
TOOL = (
    ROOT
    / "plugins"
    / "foreign-trade-workflow-director"
    / "skills"
    / "foreign-trade-workflow-director"
    / "scripts"
    / "workflow-governance.py"
)
EMPTY_SHA = hashlib.sha256(b"").hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical_event_hash(event: dict) -> str:
    payload = {key: value for key, value in event.items() if key != "event_sha256"}
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return sha_bytes(encoded)


def tree_fingerprint(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def base_registry(root: Path, *, editor: str = "editor-a") -> dict:
    return {
        "schema_version": "1.0.0-draft.1",
        "registry_id": "FTWG-REG-framework-fixture",
        "contract_id": "FTWG-INSPECTOR-GOVERNANCE",
        "contract_version": "1.0.0-draft.2",
        "company_id": None,
        "framework_id": "framework-fixture",
        "governance_root": str(root.resolve()),
        "parent_framework_registry_reference": None,
        "parent_framework_registry_sha256": None,
        "inherited_finding_ids": [],
        "blueprint_id": "foreign-trade-complete-workflow",
        "blueprint_version": "0.4.0-beta.1",
        "single_editor_id": editor,
        "findings_log": {
            "reference": "findings.jsonl",
            "event_count": 0,
            "terminal_event_sha256": None,
            "file_sha256": EMPTY_SHA,
        },
        "improvement_log": {
            "reference": "improvement-events.jsonl",
            "event_count": 0,
            "terminal_event_sha256": None,
            "file_sha256": EMPTY_SHA,
        },
        "validation_log": {
            "reference": "validation-events.jsonl",
            "event_count": 0,
            "terminal_event_sha256": None,
            "file_sha256": EMPTY_SHA,
        },
        "evidence_index": {
            "reference": "evidence-index.jsonl",
            "record_count": 0,
            "terminal_event_sha256": None,
            "file_sha256": EMPTY_SHA,
        },
        "registered_skills": [],
        "improvement_cycles": [],
        "activated_migration_batches": [],
        "highest_open_disposition": "continue",
        "active_blocking_finding_ids": [],
        "latest_preflight_reference": None,
        "latest_preflight_sha256": None,
        "one_next_action": None,
        "next_action_owner": None,
        "next_authorization_required": None,
        "snapshot_sequence": 0,
        "rebuilt_from_logs": True,
        "last_rebuilt_at": None,
    }


def create_root(parent: Path, *, editor: str = "editor-a") -> Path:
    root = parent / "governance"
    root.mkdir()
    for name in (
        "findings.jsonl",
        "improvement-events.jsonl",
        "validation-events.jsonl",
        "evidence-index.jsonl",
    ):
        (root / name).write_bytes(b"")
    registry = base_registry(root, editor=editor)
    (root / "governance-registry.yaml").write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "governance-summary.md").write_text(
        "# Workflow Governance Summary\n\n"
        "- registry_id: FTWG-REG-framework-fixture\n"
        "- highest_open_disposition: continue\n"
        "- one_next_action: null\n",
        encoding="utf-8",
    )
    return root


def finding_candidate(*, event_id: str = "FTWG-EVT-20260831-0001") -> dict:
    return {
        "schema_version": "1.0.0-draft.1",
        "event_id": event_id,
        "event_type": "opened",
        "finding_id": "FTWG-FND-flow-20260831-0001",
        "title": "Portable fixture finding",
        "company_id": None,
        "framework_id": "framework-fixture",
        "work_unit_id": None,
        "task_id": None,
        "affected_skill_id": "portable-specialist-fixture",
        "affected_skill_version": "0.1.0",
        "affected_source_commit": None,
        "affected_scope": ["fixture-stage"],
        "evidence": [{"reference": "fixture-evidence", "sha256": None, "evidence_role": "observed_failure"}],
        "severity": "record",
        "flow_disposition": "continue",
        "flow_impact": "No impact on the current safe action.",
        "temporary_handling": "Preserve and continue.",
        "later_fix": "Review in the next improvement cycle.",
        "lifecycle_state": "open",
        "related_improvement_ids": [],
        "required_validation_layers": ["deterministic_regression"],
        "completed_validation_layers": [],
        "related_finding_ids": [],
        "supersedes_event_id": None,
        "user_authorization_reference": "AUTH-FIXTURE-1",
        "authorization_class": "governance_registry_write",
        "observed_at": None,
        "recorded_at": "2026-08-31T00:00:00Z",
        "recorder_role": "workflow_director",
        "one_next_action": "Continue the authorized fixture action.",
        "next_action_owner": "workflow_director",
        "next_authorization_required": None,
    }


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(TOOL), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class GovernanceToolTests(unittest.TestCase):
    def test_validate_is_read_only_for_valid_empty_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_root(Path(temp))
            before = tree_fingerprint(root)
            result = run_tool("validate", "--governance-root", str(root))
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "PASS")
            self.assertEqual(payload["operation"], "validate")
            self.assertIsNone(payload["one_next_action"])
            self.assertEqual(tree_fingerprint(root), before)

    def test_append_computes_chain_and_only_changes_declared_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = create_root(parent)
            candidate_path = parent / "candidate.json"
            candidate_path.write_text(json.dumps(finding_candidate()), encoding="utf-8")
            registry_sha = sha_file(root / "governance-registry.yaml")
            before = tree_fingerprint(root)
            old_log = (root / "findings.jsonl").read_bytes()

            result = run_tool(
                "append", "--governance-root", str(root),
                "--event-kind", "finding", "--event-file", str(candidate_path),
                "--authorization-reference", "AUTH-FIXTURE-1",
                "--single-editor-id", "editor-a",
                "--expected-registry-sha256", registry_sha,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "PASS")
            self.assertEqual(payload["sequence"], 1)
            self.assertEqual(payload["event_id"], "FTWG-EVT-20260831-0001")

            new_log = (root / "findings.jsonl").read_bytes()
            self.assertTrue(new_log.startswith(old_log))
            event = json.loads(new_log.decode("utf-8").strip())
            self.assertEqual(event["sequence"], 1)
            self.assertIsNone(event["previous_event_sha256"])
            self.assertEqual(event["event_sha256"], canonical_event_hash(event))
            changed = {
                name for name, digest in tree_fingerprint(root).items()
                if before.get(name) != digest
            }
            self.assertEqual(
                changed,
                {"findings.jsonl", "governance-registry.yaml", "governance-summary.md"},
            )
            validate = run_tool("validate", "--governance-root", str(root))
            self.assertEqual(validate.returncode, 0, validate.stderr + validate.stdout)

    def test_append_rejects_stale_hash_wrong_editor_and_wrong_authorization_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = create_root(parent)
            event_file = parent / "candidate.json"
            event_file.write_text(json.dumps(finding_candidate()), encoding="utf-8")
            base_args = [
                "append", "--governance-root", str(root), "--event-kind", "finding",
                "--event-file", str(event_file), "--authorization-reference", "AUTH-FIXTURE-1",
                "--single-editor-id", "editor-a", "--expected-registry-sha256",
                sha_file(root / "governance-registry.yaml"),
            ]
            variants = [
                base_args[:-1] + ["0" * 64],
                base_args[: base_args.index("--single-editor-id") + 1] + ["editor-b"] + base_args[base_args.index("--expected-registry-sha256"):],
                base_args[: base_args.index("--authorization-reference") + 1] + ["AUTH-OTHER"] + base_args[base_args.index("--single-editor-id"):],
            ]
            for args in variants:
                before = tree_fingerprint(root)
                result = run_tool(*args)
                self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                self.assertEqual(json.loads(result.stdout)["result"], "FAIL")
                self.assertEqual(tree_fingerprint(root), before)

    def test_validate_rejects_duplicate_ids_broken_chain_and_unproved_closure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_root(Path(temp))
            first = finding_candidate()
            first.update({"sequence": 1, "previous_event_sha256": None})
            first["event_sha256"] = canonical_event_hash(first)
            second = dict(first)
            second["sequence"] = 2
            second["previous_event_sha256"] = "f" * 64
            second["lifecycle_state"] = "verified_closed"
            second["event_sha256"] = canonical_event_hash(second)
            (root / "findings.jsonl").write_text(
                json.dumps(first, sort_keys=True, separators=(",", ":")) + "\n"
                + json.dumps(second, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            result = run_tool("validate", "--governance-root", str(root))
            self.assertEqual(result.returncode, 2, result.stdout)
            issues = " ".join(json.loads(result.stdout)["issues"])
            self.assertIn("duplicate event id", issues)
            self.assertIn("previous event hash", issues)
            self.assertIn("verified_closed", issues)

    def test_verified_closed_requires_matching_current_version_validation_events(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_root(Path(temp))
            event = finding_candidate()
            event["lifecycle_state"] = "verified_closed"
            event["completed_validation_layers"] = ["deterministic_regression"]
            event["one_next_action"] = None
            event.update({"sequence": 1, "previous_event_sha256": None})
            event["event_sha256"] = canonical_event_hash(event)
            finding_path = root / "findings.jsonl"
            finding_path.write_text(
                json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            registry_path = root / "governance-registry.yaml"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["findings_log"] = {
                "reference": "findings.jsonl",
                "event_count": 1,
                "terminal_event_sha256": event["event_sha256"],
                "file_sha256": sha_file(finding_path),
            }
            registry_path.write_text(
                json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            result = run_tool("validate", "--governance-root", str(root))
            self.assertEqual(result.returncode, 2)
            issues = " ".join(json.loads(result.stdout)["issues"])
            self.assertIn("matching current-version validation event", issues)

    def test_append_rejects_event_without_stable_id(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = create_root(parent)
            candidate = finding_candidate()
            candidate.pop("event_id")
            event_file = parent / "candidate.json"
            event_file.write_text(json.dumps(candidate), encoding="utf-8")
            before = tree_fingerprint(root)
            result = run_tool(
                "append", "--governance-root", str(root), "--event-kind", "finding",
                "--event-file", str(event_file), "--authorization-reference", "AUTH-FIXTURE-1",
                "--single-editor-id", "editor-a", "--expected-registry-sha256",
                sha_file(root / "governance-registry.yaml"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("event_id", " ".join(json.loads(result.stdout)["issues"]))
            self.assertEqual(tree_fingerprint(root), before)

    def test_missing_root_multiple_events_and_symlink_escape_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            missing = parent / "missing"
            result = run_tool("validate", "--governance-root", str(missing))
            self.assertEqual(result.returncode, 2)
            self.assertFalse(missing.exists())

            root = create_root(parent)
            event_file = parent / "events.json"
            event_file.write_text(json.dumps([finding_candidate(), finding_candidate()]), encoding="utf-8")
            result = run_tool(
                "append", "--governance-root", str(root), "--event-kind", "finding",
                "--event-file", str(event_file), "--authorization-reference", "AUTH-FIXTURE-1",
                "--single-editor-id", "editor-a", "--expected-registry-sha256",
                sha_file(root / "governance-registry.yaml"),
            )
            self.assertEqual(result.returncode, 2)

            outside = parent / "outside.jsonl"
            outside.write_bytes(b"")
            (root / "evidence-index.jsonl").unlink()
            os.symlink(outside, root / "evidence-index.jsonl")
            result = run_tool("validate", "--governance-root", str(root))
            self.assertEqual(result.returncode, 2)
            self.assertIn("symlink", " ".join(json.loads(result.stdout)["issues"]))

    def test_rebuild_repairs_only_stale_derived_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_root(Path(temp))
            registry = json.loads((root / "governance-registry.yaml").read_text(encoding="utf-8"))
            registry["findings_log"]["event_count"] = 99
            (root / "governance-registry.yaml").write_text(
                json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            before_logs = {name: sha_file(root / name) for name in (
                "findings.jsonl", "improvement-events.jsonl", "validation-events.jsonl", "evidence-index.jsonl"
            )}
            result = run_tool(
                "rebuild", "--governance-root", str(root),
                "--authorization-reference", "AUTH-FIXTURE-REBUILD",
                "--single-editor-id", "editor-a",
                "--expected-registry-sha256", sha_file(root / "governance-registry.yaml"),
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(result.stdout)["result"], "PASS")
            self.assertEqual(
                before_logs,
                {name: sha_file(root / name) for name in before_logs},
            )
            validate = run_tool("validate", "--governance-root", str(root))
            self.assertEqual(validate.returncode, 0, validate.stderr + validate.stdout)

    def test_rebuild_restores_a_missing_derived_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_root(Path(temp))
            (root / "governance-summary.md").unlink()
            result = run_tool(
                "rebuild", "--governance-root", str(root),
                "--authorization-reference", "AUTH-FIXTURE-REBUILD",
                "--single-editor-id", "editor-a",
                "--expected-registry-sha256", sha_file(root / "governance-registry.yaml"),
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue((root / "governance-summary.md").is_file())
            validate = run_tool("validate", "--governance-root", str(root))
            self.assertEqual(validate.returncode, 0, validate.stderr + validate.stdout)

    def test_rebuild_failure_after_append_preserves_event_for_explicit_rebuild(self):
        self.assertTrue(TOOL.exists())
        spec = importlib.util.spec_from_file_location("workflow_governance", TOOL)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = create_root(parent)
            event_file = parent / "candidate.json"
            event_file.write_text(json.dumps(finding_candidate()), encoding="utf-8")
            args = types.SimpleNamespace(
                governance_root=str(root), event_kind="finding", event_file=str(event_file),
                authorization_reference="AUTH-FIXTURE-1", single_editor_id="editor-a",
                expected_registry_sha256=sha_file(root / "governance-registry.yaml"),
            )
            real_replace = module.os.replace

            def fail_summary_replace(source, destination):
                if Path(destination).name == "governance-summary.md":
                    raise OSError("simulated summary replace failure")
                return real_replace(source, destination)

            with mock.patch.object(module.os, "replace", side_effect=fail_summary_replace):
                code, payload = module.append_operation(args)
            self.assertEqual(code, 2)
            self.assertEqual(payload["result"], "FAIL")
            self.assertTrue(payload["event_appended"])
            self.assertTrue(payload["derived_files_stale"])
            self.assertEqual(len((root / "findings.jsonl").read_text(encoding="utf-8").splitlines()), 1)

            rebuild = run_tool(
                "rebuild", "--governance-root", str(root),
                "--authorization-reference", "AUTH-FIXTURE-REBUILD",
                "--single-editor-id", "editor-a",
                "--expected-registry-sha256", sha_file(root / "governance-registry.yaml"),
            )
            self.assertEqual(rebuild.returncode, 0, rebuild.stderr + rebuild.stdout)
            self.assertEqual(len((root / "findings.jsonl").read_text(encoding="utf-8").splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
