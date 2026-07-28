---
name: foreign-trade-customer-development
description: Use when a foreign-trade salesperson needs product-led prospecting-direction discovery, direction validation, evidence-bound candidate-company research, company or contact due diligence, or a development handoff package before any external communication is drafted.
---

# Foreign Trade Customer Development

## Core role

Find and research who may be worth developing. The salesperson owns target selection, customer value, priority, commercial judgment, final product decision, contact approval, and every external message. This skill never writes an external email, sends a message, or runs a scheduled search.

## Route

Choose exactly one `task_route` before researching:

| Route | Entry condition | Output and stop point |
|---|---|---|
| `direction_discovery` | Salesperson manually asks to explore from approved local product facts | `development_direction_packet`; stop for a decision |
| `direction_validation` | A direction draft needs public or explicitly authorized-source validation | `direction_validation_packet`; do not collect a customer pool |
| `candidate_scan` | Named company, or `direction_status = 已确认可扫描` and a salesperson-declared scope | Candidate pool or initial check; stop for salesperson screening |
| `direction_review` | The salesperson asks to review saved scan results for one direction | `direction_feedback_packet`; do not change the direction status |
| `full_due_diligence` | `salesperson_classification = 潜力客户` **and** salesperson explicitly starts it | Full evidence-bound research and one `project_recommendation` or an insufficiency conclusion |
| `outreach_handoff` | Salesperson selected the company and explicitly asks to prepare communication | `outreach_handoff_packet` for `foreign-trade-customer-operations`; no email body |
| `reply_handoff` | A received or suspected customer reply appears while this skill is active | Stop development work and hand the saved context to `foreign-trade-customer-operations` |

`direction_discovery` is not an industry list or a supply-chain map. It turns approved product boundaries into a reusable, testable rule for identifying target enterprises. A direction is not eligible for scanning until the salesperson records `direction_status = 已确认可扫描`.

## Required references

1. Read `references/research-and-sources.md` before direction work or research.
2. Read `references/evidence-contacts-and-risk.md` before conclusions or contact work.
3. Read `references/opportunity-and-outreach.md` before a project recommendation or outreach handoff.
4. Read `references/workbook-and-handoff.md` before a record update or handoff.

## Hard boundaries

- Use approved local product facts only. Preserve the source, evidence state, publication date or `未知`, observation date, conflict, and gap.
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

- `development_direction_packet` contains: approved product reference; product boundary; observable enterprise rule; later candidate direct-evidence rule; exclusions; unresolved conditions; external-evidence posture; declared scope; and exactly one salesperson decision request: `确认可扫描`, `继续核实`, `暂缓`, or `淘汰`.
- `direction_validation_packet` states supporting evidence, refuting evidence, access limits, and whether the direction remains `待外部核实` or can be presented for `已确认可扫描`. It contains no customer pool.
- `candidate_scan` returns qualified and excluded companies separately, with evidence and gaps, then stops for salesperson screening.
- `direction_review` returns saved supporting outcomes, refuting outcomes, uncovered scope, and one salesperson decision request: `保留`, `调整`, `暂缓`, or `淘汰`; it never rewrites `direction_status` by itself.
- `full_due_diligence` may provide one final `project_recommendation` or a concrete evidence-insufficiency conclusion; it never writes a communication draft.
- `outreach_handoff_packet` contains only evidence-bound communication inputs: customer identity, approved product references, allowed and prohibited claims, contact evidence and permission, outreach scope, actual-send facts if any, risk status, gaps, and the salesperson's explicit request.
- Every output is Chinese analysis, identifies what remains the salesperson's decision, and reports a truthful `workbook_status` of `未写入`, `待授权`, or `已重开验证`.
