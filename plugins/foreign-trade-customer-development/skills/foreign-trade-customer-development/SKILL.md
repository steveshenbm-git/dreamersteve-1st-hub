---
name: foreign-trade-customer-development
description: Use when a foreign-trade salesperson needs route-led prospecting-direction compilation, direction validation, evidence-bound candidate-company research, company or contact due diligence, or a development handoff package before any external communication is drafted.
---

# Foreign Trade Customer Development

## Core role

Find and research who may be worth developing. The salesperson owns target selection, customer value, priority, commercial judgment, final product decision, contact approval, and every external message. This skill never writes an external email, sends a message, or runs a scheduled search. When routed by `foreign-trade-workflow-director`, keep this skill's evidence work in the machine backend and return a traceable business projection for its `salesperson_workbench`.

## Route

Choose exactly one `task_route` before researching:

| Route | Entry condition | Output and stop point |
|---|---|---|
| `route_portfolio_review` | A registered `company_route_pool_packet` needs comparison, readiness requests, and salesperson selection | `route_portfolio_review_packet`; stop for missing readiness views or a salesperson route decision |
| `direction_compilation` | One route review has `salesperson_route_decision = 选择编译` and passes the current readiness gates | `development_direction_packet`; stop for public validation and a direction decision |
| `direction_validation` | A direction draft needs public or explicitly authorized-source validation, including a route lead accepted only for limited validation | `direction_validation_packet`; validate seed/holdout independence and do not collect a customer pool |
| `candidate_scan` | Compatibility entry for a named-company initial check, or for a confirmed direction when the user has not named the collection phase | Route to exactly one of `candidate_task_export`, `candidate_batch_intake`, or `candidate_review`; never combine collection and review invisibly |
| `candidate_task_export` | `direction_status = 已确认可扫描` and a salesperson-declared scope need a bounded collection task | `candidate_collection_task`; stop without collecting or judging companies |
| `candidate_batch_intake` | An approved executor returns one collection batch for a current task | Append-only `raw_candidate_batch` intake result; stop without qualification conclusions |
| `candidate_review` | One or more accepted raw batches need independent evidence review | Qualified, excluded, and `UNVERIFIED` companies separately; stop for salesperson screening |
| `direction_review` | The salesperson asks to review saved scan results for one direction | `direction_feedback_packet`; do not change the direction status |
| `full_due_diligence` | `salesperson_classification = 潜力客户` **and** salesperson explicitly starts it | Full evidence-bound research and one `project_recommendation` or an insufficiency conclusion |
| `outreach_handoff` | Salesperson selected the company and explicitly asks to prepare communication | Bound `outreach_handoff_packet` for `foreign-trade-customer-operations`, `target_route = outreach_activation`; no email body |
| `reply_handoff` | A received or suspected customer reply appears while this skill is active | Stop development work and hand the saved context to `foreign-trade-customer-operations`, `target_route = interaction_intake` |

`direction_discovery` is a compatibility alias for `direction_compilation`; it is not an alternate product-led discovery route. Both names use the same producer-registry preflight, route-review record, readiness view, and salesperson decision gate.

This skill does not independently infer an industry from product facts. It verifies one `company_route_pool_packet`, presents its routes without a composite score, and compiles only the route the salesperson selected into a reusable, testable enterprise-identification rule. If no valid route-pool packet exists, return the task to `industry-application-map-builder`; do not recreate the missing industry/application map here. A direction is not eligible for scanning until the salesperson records `direction_status = 已确认可扫描`.

命名公司初查 remains an independent `candidate_scan` entry: it does not require a prebuilt route pool, but it cannot upgrade product fit, industry route, material use, purchasing role, or demand into fact. For a direction-led pool, `candidate_scan` is only a compatibility router; the task, raw intake, and independent review must remain separately traceable.

## Required references

1. Read `references/research-and-sources.md` before direction work or research.
2. Read `references/evidence-contacts-and-risk.md` before conclusions or contact work.
3. Read `references/opportunity-and-outreach.md` before a project recommendation or outreach handoff.
4. Read `references/workbook-and-handoff.md` before a record update or handoff.
5. Read [optimization-validation.md](references/optimization-validation.md) before retaining or installing an optimized skill version.

## Hard boundaries

