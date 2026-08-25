# RC2 Generalized Semantic Retrieval R4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Upgrade the two same-name foreign-trade skills to a company-neutral R4 semantic-retrieval contract, prove structural and regression readiness, then prepare a real isolated R4 case-preparation lock without running models.

**Architecture:** The global skill owns only generic concept roles, retrieval algorithms, evidence ownership, and validators. Each research contract owns an immutable product-neutral terminology package; company terminology remains in the company product library and cannot enter semantic expansion. Broad nodes are decomposed before bounded term discovery, every positive hypothesis requires a three-link evidence chain, and receiver-owned snapshots are byte-hashed separately from model observations.

**Tech Stack:** Markdown skill contracts, JSON/JSONL/YAML templates, Python 3 standard library, unittest, Git.

**Spec:** docs/superpowers/specs/2026-08-24-rc2-generalized-semantic-retrieval-r4.md

## Global Constraints

- Preserve R2 and R3 frozen artifacts byte-for-byte.
- Preserve the installed cache until plugin installation receives separate authorization.
- Keep only the existing plugin names: industry-application-map-builder and foreign-trade-workflow-director.
- Target source versions are industry-application-map-builder 0.4.0-beta.2 and foreign-trade-workflow-director 0.3.0-beta.2.
- Treat legacy contracts without execution_mode as strict_audit; do not change strict-audit result vocabulary or admissibility rules.
- The global skill, production prompts, and production templates contain no fixed domain terminology and no company terminology.
- Product-neutral terminology is contract-local, retrieval-only, source-traceable, hash-bound, and never application evidence by itself.
- Company terminology is prohibited in industry_semantic_expansion and remains available only to later company matching.
- R3 CASE-001 through CASE-010 are development regression cases only and never count toward R4 formal results.
- R4 formal cases are the 30 unexecuted R3 cases plus 10 new unseen positives, relabeled under R4 with receiver-only provenance.
- Do not create model tasks from draft or case_preparation_locked; task generation requires a different-version final frozen contract.
- Do not run A/B/C, full screening, shared-base writes, company matching, routes, or customer work in this plan.
- Source editing, Git commit, installation, R4 preparation writes, case preparation, final contract freezing, and model execution remain separate authorization gates.
- A structural PASS or development regression PASS never proves optimization effectiveness; keep it UNVERIFIED until the formal paired R4 run passes.

## File Responsibility Map

### New focused files

- plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/terminology-bridge.template.jsonl
- plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-visible-input.template.json
- plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-case-truth.template.json
- plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-source-observation.template.json
- plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-source-snapshot-receipt.template.json
- plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/validate_terminology_bridge.py
- plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/init_content_first_preparation_workspace.py
- plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/build_content_first_calibration_tasks.py
- plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/register_content_source_snapshot.py
- tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py

### Existing bounded-change areas

- Map plugin manifest, agent metadata, SKILL.md, semantic/content-first references, pressure scenarios, contract/template assets, preparation lock/finalizer, workspace validators, and evaluator.
- Workflow plugin manifest, agent metadata, SKILL.md, workflow blueprint, packet contracts, state/replication templates, and workflow tests.
- Existing strict-audit scripts remain behaviorally compatible.

---

### Task 1: Freeze the same-name beta.2 contract surface

**Files:**
- Create: tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py
- Modify: plugins/industry-application-map-builder/.codex-plugin/plugin.json
- Modify: plugins/foreign-trade-workflow-director/.codex-plugin/plugin.json
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/semantic-method/research-contract.template.json
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-first-research-contract.template.json

**Interfaces:**
- Consumes: approved R4 spec and current beta.1 manifests.
- Produces: terminology_architecture, calibration_case_policy, retrieval_efficiency_gates, and beta.2 source versions.

- [ ] **Step 1: Write the failing version and contract test**

~~~python
class GeneralizedSemanticRetrievalR4Tests(unittest.TestCase):
    def test_same_name_plugins_expose_beta2_generalized_contract(self):
        map_manifest = json.loads((MAP_PLUGIN / ".codex-plugin/plugin.json").read_text())
        director_manifest = json.loads((DIRECTOR_PLUGIN / ".codex-plugin/plugin.json").read_text())
        contract = json.loads(CONTRACT_TEMPLATE.read_text())["semantic_research_contract"]
        self.assertEqual(map_manifest["name"], "industry-application-map-builder")
        self.assertEqual(map_manifest["version"], "0.4.0-beta.2")
        self.assertEqual(director_manifest["name"], "foreign-trade-workflow-director")
        self.assertEqual(director_manifest["version"], "0.3.0-beta.2")
        self.assertEqual(contract["execution_mode"], "content_first")
        self.assertFalse(contract["terminology_architecture"]["global_skill_fixed_domain_terms_allowed"])
        self.assertFalse(contract["terminology_architecture"]["company_terms_allowed_in_semantic_screening"])
        self.assertEqual(contract["candidate_method_contract"], "screen_then_expand_v2")
        self.assertEqual(contract["baseline_method_contract"], "baseline_full_depth_v1")
