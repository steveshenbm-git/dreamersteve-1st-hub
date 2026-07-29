# Development handoff contract

## Purpose

Transfer controlled product facts to `industry-application-map-builder` without transferring authority to alter evidence, invent routes, select customers, or communicate externally.

## Packet

```json
{
  "product_development_fact_packet": {
    "company_id": "ACME-001",
    "product_family_id": "ACME-001-PF-001",
    "product_family": "Effect pigments",
    "product_series_or_model": null,
    "confirmed_form": ["ACME-001-K-0002"],
    "confirmed_parameters": ["ACME-001-K-0001"],
    "confirmed_properties": [],
    "confirmed_mechanisms": [],
    "confirmed_functions": [],
    "confirmed_effects": [],
    "confirmed_applications": [],
    "required_conditions": ["ACME-001-K-0003"],
    "known_limits": ["ACME-001-K-0004"],
    "unresolved_conditions": ["No model-level mapping confirmed"],
    "approved_references": ["ACME-001-S-0001"],
    "knowledge_snapshot": {
      "facts_sha256": "<sha256>",
      "product_system_sha256": "<sha256>",
      "source_registry_sha256": "<sha256>"
    },
    "allowed_use": ["internal_industry_application_mapping"],
    "prohibited_inference": ["No certificate, regulation, MOQ, price, inventory, or lead-time claim"],
    "generated_at": "2026-07-29",
    "generator_version": "1.0"
  }
}
```

## Inclusion rules

- `confirmed_*`, `required_conditions`, and `known_limits` contain fact IDs, not rewritten claims.
- Every ID in a confirmed field must be an approved E3 `own_company` fact.
- `approved_references` contains registered source IDs supporting included facts.
- `unresolved_conditions` states what the downstream user must not assume.
- `allowed_use` defaults to `internal_industry_application_mapping`.
- `prohibited_inference` carries high-risk gaps and scope limits forward.
- E2 may appear only in a separately labelled internal annex when explicitly requested. It never enters `confirmed_*`.
- E1 and E0 never enter confirmed fields.
- Generate the packet with `export_product_development_fact_packet.py`; do not hand-select facts when the deterministic exporter can resolve the requested product family.
- `knowledge_snapshot` must match the current fact library, product system, and source registry when the packet is generated or validated.

## Downstream boundary

The packet contains no:

- industry or application-route recommendation;
- country/region priority;
- candidate company;
- customer selection, score, or ranking;
- commercial-entry judgment;
- outreach draft or sending action.

`industry-application-map-builder` may match these approved facts against separately sourced application requirements and emit labelled route hypotheses. It cannot modify the company library, upgrade evidence, remove restrictions, or treat the packet itself as proof of an industry/application route. Customer development must receive a separate `company_route_pool_packet`; it must not derive industry routes directly from this product-fact packet.

## Development readiness request

Customer development cannot call this skill as a background service. When readiness is missing, it returns a structured request and stops that route until the request is answered:

```json
{
  "development_readiness_request": {
    "request_id": "READY-001",
    "company_id": "ACME-001",
    "product_scope": "Effect pigments",
    "route_candidate_id": "ACME-001-R-001",
    "intended_use_scope": ["industrial coatings"],
    "geography_scope": ["DE"],
    "customer_type_scope": ["manufacturer"],
    "requested_dimensions": ["minimum_order_quantity", "lead_time"],
    "declared_conditions": [
      {
        "dimension": "minimum_order_quantity",
        "value": 50,
        "unit": "kg"
      }
    ],
    "requested_at": "2026-07-29",
    "return_to": {
      "skill": "foreign-trade-customer-development",
      "task_route": "route_portfolio_review"
    }
  }
}
```

`route_candidate_id` is an opaque trace key. This skill must not look up the route map, infer its application meaning, or decide its market value. Match only the declared request context to this company's facts.

## Development readiness view

Return one `development_readiness_view` containing:

- request, company, product, and opaque route identifiers;
- the declared context and requested dimensions;
- fact/product/source snapshot hashes;
- `confirmed_items`: current approved E3 own-company commercial facts;
- `internal_reference_annex`: explicitly requested E2 facts, which never affect state;
- stale items, missing dimensions, confirmed conflicts, and conditional items;
- `readiness_state`: exactly `可承接`, `有条件`, `未知`, or `已确认冲突`;
- prohibited inference, generation date, next owner, and salesperson decision ownership.

State rules are deterministic:

| Observable condition | State |
|---|---|
| A current E3 condition is directly violated by comparable declared context | `已确认冲突` |
| Current E3 conditions exist but context, unit, or confirmation is insufficient | `有条件` |
| A requested dimension has no current E3 fact, or relevant facts are stale | `未知` |
| Every requested dimension is supported by comparable current E3 facts and no conflict exists | `可承接` |

The default view is emitted on demand and is not a maintained second fact store. Persist a snapshot only with explicit write authorization for a material decision. The view never modifies technical route status, chooses a country, ranks routes, authorizes scanning, or makes the salesperson's decision.
