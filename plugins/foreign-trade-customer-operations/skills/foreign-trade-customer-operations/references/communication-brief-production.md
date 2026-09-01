# Communication brief production

## Gate

Produce a brief only when all are present and current:

- accepted immediate input receipt
- current `customer_thread_snapshot_v1`
- `operations_decision_packet.decision_state = OPERATION_DECISION_READY`
- one exact communication route and purpose
- confirmed salesperson draft-request receipt
- route-specific actual-send, inbound-message, or risk-review binding
- allowed/prohibited claims and risk gate

The brief is a business instruction to `foreign-trade-customer-communication`, not external copy and not a send authorization.

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

Bind the packet with `bind_customer_flow_transition.py` using the exact registered operations-to-communication transition. Then validate the new package with `validate_customer_flow_transition.py`. A valid envelope alone is insufficient.

## Routes

- `outreach_activation` -> communication `cold_outreach`
- `account_operation` with actual-send evidence and no reply -> `unanswered_follow_up`
- `interaction_intake` with received or suspected inbound content -> `reply_communication`
- `account_operation` for a proactive existing-account purpose -> `account_communication`
- `serious_case_operation` -> `sensitive_communication`

Do not combine routes. Missing predecessor acceptance, thread freshness, human request, or route-specific binding returns `communication_brief_blocked_packet` and stops.
