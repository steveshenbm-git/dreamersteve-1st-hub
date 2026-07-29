# Industry Application Map Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an evidence-traceable industry application map plugin between company product knowledge and foreign-trade customer development.

**Architecture:** Store product-neutral taxonomy and application facts in a shared map root, while isolating every company map by `company_id`. Use Excel as the readable working surface and a JSON `company_route_pool_packet` as the machine handoff; keep customer search and salesperson decisions in the downstream customer-development plugin.

**Tech Stack:** Markdown skill contracts, JSON manifests and packets, Python standard-library validation/export tools, `@oai/artifact-tool` workbook authoring, Python `unittest` contract and mutation tests.

## Global Constraints

- Work only in the `ft-customer-dev` source checkout; never edit `~/.codex/plugins/cache/`.
- Source-edit authorization does not authorize commit, install, cache mutation, or push.
- Preserve one-company isolation and immutable product-source ownership.
- Do not use a composite score for evidence, technical fit, route priority, country priority, or customer priority.
- Do not let the new skill search companies or set `direction_status = 已确认可扫描`.
- Keep live forward-testing `UNVERIFIED` because subagents were not authorized.

---

### Task 1: Lock RED contracts

**Files:**
- Create: `tests/industry-application-map-builder/test_contract.py`
- Create: `tests/industry-application-map-builder/test_workspace_tools.py`
- Create: `tests/industry-application-map-builder/pressure-prompts.md`
- Create: `tests/industry-application-map-builder/scorecard.md`

**Interfaces:**
- Consumes: the approved design and observed conversation failures.
- Produces: failing tests for plugin existence, workbook structure, company isolation, fact resolution, four-state matching, route export, and downstream ownership.

- [ ] Write contract assertions for required route names, ownership strings, state vocabularies, formula fields, and forbidden customer-search authority.
- [ ] Write tool tests that call `init_industry_application_workspace.py`, `validate_industry_application_workspace.py`, and `export_company_route_pool.py` through subprocesses.
- [ ] Run both test files and confirm failure is caused by the missing plugin and scripts.

### Task 2: Scaffold plugin and skill

**Files:**
- Create: `plugins/industry-application-map-builder/.codex-plugin/plugin.json`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/SKILL.md`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/agents/openai.yaml`
- Modify: `.agents/plugins/marketplace.json`

**Interfaces:**
- Consumes: plugin name `industry-application-map-builder` and Chinese title `行业应用地图构建`.
- Produces: a discoverable repo-local plugin with one skill and marketplace entry.

- [ ] Run the plugin scaffold into `plugins/` with the repo marketplace path.
- [ ] Run `init_skill.py` for the nested skill with `scripts,references,assets` resources and explicit interface strings.
- [ ] Replace all scaffold placeholders and validate frontmatter contains only `name` and `description`.

### Task 3: Implement workspace and workbook templates

**Files:**
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/empty-industry-taxonomy.xlsx`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/empty-industry-application-base.xlsx`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/empty-company-industry-application-map.xlsx`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/empty-industry-application-map-root/AGENTS.md`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/empty-industry-application-map-root/00-管理/map-registry.json`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/assets/empty-industry-application-map-root/00-管理/change-log.json`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/init_industry_application_workspace.py`

**Interfaces:**
- Consumes: `--destination`, optional `--company-id`, `--company-library-root`, and `--product-packet`.
- Produces: an overwrite-safe shared root and, when requested, one company directory with copied templates and frozen input references.

- [ ] Build the three workbooks with two header rows, filters, freeze panes, controlled-state validation, readable widths, and no company data.
- [ ] Implement initializer refusal code `DESTINATION_EXISTS` and company isolation checks.
- [ ] Run initializer tests and reopen every workbook to verify sheet order and headers.

### Task 4: Implement schema, derivation, and validation contracts

**Files:**
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/references/workspace-and-ownership-contract.md`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/references/industry-application-schema.md`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/references/evidence-and-derivation.md`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/references/coverage-and-lifecycle.md`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/references/handoff-contracts.md`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/references/pressure-scenarios.md`
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/validate_industry_application_workspace.py`

**Interfaces:**
- Consumes: one map root plus optional company library path.
- Produces: JSON validation report with `PASS` or errors such as `CROSS_COMPANY_ROUTE`, `UNRESOLVED_PRODUCT_FACT`, `ROUTE_STATUS_EXCEEDS_AUTHORITY`, and `TAXONOMY_VERSION_MISSING`.

