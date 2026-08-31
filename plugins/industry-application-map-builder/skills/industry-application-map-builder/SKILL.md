---
name: industry-application-map-builder
description: Use when work involves an official industry taxonomy, generalized content-first R4 or legacy strict-audit RC2 semantic screening, 40-case scoring, evidence expansion, reverse-audit coverage, a company-specific industry application map, route candidates, or controlled handoff before customer-development validation.
---

# 行业应用地图构建

## RC2 mode selection

Use one semantic evaluation mode per research contract. For a newly prepared RC2 research contract, set `execution_mode = content_first`; this is the current default route. Use `strict_audit` only when the user explicitly selects it, or when a legacy beta.3 contract has no mode field. A legacy no-mode contract remains strict-audit compatible and retains every beta.3 identity, transport, receipt, and admissibility gate unchanged.

Within `content_first`, source version `0.4.0-beta.6` uses the `content_first_r4` marker plus `case_package_contract_version = 1.0-beta5`, `truth_contract_version = 2.1-r4-adjudicated`, and `truth_scorecard_contract_version = 2.1-r4`. It remains the same `industry-application-map-builder` skill; do not create or route to a candidate skill. Never downgrade an R4 artifact because a marker, version or arm field is missing: that is a refusal, not legacy detection. Beta.3, beta.4 and beta.5 R4 artifacts are historical read-only inputs for beta.6 and cannot be continued by a beta.6 lock, finalizer, task builder, or scorer.

| Mode | Content decision evidence | Status vocabulary | Boundary |
| --- | --- | --- | --- |
| `content_first` | Complete raw answer, visible input/hash, source/truth comparison, itemized scorecard, and unknown items; platform audit is separate | `CONTENT_CONTRACT_FROZEN`, `CONTENT_CALIBRATION_*`, content full-scope states | Research-only; never emit strict `EFFECTIVE` or release downstream work. |
| `strict_audit` | The existing beta.3 evidence and admissibility contract | `INCONCLUSIVE / EFFECTIVE / NOT_EFFECTIVE` | Preserve the existing route and tools unchanged. |

Never infer `content_first` from missing platform metadata. Read [content-first-mode-contract.md](references/content-first-mode-contract.md), [compatibility-matrix.md](references/compatibility-matrix.md), and [optimization-validation.md](references/optimization-validation.md) before evaluating or retaining an optimized content-first version. Use `assets/content-first/` only for a new content-first contract; never retrofit its fields into a frozen beta.3 contract.

## Generalized R4 retrieval contract

Keep three terminology layers separate:

1. `global skill terminology schema`: only the six generic concept roles, discovery behavior, provenance fields, isolation gates and hashing rules; it contains no production terms;
2. `contract-local terminology`: product-neutral discovery terms accepted for one research contract, stored and hashed in that contract's local terminology bridge;
3. `company-local terminology pack`: company, brand, product, process and salesperson language stored only inside that company's workspace and never used by product-neutral semantic calibration.

Official taxonomy semantics are frozen case inputs, not a terminology layer and not a production synonym list.

A cold start may be empty. Do not ship a fixed production terminology list, company vocabulary, answer-derived sentinel list or any industry-specific shortcut in this skill. Do not copy a company-local terminology pack across companies. Model-discovered terms are case-local retrieval candidates only; they never become evidence and never mutate the frozen contract-local terminology bridge or later tasks.

For a broad node, perform `output-family` decomposition before bounded discovery. The candidate arm may expand case-local queries only after the frozen core search cannot establish all three links. A research claim requires all of:

- `taxonomy membership basis`;
- `output or subprocess basis`;
- `mechanism or use-point basis`.

Classification names, query matches and model terms cannot satisfy those links by themselves.

## Core principle

Build the missing evidence layer between approved company product facts and customer-development direction validation. Use official industry classification as an activity skeleton, public product-neutral application evidence as the application layer, and one company's approved facts as the matching input.

