import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = Path(
    os.environ.get("R4_CONTRACT_REPOSITORY_ROOT", DEFAULT_REPOSITORY_ROOT)
)
MAP_PLUGIN = REPOSITORY_ROOT / "plugins/industry-application-map-builder"
DIRECTOR_PLUGIN = REPOSITORY_ROOT / "plugins/foreign-trade-workflow-director"
SKILL_ROOT = MAP_PLUGIN / "skills/industry-application-map-builder"
INIT_PREP = SKILL_ROOT / "scripts/init_content_first_preparation_workspace.py"
VALIDATE_TERMS = SKILL_ROOT / "scripts/validate_terminology_bridge.py"
LOCK = SKILL_ROOT / "scripts/lock_semantic_case_preparation_contract.py"
FINALIZE = SKILL_ROOT / "scripts/finalize_semantic_research_contract.py"
FREEZE_VISIBLE = SKILL_ROOT / "scripts/freeze_content_first_visible_case_set.py"
VALIDATE_WORKSPACE = SKILL_ROOT / "scripts/validate_semantic_research_workspace.py"
BUILD_TASKS = SKILL_ROOT / "scripts/build_content_first_calibration_tasks.py"
EVALUATE_CONTENT = SKILL_ROOT / "scripts/evaluate_content_first_calibration.py"
FREEZE_STABILITY = SKILL_ROOT / "scripts/freeze_content_first_stability_tasks.py"
CALIBRATION_ARM_TEMPLATE = (
    SKILL_ROOT / "assets/content-first/content-calibration-arm.template.json"
)
RESOURCE_OBSERVATION_TEMPLATE = (
    SKILL_ROOT / "assets/content-first/content-resource-observation.template.json"
)
CONTENT_FIRST_CONTRACT = (
    SKILL_ROOT / "assets/content-first/content-first-research-contract.template.json"
)
TERM_TEMPLATE = SKILL_ROOT / "assets/content-first/terminology-bridge.template.jsonl"
PYTHON = Path(
    "/Users/lirongjing/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
)
CONTRACT_TEMPLATES = (
    MAP_PLUGIN
    / "skills/industry-application-map-builder/assets/semantic-method"
    / "research-contract.template.json",
    MAP_PLUGIN
    / "skills/industry-application-map-builder/assets/content-first"
    / "content-first-research-contract.template.json",
)

EXPECTED_TERMINOLOGY_ARCHITECTURE = {
    "global_skill_fixed_domain_terms_allowed": False,
    "case_specific_answer_terms_allowed_in_skill": False,
    "company_terms_allowed_in_semantic_screening": False,
    "concept_roles": [
        "industry_output",
        "material_form",
        "phase_relation",
        "process_action",
        "use_point",
        "exclusion",
    ],
    "term_pack_reference": None,
    "term_pack_sha256": None,
    "term_pack_state": "not_prepared",
    "dynamic_discovery_enabled": True,
}

EXPECTED_CALIBRATION_CASE_POLICY = {
    "formal_case_count": 40,
    "known_positive_count": 14,
    "development_case_ids_excluded_from_formal": [],
    "required_category_counts": {
        "direct_supported_positive": 8,
        "hidden_positive": 6,
        "misleading_name_similarity": 6,
        "source_sparse_or_inaccessible": 5,
        "ambiguous_or_incomplete_conditions": 5,
        "circular_or_mixed_company_source": 4,
        "empty_generalization": 3,
        "contamination_drift_or_structure_error": 3,
    },
    "selection_origin_counts": {
        "retained_r3_unexecuted": 30,
        "new_unseen_positive": 10,
    },
    "selection_origin_category_counts": {
        "retained_r3_unexecuted": {
            "hidden_positive": 4,
            "misleading_name_similarity": 6,
            "source_sparse_or_inaccessible": 5,
            "ambiguous_or_incomplete_conditions": 5,
            "circular_or_mixed_company_source": 4,
            "empty_generalization": 3,
            "contamination_drift_or_structure_error": 3,
        },
        "new_unseen_positive": {
            "direct_supported_positive": 8,
            "hidden_positive": 2,
        },
    },
}

EXPECTED_RETRIEVAL_EFFICIENCY_GATES = {
    "minimum_deep_expansion_reduction": 0.2,
    "maximum_query_count_increase": 0.1,
    "maximum_source_open_count_increase": 0.0,
    "stability_repeat_case_count": 6,
}


