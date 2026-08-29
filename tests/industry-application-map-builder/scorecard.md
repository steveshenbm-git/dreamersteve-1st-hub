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
| SEMANTIC-1 | Keeps screening, work progress, and evidence truth on three separate state axes; `no_hypothesis_formed` is never an exclusion. |
| SEMANTIC-2 | Requires two query groups and five inspected results per available group before `no_hypothesis_formed`. |
| CONTRACT-1 | Freezes taxonomy, model profile, prompt hashes, source permissions, budget, gates, sampling, and allowed writes in one versioned research contract. |
| MODEL-1 | Separates A generation/search, B source reread, and C dispute/reverse-audit visibility; model agreement never upgrades evidence. |
| CALIBRATION-1 | For legacy `strict_audit` only, runs paired full-depth and screen-then-expand arms on the same 40 frozen cases and returns only EFFECTIVE, NOT_EFFECTIVE, or INCONCLUSIVE. |
| AUDIT-1 | Uses mutually exclusive risk strata, reproducible without-replacement samples, an exact finite-population upper bound, and a separate industry-coverage supplement. |
| AUTH-1 | Separates source edit, calibration, full screening, shared-base write, company matching, customer search, commit, and install authorizations. |
| WRITE-1 | Calibration writes only to the semantic research workspace and cannot write the shared application workbook. |
| R4-TERM-1 | Keeps official taxonomy semantics, a contract-local product-neutral terminology bridge, and each company's local terminology pack separate; cold start may be empty and no production term list ships in the skill. |
| R4-DISCOVERY-1 | Decomposes broad nodes into output families, bounds dynamic discovery to the current case, and never mutates the frozen term pack or treats model terms as evidence. |
| R4-CHAIN-1 | Requires separate taxonomy-membership, output/subprocess, and mechanism/use-point bases before a claim can close. |
| R4-BLIND-1 | Builds 40 paired tasks only from the frozen visible-only case set and rejects truth, receiver fields, encoded value laundering, aliases, symlinks, and hard-link reuse. |
| R4-OWNERSHIP-1 | Keeps model observations, receiver-owned source/resource snapshots and receipts, formal truth, and scorecards in separate roles with exact final-contract binding. |
| R4-CASE-1 | Uses 30 retained unexecuted cases plus 10 new unseen cases with neutral sampling labels, excludes every `development_regression_only` case, and derives accepted positive, accepted negative, and unresolved sets only from independent adjudication. |
| R4-SCORE-1 | Enforces the exact six-item `2.1-r4` scorecard, five source-equivalence dimensions, allowed evidence pointers, fixed reviewers/critical flags, dynamic accepted-positive recall, truth-revision invalidation, and downgrade refusal. |
| R4-REALITY-1 | Recomputes the 80 `baseline_full_depth_v1` / `screen_then_expand_v2` task/raw/scorecard/resource chains and six predeclared single-case repeats instead of trusting arm summaries or repeat IDs. |
| R4-GATE-1 | Applies safety, recall, receiver-evidence, stability, then efficiency; uses frozen 20%/10%/0 thresholds and rejects R4 CLI overrides. |
| R4-STOP-1 | Uses only `CONTENT_CALIBRATION_*` for R4; platform audit stays separate. Even after `CONTENT_CALIBRATION_PASS`, explicit human full-screen authorization and unchanged scope are required for `AUTHORIZED_NOT_STARTED`; it keeps `RESEARCH_ONLY_BLOCKED`, leaves the first incomplete stage at industry semantic expansion, and never claims `EFFECTIVE`. |

Failures of OWNER, IDENTITY, MATCH, EVIDENCE, ROUTE, STATUS, or VERSION are material.
