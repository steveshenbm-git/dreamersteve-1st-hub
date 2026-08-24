# RC2 Content-First Candidate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build isolated candidate plugins that make RC2 content evidence scorable without requiring platform transport metadata, while retaining strict beta.3 behavior and all downstream safety stops.

**Architecture:** Copy the two beta.3 plugin packages into distinct candidate package names, then add an opt-in content-first contract lane. The map candidate owns evidence structures and deterministic gates; the workflow candidate exposes the mode and blocks all downstream stages.

**Tech Stack:** Markdown skill contracts, JSON/YAML templates, Python 3 standard library validators/evaluators, unittest.

**Spec:** docs/superpowers/specs/2026-08-24-rc2-content-first-design.md

## Global Constraints

- Do not change the beta.3 plugin directories, installed caches, RC2-40-R2 artifacts, or shared application base.
- Treat a legacy contract without a mode field as strict-audit compatible.
- Require unchanged raw response bytes, visible input/hash, source/truth packet/hash, method arm, item scores, and unknowns for content scoring.
- Never let content-first emit beta.3 `EFFECTIVE`, authorize full scope by default, or release company, route, customer, or shared-base work.
- Do not run A/B/C, 40-case live work, or a full-node run during implementation.

### Task 1: Create isolated candidate package surfaces

**Files:**
- Create: `plugins/industry-application-map-builder-rc2-content-first/**`
- Create: `plugins/foreign-trade-workflow-director-rc2-content-first/**`
- Modify: `.agents/plugins/marketplace.json`

**Interfaces:**
- Produces candidate manifests named `industry-application-map-builder-rc2-content-first` and `foreign-trade-workflow-director-rc2-content-first`.
- Consumes beta.3 files as read-only baseline only.

- [ ] Create the two copied candidate package trees without changing their beta.3 origins.
- [ ] Add failing package-contract tests that require distinct names and candidate versions.
- [ ] Update candidate manifests, agents metadata, and marketplace entries.
- [ ] Run candidate package-contract tests.

### Task 2: Add content-first contracts and documentation

**Files:**
- Create: `plugins/industry-application-map-builder-rc2-content-first/skills/industry-application-map-builder-rc2-content-first/assets/content-first/*.json`
- Create: `plugins/industry-application-map-builder-rc2-content-first/skills/industry-application-map-builder-rc2-content-first/references/content-first-mode-contract.md`
- Create: `plugins/industry-application-map-builder-rc2-content-first/skills/industry-application-map-builder-rc2-content-first/references/compatibility-matrix.md`
- Modify: both candidate `SKILL.md` files and workflow candidate templates/references.

**Interfaces:**
- `execution_mode = strict_audit | content_first`.
- A content raw-answer envelope references immutable raw bytes and a scorecard references the envelope.
- Content state names remain separate from beta.3 validation states.

- [ ] Write failing contract tests for the required minimum evidence fields, separated platform audit field, unique status vocabulary, and downstream block.
- [ ] Add templates and references defining field ownership, stops, rollback, compatibility, and pressure cases.
- [ ] Update the two candidate skill instructions and workflow-state template.
- [ ] Run candidate contract tests.

### Task 3: Implement deterministic content-first checks

**Files:**
- Create: `plugins/industry-application-map-builder-rc2-content-first/skills/industry-application-map-builder-rc2-content-first/scripts/validate_content_first_workspace.py`
- Create: `plugins/industry-application-map-builder-rc2-content-first/skills/industry-application-map-builder-rc2-content-first/scripts/evaluate_content_first_calibration.py`
- Create: `plugins/industry-application-map-builder-rc2-content-first/skills/industry-application-map-builder-rc2-content-first/scripts/check_content_first_full_screening_gate.py`
- Create: `tests/industry-application-map-builder-content-first/test_content_first_tools.py`

**Interfaces:**
- Validator returns PASS only when each raw response is byte-hashed and paired with complete source/truth and score evidence.
- Evaluator returns only `CONTENT_CALIBRATION_PASS`, `CONTENT_CALIBRATION_FAIL`, or `CONTENT_CALIBRATION_INCOMPLETE`.
- Full-scope checker returns `NOT_AUTHORIZED` unless both content calibration and a human authorization reference pass.

- [ ] Write a failing normal-mode test proving missing platform metadata does not fail content evidence.
- [ ] Write failing incomplete, altered-raw, missing-source/truth, cross-company, and no-full-authorization tests.
- [ ] Implement the smallest validator and run the tests to green.
- [ ] Write a failing 40-case evaluator test for content pass and an identity-metadata non-gate.
- [ ] Implement the evaluator and run the tests to green.
- [ ] Write a failing full-scope-gate test, implement the checker, and run the tests to green.

### Task 4: Regression, independent consistency, and self-audit

**Files:**
- Modify: candidate tests and pressure scenarios only if a discovered failure needs a regression test.

**Interfaces:**
- Existing beta.3 test suites remain unmodified and pass from their original paths.
- Candidate tests demonstrate strict compatibility, normal content-first behavior, incomplete inputs, and adversarial boundaries.

- [ ] Run baseline beta.3 structural and tool tests from original paths.
- [ ] Run all candidate tests and skill structural validation.
- [ ] Check marketplace JSON, candidate manifest names/versions, and no diff in beta.3/cache/RC2-40-R2.
- [ ] Inspect the strongest counterexamples: style-only score, missing raw bytes, no full authorization, and downstream-release attempt.
- [ ] Record the exact verification layer and remaining live-evidence limit.
