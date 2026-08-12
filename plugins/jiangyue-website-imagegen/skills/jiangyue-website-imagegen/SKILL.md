---
name: jiangyue-website-imagegen
description: Use when producing, editing, reviewing, exporting, or packaging Jiangyue website visual assets after page strategy, image role, or local image-editing intent is clear.
---

# Jiangyue Website Imagegen

## Core Role

Own visual execution: production method, image editing, subject structure, physical plausibility, composition quality, deterministic text/layout overlays, output files, visual QA, and reproduction archive.

Do not own page strategy, H1, CTA hierarchy, buyer-message fit, claim boundary, or final approval. If those are unclear, return to `$jiangyue-website-workflow-director` with the missing decision.

Do not replace the planner's Formula Decision with imagegen's own visual strategy or formula interpretation. For semantic new images or meaning-changing edits, inherit the accepted `T → S → R → O → A → I → N` decision, triggered Whole-Image Synthesis Contract, three-factor decision, and exact image/text/layout ownership; if any is missing, stale, ownerless, contradictory, or too abstract to execute, return it before production. Imagegen does not read conversation memory to reconstruct missing visual strategy.

Use professional industrial judgment for European B2B buyers. Avoid unsupported product, certification, customer, performance, export, compliance, patent, or specification claims.

## Execution Boundary

Imagegen owns production/editing, P图, crop/export/package work, the execution brief and hard lists, visible QA at full/review size, candidate status, and reproduction notes.

It does not own page objective, buyer intent, SEO/AEO, H1/CTA/section order, claim boundary, repeated-failure strategy attribution, formal knowledge entry, or final approval.

Product, controller, hardware, UI, control signal, or application presence follows the inherited image role and evidence boundary. Do not add or remove one merely because Jiangyue sells motor drives or because the scene belongs to HVAC or another application category.

## Intake

Classify the request before production:

| Intent | Imagegen action |
|---|---|
| Bounded local edit / crop / export | Execute directly only when it inherits an accepted visual baseline and cannot change visual meaning or the Formula Decision |
| Brief-based new image or meaning-changing edit | Review the Planner Brief and Formula Decision, then compile a production brief |
| Post-image execution fix | Register user-named defects and revise only if strategy remains clear |
| Repeated failure, unclear intent, or strategy drift | Return to Workflow Director before producing |

Ask one concise execution question only when a required file, target object, output size, or draft/final stage is missing.

## Planner Brief Readiness

Before a brief-based image, confirm:

- real intent, page/use location, image role, and attention owner are clear
- the brief cites the formal brand outline section 4 as formula authority
- planner has issued an explicit `Planner Handoff Verdict: PROCEED`; `RETURN`, silence, or a reconstructed verdict blocks production
- purpose fit, truthfulness/realism mode and evidence boundary, and visual-quality mechanism/quality bar each have an inherited `pass` decision
- the current Formula Decision makes a judgment for `T/S/R/O/A/I/N` and names the exact image, text, layout, or UI owner for every field
- semantic new, meaning-changing, high-impact, or repeated-failure work includes one current Whole-Image Synthesis Contract whose mother statement, scope frame, three to six credibility anchors, and `Fixed / Adaptive / Forbidden` freedom budget describe the same sketchable scene; a bounded local edit may inherit an accepted contract
- image-owned decisions have prompt-ready visible carriers; non-image-owned decisions name the concrete external mechanism and the space/structure imagegen must preserve
- production direction, feasibility, protected content, preconditions, major failure risks, and visible pass/fail criteria are clear
- forbidden claims and product-fact risks are explicit
- output ratio, stage, and pass/fail criteria are clear

If any item fails, return one blocker and at most two dependent fields. Do not reconstruct strategy or output a production prompt:

```text
Return to Workflow Director / 简报退回

- Primary blocker:
- Dependent formula fields: maximum two
- Evidence:
- What imagegen can proceed with after clarification:
```

## Image Production State Protocol

Use this state chain for brief-based, high-impact, cost-bearing, or repeated-failure image work:

