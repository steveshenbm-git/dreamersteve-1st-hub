# Foreign Trade Development and Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add product-led direction discovery to customer development and create a separate, salesperson-controlled customer-operations-and-communication plugin that owns every external communication draft from the first cold email onward.

**Architecture:** `foreign-trade-customer-development` owns local-product-bound direction discovery, direction validation, candidate scans, and evidence-backed development packets. A new `foreign-trade-customer-operations` plugin owns cold outreach, unanswered follow-up, reply communication, and account operation after an explicit outreach handoff. A future local scheduled job may create drafts and review tasks at 10:00 Asia/Shanghai on workdays; it must not be installed or activated until a named workbook and standing draft-write authorization exist.

**Tech Stack:** Markdown Codex skills, JSON plugin manifests, Python contract/workbook validators, `openpyxl` 3.1.5, local Codex cron automation (deferred activation).

## Global Constraints

- Edit only this repository's `ft-customer-dev` source tree; never modify `~/.codex/plugins/cache/`.
- Preserve existing uncommitted candidate-pool changes and do not commit, push, install, or create a live automation in this implementation.
- The salesperson owns target selection, priority, commercial judgment, final wording, channel, sending, restricted-contact approval, and status decisions.
- No skill sends messages, performs automatic market scans, ranks candidate companies, or turns inference into customer facts.
- Candidate scans return every qualified company in the declared scope, with no fixed cap, only when company/brand-specific direct product evidence meets the existing gate.
- Company facts, customer records, contacts, actual workbook data, and automation configuration remain local; no private data enters a public plugin.
- A draft is never an actual sent message. Automated writing is limited to a named workbook's draft fields under a future explicit standing authorization.

---

### Task 1: Add failing behavior contracts for the new boundaries

**Files:**
- Create: `tests/foreign-trade-customer-development/fixtures/24-product-led-direction-discovery.md`
- Create: `tests/foreign-trade-customer-development/fixtures/25-unvalidated-direction-cannot-scan.md`
- Create: `tests/foreign-trade-customer-operations/fixtures/01-cold-outreach-handoff.md`
- Create: `tests/foreign-trade-customer-operations/fixtures/02-due-draft-no-send.md`
- Create: `tests/foreign-trade-customer-operations/fixtures/03-reply-switches-route.md`
- Create: `tests/foreign-trade-customer-operations/scorecard.md`
- Create: `tests/foreign-trade-customer-operations/validate_contract.py`
- Modify: `tests/foreign-trade-customer-development/scorecard.md`
- Modify: `tests/foreign-trade-customer-development/validate_contract.py`

**Interfaces:**
- Consumes: existing candidate evidence and salesperson-authority contracts.
- Produces: RED scenarios for `direction_discovery`, `direction_validation`, `outreach_handoff`, `cold_outreach`, and `reply_communication`.

- [ ] **Step 1: Write failing direction-discovery contract tests**

Require `direction_discovery` to emit an internal-product boundary, a testable enterprise rule, exclusions, evidence posture, and a salesperson decision gate. Require `direction_validation` to stop at validation and prohibit candidate scanning before `direction_status = 已确认可扫描`.

- [ ] **Step 2: Run the development validator to verify RED**

Run: `python3 tests/foreign-trade-customer-development/validate_contract.py`

Expected: FAIL because the current skill still requires a salesperson-confirmed market theme and has no direction routes.

- [ ] **Step 3: Write failing operations contracts**

Require a selected prospect plus explicit outreach request to be accepted as `outreach_handoff`; require cold email and follow-up drafts to remain drafts; require a received or suspected reply to switch to `reply_communication` and stop new cold-outreach drafts.

- [ ] **Step 4: Run the operations validator to verify RED**

Run: `python3 tests/foreign-trade-customer-operations/validate_contract.py`

Expected: FAIL because the operations plugin does not exist.

### Task 2: Add direction discovery to customer development

