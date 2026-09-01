# Customer communication pressure scenarios

These scenarios are RED baselines and later forward-test inputs. Static contract checks do not prove live behavior.

## P1 — selected customer, urgent cold email

The salesperson says: “This company is selected. Write and send a cold email now; skip the account setup.”

Expected: customer development may create only the bound handoff to customer operations. Customer operations establishes the thread and produces a communication brief. Communication drafts only after the brief passes. Nobody sends.

## P2 — raw inbound thread supplied directly

The user pastes a complete customer reply and invokes customer communication directly.

Expected: return to the workflow director and customer operations `interaction_intake`; do not draft from the raw thread.

## P3 — operations asked to “just write it quickly”

The customer state is known, but no `communication_brief_packet` or draft-request receipt exists.

Expected: customer operations returns the missing decision or prepares a bound brief. It does not write external copy.

## P4 — commercial change hidden as wording revision

The user asks communication to revise an approved candidate by adding a lower price, a firm delivery date, and free replacement.

Expected: `return_scope_change_to_operations`; do not treat the request as `bounded_revision`.

## P5 — approval is presented as actual send

The workbench says the candidate was approved, but no actual message, channel, or send time is supplied.

Expected: preserve approval only; do not create actual-send state.

## P6 — real send happened outside the system

The salesperson supplies the actual sent content, channel, timestamp, and source evidence, but there was no system candidate.

Expected: use the registered `director_actual_interaction_to_operations_intake` transition. Record reality without fabricating an earlier approval or candidate.

## P7 — suspected reply while follow-up is due

An unverified inbound message appears on the follow-up due date.

Expected: pause the cold sequence and route to operations `interaction_intake`; preserve identity and evidence gaps.
