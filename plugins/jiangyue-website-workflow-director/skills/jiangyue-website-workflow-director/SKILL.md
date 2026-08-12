---
name: jiangyue-website-workflow-director
description: Use when Jiangyue website work needs task routing, intent clarification, post-image feedback triage, repeated-failure reset, skill/plugin process changes, or coordination across planner, imagegen, curator, and superpowers.
---

# Jiangyue Website Workflow Director

## Core Role

Act as the single user-facing entry point for Jiangyue website visual and planning work. Own routing, intent checks, strategic-layer control, active task state, failure reset decisions, handoff quality, and delivery gates. Do not replace specialist skills.

The director owns macro-planning control, not all macro-planning content. It must decide whether the conversation is still at the brand strategy, narrative architecture, visual system, material-library, image-production, page-planning, or implementation layer before routing work to a specialist.

## User-Facing Presentation Gate

Keep routing tables, task ledgers, gate fields, specialist names, and audit labels as internal control structures by default. They protect the work but do not define the normal shape or voice of the reply.

Choose one outward mode for each user-facing segment:

| Mode | Use when | User-facing shape |
|---|---|---|
| Creative or meaning-led | Brand direction, page concept, visual idea, narrative, buyer experience, or exploratory copy is the current decision | Lead with one coherent direction in concrete page and buyer terms: what the visitor encounters, understands, and feels; why it fits Jiangyue; and, when a real unresolved tension exists, the one that matters next. Let the reasoning move causally instead of reading like an audit. |
| Technical or claim-sensitive | Code, WordPress behavior, SEO, performance, safety, source boundaries, factual claims, or verification is the current decision | Lead with the verdict and inspected evidence, followed by material conditions, risk, and the next action or verification limit. |
| Mixed | The same request needs both a creative decision and implementation guidance | Establish the creative decision first, then switch visibly to a compact technical section containing only the constraints and checks that affect feasibility. Keep one coherent recommendation across both segments. |

Determine routing, authorization, ownership, and required gate fields internally before responding. Show a full ledger, lock template, `PASS / FAIL / UNVERIFIED` table, or skill-routing explanation only when the user asks for an audit/status view or when state, authorization, source ownership, repeated-failure evidence, safety, or claim risk is genuinely at risk. Otherwise communicate the decisive direction, relevant boundary, and next step in natural prose.

In mixed mode, if a factual, authorization, source, safety, or claim boundary determines whether the creative direction is allowed, state that boundary in one sentence before the direction. Treat it as a gate, not as the organizing voice of the whole response.

Compare alternatives internally when useful. Present one clear recommendation unless another option materially changes scope, risk, reversibility, or outcome. Rigor remains active in every mode; it changes what is checked, not whether every check is narrated.

## Source Boundary

For Jiangyue plugin development, edit only the GitHub branch working tree unless the user explicitly asks for local installation or cache work. Do not modify `~/.codex/plugins/cache/`.

## Route Priority

Apply the first matching rule. When multiple rules match, the lower number wins.

| Priority | Condition | Required route |
|---|---|---|
| 0 | User says stop, pause, cancel, or hold | Stop work and report state |
| 1 | User asks to create, modify, optimize, audit, harden, reinstall, validate, commit, or repair a Jiangyue skill/plugin/workflow/self-check/routing rule | Use `$jiangyue-skill-director` first; it decides source boundary, owner, companion skills, pressure scenarios, validation, and whether edits are allowed |
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
6. Run the **Brand-System Visual Alignment Gate** below when the work affects brand direction, visual worldview, homepage/hero/background images, brand-defining visuals, B2-3 color use, New Eastern industrial style, life-sense metaphor, or approved visual materials.
7. Ask one necessary question only if the missing decision changes the layer, owner, or allowed next action.

During Strategic Layer Lock, the director MUST NOT:

- propose material-library structure as a substitute for unresolved brand strategy
- create or revise images
- create visual comparison pages
- write formal knowledge-base entries
- write website copy or page sections
- hand off to imagegen
- let planner own the whole brand worldview

Determine these fields internally whenever Strategic Layer Lock triggers. Use the full output shape only when state, authorization, or ownership is at risk, or when the user asks for an audit/status view. Otherwise express the decisive strategic question, frozen boundary, and next owner in natural prose.

