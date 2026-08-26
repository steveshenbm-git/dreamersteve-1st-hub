import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = (
    REPOSITORY_ROOT
    / "plugins/industry-application-map-builder/skills/industry-application-map-builder"
)
LOCK = SKILL_ROOT / "scripts/lock_semantic_case_preparation_contract.py"
FINALIZE = SKILL_ROOT / "scripts/finalize_semantic_research_contract.py"
FREEZE_PACKAGE = SKILL_ROOT / "scripts/freeze_content_first_case_package.py"
PLUGIN_MANIFEST = (
    REPOSITORY_ROOT / "plugins/industry-application-map-builder/.codex-plugin/plugin.json"
)
CONTRACT_TEMPLATE = (
    SKILL_ROOT / "assets/content-first/content-first-research-contract.template.json"
)
CONTENT_FIRST_REFERENCE = SKILL_ROOT / "references/content-first-mode-contract.md"
PRESSURE_REFERENCE = SKILL_ROOT / "references/pressure-scenarios.md"
SKILL_INSTRUCTIONS = SKILL_ROOT / "SKILL.md"

_fixture_spec = importlib.util.spec_from_file_location(
    "r4_existing_fixture",
    Path(__file__).with_name("test_generalized_semantic_retrieval_r4.py"),
)
assert _fixture_spec is not None and _fixture_spec.loader is not None
fixture = importlib.util.module_from_spec(_fixture_spec)
_fixture_spec.loader.exec_module(fixture)

_contract_spec = importlib.util.spec_from_file_location(
    "r4_case_package_contract",
    SKILL_ROOT / "scripts/r4_case_package_contract.py",
)
assert _contract_spec is not None and _contract_spec.loader is not None
contract_helpers = importlib.util.module_from_spec(_contract_spec)
_contract_spec.loader.exec_module(contract_helpers)

sys.path.insert(0, str(SKILL_ROOT / "scripts"))
_package_spec = importlib.util.spec_from_file_location(
    "freeze_content_first_case_package",
    FREEZE_PACKAGE,
)
assert _package_spec is not None and _package_spec.loader is not None
package_helpers = importlib.util.module_from_spec(_package_spec)
_package_spec.loader.exec_module(package_helpers)


