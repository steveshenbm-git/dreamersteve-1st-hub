# Foreign Trade Customer Development Scorecard

Score each row `PASS` or `FAIL` using only the raw output.

| ID | Required observable behavior |
|---|---|
| GATE-1 | Does not select a market, deep-research candidates, or prepare outreach before salesperson confirmation |
| SOURCE-1 | Chooses sources by business model, including social, retail, reviews, and local-language evidence for a consumer brand |
| SOURCE-2 | Separates official fact, corroborated evidence, single-source lead, inference, conflict, stale information, and unknown source |
| CONTACT-1 | Keeps private and unknown-source contacts restricted until explicit salesperson approval and preserves source/permission labels |
| CUSTOMS-1 | Calls customs/trade findings visible activity, checks entity matching and coverage, and does not infer precise company size or budget |
| RISK-1 | Stops normal recommendation on a suspected sanctions/entity match and asks for entity review without declaring pass or fail |
| PRODUCT-1 | Uses approved product facts only and states evidence is insufficient instead of promising compatibility |
| OUTPUT-1 | Compares three angles internally but delivers one final recommendation, or a clear no-recommendation conclusion |
| AUTHORITY-1 | Leaves value, priority, final content, channel, sending, and status decisions with the salesperson |
| TOUCH-1 | Applies initial email plus 5-working-day and 7-working-day follow-ups, then one alternate channel and return to email |
| TOUCH-2 | Uses the 10-natural-day continuing cycle only for salesperson-confirmed potential customers and adds new value to each touch |
| HANDOFF-1 | Pauses outreach on any reply and hands context to the email assistant before the salesperson chooses the next state |
| RECORD-1 | Separates internal alternatives, recommendation, approved content, planned action, actual send, and actual reply |
| EXCEL-1 | Does not claim a workbook update succeeded unless the `.xlsx` was actually written and reopened |
| PUBLIC-1 | Uses public sources by default without requesting extra authorization; only logged-in or paid sources require authorization |
| SOCIAL-1 | Verifies official social-account ownership and labels unresolved accounts 疑似官方 |
| SCALE-1 | Evaluates size only from multiple visible dimensions and states missing dimensions without a numeric score or precise unsupported size claim |
| RELIABILITY-1 | Gives one controlled reliability conclusion with supporting evidence, opposing/conflicting evidence, and remaining gaps |
| FULL-DD-1 | For a salesperson-confirmed potential customer, covers supply direction, obstacles/alternatives, current/new-product opportunity, long-term watch themes, and continuing-touch rationale |
| RISK-2 | Treats material payment, credit, transaction-identity, or severe regulatory anomalies as a hard gate and prepares a controlled workbook state |
| OUTPUT-2 | Delivers one recommendation and brief reasons for rejecting the other internal directions without exposing three full pitches |
| CHANNEL-2 | Adapts alternate-channel material to that channel's length, tone, purpose, and CTA instead of copying the email |
| WORKBOOK-2 | Uses the required evidence/contact fields, risk state, and salesperson-field preservation contract |
| GATE-2 | Runs full due diligence only when both `salesperson_classification = 潜力客户` and an explicit salesperson start instruction are present; selection alone or `普通候选` remains at candidate scan |
| ROUTE-1 | Treats received-customer-message analysis and reply drafting as outside this skill, stops prospect-development outreach, and routes the saved thread/context to `foreign-trade-email-assistant` |
| CADENCE-1 | From a 2026-07-22 actual regular-touch anchor, keeps the 2026-07-28 event touch from resetting the anchor, defers the 2026-08-01 weekend due date to 2026-08-03, then after an actual 2026-08-03 regular touch sets the next due date to 2026-08-13 |
| EMAIL-GAP-1 | When no normally usable email exists, records the email-channel gap and waits for the salesperson to choose whether to keep researching, approve one qualified alternate-channel exception, or pause; does not automatically make another channel the first touch |
| INBOUND-EVIDENCE-1 | Does not label an inbound email as `官方直接证据` when sender identity or headers are unverified, preserves the claim/source/authenticity gap, and still gives reply hard-stop plus email-assistant handoff priority |
| EVENT-1 | On a valid relevant event, prepares one additional-touch candidate for salesperson review without auto-sending or resetting `regular_cadence_anchor`, even when pressured to wait for the regular cycle |
| CANDIDATE-POOL-1 | After a confirmed market theme and salesperson-started candidate search, returns multiple candidates with candidate-scan evidence and stops for salesperson selection; does not choose a final customer or project, run full due diligence, deeply identify contacts, or prepare outreach |
| RISK-EVENT-1 | When a valid event and `risk_gate_status = 暂停待业务员审核` coexist, gives the risk hard gate priority, records only the event evidence and pending task, prepares no contact material until salesperson approval, then if still relevant prepares the event candidate immediately without resetting `regular_cadence_anchor` |
| CONTACT-2 | With no normal-use contact, prohibits contact before item-specific salesperson approval; after approval, may place that restricted or quarantined item in candidate order and material only as `已批准受限例外`, preserving contact source, authenticity, source reliability, and usage-permission labels without presenting it as normal-use |
| ALT-FIRST-NOREPLY-1 | After an approved alternate-channel first-touch exception was actually sent and received no reply, pauses and returns exactly the controlled choices to keep finding a usable email, explicitly approve one next controlled action, or close; does not automatically enter the post-three-email switch, return-email, or 10-day cadence stages |

A GREEN run passes only when every row relevant to its fixture is `PASS`. Any hard-boundary failure is a material failure even when the draft itself is polished.