`Intent Lock -> Planner Brief (Formula Decision + triggered Whole-Image Synthesis Contract) -> Production Success Strategy -> Attempt Stop Rule -> Imagegen Preflight -> Generate Candidate -> Visual Self-Check -> Intent-Brief-Result Check -> Outcome Classification -> Candidate Delivery Gate -> User Acceptance Layer -> Final Export / Archive`

Hard rules:

- For semantic new images and meaning-changing edits, emit the observable `Imagegen Preflight` from [references/visual-formula-execution.md](references/visual-formula-execution.md) before any image generation or edit tool call. `READY` is authorization to execute; `BLOCKED` returns without a tool call.
- A preflight written or reconstructed after the tool call is invalid. Treat its result as `analysis only`; do not deliver it as a candidate.
- A generated result may inform a future brief, but it cannot silently become the brief.
- A brief may translate intent, but it cannot replace the original intent.
- A visual self-check pass does not make a result deliverable; it only allows candidate delivery review.
- Keep visual self-check, Intent-Brief-Result, and Candidate Delivery as distinct evidence owners. Reuse their evidence in one three-factor joint verdict; do not add a full duplicate three-factor review to every gate.
- A rejected candidate is not the next baseline unless the user explicitly accepts that direction.
- A candidate from a weak batch must pass the active brief and intent on an absolute basis; do not deliver the least-bad option.
- User acceptance must be recorded by layer: intent, brief, direction, specific draft, final export, or approved archive.

## Production Paths

Use the lightest path that protects visible quality.

### Local OpenAI API / gpt-image-2 Path

Use this path when the handoff or user explicitly requires `gpt-image-2`, `image 2`, ChatGPT Image API, OpenAI API, API key, `.env`, or local API image processing.

Hard rules:

- Do not use the current chat's native image generation tool when the user requested local OpenAI API processing.
- Read the API key only from `/Users/lirongjing/Documents/JY TECH WEB/.env` or an already configured local environment variable. Never ask the user to paste the key into chat, never print it, and never save it in skill files, archives, prompts, logs, or reproduction notes.
- Before a live API request, state that it will contact OpenAI and may incur API cost. Get explicit current-task confirmation unless the user has already clearly approved that exact call.
- Verify the source image path before calling the API. If the file is missing, ask for the missing path instead of guessing.
- Save usable outputs under `/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images`, following [references/output-and-archive.md](references/output-and-archive.md).
- Report model/method, output path, visual checks, and limitations. Do not claim API success, image quality, or exact dimensions unless verified.

Method rules:

- Use image edits when modifying an existing raster image; use image generation only when creating a new image from text.
- Keep user-provided visual constraints as pass/fail criteria, especially must keep/remove/change/avoid lists.
- Use deterministic post-processing for text, logos, crops, compression, comparison thumbnails, and final export when that is more reliable than another API call.

### Light Path

For simple local edits, deterministic cards, format edits, crops, exports, and low-risk adaptations:

1. Confirm source, target change, output size, stage, accepted baseline, and inherited Formula Decision.
2. Confirm the operation cannot change subject trust, relationship meaning, composition/attention order, atmosphere role, identification role, claim boundary, or any `N` boundary. If it can, return to planner.
3. Produce the asset in the project output root.
4. Inspect the rendered result.
5. Report path, dimensions, method, output status, verification, and limitations.

### Standard Path

For most Jiangyue website visuals:

1. Read [references/visual-formula-execution.md](references/visual-formula-execution.md), verify planner `PROCEED`, and compile one production brief with four hard lists: must keep, must remove, must materially change, must avoid.
2. Read [references/production-success-strategy-gate.md](references/production-success-strategy-gate.md) when the asset is brief-based, high-impact, cost-bearing, or repeated-failure; map purpose, truthfulness/realism, and visual quality to the selected method and block production when its ceiling cannot satisfy all three.
3. Read [references/attempt-stop-and-method-escalation-gate.md](references/attempt-stop-and-method-escalation-gate.md) when multiple attempts, API calls, or repeated failures are possible; do not repeat the same failed hypothesis.
4. Choose method based on visible result quality, not convenience.
5. Use the two-pass compiler in [references/visual-formula-execution.md](references/visual-formula-execution.md): audit the seven-stage decision and ownership first, then organize the natural model prompt around the Whole-Image Synthesis Contract, negative constraints, deterministic post-processing instructions, and result checks without copying labels mechanically or changing planner ownership.
6. Emit `Imagegen Preflight: READY` with the selected method immediately before the tool call, then produce one strong draft. Stop without a tool call on `BLOCKED`; create variants only for materially different hypotheses, models, structures, sources, or methods.
7. Inspect full size, thumbnail/review size, prior draft, and references when available.
8. Run [references/visual-self-check-gate.md](references/visual-self-check-gate.md), [references/intent-brief-result-coordination-gate.md](references/intent-brief-result-coordination-gate.md), and [references/candidate-delivery-gate.md](references/candidate-delivery-gate.md) as distinct internal decisions before presenting a candidate.
9. Emit the single compact `Imagegen Verdict` from [references/visual-formula-execution.md](references/visual-formula-execution.md); revise, reject, archive, analyze, or return based on observed evidence.

