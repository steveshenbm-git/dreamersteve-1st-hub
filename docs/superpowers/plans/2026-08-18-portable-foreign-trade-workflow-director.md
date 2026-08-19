# Portable Foreign-Trade Workflow Director Implementation Plan

> **Design:** `docs/superpowers/specs/2026-08-18-portable-foreign-trade-workflow-director-design.md`
>
> **Execution boundary:** Modify and verify source on `ft-customer-dev`. Do not commit, push, reinstall the plugin, edit business workbooks, or transfer company data in this stage.

## Goal

Turn `foreign-trade-workflow-director` from a six-sheet single-salesperson front door into a portable full-workflow controller and replication guide while retaining the existing workbench as a downstream business interface.

## Task 1: Encode the missing architecture as failing tests

**Files**

- Modify: `tests/foreign-trade-workflow-director/test_contract.py`
- Modify: `tests/foreign-trade-workflow-director/pressure-prompts.md`
- Modify: `tests/foreign-trade-workflow-director/scorecard.md`

**Steps**

1. Replace the single-front-door contract with checks for `portable_workflow_blueprint_beta`.
2. Require the eleven ordered stages, the first-incomplete-stage rule, bootstrap/resume/audit/replication routes, and the three portable artifact contracts.
3. Separate the company foundation from recurring route, direction, and customer-thread work units.
4. Add pressure cases for incomplete industry semantics, a blank second company, cross-company contamination, another account with missing dependencies, and repeated business instances.
5. Run only the workflow-director contract test and confirm it fails against the current skill for the intended missing requirements.

**RED command**

```bash
python3 -m unittest tests/foreign-trade-workflow-director/test_contract.py
```

## Task 2: Add the portable workflow blueprint

**Files**

- Create: `plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/references/workflow-blueprint.md`
- Create: `plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/assets/company-workflow-state.template.yaml`
- Create: `plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/assets/workflow-replication-manifest.template.yaml`
- Modify: `plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/references/workflow-and-packet-contracts.md`

**Steps**

1. Define the ordered stage graph, owners, required inputs/outputs, acceptance gates, STOP conditions, and stale rollback targets.
2. Define `workflow_blueprint`, `company_workflow_state`, and `workflow_replication_manifest` with explicit company-data isolation.
3. Extend packet contracts so framework audit/bootstrap/resume/replication results are traceable while preserving existing specialist and workbench packets.
4. Make cross-account installation and data transfer separate authorization gates.

## Task 3: Rewrite the director routing contract

**Files**

- Modify: `plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/SKILL.md`
- Modify: `plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/agents/openai.yaml`

**Steps**

1. Change the core role to `portable_workflow_blueprint_beta`.
2. Make `framework_audit`, `company_framework_bootstrap`, `framework_resume`, `specialist_handoff`, `framework_replication_plan`, and `business_decision_record` the explicit routes.
3. Require actual artifact inspection and route only to the earliest incomplete or stale stage.
4. Retain the six-sheet workbench as the downstream salesperson interface, not the framework source of truth.
5. Preserve specialist ownership, human decisions, single-editor writing, and no-send boundaries.

## Task 4: Update plugin-facing metadata and documentation

**Files**

- Modify: `plugins/foreign-trade-workflow-director/.codex-plugin/plugin.json`
- Modify: `README.md`
- Modify: `CHANGELOG.md`

**Steps**

1. Bump the Beta patch version and describe the portable controller/replicator role accurately.
2. Update discovery text and example prompt so a user can start with a new company, resume an existing framework, or prepare a replication audit.
3. Record that live second-company and cross-account validation remain unverified.

## Task 5: Verify the changed skill and guard against regression

**Files**

- Verify: all files above
- Verify: `tests/foreign-trade-workflow-director/validate_workbook.py`
- Verify: specialist plugin contract tests

**Steps**

1. Run the workflow-director contract test and confirm GREEN.
2. Validate the existing six-sheet workbook so the downstream interface is not broken.
3. Run the company-product, industry-map, customer-development, and customer-operations contract tests.
4. Search the changed skill for stale claims that it is only a single-salesperson front door.
5. Review the diff for scope creep, company-specific data, installation claims, or unsupported live-effectiveness claims.
6. Report source changes as locally verified only. Wait for separate authorization before commit, reinstall, push, or live cross-account testing.

**Verification commands**

```bash
python3 -m unittest tests/foreign-trade-workflow-director/test_contract.py
python3 tests/foreign-trade-workflow-director/validate_workbook.py
python3 -m unittest discover -s tests/company-product-knowledge-builder -p 'test*.py'
python3 -m unittest discover -s tests/industry-application-map-builder -p 'test*.py'
python3 -m unittest discover -s tests/foreign-trade-customer-development -p 'test*.py'
python3 -m unittest discover -s tests/foreign-trade-customer-operations -p 'test*.py'
git diff --check
```

Use the workspace-bundled Python for the industry-map and customer-development suites when the system Python does not provide `openpyxl`.
