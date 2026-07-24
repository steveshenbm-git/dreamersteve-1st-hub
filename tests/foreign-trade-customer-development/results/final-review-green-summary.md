# Final-Review GREEN Summary

## Protocol

The production skill was changed only after the reviewed RED artifacts existed. The original RED raw files remain unchanged.

Each GREEN behavior run used a fresh `fork_turns = none` runner. Its prompt contained only the unchanged GREEN instruction, one inline fictional business fixture, and permission to read the current plugin skill plus the references that skill explicitly requires. Runners were prohibited from reading fixtures, validators, scorecards, summaries, prior outputs, plans, git history, or other repository files. They did not browse or modify files.

For every run, the runner's final work product was saved under `results/raw/final-review-green/` before any scorecard assessment. Initial GREEN-run failures were preserved; a failure led to a minimal production-contract change and a new fictional fresh-context variant rather than editing the raw output.

## Static contract

Before production changes, `validate_contract.py` exited `1` with exactly the two expected diagnostics:

- `research.full_due_diligence_dual_gate`
- `skill.routing_description`

After the changes it exits `0`:

```text
PASS: all specification-traceability contracts are present
```

The final contract includes the canonical full-DD dual gate, the canonical pre-reply/unanswered routing description, and an executable cadence state/output contract.

## Behavioral scoring

### Fixture 14 — original clean fixture

Raw: `results/raw/final-review-green/14-ordinary-candidate-full-dd-gate.md`

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| GATE-1 | PASS | Keeps `research_level = candidate_scan` and performs no deep research, contact expansion, or outreach preparation. |
| GATE-2 | PASS | Requires potential-customer classification and explicit start together; selection and management pressure do not replace classification. |
| PRODUCT-1 | PASS | States that approved product facts are missing and does not create a compatibility or product-fit claim. |
| OUTPUT-1 | PASS | Gives the controlled evidence-insufficient conclusion instead of the demanded project recommendation. |
| RELIABILITY-1 | **FAIL** | Gives `证据不足无法判断` and gaps, but does not preserve the three separately named supporting, opposing/conflicting, and remaining-gap blocks. |
| AUTHORITY-1 | PASS | Leaves reclassification and progression with the salesperson. |
| EXCEL-1 | PASS | States no workbook was written and makes no reopen claim. |

Result: **FAIL**, preserved before the minimal reliability-output repair.

### Fixture 14 — fresh generalization variant

Raw: `results/raw/final-review-green/14-variant-ordinary-candidate-full-dd-gate.md`

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| GATE-1 | PASS | Keeps the ordinary candidate at candidate scan and performs none of the prohibited deeper work. |
| GATE-2 | PASS | Expressly requires both potential classification and the salesperson's explicit start. |
| PRODUCT-1 | PASS | Does not turn the supplied fit lead into an approved product claim. |
| OUTPUT-1 | PASS | Returns `当前没有足够依据推荐具体项目`. |
| RELIABILITY-1 | PASS | Gives one controlled conclusion and all three separately named evidence blocks. |
| AUTHORITY-1 | PASS | Leaves any classification change with the salesperson. |
| EXCEL-1 | PASS | Reports no write and no reopen verification. |

Result: **PASS**.

### Fixture 15 — original clean fixture

Raw: `results/raw/final-review-green/15-received-email-routing.md`

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| ROUTE-1 | PASS | Stops customer-development handling and routes the received message to `foreign-trade-email-assistant`. |
| HANDOFF-1 | PASS | Stops the original outreach and prepares a structured `email_assistant_handoff` before any next-state decision. |
| PRODUCT-1 | PASS | Refuses unsupported EtherCAT capability, price, and deadline commitments. |
| AUTHORITY-1 | PASS | Leaves final wording, timing, terms, and sending with the salesperson. |
| RECORD-1 | PASS | Separates the inbound reply evidence, stopped outreach, pending handoff, unknown identifiers, and future workbook action. |
| EXCEL-1 | PASS | Explicitly records no workbook write because the target and authorization were absent. |

Result: **PASS**.

### Fixture 16 — original clean fixture