**Files:**
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/SKILL.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/research-and-sources.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/opportunity-and-outreach.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/workbook-and-handoff.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/agents/openai.yaml`
- Modify: `plugins/foreign-trade-customer-development/.codex-plugin/plugin.json`
- Modify: `tests/foreign-trade-customer-development/validate_contract.py`

**Interfaces:**
- Consumes: local approved product facts and salesperson-declared source scope.
- Produces: `development_direction_packet`, `direction_validation_packet`, and `outreach_handoff_packet`.

- [ ] **Step 1: Implement three explicit routes**

Add `direction_discovery`, `direction_validation`, and `outreach_handoff`. Keep `candidate_scan` and `full_due_diligence`; remove first-email writing and all unanswered outreach cadence from this skill.

- [ ] **Step 2: Define the direction packet as a testable rule, not an industry claim**

Require: approved product reference; product boundary; observable enterprise rule; company-level direct-evidence rule for later scanning; exclusion boundary; unresolved conditions; external evidence posture; declared scope; and one salesperson decision: `确认可扫描`, `继续核实`, `暂缓`, or `淘汰`.

- [ ] **Step 3: Add direction records to the shared workbook contract**

Add `开发方向` and `方向证据` sheets, their paired Chinese second-row descriptions, controlled direction states, and optional `source_direction_id` on customers. Preserve all existing data and authority fields.

- [ ] **Step 4: Restrict the development-to-operations handoff**

Define `outreach_handoff_packet` with a customer identity, direct-fit evidence, approved product references, allowed claims, prohibited claims, contact evidence and permission, outreach scope (`limited` or `complete`), existing actual-send facts, risk status, open questions, and the salesperson's explicit request. No email body is produced here.

- [ ] **Step 5: Run development contracts and workbook validation**

Run the repository validator and the bundled-runtime workbook validator. Expected: all existing and new development contracts pass; workbook layout, data validation, and second-row labels pass.

### Task 3: Create the customer-operations-and-communication plugin

**Files:**
- Create: `plugins/foreign-trade-customer-operations/.codex-plugin/plugin.json`
- Create: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/SKILL.md`
- Create: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/agents/openai.yaml`
- Create: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/references/routing-and-account-state.md`
- Create: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/references/cold-outreach-and-follow-up.md`
- Create: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/references/reply-communication.md`
- Create: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/references/reply-evidence-and-contract.md`
- Create: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/references/special-handling.md`
- Create: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/references/workbook-and-automation.md`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `tests/foreign-trade-customer-operations/validate_contract.py`

**Interfaces:**
- Consumes: `outreach_handoff_packet`, complete email threads, actual-send/actual-reply records, and a user-designated shared workbook.
- Produces: `cold_outreach_draft`, `follow_up_draft`, `reply_draft`, `account_operation_packet`, `draft_write_packet`, and `automation_review_packet`.

- [ ] **Step 1: Create the minimal plugin and main router**

The router must select exactly one route: `cold_outreach`, `unanswered_follow_up`, `reply_communication`, or `account_operation`. It must stop research, product selection, and priority judgment; missing packet facts return a bounded request to customer development.

- [ ] **Step 2: Move communication behavior into route-specific references**

Implement first email, fifth-working-day follow-up, seventh-working-day follow-up, approved alternate-channel rules, return email, potential-customer 10-day cadence, and reply hard-stop under the operations plugin. Keep reply drafts bilingual and preserve the existing quality/contract/payment special-handling boundary.

- [ ] **Step 3: Add draft-only record handling**

Require `draft_content_or_local_reference`, `draft_generated_at`, `draft_for_touch_stage`, and `automation_run_id` for generated drafts. Keep `actual_sent_at`, `response_at`, and actual-content references empty until supplied as actual facts.

- [ ] **Step 4: Update marketplace entry**

Register `foreign-trade-customer-operations` as available. Preserve the standalone email-assistant behavior, but label its source metadata as an optional compatibility entry and prohibit running both skills on the same reply. Do not edit an installed cache or remove the legacy plugin in this task.

- [ ] **Step 5: Run operations contracts to GREEN**

Run: `python3 tests/foreign-trade-customer-operations/validate_contract.py`

Expected: PASS for cold first touch, no-send draft state, reply-route switch, salesperson authority, and missing-packet return.

### Task 4: Add a local-only scheduling eligibility core without activating it

**Files:**
- Create: `tools/foreign_trade_due_draft.py`
- Create: `tools/foreign_trade_automation_config.example.json`
- Create: `tests/foreign-trade-customer-operations/test_due_draft.py`
- Modify: `plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/references/workbook-and-automation.md`

**Interfaces:**
- Consumes: a named local workbook, a local-only configuration file, Asia/Shanghai clock, and existing touch/risk/reply fields.
- Produces: an idempotent due-review packet and blocked-record reasons; never writes the workbook, generates model text, sends messages, or creates live Codex automation.

- [ ] **Step 1: Write failing scheduler tests**

Cover a due follow-up, a weekend-adjusted 10-day touch, a reply hard-stop, a risk pause, an existing unreviewed draft, and a missed 10:00 catch-up run. Assert the same customer/stage/due date is emitted once only.

- [ ] **Step 2: Implement deterministic due-record selection**

Use only actual timestamps and existing controlled states. Treat Monday-Friday 10:00 Asia/Shanghai as the default schedule; include overdue eligible records on the next successful run. Skip configured holidays only when an explicit local holiday list is supplied.

- [ ] **Step 3: Define the future safe-write boundary without implementing a writer**

Document the required workbook normalization, stable IDs, allowed draft fields, re-open verification, and authorization gates. The current helper stops at a review packet. A future writer must refuse work when a reply, risk pause, stop condition, schema mismatch, duplicate draft, missing named workbook, or missing standing authorization exists.

- [ ] **Step 4: Run scheduler tests with the bundled Python runtime**

Run the new tests with `/Users/lirongjing/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.

### Task 5: Cross-plugin verification and review

**Files:**
- Modify: `README.md`
- Modify: `tests/foreign-trade-customer-development/scorecard.md`
- Modify: `tests/foreign-trade-customer-operations/scorecard.md`

- [ ] **Step 1: Run all static validators and workbook checks**

Run both contract validators, both workbook validations, scheduler tests, plugin JSON parsing, and `git diff --check`.

- [ ] **Step 2: Run pressure fixtures manually in fresh contexts**

Test product-led direction discovery, insufficient external validation, direct-evidence candidate inclusion, limited ordinary-candidate handoff, unattended due-draft generation, no-send discipline, and reply hard-stop.

- [ ] **Step 3: Report source-only completion**

Report changed files, test outputs, remaining unverified UI behavior for Codex notifications, and the still-required later approvals for commit, installation, named-workbook standing authorization, and live 10:00 automation activation.
