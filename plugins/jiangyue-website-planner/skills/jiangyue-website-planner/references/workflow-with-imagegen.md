# Workflow With Superpowers And Imagegen

Use this reference when a Jiangyue website task crosses page strategy, visual production, user review, and final verification.

## End-To-End Flow

```text
Fuzzy page or image request
-> superpowers:brainstorming when the goal, buyer, message, or success criteria are unclear
-> jiangyue-website-planner defines page strategy, Jiangyue design judgment, and Planner Brief
-> user confirms the strategy contract
-> jiangyue-website-imagegen creates the Production Brief from the Planner Brief's Asset Production Section and then produces the visual asset
-> user reviews the draft
-> planner classifies feedback when strategy, hierarchy, credibility, or message ownership is questioned
-> planner records user-named defects and reference attribution when feedback names visible problems or missed references
-> imagegen continues only when the problem is visual execution
-> superpowers:systematic-debugging enters if repeated failures have unclear root cause
-> superpowers:verification-before-completion checks evidence before completion is claimed
```

## Routing Table

| Situation | Use |
|---|---|
| Page goal, buyer, SEO/AEO intent, H1, CTA, section order, attention hierarchy, Jiangyue design judgment, or image role is unclear | `superpowers:brainstorming` then `$jiangyue-website-planner` |
| Planner Brief is approved and the task is visual production, image editing, export, or asset packaging | `$jiangyue-website-imagegen` |
| User feedback challenges brand direction, credibility, visual hierarchy, layout integration, message ownership, or claim safety | `$jiangyue-website-planner` |
| User asks for sharper crop, cleaner text, format conversion, local cleanup, or visual execution changes without strategy change | `$jiangyue-website-imagegen` |
| User names/marks a visible defect, says self-check failed, or disputes reference use | `$jiangyue-website-planner` classifies and registers the defect, then routes to `$jiangyue-website-imagegen` hard gates or revised Planner Brief |
| The same visual or strategy problem repeats and the cause is unclear | `superpowers:systematic-debugging` |
| The plan, handoff, image, archive, or implementation is about to be called complete | `superpowers:verification-before-completion` |

## Planner To Imagegen Handoff

Planner hands off one Planner Brief. The brief is a strategy, design-judgment, page/content, and composition contract with an internal Asset Production Section. Do not create a separate peer asset script for normal imagegen work.

Planner must define:

- page and page goal
- target buyer and search/AEO intent when relevant
- core page message
- Jiangyue Context Packet: page-role intensity, business job, trusted subject, formal sources, approved materials when relevant, forbidden directions, and claim boundary
- Jiangyue Design Judgment: design risk, quality standard, design trade-off, brand fit, B2-3 role, life-sense boundary, and anti-cheapness filter
- first-screen attention owner
- image role
- what the image must support
- what HTML/page copy must carry
- required subject cues
- visual composition contract: image type, visible layers, subject/support/background roles, placement, approximate proportion, shape/form language, direction, hierarchy, negative space, buyer-readable meaning, and forbidden forms
- forbidden claims and product facts
- recommended and forbidden directions
- CTA/title/logo relationship
- Asset Production Section: subject carriers, scene carriers, composition rules, color/material rules, negative-space/text-support rules, must include, must avoid, prompt-ready direction, QA checks, and rejection triggers
- output ratio or usage position
- visible pass/fail criteria
- user-named defects and whether each is blocking, when this is a rework
- reference attribution: used before generation, conversation-only, or next-version reference

Imagegen then defines:

- execution intent
- must keep, remove, materially change, and avoid lists
- production-level subject carriers and relationship model within the Planner Brief's Visual Composition Contract and Asset Production Section
- physical logic and method selection
- production brief
- image output, review, and archive
- candidate review, defect closure, reference translation, and visual verification records when hard gates are triggered

## Feedback Loop

Planner should not send another vague instruction such as "make it more premium" or "try again." A next-round optimization brief must say:

- what visible problem must change
- what must remain unchanged
- whether page goal, H1, CTA, image role, or claim boundary changes
- what composition element, placement, proportion, shape, hierarchy, or negative-space relationship must change when the problem is design-level
- what old direction imagegen must not repeat
- what the next draft must show to pass

If the page strategy remains correct and the issue is execution quality, return the draft to imagegen. If the image can only work by changing page message, attention hierarchy, CTA, H1, or claim boundary, revise the Planner Brief first.

If the design judgment is correct but imagegen did not receive concrete visible carriers, revise the Asset Production Section inside the Planner Brief. If the brief has concrete carriers and the result is still visibly weak, return to imagegen with execution defects.

## Hard Handoff Rules

Before planner sends a rework back to imagegen after user feedback, decide and state one route:

- `continue in imagegen`
- `revise Planner Brief`
- `failure reset`
- `stop image work`

Do not send another imagegen request while the route is ambiguous.

For rework after a user-named defect, planner must include:

- exact user wording or marked defect
- planner classification: strategy, hierarchy, image role, claim, layout integration, brand direction, or execution
- failed layer when applicable: design judgment, page/content plan, Visual Composition Contract, Asset Production Section, or imagegen execution
- whether the defect blocks delivery
- what evidence closes the defect
- references that must be used or must not be implied

If the same blocking defect remains after one imagegen revision, planner must require imagegen failure reset or revise the Planner Brief. It may not send "try again" or "make it better".

If final or 4K output is requested after a disputed draft, planner must block final export until a draft is accepted or the request is only deterministic export from an accepted draft.
