---
name: jiangyue-knowledge-curator
description: Use when curating Jiangyue Technology website project knowledge after image generation, page planning, competitor research, product-fact review, or repeated visual failures. Collect task outputs, README/REPRODUCTION notes, user feedback, approved materials, failure cases, source materials, product fact boundaries, visual standards, page-strategy lessons, and competitor references into the local brand-system knowledge base with semi-automatic classification and user confirmation before formal entry.
---

# Jiangyue Knowledge Curator

## Core Role

Maintain Jiangyue Technology's local website knowledge base. Curate evidence from completed work into reusable project memory so `$jiangyue-website-planner` and `$jiangyue-website-imagegen` can later rely on confirmed facts, visual standards, approved materials, failure cases, and competitor references.

Do not generate images, approve final visuals, write final page strategy, or replace the user's judgment. This skill prepares curation cards and writes formal entries only after the user confirms what should enter the formal knowledge base.

## Source And Destination

Default knowledge root:

```text
/Users/lirongjing/Documents/JY TECH WEB/brand-system/
```

Common source locations:

```text
/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images/
/Users/lirongjing/Documents/JY TECH WEB/website-content-brand-plan/
/Users/lirongjing/Documents/JY TECH WEB/市场调研/
```

Formal knowledge files live under `brand-system/01-*` through `brand-system/06-*`. Inbox and daily logs are not formal authority.

## Curation Model

Use a semi-automatic workflow:

```text
collect evidence -> classify -> produce curation card -> ask for user confirmation -> write formal entries -> verify paths and claims
```

Never move a material directly from task output into `approved` status without user confirmation.

## Workflow

1. **Intent Lock**
   Identify whether the user wants daily curation, single-task recap, failure-case capture, approved-material indexing, competitor-reference capture, product-fact boundary update, or inbox cleanup.

2. **Evidence Capture**
   Read relevant README, REPRODUCTION, review images, source paths, user feedback, and competitor notes. When visual quality is being judged, inspect the image or state clearly that visual inspection was not performed.

3. **Classification**
   Classify each item using [references/material-classification.md](references/material-classification.md). Default ordinary intermediate drafts to `process-only`.

4. **Curation Card**
   Produce a short confirmation card instead of asking the user to review every image. Use [references/curation-card-template.md](references/curation-card-template.md).

5. **User Confirmation**
   Ask the user to confirm only entries that affect future judgment: success references, failure cases, reusable source materials, product fact boundaries, and competitor references.

6. **Formal Entry**
   After confirmation, write only the confirmed items into the matching `brand-system` file. Use [references/formal-entry-templates.md](references/formal-entry-templates.md).

7. **Verification**
   Verify that file paths exist, claims are not invented, status labels are clear, and inbox material is not presented as formal authority.

## Brand-System Write Rules

Use these destinations:

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

Do not let `$jiangyue-website-planner` or `$jiangyue-website-imagegen` treat `90-inbox/` as formal evidence.

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

Use only these status labels unless the user asks for a new one:

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
- a material implies product structure, application, certification, performance, customer case, export market, patent, compliance, or verified specification
- a competitor reference could be mistaken for a Jiangyue-owned design rule
- the source path is missing or the user feedback is ambiguous
