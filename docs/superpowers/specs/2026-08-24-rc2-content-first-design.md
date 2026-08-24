# RC2 Content-First Candidate Design

## Decision

Create two installable-but-not-installed candidate plugins instead of changing the current beta.3 sources or caches.

- `industry-application-map-builder-rc2-content-first` version `0.4.0-rc2-content-first.1`
- `foreign-trade-workflow-director-rc2-content-first` version `0.3.0-rc2-content-first.1`

Each candidate carries a versioned copy of the beta.3 contract surface. Old beta.3 source, cache, contracts, prompt hashes, and RC2-40-R2 artifacts remain untouched.

## Problem Boundary

Beta.3 correctly preserves raw returns and receiver receipts, but treats platform identity and transport admissibility as part of the calibration count gate. This candidate introduces a distinct content-quality lane. It does not relax source, safety, coverage, or downstream boundaries.

## Modes and Compatibility

`strict_audit` is the compatibility default. A legacy contract with no mode field is interpreted as `strict_audit`; its old validator and evaluator keep their existing behavior.

`content_first` is opt-in through a new final frozen contract field. It is not readable as a beta.3 formal result and must never emit beta.3 `EFFECTIVE`. It has its own vocabulary:

| Gate | Content-first state | Meaning |
| --- | --- | --- |
| Contract | `CONTENT_CONTRACT_FROZEN` | Inputs and content rubric are frozen. |
| 40 cases | `CONTENT_CALIBRATION_PASS`, `CONTENT_CALIBRATION_FAIL`, or `CONTENT_CALIBRATION_INCOMPLETE` | Checks content evidence only; it is not beta.3 method effectiveness. |
| Full scope | `NOT_AUTHORIZED`, `AUTHORIZED_NOT_STARTED`, `IN_PROGRESS`, `COVERAGE_INCOMPLETE`, `READY_FOR_REVERSE_AUDIT`, or `BLOCKED` | Requires a separate explicit human authorization. |
| Downstream | `RESEARCH_ONLY_BLOCKED` | Company matching, routes, customer work, and shared-base writes stay blocked. |

Rollback is removal of the candidate source entry or choosing beta.3. Candidate artifacts are append-only and retained for review; they are never merged into beta.3 or RC2-40-R2.

## Evidence Layering

Content pass requires a one-to-one content envelope and scorecard for every case or node. The envelope points to an unchanged, byte-hashed raw response; it is never replaced by a summary. The scorecard points to the same raw response, visible-input hash, source/truth packet and hash, method arm, itemized rubric results, and explicit unknowns.

The item rubric measures taxonomy/scope grounding, three-state-axis handling, source/truth alignment, safety boundaries, and unknown disclosure. It has no style or fluency dimension. A source packet remains mandatory; AI reasoning and score wording cannot manufacture supported evidence.

Platform transport and model identity are recorded only in a separate optional audit field in this mode. `UNVERIFIED` platform metadata cannot by itself fail content scoring, but missing or altered raw answer, frozen input, source/truth reference, scorecard, or unknown list does.

## Forty-Case and Full-Scope Gates

The evaluator requires both method arms to use the same 40 unique case IDs, contract, taxonomy snapshot, case-set hash, source/truth-package hash, visible inputs, and rubric. It first applies all critical content/safety gates, then checks 100 percent known-positive recall and the frozen 20 percent depth-reduction threshold. The result deliberately uses the content-first state vocabulary.

The full-scope gate requires `CONTENT_CALIBRATION_PASS`, an explicit authorization reference, unchanged frozen terminal-node scope and hash, and zero known safety failure. It authorizes only append-only screening in controlled batches. It does not run any node, write the shared base, or change the workflow stage. Each batch stops for drift, budget, missing evidence, or any coverage mismatch. Full coverage still requires selective evidence expansion and reverse audit before a research review; no research review opens downstream work without a separately designed migration decision.

## Candidate Interfaces

The map candidate supplies:

- content-first contract, raw-answer, scorecard, and calibration-arm templates;
- a content evidence validator that checks raw-byte, input, source/truth, scorecard, safety, and scope relationships;
- a 40-case evaluator that intentionally ignores platform identity as a content gate;
- a full-scope authorization checker that refuses default authorization;
- a compatibility matrix and adversarial pressure scenarios.

The workflow candidate consumes only the content-first summary fields. Its Stage 5 route remains `industry_semantic_expansion`, always exposes one stop point, and records `RESEARCH_ONLY_BLOCKED` until an explicit future migration contract exists.

## Non-claims

Static validation and synthetic behavior tests prove only schema and gate behavior. No A/B/C run, 40-case live calibration, 1,382-node run, product-neutral base write, company match, route, or customer action occurs in this change. Therefore this candidate is structurally ready for controlled evaluation, not demonstrated effective.
