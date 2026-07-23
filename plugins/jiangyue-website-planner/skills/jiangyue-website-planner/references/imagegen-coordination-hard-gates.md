# Imagegen Coordination Hard Gates

Use this file when planner reviews an imagegen result, creates a rework order, or routes a failed visual task back to imagegen. Planner owns strategy and routing; imagegen owns production. These gates prevent vague handoffs and repeated failed loops.

## Trigger

Run these gates before another imagegen round when any of these occur:

- the user names or marks a visible defect
- the user says self-check failed, the reference was missed, the attachment was ignored, or the draft is still not qualified
- the same visual concern remains after one revision
- the issue may involve page goal, image role, attention hierarchy, claim boundary, brand credibility, layout integration, or message ownership
- planner needs to decide whether imagegen should continue or stop
- imagegen output status, candidate delivery value, or user acceptance layer is unclear
- a rejected candidate is being treated as the next baseline
- repeated generation attempts are happening without a changed hypothesis, method, visual model, source basis, or edit scope

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
| Analysis only | Candidate failed hard gates but contains useful evidence, anti-reference value, or discovery insight | Rejected-result analysis; no imagegen handoff unless brief/method is revised |
| Stop image work | User pauses, approval is missing, or next action is knowledge curation/review only | No imagegen handoff |

Do not send imagegen another prompt if the route is not decided.

## Handoff Must Include

Every rework handoff after user feedback must include:

- current version or source
- user-named defects copied verbatim
- planner attribution for each defect
- failed layer when applicable: design judgment, page/content plan, image role, Visual Composition Contract, Asset Production Section, or imagegen execution
- whether page goal, H1, CTA, image role, or claim boundary changes
- brief reasoning: what part of the user's requested direction is accepted, constrained, or rejected, and why
- what must remain unchanged
- what must visibly change
- forbidden old direction
- reference attribution and whether each reference should be used for the next version
- pass/fail criteria for full-size and thumbnail review
- whether imagegen must run its failure reset hard gates
- current output status: rejected internally, analysis only, discovery candidate, candidate for review, accepted draft, or final export
- brief anchor: original brief, revised brief, accepted draft, or anti-reference
- user acceptance layer: intent, brief, direction, specific draft, final export, or unknown
- production success strategy and attempt stop rule when another generation attempt is requested

For a new image direction or strategy-level rework, every handoff must also include a visual composition contract:

- Jiangyue design judgment: design risk, quality standard, trusted subject, brand temperament, design trade-off, and anti-cheapness filter
- image type
- visual thesis / core image proposition
- visual organization intent: attention owner, negative-space role, first/second read, and text support
- visual relationship model: primary role, secondary role, background carrier, relationship type, relationship strength, and forbidden relationship
- readable form language: abstraction level, allowed form families, forbidden form families, buyer-readable meaning, and likely misreads
- visible layers and their roles
- element placement and approximate proportion
- direction or movement
- hierarchy and negative-space area
- buyer-readable meaning
- forbidden visible forms
- Asset Production Section: subject carriers, scene carriers, composition rules, color/material rules, negative-space/text-support rules, must include, must avoid, prompt-ready direction, QA checks, and rejection triggers
- brief feasibility analysis: whether imagegen may proceed, production controllability, main failure risks, protected content, and preconditions

If these fields are missing, planner must revise the brief before imagegen continues.

The Planner Brief is the main handoff. Do not create a separate peer asset script unless Workflow Director explicitly requests a multi-asset production package.

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
- Visual thesis:
- Visual organization intent:
  - Attention owner:
  - Negative-space / text-support role:
  - First read:
  - Second read:
  - What must not steal attention:
- Visual relationship model:
  - Primary visual role:
  - Secondary visual role:
  - Background carrier role:
  - Relationship type:
  - Relationship strength:
  - Forbidden relationship:
- Readable form language:
  - Recommended concreteness: abstract / semi-concrete / concrete
  - Allowed form families:
  - Forbidden form families:
  - Buyer-readable meaning:
  - Likely misread:
