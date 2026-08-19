---
name: industry-application-map-builder
description: Use when work involves an official industry taxonomy, product-neutral industry semantic screening, method calibration, evidence expansion, reverse-audit coverage, a company-specific industry application map, route candidates, or a controlled route-pool handoff before customer-development validation.
---

# 行业应用地图构建

## Core principle

Build the missing evidence layer between approved company product facts and customer-development direction validation. Use official industry classification as an activity skeleton, public product-neutral application evidence as the application layer, and one company's approved facts as the matching input.

This skill owns shared industry/application knowledge, RC2 semantic-method research, company-specific matching, route candidates, and coverage. Its workbooks and semantic research records are a machine evidence backend, not the salesperson's daily interface. When work starts from `foreign-trade-workflow-director`, return a traceable business projection for its `salesperson_workbench`; do not make the coordinator or salesperson maintain machine sheets.

本技能不得搜索具体客户，不得用综合评分给路线或国家排序，不得选择客户、起草外联内容或修改公司产品知识库。本技能不得写入 `direction_status = 已确认可扫描`；该决定仍由业务员在 `foreign-trade-customer-development` 中记录。

## Start contract

1. Select exactly one route from the table below.
2. Determine whether the request authorizes writes. Review, audit, explain, and diagnose requests remain read-only.
3. For semantic-method routes, require one map root, frozen taxonomy snapshot, product-neutral research theme, contract version, model profile, allowed source scope, budget, and explicit authorization for the requested phase. Do not require or load company facts.
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
| `semantic_contract_prepare` | Freeze the product-neutral theme, taxonomy snapshot, model profile, prompts, budget, sampling and write boundary | [industry-semantic-research-contract.md](references/industry-semantic-research-contract.md) | Frozen `semantic_research_contract`; stop before case preparation |
| `semantic_calibration_case_prepare` | Build the frozen 40-case truth package | [industry-semantic-calibration-and-audit.md](references/industry-semantic-calibration-and-audit.md) | Versioned case set and hashes; incomplete truth returns `INCONCLUSIVE` |
| `semantic_method_calibration` | Run paired baseline and candidate arms under identical controls | [industry-semantic-calibration-and-audit.md](references/industry-semantic-calibration-and-audit.md) and [industry-semantic-model-protocol.md](references/industry-semantic-model-protocol.md) | `EFFECTIVE / NOT_EFFECTIVE / INCONCLUSIVE`; stop before full screening |
| `semantic_full_screening` | Shallow-screen every frozen terminal node in controlled batches | [industry-semantic-research-contract.md](references/industry-semantic-research-contract.md) | Append-only screening batch; stop after each batch and check drift/budget |
| `semantic_evidence_expansion` | Expand triggered nodes into minimal claims and source packets | [industry-semantic-model-protocol.md](references/industry-semantic-model-protocol.md) | Evidence packets and B-review tasks; no `supported` before B PASS |
| `semantic_reverse_audit` | Sample the rejected population by risk and calculate the finite-population bound | [industry-semantic-calibration-and-audit.md](references/industry-semantic-calibration-and-audit.md) | Audit plan/report; any confirmed miss fails the contract |
| `semantic_stage_review` | Validate full coverage, one contract version, evidence gates, audit and safety | [coverage-and-lifecycle.md](references/coverage-and-lifecycle.md) | Stage `PASS / FAIL / UNVERIFIED`; stop before company matching |

Do not combine routes merely because the next step is convenient. Complete the requested route, validate it, and stop unless the user separately authorized the next route.

## RC2 semantic-method gate

Keep method status `INCONCLUSIVE` until the frozen 40-case paired run passes. Writing clearer rules, passing static tests, or producing a pilot does not prove method effectiveness.

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

Use deterministic scripts for repeatable operations:

```bash
python3 scripts/init_semantic_research_workspace.py --map-root /absolute/map-root --contract /absolute/semantic-research-contract.json
python3 scripts/build_semantic_model_handoff.py --task /absolute/filled-model-task.json --input /absolute/visible-input.json --output /absolute/self-contained-handoff.json
python3 scripts/freeze_semantic_taxonomy_snapshot.py --taxonomy-workbook /absolute/industry-taxonomy.xlsx --output /absolute/taxonomy-snapshot.json
python3 scripts/validate_semantic_research_workspace.py /absolute/semantic-research-workspace --format json
python3 scripts/sample_semantic_reverse_audit.py --screening-records /absolute/screening-records.jsonl --seed frozen-seed --output /absolute/audit-plan.json
python3 scripts/evaluate_semantic_calibration.py --baseline /absolute/baseline.json --candidate /absolute/candidate.json --output /absolute/calibration-report.json
```

These scripts refuse overwrites where results are append-only. Do not add force flags or delete prior runs to reuse an ID.

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
