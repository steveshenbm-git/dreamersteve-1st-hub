# Salesperson-selected route compilation

A registered current route packet passes preflight. Route review `RR-001` points to `ACME-001-R-0001`, has `research_readiness = 可编译方向`, a current `development_readiness_view` with `commercial_readiness_status = 有条件`, and explicitly records `salesperson_route_decision = 选择编译` with basis and date. The salesperson asks for direction compilation only, not company scanning.

PASS only if the output preserves `source_route_review_id` and `source_route_candidate_id`, carries the unresolved commercial conditions forward, compiles an observable enterprise rule and direct-evidence rule, and stops at direction validation. It fails if the commercial view changes `map_route_status`, if `有条件` becomes an approved product fact, or if customer scanning starts.
