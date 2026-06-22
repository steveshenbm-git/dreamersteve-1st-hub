# Workflow With Superpowers And Imagegen

Use this reference when a Jiangyue website task crosses page strategy, visual production, user review, and final verification.

## End-To-End Flow

```text
Fuzzy page or image request
-> superpowers:brainstorming when the goal, buyer, message, or success criteria are unclear
-> jiangyue-website-planner defines page strategy and Planner Brief
-> user confirms the strategy contract
-> jiangyue-website-imagegen creates the Production Brief and visual asset
-> user reviews the draft
-> planner classifies feedback when strategy, hierarchy, credibility, or message ownership is questioned
-> imagegen continues only when the problem is visual execution
-> superpowers:systematic-debugging enters if repeated failures have unclear root cause
-> superpowers:verification-before-completion checks evidence before completion is claimed
```

## Routing Table

| Situation | Use |
|---|---|
| Page goal, buyer, SEO/AEO intent, H1, CTA, section order, attention hierarchy, or image role is unclear | `superpowers:brainstorming` then `$jiangyue-website-planner` |
| Planner Brief is approved and the task is visual production, image editing, export, or asset packaging | `$jiangyue-website-imagegen` |
| User feedback challenges brand direction, credibility, visual hierarchy, layout integration, message ownership, or claim safety | `$jiangyue-website-planner` |
| User asks for sharper crop, cleaner text, format conversion, local cleanup, or visual execution changes without strategy change | `$jiangyue-website-imagegen` |
| The same visual or strategy problem repeats and the cause is unclear | `superpowers:systematic-debugging` |
| The plan, handoff, image, archive, or implementation is about to be called complete | `superpowers:verification-before-completion` |

## Planner To Imagegen Handoff

Planner hands off a strategy contract, not a production recipe.

Planner must define:

- page and page goal
- target buyer and search/AEO intent when relevant
- core page message
- first-screen attention owner
- image role
- what the image must support
- what HTML/page copy must carry
- required subject cues
- forbidden claims and product facts
- recommended and forbidden directions
- CTA/title/logo relationship
- output ratio or usage position
- visible pass/fail criteria

Imagegen then defines:

- execution intent
- must keep, remove, materially change, and avoid lists
- subject carriers and relationship model
- physical logic and method selection
- production brief
- image output, review, and archive

## Feedback Loop

Planner should not send another vague instruction such as "make it more premium" or "try again." A next-round optimization brief must say:

- what visible problem must change
- what must remain unchanged
- whether page goal, H1, CTA, image role, or claim boundary changes
- what old direction imagegen must not repeat
- what the next draft must show to pass

If the page strategy remains correct and the issue is execution quality, return the draft to imagegen. If the image can only work by changing page message, attention hierarchy, CTA, H1, or claim boundary, revise the Planner Brief first.
