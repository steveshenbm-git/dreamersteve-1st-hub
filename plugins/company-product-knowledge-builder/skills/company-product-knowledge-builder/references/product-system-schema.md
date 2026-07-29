# Product system schema

## Hierarchy

Model only supported levels:

`company → product_family → product_series/type → product_model/specification`

Do not invent a series or model to complete the tree. Store aliases as unresolved mappings until evidence supports identity.

## Atomic fact record

```json
{
  "fact_id": "ACME-001-K-0001",
  "company_id": "ACME-001",
  "product_family": "Effect pigments",
  "product_series": null,
  "product_model": null,
  "fact_type": "parameter",
  "fact_value": {"value": 25},
  "statement_kind": "source_fact",
  "unit": "micrometre",
  "unit_status": "provided",
  "test_method": "laser diffraction",
  "test_method_status": "provided",
  "applicable_conditions": ["dry powder"],
  "known_limits": ["No wet-dispersion result established"],
  "subject_scope": "own_company",
  "source_id": "ACME-001-S-0001",
  "source_location": "page 1, table 2",
  "evidence_level": "E3",
  "review_status": "approved",
  "reviewed_by": "owner",
  "reviewed_at": "2026-07-29",
  "allowed_use": ["internal", "external"],
  "conflict_status": "none",
  "conflicts_with": [],
  "updated_at": "2026-07-29"
}
```

## Controlled values

`fact_type`:

- `identity`
- `form`
- `material`
- `parameter`
- `property`
- `mechanism`
- `function`
- `effect`
- `required_condition`
- `known_limit`
- `application`
- `technical_document`
- `commercial_condition`
- `company_fact`

`subject_scope`: `own_company`, `supplier`, `customer`, `general_industry`, `unknown`.

`statement_kind`: `source_fact`, `inference`, `unknown`. Only `source_fact` may become E3.

`conflict_status`: `none`, `open`, `resolved`, `superseded`.

## Commercial condition facts

`commercial_condition` is still an atomic company fact. Store the comparison rule inside `fact_value`:

```json
{
  "fact_type": "commercial_condition",
  "fact_value": {
    "dimension": "minimum_order_quantity",
    "operator": "minimum",
    "value": 25,
    "unit": "kg"
  },
  "observed_at": "2026-07-01",
  "valid_until": "2026-12-31",
  "review_due": "2026-12-31",
  "sensitivity": "commercial_internal",
  "geographic_scope": [],
  "customer_type_scope": [],
  "application_scope": []
}
```

Allowed operators are `minimum`, `maximum`, `equals`, `one_of`, `not_one_of`, `required_boolean`, and `requires_confirmation`. Sensitivity is `commercial_internal`, `customer_safe`, or `restricted`.

Operator and value types are a hard contract: `minimum` and `maximum` require a non-boolean number; `one_of` and `not_one_of` require a non-empty JSON list; `required_boolean` requires a JSON boolean; `equals` requires one non-null scalar; `requires_confirmation` deliberately produces no automatic comparison result. A declared value with a missing/different unit or incompatible type is `有条件`, not a confirmed conflict and never a runtime error.

At least one of `valid_until` or `review_due` is required. The readiness exporter calculates freshness at request time; do not store a permanently current `stale_status` in the fact. Expired, missing, differently scoped, or incomparable facts cannot support `可承接` or `已确认冲突`.

## Parameter completeness

A parameter is usable only inside its recorded scope. Preserve, when applicable:

- value or range;
- unit or explicit `not_applicable` status;
- test method or explicit `not_applicable` status;
- material, substrate, process, equipment, and environment conditions;
- sampling or preparation conditions;
- known limits and counterexamples.

Missing information stays `missing` or in an unresolved list. Do not silently convert a bare number into a complete parameter.

## Product tree record

```json
{
  "product_family_id": "ACME-001-PF-001",
  "name": "Effect pigments",
  "alias_terms": [
    {"term": "mica pearl", "identity_status": "unverified"}
  ],
  "fact_ids": ["ACME-001-K-0001"],
  "series": [],
  "unresolved_structure": ["No model-level mapping confirmed"]
}
```

The tree points to facts; it does not restate claims. A hierarchy link is not evidence and cannot raise a fact's evidence level.
