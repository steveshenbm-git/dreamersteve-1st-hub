# Foreign-Trade Shared Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development and superpowers:writing-skills. Execute inline; this task does not authorize subagent implementation or Git commits.

**Goal:** Prepare a versioned, testable four-plugin candidate set with complete marketplace discovery and one bound cross-skill handoff envelope.

**Architecture:** The workflow director owns one small deterministic envelope validator and the canonical schema. Specialist payloads remain separate. Industry returns the controller's current semantic packet; development and operations share the same envelope binding while retaining their existing responsibilities.

**Tech Stack:** Markdown skill contracts, JSON plugin manifests, Python `unittest`, one Python standard-library validator.

**Spec:** `docs/superpowers/specs/2026-08-31-foreign-trade-shared-contracts-design.md`

## Global Constraints

- Do not edit installed caches or company data.
- Do not install, publish, push, freeze, or send.
- Do not commit; Git commit is separately authorized.
- Keep `RESEARCH_ONLY_BLOCKED` and all salesperson decision gates.
- Existing beta.5 industry testing remains on its current baseline.

---

### Task 1: Cross-plugin RED tests

**Files:**
- Create: `tests/foreign-trade-shared-contracts/test_shared_contracts.py`

**Interfaces:**
- Consumes: current marketplace, manifests, semantic and customer handoff references.
- Produces: failing assertions for the candidate version set, complete marketplace, schema alignment, and executable envelope validation.

- [ ] Write tests with literal expected versions and failure reason codes.
- [ ] Run the new suite and confirm failures are caused by the missing candidate behavior.

### Task 2: Canonical envelope validator

**Files:**
- Create: `plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/scripts/validate_handoff_envelope.py`
- Modify: `plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/references/workflow-and-packet-contracts.md`

**Interfaces:**
- Consumes: envelope JSON, payload JSON, expected company/target, and the required receiver-owned accepted-ID registry.
- Produces: JSON `PASS` or `FAIL` with stable reason codes; performs no writes.

- [ ] Implement only the behavior required by the failing tests.
- [ ] Run envelope tests until valid input passes and every adverse case fails for its named reason.

### Task 3: Industry semantic return and candidate versions

**Files:**
- Modify: the four `.codex-plugin/plugin.json` manifests and matching UI/version references.
- Modify: industry `handoff-contracts.md`, compatibility references, R4 version bindings, and affected tests.
- Modify: director blueprint version, state templates, and semantic contract references.

**Interfaces:**
- Consumes: controller `semantic_specialist_return_packet` schema.
- Produces: the identical content-first/strict-audit return fields from industry.

- [ ] Update the minimum version and contract fields.
- [ ] Run industry and director targeted tests until green.

### Task 4: Development-to-operations binding

**Files:**
- Modify: customer-development `SKILL.md`, `opportunity-and-outreach.md`, and `workbook-and-handoff.md`.
- Modify: customer-operations `SKILL.md` and `routing-and-account-state.md`.
- Add or modify the matching contract tests.

**Interfaces:**
- Consumes: `handoff_envelope_v1` plus `outreach_handoff_packet` or `customer_operations_handoff`.
- Produces: exact receiver acceptance and rejection behavior without drafting or sending in development.

- [ ] Add `company_id`, envelope ownership, and receiver rejection rules.
- [ ] Run customer-development and customer-operations tests until green.

### Task 5: Marketplace and independent validation lanes

**Files:**
- Modify: `.agents/plugins/marketplace.json`, `README.md`, and compatibility documentation.
- Add: concise specialist optimization-validation references where absent.

**Interfaces:**
- Consumes: exact candidate plugin set.
- Produces: complete structural discovery and three separate evaluation contracts; no effectiveness claim.

- [ ] Register the required plugins and document all install commands without executing them.
- [ ] State separate critical gates and verdict ownership for each specialist.
- [ ] Run marketplace and integration tests.

### Task 6: Full verification and stop

**Files:**
- Verify all changed files and tests; do not modify active installation state.

**Interfaces:**
- Consumes: complete candidate diff.
- Produces: verification report, remaining `UNVERIFIED` installation layer, and rollback path.

- [ ] Run all four plugin suites and the shared-contract suite.
- [ ] Run static validators and JSON/YAML parsing checks.
- [ ] Inspect `git diff --check`, `git status`, version consistency, and prohibited-action text.
- [ ] Stop for user review without commit or installation.
