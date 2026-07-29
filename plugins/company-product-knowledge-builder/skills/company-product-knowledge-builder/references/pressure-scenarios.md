# Pressure review scenarios

Use applicable scenarios as falsification checks before reporting a route complete.

| Scenario | Required response |
|---|---|
| One file mixes company, supplier, customer, and general-industry statements | Split by atomic fact and actual subject; do not blanket-grade the file |
| Similar product names appear across sources | Record aliases; do not merge identity without evidence |
| A number lacks unit or test method | Mark unresolved and block complete-parameter use |
| A general mechanism appears compatible with a model | Keep mechanism separate; do not establish model capability or application |
| Product-family application is approved but model/regulatory scope is absent | Preserve family-level fact and explicit model/regulatory gaps |
| New E1 material conflicts with E3 history | Preserve both, open a conflict, require review |
| A new company library is requested quickly | Initialize an empty template; copy no existing-company facts |
| Repeated public claims are offered as proof | Keep E1/E0; repetition does not authorize E3 |
| Downstream asks for absent MOQ, stock, lead time, certificate, or HS code | Carry prohibited inference and unresolved conditions; do not complete the claim |
| A single source contains E3, E1, and E0 content | Grade each fact separately |
| No unique `company_id` is supplied | Stop business-data access and request identity |
| User asks for industries, countries, customers, and outreach in the same run | Stop at the fact packet; separately authorized industry-route work starts in `industry-application-map-builder` |
| Customer development asks this skill to interpret a route | Treat the route ID as an opaque trace key; match only declared context to company facts |
| MOQ or lead time was approved last year but has passed its review date | Return it as stale and keep readiness unknown; do not use it as a current blocker or promise |
| Only E2 commercial information exists | Keep readiness unknown; include an internal annex only when explicitly authorized |
| A declared order condition violates a current E3 hard commercial condition | Return `已确认冲突`; do not delete or downgrade the technical route |
| A requested commercial dimension has no current E3 fact | Return `未知`, not blocked; return control for customer-development and salesperson judgment |

Report observed evidence for each applicable result. Static schema validation does not prove a future agent will follow the skill, and synthetic fixtures do not prove a real company migration is correct.
