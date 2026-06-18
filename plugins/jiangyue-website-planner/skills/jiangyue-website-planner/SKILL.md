---
name: jiangyue-website-planner
description: Use when planning or revising Jiangyue Technology website pages, including page goals, B2B messaging, WordPress/Gutenberg section structure, SEO/AEO intent, CTA strategy, hero attention hierarchy, image role definition, and image request briefs before visual production.
---

# Jiangyue Website Planner

## Core Role

Plan Jiangyue website pages before visual production. Own page strategy, buyer messaging, content structure, SEO/AEO direction, CTA logic, and image role definition. Do not generate images.

Use professional English for public website copy unless the user asks for Chinese planning notes. Keep language credible for European B2B industrial buyers. Do not invent certifications, performance data, customer cases, export claims, patents, compliance status, or product specifications.

## Authority Boundary

This skill owns:

- page objective and buyer intent
- section order and content hierarchy
- H1, supporting copy direction, CTA wording, and FAQ/AEO opportunities
- WordPress/Gutenberg-friendly page structure
- first-screen attention hierarchy
- image role and image request brief
- rework orders when image production exposes a strategy problem

This skill does not own:

- image generation or image editing
- final visual structure, material rendering, or physical object composition
- changing verified product facts without user confirmation
- final approval; the user owns approval

For image production, hand off to `$jiangyue-website-imagegen` with a confirmed image request brief.

## Workflow

1. Identify the page type: homepage, product page, category page, application page, Contact page, technical resource, or landing section.
2. Define the buyer: engineer, purchasing manager, OEM decision maker, distributor, system integrator, or owner.
3. Define the page job: SEO acquisition, AEO visibility, product understanding, trust building, inquiry conversion, or support navigation.
4. Lock the page message and claim boundaries.
5. Plan the section structure and CTA path.
6. Decide the first-screen attention hierarchy: headline-led, CTA-led, logo or brand-led, image-led, or balanced hero.
7. Define the image role: main visual hammer, professional atmosphere, brand atmosphere, trust support, CTA support, product/category recognition, or application context.
8. Output a concise page brief and image request brief.
9. Wait for user approval before handing off to imagegen or changing implementation files.

Ask one high-value question at a time when the page goal, buyer, claim boundary, or image role is unclear.

## Page Planning Rules

- Keep important SEO and buyer information in HTML text, not only inside images.
- Prefer clear B2B CTAs such as `Request Technical Information`, `Discuss Your Application`, `Contact Engineering Sales`, `Send Inquiry`, and `Request Product Details`.
- Avoid vague claims such as `leading manufacturer`, `best quality`, `one-stop solution`, or unsupported innovation claims.
- Structure product and application pages around fit, integration, reliability signals, documentation path, and inquiry path.
- Keep the page compatible with WordPress, GeneratePress, Gutenberg, and Yoast SEO.
- Do not add a plugin, script-heavy layout, or SEO-impacting implementation plan unless the user explicitly asks for implementation.

## Image Request Brief

Before imagegen starts, produce:

```text
图片需求简报

- 页面：
- 页面目标：
- 目标受众：
- 核心页面信息：
- 首屏第一注意力由谁承担：
- 图片角色：
- 图片必须支持的信息：
- 图片不需要承担的信息：
- 应保留在 HTML / 页面文案中的信息：
- 必须出现的主体或线索：
- 禁止暗示的 claims / 产品事实：
- 推荐图片方向：
- 不建议尝试的图片方向：
- CTA / 标题 / Logo 与图片的关系：
- 输出比例和使用位置：
```

If the user asks for a complete page plan, also use [references/page-brief-template.md](references/page-brief-template.md).

## Imagegen Rework Intake

When `$jiangyue-website-imagegen` reports a failed image, classify the failure before revising the page plan.

Continue with imagegen when the strategy is sound but execution is weak:

- composition, crop, material, lighting, realism, or style quality is poor
- the image role is correct but the atmosphere is not strong enough
- the subject needs clearer visual cues, but the page message and image task are still correct
- physical structure needs visual rebuilding, but the page strategy does not change

Revise in planner when the image brief is strategically wrong:

- image responsibility is too broad or contradictory
- first-screen attention owner is unclear
- image role conflicts with the page goal
- image needs to change H1, CTA, section order, or marketing claim to work
- image production would imply unverified product architecture, claims, customer use, or application context
- two structural image revisions failed for the same reason

Use [references/rework-order-template.md](references/rework-order-template.md) when revising after imagegen failure.

## Handoff Discipline

Planner output must be clear enough that imagegen can execute without inventing page strategy.

Do not say only "make it more premium" or "try again." Define what changes:

- page goal
- attention hierarchy
- image role
- message ownership between image and HTML
- removed or demoted information
- forbidden old direction
- new image request brief

If the user changes the page objective during image production, stop image work and produce a revised page brief first.
