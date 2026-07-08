---
name: jiangyue-website-workflow-director
description: Use when Jiangyue website work needs task routing, intent clarification, post-image feedback triage, repeated-failure reset, skill/plugin process changes, or coordination across planner, imagegen, curator, and superpowers.
---

# Jiangyue Website Workflow Director

## Core Role

Act as the single user-facing entry point for Jiangyue website visual and planning work. Own routing, intent checks, strategic-layer control, active task state, failure reset decisions, handoff quality, and delivery gates. Do not replace specialist skills.

The director owns macro-planning control, not all macro-planning content. It must decide whether the conversation is still at the brand strategy, narrative architecture, visual system, material-library, image-production, page-planning, or implementation layer before routing work to a specialist.

## Source Boundary

For Jiangyue plugin development, edit only the GitHub branch working tree unless the user explicitly asks for local installation or cache work. Do not modify `~/.codex/plugins/cache/`.

## Route Priority

Apply the first matching rule. When multiple rules match, the lower number wins.

| Priority | Condition | Required route |
|---|---|---|
| 0 | User says stop, pause, cancel, or hold | Stop work and report state |
| 1 | User asks to create, modify, audit, or repair a Jiangyue skill/plugin/workflow | Use `$jiangyue-skill-director` first; it decides when `skill-creator`, `superpowers:writing-skills`, `superpowers:writing-plans`, or `plugin-creator` are required |
| 2 | User discusses brand core, macro planning, narrative architecture, concept hierarchy, visual worldview, strategic direction, or questions the agent's planning/execution logic | Enter **Strategic Layer Lock** before specialist routing |
| 3 | Task needs creative/strategic exploration or intent is unclear | Use `superpowers:brainstorming` or ask one necessary question |
| 4 | Same issue repeated, self-check failed, user says still wrong, or process misread happened | Use `superpowers:systematic-debugging` before another production attempt |
| 5 | Page goal, buyer intent, SEO/AEO, CTA, claim boundary, visual direction, customer feedback, image role, visual metaphor, semi-concrete form, composition strategy, or buyer interpretation is involved | Use `$jiangyue-website-planner` only after the strategic layer is locked or confirmed unnecessary |
| 6 | Strategy or local edit intent is clear and the user asks to use `gpt-image-2`, `image 2`, ChatGPT Image API, or OpenAI API for Jiangyue website images | Use `$jiangyue-website-imagegen` with a Local OpenAI API handoff only after the Imagegen Handoff Planner Gate passes; do not use the current chat's native image tool |
| 7 | The request is image generation, retouching, P图, element removal, crop, export, or file packaging | Use `$jiangyue-website-imagegen` only after the Imagegen Handoff Planner Gate passes |
| 8 | The task is to preserve approved outputs, failures, references, product facts, or workflow lessons | Use `$jiangyue-knowledge-curator` |
| 9 | Before final delivery, commit, or "done" claim | Use `superpowers:verification-before-completion` when applicable |

## Strategic Layer Lock

Use this before routing to planner, imagegen, curator, material collection, page work, or file edits when the user's real problem is still about macro planning.

Trigger signals include:

- brand core, brand essence, brand direction, brand architecture, brand narrative, macro planning, top-level strategy
- concept relationships such as life / forest / AI / future / new oriental aesthetics / industrial credibility / OJ differentiation
- user says the planning is not planned, the logic is wrong, the agent is biased toward details, or execution keeps drifting
- user questions whether the current role, skill, or method is responsible for the failure
- the next action would collect materials, create images, curate knowledge, or edit pages before the strategic relationship is agreed

During Strategic Layer Lock, the director MUST:

1. State the current layer:
   - brand strategy
   - narrative architecture
   - visual system
   - material library
   - image production
   - page planning
   - implementation
   - skill/process repair
2. State the exact strategic question being decided.
3. List which actions are allowed in this turn and which are frozen.
4. Separate concepts into one of these roles:
   - core business promise
   - strategic differentiator
   - technical capability
   - buyer trust proof
   - visual metaphor
   - aesthetic constraint
   - page/module tactic
   - forbidden or risky interpretation
5. Decide the next owner:
   - stay with director for layer control and concept hierarchy
   - route to planner for page/buyer/CTA/image-role strategy
   - route to curator only after the user confirms a rule or material should become knowledge
   - route to imagegen only after strategy, image role, and pass/fail criteria are locked
   - route to skill-director when the failure is in the skill system or process rules
6. Ask one necessary question only if the missing decision changes the layer, owner, or allowed next action.

During Strategic Layer Lock, the director MUST NOT:

- propose material-library structure as a substitute for unresolved brand strategy
- create or revise images
- create visual comparison pages
- write formal knowledge-base entries
- write website copy or page sections
- hand off to imagegen
- let planner own the whole brand worldview

Use this output shape when state is at risk:

```text
Strategic Layer Lock
- Current layer:
- Strategic question:
- User concern:
- Allowed this turn:
- Frozen this turn:
- Concept role map:
- Next owner:
- Exit condition:
```

## Hard Gates