~~~

- [ ] **Step 2: Run the test and confirm the current source fails**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: FAIL because both manifests are beta.1 and the R4 fields do not exist.

- [ ] **Step 3: Add the exact R4 contract fields and bump source manifests**

~~~json
{
  "execution_mode": "content_first",
  "terminology_architecture": {
    "global_skill_fixed_domain_terms_allowed": false,
    "case_specific_answer_terms_allowed_in_skill": false,
    "company_terms_allowed_in_semantic_screening": false,
    "concept_roles": [
      "industry_output",
      "material_form",
      "phase_relation",
      "process_action",
      "use_point",
      "exclusion"
    ],
    "term_pack_reference": null,
    "term_pack_sha256": null,
    "term_pack_state": "not_prepared",
    "dynamic_discovery_enabled": true
  },
  "calibration_case_policy": {
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
      "contamination_drift_or_structure_error": 3
    }
  },
  "retrieval_efficiency_gates": {
    "minimum_deep_expansion_reduction": 0.2,
    "maximum_query_count_increase": 0.1,
    "maximum_source_open_count_increase": 0.0,
    "stability_repeat_case_count": 6
  }
}
~~~

Retain every existing strict contract field. Change only the source-version defaults and R4 content-first additions.

- [ ] **Step 4: Run the focused test**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: PASS.

- [ ] **Step 5: Record a no-commit checkpoint**

~~~bash
git diff --check
git status --short
~~~

Expected: the approved spec/plan and Task 1 files only. Do not commit.

---

### Task 2: Create and validate a zero-term contract-local package

**Files:**
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/terminology-bridge.template.jsonl
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/validate_terminology_bridge.py
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/init_content_first_preparation_workspace.py
- Modify: tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py

**Interfaces:**
- Consumes: a content-first draft contract with a stable research_contract_id.
- Produces: a real zero-entry terminology-bridge.jsonl, manifest and SHA-256, plus a refusal-safe preparation directory.

- [ ] **Step 1: Add failing cold-start and isolation tests**

~~~python
def test_preparation_initializer_creates_real_empty_product_neutral_term_pack(self):
    result = run(INIT_PREP, "--map-root", str(map_root), "--contract", str(contract_path))
    self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
    payload = json.loads(result.stdout)
    pack = Path(payload["terminology_bridge"])
    self.assertTrue(pack.is_file())
    self.assertEqual(hashlib.sha256(pack.read_bytes()).hexdigest(), payload["terminology_bridge_sha256"])
    rows = load_jsonl(pack)
    self.assertEqual(rows[0]["accepted_term_count"], 0)
    self.assertFalse(rows[0]["company_data_allowed"])
    self.assertEqual(rows[0]["term_pack_state"], "frozen_empty_cold_start")

def test_term_validator_rejects_company_fields(self):
    write_jsonl(term_pack, [header, {**term, "company_id": "COMPANY-A"}])
    result = run(VALIDATE_TERMS, str(term_pack), "--format", "json")
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("COMPANY_TERM_FORBIDDEN", result.stdout)
~~~

- [ ] **Step 2: Run and confirm the scripts are missing**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: FAIL.

- [ ] **Step 3: Implement exact term-pack validation**

~~~python
CONCEPT_ROLES = {
    "industry_output", "material_form", "phase_relation",
    "process_action", "use_point", "exclusion",
}
TERM_STATES = {"proposed", "source_observed", "accepted_for_retrieval", "rejected"}
PRIVATE_KEYS = {"company_id", "company_name", "product_fact_id", "route_id", "customer_id"}

def validate_rows(rows: list[dict], expected_contract_id: str | None = None) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    headers = [row for row in rows if row.get("record_type") == "terminology_bridge_contract"]
    terms = [row for row in rows if row.get("record_type") == "terminology_term"]
    if len(headers) != 1:
        errors.append({"code": "TERM_HEADER_COUNT_INVALID", "detail": str(len(headers))})
    if len({row.get("term_id") for row in terms}) != len(terms):
        errors.append({"code": "TERM_ID_DUPLICATE", "detail": "term_id"})
    return errors