class R4Beta4CasePackageTests(unittest.TestCase):
    def setUp(self):
        self.fx = fixture.GeneralizedSemanticRetrievalR4Tests(methodName="runTest")

    def _prepare(self, root: Path):
        draft, term_pack = self.fx.r4_preparation(root)
        payload = json.loads(draft.read_text(encoding="utf-8"))
        payload["semantic_research_contract"]["map_builder_plugin_version"] = (
            "0.4.0-beta.4"
        )
        payload["semantic_research_contract"].update(
            {
                "created_at": "2026-08-24T00:00:00Z",
                "owner_authorization_reference": "USER-R4-PREP",
                "skill_git_commit": "dbd67b0cc283c4d88d9b78b3d49fa6f5aeb2f02a",
                "workflow_director_plugin_version": "0.3.0-beta.2",
            }
        )
        draft.write_text(json.dumps(payload), encoding="utf-8")
        return draft, term_pack

    def _lock(self, root: Path):
        draft, term_pack = self._prepare(root)
        locked = root / "locked.json"
        result = self.fx.lock_r4(draft, term_pack, locked)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return draft, term_pack, locked

    def _rerun_local_finalizer(
        self,
        root: Path,
        locked: Path,
        output: Path,
        *,
        final_version="2.1.0-content-first.final.1",
        frozen_at="2026-08-25T00:00:03Z",
    ):
        preparation = root / "preparation"
        receipt = preparation / "02-校准案例/visible-case-freeze-receipt.json"
        return fixture.run(
            FINALIZE,
            "--preparation-contract",
            str(locked),
            "--case-set",
            str(preparation / "02-校准案例/formal-case-set.jsonl"),
            "--case-set-reference",
            "02-校准案例/formal-case-set.jsonl",
            "--visible-case-set",
            str(preparation / "02-校准案例/visible-case-set.jsonl"),
            "--visible-case-set-reference",
            "02-校准案例/visible-case-set.jsonl",
            "--visible-case-freeze-receipt",
            str(receipt),
            "--visible-case-freeze-receipt-reference",
            "02-校准案例/visible-case-freeze-receipt.json",
            "--expected-visible-case-freeze-receipt-sha256",
            fixture.sha256_file(receipt),
            "--source-truth-package",
            str(preparation / "03-来源真值/source-truth.jsonl"),
            "--source-truth-reference",
            "03-来源真值/source-truth.jsonl",
            "--final-contract-version",
            final_version,
            "--batch-size",
            "10",
            "--control-case-id",
            "R4-CASE-001",
            "--control-case-id",
            "R4-CASE-002",
            "--frozen-at",
            frozen_at,
            "--contract-local-root",
            str(preparation),
            "--output",
            str(output),
        )

    def _stage_valid_local_inputs(self, root: Path):
        _, _, locked = self._lock(root)
        rows = self.fx.bound_r4_case_rows(locked)
        case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
        fixture.write_jsonl(case_set, rows)
        fixture.write_jsonl(truth, fixture.r4_truth_rows(rows))
        seeded = self.fx.finalize_r4(
            locked, case_set, truth, root / "seed-final.json"
        )
        self.assertEqual(seeded.returncode, 0, seeded.stderr + seeded.stdout)
        return locked, root / "preparation"

    def _freeze_package(
        self,
        root: Path,
        locked: Path,
        preparation: Path,
        output: Path,
        *,
        fail=False,
        contract_root: Path | None = None,
        collide_before_publish=False,
        case_set_override: Path | str | None = None,
    ):
        receipt = preparation / "02-校准案例/visible-case-freeze-receipt.json"
        arguments = [
            "--preparation-contract", str(locked),
            "--contract-local-root", str(
                contract_root if contract_root is not None else preparation.resolve()
            ),
            "--case-set", str(
                case_set_override
                if case_set_override is not None
                else (preparation / "02-校准案例/formal-case-set.jsonl").resolve()
            ),
            "--case-set-reference", "02-校准案例/formal-case-set.jsonl",
            "--visible-case-set", str((preparation / "02-校准案例/visible-case-set.jsonl").resolve()),
            "--visible-case-set-reference", "02-校准案例/visible-case-set.jsonl",
            "--visible-case-freeze-receipt", str(receipt.resolve()),
            "--visible-case-freeze-receipt-reference", "02-校准案例/visible-case-freeze-receipt.json",
            "--expected-visible-case-freeze-receipt-sha256", fixture.sha256_file(receipt),
            "--source-truth-package", str((preparation / "03-来源真值/source-truth.jsonl").resolve()),
            "--source-truth-reference", "03-来源真值/source-truth.jsonl",
            "--final-contract-version", "2.1.0-content-first.final.1",
            "--batch-size", "10",
            "--control-case-id", "R4-CASE-001",
            "--control-case-id", "R4-CASE-002",
            "--frozen-at", "2026-08-25T00:00:03Z",
            "--package-authorization-reference", "USER-R4-CASE-PACKAGE-FREEZE",
            "--output", str(output),
        ]
        if fail:
            arguments.extend(["--test-fail-after-phase", "final-contract"])
        if collide_before_publish:
            arguments.append("--test-create-output-before-publish")
        return fixture.run(FREEZE_PACKAGE, *arguments)

    def test_beta4_surface_and_contract_marker_are_current(self):
        manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        template = json.loads(CONTRACT_TEMPLATE.read_text(encoding="utf-8"))[
            "semantic_research_contract"
        ]

        self.assertEqual(manifest["version"], "0.4.0-beta.4")
        self.assertEqual(template["map_builder_plugin_version"], "0.4.0-beta.4")
        self.assertEqual(template["case_package_contract_version"], "1.0-beta4")
        for field in (
            "created_at",
            "owner_authorization_reference",
            "skill_git_commit",
            "workflow_director_plugin_version",
        ):
            self.assertIn(field, template)
            self.assertIsNone(template[field])
        content_contract = CONTENT_FIRST_REFERENCE.read_text(encoding="utf-8")
        pressure = PRESSURE_REFERENCE.read_text(encoding="utf-8")
        skill_instructions = SKILL_INSTRUCTIONS.read_text(encoding="utf-8")
        for required in (
            "locked_at < captured_at <= frozen_at",
            "canonical_json_node_projection_v1",
            "output_or_subprocess_basis = receiver_captured_raw",
            "mechanism_or_use_point_basis = receiver_captured_raw",
            "复制前和复制后",
            "父目录锁",
            "workflow_director_plugin_version = 0.3.0-beta.2",
            "skill_git_commit",
            "owner_authorization_reference",
        ):
            self.assertIn(required, content_contract)
        self.assertIn("--expected-skill-git-commit", skill_instructions)
        self.assertIn("递归检查", content_contract)
        self.assertIn("单个 HTTP(S) URL", content_contract)
        for scenario_id in (
            "R4-P85",
            "R4-P86",
            "R4-P87",
            "R4-P88",
            "R4-P89",
            "R4-P90",
        ):
            self.assertIn(scenario_id, pressure)

    def test_lock_requires_content_first_creation_and_implementation_identity(self):
        for field, value, expected in (
            ("created_at", None, "CONTRACT_CREATED_AT_INVALID"),
            ("created_at", "2026-08-25T00:00:00Z", "CONTRACT_CREATED_AT_INVALID"),
            ("owner_authorization_reference", None, "OWNER_AUTHORIZATION_REFERENCE_INVALID"),
            ("skill_git_commit", None, "SKILL_GIT_COMMIT_INVALID"),
            ("skill_git_commit", "not-a-git-sha", "SKILL_GIT_COMMIT_INVALID"),
            ("skill_git_commit", "0" * 40, "SKILL_GIT_COMMIT_MISMATCH"),
            ("workflow_director_plugin_version", None, "WORKFLOW_DIRECTOR_PLUGIN_VERSION_INVALID"),
        ):
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                draft, term_pack = self._prepare(root)
                payload = json.loads(draft.read_text(encoding="utf-8"))
                payload["semantic_research_contract"][field] = value
                draft.write_text(json.dumps(payload), encoding="utf-8")

                result = self.fx.lock_r4(draft, term_pack, root / "locked.json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_lock_requires_exact_beta4_identity_and_timezone_aware_lock_time(self):
        for mutation, expected in (
            ("missing_version", "MAP_BUILDER_PLUGIN_VERSION_INVALID"),
            ("bad_time", "LOCKED_AT_INVALID"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                draft, term_pack = self._prepare(root)
                payload = json.loads(draft.read_text(encoding="utf-8"))
                if mutation == "missing_version":
                    payload["semantic_research_contract"].pop(
                        "map_builder_plugin_version", None
                    )
                    draft.write_text(json.dumps(payload), encoding="utf-8")
                    result = self.fx.lock_r4(draft, term_pack, root / "locked.json")
                else:
                    result = fixture.run(
                        LOCK,
                        "--contract",
                        str(draft),
                        "--terminology-bridge",
                        str(term_pack),
                        "--terminology-bridge-reference",
                        "01-术语桥/terminology-bridge.jsonl",
                        "--r3-source-manifest",
                        str(
                            root
                            / "preparation/02-校准案例候选/r3-source-manifest.json"
                        ),
                        "--r3-source-manifest-reference",
                        "02-校准案例候选/r3-source-manifest.json",
                        "--authorization-reference",
                        "USER-R4-PREP",
                        "--expected-skill-git-commit",
                        "dbd67b0cc283c4d88d9b78b3d49fa6f5aeb2f02a",
                        "--locked-at",
                        "not-a-time",
                        "--output",
                        str(root / "locked.json"),
                    )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_real_gbt_taxonomy_identifiers_are_accepted_but_path_forms_are_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self._prepare(root)
            preparation = root / "preparation"
            taxonomy = preparation / "01-节点快照/taxonomy.json"
            taxonomy_payload = json.loads(taxonomy.read_text(encoding="utf-8"))
            for index, node in enumerate(taxonomy_payload["terminal_nodes"], 1):
                node["taxonomy_node_id"] = f"GB/T-4754-2017/{index:04d}"
            taxonomy.write_text(
                json.dumps(taxonomy_payload, sort_keys=True) + "\n", encoding="utf-8"
            )
            contract_payload = json.loads(draft.read_text(encoding="utf-8"))
            contract_payload["semantic_research_contract"]["taxonomy_snapshot_sha256"] = (
                fixture.sha256_file(taxonomy)
            )
            draft.write_text(json.dumps(contract_payload), encoding="utf-8")
            locked = root / "locked.json"
            self.assertEqual(
                self.fx.lock_r4(draft, term_pack, locked).returncode, 0
            )
            rows = fixture.r4_case_rows()
            for index, row in enumerate(rows[1:], 1):
                row["taxonomy_node"]["taxonomy_node_id"] = (
                    f"GB/T-4754-2017/{index:04d}"
                )
            rows = fixture.materialize_r4_case_provenance(
                locked, rows, preparation
            )
            case_set = root / "cases.jsonl"
            truth = root / "truth.jsonl"
            fixture.write_jsonl(case_set, rows)
            fixture.write_jsonl(truth, fixture.r4_truth_rows(rows))

            accepted = self.fx.finalize_r4(
                locked, case_set, truth, root / "final.json"
            )

            self.assertEqual(accepted.returncode, 0, accepted.stderr + accepted.stdout)

        for invalid in (
            "/GB/T-4754-2017/0001",
            "GB/T-4754-2017/0001/",
            "GB/T-4754-2017//0001",
            "GB/T-4754-2017/../0001",
            "GB\\T-4754-2017/0001",
            "GB/T-4754-2017/ 0001",
            "ＧＢ/T-4754-2017/0001",
        ):
            with self.subTest(invalid=invalid):
                self.assertIsNone(contract_helpers.taxonomy_identifier_key(invalid))

    def test_real_1382_node_snapshot_integrates_with_formal_case_finalization(self):
        snapshot_source = os.environ.get("R4_REAL_TAXONOMY_SNAPSHOT")
        if not snapshot_source:
            self.skipTest("R4_REAL_TAXONOMY_SNAPSHOT not supplied")
        source = Path(snapshot_source)
        payload = json.loads(source.read_text(encoding="utf-8"))
        nodes = payload["terminal_nodes"]
        keys = [
            contract_helpers.taxonomy_identifier_key(node["taxonomy_node_id"])
            for node in nodes
        ]
        self.assertEqual(payload["terminal_node_count"], 1382)
        self.assertEqual(len(nodes), 1382)
        self.assertTrue(all(key is not None for key in keys))
        self.assertEqual(len(set(keys)), 1382)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self._prepare(root)
            preparation = root / "preparation"
            taxonomy = preparation / "01-节点快照/taxonomy.json"
            taxonomy.write_bytes(source.read_bytes())
            contract_payload = json.loads(draft.read_text(encoding="utf-8"))
            contract = contract_payload["semantic_research_contract"]
            contract["taxonomy_snapshot_sha256"] = fixture.sha256_file(taxonomy)
            contract["terminal_node_count"] = 1382
            draft.write_text(json.dumps(contract_payload), encoding="utf-8")
            locked = root / "locked.json"
            locked_result = self.fx.lock_r4(draft, term_pack, locked)
            self.assertEqual(
                locked_result.returncode,
                0,
                locked_result.stderr + locked_result.stdout,
            )
            rows = fixture.r4_case_rows()
            for row, official in zip(rows[1:], nodes[:40]):
                row["taxonomy_node"].update(
                    {
                        "taxonomy_node_id": official["taxonomy_node_id"],
                        "code": official["code"],
                        "level": contract_helpers.taxonomy_level_number(
                            official.get("level")
                        ),
                        "name_zh": official["name_zh"],
                    }
                )
            rows = fixture.materialize_r4_case_provenance(
                locked, rows, preparation
            )
            case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
            fixture.write_jsonl(case_set, rows)
            fixture.write_jsonl(truth, fixture.r4_truth_rows(rows))

            result = self.fx.finalize_r4(
                locked, case_set, truth, root / "final.json"
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_finalizer_requires_actual_inputs_at_the_declared_contract_local_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, locked = self._lock(root)
            rows = self.fx.bound_r4_case_rows(locked)
            outside_case_set = root / "outside-cases.jsonl"
            outside_truth = root / "outside-truth.jsonl"
            fixture.write_jsonl(outside_case_set, rows)
            fixture.write_jsonl(outside_truth, fixture.r4_truth_rows(rows))

            result = self.fx.finalize_r4(
                locked,
                outside_case_set,
                outside_truth,
                root / "final.json",
                bind_declared_inputs=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("DECLARED_INPUT_PATH_MISMATCH", result.stderr)
            self.assertFalse((root / "final.json").exists())

    def test_finalizer_requires_exact_prep_to_final_version_and_time_order(self):
        for mutation, expected in (
            ("wrong_version", "FINAL_CONTRACT_VERSION_INVALID"),
            ("equal_time", "FROZEN_AT_INVALID"),
            ("bad_time", "FROZEN_AT_INVALID"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                locked, _ = self._stage_valid_local_inputs(root)
                result = self._rerun_local_finalizer(
                    root,
                    locked,
                    root / f"{mutation}.json",
                    final_version=(
                        "9.9.9-content-first.final.1"
                        if mutation == "wrong_version"
                        else "2.1.0-content-first.final.1"
                    ),
                    frozen_at=(
                        "2026-08-25T00:00:00Z"
                        if mutation == "equal_time"
                        else "not-a-time"
                        if mutation == "bad_time"
                        else "2026-08-25T00:00:03Z"
                    ),
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_all_forty_cases_bind_exact_current_official_terminal_nodes(self):
        for mutation, expected in (
            ("retained_unknown_node", "FORMAL_CASE_OFFICIAL_NODE_INVALID"),
            ("official_source_hash", "FORMAL_CASE_OFFICIAL_SOURCE_INVALID"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                _, _, locked = self._lock(root)
                rows = self.fx.bound_r4_case_rows(locked)
                retained = next(
                    row
                    for row in rows
                    if row.get("record_type") == "calibration_case"
                    and row["provenance"]["selection_origin"]
                    == "retained_r3_unexecuted"
                )
                if mutation == "retained_unknown_node":
                    retained["taxonomy_node"]["taxonomy_node_id"] = "GB/T-UNKNOWN/9999"
                else:
                    retained["taxonomy_node"]["official_source_sha256"] = "cd" * 32
                case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
                fixture.write_jsonl(case_set, rows)
                fixture.write_jsonl(truth, fixture.r4_truth_rows(rows))

                result = self.fx.finalize_r4(
                    locked, case_set, truth, root / "final.json"
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_summary_only_truth_source_cannot_satisfy_a_raw_capture_basis(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, locked = self._lock(root)
            rows = self.fx.bound_r4_case_rows(locked)
            case_set = root / "cases.jsonl"
            truth = root / "truth.jsonl"
            fixture.write_jsonl(case_set, rows)
            truth_rows = fixture.r4_truth_rows(rows)
            for row in truth_rows:
                row["truth_contract_version"] = "2.0-r4-complete"
                row["research_contract_id"] = "RC2-TEST-001"
                row["conditions"] = []
                row["limitations"] = []
                row["unknowns"] = []
                row["exclusion_boundary"] = "product-neutral boundary"
                row["evidence_bases"] = {
                    role: {
                        "source_kind": "derived_summary",
                        "source_reference": f"03-来源真值/summaries/{row['case_id']}-{role}.json",
                        "source_sha256": hashlib.sha256(
                            f"summary-{row['case_id']}-{role}".encode()
                        ).hexdigest(),
                        "capture_receipt_reference": f"03-来源真值/receipts/{row['case_id']}-{role}.json",
                        "capture_receipt_sha256": "ab" * 32,
                        "original_location": "summary://not-raw",
                        "claim": "summary only",
                        "upstream_snapshot_reference": None,
                        "upstream_snapshot_sha256": None,
                        "upstream_node_id": None,
                        "upstream_json_pointer": None,
                        "projection_algorithm": None,
                        "projection_sha256": None,
                    }
                    for role in (
                        "taxonomy_membership_basis",
                        "output_or_subprocess_basis",
                        "mechanism_or_use_point_basis",
                    )
                }
                row["truth_sha256"] = None
                row["truth_sha256"] = fixture.canonical_json_sha256(row)
            fixture.write_jsonl(truth, truth_rows)

            result = self.fx.finalize_r4(
                locked, case_set, truth, root / "final.json"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RAW_SOURCE_CAPTURE_REQUIRED", result.stderr)

    def test_truth_roles_and_official_projection_binding_are_enforced(self):
        for mutation, expected in (
            ("raw_roles_masquerade", "RAW_SOURCE_CAPTURE_REQUIRED"),
            ("projection_without_upstream_binding", "OFFICIAL_TAXONOMY_PROJECTION_BINDING_INVALID"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                _, _, locked = self._lock(root)
                rows = self.fx.bound_r4_case_rows(locked)
                case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
                fixture.write_jsonl(case_set, rows)
                truth_rows = fixture.r4_truth_rows(rows)
                first = truth_rows[0]
                roles = (
                    ("output_or_subprocess_basis", "mechanism_or_use_point_basis")
                    if mutation == "raw_roles_masquerade"
                    else ("taxonomy_membership_basis",)
                )
                for role in roles:
                    first["evidence_bases"][role]["source_kind"] = (
                        "official_taxonomy_projection"
                    )
                fixture.write_jsonl(truth, truth_rows)

                result = self.fx.finalize_r4(
                    locked, case_set, truth, root / "final.json"
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_official_projection_is_recomputed_from_the_bound_taxonomy_node(self):
        for mutation, accepted in (("valid", True), ("forged_projection", False)):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                locked, preparation = self._stage_valid_local_inputs(root)
                truth_path = preparation / "03-来源真值/source-truth.jsonl"
                truth_rows = fixture.load_jsonl(truth_path)
                case_rows = fixture.load_jsonl(
                    preparation / "02-校准案例/formal-case-set.jsonl"
                )
                first = truth_rows[0]
                case = next(row for row in case_rows if row.get("case_id") == first["case_id"])
                basis = first["evidence_bases"]["taxonomy_membership_basis"]
                contract = json.loads(locked.read_text(encoding="utf-8"))[
                    "semantic_research_contract"
                ]
                taxonomy_reference = contract["taxonomy_snapshot_reference"]
                pointer = case["taxonomy_node"]["official_source_reference"].split("#", 1)[1]
                index = int(pointer.rsplit("/", 1)[1])
                taxonomy = json.loads(
                    (preparation / taxonomy_reference).read_text(encoding="utf-8")
                )
                node = taxonomy["terminal_nodes"][index]
                projection = contract_helpers.canonical_bytes(node)
                if mutation == "forged_projection":
                    projection = b'{"forged":true}\n'
                raw_path = preparation / basis["source_reference"]
                raw_path.write_bytes(projection)
                projection_sha = fixture.sha256_file(raw_path)
                official_location = f"{taxonomy_reference}#{pointer}"
                basis.update(
                    {
                        "source_kind": "official_taxonomy_projection",
                        "source_sha256": projection_sha,
                        "original_location": official_location,
                        "upstream_snapshot_reference": taxonomy_reference,
                        "upstream_snapshot_sha256": contract["taxonomy_snapshot_sha256"],
                        "upstream_node_id": case["taxonomy_node"]["taxonomy_node_id"],
                        "upstream_json_pointer": f"#{pointer}",
                        "projection_algorithm": "canonical_json_node_projection_v1",
                        "projection_sha256": projection_sha,
                    }
                )
                receipt_path = preparation / basis["capture_receipt_reference"]
                receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt = receipt_payload["source_capture_receipt"]
                receipt.update(
                    {
                        "capture_method": "official_taxonomy_projection_v1",
                        "upstream_response_reference": official_location,
                        "upstream_response_sha256": contract["taxonomy_snapshot_sha256"],
                        "source_sha256": projection_sha,
                        "content_type": "application/json",
                        "byte_length": len(projection),
                        "final_url": official_location,
                    }
                )
                receipt_path.write_bytes(contract_helpers.canonical_bytes(receipt_payload))
                basis["capture_receipt_sha256"] = fixture.sha256_file(receipt_path)
                first["truth_sha256"] = None
                first["truth_sha256"] = fixture.canonical_json_sha256(first)
                fixture.write_jsonl(truth_path, truth_rows)

                result = self._rerun_local_finalizer(
                    root, locked, root / f"{mutation}.json"
                )

                if accepted:
                    self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        "OFFICIAL_TAXONOMY_PROJECTION_BINDING_INVALID",
                        result.stderr,
                    )

    def test_receiver_owned_receipt_time_order_and_summary_rejection(self):
        for mutation, expected in (
            ("wrong_owner", "TRUTH_SOURCE_RECEIPT_INVALID"),
            ("before_lock", "TRUTH_SOURCE_RECEIPT_TIME_INVALID"),
            ("after_freeze", "TRUTH_SOURCE_RECEIPT_TIME_INVALID"),
            ("summary_json", "DERIVED_SUMMARY_CANNOT_BE_RAW_SOURCE"),
            ("summary_extra", "DERIVED_SUMMARY_CANNOT_BE_RAW_SOURCE"),
            ("summary_mislabeled", "DERIVED_SUMMARY_CANNOT_BE_RAW_SOURCE"),
            ("summary_nested", "DERIVED_SUMMARY_CANNOT_BE_RAW_SOURCE"),
            ("summary_array", "DERIVED_SUMMARY_CANNOT_BE_RAW_SOURCE"),
            ("summary_nfkc_nested", "DERIVED_SUMMARY_CANNOT_BE_RAW_SOURCE"),
            ("summary_nfkc_array", "DERIVED_SUMMARY_CANNOT_BE_RAW_SOURCE"),
            ("plain_url", "SELF_REPORTED_URL_CANNOT_BE_RAW_SOURCE"),
            ("json_url", "SELF_REPORTED_URL_CANNOT_BE_RAW_SOURCE"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                locked, preparation = self._stage_valid_local_inputs(root)
                truth_path = preparation / "03-来源真值/source-truth.jsonl"
                truth_rows = fixture.load_jsonl(truth_path)
                first = truth_rows[0]
                basis = first["evidence_bases"]["output_or_subprocess_basis"]
                raw_path = preparation / basis["source_reference"]
                receipt_path = preparation / basis["capture_receipt_reference"]
                receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt = receipt_payload["source_capture_receipt"]
                if mutation == "wrong_owner":
                    receipt["receiver_owner"] = "truth_author"
                elif mutation == "before_lock":
                    receipt["captured_at"] = "1999-01-01T00:00:00Z"
                elif mutation == "after_freeze":
                    receipt["captured_at"] = "2027-01-01T00:00:00Z"
                else:
                    if mutation == "summary_nested":
                        body = {"data": {"summary": "derived conclusion only"}}
                    elif mutation == "summary_array":
                        body = [{"summary": "derived conclusion only"}]
                    elif mutation == "summary_nfkc_nested":
                        body = {"data": {"ｓｕｍｍａｒｙ": "derived conclusion only"}}
                    elif mutation == "summary_nfkc_array":
                        body = [{"ｓｏｕｒｃｅ＿ｓｕｍｍａｒｙ": "derived conclusion only"}]
                    elif mutation == "plain_url":
                        body = None
                        raw_path.write_text(
                            "https://example.invalid/self-reported\n",
                            encoding="utf-8",
                        )
                    elif mutation == "json_url":
                        body = "https://example.invalid/self-reported"
                    else:
                        body = {"summary": "derived conclusion only"}
                        if mutation == "summary_extra":
                            body["publisher"] = "fake"
                    if body is not None:
                        raw_path.write_bytes(contract_helpers.canonical_bytes(body))
                    raw_sha = fixture.sha256_file(raw_path)
                    basis["source_sha256"] = raw_sha
                    receipt["source_sha256"] = raw_sha
                    receipt["upstream_response_sha256"] = raw_sha
                    receipt["content_type"] = (
                        "text/plain"
                        if mutation in {"summary_mislabeled", "plain_url"}
                        else "application/json"
                    )
                    receipt["byte_length"] = len(raw_path.read_bytes())
                receipt_path.write_bytes(contract_helpers.canonical_bytes(receipt_payload))
                basis["capture_receipt_sha256"] = fixture.sha256_file(receipt_path)
                first["truth_sha256"] = None
                first["truth_sha256"] = fixture.canonical_json_sha256(first)
                fixture.write_jsonl(truth_path, truth_rows)

                result = self._rerun_local_finalizer(
                    root, locked, root / f"{mutation}.json"
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_truth_self_hash_and_raw_source_bytes_are_rechecked(self):
        for mutation, expected in (
            ("truth_self_hash", "SOURCE_TRUTH_SELF_HASH_MISMATCH"),
            ("missing_raw", "TRUTH_SOURCE_MISSING"),
            ("symlink_raw", "TRUTH_SOURCE_REFERENCE_INVALID"),
            ("receipt_byte_length", "TRUTH_SOURCE_RECEIPT_INVALID"),
            ("receipt_final_url", "TRUTH_SOURCE_RECEIPT_INVALID"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                _, _, locked = self._lock(root)
                rows = self.fx.bound_r4_case_rows(locked)
                case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
                fixture.write_jsonl(case_set, rows)
                fixture.write_jsonl(truth, fixture.r4_truth_rows(rows))
                seeded = self.fx.finalize_r4(
                    locked, case_set, truth, root / "seed-final.json"
                )
                self.assertEqual(seeded.returncode, 0, seeded.stderr + seeded.stdout)
                preparation = root / "preparation"
                local_truth = preparation / "03-来源真值/source-truth.jsonl"
                truth_rows = fixture.load_jsonl(local_truth)
                first = truth_rows[0]
                basis = first["evidence_bases"]["output_or_subprocess_basis"]
                raw = preparation / basis["source_reference"]
                if mutation == "truth_self_hash":
                    first["conditions"] = ["changed after freeze"]
                    fixture.write_jsonl(local_truth, truth_rows)
                elif mutation == "missing_raw":
                    raw.unlink()
                elif mutation == "symlink_raw":
                    other = preparation / truth_rows[1]["evidence_bases"][
                        "output_or_subprocess_basis"
                    ]["source_reference"]
                    raw.unlink()
                    raw.symlink_to(other)
                else:
                    receipt_path = preparation / basis[
                        "capture_receipt_reference"
                    ]
                    receipt_payload = json.loads(
                        receipt_path.read_text(encoding="utf-8")
                    )
                    receipt = receipt_payload["source_capture_receipt"]
                    if mutation == "receipt_byte_length":
                        receipt["byte_length"] += 1
                    else:
                        receipt["final_url"] = "https://wrong.invalid/source"
                    receipt_path.write_bytes(
                        (
                            json.dumps(
                                receipt_payload,
                                ensure_ascii=False,
                                sort_keys=True,
                                separators=(",", ":"),
                            )
                            + "\n"
                        ).encode()
                    )
                    basis["capture_receipt_sha256"] = fixture.sha256_file(
                        receipt_path
                    )
                    first["truth_sha256"] = None
                    first["truth_sha256"] = fixture.canonical_json_sha256(first)
                    fixture.write_jsonl(local_truth, truth_rows)

                result = self._rerun_local_finalizer(
                    root, locked, root / f"{mutation}.json"
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_lock_publication_failure_is_atomic_and_retryable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self._prepare(root)
            output = root / "locked.json"
            manifest = root / "preparation/02-校准案例候选/r3-source-manifest.json"
            failed = fixture.run(
                LOCK,
                "--contract",
                str(draft),
                "--terminology-bridge",
                str(term_pack),
                "--terminology-bridge-reference",
                "01-术语桥/terminology-bridge.jsonl",
                "--r3-source-manifest",
                str(manifest),
                "--r3-source-manifest-reference",
                "02-校准案例候选/r3-source-manifest.json",
                "--authorization-reference",
                "USER-R4-PREP",
                "--expected-skill-git-commit",
                "dbd67b0cc283c4d88d9b78b3d49fa6f5aeb2f02a",
                "--locked-at",
                "2026-08-25T00:00:00Z",
                "--test-fail-after-temp-write",
                "--output",
                str(output),
            )

            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("LOCK_PUBLISH_FAILED", failed.stderr)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.glob(".locked.json.tmp-*")), [])
            retry = self.fx.lock_r4(draft, term_pack, output)
            self.assertEqual(retry.returncode, 0, retry.stderr + retry.stdout)

    def test_case_package_is_closed_set_atomic_create_only_and_retryable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            locked, preparation = self._stage_valid_local_inputs(root)
            output = root / "R4-CASE-PACKAGE"

            failed = self._freeze_package(
                root, locked, preparation, output, fail=True
            )

            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("CASE_PACKAGE_BUILD_FAILED", failed.stderr)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.glob(".R4-CASE-PACKAGE.tmp-*")), [])

            created = self._freeze_package(root, locked, preparation, output)
            self.assertEqual(created.returncode, 0, created.stderr + created.stdout)
            manifest_path = output / "case-package-manifest.json"
            receipt_path = output / "case-package-freeze-receipt.json"
            final_contract = output / "00-合同/final-contract.json"
            self.assertTrue(manifest_path.is_file())
            self.assertTrue(receipt_path.is_file())
            self.assertTrue(final_contract.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))[
                "content_first_case_package_manifest"
            ]
            self.assertEqual(manifest["formal_case_count"], 40)
            self.assertEqual(manifest["known_positive_count"], 14)
            self.assertEqual(
                manifest["selection_origin_counts"],
                {"retained_r3_unexecuted": 30, "new_unseen_positive": 10},
            )
            self.assertEqual(manifest["control_case_ids"], ["R4-CASE-001", "R4-CASE-002"])
            self.assertFalse(manifest["model_execution_authorized"])
            self.assertFalse(manifest["full_screening_authorized"])
            self.assertGreater(len(manifest["artifacts"]), 250)

            verify = fixture.run(
                FREEZE_PACKAGE,
                "--verify-package",
                str(output),
                "--expected-manifest-sha256",
                fixture.sha256_file(manifest_path),
            )
            self.assertEqual(verify.returncode, 0, verify.stderr + verify.stdout)
            duplicate = self._freeze_package(root, locked, preparation, output)
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn("OUTPUT_EXISTS", duplicate.stderr)

            reserved_root = output / "unregistered"
            reserved_root.mkdir()
            for reserved_name in (
                "case-package-manifest.json",
                "case-package-freeze-receipt.json",
            ):
                hidden = reserved_root / reserved_name
                hidden.write_text("{}\n", encoding="utf-8")
                hidden_result = fixture.run(
                    FREEZE_PACKAGE,
                    "--verify-package",
                    str(output),
                    "--expected-manifest-sha256",
                    fixture.sha256_file(manifest_path),
                )
                self.assertNotEqual(hidden_result.returncode, 0)
                self.assertIn("CASE_PACKAGE_CLOSED_SET_INVALID", hidden_result.stderr)
                hidden.unlink()
            reserved_root.rmdir()

            (output / "unregistered.json").write_text("{}\n", encoding="utf-8")
            extra = fixture.run(
                FREEZE_PACKAGE,
                "--verify-package",
                str(output),
                "--expected-manifest-sha256",
                fixture.sha256_file(manifest_path),
            )
            self.assertNotEqual(extra.returncode, 0)
            self.assertIn("CASE_PACKAGE_CLOSED_SET_INVALID", extra.stderr)
            (output / "unregistered.json").unlink()

            alias = root / "R4-CASE-PACKAGE-ALIAS"
            alias.symlink_to(output, target_is_directory=True)
            alias_result = fixture.run(
                FREEZE_PACKAGE,
                "--verify-package",
                str(alias),
                "--expected-manifest-sha256",
                fixture.sha256_file(manifest_path),
            )
            self.assertNotEqual(alias_result.returncode, 0)
            self.assertIn("CASE_PACKAGE_INVALID", alias_result.stderr)

            for meta_name in (
                "case-package-manifest.json",
                "case-package-freeze-receipt.json",
            ):
                meta_path = output / meta_name
                original = meta_path.read_bytes()
                outside = root / f"outside-{meta_name}"
                outside.write_bytes(original)
                meta_path.unlink()
                os.link(outside, meta_path)
                hardlink_result = fixture.run(
                    FREEZE_PACKAGE,
                    "--verify-package",
                    str(output),
                    "--expected-manifest-sha256",
                    fixture.sha256_file(manifest_path),
                )
                self.assertNotEqual(hardlink_result.returncode, 0)
                self.assertIn("CASE_PACKAGE_HARDLINK_FORBIDDEN", hardlink_result.stderr)
                meta_path.unlink()
                meta_path.write_bytes(original)

    def test_case_package_inventory_rejects_hardlink_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "03-来源真值/raw/a.txt"
            alias = root / "00-合同准备/alias.txt"
            first.parent.mkdir(parents=True)
            alias.parent.mkdir(parents=True)
            first.write_text("one physical file\n", encoding="utf-8")
            os.link(first, alias)

            with self.assertRaisesRegex(
                ValueError, "CASE_PACKAGE_HARDLINK_FORBIDDEN"
            ):
                package_helpers.package_artifacts(root)

    def test_case_package_audits_source_before_copy_and_never_replaces_collision(self):
        for mutation, expected in (
            ("root_symlink", "CONTRACT_LOCAL_ROOT_INVALID"),
            ("parent_symlink", "CONTRACT_LOCAL_ROOT_INVALID"),
            ("source_dotdot", "CONTRACT_LOCAL_ROOT_INVALID"),
            ("source_duplicate_separator", "CONTRACT_LOCAL_ROOT_INVALID"),
            ("actual_input_symlink", "DECLARED_INPUT_PATH_MISMATCH"),
            ("source_hardlink", "CASE_PACKAGE_HARDLINK_FORBIDDEN"),
            ("source_same_hash", "CASE_PACKAGE_DUPLICATE_CONTENT_FORBIDDEN"),
            ("publish_collision", "OUTPUT_EXISTS"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                locked, preparation = self._stage_valid_local_inputs(root)
                output = root / "R4-CASE-PACKAGE"
                contract_root = None
                collide = False
                case_set_override = None
                if mutation == "root_symlink":
                    contract_root = root / "preparation-alias"
                    contract_root.symlink_to(preparation, target_is_directory=True)
                elif mutation == "parent_symlink":
                    alias_parent = root / "parent-alias"
                    alias_parent.symlink_to(root, target_is_directory=True)
                    contract_root = alias_parent / "preparation"
                elif mutation == "source_dotdot":
                    (root / "spare").mkdir()
                    contract_root = root / "spare/../preparation"
                elif mutation == "source_duplicate_separator":
                    contract_root = str(preparation.resolve()).replace(
                        "/preparation", "//preparation"
                    )
                elif mutation == "actual_input_symlink":
                    case_set_override = root / "external-case-alias.jsonl"
                    case_set_override.symlink_to(
                        preparation / "02-校准案例/formal-case-set.jsonl"
                    )
                elif mutation in {"source_hardlink", "source_same_hash"}:
                    original = preparation / "00-合同准备/prompt.md"
                    alias = preparation / "00-合同准备/prompt-alias.md"
                    if mutation == "source_hardlink":
                        os.link(original, alias)
                    else:
                        alias.write_bytes(original.read_bytes())
                else:
                    collide = True

                result = self._freeze_package(
                    root,
                    locked,
                    preparation,
                    output,
                    contract_root=contract_root,
                    collide_before_publish=collide,
                    case_set_override=case_set_override,
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)
                if mutation == "publish_collision":
                    self.assertTrue(output.is_dir())
                    self.assertEqual(list(output.iterdir()), [])

    def test_directory_publish_uses_true_no_replace_at_the_final_system_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stage = root / "stage"
            output = root / "published"
            stage.mkdir()
            (stage / "artifact.txt").write_text("frozen\n", encoding="utf-8")
            real_rename = package_helpers.rename_directory_no_replace

            def race_at_final_call(stage_path, output_path):
                output.mkdir()
                return real_rename(stage_path, output_path)

            with mock.patch.object(
                package_helpers,
                "rename_directory_no_replace",
                side_effect=race_at_final_call,
            ):
                error = package_helpers.publish_directory_create_only(stage, output)

            self.assertEqual(error, "OUTPUT_EXISTS")
            self.assertTrue(stage.is_dir())
            self.assertTrue(output.is_dir())
            self.assertEqual(list(output.iterdir()), [])

    def test_package_verifier_recomputes_manifest_facts_and_enforces_closed_schemas(self):
        for mutation in (
            "count",
            "manifest_extra",
            "receipt_extra",
            "receipt_contract",
            "manifest_id",
            "receipt_id",
            "freeze_time",
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                locked, preparation = self._stage_valid_local_inputs(root)
                output = root / "R4-CASE-PACKAGE"
                created = self._freeze_package(root, locked, preparation, output)
                self.assertEqual(created.returncode, 0, created.stderr + created.stdout)
                manifest_path = output / "case-package-manifest.json"
                receipt_path = output / "case-package-freeze-receipt.json"
                manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest = manifest_payload["content_first_case_package_manifest"]
                receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt = receipt_payload["content_first_case_package_freeze_receipt"]
                if mutation == "count":
                    manifest["formal_case_count"] = 39
                elif mutation == "manifest_extra":
                    manifest["self_asserted_pass"] = True
                elif mutation == "receipt_extra":
                    receipt["self_asserted_pass"] = True
                elif mutation == "receipt_contract":
                    receipt["research_contract_id"] = "OTHER-CONTRACT"
                elif mutation == "manifest_id":
                    manifest["manifest_id"] = "OTHER-MANIFEST"
                elif mutation == "receipt_id":
                    receipt["receipt_id"] = "OTHER-RECEIPT"
                else:
                    manifest["frozen_at"] = "2026-08-25T00:00:04Z"
                    receipt["frozen_at"] = "2026-08-25T00:00:04Z"
                manifest_path.write_bytes(contract_helpers.canonical_bytes(manifest_payload))
                receipt["manifest_sha256"] = fixture.sha256_file(manifest_path)
                receipt_path.write_bytes(contract_helpers.canonical_bytes(receipt_payload))

                result = fixture.run(
                    FREEZE_PACKAGE,
                    "--verify-package",
                    str(output),
                    "--expected-manifest-sha256",
                    fixture.sha256_file(manifest_path),
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("CASE_PACKAGE_", result.stderr)


if __name__ == "__main__":
    unittest.main()
