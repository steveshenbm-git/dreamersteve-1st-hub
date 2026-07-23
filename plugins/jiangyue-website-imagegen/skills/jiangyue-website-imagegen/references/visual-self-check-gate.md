# Visual Self-Check Gate

Use this after producing or revising a candidate, before any user-facing delivery claim. This gate blocks visible defects; it does not prove the result is worth showing.

## Core Rule

Self-check is a delivery license, not a comment. If evidence is missing or fails, do not deliver the candidate as a result.

## Required Evidence

```text
Visual Self-Check Evidence
- Candidate:
- Baseline or reference:
- User-named defect register:
- Full-size image checked: yes/no
- Review-size or thumbnail checked: yes/no
- Side-by-side comparison: path / not applicable
- Normal-view visible change: pass/fail/not applicable
- Forbidden object check: pass/fail
- User defect check: pass/fail
- Brief fidelity quick check: pass/fail
- Self-check status: pass/fail
- If fail, delivery blocked because:
```

## Hard Rules

- File existence, correct dimensions, successful script output, prompt compliance, and archive completeness are not visual verification.
- Amplified difference images may help diagnose, but they do not prove a user-visible change. If normal full-size and review-size views do not show the requested change, mark fail.
- For revisions, compare with the prior draft or reference. Single-image review is not enough when a prior state exists.
- Copy user-named defects verbatim. Do not soften "I cannot see the air layer" into "air layer can be stronger."
- If the candidate passes this gate, it may enter the candidate delivery gate. It is not automatically deliverable.

## Fail Conditions

Fail when:

- any blocking user-named defect remains visible;
- the requested visible change is not clear in normal review size;
- the candidate relies on labels or explanation to show the improvement;
- forbidden objects, fake claims, fake UI, readable generated text, or unsupported product details appear;
- the candidate no longer supports the active brief or local edit intent.
