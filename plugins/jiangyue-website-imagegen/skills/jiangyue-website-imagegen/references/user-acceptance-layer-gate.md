# User Acceptance Layer Gate

Use this whenever the user says a direction is acceptable, asks for a revision after review, requests final export, or responds ambiguously to an image draft.

## Core Rule

User acceptance has layers. Do not treat acceptance of one layer as acceptance of another.

## Acceptance Layers

```text
User Acceptance Layer
- Intent accepted: yes/no/unknown
- Brief accepted: yes/no/unknown
- Visual direction accepted: yes/no/unknown
- Specific draft accepted: yes/no/unknown
- Local edit accepted: yes/no/unknown
- Final export accepted: yes/no/unknown
- Approved archive accepted: yes/no/unknown
- Evidence or exact user wording:
- Next allowed action:
```

## Interpretation Rules

| User signal | Safe interpretation |
|---|---|
| "This direction can work" | Visual direction may be accepted; specific draft is not final |
| "Make the air layer stronger" | Bounded local revision only if current direction is accepted |
| "Still wrong" / "not qualified" | No acceptance; register defect and run routing/failure gate |
| "Use this one" | Specific draft accepted for bounded edit or deterministic export |
| "Export final / 4K" | Allowed only from an accepted draft or explicit deterministic export request |
| "Approved" | Ask/record whether this means draft acceptance, final export, or approved archive if ambiguous |

## Hard Rules

- Do not infer final approval from direction approval.
- Do not infer install, commit, archive, or approved-material status from image draft acceptance.
- Do not use an accepted direction to carry forward defects that were explicitly rejected.
- If acceptance is unclear and changes the next action, ask one concise question or return to Workflow Director.