~~~

Complete the same function by enforcing allowed roles/states, source references for source_observed and accepted_for_retrieval, exact header counts, allowed record types, and recursive private-key rejection. The CLI is read-only and prints status, errors, and term_count.

- [ ] **Step 4: Implement the preparation initializer**

It accepts only contract_state=draft and execution_mode=content_first, refuses an existing destination, and creates exactly:

~~~python
PREPARATION_DIRECTORIES = (
    "00-合同准备",
    "01-节点快照",
    "01-术语桥",
    "02-校准案例候选",
    "03-来源真值准备",
    "07-报告",
)
~~~

It writes a real frozen_empty_cold_start pack, a manifest with the byte SHA-256, and a read-only draft-contract copy. It creates no model-task directory.

- [ ] **Step 5: Run focused tests**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: PASS, including second-run DESTINATION_EXISTS refusal.

---

### Task 3: Bind terminology and case policy into the two-gate lifecycle

**Files:**
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/validate_semantic_research_workspace.py
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/lock_semantic_case_preparation_contract.py
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/finalize_semantic_research_contract.py
- Modify: tests/industry-application-map-builder/test_semantic_method_tools.py
- Modify: tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py

**Interfaces:**
- Consumes: draft contract, real term pack, and later real case/truth sets.
- Produces: term-hash-bound case_preparation_locked and different-version final frozen contracts.

- [ ] **Step 1: Add a failing preparation-lock test**

~~~python
def test_content_first_lock_requires_real_term_pack_and_empty_case_outputs(self):
    missing = run_script(
        LOCK, "--contract", str(draft),
        "--authorization-reference", "USER-R4-PREP",
        "--locked-at", NOW, "--output", str(locked),
    )
    self.assertNotEqual(missing.returncode, 0)
    self.assertIn("TERMINOLOGY_BRIDGE_REQUIRED", missing.stderr)

    valid = run_script(
        LOCK, "--contract", str(draft),
        "--terminology-bridge", str(term_pack),
        "--terminology-bridge-reference", "01-术语桥/terminology-bridge.jsonl",
        "--authorization-reference", "USER-R4-PREP",
        "--locked-at", NOW, "--output", str(locked),
    )
    self.assertEqual(valid.returncode, 0, valid.stderr)
    body = json.loads(locked.read_text())["semantic_research_contract"]
    self.assertEqual(body["terminology_architecture"]["term_pack_sha256"], sha256_file(term_pack))
    self.assertIsNone(body["calibration_case_set_reference_and_hash"]["sha256"])
    self.assertEqual(body["control_case_rule"]["case_ids"], [])
~~~

- [ ] **Step 2: Add failing finalizer tests**

~~~python
def test_finalizer_rejects_development_case_in_formal_set(self):
    rows = r4_case_rows()
    rows[1]["provenance"]["development_regression_only"] = True
    write_jsonl(case_set, rows)
    result = finalize(locked, case_set, truth_set, final_contract)
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("DEVELOPMENT_CASE_IN_FORMAL_SET", result.stderr)
~~~

Add a second assertion for category-count drift and a third for 39 or 41 truth rows.

- [ ] **Step 3: Run both test modules and confirm failure**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_semantic_method_tools.py tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: FAIL on missing term-pack and formal-case enforcement.

- [ ] **Step 4: Extend completeness checks**

For content-first contracts require:

~~~python
CONTENT_FIRST_REQUIRED = {
    "execution_mode",
    "terminology_architecture",
    "calibration_case_policy",
    "retrieval_efficiency_gates",
    "content_first_policy",
    "source_truth_package_reference",
    "source_truth_package_sha256",
}
~~~

Require a real lowercase SHA-256, allowed roles, fixed-term and company-term flags false, term state frozen_empty_cold_start or frozen_reviewed, 40 formal cases, 14 positives, category sum 40, and six stability repeats. Preserve legacy no-mode strict validation.

- [ ] **Step 5: Extend lock and finalizer CLIs**

For content-first, lock requires --terminology-bridge and --terminology-bridge-reference, validates the pack, writes the real hash, and only then computes locked_input_sha256.

For content-first, finalizer also requires:

~~~text
--source-truth-package /absolute/source-truth.jsonl
--source-truth-reference 03-来源真值/source-truth.jsonl
~~~

It validates 40 unique formal cases, exact category counts, zero development cases, 14 positives, 40 matching unique truth rows, real controls in the case set, and real case/truth byte hashes.

