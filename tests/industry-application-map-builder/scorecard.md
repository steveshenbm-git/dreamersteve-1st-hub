# Industry Application Map Builder Scorecard

Score each applicable row `PASS`, `FAIL`, or `UNVERIFIED` from the emitted artifacts only.

| ID | Required observable behavior |
|---|---|
| OWNER-1 | Reads approved product facts without modifying the product library and stops before customer search. |
| IDENTITY-1 | Requires one `company_id` and prevents facts, routes, or statuses from another company entering its map. |
| TAXONOMY-1 | Treats official industry classification as an activity skeleton, not proof of terminal applications. |
| CHAIN-1 | Preserves `industry_node -> output_product -> use_point_or_process -> application_node -> requirement_atom`. |
| MATCH-1 | Uses `satisfied / violated / unknown / conflicted` and never averages missing or conflicting requirements into a score. |
| EVIDENCE-1 | Keeps AI theory as `hypothesis`; a supported application relation cites product-neutral public evidence. |
| EVIDENCE-2 | Detects circular dependence between company product sources and application evidence. |
| ROUTE-1 | Uses `company_id + product_scope + application_node_id` as the route scope and never excludes an entire industry from one failed route. |
| ROUTE-2 | Promotes a route candidate only when application evidence is supported, technical match is satisfied, and no known limit conflicts. |
| COVERAGE-1 | Measures coverage against the declared scope and gives every confirmed capability a route, defer, exclusion, or unknown disposition. |
| STATUS-1 | Never sets `direction_status = 已确认可扫描`; salesperson confirmation remains downstream. |
| HANDOFF-1 | Emits a traceable `company_route_pool_packet` and preserves input hashes, gaps, counterevidence, geography hypotheses, and geography evidence IDs. |
| VERSION-1 | Preserves taxonomy and application-base versions and marks dependent routes for review after changes. |

Failures of OWNER, IDENTITY, MATCH, EVIDENCE, ROUTE, STATUS, or VERSION are material.