This skill owns shared industry/application knowledge, RC2 semantic-method research, company-specific matching, route candidates, and coverage. Its workbooks and semantic research records are a machine evidence backend, not the salesperson's daily interface. When work starts from `foreign-trade-workflow-director`, return a traceable business projection for its `salesperson_workbench`; do not make the coordinator or salesperson maintain machine sheets.

本技能不得搜索具体客户，不得用综合评分给路线或国家排序，不得选择客户、起草外联内容或修改公司产品知识库。本技能不得写入 `direction_status = 已确认可扫描`；该决定仍由业务员在 `foreign-trade-customer-development` 中记录。

## Start contract

1. Select exactly one route from the table below.
2. Determine whether the request authorizes writes. Review, audit, explain, and diagnose requests remain read-only.
3. For semantic-method routes, require one map root, frozen taxonomy snapshot, product-neutral research theme, contract version, model profile, allowed source scope, budget, and explicit authorization for the requested phase. `semantic_calibration_case_prepare` requires a hash-valid `case_preparation_locked` contract; model tasks require the new-version final `frozen` contract. Do not require or load company facts.
4. For company routes, require one explicit `company_id`, company product-library root, product fact packet, product scope, map root, and declared research scope. Resolve every fact ID to the same company's `facts.json` and freeze all input hashes before matching.
5. Stop if an input is missing, another company appears, a hash or contract changed, a confirmed ID does not resolve, the taxonomy version is unfrozen, or the requested semantic phase lacks its own authorization.

## Route selection

