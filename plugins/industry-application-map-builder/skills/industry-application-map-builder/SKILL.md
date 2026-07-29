---
name: industry-application-map-builder
description: Use when a company needs a shared industry/application framework, product-neutral application evidence, a company-specific industry application map, route candidates, route coverage review, or a controlled route-pool handoff before customer-development direction validation.
---

# 行业应用地图构建

## Core principle

Build the missing evidence layer between approved company product facts and customer-development direction validation. Use official industry classification as an activity skeleton, public product-neutral application evidence as the application layer, and one company's approved facts as the matching input.

This skill owns shared industry/application knowledge, company-specific matching, route candidates, and coverage. 本技能不得搜索具体客户，不得用综合评分给路线或国家排序，不得选择客户、起草外联内容或修改公司产品知识库。本技能不得写入 `direction_status = 已确认可扫描`；该决定仍由业务员在 `foreign-trade-customer-development` 中记录。

## Start contract

1. Select exactly one route from the table below.
2. Determine whether the request authorizes writes. Review, audit, explain, and diagnose requests remain read-only.
3. For every company route, require one explicit `company_id`, company product-library root, product fact packet, product scope, map root, and declared research scope.
4. Resolve every product fact ID to the same company's `facts.json`, run the product-library validator, and freeze the packet, facts, taxonomy, and application-base SHA-256 values before matching.
5. Stop if an input is missing, another company appears, a hash changed, a confirmed ID does not resolve, or the shared taxonomy version is not frozen.

## Route selection

| Route | Trigger | Required reference | Output and stop point |
|---|---|---|---|
| `base_bootstrap` | Create an empty shared map root and versioned workbook skeletons | [workspace-and-ownership-contract.md](references/workspace-and-ownership-contract.md) | Empty root validates; no application facts or company map are inferred |
| `application_knowledge_update` | Add or revise official taxonomy or product-neutral application evidence | [industry-application-schema.md](references/industry-application-schema.md) and [evidence-and-derivation.md](references/evidence-and-derivation.md) | Shared base and affected-route review flags are updated; no company fit is asserted |
| `company_map_build` | Match one approved product fact packet to the shared application base | [evidence-and-derivation.md](references/evidence-and-derivation.md) and [coverage-and-lifecycle.md](references/coverage-and-lifecycle.md) | Company routes and coverage dispositions are recorded; no customer search starts |
| `company_map_review` | Review coverage, conflicts, stale inputs, exclusions, or route lifecycle | [coverage-and-lifecycle.md](references/coverage-and-lifecycle.md) and [pressure-scenarios.md](references/pressure-scenarios.md) | `PASS / FAIL / UNVERIFIED` review and required action are recorded |
| `route_pool_handoff` | Export validated route candidates for customer-development direction work | [handoff-contracts.md](references/handoff-contracts.md) | A registered `company_route_pool_packet` is written inside the company map; stop before direction or company research |

Do not combine routes merely because the next step is convenient. Complete the requested route, validate it, and stop unless the user separately authorized the next route.

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

## Completion report

Report the selected route, `company_id` when applicable, declared scope, files changed, input hashes, evidence and route IDs affected, validation command and actual result, coverage gaps, material `FAIL` or `UNVERIFIED` items, and downstream work not performed.

Before completion, read [pressure-scenarios.md](references/pressure-scenarios.md). Static contract checks do not prove live agent behavior, real-company correctness, public-source completeness, or market coverage.
