# Brief intake and routing

## Accepted brief

Every new communication task starts from this operations-owned business packet:

```text
communication_brief_packet:
  company_id
  customer_id
  brief_id
  customer_thread_reference
  customer_thread_sha256
  source_operations_decision_reference
  source_operations_decision_sha256
  communication_purpose
  requested_customer_action
  channel
  language
  confirmed_facts
  customer_claims
  unknowns
  allowed_claims
  prohibited_claims
  commercial_decisions
  risk_gate_status
  draft_scope
  salesperson_request
  customer_flow_link_v1
```

The packet must be wrapped by `handoff_envelope_v1` and pass `validate_customer_flow_transition.py`. The flow link binds the immediate operations decision, the accepted prior handoff receipt, the current customer-thread snapshot, the salesperson's draft-request receipt, and the exact target route.

## Routing

- First controlled prospect contact -> `cold_outreach`.
- No-reply follow-up with actual-send evidence -> `unanswered_follow_up`.
- Received or suspected reply -> `reply_communication` and never a follow-up.
- Proactive message for an existing account -> `account_communication`.
- Quality, contract, payment, liability, compensation, warranty, or comparable risk -> `sensitive_communication`.

If the purpose is missing or several routes appear necessary, return `invalid_communication_brief_packet` to customer operations. Do not execute several routes in one answer.

## Freshness and stop conditions

Stop when the source acceptance receipt is absent, the thread snapshot is stale, a required actual-send or inbound-message binding is absent, the draft-request receipt is not confirmed, the risk gate conflicts with the requested action, or the brief asks for a fact or decision outside operations ownership.

Do not repair a failed brief by searching, guessing, copying an older thread, or asking the communication skill to decide the missing business position.
