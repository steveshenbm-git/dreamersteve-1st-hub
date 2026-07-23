# Failure Reset Hard Gates

Use this file when a Jiangyue image task has repeated visual failure, user frustration, missed references, or a self-check breakdown. These are hard delivery gates, not advice.

## Trigger

Enter failure reset before producing another image when any of these happen:

- the same visible defect remains after one revision
- the user says self-check failed, still wrong, not qualified, ugly, missed the reference, did not look at the attachment, or similar
- the user marks a defect in red or names a specific visible defect
- two drafts fail for the same structural reason
- the production method caused the defect, such as script curves used for an organic natural structure
- the user says a requested visible change did not happen, such as repeated enlargement, cleanup, softening, or color control with no apparent result
- a candidate passed a narrow self-check but is still visually weak, generic, off-intent, or not worth showing
- a rejected candidate is being treated as the next baseline without explicit user acceptance
- repeated generation attempts are happening without a changed method, visual model, source basis, edit scope, or brief

Do not continue with small adjustments until this reset is complete.

## Required Sequence

Failure reset is a four-step workflow. Do not skip directly to a new prompt, new method, or new draft.

1. **Analyze the problem / 分析问题:** state the visible failure, user-named defects, baseline version, affected image role, references, and evidence checked.
2. **Find the root cause / 找到问题:** name the failed layer. The failed layer may be above imagegen: macro planning, core intent, intent lock, strategic layer ownership, page strategy, image role, strategy brief, Visual Composition Contract, source/reference use, production method, edit scope, verification, or delivery judgment. State the wrong assumption and why the previous method cannot solve the defect.
3. **Propose the method / 提出方法:** choose the next route and method change. State what method, structure, reference basis, mask/edit scope, or composition element must change, and which shortcuts are rejected.
4. **Output the plan / 输出方案:** produce the next-round plan with protected elements, changed elements, pass/fail checks, draft-before-final rule, and verification evidence required before delivery.

If any step cannot be answered from available evidence, stop production and return to Workflow Director or planner instead of generating another image.

## Root-Cause Climb Gate

The root-cause step is the core of failure reset. It must be allowed to climb above the current production skill.

Before choosing a new method, ask:

- Is the core intent clear enough to lock what must keep, change, avoid, and pass?
- Is the macro planning layer clear, or is the task mixing brand strategy, visual system, page role, and image production?
- Is the failure caused by a missing or wrong Planner Brief / Visual Composition Contract rather than image execution?
- Is imagegen being asked to solve a decision that belongs to Workflow Director or planner?

If macro planning, core intent, or intent lock is unclear, imagegen must not solve it with a new prompt or method. Return to Workflow Director for Strategic Layer Lock, or to planner when the missing decision is page/image strategy.

## Required Reset Record

Before revising, write a short internal or user-visible reset record:

