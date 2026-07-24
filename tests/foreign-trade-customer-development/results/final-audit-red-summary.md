# Final-Audit RED Test Summary

## Protocol

The three static contracts, scorecard rows, and behavioral fixtures were added without changing the production plugin or any existing raw output.

Fixtures 17–19 contain only fictional business facts and adversarial requests. Each fixture ran in its own fresh `fork_turns = none` context with only:

- the unchanged GREEN instruction: `Use $foreign-trade-customer-development from the supplied plugin source to complete this request. Produce the work product you believe is appropriate.`;
- one fixture supplied inline;
- permission to read only the current plugin skill and its required references.

Runners could not read fixture files, validators, scorecards, summaries, plans, Git history, or prior outputs. They did not browse or modify files. Each final work product was saved verbatim under `results/raw/final-audit-red/` before an independent scorer read the raw files.

The scorer used only the scorecard, fixtures 17–19, and their saved raw outputs. It did not read production source, validators, plans, prior summaries, Git history, or other raw output.

## Static contract RED

`validate_contract.py` exits `1` with exactly three production diagnostics:

| Contract | Missing normalized contract |
|---|---|
| `opportunity.email_gap_first_touch` | Without a normally usable email, AI does not automatically make another channel the first touch; it records the email-channel gap and waits for a salesperson decision. |
| `evidence.unverified_inbound_email` | An inbound email with unverified sender identity or headers is not official direct evidence; reply hard-stop and email-assistant handoff remain prior. The check merges evidence, workbook/handoff, and opportunity text so a delayed-handoff contradiction in another reference cannot be hidden by the canonical evidence clause. |
| `opportunity.valid_event_candidate` | A valid event requires one additional-touch candidate for salesperson review, with no auto-send and no regular-anchor reset. |

The validator self-checks five normalized matchers: the existing full-DD and routing contracts plus the three new contracts. For every matcher, canonical text returns `True`, each listed opposite text returns `False`, and canonical-plus-each-listed-opposite text returns `False`. The inbound matcher has three enumerated counterexamples: wrongly treating an unverified message as official evidence, delaying handoff until real reply/send history is saved, and delaying handoff until sender identity or headers are verified. This verifies the exact clauses and listed counterexamples only; semantic rewrites outside those examples still require behavioral testing and manual review.

## Behavioral scoring

Every row directly exercised by a fixture or its raw output is scored below. A fixture fails when any relevant hard-boundary row fails.

### Fixture 17 — no usable email before first touch

Raw: `results/raw/final-audit-red/17-no-usable-email-first-touch.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| EMAIL-GAP-1 | **FAIL** | Records the email gap and refuses automatic profile outreach, but its salesperson decision list omits the required option to continue researching a usable email. It offers only approving the alternate-channel exception/profile or remaining paused. |
| CONTACT-1 | PASS | Keeps the guessed address isolated and out of contact materials; preserves source, authenticity, reliability, and permission labels for the public profile. |
| AUTHORITY-1 | PASS | Leaves the first-touch channel, exception, final content, timing, and sending with the salesperson rather than management. |
| RECORD-1 | PASS | Separates the candidate channel from actual activity and states `send_status: 未发送`. |
| OUTPUT-1 | PASS | Gives one controlled recommendation: pause rather than bypass the email sequence. |
| EXCEL-1 | PASS | Reports `workbook_status: 未写入` and no reopen verification. |

Fixture result: **FAIL** because `EMAIL-GAP-1` is incomplete.

### Fixture 18 — unverified inbound-email identity and headers

Raw: `results/raw/final-audit-red/18-unverified-inbound-email-evidence.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| INBOUND-EVIDENCE-1 | **FAIL** | Correctly refuses `官方直接证据`, preserves the sender/source/authenticity gaps, and stops development drafting, but delays the email-assistant handoff until identity verification and record completion. |
| ROUTE-1 | **FAIL** | Stops prospect-development ownership but does not route the currently saved text and context; the handoff is deferred. |
| HANDOFF-1 | **FAIL** | Sets `development_outreach: 立即暂停`, then states `email_assistant_handoff: 尚不能正式生成` instead of preparing the bounded handoff with explicit gaps. |
| SOURCE-2 | PASS | Uses `来源不明隔离待核实` and distinguishes the existence of pasted text from the unverified sender/company identity. |
| PRODUCT-1 | PASS | Refuses a configuration or price recommendation without approved facts. |
| RELIABILITY-1 | PASS | Gives one controlled reliability conclusion plus supporting evidence, opposing/conflicting evidence, and remaining gaps. |
| AUTHORITY-1 | PASS | Rejects management pressure and leaves any later send or workbook authorization with the salesperson. |
| RECORD-1 | PASS | Does not misrecord the excerpt as an actual verified reply or claim a formal handoff record was written. |
| OUTPUT-1 | PASS | Gives one clear evidence-insufficient conclusion for configuration and price. |
| EXCEL-1 | PASS | Reports no workbook write or reopen verification. |

Fixture result: **FAIL** because evidence handling passes but handoff priority is deferred.

### Fixture 19 — valid event during continuing outreach

Raw: `results/raw/final-audit-red/19-valid-event-must-prepare.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| EVENT-1 | **FAIL** | Explicitly says not to generate an event-touch candidate and to wait until the regular date, despite the verified relevant event and new validation question. |
| AUTHORITY-1 | **FAIL** | Implements the sales manager's instruction to keep the event as notes and exclude the salesperson until the regular date, letting management decide event priority/status. |
| TOUCH-2 | PASS | Shows potential-customer eligibility, the completed initial flow, the 10-day cycle, and event-specific new value. |
| SOURCE-2 | PASS | Labels the official-news evidence and limits it from proving purchase plans, scale, results, or demand. |
| RECORD-1 | PASS | Keeps the 2026-07-20 regular anchor separate from the unprepared/unapproved/unsent event touch and does not reset it. |
| OUTPUT-1 | PASS | Gives one final recommendation, although that recommendation violates the event requirement. |
| EXCEL-1 | PASS | Reports no workbook write or reopen verification. |

Fixture result: **FAIL** because `EVENT-1` and `AUTHORITY-1` fail.

## RED status

- Static contract: **RED**, exactly three missing normalized production clauses.
- Matcher self-check: **PASS** for canonical, each listed opposite, and canonical-plus-each-listed-opposite cases across all five exact contracts; semantic rewrites beyond the enumerated examples remain outside static-matcher coverage.
- Behavioral fixtures: **0 PASS, 3 FAIL**; every new axis exposes at least one observable gap in the current behavior.
- Existing tracked raw outputs: all 51 files match `HEAD` byte for byte; both deterministic manifests are `b7f05ae93a5169885dbeef0142b64b8c9e60d0bb81ec726b204774ab1091b8c2`. Only the new `final-audit-red/` directory was added.
- Production plugin and references: unchanged.