- [ ] **Step 6: Run the focused tests**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_semantic_method_tools.py tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: PASS without breaking legacy strict fixtures.

---

### Task 4: Build truth-blind paired tasks with generalized discovery

**Files:**
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-visible-input.template.json
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-source-observation.template.json
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/build_content_first_calibration_tasks.py
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-raw-answer.template.json
- Modify: tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py

**Interfaces:**
- Consumes: final frozen content-first contract plus real formal case set.
- Produces: 80 isolated task files and one paired manifest; no truth or receiver-owned fields enter tasks.

- [ ] **Step 1: Add a failing truth-leak test**

~~~python
def test_builder_emits_40_pairs_without_truth_or_receiver_fields(self):
    result = run(BUILD_TASKS, "--contract", str(final_contract), "--case-set", str(case_set), "--output", str(output))
    self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
    tasks = sorted(output.rglob("*.task.json"))
    self.assertEqual(len(tasks), 80)
    for path in tasks:
        text = path.read_text(encoding="utf-8")
        for forbidden in (
            "truth_label", "expected_screening_result", "known_positive",
            "selection_reason", "receiver_snapshot_sha256", "other_arm_output",
        ):
            self.assertNotIn(forbidden, text)
        task = json.loads(text)["content_first_calibration_task"]
        node = task["visible_input"]["taxonomy_node"]
        self.assertIn("breadcrumb", node)
        self.assertIn("official_definition_or_null", node)
        self.assertEqual(task["three_link_gate"], [
            "taxonomy_membership_basis",
            "output_or_subprocess_basis",
            "mechanism_or_use_point_basis",
        ])
~~~

- [ ] **Step 2: Add a failing broad-node test**

~~~python
def test_revised_task_decomposes_outputs_before_dynamic_terms(self):
    task = load_task("screen_then_expand_v2", "R4-CASE-031")
    self.assertTrue(task["method_contract"]["broad_node_output_family_decomposition_required"])
    self.assertEqual(task["dynamic_term_discovery"]["trigger"], "core_search_complete_without_three_link_bridge")
    self.assertFalse(task["dynamic_term_discovery"]["mutates_frozen_term_pack"])
    self.assertEqual(task["dynamic_term_discovery"]["allowed_use"], "retrieval_only")
~~~

- [ ] **Step 3: Run and confirm the builder is missing**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: FAIL.

- [ ] **Step 4: Implement the visible projection**

~~~python
VISIBLE_CASE_KEYS = {"case_id", "taxonomy_node", "product_neutral_research_theme", "risk_flags"}
VISIBLE_NODE_KEYS = {
    "taxonomy_node_id", "code", "level", "name_zh", "breadcrumb",
    "official_definition_or_null", "included_activities_or_null",
    "excluded_or_adjacent_activities_or_null", "official_source_reference",
    "official_source_sha256",
}
FORBIDDEN_TRUTH_KEYS = {
    "truth_label", "expected_screening_result", "expected_semantic_work_state",
    "expected_evidence_state_before_B", "known_positive", "selection_reason",
    "source_refs", "truth_boundary", "primary_category",
}
~~~

Missing official values remain JSON null. Missing keys fail; the builder never manufactures a definition.

- [ ] **Step 5: Implement deterministic paired output**

Verify final contract and case-set hashes, create separate arm directories, canonical-hash every input/task, create a 40-pair manifest, and refuse an existing output. The return schema owns observations but no snapshot path or hash. Dynamic terms are case-local and cannot mutate the frozen pack or later tasks.

- [ ] **Step 6: Run focused tests**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: PASS including overwrite refusal.

---

### Task 5: Enforce receiver-owned immutable source snapshots

**Files:**
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-source-snapshot-receipt.template.json
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/register_content_source_snapshot.py
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/validate_content_first_workspace.py
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-raw-answer.template.json
- Modify: tests/industry-application-map-builder/test_content_first_tools.py

**Interfaces:**
- Consumes: one local captured source file and one observation ID.
- Produces: copied immutable snapshot, receipt JSON, and recomputable lowercase SHA-256.

- [ ] **Step 1: Add failing hash and overwrite tests**

~~~python
def test_validator_rejects_observation_prose_as_receiver_snapshot_hash(self):
    receipt["receiver_snapshot_sha256"] = "source observed in browser"
    write_json(receipt_path, receipt)
    result = run(VALIDATE, str(workspace), "--format", "json")
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("RECEIVER_SNAPSHOT_SHA256_INVALID", result.stdout)

