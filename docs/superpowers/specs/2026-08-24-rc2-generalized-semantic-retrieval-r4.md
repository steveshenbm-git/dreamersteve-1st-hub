# RC2 Generalized Semantic Retrieval R4

## Status

Approved architecture specification for review before implementation.

- Source skill baseline: `industry-application-map-builder 0.4.0-beta.1`
- Controller baseline: `foreign-trade-workflow-director 0.3.0-beta.1`
- Rollback Git commit: `859bd6d948213a10464eddec635c264a24f68d77`
- Proposed source versions: `0.4.0-beta.2` and `0.3.0-beta.2`
- Current lifecycle gate: `first_incomplete_stage = industry_semantic_expansion`
- Current content state: `CONTENT_CALIBRATION_INCOMPLETE`
- Full screening: `NOT_AUTHORIZED`
- Downstream state: `RESEARCH_ONLY_BLOCKED`

This specification does not authorize source edits, plugin installation, Git commit or push, model execution, full screening, shared-base writes, company matching, routes, or customer work.

## Decision

Upgrade the two existing same-name skills in place. Do not create or retain a second daily-use candidate skill. Git history and the recorded baseline commit provide rollback.

The production skill must not contain a fixed domain terminology list, a company vocabulary, or terms copied from a calibration answer. It contains only the generalized discovery procedure, schemas, gates, and validators. Product-neutral terms belong to a versioned research-contract workspace. Company-specific terms remain in that company's product library and are not visible to industry semantic expansion.

The experimental comparison still has two method arms inside the same skill:

- `baseline_full_depth_v1`: the frozen full-depth baseline behavior;
- `screen_then_expand_v2`: the revised generalized screen-then-expand behavior.

An experimental method arm is not a separate installed skill.

## R3 Findings That R4 Must Address

R4 is not a terminology-only patch. It must address all established failure classes:

1. A hidden-positive case reached deep expansion but failed to bridge node-specific process language to the product-neutral mechanism.
2. A broad-node positive formed a reasonable mechanism hypothesis but failed to search the relevant output family or subprocess and missed an accepted node-specific source.
3. All 40 visible inputs lacked official definitions and named parent breadcrumbs; they carried only code, level, name, source ID, parent ID, node ID, taxonomy system, and version.
4. Nine non-null snapshot fields in the first 20 raw responses contained observation prose rather than a valid 64-character SHA-256; none contained a valid SHA-256.
5. The truth package did not separately own taxonomy-membership evidence and mechanism evidence.
6. One combined `source_truth_alignment` score mixed semantic correctness, retrieval equivalence, and receiver evidence completeness.
7. The first executed batch contained ten known positives, so both arms expanded all ten and the frozen efficiency objective could not be measured.

The first ten exposed cases are development evidence only. They cannot contribute to R4 effectiveness.

## Three-Layer Terminology Architecture

### Layer 1: Global skill

The skill contains no production domain terms. It defines only:

- concept roles;
- candidate-term discovery and bounded-query behavior;
- product-neutrality and company-isolation gates;
- term provenance, state, scope, and exclusion fields;
- contract hashing and invalidation rules;
- three-link hypothesis gate;
- evidence capture and scoring ownership.

The generic concept roles are:

```text
industry_output
material_form
phase_relation
process_action
use_point
exclusion
```

Examples used in tests must remain fixtures and must not be copied into production prompts, templates, or defaults.

### Layer 2: Research-contract-local product-neutral terminology

Each research contract owns an isolated product-neutral terminology package:

```text
05-工作区/行业语义研究/<research_contract_id>/
└── 01-术语桥/
    ├── terminology-bridge.jsonl
    ├── terminology-bridge.manifest.json
    ├── terminology-bridge.sha256
    └── dynamic-term-observations.jsonl
```

The initializer creates an empty package or a newly prepared package for the current research theme. It never copies a prior company package automatically.

Minimum term record:

```json
{
  "term_id": "TERM-...",
  "research_contract_id": "RC2-...",
  "concept_role": "industry_output | material_form | phase_relation | process_action | use_point | exclusion",
  "language": "zh | en | other",
  "surface_form": "string",
  "term_state": "proposed | source_observed | accepted_for_retrieval | rejected",
  "origin": "official_taxonomy | public_source | model_query_candidate",
  "source_reference": null,
  "source_snapshot_sha256": null,
  "applicable_scope": [],
  "exclusions": [],
  "company_data_present": false
}
```

Rules:

- `proposed` terms may be used only in the frozen bounded discovery search.
- `source_observed` requires a readable public source and original location.
- `accepted_for_retrieval` means search vocabulary only; it is never application evidence.
- Dynamic observations are append-only and cannot alter the frozen term pack during a formal run.
- Any frozen term-pack byte change invalidates dependent task packages and requires a new contract version.
- Cross-contract reuse is never automatic. It requires the same product-neutral theme hash, compatible taxonomy version and source permissions, explicit scope review, and a new contract version.
- No term is promoted into the global skill or shared application base automatically.

### Layer 3: Company-local terminology adapter

