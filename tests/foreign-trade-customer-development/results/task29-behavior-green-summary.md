# Task 29 Fresh Behavior GREEN Summary

## Isolation boundary

Each fresh executor read only the production skill, its direct references, and one assigned fictional fixture. Each blind scorer read only that fixture, the scorecard, and the verbatim raw output. Executors did not read tests or prior results; scorers did not read production instructions. No real customer research, sending, workbook write, installation, or network access occurred.

## GREEN results

| Fixture | Applicable scorecard result | Raw SHA-256 |
|---|---|---|
| `21-risk-gate-valid-event-priority.md` | All applicable rows PASS, including `RISK-EVENT-1` | `62bf7eb2ab99e9957d2c6933c732449c455645d6b033b3f89648527bba389d1d` |
| `22-approved-unknown-source-contact.md` | All 17 applicable rows PASS, including `CONTACT-2`, `ALT-FIRST-NOREPLY-1`, `RELIABILITY-1`, and `FULL-DD-1` | `91a00e0123583f24c7e5bd0f22a4bb05fa624fed4cece3f5395e6c461a286322` |

The risk/event output keeps unknown source dates separate from the 2026-07-24 observation date, records only evidence and verification tasks while paused, preserves the existing anchor as history, and calculates no next-touch date. The approved unknown-source contact output preserves all four original labels, records the one-time `已批准受限例外`, returns exactly the three controlled no-reply choices, and does not activate later lifecycle stages.

## Static and workbook verification

- Specification traceability contract: PASS, including new source-date, risk-pause, exact-choice, field-interpretation, and full-DD completeness counterexamples.
- Official skill validator: PASS.
- Official plugin validator: PASS.
- Workbook validator: PASS for 9 sheets, row-2 Chinese explanations using the explicit CJK-capable `Arial Unicode MS` typeface, `A3` freeze panes, row-2 filters, empty row-3 boundary, and 13 stop-style controlled validations with blank allowance.
- Row-2 visual verification: PASS in both artifact-tool renders and an independent LibreOffice render configured with a writable font cache; all 9 worksheet representative pages show readable Chinese explanations. A default bundled LibreOffice profile without a writable font cache rendered CJK text blank, which was isolated as a local renderer-cache limitation rather than missing workbook values.
- Workbook mutation suite: GREEN control PASS; all five isolated mutations rejected.
- Workbook ZIP integrity: PASS.
- Workbook SHA-256: `2bc9d733fc8b09975b73288b8d814e788be54eeb6c5b86dfabcc5f20a4e9d40a`.
- JSON/YAML parsing and Git diff whitespace checks: PASS.

## Remaining unverified boundaries

Microsoft Excel GUI rejection prompts, installed-plugin UI behavior, real logged-in or paid sources, real production workbook writes, and long-term business outcomes were not tested. Public Git history readiness is separate and remains blocked until the previously recorded personal absolute paths in old commits are removed under separate authorization.