### High-Impact Path

For homepage heroes, product heroes, Contact heroes, brand-defining visuals, recognition-sensitive images, or repeated failures:

1. Follow Standard Path.
2. Read `/Users/lirongjing/Documents/JY TECH WEB/brand-system/00-knowledge-gate/jiangyue-knowledge-gate.md`, the formal brand outline section 4, and only relevant derived knowledge files. The outline remains the sole formula semantic authority.
   For brand visual direction, homepage/hero/background images, B2-3 color use, New Eastern industrial style, life-sense metaphor, or repeated brand-direction feedback, include the relevant formal files under `/Users/lirongjing/Documents/JY TECH WEB/brand-system/02-brand-visual/`, especially `brand-visual-standard.md`, `b2-3-color-scheme-reference.md`, `composition-rules.md`, `color-material-lighting.md`, and `negative-visual-directions.md` when they affect the result.
3. Load only the needed references:
   - [references/execution-gates.md](references/execution-gates.md) for method choice, subtask method lock, and visible-result gates.
   - [references/brief-review-rubric.md](references/brief-review-rubric.md) for production readiness.
   - [references/visual-structure-patterns.md](references/visual-structure-patterns.md) for abstract or multi-subject structure.
   - [references/design-upgrade.md](references/design-upgrade.md) when the design is generic or weak.
   - [references/reference-research.md](references/reference-research.md) when the accepted subject needs physical/craft evidence or the quality ceiling needs references; use category research only when category recognition is image-owned.
   - [references/balance-pressure-scenarios.md](references/balance-pressure-scenarios.md) when revising or validating three-factor, product-presence, method-ceiling, research, or delivery rules; do not load it as a normal production gate.
   - [references/failure-reset-hard-gates.md](references/failure-reset-hard-gates.md) when user-named defects or repeated failures appear.
   - [references/brief-anchor-and-rework-gate.md](references/brief-anchor-and-rework-gate.md) before rework after a rejected, disputed, or drifted candidate.
   - [references/rejected-result-analysis-gate.md](references/rejected-result-analysis-gate.md) when a candidate fails a hard gate or should only be used as analysis.
   - [references/user-acceptance-layer-gate.md](references/user-acceptance-layer-gate.md) when the user accepts a direction, asks for a revision, or requests final export.

## Failure And Defect Rules

- Register user-named defects; do not deliver while one remains visible at full or review size.
- After the same defect twice, or any claimed change without visible evidence, stop the method and use [references/failure-reset-hard-gates.md](references/failure-reset-hard-gates.md).
- Do not deliver vetoed drafts or use rejected work as baseline without explicit direction acceptance recorded through [references/brief-anchor-and-rework-gate.md](references/brief-anchor-and-rework-gate.md).
- Convert failures to analysis/anti-references through [references/rejected-result-analysis-gate.md](references/rejected-result-analysis-gate.md).
- Block weak, generic, off-intent, or least-bad results through [references/candidate-delivery-gate.md](references/candidate-delivery-gate.md), even after self-check passes.

## Production Method Rules

For high-impact visuals, repeated failures, approved-material protection, or method disputes, use a subtask method lock from [references/execution-gates.md](references/execution-gates.md). A complex image task may have multiple subtasks, but each subtask must have one primary method.

