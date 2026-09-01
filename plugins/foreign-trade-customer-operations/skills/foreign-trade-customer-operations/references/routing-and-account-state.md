# Routing and customer-thread state

## Cross-skill intake

All cross-skill customer inputs require `handoff_envelope_v1` plus `customer_flow_link_v1` and must pass `validate_customer_flow_transition.py` before business content is used.

`outreach_activation` accepts only the registered `development_outreach_to_operations_activation` transition and its `outreach_handoff_packet`. A customer-selection receipt, confirmed outreach-request receipt, current development source packet, company/customer identity, and hashes are mandatory.

`interaction_intake` accepts exactly one registered source:

- `development_reply_to_operations_intake` with `customer_operations_handoff`
- `director_actual_interaction_to_operations_intake` with `interaction_evidence_packet`

The shared route does not make the payloads interchangeable. `transition_id` selects the exact predecessor and payload contract.

## Development reply handoff

```text
customer_operations_handoff:
  company_id
  customer_id
  trigger_channel
  trigger_touch_id
  response_reference
  sender_identity_status
  confirmed_context
  actual_send_history
  open_questions
  risk_gate_status
  target_skill
  salesperson_request
  customer_flow_link_v1
```

The target is `foreign-trade-customer-operations / interaction_intake`. A suspected reply is sufficient to pause cold outreach. Missing identity, headers, entity relationship, or prior-send evidence remains an explicit gap; it does not authorize treating the message as a verified reply.

## Actual interaction intake

```text
interaction_evidence_packet:
  company_id
  customer_id
  interaction_type
  touch_id
  related_touch_id
  channel
  actual_content_reference
  actual_content_sha256
  actual_at
  source_evidence_reference
  source_evidence_sha256
  prior_candidate_reference
  prior_candidate_sha256
  prior_approval_reference
  evidence_gaps
  customer_flow_link_v1
```

`prior_candidate` and `prior_approval` may be empty when a real interaction occurred outside the system. Their absence must not erase reality or fabricate earlier workflow states. Actual content, channel, time, and source evidence remain mandatory.

## State priority

Evaluate in this order:

1. received or suspected reply
2. serious risk or risk pause
3. stop/rejection request
4. sustained delivery failure
5. actual interaction evidence
6. current development handoff scope
7. due next action
8. ordinary account operation

## Operations decision

```text
operations_decision_packet:
  company_id
  customer_id
  operations_decision_id
  accepted_input_handoff_id
  accepted_input_payload_reference
  accepted_input_payload_sha256
  source_thread_reference
  source_thread_sha256
  source_state
  selected_operation
  communication_needed
  communication_route
  communication_purpose
  requested_customer_action
  approved_commercial_position
  channel_basis
  date_basis
  risk_gate_status
  missing_decisions
  salesperson_decision_required
  decision_state: OPERATION_DECISION_READY | BLOCKED
```

Choose one selected operation. If wording is needed, continue to `communication-brief-production.md`. If a material fact or decision is missing, return to its owner and stop; do not write around it.