```text
Failure Reset
- Step 1 - Problem analysis:
- User-named defect register:
- Baseline / evidence checked:
- Step 2 - Root cause:
- Failed layer:
- Root-cause climb needed: yes/no
- If yes, target owner: Workflow Director / planner / imagegen
- Wrong assumption:
- Failed method:
- Failure category:
- Why small revision is invalid:
- Step 3 - Proposed method:
- New method or structure:
- Rejected shortcut(s):
- Brief anchor:
- Next-round baseline:
- Step 4 - Output plan:
- Protected elements:
- Changed elements:
- Hard pass/fail checks:
- Verification required before delivery:
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

## Observable Change Gate

When the user says a requested change did not happen, the next candidate must prove the change visually. Do not rely on parameter changes, prompt wording, saved filenames, or claimed edit strength.

Required check:

```text
Observable Change Check
- Requested visible change:
- Baseline version:
- New version:
- What should be visibly different:
- Full-size pass/fail:
- Thumbnail/review-size pass/fail:
- If fail, changed method or edit scope:
```

If the difference is not visible at full size and review size, reject the candidate internally. A third attempt for the same observable change must change method, edit scope, reference source, mask strategy, or composition structure before production.

## Brief Anchor Gate

Before another production attempt, decide whether the next baseline is the original brief, an accepted draft, a revised brief, or a rejected candidate used only as an anti-reference.

Use [brief-anchor-and-rework-gate.md](brief-anchor-and-rework-gate.md) when any candidate was rejected, disputed, or found to drift from the brief.

Hard rules:

- Rejected candidates default to anti-reference status.
- Do not optimize the latest candidate simply because it is the latest file.
- If the next baseline is a rejected candidate, cite the user's explicit direction acceptance.
- If the failure is brief drift, rebuild from the original brief or return to planner.

## Rejected Result Analysis Gate

When a candidate fails self-check, brief fit, intent fit, or delivery value, use [rejected-result-analysis-gate.md](rejected-result-analysis-gate.md) before producing again.

Hard rules:

- Failed outputs may be analyzed, but not delivered as usable candidates.
- If a failed output reveals a better direction, label it as a discovery candidate and route to planner or user acceptance before changing the brief.
- Do not ask the user to choose from a batch of rejected outputs.

## False-Pass Gate

When a candidate passes defect checks but still feels wrong, generic, low-grade, or off-intent, treat this as a false pass.

Required response:

```text
False-Pass Review
- What passed:
- What still fails:
- Missed gate: visual value / brief fit / intent fit / buyer credibility / method quality
- Why the self-check was insufficient:
- Candidate status: rejected internally / analysis only / discovery candidate
- Rule or gate to strengthen:
```

Do not deliver a false-pass candidate as `Candidate for review`.

## Attempt Stop Gate

For high-impact, cost-bearing, or repeated-failure tasks, use [attempt-stop-and-method-escalation-gate.md](attempt-stop-and-method-escalation-gate.md).

Hard rules:

- Each new attempt must test a distinct hypothesis.
- Same-method prompt retries are blocked after a repeated visible failure.
- After the stop trigger fires, output analysis or return to planner / Workflow Director instead of generating again.

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
6. **No visible enlargement:** User asks to expand water ripples three times and says there is no change. Expected behavior: stop small parameter edits, run Observable Change Check, and require a materially larger edited area or changed method before another draft.
7. **Reset jumps to new draft:** A draft fails and the next response proposes a new prompt without naming the failed layer or wrong assumption. Expected behavior: block production, complete the four-step Failure Reset sequence, and only then decide whether imagegen, planner, or Workflow Director owns the next action.
8. **Macro intent failure misread as prompt issue:** The user says the image keeps failing because the brand direction, life/AI/industrial relationship, or core intent was never locked. Expected behavior: root-cause climb to macro planning or intent lock, return to Workflow Director for Strategic Layer Lock, and forbid another image prompt as the next action.
9. **A13 invisible air layer:** Brief asks for a visible silver-gray air layer, but normal review-size output shows no visible change and only amplified diff makes it detectable. Expected behavior: reject internally, record "air layer not visible" verbatim, and rebuild with changed edit scope or visual model before delivery.
10. **False pass:** Candidate avoids forbidden objects and defects but remains generic, lifeless, or below brief quality. Expected behavior: mark false pass, block delivery, run candidate delivery or design-upgrade review.
11. **Rejected baseline drift:** Candidate drifts from the brief, is rejected, then the next round starts optimizing that candidate. Expected behavior: treat candidate as anti-reference unless user explicitly accepts its direction; next baseline returns to original or revised brief.
12. **Least-bad batch option:** A batch contains only weak candidates and the assistant selects the least-bad one. Expected behavior: reject the batch or mark analysis only; do not deliver a relative winner as a candidate.
13. **Endless background attempts:** Multiple API/generation attempts repeat the same hypothesis. Expected behavior: stop after the attempt stop rule, analyze failed hypotheses, and route to method change, planner, or Workflow Director.
