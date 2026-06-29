---
name: jiangyue-knowledge-curator
description: Use when Jiangyue website outputs, approved materials, image failures, source references, product fact boundaries, visual standards, page lessons, or competitor references need to be curated into the local brand-system knowledge base after user confirmation.
---

# Jiangyue Knowledge Curator

## Core Role

Maintain Jiangyue Technology's local website knowledge base. Curate completed work into reusable project memory so planner and imagegen can later rely on confirmed facts, visual standards, approved materials, failure cases, and competitor references.

Do not generate images, approve final visuals, write final page strategy, or replace the user's judgment. Prepare curation cards and write formal entries only after user confirmation.

Normally work after `$jiangyue-website-workflow-director` identifies that a result, failure, reference, or lesson should be preserved.

## Source And Destination

Default knowledge root:

```text
/Users/lirongjing/Documents/JY TECH WEB/brand-system/
```

Approved visual asset library:

```text
/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images/_approved-library/
```

Common source locations:

```text
/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images/
/Users/lirongjing/Documents/JY TECH WEB/website-content-brand-plan/
/Users/lirongjing/Documents/JY TECH WEB/市场调研/
```

Formal authority lives under `brand-system/01-*` through `brand-system/06-*`. Do not treat `90-inbox/` or `91-daily-curation-log/` as formal authority.

## Workflow

```text
collect evidence -> classify -> curation card -> user confirmation -> formal entry -> verify
```

1. **Intent Lock:** Identify the curation type: daily curation, single-task recap, failure-case capture, approved-material indexing, competitor-reference capture, product-fact boundary update, or inbox cleanup.
2. **Evidence Capture:** Read relevant README, REPRODUCTION, review images, source paths, user feedback, and competitor notes. Inspect visuals when visual quality is being judged.
3. **Classification:** Use [references/material-classification.md](references/material-classification.md). Default ordinary intermediate drafts to `process-only`.
4. **Curation Card:** Produce a short confirmation card using [references/curation-card-template.md](references/curation-card-template.md).
5. **User Confirmation:** Ask confirmation only for entries that affect future judgment.
6. **Formal Entry:** After confirmation, write confirmed items using [references/formal-entry-templates.md](references/formal-entry-templates.md).
7. **Approved Asset Library:** If a final website visual is confirmed as `approved`, run the approved-library rules below.
8. **Verification:** Verify paths, claim safety, status labels, and destination.

## Destinations

```text
product facts and claim boundaries -> brand-system/01-product-facts/
visual standards and design rules -> brand-system/02-brand-visual/
page strategy lessons -> brand-system/03-page-strategy/
image failure cases -> brand-system/04-image-failures/
approved or source materials -> brand-system/05-approved-materials/
competitor references -> brand-system/06-competitor-references/
unconfirmed candidates -> brand-system/90-inbox/
daily curation summary -> brand-system/91-daily-curation-log/
```

## Approved Asset Library

Only user-confirmed `approved` final visuals enter the centralized asset library. Do not copy `source-only`, `partial-reference`, `process-only`, `candidate`, `rejected`, failure cases, or pure reference images.

When a final website visual is confirmed as `approved`:

1. Keep the original task folder unchanged for reproduction and audit context.
2. Copy the reusable final image into the matching library folder:

```text
_approved-library/backgrounds/
_approved-library/hero/
_approved-library/product/
_approved-library/modules/
```

3. Generate a small preview under:

```text
_approved-library/thumbnails/
```

4. Update:

```text
_approved-library/asset-library-index.md
```

Each index entry must include asset ID, status `approved`, asset type, library path, original source path, reproduction document path when available, approved use, prohibited use or limitations, confirmation date, and user confirmation note.

Use stable semantic filenames, for example:

```text
b2-3-natural-leaf-vein-background-approved-4k-01.png
```

## Naming Rules

Use semantic filenames, not date-first filenames:

```text
page-module-topic-status-dNN.md
```

Examples:

```text
home-hero-左右分割-失败-d01.md
home-hero-HUD面板感-失败-d01.md
home-hero-屋顶HVAC场景-成功参考-d01.md
product-page-参数暗示风险-禁用claim-d01.md
oj-product-page-页面结构-竞品参考-d01.md
```

Put date, source task, and original paths inside the file body.

## Status Labels

Use only:

```text
inbox
candidate
approved
rejected
source-only
partial-reference
process-only
risk-material
archived
```

## Hard Stops

Stop and ask for confirmation before formal entry when:

- a visual is being promoted to `approved`
- a failure case will become a future hard negative reference
- material implies product structure, application, certification, performance, customer case, export market, patent, compliance, or verified specification
- a competitor reference could be mistaken for a Jiangyue-owned rule
- the source path is missing or user feedback is ambiguous