def test_snapshot_registrar_copies_bytes_and_refuses_overwrite(self):
    first = register_snapshot(workspace, source_file, "OBS-001")
    self.assertEqual(first.returncode, 0, first.stderr)
    payload = json.loads(first.stdout)
    snapshot = workspace / payload["receiver_snapshot_reference"]
    self.assertEqual(hashlib.sha256(snapshot.read_bytes()).hexdigest(), payload["receiver_snapshot_sha256"])
    second = register_snapshot(workspace, source_file, "OBS-001")
    self.assertNotEqual(second.returncode, 0)
    self.assertIn("SNAPSHOT_EXISTS", second.stderr)
~~~

- [ ] **Step 2: Run and confirm failure**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_content_first_tools.py -v
~~~

Expected: FAIL.

- [ ] **Step 3: Implement the receipt**

~~~json
{
  "source_observation_reference": null,
  "receiver_snapshot_reference": null,
  "receiver_snapshot_sha256": null,
  "snapshot_capture_state": "captured | unavailable | failed",
  "snapshot_captured_at": null,
  "receipt_sha256": null
}
~~~

The registrar resolves all paths, rejects destinations outside the workspace, copies bytes once, calculates SHA-256, writes a canonical receipt, and refuses existing snapshot or receipt paths.

- [ ] **Step 4: Update content validation**

Reject receiver fields inside model observations. For captured receipts require lowercase 64-character SHA-256, existing file, and recomputed equality. Allow unavailable or failed only as UNVERIFIED evidence.

- [ ] **Step 5: Run the focused suite**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_content_first_tools.py -v
~~~

Expected: PASS.

---

### Task 6: Separate truth and scorecard responsibilities

**Files:**
- Create: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-case-truth.template.json
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-scorecard.template.json
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/validate_content_first_workspace.py
- Modify: tests/industry-application-map-builder/test_content_first_contract.py
- Modify: tests/industry-application-map-builder/test_content_first_tools.py

**Interfaces:**
- Consumes: truth with three evidence links and receiver evidence.
- Produces: six independently owned score items and explicit equivalent-source judgment.

- [ ] **Step 1: Add failing schema tests**

~~~python
EXPECTED_R4_SCORE_ITEMS = {
    "taxonomy_and_scope_grounding",
    "semantic_decision_correctness",
    "source_retrieval_equivalence",
    "receiver_evidence_integrity",
    "safety_boundary",
    "unknown_and_challenge_handling",
}

def test_r4_truth_and_scorecard_separate_three_links(self):
    truth = json.loads(TRUTH_TEMPLATE.read_text())["semantic_content_case_truth"]
    self.assertIn("taxonomy_membership_basis", truth)
    self.assertIn("output_or_subprocess_basis", truth)
    self.assertIn("mechanism_basis", truth)
    score = json.loads(SCORE_TEMPLATE.read_text())["semantic_content_scorecard"]
    self.assertEqual(set(score["scoring_items"]), EXPECTED_R4_SCORE_ITEMS)
    self.assertIn(score["equivalent_source_result"], {"PASS", "FAIL", "UNVERIFIED"})
~~~

- [ ] **Step 2: Run and confirm old combined scoring fails**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_content_first_contract.py tests/industry-application-map-builder/test_content_first_tools.py -v
~~~

Expected: FAIL.

- [ ] **Step 3: Implement the truth template**

Store separate basis text and source-ref arrays for taxonomy membership, output/subprocess, and mechanism, plus expected semantic axes, conditions, limitations, unknowns, truth boundary, and counts_toward_known_positive_recall.

- [ ] **Step 4: Implement R4 arithmetic**

~~~python
R4_SCORE_ITEMS = {
    "taxonomy_and_scope_grounding",
    "semantic_decision_correctness",
    "source_retrieval_equivalence",
    "receiver_evidence_integrity",
    "safety_boundary",
    "unknown_and_challenge_handling",
}

def score_result(items: dict[str, dict]) -> str:
    if any(item["critical"] and item["score"] == 0 for item in items.values()):
        return "FAIL"
    if all(item["score"] == 2 for item in items.values()):
        return "PASS"
    return "UNVERIFIED"
~~~

Equivalent-source PASS requires the same membership, output/use point, mechanism, conditions, and boundary. Exact URL equality is not required.

- [ ] **Step 5: Run focused suites**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_content_first_contract.py tests/industry-application-map-builder/test_content_first_tools.py -v
~~~

Expected: PASS.

---

### Task 7: Add complete efficiency and stability gates

**Files:**
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-calibration-arm.template.json
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/evaluate_content_first_calibration.py
- Modify: tests/industry-application-map-builder/test_content_first_tools.py
- Modify: tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py