| Route | Trigger | Required reference | Output and stop point |
|---|---|---|---|
| `base_bootstrap` | Create an empty shared map root and versioned workbook skeletons | [workspace-and-ownership-contract.md](references/workspace-and-ownership-contract.md) | Empty root validates; no application facts or company map are inferred |
| `application_knowledge_update` | Add or revise official taxonomy or product-neutral application evidence | [industry-application-schema.md](references/industry-application-schema.md) and [evidence-and-derivation.md](references/evidence-and-derivation.md) | Shared base and affected-route review flags are updated; no company fit is asserted |
| `company_map_build` | Match one approved product fact packet to the shared application base | [evidence-and-derivation.md](references/evidence-and-derivation.md) and [coverage-and-lifecycle.md](references/coverage-and-lifecycle.md) | Company routes and coverage dispositions are recorded; no customer search starts |
| `company_map_review` | Review coverage, conflicts, stale inputs, exclusions, or route lifecycle | [coverage-and-lifecycle.md](references/coverage-and-lifecycle.md) and [pressure-scenarios.md](references/pressure-scenarios.md) | `PASS / FAIL / UNVERIFIED` review and required action are recorded |
| `route_pool_handoff` | Export validated route candidates for customer-development direction work | [handoff-contracts.md](references/handoff-contracts.md) | A registered `company_route_pool_packet` is written inside the company map; stop before direction or company research |
| `semantic_contract_prepare` | Complete and lock the product-neutral theme, taxonomy snapshot, model profile, prompts, budget, sampling and isolated write boundary | [industry-semantic-research-contract.md](references/industry-semantic-research-contract.md) | `case_preparation_locked` contract with `locked_input_sha256`; case-set hash and control IDs remain empty; stop before candidate preparation |
| `semantic_calibration_case_prepare` | Build and freeze the 40-case truth package, then bind it to a new final contract version | [industry-semantic-calibration-and-audit.md](references/industry-semantic-calibration-and-audit.md) | Real case-set hash, real control IDs and new-version final `frozen` contract; incomplete truth returns `INCONCLUSIVE` and no model task is issued |
| `semantic_method_calibration` | Run paired baseline and candidate arms under identical controls for legacy `strict_audit` only | [industry-semantic-calibration-and-audit.md](references/industry-semantic-calibration-and-audit.md) and [industry-semantic-model-protocol.md](references/industry-semantic-model-protocol.md) | Legacy `EFFECTIVE / NOT_EFFECTIVE / INCONCLUSIVE`; stop before full screening |
| `semantic_full_screening` | Shallow-screen every frozen terminal node in controlled batches | [industry-semantic-research-contract.md](references/industry-semantic-research-contract.md) | Append-only screening batch; stop after each batch and check drift/budget |
| `semantic_evidence_expansion` | Expand triggered nodes into minimal claims and source packets | [industry-semantic-model-protocol.md](references/industry-semantic-model-protocol.md) | Evidence packets and B-review tasks; no `supported` before B PASS |
| `semantic_reverse_audit` | Sample the rejected population by risk and calculate the finite-population bound | [industry-semantic-calibration-and-audit.md](references/industry-semantic-calibration-and-audit.md) | Audit plan/report; any confirmed miss fails the contract |
| `semantic_stage_review` | Validate full coverage, one contract version, evidence gates, audit and safety | [coverage-and-lifecycle.md](references/coverage-and-lifecycle.md) | Stage `PASS / FAIL / UNVERIFIED`; stop before company matching |
| `content_first_contract_prepare` | Freeze a content-first contract and rubric after the existing preparation/case-set gates | [content-first-mode-contract.md](references/content-first-mode-contract.md) | `CONTENT_CONTRACT_FROZEN`; stop before 40-case content work |
| `content_first_calibration_review` | Score both 40-case arms from raw-answer envelopes and source/truth packets | [content-first-mode-contract.md](references/content-first-mode-contract.md) | `CONTENT_CALIBRATION_*`; stop at a full-scope authorization request |
| `content_first_full_screening_gate` | Check content calibration and explicit human full-scope authorization | [content-first-mode-contract.md](references/content-first-mode-contract.md) | `NOT_AUTHORIZED` or `AUTHORIZED_NOT_STARTED`; do not run nodes automatically |
| `content_first_full_screening` | Run only explicitly authorized append-only content screening batches | [content-first-mode-contract.md](references/content-first-mode-contract.md) | `IN_PROGRESS / COVERAGE_INCOMPLETE / READY_FOR_REVERSE_AUDIT`; stop after every batch |
| `content_first_r4_contract_prepare` | Prepare beta.3 generalized terminology, visible-only cases, truth and frozen R4 bindings | [content-first-mode-contract.md](references/content-first-mode-contract.md) | Frozen R4 contract inputs only; no model execution |
| `content_first_r4_task_prepare` | Build truth-blind paired tasks from the frozen visible-only case set | [industry-semantic-model-protocol.md](references/industry-semantic-model-protocol.md) | Exactly `40 pairs`; model execution remains denied |
| `content_first_r4_calibration_review` | Validate the real 80-task evidence chains and six repeats | [industry-semantic-calibration-and-audit.md](references/industry-semantic-calibration-and-audit.md) | `CONTENT_CALIBRATION_PASS / FAIL / INCOMPLETE`; never strict `EFFECTIVE` |

Do not combine routes merely because the next step is convenient. Complete the requested route, validate it, and stop unless the user separately authorized the next route.

## RC2 semantic-method gate

Keep method status `INCONCLUSIVE` until the frozen 40-case paired run passes. Writing clearer rules, passing static tests, or producing a pilot does not prove method effectiveness.

For `content_first`, keep `content_method_state = CONTENT_CALIBRATION_INCOMPLETE` until its frozen 40-case content evidence gate passes. This state can only determine whether explicit full-scope authorization may be requested; it is not a real-world effectiveness claim and must never be relabeled as strict-audit `EFFECTIVE`.

R4 calibration uses `baseline_full_depth_v1` and `screen_then_expand_v2` on the same frozen visible inputs. Build exactly `40 pairs`, then validate each real task, raw response, raw envelope, six-item scorecard, receiver resource observation and receipt. Stability is `6 predeclared high-risk single-case repeats`, not six copied arm summaries or six additional 40-case runs. Apply gates in the frozen order: `safety -> recall -> receiver evidence -> stability -> efficiency`. Do not report efficiency metrics before all earlier gates close.

Preserve three independent semantic axes:

