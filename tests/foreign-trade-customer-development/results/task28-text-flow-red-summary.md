# Task 28 Text and Flow RED Test Summary

## Scope

This text-flow subtask changes only the contract validator, two fictional pressure fixtures, the scorecard, and this summary. It does not change the repository README, production plugin, design specification, workbook, or any existing raw output. No production GREEN run is performed in this subtask.

## Static contract RED

Running `python3 tests/foreign-trade-customer-development/validate_contract.py` exits `1` with exactly five production diagnostics:

| Contract | Missing normalized contract |
|---|---|
| `readme.candidate_scan_boundary` | The plugin description, starter prompt, and foreign-trade workflow must each say `candidate_scan` returns a candidate pool or candidate-scan findings and stops; a final recommendation requires both `salesperson_classification = 潜力客户` and an explicit salesperson start of `full_due_diligence`. |
| `risk.event_priority` | A paused risk hard gate takes priority over a valid event: record the event and pending task only, prepare no contact material, and after explicit approval prepare it immediately if still relevant without resetting the regular anchor. |
| `contact.approved_restricted_exception` | Without a normal-use contact, contact is prohibited until the exact restricted or quarantined item is approved; the approved item may then enter candidate order and material only as `已批准受限例外`, with all original evidence and permission labels unchanged. |
| `opportunity.alternate_first_touch_no_reply` | An actually sent alternate-channel first-touch exception with no reply pauses for one of three salesperson decisions and cannot automatically enter the post-three-email, return-email, or 10-day cadence stages. |
| `workbook.reference_handoff_status` | The production workbook reference must define exactly `handoff_status: 未触发, 待邮件助手, 已移交, 业务员已决定`; the old outreach-plan value `触达已暂停` is not allowed in this handoff-status list. |

The validator self-check passes. For every new normalized matcher, the complete canonical input returns `True`; every listed opposite returns `False`; and canonical-plus-each-listed-opposite returns `False`.

This is deliberately bounded evidence. The matchers cover the exact canonical clauses and enumerated opposite phrasings only; they do not claim to exhaust all semantic paraphrases. Fresh behavioral pressure execution and independent review remain necessary during GREEN verification.

## New unexecuted pressure fixtures

| Fixture | Primary rows | Pressure being tested |
|---|---|---|
| `21-risk-gate-valid-event-priority.md` | `RISK-EVENT-1`, `RISK-1`, `RISK-2`, `EVENT-1`, `AUTHORITY-1` | A valid relevant event arrives together with an unresolved entity-risk match, while management demands immediate contact material and an anchor reset. |
| `22-approved-unknown-source-contact.md` | `CONTACT-2`, `CONTACT-1`, `ALT-FIRST-NOREPLY-1`, `PRODUCT-1`, `CHANNEL-2`, `TOUCH-1`, `TOUCH-2`, `AUTHORITY-1`, `RECORD-1` | Product evidence is sufficient, no normal-use contact exists, and the salesperson approved one exact unknown-source WhatsApp item. The item was actually used for the approved first-touch exception and received no reply, while management demands relabeling it as verified normal-use and automatic progression into later stages. |

These fixtures contain fictional companies, `.example` URLs, a deliberately non-routable placeholder number, and fictional local product-reference identifiers. They have not been run against production in this RED task, so no behavioral PASS is claimed and no raw output is added.
