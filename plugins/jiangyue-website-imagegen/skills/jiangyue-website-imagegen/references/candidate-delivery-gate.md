# Candidate Delivery Gate

Use this after a candidate passes visual self-check and intent-brief-result coordination. This gate decides whether the candidate is worth showing to the user.

## Core Rule

Do not deliver the least-bad image from a weak batch. A candidate must satisfy the active brief and intent on an absolute basis.

## Delivery Statuses

| Status | Meaning | User-facing handling |
|---|---|---|
| Rejected internally | Fails a hard gate | Do not present as a candidate |
| Analysis only | Useful as evidence or anti-reference | Present analysis, not as a usable image |
| Discovery candidate | Interesting but not in the active brief | Ask whether to revise brief before production continues |
| Candidate for review | Passes self-check, brief, intent, and quality threshold | May show to user for decision |
| Accepted draft | User accepted this specific draft or direction layer | May receive bounded local edits |
| Final export | Deterministic export from an accepted draft | May be archived or delivered as final |

## Required Review

```text
Candidate Delivery Gate
- Candidate:
- Delivery status:
- Absolute brief fit: pass/fail
- Original intent fit: pass/fail
- Visual value: pass/fail
- Brand and buyer fit: pass/fail
- Mechanism attribution: professional/credible from S; small-and-refined from S+O; affinity/life from R; industrial New Eastern order from O; recognition/state cue from I — pass/fail/not targeted
- Attribution mismatch or substitute cue:
- Small-size readability: pass/fail
- Batch-relative ranking used: yes/no
- If batch was used, why selected candidate is absolutely qualified:
- User-facing delivery allowed: yes/no
- If no, required analysis or next route:
```

## Hard Stops

Do not deliver as `Candidate for review` when:

- the candidate is only better than worse options in the same batch;
- it needs a written defense to look aligned;
- it is clean but generic, lifeless, or below the brief's visual grade;
- it repeats a rejected visual model;
- it changes the image role, claim boundary, or attention owner without planner/user acceptance;
- a targeted brand quality appears only through an incorrect substitute mechanism, such as glow for technology, a person for participation, motion effects for continuity, or teal dominance for recognition;
- it passes defect checks but has no meaningful design value for the page.