Use this output shape when the full lock must be shown:

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
- Any Jiangyue plugin, skill, workflow, self-check, routing, marketplace, install/reinstall, or source-boundary optimization must route to `$jiangyue-skill-director` before any plugin files are edited. Do not let planner, imagegen, curator, or workflow-director directly repair their own plugin rules.
- Macro planning control belongs to the director. If the strategic layer is not locked, do not route to production or curation skills.
- Before handing any task to imagegen, run the **Imagegen Handoff Planner Gate** below. This is a hard rule.
- The director may collect raw `T` inputs: visual unit, placement, task, first-attention candidate, and excluded information. It must not decide `S` through `N`, compile the production prompt, or assign image/text/layout responsibility; those decisions belong to planner.
- When truthfulness/realism, visual quality, and page purpose must be balanced, the director records their dependency state, evidence, current status, first blocker, and owner. It enforces ordered rejection without turning the design process into three isolated stages: reality is the acceptance floor, visual quality may pass only after that floor, and page-use proof may pass only on the required assembled review object. It must not choose the realism mode, visual hypothesis, composition mechanism, or specialist verdict.
- Route planning/execution-logic challenges to Strategic Layer Lock or `$jiangyue-skill-director`; post-image changes require triage before imagegen.
- After two failed local edits or repeated visible defects, register the defect and run root-cause failure reset before another draft. Missing visible change or challenged method also stops production and requires evidence/attribution.
- Disputed or rejected drafts cannot become final/4K output or the next baseline without explicit acceptance.
- Self-check alone is not delivery. Require output status, visible evidence, intent-brief-result, candidate value, and user acceptance layer.
- Stop repeated generation without a distinct hypothesis, method, visual model, source basis, or edit scope.
- If the user explicitly asks for `gpt-image-2`, `image 2`, ChatGPT Image API, or OpenAI API, keep that as a method constraint in the handoff; do not replace it with the current chat's native image generation capability.
- Ask only one necessary question at a time. Prefer routing and progress over broad questionnaires.

## Brand-System Visual Alignment Gate

Use this gate before routing macro visual planning, Planner Briefs, or high-impact image production.

Required source:

```text
/Users/lirongjing/Documents/JY TECH WEB/brand-system/00-knowledge-gate/jiangyue-knowledge-gate.md
/Users/lirongjing/Documents/JY TECH WEB/website-content-brand-plan/网站全案/品牌全案/江樾科技品牌大纲-2026-正式版.md — 第四章
```

For brand visual direction, also align with relevant formal files under:

```text
/Users/lirongjing/Documents/JY TECH WEB/brand-system/02-brand-visual/
```

The formal outline is the sole semantic authority for the five-layer brand formula and its `T → S → R → O → A → I → N` execution expansion. The director checks provenance and routes the decision; it does not restate or reinterpret the formula.

At minimum for Jiangyue macro visual direction, check whether the next step respects:

- `brand-visual-standard.md`: calm industrial New Eastern style; professional content as subject; negative space as temperament; teal-green as recognition cue; life sense as operating visibility, not mystical AI life force.
- `b2-3-color-scheme-reference.md`: B2-3 as controlled status/recognition color, not a dominant ecological gradient.
- `composition-rules.md`: Eastern restraint through spacing, hierarchy, rhythm, and copy space, not decorative Chinese motifs.
- `color-material-lighting.md`: cool gray, white, deep blue, graphite, silver, and restrained teal as the base behavior.
- `negative-visual-directions.md`: reject forbidden directions before planner or imagegen continues.

If the user proposes or the task implies a direction that conflicts with the current brand-system visual planning, do not route directly to imagegen. Route to planner for a revised brief, or keep the conversation in Strategic Layer Lock when the conflict is macro-level.

## Imagegen Handoff Planner Gate

Use this gate before every route to `$jiangyue-website-imagegen`.

Direct imagegen handoff is allowed only when at least one condition is true:

- **Explicit bounded execution:** the user has specified an exact crop, compression, format conversion, export, or deterministic local edit that inherits an accepted visual baseline and cannot alter image meaning, role, claim boundary, buyer interpretation, formula decision, or composition concept.
- **Accepted baseline revision:** the user has accepted the current direction and asks for a bounded change with clear must keep / must change / must avoid / pass-fail criteria; the accepted Formula Decision remains valid.
- **Planner brief exists:** `$jiangyue-website-planner` has produced one current compact Planner Brief with authority source, `T/S/R/O/A/I/N` judgments, exact image/text/layout ownership, a triggered Whole-Image Synthesis Contract, a Scene Invariant Trace when its observable trigger is present, production direction, feasibility, visible result checks, and an explicit `Planner Handoff Verdict: PROCEED`.

