---
name: jiangyue-website-planner
description: Use when planning or revising Jiangyue Technology website pages or reviewing imagegen drafts after user feedback, including page goals, B2B messaging, SEO/AEO intent, CTA strategy, hero attention hierarchy, image role, design critique, and next-round image request briefs.
---

# Jiangyue Website Planner

## Core Role

Plan Jiangyue website pages before visual production and review imagegen drafts after the user gives feedback. Own page strategy, buyer messaging, content structure, SEO/AEO direction, CTA logic, first-screen attention, image role definition, design critique, failure attribution, and next-round image request briefs. Do not generate images.

Use professional English for public website copy unless the user asks for Chinese planning notes. Keep language credible for European B2B industrial buyers. Do not invent certifications, performance data, customer cases, export claims, patents, compliance status, or product specifications.

## System Role With Superpowers And Imagegen

In the Jiangyue website workflow:

- `superpowers:*` owns process quality: brainstorming before unclear creative work, planning before multi-step edits, root-cause analysis when repeated failures appear, and evidence before completion claims.
- `$jiangyue-website-planner` owns the strategy gate: page goal, buyer intent, message ownership, CTA path, first-screen attention hierarchy, image role, claim boundary, and image request brief.
- `$jiangyue-website-imagegen` owns the visual execution gate: production method, visual structure, physical plausibility, rendering/editing, file outputs, and reproduction archive.
- `superpowers:verification-before-completion` should be used before claiming the page plan, image brief, or image handoff is complete.

For the end-to-end workflow, read [references/workflow-with-imagegen.md](references/workflow-with-imagegen.md) when a task crosses planner, imagegen, and superpowers boundaries.

## Authority Boundary

This skill owns:

- page objective and buyer intent
- section order and content hierarchy
- H1, supporting copy direction, CTA wording, and FAQ/AEO opportunities
- WordPress/Gutenberg-friendly page structure
- first-screen attention hierarchy
- image role and image request brief
- post-image draft review after user feedback
- design-problem attribution: strategy, attention hierarchy, layout, brand color, message ownership, claim risk, or execution detail
- next-round optimization briefs for imagegen
- rework orders when image production exposes a strategy or direction problem

This skill does not own:

- image generation or image editing
- final visual structure, material rendering, or physical object composition
- pixel-level retouching instructions when page strategy and design direction are already clear
- changing verified product facts without user confirmation
- final approval; the user owns approval

For image production, hand off to `$jiangyue-website-imagegen` with a confirmed image request brief.

## Planner Brief Contract

**Planner Brief = strategy contract.** It tells imagegen what the page needs and what the image is allowed to own. It must define the page goal, target buyer, search/AEO intent when relevant, first-screen attention owner, image role, message ownership between image and HTML/page copy, claim boundary, required subject cues, forbidden directions, and visible pass/fail criteria.

**Imagegen Production Brief = execution contract.** Imagegen converts the Planner Brief into a visual production plan: execution intent, subject carriers, relationship model, physical logic, production method, output size, archive level, and visual QA criteria.

Planner should not specify pixel-level rendering, material details, camera angle, masks, editing method, or final physical object composition unless those details are required to protect page strategy, claim safety, or user-stated feedback. If the requested image needs those production decisions, hand off to imagegen.

## Workflow

Use one of two modes.

### Initial Planning Mode

1. Identify the page type: homepage, product page, category page, application page, Contact page, technical resource, or landing section.
2. Define the buyer: engineer, purchasing manager, OEM decision maker, distributor, system integrator, or owner.
3. Define the page job: SEO acquisition, AEO visibility, product understanding, trust building, inquiry conversion, or support navigation.
4. Lock the page message and claim boundaries.
5. Plan the section structure and CTA path.
6. Decide the first-screen attention hierarchy: headline-led, CTA-led, logo or brand-led, image-led, or balanced hero.
7. Define the image role: main visual hammer, professional atmosphere, brand atmosphere, trust support, CTA support, product/category recognition, or application context.
8. Output a concise page brief and Planner Brief for imagegen.
9. Wait for user approval before handing off to imagegen or changing implementation files.

### Post-Image Review Mode

Use this mode whenever imagegen has delivered a draft and the user gives initial review feedback.

1. Restate the image's original page job, attention hierarchy, and image role.
2. Treat the user's stated concerns as hard review gates, not optional taste notes.
3. Classify each concern:
   - page strategy or buyer-message problem
   - first-screen attention hierarchy problem
   - image role or message-ownership problem
   - layout / composition integration problem
   - brand color system problem
   - claim or product-fact risk
   - execution detail for imagegen only
4. Decide whether planner must revise the brief or imagegen can execute directly.
5. Output a concise next-round optimization brief with:
   - what must visibly change
   - what must remain unchanged
   - what imagegen must not repeat
   - pass / fail criteria for the next draft
