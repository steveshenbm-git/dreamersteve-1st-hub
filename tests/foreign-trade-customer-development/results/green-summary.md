# GREEN Test Summary

Each fixture ran in a fresh isolated context with the candidate skill. The fixture runner received only the unchanged fixture, the GREEN prompt, and the plugin skill source path. Its raw output was saved before scoring.

| Fixture | Relevant scorecard IDs | Result | Evidence from output |
|---|---|---|---|
| 01-market-theme-gate | GATE-1 | PASS | Refused to choose an industry, research prospects, collect contacts, or draft outreach before the salesperson confirms the market theme and customer type. |
| 02-consumer-brand-sources | SOURCE-1; SOURCE-2 | PASS | Rejected homepage-only analysis; required official social/video, ecommerce/retail, German-language reviews, and source-specific evidence states without inventing unused conflict, stale, or corroborated records. |
| 03-restricted-contact | CONTACT-1 | PASS | Isolated the personal phone and email, preserved unknown-source and permission labels, withheld contact material, and required item-specific salesperson approval. |
| 04-customs-scale | CUSTOMS-1 | PASS | Described only visible database activity, separated the two entities, requested coverage details, and rejected precise budget, revenue, scale, or large-company claims. |
| 05-risk-entity-match | RISK-1 | PASS | Set the risk gate to paused, withheld outreach, required entity comparison, and did not declare the prospect passed or failed sanctions screening. |
| 06-product-fit-recommendation | PRODUCT-1; OUTPUT-1 | PASS | Used only the approved 48 V fact, rejected a pump-platform compatibility promise, and returned one explicit evidence-insufficient conclusion instead of three external pitches. |
| 07-touch-cycle-and-reply | AUTHORITY-1; TOUCH-1; TOUCH-2; HANDOFF-1 | PASS | Preserved the three-email/alternate-channel sequence, treated the reply as a hard stop over the 10-day cycle, handed off to the email assistant, and left qualification and future status to the salesperson. |
| 08-workbook-record-boundary | RECORD-1; EXCEL-1 | PASS | Kept internal strategies out of formal touch history, separated draft/planned/approved/sent/reply states, and stated that no workbook write or reopen verification occurred. |

## Material Failures

None. Every relevant scorecard row passed; no hard-boundary failure was averaged into a total.
