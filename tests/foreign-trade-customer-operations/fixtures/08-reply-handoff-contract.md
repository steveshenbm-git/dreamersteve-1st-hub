# Reply handoff contract

Customer development supplies a bound `development_reply_to_operations_intake` package containing `customer_operations_handoff`, the inbound-message evidence binding, trigger channel, trigger touch, actual-send history, sender-identity gaps, risk state, and open questions.

PASS only if operations validates the exact predecessor, immediately pauses cold activity, records `INTERACTION_ACCEPTED`, preserves gaps, and returns one operations decision or a bounded missing-input result. If a reply candidate is needed, only a later accepted `communication_brief_packet` may invoke communication; operations must not restart prospect research or write the reply.