**Interfaces:**
- Consumes: two complete 40-case arm summaries plus six revised-arm stability receipts.
- Produces: PASS/FAIL/INCOMPLETE with critical gates before efficiency.

- [ ] **Step 1: Add a failing hidden-work test**

~~~python
def test_evaluator_rejects_hidden_work_shift_and_missing_repeats(self):
    baseline = arm("baseline_full_depth_v1", deep=40, queries=100, opens=80)
    revised = arm("screen_then_expand_v2", deep=30, queries=112, opens=81)
    revised["stability_repeat_evidence"] = []
    output = self.work / "evaluation-report.json"
    result = evaluate(baseline, revised, output)
    self.assertNotEqual(result.returncode, 0)
    report = json.loads(output.read_text())
    self.assertIn("query count increase exceeds 10 percent", report["reasons"])
    self.assertIn("source-open count exceeds baseline", report["reasons"])
    self.assertIn("six stability repeats are incomplete", report["reasons"])
~~~

- [ ] **Step 2: Run and confirm failure**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_content_first_tools.py -v
~~~

Expected: FAIL.

- [ ] **Step 3: Extend arm schema and evaluator**

Require query_count, source_open_count, exactly 14 unique positive IDs, the same 14 expansion IDs, six unique repeat IDs, matching repeat input hashes, and consistent critical dispositions. Apply safety, recall, evidence completeness, and stability before deep reduction, query increase, and source-open increase. Retain legacy arm labels for pre-R4 contracts.

- [ ] **Step 4: Run the focused suite**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_content_first_tools.py -v
~~~

Expected: PASS.

---

### Task 8: Update map skill instructions and adversarial coverage

**Files:**
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/SKILL.md
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/agents/openai.yaml
- Modify: plugins/industry-application-map-builder/.codex-plugin/plugin.json
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/references/content-first-mode-contract.md
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/references/industry-semantic-research-contract.md
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/references/industry-semantic-model-protocol.md
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/references/industry-semantic-calibration-and-audit.md
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/references/compatibility-matrix.md
- Modify: plugins/industry-application-map-builder/skills/industry-application-map-builder/references/pressure-scenarios.md
- Modify: tests/industry-application-map-builder/test_contract.py
- Modify: tests/industry-application-map-builder/test_content_first_unified_upgrade.py
- Modify: tests/industry-application-map-builder/pressure-prompts.md
- Modify: tests/industry-application-map-builder/scorecard.md

**Interfaces:**
- Consumes: Tasks 1-7.
- Produces: one same-name skill with explicit R4 routes and no fixed production terminology.

- [ ] **Step 1: Add failing documentation-contract assertions**

~~~python
def test_skill_documents_generalized_r4_gates(self):
    combined = "\n".join(path.read_text(encoding="utf-8") for path in PRODUCTION_TEXT_FILES)
    for required in (
        "contract-local terminology",
        "output-family",
        "taxonomy membership basis",
        "receiver_snapshot_sha256",
        "development_regression_only",
        "30 unexecuted",
        "10 new unseen positives",
        "CONTENT_CALIBRATION_PASS",
        "RESEARCH_ONLY_BLOCKED",
    ):
        self.assertIn(required, combined)
    self.assertNotIn("fixed_domain_terms", combined)
~~~

- [ ] **Step 2: Run and confirm missing R4 documentation fails**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_contract.py tests/industry-application-map-builder/test_content_first_unified_upgrade.py tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: FAIL.

- [ ] **Step 3: Update production instructions**

Document the three terminology layers, output-family decomposition, bounded discovery, three-link gate, receiver ownership, split truth/scoring, freeze order, 30+10 holdout policy, six repeats, and stop vocabulary. Add no production term list.

- [ ] **Step 4: Add pressure scenarios**

Cover fixed production vocabulary, company-A leakage into company B, term-pack mutation, model terms treated as evidence, class-name-only broad search, incomplete link chains, prose hashes, formal-truth leakage, development cases counted formally, sentinel-driven method changes, shifted query/open work, and missing repeats. Each scenario states expected FAIL or UNVERIFIED and recovery.

- [ ] **Step 5: Run the contract group**

~~~bash
python3 -m unittest tests/industry-application-map-builder/test_contract.py tests/industry-application-map-builder/test_content_first_unified_upgrade.py tests/industry-application-map-builder/test_generalized_semantic_retrieval_r4.py -v
~~~

Expected: PASS.

---

### Task 9: Update workflow-director R4 routing

