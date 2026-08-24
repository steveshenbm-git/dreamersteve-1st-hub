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
    / "industry-application-map-builder"
    / "skills"
    / "industry-application-map-builder"
)
VALIDATE = SKILL_ROOT / "scripts" / "validate_content_first_workspace.py"
EVALUATE = SKILL_ROOT / "scripts" / "evaluate_content_first_calibration.py"
FULL_GATE = SKILL_ROOT / "scripts" / "check_content_first_full_screening_gate.py"
INIT_CONTENT_WORKSPACE = SKILL_ROOT / "scripts" / "init_content_first_workspace.py"
STRICT_EVALUATE = SKILL_ROOT / "scripts" / "evaluate_semantic_calibration.py"
FULL_COVERAGE = SKILL_ROOT / "scripts" / "validate_content_first_full_coverage.py"


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        text=True,
        capture_output=True,
    )


class ContentFirstToolTests(unittest.TestCase):
    def content_contract(self, authorized: bool = False) -> dict:
        return {
            "schema_version": "1.0",
            "semantic_research_contract": {
                "research_contract_id": "CONTENT-RC2-001",
                "contract_version": "1.0.0-content.1",
                "contract_state": "frozen",
                "execution_mode": "content_first",
                "taxonomy_snapshot_sha256": "a" * 64,
                "terminal_node_count": 1382,
                "terminal_node_manifest_reference": "01-节点快照/terminal-nodes.json",
                "terminal_node_manifest_sha256": "d" * 64,
                "calibration_case_set_reference_and_hash": {
                    "reference": "02-校准案例/cases.jsonl",
                    "sha256": "b" * 64,
                },
                "source_truth_package_reference": "02-来源真值/source-truth.json",
                "source_truth_package_sha256": "c" * 64,
                "full_screening_authorization": authorized,
                "full_screening_authorization_reference": (
                    "USER-CONTENT-FULL-001" if authorized else None
                ),
                "content_first_policy": {
                    "contract_version": "1.0",
                    "raw_response_must_be_unchanged": True,
                    "platform_audit_required_for_content_pass": False,
                    "content_method_state": "CONTENT_CALIBRATION_PASS",
                    "content_full_screening_state": (
                        "AUTHORIZED_NOT_STARTED" if authorized else "NOT_AUTHORIZED"
                    ),
                    "downstream_release_state": "RESEARCH_ONLY_BLOCKED",
                    "minimum_evidence_fields": [
                        "subject",
                        "method_arm",
                        "visible_input",
                        "visible_input_sha256",
                        "raw_response_reference",
                        "raw_response_sha256",
                        "source_truth_comparison_reference",
                        "source_truth_comparison_sha256",
                        "unknown_items",
                    ],
                },
            },
        }

    def make_workspace(self, parent: Path) -> tuple[Path, Path]:
        workspace = parent / "content-first-workspace"
        raw_path = workspace / "03-内容原始回答" / "candidate" / "CASE-001.raw.txt"
        source_path = workspace / "02-来源真值" / "CASE-001.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(b'{"answer":"preserved verbatim","unknowns":["not measured"]}\n')
        source = {"case_id": "CASE-001", "truth": "hypothesis only", "sources": ["SRC-001"]}
        write_json(source_path, source)
        visible_input = {"case_id": "CASE-001", "official_name": "Test industry"}
        envelope = {
            "schema_version": "1.0",
            "semantic_content_raw_answer": {
                "raw_answer_id": "RAW-CASE-001-CANDIDATE",
                "research_contract_id": "CONTENT-RC2-001",
                "contract_version": "1.0.0-content.1",
                "subject": {"kind": "calibration_case", "id": "CASE-001"},
                "method_arm": "candidate_screen_then_expand",
                "visible_input": visible_input,
                "visible_input_sha256": canonical_sha256(visible_input),
                "raw_response_reference": str(raw_path.relative_to(workspace)),
                "raw_response_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
                "raw_response_format": "json",
                "source_truth_comparison_reference": str(source_path.relative_to(workspace)),
                "source_truth_comparison_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                "platform_audit_state": "NOT_COLLECTED",
                "platform_audit_reference_or_null": None,
                "envelope_sha256": None,
            },
        }
        envelope_body = envelope["semantic_content_raw_answer"]
        envelope_body["envelope_sha256"] = canonical_sha256(
            {**envelope_body, "envelope_sha256": None}
        )
        envelope_path = workspace / "03-内容原始回答" / "candidate" / "CASE-001.envelope.json"
        write_json(envelope_path, envelope)
        scorecard = {
            "schema_version": "1.0",
            "semantic_content_scorecard": {
                "scorecard_id": "SCORE-CASE-001-CANDIDATE",
                "raw_answer_reference": str(envelope_path.relative_to(workspace)),
                "raw_answer_sha256": hashlib.sha256(envelope_path.read_bytes()).hexdigest(),
                "subject": {"kind": "calibration_case", "id": "CASE-001"},
                "method_arm": "candidate_screen_then_expand",
                "visible_input_sha256": envelope_body["visible_input_sha256"],
                "source_truth_comparison_reference": envelope_body[
                    "source_truth_comparison_reference"
                ],
                "source_truth_comparison_sha256": envelope_body[
                    "source_truth_comparison_sha256"
                ],
                "scoring_rubric_version": "1.0",
                "scoring_items": {
                    name: {"score": 2, "critical": critical, "reason": "checked"}
                    for name, critical in (
                        ("scope_taxonomy_grounding", True),
                        ("three_axis_handling", True),
                        ("source_truth_alignment", True),
                        ("safety_boundary", True),
                        ("unknown_disclosure", False),
                    )
                },
                "unknown_items": ["not measured"],
                "content_score_result": "PASS",
                "platform_audit_state": "NOT_COLLECTED",
                "platform_audit_reference_or_null": None,
                "scorecard_sha256": None,
            },
        }
        score_body = scorecard["semantic_content_scorecard"]
        score_body["scorecard_sha256"] = canonical_sha256(
            {**score_body, "scorecard_sha256": None}
        )
        write_json(workspace / "07-报告" / "content-scorecards" / "CASE-001.json", scorecard)
        write_json(workspace / "00-合同" / "semantic-research-contract.json", self.content_contract())
        return workspace, raw_path

    def arm(self, method_arm: str) -> dict:
        case_ids = [f"CASE-{index:03d}" for index in range(1, 41)]
        return {
            "schema_version": "1.0",
            "semantic_content_calibration_arm": {
                "research_contract_id": "CONTENT-RC2-001",
                "contract_version": "1.0.0-content.1",
                "taxonomy_snapshot_sha256": "a" * 64,
                "calibration_case_set_sha256": "b" * 64,
                "source_truth_package_sha256": "c" * 64,
                "method_arm": method_arm,
                "run_complete": True,
                "case_evidence": [
                    {
                        "case_id": case_id,
                        "visible_input_sha256": f"{index + 200:064x}",
                        "raw_response_sha256": f"{index:064x}",
                        "scorecard_sha256": f"{index + 100:064x}",
                        "content_score_result": "PASS",
                        "unknown_items_present": True,
                    }
                    for index, case_id in enumerate(case_ids, start=1)
                ],
                "known_positive_case_ids": case_ids[:14],
                "known_positive_entered_expansion_case_ids": case_ids[:14],
                "deep_expansion_count": 40 if method_arm == "baseline_full_depth" else 30,
                "safety_failures": [],
                "content_reproducible": True,
                "platform_audit_summary": "NOT_COLLECTED",
            },
        }

    def test_validator_accepts_complete_content_evidence_without_platform_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            result = run(VALIDATE, str(workspace), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_content_workspace_initializer_creates_isolated_append_only_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            map_root = parent / "industry-map"
            map_root.mkdir()
            contract_path = parent / "content-contract.json"
            write_json(contract_path, self.content_contract())
            created = run(
                INIT_CONTENT_WORKSPACE,
                "--map-root",
                str(map_root),
                "--contract",
                str(contract_path),
            )
            self.assertEqual(created.returncode, 0, created.stderr + created.stdout)
            workspace = map_root / "05-工作区" / "行业语义研究" / "CONTENT-RC2-001"
            for relative in (
                "00-合同/semantic-research-contract.json",
                "01-节点快照",
                "02-校准案例",
                "02-来源真值",
                "03-内容原始回答/baseline_full_depth",
                "03-内容原始回答/candidate_screen_then_expand",
                "04-平台审计",
                "05-证据包",
                "06-反向审计",
                "07-报告/content-scorecards",
                "08-隔离失败返回",
            ):
                self.assertTrue((workspace / relative).exists(), relative)
            second = run(
                INIT_CONTENT_WORKSPACE,
                "--map-root",
                str(map_root),
                "--contract",
                str(contract_path),
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("DESTINATION_EXISTS", second.stderr + second.stdout)

    def test_validator_rejects_missing_or_altered_raw_and_cross_company_visible_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, raw_path = self.make_workspace(Path(tmp))
            raw_path.unlink()
            missing = run(VALIDATE, str(workspace), "--format", "json")
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("RAW_RESPONSE_MISSING", missing.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            workspace, raw_path = self.make_workspace(Path(tmp))
            raw_path.write_text("altered", encoding="utf-8")
            altered = run(VALIDATE, str(workspace), "--format", "json")
            self.assertNotEqual(altered.returncode, 0)
            self.assertIn("RAW_RESPONSE_HASH_MISMATCH", altered.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            envelope_path = workspace / "03-内容原始回答" / "candidate" / "CASE-001.envelope.json"
            envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
            visible = envelope["semantic_content_raw_answer"]["visible_input"]
            visible["company_id"] = "OTHER-COMPANY"
            envelope["semantic_content_raw_answer"]["visible_input_sha256"] = canonical_sha256(visible)
            body = envelope["semantic_content_raw_answer"]
            body["envelope_sha256"] = canonical_sha256({**body, "envelope_sha256": None})
            write_json(envelope_path, envelope)
            contaminated = run(VALIDATE, str(workspace), "--format", "json")
            self.assertNotEqual(contaminated.returncode, 0)
            self.assertIn("CROSS_COMPANY_INPUT_FORBIDDEN", contaminated.stdout)

    def test_validator_rejects_an_empty_source_truth_packet_even_when_its_hash_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            source_path = workspace / "02-来源真值" / "CASE-001.json"
            envelope_path = workspace / "03-内容原始回答" / "candidate" / "CASE-001.envelope.json"
            score_path = workspace / "07-报告" / "content-scorecards" / "CASE-001.json"
            source_path.write_bytes(b"")
            envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
            envelope_body = envelope["semantic_content_raw_answer"]
            envelope_body["source_truth_comparison_sha256"] = hashlib.sha256(
                source_path.read_bytes()
            ).hexdigest()
            envelope_body["envelope_sha256"] = canonical_sha256(
                {**envelope_body, "envelope_sha256": None}
            )
            write_json(envelope_path, envelope)
            scorecard = json.loads(score_path.read_text(encoding="utf-8"))
            score_body = scorecard["semantic_content_scorecard"]
            score_body["raw_answer_sha256"] = hashlib.sha256(envelope_path.read_bytes()).hexdigest()
            score_body["source_truth_comparison_sha256"] = envelope_body[
                "source_truth_comparison_sha256"
            ]
            score_body["scorecard_sha256"] = canonical_sha256(
                {**score_body, "scorecard_sha256": None}
            )
            write_json(score_path, scorecard)
            result = run(VALIDATE, str(workspace), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCE_TRUTH_COMPARISON_EMPTY", result.stdout)

    def test_content_calibration_uses_full_case_evidence_not_platform_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline_path = parent / "baseline.json"
            candidate_path = parent / "candidate.json"
            output_path = parent / "report.json"
            write_json(baseline_path, self.arm("baseline_full_depth"))
            write_json(candidate_path, self.arm("candidate_screen_then_expand"))
            result = run(
                EVALUATE,
                "--baseline",
                str(baseline_path),
                "--candidate",
                str(candidate_path),
                "--output",
                str(output_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["content_method_state"], "CONTENT_CALIBRATION_PASS")
            self.assertNotIn("EFFECTIVE", report["content_method_state"])
            self.assertFalse(report["platform_audit_used_as_content_gate"])

    def test_unified_skill_retains_strict_audit_evaluator_for_legacy_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            fields = {
                "research_contract_id": "STRICT-RC2-001",
                "contract_version": "1.0.0",
                "taxonomy_snapshot_sha256": "a" * 64,
                "calibration_case_set_sha256": "b" * 64,
                "model_profile_id": "rc2-pilot-v1",
                "case_ids": [f"CASE-{index:03d}" for index in range(1, 41)],
                "run_complete": True,
            }
            baseline = {
                **fields,
                "method_arm": "baseline_full_depth",
                "deep_expansion_count": 40,
                "known_positive_count": 14,
            }
            candidate = {
                **fields,
                "method_arm": "candidate_screen_then_expand",
                "deep_expansion_count": 30,
                "known_positive_count": 14,
                "known_positive_entered_expansion": 14,
                "safety_failures": [],
                "reproducible": True,
            }
            baseline_path = parent / "strict-baseline.json"
            candidate_path = parent / "strict-candidate.json"
            output_path = parent / "strict-report.json"
            write_json(baseline_path, baseline)
            write_json(candidate_path, candidate)
            result = run(
                STRICT_EVALUATE,
                "--baseline",
                str(baseline_path),
                "--candidate",
                str(candidate_path),
                "--output",
                str(output_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))["method_validation_state"],
                "EFFECTIVE",
            )

    def test_full_scope_gate_never_defaults_to_authorized(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            contract_path = parent / "contract.json"
            report_path = parent / "calibration.json"
            output_path = parent / "gate.json"
            write_json(contract_path, self.content_contract(authorized=False))
            write_json(
                report_path,
                {
                    "content_method_state": "CONTENT_CALIBRATION_PASS",
                    "research_contract_id": "CONTENT-RC2-001",
                    "contract_version": "1.0.0-content.1",
                    "taxonomy_snapshot_sha256": "a" * 64,
                    "not_beta3_effectiveness": True,
                    "safety_failures": [],
                },
            )
            blocked = run(
                FULL_GATE,
                "--contract",
                str(contract_path),
                "--calibration-report",
                str(report_path),
                "--output",
                str(output_path),
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))["content_full_screening_state"],
                "NOT_AUTHORIZED",
            )

            write_json(contract_path, self.content_contract(authorized=True))
            output_path = parent / "authorized-gate.json"
            allowed = run(
                FULL_GATE,
                "--contract",
                str(contract_path),
                "--calibration-report",
                str(report_path),
                "--output",
                str(output_path),
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr + allowed.stdout)
            gate = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(gate["content_full_screening_state"], "AUTHORIZED_NOT_STARTED")
            self.assertEqual(gate["downstream_release_state"], "RESEARCH_ONLY_BLOCKED")

    def test_full_coverage_requires_every_frozen_node_and_stays_research_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            manifest_path = parent / "terminal-nodes.json"
            index_path = parent / "screening-index.json"
            contract_path = parent / "contract.json"
            output_path = parent / "coverage.json"
            manifest = {"terminal_node_ids": ["NODE-001", "NODE-002"]}
            write_json(manifest_path, manifest)
            contract = self.content_contract(authorized=True)
            body = contract["semantic_research_contract"]
            body["terminal_node_count"] = 2
            body["terminal_node_manifest_reference"] = str(manifest_path)
            body["terminal_node_manifest_sha256"] = hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest()
            body["content_first_policy"]["content_full_screening_state"] = "IN_PROGRESS"
            write_json(contract_path, contract)

            def index(node_ids: list[str]) -> dict:
                return {
                    "semantic_content_full_screening_index": {
                        "research_contract_id": "CONTENT-RC2-001",
                        "contract_version": "1.0.0-content.1",
                        "terminal_node_manifest_sha256": body["terminal_node_manifest_sha256"],
                        "method_arm": "candidate_screen_then_expand",
                        "node_evidence": [
                            {
                                "industry_node_id": node_id,
                                "visible_input_sha256": "a" * 64,
                                "raw_response_sha256": "b" * 64,
                                "scorecard_sha256": "c" * 64,
                                "screening_result": "no_hypothesis_formed",
                                "semantic_work_state": "screened",
                                "evidence_state": "unknown",
                                "unknown_items_present": True,
                            }
                            for node_id in node_ids
                        ],
                    }
                }

            write_json(index_path, index(["NODE-001"]))
            incomplete = run(
                FULL_COVERAGE,
                "--contract",
                str(contract_path),
                "--terminal-node-manifest",
                str(manifest_path),
                "--screening-index",
                str(index_path),
                "--output",
                str(output_path),
            )
            self.assertNotEqual(incomplete.returncode, 0)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))["content_full_screening_state"],
                "COVERAGE_INCOMPLETE",
            )
            write_json(index_path, index(["NODE-001", "NODE-002"]))
            output_path = parent / "coverage-ready.json"
            complete = run(
                FULL_COVERAGE,
                "--contract",
                str(contract_path),
                "--terminal-node-manifest",
                str(manifest_path),
                "--screening-index",
                str(index_path),
                "--output",
                str(output_path),
            )
            self.assertEqual(complete.returncode, 0, complete.stderr + complete.stdout)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["content_full_screening_state"], "READY_FOR_REVERSE_AUDIT")
            self.assertTrue(report["requires_content_workspace_validation"])
            self.assertEqual(report["downstream_release_state"], "RESEARCH_ONLY_BLOCKED")


if __name__ == "__main__":
    unittest.main()
