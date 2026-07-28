# Reply handoff contract

Customer development supplies a `customer_operations_handoff` containing a saved inbound message, trigger channel, trigger touch, confirmed facts, actual-send history, sender-identity gaps, risk state, and open questions.

PASS only if customer operations accepts the named packet, immediately chooses `reply_communication`, preserves the identity gap, and requests only missing material fields through a bounded `reply_return_packet` without restarting prospect research.
