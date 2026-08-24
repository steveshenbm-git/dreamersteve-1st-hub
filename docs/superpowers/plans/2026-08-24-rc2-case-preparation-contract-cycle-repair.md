# RC2 Case-Preparation Contract Cycle Repair Plan

**Goal:** Remove the circular dependency between the final frozen research contract and the 40-case set without weakening the model-run gate.

**Architecture:** Add a separate `case_preparation_locked` contract state whose immutable input projection is SHA-256 bound while the case-set hash and control IDs remain empty. Candidate/case preparation may use only that locked preparation contract. A deterministic finalizer then verifies the lock, binds the real 40-case file hash and real control IDs into a new contract version, and emits the only `frozen` contract accepted by model-run workspace initialization.

**Scope:** Source files and tests for `industry-application-map-builder` and the stage-5 route language in `foreign-trade-workflow-director`. No plugin installation, Git commit, formal candidate preparation, model run, full screening, shared-base write, company matching, route generation, or customer search.

## Task 1: Capture the circular dependency as failing tests

- Extend `tests/industry-application-map-builder/test_semantic_method_tools.py` with a complete locked-preparation-to-final-contract lifecycle test.
- Prove a locked preparation contract cannot initialize a model-run workspace.
- Prove placeholders, prefilled case outputs, lock drift, and missing/invalid 40-case data are rejected.
- Run the targeted test file and retain the expected RED result before production edits.

## Task 2: Implement the two-gate contract lifecycle

- Extend the research-contract template with an explicit `case_preparation_gate`.
- Add deterministic lock and finalization scripts with refuse-overwrite behavior.
- Add shared validation helpers while preserving all existing `frozen_contract_completeness_errors` requirements.
- Keep the existing runtime initializer frozen-only.

## Task 3: Align skill and workflow contracts

- Change `semantic_contract_prepare` to output a locked preparation contract, not a final runtime contract.
- Change `semantic_calibration_case_prepare` to output the real case set plus a new-version final frozen contract.
- Document the two gates and add a pressure scenario for placeholders/circular ordering.
- Keep `semantic_method_calibration` frozen-contract-only.

## Task 4: Verify without committing or installing

- Run targeted semantic-method tests.
- Run both plugin contract suites and the relevant full test set.
- Run skill/plugin structure validation available in the repository.
- Inspect the final diff and confirm no installed-cache or calibration-workspace files changed.
- Stop and request separate authority for any commit, installation, or candidate-pool resumption.
