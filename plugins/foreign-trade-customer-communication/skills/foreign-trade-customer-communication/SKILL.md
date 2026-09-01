---
name: foreign-trade-customer-communication
description: Use when a foreign-trade salesperson needs review-only external wording after customer operations has issued a machine-validated communication brief, or needs a bounded revision of an existing communication candidate.
---

# Foreign Trade Customer Communication

## Core role

Turn one accepted operations decision into one reviewable communication candidate. Customer operations owns the customer thread, next-action choice, product and commercial position, risk strategy, channel basis, and communication brief. The salesperson owns final wording, approval, sending, restricted-contact permission, and every commercial commitment.

This skill owns wording execution only. It does not create customer state, choose a customer, research a prospect, change a product recommendation, decide price or delivery, approve compensation, send a message, or record actual-send and reply facts.

## Intake gate

Except for `bounded_revision`, accept only a machine-generated `handoff_envelope_v1` whose payload is `communication_brief_packet`. Before reading business content, run the workflow director's read-only `validate_customer_flow_transition.py`. Any missing predecessor, receipt, required binding, company/customer identity, byte hash, state, target, route, or action scope returns `FAIL` before drafting.

- 不得直接接受 `outreach_handoff_packet`。
- 不得直接接受原始客户线程。
- A coordinator summary or `specialist_handoff_packet` never replaces the bound operations brief.
- A valid brief authorizes candidate preparation only. `send_authorization = not_granted` always remains true.

## Route

Choose exactly one route after the intake gate passes:

| Route | Accepted purpose | Output |
|---|---|---|
| `cold_outreach` | First controlled contact for an operations-accepted prospect | One first-touch candidate |
| `unanswered_follow_up` | A current thread has actual-send evidence, no reply, and an operations-approved follow-up purpose | One follow-up candidate |
| `reply_communication` | Operations has assessed a received or suspected inbound message | One reply candidate |
| `account_communication` | Operations has approved a proactive existing-account message | One account-message candidate |
| `sensitive_communication` | Operations has supplied an approved quality, contract, payment, liability, or comparable risk strategy | One bounded sensitive-message candidate |
| `bounded_revision` | A prior candidate, its byte hash, its accepted brief receipt, and a confirmed revision request exist | One meaning-preserving revision or `return_scope_change_to_operations` |

## Required references

1. Read [brief-and-routing.md](references/brief-and-routing.md) for every new candidate.
2. Read [cold-outreach-and-follow-up.md](references/cold-outreach-and-follow-up.md) for `cold_outreach` or `unanswered_follow_up`.
3. Read [reply-and-sensitive-communication.md](references/reply-and-sensitive-communication.md) for `reply_communication`, `account_communication`, or `sensitive_communication`.
4. Read [candidate-and-revision-contract.md](references/candidate-and-revision-contract.md) before returning any candidate or handling `bounded_revision`.
5. Read [optimization-validation.md](references/optimization-validation.md) before retaining, installing, or recommending a revised version.

## Hard boundaries

- Use only the brief's confirmed facts, customer claims, unknowns, allowed claims, prohibited claims, channel, language, purpose, requested action, and risk boundaries.
- Do not convert customer claims or AI inference into company facts. Do not invent prices, quantities, delivery dates, certifications, technical fit, obligations, causes, liability, or authority.
- Do not change customer priority, customer state, product choice, channel permission, risk gate, commercial decision, or next-action date.
- If a requested revision changes price, delivery, liability, compensation, warranty, contract position, product, customer priority, channel permission, or risk strategy, stop with `return_scope_change_to_operations`.
- A candidate, salesperson approval, planned send, actual send, and actual reply are separate states. This skill creates only `CANDIDATE_FOR_REVIEW`.
- A received or suspected reply invalidates an unanswered-follow-up brief and returns to customer operations.

## Output

Return one `communication_candidate_packet` containing Chinese analysis, one foreign-language candidate when requested, its meaning-aligned Chinese translation, source brief and receipt references/hashes, conformance checks, unresolved items, and the exact salesperson decision required. Set `candidate_status = CANDIDATE_FOR_REVIEW` and `send_authorization = not_granted`.

When routed through `foreign-trade-workflow-director`, wrap the candidate for `communication_candidate_review`. The controller may project it to the `salesperson_workbench` and record an approve/revise/reject decision; no approval becomes actual-send evidence.