Company product names, internal language, model names, capability terms, and customer language remain in the company's controlled product library. A company-local adapter may map approved fact IDs to product-neutral mechanism atoms only during `company_industry_match`.

Company-local terms are prohibited inputs to semantic contract preparation, calibration cases, semantic screening, contract-local terminology, shared taxonomy, and another company. The adapter is not a fallback vocabulary source for stage 5.

## Generalized Retrieval Algorithm

### 1. Input grounding

Each visible input includes, when the official source provides it:

- node ID, code, level, and name;
- full named breadcrumb;
- official definition;
- included activities or outputs;
- excluded or adjacent activities;
- official source reference and snapshot hash.

Unavailable official fields are explicit `null`; they are never inferred or invented.

### 2. Output-family and subprocess decomposition

Before terminology expansion, broad, auxiliary, miscellaneous, mixed-output, or otherwise high-risk nodes are decomposed from official material into bounded output families and subprocess families. The search must not rely only on the class name.

Every family record preserves its official basis, scope, exclusions, and source reference. Model-generated families remain hypotheses and cannot establish taxonomy membership.

### 3. Core retrieval

Both existing query groups remain:

1. industry output or process;
2. mechanism, use point, and cross-domain equivalents.

The query and source-open budget is frozen before a formal run. Query records preserve exact query, role, language, region, observed results, inspected URLs, opened URLs, and access outcome.

### 4. Bounded dynamic term discovery

If core retrieval completes without a node-to-mechanism bridge, the revised arm uses the generic concept roles, current official node context, and current product-neutral theme to generate bounded query candidates. No company facts, truth package, accepted answer, scorecard, other-arm output, or prior-case output is visible.

Newly observed terms remain case-local observations during the formal run. They do not mutate the frozen terminology package or later cases.

### 5. Three-link hypothesis gate

A term match alone cannot form a hypothesis. `hypothesis_formed` requires a bounded chain:

```text
taxonomy membership basis
→ node output or subprocess basis
→ mechanism, form, or use-point basis
```

Each link preserves source, original location, conditions, limitations, counterevidence, and unresolved items. A missing or conflicting link returns `ambiguous` or `no_hypothesis_formed` according to the frozen retrieval-completeness rule. Neither result is an industry exclusion.

### 6. Evidence expansion

All `hypothesis_formed`, all `ambiguous`, retrieval conflicts, high-risk broad/miscellaneous nodes, and later audit hits enter deep expansion. The baseline performs full depth for every case; the revised arm uses the frozen triggers.

### 7. Receiver-owned evidence capture

The model reports only the observed source URL, publisher, title, original location, bounded summary, access state, conditions, limitations, and counterevidence.

The receiver owns:

```text
source_observation_reference
receiver_snapshot_reference
receiver_snapshot_sha256
snapshot_capture_state
snapshot_captured_at
```

`receiver_snapshot_sha256` is valid only when it matches `^[0-9a-f]{64}$`, the referenced file exists, and recomputing the byte hash yields the same value. Observation prose, browser reference IDs, timestamps, or URLs are rejected as hashes. A failed or unavailable capture is explicit `UNVERIFIED`; it is not silently replaced by model text.

## Truth and Scoring Ownership

### Truth package

Known-positive truth separates:

- `taxonomy_membership_basis` and `taxonomy_membership_source_refs`;
- `output_or_subprocess_basis` and source refs;
- `mechanism_basis` and `mechanism_source_refs`;
- expected semantic axes;
- truth boundary, conditions, limitations, and unknowns.

The exact accepted URL is not mandatory when an independently retrieved source establishes the same taxonomy membership, output/use point, mechanism, conditions, and boundary. Equivalent-source acceptance is scored explicitly.

### Scorecard

The scorecard separates:

```text
taxonomy_and_scope_grounding
semantic_decision_correctness
source_retrieval_equivalence
receiver_evidence_integrity
safety_boundary
unknown_and_challenge_handling
```

Each item is 0, 1, or 2. Critical zero is evaluated before totals. Style, fluency, confidence, provider metadata, and agreement with another model are not quality scores.

Platform audit remains separate. Missing platform metadata cannot erase a byte-preserved scoreable answer, but missing or changed content evidence remains `UNVERIFIED` or `FAIL`.

## R4 Case Lifecycle

### Development regression set

R3 `CASE-001` through `CASE-010` are `development_regression_only`. They are used to test that the revised generalized method addresses established failures without regressions. They never count toward R4 formal recall, efficiency, or effectiveness.

### Formal holdout set

R4 uses 40 formal cases:

- the 30 R3 cases that were prepared but never executed, relabeled under R4 with receiver-only provenance;
- 10 new unseen known positives selected from official terminal nodes after the method and frozen terminology input are fixed.

The exact composition is:

| Primary category | Count |
| --- | ---: |
| direct supported positive | 8 |
| hidden positive | 6 |
| misleading name similarity | 6 |
| source sparse or inaccessible | 5 |
| ambiguous or incomplete conditions | 5 |
| circular or mixed-company source | 4 |
| empty generalization | 3 |
| contamination, drift, or structure error | 3 |

The retained 30 provide four hidden positives and all 26 adverse/boundary cases. The new 10 provide eight direct positives and two hidden positives.

