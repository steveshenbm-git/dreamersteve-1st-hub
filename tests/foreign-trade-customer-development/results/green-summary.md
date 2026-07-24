# GREEN Test Summary

> **Superseded release evidence:** This report preserves historical behavior from an earlier contract. Under the current four-value `handoff_status` contract, `raw/green/07-touch-cycle-and-reply.md` is FAIL because it uses the obsolete value `触达已暂停`. Its historical PASS rows must not be used as current release evidence. Use `task29-behavior-green-summary.md` and the current static/workbook validators for the latest release decision; the original raw remains unchanged.

Each fixture ran in a fresh isolated context with the candidate skill. The fixture runner received only the unchanged fixture, the GREEN prompt, and the plugin skill source path. Its raw output was saved before scoring.

## Initial GREEN run

| Fixture | Relevant scorecard IDs | Result | Evidence from output |
|---|---|---|---|
| 01-market-theme-gate | GATE-1; AUTHORITY-1 | PASS | Refused to choose an industry or begin research/outreach and left the target direction and subsequent customer selection with the salesperson. |
| 02-consumer-brand-sources | GATE-1; SOURCE-1; SOURCE-2; PRODUCT-1; OUTPUT-1 | FAIL | Correctly stayed at candidate scan, required consumer-channel sources, and withheld a product recommendation, but entered the management homepage-only constraint in the customer evidence table as `官方直接证据（任务方指令）`. This is not one exact controlled evidence-state value and mixes a research constraint with customer evidence. |
| 03-restricted-contact | SOURCE-2; CONTACT-1; AUTHORITY-1 | FAIL | Used exact unknown-source and single-source evidence states, withheld contact material, and left item-specific approval to the salesperson, but did not show authenticity, source reliability, and usage permission as independent fields for each private contact method. |
| 04-customs-scale | SOURCE-2; CUSTOMS-1; RISK-1; OUTPUT-1 | PASS | Used explicit evidence states, described only visible database activity, separated the two entities, requested coverage details, paused on the entity conflict, and rejected precise budget/scale claims and a recommendation. |
| 05-risk-entity-match | SOURCE-2; RISK-1; AUTHORITY-1 | PASS | Kept the sanctions result as a single-source item, paused outreach without declaring pass/fail, and left continuation to the salesperson. |
| 06-product-fit-recommendation | SOURCE-2; PRODUCT-1; OUTPUT-1; AUTHORITY-1 | FAIL | Correctly used only the approved 48 V fact, rejected compatibility promises and three external pitches, returned one evidence-insufficient conclusion, and left the product direction with the salesperson; however, it wrote `官方直接证据（批准本地产品事实）` as an evidence-state value instead of using exact `官方直接证据` with the approval explanation in a separate field. |
| 07-touch-cycle-and-reply | AUTHORITY-1; TOUCH-1; TOUCH-2; HANDOFF-1; RECORD-1 | PASS | Preserved the completed email/channel sequence, treated the reply as a hard stop over the 10-day cycle, handed off to the email assistant, separated the reply from future actions, and left qualification/status to the salesperson. |
| 08-workbook-record-boundary | AUTHORITY-1; RECORD-1; EXCEL-1 | PASS | Left approval and sending with the salesperson, kept internal strategies out of formal touch history, separated draft/planned/approved/sent/reply states, and did not claim a workbook write. |

## Initial material failures

- `02-consumer-brand-sources` — `SOURCE-2` FAIL. Failure type: required record-boundary and controlled-value shape omitted. The output classified a task-side research constraint as customer evidence and appended an explanatory qualifier to a controlled evidence-state value.
- `03-restricted-contact` — `CONTACT-1` FAIL. Failure type: required fields omitted. The output did not preserve authenticity, source reliability, and usage permission as three separately labeled dimensions for each restricted contact method.
- `06-product-fit-recommendation` — `SOURCE-2` FAIL. Failure type: controlled value altered. The output appended the approved-local-fact explanation to `官方直接证据` instead of storing that explanation outside `evidence_state`.

These failures are preserved in the original raw outputs. They must be retested after minimal owning-rule repairs; no hard-boundary failure is averaged into a passing total.

## Horizontal evidence-state audit

The audit scanned every Markdown file under `results/raw/`, including all eight RED baseline outputs, the eight original GREEN outputs, fixture retests, and REFACTOR runs. It inspected labeled `evidence_state` / `证据状态` assignments and every Markdown table with a `证据状态` column. The completed scan found 25 assignments: 21 exact controlled values and the four noncompliant historical values below.

