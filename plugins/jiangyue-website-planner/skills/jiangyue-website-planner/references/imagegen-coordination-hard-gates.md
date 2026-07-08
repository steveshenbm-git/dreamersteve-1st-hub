# Imagegen Coordination Hard Gates

Use this file when planner reviews an imagegen result, creates a rework order, or routes a failed visual task back to imagegen. Planner owns strategy and routing; imagegen owns production. These gates prevent vague handoffs and repeated failed loops.

## Trigger

Run these gates before another imagegen round when any of these occur:

- the user names or marks a visible defect
- the user says self-check failed, the reference was missed, the attachment was ignored, or the draft is still not qualified
- the same visual concern remains after one revision
- the issue may involve page goal, image role, attention hierarchy, claim boundary, brand credibility, layout integration, or message ownership
- planner needs to decide whether imagegen should continue or stop

## Planner Defect Register

Planner must copy user-stated visual defects into the rework brief. Do not soften them into broad taste words.

```text
Planner Defect Register
- User wording:
- Visible defect:
- Planner classification: strategy / hierarchy / role / claim / execution
- Blocking for delivery: yes/no
- Required evidence to close:
```

If a defect is blocking, imagegen must receive it as a hard pass/fail item, not as optional feedback.

## Routing Decision

Before handing off, decide one route:

| Route | Use when | Planner output |
|---|---|---|
| Continue in imagegen | Page strategy and image role are still correct; defect is execution, composition, realism, method, crop, or artifact quality | Imagegen rework brief with defect register and pass/fail checks |
| Planner revise brief | Page goal, attention hierarchy, image role, message ownership, brand direction, layout integration, or claim boundary is unclear/wrong | Revised Planner Brief before imagegen continues |
| Failure reset | Same defect repeated, process complaint, missed reference, or root cause unclear | Failure Reset record before any new imagegen request |
| Stop image work | User pauses, approval is missing, or next action is knowledge curation/review only | No imagegen handoff |

Do not send imagegen another prompt if the route is not decided.

## Handoff Must Include

Every rework handoff after user feedback must include:

- current version or source
- user-named defects copied verbatim
- planner attribution for each defect
- whether page goal, H1, CTA, image role, or claim boundary changes
- what must remain unchanged
- what must visibly change
- forbidden old direction
- reference attribution and whether each reference should be used for the next version
- pass/fail criteria for full-size and thumbnail review
- whether imagegen must run its failure reset hard gates

For a new image direction or strategy-level rework, every handoff must also include a visual composition contract:

- image type
- visible layers and their roles
- element placement and approximate proportion
- shape / semi-concrete form language
- direction or movement
- hierarchy and negative-space area
- buyer-readable meaning
- forbidden visible forms

If these fields are missing, planner must revise the brief before imagegen continues.

## Visual Intention Decomposition

Use this when feedback contains abstract visual goals such as overall unity, connection, spatial depth, realism, calm control, warmth, premium feel, or brand atmosphere. Planner must translate the intention into visible evidence without prescribing imagegen's exact production method.

```text
Visual Intention Decomposition
- User wording:
- Strategy meaning:
- Subject relationship:
- Environment carrier:
- Spatial evidence:
- Material / texture evidence:
- Light / color boundary:
- Approved material that must not change:
- Visible pass/fail criteria:
```

## Visual Composition Contract

Use this before imagegen when the request asks how an image should be designed, shown, arranged, made semi-concrete, or made readable to buyers.

```text
Visual Composition Contract
- Image type:
- Background layer:
- Primary visual layer:
- Support layer:
- Negative-space / text-support area:
- Placement and approximate proportion:
- Shape / semi-concrete form:
- Direction or movement:
- Attention hierarchy:
- Buyer-readable meaning:
- Forbidden visible forms:
- Visible pass/fail criteria:
```

Passing standard: a person should be able to roughly sketch the composition from this contract alone. If the contract only contains concept words such as "industrial life", "AI analysis", "premium", "future", "connection", or "energy" without visible placement, shape, hierarchy, and forbidden forms, it is not ready for imagegen.

Examples:

- "整体性 / 关联感": require shared environment, contact logic, consistent light, material transition, overlap, reflection, shadow, or depth relationship. Do not default to line connectors.
- "空间感": require foreground/background order, contact surface, floating/attached/embedded logic, shadow, reflection, refraction, or scale consistency.
- "真实性": require photographic or source-based texture behavior, natural non-geometric forms, plausible light, and detail scale that matches the subject.
- "颜色不能大改": define protected hue, saturation, luminance, and affected area for approved materials.

## Reference Attribution

Planner must distinguish:

- reference used to form the original Planner Brief
- reference used by imagegen to generate the current version
- reference surfaced in conversation but not used
- reference added or confirmed later for the next version

Do not imply that the current image was generated from a reference unless the workflow actually used it.

## Failure Reset

Trigger Failure Reset when:

- the same blocking defect remains after one imagegen revision
- the user challenges the process or self-check
- a visual problem repeats and planner cannot clearly assign strategy vs execution cause
- references, baseline assets, or check objects were wrong or incomplete

Failure Reset must follow this order before any new imagegen request:

1. **Analyze the problem / 分析问题:** restate the real objective, image role, visible blocking defects, baseline, reference set, and evidence checked.
2. **Find the root cause / 找到问题:** decide whether the failed layer is page strategy, image role, Visual Composition Contract, reference attribution, imagegen method, verification, or routing. State the wrong assumption.
3. **Propose the method / 提出方法:** decide whether to revise the Planner Brief, continue in imagegen with hard gates, return to Workflow Director, or stop image work. Name methods or routes that are prohibited.
4. **Output the plan / 输出方案:** issue a revised planner brief, imagegen rework order, or stop instruction with pass/fail criteria and next allowed action.

Failure Reset must state:

```text
Planner Failure Reset
- Step 1 - Problem analysis:
- Real objective:
- Current image role:
- Blocking defects:
- Baseline / evidence checked:
- Step 2 - Root cause:
- Failed layer:
- Wrong assumption:
- Strategy assumptions to keep:
- Strategy assumptions to revisit:
- Step 3 - Proposed method:
- Correct next route:
- Rejected shortcut(s):
- Step 4 - Output plan:
- Required visual evidence:
- Correct reference set:
- Pass/fail criteria:
- Explicitly prohibited next actions:
```

After reset, do not request a final/4K image until a draft has passed the reset criteria.

## Pressure Scenarios For Planner Validation

1. **User marks a curve defect in red:** planner must register the exact defect, classify it, and send imagegen a hard pass/fail item.
2. **Reference attribution dispute:** planner must distinguish assistant-sourced conversation reference from user-added reference and state whether it was used in the current image.
3. **Imagegen self-check failed:** planner must stop vague "continue" routing and decide imagegen hard-gate reset vs revised Planner Brief.
4. **Repeated bad visual direction:** planner must decide whether page/image role changed or production method failed; it may not keep sending "make it better".
5. **4K requested after disputed draft:** planner must block final export unless a draft is accepted or the request is deterministic export from an accepted draft.
6. **Semi-concrete AI/industrial field:** user asks for a silver-gray background with teal-green and blue B2-3 semi-concrete field intersection, not too hard-core industrial and not too abstract. Planner must output a visual composition contract with layers, positions, proportions, shapes, direction, buyer-readable meaning, forbidden forms, and pass/fail criteria before imagegen. It may not send only "industrial operation field + AI analysis field" as a vague concept.