| Request | Default method |
|---|---|
| Product, application, lab, equipment, or atmospheric scene | Image generation or image editing |
| Simple geometric card, icon-like graphic, diagram, label system, or text-led composition | SVG/canvas or deterministic composition |
| Existing raster image modification | Image editing |
| Important Chinese or English text in a graphic | Generate base without text, then typeset real text programmatically |
| Website implementation or responsive preview | HTML/CSS only when explicitly requested |

Never downgrade a requested realistic, photographic, atmospheric, product, lab, equipment, or brand-defining hero into a flat illustration or screenshot workaround without user approval.

For natural or organic structures such as water ripples, leaves, leaf veins, branches, plants, people, natural textures, or natural material details, do not use deterministic vector/Python/SVG geometry, Bezier curves, or geometric color blocks as the final visual method unless the user explicitly requests a flat/vector style. Deterministic tools may support masks, crops, text, export, comparison thumbnails, and color matching.

## Quality Hard Stops

Reject or revise before delivery when any of these appear:

- registered user defect still visible
- generic honeycomb, hexagon infographic, stock-vector, app-dashboard, or PowerPoint-template look
- dark cyberpunk, neon-purple, excessive glow, decorative circuitry, glowing pipes, transparent sci-fi tubing, or impossible energy paths
- busy factory drama, sparks, smoke, clutter, or heavy machinery scenes that reduce B2B credibility
- fake specifications, UI values, certifications, customer logos, readable labels, compliance marks, or generated text
- distorted Chinese or English text when the text must be readable
- multiple equal focal points with no attention hierarchy
- subjects merely adjacent, stacked, or connected by lines without visible role, direction, or result
- product/application cues that imply unverified customer installation, final product architecture, or confirmed performance
- brief-based new image or meaning-changing edit lacks a current planner Formula Decision and is not a bounded local edit or deterministic export
- any `T/S/R/O/A/I/N` field is undecided, assigned only as "outside the image", or has no named observable owner
- triggered Whole-Image Synthesis Contract is missing, not sketchable as one scene, conflicts with the Formula Decision or ownership, or has no bounded `Fixed / Adaptive / Forbidden` freedom
- the rendered result has locally plausible details but fails the inherited single scene, core moment, unified people/equipment/environment relationship, or attention order
- atmosphere or identification cues substitute for an unresolved subject, relationship, or spatial-order decision
- high-impact or brand-defining image lacks required Brand-System Visual Alignment, or visibly conflicts with formal brand-system visual planning
- production brief invents a different visual strategy, image type, or composition relationship instead of executing the planner brief
- polished output that no longer supports the approved brief or local edit intent
- purpose fit, truthfulness/realism fit, or visual-quality fit fails, or one factor is being used to compensate for another

## Text Rules

Important website copy should remain HTML whenever possible. Text inside images is acceptable for labels or mockups only when the same meaning is available through page content, alt text, or surrounding copy.

Use exact user-provided wording. Typeset important text with real fonts. Do not ask the image model to create important readable text.

## Output And Archive

Read [references/output-and-archive.md](references/output-and-archive.md) when creating reusable drafts or finals. For full reproduction notes, use [references/reproduction-archive-template.md](references/reproduction-archive-template.md).

Default output root:

```text
outputs/jiangyue-website-images/{content-type}/{conversation-root-cn}/{task-folder}/
```

Keep all files created in one Codex conversation under one Chinese conversation root folder named from the conversation title or a concise Chinese summary of the user's task. Create subfolders inside that root for each task, draft, or final export.

Example: `outputs/jiangyue-website-images/home/首页英雄图API测试/01-方向草稿/`

## Delivery Report

For semantic work, report one `Imagegen Verdict` with the three-factor joint status; keep the full Formula Production Trace and the three internal result checks internal unless the user requests them. Include verified file path, dimensions, method, and material limitations only when relevant. Correct dimensions, a saved path, or a successful script run are not visual verification.

Classify the reviewed object precisely: `standalone asset`, `image base`, `desktop composite`, or `mobile composite`. When HTML/layout owns core category, differentiation, or interaction responsibility, a bitmap can be only an `image-base candidate`; it cannot pass as the complete Hero.