```text
screening_result: hypothesis_formed | ambiguous | no_hypothesis_formed
semantic_work_state: not_screened | screened | evidence_expansion_required | evidence_expanded | audit_reopened
evidence_state: supported | hypothesis | unknown | conflicted
```

Never convert absence of a hypothesis, low keyword similarity, sparse public information, or an unprocessed node into an industry exclusion. Read all three semantic references before any semantic-method route:

1. [industry-semantic-research-contract.md](references/industry-semantic-research-contract.md)
2. [industry-semantic-model-protocol.md](references/industry-semantic-model-protocol.md)
3. [industry-semantic-calibration-and-audit.md](references/industry-semantic-calibration-and-audit.md)

Use the templates under `assets/semantic-method/`. Current external-model transport is `manual_external_handoff`: Codex must build one self-contained package containing the visible input, canonical input hash, exact return schema, field ownership, null rules and stop condition. The user only transfers that package and the raw return; never ask the user to fill machine evidence fields. After receipt, keep the untouched external return separate from the receiver-owned `semantic_model_receipt`; never backfill model-reported run IDs or timestamps with Codex receipt data. Do not claim automatic Claude or Grok invocation without a separately authorized connector.

Keep `review_result` separate from `admissibility_state`. An external reviewer may return `PASS` on source content while the transport or identity evidence remains `UNVERIFIED`; in that case do not upgrade evidence or count the run in the 40-case calibration.

In `content_first`, preserve the actual raw response in a separate immutable file and make the content envelope point to its byte SHA-256. Every case or node must retain: case/node ID, visible input and hash, method arm, raw response reference and hash, source/truth comparison reference and hash, a non-style itemized scorecard, and explicit unknown items. Platform transport, platform time, run IDs, and model identity evidence belong only to `platform_audit_state` and cannot replace this evidence. An unknown platform audit cannot by itself fail a complete content scorecard; a missing or changed raw response, input, source/truth packet, scorecard, or unknown list must return `UNVERIFIED` or `FAIL`.

`content_first` retains product neutrality, independently adjudicated accepted-positive recall, accepted negatives, unresolved truth, misleading controls, source-scarce and cyclic-source handling, cross-company isolation, claim-inflation prevention, three independent semantic axes, direct-source evidence, evidence expansion, and reverse audit. Sampling labels and selection reasons never define truth. Recall uses the accepted-positive set derived from the current accepted truth package; reopened or superseded truth invalidates prior tasks, scores, arm summaries, and calibration results. `CONTENT_CALIBRATION_PASS` does not authorize all nodes. Full-scope authorization remains false by default and requires an explicit human authorization reference plus unchanged `terminal_node_manifest_sha256`. Use the coverage validator to compare every append-only node record with the frozen manifest; `READY_FOR_REVERSE_AUDIT` still requires the content-evidence validator and does not mean stage PASS. Keep `downstream_release_state = RESEARCH_ONLY_BLOCKED`; do not enter shared-base writes, company matching, routes, or customers without a separately authorized migration decision.

Until all full-scope evidence and reverse-audit gates are genuinely satisfied, return `first_incomplete_stage = industry_semantic_expansion`. A static test, frozen task package or `CONTENT_CALIBRATION_PASS` cannot advance this lifecycle stage by itself.

## Legacy strict_audit semantic method

Only an explicit legacy strict-audit contract uses the retained beta.3 identity/admissibility gates and `INCONCLUSIVE / EFFECTIVE / NOT_EFFECTIVE` vocabulary. Do not apply those identity requirements as a content PASS gate, relabel `CONTENT_CALIBRATION_PASS` as `EFFECTIVE`, or downgrade a damaged R4 artifact into this branch.

## Shared deterministic tools

Use deterministic scripts for repeatable operations:

