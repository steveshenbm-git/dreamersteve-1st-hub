# Company library contract

## Purpose

Use one independent root per company. Keep immutable sources, atomic facts, product structure, review records, downstream handoff, temporary work, and risk material in separate areas.

## Required layout

```text
company-root/
├── AGENTS.md
├── README.md
├── company.json
├── 00-管理/
│   ├── 源文件清单.json
│   └── 变更记录.json
├── 01-源文件封存/
├── 02-事实库/
│   └── facts.json
├── 03-产品体系/
│   └── product-system.json
├── 04-开发交接/
│   └── product-development-fact-packet.json
├── 05-复核/
│   └── review-log.json
├── 06-工作区/
└── 07-风险隔离/
```

## Mutation contract

1. Confirm the exact company root and `company_id`.
2. Reject a write if a target record carries another `company_id`.
3. Preserve original sources and compare stored SHA-256 with the current archived file.
4. Append a source before referencing it from a fact.
5. Add or revise facts without deleting the previous evidence trail.
6. Write product hierarchy and handoff entries as references to fact IDs.
7. Add a change record containing date, actor, reason, affected source/fact IDs, prior state, new state, and authorization basis.
8. Validate, reopen changed files, and report actual status.

## Source record

```json
{
  "source_id": "ACME-001-S-0001",
  "company_id": "ACME-001",
  "archived_path": "01-源文件封存/original.pdf",
  "sha256": "64-lowercase-hex-characters",
  "actual_subject": "own_company",
  "intake_date": "2026-07-29",
  "notes": "Original manufacturer brochure"
}
```

Allowed `actual_subject` values are `own_company`, `supplier`, `customer`, `general_industry`, `unknown`, and `mixed`. Use `mixed` only for a container with multiple subjects, then assign a specific subject to every atomic fact. Do not add an `evidence_level` to the source record; evidence belongs to atomic facts.

## Immutability and rollback

- Never overwrite or edit an archived original.
- If a corrected source arrives, archive it as a new source and link affected facts through the change log.
- If the stored hash differs, stop normal use and report `SOURCE_HASH_MISMATCH`.
- Roll back derived knowledge by restoring the prior fact/product/handoff JSON state; do not delete the archived evidence or historical change record.

## Company isolation

An initializer must produce placeholders only. It must not copy facts, source IDs, supplier names, customers, product examples, or review history from an existing company. A cross-company comparison belongs in a separately authorized workspace and never modifies either source library automatically.
