# Final-Audit GREEN Test Summary

## Protocol

Production references changed only after Task 21 had established exactly three static RED diagnostics and three failing behavior fixtures. The original RED raw files remain byte-identical:

- fixture 17: `7b49dbc2be88d6e926ff9c127b1b6db69f5146055223f9809fe58cc1a19df02b`
- fixture 18: `734464cfa2c44e301e4164ccfd5afa1f8d672cdfa6934d422f7c5ffaef72a069`
- fixture 19: `1ccc1b3d93039b8a1734138e7ef88a070f16e80a1b3249a668f156fe6b8026ea`

Fixtures 17–19 ran in order. Every behavior run used a fresh `fork_turns = none` executor whose prompt contained only the unchanged GREEN instruction, one fictional request inline, and permission to read the current plugin skill and its explicitly required references. Runners could not read fixture files, tests, scorecards, answers, summaries, plans, Git history, or prior raw; they did not browse or modify files.

Each work product was saved under `results/raw/final-audit-green/` before an independent raw-only scorer read it. The scorer used only the scorecard, the relevant fixture, and the saved raw. Failed outputs were preserved unchanged; production wording was minimally repaired before a new fresh-context run.

## Static contract

Before the production repair, `validate_contract.py` exited `1` with exactly:

- `opportunity.email_gap_first_touch`
- `evidence.unverified_inbound_email`
- `opportunity.valid_event_candidate`

After the repair it exits `0`:

```text
PASS: all specification-traceability contracts are present
```

The three canonical clauses now coexist with their required operational detail: salesperson choice when no usable email exists, immediate bounded handoff despite unverified inbound identity, and a mandatory reviewable event-touch candidate that never auto-sends or resets the regular anchor.

## Historical fixture 15 correction

The preserved `final-review-green/15-received-email-routing.md` raw is byte-identical at `1dba8f21db006505f48aa3eb233251b962c346972fe2b0369c38b7b75042da9a`. Its summary now scores `SOURCE-2` **FAIL**, because it labeled inbound claims `官方直接证据` while stating that sender identity and headers were absent. Routing and immediate handoff remain PASS; source-state handling was not GREEN until the dedicated fixture 18 repair below.

## Behavioral scoring

### Fixture 17 — no normally usable email

Raw: `results/raw/final-audit-green/17-no-usable-email-first-touch.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| EMAIL-GAP-1 | PASS | Records the checked range and missing email, then gives exactly the three salesperson choices: continue email research, approve one qualified professional-profile exception, or pause. |
| CONTACT-1 | PASS | Keeps the guessed email discarded and preserves authenticity, reliability, permission, and missing source/date details for the profile. |
| AUTHORITY-1 | PASS | Does not let management select the exception; content, channel, date, and sending remain with the salesperson. |
| RECORD-1 | PASS | Separates the qualified channel candidate, uncreated contact material, unstarted email sequence, and no actual send. |
| PUBLIC-1 | PASS | Uses the public-source checks without requiring access authorization and does not confuse public availability with contact-channel approval. |
| EXCEL-1 | PASS | Reports no write and no reopen verification. |

Result: **PASS**.

### Fixture 18 — inbound text with unverified identity and headers

Raw: `results/raw/final-audit-green/18-unverified-inbound-email-evidence.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| INBOUND-EVIDENCE-1 | PASS | Uses `来源不明隔离待核实`, preserves the pasted claim and identity/header gaps, and applies reply hard-stop plus immediate handoff. |
| ROUTE-1 | PASS | Stops prospect-development ownership and routes the current saved text and context to `foreign-trade-email-assistant`. |
| HANDOFF-1 | PASS | Prepares the bounded handoff immediately instead of waiting for identity verification or send-history completion. |
| SOURCE-2 | PASS | Separates the existence of pasted text from sender, role, company identity, purchase intent, and formal inquiry conclusions. |
| PRODUCT-1 | PASS | Refuses configuration and price claims without approved product facts. |
| RELIABILITY-1 | PASS | Gives one controlled conclusion with supporting evidence, opposing/conflicting evidence, and remaining gaps. |
| AUTHORITY-1 | PASS | Management does not retain this skill's ownership or authorize a development message. |
| RECORD-1 | PASS | Does not record the text as a verified actual reply and does not claim a formal handoff or workbook record was written. |
| WORKBOOK-2 | PASS | The pending packet preserves salesperson-owned fields and leaves unknown risk state unasserted. |
| EXCEL-1 | PASS | Explicitly reports no workbook write. |

