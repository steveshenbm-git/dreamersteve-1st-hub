---
name: foreign-trade-customer-development
description: Use when a foreign-trade salesperson needs route-led prospecting-direction compilation, direction validation, evidence-bound candidate-company research, company or contact due diligence, or a development handoff package before any external communication is drafted.
---

# Foreign Trade Customer Development

## Core role

Find and research who may be worth developing. The salesperson owns target selection, customer value, priority, commercial judgment, final product decision, contact approval, and every external message. This skill never writes an external email, sends a message, or runs a scheduled search.

## Route

Choose exactly one `task_route` before researching:

| Route | Entry condition | Output and stop point |
|---|---|---|
| `route_portfolio_review` | A registered `company_route_pool_packet` needs comparison, readiness requests, and salesperson selection | `route_portfolio_review_packet`; stop for missing readiness views or a salesperson route decision |
| `direction_compilation` | One route review has `salesperson_route_decision = 选择编译` and passes the current readiness gates | `development_direction_packet`; stop for public validation and a direction decision |
| `direction_validation` | A direction draft needs public or explicitly authorized-source validation | `direction_validation_packet`; do not collect a customer pool |
| `candidate_scan` | Named company, or `direction_status = 已确认可扫描` and a salesperson-declared scope | Candidate pool or initial check; stop for salesperson screening |
| `direction_review` | The salesperson asks to review saved scan results for one direction | `direction_feedback_packet`; do not change the direction status |
| `full_due_diligence` | `salesperson_classification = 潜力客户` **and** salesperson explicitly starts it | Full evidence-bound research and one `project_recommendation` or an insufficiency conclusion |
| `outreach_handoff` | Salesperson selected the company and explicitly asks to prepare communication | `outreach_handoff_packet` for `foreign-trade-customer-operations`; no email body |
| `reply_handoff` | A received or suspected customer reply appears while this skill is active | Stop development work and hand the saved context to `foreign-trade-customer-operations` |

`direction_discovery` is a compatibility alias for `direction_compilation`; it is not an alternate product-led discovery route. Both names use the same producer-registry preflight, route-review record, readiness view, and salesperson decision gate.

This skill does not independently infer an industry from product facts. It verifies one `company_route_pool_packet`, presents its routes without a composite score, and compiles only the route the salesperson selected into a reusable, testable enterprise-identification rule. If no valid route-pool packet exists, return the task to `industry-application-map-builder`; do not recreate the missing industry/application map here. A direction is not eligible for scanning until the salesperson records `direction_status = 已确认可扫描`.

命名公司初查 remains an independent `candidate_scan` entry: it does not require a prebuilt route pool, but it cannot upgrade product fit, industry route, material use, purchasing role, or demand into fact.

## Required references

1. Read `references/research-and-sources.md` before direction work or research.
2. Read `references/evidence-contacts-and-risk.md` before conclusions or contact work.
3. Read `references/opportunity-and-outreach.md` before a project recommendation or outreach handoff.
4. Read `references/workbook-and-handoff.md` before a record update or handoff.

## Hard boundaries

- Before route review or direction compilation, run `scripts/verify_route_pool_packet.py` with the trusted map root and expected `company_id`. Reject missing, copied, stale, superseded, cross-company, hash-mismatched, snapshot-stale, or unregistered packets.
- For direction work, consume only a validated `company_route_pool_packet`, a `route_portfolio_review` record, and the approved product references carried by its selected route. Preserve route, source, evidence, hash, conflict, and gap fields; never reconstruct missing route evidence from model knowledge.
- Commercial readiness is a read-only decision input from `company-product-knowledge-builder`. It never changes `map_route_status`, creates a route, proves market demand, or selects a route. The salesperson owns `salesperson_route_decision`, its basis, and date.
- Do not generate a composite customer score, final development priority, industry certainty, or unsupported product claim.
- External evidence validates or refutes a direction; absent public evidence does not prove no market. It limits the task to validation until the salesperson decides otherwise.
- A candidate pool includes only companies with company- or brand-specific direct product evidence of current use, sale, or clear need for a similar approved material or effect. Generic industry use, unlinked third-party claims, and inference are excluded.
- A candidate scan returns every qualified company in its declared scope; do not cap, rank, or claim market exhaustion.
- Candidate outcomes may support a direction review, but the AI must not convert counts, positive examples, or missing public evidence into a direction-status decision.
- `project_recommendation` means what to recommend to one researched company. It is distinct from `development_direction`, which defines what kind of company to search for.
- Do not prepare an external email, follow-up message, channel message, cadence, or send action. Those belong to `foreign-trade-customer-operations` after `outreach_handoff`.
- Stop normal recommendations at the risk gate. Do not overwrite salesperson-owned classification, notes, decision, approval, or date fields.
- On any reply or suspected reply, stop development outreach work and hand off; never treat an unverified inbound message as a verified reply or success.

## Output

- `route_portfolio_review_packet` contains the verified `route_packet_reference`, `route_packet_sha256`, `producer_registry_reference`, input snapshot, one non-scored review record per upstream route, any `development_readiness_request`, returned readiness-view references, unresolved conditions, and exactly one salesperson-owned route decision per reviewed route: `选择编译`, `继续核实`, `暂缓`, or `淘汰`.
- `development_readiness_request` is an explicit handoff with `next_owner: company-product-knowledge-builder`; this skill stops that route until a traceable `development_readiness_view` is returned. Skills are not callable background services.
- `development_direction_packet` contains: `source_route_review_id`; `source_route_candidate_id`; approved product reference; product boundary; application/industry route boundary; observable enterprise rule; later candidate direct-evidence rule; exclusions; unresolved conditions; external-evidence posture; declared scope; and exactly one salesperson decision request: `确认可扫描`, `继续核实`, `暂缓`, or `淘汰`.
- `direction_validation_packet` states supporting evidence, refuting evidence, access limits, and whether the direction remains `待外部核实` or can be presented for `已确认可扫描`. It contains no customer pool.
- `candidate_scan` returns qualified and excluded companies separately, with evidence and gaps, then stops for salesperson screening.
- `direction_review` returns saved supporting outcomes, refuting outcomes, uncovered scope, and one salesperson decision request: `保留`, `调整`, `暂缓`, or `淘汰`; it never rewrites `direction_status` by itself.
- `full_due_diligence` may provide one final `project_recommendation` or a concrete evidence-insufficiency conclusion; it never writes a communication draft.
- `outreach_handoff_packet` contains only evidence-bound communication inputs: customer identity, approved product references, allowed and prohibited claims, contact evidence and permission, outreach scope, actual-send facts if any, risk status, gaps, and the salesperson's explicit request.
- Every output is Chinese analysis, identifies what remains the salesperson's decision, and reports a truthful `workbook_status` of `未写入`, `待授权`, or `已重开验证`.
