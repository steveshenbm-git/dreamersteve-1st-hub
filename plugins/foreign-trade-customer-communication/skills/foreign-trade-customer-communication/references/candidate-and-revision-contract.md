# Candidate and bounded revision contract

## Candidate packet

```text
communication_candidate_packet:
  company_id
  customer_id
  candidate_id
  flow_state: COMMUNICATION_CANDIDATE_READY
  accepted_input_handoff_id
  accepted_input_payload_reference
  accepted_input_payload_sha256
  source_brief_reference
  source_brief_sha256
  accepted_brief_receipt_reference
  accepted_brief_receipt_sha256
  source_route
  chinese_recommendation
  customer_language_candidate
  meaning_aligned_chinese_translation
  evidence_and_claim_state
  conformance_checks
  unresolved_items
  salesperson_decision_required
  candidate_status: CANDIDATE_FOR_REVIEW
  send_authorization: not_granted
  customer_flow_link_v1
```

The candidate returns through the registered `communication_candidate_review` transition. The workflow director records approve, revise, or reject separately. Approval does not add `actual_sent_at`, actual content, channel, or reply state.

## Bounded revision intake

`bounded_revision` requires a `revision_brief_packet` bound to:

- `prior_candidate_reference`
- `prior_candidate_sha256`
- the prior candidate's acceptance receipt
- `revision_request_receipt`
- protected meaning and fields that must remain unchanged

The revision may improve clarity, tone, length, order, grammar, translation alignment, or the exact wording requested by the salesperson while preserving the accepted business position.

Any requested change to 价格、交期、责任、赔偿、保修、合同立场、产品、客户优先级、渠道权限或风险策略 returns `return_scope_change_to_operations`. Do not silently alter the prior brief or invent a new operations decision.

Return a new candidate ID and preserve a reference to the superseded candidate. Never overwrite the old candidate.

The director's source packet for this route is:

```text
revision_decision_packet:
  company_id
  customer_id
  revision_decision_id
  decision_state: REVISION_REQUEST_CONFIRMED
  accepted_input_handoff_id
  accepted_input_payload_reference
  accepted_input_payload_sha256
  prior_candidate_reference
  prior_candidate_sha256
  revision_request_receipt_reference
  revision_request_receipt_sha256
```
