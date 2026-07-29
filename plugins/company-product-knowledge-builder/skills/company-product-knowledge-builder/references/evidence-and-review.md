# Evidence and review

## Evidence matrix

| Level | Meaning | Allowed use | Approval rule |
|---|---|---|---|
| E3 | Reviewed own-company fact approved for external use | `internal`, `external` | Explicit authorized reviewer, date, exact fact scope |
| E2 | Reviewed fact approved only for internal use | `internal` | Explicit authorized reviewer, date, exact fact scope |
| E1 | Source statement awaiting confirmation | `verification` | Default for newly extracted source statements |
| E0 | Risk, warning, unsupported hypothesis, or isolated general material | `risk_review` | Never available to ordinary customer development or external messaging |

Evidence applies to each fact, not to a file. One source may legitimately support E3, E1, and E0 records at the same time.

## Subject separation

Classify the actual subject before evidence review:

- `own_company`: the statement is explicitly about the selected company or its identified product.
- `supplier`: the statement is about a supplier or upstream product.
- `customer`: the statement is about a customer, brand, or downstream case.
- `general_industry`: the statement describes a general mechanism, convention, or market pattern.
- `unknown`: the subject cannot be resolved from evidence.

Only `own_company` may become E3. Repetition across public pages, distributor listings, search results, or AI summaries does not authorize E2/E3.

## Review gate

Before upgrading a fact, capture:

1. exact `fact_id` values;
2. reviewer identity or role;
3. review date;
4. approved wording or factual scope;
5. applicable products, materials, processes, and environments;
6. allowed use;
7. remaining limits and prohibited inference.

If any approval dimension is ambiguous, keep the fact at E1 and record the missing decision.

## Conflict handling

- Preserve every source and atomic fact.
- Link contradictory facts using `conflicts_with` and set `conflict_status: open`.
- Do not overwrite E3 with a newer E1.
- Resolve only with explicit review; mark the losing record `superseded` rather than deleting it.
- Record why the conflict was resolved and which source/fact IDs were affected.

## High-risk omissions

Never invent or promote missing claims about price, inventory, MOQ, lead time, payment, packaging, certification, regulation, HS/customs, production capacity, factory ownership, order-level performance, or customer cases.

## Review result

- `PASS`: concrete evidence and file inspection satisfy the applicable contract.
- `FAIL`: a material contract violation is observed.
- `UNVERIFIED`: reliable evidence or an authorized decision is unavailable.

Self-review checks implementation against the frozen contract; it does not retroactively replace the approved scope or turn unknowns into facts.