```bash
python3 scripts/lock_semantic_case_preparation_contract.py --contract /absolute/research-contract.draft.json --authorization-reference /absolute/authorization-event.json --expected-skill-git-commit REAL_40_HEX_GIT_COMMIT --locked-at 2026-01-01T00:00:00Z --output /absolute/case-preparation-contract.locked.json
python3 scripts/finalize_semantic_research_contract.py --preparation-contract /absolute/case-preparation-contract.locked.json --case-set /absolute/calibration-case-set.jsonl --case-set-reference 02-校准案例/calibration-case-set.jsonl --final-contract-version 1.0.0 --batch-size 10 --control-case-id CASE-001 --frozen-at 2026-01-02T00:00:00Z --output /absolute/semantic-research-contract.json
python3 scripts/init_semantic_research_workspace.py --map-root /absolute/map-root --contract /absolute/semantic-research-contract.json
python3 scripts/build_semantic_model_handoff.py --task /absolute/filled-model-task.json --input /absolute/visible-input.json --output /absolute/self-contained-handoff.json
python3 scripts/freeze_semantic_taxonomy_snapshot.py --taxonomy-workbook /absolute/industry-taxonomy.xlsx --output /absolute/taxonomy-snapshot.json
python3 scripts/validate_semantic_research_workspace.py /absolute/semantic-research-workspace --format json
python3 scripts/sample_semantic_reverse_audit.py --screening-records /absolute/screening-records.jsonl --seed frozen-seed --output /absolute/audit-plan.json
python3 scripts/evaluate_semantic_calibration.py --baseline /absolute/baseline.json --candidate /absolute/candidate.json --output /absolute/calibration-report.json
python3 scripts/validate_content_first_workspace.py /absolute/content-first-workspace --format json
python3 scripts/freeze_content_first_visible_case_set.py --visible-case-draft /absolute/visible-draft.jsonl --visible-case-set-reference 02-校准案例/visible-case-set.jsonl --freeze-authorization-reference USER-R4-VISIBLE-FREEZE --frozen-at 2026-01-01T00:00:00Z --output /absolute/visible-case-set.jsonl --receipt-output /absolute/visible-case-freeze-receipt.json
python3 scripts/freeze_content_first_case_package.py --preparation-contract /absolute/case-preparation-contract.locked.json --contract-local-root /absolute/preparation-root --case-set /absolute/preparation-root/02-校准案例/formal-case-set.jsonl --case-set-reference 02-校准案例/formal-case-set.jsonl --visible-case-set /absolute/preparation-root/02-校准案例/visible-case-set.jsonl --visible-case-set-reference 02-校准案例/visible-case-set.jsonl --visible-case-freeze-receipt /absolute/preparation-root/02-校准案例/visible-case-freeze-receipt.json --visible-case-freeze-receipt-reference 02-校准案例/visible-case-freeze-receipt.json --expected-visible-case-freeze-receipt-sha256 REAL_SHA256 --source-truth-package /absolute/preparation-root/03-来源真值/source-truth.jsonl --source-truth-reference 03-来源真值/source-truth.jsonl --final-contract-version NEW_VERSION --batch-size 10 --control-case-id CASE-001 --frozen-at 2026-01-02T00:00:00Z --package-authorization-reference USER-R4-PACKAGE-FREEZE --output /absolute/immutable-case-package
python3 scripts/build_content_first_calibration_tasks.py --contract /absolute/final-contract.json --visible-case-set /absolute/visible-case-set.jsonl --contract-local-root /absolute/research-root --expected-final-contract-sha256 REAL_SHA256 --package-generation-authorization-receipt /absolute/package-generation-authorization.json --expected-package-generation-authorization-receipt-sha256 REAL_SHA256 --output /absolute/paired-tasks
python3 scripts/freeze_content_first_stability_tasks.py --workspace /absolute/content-first-workspace --contract /absolute/final-contract.json --expected-final-contract-sha256 REAL_SHA256 --formal-case-set /absolute/formal-case-set.jsonl --expected-formal-case-set-sha256 REAL_SHA256 --paired-task-manifest /absolute/paired-tasks/paired-task-manifest.json --expected-paired-task-manifest-sha256 REAL_SHA256 --authorization-id-prefix R4-REPEAT --authorized-at 2026-01-01T00:00:00Z --output /absolute/stability-tasks
python3 scripts/init_content_first_workspace.py --map-root /absolute/map-root --contract /absolute/content-first-contract.json
python3 scripts/evaluate_content_first_calibration.py --baseline /absolute/content-baseline.json --candidate /absolute/content-candidate.json --output /absolute/content-calibration-report.json
python3 scripts/check_content_first_full_screening_gate.py --workspace /absolute/preparation-workspace --contract /absolute/preparation-workspace/00-contract/final-contract.json --expected-final-contract-sha256 <sha256> --calibration-report /absolute/preparation-workspace/07-reports/r4-evaluation.json --expected-calibration-report-sha256 <sha256> --terminal-node-manifest /absolute/preparation-workspace/01-snapshots/terminal-node-manifest.json --expected-terminal-node-manifest-sha256 <sha256> --authorization-receipt /absolute/preparation-workspace/00-contract/full-screen-authorization.receipt.json --expected-authorization-receipt-sha256 <sha256> --output /absolute/full-scope-gate.json
python3 scripts/validate_content_first_full_coverage.py --contract /absolute/content-first-contract.json --terminal-node-manifest /absolute/terminal-nodes.json --screening-index /absolute/content-screening-index.json --output /absolute/content-coverage-report.json
```

