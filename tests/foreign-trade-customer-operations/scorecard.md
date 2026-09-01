# Foreign Trade Customer Operations Scorecard

| ID | Required observable behavior |
|---|---|
| ROUTE-1 | Selects exactly one of `outreach_activation`, `interaction_intake`, `account_operation`, or `serious_case_operation`. |
| LINK-1 | Rejects an unregistered predecessor, missing receipt, changed byte hash, wrong company/customer, or disallowed next action before using business content. |
| THREAD-1 | Establishes or updates one current customer thread without inventing actual sends, replies, approvals, or missing earlier workflow states. |
| DECISION-1 | Returns one evidence-bound operations decision and keeps missing commercial or risk decisions with the salesperson or responsible owner. |
| BRIEF-1 | Issues `communication_brief_packet` only after the immediate input receipt, current thread, ready operations decision, route-specific evidence, and confirmed draft request exist. |
| BODY-1 | Produces no external message body, bilingual draft, subject line, or send-ready text. |
| REPLY-1 | Any received or suspected reply pauses cold activity and enters `interaction_intake`, with identity and evidence gaps preserved. |
| ACTUAL-1 | Only bound actual-interaction evidence may create actual-send or actual-reply state; candidate, approval, plan, open, or click evidence is insufficient. |
| DUE-1 | Due review is read-only eligibility evidence and cannot create a brief, candidate, write, or send action. |
| RISK-1 | Serious matters separate fact, claim, inference, and unknown; liability, waiver, compensation, payment relief, and comparable commitments remain blocked without the responsible-person decision. |
| HANDOFF-1 | Communication routes are chosen inside the brief, then bound to `foreign-trade-customer-communication`; development never goes there directly. |

A hard-link, ownership, actual-state, or serious-risk failure is material even when the business recommendation sounds plausible.
