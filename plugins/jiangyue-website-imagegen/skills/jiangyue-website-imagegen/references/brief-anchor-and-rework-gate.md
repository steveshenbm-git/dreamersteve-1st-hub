# Brief Anchor And Rework Gate

Use this before any rework after a generated result is rejected, disputed, or found to drift from the brief.

## Core Rule

A rejected candidate cannot become the next baseline unless the user explicitly accepts its direction. Default rejected candidates are anti-references.

## Required Lock

```text
Brief Anchor Lock
- Original intent:
- Active brief:
- Accepted direction, if any:
- Rejected candidate:
- Rejected because:
- Salvageable elements:
- Forbidden carry-over:
- Next-round baseline:
- New draft must compare against:
- Rework route: local repair / rebuild from brief / revise brief / stop
```

## Rework Routes

| Situation | Baseline | Route |
|---|---|---|
| Local artifact, edge issue, crop, small tonal mismatch | Accepted draft | Local repair |
| Candidate mostly fits brief, one execution defect remains | Accepted or candidate draft, if direction accepted | Bounded revision |
| Candidate has major brief drift | Original brief | Rebuild from brief |
| Candidate suggests a better direction outside brief | Original brief until brief is revised | Discovery analysis, then planner/user acceptance |
| Brief itself caused the failure | Revised planner brief | Return to planner |

## Hard Rules

- "Keep improving this" is not enough when the current candidate is rejected or has brief drift.
- Do not optimize a rejected visual model merely because it is the latest file.
- Do not carry over visual elements from a failed candidate unless they are listed as salvageable.
- If the next-round baseline is the rejected candidate, cite the exact user acceptance that made it valid.
