# Customer Development Integration Hardening Implementation Plan

> **For agentic workers:** Execute inline with RED-GREEN-REFACTOR. The user authorized source edits only; do not commit, install, or modify plugin cache.

**Goal:** Connect the company product knowledge, industry application map, and customer development skills through deterministic, traceable, stale-aware handoff contracts.

**Architecture:** Persist the technical product fact packet, generate the commercial readiness view on demand, register every exported route-pool packet in a producer-owned registry, and add a customer-development route-review stage before direction compilation. Keep technical route state, research readiness, commercial readiness, and salesperson decisions separate.

**Tech Stack:** Markdown skill contracts, Python 3 standard library, JSON, `unittest`, `@oai/artifact-tool`, XLSX templates.

## Global Constraints

- Edit only `/Users/lirongjing/Documents/传统外贸/github/dreamersteve-1st-hub`.
- Preserve all pre-existing staged and unstaged changes.
- Do not edit `~/.codex/plugins/cache/`, commit, push, install, or reinstall.
- Keep one company per knowledge and map root; never mix `company_id` values.
- Only approved E3 `own_company` facts may enter confirmed technical or commercial outputs.
- Do not turn geography hypotheses into country priority, route evidence into customer facts, or commercial unknowns into blockers.
- The salesperson owns route selection, market priority, customer selection, commercial judgment, and external communication.

---

### Task 1: Product fact packet and readiness view

**Files:**

- Create: `plugins/company-product-knowledge-builder/skills/company-product-knowledge-builder/scripts/export_product_development_fact_packet.py`
- Create: `plugins/company-product-knowledge-builder/skills/company-product-knowledge-builder/scripts/export_development_readiness_view.py`
- Modify: `plugins/company-product-knowledge-builder/skills/company-product-knowledge-builder/scripts/validate_company_library.py`
- Modify: product packet template, `SKILL.md`, handoff/schema/pressure references, agent metadata
- Test: `tests/company-product-knowledge-builder/test_library_tools.py`

**Interfaces:**

- `export_product_development_fact_packet.py <library> --product-family-id <id> [--output <path>]`
- `export_development_readiness_view.py <library> --request <json> [--output <path>] [--include-e2-annex]`
- Produces `product_development_fact_packet` schema `1.2` and `development_readiness_view` schema `1.0`.

- [x] Write tests for deterministic E3 selection, snapshot hashes, E2 exclusion, stale commercial facts, hard conflicts, conditional/unknown states, type safety, and cross-company rejection.
- [x] Run the tests and confirm the missing exporters/contracts fail.
- [x] Implement the two exporters and validation rules.
- [x] Run product-builder tests and refactor without changing behavior.

### Task 2: Route-pool producer registry

**Files:**

- Create at company-map initialization: `04-公司地图/<company_id>/route-pool-export-registry.json`
- Modify: map initializer, validator, exporter, `SKILL.md`, handoff/workspace/pressure references
- Test: `tests/industry-application-map-builder/test_workspace_tools.py`

**Interfaces:**

- Route packet carries `export_id` and `producer_registry_reference`.
- Producer registry records packet path, SHA-256, input snapshot, validator version, validation date, state, and invalidation reason.

- [x] Write tests for registry creation, packet-hash registration, tampering, missing registration, stale status, copied paths, cross-company references, and source-map changes after export.
- [x] Run the tests and confirm they fail for the missing registry behavior.
- [x] Implement export registration and validation.
- [x] Run map-builder tests and refactor while green.

### Task 3: Route review, direction compilation, and workbook

**Files:**

- Modify: customer-development `SKILL.md`, research/workbook references, agent metadata
- Modify: `assets/prospect-development-workbook.xlsx`
- Modify: customer-development contract and workbook validators/tests
- Add pressure fixtures for route tampering, readiness unknown/conflict, named-company exception, and salesperson decision ownership

**Interfaces:**

- Add `route_portfolio_review`.
- Add canonical `direction_compilation`; keep `direction_discovery` as a compatibility alias.
- Add `路线评审` sheet and `开发方向.source_route_review_id`.
- Return `next_owner` for map defects, product-readiness gaps, or salesperson decisions.

- [x] Write failing static and workbook-contract tests.
- [x] Run tests and confirm missing routes, fields, validations, and sheets fail.
- [x] Update the skill contracts and workbook template with `@oai/artifact-tool`.
- [x] Reopen, inspect, render, and validate every sheet.
- [x] Run customer-development tests and refactor while green.

### Task 4: End-to-end acceptance and falsification

**Files:**

- Add only the smallest synthetic integration fixture required under the existing three test roots.

- [x] Initialize a synthetic company library and export a technical fact packet.
- [x] Build a synthetic company map and export a registered route-pool packet.
- [x] Verify customer preflight accepts the intact packet and rejects tampered, copied, cross-company, stale, or source-map-stale packets.
- [x] Generate readiness states for current, conditional, unknown, and confirmed-conflict inputs.
- [x] Validate the updated workbook and run all three plugin test suites.
- [x] Inspect the final diff for company contamination, duplicated rules, cache writes, placeholders, and unauthorized commit/install changes.

## Authorization stop

Stop after source validation. Report `PASS / FAIL / UNVERIFIED`. Do not commit or install without separate explicit authorization.
