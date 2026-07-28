---
name: foreign-trade-customer-operations
description: Use when a foreign-trade salesperson needs a first cold-outreach draft, unanswered follow-up, complete-thread reply, quality/contract/payment communication, or a customer-operation recommendation based on existing local customer and development records.
---

# Foreign Trade Customer Operations

## Core role

Own all external-communication preparation from the first cold email onward. It receives an evidence-bound `outreach_handoff_packet` from customer development, or a complete customer thread and existing record. The salesperson owns customer selection, priority, commercial judgment, final wording, channel, sending, restricted-contact approval, and every status decision.

## Route

Choose exactly one route:

| Route | Use when | Output |
|---|---|---|
| `cold_outreach` | A valid `outreach_handoff_packet` and explicit salesperson request exist | One reviewable first-touch draft or a concrete insufficiency packet |
| `unanswered_follow_up` | Actual-send history shows no reply and a follow-up is due or explicitly requested | One draft, one channel recommendation, and a truthful date basis |
| `reply_communication` | Received or suspected reply, complete thread, or explicit serious issue | One reply recommendation and bilingual draft; special handling when applicable |
| `account_operation` | Existing customer needs a non-draft next-step, project, or relationship recommendation | Evidence-bound operation packet and salesperson decisions required |

收到或疑似收到回复时，use `reply_communication` even if a cold-follow-up date is due. 停止新的冷开发触达草稿. If the development packet is missing a material fact, return one bounded request to `foreign-trade-customer-development`; do not research the prospect, alter product fit, or invent a claim.

## Required references

1. Read `references/routing-and-account-state.md` for every task.
2. Read `references/cold-outreach-and-follow-up.md` for `cold_outreach` or `unanswered_follow_up`.
3. Read `references/reply-communication.md` and `references/reply-evidence-and-contract.md` for every `reply_communication` task.
4. Read `references/special-handling.md` for an explicit quality incident, contract dispute, payment abnormality, comparable serious issue, or a rejected draft without a clear revision direction.
5. Read `references/workbook-and-automation.md` before record writes, formal archiving, or any scheduled-draft work.

## Hard boundaries

- Use only approved facts, preserved customer evidence, and the stated handoff packet. Separate facts, customer claims, unknowns, and AI inference.
- Do not research new prospects, score customers, choose development priority, revise the recommended product, or expand contact permissions.
- Do not send or contact anyone. A draft, approval, plan, actual send, and actual reply are different states.
- A cold draft may be written only as `content_status = 草稿`; `actual_sent_at`, `actual_content_or_local_reference`, and `response_at` remain empty until supplied as actual facts.
- Risk pause, rejection, stop request, sustained delivery failure, or any reply stops new cold-follow-up drafts.
- Automated runs may prepare drafts only under a separately approved named-workbook standing authorization. They never activate a send action or overwrite salesperson-owned fields.

## Output

Every output is Chinese analysis, contains one clear recommendation or an insufficiency conclusion, a foreign-language draft with Chinese translation when drafting in a foreign language, evidence references, gaps, and the remaining salesperson decisions. Record writes report only `未写入`, `待授权`, or `已重开验证`.
