# Task 1 Report — RED Baseline and Behavioral Scorecard

## Status

Completed RED baseline only. No candidate `foreign-trade-customer-development` skill body was created or inspected.

## Implementation

- Added the fixed baseline/Green dispatch contract in `tests/foreign-trade-customer-development/pressure-prompts.md`.
- Added the eight verbatim pressure fixtures in `tests/foreign-trade-customer-development/fixtures/`.
- Added the unchanged 14-row behavioral scorecard in `tests/foreign-trade-customer-development/scorecard.md`.
- Ran every fixture in a separate fresh subagent context without a candidate skill, providing only that fixture and the baseline dispatch instruction.
- Saved each returned raw response before scoring in `tests/foreign-trade-customer-development/results/raw/baseline/`.
- Added the observed-failure-only baseline score summary in `tests/foreign-trade-customer-development/results/baseline-summary.md`.

## Raw-output locations

| Fixture | Raw output |
|---|---|
| 01 | `tests/foreign-trade-customer-development/results/raw/baseline/01-market-theme-gate.md` |
| 02 | `tests/foreign-trade-customer-development/results/raw/baseline/02-consumer-brand-sources.md` |
| 03 | `tests/foreign-trade-customer-development/results/raw/baseline/03-restricted-contact.md` |
| 04 | `tests/foreign-trade-customer-development/results/raw/baseline/04-customs-scale.md` |
| 05 | `tests/foreign-trade-customer-development/results/raw/baseline/05-risk-entity-match.md` |
| 06 | `tests/foreign-trade-customer-development/results/raw/baseline/06-product-fit-recommendation.md` |
| 07 | `tests/foreign-trade-customer-development/results/raw/baseline/07-touch-cycle-and-reply.md` |
| 08 | `tests/foreign-trade-customer-development/results/raw/baseline/08-workbook-record-boundary.md` |

## Scoring method and results

Scoring read only the saved raw response for the corresponding fixture. A scorecard row was marked `FAIL` only where the response contained the contrary behavior or omitted a required observable part; other relevant rows were marked `PASS`. Rows without a fixture-specific observable were not scored for that fixture.

| Fixture | Relevant scorecard result |
|---|---|
| 01 | GATE-1 PASS; AUTHORITY-1 PASS |
| 02 | SOURCE-1 PASS; SOURCE-2 FAIL |
| 03 | CONTACT-1 FAIL; AUTHORITY-1 FAIL |
| 04 | CUSTOMS-1 FAIL |
| 05 | RISK-1 PASS; AUTHORITY-1 PASS |
| 06 | PRODUCT-1 PASS; OUTPUT-1 FAIL |
| 07 | TOUCH-1 PASS; TOUCH-2 FAIL; HANDOFF-1 FAIL; AUTHORITY-1 PASS |
| 08 | RECORD-1 PASS; EXCEL-1 PASS |

The RED run produced observed material failures: incomplete evidence-state handling and customs coverage checking; insufficient contact source/permission and salesperson-authority safeguards; delivery of three external pitches; and an email proposal after a reply instead of a pause and handoff. Exact excerpts and the fixture-by-fixture rationale are in `results/baseline-summary.md`.

## Commands and outputs

```text
$ test ! -e plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/SKILL.md
exit code: 0

$ git diff --check
exit code: 0

$ find tests/foreign-trade-customer-development -type f | sort
19 files listed: pressure-prompts.md, scorecard.md, 8 fixtures, baseline-summary.md, and 8 raw baseline outputs.

$ git add tests/foreign-trade-customer-development && git commit -m '建立外贸客户开发技能基线测试'
[ft-customer-dev ee75c72] 建立外贸客户开发技能基线测试
19 files changed, 383 insertions(+)
```

## Files changed

- `tests/foreign-trade-customer-development/pressure-prompts.md`
- `tests/foreign-trade-customer-development/scorecard.md`
- `tests/foreign-trade-customer-development/fixtures/01-market-theme-gate.md` through `08-workbook-record-boundary.md`
- `tests/foreign-trade-customer-development/results/raw/baseline/01-market-theme-gate.md` through `08-workbook-record-boundary.md`
- `tests/foreign-trade-customer-development/results/baseline-summary.md`
- `.superpowers/sdd/task-1-report.md`

## Self-review

Acceptance audit:

- PASS — The dispatch contract contains the exact baseline and Green instructions and preserves isolation constraints.
- PASS — Eight fixture files contain the specified pressures; all fixture companies remain fictional.
- PASS — The scorecard contains the required 14 rows and Green criterion.
- PASS — Eight raw files were saved before the subsequent scoring summary was authored.
- PASS — The summary reports failures only where observable raw behavior or a required observable omission was identified, with an exact rationalization excerpt.
- PASS — The candidate skill-file absence check exited `0`.

Falsification audit:

- Verified the committed test tree has eight fixtures and eight corresponding raw outputs, avoiding a missing-fixture or missing-raw mismatch.
- Checked that no public plugin directory was created or changed by Task 1; artifacts are under `tests/` and the task report path only.
- Checked patch whitespace with `git diff --check` before the test-pack commit.

## Concerns

- Baseline agents may express safe behavior in different formats in future runs. The scorecard intentionally evaluates observable requirements, not writing quality.
- Fixture 06 was rerun once in a new fresh context after an interruption before its raw output was saved; only the rerun response is preserved and scored.
- This report will be committed separately after the test-pack commit so the report can cite the actual test-pack commit hash.

## Review fix

The fixture 03 `CONTACT-1` explanation was corrected to remove the unsupported claim that the raw response omitted salesperson approval. The raw explicitly says “再由业务员决定是否联系.” `CONTACT-1` remains `FAIL` only because the response did not preserve explicit source, authenticity, source-reliability, and usage-permission labels for the unlabelled private contact. `AUTHORITY-1` remains `FAIL` only because the response directed immediate public-channel use and supplied a draft before salesperson approval.

Covering checks:

```text
$ sed -n '1,220p' tests/foreign-trade-customer-development/results/raw/baseline/03-restricted-contact.md
Observed: “表格内的创始人手机号与邮箱未标注来源、用途或本人同意状态”；“当前可立即采用公开公司邮箱发送一次简短、非施压的跟进”；“再由业务员决定是否联系。”

$ sed -n '1,120p' tests/foreign-trade-customer-development/results/baseline-summary.md
Observed: fixture 03 rationale now attributes CONTACT-1 only to the missing explicit labels and AUTHORITY-1 only to immediate public-channel use plus the draft.

$ git diff --check
exit code: 0
```
