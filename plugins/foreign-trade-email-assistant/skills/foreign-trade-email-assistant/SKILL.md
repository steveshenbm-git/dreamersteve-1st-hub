---
name: foreign-trade-email-assistant
description: Use when an older workflow explicitly invokes the legacy foreign-trade email assistant for a complete thread or an existing-candidate revision.
---

# Foreign Trade Email Assistant

## Compatibility role

This skill is a compatibility router, not an independent email-writing workflow. 不再独立起草完整线程回复.

## Route

- Complete customer thread, received or suspected reply, new cold outreach, follow-up, account message, or quality/contract/payment issue -> return to `foreign-trade-workflow-director`.
- The workflow director captures the input as a registered transition and routes it to `foreign-trade-customer-operations` for thread state and business decision.
- Customer operations may then issue a bound `communication_brief_packet` to `foreign-trade-customer-communication`.
- A revision of an existing communication candidate may use `bounded_revision` only when the prior candidate reference/hash, acceptance receipt, and confirmed revision request are supplied.

## Hard boundaries

- Do not accept a raw thread as a communication brief.
- Do not create an external draft, recommendation, customer state, communication brief, actual send, or reply fact.
- Do not send or archive anything.
- If a revision changes product, price, delivery, liability, compensation, warranty, contract position, customer priority, channel permission, or risk strategy, return it to customer operations.

The old standalone drafting references are removed so this router cannot become a second source of wording authority. The workflow director, customer operations, and customer communication contracts govern current behavior.
