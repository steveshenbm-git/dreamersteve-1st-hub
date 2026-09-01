# Workbook, interaction evidence, and due review

## Source-of-truth boundary

The local customer workbook or designated customer store owns customer state. The workflow director's salesperson workbench is a projection and decision surface. Neither a candidate nor a workbench approval proves an actual interaction.

Operations may propose a state update only from a validated handoff or bound actual-interaction evidence. Writes still require the relevant named-workbook authorization and reopen validation after saving.

## Customer-thread snapshot

```text
customer_thread_snapshot_v1:
  company_id
  customer_id
  source_store_reference
  source_store_sha256
  source_record_fingerprint
  latest_actual_touch_id
  latest_actual_sent_at
  latest_inbound_reference
  response_state
  risk_gate_status
  stop_state
  next_action
  next_action_date
  open_questions
  freshness: current | stale | unknown
```

The snapshot is a read-only projection, not an independent truth store. `freshness != current` blocks downstream communication.

## Actual interaction

Only `interaction_evidence_packet` may support actual send or actual reply state. Actual content/reference, content hash, channel, actual time, and source evidence are mandatory. A candidate, approval, planned date, draft date, open/read signal, or click signal is insufficient.

If an interaction occurred outside the workflow, record the actual evidence without inventing a prior candidate, approval, or planned send. Preserve those earlier fields as absent.

## Due review

`tools/foreign_trade_due_draft.py` remains a read-only eligibility reviewer and returns `daily_due_draft_review`. It may identify due records only when actual-send basis, no reply, no stop/risk pause, no unreviewed candidate, and new value or a validation question are present.

The review enters `account_operation`. It does not create a communication brief, candidate, workbook write, or send action. Customer operations rechecks the current thread and obtains a new draft-request receipt before any communication handoff.

## Isolation and archive

Different companies use different stable `company_id` values and data roots. Only actual sent/received messages and actual attachments enter the formal correspondence archive. AI analysis, operations decisions, briefs, candidates, revisions, and approval receipts remain internal work materials.