- [ ] Define IDs, relationship edges, state vocabularies, source metadata, coverage semantics, and the four-state aggregation order.
- [ ] Implement validation of workbook structure, company IDs, product fact references, source independence, route-edge exclusion scope, and prohibited status values.
- [ ] Run mutation tests for each material error code and confirm the valid synthetic workspaces pass.

### Task 5: Implement controlled route-pool export

**Files:**
- Create: `plugins/industry-application-map-builder/skills/industry-application-map-builder/scripts/export_company_route_pool.py`

**Interfaces:**
- Consumes: a validated company workbook, shared-base version, and frozen input hashes.
- Produces: `company_route_pool_packet.json` with `target_skill = foreign-trade-customer-development`.

- [ ] Reject export unless validation passes.
- [ ] Export only `路线候选` and `待外部核实` records; preserve excluded, deferred, unknown, conflict, coverage, derivation, and geography hypotheses in separate arrays.
- [ ] Reject `已确认可扫描`, customer names, composite scores, and another company's identifiers.
- [ ] Run export tests and validate the emitted JSON references.

### Task 6: Write the skill workflow

**Files:**
- Modify: `plugins/industry-application-map-builder/skills/industry-application-map-builder/SKILL.md`
- Modify: `plugins/industry-application-map-builder/skills/industry-application-map-builder/agents/openai.yaml`

**Interfaces:**
- Consumes: product fact packet, shared base, declared scope, and one authorized route.
- Produces: shared-base update, company-map update, coverage review, or controlled route-pool handoff, then stops.

- [ ] Define exactly one route among `base_bootstrap`, `application_knowledge_update`, `company_map_build`, `company_map_review`, and `route_pool_handoff`.
- [ ] Require the relevant reference file for each route and preserve read-only versus mutation authorization.
- [ ] Add hard stops for missing company identity, unresolved facts, customer search, priority scoring, and salesperson-owned status.
- [ ] Run static contract tests and quick skill validation.

### Task 7: Rewire upstream and downstream contracts

**Files:**
- Modify: `plugins/company-product-knowledge-builder/skills/company-product-knowledge-builder/SKILL.md`
- Modify: `plugins/company-product-knowledge-builder/skills/company-product-knowledge-builder/references/handoff-contracts.md`
- Modify: `plugins/company-product-knowledge-builder/skills/company-product-knowledge-builder/assets/empty-company-library/04-开发交接/product-development-fact-packet.json`
- Modify: `plugins/company-product-knowledge-builder/skills/company-product-knowledge-builder/agents/openai.yaml`
- Modify: `plugins/company-product-knowledge-builder/.codex-plugin/plugin.json`
- Modify: `tests/company-product-knowledge-builder/test_library_tools.py`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/SKILL.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/research-and-sources.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/workbook-and-handoff.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/agents/openai.yaml`
- Modify: `plugins/foreign-trade-customer-development/.codex-plugin/plugin.json`
- Modify: `tests/foreign-trade-customer-development/test_direction_contract.py`
- Modify: `tests/foreign-trade-customer-development/validate_contract.py`
- Modify: `tests/foreign-trade-customer-development/validate_workbook.py`
- Modify: `tests/foreign-trade-customer-development/test_validate_workbook_mutations.py`
- Modify: `tests/foreign-trade-customer-development/fixtures/24-product-led-direction-discovery.md`
- Modify: `tests/foreign-trade-customer-development/fixtures/25-unvalidated-direction-cannot-scan.md`

**Interfaces:**
- Consumes: `product_development_fact_packet -> company_route_pool_packet`.
- Produces: customer-development direction records with stable `source_route_candidate_id` and unchanged salesperson confirmation gate.

- [ ] Change the product handoff allowed use to `internal_industry_application_mapping` and clarify that downstream route candidates remain inference, not company facts.
- [ ] Make direct product-to-industry exploration return to `industry-application-map-builder`; preserve named-company initial-check exception.
- [ ] Add `source_route_candidate_id` to the customer-development workbook and its exact bilingual header contract.
- [ ] Run both upstream and downstream regression suites.

### Task 8: Package documentation and final verification

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: the validated three-skill workflow.
- Produces: package discovery and installation documentation without performing installation.

- [ ] Add the plugin to the package list, structure, install commands, starter prompts, and foreign-trade workflow.
- [ ] Run skill quick validation, plugin validation, all unit and contract tests, all workbook validations, JSON parsing, placeholder scan, `git diff --check`, and public-safety scan.
- [ ] Render every sheet of all new or changed workbooks and fix material clipping or layout defects.
- [ ] Report `PASS`, `FAIL`, and `UNVERIFIED` truthfully; do not commit, install, or push.
