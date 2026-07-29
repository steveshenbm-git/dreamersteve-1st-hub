# Development handoff contract

## Purpose

Transfer controlled product facts to downstream direction research without transferring authority to alter evidence, select customers, or communicate externally.

## Packet

```json
{
  "product_development_fact_packet": {
    "company_id": "ACME-001",
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
    "allowed_use": ["internal_direction_research"],
    "prohibited_inference": ["No certificate, regulation, MOQ, price, inventory, or lead-time claim"],
    "generated_at": "2026-07-29"
  }
}
```

## Inclusion rules

- `confirmed_*`, `required_conditions`, and `known_limits` contain fact IDs, not rewritten claims.
- Every ID in a confirmed field must be an approved E3 `own_company` fact.
- `approved_references` contains registered source IDs supporting included facts.
- `unresolved_conditions` states what the downstream user must not assume.
- `allowed_use` defaults to internal direction research.
- `prohibited_inference` carries high-risk gaps and scope limits forward.
- E2 may appear only in a separately labelled internal annex when explicitly requested. It never enters `confirmed_*`.
- E1 and E0 never enter confirmed fields.

## Downstream boundary

The packet contains no:

- industry or application-route recommendation;
- country/region priority;
- candidate company;
- customer selection, score, or ranking;
- commercial-entry judgment;
- outreach draft or sending action.

The downstream customer-development skill may derive and test hypotheses from the packet, but it cannot modify the company library, upgrade evidence, or remove restrictions.
