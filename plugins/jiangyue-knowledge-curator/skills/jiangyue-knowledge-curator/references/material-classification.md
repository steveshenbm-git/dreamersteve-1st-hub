# Material Classification

Use this file to classify Jiangyue website materials before asking the user what should enter the formal knowledge base.

## Labels

`final-candidate`: A version appears to be the final or strongest candidate in a task chain, but is not formally approved until the user confirms.

`partial-reference`: A material has one useful quality, such as lighting, material, composition, crop, or page integration, but should not be copied as a whole.

`failure-candidate`: A material likely deserves entry into the failure bank because the user rejected it, the same flaw repeated, or the README/REPRODUCTION states a visible failure.

`process-only`: Ordinary intermediate draft. Keep it in task output/history and do not add it to formal knowledge.

`source-material`: Raw product, logo, background, generated scene, or reference asset that may be reused but is not itself a finished website visual.

`risk-material`: Any material that touches product facts, application claims, certification, customer use, performance, export markets, patents, compliance, or verified specifications.

## Default Decisions

- Treat intermediate drafts as `process-only` unless there is clear evidence of future value.
- Treat user-approved or final selected versions as `final-candidate`, not `approved`, until user confirmation.
- Treat user-rejected images as `failure-candidate`, not formal `rejected`, until user confirmation.
- Treat competitor materials as `competitor-reference`, never as direct Jiangyue design rules.
- Treat AI-generated product-like images as concept visuals unless the user confirms they match real products.

## Confirmation Required

Ask for confirmation before writing any item as:

- `approved`
- `rejected`
- `source-only`
- product fact or claim boundary
- formal competitor reference
