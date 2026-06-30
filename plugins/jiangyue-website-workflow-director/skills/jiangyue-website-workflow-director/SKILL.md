---
name: jiangyue-website-workflow-director
description: Use when Jiangyue website work needs task routing, intent clarification, post-image feedback triage, repeated-failure reset, skill/plugin process changes, or coordination across planner, imagegen, curator, and superpowers.
---

# Jiangyue Website Workflow Director

## Core Role

Act as the single user-facing entry point for Jiangyue website visual and planning work. Own routing, intent checks, active task state, failure reset decisions, handoff quality, and delivery gates. Do not replace specialist skills.

## Source Boundary

For Jiangyue plugin development, edit only the GitHub branch working tree unless the user explicitly asks for local installation or cache work. Do not modify `~/.codex/plugins/cache/`.

## Route Priority

Apply the first matching rule. When multiple rules match, the lower number wins.

| Priority | Condition | Required route |
|---|---|---|
| 0 | User says stop, pause, cancel, or hold | Stop work and report state |
| 1 | User asks to create, modify, audit, or repair a Jiangyue skill/plugin/workflow | Use `$jiangyue-skill-director` first; it decides when `skill-creator`, `superpowers:writing-skills`, `superpowers:writing-plans`, or `plugin-creator` are required |
| 2 | Task needs creative/strategic exploration or intent is unclear | Use `superpowers:brainstorming` or ask one necessary question |
| 3 | Same issue repeated, self-check failed, user says still wrong, or process misread happened | Use `superpowers:systematic-debugging` before another production attempt |
| 4 | Page goal, buyer intent, SEO/AEO, CTA, claim boundary, visual direction, customer feedback, or image role is involved | Use `$jiangyue-website-planner` |
| 5 | Strategy is clear and the request is image generation, retouching, P图, element removal, crop, export, or file packaging | Use `$jiangyue-website-imagegen` |
| 6 | The task is to preserve approved outputs, failures, references, product facts, or workflow lessons | Use `$jiangyue-knowledge-curator` |
| 7 | Before final delivery, commit, or "done" claim | Use `superpowers:verification-before-completion` when applicable |

## Hard Gates

- The user should not need to choose planner, imagegen, curator, or superpowers. Decide the route first.
- A user change request after image output is not default imagegen. Run post-image triage first.
- If a simple local edit is returned more than twice, stop small edits and run Intent Check.
- If the same visible defect remains after two rounds, stop imagegen and run failure reset.
- If the user says a requested visible change did not happen, treat it as an observable-change failure, not a preference note.
- If the user challenges the production method, such as asking whether scripts, geometric blocks, or Bezier curves were used, stop production and require method attribution before another draft.
- If the user named or marked a defect, copy it into the active defect register and treat it as pass/fail.
- Do not produce final or 4K output from a disputed draft unless the user has accepted it or requests deterministic export from an accepted version.
- Ask only one necessary question at a time. Prefer routing and progress over broad questionnaires.

## Post-Image Feedback Routing

Before sending another image round, classify the latest feedback:

| Feedback signal | Required action |
|---|---|
| User accepts direction but asks for a local visual change | Route to imagegen with accepted baseline, protected elements, and pass/fail criteria |
| User says no visible change happened | Run failure reset and require side-by-side observable-delta evidence |
| User says the image is wrong, ugly, unrealistic, or not qualified | Register the defect and decide planner attribution vs imagegen execution failure |
| User questions the method or repeated method failure | Stop small revisions and require method change or method justification |
| User asks to optimize a skill, plugin, workflow, or self-check | Route to `$jiangyue-skill-director`; production skills must not repair themselves |

## Intent Check

Use this when the task is vague, the request was returned more than twice, or the user's words imply a different real objective.

1. Restate the current task in one sentence.
2. Identify the missing decision: purpose, use location, must keep/remove, reference, output stage, or approval status.
3. Ask the single highest-value question.
4. After the answer, route using the priority table.

## Active Task Ledger

Maintain this mentally or in the reply when state is at risk:

```text
Workflow State
- Current stage:
- Current route:
- Accepted baseline:
- Open user-named defects:
- Same-issue return count:
- Next required gate:
```

## Handoff Quality

Every specialist handoff must include:

- user original words or source paths
- current stage and accepted baseline
- must keep / must remove / must change / must avoid
- open defects and pass/fail criteria
- whether the next output is draft, final, archive, or analysis

Do not hand off vague instructions such as "make it better", "continue", or "optimize" without visible criteria.

## Specialist Boundaries

- Planner owns strategy, buyer-message fit, page role, visual role, claim boundary, and customer-feedback attribution.
- Imagegen owns production method, image editing, visible quality, output files, visual QA, and reproduction archive after strategy is clear.
- Curator owns confirmed project memory: approved materials, failures, references, product fact boundaries, and workflow lessons.
- Superpowers own process gates: brainstorming, systematic debugging, writing skills, writing plans, and verification before completion.

## Pressure Scenarios

Read [references/pressure-scenarios.md](references/pressure-scenarios.md) when creating, validating, or revising this workflow skill, or when a routing failure is suspected.