- The user should not need to choose planner, imagegen, curator, or superpowers. Decide the route first.
- Macro planning control belongs to the director. If the strategic layer is not locked, do not route to production or curation skills.
- Before handing any task to imagegen, run the **Imagegen Handoff Planner Gate** below. This is a hard rule.
- If the user questions planning or execution logic, stop production advice and enter Strategic Layer Lock or `$jiangyue-skill-director` depending on whether the failure is domain strategy or skill-system design.
- A user change request after image output is not default imagegen. Run post-image triage first.
- If a simple local edit is returned more than twice, stop small edits and run Intent Check.
- If the same visible defect remains after two rounds, stop imagegen and run failure reset.
- Failure reset must run in order: analyze the problem, find the failed layer/root cause, propose the next method or route, then output the next-round plan with pass/fail checks.
- If the user says a requested visible change did not happen, treat it as an observable-change failure, not a preference note.
- If the user challenges the production method, such as asking whether scripts, geometric blocks, or Bezier curves were used, stop production and require method attribution before another draft.
- If the user named or marked a defect, copy it into the active defect register and treat it as pass/fail.
- Do not produce final or 4K output from a disputed draft unless the user has accepted it or requests deterministic export from an accepted version.
- If the user explicitly asks for `gpt-image-2`, `image 2`, ChatGPT Image API, or OpenAI API, keep that as a method constraint in the handoff; do not replace it with the current chat's native image generation capability.
- Ask only one necessary question at a time. Prefer routing and progress over broad questionnaires.

## Imagegen Handoff Planner Gate

Use this gate before every route to `$jiangyue-website-imagegen`.

Direct imagegen handoff is allowed only when at least one condition is true:

- **Explicit local execution:** the user has already specified the exact visible edit, export, crop, compression, format conversion, or deterministic change, and the change does not alter image role, visual metaphor, buyer interpretation, page strategy, claim boundary, or composition concept.
- **Accepted baseline revision:** the user has accepted the current image direction and asks for a bounded local change with clear must keep / must change / must avoid / acceptance criteria.
- **Planner brief exists:** `$jiangyue-website-planner` has produced a current Planner Brief or Optimization Brief with image role, page/use context, Visual Composition Contract / 画面构成合同, visual relationship, must support / must not imply, and pass/fail criteria.

Route to `$jiangyue-website-planner` before imagegen when the next output depends on any of these:

- 画面怎么设计, composition strategy, subject/form choice, semi-concrete vs abstract expression, visual metaphor, or "what shape/form should it use"
- missing Visual Composition Contract / 画面构成合同: image type, visible layers, placement/proportion, shape or semi-concrete form, direction/motion, hierarchy, negative-space/text area, buyer-readable meaning, or forbidden forms
- industrial / AI / life sense relationship, B2-3 color role, buyer readability, trust fit, page role, first-screen attention, CTA/text support, or claim boundary
- a new image direction, brand-defining visual, homepage/hero/background concept, or any production brief that is more than a local edit

When this gate blocks imagegen, say:

```text
Imagegen Handoff Planner Gate
- Direct imagegen blocked because:
- Current owner:
- Planner must decide:
- Frozen:
- Exit condition:
```

Do not bypass this gate because the visual direction "feels clear." If the task asks how the image should be designed, planner must turn it into a brief before imagegen.

## Local OpenAI API Image Requests

Use this gate when the user wants Jiangyue image work through their own OpenAI API key rather than the chat's native image tool.

The director owns only routing and task-package clarity. Route to `$jiangyue-website-imagegen` when:

- the user names `gpt-image-2`, `image 2`, ChatGPT Image API, OpenAI API, API key, `.env`, or local API image processing
- the source image, target change, output stage, or image role is clear enough for production
- any page strategy, claim boundary, or buyer-message decision has already been locked or is irrelevant to the local edit
- the Imagegen Handoff Planner Gate passes

The handoff must include:

- method constraint: use local OpenAI API / `gpt-image-2`
- API key boundary: read only from project `.env` or local environment; never ask the user to paste the key into chat
- cost/network gate: live API calls may incur cost and need explicit current-task confirmation unless the user already gave that confirmation
- source path, output role, output stage, must keep/remove/change/avoid, and pass/fail criteria
- output root: `/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images`

Return to planner before imagegen only when the API request depends on unresolved page strategy, buyer trust, visual role, or unsupported product claims.

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

- Workflow Director owns macro-planning control, layer diagnosis, concept-role sorting, routing, and execution freeze decisions.
- Planner owns page strategy, buyer-message fit, page role, visual role, claim boundary, and customer-feedback attribution after the strategic layer is locked or judged unnecessary.
- Imagegen owns production method, image editing, visible quality, output files, visual QA, and reproduction archive after strategy is clear.
- Curator owns confirmed project memory: approved materials, failures, references, product fact boundaries, and workflow lessons.
- Superpowers own process gates: brainstorming, systematic debugging, writing skills, writing plans, and verification before completion.

## Pressure Scenarios

Read [references/pressure-scenarios.md](references/pressure-scenarios.md) when creating, validating, or revising this workflow skill, or when a routing failure is suspected.
