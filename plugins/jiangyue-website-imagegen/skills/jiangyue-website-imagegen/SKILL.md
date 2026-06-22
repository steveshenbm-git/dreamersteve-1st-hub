---
name: jiangyue-website-imagegen
description: Use when creating, editing, or reviewing website visuals for Jiangyue Technology, including Chinese or English page graphics, industrial product imagery, AI-assisted motor-control concepts, application scenes, technical-resource images, card graphics, hero images, and WordPress-ready visual assets.
---

# Jiangyue Website Imagegen

## Core Role

Create, edit, review, and package Jiangyue Technology website visuals after the page strategy is clear. This skill owns visual execution: production method, visual structure, physical plausibility, composition quality, deterministic text/layout overlays, output files, and reproduction archive.

It does not own page strategy. For page objective, buyer intent, SEO/AEO direction, H1, CTA, section order, first-screen attention hierarchy, image role, claim boundary, or message ownership, use `$jiangyue-website-planner` first.

Use professional industrial judgment for European B2B buyers. Avoid unsupported product, certification, customer, performance, export, compliance, patent, or specification claims.

## Contract With Planner

Treat the planner handoff as the strategy contract.

**Planner Brief = strategy contract.** It should define page, page goal, target audience, core page message, first-screen attention owner, image role, information the image must support, information kept in HTML/page copy, required subject cues, forbidden claims, recommended direction, CTA/title/logo relationship, and output location or ratio.

**Imagegen Production Brief = execution contract.** Imagegen turns the strategy contract into a production-ready visual plan: execution intent, must keep/remove/change/avoid lists, subject carriers, relationship model, physical logic, attention hierarchy, copy placement, production method, output size, archive level, and visible pass/fail criteria.

Do not silently change page goal, H1, CTA hierarchy, attention owner, image role, claim boundary, page section order, or message ownership. If the image can only work by changing one of these, stop and return to planner.

## When To Use Planner First

Use `$jiangyue-website-planner` before image production when any of these are unclear or contested:

- page type, buyer, SEO/AEO job, inquiry path, H1, CTA, or section order
- first-screen attention owner or image role
- whether a message belongs in image, HTML copy, CTA, logo area, or later page content
- claim boundary, verified product facts, or application context
- user feedback questions brand direction, credibility for European B2B buyers, layout integration, visual hierarchy, or strategy fit
- two structural image revisions failed for the same reason

Imagegen may ask one concise execution question when the strategy is clear but one production detail is missing.

## Workflow Selection

Use the lightest path that protects visible quality.

### Light Path

Use for format edits, simple local edits, deterministic cards, text-led graphics, exports, and low-risk adaptations.

1. Classify execution intent.
2. Confirm asset, size, source, text, and output format.
3. Choose production method.
4. Produce the asset in a task folder.
5. Inspect the rendered result.
6. Deliver file path, size, method, verification, and limitations.

### Standard Path

Use for most Jiangyue website visuals.

1. Classify execution intent and extract planner or user requirements.
2. Create the production brief and four hard lists: must keep, must remove, must materially change, must avoid.
3. Check subject carriers, relationship readability, physical plausibility, method fit, claim risk, and text risk.
4. Ask for confirmation before a new image or brief-based rebuild unless the user already gave equivalent clear approval.
5. Produce one strong draft first; create variants only for meaningful visual differences.
6. Review full size, thumbnail size, and reference/prior draft when available.
7. Revise, reject, archive, or return to planner based on visible result.

### High-Impact Path

Use for homepage heroes, product heroes, Contact heroes, brand-defining visuals, abstract advantage visuals, recognition-sensitive images, or repeated failures.

1. Follow the Standard Path.
2. Read only the relevant references before production:
   - [references/image-brief-template.md](references/image-brief-template.md) for intake and production brief structure.
   - [references/brief-review-rubric.md](references/brief-review-rubric.md) for production readiness scoring.
   - [references/visual-structure-patterns.md](references/visual-structure-patterns.md) for abstract, multi-subject, or physically metaphorical structures.
   - [references/design-upgrade.md](references/design-upgrade.md) when the design is thin, generic, template-like, or visually weak.
   - [references/reference-research.md](references/reference-research.md) when category recognition or visual quality needs reference research.
