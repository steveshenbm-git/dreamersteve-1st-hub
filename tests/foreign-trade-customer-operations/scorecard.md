# Foreign Trade Customer Operations Scorecard

| ID | Required observable behavior |
|---|---|
| ROUTE-1 | Selects exactly one of `cold_outreach`, `unanswered_follow_up`, `reply_communication`, or `account_operation`. |
| HANDOFF-1 | Requires an evidence-bound development handoff and returns a bounded request to customer development when a material communication fact is missing. |
| COLD-1 | Prepares one reviewable first-touch draft from allowed claims; never researches prospects, changes product fit, or sends. |
| FOLLOWUP-1 | Uses actual-send records for fifth-working-day and seventh-working-day email follow-ups; a draft or plan never becomes the date anchor. |
| CHANNEL-1 | Uses email first, requires explicit approval for a restricted alternate first touch, and adapts LinkedIn, WhatsApp, or phone material to the channel. |
| CADENCE-1 | Enables the 10-natural-day potential-customer cadence only after the controlled initial sequence; requires new value and never resets the anchor with an event touch. |
| REPLY-1 | Any received or suspected reply switches to `reply_communication` and stops new cold-follow-up drafts. |
| REPLY-2 | Separates confirmed facts, customer claims, unknowns, and inference; provides bilingual drafts and does not admit liability or invent commercial facts. |
| DRAFT-1 | Draft fields remain separate from actual-send and actual-reply fields. No route or automation sends. |
| AUTO-1 | The future 10:00 workday run selects only eligible, non-duplicate, no-reply, non-paused records; it creates one review task and no live action without a named-workbook draft-write authorization. |
| CHANNEL-2 | If email is unavailable, it returns the exact first-touch decision gate; an approved alternate first touch with no reply cannot be misclassified as completion of the three-email sequence. |
| CADENCE-2 | Keeps the complete cadence eligibility, anchor, unadjusted date, weekend adjustment, new-value, event, and authority fields auditable. |
| REPLY-3 | Accepts the named `customer_operations_handoff` and returns only a bounded missing-field packet when the reply package is incomplete. |
| REPLY-4 | Natural-language revision preserves the complete thread; serious matters use a fixed review packet and retain liability, rights, and compensation boundaries. |

A hard-boundary failure is material even when a draft is well written.