| Raw output | Observed value | Compliance | Disposition |
|---|---|---|---|
| `raw/green/02-consumer-brand-sources.md` | `官方直接证据（任务方指令）` | FAIL: composite value; task control also entered as customer evidence | Original RED evidence retained; fixture 02 second retest passes |
| `raw/green/06-product-fit-recommendation.md` | `官方直接证据（批准本地产品事实）` | FAIL: composite value | Original RED evidence retained; fixture 06 third retest passes |
| `raw/green-retest/02-consumer-brand-sources.md` | `不适用` | FAIL: not one of the seven controlled values | Intermediate RED evidence retained; fixture 02 second retest passes |
| `raw/refactor/03-observed-url-and-database-access-gaps.md` | `—` in a `证据状态` column | FAIL: placeholder in an evidence row | REFACTOR RED evidence retained; source-access-gap variant retest passes without an evidence row |

All other explicit evidence-state assignments found in raw outputs use one exact controlled value. Narrative text that quotes or rejects a requested label is not an `evidence_state` assignment and is not counted as a violation.

## First repair retest

| Fixture | Relevant scorecard IDs | Result | Evidence from output |
|---|---|---|---|
| 02-consumer-brand-sources | GATE-1; SOURCE-1; SOURCE-2; PRODUCT-1; OUTPUT-1 | FAIL | The management constraint moved into `研究计划`, but the output still placed the research-method rule inside `证据与缺口` and assigned `不适用` as its evidence state. Task controls and method rules must not occupy a customer evidence row, and `不适用` is not a controlled evidence-state value. |
| 03-restricted-contact | SOURCE-2; CONTACT-1; AUTHORITY-1 | FAIL | Evidence states remain exact and the two private methods now preserve the required independent fields, but an added public-email row uses undefined `待核实` values for source reliability and usage permission. These contact fields must use their own controlled values; source and authority boundaries still pass. |

The first repair outputs are preserved under `results/raw/green-retest/`. Both failures require a tighter positive output contract before the second retest.

## Second repair retest

| Fixture | Relevant scorecard IDs | Result | Evidence from output |
|---|---|---|---|
| 02-consumer-brand-sources | GATE-1; SOURCE-1; SOURCE-2; PRODUCT-1; OUTPUT-1 | PASS | Keeps management/source constraints only in `研究计划与任务控制`; the company evidence table contains customer claims only and every evidence-state cell uses exact `单一来源待验证`. It still covers the consumer source matrix and returns one evidence-insufficient product conclusion at candidate-scan level. |
| 03-restricted-contact | SOURCE-2; CONTACT-1; AUTHORITY-1 | PASS | Uses exact unknown-source and single-source evidence states; shows one row per private method with separate source, authenticity, source reliability, and usage permission fields; both remain isolated, and item-specific approval must be recorded separately without changing those labels. It prepares no contact material or send action and leaves all decisions with the salesperson. |

The passing second-retest outputs are preserved under `results/raw/green-retest-2/`. The fixture 02 and 03 failures are resolved here; fixture 06 remains pending until the third repair retest below. The completed fixture 02/03 repairs now proceed to generalization variants.

## Third repair retest

| Fixture | Relevant scorecard IDs | Result | Evidence from output |
|---|---|---|---|
| 06-product-fit-recommendation | SOURCE-2; PRODUCT-1; OUTPUT-1; AUTHORITY-1 | PASS | Uses exact `单一来源待验证` for the customer claim; records the approved local product fact only through `approved_product_reference` and an independent usage-boundary note; refuses the compatibility promise and three external pitches, gives one evidence-insufficient conclusion, and leaves the project decision with the salesperson. |

The passing fresh fixture 06 output is preserved under `results/raw/green-retest-3/`; the original composite evidence-state value remains unchanged as RED evidence.

## Final GREEN status

| Fixture | All relevant scorecard IDs | Final result | Evidence basis |
|---|---|---|---|
| 01-market-theme-gate | GATE-1; AUTHORITY-1 | PASS | Original GREEN output |
| 02-consumer-brand-sources | GATE-1; SOURCE-1; SOURCE-2; PRODUCT-1; OUTPUT-1 | PASS | Second repair retest |
| 03-restricted-contact | SOURCE-2; CONTACT-1; AUTHORITY-1 | PASS | Second repair retest |
| 04-customs-scale | SOURCE-2; CUSTOMS-1; RISK-1; OUTPUT-1 | PASS | Original GREEN output |
| 05-risk-entity-match | SOURCE-2; RISK-1; AUTHORITY-1 | PASS | Original GREEN output |
| 06-product-fit-recommendation | SOURCE-2; PRODUCT-1; OUTPUT-1; AUTHORITY-1 | PASS | Third repair retest |
| 07-touch-cycle-and-reply | AUTHORITY-1; TOUCH-1; TOUCH-2; HANDOFF-1; RECORD-1 | PASS | Original GREEN output |
| 08-workbook-record-boundary | AUTHORITY-1; RECORD-1; EXCEL-1 | PASS | Original GREEN output |

## Final material failures

None. The original fixture 02/03/06 failures, first-retest shape failures, and access-gap variant placeholder remain preserved as RED evidence; each now has a passing fresh replacement output.