- Before route review or direction compilation, run `scripts/verify_route_pool_packet.py` with the trusted map root and expected `company_id`. Reject missing, copied, stale, superseded, cross-company, hash-mismatched, snapshot-stale, or unregistered packets.
- For direction work, consume only a validated `company_route_pool_packet`, a `route_portfolio_review` record, and the approved product references carried by its selected route. Preserve route, source, evidence, hash, conflict, and gap fields; never reconstruct missing route evidence from model knowledge.
- A `路线线索` may enter only `limited_direction_validation` when the packet carries `customer_discovery_readiness = ready_for_limited_direction_validation` and one accepted business-route closure. Preserve technical/regulatory unknowns; prohibit product recommendation, product-fit/compliance claims, and candidate scanning. `violated`, `conflicted`, or a known-limit conflict blocks that product track.
- Limited validation must contain both `application_seed` and independently sourced `direction_holdout` evidence. Dependency groups, source references, and observed companies may not overlap. Run `scripts/validate_direction_validation.py` before presenting the result.
- Commercial readiness is a read-only decision input from `company-product-knowledge-builder`. It never changes `map_route_status`, creates a route, proves market demand, or selects a route. The salesperson owns `salesperson_route_decision`, its basis, and date.
- Do not generate a composite customer score, final development priority, industry certainty, or unsupported product claim.
- External evidence validates or refutes a direction; absent public evidence does not prove no market. It limits the task to validation until the salesperson decides otherwise.
- A candidate pool includes only companies with company- or brand-specific direct product evidence of current use, sale, or clear need for a similar approved material or effect. Generic industry use, unlinked third-party claims, and inference are excluded.
- A completed direction-led `candidate_review`, or a named-company `candidate_scan`, returns every qualified company in its declared scope; do not cap, rank, or claim market exhaustion.
- A collection executor receives only `candidate_collection_task` and may only 追加 an `append_only: true` `raw_candidate_batch`. It cannot write PASS/FAIL/UNVERIFIED, direction status, customer classification, priority, or the `salesperson_workbench`, and it cannot overwrite an old batch.
- `candidate_batch_intake` checks task identity, current hashes, declared scope, batch shape, source presence, and duplicate observations only. It must not decide qualification. `candidate_review` is a separate evidence judgment by this skill and must not inherit the collector's labels as facts.
- Candidate outcomes may support a direction review, but the AI must not convert counts, positive examples, or missing public evidence into a direction-status decision.
- `project_recommendation` means what to recommend to one researched company. It is distinct from `development_direction`, which defines what kind of company to search for.
- Do not prepare an external email, follow-up message, channel message, cadence, or send action. Customer operations first owns thread activation and the business decision; `foreign-trade-customer-communication` may draft only from its later bound operations brief.
- 不得直接交给 `foreign-trade-customer-communication`. Every customer handoff must carry `customer_flow_link_v1` and pass the workflow director's `validate_customer_flow_transition.py` at the receiving route.
- Stop normal recommendations at the risk gate. Do not overwrite salesperson-owned classification, notes, decision, approval, or date fields.
- On any reply or suspected reply, stop development outreach work and hand off; never treat an unverified inbound message as a verified reply or success.

## Output

- `route_portfolio_review_packet` contains the verified `route_packet_reference`, `route_packet_sha256`, `producer_registry_reference`, input snapshot, one non-scored review record per upstream route, any `development_readiness_request`, returned readiness-view references, unresolved conditions, and exactly one salesperson-owned route decision per reviewed route: `选择编译`, `继续核实`, `暂缓`, or `淘汰`.
- `development_readiness_request` is an explicit handoff with `next_owner: company-product-knowledge-builder`; this skill stops that route until a traceable `development_readiness_view` is returned. Skills are not callable background services.
- `development_direction_packet` contains: `source_route_review_id`; `source_route_candidate_id`; approved product reference; product boundary; application/industry route boundary; observable enterprise rule; later candidate direct-evidence rule; exclusions; unresolved conditions; external-evidence posture; declared scope; and exactly one salesperson decision request: `确认可扫描`, `继续核实`, `暂缓`, or `淘汰`.
- `direction_validation_packet` states supporting evidence, refuting evidence, access limits, seed/holdout roles, source dependency groups, and whether the direction remains `待外部核实` or can be presented to the salesperson for a scan decision. It contains no customer pool and its own `salesperson_scan_authorization` remains `blocked`.
- `candidate_task_export` returns one read-only `candidate_collection_task` with the current direction hash, declared scope, observable enterprise rule, direct-evidence rule, exclusions, prohibited inference, and `raw_candidate_batch` output contract.
- `candidate_batch_intake` returns an accepted or rejected intake record. Accepted batches remain append-only raw observations and do not create customer records.
- `candidate_review` returns `PASS`, `FAIL`, and `UNVERIFIED` companies separately, with evidence, counterevidence, scope gaps, and source batch IDs, then stops for salesperson screening. The compatibility `candidate_scan` must disclose which one of these phases it actually performed.
- `direction_review` returns saved supporting outcomes, refuting outcomes, uncovered scope, and one salesperson decision request: `保留`, `调整`, `暂缓`, or `淘汰`; it never rewrites `direction_status` by itself.
- `full_due_diligence` may provide one final `project_recommendation` or a concrete evidence-insufficiency conclusion; it never writes a communication draft.
- `outreach_handoff_packet` contains only evidence-bound operations inputs: `company_id`, customer identity, approved product references, allowed and prohibited claims, contact evidence and permission, outreach scope, actual-send facts if any, risk status, gaps, the salesperson's explicit request, and `customer_flow_link_v1`. The machine-owned `handoff_envelope_v1` holds the only `handoff_id`, exact payload reference/hash, target and empty write scope; this skill does not place an independent `handoff_id` inside the payload.
- Every output is Chinese analysis, identifies what remains the salesperson's decision, and reports a truthful `workbook_status` of `未写入`, `待授权`, or `已重开验证`.
- If invoked through `foreign-trade-workflow-director`, also return `specialist_return_packet` plus a minimal `salesperson_workbench` projection. The coordinator may record the salesperson decision after authorization; this skill does not directly overwrite the six-page business front.
