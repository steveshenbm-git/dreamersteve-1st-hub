# Cold outreach and unanswered follow-up

## First contact

Use the brief's approved customer scene, allowed product facts, one relevant reason for contact, and one requested customer action. Prepare one concise candidate in the approved channel and language. Do not add a second product, unapproved technical fit, social proof, urgency, discount, delivery promise, or contact permission.

If ordinary email contact is unavailable, do not select an alternate channel here. Customer operations must first return an approved channel decision and an updated brief. LinkedIn, WhatsApp, phone, and email content are channel-specific and must not be copied verbatim across channels.

## Follow-up gate

`unanswered_follow_up` requires all of:

- actual prior send content and `actual_sent_at`
- matching `customer_id` and stable prior `touch_id`
- no received or suspected reply
- current risk gate permits contact
- no stop request, sustained delivery failure, or unreviewed candidate for the same due point
- an operations-approved new value or validation question
- a confirmed draft request

Draft date, approval date, planned date, and recommended date are never actual-send evidence. Missing prior actual-send evidence returns to customer operations.

The first and second email follow-up dates remain based on the 5th and 7th workday from actual send when that cadence is the approved operations decision. Longer regular or event cadence remains operations-owned. Communication uses the supplied date basis and never recalculates or resets account cadence.

## Output

Return one candidate with a specific relation to the prior actual message. Do not produce placeholder checking-in language when the brief has no new value or open question. Any suspected reply stops this route and returns to `interaction_intake`.