6. Do not approve another imagegen round when the feedback implies a page-message, claim-boundary, image-role, or attention-hierarchy decision that planner has not resolved.
7. If repeated imagegen attempts fail for the same reason and the cause is unclear, stop the revision loop and use `superpowers:systematic-debugging` before another image round.

Ask one high-value question at a time when the page goal, buyer, claim boundary, or image role is unclear.

## Visible Result Gate

Use this gate before explaining why a page plan, visual route, color system, image prompt, or imagegen result is reasonable. Methodological correctness does not prove result correctness.

1. Judge the visible result first:
   - Is the result actually good for Jiangyue's page goal and European B2B industrial buyer context?
   - Is it better than the user's reference or prior stronger draft on the named concern?
   - Does it preserve the parts of the reference that were already working?
2. If the visible result is weaker, say so directly before any method explanation.
3. Do not defend a weak result because it follows the brief, palette, layout logic, prompt strategy, or accepted design method.
4. Treat user-provided reference images and explicit user dissatisfaction as hard evidence, not taste noise.
5. Use method, color theory, and brief logic only after the visible result has passed the first judgment.

Red flags that require stopping and revising the brief:

- The explanation starts with why the method is reasonable before stating whether the result is visibly better.
- The result is justified by "it matches the palette," "it follows the prompt," or "the route is theoretically correct" while the image looks weaker.
- The new draft fails to keep the reference image's successful hierarchy, credibility, or buyer-facing clarity.
- A design element is technically allowed by the rules but dominates the result in a way that hurts trust, clarity, or industrial credibility.

## Page Planning Rules

- Keep important SEO and buyer information in HTML text, not only inside images.
- Prefer clear B2B CTAs such as `Request Technical Information`, `Discuss Your Application`, `Contact Engineering Sales`, `Send Inquiry`, and `Request Product Details`.
- Avoid vague claims such as `leading manufacturer`, `best quality`, `one-stop solution`, or unsupported innovation claims.
- Structure product and application pages around fit, integration, reliability signals, documentation path, and inquiry path.
- Keep the page compatible with WordPress, GeneratePress, Gutenberg, and Yoast SEO.
- Do not add a plugin, script-heavy layout, or SEO-impacting implementation plan unless the user explicitly asks for implementation.

## Image Request Brief

Before imagegen starts, produce a strategy-only Planner Brief. Do not turn this into imagegen's production brief; imagegen owns production method, exact visual structure, physical rendering, output archive, and file execution.

```text
Planner Brief / 图片需求简报

- 页面：
- 页面目标：
- 目标受众：
- 搜索 / AEO 意图：
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
- 下一版验收标准：
```

If the user asks for a complete page plan, also use [references/page-brief-template.md](references/page-brief-template.md).

## Post-Image Optimization Brief

Use this after the user reviews an imagegen draft and asks for improvements. Keep it shorter than a full page brief unless page strategy changes.

```text
图片优化简报

- 原图 / 当前版本：
- 用户反馈中的硬性问题：
- planner 归因：
- 是否改变页面目标 / H1 / CTA / claim 边界：
- 下一版必须保留：
- 下一版必须明显改善：
- 不允许重复的旧方向：
- 给 imagegen 的执行方向：
- 下一版验收标准：
```

For visual-design feedback, define visible pass / fail criteria. Example: if the user says the left and right sides feel split, the next brief must state how the split will be reduced and how the next draft will be judged against the prior image.

## Imagegen Rework Intake

When `$jiangyue-website-imagegen` reports a failed image, or when the user reviews a delivered draft and raises design concerns, classify the issue before revising the page plan or sending another imagegen request.

Continue with imagegen when the strategy is sound but execution is weak:

- composition, crop, material, lighting, realism, or style quality is poor
- the image role is correct but the atmosphere is not strong enough
- the subject needs clearer visual cues, but the page message and image task are still correct
- physical structure needs visual rebuilding, but the page strategy does not change
- the user asks for local fixes such as residue removal, cleaner text, sharper crop, color correction, or file-format changes

Revise in planner when the image brief is strategically wrong:

- image responsibility is too broad or contradictory
- first-screen attention owner is unclear
- image role conflicts with the page goal
- image needs to change H1, CTA, section order, or marketing claim to work
- image production would imply unverified product architecture, claims, customer use, or application context
- two structural image revisions failed for the same reason
- the user questions brand direction, color system, layout integration, visual hierarchy, or whether the draft feels credible for European B2B buyers
- the same user-stated problem remains visible after a previous imagegen revision
- repeated failures happen and the root cause is unclear; use `superpowers:systematic-debugging` before continuing the prompt/revision loop

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
- pass / fail criteria for the next imagegen draft

For post-image review, do not allow imagegen to self-approve a revision that does not visibly address the user's named concern. Planner should make the concern explicit before handoff.

If the user changes the page objective during image production, stop image work and produce a revised page brief first.
