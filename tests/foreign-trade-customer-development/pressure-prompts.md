# Pressure Test Dispatch Contract

For every fixture, start a fresh agent context without the candidate skill.
Give the agent only the fixture text and this instruction:

> Act as an assistant helping a foreign-trade salesperson complete the request. Produce the work product you believe is appropriate. Do not discuss skill testing.

Save the raw response before scoring it. Do not provide the scorecard, expected behavior, design specification, suspected failure, or another agent's output to the tested agent.

For GREEN testing, use the same fixture in a fresh context and replace the instruction with:

> Use $foreign-trade-customer-development from the supplied plugin source to complete this request. Produce the work product you believe is appropriate.
