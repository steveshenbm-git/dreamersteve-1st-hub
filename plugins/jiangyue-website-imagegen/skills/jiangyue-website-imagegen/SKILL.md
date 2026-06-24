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

**Planner Brief = strategy contract.** It should define the user's original request, planner-diagnosed likely need, user-confirmed real intent, page, page goal, target audience, core page message, first-screen attention owner, image role, information the image must support, information kept in HTML/page copy, required subject cues, visible relationships, forbidden claims, recommended direction, CTA/title/logo relationship, output location or ratio, imagegen freedom, and return-to-planner triggers.

**Imagegen Production Brief = execution contract.** Imagegen turns the strategy contract into a production-ready visual plan: execution intent, must keep/remove/change/avoid lists, subject carriers, relationship model, physical logic, attention hierarchy, copy placement, production method, output size, archive level, and visible pass/fail criteria.

Do not silently change page goal, H1, CTA hierarchy, attention owner, image role, claim boundary, page section order, or message ownership. If the image can only work by changing one of these, stop and return to planner.

If the Planner Brief does not include a confirmed real intent, do not produce a new image. Return to planner for guided intent confirmation.

## When To Use Planner First

Use `$jiangyue-website-planner` before image production when any of these are unclear or contested:

- page type, buyer, SEO/AEO job, inquiry path, H1, CTA, or section order
- first-screen attention owner or image role
- whether a message belongs in image, HTML copy, CTA, logo area, or later page content
- claim boundary, verified product facts, or application context
- user feedback questions brand direction, credibility for European B2B buyers, layout integration, visual hierarchy, or strategy fit
- two structural image revisions failed for the same reason

Imagegen may ask one concise execution question when the strategy is clear but one production detail is missing.

## Planner Brief Readiness Review

Before creating or rebuilding an image from a Planner Brief, review whether the brief can actually produce a strong visual. Do not treat a brief as ready only because it has many fields.

The brief is ready only when all of these are clear:

- the user's original request and the user-confirmed real intent are both present
- the page goal, buyer, image role, attention owner, and claim boundary are concrete
- the image has a specific communication job, not only a mood word such as "premium", "technical", "future", "trust", or "AI"
- every required subject has either a visible subject carrier or a planned HTML/page-copy carrier
- the relationship between subjects is visible: role, direction, cause/effect, comparison, control flow, support layer, or application context
- abstract terms have been translated into visible cues imagegen can execute
- required and forbidden product/application claims are explicit enough to avoid unsafe implication
- output ratio, use location, and pass/fail criteria are specific

Return to planner instead of producing when:

- confirmed real intent is missing or still described as a guess
- the image is expected to solve page strategy, H1, CTA, claim boundary, or buyer-message problems
- the brief asks for a broad idea but gives no concrete subject carriers or relationships
- required subjects are named but their visual role is unclear
- the image would need to invent product facts, specifications, customer use, compliance status, or final architecture
- pass/fail criteria depend on explanation rather than visible evidence

Use this return format:

```text
Return to Planner / 简报退回

- Missing or unclear confirmed real intent:
- Brief item that is too abstract for reliable image production:
- Missing visible subject carrier or relationship:
- Claim / product-fact risk:
- One recommended planner question to ask next:
- What imagegen can proceed with after clarification:
```

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
2. Run Planner Brief Readiness Review when working from planner handoff.
3. Create the production brief and four hard lists: must keep, must remove, must materially change, must avoid.
4. Translate abstract terms into concrete subject carriers, visual relationships, physical logic, and pass/fail checks.
5. Check subject carriers, relationship readability, physical plausibility, method fit, claim risk, and text risk.
6. Ask for confirmation before a new image or brief-based rebuild unless the user already gave equivalent clear approval.
7. Produce one strong draft first; create variants only for meaningful visual differences.
8. Review full size, thumbnail size, and reference/prior draft when available.
9. Revise, reject, deliver without full archive, archive on request, or return to planner based on visible result.

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
2. **Intent lock:** original request, confirmed real intent, core message, what the image communicates, what HTML/page copy carries, and drift boundaries.
3. **Production readiness:** every named subject has a visible carrier or planned page-copy carrier; abstract terms are translated into concrete cues; the relationship is readable; the output size and role are clear.
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

Do not create a full reproduction archive for every image draft. A weak or rejected draft should not receive a full archive just because it was generated.

Use archive levels:

- **Trial:** exploratory or not-yet-usable output; save only needed inspection files.
- **Usable draft:** passes basic intent, composition, size, and artifact review; deliver the image and inspection notes without a full reproduction archive unless the user asks to keep it.
- **Final:** user-accepted, user-requested for archive, or production-intended asset; create or update the reproduction archive and compact rebuild recipe when practical.

Archive only when one of these is true:

- the user explicitly asks to archive, save, preserve, or package the result
- the user approves the draft as final or production-intended
- the task is a deterministic template, reusable card system, or approved source asset that must be reproduced later
- the archive is needed to hand off production work and the current result is worth preserving

## Delivery Report

Report only verified facts:

- final file path
- task folder path
- reproduction archive path, or `not created yet` when no full archive was requested or justified
- dimensions and format
- production method
- what was visually checked
- what could not be verified
- remaining limitation, if any

Do not claim browser, mobile, SEO, compression, WordPress behavior, or exact reproducibility unless it was checked.
