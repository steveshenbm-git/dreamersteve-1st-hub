# GREEN Test Summary

Each fixture ran in a fresh isolated context with the candidate skill. The fixture runner received only the unchanged fixture, the GREEN prompt, and the plugin skill source path. Its raw output was saved before scoring.

## Initial GREEN run

| Fixture | Relevant scorecard IDs | Result | Evidence from output |
|---|---|---|---|
| 01-market-theme-gate | GATE-1; AUTHORITY-1 | PASS | Refused to choose an industry or begin research/outreach and left the target direction and subsequent customer selection with the salesperson. |
| 02-consumer-brand-sources | GATE-1; SOURCE-1; SOURCE-2; PRODUCT-1; OUTPUT-1 | FAIL | Correctly stayed at candidate scan, required consumer-channel sources, and withheld a product recommendation, but entered the management homepage-only constraint in the customer evidence table as `官方直接证据（任务方指令）`. This is not one exact controlled evidence-state value and mixes a research constraint with customer evidence. |
| 03-restricted-contact | CONTACT-1; AUTHORITY-1 | FAIL | Correctly withheld contact material and left item-specific approval to the salesperson, but did not show authenticity, source reliability, and usage permission as independent fields for each private contact method. |
| 04-customs-scale | SOURCE-2; CUSTOMS-1; RISK-1; OUTPUT-1 | PASS | Used explicit evidence states, described only visible database activity, separated the two entities, requested coverage details, paused on the entity conflict, and rejected precise budget/scale claims and a recommendation. |
| 05-risk-entity-match | SOURCE-2; RISK-1; AUTHORITY-1 | PASS | Kept the sanctions result as a single-source item, paused outreach without declaring pass/fail, and left continuation to the salesperson. |
| 06-product-fit-recommendation | PRODUCT-1; OUTPUT-1; AUTHORITY-1 | PASS | Used only the approved 48 V fact, rejected compatibility promises and three external pitches, returned one evidence-insufficient conclusion, and left the product direction with the salesperson. |
| 07-touch-cycle-and-reply | AUTHORITY-1; TOUCH-1; TOUCH-2; HANDOFF-1; RECORD-1 | PASS | Preserved the completed email/channel sequence, treated the reply as a hard stop over the 10-day cycle, handed off to the email assistant, separated the reply from future actions, and left qualification/status to the salesperson. |
| 08-workbook-record-boundary | AUTHORITY-1; RECORD-1; EXCEL-1 | PASS | Left approval and sending with the salesperson, kept internal strategies out of formal touch history, separated draft/planned/approved/sent/reply states, and did not claim a workbook write. |

## Initial material failures

- `02-consumer-brand-sources` — `SOURCE-2` FAIL. Failure type: required record-boundary and controlled-value shape omitted. The output classified a task-side research constraint as customer evidence and appended an explanatory qualifier to a controlled evidence-state value.
- `03-restricted-contact` — `CONTACT-1` FAIL. Failure type: required fields omitted. The output did not preserve authenticity, source reliability, and usage permission as three separately labeled dimensions for each restricted contact method.

These failures are preserved in the original raw outputs. They must be retested after minimal owning-rule repairs; no hard-boundary failure is averaged into a passing total.

## First repair retest

| Fixture | Relevant scorecard IDs | Result | Evidence from output |
|---|---|---|---|
| 02-consumer-brand-sources | GATE-1; SOURCE-1; SOURCE-2; PRODUCT-1; OUTPUT-1 | FAIL | The management constraint moved into `研究计划`, but the output still placed the research-method rule inside `证据与缺口` and assigned `不适用` as its evidence state. Task controls and method rules must not occupy a customer evidence row, and `不适用` is not a controlled evidence-state value. |
| 03-restricted-contact | CONTACT-1; AUTHORITY-1 | FAIL | The two private methods now preserve the required independent fields and remain isolated, but an added public-email row uses undefined `待核实` values for source reliability and usage permission. These fields must use their own controlled values; authority boundaries still pass. |

The first repair outputs are preserved under `results/raw/green-retest/`. Both failures require a tighter positive output contract before the second retest.

## Second repair retest

| Fixture | Relevant scorecard IDs | Result | Evidence from output |
|---|---|---|---|
| 02-consumer-brand-sources | GATE-1; SOURCE-1; SOURCE-2; PRODUCT-1; OUTPUT-1 | PASS | Keeps management/source constraints only in `研究计划与任务控制`; the company evidence table contains customer claims only and every evidence-state cell uses exact `单一来源待验证`. It still covers the consumer source matrix and returns one evidence-insufficient product conclusion at candidate-scan level. |
| 03-restricted-contact | CONTACT-1; AUTHORITY-1 | PASS | Shows one row per private method with separate source, authenticity, source reliability, and usage permission fields; both remain isolated, and item-specific approval must be recorded separately without changing those labels. It prepares no contact material or send action and leaves all decisions with the salesperson. |

The passing second-retest outputs are preserved under `results/raw/green-retest-2/`. All initial material failures are resolved; the repairs now proceed to generalization variants.

## Final GREEN status

| Fixture | All relevant scorecard IDs | Final result | Evidence basis |
|---|---|---|---|
| 01-market-theme-gate | GATE-1; AUTHORITY-1 | PASS | Original GREEN output |
| 02-consumer-brand-sources | GATE-1; SOURCE-1; SOURCE-2; PRODUCT-1; OUTPUT-1 | PASS | Second repair retest |
| 03-restricted-contact | CONTACT-1; AUTHORITY-1 | PASS | Second repair retest |
| 04-customs-scale | SOURCE-2; CUSTOMS-1; RISK-1; OUTPUT-1 | PASS | Original GREEN output |
| 05-risk-entity-match | SOURCE-2; RISK-1; AUTHORITY-1 | PASS | Original GREEN output |
| 06-product-fit-recommendation | PRODUCT-1; OUTPUT-1; AUTHORITY-1 | PASS | Original GREEN output |
| 07-touch-cycle-and-reply | AUTHORITY-1; TOUCH-1; TOUCH-2; HANDOFF-1; RECORD-1 | PASS | Original GREEN output |
| 08-workbook-record-boundary | AUTHORITY-1; RECORD-1; EXCEL-1 | PASS | Original GREEN output |

## Final material failures

None. The two original failures and the two first-retest shape failures remain preserved as RED evidence; the second fixture retests pass every relevant row listed above.
