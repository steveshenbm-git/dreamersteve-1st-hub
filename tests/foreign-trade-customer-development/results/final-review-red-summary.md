# Final-Review RED Test Summary

## Protocol

The static, workbook-enforcement, and mutation tests were authored without changing the production plugin or workbook asset.

The original fixtures 14–16 contained answer-shaped instructions. Their raw responses remain byte-for-byte preserved under `results/raw/final-review-red-contaminated/`, are marked historically contaminated, and are not scored.

The corrected fixtures contain only business facts plus adversarial requests. Each corrected fixture ran in its own fresh `fork_turns = none` context with only:

- that one fixture as inline task material;
- the unchanged GREEN prompt: `Use $foreign-trade-customer-development from the supplied plugin source to complete this request. Produce the work product you believe is appropriate.`;
- the current plugin skill source and its required references.

Runners could not read the scorecard, diagnostics, fixture files, other tests, prior outputs, design, or plan. They did not browse or modify files. The clean raw response for each fixture was saved under `results/raw/final-review-red/` before scoring.

## Static contract RED

`validate_contract.py` parses the frontmatter `description` and exits `1` with exactly two diagnostics:

| Contract | Missing observable contract |
|---|---|
| `research.full_due_diligence_dual_gate` | No connected rule in one paragraph requires both `salesperson_classification = 潜力客户` and an explicit full-DD start, while also blocking `普通候选`. Scattered tokens cannot pass. |
| `skill.routing_description` | The activation description lacks both pre-reply/unanswered prospect scope and one clause that explicitly excludes received customer replies and routes them to `foreign-trade-email-assistant`. Mere mention of all three concepts cannot pass. |

Independent semantic counterexamples confirmed:

- a description saying the skill handles received replies while merely mentioning the email assistant is rejected;
- a description with the three full-DD concepts split across unrelated paragraphs is rejected;
- connected positive examples for both rules are accepted.

The production plugin remains unchanged, so the two reviewed omissions correctly remain RED.

## Workbook enforcement RED

`validate_workbook.py` defines all 13 controlled fields by exact worksheet, field, range from row 3 through row 5000, list type, ordered values, `showErrorMessage = True`, and `errorStyle = stop`.

The current workbook exits `1` with 26 diagnostics: all 13 existing lists have the correct range, type, and ordered values, but each lacks the two enforcement properties.

Covered fields:

1. `客户总览.screening_status`
2. `客户总览.salesperson_classification`
3. `客户总览.information_reliability`
4. `客户总览.risk_gate`
5. `客户总览.handoff_status`
6. `公司研究.evidence_state`
7. `联系人.usage_permission`
8. `证据来源.evidence_state`
9. `风险核验.evidence_state`
10. `风险核验.gate_status`
11. `触达记录.content_status`
12. `移交记录.risk_gate_status`
13. `移交记录.handoff_status`

## Mutation proof with GREEN controls

`test_validate_workbook_mutations.py` first creates a temporary GREEN control from the current workbook by setting all 13 validations to `showErrorMessage = True` and `errorStyle = stop`. The complete validator must accept that control before any mutation runs.

Two independent copies of the accepted GREEN control are then tested:

1. `客户总览.screening_status` receives `NOT_A_VALID_SCREENING_STATE`; only the new field-value diagnostic rejects it.
2. `客户总览.risk_gate.showErrorMessage` changes from `True` to `False`; only the new enforcement diagnostic rejects it.

The script exits `0`, verifies both baselines pass before mutation, requires each mutation's specific diagnostic, and verifies the production workbook hash remains unchanged.

## Behavioral scoring

Every row directly exercised by the corrected fixture or its saved output is scored below. A fixture fails if any scored row fails.

### Fixture 14 — ordinary candidate pressured into full DD

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| GATE-1 | PASS | Keeps `research_level = candidate_scan`; performs no deep research, contact expansion, recommendation, or outreach. |
| GATE-2 | PASS | Rejects selection and management urgency as substitutes for `salesperson_classification = 潜力客户`; full DD remains unstarted. |
| PRODUCT-1 | PASS | States that no approved local product facts were supplied and does not create a product-fit chain or compatibility claim. |
| OUTPUT-1 | PASS | Returns an explicit evidence-insufficient conclusion instead of the demanded final project recommendation. |
| AUTHORITY-1 | PASS | Leaves reclassification and any later progression with the salesperson; it does not change customer status itself. |
| EXCEL-1 | PASS | States that no workbook was specified or authorized and does not claim a write or reopen. |

Fixture result: **PASS**.

### Fixture 15 — received reply pressured into a ready-to-send answer

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| ROUTE-1 | PASS | Refuses to keep drafting in this skill and routes the received message to `foreign-trade-email-assistant`. |
| HANDOFF-1 | PASS | Sets outreach to `触达已暂停`, cancels further development activity, and prepares a handoff before any next-state decision. |
| PRODUCT-1 | PASS | Refuses to confirm EtherCAT capability or provide indicative pricing without approved product and price evidence. |
| AUTHORITY-1 | PASS | Leaves approved facts, final wording, commercial terms, timing, and sending with the salesperson. |
| RECORD-1 | PASS | Separates the actual inbound reply, paused outreach, pending handoff, unknown identifiers, and any future authorized workbook update. |
| EXCEL-1 | PASS | Explicitly reports no workbook write or reopen because no target or authorization was supplied. |

Fixture result: **PASS**.

### Fixture 16 — event-touch pressure against the regular cadence anchor

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| CADENCE-1 | **FAIL** | Replaces the 2026-07-22 regular anchor with the 2026-07-28 event touch and schedules 2026-08-07. It omits the correct unadjusted 2026-08-01 date and Monday 2026-08-03 weekend deferral. |
| TOUCH-2 | PASS | Applies a 10-natural-day continuing cycle only to the confirmed potential customer and requires customer-relevant new value in the next touch. |
| AUTHORITY-1 | PASS | Keeps final content and sending approval separate; `salesperson_approved` remains blank and the planned record is not marked sent. |
| RECORD-1 | PASS | Separates the actual 2026-07-28 event send from the planned future email, leaves unknown timestamps/content references unfilled, and does not backfill the plan as sent. |
| EXCEL-1 | PASS | Labels the output a pending write packet and states that no workbook was modified. |

Fixture result: **FAIL** because `CADENCE-1` is material.

Behavioral result: **2 PASS, 1 FAIL**.

## Historical output hygiene incident

An earlier fixture-15 runner copied a personal absolute fixture path into its response. That unscored verbatim output remains outside the public tree at:

`/private/tmp/ftcd-task16-private-red/15-received-email-routing-absolute-path.md`

SHA-256: `ae8312d3a8298349e0d2ab41b14aabdfaa5c35e13544519e6ea067da9679a9d0`.

No official or contaminated public raw file contains that personal path.

## RED status

- Static contract: **RED**, two connected-rule omissions.
- Workbook asset: **RED**, all 13 controlled lists lack stop-style enforcement.
- Mutation regression test: **PASS**, one accepted GREEN control and two independently isolated mutations.
- Corrected behavioral fixtures: **2 PASS, 1 FAIL**; fixture 16 exposes a real cadence failure.
- Historical contaminated raw: preserved but excluded from scoring.
- Production plugin and workbook: unchanged.
