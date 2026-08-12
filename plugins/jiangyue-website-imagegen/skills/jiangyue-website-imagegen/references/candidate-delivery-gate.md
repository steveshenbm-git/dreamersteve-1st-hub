# Candidate Delivery Gate

Use this after a candidate passes visual self-check and intent-brief-result coordination. This gate decides whether the candidate is worth showing to the user.

## Core Rule

Do not deliver the least-bad image from a weak batch. A candidate must satisfy the active brief and intent on an absolute basis.

Match the claim to the review object. When page use depends on HTML copy, CTA, or responsive layout, a raw bitmap with pending composite proof is an `Image-base candidate`, not a page-level `Candidate for review`.

## Delivery Statuses

| Status | Meaning | User-facing handling |
|---|---|---|
| Rejected internally | Fails a hard gate | Do not present as a candidate |
| Analysis only | Useful as evidence or anti-reference | Present analysis, not as a usable image |
| Discovery candidate | Interesting but not in the active brief | Ask whether to revise brief before production continues |
| Image-base candidate | Standalone bitmap clears its current image-level gates but page use still awaits required composite proof | May show only as an image-base review object |
| Candidate for review | Passes self-check, brief, intent, and quality threshold | May show to user for decision |
| Accepted draft | User accepted this specific draft or direction layer | May receive bounded local edits |
| Final export | Deterministic export from an accepted draft | May be archived or delivered as final |

## Required Review

```text
Candidate Delivery Gate
- Candidate:
- Review object: standalone asset / image base / desktop composite / mobile composite
- Delivery status:
- Whole-image synthesis: pass/fail/unverified — reuse full-size and review-size Visual Self-Check evidence; no compensation by local detail
- Semantic purpose: source / defined or missing / observed image-role result
- Reality floor: pass/fail/unverified — reuse fact/material, physical plausibility, claim-boundary, formula, scene-invariant, and visual-self-check evidence
- Visual-quality floor: waiting on reality/pass/fail/unverified — reuse visual value, composition, hierarchy, craft, brand/buyer fit, and small-size evidence only after reality passes
- Page-use proof: defined/awaiting composite/pass/fail/unverified — name every required review object and reuse actual copy/layout/CTA composite evidence
- Ordered no-compensation verdict: pass/fail — reality first, visual quality second, page use last
- First blocking factor:
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

- the reality floor fails or remains unverified;
- whole-image synthesis fails or remains unverified at full size or review size;
- visual quality is being passed before reality, or page use is being passed before the named assembled review objects are inspected;
- current copy, layout responsibility, CTA, or breakpoint evidence is missing but page use is reported as passed;
- a strong factor is being used to excuse or compensate for a failed factor;
- the candidate is only better than worse options in the same batch;
- it needs a written defense to look aligned;
- it is clean but generic, lifeless, or below the brief's visual grade;
- it repeats a rejected visual model;
- it changes the image role, claim boundary, or attention owner without planner/user acceptance;
- a targeted brand quality appears only through an incorrect substitute mechanism, such as glow for technology, a person for participation, motion effects for continuity, or teal dominance for recognition;
- it passes defect checks but has no meaningful design value for the page.
- it came from a diagnostic attempt and is therefore `analysis only`, regardless of apparent quality.
