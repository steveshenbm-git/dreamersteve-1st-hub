# Final-Review RED Test Summary

## Protocol

The static and workbook-enforcement tests were added before any plugin-source or workbook repair. Production skill files and the `.xlsx` asset were not modified.

Each official behavioral fixture ran in a fresh `fork_turns = none` agent context with only:

- one fixture, either as the sole file input or inline task material;
- the unchanged GREEN prompt: `Use $foreign-trade-customer-development from the supplied plugin source to complete this request. Produce the work product you believe is appropriate.`;
- the current plugin skill source and the references required by that skill.

Runners could not read the scorecard, diagnostics, other fixtures, prior outputs, design, or plan. They did not browse the web or modify files. Each official raw output was saved under `results/raw/final-review-red/` before scoring.

## Static contract RED

`python3 tests/foreign-trade-customer-development/validate_contract.py` exits `1` with two named diagnostics:

| Contract | Missing observable contract |
|---|---|
| `research.full_due_diligence_dual_gate` | The research reference does not directly require both `salesperson_classification = 潜力客户` and an explicit full-due-diligence start, nor directly state that selection or `普通候选` is insufficient. |
| `skill.routing_description` | The activation description does not limit this skill to pre-reply or unanswered prospect-development outreach or route received customer replies to `foreign-trade-email-assistant`. |

The validator parsed the skill and all four UTF-8 reference files. RED is caused by the two reviewed contract omissions, not an import, syntax, path, or decoding error.

## Workbook enforcement RED

The validator now defines every controlled validation by exact worksheet, field, column range from row 3 through row 5000, list type, ordered values, `showErrorMessage = True`, and `errorStyle = stop`.

The current workbook exits `1` with 26 named diagnostics: each of the 13 controlled validations has the correct existing range, list type, and values, but lacks both enabled error-message enforcement and stop style.

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

## Mutation proof

Before the validator was tightened, two separate temporary-workbook counterexamples both false-passed with exit `0`:

- `客户总览.screening_status` contained `NOT_A_VALID_SCREENING_STATE`;
- `客户总览.risk_gate` had its error alert disabled.

After adding the test-side contract, `test_validate_workbook_mutations.py` passes because the validator rejects both temporary mutations with their named field diagnostics. The script uses separate temporary copies, verifies the production-workbook hash is unchanged, and requires no production repair. It is ready to stay GREEN after the workbook itself is repaired.

## Behavioral scoring

### Fixture 14 — ordinary candidate requests full due diligence

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| GATE-2 | **PASS** | Refuses full due diligence, expanded contact research, final recommendation, and outreach while `salesperson_classification = 普通候选`; states that selection alone is insufficient and requires reclassification to `潜力客户`. |

Fixture result: **PASS**. Current behavior held the gate despite the missing durable wording in the detailed research contract.

### Fixture 15 — received email asks for analysis and reply

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| ROUTE-1 | **PASS** | Stops all prospect-development follow-up, explicitly refuses to draft the final reply, preserves missing product and price facts, and routes the saved message and open questions to `foreign-trade-email-assistant`. |

Fixture result: **PASS**. Current body guidance routed correctly despite the ambiguous activation description.

### Fixture 16 — positive 10-day cadence

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| CADENCE-1 | **PASS** | Keeps the anchor at 2026-07-22 after the 2026-07-28 event touch, computes the unadjusted due date as Saturday 2026-08-01, defers it to Monday 2026-08-03, and after an actual regular send on 2026-08-03 computes the next due date as 2026-08-13. |

Fixture result: **PASS**. This adds the previously missing positive date-calculation evidence without forcing a correct behavior to fail.

Behavioral result: **3 PASS, 0 FAIL**.

## Output-hygiene incident

The first fixture-15 runner correctly routed the reply but copied a personal absolute fixture path into its handoff packet. That output was not scored and is not in the public test tree. Its verbatim evidence was moved without rewriting to:

`/private/tmp/ftcd-task16-private-red/15-received-email-routing-absolute-path.md`

SHA-256: `ae8312d3a8298349e0d2ab41b14aabdfaa5c35e13544519e6ea067da9679a9d0`.

A new fresh runner received the fixture as inline task material, was told not to cite local filesystem paths, still received no scorecard or expected answer, and produced the official saved raw output. The public Task 16 additions contain no personal absolute path.

## RED status

- Static contract: **RED**, two reviewed omissions.
- Workbook asset: **RED**, all 13 controlled lists lack stop-style enforcement.
- Mutation regression script: **PASS**, both known validator blind spots are now detected.
- Behavioral fixtures: **3 PASS, 0 FAIL**; the cadence coverage gap is closed by a real positive case.
- Plugin production files and workbook asset: **unchanged**.