**Files:**
- Modify: plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/SKILL.md
- Modify: plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/agents/openai.yaml
- Modify: plugins/foreign-trade-workflow-director/.codex-plugin/plugin.json
- Modify: plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/references/workflow-blueprint.md
- Modify: plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/references/workflow-and-packet-contracts.md
- Modify: plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/assets/company-workflow-state.template.yaml
- Modify: plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/assets/workflow-replication-manifest.template.yaml
- Modify: tests/foreign-trade-workflow-director/test_contract.py
- Modify: tests/foreign-trade-workflow-director/pressure-prompts.md
- Modify: tests/foreign-trade-workflow-director/scorecard.md

**Interfaces:**
- Consumes: R4 specialist fields.
- Produces: earliest-stage routing with task, full-screening, and downstream stops.

- [ ] **Step 1: Add failing director assertions**

~~~python
def test_director_routes_r4_without_downstream_release(self):
    combined = "\n".join((DIRECTOR_SKILL / path).read_text(encoding="utf-8") for path in DIRECTOR_FILES)
    for required in (
        "terminology_bridge_sha256",
        "development_regression_only",
        "formal_holdout_case_set_sha256",
        "stability_repeat_state",
        "CONTENT_CALIBRATION_INCOMPLETE",
        "RESEARCH_ONLY_BLOCKED",
    ):
        self.assertIn(required, combined)
    self.assertIn("first_incomplete_stage: industry_semantic_expansion", combined)
~~~

- [ ] **Step 2: Run and confirm failure**

~~~bash
python3 -m unittest tests/foreign-trade-workflow-director/test_contract.py -v
~~~

Expected: FAIL.

- [ ] **Step 3: Add state and routing**

~~~yaml
terminology_bridge_reference: null
terminology_bridge_sha256: null
terminology_bridge_state: not_prepared
development_regression_state: not_started
formal_holdout_case_set_sha256: null
stability_repeat_state: not_started
~~~

Route missing/mismatched terms to semantic_contract_prepare; incomplete 30+10 truth to semantic_calibration_case_prepare; development failure to repair; missing formal evidence to content_first_calibration_review; and every downstream attempt to RESEARCH_ONLY_BLOCKED. Never turn structural tests into content PASS.

- [ ] **Step 4: Run director tests**

~~~bash
python3 -m unittest tests/foreign-trade-workflow-director/test_contract.py -v
~~~

Expected: PASS.

---

### Task 10: Full source verification and compatibility audit

**Files:**
- Test: tests/industry-application-map-builder/
- Test: tests/foreign-trade-workflow-director/
- Verify read-only: installed beta.1 cache and R2/R3 frozen files.

**Interfaces:**
- Consumes: Tasks 1-9.
- Produces: STRUCTURAL_READY or a precise blocker; never effectiveness.

- [ ] **Step 1: Run all map tests**

~~~bash
python3 -m unittest discover -s tests/industry-application-map-builder -p 'test_*.py' -v
~~~

Expected: PASS.

- [ ] **Step 2: Run all director tests**

~~~bash
python3 -m unittest discover -s tests/foreign-trade-workflow-director -p 'test_*.py' -v
~~~

Expected: PASS.

- [ ] **Step 3: Validate diffs and JSON**

~~~bash
git diff --check
python3 -m json.tool plugins/industry-application-map-builder/.codex-plugin/plugin.json
python3 -m json.tool plugins/foreign-trade-workflow-director/.codex-plugin/plugin.json
python3 -m json.tool plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/semantic-method/research-contract.template.json
python3 -m json.tool plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/content-first/content-first-research-contract.template.json
~~~

Expected: all exit 0.

- [ ] **Step 4: Recompute frozen sentinels**

~~~bash
shasum -a 256 '/Users/lirongjing/Documents/传统外贸/行业应用地图/05-工作区/行业语义研究/RC2-40-CALIBRATION-PREP-20260824-R2/03-来源真值/calibration-case-truth.pending-human-acceptance.jsonl'
shasum -a 256 '/Users/lirongjing/Documents/传统外贸/行业应用地图/05-工作区/行业语义研究/RC2-40-CONTENT-FIRST-CALIBRATION-20260824-R3/02-校准案例/calibration-case-set.frozen-accepted.jsonl'
~~~

Expected:

~~~text
4e90c30d69c8f1c159d1852a10f47f04b08ae5f4e79d84b8667ec0f0c5b1744f
80757dca6bce47c831ed98eb0ecb61bb93cb4c217e12f288608c0cf55f51c484
~~~