- Background layer:
- Primary visual layer:
- Support layer:
- Negative-space / text-support area:
- Placement and approximate proportion:
- Direction or movement:
- Attention hierarchy:
- Buyer-readable meaning:
- Forbidden visible forms:
- Visible pass/fail criteria:
```

Passing standard: a person should be able to roughly sketch the composition and explain the intended buyer reading from this contract alone. If the contract only contains concept words such as "industrial life", "AI analysis", "premium", "future", "connection", or "energy" without visible organization, relationship model, readable form language, hierarchy, and forbidden forms, it is not ready for imagegen.

Design-led passing standard: words such as "premium", "professional", "restrained", "high-end", "calm", or "Jiangyue style" are insufficient unless planner states which design fundamental makes them true and how imagegen can make that visible: proportion, hierarchy, rhythm, restraint, information density, material credibility, space credibility, controlled B2-3 cue, trusted subject, or buyer-readable meaning.

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
2. **Find the root cause / 找到问题:** decide whether the failed layer is macro planning, core intent, intent lock, strategic layer ownership, page strategy, image role, Visual Composition Contract, reference attribution, imagegen method, verification, or routing. State the wrong assumption.
3. **Propose the method / 提出方法:** decide whether to revise the Planner Brief, continue in imagegen with hard gates, return to Workflow Director, or stop image work. Name methods or routes that are prohibited.
4. **Output the plan / 输出方案:** issue a revised planner brief, imagegen rework order, or stop instruction with pass/fail criteria and next allowed action.

The root-cause step may climb above planner. If the real failure is unclear macro planning, unresolved brand/narrative direction, or an unlocked core intent, planner must return to Workflow Director for Strategic Layer Lock instead of producing a narrower image brief.

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
- Root-cause climb needed: yes/no
- If yes, target owner: Workflow Director / planner / imagegen
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

## Output Status And Brief Anchor

Planner must not let imagegen output rewrite the brief.

```text
Planner Output Status Check
- Original intent:
- Active Planner Brief:
- Imagegen result status:
- Result vs brief:
- Result vs intent:
- Accepted direction:
- Rejected candidate / anti-reference:
- Next baseline:
- User acceptance layer:
- Next route:
```

Hard rules:

- A rejected candidate is not an accepted baseline.
- A discovery candidate requires planner/user acceptance before it becomes a revised brief.
- A candidate that passes self-check but lacks delivery value must remain internal or analysis-only.
- "Direction accepted" does not equal "specific draft accepted" or "final export accepted."

## Attempt Stop Rule

Before planner approves another generation round after failure, require a distinct production hypothesis. At least one must change: visual model, composition structure, subject carrier, crop/scale hierarchy, source/reference basis, production method, or mask/edit scope.

Changing only prompt adjectives, color, glow, blur, opacity, line weight, shadow, or export size is not enough for structural failure.

## Pressure Scenarios For Planner Validation

1. **User marks a curve defect in red:** planner must register the exact defect, classify it, and send imagegen a hard pass/fail item.
2. **Reference attribution dispute:** planner must distinguish assistant-sourced conversation reference from user-added reference and state whether it was used in the current image.
3. **Imagegen self-check failed:** planner must stop vague "continue" routing and decide imagegen hard-gate reset vs revised Planner Brief.
4. **Repeated bad visual direction:** planner must decide whether page/image role changed or production method failed; it may not keep sending "make it better".
5. **4K requested after disputed draft:** planner must block final export unless a draft is accepted or the request is deterministic export from an accepted draft.
6. **Semi-concrete AI/industrial field:** user asks for a silver-gray background with teal-green and blue B2-3 semi-concrete field intersection, not too hard-core industrial and not too abstract. Planner must output a visual composition contract with visual thesis, visual organization intent, visual relationship model, readable form language, layers, proportions, direction, buyer-readable meaning, forbidden forms, feasibility analysis, and pass/fail criteria before imagegen. It may not send only "industrial operation field + AI analysis field" as a vague concept.
7. **Core intent not locked:** user says the failure is not only image quality, but that the macro relationship or core intent was unclear from the start. Planner must name the failed layer as macro planning / core intent / intent lock and return to Workflow Director for Strategic Layer Lock. It may not produce a narrower imagegen rework order to hide the unresolved strategic problem.
8. **User challenge should not cause automatic agreement:** user says one part of the planner brief "feels wrong" without specifying a replacement. Planner must classify the challenge, preserve the parts of the existing reasoning that still stand, constrain or replace only the failed part, and explain why. It may not answer with unqualified agreement or rewrite the brief around the user's wording alone.
9. **Homepage hero design-led brief:** user asks for a Jiangyue homepage hero direction. Planner must produce a Jiangyue Context Packet and Design Judgment before the image role or composition contract. It must identify trusted subject, page-role intensity, B2-3 role, life-sense boundary, design trade-off, claim boundary, and anti-cheapness filter. It may not only say "left text, right industrial image, premium and restrained."
10. **Not premium enough:** user says the planner output or draft is still not high-end. Planner must diagnose the failed design fundamental: proportion, hierarchy, rhythm, restraint, information density, material credibility, space credibility, buyer readability, or brand temperament. It may not answer with only "make it more premium", "more clean", or "more refined".
11. **Asset script confusion:** user asks whether Page Brief and Asset Production Script are separate. Planner must state that the Planner Brief is the main imagegen handoff and the Asset Production Section is an internal section, unless Workflow Director explicitly requests a multi-asset production package.
12. **Correct judgment, weak carrier:** user accepts the Jiangyue design judgment but imagegen output is generic. Planner must revise the Asset Production Section with concrete visible carriers and QA checks before another imagegen round. It may not rewrite the whole strategy or send vague execution feedback.
13. **Rejected output becomes baseline:** imagegen returns a drifted candidate and the next planner rework starts from it. Planner must mark it as anti-reference unless the user explicitly accepted its direction, then return to original or revised brief.
14. **Least-bad batch:** imagegen produces several weak options. Planner must reject the batch or classify analysis-only; it may not select the least-bad option as a candidate.
15. **Endless generation:** two attempts fail the same brief goal with the same method. Planner must block further same-method attempts and require attempt-stop analysis or a route change.
16. **Acceptance layer:** user says "this direction can work" and asks for a small revision. Planner must record direction acceptance only; it may not approve final export or approved archive from that statement.