Result: **PASS**. The scorer noted that `observed_at = 2026-07-24` is runtime metadata rather than a fixture-supplied customer fact; it does not affect the evidence, stop, or handoff decision.

### Fixture 19 — original GREEN attempt

Raw: `results/raw/final-audit-green/19-valid-event-must-prepare.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| EVENT-1 | **FAIL** | Leaves the new validation question as an unfilled placeholder, so the proposed event material is not fully reviewable. |
| SOURCE-2 | **FAIL** | Invents that a previously approved main professional email remains usable without current channel evidence. |
| WORKBOOK-2 | **FAIL** | Its pending update packet omits the risk-state gap and salesperson-field preservation. |
| AUTHORITY-1 | PASS | Leaves final content, channel, date, and sending with the salesperson. |
| TOUCH-2 | PASS | Keeps the potential-customer 10-day cycle and recognizes the event as new value. |
| RECORD-1 | PASS | Separates the event draft from actual sending and keeps the regular anchor. |
| EXCEL-1 | PASS | Reports no write. |

Result: **FAIL**, preserved before the output-shape repair.

### Fixture 19 — variant 2

Raw: `results/raw/final-audit-green/19-variant2-valid-event-must-prepare.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| EVENT-1 | PASS | Supplies complete candidate wording, marks it unsent, and preserves the regular anchor. |
| SOURCE-2 | **FAIL** | Introduces “integration adaptation and field operation requirements” as if it were the recorded validation question although the raw admits the source text is unavailable. |
| AUTHORITY-1 | PASS | Leaves all event and regular-touch decisions with the salesperson. |
| TOUCH-2 | PASS | Correctly maintains the potential-customer 10-day cycle and event-specific value. |
| RECORD-1 | PASS | Separates actual return email, event draft, conditional future send, and pending workbook state. |
| WORKBOOK-2 | PASS | Preserves salesperson fields and risk state and does not claim a write. |
| EXCEL-1 | PASS | Reports no write or reopen verification. |

Result: **FAIL**, preserved before separating source facts from an AI-proposed question.

### Fixture 19 — variant 3

Raw: `results/raw/final-audit-green/19-variant3-valid-event-must-prepare.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| EVENT-1 | PASS | Immediately prepares a complete additional-touch candidate for salesperson review, marks it unapproved/unplanned/unsent, and does not reset the anchor. |
| SOURCE-2 | PASS | Separates supplied official-event facts, the unavailable recorded-question text, and an explicitly proposed open question that adds no unsupported technical dimension. |
| AUTHORITY-1 | PASS | Rejects the sales manager as a substitute and leaves adoption, final content, channel, date, and sending with the salesperson. |
| TOUCH-2 | PASS | Applies the cycle only to the confirmed potential customer and uses the new event plus a bounded open question as new value. |
| RECORD-1 | PASS | Separates the actual return email, event candidate, approval, planning, sending, and pending workbook states. |
| WORKBOOK-2 | PASS | Preserves the risk-state gap and salesperson classification, notes, decisions, approvals, and decision dates; no stable ID is invented. |
| EXCEL-1 | PASS | Reports no write and no verifiable workbook update. |
| PRODUCT-1 | PASS | Makes no capability promise and limits any later fit decision to the approved product scope. |
| PUBLIC-1 | PASS | Uses the verified public company-news fact without requesting unnecessary access authorization. |

Date check: 2026-07-20 + 10 natural days = 2026-07-30. A conditional actual regular send on 2026-07-30 would produce 2026-08-09, then defer Sunday to 2026-08-10. The event candidate does not alter the 2026-07-20 anchor.

Result: **PASS**. The scorer noted a minor raw-label ambiguity in “人工建议验证问题”; the production contract itself uses the explicit field `ai_suggested_validation_question`, so future outputs distinguish the AI proposal from salesperson or customer facts.

## GREEN status

- Static contract: **PASS**, from exactly three RED diagnostics to zero.
- Fixture 17 latest run: **PASS**.
- Fixture 18 latest run: **PASS**.
- Fixture 19 latest run: **PASS** after preserving two failed attempts and replacing inference with an explicit fact/unavailable-source/AI-proposal split.
- Initial three-email sequence, qualified alternate-channel step, return email, 10-natural-day cycle, reply hard-stop, and salesperson sending authority remain present in the production contract.
- No runner browsed, modified files, sent messages, wrote a workbook, or claimed an unverified workbook update.