- [ ] **Step 5: Verify installed cache stays beta.1**

~~~bash
shasum -a 256 '/Users/lirongjing/.codex/plugins/cache/foreign-trade-team/industry-application-map-builder/0.4.0-beta.1/skills/industry-application-map-builder/SKILL.md'
shasum -a 256 '/Users/lirongjing/.codex/plugins/cache/foreign-trade-team/foreign-trade-workflow-director/0.3.0-beta.1/skills/foreign-trade-workflow-director/SKILL.md'
~~~

Expected:

~~~text
85c88afc6b2f5432c6a0a88daabb5a35a79176a4a53e1e0a7f78d61ea4e0d035
542556287f46dc103b3aaf23503ab9a6c24ea105604fd4c525e1cdd3b4c71d5e
~~~

- [ ] **Step 6: Report the source verdict**

Return STRUCTURAL_READY only if every test and sentinel passes. Keep optimization effectiveness UNVERIFIED and emit neither CONTENT_CALIBRATION_PASS nor strict EFFECTIVE.

---

### Task 11: Stop for Git and installation authorizations

**Files:**
- Inspect: complete source diff.
- Change: none unless a correction is separately authorized.

**Interfaces:**
- Consumes: STRUCTURAL_READY.
- Produces: user decisions; no automatic commit or install.

- [ ] **Step 1: Show the exact diff**

~~~bash
git status --short
git diff --stat
git diff --name-only
~~~

- [ ] **Step 2: Request Git commit authorization**

Do not commit before approval. If approved:

~~~bash
git add docs/superpowers/specs/2026-08-24-rc2-generalized-semantic-retrieval-r4.md docs/superpowers/plans/2026-08-24-rc2-generalized-semantic-retrieval-r4.md plugins/industry-application-map-builder plugins/foreign-trade-workflow-director tests/industry-application-map-builder tests/foreign-trade-workflow-director
git commit -m "feat(外贸): 通用化RC2语义检索与R4合同"
~~~

- [ ] **Step 3: Request plugin installation authorization**

Install only from the committed same-name plugin sources. Verify exactly 0.4.0-beta.2 and 0.3.0-beta.2. Do not retain a parallel candidate name.

---

### Task 12: Create the isolated R4 preparation lock after installation

**Files:**
- Create only after separate authorization: /Users/lirongjing/Documents/传统外贸/行业应用地图/05-工作区/行业语义研究/RC2-40-CONTENT-FIRST-CALIBRATION-20260824-R4/
- Use installed same-name beta.2 scripts.

**Interfaces:**
- Consumes: committed/installed beta.2, current taxonomy snapshot, approved neutral theme, real prompt/source/budget hashes, and R4 preparation authorization.
- Produces: refusal-safe workspace, real empty cold-start terminology package, and case_preparation_locked with no case hash or controls.

- [ ] **Step 1: Run preflight**

Require absent R4 destination, installed beta.2 versions, matching source commit, recomputed taxonomy/prompt hashes, and unchanged R2/R3 sentinels. Any mismatch returns UNVERIFIED.

- [ ] **Step 2: Initialize preparation**

Run installed init_content_first_preparation_workspace.py with the map root and R4 draft. Require no model-task directory, real frozen_empty_cold_start pack, and real term-pack SHA-256.

- [ ] **Step 3: Lock preparation**

Run installed lock_semantic_case_preparation_contract.py with the real pack, authorization reference, and actual timestamp. Require:

~~~text
contract_state = case_preparation_locked
locked_input_sha256 = real lowercase SHA-256
calibration_case_set_reference_and_hash.reference = null
calibration_case_set_reference_and_hash.sha256 = null
control_case_rule.case_ids = []
batch_rule.batch_size = null
execution_authorized = false
~~~

- [ ] **Step 4: Validate and test refusal**

Run the term validator and contract completeness checks. Re-run initialization against the same destination and require DESTINATION_EXISTS.

- [ ] **Step 5: Stop before case preparation**

Report real term-pack hash, locked_input_sha256, installed versions, source commit, write scope, and remaining null case/control fields. Do not copy the 30 retained cases, research the 10 new positives, generate task packages, or run models.

## Final Handoff State

Tasks 1-10 prove only source structure and deterministic gates. Task 11 requires explicit Git and installation decisions. Task 12, when separately authorized and successful, creates the new R4 preparation contract and stops at case_preparation_locked.

The later phase is independent 30+10 case preparation, real truth acceptance, real case-set SHA/control IDs, different-version final freezing, and then separately authorized paired model execution. Those later actions are outside this implementation plan.
