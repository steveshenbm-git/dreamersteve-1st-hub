# Foreign Trade Customer Development Final Review Remediation Plan

> **Execution rule:** Use fresh independent implementers and reviewers task by task. Add RED evidence before production repairs. Do not install, push, create a pull request, publish, or rewrite Git history.

**Goal:** Close the five Important issues found by the fresh whole-branch review while preserving the approved plugin boundary, salesperson authority, empty public workbook, and historical raw outputs.

## Global constraints

- Full due diligence requires both `salesperson_classification = 潜力客户` and an explicit salesperson start instruction.
- Received customer replies belong to `foreign-trade-email-assistant`; this skill only prepares pre-reply prospect-development outreach.
- The 10-natural-day cadence applies only to salesperson-confirmed potential customers after the initial sequence, uses the actual regular-touch send as its anchor, shifts weekend dates forward, and does not reset on an additional event touch.
- Every controlled workbook field must use an exact list validation beginning at row 3 with a stop-style error alert enabled.
- Existing raw pressure-test outputs remain immutable.
- The current 30-commit history is not authorized for public publication. Publication requires a separately approved clean squashed/rebased history and a scan of every commit intended for release.

---

### Task 16: Add RED gate, routing, cadence, and workbook-enforcement tests

**Files:**
- Modify: `tests/foreign-trade-customer-development/validate_contract.py`
- Modify: `tests/foreign-trade-customer-development/validate_workbook.py`
- Create: `tests/foreign-trade-customer-development/test_validate_workbook_mutations.py`
- Create: `tests/foreign-trade-customer-development/fixtures/14-ordinary-candidate-full-dd-gate.md`
- Create: `tests/foreign-trade-customer-development/fixtures/15-received-email-routing.md`
- Create: `tests/foreign-trade-customer-development/fixtures/16-ten-day-cadence-weekend-event.md`
- Modify: `tests/foreign-trade-customer-development/scorecard.md`
- Create: `tests/foreign-trade-customer-development/results/final-review-red-summary.md`
- Create: `tests/foreign-trade-customer-development/results/raw/final-review-red/*.md`

**Requirements:**

1. Add static assertions for the dual full-DD gate and the pre-reply/email-assistant routing exclusion.
2. Define exact controlled-value mappings for every workbook validation. Validate exact range, exact list values, `type=list`, and enabled stop-style error enforcement.
3. Add mutation tests proving a bad non-risk list and a disabled error alert are rejected.
4. Run fixtures 14–16 in fresh isolated contexts with only the fixture, GREEN prompt, and plugin source; save raw before scoring.
5. Confirm RED comes from the four reviewed gaps, not syntax/import failures.
6. Commit: `建立客户开发最终审查回归测试`.

---

### Task 17: Repair the potential-customer gate, routing, and cadence contracts

**Files:**
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/SKILL.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/research-and-sources.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/opportunity-and-outreach.md`

**Requirements:**

1. Require potential-customer classification plus explicit start before full DD; an ordinary selected candidate remains at candidate scan.
2. Limit the skill description to pre-reply/unanswered prospect development and explicitly route received-email analysis/drafting to `foreign-trade-email-assistant`.
3. State the 10-day anchor transition and weekend/event rules in directly executable terms.
4. Run static contract GREEN and fresh behavior tests for fixtures 14–16. Preserve RED raw and save GREEN raw before scoring.
5. Commit: `收紧客户背调门槛与邮件路由`.

---

### Task 18: Enforce and fully validate all workbook controlled lists

**Files:**
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/workbook-and-handoff.md`
- Verify: `tests/foreign-trade-customer-development/validate_workbook.py`
- Verify: `tests/foreign-trade-customer-development/test_validate_workbook_mutations.py`

**Requirements:**

1. Use `spreadsheets:Spreadsheets` and `@oai/artifact-tool` for authoring. Do not use openpyxl to author workbook content.
2. Enable stop-style invalid-value blocking for all 13 controlled validations, keep exact lists/ranges, row 1/2, `A3`, row-2 filters, nine sheets, and the empty-data boundary.
3. If artifact-tool cannot persist only an enforcement property, stop and report the exact blocker; do not expand the prior pane/filter OOXML exception without explicit controller authorization.
4. Run workbook validator, both mutation counterexamples, ZIP integrity, artifact-tool reopen/inspect/error scan, and visual inspection of all nine sheets.
5. Commit: `强制客户开发工作簿受控值`.

---

### Task 19: Add clean-history publication gate and correct specification status

**Files:**
- Modify: `PUBLIC_RELEASE_CHECKLIST.md`
- Modify: `docs/superpowers/specs/2026-07-23-foreign-trade-customer-development-design.md`

**Requirements:**

1. Change the specification status to reflect the user's completed approval.
2. State that the final-tree scan is insufficient for an unsquashed history. Before public push, create a separately approved clean release history, inspect every commit intended for publication, and scan both commit contents and final tree.
3. Do not rewrite the current branch history in this task.
4. Commit: `补充客户开发公开历史门槛`.

---

### Task 20: Repeat final verification and whole-branch review

1. Run all JSON, official skill/plugin, contract, workbook, mutation, behavior, ZIP, whitespace, path, credential, and status checks.
2. Use fresh acceptance and falsification auditors for the repaired axes.
3. Obtain a fresh whole-branch review. Fix all Critical and Important issues and re-review.
4. Keep installed runtime behavior, real logged-in sources, production workbook use, long-term business outcomes, and public-history cleanup `UNVERIFIED` unless separately executed.
5. Stop before install, push, PR, publication, merge, or history rewrite.
