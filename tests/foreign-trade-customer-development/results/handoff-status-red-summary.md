# Handoff-Status RED Test Summary

## Contract

`handoff_status` has exactly four allowed values, in this order:

1. `未触发`
2. `待邮件助手`
3. `已移交`
4. `业务员已决定`

The exact controlled ranges are `客户总览!Q3:Q5000` and `移交记录!J3:J5000`. `触达已暂停` is an outreach-plan state, not a reachable `handoff_status` value.

## RED evidence

The current source workbook exits `1` with exactly two diagnostics. Both controlled ranges still contain the obsolete fifth value `触达已暂停`; no other workbook-contract diagnostic is reported.

## Mutation proof

The mutation suite first creates a temporary GREEN control by preserving all 13 existing validation ranges and enforcement properties while replacing only the two handoff lists with the four-value contract. The complete workbook validator accepts that control.

Five isolated mutations are then rejected:

1. wrong `screening_status` value;
2. disabled stop-style alert;
3. disabled blank allowance;
4. `触达已暂停` reinserted only into `客户总览!Q3:Q5000`;
5. `触达已暂停` reinserted only into `移交记录!J3:J5000`.

Each mutation is tested from an accepted GREEN copy and must produce exactly its expected diagnostic.

## Integrity

The workbook SHA-256 remains `45adcd77f8c7cdd89f1950339eda0e8b532ae376a46c0709df4160fe2354dc2e`. The workbook asset, production skill, references, design, plan, and existing raw outputs were not modified.