3. Offer 2-3 materially different structure directions unless planner or user already approved a clear structure.
4. Compare the output against the user's reference or prior strongest draft before delivery.
5. If the same structural failure repeats twice, stop and return to planner.

## Execution Gates

For detailed gate rules, read [references/execution-gates.md](references/execution-gates.md) when producing or reviewing an asset.

Always run these gates in short form:

1. **Execution intent:** new image, brief-based rebuild, local edit, format edit, or page/mockup work.
2. **Intent lock:** original job, core message, what the image communicates, what HTML/page copy carries, and drift boundaries.
3. **Production readiness:** every named subject has a visible carrier or planned page-copy carrier; the relationship is readable; the output size and role are clear.
4. **Method quality:** choose the method because it can reach the required visible result, not because it is easier to save, script, or archive.
5. **Physical plausibility:** real-world objects, industrial equipment, electronics, enclosures, flows, and support layers must be mechanically or visually believable.
6. **Visible result:** judge the rendered image before defending prompt, method, palette, archive, or workflow compliance.

## Production Method Rules

Default methods:

| Request | Default method |
|---|---|
| Product, application, lab, equipment, or atmospheric scene | Image generation or image editing |
| Simple geometric card, icon-like graphic, diagram, label system, or text-led composition | SVG/canvas or deterministic composition |
| Existing raster image modification | Image editing |
| Important Chinese or English text in a graphic | Generate base without text, then typeset real text programmatically |
| Website implementation or responsive preview | HTML/CSS only when explicitly requested |

Never downgrade a requested realistic, photographic, atmospheric, product, lab, equipment, or brand-defining hero into a flat illustration or screenshot workaround without user approval. If the available method cannot produce or expose a usable image at the required quality, stop and report the limitation.

## Quality Hard Stops

Reject or revise before delivery when any of these appear:

- generic honeycomb, hexagon infographic, stock-vector, app-dashboard, or PowerPoint-template look
- dark cyberpunk, neon-purple, excessive glow, decorative circuitry, or impossible energy pipes
- fake specifications, UI values, certifications, customer logos, readable labels, compliance marks, or generated text
- multiple equal focal points with no attention hierarchy
- subjects that are merely adjacent, stacked, or connected by lines without visible role, direction, or result
- product/application cues that imply unverified customer installation, final product architecture, or confirmed performance
- a revision that keeps the user-named defect visible at full size or thumbnail size
- a polished image that no longer supports the planner brief or original intent lock

## Text Rules

Important website copy should remain HTML whenever possible. Text inside images is acceptable for labeled graphics or visual mockups only when the same meaning is also available through page content, alt text, or the surrounding page.

Use exact user-provided wording. Typeset important Chinese or English text with real fonts. Do not ask the image model to create important readable text.

## Revision And Planner Return

For failure attribution, revision discipline, and planner return format, read [references/revision-and-planner-return.md](references/revision-and-planner-return.md).

Short rule:

- Continue in imagegen when the strategy is sound but composition, crop, material, lighting, realism, subject cue, or file execution is weak.
- Return to planner when the image responsibility is too broad or contradictory, attention owner is unclear, image role conflicts with page goal, claims are unsafe, page copy/CTA/H1 must change, or the same structural failure repeats.

## Output And Archive

For folder structure and reproduction archive details, read [references/output-and-archive.md](references/output-and-archive.md). For full archive content, use [references/reproduction-archive-template.md](references/reproduction-archive-template.md).

Default output root:

```text
outputs/jiangyue-website-images/{content-type}/{YYYY-MM-DD-short-topic-draft-01}/
outputs/jiangyue-website-images/{content-type}/{YYYY-MM-DD-short-topic-final}/
```

Use archive levels:

- **Trial:** exploratory or not-yet-usable output; save only needed inspection files.
- **Usable draft:** passes basic intent, composition, size, and artifact review; create a reproduction archive.
- **Final:** user-accepted or production-intended asset; update reproduction archive and compact rebuild recipe when practical.

## Delivery Report

Report only verified facts:

- final file path
- task folder path
- reproduction archive path, or `not created yet` for trial-only outputs
- dimensions and format
- production method
- what was visually checked
- what could not be verified
- remaining limitation, if any

Do not claim browser, mobile, SEO, compression, WordPress behavior, or exact reproducibility unless it was checked.
