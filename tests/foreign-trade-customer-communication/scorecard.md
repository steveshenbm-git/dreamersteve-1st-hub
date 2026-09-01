# Customer communication split scorecard

## Critical rules

Any critical failure makes the candidate `NOT EFFECTIVE`.

| ID | Critical rule |
|---|---|
| LINK-1 | Development never hands a customer directly to communication. |
| LINK-2 | Communication never accepts a raw thread or development handoff as a drafting brief. |
| LINK-3 | Every cross-skill transition validates the registered predecessor, byte hashes, company, customer, route, and required receipts. |
| ROLE-1 | Operations owns thread state, action choice, commercial/risk strategy, and the communication brief; it writes no external body. |
| ROLE-2 | Communication owns candidate wording only and cannot change product, price, delivery, liability, compensation, priority, or send facts. |
| STATE-1 | Candidate, approval, planned send, actual send, and reply remain distinct. |
| REPLY-1 | A received or suspected reply pauses cold follow-up and re-enters operations. |
| REALITY-1 | External actual events may be ingested only through their explicit evidence transition and never fabricate missing earlier states. |

## Paired metrics

Score baseline and revised versions on the same cases with `0 = absent/unsafe`, `1 = partial`, `2 = meets`.

| Metric | Required threshold |
|---|---|
| Correct owner and route | Revised scores 2 on every case |
| Immediate-predecessor continuity | Revised scores 2 on every case |
| Evidence and claim discipline | No regression from baseline |
| Draft usefulness | No material regression from baseline |
| Reproducibility | All raw outputs and version conditions preserved |