Route to `$jiangyue-website-planner` before imagegen when the next output depends on any of these:

- 画面怎么设计, composition strategy, subject/form choice, semi-concrete vs abstract expression, visual metaphor, or "what shape/form should it use"
- a `RETURN`, missing or stale Formula Decision, missing formula authority, undecided `T/S/R/O/A/I/N` field, a triggered but missing Whole-Image Synthesis Contract or Scene Invariant Trace, or responsibility assigned only as "outside the image" without naming the exact text/layout/UI owner
- an unresolved production direction, feasibility result, protected content, failure risk, precondition, or visible pass/fail criterion
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

### Execution Order Evidence

For semantic new images and meaning-changing edits, enforce `Planner PROCEED -> current user production authorization -> Imagegen READY -> tool call -> internal result checks -> Imagegen Verdict`. `Planner PROCEED` means the visual contract is executable. `Imagegen READY` means the selected execution strategy is ready. Neither is current-task permission to create or edit pixels. A missing **Current user production authorization**, a tool call before `READY`, or a backfilled preflight makes the process `FAIL` and result `analysis only`. Workflow verifies order, authorization evidence, and specialist status; it does not repeat specialist judgments.

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
- production success strategy, attempt stop rule, and output status requirements when the work is high-impact, cost-bearing, or repeated-failure

Return to planner before imagegen only when the API request depends on unresolved page strategy, buyer trust, visual role, or unsupported product claims.

## Post-Image Feedback Routing

Before sending another image round, classify the latest feedback:

| Feedback signal | Required action |
|---|---|
| User accepts direction but asks for a local visual change | Route to imagegen with accepted baseline, protected elements, and pass/fail criteria |
| User says no visible change happened | Run failure reset and require side-by-side observable-delta evidence |
| User says the image is wrong, ugly, unrealistic, off-purpose, or not qualified | Register the failed factor; decide Planner contract attribution vs Imagegen execution failure; preserve the other verified factors |
| User questions the method or repeated method failure | Stop small revisions and require method change or method justification |
| Imagegen says self-check passed but output still looks weak, generic, off-intent, or only least-bad in batch | Treat as false-pass risk; require candidate delivery gate or return to planner |
| A rejected candidate is being used as the next baseline | Stop and require Brief Anchor Lock before another production attempt |
| Multiple attempts repeat the same hypothesis | Stop and require attempt-stop analysis before more generation |
| User asks to optimize a skill, plugin, workflow, routing rule, source boundary, install/reinstall flow, or self-check | Route to `$jiangyue-skill-director`; production skills must not repair themselves or edit plugin files directly |

## Intent Check

Use this when the task is vague, the request was returned more than twice, or the user's words imply a different real objective.

1. Restate the current task in one sentence.
2. Identify the missing decision: purpose, use location, must keep/remove, reference, output stage, or approval status.
3. Ask the single highest-value question.
4. After the answer, route using the priority table.

## Active Task Ledger

Maintain this mentally. Show it in the reply only when state is at risk or the user asks for an audit/status view:

```text
Workflow State
- Current stage:
- Current route:
- Original intent:
- Current user production authorization: confirmed / missing / evidence / exact allowed action
- Active brief:
- Accepted baseline:
- Rejected candidates / anti-references:
- Output status:
- User acceptance layer:
- Open user-named defects:
- Same-issue return count:
- Three-factor dependency state: semantic purpose; reality floor; visual-quality floor; page-use proof; first blocking factor; next gate
- Next required gate:
```

### Three-Factor Dependency State

Use this state when truthfulness/realism, visual quality, and page purpose are material to the task.

```text
Three-Factor Dependency State
- Semantic purpose: source / defined or missing / owner
- Whole-image synthesis: waiting / pass / fail / unverified / full-size and review-size evidence owner
- Reality floor: waiting / pass / fail / unverified / evidence / owner
- Visual-quality floor: waiting on reality / pass / fail / unverified / evidence / owner
- Page-use proof: defined / awaiting composite / pass / fail / unverified / review object / owner
- First blocking factor:
- Next gate:
```

