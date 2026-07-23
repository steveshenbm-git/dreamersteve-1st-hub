# Design-Led Planner

Use this reference when a Jiangyue planner task involves layout, scene, content design, homepage/hero/background visuals, product/application pages, brand-defining visuals, imagegen handoff, "not premium enough" feedback, or repeated visual failure.

## Core Rule

Planner is not replaced by a designer. Planner must use a Jiangyue design judgment layer before page, content, image-role, or imagegen-handoff decisions.

The output must not become a longer checklist. Every design judgment that affects production must be translated into:

```text
design judgment -> visible carrier -> production constraint -> QA check
```

If a judgment cannot be translated into a visible carrier or a page/content decision, keep it as reasoning only. Do not place it in the Asset Production Section.

## Task Intensity

| Level | Use when | Required output |
|---|---|---|
| Micro | small title, CTA, local wording, one-module adjustment | short Jiangyue design check plus decision |
| Standard | section plan, image direction, module order, page copy direction | Jiangyue Context Packet, Design Judgment, Page Brief |
| High-impact | homepage hero, product/application page, brand-defining visual, imagegen handoff, repeated failure, "not premium enough" feedback | full design-led Planner Brief with Asset Production Section |

Do not use full-length output for every small task. Do not skip the design check when the task looks small but affects first-screen attention, buyer trust, SEO/AEO, or visual direction.

## Jiangyue Context Packet

Build this before making design decisions:

- Page role and intensity: product, application, homepage, Contact, technical resource, or brand/vision.
- Business job: SEO acquisition, AEO visibility, product understanding, trust building, inquiry conversion, or support navigation.
- Trusted subject: product/controller expertise, HVAC/ventilation/fan/pump/application context, operating status, fault analysis, maintenance evidence, or technical documentation.
- Available formal sources: relevant `brand-system` files, approved materials, competitor references, page strategy, claim boundary.
- Visual intensity: professional content vs. atmosphere. Products and applications should stay mostly professional; brand/vision pages may carry more temperament.
- Claim boundary: what the visual or copy must not imply.

## Jiangyue Design Judgment

Judge design quality through Jiangyue-specific fundamentals, not generic adjectives.

Required checks:

- **Design risk diagnosis:** where this task can become cheap, generic, confusing, overdesigned, or off-brand.
- **Quality standard:** what "premium" means in this context: proportion, hierarchy, rhythm, restraint, information density, material credibility, space credibility, and buyer readability.
- **Trusted subject:** what visible or textual subject creates industrial credibility.
- **Brand temperament:** professional content is the subject; negative space is the temperament; B2-3 is a controlled status/recognition cue; life sense means operating visibility, not mystical AI life force.
- **Design trade-off:** what to delete, weaken, lower, crop out, leave to HTML, or refuse so the page remains credible and restrained.
- **Anti-cheapness filter:** reject AI poster look, cyber HUD, stock-vector technology, generic industrial minimalism, ecological green gradient, domestic trade-show poster feel, big-company launch spectacle, fake data/specs/certifications, and decorative Chinese motifs.

Do not say only "professional", "premium", "restrained", "high-end", or "calm". State which design fundamental makes it true and how it will be visible.

## Design-To-Brief Compiler

Use this compiler before writing the Planner Brief or revising one:

```text
Design judgment:
Visible carrier:
Page/content decision:
Production constraint:
QA check:
Reject if:
```

Examples:

```text
Design judgment: Jiangyue credibility must come from real industrial application, not abstract technology mood.
Visible carrier: recognizable HVAC/ventilation/pump/controller cues.
Page/content decision: technical and buyer information remains in HTML; image supports context.
Production constraint: include plausible equipment/environment cues; no fake UI, labels, certification marks, or readable specs.
QA check: thumbnail still reads as industrial application, not generic tech background.
Reject if: the result looks like AI poster, stock dashboard, or unverifiable customer installation evidence.
```

```text
Design judgment: B2-3 should act as recognition/status, not ecological identity.
Visible carrier: small teal status points, subtle signal accents, restrained teal-gray atmosphere.
Page/content decision: do not make green the main message or CTA proof.
Production constraint: keep teal limited; avoid large lime/green gradients and energy-flow metaphors.
QA check: first read is industrial credibility; second read notices controlled status cue.
Reject if: it reads as renewable energy, forest ecology, or neon technology.
```

## Planner Brief Relationship

The Planner Brief is the single main handoff to imagegen. The Asset Production Section lives inside the Planner Brief.

Use this internal order:

1. Context: page role, goal, audience, SEO/AEO, claim boundary.
2. Jiangyue Design Judgment: why the direction fits Jiangyue and what must be rejected.
3. Page And Content Plan: H1, support copy, CTA, module order, HTML-owned information.
4. Image Role: what the image supports, what it must not carry, first-screen attention relationship.
5. Visual Composition Contract: visible organization, relationship, form language, hierarchy, negative space, forbidden forms.
6. Asset Production Section: production-facing carriers, constraints, prompt-ready direction, QA, rejection triggers.
7. Feasibility and handoff: whether imagegen may proceed and when it must return to planner.

## Asset Production Section

The Asset Production Section is not a second brief. It compiles the design and page decisions into production-ready constraints:

```text
Asset Production Section / 素材生产段
- Source design decisions:
- Asset role:
- Output type and ratio:
- Subject carriers:
- Scene carriers:
- Composition rules:
- Color / material rules:
- Negative-space and HTML text-support rules:
- Must include:
- Must avoid:
- Prompt-ready direction:
- Deterministic post-processing:
- QA checks:
- Rejection triggers:
```

Write production constraints, not final pixels. Imagegen owns method, rendering, local retouching, and exact output files.

## Failure Attribution

When feedback arrives, assign the failure to the lowest correct layer:

| Failure signal | Likely layer | Action |
|---|---|---|
| wrong business goal, buyer, CTA, claim boundary | page strategy | revise Planner Brief |
| generic, cheap, not Jiangyue, wrong temperament | design judgment | revise Jiangyue Design Judgment |
| right judgment but missing visible subject/carrier | Asset Production Section | revise carriers and constraints |
| right brief but poor realism, artifacts, crop, lighting, execution | imagegen execution | return to imagegen with hard defects |
| macro relationship or brand worldview unclear | Workflow Director strategic layer | return to Workflow Director |

Do not send "make it better" or "more premium". Name the failed layer and the evidence that closes it.

## Pressure Scenarios

These scenarios should pass after the skill revision:

1. **Homepage hero request:** planner reads relevant Jiangyue brand context, identifies trusted industrial subject, design risk, B2-3 role, and claim boundary before composing the brief.
2. **"Not premium enough" feedback:** planner diagnoses proportion, hierarchy, rhythm, restraint, density, material/space credibility, or buyer readability instead of only saying "more premium".
3. **Imagegen failure:** planner decides whether failure belongs to design judgment, page brief, Asset Production Section, or imagegen execution before another production round.
4. **Script confusion:** planner does not hand imagegen a separate peer script when a Planner Brief with Asset Production Section is sufficient.