### Freeze order and leakage prevention

The order is mandatory:

1. freeze revised method specification, prompt/schema hashes, source permissions, budget, and terminology input;
2. independently prepare and seal the 10 new positive cases and truth;
3. create a new 40-case set, real SHA-256, real R4 case IDs, and real control IDs;
4. bind those values to a new final frozen contract version;
5. generate model tasks only after final-contract validation and separate execution authorization.

The method builder cannot read formal truth. If a formal sentinel causes any method, prompt, terminology, budget, scoring, or source-policy change, that sentinel becomes development evidence, the contract is invalidated, and replacement unseen cases are required.

## Paired Evaluation

Both arms use the same formal cases, declared GPT-5.6 Terra configuration, tools, source permissions, observation window, visible input, truth package, budget accounting, and rubric. Every arm/case pair runs in a fresh independent context, with the other arm and all truth hidden. Raw answers and receiver evidence are append-only.

The first eight sealed pairs are sentinels. They count toward the formal 40 only if no method or contract input changes. If they reveal a defect that changes the method, they are retired from formal scoring.

After the 40 formal pairs, repeat six predeclared high-risk revised-arm cases in fresh contexts for stability. Repeats do not replace or increase the 40-case score. Critical semantic and safety dispositions must remain consistent.

## R4 Verdict Gates

The revised method may receive `CONTENT_CALIBRATION_PASS` only when:

- all 40 paired cases have complete, hash-valid content evidence;
- all 14 known positives enter evidence expansion;
- critical safety failures are zero;
- no company contamination, unsupported `supported` state, industry-wide exclusion, truth leakage, or three-axis collapse occurs;
- deep-expansion case count is at least 20% below baseline;
- total query count is no more than 10% above baseline;
- source-open count is no higher than baseline;
- equivalent-source judgments and receiver snapshot integrity pass;
- six stability repeats have consistent critical dispositions;
- all frozen inputs, source permissions, model configuration, task hashes, and raw-output hashes reproduce.

`CONTENT_CALIBRATION_PASS` is not strict-audit `EFFECTIVE`, does not prove the full terminal-node miss rate, and does not authorize full screening. Full screening remains default-deny and requires a separate user authorization. Downstream remains `RESEARCH_ONLY_BLOCKED`.

## R4 Preparation Contract Shape

The first R4 contract is a preparation contract, not a model-run contract:

```json
{
  "research_contract_id": "RC2-40-CONTENT-FIRST-CALIBRATION-20260824-R4",
  "contract_version": "2.1.0-content-first.prep.1",
  "contract_state": "draft_pending_skill_upgrade",
  "target_contract_state": "case_preparation_locked",
  "execution_mode": "content_first",
  "skill_versions": {
    "industry_application_map_builder": "0.4.0-beta.2",
    "foreign_trade_workflow_director": "0.3.0-beta.2"
  },
  "rollback_git_commit": "859bd6d948213a10464eddec635c264a24f68d77",
  "revised_skill_git_commit": null,
  "terminology_bridge_reference": null,
  "terminology_bridge_sha256": null,
  "formal_case_set_sha256": null,
  "control_case_ids": [],
  "batch_size": null,
  "locked_input_sha256": null,
  "execution_authorized": false,
  "full_screening_authorization": false,
  "application_base_write_authorization": false,
  "first_incomplete_stage": "industry_semantic_expansion",
  "downstream_release_state": "RESEARCH_ONLY_BLOCKED"
}
```

Null hashes, control IDs, batch size, and revised commit are mandatory while their real objects do not yet exist. No placeholder may make the draft appear locked or frozen.

## Implementation Scope After Spec Approval

Implementation will use failing tests before source edits and will be limited to:

- same-name map skill instructions and relevant semantic/content-first references;
- generalized terminology, task, truth, scorecard, and receiver-evidence templates;
- task builder, contract locker/finalizer, validator, and evaluator changes;
- same-name workflow controller compatibility fields and stop gates;
- source tests for fixed-term absence, cross-company isolation, cold start, invalid hashes, stale term packs, truth leakage, output-family decomposition, three-link gating, scoring separation, case reuse, and formal-run refusal before final freeze.

The installed cache and all R2/R3 frozen artifacts remain unchanged. Source implementation, Git commit, installation, R4 preparation writes, case preparation, and model execution remain separate authorizations.

## Verification Layers

1. **Structural:** schemas, versions, references, fixed-term absence, isolation, hash and refusal tests.
2. **Development regression:** the exposed first ten R3 cases; no formal credit.
3. **Cross-domain cold start:** at least three unrelated product-neutral research themes and two isolated company roots; no prior-company terminology transfer.
4. **Formal content validation:** the new R4 paired 40-case set plus the six stability repeats.

Structural or regression PASS establishes implementation readiness only. Optimization effectiveness remains `UNVERIFIED` until layer 4 passes.

## Rollback

Rollback returns the source and installed plugin to the recorded baseline commit/version without deleting append-only R4 preparation or run artifacts. A rollback cannot relabel R4 results as R3 evidence or merge them into frozen R2/R3 directories.