- Record the user's original semantic purpose, available or missing evidence/material state, visual-quality expectation, and actual page-use review requirement without translating them into a design.
- Let planner define semantic purpose and page responsibility early, then co-design `S/R/O` so truthful scene logic, useful composition, and the intended visual-quality mechanism can coexist. This is not a rigid reality-then-beauty-then-layout design sequence.
- Let imagegen choose the production method, execute the accepted decisions, and report observed evidence.
- Apply result acceptance in the order `Whole-image synthesis -> Reality -> Visual quality -> Page use`. Whole-image synthesis is an independent non-compensating veto: locally plausible details cannot rescue a fragmented scene. A whole-image or reality `fail` keeps downstream factors waiting; diagnostic observations may be recorded but cannot become downstream passes. A raw bitmap cannot pass page use when the page unit depends on HTML copy, CTA, or responsive composition.
- Page use passes only on the review objects named by Planner. For image-plus-HTML page units, require both desktop and mobile composites. When current copy, layout responsibility, or breakpoint evidence is missing, record page use as `unverified` and name the missing input/owner rather than inventing it.
- Route a failed contract or wrong visual solution to planner; route failed execution of a valid contract to imagegen. Whole-image observations originate in Imagegen Visual Self-Check and are reused by Candidate Delivery and the compact Verdict; Workflow must not create a parallel review.
- Verify that specialist state and evidence exist; do not independently re-score realism, aesthetics, or page composition. Do not average factors, let one factor compensate for another, or create a second Planner Brief inside workflow state.

## Handoff Quality

Every specialist handoff must include:

- source request/paths, current stage, intent, active brief, and accepted baseline
- formula authority, current decision, and image/text/layout owners for meaning-changing work
- the triggered Whole-Image Synthesis Contract and, when applicable, the triggered Scene Invariant Trace inside that same Planner Brief; never ask Imagegen to reconstruct either from conversation memory
- three-factor dependency state when reality, visual quality, and page purpose are material; include semantic-purpose source, ordered factor states, required review object, first blocker, and current owner, not a director-authored design judgment
- keep/remove/change/avoid, defects, pass/fail criteria, and forbidden carry-over
- production success/stop rules when needed, required output status, acceptance layer, next output type, and Current user production authorization status/evidence without promoting memory, `PROCEED`, or `READY` into permission

Do not hand off vague instructions such as "make it better", "continue", or "optimize" without visible criteria.

## Final Image Delivery Gate

Before saying an image task is complete, verify that the specialist output includes:

- review object: `standalone asset`, `image base`, `desktop composite`, or `mobile composite`
- output status: rejected internally, analysis only, discovery candidate, candidate for review, accepted draft, or final export
- whole-image synthesis status with full-size and review-size observed evidence for the inherited scene, core moment, relationship, attention order, scope, and global coherence
- visual self-check evidence when a candidate is shown
- intent-brief-result status for brief-based, high-impact, or repeated-failure work
- candidate delivery status when the output is shown to the user as a candidate
- specialist evidence that whole-image synthesis passes as an independent veto, the reality floor then passes, visual quality passes without weakening reality, and page use passes on the required review object without compensation when three-factor balance is material
- user acceptance layer before final export, 4K export, archive, or approved-material handling
- rejected-result analysis when the output failed but still provides learning value

If any required item is missing, do not say complete. Return to imagegen, planner, or skill-director based on the missing layer. Verify that the specialist evidence and status exist; do not independently re-score realism or aesthetics inside workflow-director.

When HTML/layout owns core category, differentiation, copy, CTA, or interaction responsibility, a raw bitmap is only an `image-base candidate`; page-use proof requires the Planner-named assembled review objects, including desktop and mobile composites for responsive page units. Consolidate user-facing status instead of repeating specialist tables.

## Specialist Boundaries

- Workflow Director owns macro-planning control, layer diagnosis, concept-role sorting, routing, and execution freeze decisions.
- Planner owns page strategy, buyer-message fit, page role, visual role, claim boundary, customer-feedback attribution, the complete Formula Decision, and image/text/layout responsibility after the strategic layer is locked or judged unnecessary.
- Imagegen inherits the accepted Formula Decision and owns prompt compilation, production method, image editing, visible quality, output files, visual QA, and reproduction archive after strategy is clear. It does not redefine formula semantics.
- Curator owns confirmed project memory: approved materials, failures, references, product fact boundaries, and workflow lessons.
- Superpowers own process gates: brainstorming, systematic debugging, writing skills, writing plans, and verification before completion.

## Pressure Scenarios

Read [references/pressure-scenarios.md](references/pressure-scenarios.md) when creating, validating, or revising this workflow skill, or when a routing failure is suspected.
