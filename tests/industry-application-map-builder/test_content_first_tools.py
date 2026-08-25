from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = (
    ROOT
    / "plugins"
    / "industry-application-map-builder"
    / "skills"
    / "industry-application-map-builder"
)
VALIDATE = SKILL_ROOT / "scripts" / "validate_content_first_workspace.py"
REGISTER_SOURCE_SNAPSHOT = SKILL_ROOT / "scripts" / "register_content_source_snapshot.py"
EVALUATE = SKILL_ROOT / "scripts" / "evaluate_content_first_calibration.py"
FREEZE_STABILITY = SKILL_ROOT / "scripts" / "freeze_content_first_stability_tasks.py"
ARM_TEMPLATE = SKILL_ROOT / "assets" / "content-first" / "content-calibration-arm.template.json"
FULL_GATE = SKILL_ROOT / "scripts" / "check_content_first_full_screening_gate.py"
INIT_CONTENT_WORKSPACE = SKILL_ROOT / "scripts" / "init_content_first_workspace.py"
STRICT_EVALUATE = SKILL_ROOT / "scripts" / "evaluate_semantic_calibration.py"
FULL_COVERAGE = SKILL_ROOT / "scripts" / "validate_content_first_full_coverage.py"
R4_SCORE_ITEMS = {
    "taxonomy_and_scope_grounding": ("taxonomy_truth_reviewer", True),
    "semantic_decision_correctness": ("semantic_truth_reviewer", True),
    "source_retrieval_equivalence": ("source_equivalence_reviewer", True),
    "receiver_evidence_integrity": ("receiver_evidence_reviewer", True),
    "safety_boundary": ("safety_boundary_reviewer", True),
    "unknown_and_challenge_handling": ("challenge_and_unknown_reviewer", False),
}
R4_EQUIVALENCE_DIMENSIONS = {
    "taxonomy_membership": "taxonomy_membership_basis",
    "output_or_use_point": "output_or_subprocess_basis",
    "mechanism": "mechanism_basis",
    "conditions": "conditions",
    "boundary": "truth_boundary",
}


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
    def content_contract(self, authorized: bool = False, r4_methods: bool = False) -> dict:
        payload = {
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
                    "truth_scorecard_contract_version": (
                        "2.0-r4" if r4_methods else "1.0-legacy"
                    ),
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
        if r4_methods:
            body = payload["semantic_research_contract"]
            body["baseline_method_contract"] = "baseline_full_depth_v1"
            body["candidate_method_contract"] = "screen_then_expand_v2"
        return payload

    def full_gate_fixture(self, parent: Path) -> tuple[dict[str, Path], list[str]]:
        workspace = parent / "full-gate-workspace"
        workspace.mkdir()
        manifest_path = workspace / "01-节点快照" / "terminal-node-manifest.json"
        manifest = {
            "manifest_type": "content_first_terminal_node_manifest",
            "research_contract_id": "CONTENT-RC2-001",
            "schema_version": "1.0",
            "taxonomy_snapshot_reference": "01-节点快照/taxonomy-snapshot.json",
            "taxonomy_snapshot_sha256": "a" * 64,
            "terminal_node_count": 2,
            "terminal_node_ids": ["GB-T-4754-NODE-001", "GB-T-4754-NODE-002"],
        }
        write_json(manifest_path, manifest)
        manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        contract_path = workspace / "00-合同" / "final-contract.json"
        contract = {
            "schema_version": "1.2",
            "semantic_research_contract": {
                "research_contract_id": "CONTENT-RC2-001",
                "contract_version": "2.1.0-content-first.final.1",
                "contract_state": "frozen",
                "execution_mode": "content_first",
                "taxonomy_snapshot_sha256": "a" * 64,
                "terminal_node_count": 2,
                "terminal_node_manifest_reference": manifest_path.relative_to(
                    workspace
                ).as_posix(),
                "terminal_node_manifest_sha256": manifest_hash,
                "baseline_method_contract": "baseline_full_depth_v1",
                "candidate_method_contract": "screen_then_expand_v2",
                "retrieval_efficiency_gates": {
                    "minimum_deep_expansion_reduction": 0.2,
                    "maximum_query_count_increase": 0.1,
                    "maximum_source_open_count_increase": 0.0,
                    "stability_repeat_case_count": 6,
                },
                "full_screening_authorization": False,
                "full_screening_authorization_reference": None,
                "content_first_policy": {
                    "truth_scorecard_contract_version": "2.0-r4",
                    "platform_audit_required_for_content_pass": False,
                    "content_method_state": "CONTENT_CALIBRATION_INCOMPLETE",
                    "content_full_screening_state": "NOT_AUTHORIZED",
                    "downstream_release_state": "RESEARCH_ONLY_BLOCKED",
                },
            },
        }
        write_json(contract_path, contract)
        contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
        report_path = workspace / "07-报告" / "r4-evaluation.json"
        report = {
            "schema_version": "2.0-r4",
            "evaluation_result": "PASS",
            "content_method_state": "CONTENT_CALIBRATION_PASS",
            "gate_order": [
                "safety",
                "known_positive_recall",
                "receiver_evidence_completeness",
                "stability",
                "efficiency",
            ],
            "critical_content_rules_applied_before_efficiency": True,
            "platform_audit_used_as_content_gate": False,
            "not_beta3_effectiveness": True,
            "research_contract_id": "CONTENT-RC2-001",
            "contract_version": "2.1.0-content-first.final.1",
            "final_contract_sha256": contract_hash,
            "paired_task_manifest_sha256": "b" * 64,
            "case_count": 40,
            "stability_repeat_count": 6,
            "efficiency_gate_state": "PASS",
            "baseline_query_count": 100,
            "candidate_query_count": 110,
            "baseline_source_open_count": 80,
            "candidate_source_open_count": 80,
            "baseline_deep_expansion_count": 40,
            "candidate_deep_expansion_count": 32,
            "deep_expansion_reduction": 0.2,
            "minimum_required_reduction": 0.2,
            "maximum_allowed_query_count_increase": 0.1,
            "maximum_allowed_source_open_count_increase": 0.0,
            "safety_failures": [],
            "downstream_authorized": False,
            "reasons": [],
        }
        write_json(report_path, report)
        report_hash = hashlib.sha256(report_path.read_bytes()).hexdigest()
        receipt_path = workspace / "00-合同" / "full-screen-authorization.receipt.json"
        receipt = {
            "authorization_receipt_id": "FULL-SCREEN-AUTH-001",
            "research_contract_id": "CONTENT-RC2-001",
            "contract_version": "2.1.0-content-first.final.1",
            "user_authorization_reference": "USER-FULL-SCREEN-20260825-001",
            "authorized_at": "2026-08-25T12:00:00+08:00",
            "final_contract_reference": contract_path.relative_to(workspace).as_posix(),
            "final_contract_sha256": contract_hash,
            "calibration_report_reference": report_path.relative_to(workspace).as_posix(),
            "calibration_report_sha256": report_hash,
            "terminal_node_manifest_reference": manifest_path.relative_to(workspace).as_posix(),
            "terminal_node_manifest_sha256": manifest_hash,
            "authorization_scope": "content_first_full_screening_research_only",
            "runs_nodes": False,
            "downstream_release_state": "RESEARCH_ONLY_BLOCKED",
            "receipt_sha256": None,
        }
        receipt["receipt_sha256"] = canonical_sha256(
            {**receipt, "receipt_sha256": None}
        )
        write_json(
            receipt_path,
            {
                "schema_version": "1.0",
                "content_first_full_screening_authorization_receipt": receipt,
            },
        )
        paths = {
            "workspace": workspace,
            "contract": contract_path,
            "report": report_path,
            "manifest": manifest_path,
            "receipt": receipt_path,
        }
        args = [
            "--workspace", str(workspace),
            "--contract", str(contract_path),
            "--expected-final-contract-sha256", contract_hash,
            "--calibration-report", str(report_path),
            "--expected-calibration-report-sha256", report_hash,
            "--terminal-node-manifest", str(manifest_path),
            "--expected-terminal-node-manifest-sha256", manifest_hash,
            "--authorization-receipt", str(receipt_path),
            "--expected-authorization-receipt-sha256", hashlib.sha256(
                receipt_path.read_bytes()
            ).hexdigest(),
        ]
        return paths, args

    def source_observation(self, **overrides: object) -> dict:
        observation = {
            "source_url_or_null": "https://example.invalid/source",
            "publisher_or_null": "Example",
            "title_or_null": "Title",
            "original_location_or_null": "section 1",
            "bounded_summary_or_null": "bounded",
            "access_state": "OBSERVED",
            "conditions": [],
            "limitations": [],
            "counterevidence": [],
        }
        observation.update(overrides)
        return observation

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
                "source_observations": [],
                "source_snapshot_receipt_references": [],
                "source_truth_comparison_reference": str(source_path.relative_to(workspace)),
                "source_truth_comparison_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                "unknown_items": ["not measured"],
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

    def make_r4_workspace(self, parent: Path) -> tuple[Path, Path]:
        workspace, raw_path = self.make_workspace(parent)
        envelope_path = workspace / "03-内容原始回答" / "candidate" / "CASE-001.envelope.json"
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        envelope_body = envelope["semantic_content_raw_answer"]
        envelope_body["method_arm"] = "screen_then_expand_v2"

        receipt_references: list[str] = []
        observations: list[dict] = []
        roles = ("TAXONOMY", "OUTPUT", "MECHANISM")
        for index, role in enumerate(roles):
            observation_id = f"OBS-R4-{role}"
            receipt_reference = (
                f"05-证据包/source-snapshot-receipts/{observation_id}.receipt.json"
            )
            snapshot_reference = (
                f"05-证据包/receiver-source-snapshots/{observation_id}.snapshot"
            )
            snapshot_path = workspace / snapshot_reference
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_bytes(f"verified receiver evidence {role}\n".encode("utf-8"))
            observation_reference = (
                f"{envelope_path.relative_to(workspace).as_posix()}"
                f"#/semantic_content_raw_answer/source_observations/{index}"
            )
            receipt_body = {
                "receipt_id": f"SNAPSHOT-{observation_id}",
                "observation_id": observation_id,
                "source_observation_reference": observation_reference,
                "receiver_snapshot_reference": snapshot_reference,
                "receiver_snapshot_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
                "snapshot_capture_state": "captured",
                "snapshot_captured_at": "2026-08-25T09:30:00+08:00",
                "receipt_sha256": None,
            }
            receipt_body["receipt_sha256"] = canonical_sha256(
                {**receipt_body, "receipt_sha256": None}
            )
            write_json(
                workspace / receipt_reference,
                {
                    "schema_version": "1.0",
                    "content_source_snapshot_receipt": receipt_body,
                },
            )
            receipt_references.append(receipt_reference)
            observations.append(
                self.source_observation(
                    source_url_or_null=f"https://example.invalid/{role.lower()}",
                    title_or_null=f"{role.title()} evidence",
                )
            )
        envelope_body["source_observations"] = observations
        envelope_body["source_snapshot_receipt_references"] = receipt_references

        truth_source_references: list[dict[str, str]] = []
        for role in roles:
            truth_source_reference = (
                f"02-来源真值/truth-source-snapshots/CASE-001.{role.lower()}.source"
            )
            truth_source_path = workspace / truth_source_reference
            truth_source_path.parent.mkdir(parents=True, exist_ok=True)
            truth_source_path.write_bytes(
                f"independently frozen truth source {role}\n".encode("utf-8")
            )
            truth_source_references.append(
                {
                    "reference": truth_source_reference,
                    "sha256": hashlib.sha256(truth_source_path.read_bytes()).hexdigest(),
                }
            )

        truth_path = workspace / "02-来源真值" / "CASE-001.json"
        truth_reference = truth_path.relative_to(workspace).as_posix()
        truth_body = {
            "truth_id": "TRUTH-CASE-001",
            "research_contract_id": "CONTENT-RC2-001",
            "contract_version": "1.0.0-content.1",
            "case_id": "CASE-001",
            "taxonomy_membership_basis": {
                "basis_text": "The official activity definition includes the case activity.",
                "source_references": [truth_source_references[0]],
            },
            "output_or_subprocess_basis": {
                "basis_text": "The activity produces or performs the stated output or subprocess.",
                "source_references": [truth_source_references[1]],
            },
            "mechanism_basis": {
                "basis_text": "The documented mechanism connects that output or subprocess to the use point.",
                "source_references": [truth_source_references[2]],
            },
            "expected_semantic_axes": {
                "screening_result": "hypothesis_formed",
                "semantic_work_state": "evidence_expansion_required",
                "evidence_state": "hypothesis",
            },
            "conditions": ["Only within the stated activity boundary."],
            "limitations": ["No company or product fit is established."],
            "unknowns": ["Operating details remain unknown."],
            "truth_boundary": "Product-neutral research only; no downstream conclusion.",
            "counts_toward_known_positive_recall": True,
            "truth_sha256": None,
        }
        truth_body["truth_sha256"] = canonical_sha256(
            {**truth_body, "truth_sha256": None}
        )
        write_json(
            truth_path,
            {"schema_version": "1.0", "semantic_content_case_truth": truth_body},
        )
        envelope_body["source_truth_comparison_reference"] = truth_reference
        envelope_body["source_truth_comparison_sha256"] = hashlib.sha256(
            truth_path.read_bytes()
        ).hexdigest()
        envelope_body["envelope_sha256"] = canonical_sha256(
            {**envelope_body, "envelope_sha256": None}
        )
        write_json(envelope_path, envelope)

        score_path = workspace / "07-报告" / "content-scorecards" / "CASE-001.json"
        truth_pointer_refs = {
            dimension: f"{truth_reference}#/semantic_content_case_truth/{truth_field}"
            for dimension, truth_field in R4_EQUIVALENCE_DIMENSIONS.items()
        }
        score_evidence_refs = {
            "taxonomy_and_scope_grounding": [truth_pointer_refs["taxonomy_membership"]],
            "semantic_decision_correctness": [
                f"{truth_reference}#/semantic_content_case_truth/expected_semantic_axes"
            ],
            "source_retrieval_equivalence": [
                f"{envelope_path.relative_to(workspace).as_posix()}"
                "#/semantic_content_raw_answer/source_observations"
            ],
            "receiver_evidence_integrity": [receipt_references[0]],
            "safety_boundary": [truth_pointer_refs["boundary"]],
            "unknown_and_challenge_handling": [
                f"{truth_reference}#/semantic_content_case_truth/unknowns"
            ],
        }
        score_body = {
            "scorecard_id": "SCORE-CASE-001-CANDIDATE",
            "raw_answer_reference": envelope_path.relative_to(workspace).as_posix(),
            "raw_answer_sha256": hashlib.sha256(envelope_path.read_bytes()).hexdigest(),
            "subject": {"kind": "calibration_case", "id": "CASE-001"},
            "method_arm": "screen_then_expand_v2",
            "visible_input_sha256": envelope_body["visible_input_sha256"],
            "source_truth_comparison_reference": truth_reference,
            "source_truth_comparison_sha256": envelope_body[
                "source_truth_comparison_sha256"
            ],
            "scoring_rubric_version": "2.0-r4",
            "scoring_items": {
                name: {
                    "responsibility": responsibility,
                    "critical": critical,
                    "score": 2,
                    "reason": f"{name} checked against its owned evidence.",
                    "evidence_references": score_evidence_refs[name],
                }
                for name, (responsibility, critical) in R4_SCORE_ITEMS.items()
            },
            "equivalent_source_dimensions": {
                dimension: {
                    "result": "PASS",
                    "reason": f"Equivalent {dimension} meaning was established.",
                    "truth_evidence_references": [truth_pointer_refs[dimension]],
                    "receiver_evidence_references": [receipt_references[index % 3]],
                }
                for index, dimension in enumerate(R4_EQUIVALENCE_DIMENSIONS)
            },
            "equivalent_source_result": "PASS",
            "unknown_items": ["not measured"],
            "content_score_result": "PASS",
            "platform_audit_state": "NOT_COLLECTED",
            "platform_audit_reference_or_null": None,
            "scorecard_sha256": None,
        }
        score_body["scorecard_sha256"] = canonical_sha256(
            {**score_body, "scorecard_sha256": None}
        )
        write_json(
            score_path,
            {"schema_version": "1.0", "semantic_content_scorecard": score_body},
        )
        write_json(
            workspace / "00-合同" / "semantic-research-contract.json",
            self.content_contract(r4_methods=True),
        )
        return workspace, raw_path

    def rewrite_r4_truth_and_bind(self, workspace: Path, mutate) -> None:
        truth_path = workspace / "02-来源真值" / "CASE-001.json"
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        truth_body = truth["semantic_content_case_truth"]
        mutate(truth_body)
        truth_body["truth_sha256"] = canonical_sha256(
            {**truth_body, "truth_sha256": None}
        )
        write_json(truth_path, truth)

        envelope_path = workspace / "03-内容原始回答/candidate/CASE-001.envelope.json"
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        envelope_body = envelope["semantic_content_raw_answer"]
        envelope_body["source_truth_comparison_sha256"] = hashlib.sha256(
            truth_path.read_bytes()
        ).hexdigest()
        envelope_body["envelope_sha256"] = canonical_sha256(
            {**envelope_body, "envelope_sha256": None}
        )
        write_json(envelope_path, envelope)

        score_path = workspace / "07-报告/content-scorecards/CASE-001.json"
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

    def rewrite_r4_scorecard(self, workspace: Path, mutate) -> None:
        score_path = workspace / "07-报告/content-scorecards/CASE-001.json"
        scorecard = json.loads(score_path.read_text(encoding="utf-8"))
        score_body = scorecard["semantic_content_scorecard"]
        mutate(score_body)
        score_body["scorecard_sha256"] = canonical_sha256(
            {**score_body, "scorecard_sha256": None}
        )
        write_json(score_path, scorecard)

    def register_snapshot(
        self,
        workspace: Path,
        source_file: Path,
        observation_id: str,
        source_observation_reference: str,
        *extra: str,
    ) -> subprocess.CompletedProcess[str]:
        return run(
            REGISTER_SOURCE_SNAPSHOT,
            "--workspace",
            str(workspace),
            "--source-file",
            str(source_file),
            "--observation-id",
            observation_id,
            "--source-observation-reference",
            source_observation_reference,
            "--captured-at",
            "2026-08-25T09:30:00+08:00",
            *extra,
        )

    def attach_source_observation_and_receipt(
        self,
        workspace: Path,
        observation: dict,
        receipt_reference: str,
    ) -> Path:
        envelope_path = workspace / "03-内容原始回答" / "candidate" / "CASE-001.envelope.json"
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        body = envelope["semantic_content_raw_answer"]
        body["source_observations"] = [observation]
        body["source_snapshot_receipt_references"] = [receipt_reference]
        body["envelope_sha256"] = canonical_sha256({**body, "envelope_sha256": None})
        write_json(envelope_path, envelope)
        score_path = workspace / "07-报告" / "content-scorecards" / "CASE-001.json"
        scorecard = json.loads(score_path.read_text(encoding="utf-8"))
        score_body = scorecard["semantic_content_scorecard"]
        score_body["raw_answer_sha256"] = hashlib.sha256(envelope_path.read_bytes()).hexdigest()
        score_body["scorecard_sha256"] = canonical_sha256(
            {**score_body, "scorecard_sha256": None}
        )
        write_json(score_path, scorecard)
        return envelope_path

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
                "calibration_contract_marker": "1.0-legacy",
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

    def r4_arm(
        self,
        method_arm: str,
        *,
        deep: int,
        queries: int,
        opens: int,
    ) -> dict:
        case_ids = [f"CASE-{index:03d}" for index in range(1, 41)]
        query_parts = [queries // 40 + (1 if index < queries % 40 else 0) for index in range(40)]
        open_parts = [opens // 40 + (1 if index < opens % 40 else 0) for index in range(40)]
        deep_parts = [1 if index < deep else 0 for index in range(40)]
        critical = {
            "taxonomy_and_scope_grounding": "PASS",
            "semantic_decision_correctness": "PASS",
            "source_retrieval_equivalence": "PASS",
            "receiver_evidence_integrity": "PASS",
            "safety_boundary": "PASS",
        }
        rows = []
        for index, case_id in enumerate(case_ids, start=1):
            task_id = f"{case_id}--{method_arm}"
            observation = {
                "observation_id": f"RESOURCE-{method_arm}-{case_id}",
                "case_id": case_id,
                "task_id": task_id,
                "method_arm": method_arm,
                "query_count": query_parts[index - 1],
                "source_open_count": open_parts[index - 1],
                "deep_expansion_count": deep_parts[index - 1],
                "observation_sha256": None,
            }
            observation["observation_sha256"] = canonical_sha256(
                {**observation, "observation_sha256": None}
            )
            rows.append(
                {
                    "case_id": case_id,
                    "visible_input_sha256": f"{index + 200:064x}",
                    "task_id": task_id,
                    "task_sha256": f"{index + (1000 if method_arm == 'baseline_full_depth_v1' else 2000):064x}",
                    "paired_task_manifest_sha256": "d" * 64,
                    "raw_response_sha256": f"{index + 3000:064x}",
                    "scorecard_sha256": f"{index + (4000 if method_arm == 'baseline_full_depth_v1' else 5000):064x}",
                    "content_score_result": "PASS",
                    "unknown_items_present": True,
                    "critical_dispositions": dict(critical),
                    "resource_observation": observation,
                }
            )
        return {
            "schema_version": "2.0-r4",
            "semantic_content_calibration_arm": {
                "calibration_contract_marker": "2.0-r4",
                "research_contract_id": "CONTENT-RC2-001",
                "contract_version": "2.1.0-content-first.final.1",
                "taxonomy_snapshot_sha256": "a" * 64,
                "calibration_case_set_sha256": "b" * 64,
                "source_truth_package_sha256": "c" * 64,
                "paired_task_manifest_sha256": "d" * 64,
                "method_arm": method_arm,
                "run_complete": True,
                "case_evidence": rows,
                "known_positive_case_ids": case_ids[:14],
                "known_positive_entered_expansion_case_ids": case_ids[:14],
                "query_count": queries,
                "source_open_count": opens,
                "deep_expansion_count": deep,
                "safety_failures": [],
                "content_reproducible": True,
                "stability_repeat_input_sha256": "e" * 64,
                "stability_repeat_receipts": [],
                "platform_audit_summary": "NOT_COLLECTED",
            },
        }

    def write_r4_repeat_receipts(self, parent: Path, candidate: dict) -> None:
        body = candidate["semantic_content_calibration_arm"]
        cases = body["case_evidence"]
        references = []
        for repeat_index in range(1, 7):
            receipt_body = {
                "receipt_id": f"R4-STABILITY-{repeat_index:02d}",
                "research_contract_id": body["research_contract_id"],
                "contract_version": body["contract_version"],
                "calibration_case_set_sha256": body["calibration_case_set_sha256"],
                "paired_task_manifest_sha256": body["paired_task_manifest_sha256"],
                "method_arm": body["method_arm"],
                "repeat_input_sha256": body["stability_repeat_input_sha256"],
                "repeat_unit": {
                    "kind": "complete_40_case_arm",
                    "case_count": 40,
                    "case_ids": [row["case_id"] for row in cases],
                },
                "critical_dispositions_by_case": [
                    {
                        "case_id": row["case_id"],
                        "critical_dispositions": row["critical_dispositions"],
                    }
                    for row in cases
                ],
                "receipt_sha256": None,
            }
            receipt_body["receipt_sha256"] = canonical_sha256(
                {**receipt_body, "receipt_sha256": None}
            )
            path = parent / "stability" / f"repeat-{repeat_index:02d}.json"
            write_json(
                path,
                {"schema_version": "1.0", "stability_repeat_receipt": receipt_body},
            )
            references.append(
                {
                    "reference": path.relative_to(parent).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
        body["stability_repeat_receipts"] = references

    def evaluate_r4(
        self,
        parent: Path,
        baseline: dict,
        candidate: dict,
        output_name: str = "report.json",
        *extra: str,
    ) -> tuple[subprocess.CompletedProcess[str], Path]:
        baseline_path = parent / "baseline.json"
        candidate_path = parent / "candidate.json"
        output_path = parent / output_name
        write_json(baseline_path, baseline)
        write_json(candidate_path, candidate)
        return (
            run(
                EVALUATE,
                "--baseline",
                str(baseline_path),
                "--candidate",
                str(candidate_path),
                "--output",
                str(output_path),
                *extra,
            ),
            output_path,
        )

    def real_r4_evaluation_fixture(
        self,
        parent: Path,
        *,
        candidate_deep: int = 32,
        baseline_queries: int = 100,
        candidate_queries: int = 110,
        baseline_opens: int = 80,
        candidate_opens: int = 80,
        include_repeats: bool = True,
        repeat_context_collision: bool = False,
    ) -> tuple[dict, dict, list[str], dict[str, Path]]:
        workspace = parent / "workspace"
        workspace.mkdir()
        case_ids = [f"CASE-{index:03d}" for index in range(1, 41)]
        repeat_case_ids = case_ids[:6]
        case_rows = [
            {
                "record_type": "case_set_contract",
                "formal_case_ids": case_ids,
                "stability_repeat_case_ids": repeat_case_ids,
            },
            *[
                {
                    "record_type": "calibration_case",
                    "case_id": case_id,
                }
                for case_id in case_ids
            ],
        ]
        truth_rows = [
            {
                "record_type": "source_truth",
                "case_id": case_id,
                "known_positive": index <= 14,
            }
            for index, case_id in enumerate(case_ids, 1)
        ]
        case_path = workspace / "frozen" / "cases.jsonl"
        truth_path = workspace / "frozen" / "source-truth.jsonl"
        case_path.parent.mkdir(parents=True)
        case_path.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in case_rows),
            encoding="utf-8",
        )
        truth_path.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in truth_rows),
            encoding="utf-8",
        )
        contract = {
            "schema_version": "1.2",
            "semantic_research_contract": {
                "research_contract_id": "CONTENT-RC2-001",
                "contract_version": "2.1.0-content-first.final.1",
                "contract_state": "frozen",
                "execution_mode": "content_first",
                "taxonomy_snapshot_sha256": "a" * 64,
                "baseline_method_contract": "baseline_full_depth_v1",
                "candidate_method_contract": "screen_then_expand_v2",
                "content_first_policy": {
                    "truth_scorecard_contract_version": "2.0-r4"
                },
                "retrieval_efficiency_gates": {
                    "minimum_deep_expansion_reduction": 0.2,
                    "maximum_query_count_increase": 0.1,
                    "maximum_source_open_count_increase": 0.0,
                    "stability_repeat_case_count": 6,
                },
                "calibration_case_set_reference_and_hash": {
                    "reference": case_path.relative_to(workspace).as_posix(),
                    "sha256": hashlib.sha256(case_path.read_bytes()).hexdigest(),
                },
                "source_truth_package_reference": truth_path.relative_to(workspace).as_posix(),
                "source_truth_package_sha256": hashlib.sha256(truth_path.read_bytes()).hexdigest(),
            },
        }
        contract_path = workspace / "frozen" / "final-contract.json"
        write_json(contract_path, contract)
        contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
        contract_body = contract["semantic_research_contract"]

        task_root = workspace / "paired-tasks"
        pairs = []
        task_info: dict[tuple[str, str], dict[str, str]] = {}
        for index, case_id in enumerate(case_ids, 1):
            visible_input = {
                "case_id": case_id,
                "taxonomy_node": {"taxonomy_node_id": f"NODE-{index:03d}"},
                "product_neutral_research_theme": "fixture neutral theme",
                "risk_flags": [],
            }
            visible_hash = canonical_sha256(visible_input)
            task_files = {}
            for arm in ("baseline_full_depth_v1", "screen_then_expand_v2"):
                task = {
                    "schema_version": "1.0",
                    "content_first_calibration_task": {
                        "task_id": f"{case_id}--{arm}",
                        "research_contract_id": contract_body["research_contract_id"],
                        "contract_version": contract_body["contract_version"],
                        "method_arm": arm,
                        "execution_authorized": False,
                        "visible_input": visible_input,
                        "visible_input_sha256": visible_hash,
                    },
                }
                task_path = task_root / arm / f"{case_id}.task.json"
                write_json(task_path, task)
                relative = task_path.relative_to(task_root).as_posix()
                task_hash = hashlib.sha256(task_path.read_bytes()).hexdigest()
                task_files[arm] = {"path": relative, "task_file_sha256": task_hash}
                task_info[(case_id, arm)] = {
                    "reference": task_path.relative_to(workspace).as_posix(),
                    "sha256": task_hash,
                    "task_id": task["content_first_calibration_task"]["task_id"],
                    "visible_input_sha256": visible_hash,
                }
            pairs.append(
                {
                    "case_id": case_id,
                    "visible_input_sha256": visible_hash,
                    "task_files": task_files,
                }
            )
        manifest = {
            "schema_version": "1.0",
            "content_first_paired_task_manifest": {
                "research_contract_id": contract_body["research_contract_id"],
                "contract_version": contract_body["contract_version"],
                "final_contract_sha256": contract_hash,
                "formal_case_set_sha256": contract_body[
                    "calibration_case_set_reference_and_hash"
                ]["sha256"],
                "pair_count": 40,
                "task_count": 80,
                "execution_authorized": False,
                "pairs": pairs,
            },
        }
        manifest_path = task_root / "paired-task-manifest.json"
        write_json(manifest_path, manifest)
        manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

        def parts(total: int) -> list[int]:
            return [
                total // 40 + (1 if index < total % 40 else 0)
                for index in range(40)
            ]

        metric_parts = {
            "baseline_full_depth_v1": (
                parts(baseline_queries),
                parts(baseline_opens),
                [1] * 40,
            ),
            "screen_then_expand_v2": (
                parts(candidate_queries),
                parts(candidate_opens),
                [1 if index < candidate_deep else 0 for index in range(40)],
            ),
        }

        def make_run(
            case_id: str,
            arm: str,
            task_reference: str,
            task_hash: str,
            visible_hash: str,
            query_count: int,
            open_count: int,
            deep: int,
            root_reference: str,
            preauthorization_reference: str | None = None,
            preauthorization_sha256: str | None = None,
        ) -> dict[str, object]:
            run_root = workspace / root_reference
            task_payload = json.loads((workspace / task_reference).read_text(encoding="utf-8"))
            task_body = task_payload.get("content_first_calibration_task")
            if not isinstance(task_body, dict):
                repeat_body = task_payload["content_first_stability_repeat_task"]
                original_task = json.loads(
                    (
                        workspace / repeat_body["original_candidate_task_reference"]
                    ).read_text(encoding="utf-8")
                )
                task_body = original_task["content_first_calibration_task"]
            visible_input = task_body["visible_input"]
            raw_path = run_root / "raw-response.json"
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(b'{"answer":"byte-identical output is allowed"}\n')
            raw_ref = raw_path.relative_to(workspace).as_posix()
            raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

            snapshot_receipts: list[str] = []
            for source_index in range(open_count):
                snapshot_path = run_root / "snapshots" / f"source-{source_index:03d}.snapshot"
                snapshot_path.parent.mkdir(parents=True, exist_ok=True)
                snapshot_path.write_bytes(b"identical receiver snapshot bytes\n")
                snapshot_ref = snapshot_path.relative_to(workspace).as_posix()
                snapshot_receipt_path = (
                    run_root / "snapshot-receipts" / f"source-{source_index:03d}.receipt.json"
                )
                snapshot_receipt_ref = snapshot_receipt_path.relative_to(workspace).as_posix()
                snapshot_receipt_body = {
                    "receipt_id": f"SNAP-{root_reference}-{source_index}",
                    "observation_id": f"OBS-{root_reference}-{source_index}",
                    "source_observation_reference": f"{root_reference}/raw-envelope.json#/semantic_content_raw_answer/source_observations/0",
                    "receiver_snapshot_reference": snapshot_ref,
                    "receiver_snapshot_sha256": hashlib.sha256(
                        snapshot_path.read_bytes()
                    ).hexdigest(),
                    "snapshot_capture_state": "captured",
                    "snapshot_captured_at": "2026-08-25T09:30:00+08:00",
                    "receipt_sha256": None,
                }
                snapshot_receipt_body["receipt_sha256"] = canonical_sha256(
                    {**snapshot_receipt_body, "receipt_sha256": None}
                )
                write_json(
                    snapshot_receipt_path,
                    {
                        "schema_version": "1.0",
                        "content_source_snapshot_receipt": snapshot_receipt_body,
                    },
                )
                snapshot_receipts.append(snapshot_receipt_ref)

            truth_source_references = []
            for truth_index, label in enumerate(("taxonomy", "output", "mechanism"), 1):
                truth_source_path = run_root / "truth-sources" / f"{label}.txt"
                truth_source_path.parent.mkdir(parents=True, exist_ok=True)
                truth_source_path.write_text(
                    f"{label} source for {root_reference} {truth_index}\n",
                    encoding="utf-8",
                )
                truth_source_references.append(
                    {
                        "reference": truth_source_path.relative_to(workspace).as_posix(),
                        "sha256": hashlib.sha256(truth_source_path.read_bytes()).hexdigest(),
                    }
                )
            truth_case_path = run_root / "case-truth.json"
            truth_case_ref = truth_case_path.relative_to(workspace).as_posix()
            truth_case = {
                "truth_id": f"TRUTH-{root_reference}",
                "research_contract_id": contract_body["research_contract_id"],
                "contract_version": contract_body["contract_version"],
                "case_id": case_id,
                "taxonomy_membership_basis": {
                    "basis_text": "fixture taxonomy basis",
                    "source_references": [truth_source_references[0]],
                },
                "output_or_subprocess_basis": {
                    "basis_text": "fixture output basis",
                    "source_references": [truth_source_references[1]],
                },
                "mechanism_basis": {
                    "basis_text": "fixture mechanism basis",
                    "source_references": [truth_source_references[2]],
                },
                "expected_semantic_axes": {
                    "screening_result": "hypothesis_formed",
                    "semantic_work_state": "evidence_expanded",
                    "evidence_state": "supported",
                },
                "conditions": ["fixture condition"],
                "limitations": ["fixture limitation"],
                "unknowns": ["fixture unknown"],
                "truth_boundary": "fixture boundary",
                "counts_toward_known_positive_recall": case_id in case_ids[:14],
                "truth_sha256": None,
            }
            truth_case["truth_sha256"] = canonical_sha256(
                {**truth_case, "truth_sha256": None}
            )
            write_json(
                truth_case_path,
                {"schema_version": "1.0", "semantic_content_case_truth": truth_case},
            )
            truth_case_hash = hashlib.sha256(truth_case_path.read_bytes()).hexdigest()

            envelope_path = run_root / "raw-envelope.json"
            envelope_ref = envelope_path.relative_to(workspace).as_posix()
            envelope_body = {
                "raw_answer_id": f"RAW-{root_reference}",
                "research_contract_id": contract_body["research_contract_id"],
                "contract_version": contract_body["contract_version"],
                "subject": {"kind": "calibration_case", "id": case_id},
                "method_arm": arm,
                "visible_input": visible_input,
                "visible_input_sha256": visible_hash,
                "raw_response_reference": raw_ref,
                "raw_response_sha256": raw_hash,
                "raw_response_format": "application/json",
                "source_observations": [
                    {"observation_id": f"OBS-{root_reference}-{index}"}
                    for index in range(len(snapshot_receipts))
                ],
                "source_snapshot_receipt_references": snapshot_receipts,
                "source_truth_comparison_reference": truth_case_ref,
                "source_truth_comparison_sha256": truth_case_hash,
                "unknown_items": ["fixture unknown"],
                "platform_audit_state": "NOT_COLLECTED",
                "platform_audit_reference_or_null": None,
                "envelope_sha256": None,
            }
            envelope_body["envelope_sha256"] = canonical_sha256(
                {**envelope_body, "envelope_sha256": None}
            )
            write_json(
                envelope_path,
                {"schema_version": "1.0", "semantic_content_raw_answer": envelope_body},
            )
            envelope_hash = hashlib.sha256(envelope_path.read_bytes()).hexdigest()

            scorecard_path = run_root / "scorecard.json"
            scorecard_ref = scorecard_path.relative_to(workspace).as_posix()
            truth_prefix = f"{truth_case_ref}#/semantic_content_case_truth/"
            evidence_by_item = {
                "taxonomy_and_scope_grounding": [
                    truth_prefix + "taxonomy_membership_basis"
                ],
                "semantic_decision_correctness": [
                    truth_prefix + "expected_semantic_axes"
                ],
                "source_retrieval_equivalence": [
                    envelope_ref + "#/semantic_content_raw_answer/source_observations"
                ],
                "receiver_evidence_integrity": [snapshot_receipts[0]],
                "safety_boundary": [truth_prefix + "truth_boundary"],
                "unknown_and_challenge_handling": [raw_ref],
            }
            score_items = {
                name: {
                    "responsibility": owner,
                    "critical": critical,
                    "score": 2,
                    "reason": "fixture checked",
                    "evidence_references": evidence_by_item[name],
                }
                for name, (owner, critical) in R4_SCORE_ITEMS.items()
            }
            equivalent_dimensions = {
                name: {
                    "result": "PASS",
                    "reason": "fixture receiver source matches truth dimension",
                    "truth_evidence_references": [truth_prefix + truth_field],
                    "receiver_evidence_references": [snapshot_receipts[0]],
                }
                for name, truth_field in {
                    "taxonomy_membership": "taxonomy_membership_basis",
                    "output_or_use_point": "output_or_subprocess_basis",
                    "mechanism": "mechanism_basis",
                    "conditions": "conditions",
                    "boundary": "truth_boundary",
                }.items()
            }
            scorecard_body = {
                "scorecard_id": f"SCORE-{root_reference}",
                "raw_answer_reference": envelope_ref,
                "raw_answer_sha256": envelope_hash,
                "subject": {"kind": "calibration_case", "id": case_id},
                "method_arm": arm,
                "visible_input_sha256": visible_hash,
                "source_truth_comparison_reference": truth_case_ref,
                "source_truth_comparison_sha256": truth_case_hash,
                "scoring_rubric_version": "2.0-r4",
                "scoring_items": score_items,
                "equivalent_source_dimensions": equivalent_dimensions,
                "equivalent_source_result": "PASS",
                "unknown_items": ["fixture unknown"],
                "content_score_result": "PASS",
                "platform_audit_state": "NOT_COLLECTED",
                "platform_audit_reference_or_null": None,
                "scorecard_sha256": None,
            }
            scorecard_body["scorecard_sha256"] = canonical_sha256(
                {**scorecard_body, "scorecard_sha256": None}
            )
            write_json(
                scorecard_path,
                {"schema_version": "1.0", "semantic_content_scorecard": scorecard_body},
            )
            scorecard_hash = hashlib.sha256(scorecard_path.read_bytes()).hexdigest()

            if preauthorization_reference is None:
                preauthorization_path = run_root / "resource-preauthorization.json"
                preauthorization_reference = preauthorization_path.relative_to(workspace).as_posix()
                preauthorization_body = {
                    "authorization_id": f"AUTH-{root_reference}",
                    "permitted_action": "capture_content_resource_observation_only",
                    "research_contract_id": contract_body["research_contract_id"],
                    "contract_version": contract_body["contract_version"],
                    "case_id": case_id,
                    "method_arm": arm,
                    "original_candidate_task_reference": task_reference,
                    "task_sha256": task_hash,
                    "fresh_context_id": f"FRESH-{root_reference}",
                    "authorized_at": "2026-08-25T09:00:00+08:00",
                    "model_execution_authorized": False,
                    "downstream_authorized": False,
                }
                write_json(
                    preauthorization_path,
                    {
                        "schema_version": "1.0",
                        "receiver_resource_observation_preauthorization": preauthorization_body,
                    },
                )
                preauthorization_sha256 = hashlib.sha256(
                    preauthorization_path.read_bytes()
                ).hexdigest()

            opened_by_query = [[] for _ in range(query_count)]
            for source_index, receipt_reference in enumerate(snapshot_receipts):
                opened_by_query[source_index % query_count].append(receipt_reference)
            queries = []
            for query_index in range(query_count):
                opened = opened_by_query[query_index]
                queries.append(
                    {
                        "query_id": f"QUERY-{root_reference}-{query_index}",
                        "query_text": f"exact fixture query {root_reference} {query_index}",
                        "role": "mechanism",
                        "language": "en",
                        "region": "global",
                        "observed_result_references": list(opened),
                        "inspected_result_count": len(opened),
                        "opened_source_references": list(opened),
                        "access_outcomes": [
                            {"source_reference": ref, "access_state": "opened"}
                            for ref in opened
                        ],
                    }
                )
            observation_path = run_root / "resource-observation.json"
            observation_ref = observation_path.relative_to(workspace).as_posix()
            observation_body = {
                "observation_id": f"RESOURCE-{root_reference}",
                "research_contract_id": contract_body["research_contract_id"],
                "contract_version": contract_body["contract_version"],
                "case_id": case_id,
                "method_arm": arm,
                "task_reference": task_reference,
                "task_sha256": task_hash,
                "deep_expansion_disposition": "expanded" if deep else "screen_only",
                "queries": queries,
                "query_count": query_count,
                "source_open_count": open_count,
                "observation_sha256": None,
            }
            observation_body["observation_sha256"] = canonical_sha256(
                {**observation_body, "observation_sha256": None}
            )
            write_json(
                observation_path,
                {"schema_version": "1.0", "content_resource_observation": observation_body},
            )
            observation_hash = hashlib.sha256(observation_path.read_bytes()).hexdigest()
            resource_receipt_path = run_root / "resource-receipt.json"
            resource_receipt_ref = resource_receipt_path.relative_to(workspace).as_posix()
            resource_receipt_body = {
                "receipt_id": f"RESOURCE-RECEIPT-{root_reference}",
                "receiver_owned": True,
                "preauthorization_reference": preauthorization_reference,
                "preauthorization_sha256": preauthorization_sha256,
                "resource_observation_reference": observation_ref,
                "resource_observation_sha256": observation_hash,
                "captured_at": "2026-08-25T09:30:00+08:00",
                "receipt_sha256": None,
            }
            resource_receipt_body["receipt_sha256"] = canonical_sha256(
                {**resource_receipt_body, "receipt_sha256": None}
            )
            write_json(
                resource_receipt_path,
                {
                    "schema_version": "1.0",
                    "content_resource_observation_receipt": resource_receipt_body,
                },
            )
            return {
                "raw_envelope_reference": envelope_ref,
                "raw_envelope_sha256": envelope_hash,
                "raw_response_reference": raw_ref,
                "raw_response_sha256": raw_hash,
                "scorecard_reference": scorecard_ref,
                "scorecard_sha256": scorecard_hash,
                "resource_observation_reference": observation_ref,
                "resource_observation_sha256": observation_hash,
                "resource_observation_receipt_reference": resource_receipt_ref,
                "resource_observation_receipt_sha256": hashlib.sha256(
                    resource_receipt_path.read_bytes()
                ).hexdigest(),
            }

        arms: dict[str, dict] = {}
        for arm in ("baseline_full_depth_v1", "screen_then_expand_v2"):
            query_parts, open_parts, deep_parts = metric_parts[arm]
            rows = []
            for index, case_id in enumerate(case_ids):
                task = task_info[(case_id, arm)]
                run_fields = make_run(
                    case_id,
                    arm,
                    task["reference"],
                    task["sha256"],
                    task["visible_input_sha256"],
                    query_parts[index],
                    open_parts[index],
                    deep_parts[index],
                    f"runs/{arm}/{case_id}",
                )
                rows.append(
                    {
                        "case_id": case_id,
                        "visible_input_sha256": task["visible_input_sha256"],
                        "task_id": task["task_id"],
                        "task_reference": task["reference"],
                        "task_sha256": task["sha256"],
                        **run_fields,
                        "content_score_result": "PASS",
                        "unknown_items_present": True,
                        "critical_dispositions": {
                            name: "PASS"
                            for name in (
                                "taxonomy_and_scope_grounding",
                                "semantic_decision_correctness",
                                "source_retrieval_equivalence",
                                "receiver_evidence_integrity",
                                "safety_boundary",
                            )
                        },
                    }
                )
            arms[arm] = {
                "schema_version": "2.0-r4",
                "semantic_content_calibration_arm": {
                    "calibration_contract_marker": "2.0-r4",
                    "research_contract_id": contract_body["research_contract_id"],
                    "contract_version": contract_body["contract_version"],
                    "taxonomy_snapshot_sha256": contract_body["taxonomy_snapshot_sha256"],
                    "calibration_case_set_sha256": contract_body[
                        "calibration_case_set_reference_and_hash"
                    ]["sha256"],
                    "source_truth_package_sha256": contract_body[
                        "source_truth_package_sha256"
                    ],
                    "final_contract_reference_and_hash": {
                        "reference": contract_path.relative_to(workspace).as_posix(),
                        "sha256": contract_hash,
                    },
                    "paired_task_manifest_reference_and_hash": {
                        "reference": manifest_path.relative_to(workspace).as_posix(),
                        "sha256": manifest_hash,
                    },
                    "method_arm": arm,
                    "run_complete": True,
                    "case_evidence": rows,
                    "known_positive_case_ids": case_ids[:14],
                    "known_positive_entered_expansion_case_ids": case_ids[:14],
                    "query_count": sum(query_parts),
                    "source_open_count": sum(open_parts),
                    "deep_expansion_count": sum(deep_parts),
                    "safety_failures": [],
                    "content_reproducible": True,
                    "stability_task_manifest_reference_and_hash": {
                        "reference": None,
                        "sha256": None,
                    },
                    "stability_repeat_receipts": [],
                    "platform_audit_summary": "NOT_COLLECTED",
                },
            }

        stability_root = workspace / "stability-package"
        freeze = run(
            FREEZE_STABILITY,
            "--workspace",
            str(workspace),
            "--contract",
            str(contract_path),
            "--expected-final-contract-sha256",
            contract_hash,
            "--formal-case-set",
            str(case_path),
            "--expected-formal-case-set-sha256",
            hashlib.sha256(case_path.read_bytes()).hexdigest(),
            "--paired-task-manifest",
            str(manifest_path),
            "--expected-paired-task-manifest-sha256",
            manifest_hash,
            "--authorization-id-prefix",
            "RECEIVER-STABILITY",
            "--authorized-at",
            "2026-08-25T08:00:00+08:00",
            "--output",
            str(stability_root),
        )
        self.assertEqual(freeze.returncode, 0, freeze.stderr + freeze.stdout)
        stability_manifest_path = stability_root / "stability-task-manifest.json"
        if repeat_context_collision:
            stability_manifest_payload = json.loads(
                stability_manifest_path.read_text(encoding="utf-8")
            )
            stability_body = stability_manifest_payload[
                "content_first_stability_task_manifest"
            ]
            first_entry, second_entry = stability_body["entries"][:2]
            first_preauth = json.loads(
                (stability_root / first_entry["preauthorization_reference"]).read_text(
                    encoding="utf-8"
                )
            )["receiver_resource_observation_preauthorization"]
            second_preauth_path = stability_root / second_entry[
                "preauthorization_reference"
            ]
            second_preauth_payload = json.loads(
                second_preauth_path.read_text(encoding="utf-8")
            )
            second_preauth = second_preauth_payload[
                "receiver_resource_observation_preauthorization"
            ]
            second_preauth["authorization_id"] = first_preauth["authorization_id"]
            second_preauth["fresh_context_id"] = first_preauth["fresh_context_id"]
            write_json(second_preauth_path, second_preauth_payload)
            second_entry["preauthorization_sha256"] = hashlib.sha256(
                second_preauth_path.read_bytes()
            ).hexdigest()
            second_task_path = stability_root / second_entry["repeat_task_reference"]
            second_task_payload = json.loads(
                second_task_path.read_text(encoding="utf-8")
            )
            second_task = second_task_payload["content_first_stability_repeat_task"]
            second_task["preauthorization_sha256"] = second_entry[
                "preauthorization_sha256"
            ]
            second_task["fresh_context_id"] = first_preauth["fresh_context_id"]
            write_json(second_task_path, second_task_payload)
            second_entry["repeat_task_sha256"] = hashlib.sha256(
                second_task_path.read_bytes()
            ).hexdigest()
            write_json(stability_manifest_path, stability_manifest_payload)
        stability_manifest_hash = hashlib.sha256(stability_manifest_path.read_bytes()).hexdigest()
        candidate_body = arms["screen_then_expand_v2"]["semantic_content_calibration_arm"]
        candidate_body["stability_task_manifest_reference_and_hash"] = {
            "reference": stability_manifest_path.relative_to(workspace).as_posix(),
            "sha256": stability_manifest_hash,
        }
        stability_manifest = json.loads(stability_manifest_path.read_text(encoding="utf-8"))[
            "content_first_stability_task_manifest"
        ]
        stability_receipts = []
        if include_repeats:
            for entry in stability_manifest["entries"]:
                case_id = entry["case_id"]
                repeat_task_path = stability_root / entry["repeat_task_reference"]
                repeat_task_ref = repeat_task_path.relative_to(workspace).as_posix()
                repeat_task_hash = hashlib.sha256(repeat_task_path.read_bytes()).hexdigest()
                preauth_path = stability_root / entry["preauthorization_reference"]
                preauth_ref = preauth_path.relative_to(workspace).as_posix()
                run_fields = make_run(
                    case_id,
                    "screen_then_expand_v2",
                    repeat_task_ref,
                    repeat_task_hash,
                    task_info[(case_id, "screen_then_expand_v2")]["visible_input_sha256"],
                    1,
                    1,
                    1,
                    f"stability-runs/{case_id}",
                    preauthorization_reference=preauth_ref,
                    preauthorization_sha256=hashlib.sha256(preauth_path.read_bytes()).hexdigest(),
                )
                receipt_path = workspace / "stability-receipts" / f"{case_id}.json"
                receipt_body = {
                    "receipt_id": f"STABILITY-RECEIPT-{case_id}",
                    "repeat_id": entry["repeat_id"],
                    "case_id": case_id,
                    "method_arm": "screen_then_expand_v2",
                    "visible_input_sha256": entry["visible_input_sha256"],
                    "repeat_task_reference": repeat_task_ref,
                    "repeat_task_sha256": repeat_task_hash,
                    "preauthorization_reference": preauth_ref,
                    "preauthorization_sha256": hashlib.sha256(preauth_path.read_bytes()).hexdigest(),
                    "original_candidate_task_reference": task_info[
                        (case_id, "screen_then_expand_v2")
                    ]["reference"],
                    "original_candidate_task_sha256": task_info[
                        (case_id, "screen_then_expand_v2")
                    ]["sha256"],
                    **run_fields,
                    "receipt_sha256": None,
                }
                receipt_body["receipt_sha256"] = canonical_sha256(
                    {**receipt_body, "receipt_sha256": None}
                )
                write_json(
                    receipt_path,
                    {
                        "schema_version": "1.0",
                        "content_first_stability_repeat_receipt": receipt_body,
                    },
                )
                stability_receipts.append(
                    {
                        "reference": receipt_path.relative_to(workspace).as_posix(),
                        "sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
                    }
                )
        candidate_body["stability_repeat_receipts"] = stability_receipts
        common_args = [
            "--workspace",
            str(workspace),
            "--contract",
            str(contract_path),
            "--expected-final-contract-sha256",
            contract_hash,
            "--paired-task-manifest",
            str(manifest_path),
            "--expected-paired-task-manifest-sha256",
            manifest_hash,
            "--stability-task-manifest",
            str(stability_manifest_path),
            "--expected-stability-task-manifest-sha256",
            stability_manifest_hash,
        ]
        return (
            arms["baseline_full_depth_v1"],
            arms["screen_then_expand_v2"],
            common_args,
            {
                "workspace": workspace,
                "contract": contract_path,
                "cases": case_path,
                "truth": truth_path,
                "manifest": manifest_path,
                "stability_manifest": stability_manifest_path,
            },
        )

    def test_validator_accepts_complete_content_evidence_without_platform_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            result = run(VALIDATE, str(workspace), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_validator_accepts_task4_frozen_r4_method_arm_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_validator_rejects_unmarked_legacy_five_item_scorecard(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            contract_path = workspace / "00-合同/semantic-research-contract.json"
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["content_first_policy"].pop(
                "truth_scorecard_contract_version"
            )
            write_json(contract_path, payload)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TRUTH_SCORECARD_CONTRACT_VERSION_INVALID", result.stdout)

    def test_r4_validator_requires_explicit_truth_scorecard_contract_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            contract_path = workspace / "00-合同/semantic-research-contract.json"
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["content_first_policy"].pop(
                "truth_scorecard_contract_version"
            )
            write_json(contract_path, payload)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TRUTH_SCORECARD_CONTRACT_VERSION_INVALID", result.stdout)

    def test_r4_marker_cannot_downgrade_by_deleting_method_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            contract_path = workspace / "00-合同/semantic-research-contract.json"
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            contract = payload["semantic_research_contract"]
            contract.pop("baseline_method_contract")
            contract.pop("candidate_method_contract")
            write_json(contract_path, payload)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CONTENT_CONTRACT_METHOD_ARMS_INVALID", result.stdout)

    def test_r4_validator_rejects_swapped_declared_method_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            contract_path = workspace / "00-合同/semantic-research-contract.json"
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            contract = payload["semantic_research_contract"]
            contract["baseline_method_contract"] = "screen_then_expand_v2"
            contract["candidate_method_contract"] = "baseline_full_depth_v1"
            write_json(contract_path, payload)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CONTENT_CONTRACT_METHOD_ARMS_INVALID", result.stdout)

    def test_legacy_marker_is_limited_to_the_frozen_legacy_contract_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            contract_path = workspace / "00-合同/semantic-research-contract.json"
            payload = json.loads(contract_path.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["contract_version"] = (
                "2.1.0-content-first.final.1"
            )
            write_json(contract_path, payload)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CONTENT_CONTRACT_METHOD_ARMS_INVALID", result.stdout)

    def test_r4_validator_rejects_wrong_truth_binding_and_missing_three_link_basis(self):
        cases = (
            (
                lambda truth: truth.__setitem__("case_id", "CASE-OTHER"),
                "CONTENT_CASE_TRUTH_BINDING_MISMATCH",
            ),
            (
                lambda truth: truth.pop("mechanism_basis"),
                "CONTENT_CASE_TRUTH_INVALID",
            ),
        )
        for mutate, expected_code in cases:
            with self.subTest(expected_code=expected_code), tempfile.TemporaryDirectory() as tmp:
                workspace, _ = self.make_r4_workspace(Path(tmp))
                self.rewrite_r4_truth_and_bind(workspace, mutate)

                result = run(VALIDATE, str(workspace), "--format", "json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_code, result.stdout)

    def test_r4_validator_rejects_duplicate_cross_responsibility_truth_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))

            def reuse_taxonomy_source(truth: dict) -> None:
                truth["output_or_subprocess_basis"]["source_references"] = list(
                    truth["taxonomy_membership_basis"]["source_references"]
                )

            self.rewrite_r4_truth_and_bind(workspace, reuse_taxonomy_source)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TRUTH_SOURCE_REFERENCE_REUSED", result.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            source = (
                workspace
                / "02-来源真值/truth-source-snapshots/CASE-001.taxonomy.source"
            )
            copied = (
                workspace
                / "02-来源真值/truth-source-snapshots/CASE-001.taxonomy-copy.source"
            )
            copied.write_bytes(source.read_bytes())

            def reuse_taxonomy_bytes(truth: dict) -> None:
                truth["output_or_subprocess_basis"]["source_references"] = [{
                    "reference": copied.relative_to(workspace).as_posix(),
                    "sha256": hashlib.sha256(copied.read_bytes()).hexdigest(),
                }]

            self.rewrite_r4_truth_and_bind(workspace, reuse_taxonomy_bytes)
            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TRUTH_SOURCE_REFERENCE_REUSED", result.stdout)

    def test_r4_truth_reference_must_be_canonical_not_absolute_or_symlinked(self):
        for alias_kind in ("absolute", "symlink"):
            with self.subTest(alias_kind=alias_kind), tempfile.TemporaryDirectory() as tmp:
                workspace, _ = self.make_r4_workspace(Path(tmp))
                truth_path = workspace / "02-来源真值/CASE-001.json"
                if alias_kind == "absolute":
                    alias_reference = str(truth_path)
                else:
                    alias_path = workspace / "02-来源真值/CASE-001.alias.json"
                    alias_path.symlink_to(truth_path)
                    alias_reference = alias_path.relative_to(workspace).as_posix()
                envelope_path = (
                    workspace
                    / "03-内容原始回答/candidate/CASE-001.envelope.json"
                )
                envelope_payload = json.loads(envelope_path.read_text(encoding="utf-8"))
                envelope = envelope_payload["semantic_content_raw_answer"]
                envelope["source_truth_comparison_reference"] = alias_reference
                envelope["envelope_sha256"] = canonical_sha256(
                    {**envelope, "envelope_sha256": None}
                )
                write_json(envelope_path, envelope_payload)
                score_path = workspace / "07-报告/content-scorecards/CASE-001.json"
                score_payload = json.loads(score_path.read_text(encoding="utf-8"))
                score = score_payload["semantic_content_scorecard"]
                score["raw_answer_sha256"] = hashlib.sha256(
                    envelope_path.read_bytes()
                ).hexdigest()
                score["source_truth_comparison_reference"] = alias_reference
                score["scorecard_sha256"] = canonical_sha256(
                    {**score, "scorecard_sha256": None}
                )
                write_json(score_path, score_payload)

                result = run(VALIDATE, str(workspace), "--format", "json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("SOURCE_TRUTH_COMPARISON_REFERENCE_INVALID", result.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            source = (
                workspace
                / "02-来源真值/truth-source-snapshots/CASE-001.taxonomy.source"
            )
            alias = (
                workspace
                / "02-来源真值/truth-source-snapshots/CASE-001.taxonomy-alias.source"
            )
            alias.hardlink_to(source)

            def reuse_taxonomy_inode(truth: dict) -> None:
                truth["output_or_subprocess_basis"]["source_references"] = [{
                    "reference": alias.relative_to(workspace).as_posix(),
                    "sha256": hashlib.sha256(alias.read_bytes()).hexdigest(),
                }]

            self.rewrite_r4_truth_and_bind(workspace, reuse_taxonomy_inode)
            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TRUTH_SOURCE_REFERENCE_REUSED", result.stdout)

    def test_r4_truth_source_must_be_hash_verified_not_scorecard_self_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))

            def replace_truth_source_with_scorecard(truth: dict) -> None:
                scorecard_path = workspace / "07-报告/content-scorecards/CASE-001.json"
                truth["taxonomy_membership_basis"]["source_references"] = [{
                    "reference": scorecard_path.relative_to(workspace).as_posix(),
                    "sha256": hashlib.sha256(scorecard_path.read_bytes()).hexdigest(),
                }]

            self.rewrite_r4_truth_and_bind(workspace, replace_truth_source_with_scorecard)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TRUTH_SOURCE_REFERENCE_INVALID", result.stdout)

    def test_r4_scorecard_enforces_exact_six_owned_items_and_disjoint_evidence_refs(self):
        cases = (
            (
                lambda score: score["scoring_items"]["taxonomy_and_scope_grounding"].__setitem__(
                    "responsibility", "source_equivalence_reviewer"
                ),
                "SCORECARD_ITEMS_INVALID",
            ),
            (
                lambda score: score["scoring_items"]["semantic_decision_correctness"].__setitem__(
                    "evidence_references",
                    list(
                        score["scoring_items"]["taxonomy_and_scope_grounding"][
                            "evidence_references"
                        ]
                    ),
                ),
                "SCORECARD_EVIDENCE_REFERENCE_REUSED",
            ),
            (
                lambda score: score["scoring_items"]["safety_boundary"].__setitem__(
                    "critical", False
                ),
                "SCORECARD_ITEMS_INVALID",
            ),
            (
                lambda score: score["scoring_items"]["receiver_evidence_integrity"].__setitem__(
                    "evidence_references",
                    ["07-报告/content-scorecards/CASE-001.json"],
                ),
                "SCORECARD_ITEMS_INVALID",
            ),
            (
                lambda score: score["scoring_items"]["taxonomy_and_scope_grounding"].__setitem__(
                    "evidence_references",
                    ["02-来源真值/CASE-001.json#/semantic_content_case_truth/not-a-field"],
                ),
                "SCORECARD_ITEMS_INVALID",
            ),
            (
                lambda score: score.__setitem__(
                    "taxonomy_membership_basis", {"basis_text": "laundered truth"}
                ),
                "SCORECARD_FIELDS_INVALID",
            ),
        )
        for mutate, expected_code in cases:
            with self.subTest(expected_code=expected_code), tempfile.TemporaryDirectory() as tmp:
                workspace, _ = self.make_r4_workspace(Path(tmp))
                self.rewrite_r4_scorecard(workspace, mutate)

                result = run(VALIDATE, str(workspace), "--format", "json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_code, result.stdout)

    def test_r4_score_evidence_is_bound_to_current_truth_arm_and_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))

            def use_raw_observation_as_semantic_truth(score: dict) -> None:
                score["scoring_items"]["semantic_decision_correctness"][
                    "evidence_references"
                ] = [
                    "03-内容原始回答/candidate/CASE-001.envelope.json"
                    "#/semantic_content_raw_answer/source_observations/0"
                ]

            self.rewrite_r4_scorecard(workspace, use_raw_observation_as_semantic_truth)
            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCORECARD_EVIDENCE_ROLE_INVALID", result.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            candidate_receipt = (
                workspace
                / "05-证据包/source-snapshot-receipts/OBS-R4-TAXONOMY.receipt.json"
            )
            baseline_reference = (
                "05-证据包/source-snapshot-receipts/OBS-BASELINE-TAXONOMY.receipt.json"
            )
            baseline_receipt = workspace / baseline_reference
            baseline_receipt.write_bytes(candidate_receipt.read_bytes())

            def use_baseline_receipt_for_candidate(score: dict) -> None:
                score["scoring_items"]["receiver_evidence_integrity"][
                    "evidence_references"
                ] = [baseline_reference]

            self.rewrite_r4_scorecard(workspace, use_baseline_receipt_for_candidate)
            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCORECARD_EVIDENCE_ROLE_INVALID", result.stdout)

    def test_r4_scorecard_hardlink_self_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            score_path = workspace / "07-报告/content-scorecards/CASE-001.json"
            alias_reference = "05-证据包/scorecard-hardlink.json"
            alias = workspace / alias_reference
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.hardlink_to(score_path)

            def self_cite_hardlink(score: dict) -> None:
                score["scoring_items"]["receiver_evidence_integrity"][
                    "evidence_references"
                ] = [alias_reference]

            self.rewrite_r4_scorecard(workspace, self_cite_hardlink)
            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCORECARD_EVIDENCE_SELF_REFERENCE", result.stdout)

    def test_r4_truth_and_receiver_snapshot_cannot_share_inode(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            truth_path = workspace / "02-来源真值/CASE-001.json"
            snapshot_path = (
                workspace
                / "05-证据包/receiver-source-snapshots/OBS-R4-TAXONOMY.snapshot"
            )
            snapshot_path.unlink()
            snapshot_path.hardlink_to(truth_path)
            receipt_path = (
                workspace
                / "05-证据包/source-snapshot-receipts/OBS-R4-TAXONOMY.receipt.json"
            )
            receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt = receipt_payload["content_source_snapshot_receipt"]
            receipt["receiver_snapshot_sha256"] = hashlib.sha256(
                snapshot_path.read_bytes()
            ).hexdigest()
            receipt["receipt_sha256"] = canonical_sha256(
                {**receipt, "receipt_sha256": None}
            )
            write_json(receipt_path, receipt_payload)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ARTIFACT_ROLE_INODE_COLLISION", result.stdout)

    def test_r4_score_arithmetic_fails_critical_zero_and_leaves_other_incomplete_unverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))

            def critical_zero(score: dict) -> None:
                score["scoring_items"]["safety_boundary"]["score"] = 0
                score["content_score_result"] = "UNVERIFIED"

            self.rewrite_r4_scorecard(workspace, critical_zero)
            failed = run(VALIDATE, str(workspace), "--format", "json")
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("SCORECARD_RESULT_INVALID", failed.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))

            def noncritical_incomplete(score: dict) -> None:
                score["scoring_items"]["unknown_and_challenge_handling"]["score"] = 1
                score["content_score_result"] = "UNVERIFIED"

            self.rewrite_r4_scorecard(workspace, noncritical_incomplete)
            unverified = run(VALIDATE, str(workspace), "--format", "json")
            self.assertEqual(unverified.returncode, 0, unverified.stderr + unverified.stdout)
            self.assertEqual(json.loads(unverified.stdout)["status"], "UNVERIFIED")

    def test_r4_equivalent_source_result_is_derived_from_all_five_dimensions(self):
        cases = (
            (
                lambda score: score["equivalent_source_dimensions"].pop("boundary"),
                "EQUIVALENT_SOURCE_DIMENSIONS_INVALID",
            ),
            (
                lambda score: score["equivalent_source_dimensions"]["mechanism"].__setitem__(
                    "result", "UNVERIFIED"
                ),
                "EQUIVALENT_SOURCE_RESULT_INVALID",
            ),
            (
                lambda score: score["equivalent_source_dimensions"]["conditions"].__setitem__(
                    "receiver_evidence_references", []
                ),
                "EQUIVALENT_SOURCE_DIMENSIONS_INVALID",
            ),
            (
                lambda score: (
                    score["equivalent_source_dimensions"]["mechanism"].__setitem__(
                        "result", "UNVERIFIED"
                    ),
                    score.__setitem__("equivalent_source_result", "UNVERIFIED"),
                ),
                "EQUIVALENT_SOURCE_SCORE_INCONSISTENT",
            ),
        )
        for mutate, expected_code in cases:
            with self.subTest(expected_code=expected_code), tempfile.TemporaryDirectory() as tmp:
                workspace, _ = self.make_r4_workspace(Path(tmp))
                self.rewrite_r4_scorecard(workspace, mutate)

                result = run(VALIDATE, str(workspace), "--format", "json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_code, result.stdout)

    def test_r4_equivalence_pass_does_not_require_matching_source_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_r4_truth_sources_are_independent_from_arm_receiver_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_r4_workspace(Path(tmp))
            envelope = json.loads(
                (
                    workspace
                    / "03-内容原始回答/candidate/CASE-001.envelope.json"
                ).read_text(encoding="utf-8")
            )["semantic_content_raw_answer"]
            truth = json.loads(
                (workspace / "02-来源真值/CASE-001.json").read_text(encoding="utf-8")
            )["semantic_content_case_truth"]
            truth_references = {
                reference["reference"]
                for basis_name in (
                    "taxonomy_membership_basis",
                    "output_or_subprocess_basis",
                    "mechanism_basis",
                )
                for reference in truth[basis_name]["source_references"]
            }

            self.assertTrue(
                truth_references.isdisjoint(
                    set(envelope["source_snapshot_receipt_references"])
                )
            )
            result = run(VALIDATE, str(workspace), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_validator_rejects_legacy_arm_when_frozen_r4_contract_declares_exact_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            write_json(
                workspace / "00-合同" / "semantic-research-contract.json",
                self.content_contract(r4_methods=True),
            )

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RAW_ENVELOPE_SEMANTICS_INVALID", result.stdout)

    def test_snapshot_registrar_copies_exact_bytes_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace, _ = self.make_workspace(root)
            source_file = root / "captured-source.bin"
            source_file.write_bytes(b"receiver-owned\x00source\n")
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(),
                "05-证据包/source-snapshot-receipts/OBS-001.receipt.json",
            )

            first = self.register_snapshot(
                workspace, source_file, "OBS-001", observation_reference
            )

            self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
            payload = json.loads(first.stdout)
            snapshot = workspace / payload["receiver_snapshot_reference"]
            receipt = workspace / payload["receipt_reference"]
            self.assertEqual(snapshot.read_bytes(), b"receiver-owned\x00source\n")
            self.assertEqual(
                hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                payload["receiver_snapshot_sha256"],
            )
            receipt_payload = json.loads(receipt.read_text(encoding="utf-8"))[
                "content_source_snapshot_receipt"
            ]
            self.assertEqual(receipt_payload["observation_id"], "OBS-001")
            self.assertEqual(
                receipt_payload["source_observation_reference"], observation_reference
            )

            second = self.register_snapshot(
                workspace, source_file, "OBS-001", observation_reference
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("SNAPSHOT_EXISTS", second.stderr)
            self.assertEqual(snapshot.read_bytes(), b"receiver-owned\x00source\n")

    def test_snapshot_registrar_rejects_escape_aliases_and_cleans_partial_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace, _ = self.make_workspace(root)
            envelope_path = workspace / "03-内容原始回答/candidate/CASE-001.envelope.json"
            source_alias = root / "captured-source-alias.json"
            source_alias.hardlink_to(envelope_path)
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(),
                "05-证据包/source-snapshot-receipts/OBS-ALIAS.receipt.json",
            )

            aliased = self.register_snapshot(
                workspace, source_alias, "OBS-ALIAS", observation_reference
            )

            self.assertNotEqual(aliased.returncode, 0)
            self.assertIn("SOURCE_FILE_NOT_EXTERNAL", aliased.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace, _ = self.make_workspace(root)
            source_file = root / "captured-source.bin"
            source_file.write_bytes(b"source")
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(),
                "05-证据包/source-snapshot-receipts/OBS-ESCAPE.receipt.json",
            )
            outside = root / "outside"
            outside.mkdir()
            evidence = workspace / "05-证据包"
            evidence.mkdir(parents=True, exist_ok=True)
            (evidence / "receiver-source-snapshots").symlink_to(outside, target_is_directory=True)

            escaped = self.register_snapshot(
                workspace, source_file, "OBS-ESCAPE", observation_reference
            )

            self.assertNotEqual(escaped.returncode, 0)
            self.assertIn("SNAPSHOT_DESTINATION_OUTSIDE_WORKSPACE", escaped.stderr)
            self.assertEqual(list(outside.iterdir()), [])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace, _ = self.make_workspace(root)
            source_file = root / "captured-source.bin"
            source_file.write_bytes(b"source")
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(),
                "05-证据包/source-snapshot-receipts/OBS-FAIL.receipt.json",
            )

            failed = self.register_snapshot(
                workspace,
                source_file,
                "OBS-FAIL",
                observation_reference,
                "--test-fail-after-snapshot-publish",
            )

            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("SNAPSHOT_WRITE_FAILED", failed.stderr)
            self.assertFalse(
                (workspace / "05-证据包/receiver-source-snapshots/OBS-FAIL.snapshot").exists()
            )
            self.assertFalse(
                (workspace / "05-证据包/source-snapshot-receipts/OBS-FAIL.receipt.json").exists()
            )

    def test_snapshot_registrar_rejects_workspace_source_and_external_hardlink_alias(self):
        for alias_kind in ("direct", "external_hardlink"):
            with self.subTest(alias_kind=alias_kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                workspace, _ = self.make_workspace(root)
                internal_source = workspace / "02-来源真值" / "CASE-001.json"
                source_file = internal_source
                if alias_kind == "external_hardlink":
                    source_file = root / "external-source-alias.json"
                    source_file.hardlink_to(internal_source)
                observation_reference = (
                    "03-内容原始回答/candidate/CASE-001.envelope.json"
                    "#/semantic_content_raw_answer/source_observations/0"
                )
                self.attach_source_observation_and_receipt(
                    workspace,
                    self.source_observation(),
                    "05-证据包/source-snapshot-receipts/OBS-INTERNAL.receipt.json",
                )

                result = self.register_snapshot(
                    workspace, source_file, "OBS-INTERNAL", observation_reference
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("SOURCE_FILE_NOT_EXTERNAL", result.stderr)

    def test_snapshot_registrar_requires_canonical_existing_valid_observation_pointer(self):
        invalid_references = (
            "03-内容原始回答/candidate/CASE-001.envelope.json#/semantic_content_raw_answer/source_observations/00",
            "03-内容原始回答/candidate/CASE-001.envelope.json#/semantic_content_raw_answer/source_observations/1",
        )
        for invalid_reference in invalid_references:
            with self.subTest(reference=invalid_reference), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                workspace, _ = self.make_workspace(root)
                source_file = root / "captured-source.bin"
                source_file.write_bytes(b"source")
                self.attach_source_observation_and_receipt(
                    workspace,
                    self.source_observation(),
                    "05-证据包/source-snapshot-receipts/OBS-POINTER.receipt.json",
                )

                result = self.register_snapshot(
                    workspace, source_file, "OBS-POINTER", invalid_reference
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("SOURCE_OBSERVATION_REFERENCE_INVALID", result.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace, _ = self.make_workspace(root)
            source_file = root / "captured-source.bin"
            source_file.write_bytes(b"source")
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(receipt_sha256="model-owned"),
                "05-证据包/source-snapshot-receipts/OBS-INVALID.receipt.json",
            )

            result = self.register_snapshot(
                workspace, source_file, "OBS-INVALID", observation_reference
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCE_OBSERVATION_INVALID", result.stderr)

    def test_snapshot_registrar_rejects_fullwidth_and_true_multilayer_receiver_keys(self):
        multilayer_key = "%72eceiver_snapshot_sha256"
        for _ in range(8):
            multilayer_key = quote(multilayer_key, safe="")
        multilayer_fullwidth_key = "％72eceiver_snapshot_sha256"
        for _ in range(8):
            multilayer_fullwidth_key = quote(multilayer_fullwidth_key, safe="")
        for disguised_key in (
            "％72eceiver_snapshot_sha256",
            multilayer_key,
            multilayer_fullwidth_key,
        ):
            with self.subTest(disguised_key=disguised_key), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                workspace, _ = self.make_workspace(root)
                source_file = root / "captured-source.bin"
                source_file.write_bytes(b"source")
                observation_reference = (
                    "03-内容原始回答/candidate/CASE-001.envelope.json"
                    "#/semantic_content_raw_answer/source_observations/0"
                )
                self.attach_source_observation_and_receipt(
                    workspace,
                    self.source_observation(conditions=[{disguised_key: "model claim"}]),
                    "05-证据包/source-snapshot-receipts/OBS-DISGUISED.receipt.json",
                )

                result = self.register_snapshot(
                    workspace, source_file, "OBS-DISGUISED", observation_reference
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("SOURCE_OBSERVATION_INVALID", result.stderr)

    def test_validator_rejects_receiver_fields_inside_model_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            observation = {
                "source_url_or_null": "https://example.invalid/source",
                "publisher_or_null": "Example",
                "title_or_null": "Title",
                "original_location_or_null": "section 1",
                "bounded_summary_or_null": "bounded",
                "access_state": "OBSERVED",
                "conditions": [],
                "limitations": [],
                "counterevidence": [],
                "receiver_snapshot_sha256": "a" * 64,
            }
            self.attach_source_observation_and_receipt(
                workspace, observation, "05-证据包/source-snapshot-receipts/OBS-001.receipt.json"
            )

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("MODEL_OBSERVATION_RECEIVER_FIELD_FORBIDDEN", result.stdout)

    def test_validator_rejects_nested_receipt_fields_and_deep_percent_encoding(self):
        nested_keys = ["receipt_sha256", "snapshot_capture_state"]
        deeply_encoded = "receiver_snapshot_sha256"
        for _ in range(8):
            deeply_encoded = quote(deeply_encoded, safe="")
        nested_keys.append(deeply_encoded)
        for nested_key in nested_keys:
            with self.subTest(nested_key=nested_key), tempfile.TemporaryDirectory() as tmp:
                workspace, _ = self.make_workspace(Path(tmp))
                observation = self.source_observation(conditions=[{nested_key: "model claim"}])
                self.attach_source_observation_and_receipt(
                    workspace,
                    observation,
                    "05-证据包/source-snapshot-receipts/OBS-001.receipt.json",
                )

                result = run(VALIDATE, str(workspace), "--format", "json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("MODEL_OBSERVATION_RECEIVER_FIELD_FORBIDDEN", result.stdout)

    def test_validator_rejects_fullwidth_and_true_multilayer_receiver_keys(self):
        multilayer_key = "%72eceiver_snapshot_sha256"
        for _ in range(8):
            multilayer_key = quote(multilayer_key, safe="")
        multilayer_fullwidth_key = "％72eceiver_snapshot_sha256"
        for _ in range(8):
            multilayer_fullwidth_key = quote(multilayer_fullwidth_key, safe="")
        for disguised_key in (
            "％72eceiver_snapshot_sha256",
            multilayer_key,
            multilayer_fullwidth_key,
        ):
            with self.subTest(disguised_key=disguised_key), tempfile.TemporaryDirectory() as tmp:
                workspace, _ = self.make_workspace(Path(tmp))
                self.attach_source_observation_and_receipt(
                    workspace,
                    self.source_observation(conditions=[{disguised_key: "model claim"}]),
                    "05-证据包/source-snapshot-receipts/OBS-DISGUISED.receipt.json",
                )

                result = run(VALIDATE, str(workspace), "--format", "json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("MODEL_OBSERVATION_RECEIVER_FIELD_FORBIDDEN", result.stdout)

    def test_validator_recomputes_captured_snapshot_and_rejects_prose_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace, _ = self.make_workspace(root)
            source_file = root / "captured-source.bin"
            source_file.write_bytes(b"captured bytes")
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(),
                "05-证据包/source-snapshot-receipts/OBS-001.receipt.json",
            )
            registered = self.register_snapshot(
                workspace, source_file, "OBS-001", observation_reference
            )
            self.assertEqual(registered.returncode, 0, registered.stderr)
            registered_payload = json.loads(registered.stdout)
            observation = {
                "source_url_or_null": "https://example.invalid/source",
                "publisher_or_null": "Example",
                "title_or_null": "Title",
                "original_location_or_null": "section 1",
                "bounded_summary_or_null": "bounded",
                "access_state": "OBSERVED",
                "conditions": [],
                "limitations": [],
                "counterevidence": [],
            }
            self.attach_source_observation_and_receipt(
                workspace, observation, registered_payload["receipt_reference"]
            )
            valid = run(VALIDATE, str(workspace), "--format", "json")
            self.assertEqual(valid.returncode, 0, valid.stderr + valid.stdout)

            receipt_path = workspace / registered_payload["receipt_reference"]
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt_body = receipt["content_source_snapshot_receipt"]
            receipt_body["receiver_snapshot_sha256"] = "source observed in browser"
            receipt_body["receipt_sha256"] = canonical_sha256(
                {**receipt_body, "receipt_sha256": None}
            )
            write_json(receipt_path, receipt)

            invalid = run(VALIDATE, str(workspace), "--format", "json")
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("RECEIVER_SNAPSHOT_SHA256_INVALID", invalid.stdout)

    def test_validator_rejects_a_hash_valid_non_snapshot_file_laundered_as_receiver_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace, _ = self.make_workspace(root)
            source_file = root / "captured-source.bin"
            source_file.write_bytes(b"captured bytes")
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(),
                "05-证据包/source-snapshot-receipts/OBS-001.receipt.json",
            )
            registered = self.register_snapshot(
                workspace, source_file, "OBS-001", observation_reference
            )
            self.assertEqual(registered.returncode, 0, registered.stderr)
            registered_payload = json.loads(registered.stdout)
            observation = {
                "source_url_or_null": "https://example.invalid/source",
                "publisher_or_null": "Example",
                "title_or_null": "Title",
                "original_location_or_null": "section 1",
                "bounded_summary_or_null": "bounded",
                "access_state": "OBSERVED",
                "conditions": [],
                "limitations": [],
                "counterevidence": [],
            }
            self.attach_source_observation_and_receipt(
                workspace, observation, registered_payload["receipt_reference"]
            )
            receipt_path = workspace / registered_payload["receipt_reference"]
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            body = receipt["content_source_snapshot_receipt"]
            unrelated = workspace / "02-来源真值" / "CASE-001.json"
            body["receiver_snapshot_reference"] = unrelated.relative_to(workspace).as_posix()
            body["receiver_snapshot_sha256"] = hashlib.sha256(unrelated.read_bytes()).hexdigest()
            body["receipt_sha256"] = canonical_sha256({**body, "receipt_sha256": None})
            write_json(receipt_path, receipt)

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RECEIVER_SNAPSHOT_REFERENCE_INVALID", result.stdout)

    def test_validator_binds_receipt_id_to_observation_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            receipt_body = {
                "receipt_id": "SNAPSHOT-OTHER",
                "observation_id": "OBS-001",
                "source_observation_reference": observation_reference,
                "receiver_snapshot_reference": None,
                "receiver_snapshot_sha256": None,
                "snapshot_capture_state": "unavailable",
                "snapshot_captured_at": "2026-08-25T09:30:00+08:00",
                "receipt_sha256": None,
            }
            receipt_body["receipt_sha256"] = canonical_sha256(
                {**receipt_body, "receipt_sha256": None}
            )
            receipt_reference = "05-证据包/source-snapshot-receipts/OBS-001.receipt.json"
            write_json(
                workspace / receipt_reference,
                {
                    "schema_version": "1.0",
                    "content_source_snapshot_receipt": receipt_body,
                },
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(
                    access_state="UNVERIFIED", limitations=["capture unavailable"]
                ),
                receipt_reference,
            )

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCE_SNAPSHOT_RECEIPT_ID_INVALID", result.stdout)

    def test_validator_rejects_receipt_bound_to_the_wrong_observation_pointer(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            receipt_body = {
                "receipt_id": "SNAPSHOT-OBS-001",
                "observation_id": "OBS-001",
                "source_observation_reference": (
                    "03-内容原始回答/candidate/CASE-001.envelope.json"
                    "#/semantic_content_raw_answer/source_observations/1"
                ),
                "receiver_snapshot_reference": None,
                "receiver_snapshot_sha256": None,
                "snapshot_capture_state": "unavailable",
                "snapshot_captured_at": "2026-08-25T09:30:00+08:00",
                "receipt_sha256": None,
            }
            receipt_body["receipt_sha256"] = canonical_sha256(
                {**receipt_body, "receipt_sha256": None}
            )
            receipt_reference = "05-证据包/source-snapshot-receipts/OBS-001.receipt.json"
            write_json(
                workspace / receipt_reference,
                {
                    "schema_version": "1.0",
                    "content_source_snapshot_receipt": receipt_body,
                },
            )
            self.attach_source_observation_and_receipt(
                workspace,
                self.source_observation(
                    access_state="UNVERIFIED", limitations=["capture unavailable"]
                ),
                receipt_reference,
            )

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCE_SNAPSHOT_RECEIPT_SEMANTICS_INVALID", result.stdout)

    def test_validator_rejects_duplicate_receipt_ids_across_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            envelope_path = workspace / "03-内容原始回答/candidate/CASE-001.envelope.json"
            envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
            envelope_body = envelope["semantic_content_raw_answer"]
            observations = [
                self.source_observation(
                    access_state="UNVERIFIED", limitations=["capture unavailable"]
                ),
                self.source_observation(
                    access_state="UNVERIFIED", limitations=["capture unavailable"]
                ),
            ]
            receipt_references = [
                "05-证据包/source-snapshot-receipts/OBS-001.receipt.json",
                "05-证据包/source-snapshot-receipts/OBS-002.receipt.json",
            ]
            envelope_body["source_observations"] = observations
            envelope_body["source_snapshot_receipt_references"] = receipt_references
            envelope_body["envelope_sha256"] = canonical_sha256(
                {**envelope_body, "envelope_sha256": None}
            )
            write_json(envelope_path, envelope)
            score_path = workspace / "07-报告/content-scorecards/CASE-001.json"
            scorecard = json.loads(score_path.read_text(encoding="utf-8"))
            score_body = scorecard["semantic_content_scorecard"]
            score_body["raw_answer_sha256"] = hashlib.sha256(envelope_path.read_bytes()).hexdigest()
            score_body["scorecard_sha256"] = canonical_sha256(
                {**score_body, "scorecard_sha256": None}
            )
            write_json(score_path, scorecard)
            for index, observation_id in enumerate(("OBS-001", "OBS-002")):
                receipt_body = {
                    "receipt_id": "SNAPSHOT-OBS-001",
                    "observation_id": observation_id,
                    "source_observation_reference": (
                        "03-内容原始回答/candidate/CASE-001.envelope.json"
                        f"#/semantic_content_raw_answer/source_observations/{index}"
                    ),
                    "receiver_snapshot_reference": None,
                    "receiver_snapshot_sha256": None,
                    "snapshot_capture_state": "unavailable",
                    "snapshot_captured_at": "2026-08-25T09:30:00+08:00",
                    "receipt_sha256": None,
                }
                receipt_body["receipt_sha256"] = canonical_sha256(
                    {**receipt_body, "receipt_sha256": None}
                )
                write_json(
                    workspace / receipt_references[index],
                    {
                        "schema_version": "1.0",
                        "content_source_snapshot_receipt": receipt_body,
                    },
                )

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCE_SNAPSHOT_RECEIPT_ID_REUSED", result.stdout)

    def test_validator_marks_unavailable_receipt_as_unverified_without_accepting_snapshot_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace, _ = self.make_workspace(Path(tmp))
            observation_reference = (
                "03-内容原始回答/candidate/CASE-001.envelope.json"
                "#/semantic_content_raw_answer/source_observations/0"
            )
            receipt_body = {
                "receipt_id": "SNAPSHOT-OBS-001",
                "observation_id": "OBS-001",
                "source_observation_reference": observation_reference,
                "receiver_snapshot_reference": None,
                "receiver_snapshot_sha256": None,
                "snapshot_capture_state": "unavailable",
                "snapshot_captured_at": "2026-08-25T09:30:00+08:00",
                "receipt_sha256": None,
            }
            receipt_body["receipt_sha256"] = canonical_sha256(
                {**receipt_body, "receipt_sha256": None}
            )
            receipt_reference = "05-证据包/source-snapshot-receipts/OBS-001.receipt.json"
            write_json(
                workspace / receipt_reference,
                {
                    "schema_version": "1.0",
                    "content_source_snapshot_receipt": receipt_body,
                },
            )
            observation = {
                "source_url_or_null": "https://example.invalid/source",
                "publisher_or_null": "Example",
                "title_or_null": "Title",
                "original_location_or_null": None,
                "bounded_summary_or_null": None,
                "access_state": "UNVERIFIED",
                "conditions": [],
                "limitations": ["capture unavailable"],
                "counterevidence": [],
            }
            self.attach_source_observation_and_receipt(
                workspace, observation, receipt_reference
            )

            result = run(VALIDATE, str(workspace), "--format", "json")

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "UNVERIFIED")
            self.assertEqual(report["unverified_source_observation_ids"], ["OBS-001"])

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

    def test_content_workspace_initializer_uses_explicit_r4_arms_without_downgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            map_root = parent / "industry-map"
            map_root.mkdir()
            contract_path = parent / "r4-contract.json"
            write_json(contract_path, self.content_contract(r4_methods=True))

            created = run(
                INIT_CONTENT_WORKSPACE,
                "--map-root", str(map_root),
                "--contract", str(contract_path),
            )

            self.assertEqual(created.returncode, 0, created.stderr + created.stdout)
            workspace = map_root / "05-工作区" / "行业语义研究" / "CONTENT-RC2-001"
            self.assertTrue(
                (workspace / "03-内容原始回答/baseline_full_depth_v1").is_dir()
            )
            self.assertTrue(
                (workspace / "03-内容原始回答/screen_then_expand_v2").is_dir()
            )
            self.assertFalse(
                (workspace / "03-内容原始回答/candidate_screen_then_expand").exists()
            )

        for mutation in (
            "missing_arm",
            "unknown_marker",
            "r4_version_disguised_as_legacy",
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                map_root = parent / "industry-map"
                map_root.mkdir()
                contract = self.content_contract(r4_methods=True)
                body = contract["semantic_research_contract"]
                if mutation == "missing_arm":
                    body.pop("candidate_method_contract")
                elif mutation == "unknown_marker":
                    body["content_first_policy"][
                        "truth_scorecard_contract_version"
                    ] = "2.0-r4-unknown"
                else:
                    body["contract_version"] = "2.1.0-content-first.final.1"
                    body["content_first_policy"][
                        "truth_scorecard_contract_version"
                    ] = "1.0-legacy"
                    body["baseline_method_contract"] = "baseline_full_depth"
                    body["candidate_method_contract"] = (
                        "candidate_screen_then_expand"
                    )
                contract_path = parent / "invalid-contract.json"
                write_json(contract_path, contract)

                result = run(
                    INIT_CONTENT_WORKSPACE,
                    "--map-root", str(map_root),
                    "--contract", str(contract_path),
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(
                    (
                        map_root
                        / "05-工作区"
                        / "行业语义研究"
                        / "CONTENT-RC2-001"
                    ).exists()
                )

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

    def test_r4_arm_template_declares_auditable_resource_and_stability_fields(self):
        payload = json.loads(ARM_TEMPLATE.read_text(encoding="utf-8"))
        arm = payload["semantic_content_calibration_arm"]
        self.assertEqual(arm["calibration_contract_marker"], "2.0-r4")
        self.assertEqual(arm["method_arm"], "screen_then_expand_v2")
        self.assertIn("paired_task_manifest_reference_and_hash", arm)
        self.assertIn("query_count", arm)
        self.assertIn("source_open_count", arm)
        self.assertIn("stability_task_manifest_reference_and_hash", arm)
        self.assertIn("stability_repeat_receipts", arm)
        case = arm["case_evidence"][0]
        self.assertIn("task_id", case)
        self.assertIn("task_sha256", case)
        self.assertIn("critical_dispositions", case)
        self.assertIn("resource_observation_reference", case)
        self.assertIn("resource_observation_receipt_reference", case)

    def test_r4_evaluator_passes_exact_efficiency_thresholds_after_critical_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(parent)

            result, output = self.evaluate_r4(
                parent, baseline, candidate, "report.json", *trusted_args
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_result"], "PASS")
            self.assertEqual(report["content_method_state"], "CONTENT_CALIBRATION_PASS")
            self.assertEqual(report["gate_order"], [
                "safety",
                "known_positive_recall",
                "receiver_evidence_completeness",
                "stability",
                "efficiency",
            ])
            self.assertNotIn("EFFECTIVE", json.dumps(report))

    def test_r4_evaluator_stops_at_missing_stability_before_efficiency(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(
                parent,
                candidate_deep=33,
                candidate_queries=112,
                candidate_opens=81,
                include_repeats=False,
            )

            result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_result"], "INCOMPLETE")
            self.assertIn("six stability repeats are incomplete", report["reasons"])
            self.assertEqual(report["efficiency_gate_state"], "NOT_EVALUATED")
            self.assertIsNone(report["candidate_query_count"])

    def test_r4_evaluator_fails_all_hidden_work_efficiency_gates_after_stability(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(
                parent, candidate_deep=33, candidate_queries=111, candidate_opens=81
            )

            result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_result"], "FAIL")
            self.assertIn("deep expansion reduction is below the frozen threshold", report["reasons"])
            self.assertIn("query count increase exceeds 10 percent", report["reasons"])
            self.assertIn("source-open count exceeds baseline", report["reasons"])

    def test_r4_evaluator_recomputes_resource_totals_instead_of_trusting_top_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(parent)
            candidate["semantic_content_calibration_arm"]["query_count"] = 1

            result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_result"], "INCOMPLETE")
            self.assertIn("resource totals do not match receiver-owned observations", report["reasons"])

    def test_r4_evaluator_rejects_duplicate_or_cross_arm_resource_observations(self):
        for mutation in ("duplicate", "borrow_baseline"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(parent)
                source = (
                    candidate["semantic_content_calibration_arm"]["case_evidence"][0]
                    if mutation == "duplicate"
                    else baseline["semantic_content_calibration_arm"]["case_evidence"][0]
                )
                target = candidate["semantic_content_calibration_arm"]["case_evidence"][1]
                for prefix in (
                    "resource_observation",
                    "resource_observation_receipt",
                ):
                    target[f"{prefix}_reference"] = source[f"{prefix}_reference"]
                    target[f"{prefix}_sha256"] = source[f"{prefix}_sha256"]

                result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

                self.assertNotEqual(result.returncode, 0)
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(report["evaluation_result"], "INCOMPLETE")
                self.assertEqual(report["evaluation_result"], "INCOMPLETE")

    def test_r4_evaluator_rejects_same_open_record_counted_by_two_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, paths = self.real_r4_evaluation_fixture(parent)
            candidate_body = candidate["semantic_content_calibration_arm"]
            row = candidate_body["case_evidence"][0]
            observation_path = paths["workspace"] / row[
                "resource_observation_reference"
            ]
            observation_payload = json.loads(
                observation_path.read_text(encoding="utf-8")
            )
            observation = observation_payload["content_resource_observation"]
            repeated = observation["queries"][0]["opened_source_references"][0]
            observation["queries"][1]["observed_result_references"].append(repeated)
            observation["queries"][1]["opened_source_references"].append(repeated)
            observation["queries"][1]["access_outcomes"].append(
                {"source_reference": repeated, "access_state": "opened"}
            )
            observation["queries"][1]["inspected_result_count"] += 1
            observation["source_open_count"] += 1
            observation["observation_sha256"] = canonical_sha256(
                {**observation, "observation_sha256": None}
            )
            write_json(observation_path, observation_payload)
            observation_file_hash = hashlib.sha256(
                observation_path.read_bytes()
            ).hexdigest()
            row["resource_observation_sha256"] = observation_file_hash
            receipt_path = paths["workspace"] / row[
                "resource_observation_receipt_reference"
            ]
            receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt = receipt_payload["content_resource_observation_receipt"]
            receipt["resource_observation_sha256"] = observation_file_hash
            receipt["receipt_sha256"] = canonical_sha256(
                {**receipt, "receipt_sha256": None}
            )
            write_json(receipt_path, receipt_payload)
            row["resource_observation_receipt_sha256"] = hashlib.sha256(
                receipt_path.read_bytes()
            ).hexdigest()
            candidate_body["source_open_count"] += 1

            result, output = self.evaluate_r4(
                parent, baseline, candidate, "report.json", *trusted_args
            )

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_result"], "INCOMPLETE")
            self.assertIn("record is reused", report["reasons"][0])

    def test_r4_evaluator_requires_exact_shared_fourteen_positive_ids(self):
        for mutation in ("thirteen", "candidate_different", "entered_missing"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(parent)
                baseline_body = baseline["semantic_content_calibration_arm"]
                candidate_body = candidate["semantic_content_calibration_arm"]
                if mutation == "thirteen":
                    baseline_body["known_positive_case_ids"] = baseline_body["known_positive_case_ids"][:13]
                elif mutation == "candidate_different":
                    candidate_body["known_positive_case_ids"][-1] = "CASE-015"
                else:
                    candidate_body["known_positive_entered_expansion_case_ids"] = candidate_body[
                        "known_positive_entered_expansion_case_ids"
                    ][:-1]

                result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

                self.assertNotEqual(result.returncode, 0)
                report = json.loads(output.read_text(encoding="utf-8"))
                expected = "FAIL" if mutation == "entered_missing" else "INCOMPLETE"
                self.assertEqual(report["evaluation_result"], expected)

    def test_r4_evaluator_rejects_repeat_alias_and_id_only_receipt_copy(self):
        for mutation in ("alias", "id_only_copy"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                baseline, candidate, trusted_args, paths = self.real_r4_evaluation_fixture(parent)
                candidate_body = candidate["semantic_content_calibration_arm"]
                refs = candidate_body["stability_repeat_receipts"]
                if mutation == "alias":
                    refs[1] = dict(refs[0])
                else:
                    first_path = paths["workspace"] / refs[0]["reference"]
                    path = paths["workspace"] / refs[1]["reference"]
                    receipt = json.loads(first_path.read_text(encoding="utf-8"))
                    body = receipt["content_first_stability_repeat_receipt"]
                    body["receipt_id"] = "STABILITY-RECEIPT-COPIED-ID"
                    body["receipt_sha256"] = canonical_sha256(
                        {**body, "receipt_sha256": None}
                    )
                    write_json(path, receipt)
                    refs[1]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()

                result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

                self.assertNotEqual(result.returncode, 0)
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(report["evaluation_result"], "INCOMPLETE")

    def test_r4_evaluator_rejects_shared_repeat_authorization_or_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(
                parent, repeat_context_collision=True
            )

            result, output = self.evaluate_r4(
                parent, baseline, candidate, "report.json", *trusted_args
            )

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_result"], "INCOMPLETE")
            self.assertIn("independent", report["reasons"][0])

    def test_r4_evaluator_prioritizes_critical_failure_over_efficiency(self):
        for failing_arm in ("baseline", "candidate"):
            with self.subTest(failing_arm=failing_arm), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(
                    parent, candidate_deep=40, candidate_queries=140, candidate_opens=100
                )
                target = baseline if failing_arm == "baseline" else candidate
                target["semantic_content_calibration_arm"]["safety_failures"] = [
                    "fixture safety failure"
                ]

                result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

                self.assertNotEqual(result.returncode, 0)
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(report["evaluation_result"], "FAIL")
                self.assertEqual(report["reasons"], ["critical safety gate failed"])

    def test_r4_evaluator_prioritizes_safety_before_positive_recall(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(parent)
            baseline["semantic_content_calibration_arm"]["safety_failures"] = [
                "fixture safety failure"
            ]
            candidate["semantic_content_calibration_arm"][
                "known_positive_entered_expansion_case_ids"
            ] = candidate["semantic_content_calibration_arm"][
                "known_positive_entered_expansion_case_ids"
            ][:-1]

            result, output = self.evaluate_r4(
                parent, baseline, candidate, "report.json", *trusted_args
            )

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_result"], "FAIL")
            self.assertEqual(report["reasons"], ["critical safety gate failed"])
            self.assertEqual(report["efficiency_gate_state"], "NOT_EVALUATED")

    def test_r4_evaluator_refuses_existing_output_and_cleans_atomic_test_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(parent)
            sentinel = parent / "sentinel-report.json"
            sentinel.write_text("keep", encoding="utf-8")
            refused, _ = self.evaluate_r4(parent, baseline, candidate, sentinel.name, *trusted_args)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

            failed, output = self.evaluate_r4(
                parent,
                baseline,
                candidate,
                "atomic-report.json",
                *trusted_args,
                "--test-fail-before-publish",
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(output.exists())
            self.assertEqual(list(parent.glob(".atomic-report.json.*.tmp")), [])

    def test_r4_evaluator_cannot_relax_frozen_thresholds_from_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(
                parent, candidate_deep=40, candidate_queries=140, candidate_opens=80
            )

            result, output = self.evaluate_r4(
                parent,
                baseline,
                candidate,
                "relaxed.json",
                *trusted_args,
                "--minimum-reduction",
                "0",
                "--maximum-query-increase",
                ".99",
            )

            self.assertNotEqual(result.returncode, 0)
            if output.exists():
                self.assertNotEqual(
                    json.loads(output.read_text(encoding="utf-8"))["evaluation_result"],
                    "PASS",
                )

    def test_r4_evaluator_does_not_accept_summary_selected_positive_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(parent)
            arbitrary = [f"CASE-{index:03d}" for index in range(15, 29)]
            for payload in (baseline, candidate):
                payload["semantic_content_calibration_arm"]["known_positive_case_ids"] = arbitrary
            candidate["semantic_content_calibration_arm"][
                "known_positive_entered_expansion_case_ids"
            ] = arbitrary
            result, _ = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

            self.assertNotEqual(result.returncode, 0)

    def test_r4_early_gate_report_does_not_expose_unevaluated_efficiency(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(
                parent, candidate_deep=33, candidate_queries=112, candidate_opens=81,
                include_repeats=False,
            )

            result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["efficiency_gate_state"], "NOT_EVALUATED")
            for key in (
                "baseline_query_count",
                "candidate_query_count",
                "baseline_source_open_count",
                "candidate_source_open_count",
                "baseline_deep_expansion_count",
                "candidate_deep_expansion_count",
                "deep_expansion_reduction",
            ):
                self.assertIsNone(report[key])

    def test_r4_malformed_positive_collection_returns_atomic_incomplete_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, _ = self.real_r4_evaluation_fixture(parent)
            candidate["semantic_content_calibration_arm"]["known_positive_case_ids"] = [
                {"not": "a string"},
                *[f"CASE-{index:03d}" for index in range(2, 15)],
            ]
            result, output = self.evaluate_r4(parent, baseline, candidate, "report.json", *trusted_args)

            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(output.is_file())
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["evaluation_result"],
                "INCOMPLETE",
            )

    def test_r4_evaluator_opens_real_tasks_and_rejects_summary_artifact_reuse(self):
        for mutation in ("task_tamper", "all_summary_artifacts_reused"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                baseline, candidate, trusted_args, paths = self.real_r4_evaluation_fixture(parent)
                if mutation == "task_tamper":
                    task_ref = candidate["semantic_content_calibration_arm"]["case_evidence"][0][
                        "task_reference"
                    ]
                    task_path = paths["workspace"] / task_ref
                    task_path.write_bytes(task_path.read_bytes() + b"\n")
                else:
                    source = candidate["semantic_content_calibration_arm"]["case_evidence"][0]
                    target = candidate["semantic_content_calibration_arm"]["case_evidence"][1]
                    for prefix in (
                        "task",
                        "raw_envelope",
                        "raw_response",
                        "scorecard",
                        "resource_observation",
                        "resource_observation_receipt",
                    ):
                        if f"{prefix}_reference" in source:
                            target[f"{prefix}_reference"] = source[f"{prefix}_reference"]
                        target[f"{prefix}_sha256"] = source[f"{prefix}_sha256"]

                result, output = self.evaluate_r4(
                    parent, baseline, candidate, "report.json", *trusted_args
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(
                    json.loads(output.read_text(encoding="utf-8"))["evaluation_result"],
                    "INCOMPLETE",
                )

    def test_r4_stability_recomputes_repeat_scorecard_critical_dispositions(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            baseline, candidate, trusted_args, paths = self.real_r4_evaluation_fixture(parent)
            ref = candidate["semantic_content_calibration_arm"]["stability_repeat_receipts"][0]
            receipt_path = paths["workspace"] / ref["reference"]
            receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt = receipt_payload["content_first_stability_repeat_receipt"]
            score_path = paths["workspace"] / receipt["scorecard_reference"]
            score_payload = json.loads(score_path.read_text(encoding="utf-8"))
            score = score_payload["semantic_content_scorecard"]
            score["scoring_items"]["safety_boundary"]["score"] = 0
            score["content_score_result"] = "FAIL"
            score["scorecard_sha256"] = canonical_sha256(
                {**score, "scorecard_sha256": None}
            )
            write_json(score_path, score_payload)
            receipt["scorecard_sha256"] = hashlib.sha256(score_path.read_bytes()).hexdigest()
            receipt["receipt_sha256"] = canonical_sha256(
                {**receipt, "receipt_sha256": None}
            )
            write_json(receipt_path, receipt_payload)
            ref["sha256"] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()

            result, output = self.evaluate_r4(
                parent, baseline, candidate, "report.json", *trusted_args
            )

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_result"], "FAIL")
            self.assertIn("stability critical dispositions are inconsistent", report["reasons"])
            self.assertEqual(report["efficiency_gate_state"], "NOT_EVALUATED")

    def test_r4_evaluator_rejects_task6_scorecard_schema_weakening(self):
        for mutation in ("wrong_reviewer", "null_reason", "empty_refs", "empty_dims"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                baseline, candidate, trusted_args, paths = self.real_r4_evaluation_fixture(parent)
                row = candidate["semantic_content_calibration_arm"]["case_evidence"][0]
                score_path = paths["workspace"] / row["scorecard_reference"]
                score_payload = json.loads(score_path.read_text(encoding="utf-8"))
                score = score_payload["semantic_content_scorecard"]
                item = score["scoring_items"]["taxonomy_and_scope_grounding"]
                if mutation == "wrong_reviewer":
                    item["responsibility"] = "wrong_reviewer"
                elif mutation == "null_reason":
                    item["reason"] = None
                elif mutation == "empty_refs":
                    item["evidence_references"] = []
                else:
                    score["equivalent_source_dimensions"] = {}
                score["scorecard_sha256"] = canonical_sha256(
                    {**score, "scorecard_sha256": None}
                )
                write_json(score_path, score_payload)
                row["scorecard_sha256"] = hashlib.sha256(
                    score_path.read_bytes()
                ).hexdigest()

                result, output = self.evaluate_r4(
                    parent, baseline, candidate, "report.json", *trusted_args
                )

                self.assertNotEqual(result.returncode, 0)
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(report["evaluation_result"], "INCOMPLETE")

    def test_r4_evaluator_rejects_wrong_contract_and_open_schema_run_artifacts(self):
        mutations = (
            "raw_contract",
            "resource_contract",
            "preauth_contract",
            "preauth_version",
            "preauth_blank_auth",
            "preauth_invalid_time",
            "preauth_extra_field",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                baseline, candidate, trusted_args, paths = self.real_r4_evaluation_fixture(parent)
                row = candidate["semantic_content_calibration_arm"]["case_evidence"][0]
                workspace = paths["workspace"]
                if mutation == "raw_contract":
                    envelope_path = workspace / row["raw_envelope_reference"]
                    envelope_payload = json.loads(envelope_path.read_text(encoding="utf-8"))
                    envelope = envelope_payload["semantic_content_raw_answer"]
                    envelope["research_contract_id"] = "OTHER-CONTRACT"
                    envelope["envelope_sha256"] = canonical_sha256(
                        {**envelope, "envelope_sha256": None}
                    )
                    write_json(envelope_path, envelope_payload)
                    envelope_hash = hashlib.sha256(envelope_path.read_bytes()).hexdigest()
                    row["raw_envelope_sha256"] = envelope_hash
                    score_path = workspace / row["scorecard_reference"]
                    score_payload = json.loads(score_path.read_text(encoding="utf-8"))
                    score = score_payload["semantic_content_scorecard"]
                    score["raw_answer_sha256"] = envelope_hash
                    score["scorecard_sha256"] = canonical_sha256(
                        {**score, "scorecard_sha256": None}
                    )
                    write_json(score_path, score_payload)
                    row["scorecard_sha256"] = hashlib.sha256(
                        score_path.read_bytes()
                    ).hexdigest()
                elif mutation == "resource_contract":
                    observation_path = workspace / row["resource_observation_reference"]
                    observation_payload = json.loads(
                        observation_path.read_text(encoding="utf-8")
                    )
                    observation = observation_payload["content_resource_observation"]
                    observation["research_contract_id"] = "OTHER-CONTRACT"
                    observation["observation_sha256"] = canonical_sha256(
                        {**observation, "observation_sha256": None}
                    )
                    write_json(observation_path, observation_payload)
                    observation_hash = hashlib.sha256(
                        observation_path.read_bytes()
                    ).hexdigest()
                    row["resource_observation_sha256"] = observation_hash
                    receipt_path = workspace / row[
                        "resource_observation_receipt_reference"
                    ]
                    receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
                    receipt = receipt_payload["content_resource_observation_receipt"]
                    receipt["resource_observation_sha256"] = observation_hash
                    receipt["receipt_sha256"] = canonical_sha256(
                        {**receipt, "receipt_sha256": None}
                    )
                    write_json(receipt_path, receipt_payload)
                    row["resource_observation_receipt_sha256"] = hashlib.sha256(
                        receipt_path.read_bytes()
                    ).hexdigest()
                else:
                    receipt_path = workspace / row[
                        "resource_observation_receipt_reference"
                    ]
                    receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
                    receipt = receipt_payload["content_resource_observation_receipt"]
                    preauth_path = workspace / receipt["preauthorization_reference"]
                    preauth_payload = json.loads(preauth_path.read_text(encoding="utf-8"))
                    preauth = preauth_payload[
                        "receiver_resource_observation_preauthorization"
                    ]
                    if mutation == "preauth_contract":
                        preauth["research_contract_id"] = "OTHER-CONTRACT"
                    elif mutation == "preauth_version":
                        preauth["contract_version"] = "WRONG-VERSION"
                    elif mutation == "preauth_blank_auth":
                        preauth["authorization_id"] = ""
                    elif mutation == "preauth_invalid_time":
                        preauth["authorized_at"] = "not-a-time"
                    else:
                        preauth["unexpected"] = True
                    write_json(preauth_path, preauth_payload)
                    receipt["preauthorization_sha256"] = hashlib.sha256(
                        preauth_path.read_bytes()
                    ).hexdigest()
                    receipt["receipt_sha256"] = canonical_sha256(
                        {**receipt, "receipt_sha256": None}
                    )
                    write_json(receipt_path, receipt_payload)
                    row["resource_observation_receipt_sha256"] = hashlib.sha256(
                        receipt_path.read_bytes()
                    ).hexdigest()

                result, output = self.evaluate_r4(
                    parent, baseline, candidate, "report.json", *trusted_args
                )

                self.assertNotEqual(result.returncode, 0)
                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(report["evaluation_result"], "INCOMPLETE")

    def test_r4_resource_counts_reject_bool_and_handle_huge_inspection_integer(self):
        for mutation in ("bool", "huge"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                baseline, candidate, trusted_args, paths = self.real_r4_evaluation_fixture(parent)
                row = candidate["semantic_content_calibration_arm"]["case_evidence"][0]
                if mutation == "bool":
                    candidate["semantic_content_calibration_arm"]["query_count"] = True
                    expected = "INCOMPLETE"
                else:
                    observation_path = paths["workspace"] / row[
                        "resource_observation_reference"
                    ]
                    observation_payload = json.loads(
                        observation_path.read_text(encoding="utf-8")
                    )
                    observation = observation_payload["content_resource_observation"]
                    observation["queries"][0]["inspected_result_count"] = 10**1000
                    observation["observation_sha256"] = canonical_sha256(
                        {**observation, "observation_sha256": None}
                    )
                    write_json(observation_path, observation_payload)
                    observation_file_hash = hashlib.sha256(
                        observation_path.read_bytes()
                    ).hexdigest()
                    row["resource_observation_sha256"] = observation_file_hash
                    resource_receipt_path = paths["workspace"] / row[
                        "resource_observation_receipt_reference"
                    ]
                    resource_receipt_payload = json.loads(
                        resource_receipt_path.read_text(encoding="utf-8")
                    )
                    resource_receipt = resource_receipt_payload[
                        "content_resource_observation_receipt"
                    ]
                    resource_receipt["resource_observation_sha256"] = observation_file_hash
                    resource_receipt["receipt_sha256"] = canonical_sha256(
                        {**resource_receipt, "receipt_sha256": None}
                    )
                    write_json(resource_receipt_path, resource_receipt_payload)
                    row["resource_observation_receipt_sha256"] = hashlib.sha256(
                        resource_receipt_path.read_bytes()
                    ).hexdigest()
                    expected = "INCOMPLETE"

                result, output = self.evaluate_r4(
                    parent, baseline, candidate, "report.json", *trusted_args
                )

                report = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(report["evaluation_result"], expected)
                self.assertEqual(result.returncode, 0 if expected == "PASS" else 1)
                if mutation == "huge":
                    self.assertIn(
                        "inspected-result count does not match exact records",
                        report["reasons"][0],
                    )

    def test_stability_task_freezer_is_create_only_atomic_and_workspace_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            _, _, trusted_args, paths = self.real_r4_evaluation_fixture(parent)
            workspace = paths["workspace"]
            common = [
                "--workspace", str(workspace),
                "--contract", str(paths["contract"]),
                "--expected-final-contract-sha256", hashlib.sha256(paths["contract"].read_bytes()).hexdigest(),
                "--formal-case-set", str(paths["cases"]),
                "--expected-formal-case-set-sha256", hashlib.sha256(paths["cases"].read_bytes()).hexdigest(),
                "--paired-task-manifest", str(paths["manifest"]),
                "--expected-paired-task-manifest-sha256", hashlib.sha256(paths["manifest"].read_bytes()).hexdigest(),
                "--authorization-id-prefix", "RECEIVER-SECOND",
                "--authorized-at", "2026-08-25T08:00:00+08:00",
            ]
            existing = workspace / "stability-package"
            refused = run(FREEZE_STABILITY, *common, "--output", str(existing))
            self.assertNotEqual(refused.returncode, 0)
            self.assertTrue((existing / "stability-task-manifest.json").is_file())

            failed_output = workspace / "stability-failed"
            failed = run(
                FREEZE_STABILITY,
                *common,
                "--output", str(failed_output),
                "--test-fail-after-file-count", "2",
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(failed_output.exists())
            self.assertEqual(list(workspace.glob(".stability-failed.staging-*")), [])

            escaped = run(
                FREEZE_STABILITY,
                *common,
                "--output", str(parent / "outside-stability"),
            )
            self.assertNotEqual(escaped.returncode, 0)

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
            paths, args = self.full_gate_fixture(parent)
            output_path = parent / "gate.json"
            allowed = run(FULL_GATE, *args, "--output", str(output_path))
            self.assertEqual(allowed.returncode, 0, allowed.stderr + allowed.stdout)
            gate = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(gate["content_full_screening_state"], "AUTHORIZED_NOT_STARTED")
            self.assertEqual(gate["downstream_release_state"], "RESEARCH_ONLY_BLOCKED")
            self.assertFalse(gate["runs_nodes"])
            contract = json.loads(paths["contract"].read_text(encoding="utf-8"))[
                "semantic_research_contract"
            ]
            self.assertFalse(contract["full_screening_authorization"])
            self.assertIsNone(contract["full_screening_authorization_reference"])

    def test_full_scope_gate_rejects_legacy_minimal_three_file_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            contract_path = parent / "contract.json"
            report_path = parent / "minimal-report.json"
            output_path = parent / "gate.json"
            write_json(contract_path, self.content_contract(authorized=True))
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

            result = run(
                FULL_GATE,
                "--contract", str(contract_path),
                "--calibration-report", str(report_path),
                "--output", str(output_path),
            )

            self.assertNotEqual(result.returncode, 0)
            if output_path.exists():
                self.assertNotEqual(
                    json.loads(output_path.read_text(encoding="utf-8"))[
                        "content_full_screening_state"
                    ],
                    "AUTHORIZED_NOT_STARTED",
                )

    def test_full_scope_gate_rejects_incomplete_or_misbound_r4_chain(self):
        mutations = (
            "changed_manifest",
            "null_manifest_contract",
            "minimal_report",
            "wrong_report_expected_hash",
            "wrong_report_contract_hash",
            "non_r4_report",
            "old_contract_arms",
            "contract_self_authorized",
            "missing_receipt",
            "misbound_receipt",
            "receipt_extra_field",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                paths, args = self.full_gate_fixture(parent)
                if mutation == "changed_manifest":
                    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
                    manifest["terminal_node_ids"].append("GB-T-4754-NODE-003")
                    write_json(paths["manifest"], manifest)
                elif mutation == "null_manifest_contract":
                    contract = json.loads(paths["contract"].read_text(encoding="utf-8"))
                    contract["semantic_research_contract"][
                        "terminal_node_manifest_sha256"
                    ] = None
                    write_json(paths["contract"], contract)
                elif mutation == "minimal_report":
                    write_json(
                        paths["report"],
                        {
                            "schema_version": "2.0-r4",
                            "content_method_state": "CONTENT_CALIBRATION_PASS",
                            "safety_failures": [],
                        },
                    )
                    args[args.index("--expected-calibration-report-sha256") + 1] = (
                        hashlib.sha256(paths["report"].read_bytes()).hexdigest()
                    )
                elif mutation == "wrong_report_expected_hash":
                    args[args.index("--expected-calibration-report-sha256") + 1] = "f" * 64
                elif mutation in {"wrong_report_contract_hash", "non_r4_report"}:
                    report = json.loads(paths["report"].read_text(encoding="utf-8"))
                    if mutation == "wrong_report_contract_hash":
                        report["final_contract_sha256"] = "f" * 64
                    else:
                        report["schema_version"] = "1.0-legacy"
                    write_json(paths["report"], report)
                    args[args.index("--expected-calibration-report-sha256") + 1] = (
                        hashlib.sha256(paths["report"].read_bytes()).hexdigest()
                    )
                elif mutation in {"old_contract_arms", "contract_self_authorized"}:
                    contract = json.loads(paths["contract"].read_text(encoding="utf-8"))
                    body = contract["semantic_research_contract"]
                    if mutation == "old_contract_arms":
                        body["baseline_method_contract"] = "baseline_full_depth"
                        body["candidate_method_contract"] = "candidate_screen_then_expand"
                    else:
                        body["full_screening_authorization"] = True
                        body["full_screening_authorization_reference"] = "FORGED-IN-CONTRACT"
                    write_json(paths["contract"], contract)
                    new_contract_hash = hashlib.sha256(
                        paths["contract"].read_bytes()
                    ).hexdigest()
                    args[args.index("--expected-final-contract-sha256") + 1] = (
                        new_contract_hash
                    )
                    if mutation == "contract_self_authorized":
                        report = json.loads(paths["report"].read_text(encoding="utf-8"))
                        report["final_contract_sha256"] = new_contract_hash
                        write_json(paths["report"], report)
                        new_report_hash = hashlib.sha256(
                            paths["report"].read_bytes()
                        ).hexdigest()
                        args[args.index("--expected-calibration-report-sha256") + 1] = (
                            new_report_hash
                        )
                        receipt_payload = json.loads(
                            paths["receipt"].read_text(encoding="utf-8")
                        )
                        receipt = receipt_payload[
                            "content_first_full_screening_authorization_receipt"
                        ]
                        receipt["final_contract_sha256"] = new_contract_hash
                        receipt["calibration_report_sha256"] = new_report_hash
                        receipt["receipt_sha256"] = canonical_sha256(
                            {**receipt, "receipt_sha256": None}
                        )
                        write_json(paths["receipt"], receipt_payload)
                        args[args.index("--expected-authorization-receipt-sha256") + 1] = (
                            hashlib.sha256(paths["receipt"].read_bytes()).hexdigest()
                        )
                elif mutation == "missing_receipt":
                    paths["receipt"].unlink()
                else:
                    receipt_payload = json.loads(
                        paths["receipt"].read_text(encoding="utf-8")
                    )
                    receipt = receipt_payload[
                        "content_first_full_screening_authorization_receipt"
                    ]
                    if mutation == "misbound_receipt":
                        receipt["calibration_report_sha256"] = "f" * 64
                    else:
                        receipt["unexpected"] = True
                    receipt["receipt_sha256"] = canonical_sha256(
                        {**receipt, "receipt_sha256": None}
                    )
                    write_json(paths["receipt"], receipt_payload)
                    args[args.index("--expected-authorization-receipt-sha256") + 1] = (
                        hashlib.sha256(paths["receipt"].read_bytes()).hexdigest()
                    )

                output_path = parent / "gate.json"
                result = run(FULL_GATE, *args, "--output", str(output_path))

                self.assertNotEqual(result.returncode, 0)
                if output_path.exists():
                    self.assertNotEqual(
                        json.loads(output_path.read_text(encoding="utf-8"))[
                            "content_full_screening_state"
                        ],
                        "AUTHORIZED_NOT_STARTED",
                    )

    def test_full_scope_gate_refuses_overwrite_and_cleans_atomic_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            _, args = self.full_gate_fixture(parent)
            existing = parent / "existing.json"
            existing.write_text("keep", encoding="utf-8")
            refused = run(FULL_GATE, *args, "--output", str(existing))
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(existing.read_text(encoding="utf-8"), "keep")

            output = parent / "atomic.json"
            failed = run(
                FULL_GATE,
                *args,
                "--output", str(output),
                "--test-fail-before-publish",
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(output.exists())
            self.assertEqual(list(parent.glob(".atomic.json.*.tmp")), [])

    def test_full_coverage_requires_every_frozen_node_and_stays_research_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            paths, gate_args = self.full_gate_fixture(parent)
            gate_path = paths["workspace"] / "07-报告" / "full-screen-gate.json"
            gate_result = run(
                FULL_GATE, *gate_args, "--output", str(gate_path)
            )
            self.assertEqual(
                gate_result.returncode, 0, gate_result.stderr + gate_result.stdout
            )
            gate_hash = hashlib.sha256(gate_path.read_bytes()).hexdigest()
            calibration_report_hash = hashlib.sha256(
                paths["report"].read_bytes()
            ).hexdigest()
            index_path = parent / "screening-index.json"
            output_path = parent / "coverage.json"
            contract = json.loads(paths["contract"].read_text(encoding="utf-8"))[
                "semantic_research_contract"
            ]
            manifest_hash = hashlib.sha256(paths["manifest"].read_bytes()).hexdigest()
            manifest_node_ids = json.loads(
                paths["manifest"].read_text(encoding="utf-8")
            )["terminal_node_ids"]

            def index(node_ids: list[str]) -> dict:
                return {
                    "semantic_content_full_screening_index": {
                        "research_contract_id": "CONTENT-RC2-001",
                        "contract_version": contract["contract_version"],
                        "terminal_node_manifest_sha256": manifest_hash,
                        "method_arm": "screen_then_expand_v2",
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

            write_json(index_path, index(manifest_node_ids[:1]))
            incomplete = run(
                FULL_COVERAGE,
                "--contract",
                str(paths["contract"]),
                "--terminal-node-manifest",
                str(paths["manifest"]),
                "--screening-index",
                str(index_path),
                "--full-screen-gate-report",
                str(gate_path),
                "--expected-full-screen-gate-report-sha256",
                gate_hash,
                "--calibration-report",
                str(paths["report"]),
                "--expected-calibration-report-sha256",
                calibration_report_hash,
                "--output",
                str(output_path),
            )
            self.assertNotEqual(incomplete.returncode, 0)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))["content_full_screening_state"],
                "COVERAGE_INCOMPLETE",
            )
            write_json(index_path, index(manifest_node_ids))
            output_path = parent / "coverage-ready.json"
            complete = run(
                FULL_COVERAGE,
                "--contract",
                str(paths["contract"]),
                "--terminal-node-manifest",
                str(paths["manifest"]),
                "--screening-index",
                str(index_path),
                "--full-screen-gate-report",
                str(gate_path),
                "--expected-full-screen-gate-report-sha256",
                gate_hash,
                "--calibration-report",
                str(paths["report"]),
                "--expected-calibration-report-sha256",
                calibration_report_hash,
                "--output",
                str(output_path),
            )
            self.assertEqual(complete.returncode, 0, complete.stderr + complete.stdout)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["content_full_screening_state"], "READY_FOR_REVERSE_AUDIT")
            self.assertTrue(report["requires_content_workspace_validation"])
            self.assertEqual(report["downstream_release_state"], "RESEARCH_ONLY_BLOCKED")

    def test_r4_full_coverage_rejects_old_arm_missing_or_misbound_gate(self):
        for mutation in (
            "old_arm",
            "missing_gate",
            "misbound_gate",
            "invalid_calibration_report_hash",
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                paths, gate_args = self.full_gate_fixture(parent)
                gate_path = paths["workspace"] / "07-报告" / "full-screen-gate.json"
                gate_result = run(
                    FULL_GATE, *gate_args, "--output", str(gate_path)
                )
                self.assertEqual(gate_result.returncode, 0)
                gate_hash = hashlib.sha256(gate_path.read_bytes()).hexdigest()
                calibration_report_hash = hashlib.sha256(
                    paths["report"].read_bytes()
                ).hexdigest()
                if mutation == "misbound_gate":
                    gate = json.loads(gate_path.read_text(encoding="utf-8"))
                    gate["final_contract_sha256"] = "f" * 64
                    write_json(gate_path, gate)
                    gate_hash = hashlib.sha256(gate_path.read_bytes()).hexdigest()
                elif mutation == "invalid_calibration_report_hash":
                    gate = json.loads(gate_path.read_text(encoding="utf-8"))
                    gate["calibration_report_sha256"] = ""
                    write_json(gate_path, gate)
                    gate_hash = hashlib.sha256(gate_path.read_bytes()).hexdigest()
                contract = json.loads(paths["contract"].read_text(encoding="utf-8"))[
                    "semantic_research_contract"
                ]
                manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
                index_path = parent / "screening-index.json"
                write_json(
                    index_path,
                    {
                        "semantic_content_full_screening_index": {
                            "research_contract_id": contract["research_contract_id"],
                            "contract_version": contract["contract_version"],
                            "terminal_node_manifest_sha256": contract[
                                "terminal_node_manifest_sha256"
                            ],
                            "method_arm": (
                                "candidate_screen_then_expand"
                                if mutation == "old_arm"
                                else "screen_then_expand_v2"
                            ),
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
                                for node_id in manifest["terminal_node_ids"]
                            ],
                        }
                    },
                )
                extra = []
                if mutation != "missing_gate":
                    extra = [
                        "--full-screen-gate-report", str(gate_path),
                        "--expected-full-screen-gate-report-sha256", gate_hash,
                    ]
                output_path = parent / "coverage.json"

                result = run(
                    FULL_COVERAGE,
                    "--contract", str(paths["contract"]),
                    "--terminal-node-manifest", str(paths["manifest"]),
                    "--screening-index", str(index_path),
                    "--calibration-report", str(paths["report"]),
                    "--expected-calibration-report-sha256",
                    calibration_report_hash,
                    *extra,
                    "--output", str(output_path),
                )

                self.assertNotEqual(result.returncode, 0)
                if output_path.exists():
                    self.assertEqual(
                        json.loads(output_path.read_text(encoding="utf-8"))[
                            "content_full_screening_state"
                        ],
                        "BLOCKED",
                    )

    def test_r4_full_coverage_reopens_and_validates_evaluator_report(self):
        mutations = (
            "deleted",
            "replaced",
            "wrong_expected_hash",
            "non_r4",
            "contract_binding_drift",
            "manifest_binding_drift",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                parent = Path(tmp)
                paths, gate_args = self.full_gate_fixture(parent)
                gate_path = paths["workspace"] / "07-报告" / "full-screen-gate.json"
                gate_result = run(FULL_GATE, *gate_args, "--output", str(gate_path))
                self.assertEqual(
                    gate_result.returncode,
                    0,
                    gate_result.stderr + gate_result.stdout,
                )
                gate_hash = hashlib.sha256(gate_path.read_bytes()).hexdigest()
                report_hash = hashlib.sha256(paths["report"].read_bytes()).hexdigest()
                if mutation == "deleted":
                    paths["report"].unlink()
                elif mutation == "replaced":
                    write_json(paths["report"], {"schema_version": "2.0-r4"})
                    report_hash = hashlib.sha256(paths["report"].read_bytes()).hexdigest()
                elif mutation == "wrong_expected_hash":
                    report_hash = "f" * 64
                elif mutation in {"non_r4", "contract_binding_drift"}:
                    report = json.loads(paths["report"].read_text(encoding="utf-8"))
                    if mutation == "non_r4":
                        report["schema_version"] = "1.0-legacy"
                    else:
                        report["final_contract_sha256"] = "f" * 64
                    write_json(paths["report"], report)
                    report_hash = hashlib.sha256(paths["report"].read_bytes()).hexdigest()
                else:
                    contract_payload = json.loads(
                        paths["contract"].read_text(encoding="utf-8")
                    )
                    contract = contract_payload["semantic_research_contract"]
                    contract["terminal_node_manifest_sha256"] = "f" * 64
                    write_json(paths["contract"], contract_payload)
                    contract_hash = hashlib.sha256(
                        paths["contract"].read_bytes()
                    ).hexdigest()
                    report = json.loads(paths["report"].read_text(encoding="utf-8"))
                    report["final_contract_sha256"] = contract_hash
                    write_json(paths["report"], report)
                    report_hash = hashlib.sha256(paths["report"].read_bytes()).hexdigest()
                    gate = json.loads(gate_path.read_text(encoding="utf-8"))
                    gate["final_contract_sha256"] = contract_hash
                    gate["calibration_report_sha256"] = report_hash
                    gate["terminal_node_manifest_sha256"] = "f" * 64
                    write_json(gate_path, gate)
                    gate_hash = hashlib.sha256(gate_path.read_bytes()).hexdigest()

                contract = json.loads(paths["contract"].read_text(encoding="utf-8"))[
                    "semantic_research_contract"
                ]
                manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
                index_path = parent / "screening-index.json"
                write_json(
                    index_path,
                    {
                        "semantic_content_full_screening_index": {
                            "research_contract_id": contract["research_contract_id"],
                            "contract_version": contract["contract_version"],
                            "terminal_node_manifest_sha256": contract[
                                "terminal_node_manifest_sha256"
                            ],
                            "method_arm": "screen_then_expand_v2",
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
                                for node_id in manifest["terminal_node_ids"]
                            ],
                        }
                    },
                )
                output_path = parent / "coverage.json"

                result = run(
                    FULL_COVERAGE,
                    "--contract", str(paths["contract"]),
                    "--terminal-node-manifest", str(paths["manifest"]),
                    "--screening-index", str(index_path),
                    "--full-screen-gate-report", str(gate_path),
                    "--expected-full-screen-gate-report-sha256", gate_hash,
                    "--calibration-report", str(paths["report"]),
                    "--expected-calibration-report-sha256", report_hash,
                    "--output", str(output_path),
                )

                self.assertNotEqual(result.returncode, 0)
                if output_path.exists():
                    self.assertEqual(
                        json.loads(output_path.read_text(encoding="utf-8"))[
                            "content_full_screening_state"
                        ],
                        "BLOCKED",
                    )

    def test_legacy_full_coverage_requires_explicit_legacy_marker_and_old_arm(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            manifest_path = parent / "terminal-nodes.json"
            write_json(manifest_path, {"terminal_node_ids": ["NODE-001"]})
            contract = self.content_contract(authorized=True)
            body = contract["semantic_research_contract"]
            body["terminal_node_count"] = 1
            body["terminal_node_manifest_reference"] = str(manifest_path)
            body["terminal_node_manifest_sha256"] = hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest()
            body["content_first_policy"]["content_full_screening_state"] = "IN_PROGRESS"
            contract_path = parent / "legacy-contract.json"
            write_json(contract_path, contract)
            index_path = parent / "legacy-index.json"
            write_json(
                index_path,
                {
                    "semantic_content_full_screening_index": {
                        "research_contract_id": body["research_contract_id"],
                        "contract_version": body["contract_version"],
                        "terminal_node_manifest_sha256": body[
                            "terminal_node_manifest_sha256"
                        ],
                        "method_arm": "candidate_screen_then_expand",
                        "node_evidence": [
                            {
                                "industry_node_id": "NODE-001",
                                "visible_input_sha256": "a" * 64,
                                "raw_response_sha256": "b" * 64,
                                "scorecard_sha256": "c" * 64,
                                "screening_result": "no_hypothesis_formed",
                                "semantic_work_state": "screened",
                                "evidence_state": "unknown",
                                "unknown_items_present": True,
                            }
                        ],
                    }
                },
            )
            output_path = parent / "legacy-coverage.json"

            result = run(
                FULL_COVERAGE,
                "--contract", str(contract_path),
                "--terminal-node-manifest", str(manifest_path),
                "--screening-index", str(index_path),
                "--output", str(output_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8"))[
                    "content_full_screening_state"
                ],
                "READY_FOR_REVERSE_AUDIT",
            )

    def test_r4_contract_version_cannot_disguise_itself_as_legacy_full_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            paths, _ = self.full_gate_fixture(parent)
            contract_payload = json.loads(
                paths["contract"].read_text(encoding="utf-8")
            )
            contract = contract_payload["semantic_research_contract"]
            policy = contract["content_first_policy"]
            policy["truth_scorecard_contract_version"] = "1.0-legacy"
            policy["content_method_state"] = "CONTENT_CALIBRATION_PASS"
            policy["content_full_screening_state"] = "IN_PROGRESS"
            contract["full_screening_authorization"] = True
            contract["full_screening_authorization_reference"] = "LEGACY-AUTH"
            contract.pop("baseline_method_contract")
            contract.pop("candidate_method_contract")
            write_json(paths["contract"], contract_payload)
            manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
            index_path = parent / "disguised-legacy-index.json"
            write_json(
                index_path,
                {
                    "semantic_content_full_screening_index": {
                        "research_contract_id": contract["research_contract_id"],
                        "contract_version": contract["contract_version"],
                        "terminal_node_manifest_sha256": contract[
                            "terminal_node_manifest_sha256"
                        ],
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
                            for node_id in manifest["terminal_node_ids"]
                        ],
                    }
                },
            )
            output_path = parent / "disguised-legacy-coverage.json"

            result = run(
                FULL_COVERAGE,
                "--contract", str(paths["contract"]),
                "--terminal-node-manifest", str(paths["manifest"]),
                "--screening-index", str(index_path),
                "--output", str(output_path),
            )

            self.assertNotEqual(result.returncode, 0)
            if output_path.exists():
                self.assertEqual(
                    json.loads(output_path.read_text(encoding="utf-8"))[
                        "content_full_screening_state"
                    ],
                    "BLOCKED",
                )


if __name__ == "__main__":
    unittest.main()