These scripts refuse overwrites where results are append-only. Do not add force flags or delete prior runs to reuse an ID.

The preparation lock permits only candidate/case preparation inside its isolated write scope. It is not a model-run contract. Never invent a placeholder case-set hash or control case ID to make a draft look frozen; the runtime initializer remains final-`frozen` only.

## Ownership and isolation

- Treat the company product library as read-only. Never change evidence levels, facts, sources, product hierarchy, or allowed use here.
- Keep shared taxonomy and application facts product-neutral. They must not contain a company product claim, customer, supplier relationship, company route status, or company-specific example.
- Keep each company under `04-公司地图/<company_id>/`. Never copy another company's capabilities, routes, exclusions, geography hypotheses, or review history.
- For an explicitly requested cross-company comparison, use a separate working area and do not write the comparison back automatically.
- Read [workspace-and-ownership-contract.md](references/workspace-and-ownership-contract.md) before every mutating route.

## Derivation gate

Never connect an industry code directly to a company product. Preserve both chains:

```text
industry_node -> output_product -> use_point_or_process -> application_node -> requirement_atom
approved_product_fact -> capability_atom -> requirement_atom_match -> application_node -> output_product -> industry_node -> target_enterprise_activity
```

Apply the four-state formula in [evidence-and-derivation.md](references/evidence-and-derivation.md). A route becomes `路线候选` only when the application relation is supported, every hard technical requirement is satisfied, required conditions and interfaces are compatible, and no known limit conflicts. Otherwise keep it as `路线线索`, `暂缓`, `排除`, or an explicit unknown. Never average these states.

## Workbook gate

Use `spreadsheets:Spreadsheets` for every `.xlsx` creation or edit. Start from the bundled templates, preserve machine headers in row 1 and Chinese business labels in row 2, keep data from row 3 onward, and retain filters, frozen headers, validations, widths, and styles. Reopen and visually inspect every changed sheet before reporting success.

Initialize a shared root only after creation is authorized:

```bash
python3 scripts/init_industry_application_workspace.py \
  --mode root \
  --destination /absolute/path/to/industry-application-map-root \
  --taxonomy-system GB/T-4754 \
  --taxonomy-version 2017-2019-modification \
  --taxonomy-source-url https://www.stats.gov.cn/ \
  --declared-scope full-official-skeleton \
  --application-base-version 1.0.0 \
  --source-scope public-primary-sources
```

The initializer refuses to overwrite an existing root or company map. Never add a force option or delete a destination to make initialization pass.

## Shared knowledge update

Use official classification sources for taxonomy nodes. Use traceable public sources for output products, use points, processes, application nodes, and requirements. Record publisher, title, URL or local archive reference, publication date or `unknown`, observation date, source subject, original location, Chinese summary, evidence state, access scope, dependency group, conflict, and limitation.

