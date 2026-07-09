---
name: jiangyue-website-imagegen
description: Use when producing, editing, reviewing, exporting, or packaging Jiangyue website visual assets after page strategy, image role, or local image-editing intent is clear.
---

# Jiangyue Website Imagegen

## Core Role

Own visual execution: production method, image editing, subject structure, physical plausibility, composition quality, deterministic text/layout overlays, output files, visual QA, and reproduction archive.

Do not own page strategy, H1, CTA hierarchy, buyer-message fit, claim boundary, or final approval. If those are unclear, return to `$jiangyue-website-workflow-director` with the missing decision.

Do not replace a planner Visual Composition Contract / 画面构成合同 with imagegen's own visual strategy. For brief-based new images, imagegen executes the planner's strategy-and-composition contract; if the contract is missing or too abstract, return it before production.

Use professional industrial judgment for European B2B buyers. Avoid unsupported product, certification, customer, performance, export, compliance, patent, or specification claims.

## Execution Boundary

Imagegen owns:

- new image production after strategy or local edit intent is clear
- P图, element removal, crop, cleanup, background extension, upscaling/export, and file packaging
- production brief, hard keep/remove/change/avoid lists, visual QA, and reproduction notes
- visible quality checks at full size and thumbnail/review size

Imagegen does not own:

- page objective, buyer intent, SEO/AEO, H1, CTA, section order, or claim boundary
- deciding whether user feedback is a strategy problem after repeated failure
- formal knowledge-base entry
- final approval

## Intake

Classify the request before production:

| Intent | Imagegen action |
|---|---|
| Local edit / P图 / crop / export | Execute directly if source, target, and output are clear |
| Brief-based new image | Review the Planner Brief and Visual Composition Contract, then produce a production brief |
| Post-image execution fix | Register user-named defects and revise only if strategy remains clear |
| Repeated failure, unclear intent, or strategy drift | Return to Workflow Director before producing |

Ask one concise execution question only when a required file, target object, output size, or draft/final stage is missing.

## Planner Brief Readiness

Before a brief-based image, confirm:

- real intent, page/use location, image role, and attention owner are clear
- for non-local brief-based production, a Visual Composition Contract / 画面构成合同 is present, or the planner brief explicitly states why it is unnecessary
- the contract defines image type, visible layers, placement/proportion, shape or semi-concrete form, direction/motion, hierarchy, negative-space/text area, buyer-readable meaning, and forbidden forms
- for brand-defining, homepage/hero/background, B2-3, New Eastern industrial, life-sense, or repeated brand-direction tasks, the brief includes Brand-System Visual Alignment / 品牌视觉系统对齐 or explicitly states why no formal brand-system file is relevant
- for non-local brief-based production, the brief includes Brief Feasibility Analysis / 简报可行性分析 with whether imagegen may proceed, production controllability, major failure risks, protected content, and preconditions
- required subjects have visible carriers
- abstract terms are translated into visible cues
- visual relationships are readable: role, direction, cause/effect, comparison, support layer, control flow, or application context
- forbidden claims and product-fact risks are explicit
- output ratio, stage, and pass/fail criteria are clear

If not ready, return this:

```text
Return to Workflow Director / 简报退回

- Missing decision:
- Missing visual composition contract:
- Missing brand-system visual alignment:
- Missing brief feasibility analysis:
- Too abstract for production:
- Missing visible carrier or relationship:
- Claim / product-fact risk:
- What imagegen can proceed with after clarification:
```

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

1. Confirm source, target change, output size, and stage.
2. Produce the asset in the project output root.
3. Inspect the rendered result.
4. Report path, dimensions, method, verification, and limitations.

### Standard Path

For most Jiangyue website visuals:

1. Create a production brief from the planner strategy-and-composition contract and four hard lists: must keep, must remove, must materially change, must avoid.
2. Choose method based on visible result quality, not convenience.
3. Translate approved composition intent into concrete subject carriers, visual relationships, physical logic, and pass/fail checks without changing the planner's visual strategy.
4. Produce one strong draft first; create variants only when they differ materially.
5. Inspect full size, thumbnail/review size, prior draft, and references when available.
6. Revise, reject, archive, or return to Workflow Director based on visible evidence.

### High-Impact Path

For homepage heroes, product heroes, Contact heroes, brand-defining visuals, recognition-sensitive images, or repeated failures:

1. Follow Standard Path.
2. Read `/Users/lirongjing/Documents/JY TECH WEB/brand-system/00-knowledge-gate/jiangyue-knowledge-gate.md` and only relevant formal knowledge files.
   For brand visual direction, homepage/hero/background images, B2-3 color use, New Eastern industrial style, life-sense metaphor, or repeated brand-direction feedback, include the relevant formal files under `/Users/lirongjing/Documents/JY TECH WEB/brand-system/02-brand-visual/`, especially `brand-visual-standard.md`, `b2-3-color-scheme-reference.md`, `composition-rules.md`, `color-material-lighting.md`, and `negative-visual-directions.md` when they affect the result.
3. Load only the needed references:
   - [references/execution-gates.md](references/execution-gates.md) for method choice, subtask method lock, and visible-result gates.
   - [references/brief-review-rubric.md](references/brief-review-rubric.md) for production readiness.
   - [references/visual-structure-patterns.md](references/visual-structure-patterns.md) for abstract or multi-subject structure.
   - [references/design-upgrade.md](references/design-upgrade.md) when the design is generic or weak.
   - [references/reference-research.md](references/reference-research.md) when category recognition or reference quality matters.
   - [references/failure-reset-hard-gates.md](references/failure-reset-hard-gates.md) when user-named defects or repeated failures appear.

## Failure And Defect Rules

- Copy user-named defects into a defect register.
- A revised image may not be delivered if a registered defect remains visible at full size or thumbnail size.
- If the same registered defect remains twice, stop the method and return to Workflow Director.
- If the user says a requested change did not visibly happen, read [references/failure-reset-hard-gates.md](references/failure-reset-hard-gates.md) and do not deliver another draft without observable change evidence.
- If the user says self-check failed, still wrong, not qualified, ugly, missed a reference, ignored an attachment, or marks the same defect, read [references/failure-reset-hard-gates.md](references/failure-reset-hard-gates.md) before further production.
- Do not deliver a vetoed draft as a concept option.

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
- brief-based new image lacks a required planner Visual Composition Contract and is not a bounded local edit or deterministic export
- high-impact or brand-defining image lacks required Brand-System Visual Alignment, or visibly conflicts with formal brand-system visual planning
- production brief invents a different visual strategy, image type, or composition relationship instead of executing the planner brief
- polished output that no longer supports the approved brief or local edit intent

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

Examples:

```text
outputs/jiangyue-website-images/home/首页英雄图API测试/01-方向草稿/
outputs/jiangyue-website-images/home/首页英雄图API测试/02-局部修改/
outputs/jiangyue-website-images/home/首页英雄图API测试/03-final/
```

## Delivery Report

Report only verified facts:

- final file path
- task folder path
- reproduction archive path, or `not created yet`
- dimensions and format
- production method
- formal `brand-system` files consulted, if any
- what was visually checked
- what could not be verified
- remaining limitation, if any

Correct dimensions, a saved path, or a successful script run are not visual verification. Inspect the rendered output before claiming a visual pass.
