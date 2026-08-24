# RC2 Content-First Unified Upgrade

## Decision

Upgrade the existing, same-name plugins rather than expose two daily-use candidates:

- `industry-application-map-builder` becomes `0.4.0-beta.1`.
- `foreign-trade-workflow-director` becomes `0.3.0-beta.1`.

The pre-1.0 minor bumps are deliberate. The legacy strict route remains compatible, but the default route and new-contract lifecycle change materially. Git history retains `0.3.0-beta.3` and `0.2.0-beta.3` for rollback; Codex must not show duplicate old/candidate skills.

## Unified mode contract

`semantic_evaluation_mode` has two values in the same skill:

| Mode | Selection | Result vocabulary | Purpose |
| --- | --- | --- | --- |
| `content_first` | Default for a newly prepared RC2 contract and the new workflow template | `CONTENT_CONTRACT_FROZEN`, `CONTENT_CALIBRATION_*`, content full-scope states | Score the preserved answer and source/truth evidence. |
| `strict_audit` | Explicit selection, or a legacy contract with no mode field | Existing beta.3 `INCONCLUSIVE`, `EFFECTIVE`, `NOT_EFFECTIVE` | Preserve the strict transport/identity admissibility route unchanged. |

Content-first requires the stable case/node ID, visible input and hash, method arm, byte-hashed complete raw answer, source/truth comparison and hash, itemized non-style scorecard, and explicit unknown items. Platform identity/transport records remain separate `platform_audit_state`; their absence cannot erase an otherwise scoreable raw answer or automatically fail content scoring.

`CONTENT_CALIBRATION_PASS` is not beta.3 `EFFECTIVE`. It permits only a request/check for explicit full-scope authorization. The terminal-node manifest hash, append-only coverage, source evidence, three semantic axes, safety rules, evidence expansion, reverse audit, and `RESEARCH_ONLY_BLOCKED` remain mandatory. No content-first path releases shared-base writing, company matching, routes, customers, or communications.

## Migration boundary

Move only the candidate-only content-first assets, references, scripts, tests, and mode-specific contract changes into the two existing plugin directories. Preserve the original strict scripts and semantic-method prompt assets byte-for-byte. Update the existing manifests, agents metadata, workflow templates, core references, and marketplace entries in place.

Remove the two `*-rc2-content-first` plugin directories and their marketplace entries after their unique material is present under the original names. This removes only the redundant source copies from the current tree; the prior candidate commit remains in Git history. Do not edit the installation cache or any RC2-40 frozen artifact.

## Verification boundary

The refactor must prove: same-name discovery, content-first default for new templates, strict compatibility selection for legacy contracts, raw-answer/source/score/unknown requirements, default-deny full-scope gate, downstream block, no independent candidate entry, and unchanged strict-suite behavior.

These checks establish source structure and deterministic gate behavior only. No A/B/C run, live 40-case comparison, 1,382-node screening, installation, shared-base write, company action, route action, or customer action is part of this upgrade. Optimization effectiveness remains `INCONCLUSIVE` until controlled paired evidence exists.