def run(script, *args):
    return subprocess.run(
        [str(PYTHON), str(script), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_r3_source_manifest(preparation_root, contract_id):
    snapshots = preparation_root / "02-校准案例候选" / "r3-source-snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    entries = []
    for index in range(1, 41):
        r3_case_id = f"R3-CASE-{index:03d}"
        role = "development_regression_only" if index <= 10 else "formal_holdout_eligible"
        execution_state = "executed_development" if index <= 10 else "unexecuted"
        path = snapshots / f"{r3_case_id}.snapshot.json"
        payload = {
            "schema_version": "1.0",
            "retained_r3_case_snapshot": {
                "snapshot_id": f"R3-SNAPSHOT-{index:03d}",
                "r3_source_case_id": r3_case_id,
                "execution_state": execution_state,
                "captured_at": "2026-08-24T23:00:00Z",
            },
        }
        path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        entries.append({
            "r3_source_case_id": r3_case_id,
            "source_case_role": role,
            "execution_state": execution_state,
            "source_snapshot_reference": path.relative_to(preparation_root).as_posix(),
            "source_snapshot_sha256": sha256_file(path),
        })
    manifest = preparation_root / "02-校准案例候选" / "r3-source-manifest.json"
    manifest.write_text(json.dumps({
        "schema_version": "1.0",
        "r3_case_source_manifest": {
            "manifest_id": "R3-SOURCE-MANIFEST-001",
            "research_contract_id": contract_id,
            "source_round": "R3",
            "accepted_state": "accepted_source_truth",
            "accepted_at": "2026-08-24T23:30:00Z",
            "acceptance_reference": "USER-R3-SOURCE-TRUTH-ACCEPTED",
            "case_count": 40,
            "development_case_count": 10,
            "unexecuted_case_count": 30,
            "cases": entries,
        },
    }, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def canonical_json_sha256(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def term_pack_header(contract_id="RC2-TEST-001", contract_version="1.0"):
    return {
        "record_type": "terminology_bridge_contract",
        "research_contract_id": contract_id,
        "contract_version": contract_version,
        "term_pack_state": "frozen_empty_cold_start",
        "accepted_term_count": 0,
        "company_data_allowed": False,
    }


def neutral_term(contract_id="RC2-TEST-001"):
    return {
        "record_type": "terminology_term",
        "term_id": "TERM-001",
        "research_contract_id": contract_id,
        "concept_role": "process_action",
        "language": "en",
        "surface_form": "neutral-token",
        "term_state": "proposed",
        "origin": "model_query_candidate",
        "source_reference": None,
        "source_snapshot_sha256": None,
        "applicable_scope": [],
        "exclusions": [],
        "company_data_present": False,
    }


def r4_case_rows(contract_id="RC2-TEST-001"):
    category_counts = {
        "direct_supported_positive": 8,
        "hidden_positive": 6,
        "misleading_name_similarity": 6,
        "source_sparse_or_inaccessible": 5,
        "ambiguous_or_incomplete_conditions": 5,
        "circular_or_mixed_company_source": 4,
        "empty_generalization": 3,
        "contamination_drift_or_structure_error": 3,
    }
    categories = [
        category for category, count in category_counts.items() for _ in range(count)
    ]
    cases = []
    for index, category in enumerate(categories, 1):
        cases.append(
            {
                "record_type": "calibration_case",
                "case_id": f"R4-CASE-{index:03d}",
                "research_contract_id": contract_id,
                "primary_category": category,
                "known_positive": index <= 14,
                "provenance": {"development_regression_only": False},
                "taxonomy_node": {
                    "taxonomy_node_id": f"NODE-{index:03d}",
                    "code": f"{index:04d}",
                    "level": 4,
                    "name_zh": f"正式节点{index}",
                    "breadcrumb": ["正式门类", "正式大类", f"正式节点{index}"],
                    "official_definition_or_null": (
                        None if index % 2 else f"官方定义{index}"
                    ),
                    "included_activities_or_null": None,
                    "excluded_or_adjacent_activities_or_null": None,
                    "official_source_reference": f"official://taxonomy/{index}",
                    "official_source_sha256": hashlib.sha256(
                        f"official-{index}".encode("utf-8")
                    ).hexdigest(),
                },
                "product_neutral_research_theme": "product-neutral-research-theme",
                "risk_flags": ["broad_node"] if index == 31 else [],
                "truth_label": "never-visible",
                "expected_screening_result": "never-visible",
                "selection_reason": "never-visible",
                "receiver_snapshot_sha256": "never-visible",
                "other_arm_output": "never-visible",
            }
        )
    return [
        {
            "record_type": "case_set_contract",
            "case_set_id": "R4-40-001",
            "research_contract_id": contract_id,
            "case_set_state": "frozen",
            "case_count": 40,
            "actual_case_record_count": 40,
            "formal_case_ids": [case["case_id"] for case in cases],
            "category_counts": category_counts,
            "stability_repeat_case_ids": [case["case_id"] for case in cases[:6]],
        },
        *cases,
    ]


def r4_truth_rows(case_rows):
    return [
        {
            "record_type": "source_truth",
            "case_id": row["case_id"],
            "known_positive": row["known_positive"],
        }
        for row in case_rows
        if row["record_type"] == "calibration_case"
    ]


def materialize_r4_case_provenance(locked_contract, case_rows, contract_local_root):
    """Create contract-local receiver-only provenance fixtures for the formal set."""
    contract = json.loads(locked_contract.read_text(encoding="utf-8"))[
        "semantic_research_contract"
    ]
    retained_root = contract_local_root / "02-校准案例" / "provenance" / "retained"
    new_root = contract_local_root / "02-校准案例" / "provenance" / "new"
    retained_root.mkdir(parents=True, exist_ok=True)
    new_root.mkdir(parents=True, exist_ok=True)
    hidden_seen = 0
    manifest_reference = contract["r3_case_source_manifest_reference_and_hash"]["reference"]
    manifest = json.loads((contract_local_root / manifest_reference).read_text(encoding="utf-8"))[
        "r3_case_source_manifest"
    ]
    retained_entries = [
        row for row in manifest["cases"]
        if row["source_case_role"] == "formal_holdout_eligible"
    ]
    retained_index = 0
    for row in case_rows:
        if row.get("record_type") != "calibration_case":
            continue
        category = row["primary_category"]
        if category == "hidden_positive":
            hidden_seen += 1
        is_new = category == "direct_supported_positive" or (
            category == "hidden_positive" and hidden_seen <= 2
        )
        if is_new:
            path = new_root / f"{row['case_id']}.selection-receipt.json"
            reference = path.relative_to(contract_local_root).as_posix()
            receipt = {
                "schema_version": "1.0",
                "new_unseen_selection_receipt": {
                    "receipt_id": f"R4-SELECT-{row['case_id']}",
                    "research_contract_id": contract["research_contract_id"],
                    "case_id": row["case_id"],
                    "source_node_id": row["taxonomy_node"]["taxonomy_node_id"],
                    "selected_at": "2026-08-25T00:00:01Z",
                    "preparation_contract_version": contract["contract_version"],
                    "locked_input_sha256": contract["case_preparation_gate"][
                        "locked_input_sha256"
                    ],
                    "terminology_bridge_reference": contract[
                        "terminology_architecture"
                    ]["term_pack_reference"],
                    "terminology_bridge_sha256": contract[
                        "terminology_architecture"
                    ]["term_pack_sha256"],
                    "official_terminal_node_snapshot_reference": contract[
                        "taxonomy_snapshot_reference"
                    ],
                    "official_terminal_node_snapshot_sha256": contract[
                        "taxonomy_snapshot_sha256"
                    ],
                    "prior_method_exposure_state": "unseen",
                    "selection_basis": "official_terminal_node_after_method_and_terminology_lock",
                },
            }
            path.write_text(
                json.dumps(receipt, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            row["provenance"] = {
                "development_regression_only": False,
                "selection_origin": "new_unseen_positive",
                "selection_receipt_reference": reference,
                "selection_receipt_sha256": sha256_file(path),
            }
        else:
            source_entry = retained_entries[retained_index]
            retained_index += 1
            row["provenance"] = {
                "development_regression_only": False,
                "selection_origin": "retained_r3_unexecuted",
                "r3_source_case_id": source_entry["r3_source_case_id"],
                "source_snapshot_reference": source_entry["source_snapshot_reference"],
                "source_snapshot_sha256": source_entry["source_snapshot_sha256"],
            }
    return case_rows


def r4_visible_case_rows(case_rows):
    """Create the independently frozen, task-visible-only test artifact."""
    formal_header = case_rows[0]
    cases = [row for row in case_rows if row["record_type"] == "calibration_case"]
    return [
        {
            "record_type": "visible_case_set_contract",
            "visible_case_set_id": "R4-40-001-visible",
            "research_contract_id": formal_header["research_contract_id"],
            "visible_case_set_state": "frozen_visible_only",
            "visible_only": True,
            "truth_data_allowed": False,
            "frozen_before_truth_preparation": True,
            "freeze_authorization_reference": "USER-R4-VISIBLE-CASE-FREEZE",
            "frozen_at": "2026-08-25T00:00:00Z",
            "case_count": 40,
            "actual_case_record_count": 40,
            "formal_case_ids": [case["case_id"] for case in cases],
        },
        *[
            {
                "record_type": "visible_calibration_case",
                "research_contract_id": case["research_contract_id"],
                "case_id": case["case_id"],
                "taxonomy_node": case["taxonomy_node"],
                "product_neutral_research_theme": case["product_neutral_research_theme"],
                "risk_flags": case["risk_flags"],
            }
            for case in cases
        ],
    ]


def r4_visible_case_draft_rows(case_rows):
    """A truth-free input which exists before formal/truth preparation."""
    frozen = r4_visible_case_rows(case_rows)
    header = frozen[0]
    return [
        {
            "record_type": "visible_case_set_draft",
            "visible_case_set_id": header["visible_case_set_id"],
            "research_contract_id": header["research_contract_id"],
            "visible_case_set_state": "draft_visible_only",
            "visible_only": True,
            "truth_data_allowed": False,
            "case_count": 40,
            "actual_case_record_count": 40,
            "formal_case_ids": header["formal_case_ids"],
        },
        *[
            {
                "record_type": "visible_calibration_case_draft",
                "research_contract_id": row["research_contract_id"],
                "case_id": row["case_id"],
                "taxonomy_node": row["taxonomy_node"],
                "product_neutral_research_theme": row["product_neutral_research_theme"],
                "risk_flags": row["risk_flags"],
            }
            for row in frozen[1:]
        ],
    ]


class GeneralizedSemanticRetrievalR4Tests(unittest.TestCase):
    def test_task7_calibration_arm_is_bound_to_exact_r4_methods_and_auditable_work(self):
        arm = json.loads(CALIBRATION_ARM_TEMPLATE.read_text(encoding="utf-8"))[
            "semantic_content_calibration_arm"
        ]
        self.assertEqual(arm["calibration_contract_marker"], "2.0-r4")
        self.assertEqual(arm["method_arm"], "screen_then_expand_v2")
        self.assertEqual(
            set(arm["case_evidence"][0]["critical_dispositions"]),
            {
                "taxonomy_and_scope_grounding",
                "semantic_decision_correctness",
                "source_retrieval_equivalence",
                "receiver_evidence_integrity",
                "safety_boundary",
            },
        )
        case_evidence = arm["case_evidence"][0]
        self.assertEqual(
            {
                "resource_observation_reference",
                "resource_observation_sha256",
                "resource_observation_receipt_reference",
                "resource_observation_receipt_sha256",
            }.intersection(case_evidence),
            {
                "resource_observation_reference",
                "resource_observation_sha256",
                "resource_observation_receipt_reference",
                "resource_observation_receipt_sha256",
            },
        )
        observation = json.loads(
            RESOURCE_OBSERVATION_TEMPLATE.read_text(encoding="utf-8")
        )["content_resource_observation"]
        self.assertIn("queries", observation)
        self.assertIn("deep_expansion_disposition", observation)
        self.assertEqual(
            {
                "observed_result_references",
                "inspected_result_count",
                "opened_source_references",
                "access_outcomes",
            }.intersection(observation["queries"][0]),
            {
                "observed_result_references",
                "inspected_result_count",
                "opened_source_references",
                "access_outcomes",
            },
        )
        self.assertEqual(
            set(arm["stability_task_manifest_reference_and_hash"]),
            {"reference", "sha256"},
        )
        evaluator_source = EVALUATE_CONTENT.read_text(encoding="utf-8")
        self.assertIn('R4_ARMS = ("baseline_full_depth_v1", "screen_then_expand_v2")', evaluator_source)
        self.assertIn('LEGACY_MARKER = "1.0-legacy"', evaluator_source)
        self.assertNotIn('"EFFECTIVE"', evaluator_source)
        freezer_source = FREEZE_STABILITY.read_text(encoding="utf-8")
        self.assertIn("model_execution_authorized", freezer_source)
        self.assertIn("stability_repeat_case_ids", freezer_source)

    def r4_draft(self, contract_id="RC2-TEST-001"):
        payload = json.loads(CONTENT_FIRST_CONTRACT.read_text(encoding="utf-8"))
        contract = payload["semantic_research_contract"]
        contract["research_contract_id"] = contract_id
        contract["contract_version"] = "2.1.0-content-first.prep.1"
        return payload

    def lock_r4(self, draft, term_pack, locked):
        preparation_root = term_pack.parent.parent
        r3_manifest = preparation_root / "02-校准案例候选" / "r3-source-manifest.json"
        return run(
            LOCK,
            "--contract",
            str(draft),
            "--terminology-bridge",
            str(term_pack),
            "--terminology-bridge-reference",
            term_pack.relative_to(preparation_root).as_posix(),
            "--r3-source-manifest",
            str(r3_manifest),
            "--r3-source-manifest-reference",
            r3_manifest.relative_to(preparation_root).as_posix(),
            "--authorization-reference",
            "USER-R4-PREP",
            "--locked-at",
            "2026-08-25T00:00:00Z",
            "--output",
            str(locked),
        )

    def r4_preparation(self, root, contract_id="RC2-TEST-001"):
        preparation_root = root / "preparation"
        draft = preparation_root / "00-合同准备" / "draft.json"
        term_pack = preparation_root / "01-术语桥" / "terminology-bridge.jsonl"
        draft.parent.mkdir(parents=True)
        term_pack.parent.mkdir(parents=True)
        payload = self.r4_draft(contract_id)
        taxonomy = preparation_root / "01-节点快照" / "taxonomy.json"
        prompt = preparation_root / "00-合同准备" / "prompt.md"
        prompt_template = preparation_root / "00-合同准备" / "prompt-template.md"
        schema = preparation_root / "00-合同准备" / "return-schema.json"
        config = preparation_root / "00-合同准备" / "model-config.json"
        rubric = preparation_root / "00-合同准备" / "rubric.md"
        taxonomy.parent.mkdir(parents=True)
        taxonomy.write_text(
            json.dumps(
                {
                    "terminal_node_count": 40,
                    "terminal_nodes": [
                        {
                            "taxonomy_node_id": f"NODE-{index:03d}",
                            "code": f"{index:04d}",
                            "name_zh": f"正式节点{index}",
                        }
                        for index in range(1, 41)
                    ],
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        prompt.write_text("content-first prompt\n", encoding="utf-8")
        prompt_template.write_text("content-first prompt template\n", encoding="utf-8")
        schema.write_bytes((SKILL_ROOT / "assets/content-first/content-source-observation.template.json").read_bytes())
        config.write_text('{"temperature":0}\n', encoding="utf-8")
        rubric.write_text("fixture rubric\n", encoding="utf-8")
        contract = payload["semantic_research_contract"]
        contract.update(
            {
                "taxonomy_snapshot_reference": "01-节点快照/taxonomy.json",
                "taxonomy_snapshot_sha256": sha256_file(taxonomy),
                "terminal_node_count": 40,
                "prompt_template_references_and_hashes": [
                    {"reference": "00-合同准备/prompt-template.md", "sha256": sha256_file(prompt_template)}
                ],
                "paired_execution_contract": {
                    "declared_model_and_configuration": {
                        "model": "fixture-model",
                        "configuration_reference": "00-合同准备/model-config.json",
                        "configuration_sha256": sha256_file(config),
                    },
                    "tools": ["fixture-search-tool"],
                    "source_permissions": ["fixture-public-source"],
                    "observation_window": {"starts_at": "2026-08-25T00:00:00Z", "ends_at": "2026-08-25T01:00:00Z"},
                    "budgets": {
                        "query_budget": 10,
                        "source_open_budget": 10,
                        "elapsed_seconds_budget": 300,
                        "output_token_budget": 100,
                    },
                    "frozen_artifact_references_and_hashes": {
                        "prompt": [{"reference": "00-合同准备/prompt.md", "sha256": sha256_file(prompt)}],
                        "schema": [{"reference": "00-合同准备/return-schema.json", "sha256": sha256_file(schema)}],
                        "config": [{"reference": "00-合同准备/model-config.json", "sha256": sha256_file(config)}],
                        "rubric": [{"reference": "00-合同准备/rubric.md", "sha256": sha256_file(rubric)}],
                    },
                    "fresh_context_required": True,
                    "truth_isolation_required": True,
                    "other_arm_isolation_required": True,
                    "prior_case_isolation_required": True,
                    "append_only_outputs_required": True,
                    "model_execution_authorized": False,
                },
            }
        )
        draft.write_text(json.dumps(payload), encoding="utf-8")
        write_jsonl(
            term_pack,
            [term_pack_header(contract_id, payload["semantic_research_contract"]["contract_version"])],
        )
        create_r3_source_manifest(preparation_root, contract_id)
        return draft, term_pack

    def package_generation_receipt(self, final_contract, visible_case_set, output):
        receipt = final_contract.parent / "package-generation-receipt.json"
        receipt.write_text(json.dumps({
            "schema_version": "1.0",
            "package_generation_authorization_receipt": {
                "authorization_id": "AUTH-R4-PACKAGE-001",
                "authorized_at": "2026-08-25T00:00:00Z",
                "permitted_action": "package_generation_only",
                "final_contract_sha256": sha256_file(final_contract),
                "formal_case_set_sha256": json.loads(final_contract.read_text(encoding="utf-8"))["semantic_research_contract"]["calibration_case_set_reference_and_hash"]["sha256"],
                "visible_case_set_sha256": sha256_file(visible_case_set),
                "output_scope": str(output.resolve()),
                "model_execution_authorized": False,
                "full_screening_authorized": False,
            },
        }), encoding="utf-8")
        return receipt

    def build_tasks(self, final_contract, visible_case_set, output, *, fail_after=None, receipt=None):
        receipt = receipt or self.package_generation_receipt(final_contract, visible_case_set, output)
        arguments = [
            "--contract", str(final_contract),
            "--visible-case-set", str(visible_case_set),
            "--output", str(output),
            "--expected-final-contract-sha256", sha256_file(final_contract),
            "--package-generation-authorization-receipt", str(receipt),
            "--expected-package-generation-authorization-receipt-sha256", sha256_file(receipt),
            "--contract-local-root", str(final_contract.parent / "preparation"),
        ]
        if fail_after is not None:
            arguments.extend(["--test-fail-after-task-count", str(fail_after)])
        return run(BUILD_TASKS, *arguments)

    def verify_tasks(self, final_contract, visible_case_set, output, receipt=None, expected_manifest=None):
        receipt = receipt or self.package_generation_receipt(final_contract, visible_case_set, output)
        manifest = output / "paired-task-manifest.json"
        return run(
            BUILD_TASKS,
            "--contract", str(final_contract),
            "--visible-case-set", str(visible_case_set),
            "--contract-local-root", str(final_contract.parent / "preparation"),
            "--expected-final-contract-sha256", sha256_file(final_contract),
            "--package-generation-authorization-receipt", str(receipt),
            "--expected-package-generation-authorization-receipt-sha256", sha256_file(receipt),
            "--verify-package", str(output),
            "--expected-manifest-file-sha256", expected_manifest or sha256_file(manifest),
        )

    def semantic_template_preparation(self, root, contract_id="RC2-SEMANTIC-TEMPLATE-001"):
        preparation_root = root / "semantic-preparation"
        draft = preparation_root / "00-合同准备" / "draft.json"
        term_pack = preparation_root / "01-术语桥" / "terminology-bridge.jsonl"
        draft.parent.mkdir(parents=True)
        term_pack.parent.mkdir(parents=True)
        payload = json.loads((SKILL_ROOT / "assets/semantic-method/research-contract.template.json").read_text())
        contract = payload["semantic_research_contract"]
        contract["research_contract_id"] = contract_id
        contract["contract_version"] = "2.1.0-content-first.prep.1"
        prompt = preparation_root / "00-合同准备" / "prompt.md"
        schema = preparation_root / "00-合同准备" / "schema.json"
        config = preparation_root / "00-合同准备" / "config.json"
        rubric = preparation_root / "00-合同准备" / "rubric.md"
        prompt.write_text("fixture prompt\n", encoding="utf-8")
        schema.write_bytes((SKILL_ROOT / "assets/content-first/content-source-observation.template.json").read_bytes())
        config.write_text("{}\n", encoding="utf-8")
        rubric.write_text("fixture rubric\n", encoding="utf-8")
        contract["paired_execution_contract"].update({
            "declared_model_and_configuration": {
                "model": "fixture-model",
                "configuration_reference": "00-合同准备/config.json",
                "configuration_sha256": sha256_file(config),
            },
            "tools": ["fixture-tool"],
            "source_permissions": ["fixture-source"],
            "observation_window": {"starts_at": "2026-08-25T00:00:00Z", "ends_at": "2026-08-25T01:00:00Z"},
            "budgets": {"query_budget": 1, "source_open_budget": 1, "elapsed_seconds_budget": 1, "output_token_budget": 1},
            "frozen_artifact_references_and_hashes": {
                "prompt": [{"reference": "00-合同准备/prompt.md", "sha256": sha256_file(prompt)}],
                "schema": [{"reference": "00-合同准备/schema.json", "sha256": sha256_file(schema)}],
                "config": [{"reference": "00-合同准备/config.json", "sha256": sha256_file(config)}],
                "rubric": [{"reference": "00-合同准备/rubric.md", "sha256": sha256_file(rubric)}],
            },
            "model_execution_authorized": False,
        })
        draft.write_text(json.dumps(payload), encoding="utf-8")
        write_jsonl(term_pack, [term_pack_header(contract_id, contract["contract_version"])])
        create_r3_source_manifest(preparation_root, contract_id)
        return draft, term_pack

    def test_semantic_template_can_lock_as_content_first_without_legacy_mode_removal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.semantic_template_preparation(root)
            locked = root / "locked.json"

            result = self.lock_r4(draft, term_pack, locked)

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            contract = json.loads(locked.read_text(encoding="utf-8"))["semantic_research_contract"]
            self.assertEqual(contract["execution_mode"], "content_first")
            self.assertFalse(contract["execution_authorized"])

    def test_content_first_lock_rejects_unknown_mode_and_dangerous_authorizations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            payload = json.loads(draft.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["execution_mode"] = "content-frist"
            draft.write_text(json.dumps(payload), encoding="utf-8")

            unknown = self.lock_r4(draft, term_pack, locked)

            self.assertNotEqual(unknown.returncode, 0)
            self.assertIn("EXECUTION_MODE_INVALID", unknown.stderr)
            payload["semantic_research_contract"]["execution_mode"] = "content_first"
            payload["semantic_research_contract"]["execution_authorized"] = True
            draft.write_text(json.dumps(payload), encoding="utf-8")
            dangerous = self.lock_r4(draft, term_pack, locked)
            self.assertNotEqual(dangerous.returncode, 0)
            self.assertIn("CONTENT_FIRST_DEFAULT_DENY_REQUIRED", dangerous.stderr)

    def test_content_first_lock_requires_contract_local_matching_term_pack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            external = root / "external.jsonl"
            write_jsonl(external, load_jsonl(term_pack))

            cross_directory = self.lock_r4(draft, external, locked)

            self.assertNotEqual(cross_directory.returncode, 0)
            self.assertIn("TERMINOLOGY_BRIDGE_NOT_CONTRACT_LOCAL", cross_directory.stderr)
            wrong_reference = run(
                LOCK, "--contract", str(draft), "--terminology-bridge", str(term_pack),
                "--terminology-bridge-reference", "../01-术语桥/terminology-bridge.jsonl",
                "--authorization-reference", "USER-R4-PREP", "--locked-at", "2026-08-25T00:00:00Z",
                "--output", str(locked),
            )
            self.assertNotEqual(wrong_reference.returncode, 0)
            self.assertIn("TERMINOLOGY_BRIDGE_REFERENCE_INVALID", wrong_reference.stderr)
            rows = load_jsonl(term_pack)
            rows[0]["contract_version"] = "different-version"
            write_jsonl(term_pack, rows)
            version_drift = self.lock_r4(draft, term_pack, locked)
            self.assertNotEqual(version_drift.returncode, 0)
            self.assertIn("TERMINOLOGY_BRIDGE_VERSION_MISMATCH", version_drift.stderr)

    def test_content_first_lock_requires_accepted_r3_source_manifest_before_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            manifest = root / "preparation" / "02-校准案例候选" / "r3-source-manifest.json"
            manifest.unlink()

            result = self.lock_r4(draft, term_pack, root / "locked.json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("R3_SOURCE_MANIFEST", result.stderr)

    def test_content_first_lock_rejects_r3_manifest_count_snapshot_and_id_drift(self):
        scenarios = (
            "count",
            "snapshot_hash",
            "snapshot_id_alias",
            "accepted_at_equal_lock",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                draft, term_pack = self.r4_preparation(root)
                preparation = root / "preparation"
                manifest_path = preparation / "02-校准案例候选" / "r3-source-manifest.json"
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest = payload["r3_case_source_manifest"]
                if scenario == "count":
                    manifest["unexecuted_case_count"] = 29
                    expected = "R3_SOURCE_MANIFEST_COMPOSITION_INVALID"
                elif scenario == "accepted_at_equal_lock":
                    manifest["accepted_at"] = "2026-08-25T00:00:00Z"
                    expected = "R3_SOURCE_MANIFEST_NOT_ACCEPTED_BEFORE_LOCK"
                else:
                    entry = manifest["cases"][11]
                    snapshot = preparation / entry["source_snapshot_reference"]
                    if scenario == "snapshot_hash":
                        snapshot.write_bytes(snapshot.read_bytes() + b" ")
                        expected = "PROVENANCE_ASSET_HASH_MISMATCH"
                    else:
                        first = manifest["cases"][10]
                        snapshot_payload = json.loads(snapshot.read_text(encoding="utf-8"))
                        snapshot_payload["retained_r3_case_snapshot"]["snapshot_id"] = "r3-snapshot-011"
                        snapshot.write_text(json.dumps(snapshot_payload, sort_keys=True) + "\n", encoding="utf-8")
                        entry["source_snapshot_sha256"] = sha256_file(snapshot)
                        expected = "R3_SOURCE_SNAPSHOT_ID_REUSE"
                manifest_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

                result = self.lock_r4(draft, term_pack, root / "locked.json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_content_first_lock_and_finalizer_require_exact_r4_method_arms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            payload = json.loads(draft.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["candidate_method_contract"] = "screen_then_expand_v3"
            draft.write_text(json.dumps(payload), encoding="utf-8")
            wrong_lock = self.lock_r4(draft, term_pack, root / "wrong-locked.json")
            self.assertNotEqual(wrong_lock.returncode, 0)
            self.assertIn("METHOD_ARMS_INVALID", wrong_lock.stderr)

            draft, term_pack = self.r4_preparation(root / "fresh")
            locked = root / "locked.json"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            locked_payload = json.loads(locked.read_text(encoding="utf-8"))
            locked_payload["semantic_research_contract"]["baseline_method_contract"] = "other"
            locked.write_text(json.dumps(locked_payload), encoding="utf-8")
            rows = r4_case_rows()
            case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
            write_jsonl(case_set, rows)
            write_jsonl(truth, r4_truth_rows(rows))
            wrong_final = self.finalize_r4(locked, case_set, truth, root / "final.json")
            self.assertNotEqual(wrong_final.returncode, 0)
            self.assertIn("PREPARATION_", wrong_final.stderr)

    def test_content_first_lock_rejects_normalized_duplicate_excluded_case_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            payload = json.loads(draft.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["calibration_case_policy"][
                "development_case_ids_excluded_from_formal"
            ] = ["R4-DEV-001", "r4-dev-001"]
            draft.write_text(json.dumps(payload), encoding="utf-8")

            result = self.lock_r4(draft, term_pack, root / "locked.json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("development_case_ids_excluded_from_formal", result.stderr)

    def freeze_r4_visible(self, rows, frozen, receipt):
        draft = frozen.with_name(frozen.stem + "-draft.jsonl")
        write_jsonl(draft, r4_visible_case_draft_rows(rows))
        result = run(
            FREEZE_VISIBLE, "--visible-case-draft", str(draft),
            "--visible-case-set-reference", "02-校准案例/visible-case-set.jsonl",
            "--freeze-authorization-reference", "USER-R4-VISIBLE-CASE-FREEZE",
            "--frozen-at", "2026-08-25T00:00:00Z", "--output", str(frozen),
            "--receipt-output", str(receipt),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def finalize_r4(
        self,
        locked,
        case_set,
        truth_set,
        final_contract,
        visible_case_set=None,
        freeze_receipt=None,
        *,
        materialize_provenance=True,
        fail_after_temp_write=False,
    ):
        if visible_case_set is None:
            visible_case_set = final_contract.with_name(final_contract.stem + "-visible-case-set.jsonl")
            freeze_receipt = final_contract.with_name(final_contract.stem + "-visible-case-freeze-receipt.json")
            self.freeze_r4_visible(load_jsonl(case_set), visible_case_set, freeze_receipt)
        receipt_args = []
        if freeze_receipt is not None:
            receipt_args = [
                "--visible-case-freeze-receipt", str(freeze_receipt),
                "--visible-case-freeze-receipt-reference", "02-校准案例/visible-case-freeze-receipt.json",
                "--expected-visible-case-freeze-receipt-sha256", sha256_file(freeze_receipt),
            ]
        arguments = [
            FINALIZE,
            "--preparation-contract",
            str(locked),
            "--case-set",
            str(case_set),
            "--case-set-reference",
            "02-校准案例/formal-case-set.jsonl",
            "--visible-case-set",
            str(visible_case_set),
            "--visible-case-set-reference",
            "02-校准案例/visible-case-set.jsonl",
            *receipt_args,
            "--source-truth-package",
            str(truth_set),
            "--source-truth-reference",
            "03-来源真值/source-truth.jsonl",
            "--final-contract-version",
            "2.1.0-content-first.final.1",
            "--batch-size",
            "10",
            "--control-case-id",
            "R4-CASE-001",
            "--control-case-id",
            "R4-CASE-002",
            "--frozen-at",
            "2026-08-25T00:00:00Z",
            "--contract-local-root",
            str(locked.parent / "preparation"),
            "--output",
            str(final_contract),
        ]
        if fail_after_temp_write:
            arguments.append("--test-fail-after-temp-write")
        return run(*arguments)

    def bound_r4_case_rows(self, locked):
        return materialize_r4_case_provenance(
            locked, r4_case_rows(), locked.parent / "preparation"
        )

    def frozen_r4_contract_and_case_set(self, root):
        draft, term_pack = self.r4_preparation(root)
        locked = root / "locked.json"
        case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
        visible_case_set = root / "visible-case-set.jsonl"
        final_contract = root / "final.json"
        locked_result = self.lock_r4(draft, term_pack, locked)
        self.assertEqual(locked_result.returncode, 0, locked_result.stderr)
        rows = self.bound_r4_case_rows(locked)
        visible_receipt = root / "visible-case-freeze-receipt.json"
        self.freeze_r4_visible(rows, visible_case_set, visible_receipt)
        write_jsonl(case_set, rows)
        write_jsonl(truth_set, r4_truth_rows(rows))
        final_result = self.finalize_r4(locked, case_set, truth_set, final_contract, visible_case_set, visible_receipt)
        self.assertEqual(final_result.returncode, 0, final_result.stderr + final_result.stdout)
        return final_contract, visible_case_set

    def load_task(self, output, method_arm, case_id):
        return json.loads(
            (
                output / method_arm / f"{case_id}.task.json"
            ).read_text(encoding="utf-8")
        )["content_first_calibration_task"]

    def test_builder_emits_40_pairs_without_truth_or_receiver_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"

            result = self.build_tasks(final_contract, case_set, output)

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            tasks = sorted(output.rglob("*.task.json"))
            self.assertEqual(len(tasks), 80)
            for path in tasks:
                text = path.read_text(encoding="utf-8")
                for forbidden in (
                    "truth_label",
                    "expected_screening_result",
                    "known_positive",
                    "selection_reason",
                    "selection_origin",
                    "r3_source_case_id",
                    "selection_receipt_reference",
                    "receiver_snapshot_sha256",
                    "other_arm_output",
                ):
                    self.assertNotIn(forbidden, text)
                task = json.loads(text)["content_first_calibration_task"]
                node = task["visible_input"]["taxonomy_node"]
                self.assertIn("breadcrumb", node)
                self.assertIn("official_definition_or_null", node)
                self.assertEqual(
                    task["three_link_gate"],
                    [
                        "taxonomy_membership_basis",
                        "output_or_subprocess_basis",
                        "mechanism_or_use_point_basis",
                    ],
                )
                self.assertNotIn("receiver", json.dumps(task["expected_return_schema"]))

    def test_builder_uses_only_the_frozen_visible_case_set_when_truth_inputs_are_unavailable(self):
        """Removing the formal/truth files after finalization cannot affect truth-blind task construction."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, visible_case_set = self.frozen_r4_contract_and_case_set(root)
            (root / "cases.jsonl").unlink()
            (root / "truth.jsonl").unlink()

            result = self.build_tasks(final_contract, visible_case_set, root / "paired-tasks")

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_finalizer_rejects_visible_case_set_with_truth_field_or_marker_free_truth_value(self):
        """Visible cases have an exact schema and cannot reuse a sealed value under a neutral field name."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            formal, truth, visible = root / "formal.jsonl", root / "truth.jsonl", root / "visible.jsonl"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            formal_rows = self.bound_r4_case_rows(locked)
            formal_rows[1]["sealed_hint"] = "amber-orchid"
            visible_rows = r4_case_rows()
            visible_rows[1]["product_neutral_research_theme"] = "prefix Amber%2DOrchid suffix"
            receipt = root / "visible-receipt.json"
            self.freeze_r4_visible(visible_rows, visible, receipt)
            write_jsonl(formal, formal_rows)
            write_jsonl(truth, r4_truth_rows(formal_rows))

            laundered = self.finalize_r4(locked, formal, truth, root / "laundered.json", visible, receipt)
            self.assertNotEqual(laundered.returncode, 0)
            self.assertIn("VISIBLE_CASE_VALUE_LAUNDERING", laundered.stderr)

    def test_builder_rejects_truth_hash_reuse_and_reference_aliases(self):
        """Task-visible artifacts cannot be sealed bytes, spelling aliases, or symlink aliases."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked, formal, truth, visible = root / "locked.json", root / "formal.jsonl", root / "truth.jsonl", root / "visible.jsonl"
            rows = r4_case_rows()
            receipt = root / "visible-receipt.json"
            self.freeze_r4_visible(rows, visible, receipt)
            write_jsonl(formal, rows)
            write_jsonl(truth, r4_truth_rows(rows))
            prep = root / "preparation"
            formal_bytes = formal.read_bytes()
            prompt = prep / "00-合同准备" / "prompt.md"
            prompt.write_bytes(formal_bytes)
            body = json.loads(draft.read_text(encoding="utf-8"))["semantic_research_contract"]
            paired_prompt = body["paired_execution_contract"]["frozen_artifact_references_and_hashes"]["prompt"][0]
            paired_prompt["sha256"] = sha256_file(prompt)
            draft.write_text(json.dumps({"schema_version": "1.0", "semantic_research_contract": body}), encoding="utf-8")
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)

            reused = self.finalize_r4(locked, formal, truth, root / "reused.json", visible, receipt)

            self.assertNotEqual(reused.returncode, 0)
            self.assertIn("TASK_VISIBLE_ARTIFACT_HASH_COLLISION", reused.stderr)

    def test_finalizer_refuses_formal_hash_collision_before_opening_task_visible_artifact(self):
        """A declared formal-byte collision wins before the aliased task-visible file is opened."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked, formal = root / "locked.json", root / "formal.jsonl"
            truth, visible = root / "truth.jsonl", root / "visible.jsonl"
            rows = r4_case_rows()
            write_jsonl(formal, rows)
            write_jsonl(truth, r4_truth_rows(rows))
            receipt = root / "visible-receipt.json"
            self.freeze_r4_visible(rows, visible, receipt)
            prompt = root / "preparation" / "00-合同准备" / "prompt.md"
            prompt.write_bytes(formal.read_bytes())
            payload = json.loads(draft.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["paired_execution_contract"]["frozen_artifact_references_and_hashes"]["prompt"][0]["sha256"] = sha256_file(prompt)
            draft.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            prompt.unlink()

            result = self.finalize_r4(locked, formal, truth, root / "collision.json", visible, receipt)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TASK_VISIBLE_ARTIFACT_HASH_COLLISION", result.stderr)
            self.assertNotIn("FROZEN_REFERENCE_INVALID", result.stderr)

    def test_finalizer_rejects_raw_and_symlink_task_visible_reference_aliases(self):
        """Canonical spelling and filesystem identity are both mandatory before a final contract exists."""
        for alias_kind in ("raw", "symlink"):
            with self.subTest(alias_kind=alias_kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                draft, term_pack = self.r4_preparation(root)
                body = json.loads(draft.read_text(encoding="utf-8"))["semantic_research_contract"]
                prep = root / "preparation" / "00-合同准备"
                if alias_kind == "raw":
                    body["prompt_template_references_and_hashes"][0]["reference"] = "./00-合同准备/prompt-template.md"
                else:
                    alias = prep / "prompt-template-alias.md"
                    alias.symlink_to("prompt.md")
                    body["prompt_template_references_and_hashes"][0] = {
                        "reference": "00-合同准备/prompt-template-alias.md", "sha256": sha256_file(alias)
                    }
                draft.write_text(json.dumps({"schema_version": "1.0", "semantic_research_contract": body}), encoding="utf-8")
                result = self.lock_r4(draft, term_pack, root / "locked.json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("FROZEN_REFERENCE_INVALID", result.stderr)

    def test_builder_pairs_have_identical_visible_input_and_canonical_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"

            result = self.build_tasks(final_contract, case_set, output)

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            baseline = self.load_task(output, "baseline_full_depth_v1", "R4-CASE-031")
            revised = self.load_task(output, "screen_then_expand_v2", "R4-CASE-031")
            self.assertEqual(baseline["visible_input"], revised["visible_input"])
            self.assertEqual(baseline["visible_input_sha256"], revised["visible_input_sha256"])
            self.assertEqual(
                revised["visible_input_sha256"],
                canonical_json_sha256(revised["visible_input"]),
            )
            self.assertTrue(baseline["method_contract"]["full_depth_required"])
            self.assertFalse(baseline["dynamic_term_discovery"]["enabled"])
            self.assertFalse(revised["method_contract"]["full_depth_required"])
            manifest = json.loads((output / "paired-task-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["content_first_paired_task_manifest"]["pairs"]), 40)
            self.assertEqual(manifest["content_first_paired_task_manifest"]["final_contract_sha256"], sha256_file(final_contract))
            self.assertEqual(manifest["content_first_paired_task_manifest"]["visible_case_set_sha256"], sha256_file(case_set))
            self.assertEqual(manifest["content_first_paired_task_manifest"]["formal_case_set_sha256"], json.loads(final_contract.read_text(encoding="utf-8"))["semantic_research_contract"]["calibration_case_set_reference_and_hash"]["sha256"])

    def test_revised_task_decomposes_outputs_before_dynamic_terms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"
            result = self.build_tasks(final_contract, case_set, output)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            task = self.load_task(output, "screen_then_expand_v2", "R4-CASE-031")

            self.assertTrue(task["method_contract"]["broad_node_output_family_decomposition_required"])
            self.assertEqual(
                task["dynamic_term_discovery"]["trigger"],
                "core_search_complete_without_three_link_bridge",
            )
            self.assertFalse(task["dynamic_term_discovery"]["mutates_frozen_term_pack"])
            self.assertEqual(task["dynamic_term_discovery"]["allowed_use"], "retrieval_only")

    def test_builder_refuses_existing_output_without_partial_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"
            output.mkdir()
            sentinel = output / "keep.txt"
            sentinel.write_text("unchanged", encoding="utf-8")

            result = self.build_tasks(final_contract, case_set, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("OUTPUT_EXISTS", result.stderr)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")
            self.assertEqual(sorted(path.name for path in output.iterdir()), ["keep.txt"])

    def test_builder_rejects_case_set_hash_mismatch_without_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            case_set.write_text(case_set.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            output = root / "paired-tasks"

            result = self.build_tasks(final_contract, case_set, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CASE_SET_HASH_MISMATCH", result.stderr)
            self.assertFalse(output.exists())

    def test_builder_rejects_truth_marker_smuggled_into_visible_risk_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            rows = load_jsonl(case_set)
            rows[1]["risk_flags"] = ["known_positive"]
            write_jsonl(case_set, rows)
            payload = json.loads(final_contract.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["visible_case_set_reference_and_hash"]["sha256"] = sha256_file(case_set)
            final_contract.write_text(json.dumps(payload), encoding="utf-8")
            output = root / "paired-tasks"

            result = self.build_tasks(final_contract, case_set, output)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("VISIBLE_CASE_PROJECTION_INVALID", result.stderr)
            self.assertFalse(output.exists())

    def test_builder_requires_independent_contract_hash_and_package_generation_receipt(self):
        """Removing either independent input must prevent task generation."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"

            result = run(
                BUILD_TASKS,
                "--contract", str(final_contract),
                "--visible-case-set", str(case_set),
                "--output", str(output),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--package-generation-authorization-receipt", result.stderr)
            self.assertFalse(output.exists())

    def test_builder_rejects_case_id_path_escape_and_normalized_collision(self):
        """Treating a case ID as a path must fail before any task path is made."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            rows = load_jsonl(case_set)
            rows[1]["case_id"] = "R4-CASE-001/../R4-CASE-002"
            rows[2]["case_id"] = "R4-CASE-002"
            write_jsonl(case_set, rows)
            payload = json.loads(final_contract.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["visible_case_set_reference_and_hash"]["sha256"] = sha256_file(case_set)
            final_contract.write_text(json.dumps(payload), encoding="utf-8")

            result = self.build_tasks(final_contract, case_set, root / "paired-tasks")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("VISIBLE_CASE_SET_INVALID", result.stderr)
            self.assertFalse((root / "paired-tasks").exists())

    def test_builder_recursively_rejects_normalized_and_encoded_truth_markers_in_visible_fields(self):
        """A truth marker in any permitted visible value is still a leak."""
        field_mutations = (
            ("theme", lambda row: row.__setitem__("product_neutral_research_theme", "Known%5FPositive")),
            ("node", lambda row: row["taxonomy_node"].__setitem__("name_zh", "ＫＮＯＷＮ＿ＰＯＳＩＴＩＶＥ")),
            ("breadcrumb", lambda row: row["taxonomy_node"].__setitem__("breadcrumb", ["safe", "other%5Farm%5Foutput"])),
            ("risk_flags", lambda row: row.__setitem__("risk_flags", ["receiver snapshot sha256"])),
        )
        for field_name, mutate in field_mutations:
            with self.subTest(field_name=field_name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
                rows = load_jsonl(case_set)
                mutate(rows[1])
                write_jsonl(case_set, rows)
                payload = json.loads(final_contract.read_text(encoding="utf-8"))
                payload["semantic_research_contract"]["visible_case_set_reference_and_hash"]["sha256"] = sha256_file(case_set)
                final_contract.write_text(json.dumps(payload), encoding="utf-8")

                result = self.build_tasks(final_contract, case_set, root / "paired-tasks")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("VISIBLE_CASE_PROJECTION_INVALID", result.stderr)
                self.assertFalse((root / "paired-tasks").exists())

    def test_builder_manifest_hashes_each_canonical_task_and_detects_task_tamper(self):
        """Changing one task after build must disagree with the manifest's per-arm hash."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"
            result = self.build_tasks(final_contract, case_set, output)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            manifest = json.loads((output / "paired-task-manifest.json").read_text(encoding="utf-8"))["content_first_paired_task_manifest"]
            self.assertEqual(manifest["task_count"], 80)
            entries = [entry for pair in manifest["pairs"] for entry in pair["task_files"].values()]
            self.assertEqual(len(entries), 80)
            self.assertEqual(len({entry["path"] for entry in entries}), 80)
            task_path = output / entries[0]["path"]
            task_payload = json.loads(task_path.read_text(encoding="utf-8"))
            self.assertEqual(entries[0]["task_file_sha256"], sha256_file(task_path))
            task_payload["content_first_calibration_task"]["visible_input"]["risk_flags"] = ["changed"]
            task_path.write_text(json.dumps(task_payload), encoding="utf-8")
            self.assertNotEqual(entries[0]["task_file_sha256"], sha256_file(task_path))

    def test_task_source_observation_schema_is_the_canonical_array_template(self):
        """Tasks must declare the exact array-of-observations contract, not an object."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"
            result = self.build_tasks(final_contract, case_set, output)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            task = self.load_task(output, "baseline_full_depth_v1", "R4-CASE-001")
            canonical = json.loads((SKILL_ROOT / "assets/content-first/content-source-observation.template.json").read_text(encoding="utf-8"))
            self.assertEqual(
                task["expected_return_schema"]["source_observations"],
                canonical["content_source_observation"]["source_observations"],
            )

    def test_package_verifier_rejects_byte_only_task_tamper_and_manifest_rewrite(self):
        """A trusted manifest digest must reject whitespace-only and coordinated tampering."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"
            built = self.build_tasks(final_contract, case_set, output)
            self.assertEqual(built.returncode, 0, built.stderr + built.stdout)
            trusted_manifest = sha256_file(output / "paired-task-manifest.json")
            task_path = output / "baseline_full_depth_v1" / "R4-CASE-001.task.json"
            task_path.write_bytes(task_path.read_bytes() + b"\n")
            byte_only = self.verify_tasks(final_contract, case_set, output, expected_manifest=trusted_manifest)
            self.assertNotEqual(byte_only.returncode, 0)
            self.assertIn("TASK_FILE_SHA256_MISMATCH", byte_only.stderr)
            manifest_path = output / "paired-task-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["content_first_paired_task_manifest"]["pairs"][0]["task_files"]["baseline_full_depth_v1"]["task_file_sha256"] = sha256_file(task_path)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            coordinated = self.verify_tasks(final_contract, case_set, output, expected_manifest=trusted_manifest)
            self.assertNotEqual(coordinated.returncode, 0)
            self.assertIn("MANIFEST_FILE_SHA256_MISMATCH", coordinated.stderr)

    def test_package_verifier_rejects_semantic_task_leak_and_manifest_schema_extra_key(self):
        """A rehashed manifest cannot make a truth leak or extra task schema admissible."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"
            self.assertEqual(self.build_tasks(final_contract, case_set, output).returncode, 0)
            task_path = output / "screen_then_expand_v2" / "R4-CASE-001.task.json"
            task = json.loads(task_path.read_text(encoding="utf-8"))
            task["content_first_calibration_task"]["paired_execution_contract"]["truth%5Flabel"] = "hidden"
            task_path.write_text(json.dumps(task), encoding="utf-8")
            manifest_path = output / "paired-task-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["content_first_paired_task_manifest"]["pairs"][0]["task_files"]["screen_then_expand_v2"]["task_file_sha256"] = sha256_file(task_path)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            rejected = self.verify_tasks(final_contract, case_set, output)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("TASK_FORBIDDEN_LEAKAGE", rejected.stderr)

    def test_builder_rejects_receipt_binding_and_paired_contract_schema_tamper(self):
        """A valid file hash is insufficient when authorization or paired schema is fabricated."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            receipt = self.package_generation_receipt(final_contract, case_set, root / "denied")
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["package_generation_authorization_receipt"]["permitted_action"] = "model_execution"
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            denied = self.build_tasks(final_contract, case_set, root / "denied", receipt=receipt)
            self.assertNotEqual(denied.returncode, 0)
            self.assertIn("AUTHORIZATION_RECEIPT_INVALID", denied.stderr)
            receipt = self.package_generation_receipt(final_contract, case_set, root / "bad-contract")
            contract = json.loads(final_contract.read_text(encoding="utf-8"))
            contract["semantic_research_contract"]["paired_execution_contract"]["budgets"]["extra"] = 1
            final_contract.write_text(json.dumps(contract), encoding="utf-8")
            stale_receipt = self.build_tasks(final_contract, case_set, root / "bad-contract", receipt=receipt)
            self.assertNotEqual(stale_receipt.returncode, 0)
            self.assertIn("FINAL_CONTRACT_INCOMPLETE", stale_receipt.stderr)

    def test_builder_receipt_binds_the_exact_package_destination(self):
        """A receipt for one package path cannot authorize a different output directory."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            receipt = self.package_generation_receipt(final_contract, case_set, root / "approved-package")
            result = self.build_tasks(final_contract, case_set, root / "other-package", receipt=receipt)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AUTHORIZATION_RECEIPT_INVALID", result.stderr)
            self.assertFalse((root / "other-package").exists())

    def test_verifier_rejects_extra_package_payload_and_contract_local_schema_leak(self):
        """A package is closed-world, and its local observation schema cannot carry receiver data."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"
            self.assertEqual(self.build_tasks(final_contract, case_set, output).returncode, 0)
            trusted_manifest = sha256_file(output / "paired-task-manifest.json")
            (output / "hidden-truth.json").write_text('{"truth_label":"hidden"}', encoding="utf-8")
            extra = self.verify_tasks(final_contract, case_set, output, expected_manifest=trusted_manifest)
            self.assertNotEqual(extra.returncode, 0)
            self.assertIn("MANIFEST_INVALID", extra.stderr)
            schema = root / "preparation" / "00-合同准备" / "return-schema.json"
            payload = json.loads(schema.read_text(encoding="utf-8"))
            payload["content_source_observation"]["source_observations"][0]["receiver%5Fsnapshot%5Fsha256"] = None
            schema.write_text(json.dumps(payload), encoding="utf-8")
            schema_leak = self.build_tasks(final_contract, case_set, root / "schema-leak")
            self.assertNotEqual(schema_leak.returncode, 0)
            self.assertIn("SCHEMA_HASH_MISMATCH", schema_leak.stderr)

    def test_finalizer_requires_header_declared_safe_ordered_case_ids(self):
        """Formal IDs are frozen by the case-set header, never synthesized by the builder."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked, case_set, truth_set, final_contract = root / "locked.json", root / "cases.jsonl", root / "truth.jsonl", root / "final.json"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = r4_case_rows()
            rows[0]["formal_case_ids"][0] = "bad/name"
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))
            result = self.finalize_r4(locked, case_set, truth_set, final_contract)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CASE_SET_INVALID", result.stderr)

    def test_builder_mid_build_failure_is_atomic_and_retry_is_byte_identical(self):
        """A failed staging build cannot leave a package or alter a clean retry."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            output = root / "paired-tasks"
            failed = self.build_tasks(final_contract, case_set, output, fail_after=17)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("TASK_BUILD_FAILED", failed.stderr)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.glob(".paired-tasks.tmp-*")), [])
            self.assertFalse((root / "R4-CASE-001.task.json").exists())

            first = self.build_tasks(final_contract, case_set, output)
            clean = root / "paired-tasks-clean"
            second = self.build_tasks(final_contract, case_set, clean)
            self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
            self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
            first_bytes = {path.relative_to(output): path.read_bytes() for path in output.rglob("*.task.json")}
            second_bytes = {path.relative_to(clean): path.read_bytes() for path in clean.rglob("*.task.json")}
            self.assertEqual(first_bytes, second_bytes)

    def test_builder_rejects_drifted_contract_local_frozen_reference_before_staging(self):
        """A hash-valid contract cannot point at a changed prompt, schema, config, or rubric."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final_contract, case_set = self.frozen_r4_contract_and_case_set(root)
            config = root / "preparation" / "00-合同准备" / "model-config.json"
            config.write_text('{"temperature":1}\n', encoding="utf-8")

            result = self.build_tasks(final_contract, case_set, root / "paired-tasks")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CONFIG_HASH_MISMATCH", result.stderr)
            self.assertFalse((root / "paired-tasks").exists())

    def test_content_first_lock_requires_real_term_pack_and_empty_case_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            locked = root / "locked.json"
            draft, term_pack = self.r4_preparation(root)

            missing = run(
                LOCK,
                "--contract",
                str(draft),
                "--authorization-reference",
                "USER-R4-PREP",
                "--locked-at",
                "2026-08-25T00:00:00Z",
                "--output",
                str(locked),
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("TERMINOLOGY_BRIDGE_REQUIRED", missing.stderr)

            valid = self.lock_r4(draft, term_pack, locked)
            self.assertEqual(valid.returncode, 0, valid.stderr + valid.stdout)
            body = json.loads(locked.read_text(encoding="utf-8"))["semantic_research_contract"]
            self.assertEqual(
                body["terminology_architecture"]["term_pack_sha256"],
                sha256_file(term_pack),
            )
            self.assertIsNone(body["calibration_case_set_reference_and_hash"]["sha256"])
            self.assertEqual(body["control_case_rule"]["case_ids"], [])
            self.assertFalse(body["execution_authorized"])
            self.assertFalse(body["full_screening_authorization"])
            self.assertIsNone(body["full_screening_authorization_reference"])
            self.assertEqual(
                body["content_first_policy"]["content_method_state"],
                "CONTENT_CALIBRATION_INCOMPLETE",
            )
            self.assertEqual(
                body["content_first_policy"]["content_full_screening_state"],
                "NOT_AUTHORIZED",
            )
            self.assertEqual(
                body["content_first_policy"]["downstream_release_state"],
                "RESEARCH_ONLY_BLOCKED",
            )

    def test_finalizer_rejects_development_case_in_formal_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
            final_contract = root / "final.json"
            locked_result = self.lock_r4(draft, term_pack, locked)
            self.assertEqual(locked_result.returncode, 0, locked_result.stderr)
            rows = r4_case_rows()
            rows[1]["provenance"]["development_regression_only"] = True
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))

            result = self.finalize_r4(locked, case_set, truth_set, final_contract)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("DEVELOPMENT_CASE_IN_FORMAL_SET", result.stderr)

    def test_finalizer_rejects_formal_cases_without_machine_bound_holdout_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = r4_case_rows()
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))

            result = self.finalize_r4(
                locked,
                case_set,
                truth_set,
                root / "final.json",
                materialize_provenance=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CASE_PROVENANCE_INVALID", result.stderr)
            self.assertFalse((root / "final.json").exists())

    def test_finalizer_enforces_30_10_origin_and_category_composition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = self.bound_r4_case_rows(locked)
            cases = [row for row in rows if row.get("record_type") == "calibration_case"]
            cases[0]["provenance"] = cases[14]["provenance"]
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))

            result = self.finalize_r4(locked, case_set, truth_set, root / "final.json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SELECTION_ORIGIN_COMPOSITION_INVALID", result.stderr)

    def test_finalizer_requires_retained_cases_to_equal_manifest_unexecuted_membership(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = self.bound_r4_case_rows(locked)
            retained = next(
                row for row in rows
                if row.get("record_type") == "calibration_case"
                and row["provenance"]["selection_origin"] == "retained_r3_unexecuted"
            )
            manifest_path = root / "preparation" / "02-校准案例候选" / "r3-source-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))["r3_case_source_manifest"]
            development = manifest["cases"][0]
            retained["provenance"].update({
                "r3_source_case_id": development["r3_source_case_id"],
                "source_snapshot_reference": development["source_snapshot_reference"],
                "source_snapshot_sha256": development["source_snapshot_sha256"],
            })
            case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
            write_jsonl(case_set, rows)
            write_jsonl(truth, r4_truth_rows(rows))

            result = self.finalize_r4(locked, case_set, truth, root / "final.json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("R3_RETAINED_MEMBERSHIP_MISMATCH", result.stderr)

    def test_finalizer_requires_ten_distinct_normalized_official_source_nodes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = self.bound_r4_case_rows(locked)
            new_cases = [
                row for row in rows
                if row.get("record_type") == "calibration_case"
                and row["provenance"]["selection_origin"] == "new_unseen_positive"
            ]
            first, second = new_cases[:2]
            second["taxonomy_node"] = json.loads(json.dumps(first["taxonomy_node"]))
            receipt_path = root / "preparation" / second["provenance"]["selection_receipt_reference"]
            receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt_payload["new_unseen_selection_receipt"]["source_node_id"] = first[
                "taxonomy_node"
            ]["taxonomy_node_id"].lower()
            second["taxonomy_node"]["taxonomy_node_id"] = first["taxonomy_node"][
                "taxonomy_node_id"
            ].lower()
            receipt_path.write_text(json.dumps(receipt_payload, sort_keys=True) + "\n", encoding="utf-8")
            second["provenance"]["selection_receipt_sha256"] = sha256_file(receipt_path)
            case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
            write_jsonl(case_set, rows)
            write_jsonl(truth, r4_truth_rows(rows))

            result = self.finalize_r4(locked, case_set, truth, root / "final.json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NEW_SELECTION_SOURCE_NODE_REUSE", result.stderr)

    def test_finalizer_temp_publish_failure_leaves_no_output_or_staging_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = self.bound_r4_case_rows(locked)
            case_set, truth = root / "cases.jsonl", root / "truth.jsonl"
            output = root / "final.json"
            write_jsonl(case_set, rows)
            write_jsonl(truth, r4_truth_rows(rows))

            result = self.finalize_r4(
                locked, case_set, truth, output, fail_after_temp_write=True
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FINAL_CONTRACT_PUBLISH_FAILED", result.stderr)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.glob(".final.json.tmp-*")), [])

    def test_finalizer_rejects_new_unseen_case_that_is_not_a_known_positive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = self.bound_r4_case_rows(locked)
            cases = [row for row in rows if row.get("record_type") == "calibration_case"]
            new_case, retained_case = cases[0], cases[14]
            new_case["primary_category"], retained_case["primary_category"] = (
                retained_case["primary_category"],
                new_case["primary_category"],
            )
            new_case["known_positive"], retained_case["known_positive"] = False, True
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))

            result = self.finalize_r4(locked, case_set, truth_set, root / "final.json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NEW_UNSEEN_POSITIVE_REQUIRED", result.stderr)

    def test_finalizer_rechecks_retained_r3_unexecuted_snapshot_and_hash(self):
        scenarios = (
            "executed",
            "tampered",
            "duplicate_source_id",
            "normalized_duplicate_source_id",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                draft, term_pack = self.r4_preparation(root)
                locked = root / "locked.json"
                case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
                self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
                rows = self.bound_r4_case_rows(locked)
                retained = [
                    row
                    for row in rows
                    if row.get("record_type") == "calibration_case"
                    and row["provenance"]["selection_origin"] == "retained_r3_unexecuted"
                ]
                if scenario in {"duplicate_source_id", "normalized_duplicate_source_id"}:
                    retained[1]["provenance"]["r3_source_case_id"] = retained[0][
                        "provenance"
                    ]["r3_source_case_id"] + ("" if scenario == "duplicate_source_id" else "\uff21")
                    if scenario == "normalized_duplicate_source_id":
                        retained[1]["provenance"]["r3_source_case_id"] = (
                            retained[0]["provenance"]["r3_source_case_id"].lower()
                        )
                    second_path = locked.parent / "preparation" / retained[1][
                        "provenance"
                    ]["source_snapshot_reference"]
                    second_payload = json.loads(second_path.read_text(encoding="utf-8"))
                    second_payload["retained_r3_case_snapshot"]["r3_source_case_id"] = retained[1][
                        "provenance"
                    ]["r3_source_case_id"]
                    second_path.write_text(
                        json.dumps(second_payload, sort_keys=True) + "\n", encoding="utf-8"
                    )
                    retained[1]["provenance"]["source_snapshot_sha256"] = sha256_file(
                        second_path
                    )
                    expected = "R3_SOURCE_CASE_ID_REUSE"
                else:
                    provenance = retained[0]["provenance"]
                    path = locked.parent / "preparation" / provenance[
                        "source_snapshot_reference"
                    ]
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if scenario == "executed":
                        payload["retained_r3_case_snapshot"]["execution_state"] = "executed"
                        path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
                        provenance["source_snapshot_sha256"] = sha256_file(path)
                        expected = "R3_SOURCE_NOT_UNEXECUTED"
                    else:
                        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
                        expected = "PROVENANCE_ASSET_HASH_MISMATCH"
                write_jsonl(case_set, rows)
                write_jsonl(truth_set, r4_truth_rows(rows))

                result = self.finalize_r4(locked, case_set, truth_set, root / "final.json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_finalizer_rejects_provenance_path_aliases_and_copied_hash_reuse(self):
        scenarios = ("escape", "symlink", "hardlink", "same_hash_copy")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                draft, term_pack = self.r4_preparation(root)
                locked = root / "locked.json"
                case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
                self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
                rows = self.bound_r4_case_rows(locked)
                retained = [
                    row
                    for row in rows
                    if row.get("record_type") == "calibration_case"
                    and row["provenance"]["selection_origin"] == "retained_r3_unexecuted"
                ]
                first = locked.parent / "preparation" / retained[0]["provenance"][
                    "source_snapshot_reference"
                ]
                if scenario == "escape":
                    retained[0]["provenance"]["source_snapshot_reference"] = "../outside.json"
                    expected = "PROVENANCE_REFERENCE_INVALID"
                else:
                    alias = first.with_name(f"alias-{scenario}.json")
                    if scenario == "symlink":
                        alias.symlink_to(first)
                        expected = "PROVENANCE_SYMLINK_FORBIDDEN"
                    elif scenario == "hardlink":
                        os.link(first, alias)
                        expected = "PROVENANCE_ASSET_IDENTITY_REUSE"
                    else:
                        shutil.copyfile(first, alias)
                        expected = "PROVENANCE_ASSET_HASH_REUSE"
                    retained[1]["provenance"]["source_snapshot_reference"] = alias.relative_to(
                        locked.parent / "preparation"
                    ).as_posix()
                    retained[1]["provenance"]["source_snapshot_sha256"] = sha256_file(alias)
                write_jsonl(case_set, rows)
                write_jsonl(truth_set, r4_truth_rows(rows))

                result = self.finalize_r4(locked, case_set, truth_set, root / "final.json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_finalizer_rechecks_new_selection_receipt_against_preparation_lock(self):
        scenarios = (
            "selected_before_lock",
            "selected_equal_lock",
            "locked_hash_drift",
            "source_node_drift",
            "official_node_semantics_drift",
            "prior_exposure_not_unseen",
            "normalized_duplicate_receipt_id",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                draft, term_pack = self.r4_preparation(root)
                locked = root / "locked.json"
                case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
                self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
                rows = self.bound_r4_case_rows(locked)
                new_cases = [
                    row for row in rows
                    if row.get("record_type") == "calibration_case"
                    and row["provenance"]["selection_origin"] == "new_unseen_positive"
                ]
                new_case = new_cases[0]
                provenance = new_case["provenance"]
                path = locked.parent / "preparation" / provenance[
                    "selection_receipt_reference"
                ]
                payload = json.loads(path.read_text(encoding="utf-8"))
                receipt = payload["new_unseen_selection_receipt"]
                if scenario == "selected_before_lock":
                    receipt["selected_at"] = "2026-08-24T23:59:59Z"
                    expected = "NEW_SELECTION_BEFORE_PREPARATION_LOCK"
                elif scenario == "selected_equal_lock":
                    receipt["selected_at"] = "2026-08-25T00:00:00Z"
                    expected = "NEW_SELECTION_BEFORE_PREPARATION_LOCK"
                elif scenario == "locked_hash_drift":
                    receipt["locked_input_sha256"] = "ab" * 32
                    expected = "NEW_SELECTION_LOCK_BINDING_INVALID"
                elif scenario == "source_node_drift":
                    receipt["source_node_id"] = "NODE-NOT-IN-OFFICIAL-SNAPSHOT"
                    expected = "NEW_SELECTION_SOURCE_NODE_INVALID"
                elif scenario == "official_node_semantics_drift":
                    new_case["taxonomy_node"]["name_zh"] = "不是官方快照中的节点名称"
                    expected = "NEW_SELECTION_OFFICIAL_NODE_MISMATCH"
                elif scenario == "prior_exposure_not_unseen":
                    receipt["prior_method_exposure_state"] = "previously_executed"
                    expected = "NEW_SELECTION_NOT_UNSEEN"
                else:
                    other_path = locked.parent / "preparation" / new_cases[1][
                        "provenance"
                    ]["selection_receipt_reference"]
                    other_payload = json.loads(other_path.read_text(encoding="utf-8"))
                    receipt["receipt_id"] = other_payload["new_unseen_selection_receipt"][
                        "receipt_id"
                    ].lower()
                    expected = "NEW_SELECTION_RECEIPT_ID_REUSE"
                path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
                provenance["selection_receipt_sha256"] = sha256_file(path)
                write_jsonl(case_set, rows)
                write_jsonl(truth_set, r4_truth_rows(rows))

                result = self.finalize_r4(locked, case_set, truth_set, root / "final.json")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_finalizer_rejects_unknown_explicit_execution_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked, case_set = root / "locked.json", root / "cases.jsonl"
            truth_set, final_contract = root / "truth.jsonl", root / "final.json"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            locked_payload = json.loads(locked.read_text(encoding="utf-8"))
            locked_payload["semantic_research_contract"]["execution_mode"] = "strict-audit"
            locked.write_text(json.dumps(locked_payload), encoding="utf-8")
            rows = r4_case_rows()
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))

            result = self.finalize_r4(locked, case_set, truth_set, final_contract)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("EXECUTION_MODE_INVALID", result.stderr)

    def test_finalizer_requires_explicit_and_matching_case_truth_dispositions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
            final_contract = root / "final.json"
            locked_result = self.lock_r4(draft, term_pack, locked)
            self.assertEqual(locked_result.returncode, 0, locked_result.stderr)
            rows = r4_case_rows()
            rows[1]["provenance"].pop("development_regression_only")
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))
            missing_provenance = self.finalize_r4(locked, case_set, truth_set, final_contract)
            self.assertNotEqual(missing_provenance.returncode, 0)
            self.assertIn("CASE_PROVENANCE_INVALID", missing_provenance.stderr)
            rows = r4_case_rows()
            write_jsonl(case_set, rows)
            truth = r4_truth_rows(rows)
            truth[0]["known_positive"] = False
            write_jsonl(truth_set, truth)
            mismatch = self.finalize_r4(locked, case_set, truth_set, root / "final-mismatch.json")
            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn("SOURCE_TRUTH_DISPOSITION_MISMATCH", mismatch.stderr)

    def test_finalizer_rejects_policy_excluded_id_and_write_scope_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked, case_set = root / "locked.json", root / "cases.jsonl"
            truth_set, final_contract = root / "truth.jsonl", root / "final.json"
            payload = json.loads(draft.read_text(encoding="utf-8"))
            contract = payload["semantic_research_contract"]
            contract["calibration_case_policy"]["development_case_ids_excluded_from_formal"] = ["R4-CASE-001"]
            draft.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = r4_case_rows()
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))
            excluded = self.finalize_r4(locked, case_set, truth_set, final_contract)
            self.assertNotEqual(excluded.returncode, 0)
            self.assertIn("DEVELOPMENT_CASE_ID_IN_FORMAL_SET", excluded.stderr)
            payload = json.loads(draft.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["allowed_writes"] = ["02-共享应用知识/base.xlsx"]
            draft.write_text(json.dumps(payload), encoding="utf-8")
            unsafe_write = self.lock_r4(draft, term_pack, root / "unsafe.json")
            self.assertNotEqual(unsafe_write.returncode, 0)
            self.assertIn("CONTENT_FIRST_DEFAULT_DENY_REQUIRED", unsafe_write.stderr)

    def test_finalizer_rejects_category_count_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
            final_contract = root / "final.json"
            locked_result = self.lock_r4(draft, term_pack, locked)
            self.assertEqual(locked_result.returncode, 0, locked_result.stderr)
            rows = r4_case_rows()
            rows[1]["primary_category"] = "hidden_positive"
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))

            result = self.finalize_r4(locked, case_set, truth_set, final_contract)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CATEGORY_COUNT_DRIFT", result.stderr)

    def test_finalizer_rejects_truth_row_count_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
            final_contract = root / "final.json"
            locked_result = self.lock_r4(draft, term_pack, locked)
            self.assertEqual(locked_result.returncode, 0, locked_result.stderr)
            rows = r4_case_rows()
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows)[:-1])

            result = self.finalize_r4(locked, case_set, truth_set, final_contract)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCE_TRUTH_ROW_COUNT_INVALID", result.stderr)

    def test_content_first_finalizer_binds_real_case_and_truth_hashes_to_new_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            case_set, truth_set = root / "cases.jsonl", root / "truth.jsonl"
            final_contract = root / "final.json"
            locked_result = self.lock_r4(draft, term_pack, locked)
            self.assertEqual(locked_result.returncode, 0, locked_result.stderr)
            rows = self.bound_r4_case_rows(locked)
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))

            result = self.finalize_r4(locked, case_set, truth_set, final_contract)

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            contract = json.loads(final_contract.read_text(encoding="utf-8"))["semantic_research_contract"]
            self.assertEqual(contract["contract_state"], "frozen")
            self.assertNotEqual(
                contract["contract_version"],
                contract["case_preparation_gate"]["preparation_contract_version"],
            )
            self.assertEqual(
                contract["calibration_case_set_reference_and_hash"]["sha256"],
                sha256_file(case_set),
            )
            self.assertEqual(contract["source_truth_package_sha256"], sha256_file(truth_set))

    def test_content_first_workspace_rechecks_local_frozen_inputs_and_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked, case_set = root / "locked.json", root / "cases.jsonl"
            truth_set, final_contract = root / "truth.jsonl", root / "final.json"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = self.bound_r4_case_rows(locked)
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))
            self.assertEqual(
                self.finalize_r4(locked, case_set, truth_set, final_contract).returncode,
                0,
            )
            workspace = root / "workspace"
            for relative in (
                "00-合同",
                "00-合同准备",
                "01-术语桥",
                "01-节点快照",
                "02-校准案例",
                "02-校准案例候选",
                "03-来源真值",
            ):
                (workspace / relative).mkdir(parents=True)
            contract_path = workspace / "00-合同" / "semantic-research-contract.json"
            contract_path.write_bytes(final_contract.read_bytes())
            (workspace / "01-术语桥" / "terminology-bridge.jsonl").write_bytes(term_pack.read_bytes())
            preparation_root = term_pack.parent.parent
            (workspace / "01-节点快照" / "taxonomy.json").write_bytes(
                (preparation_root / "01-节点快照" / "taxonomy.json").read_bytes()
            )
            (workspace / "00-合同准备" / "prompt.md").write_bytes(
                (preparation_root / "00-合同准备" / "prompt.md").read_bytes()
            )
            for name in ("prompt-template.md", "return-schema.json", "model-config.json", "rubric.md"):
                (workspace / "00-合同准备" / name).write_bytes(
                    (preparation_root / "00-合同准备" / name).read_bytes()
                )
            (workspace / "02-校准案例" / "formal-case-set.jsonl").write_bytes((root / "cases.jsonl").read_bytes())
            (workspace / "02-校准案例" / "visible-case-set.jsonl").write_bytes(
                (root / "final-visible-case-set.jsonl").read_bytes()
            )
            (workspace / "02-校准案例" / "visible-case-freeze-receipt.json").write_bytes(
                (root / "final-visible-case-freeze-receipt.json").read_bytes()
            )
            shutil.copytree(
                preparation_root / "02-校准案例" / "provenance",
                workspace / "02-校准案例" / "provenance",
            )
            (workspace / "02-校准案例候选" / "r3-source-manifest.json").write_bytes(
                (preparation_root / "02-校准案例候选" / "r3-source-manifest.json").read_bytes()
            )
            shutil.copytree(
                preparation_root / "02-校准案例候选" / "r3-source-snapshots",
                workspace / "02-校准案例候选" / "r3-source-snapshots",
            )
            local_truth = workspace / "03-来源真值" / "source-truth.jsonl"
            local_truth.write_bytes(truth_set.read_bytes())
            (workspace / "00-合同" / "workspace-manifest.json").write_text(
                json.dumps({"contract_sha256": sha256_file(contract_path)}), encoding="utf-8"
            )

            valid = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")

            self.assertEqual(valid.returncode, 0, valid.stderr + valid.stdout)
            retained_snapshot = next(
                (workspace / "02-校准案例候选" / "r3-source-snapshots").glob(
                    "*.snapshot.json"
                )
            )
            retained_snapshot_bytes = retained_snapshot.read_bytes()
            retained_snapshot.write_bytes(retained_snapshot_bytes + b" ")
            provenance_tamper = run(
                VALIDATE_WORKSPACE, str(workspace), "--format", "json"
            )
            self.assertNotEqual(provenance_tamper.returncode, 0)
            self.assertIn("PROVENANCE_ASSET_HASH_MISMATCH", provenance_tamper.stdout)
            retained_snapshot.write_bytes(retained_snapshot_bytes)
            handoff = workspace / "04-模型交接"
            handoff.mkdir()
            packet_path = handoff / "packet.json"
            bodies = (
                ("semantic_model_task", {"research_contract_id": "RC2-TEST-001", "contract_version": "2.1.0-content-first.final.1"}),
                ("semantic_model_return", {"research_contract_id": "RC2-TEST-001", "contract_version": "2.1.0-content-first.final.1", "result_state": "UNVERIFIED"}),
                ("semantic_model_receipt", {"research_contract_id": "RC2-TEST-001", "contract_version": "2.1.0-content-first.final.1", "acceptance_state": "UNVERIFIED"}),
            )
            for key, body in bodies:
                packet_path.write_text(json.dumps({key: body}), encoding="utf-8")
                self.assertEqual(run(VALIDATE_WORKSPACE, str(workspace), "--format", "json").returncode, 0)
            packet_path.write_text(
                json.dumps({
                    "metadata": {"research_contract_id": "RC2-TEST-001", "contract_version": "2.1.0-content-first.final.1"},
                    "semantic_model_task": {"research_contract_id": "RC2-TEST-001", "contract_version": "wrong"},
                }),
                encoding="utf-8",
            )
            shadowed = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
            self.assertNotEqual(shadowed.returncode, 0)
            self.assertIn("MODEL_PACKET_CONTRACT_VERSION_MISMATCH", shadowed.stdout)
            packet_path.write_text(
                json.dumps({
                    "semantic_model_task": bodies[0][1],
                    "semantic_model_return": bodies[1][1],
                }),
                encoding="utf-8",
            )
            multiple = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
            self.assertNotEqual(multiple.returncode, 0)
            self.assertIn("MODEL_PACKET_FORMAL_RECORD_INVALID", multiple.stdout)
            malformed_formal_key_cases = (
                (
                    "valid_dict_plus_null_formal_key",
                    {
                        "semantic_model_task": bodies[0][1],
                        "semantic_model_return": None,
                    },
                ),
                (
                    "valid_dict_plus_array_formal_key",
                    {
                        "semantic_model_task": bodies[0][1],
                        "semantic_model_receipt": [],
                    },
                ),
                (
                    "single_formal_key_with_non_dict_value",
                    {"semantic_model_return": "not-a-record"},
                ),
            )
            for case_name, packet in malformed_formal_key_cases:
                with self.subTest(case_name=case_name):
                    packet_path.write_text(json.dumps(packet), encoding="utf-8")
                    malformed = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
                    self.assertNotEqual(malformed.returncode, 0)
                    self.assertIn("MODEL_PACKET_FORMAL_RECORD_INVALID", malformed.stdout)
            packet_path.unlink()
            taxonomy = workspace / "01-节点快照" / "taxonomy.json"
            taxonomy.unlink()
            missing_taxonomy = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
            self.assertNotEqual(missing_taxonomy.returncode, 0)
            self.assertIn("TAXONOMY_SNAPSHOT_MISSING", missing_taxonomy.stdout)
            taxonomy.write_bytes((preparation_root / "01-节点快照" / "taxonomy.json").read_bytes())
            prompt = workspace / "00-合同准备" / "prompt.md"
            prompt.unlink()
            missing_prompt = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
            self.assertNotEqual(missing_prompt.returncode, 0)
            self.assertIn("PAIRED_PROMPT_MISSING", missing_prompt.stdout)
            prompt.write_bytes((preparation_root / "00-合同准备" / "prompt.md").read_bytes())
            unsafe_contract = json.loads(contract_path.read_text(encoding="utf-8"))
            unsafe_contract["semantic_research_contract"]["allowed_writes"] = ["02-共享应用知识/base.xlsx"]
            contract_path.write_text(json.dumps(unsafe_contract), encoding="utf-8")
            (workspace / "00-合同" / "workspace-manifest.json").write_text(
                json.dumps({"contract_sha256": sha256_file(contract_path)}), encoding="utf-8"
            )
            unsafe_write = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
            self.assertNotEqual(unsafe_write.returncode, 0)
            self.assertIn("CONTRACT_INCOMPLETE", unsafe_write.stdout)
            contract_path.write_bytes(final_contract.read_bytes())
            (workspace / "00-合同" / "workspace-manifest.json").write_text(
                json.dumps({"contract_sha256": sha256_file(contract_path)}), encoding="utf-8"
            )
            bad_screening = workspace / "03-运行原始记录" / "candidate" / "screening-records.jsonl"
            bad_screening.parent.mkdir(parents=True)
            write_jsonl(
                bad_screening,
                [{"research_contract_id": "RC2-TEST-001", "contract_version": "wrong", "screening_result": "ambiguous"}],
            )
            wrong_record = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
            self.assertNotEqual(wrong_record.returncode, 0)
            self.assertIn("SCREENING_CONTRACT_VERSION_MISMATCH", wrong_record.stdout)
            local_truth.write_text(local_truth.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            tampered_input = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
            self.assertNotEqual(tampered_input.returncode, 0)
            self.assertIn("SOURCE_TRUTH_PACKAGE_HASH_MISMATCH", tampered_input.stdout)
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["semantic_research_contract"]["execution_authorized"] = True
            contract["semantic_research_contract"]["execution_mode"] = "strict-audit"
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            tampered_contract = run(VALIDATE_WORKSPACE, str(workspace), "--format", "json")
            self.assertNotEqual(tampered_contract.returncode, 0)
            self.assertIn("CONTRACT_INCOMPLETE", tampered_contract.stdout)
            self.assertIn("execution_mode:invalid", tampered_contract.stdout)

    def assert_generalized_contract(self, contract):
        self.assertIn("execution_mode", contract)
        self.assertIn("terminology_architecture", contract)
        self.assertIn("calibration_case_policy", contract)
        self.assertIn("retrieval_efficiency_gates", contract)
        self.assertIn("candidate_method_contract", contract)
        self.assertIn("baseline_method_contract", contract)
        self.assertEqual(contract["execution_mode"], "content_first")
        self.assertFalse(contract["execution_authorized"])
        self.assertEqual(
            contract["terminology_architecture"], EXPECTED_TERMINOLOGY_ARCHITECTURE
        )
        self.assertEqual(
            contract["calibration_case_policy"], EXPECTED_CALIBRATION_CASE_POLICY
        )
        self.assertEqual(
            contract["retrieval_efficiency_gates"], EXPECTED_RETRIEVAL_EFFICIENCY_GATES
        )
        self.assertEqual(contract["candidate_method_contract"], "screen_then_expand_v2")
        self.assertEqual(contract["baseline_method_contract"], "baseline_full_depth_v1")
        self.assertEqual(
            contract["content_first_policy"]["truth_scorecard_contract_version"],
            "2.0-r4",
        )

    def test_r4_preparation_lock_rejects_missing_truth_scorecard_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            payload = json.loads(draft.read_text(encoding="utf-8"))
            payload["semantic_research_contract"]["content_first_policy"].pop(
                "truth_scorecard_contract_version"
            )
            draft.write_text(json.dumps(payload), encoding="utf-8")
            locked = root / "locked.json"

            result = self.lock_r4(draft, term_pack, locked)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("truth_scorecard_contract_version", result.stderr)

    def test_r4_finalizer_rejects_truth_scorecard_marker_removed_after_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked = root / "locked.json"
            lock_result = self.lock_r4(draft, term_pack, locked)
            self.assertEqual(lock_result.returncode, 0, lock_result.stderr)
            locked_payload = json.loads(locked.read_text(encoding="utf-8"))
            locked_payload["semantic_research_contract"]["content_first_policy"].pop(
                "truth_scorecard_contract_version"
            )
            locked.write_text(json.dumps(locked_payload), encoding="utf-8")
            rows = r4_case_rows()
            case_set = root / "cases.jsonl"
            truth_set = root / "truth.jsonl"
            write_jsonl(case_set, rows)
            write_jsonl(truth_set, r4_truth_rows(rows))

            result = self.finalize_r4(
                locked, case_set, truth_set, root / "final.json"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PREPARATION_", result.stderr)

    def test_same_name_plugins_expose_beta3_generalized_contract(self):
        map_manifest = json.loads((MAP_PLUGIN / ".codex-plugin/plugin.json").read_text())
        director_manifest = json.loads(
            (DIRECTOR_PLUGIN / ".codex-plugin/plugin.json").read_text()
        )
        self.assertEqual(map_manifest["name"], "industry-application-map-builder")
        self.assertEqual(map_manifest["version"], "0.4.0-beta.3")
        self.assertEqual(director_manifest["name"], "foreign-trade-workflow-director")
        self.assertEqual(director_manifest["version"], "0.3.0-beta.2")
        for contract_template in CONTRACT_TEMPLATES:
            with self.subTest(contract_template=contract_template.name):
                contract = json.loads(contract_template.read_text())["semantic_research_contract"]
                self.assert_generalized_contract(contract)

    def test_preparation_initializer_creates_real_empty_product_neutral_term_pack(self):
        with tempfile.TemporaryDirectory() as directory:
            map_root = Path(directory) / "map-root"
            map_root.mkdir()
            contract_path = Path(directory) / "contract.json"
            payload = json.loads(CONTENT_FIRST_CONTRACT.read_text(encoding="utf-8"))
            contract = payload["semantic_research_contract"]
            contract["research_contract_id"] = "RC2-TERM-PACK-001"
            contract["contract_version"] = "1.0"
            contract_path.write_text(json.dumps(payload), encoding="utf-8")

            result = run(INIT_PREP, "--map-root", str(map_root), "--contract", str(contract_path))

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            response = json.loads(result.stdout)
            workspace = Path(response["preparation_workspace"])
            expected_workspace = (
                map_root
                / "05-工作区"
                / "行业语义研究"
                / "RC2-TERM-PACK-001"
            )
            self.assertEqual(workspace.resolve(), expected_workspace.resolve())
            self.assertFalse(
                (
                    map_root
                    / "05-工作区"
                    / "行业语义准备"
                    / "RC2-TERM-PACK-001"
                ).exists()
            )
            pack = Path(response["terminology_bridge"])
            self.assertTrue(pack.is_file())
            self.assertEqual(
                hashlib.sha256(pack.read_bytes()).hexdigest(),
                response["terminology_bridge_sha256"],
            )
            manifest = Path(response["manifest"])
            self.assertTrue(manifest.is_file())
            self.assertEqual(
                json.loads(manifest.read_text(encoding="utf-8"))["terminology_bridge_sha256"],
                response["terminology_bridge_sha256"],
            )
            contract_copy = workspace / "00-合同准备" / "semantic-research-contract.draft.json"
            self.assertEqual(contract_copy.read_bytes(), contract_path.read_bytes())
            self.assertEqual(contract_copy.stat().st_mode & 0o222, 0)
            rows = load_jsonl(pack)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["accepted_term_count"], 0)
            self.assertFalse(rows[0]["company_data_allowed"])
            self.assertEqual(rows[0]["term_pack_state"], "frozen_empty_cold_start")
            self.assertTrue(
                (workspace / "02-校准案例候选" / "r3-source-snapshots").is_dir()
            )
            self.assertFalse(
                (workspace / "02-校准案例候选" / "r3-source-manifest.json").exists()
            )
            self.assertTrue(response["r3_source_manifest_required_before_lock"])
            self.assertFalse(response["r3_source_manifest_created"])
            self.assertEqual(
                {path.relative_to(workspace).as_posix() for path in workspace.iterdir()},
                {
                    "00-合同准备",
                    "01-节点快照",
                    "01-术语桥",
                    "02-校准案例候选",
                    "03-来源真值准备",
                    "07-报告",
                },
            )
            self.assertFalse(any("模型任务" in path.name for path in workspace.rglob("*")))

    def test_preparation_initializer_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            map_root = Path(directory) / "map-root"
            map_root.mkdir()
            contract_path = Path(directory) / "contract.json"
            payload = json.loads(CONTENT_FIRST_CONTRACT.read_text(encoding="utf-8"))
            contract = payload["semantic_research_contract"]
            contract["research_contract_id"] = "RC2-TERM-PACK-002"
            contract["contract_version"] = "1.0"
            contract_path.write_text(json.dumps(payload), encoding="utf-8")

            first = run(INIT_PREP, "--map-root", str(map_root), "--contract", str(contract_path))
            second = run(INIT_PREP, "--map-root", str(map_root), "--contract", str(contract_path))

            self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("DESTINATION_EXISTS", second.stderr)

    def test_preparation_initializer_rejects_method_arm_drift_before_creating_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            map_root = Path(directory) / "map-root"
            map_root.mkdir()
            contract_path = Path(directory) / "contract.json"
            payload = json.loads(CONTENT_FIRST_CONTRACT.read_text(encoding="utf-8"))
            contract = payload["semantic_research_contract"]
            contract["research_contract_id"] = "RC2-TERM-PACK-METHOD-DRIFT"
            contract["contract_version"] = "1.0"
            contract["candidate_method_contract"] = "screen_then_expand_v3"
            contract_path.write_text(json.dumps(payload), encoding="utf-8")

            result = run(
                INIT_PREP, "--map-root", str(map_root), "--contract", str(contract_path)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("METHOD_ARMS_INVALID", result.stderr)
            destination = (
                map_root
                / "05-工作区"
                / "行业语义研究"
                / "RC2-TERM-PACK-METHOD-DRIFT"
            )
            self.assertFalse(destination.exists())

    def test_preparation_initializer_failure_leaves_no_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            map_root = Path(directory) / "map-root"
            map_root.mkdir()
            contract_path = Path(directory) / "contract.json"
            payload = json.loads(CONTENT_FIRST_CONTRACT.read_text(encoding="utf-8"))
            contract = payload["semantic_research_contract"]
            contract["research_contract_id"] = "RC2-TERM-PACK-INVALID"
            contract["contract_version"] = "1.0"
            contract["contract_state"] = "frozen"
            contract_path.write_text(json.dumps(payload), encoding="utf-8")

            result = run(INIT_PREP, "--map-root", str(map_root), "--contract", str(contract_path))

            destination = (
                map_root / "05-工作区" / "行业语义研究" / "RC2-TERM-PACK-INVALID"
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CONTRACT_STATE_INVALID", result.stderr)
            self.assertFalse(destination.exists())

    def test_preparation_initializer_cleans_post_staging_failure_and_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            fake_skill = temporary_root / "fake-skill"
            fake_initializer = (
                fake_skill / "scripts/init_content_first_preparation_workspace.py"
            )
            fake_initializer.parent.mkdir(parents=True)
            shutil.copyfile(INIT_PREP, fake_initializer)
            map_root = temporary_root / "map-root"
            map_root.mkdir()
            contract_path = temporary_root / "contract.json"
            payload = json.loads(CONTENT_FIRST_CONTRACT.read_text(encoding="utf-8"))
            contract = payload["semantic_research_contract"]
            contract["research_contract_id"] = "RC2-TERM-PACK-CLEANUP"
            contract["contract_version"] = "1.0"
            contract_path.write_text(json.dumps(payload), encoding="utf-8")
            destination = (
                map_root / "05-工作区" / "行业语义研究" / "RC2-TERM-PACK-CLEANUP"
            )

            first = run(
                fake_initializer, "--map-root", str(map_root), "--contract", str(contract_path)
            )

            self.assertNotEqual(first.returncode, 0)
            self.assertIn("PREPARATION_CREATE_FAILED", first.stderr)
            self.assertIn("terminology-bridge.template.jsonl", first.stderr)
            self.assertFalse(destination.exists())
            self.assertEqual(
                list(destination.parent.glob(".RC2-TERM-PACK-CLEANUP.tmp-*")), []
            )

            fake_template = (
                fake_skill / "assets/content-first/terminology-bridge.template.jsonl"
            )
            fake_template.parent.mkdir(parents=True)
            shutil.copyfile(TERM_TEMPLATE, fake_template)

            second = run(
                fake_initializer, "--map-root", str(map_root), "--contract", str(contract_path)
            )

            self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
            self.assertEqual(
                Path(json.loads(second.stdout)["preparation_workspace"]).resolve(),
                destination.resolve(),
            )

    def test_term_validator_rejects_company_fields_recursively(self):
        with tempfile.TemporaryDirectory() as directory:
            term_pack = Path(directory) / "terminology-bridge.jsonl"
            for private_key in (
                "company_id",
                "brand_name",
                "product_fact_id",
                "route_id",
                "customer_id",
            ):
                with self.subTest(private_key=private_key):
                    term = neutral_term()
                    term["exclusions"] = [{private_key: "private-value"}]
                    write_jsonl(term_pack, [term_pack_header(), term])

                    result = run(VALIDATE_TERMS, str(term_pack), "--format", "json")

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("COMPANY_TERM_FORBIDDEN", result.stdout)

    def test_term_validator_requires_source_reference_for_observed_terms(self):
        with tempfile.TemporaryDirectory() as directory:
            term_pack = Path(directory) / "terminology-bridge.jsonl"
            term = neutral_term()
            term["term_state"] = "source_observed"
            write_jsonl(term_pack, [term_pack_header(), term])

            result = run(VALIDATE_TERMS, str(term_pack), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TERM_SOURCE_REFERENCE_REQUIRED", result.stdout)

    def test_term_validator_rejects_nonempty_frozen_empty_cold_start(self):
        with tempfile.TemporaryDirectory() as directory:
            term_pack = Path(directory) / "terminology-bridge.jsonl"
            write_jsonl(term_pack, [term_pack_header(), neutral_term()])

            result = run(VALIDATE_TERMS, str(term_pack), "--format", "json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TERM_COLD_START_NOT_EMPTY", result.stdout)

    def test_term_validator_requires_real_source_snapshot_sha256(self):
        with tempfile.TemporaryDirectory() as directory:
            term_pack = Path(directory) / "terminology-bridge.jsonl"
            for state, source_snapshot_sha256 in (
                ("source_observed", None),
                ("source_observed", "0" * 64),
                ("accepted_for_retrieval", "not-a-real-sha256"),
            ):
                with self.subTest(
                    state=state, source_snapshot_sha256=source_snapshot_sha256
                ):
                    header = term_pack_header()
                    header["term_pack_state"] = "frozen"
                    if state == "accepted_for_retrieval":
                        header["accepted_term_count"] = 1
                    term = neutral_term()
                    term["term_state"] = state
                    term["source_reference"] = "https://public.example/source"
                    term["source_snapshot_sha256"] = source_snapshot_sha256
                    write_jsonl(term_pack, [header, term])

                    result = run(VALIDATE_TERMS, str(term_pack), "--format", "json")

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("TERM_SOURCE_SNAPSHOT_SHA256_INVALID", result.stdout)

    def test_term_validator_rejects_invalid_language_and_origin(self):
        with tempfile.TemporaryDirectory() as directory:
            term_pack = Path(directory) / "terminology-bridge.jsonl"
            for field, value, code in (
                ("language", "de", "TERM_LANGUAGE_INVALID"),
                ("origin", "company_product", "TERM_ORIGIN_INVALID"),
            ):
                with self.subTest(field=field):
                    header = term_pack_header()
                    header["term_pack_state"] = "frozen"
                    term = neutral_term()
                    term[field] = value
                    write_jsonl(term_pack, [header, term])

                    result = run(VALIDATE_TERMS, str(term_pack), "--format", "json")

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(code, result.stdout)

    def test_visible_case_freeze_accepts_only_truth_free_draft_and_emits_receipt(self):
        """The freeze is a separate pre-truth act, not a self-declared header."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, frozen, receipt = root / "visible-draft.jsonl", root / "visible.jsonl", root / "visible-receipt.json"
            write_jsonl(draft, r4_visible_case_draft_rows(r4_case_rows()))

            result = run(
                FREEZE_VISIBLE, "--visible-case-draft", str(draft),
                "--visible-case-set-reference", "02-校准案例/visible-case-set.jsonl",
                "--freeze-authorization-reference", "USER-R4-VISIBLE-FREEZE",
                "--frozen-at", "2026-08-25T00:00:00Z", "--output", str(frozen),
                "--receipt-output", str(receipt),
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue(frozen.is_file())
            body = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(
                body["visible_case_freeze_receipt"]["action"],
                "visible_case_freeze_only",
            )
            self.assertEqual(body["visible_case_freeze_receipt"]["visible_case_set_sha256"], sha256_file(frozen))
            self.assertFalse(body["visible_case_freeze_receipt"]["truth_authorized"])
            freeze_help = run(FREEZE_VISIBLE, "--help").stdout.lower()
            self.assertNotIn("source-truth", freeze_help)
            self.assertNotIn("--case-set", freeze_help)
            injected = r4_visible_case_draft_rows(r4_case_rows())
            injected[1]["truth_label"] = "injected"
            write_jsonl(draft, injected)
            rejected = run(
                FREEZE_VISIBLE, "--visible-case-draft", str(draft),
                "--visible-case-set-reference", "02-校准案例/visible-case-set.jsonl",
                "--freeze-authorization-reference", "USER-R4-VISIBLE-FREEZE",
                "--frozen-at", "2026-08-25T00:00:00Z", "--output", str(root / "bad.jsonl"),
                "--receipt-output", str(root / "bad-receipt.json"),
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("VISIBLE_CASE_DRAFT_INVALID", rejected.stderr)

    def test_visible_case_freeze_cleans_both_outputs_after_second_publish_failure(self):
        """A two-file freeze never leaves an orphan set if its receipt cannot publish."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, frozen, receipt = root / "draft.jsonl", root / "visible.jsonl", root / "receipt.json"
            write_jsonl(draft, r4_visible_case_draft_rows(r4_case_rows()))
            failed = run(
                FREEZE_VISIBLE, "--visible-case-draft", str(draft),
                "--visible-case-set-reference", "02-校准案例/visible-case-set.jsonl",
                "--freeze-authorization-reference", "USER-R4-VISIBLE-FREEZE",
                "--frozen-at", "2026-08-25T00:00:00Z", "--output", str(frozen),
                "--receipt-output", str(receipt), "--test-fail-after-visible-publish",
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("VISIBLE_CASE_FREEZE_WRITE_FAILED", failed.stderr)
            self.assertFalse(frozen.exists())
            self.assertFalse(receipt.exists())
            retried = run(
                FREEZE_VISIBLE, "--visible-case-draft", str(draft),
                "--visible-case-set-reference", "02-校准案例/visible-case-set.jsonl",
                "--freeze-authorization-reference", "USER-R4-VISIBLE-FREEZE",
                "--frozen-at", "2026-08-25T00:00:00+00:00", "--output", str(frozen),
                "--receipt-output", str(receipt),
            )
            self.assertEqual(retried.returncode, 0, retried.stderr + retried.stdout)
            self.assertTrue(frozen.is_file() and receipt.is_file())

    def test_visible_case_freeze_rejects_non_lowercase_or_nonhex_official_source_sha(self):
        """All visible-case gates share the same strict lowercase SHA schema."""
        for source_sha in ("A" * 64, "g" * 64):
            with self.subTest(source_sha=source_sha), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                rows = r4_visible_case_draft_rows(r4_case_rows())
                rows[1]["taxonomy_node"]["official_source_sha256"] = source_sha
                draft = root / "draft.jsonl"
                write_jsonl(draft, rows)
                result = run(
                    FREEZE_VISIBLE, "--visible-case-draft", str(draft),
                    "--visible-case-set-reference", "02-校准案例/visible-case-set.jsonl",
                    "--freeze-authorization-reference", "USER-R4-VISIBLE-FREEZE",
                    "--frozen-at", "2026-08-25T00:00:00Z", "--output", str(root / "visible.jsonl"),
                    "--receipt-output", str(root / "receipt.json"),
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("VISIBLE_CASE_DRAFT_INVALID", result.stderr)

    def test_finalizer_requires_independent_visible_freeze_receipt_before_truth(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft, term_pack = self.r4_preparation(root)
            locked, formal, truth = root / "locked.json", root / "formal.jsonl", root / "truth.jsonl"
            self.assertEqual(self.lock_r4(draft, term_pack, locked).returncode, 0)
            rows = r4_case_rows()
            write_jsonl(formal, rows)
            write_jsonl(truth, r4_truth_rows(rows))
            self_declared = root / "self-declared-visible.jsonl"
            write_jsonl(self_declared, r4_visible_case_rows(rows))

            result = self.finalize_r4(locked, formal, truth, root / "final.json", self_declared)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("VISIBLE_CASE_FREEZE_RECEIPT_REQUIRED", result.stderr)


if __name__ == "__main__":
    unittest.main()
