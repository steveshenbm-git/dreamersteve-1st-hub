# Failure Reset Hard Gates

Use this file when a Jiangyue image task has repeated visual failure, user frustration, missed references, or a self-check breakdown. These are hard delivery gates, not advice.

## Trigger

Enter failure reset before producing another image when any of these happen:

- the same visible defect remains after one revision
- the user says self-check failed, still wrong, not qualified, ugly, missed the reference, did not look at the attachment, or similar
- the user marks a defect in red or names a specific visible defect
- two drafts fail for the same structural reason
- the production method caused the defect, such as script curves used for an organic natural structure

Do not continue with small adjustments until this reset is complete.

## Required Reset Record

Before revising, write a short internal or user-visible reset record:

```text
Failure Reset
- User-named defect register:
- Failed method:
- Failure category:
- Why small revision is invalid:
- New method or structure:
- Hard pass/fail checks:
```

Copy user-named defects verbatim when possible. A defect in this register is a blocking item.

## User-Named Defect Register

- Every user-named visible defect must be copied into the register.
- A draft may not be delivered if any registered defect remains visible at full size or thumbnail size.
- If a registered defect remains after one revision, reject the draft internally.
- If the same registered defect remains after two revisions, stop the method and either change production method/structure or return to planner.
- Do not replace the user's defect with a softer paraphrase that is easier to pass.

## Method Change Gate

After a structural failure, the next revision must change at least one of:

- production method
- visual model
- source/reference basis
- composition structure
- subject carrier
- crop/scale hierarchy

Changing only color, glow, blur, opacity, border, shadow, line weight, gradient, or export size is not a valid revision.

## Organic Structure Gate

For natural or organic structures such as leaves, leaf veins, tree branches, plants, people, natural textures, realistic scenes, or natural material detail:

- Do not use deterministic vector/Python/SVG geometry as the final visual method unless the user explicitly requests a flat/vector style.
- Use image generation, image editing, real source imagery, or a photographic reference-driven method first.
- Deterministic tools may still be used for crop, export, mask cleanup, text overlays, review thumbnails, compression, and reproducible final sizing.

## Reference Translation Gate

Every important reference must be translated into pass/fail structure:

```text
Reference:
- Source:
- What to keep:
- What to avoid:
- Visible pass criteria:
- Used to generate this version: yes/no
```

Do not record a link as if it was used to generate the image when it was only mentioned later or used as a future direction.

## Candidate Review Table

When multiple generated candidates exist, create a short candidate table before delivery:

```text
Candidate Review
- Candidate:
- Pass / Reject:
- Rejection reason:
- User-named defects checked:
- Forbidden elements checked:
```

Do not deliver from a batch if rejected candidates are not accounted for and the selected candidate is not checked against the defect register.

## Two-Layer Self-Check

Run both layers before delivery:

### Layer 1: Forbidden Object Check

Check for product, readable text, arrow, black carrier block, logo, CTA, fake UI, dashboard, fake specs, certificates, customer marks, and any item forbidden by the brief.

### Layer 2: User Defect Check

Check every item in the User-Named Defect Register. Each item must be judged as pass/fail from the rendered image, not explained away.

If either layer fails, do not deliver.

## Draft Before Final

After failure reset, produce or select a draft first. Do not create a 4K/final asset directly unless the task is only deterministic export from an already accepted draft.

Final or 4K export is allowed only when:

- the draft was accepted by the user, or
- the user asked only for deterministic export from a previously accepted draft.

## Verification Gate

A successful script run, saved file path, or correct dimensions is not visual verification.

Before delivery, inspect:

- the full-size or largest available rendered output
- one thumbnail or review-size output

If visual inspection is unavailable, say so and do not claim the image passed.

## Pressure Scenarios For Skill Validation

Use these scenarios to validate future edits to this skill:

1. **Organic leaf failure:** User asks for natural leaf veins. Draft looks like abstract curves. Expected behavior: register the defect, stop deterministic curve drawing as final method, and switch to image generation/editing or reference-driven source imagery.
2. **Red-marked defect:** User marks curves or blocks in red. Expected behavior: copy the marked defect into the register and reject any revision where the same defect remains visible.
3. **Candidate contains forbidden elements:** Batch contains candidates with product, arrow, text, fake UI, or black carrier block. Expected behavior: reject those candidates and record reasons before selecting any output.
4. **Reference attribution check:** A reference link was surfaced by the assistant and later re-raised by the user. Expected behavior: record it as conversation/assistant-sourced reference confirmed by user, not as a new user-only reference, and state whether it was used to generate the current version.
5. **4K export after failure:** User requests 3840 x 2160 after a disputed draft. Expected behavior: do not generate final directly; only export 4K deterministically from an accepted draft.
