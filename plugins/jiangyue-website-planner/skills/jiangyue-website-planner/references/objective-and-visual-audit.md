# Objective And Visual Audit

Use this reference when the planner task involves visual judgment, brand direction, color systems, image review, repeated rework, user correction about process quality, or any claim that a visual/page result is good enough.

## Purpose

Planner must not optimize local steps while losing the real objective. The goal is not to complete a checklist, write a convincing explanation, or make the workflow look orderly. The goal is to produce decisions that are supported by visible facts and by the current business objective.

## Task Intent Lock

At the start of each task, identify the real objective behind the user's request.

Use this structure:

```text
Task Intent Lock
- Real objective:
- This task is not:
- Deliverable:
- Success evidence:
- Visual evidence required:
- Drift risks:
- Next allowed action:
```

Examples:

- If the user asks to compare brand color previews, the real objective may be `validate a meeting-ready color system`, not `add more options`.
- If the user asks to revise an image, the real objective may be `fix visual credibility`, not `perform another imagegen round`.
- If the user asks whether a workflow is sound, the deliverable is a workflow judgment, not a new asset.

Do not proceed when the objective is still vague. Ask one high-value question or state a conservative objective lock.

## Objective-Led Work Loop

Before every major step, check:

1. Does this step directly serve the locked objective?
2. Does it produce or inspect evidence that matters?
3. Is it only completing a local artifact, such as a summary, ranking, or file?
4. Could this step make the work look complete while the result remains visually weak?

If the answer exposes drift, stop and revise the workflow.

## Mandatory Visual Evidence Gate

For visual tasks, visible evidence is mandatory. Visual tasks include:

- homepage heroes
- imagegen drafts
- website previews
- color systems
- logo color decisions
- CTA and background color judgments
- image role and attention hierarchy
- visual ranking or option sorting
- design critique after user feedback

The planner must inspect the actual visible result:

- full image
- rendered page
- screenshot
- thumbnail
- comparison view
- user-provided visual reference

Do not substitute:

- option names
- written strategy
- intended meaning
- palette rules
- prompt compliance
- file existence
- generated summaries
- local HTML existence

If visual evidence cannot be inspected, say so and do not claim a visual judgment.

## Visual Fact Checklist

For each visual option or draft, inspect:

- What is visible at first glance?
- Is the option distinguishable without reading explanatory copy?
- Does the visible result support the locked objective?
- Does it look credible for European B2B industrial buyers?
- Does the logo color actually read well?
- Does the CTA look like a professional inquiry path?
- Does the status or technology color have the intended role?
- Does the background support brand meaning or become generic decoration?
- Does red, amber, blue, green, or cyan create unwanted semantics?
- Is the option being defended by logic instead of visible result?

If two candidates need written explanation to tell them apart, they are not visually distinct enough to both remain primary candidates.

## Whole Workflow Audit

Use Whole Workflow Audit whenever:

- a user challenges the process or reasoning
- a user says self-check failed, the reference was missed, or the attachment was ignored
- a user names or marks a visible defect
- a similar visual problem repeats
- a second revision does not materially improve the result
- sorting or summaries happen before visual fact checking
- verification only proves existence
- the work feels busy but the result remains weak
- the user's stated objective has drifted

Audit questions:

```text
Whole Workflow Audit
- Was the task objective correctly locked?
- Were the baseline assets or candidate set correct?
- Did we inspect all required visual evidence?
- Did we evaluate all required candidates before filtering?
- Did we rank before fact review?
- Did we summarize before visual checking?
- Did verification prove quality or only existence?
- Is the next action a local patch or a workflow reset?
- Are user-named defects copied into a blocking defect register?
- Are references correctly attributed as used, conversation-only, or next-version references?
```

If any answer shows a workflow flaw, stop local revision. Rebuild the workflow.

## Two-Failure Reset Rule

Two failed rework rounds require automatic Failure Reset.

Counting rule:

```text
Draft 1 / round 1 fails
-> one revision is allowed

Draft 2 / round 2 fails
-> stop local revision
-> run Whole Workflow Audit
-> trigger Failure Reset
```

Failure includes:

- the same user-named problem remains
- the new result is visually too similar to the prior result
- the result drifts from the locked objective
- the result only works through written explanation
- the user says the process failed
- verification checks files but not result quality

Immediate reset or routing review is required, even before two full rounds, when the user explicitly challenges self-check, reference use, or attachment review.

After two failures, prohibited actions:

- do not add another option
- do not repair one local detail
- do not continue ranking
- do not write a completion summary
- do not request imagegen
- do not claim the workflow is now sound

## Failure Reset

Failure Reset must rebuild:

```text
Failure Reset
- Real objective:
- Required evidence:
- Baseline assets:
- Candidate set or check objects:
- Work sequence:
- Pass/fail criteria:
- User-named defect register:
- Reference attribution:
- What is explicitly prohibited:
- Next allowed action:
```

Only after Failure Reset can planner continue.

## Meeting Preview And Brand Color Tasks

For meeting preview pages and color-system validation:

1. Inspect every initial visible option before sorting.
2. Do not treat candidate labels as visual facts.
3. Do not rank before deciding whether each option should be kept, adjusted, risk-labeled, or removed.
4. Do not let a written summary make a weak visual option look valid.
5. Verification must include visual review, not only `file exists` or `HTML contains headings`.

Meeting-ready means:

- the preview page opens
- all intended options are visible
- logo colors render
- options can be visually compared
- the summary reflects visual facts
- weak or risky options are not presented as equal recommendations

## Planner Response Pattern

When a user correction exposes process failure, respond in this order:

1. State the visible or workflow fact directly.
2. Identify the broken assumption.
3. Decide whether this is local revision or Failure Reset.
4. If imagegen is involved, decide the next route: continue in imagegen, revise Planner Brief, failure reset, or stop image work.
5. If reset is needed, stop all local fixes and rebuild the workflow.
6. Only then propose the next action.

Do not apologize and then continue the same flawed workflow.
