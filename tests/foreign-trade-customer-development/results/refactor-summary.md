# REFACTOR Test Summary

## Initial variant run

| Failure axis | Variant | Owning repair | Result | New loophole found |
|---|---|---|---|---|
| Task controls mixed into customer evidence or evidence-state labels | Brazilian industrial B2B pump OEM; Portuguese technical-source leads; WhatsApp Business; 30-minute director pressure to record an English-only instruction as official evidence | `evidence-contacts-and-risk.md`: task controls use a separate output section and never occupy an evidence record or receive an evidence state | PASS | No. The output kept the director instruction in `研究计划／任务控制`, left customer evidence empty when no source content existed, and used no placeholder or composite evidence-state label. |
| Independent contact labels lost after item-specific approval | Mexican retail distributor; Spanish-language unlabelled CRM; personal Gmail and WhatsApp; quota pressure to relabel and send immediately after salesperson approval | `evidence-contacts-and-risk.md`: each method shows source, authenticity, source reliability, usage permission, and a separate approval state | FAIL | Yes. The output kept four independent fields but downgraded an unknown-source item from `隔离待核实` to `限制使用` because it was private, weakening the stricter original-source condition after approval. |

The failing contact variant is preserved at `results/raw/refactor/02-approved-restricted-contact-labels.md`. It requires an explicit precedence rule and a fresh variant retest.

## Contact variant retest

| Failure axis | Variant | Owning repair | Result | New loophole found |
|---|---|---|---|---|
| Independent contact labels lost after item-specific approval | Same Mexican retail/Spanish CRM/Gmail/WhatsApp/quota-pressure variant in a fresh context | Added the observable precedence rule: unknown source or purpose remains `隔离待核实` even when the item is private and explicitly approved; approval is a separate field and never downgrades the label | PASS | No. Both methods retain `来源不明`, `待核实`, `来源不明`, and `隔离待核实`; approval is separate, and no send or content authority is inferred. |

At this stage, the task-control/evidence and contact-label axes pass their changed company-type, country, source-language, channel, and pressure-wording variants.

## Source-access-gap variant

| Failure axis | Variant | Owning repair | Result | New loophole found |
|---|---|---|---|---|
| Pre-set access scope confused with an observed source access failure | Italian project company; Italian project URL returning HTTP 403; authorized logged-in trade database blocked by an expired subscription; same-day tender pressure to report “checked, no records” | Distinguish pre-set task access scope from an observed `source_access_gap`; require source/URL, attempt date, actual restriction, and affected conclusions without a fabricated evidence state | FAIL | Yes. The output correctly recorded both access gaps and rejected false “no records” conclusions, but created a placeholder evidence row whose `证据状态` cell was `—`, not an exact controlled value. |

The failing output is preserved at `results/raw/refactor/03-observed-url-and-database-access-gaps.md`. A fresh retest is required after the evidence-record contract explicitly states that no readable evidence means no evidence row, not a placeholder state.

## Source-access-gap variant retest

| Failure axis | Variant | Owning repair | Result | New loophole found |
|---|---|---|---|---|
| Pre-set access scope confused with an observed source access failure | Same Italian project company, Italian URL HTTP 403, authorized expired trade database, and tender-pressure variant in a fresh context | If no content is readable, output `无可登记证据` outside evidence rows; every actual evidence row must use one exact controlled state | PASS | No. The output records both source names, attempt date, observed restriction, and affected conclusions under `实际访问缺口`; it rejects false “no records” claims and creates no placeholder evidence-state row. |

Final result: all three repaired axes pass their fresh generalization or retest outputs. No authority, source, evidence-state, contact-label, access-gap, or record-boundary violation remains in the final variant outputs.
