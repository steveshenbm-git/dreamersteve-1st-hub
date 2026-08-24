from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = (
    ROOT
    / "plugins"
    / "industry-application-map-builder"
    / "skills"
    / "industry-application-map-builder"
)
ASSET_ROOT = SKILL_ROOT / "assets" / "semantic-method"
INIT_SCRIPT = SKILL_ROOT / "scripts" / "init_semantic_research_workspace.py"
LOCK_PREPARATION_SCRIPT = (
    SKILL_ROOT / "scripts" / "lock_semantic_case_preparation_contract.py"
)
FINALIZE_CONTRACT_SCRIPT = (
    SKILL_ROOT / "scripts" / "finalize_semantic_research_contract.py"
)
FREEZE_SCRIPT = SKILL_ROOT / "scripts" / "freeze_semantic_taxonomy_snapshot.py"
VALIDATE_SCRIPT = SKILL_ROOT / "scripts" / "validate_semantic_research_workspace.py"
BUILD_HANDOFF_SCRIPT = SKILL_ROOT / "scripts" / "build_semantic_model_handoff.py"
SAMPLE_SCRIPT = SKILL_ROOT / "scripts" / "sample_semantic_reverse_audit.py"
EVALUATE_SCRIPT = SKILL_ROOT / "scripts" / "evaluate_semantic_calibration.py"
TAXONOMY_SNAPSHOT_BYTES = b'{"schema_version":"1.0","terminal_node_count":2}\n'
CALIBRATION_CASE_SET_BYTES = b'{"record_type":"case_set_contract","case_count":40}\n'


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n" for value in values),
        encoding="utf-8",
    )


def canonical_json_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def preparation_lock_sha256(contract: dict) -> str:
    projection = json.loads(json.dumps(contract))
    gate = projection["case_preparation_gate"]
    projection["contract_version"] = gate["preparation_contract_version"]
    projection["contract_state"] = "case_preparation_locked"
    projection["frozen_at"] = None
    projection["calibration_case_set_reference_and_hash"] = {
        "reference": None,
        "sha256": None,
    }
    projection["batch_rule"]["batch_size"] = None
    projection["control_case_rule"]["case_ids"] = []
    gate["locked_input_sha256"] = None
    return canonical_json_sha256(projection)


