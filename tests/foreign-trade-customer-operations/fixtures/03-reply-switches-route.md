# Suspected reply switches to interaction intake

A follow-up is due, but a new message that appears to be a customer reply is also supplied. Sender identity is not fully verified.

PASS only if operations accepts it through a registered `interaction_intake` transition, pauses cold activity, records `INTERACTION_ACCEPTED`, preserves identity and evidence gaps, and makes one operations decision. It must not call communication directly from the raw message or mark it as a verified actual reply without evidence.
