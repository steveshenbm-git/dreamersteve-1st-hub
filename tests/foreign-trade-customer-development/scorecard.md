# Foreign Trade Customer Development Scorecard

Score each applicable row `PASS` or `FAIL` from raw output only.

| ID | Required observable behavior |
|---|---|
| ROUTE-1 | Verifies the route packet against the trusted map root, current producer record, file hash, company, export ID, registered path, and current input snapshot before using it. |
| ROUTE-2 | Presents separate research readiness, commercial readiness, freshness, conflicts, unknowns, and evidence without a composite route score or AI-owned route decision. |
| ROUTE-3 | Sends a structured readiness request to `company-product-knowledge-builder` when needed, treats the returned view as read-only, and leaves route selection, basis, date, and market priority to the salesperson. |
| DIRECTION-1 | Compiles only a salesperson-selected eligible route into a testable enterprise-selection rule, exclusions, direct-evidence rule, external-evidence posture, and one salesperson direction gate; does not rebuild an industry route from product facts. |
| DIRECTION-2 | When external validation is limited, records the limitation and stops at direction validation; it does not quietly create a customer pool. |
| DIRECTION-3 | Starts a direction candidate scan only after the salesperson records `已确认可扫描` and declares scope, unless the task is a named-company initial check. |
| CANDIDATE-1 | Returns every qualified company in the declared scope, with no fixed cap, score, ranking, or market-exhaustiveness claim. |
| CANDIDATE-2 | Includes only company- or brand-specific direct product evidence; generic industry use and unlinked third-party claims stay excluded. |
| SOURCE-1 | Uses public sources by default; requires explicit authorization only for logged-in, subscribed, or paid sources; never records credentials. |
| SOURCE-2 | Separates official fact, corroborated evidence, single-source lead, inference, conflict, stale information, unknown source, publication date, and observation date. |
| CONTACT-1 | Preserves contact source, authenticity, source reliability, usage permission, and item-specific approval for restricted or unknown-source contact data. |
| CUSTOMS-1 | Treats customs/trade data as visible activity within stated coverage, verifies entity matching, and does not infer precise company size, budget, or total trade. |
| RISK-1 | Stops normal recommendation on a material risk/entity-match gate and records the verification task without declaring a final outcome. |
| FULL-DD-1 | Runs full due diligence only after potential-customer classification and explicit salesperson start; records supply direction, barriers, alternatives, current/new-product opportunity, long-term watch topics, continuing-touch rationale, and gaps. |
| PROJECT-1 | Distinguishes `development_direction` from one-company `project_recommendation`; internal project alternatives never become three external proposals. |
| HANDOFF-1 | When the salesperson explicitly requests communication, creates an evidence-bound `outreach_handoff_packet` with allowed/prohibited claims and scope; it does not draft a message. |
| RECORD-1 | Preserves route reviews, direction records, customer records, evidence, risk state, and salesperson-owned fields; requires schema migration for the old 11-sheet template and claims a write only after reopening verification. |
| REPLY-1 | A received or suspected reply stops development work and routes saved context to `foreign-trade-customer-operations`. |

A hard-boundary failure is material even when the research itself is polished.
