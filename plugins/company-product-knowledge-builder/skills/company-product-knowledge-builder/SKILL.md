---
name: company-product-knowledge-builder
description: Use when a company needs a new or updated local product-knowledge library, source intake, structured product hierarchy, evidence review, conflict handling, knowledge updates, or a controlled product-fact handoff before industry-route or customer-development work.
---

# 公司产品知识构建

## Core principle

Build a company-specific, source-traceable product fact system before any industry-route or customer work. Keep source statements, approved company facts, inference, unknowns, and downstream research conclusions separate.

This skill owns the knowledge layer only. It does not discover industries, prioritize countries, search customers, select prospects, or draft outreach.

## Start contract

Before reading or writing business material:

1. Identify one explicit `company_id` and its company-library root.
2. If `company_id` is absent or ambiguous, stop business-data access and request it.
3. Classify the request into one route from the table below.
4. Determine whether the user authorized mutation. Review, audit, explain, or diagnose requests remain read-only.
5. Freeze the requested scope and acceptance contract. Do not redefine the design merely because validation finds a failure.
6. Read [company-library-contract.md](references/company-library-contract.md) for every mutating route, then read the route-specific reference.

## Route selection

| Route | Trigger | Required reference | Stop point |
|---|---|---|---|
| `library_bootstrap` | Create a new company library | [company-library-contract.md](references/company-library-contract.md) | Empty isolated library validates |
| `source_intake` | Add or register original material | [evidence-and-review.md](references/evidence-and-review.md) | Source is archived and facts remain E1 unless separately approved |
| `product_system_build` | Organize families, series, models, parameters, effects, conditions, or gaps | [product-system-schema.md](references/product-system-schema.md) | Product structure cites fact IDs and leaves unknown levels empty |
| `knowledge_review` | Review evidence, conflicts, customer usability, or missing facts | [evidence-and-review.md](references/evidence-and-review.md) | Review result records `PASS / FAIL / UNVERIFIED` and required action |
| `knowledge_update` | Add newer material or revise an existing record | [company-library-contract.md](references/company-library-contract.md) and [evidence-and-review.md](references/evidence-and-review.md) | History is preserved and change record is written |
| `development_handoff` | Prepare approved facts for downstream development | [handoff-contracts.md](references/handoff-contracts.md) | Controlled fact packet is written; no route or customer conclusion follows |

Do not combine routes merely for convenience. Complete the requested route and stop at its boundary unless the user authorized the next route.

## Company isolation

- Resolve all business reads and writes inside the selected company root.
- Never reuse another company's facts, IDs, sources, suppliers, customers, examples, or handoff packet.
- Keep root-level company indexes limited to identifiers and paths; do not create a cross-company fact channel.
- Treat directory separation as workflow isolation only. Never describe it as operating-system, account, encryption, or physical isolation.
- For an explicitly requested cross-company comparison, use a separate working area and do not write conclusions back automatically.

## Source and fact discipline

- Preserve each original source; record `source_id`, actual subject, relative archive path, SHA-256, intake date, and notes.
- Treat a file as an evidence container. Never assign one E0/E1/E2/E3 grade to the whole file.
- Split claims into atomic facts. Record product scope, value, unit, test method, conditions, limits, source location, subject, evidence, review state, allowed use, and conflicts.
- Default newly extracted source statements to E1.
- Upgrade a specific fact to E2 or E3 only after explicit authorized review, capturing reviewer, date, exact fact IDs, and allowed use.
- Keep supplier, customer, general-industry, inferred, and unknown statements separate from own-company facts.
- Preserve both sides of a conflict. A newer date alone does not authorize overwriting approved history.
- Leave missing levels and fields unresolved; never fill gaps from plausibility.

Use the exact schema and controlled vocabulary in [product-system-schema.md](references/product-system-schema.md).

## Bootstrap

Create a new library only when creation is authorized:

```bash
python3 scripts/init_company_library.py \
  --company-id ACME-001 \
  --company-name "Acme Materials" \
  --destination /absolute/path/to/ACME-001
```

The initializer refuses to overwrite an existing destination. Do not add a force path or delete an existing library to make initialization succeed.

## Source intake

Follow this order:

1. Copy the original into `01-源文件封存/` without rewriting its contents.
2. Compute SHA-256 from the archived copy.
3. Add a source record to `00-管理/源文件清单.json` without an `evidence_level` field.
4. Extract atomic records into `02-事实库/facts.json`; use E1 unless a separate fact-level approval exists.
5. Record ambiguous subject, missing unit, missing test method, missing conditions, and conflicts explicitly.
6. Validate the library before reporting the write.

Never infer company ownership, product applicability, certification, compliance, commercial terms, or customer use from source presence alone.

## Product system build

Build only the hierarchy supported by facts:

`company → product family → series/type → model/specification → facts, conditions, limits, gaps, conflicts`

Attach fact IDs rather than copying claims into the product tree. Record aliases separately until evidence supports merging them. Mechanism may explain why an adjacent application is plausible, but mechanism alone never establishes product compatibility or an approved application.

## Evidence review and update

Apply the evidence matrix in [evidence-and-review.md](references/evidence-and-review.md). For each reviewed fact, report:

- evidence level and subject;
- source and location;
- completeness of unit, method, material/process/environment conditions;
- known limits and open conflicts;
- allowed use and prohibited inference;
- exact reason for `PASS`, `FAIL`, or `UNVERIFIED`.

When updating, append the new source and fact records, link conflicts or supersession, and add a change-log entry. Never erase the evidence trail.

## Development handoff

Populate `04-开发交接/product-development-fact-packet.json` according to [handoff-contracts.md](references/handoff-contracts.md).

Confirmed fact fields accept only approved E3 own-company fact IDs. E2 may be supplied only in a separately labelled internal context and never inside `confirmed_*`. E1 and E0 never enter confirmed fields.

Stop after producing the packet. Hand the packet to a customer-development capability only when the user separately requests downstream work. Do not infer:

- industry routes or application candidates;
- country priorities;
- candidate companies or customer selection;
- commercial entry strategy;
- outreach wording or sending actions.

## Validation

After every creation or mutation, run:

```bash
python3 scripts/validate_company_library.py /absolute/path/to/company-library
```

Use `--format json` when a machine-readable report is needed. Reopen the changed JSON files and inspect the report before claiming a write succeeded.

Before handing off or declaring the knowledge route complete, read [pressure-scenarios.md](references/pressure-scenarios.md) and test applicable failure hypotheses.

## Completion report

State:

- route and `company_id`;
- files created or changed;
- sources and fact IDs affected;
- validation command and actual result;
- material `FAIL` or `UNVERIFIED` items;
- downstream work not performed.

Do not claim agent-behavior, live downstream integration, or a real-company migration was validated when only static files or synthetic fixtures were tested.