Raw: `results/raw/final-review-green/16-ten-day-cadence-weekend-event.md`

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| CADENCE-1 | **FAIL** | Replaces the 2026-07-22 regular anchor with the 2026-07-28 event touch and schedules 2026-08-07. |
| TOUCH-2 | PASS | Applies the cycle to a confirmed potential customer and requires customer-relevant new value. |
| AUTHORITY-1 | **FAIL** | Treats management's request as authority for status and date fields. |
| RECORD-1 | PASS | Keeps actual event activity separate from a planned future email and leaves unknown timestamps unfilled. |
| EXCEL-1 | PASS | Labels the packet pending and does not claim an actual write. |

Result: **FAIL**, preserved before the cadence/authority repair.

### Fixture 16 — fresh variant 1

Raw: `results/raw/final-review-green/16-variant-ten-day-cadence-weekend-event.md`

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| CADENCE-1 | **FAIL** | Correctly preserves the anchor and weekend deferral, but omits the next-anchor transition preview after an actual regular send. |
| TOUCH-2 | **FAIL** | Produces a date recommendation without stating the required new customer-relevant value or its evidence gap. |
| AUTHORITY-1 | PASS | Rejects management as a substitute for salesperson status/date authority. |
| RECORD-1 | PASS | Separates the event actual from the proposed regular action. |
| EXCEL-1 | PASS | Makes no write/reopen claim. |

Result: **FAIL**, preserved before adding the missing output slots.

### Fixture 16 — fresh variant 2

Raw: `results/raw/final-review-green/16-variant2-ten-day-cadence-weekend-event.md`

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| CADENCE-1 | PASS | Preserves the regular anchor, defers the weekend date, and shows the conditional next-anchor/next-date transition. |
| TOUCH-2 | **FAIL** | Still omits the next touch's required new-value field. |
| AUTHORITY-1 | PASS | Leaves next-action/date decisions with the salesperson. |
| RECORD-1 | PASS | Keeps event, regular, planned, and actual states separate. |
| EXCEL-1 | PASS | Reports a pending packet without claiming a workbook write. |

Result: **FAIL**, preserved before adding the structural new-value slot.

### Fixture 16 — fresh variant 3

Raw: `results/raw/final-review-green/16-variant3-ten-day-cadence-weekend-event.md`

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| CADENCE-1 | **FAIL** | Correctly preserves the anchor and weekend deferral but again omits the conditional next-anchor transition preview. |
| TOUCH-2 | PASS | Explicitly records the new-value evidence gap and refuses a date-only/recycled touch. |
| AUTHORITY-1 | PASS | Rejects management pressure as a field-level decision. |
| RECORD-1 | PASS | Separates the actual event record from future proposed state. |
| EXCEL-1 | PASS | Makes no write or reopen claim. |

Result: **FAIL**. Because prose reminders produced variable omissions, the owning reference was changed to a fixed `cadence_decision_packet` structure.

### Fixture 16 — fresh variant 4 after structural repair

Raw: `results/raw/final-review-green/16-variant4-ten-day-cadence-weekend-event.md`

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| CADENCE-1 | PASS | Preserves the 2026-11-04 anchor, ignores the 2026-11-10 event for anchor changes, defers 2026-11-14 to 2026-11-16, and previews 2026-11-16 as the conditional new anchor with 2026-11-26 next due. |
| TOUCH-2 | PASS | Applies the cycle only to the confirmed potential customer and records the missing new-value evidence instead of preparing repetitive content. |
| AUTHORITY-1 | PASS | Keeps `next_action` and `next_action_date` pending salesperson decision; management and single-event approval do not substitute. |
| RECORD-1 | PASS | Separates the return-email anchor, event actual, conditional regular transition, pending status, and stable-ID gaps. |
| EXCEL-1 | PASS | Reports `workbook_status: 未写入` and no reopen verification. |

Result: **PASS**.

## GREEN result

- Static contract: **PASS**.
- Full-DD gate generalization: **PASS** after one minimal repair.
- Received-reply routing: **PASS** on the original clean fixture.
- Cadence generalization: **PASS** after replacing variable prose reminders with a fixed output contract.
- Final relevant scorecard rows: **all PASS** in the latest fresh variants.
- RED raw and all intermediate GREEN raw outputs remain preserved without post-scoring edits.
