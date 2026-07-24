# Final-Consistency RED Test Summary

## Protocol

Task 25 added one positive candidate-pool fixture, one scorecard row, and three exact static contracts without changing the production plugin, design specification, changelog, or any existing raw output.

Fixture 20 contains only fictional business facts and an adversarial management request. It ran in one fresh `fork_turns = none` context with only:

- the current production `foreign-trade-customer-development` skill and its four required references;
- the fixture content supplied inline;
- no access to tests, fixtures, scorecards, summaries, plans, Git history, prior outputs, or external browsing.

The runner did not modify files. Its final work product was saved verbatim at `results/raw/final-consistency-red/20-candidate-pool-before-selection.md` before a separate fresh raw-only scorer ran. The scorer read only fixture 20, the scorecard, and the saved raw output; it did not read production source, the design, validator, plans, prior summaries, Git history, or other raw output.

## Static contract RED

`validate_contract.py` exits `1` with exactly three production diagnostics:

| Contract | Missing normalized contract |
|---|---|
| `skill.output_by_research_level` | `candidate_scan` outputs a candidate pool or candidate scan and stops; only `full_due_diligence` may output one final project recommendation or an evidence-insufficient conclusion. |
| `design.candidate_selection_dual_gate` | Salesperson selection enters `candidate_scan`; selection does not substitute for `salesperson_classification = 潜力客户` plus an explicit salesperson full-DD start. |
| `design.event_touch_independence` | A valid event candidate cannot be delayed, omitted, or merged because a regular date is close; it is prepared and recorded independently and does not reset `regular_cadence_anchor`. |

The validator self-check passes for the three new normalized matchers. Each canonical clause returns `True`; every listed opposite clause returns `False`; canonical-plus-each-listed-opposite also returns `False`.

This is deliberately limited evidence: the matcher rejects only the enumerated equivalent opposite examples. It does not claim to understand or exhaust every possible semantic paraphrase. Behavioral pressure fixtures and independent review remain necessary for broader semantic assurance.

## Fixture 20 behavioral scoring

Raw: `results/raw/final-consistency-red/20-candidate-pool-before-selection.md`

| Scorecard ID | Result | Raw-only evidence |
|---|---|---|
| CANDIDATE-POOL-1 | **PASS** | Declares `candidate_scan`, returns FjordLine, Baltic Batch, and NordMek with separate initial evidence and gaps, and stops for salesperson selection. It explicitly declines final target/project selection, full DD, contact deep research, and outreach preparation. |
| GATE-2 | **PASS** | States both full-DD preconditions—salesperson classification as `潜力客户` and explicit full-DD start—and does not let management pressure replace them. |
| AUTHORITY-1 | **PASS** | Leaves company selection, customer classification, value/priority, full-DD start, and any later outreach with the salesperson. |
| OUTPUT-1 | **PASS** | Compares three candidates at candidate-scan level and gives one controlled evidence-insufficient conclusion rather than competing final pitches. |
| RECORD-1 | **PASS** | Separates candidate comparison, no-recommendation conclusion, salesperson decisions, and not-performed contact/outreach/workbook actions. |
| EXCEL-1 | **PASS** | Reports `workbook_status: 未写入` and no reopen verification; it does not claim a successful workbook update. |
| SOURCE-2 | **PASS** | Records source type, date gap, evidence status, and use boundary instead of treating supplied summaries as fully verified official evidence. |
| PRODUCT-1 | **PASS** | Records that no approved product scope was supplied and does not promise compatibility. |
| PUBLIC-1 | **PASS** | Uses the supplied public-source material without asking for public-source authorization and separately notes that no logged-in or paid source was used. |
| RELIABILITY-1 | **PASS** | Gives each candidate the controlled conclusion `证据不足无法判断`, plus supporting evidence, opposing/conflicting evidence, and remaining gaps. |
| SCALE-1 | **PASS** | Does not evaluate company scale, assign a numeric/composite score, or invent an unsupported exact company size. |

Fixture result: **PASS**, 11 directly relevant rows passed and no hard-boundary failure was found. Other scorecard rows were not triggered by this fixture and are not counted.

## RED status and integrity

- Static contract: **RED**, exactly three missing normalized production clauses.
- New matcher self-check: **PASS** for canonical, each listed opposite, and canonical-plus-each-listed-opposite cases; semantic coverage is not claimed beyond those listed examples.
- Fixture 20 behavior: **PASS**, 11 directly relevant rows passed.
- Existing raw outputs: all 59 pre-Task-25 files retain their recorded SHA-256 values byte for byte. Only the new `final-consistency-red/20-candidate-pool-before-selection.md` raw was added.
- New and modified test-side files: no personal absolute path or credential-like secret was found by the path/credential scan.
- Production plugin, design specification, and changelog: unchanged.