AI world knowledge, mechanism reasoning, semantic similarity, and common practice may create a `hypothesis` and search vocabulary only. They cannot create `supported` evidence. A classification node proves an economic activity category, not a terminal application, technical requirement, market size, or customer need.

Calibration writes only inside `05-工作区/行业语义研究/<research_contract_id>/`. `application_knowledge_update` may write a reviewed relationship into the shared base only after method `EFFECTIVE`, full-stage authorization, `application_base_write_authorization = true`, direct evidence, B PASS, and automated validation. Screening records and model consensus are never shared-base facts.

After changing a shared workbook, update its registry hash, append the change log, and mark dependent company routes for review. Never silently replace an old taxonomy version; add a new version and an explicit correspondence or unresolved migration record.

## Company map build

Use the minimum route key `company_id + product_scope + application_node_id`. Read [industry-application-schema.md](references/industry-application-schema.md) for exact fields.

For each route:

1. Cite approved product fact IDs and their source IDs.
2. Cite the product-neutral application node, requirement atoms, and application evidence IDs.
3. Match every hard requirement separately as `satisfied`, `violated`, `unknown`, or `conflicted`.
4. Record condition compatibility, process/interface compatibility, known-limit conflicts, source independence, counterevidence, and unknowns.
5. Assign evidence, technical, research-disposition, and map-route states independently.
6. Record geography only as a sourced,待验证 hypothesis. Do not convert it to a country priority.

An application failure excludes only that product-scope/application route. It does not exclude the whole industry, another product, or another company.

## Coverage and handoff

Coverage is measured against the declared scope, not route count. Every confirmed product capability, effect, application, or explicit freeze must have a route, defer, exclusion, or unknown disposition. A taxonomy branch outside the declared scope is `out_of_scope`, not irrelevant.

Before export, run:

```bash
python3 scripts/validate_industry_application_workspace.py \
  /absolute/path/to/industry-application-map-root \
  --company-id ACME-001 \
  --format json
```

Export only after `PASS`:

```bash
python3 scripts/export_company_route_pool.py \
  /absolute/path/to/industry-application-map-root \
  --company-id ACME-001 \
  --output /absolute/path/to/industry-application-map-root/04-公司地图/ACME-001/company-route-pool-packet.json
```

The exporter refuses overwrite and any destination outside that company's map directory. It writes the packet hash, input snapshot, and source company-map path/hash to `route-pool-export-registry.json`; downstream work must verify that producer record rather than trusting a copied packet by filename. If the packet or source map is changed, missing, cross-company, stale, superseded, or no longer matches the recorded snapshot, invalidate the handoff and re-export after review.

The packet targets `foreign-trade-customer-development`. It does not authorize customer scanning, full due diligence, country priority, customer selection, or `已确认可扫描`.

If the request arrived through `foreign-trade-workflow-director`, also return a `specialist_return_packet` that preserves the route IDs, packet and registry references, `PASS / FAIL / UNVERIFIED`, staleness state, business summary, blockers, and the salesperson decision required. The return is a projection only: `salesperson_workbench` may show route choices and exceptions, but it must not copy or replace taxonomy, application, relationship, evidence, coverage, or change-log sheets.

When taxonomy, application-base, product-fact, company-map, route-packet, or producer-registry hashes become stale or mismatched, return `shared_input_stale_event` to the coordinator. The event must identify the affected route IDs and exact validation status, and must block downstream direction compilation or candidate collection until this skill revalidates and re-exports a current packet.

## Completion report

Report the selected route, `company_id` when applicable, declared scope, files changed, input hashes, evidence and route IDs affected, validation command and actual result, coverage gaps, material `FAIL` or `UNVERIFIED` items, and downstream work not performed.

Before completion, read [pressure-scenarios.md](references/pressure-scenarios.md). Static contract checks do not prove live agent behavior, real-company correctness, public-source completeness, or market coverage.
