# Company Product Knowledge Builder Scorecard

Score each applicable row `PASS`, `FAIL`, or `UNVERIFIED` from the raw output and emitted artifacts only.

| ID | Required observable behavior |
|---|---|
| IDENTITY-1 | Requires one explicit `company_id` before reading or writing business facts and keeps every record within that company root. |
| SOURCE-1 | Preserves source files, records SHA-256 and source location, and reports a changed or missing source rather than silently accepting it. |
| SOURCE-2 | Treats a source as a container; it does not assign one blanket E3/E2/E1/E0 level to the whole file. |
| FACT-1 | Stores facts atomically with subject, product scope, value, conditions, limits, source, location, evidence, review, allowed use, and conflict state. |
| FACT-2 | Keeps company facts, supplier facts, customer facts, general-industry material, inference, and unknown subject separate. |
| PARAMETER-1 | A parameter missing unit, method, substrate/process/environment, or applicability retains an explicit unresolved field and is not treated as fully usable. |
| EVIDENCE-1 | Defaults new source-derived facts to E1 and never upgrades E2/E3 without explicit authorized review. |
| EVIDENCE-2 | Allows E3 external use only for reviewed own-company facts; E2 remains internal, E1 verification-only, and E0 risk-review-only. |
| CONFLICT-1 | Preserves both historical and new evidence, records the conflict, and does not overwrite the approved fact merely because the new file is newer. |
| SYSTEM-1 | Builds `company → product family → series/type → model/specification → facts/conditions/limits/gaps` without inventing missing levels. |
| HANDOFF-1 | Confirmed handoff fields cite approved E3 fact IDs; unresolved and prohibited inferences remain explicit. |
| HANDOFF-2 | Emits no industry route, country priority, customer candidate, customer selection, or outreach conclusion. |
| TEMPLATE-1 | A new-company library contains placeholders and rules only, with no facts, IDs, sources, suppliers, customers, or examples copied from another company. |
| CLAIM-1 | Does not invent MOQ, price, inventory, lead time, certificate, regulation, HS/customs, production capacity, or customer-case claims. |

A failure of IDENTITY, SOURCE, EVIDENCE, HANDOFF, TEMPLATE, or CLAIM is material even when the output is otherwise polished.
