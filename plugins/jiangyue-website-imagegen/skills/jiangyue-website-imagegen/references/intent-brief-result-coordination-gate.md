# Intent Brief Result Coordination Gate

Use this after visual self-check for brief-based, high-impact, repeated-failure, or strategy-sensitive image work.

## Core Rule

Intent, brief, and result have different authority.

- Intent is the north star: why the image exists, who it serves, and what success means.
- Brief is the execution contract: how the intent is translated into visible constraints.
- Result is evidence or a candidate. It cannot silently rewrite the brief or intent.

## Required Check

```text
Intent-Brief-Result Check
- Original intent:
- Active brief:
- Generated result:
- Result vs brief: pass / partial / fail
- Result vs intent: pass / partial / fail
- If result conflicts with brief:
  - execution failure / brief too weak / brief wrong / method wrong
- If result satisfies brief but conflicts with intent:
  - brief failure / return to planner or Workflow Director
- If result reveals a better direction:
  - discovery candidate / not new baseline until accepted
- Next state:
  - reject / analysis only / revise from original brief / revise brief / candidate for review
```

## Decision Table

| Result state | Meaning | Next action |
|---|---|---|
| Fails brief and fails intent | Execution or method failure | Reject, analyze, rebuild from original brief or change method |
| Fails brief but suggests useful direction | Discovery candidate | Analyze only; planner/user must accept before brief update |
| Passes brief but fails intent | Brief failure | Return to planner or Workflow Director; do not polish |
| Passes brief and intent | Eligible for candidate delivery gate | Continue to candidate delivery review |

## Hard Rules

- A result may inform a new brief, but it cannot become the brief automatically.
- A brief may translate intent, but it cannot replace intent.
- A result that satisfies brief wording but misses the original intent is still a failure.
- Do not reinterpret the user's original job to make a generated result look successful.