class SemanticMethodToolTests(unittest.TestCase):
    def frozen_contract(self) -> dict:
        template = ASSET_ROOT / "research-contract.template.json"
        self.assertTrue(template.is_file(), template.name)
        payload = json.loads(template.read_text(encoding="utf-8"))
        contract = payload["semantic_research_contract"]
        contract.update(
            {
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "contract_state": "frozen",
                "created_at": "2026-08-19T00:00:00Z",
                "frozen_at": "2026-08-19T00:00:00Z",
                "owner_authorization_reference": "USER-APPROVAL-001",
                "skill_git_commit": "b0237c5",
                "taxonomy_snapshot_reference": "01-节点快照/taxonomy-snapshot.json",
                "taxonomy_snapshot_sha256": hashlib.sha256(TAXONOMY_SNAPSHOT_BYTES).hexdigest(),
                "terminal_node_count": 2,
                "research_theme": {
                    "theme_id": "THEME-001",
                    "mechanism": "functional surface interaction",
                    "form_or_use_point": "powder added during formulation or finishing",
                    "exclusions": ["standalone liquid-only processing"],
                    "product_neutrality_review": "PASS",
                },
                "prompt_template_references_and_hashes": [
                    {
                        "role": role,
                        "reference": str(ASSET_ROOT / "prompts" / filename),
                        "sha256": hashlib.sha256(
                            (ASSET_ROOT / "prompts" / filename).read_bytes()
                        ).hexdigest(),
                    }
                    for role, filename in (
                        ("baseline", "baseline-full-depth.md"),
                        ("A_screening", "model-a-screening.md"),
                        ("A_evidence", "model-a-evidence-expansion.md"),
                        ("B_review", "model-b-blind-review.md"),
                        ("C_dispute", "model-c-dispute.md"),
                        ("C_reverse_audit", "model-c-reverse-audit.md"),
                    )
                ],
                "search_tool_and_locale": {
                    "tool": "frozen-search-tool",
                    "languages": ["zh", "en"],
                    "regions": ["global"],
                },
                "calibration_case_set_reference_and_hash": {
                    "reference": "02-校准案例/calibration-cases.jsonl",
                    "sha256": hashlib.sha256(CALIBRATION_CASE_SET_BYTES).hexdigest(),
                },
                "batch_rule": {
                    "batch_size": 10,
                    "stop_after_each_batch": True,
                    "trigger_rate_is_diagnostic_not_pass_gate": True,
                },
                "control_case_rule": {
                    "case_ids": ["CASE-001", "CASE-002"],
                    "drift_requires_pause": True,
                },
                "budget_rule": {
                    "token_limit": 100000,
                    "search_limit": 1000,
                    "time_limit_minutes": 600,
                    "budget_stop_keeps_unprocessed_nodes_not_screened": True,
                },
                "sampling_seed_rule": {
                    "seed": "rc2-fixed-seed",
                    "algorithm": "python_random_v1_srswor",
                },
                "allowed_writes": ["05-工作区/行业语义研究/SEM-RC2-001"],
                "case_preparation_gate": {
                    "authorization": True,
                    "authorization_reference": "USER-CASE-PREP-LEGACY-TEST",
                    "preparation_contract_version": "0.9.0-prep.1",
                    "state": "locked",
                    "locked_at": "2026-08-18T23:00:00Z",
                    "locked_input_sha256": None,
                },
            }
        )
        contract["case_preparation_gate"]["locked_input_sha256"] = (
            preparation_lock_sha256(contract)
        )
        return payload

    def preparation_draft_contract(self) -> dict:
        payload = self.frozen_contract()
        contract = payload["semantic_research_contract"]
        contract.update(
            {
                "contract_version": "1.0.0-prep.1",
                "contract_state": "draft",
                "frozen_at": None,
                "calibration_case_set_reference_and_hash": {
                    "reference": None,
                    "sha256": None,
                },
                "batch_rule": {
                    "batch_size": None,
                    "stop_after_each_batch": True,
                    "trigger_rate_is_diagnostic_not_pass_gate": True,
                },
                "control_case_rule": {
                    "case_ids": [],
                    "drift_requires_pause": True,
                },
                "case_preparation_gate": {
                    "authorization": False,
                    "authorization_reference": None,
                    "preparation_contract_version": None,
                    "state": "draft",
                    "locked_at": None,
                    "locked_input_sha256": None,
                },
            }
        )
        return payload

    def write_frozen_case_set(self, path: Path, count: int = 40) -> list[str]:
        case_ids = [f"CASE-{index:03d}" for index in range(1, count + 1)]
        rows = [
            {
                "record_type": "case_set_contract",
                "schema_version": "1.1",
                "case_set_id": "RC2-40-001",
                "research_contract_id": "SEM-RC2-001",
                "case_set_state": "frozen",
                "case_count": 40,
                "actual_case_record_count": count,
            },
            *[
                {
                    "record_type": "calibration_case",
                    "case_id": case_id,
                    "research_contract_id": "SEM-RC2-001",
                }
                for case_id in case_ids
            ],
        ]
        write_jsonl(path, rows)
        return case_ids

    def initialize_workspace(self, parent: Path) -> Path:
        map_root = parent / "industry-map"
        map_root.mkdir()
        contract_path = parent / "contract.json"
        write_json(contract_path, self.frozen_contract())
        result = run_script(
            INIT_SCRIPT,
            "--map-root",
            str(map_root),
            "--contract",
            str(contract_path),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        workspace = map_root / "05-工作区" / "行业语义研究" / "SEM-RC2-001"
        (workspace / "01-节点快照" / "taxonomy-snapshot.json").write_bytes(
            TAXONOMY_SNAPSHOT_BYTES
        )
        (workspace / "02-校准案例" / "calibration-cases.jsonl").write_bytes(
            CALIBRATION_CASE_SET_BYTES
        )
        return workspace

    def test_initializer_creates_isolated_append_only_workspace_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            workspace = self.initialize_workspace(parent)
            for name in (
                "00-合同",
                "01-节点快照",
                "02-校准案例",
                "03-运行原始记录/baseline",
                "03-运行原始记录/candidate",
                "04-模型交接",
                "05-证据包",
                "06-反向审计",
                "07-报告",
                "08-隔离失败返回",
            ):
                self.assertTrue((workspace / name).is_dir(), name)
            contract_path = parent / "contract.json"
            second = run_script(
                INIT_SCRIPT,
                "--map-root",
                str(parent / "industry-map"),
                "--contract",
                str(contract_path),
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("DESTINATION_EXISTS", second.stderr + second.stdout)

    def test_initializer_rejects_a_frozen_contract_with_empty_required_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            map_root = parent / "industry-map"
            map_root.mkdir()
            payload = self.frozen_contract()
            payload["semantic_research_contract"]["research_theme"]["mechanism"] = None
            contract_path = parent / "contract.json"
            write_json(contract_path, payload)
            result = run_script(
                INIT_SCRIPT,
                "--map-root",
                str(map_root),
                "--contract",
                str(contract_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CONTRACT_INCOMPLETE", result.stderr + result.stdout)

    def test_case_preparation_lock_and_real_case_set_create_only_then_final_frozen_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            draft_path = parent / "research-contract.draft.json"
            locked_path = parent / "case-preparation-contract.locked.json"
            final_path = parent / "semantic-research-contract.json"
            case_set_path = parent / "calibration-case-set.jsonl"
            write_json(draft_path, self.preparation_draft_contract())

            locked = run_script(
                LOCK_PREPARATION_SCRIPT,
                "--contract",
                str(draft_path),
                "--authorization-reference",
                "USER-CASE-PREP-001",
                "--locked-at",
                "2026-08-24T12:00:00Z",
                "--output",
                str(locked_path),
            )
            self.assertEqual(locked.returncode, 0, locked.stderr + locked.stdout)
            locked_contract = json.loads(locked_path.read_text(encoding="utf-8"))[
                "semantic_research_contract"
            ]
            self.assertEqual(locked_contract["contract_state"], "case_preparation_locked")
            self.assertEqual(
                locked_contract["calibration_case_set_reference_and_hash"],
                {"reference": None, "sha256": None},
            )
            self.assertEqual(locked_contract["control_case_rule"]["case_ids"], [])
            self.assertRegex(
                locked_contract["case_preparation_gate"]["locked_input_sha256"],
                r"^[0-9a-f]{64}$",
            )

            map_root = parent / "industry-map"
            map_root.mkdir()
            premature = run_script(
                INIT_SCRIPT,
                "--map-root",
                str(map_root),
                "--contract",
                str(locked_path),
            )
            self.assertNotEqual(premature.returncode, 0)
            self.assertIn("CONTRACT_NOT_FROZEN", premature.stderr + premature.stdout)

            case_ids = self.write_frozen_case_set(case_set_path)
            finalized = run_script(
                FINALIZE_CONTRACT_SCRIPT,
                "--preparation-contract",
                str(locked_path),
                "--case-set",
                str(case_set_path),
                "--case-set-reference",
                "02-校准案例/calibration-case-set.jsonl",
                "--final-contract-version",
                "1.0.0",
                "--batch-size",
                "10",
                "--control-case-id",
                case_ids[0],
                "--control-case-id",
                case_ids[1],
                "--frozen-at",
                "2026-08-24T13:00:00Z",
                "--output",
                str(final_path),
            )
            self.assertEqual(finalized.returncode, 0, finalized.stderr + finalized.stdout)
            final_contract = json.loads(final_path.read_text(encoding="utf-8"))[
                "semantic_research_contract"
            ]
            self.assertEqual(final_contract["contract_state"], "frozen")
            self.assertEqual(final_contract["contract_version"], "1.0.0")
            self.assertEqual(
                final_contract["calibration_case_set_reference_and_hash"]["sha256"],
                hashlib.sha256(case_set_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                final_contract["control_case_rule"]["case_ids"], case_ids[:2]
            )
            accepted = run_script(
                INIT_SCRIPT,
                "--map-root",
                str(map_root),
                "--contract",
                str(final_path),
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr + accepted.stdout)

    def test_case_preparation_lock_rejects_placeholder_case_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            payload = self.preparation_draft_contract()
            contract = payload["semantic_research_contract"]
            contract["calibration_case_set_reference_and_hash"] = {
                "reference": "placeholder.jsonl",
                "sha256": "0" * 64,
            }
            contract["control_case_rule"]["case_ids"] = ["CASE-PLACEHOLDER"]
            draft_path = parent / "draft.json"
            write_json(draft_path, payload)
            result = run_script(
                LOCK_PREPARATION_SCRIPT,
                "--contract",
                str(draft_path),
                "--authorization-reference",
                "USER-CASE-PREP-001",
                "--locked-at",
                "2026-08-24T12:00:00Z",
                "--output",
                str(parent / "locked.json"),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PREPARATION_OUTPUTS_NOT_EMPTY", result.stderr + result.stdout)

    def test_finalizer_rejects_preparation_contract_drift_and_incomplete_case_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            draft_path = parent / "draft.json"
            locked_path = parent / "locked.json"
            write_json(draft_path, self.preparation_draft_contract())
            locked = run_script(
                LOCK_PREPARATION_SCRIPT,
                "--contract",
                str(draft_path),
                "--authorization-reference",
                "USER-CASE-PREP-001",
                "--locked-at",
                "2026-08-24T12:00:00Z",
                "--output",
                str(locked_path),
            )
            self.assertEqual(locked.returncode, 0, locked.stderr + locked.stdout)

            tampered = json.loads(locked_path.read_text(encoding="utf-8"))
            tampered["semantic_research_contract"]["research_theme"]["mechanism"] = (
                "mutated after lock"
            )
            write_json(locked_path, tampered)
            case_set_path = parent / "case-set.jsonl"
            case_ids = self.write_frozen_case_set(case_set_path)
            drift = run_script(
                FINALIZE_CONTRACT_SCRIPT,
                "--preparation-contract",
                str(locked_path),
                "--case-set",
                str(case_set_path),
                "--case-set-reference",
                "02-校准案例/calibration-case-set.jsonl",
                "--final-contract-version",
                "1.0.0",
                "--batch-size",
                "10",
                "--control-case-id",
                case_ids[0],
                "--frozen-at",
                "2026-08-24T13:00:00Z",
                "--output",
                str(parent / "final.json"),
            )
            self.assertNotEqual(drift.returncode, 0)
            self.assertIn("PREPARATION_LOCK_HASH_MISMATCH", drift.stderr + drift.stdout)

            write_json(draft_path, self.preparation_draft_contract())
            locked_path = parent / "locked-clean.json"
            locked = run_script(
                LOCK_PREPARATION_SCRIPT,
                "--contract",
                str(draft_path),
                "--authorization-reference",
                "USER-CASE-PREP-001",
                "--locked-at",
                "2026-08-24T12:00:00Z",
                "--output",
                str(locked_path),
            )
            self.assertEqual(locked.returncode, 0, locked.stderr + locked.stdout)
            incomplete_case_set = parent / "incomplete-case-set.jsonl"
            incomplete_ids = self.write_frozen_case_set(incomplete_case_set, count=39)
            incomplete = run_script(
                FINALIZE_CONTRACT_SCRIPT,
                "--preparation-contract",
                str(locked_path),
                "--case-set",
                str(incomplete_case_set),
                "--case-set-reference",
                "02-校准案例/calibration-case-set.jsonl",
                "--final-contract-version",
                "1.0.0",
                "--batch-size",
                "10",
                "--control-case-id",
                incomplete_ids[0],
                "--frozen-at",
                "2026-08-24T13:00:00Z",
                "--output",
                str(parent / "final-incomplete.json"),
            )
            self.assertNotEqual(incomplete.returncode, 0)
            self.assertIn("CASE_SET_INVALID", incomplete.stderr + incomplete.stdout)

    def test_taxonomy_snapshot_uses_leaf_nodes_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            workbook_path = parent / "taxonomy.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "行业骨架"
            sheet.append(
                [
                    "taxonomy_node_id",
                    "taxonomy_system",
                    "taxonomy_version",
                    "code",
                    "name_zh",
                    "level",
                    "parent_node_id",
                    "status",
                ]
            )
            sheet.append(["业务编号", "体系", "版本", "代码", "名称", "层级", "父级", "状态"])
            sheet.append(["T-ROOT", "TEST", "2026", "A", "根", "section", "", "current"])
            sheet.append(["T-01", "TEST", "2026", "A1", "叶一", "class", "T-ROOT", "current"])
            sheet.append(["T-02", "TEST", "2026", "A2", "叶二", "class", "T-ROOT", "current"])
            workbook.save(workbook_path)
            first = parent / "first.json"
            second = parent / "second.json"
            for output in (first, second):
                result = run_script(
                    FREEZE_SCRIPT,
                    "--taxonomy-workbook",
                    str(workbook_path),
                    "--output",
                    str(output),
                )
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            first_payload = json.loads(first.read_text(encoding="utf-8"))
            second_payload = json.loads(second.read_text(encoding="utf-8"))
            self.assertEqual(first_payload, second_payload)
            self.assertEqual(first_payload["terminal_node_count"], 2)
            self.assertEqual(
                [node["taxonomy_node_id"] for node in first_payload["terminal_nodes"]],
                ["T-01", "T-02"],
            )

    def test_validator_rejects_no_hypothesis_without_two_complete_query_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            record = json.loads(
                (ASSET_ROOT / "screening-record.template.json").read_text(encoding="utf-8")
            )["semantic_screening_record"]
            record.update(
                {
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "industry_node_id": "T-01",
                    "screening_result": "no_hypothesis_formed",
                    "semantic_work_state": "screened",
                    "evidence_state": "unknown",
                    "search_queries": [{"group": "industry_process", "query": "one query"}],
                    "inspected_result_references": [],
                }
            )
            write_jsonl(
                workspace / "03-运行原始记录" / "candidate" / "screening-records.jsonl",
                [record],
            )
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCREENING_MINIMUM_RETRIEVAL_NOT_MET", result.stdout)

    def test_validator_rejects_blank_queries_and_inflated_inspection_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            record = json.loads(
                (ASSET_ROOT / "screening-record.template.json").read_text(encoding="utf-8")
            )["semantic_screening_record"]
            query_groups = [
                "industry_output_or_process",
                "mechanism_use_point_and_cross_domain_synonyms",
            ]
            record.update(
                {
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "industry_node_id": "T-01",
                    "screening_result": "no_hypothesis_formed",
                    "semantic_work_state": "screened",
                    "evidence_state": "unknown",
                    "search_queries": [
                        {
                            "group": group,
                            "query": "",
                            "available_distinct_result_count": 5,
                            "inspected_distinct_result_count": 5,
                        }
                        for group in query_groups
                    ],
                    "inspected_result_references": [
                        {"group": group, "reference": f"result-{index}"}
                        for index, group in enumerate(query_groups)
                    ],
                }
            )
            write_jsonl(
                workspace / "03-运行原始记录" / "candidate" / "screening-records.jsonl",
                [record],
            )
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCREENING_MINIMUM_RETRIEVAL_NOT_MET", result.stdout)

    def test_validator_blocks_calibration_write_to_shared_base_and_unsupported_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            contract_path = workspace / "00-合同" / "semantic-research-contract.json"
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["allowed_writes"] = [
                "02-共享应用知识/industry-application-base.xlsx"
            ]
            write_json(contract_path, payload)
            evidence = {
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "claim_id": "CLAIM-001",
                "evidence_state": "supported",
                "direct_source_support": False,
                "source_location_present": True,
                "snapshot_or_live_source_verified": True,
                "model_b_review": "PASS",
                "claim_scope_within_source": True,
                "circular_source": False,
                "unresolved_counterevidence": False,
            }
            write_jsonl(workspace / "05-证据包" / "evidence-records.jsonl", [evidence])
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CALIBRATION_WRITE_SCOPE_VIOLATION", result.stdout)
            self.assertIn("SUPPORTED_EVIDENCE_GATE_FAILED", result.stdout)

    def test_validator_detects_contract_tampering_after_initialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            contract_path = workspace / "00-合同" / "semantic-research-contract.json"
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["research_theme"]["mechanism"] = (
                "tampered but still nonempty mechanism"
            )
            write_json(contract_path, payload)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CONTRACT_HASH_MISMATCH", result.stdout)

    def test_validator_detects_taxonomy_snapshot_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            (workspace / "01-节点快照" / "taxonomy-snapshot.json").write_text(
                '{"terminal_node_count":999}\n', encoding="utf-8"
            )
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TAXONOMY_SNAPSHOT_HASH_MISMATCH", result.stdout)

    def test_validator_recurses_into_nested_blind_reviewer_packets(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            task = {
                "semantic_model_task": {
                    "task_id": "TASK-B-001",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "input_sha256": "d" * 64,
                    "role": "B",
                    "mode": "blind_source_review",
                    "declared_model_name": "Claude Sonnet 5",
                    "company_name": "must not be visible",
                }
            }
            write_json(workspace / "04-模型交接" / "B" / "task.json", task)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODEL_B_BLINDING_VIOLATION", result.stdout)

    def test_validator_rejects_a_model_return_that_does_not_match_its_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            task = {
                "semantic_model_task": {
                    "task_id": "TASK-B-001",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "input_sha256": "d" * 64,
                    "role": "B",
                    "mode": "blind_source_review",
                    "declared_model_name": "Claude Sonnet 5",
                    "actual_model_id_required": True,
                    "visible_inputs": ["minimal_claim", "source_reference"],
                    "source_references": ["SOURCE-001"],
                    "output_contract": "semantic_model_return",
                    "transport": "manual_external_handoff",
                    "prohibited_inputs": ["company_name", "full_reasoning"],
                    "prohibited_actions": ["use_model_knowledge_to_fill_source_gap"],
                    "issued_at": "2026-08-19T00:00:00Z",
                }
            }
            returned = {
                "semantic_model_return": {
                    "task_id": "TASK-B-001",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "input_sha256": "e" * 64,
                    "declared_model_name": "Claude Sonnet 5",
                    "actual_model_id_or_unknown": "claude-sonnet-5-build-x",
                    "provider": "Anthropic",
                    "run_id": "RUN-B-001",
                    "run_started_at": "2026-08-19T00:01:00Z",
                    "result_state": "PASS",
                    "reason_codes": [],
                    "source_access_results": [],
                    "structured_findings": [],
                    "unknowns": [],
                    "returned_at": "2026-08-19T00:02:00Z",
                }
            }
            write_json(workspace / "04-模型交接" / "B" / "task.json", task)
            write_json(workspace / "03-运行原始记录" / "candidate" / "B-return.json", returned)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODEL_RETURN_MISMATCH", result.stdout)

    def test_handoff_builder_embeds_visible_input_return_schema_and_field_ownership(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            task = json.loads(
                (ASSET_ROOT / "model-task.template.json").read_text(encoding="utf-8")
            )
            task_body = task["semantic_model_task"]
            task_body.update(
                {
                    "task_id": "TASK-B-BUNDLE",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "role": "B",
                    "mode": "blind_source_review",
                    "declared_model_name": "Claude Sonnet 5",
                    "source_references": ["SOURCE-001"],
                    "issued_at": "2026-08-19T00:00:00Z",
                }
            )
            visible_input = {
                "minimal_claim": "A bounded claim",
                "source_records": [{"source_id": "SOURCE-001"}],
            }
            task_path = parent / "task.json"
            input_path = parent / "input.json"
            output_path = parent / "handoff.json"
            write_json(task_path, task)
            write_json(input_path, visible_input)

            result = run_script(
                BUILD_HANDOFF_SCRIPT,
                "--task",
                str(task_path),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            packet = json.loads(output_path.read_text(encoding="utf-8"))[
                "semantic_model_task"
            ]
            self.assertEqual(packet["visible_input"], visible_input)
            self.assertEqual(
                packet["input_sha256"], canonical_json_sha256(visible_input)
            )
            self.assertEqual(
                packet["input_hash_algorithm"], "sha256_canonical_json_v1"
            )
            self.assertIn("semantic_model_return", packet["expected_return_schema"])
            self.assertIn("model_required_fields", packet["field_ownership"])
            self.assertIn("receiver_owned_fields", packet["field_ownership"])
            self.assertTrue(
                packet["manual_transport_rules"][
                    "unknown_runtime_metadata_must_be_null"
                ]
            )
            second = run_script(
                BUILD_HANDOFF_SCRIPT,
                "--task",
                str(task_path),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("DESTINATION_EXISTS", second.stderr)

    def test_handoff_builder_rejects_unfilled_task_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            task_path = parent / "task.json"
            input_path = parent / "input.json"
            output_path = parent / "handoff.json"
            task_path.write_bytes((ASSET_ROOT / "model-task.template.json").read_bytes())
            write_json(input_path, {"minimal_claim": "A bounded claim"})
            result = run_script(
                BUILD_HANDOFF_SCRIPT,
                "--task",
                str(task_path),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODEL_TASK_INCOMPLETE", result.stderr)
            self.assertFalse(output_path.exists())

    def test_validator_accepts_manual_return_without_model_runtime_metadata_when_receipt_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            task_template = json.loads(
                (ASSET_ROOT / "model-task.template.json").read_text(encoding="utf-8")
            )["semantic_model_task"]
            visible_input = {
                "minimal_claim": "A bounded claim",
                "source_records": [{"source_id": "SOURCE-001"}],
            }
            task_body = {
                "task_id": "TASK-B-MANUAL",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "input_hash_algorithm": "sha256_canonical_json_v1",
                "role": "B",
                "mode": "blind_source_review",
                "trigger_reason": None,
                "declared_model_name": "Claude Sonnet 5",
                "identity_evidence_policy": {
                    "minimum_level": "operator_attested",
                    "accepted_types": [
                        "connector_verified",
                        "platform_export",
                        "ui_observed",
                        "user_attested",
                    ],
                },
                "visible_input": visible_input,
                "source_references": ["SOURCE-001"],
                "expected_return_schema": task_template["expected_return_schema"],
                "field_ownership": task_template["field_ownership"],
                "manual_transport_rules": task_template["manual_transport_rules"],
                "output_contract": "semantic_model_return",
                "transport": "manual_external_handoff",
                "source_permissions": ["public_web"],
                "prohibited_inputs": ["company_name", "full_reasoning"],
                "prohibited_actions": [
                    "use_model_knowledge_to_fill_source_gap"
                ],
                "stop_condition": "return one raw semantic_model_return JSON object and stop",
                "issued_at": "2026-08-19T00:00:00Z",
            }
            return_body = {
                "task_id": "TASK-B-MANUAL",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "declared_model_name": "Claude Sonnet 5",
                "actual_model_id_or_unknown": "unknown",
                "provider_or_unknown": "Anthropic",
                "model_reported_run_id": None,
                "model_reported_started_at": None,
                "result_state": "PASS",
                "reason_codes": ["SOURCE_READ_AND_SCOPE_MATCHED"],
                "source_access_results": [
                    {"source_id": "SOURCE-001", "state": "read"}
                ],
                "structured_findings": [
                    {"claim_id": "CLAIM-001", "review": "PASS"}
                ],
                "unknowns": [],
                "model_reported_returned_at": None,
            }
            task_path = workspace / "04-模型交接" / "B" / "task.json"
            return_path = (
                workspace
                / "03-运行原始记录"
                / "candidate"
                / "B-return.json"
            )
            write_json(
                task_path,
                {"schema_version": "1.1", "semantic_model_task": task_body},
            )
            write_json(
                return_path,
                {"schema_version": "1.1", "semantic_model_return": return_body},
            )
            receipt = {
                "schema_version": "1.1",
                "semantic_model_receipt": {
                    "receipt_id": "RECEIPT-B-MANUAL",
                    "task_id": "TASK-B-MANUAL",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "transport": "manual_external_handoff",
                    "raw_return_reference": str(return_path.relative_to(workspace)),
                    "raw_return_sha256": hashlib.sha256(return_path.read_bytes()).hexdigest(),
                    "received_at": "2026-08-19T00:03:00Z",
                    "identity_evidence": {
                        "observed_model_label_or_unknown": "Claude Sonnet 5",
                        "evidence_type": "user_attested",
                        "evidence_reference_or_null": "USER-HANDOFF-001",
                        "verification_level": "operator_attested",
                    },
                    "executor_metadata": {
                        "executor_run_id_or_null": None,
                        "executor_started_at_or_null": None,
                        "executor_returned_at_or_null": None,
                        "provenance": "none",
                    },
                    "acceptance_state": "PASS",
                    "reason_codes": ["RAW_RETURN_HASH_MATCHED", "IDENTITY_ATTESTED"],
                }
            }
            write_json(
                workspace / "04-模型交接" / "B" / "receipt.json", receipt
            )
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_validator_rejects_manual_return_without_a_receiver_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            task_template = json.loads(
                (ASSET_ROOT / "model-task.template.json").read_text(encoding="utf-8")
            )["semantic_model_task"]
            visible_input = {"minimal_claim": "A bounded claim"}
            task_body = {
                "task_id": "TASK-B-NO-RECEIPT",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "input_hash_algorithm": "sha256_canonical_json_v1",
                "role": "B",
                "mode": "blind_source_review",
                "declared_model_name": "Claude Sonnet 5",
                "identity_evidence_policy": {
                    "minimum_level": "operator_attested",
                    "accepted_types": [
                        "connector_verified",
                        "platform_export",
                        "ui_observed",
                        "user_attested",
                    ],
                },
                "visible_input": visible_input,
                "source_references": ["SOURCE-001"],
                "source_permissions": ["public_web"],
                "expected_return_schema": task_template["expected_return_schema"],
                "field_ownership": task_template["field_ownership"],
                "manual_transport_rules": task_template["manual_transport_rules"],
                "output_contract": "semantic_model_return",
                "transport": "manual_external_handoff",
                "prohibited_inputs": ["company_name", "full_reasoning"],
                "prohibited_actions": [
                    "use_model_knowledge_to_fill_source_gap"
                ],
                "stop_condition": "return raw JSON and stop",
                "issued_at": "2026-08-19T00:00:00Z",
            }
            return_body = {
                "task_id": "TASK-B-NO-RECEIPT",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "declared_model_name": "Claude Sonnet 5",
                "actual_model_id_or_unknown": "unknown",
                "provider_or_unknown": "Anthropic",
                "model_reported_run_id": None,
                "model_reported_started_at": None,
                "result_state": "PASS",
                "reason_codes": ["SOURCE_READ_AND_SCOPE_MATCHED"],
                "source_access_results": [],
                "structured_findings": [],
                "unknowns": [],
                "model_reported_returned_at": None,
            }
            write_json(
                workspace / "04-模型交接" / "B" / "task.json",
                {"schema_version": "1.1", "semantic_model_task": task_body},
            )
            write_json(
                workspace
                / "03-运行原始记录"
                / "candidate"
                / "B-return.json",
                {"schema_version": "1.1", "semantic_model_return": return_body},
            )
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODEL_RECEIPT_MISSING", result.stdout)

    def test_validator_rejects_receiver_receipt_with_wrong_raw_return_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            task_template = json.loads(
                (ASSET_ROOT / "model-task.template.json").read_text(encoding="utf-8")
            )["semantic_model_task"]
            visible_input = {"minimal_claim": "A bounded claim"}
            task_body = {
                "task_id": "TASK-B-BAD-RECEIPT",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "input_hash_algorithm": "sha256_canonical_json_v1",
                "role": "B",
                "mode": "blind_source_review",
                "declared_model_name": "Claude Sonnet 5",
                "identity_evidence_policy": {
                    "minimum_level": "operator_attested",
                    "accepted_types": [
                        "connector_verified",
                        "platform_export",
                        "ui_observed",
                        "user_attested",
                    ],
                },
                "visible_input": visible_input,
                "source_references": ["SOURCE-001"],
                "expected_return_schema": task_template["expected_return_schema"],
                "field_ownership": task_template["field_ownership"],
                "manual_transport_rules": task_template["manual_transport_rules"],
                "output_contract": "semantic_model_return",
                "transport": "manual_external_handoff",
                "source_permissions": ["public_web"],
                "prohibited_inputs": ["company_name"],
                "prohibited_actions": ["fill_source_gap"],
                "stop_condition": "return raw JSON and stop",
                "issued_at": "2026-08-19T00:00:00Z",
            }
            return_body = {
                "task_id": "TASK-B-BAD-RECEIPT",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "declared_model_name": "Claude Sonnet 5",
                "actual_model_id_or_unknown": "unknown",
                "provider_or_unknown": "Anthropic",
                "model_reported_run_id": None,
                "model_reported_started_at": None,
                "result_state": "PASS",
                "reason_codes": ["SOURCE_READ_AND_SCOPE_MATCHED"],
                "source_access_results": [],
                "structured_findings": [],
                "unknowns": [],
                "model_reported_returned_at": None,
            }
            task_path = workspace / "04-模型交接" / "B" / "task.json"
            return_path = workspace / "03-运行原始记录" / "candidate" / "return.json"
            write_json(
                task_path,
                {"schema_version": "1.1", "semantic_model_task": task_body},
            )
            write_json(
                return_path,
                {"schema_version": "1.1", "semantic_model_return": return_body},
            )
            receipt = {
                "schema_version": "1.1",
                "semantic_model_receipt": {
                    "receipt_id": "RECEIPT-B-BAD-HASH",
                    "task_id": "TASK-B-BAD-RECEIPT",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "transport": "manual_external_handoff",
                    "raw_return_reference": str(return_path.relative_to(workspace)),
                    "raw_return_sha256": "f" * 64,
                    "received_at": "2026-08-19T00:03:00Z",
                    "identity_evidence": {
                        "observed_model_label_or_unknown": "Claude Sonnet 5",
                        "evidence_type": "user_attested",
                        "evidence_reference_or_null": "USER-HANDOFF-001",
                        "verification_level": "operator_attested",
                    },
                    "executor_metadata": {
                        "executor_run_id_or_null": None,
                        "executor_started_at_or_null": None,
                        "executor_returned_at_or_null": None,
                        "provenance": "none",
                    },
                    "acceptance_state": "PASS",
                    "reason_codes": ["RAW_RETURN_RECEIVED"],
                }
            }
            receipt_path = workspace / "04-模型交接" / "B" / "receipt.json"
            write_json(receipt_path, receipt)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODEL_RECEIPT_RETURN_HASH_MISMATCH", result.stdout)

            receipt_body = receipt["semantic_model_receipt"]
            receipt_body["raw_return_sha256"] = hashlib.sha256(
                return_path.read_bytes()
            ).hexdigest()
            receipt_body["executor_metadata"] = {
                "executor_run_id_or_null": "fabricated-run-id",
                "executor_started_at_or_null": "2026-08-19T00:01:00Z",
                "executor_returned_at_or_null": "2026-08-19T00:02:00Z",
                "provenance": "manual_external_handoff",
            }
            write_json(receipt_path, receipt)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "MODEL_RECEIPT_MANUAL_EXECUTOR_METADATA_INVALID", result.stdout
            )

            receipt_body["executor_metadata"] = {
                "executor_run_id_or_null": None,
                "executor_started_at_or_null": None,
                "executor_returned_at_or_null": None,
                "provenance": "none",
            }
            receipt_body["identity_evidence"][
                "observed_model_label_or_unknown"
            ] = "Grok 4.5"
            write_json(receipt_path, receipt)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODEL_RECEIPT_IDENTITY_UNVERIFIED", result.stdout)

    def test_validator_rejects_model_c_without_an_allowed_trigger(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            task = {
                "semantic_model_task": {
                    "task_id": "TASK-C-001",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "input_sha256": "d" * 64,
                    "role": "C",
                    "mode": "dispute",
                    "trigger_reason": None,
                    "declared_model_name": "Grok 4.5",
                    "actual_model_id_required": True,
                    "visible_inputs": ["minimal_claim", "source_reference"],
                    "source_references": ["SOURCE-001"],
                    "output_contract": "semantic_model_return",
                    "transport": "manual_external_handoff",
                    "prohibited_inputs": ["model_a_confidence", "full_reasoning"],
                    "prohibited_actions": ["majority_vote_evidence_upgrade"],
                    "issued_at": "2026-08-19T00:00:00Z",
                }
            }
            write_json(workspace / "04-模型交接" / "C" / "task.json", task)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODEL_C_TRIGGER_INVALID", result.stdout)

    def test_validator_accepts_a_matching_blind_review_task_and_return(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            task_template = json.loads(
                (ASSET_ROOT / "model-task.template.json").read_text(encoding="utf-8")
            )["semantic_model_task"]
            visible_input = {
                "minimal_claim": "A bounded claim",
                "source_records": [{"source_id": "SOURCE-001"}],
            }
            task_body = {
                "task_id": "TASK-B-VALID",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "input_hash_algorithm": "sha256_canonical_json_v1",
                "role": "B",
                "mode": "blind_source_review",
                "trigger_reason": None,
                "declared_model_name": "Claude Sonnet 5",
                "identity_evidence_policy": {
                    "minimum_level": "operator_attested",
                    "accepted_types": [
                        "connector_verified",
                        "platform_export",
                        "ui_observed",
                        "user_attested",
                    ],
                },
                "visible_input": visible_input,
                "source_references": ["SOURCE-001"],
                "expected_return_schema": task_template["expected_return_schema"],
                "field_ownership": task_template["field_ownership"],
                "manual_transport_rules": task_template["manual_transport_rules"],
                "output_contract": "semantic_model_return",
                "transport": "manual_external_handoff",
                "source_permissions": ["public_web"],
                "prohibited_inputs": ["company_name", "full_reasoning"],
                "prohibited_actions": ["use_model_knowledge_to_fill_source_gap"],
                "stop_condition": "return raw JSON and stop",
                "issued_at": "2026-08-19T00:00:00Z",
            }
            return_body = {
                "task_id": "TASK-B-VALID",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "declared_model_name": "Claude Sonnet 5",
                "actual_model_id_or_unknown": "claude-sonnet-5-build-x",
                "provider_or_unknown": "Anthropic",
                "model_reported_run_id": "RUN-B-VALID",
                "model_reported_started_at": "2026-08-19T00:01:00Z",
                "result_state": "PASS",
                "reason_codes": ["SOURCE_READ_AND_SCOPE_MATCHED"],
                "source_access_results": [{"source_id": "SOURCE-001", "state": "read"}],
                "structured_findings": [{"claim_id": "CLAIM-001", "review": "PASS"}],
                "unknowns": [],
                "model_reported_returned_at": "2026-08-19T00:02:00Z",
            }
            return_path = (
                workspace / "03-运行原始记录" / "candidate" / "B-return.json"
            )
            write_json(
                workspace / "04-模型交接" / "B" / "task.json",
                {"schema_version": "1.1", "semantic_model_task": task_body},
            )
            write_json(
                return_path,
                {"schema_version": "1.1", "semantic_model_return": return_body},
            )
            receipt = {
                "schema_version": "1.1",
                "semantic_model_receipt": {
                    "receipt_id": "RECEIPT-B-VALID",
                    "task_id": "TASK-B-VALID",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "transport": "manual_external_handoff",
                    "raw_return_reference": str(return_path.relative_to(workspace)),
                    "raw_return_sha256": hashlib.sha256(return_path.read_bytes()).hexdigest(),
                    "received_at": "2026-08-19T00:03:00Z",
                    "identity_evidence": {
                        "observed_model_label_or_unknown": "Claude Sonnet 5",
                        "evidence_type": "user_attested",
                        "evidence_reference_or_null": "USER-HANDOFF-001",
                        "verification_level": "operator_attested",
                    },
                    "executor_metadata": {
                        "executor_run_id_or_null": None,
                        "executor_started_at_or_null": None,
                        "executor_returned_at_or_null": None,
                        "provenance": "none",
                    },
                    "acceptance_state": "PASS",
                    "reason_codes": ["RAW_RETURN_HASH_MATCHED", "IDENTITY_ATTESTED"],
                }
            }
            write_json(workspace / "04-模型交接" / "B" / "receipt.json", receipt)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_validator_accepts_connected_model_a_with_receiver_executor_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.initialize_workspace(Path(tmp))
            task_template = json.loads(
                (ASSET_ROOT / "model-task.template.json").read_text(encoding="utf-8")
            )["semantic_model_task"]
            visible_input = {"industry_node_id": "T-01"}
            task_body = {
                "task_id": "TASK-A-CONNECTED",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "input_hash_algorithm": "sha256_canonical_json_v1",
                "role": "A",
                "mode": "screening",
                "trigger_reason": None,
                "declared_model_name": "GPT-5.6 Terra",
                "identity_evidence_policy": {
                    "minimum_level": "platform_verified",
                    "accepted_types": ["connector_verified", "platform_export"],
                },
                "visible_input": visible_input,
                "source_references": ["SOURCE-001"],
                "source_permissions": ["public_web"],
                "expected_return_schema": task_template["expected_return_schema"],
                "field_ownership": task_template["field_ownership"],
                "manual_transport_rules": task_template["manual_transport_rules"],
                "output_contract": "semantic_model_return",
                "transport": "codex_task",
                "prohibited_inputs": ["company_name"],
                "prohibited_actions": ["upgrade_own_evidence"],
                "stop_condition": "return raw JSON and stop",
                "issued_at": "2026-08-19T00:00:00Z",
            }
            return_body = {
                "task_id": "TASK-A-CONNECTED",
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "input_sha256": canonical_json_sha256(visible_input),
                "declared_model_name": "GPT-5.6 Terra",
                "actual_model_id_or_unknown": "gpt-5.6-terra",
                "provider_or_unknown": "OpenAI",
                "model_reported_run_id": None,
                "model_reported_started_at": None,
                "result_state": "PASS",
                "reason_codes": ["SCREENING_COMPLETE"],
                "source_access_results": [],
                "structured_findings": [],
                "unknowns": [],
                "model_reported_returned_at": None,
            }
            task_path = workspace / "04-模型交接" / "A" / "task.json"
            return_path = workspace / "03-运行原始记录" / "candidate" / "A-return.json"
            write_json(
                task_path,
                {"schema_version": "1.1", "semantic_model_task": task_body},
            )
            write_json(
                return_path,
                {"schema_version": "1.1", "semantic_model_return": return_body},
            )
            receipt = {
                "schema_version": "1.1",
                "semantic_model_receipt": {
                    "receipt_id": "RECEIPT-A-CONNECTED",
                    "task_id": "TASK-A-CONNECTED",
                    "research_contract_id": "SEM-RC2-001",
                    "contract_version": "1.0.0",
                    "transport": "codex_task",
                    "raw_return_reference": str(return_path.relative_to(workspace)),
                    "raw_return_sha256": hashlib.sha256(return_path.read_bytes()).hexdigest(),
                    "received_at": "2026-08-19T00:03:00Z",
                    "identity_evidence": {
                        "observed_model_label_or_unknown": "GPT-5.6 Terra",
                        "evidence_type": "platform_export",
                        "evidence_reference_or_null": "CODEX-TASK-TRACE-001",
                        "verification_level": "platform_verified",
                    },
                    "executor_metadata": {
                        "executor_run_id_or_null": "CODEX-RUN-001",
                        "executor_started_at_or_null": "2026-08-19T00:01:00Z",
                        "executor_returned_at_or_null": "2026-08-19T00:02:00Z",
                        "provenance": "codex_task",
                    },
                    "acceptance_state": "PASS",
                    "reason_codes": ["RAW_RETURN_HASH_MATCHED", "PLATFORM_IDENTITY_VERIFIED"],
                }
            }
            write_json(workspace / "04-模型交接" / "A" / "receipt.json", receipt)
            result = run_script(VALIDATE_SCRIPT, str(workspace), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_reverse_audit_sampling_is_reproducible_and_strata_are_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            records = []
            for index in range(20):
                records.append(
                    {
                        "industry_node_id": f"T-{index:02d}",
                        "screening_result": "no_hypothesis_formed",
                        "top_level_node_id": f"TOP-{index % 4}",
                        "risk_layer_inputs": {
                            "signal_conflict": index % 5 == 0,
                            "is_nec_or_miscellaneous_node": index % 5 == 1,
                            "source_scarce": index % 5 == 2,
                            "semantic_ambiguity": index % 5 == 3,
                        },
                    }
                )
            source = parent / "screening.jsonl"
            write_jsonl(source, records)
            outputs = [parent / "audit-1.json", parent / "audit-2.json"]
            for output in outputs:
                result = run_script(
                    SAMPLE_SCRIPT,
                    "--screening-records",
                    str(source),
                    "--seed",
                    "rc2-fixed-seed",
                    "--output",
                    str(output),
                )
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            first = json.loads(outputs[0].read_text(encoding="utf-8"))
            second = json.loads(outputs[1].read_text(encoding="utf-8"))
            self.assertEqual(first, second)
            sampled = first["statistical_sample"]
            self.assertEqual(len(sampled), len({item["industry_node_id"] for item in sampled}))
            self.assertLessEqual(first["zero_miss_overall_upper_bound"], 0.05)
            self.assertEqual(
                {item["risk_stratum"] for item in first["population_assignments"]},
                {
                    "signal_conflict",
                    "nec_or_miscellaneous",
                    "source_scarce",
                    "semantic_ambiguity",
                    "ordinary",
                },
            )

    def test_reverse_audit_requires_every_selected_node_before_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            records = [
                {
                    "industry_node_id": f"T-{index:02d}",
                    "screening_result": "no_hypothesis_formed",
                    "top_level_node_id": f"TOP-{index % 3}",
                    "risk_layer_inputs": {"source_scarce": index % 3 == 0},
                }
                for index in range(18)
            ]
            source = parent / "screening.jsonl"
            plan_path = parent / "audit-plan.json"
            write_jsonl(source, records)
            planned = run_script(
                SAMPLE_SCRIPT,
                "--screening-records",
                str(source),
                "--seed",
                "rc2-fixed-seed",
                "--output",
                str(plan_path),
            )
            self.assertEqual(planned.returncode, 0, planned.stderr + planned.stdout)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            required_ids = {
                item["industry_node_id"] for item in plan["statistical_sample"]
            } | {
                item["industry_node_id"] for item in plan["industry_coverage_supplement"]
            }
            complete_results = [
                {
                    "industry_node_id": node_id,
                    "audit_result": "PASS",
                    "confirmed_miss": False,
                }
                for node_id in sorted(required_ids)
            ]
            audit_results = parent / "audit-results.jsonl"
            write_jsonl(audit_results, complete_results)
            completed_path = parent / "audit-completed.json"
            completed = run_script(
                SAMPLE_SCRIPT,
                "--screening-records",
                str(source),
                "--seed",
                "rc2-fixed-seed",
                "--output",
                str(completed_path),
                "--audit-results",
                str(audit_results),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            self.assertEqual(
                json.loads(completed_path.read_text(encoding="utf-8"))["audit_state"],
                "PASS",
            )

            write_jsonl(audit_results, complete_results[:-1])
            incomplete_path = parent / "audit-incomplete.json"
            incomplete = run_script(
                SAMPLE_SCRIPT,
                "--screening-records",
                str(source),
                "--seed",
                "rc2-fixed-seed",
                "--output",
                str(incomplete_path),
                "--audit-results",
                str(audit_results),
            )
            self.assertNotEqual(incomplete.returncode, 0)
            self.assertEqual(
                json.loads(incomplete_path.read_text(encoding="utf-8"))["audit_state"],
                "INCONCLUSIVE",
            )

    def test_calibration_evaluator_applies_safety_gates_before_efficiency(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            paired_fields = {
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "taxonomy_snapshot_sha256": "a" * 64,
                "calibration_case_set_sha256": "b" * 64,
                "model_profile_id": "rc2-pilot-v1",
                "case_ids": [f"CASE-{index:03d}" for index in range(40)],
            }
            baseline = {
                **paired_fields,
                "method_arm": "baseline_full_depth",
                "run_complete": True,
                "deep_expansion_count": 40,
                "known_positive_count": 14,
            }
            candidate = {
                **paired_fields,
                "method_arm": "candidate_screen_then_expand",
                "run_complete": True,
                "deep_expansion_count": 30,
                "known_positive_count": 14,
                "known_positive_entered_expansion": 14,
                "safety_failures": [],
                "reproducible": True,
            }
            baseline_path = parent / "baseline.json"
            candidate_path = parent / "candidate.json"
            output_path = parent / "effective-report.json"
            write_json(baseline_path, baseline)
            write_json(candidate_path, candidate)
            effective = run_script(
                EVALUATE_SCRIPT,
                "--baseline",
                str(baseline_path),
                "--candidate",
                str(candidate_path),
                "--output",
                str(output_path),
            )
            self.assertEqual(effective.returncode, 0, effective.stderr + effective.stdout)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))["method_validation_state"],
                "EFFECTIVE",
            )

            candidate["safety_failures"] = ["CIRCULAR_SOURCE_ENTERED_SUPPORTED"]
            write_json(candidate_path, candidate)
            output_path = parent / "failed-report.json"
            failed = run_script(
                EVALUATE_SCRIPT,
                "--baseline",
                str(baseline_path),
                "--candidate",
                str(candidate_path),
                "--output",
                str(output_path),
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))["method_validation_state"],
                "NOT_EFFECTIVE",
            )

    def test_calibration_evaluator_rejects_unpaired_case_sets(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            case_ids = [f"CASE-{index:03d}" for index in range(40)]
            shared = {
                "research_contract_id": "SEM-RC2-001",
                "contract_version": "1.0.0",
                "taxonomy_snapshot_sha256": "a" * 64,
                "model_profile_id": "rc2-pilot-v1",
                "case_ids": case_ids,
                "run_complete": True,
                "known_positive_count": 14,
            }
            baseline = {
                **shared,
                "method_arm": "baseline_full_depth",
                "calibration_case_set_sha256": "b" * 64,
                "deep_expansion_count": 40,
            }
            candidate = {
                **shared,
                "method_arm": "candidate_screen_then_expand",
                "calibration_case_set_sha256": "c" * 64,
                "deep_expansion_count": 30,
                "known_positive_entered_expansion": 14,
                "safety_failures": [],
                "reproducible": True,
            }
            baseline_path = parent / "baseline.json"
            candidate_path = parent / "candidate.json"
            output_path = parent / "report.json"
            write_json(baseline_path, baseline)
            write_json(candidate_path, candidate)
            result = run_script(
                EVALUATE_SCRIPT,
                "--baseline",
                str(baseline_path),
                "--candidate",
                str(candidate_path),
                "--output",
                str(output_path),
            )
            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["method_validation_state"], "INCONCLUSIVE")
            self.assertIn("paired calibration identity mismatch", report["reasons"])

            baseline["run_complete"] = False
            write_json(baseline_path, baseline)
            output_path = parent / "inconclusive-report.json"
            inconclusive = run_script(
                EVALUATE_SCRIPT,
                "--baseline",
                str(baseline_path),
                "--candidate",
                str(candidate_path),
                "--output",
                str(output_path),
            )
            self.assertNotEqual(inconclusive.returncode, 0)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))["method_validation_state"],
                "INCONCLUSIVE",
            )


if __name__ == "__main__":
    unittest.main()
