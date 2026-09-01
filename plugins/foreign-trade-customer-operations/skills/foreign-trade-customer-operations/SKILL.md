---
name: foreign-trade-customer-operations
description: Use when a foreign-trade salesperson needs a customer thread activated or updated, one evidence-bound account-operation decision, a serious-case business strategy, or an operations-owned communication brief.
---

# Foreign Trade Customer Operations

## Core role

Own the customer thread and the business decision that must precede external wording. Receive machine-bound development handoffs or actual-interaction evidence, establish the current thread state, choose one next operation, handle serious-case strategy, and issue a `communication_brief_packet` only after the required human request is present.

Customer communication owns candidate wording. This skill 不生成任何对外正文. The salesperson owns customer selection, value, priority, product and commercial decisions, final wording, channel, sending, restricted-contact permission, and every actual status decision.

## Route

Choose exactly one route:

| Route | Entry condition | Output and stop point |
|---|---|---|
| `outreach_activation` | A valid development `outreach_handoff_packet` enters the customer stage | Accepted customer-thread snapshot plus one operations decision or a bounded return |
| `interaction_intake` | A bound development reply handoff or actual send/inbound evidence exists | Updated thread, cold-sequence stop when applicable, and one operations decision |
| `account_operation` | A current customer thread needs one non-sensitive next action | `operations_decision_packet` and any required salesperson decision |
| `serious_case_operation` | Quality, contract, payment, liability, compensation, warranty, or comparable risk needs a business position | Risk review and one approved strategy or an explicit missing-decision packet |

Received or suspected inbound content always enters `interaction_intake`, pauses the cold sequence, and takes priority over due follow-up. Missing development facts return to `foreign-trade-customer-development`; missing wording is never repaired here by drafting.

## Required references

1. Read [routing-and-account-state.md](references/routing-and-account-state.md) for every task.
2. Read [communication-brief-production.md](references/communication-brief-production.md) before requesting any external wording.
3. Read [serious-case-operation.md](references/serious-case-operation.md) for `serious_case_operation`.
4. Read [workbook-and-automation.md](references/workbook-and-automation.md) before state projection, actual-interaction intake, due review, or any write proposal.
5. Read [optimization-validation.md](references/optimization-validation.md) before retaining, installing, or recommending a revised version.

## Hard boundaries

- Before every cross-skill intake or communication-brief handoff, run `validate_customer_flow_transition.py`. Envelope-only validation is insufficient for customer flow.
- Do not accept a raw thread as a drafting input. Direct user-supplied actual messages first enter the workflow director's registered actual-interaction intake and then this skill.
- Use approved facts and preserved evidence; separate confirmed facts, customer claims, unknowns, and inference.
- Do not research new prospects, score customers, choose development priority, change product fit, expand contact permissions, or create a communication candidate.
- A business decision may choose a purpose, requested action, commercial position, risk boundary, channel basis, and date basis. It does not choose final wording or authorize sending.
- A candidate, approval, planned send, actual send, and actual reply remain distinct. Only bound actual evidence can create `actual_sent_at`, actual content, or response facts.
- A received or suspected reply pauses the cold sequence even when identity or headers remain unverified.
- `daily_due_draft_review` is eligibility evidence for `account_operation`; it cannot directly invoke communication or write a draft.

## Output

Every output is Chinese analysis and contains one current thread state, one operations recommendation or insufficiency conclusion, evidence and gaps, and the exact salesperson decision still required. When external wording is needed and all gates pass, return a bound `communication_brief_packet` to `foreign-trade-customer-communication`; never include the external body.

If invoked through `foreign-trade-workflow-director`, also return a `specialist_return_packet`. Its `salesperson_workbench` projection may update customer follow-up or risk state from verified evidence, or present a communication-brief request, but it cannot create a candidate, approval, or actual-send state.
