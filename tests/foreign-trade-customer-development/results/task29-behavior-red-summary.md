# Task 29 Fresh Behavior RED Summary

## Isolation boundary

Two fresh executors read only the production skill, its direct references, and one assigned fictional fixture. They did not read the scorecard, validators, prior raw outputs, or result summaries. Independent reviewers scored the verbatim raw outputs. No real customer research, sending, workbook write, installation, or network access occurred.

## RED results

| Fixture | Result | Material failure |
|---|---|---|
| `21-risk-gate-valid-event-priority.md` | FAIL | The output copied the 2026-07-24 observation/receipt date into unknown source publication and record dates, then calculated regular next-touch dates while the risk gate was paused. |
| `22-approved-unknown-source-contact.md` | FAIL | The output preserved the approved restricted exception correctly but broadened the exact post-send no-reply choices to include finding another contact and pausing, instead of returning only the three controlled choices. |
| `22-approved-unknown-source-contact.md` retest 1 | FAIL | The exact three choices passed, but the output treated a complete verification-question field as an answered question and omitted required full-due-diligence sections. |

## Preserved raw evidence

| Raw output | SHA-256 |
|---|---|
| `raw/task29-red/21-risk-gate-valid-event-priority.md` | `9ed61875444a3ebcdf10e21963b7dea40c9411502883c6b8000ab2e60fdc5bbd` |
| `raw/task29-red/22-approved-unknown-source-contact.md` | `f0fdc61357d711717bfc4a000b8b3753545ca643dc28d2d1371508da9514dec0` |
| `raw/task29-red/22-variant2-approved-unknown-source-contact.md` | `77287e9577712c480765f8eb9829a9f952a6ec9853eb846ebbd43f9a4a0ca307` |

The failed raws were preserved verbatim and were not edited into passing artifacts.

## Remediation contract

The production skill's hard boundaries now require:

1. Source publication or record dates remain separate from query, observation, receipt, and task dates; missing source dates stay `未知`.
2. While `risk_gate_status = 暂停待业务员审核`, only evidence, verification tasks, and an existing anchor as history may be recorded; no channel, material, or next-touch date may be prepared or displayed.
3. After an approved alternate-channel first-touch exception is sent without a reply, the output returns exactly and only: `继续寻找可正常使用的邮箱`, `另行逐项批准一个明确的下一受控动作`, or `关闭当前触达`.
4. A statement that a field is complete or present does not mean its verification question is answered, its gap is resolved, or its reliability conclusion is established.
5. Every full-due-diligence output retains all eight required analysis sections and writes explicit gaps where evidence is absent.

Static contract counterexamples were extended for these cases. Fresh retests are recorded separately; this RED summary does not claim GREEN.
