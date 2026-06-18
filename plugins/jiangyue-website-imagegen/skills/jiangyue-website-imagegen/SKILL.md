---
name: jiangyue-website-imagegen
description: Use when creating, editing, or reviewing website visuals for Jiangyue Technology, including Chinese or English page graphics, industrial product imagery, AI-assisted motor-control concepts, application scenes, technical-resource images, card graphics, hero images, and WordPress-ready visual assets.
---

# Jiangyue Website Imagegen

## Core Standard

Create industrial B2B visuals that support technical credibility while leaving room for real creative range. Every hero or page asset needs a clear attention hierarchy and image role; the image may be the visual hammer, or it may support a headline, CTA, logo, or brand atmosphere. Avoid unsupported product, certification, customer, or performance claims.

Treat brand guidance as a floor, not a cage: the image may be inventive in composition, crop, material, space, and metaphor as long as it remains credible for motor-control, industrial OEM, and the current target application context. Fan, HVAC, ventilation, pump, and similar fields are examples to use only when relevant to the page or user brief.

Use the shortest production path that preserves quality. Do not create an HTML preview, browser mockup, design document, competitor review, or multiple deliverables unless the user asks for them or they are necessary to judge the requested asset.

For page strategy, copy structure, CTA logic, SEO/AEO direction, or first-screen planning, use `$jiangyue-website-planner` first. This skill may consume a planner image request brief, but it must not silently change page strategy, marketing claims, CTA hierarchy, or section order.

## Brief Intake

For every new image, use [references/image-brief-template.md](references/image-brief-template.md).

- Do not dump the full questionnaire on the user.
- Ask only the highest-value missing question, one at a time.
- Infer low-risk production details from the brand rules and existing assets.
- For high-impact, abstract, multi-subject, or physically metaphorical visuals, read [references/visual-structure-patterns.md](references/visual-structure-patterns.md) before selecting the visual structure.
- For standard or high-impact briefs, read [references/brief-review-rubric.md](references/brief-review-rubric.md) and score the brief before asking for confirmation.
- Before showing the production brief to the user, run the brief self-review and physical plausibility gates. If either fails, revise the concept or ask one more question instead of asking for confirmation.
- Before production, return a concise production brief that states the original intent, intended message, subject relationship, physical logic, attention hierarchy, image role, copy placement, method, and constraints.
- Generate only after the user confirms the brief or has already provided equivalent clear instructions.

## Intent Lock

Create an intent lock before choosing the visual form. Keep it active through every revision.

The intent lock must state:

- the user's original job for the image
- the core message the image must support
- what the image itself must communicate without relying on explanation
- what will be carried by HTML/page copy instead of the image
- the drift boundaries: what the image must not become

Do not replace the original intent with a later production detail. If the user asks for a correction that may change the intent, stop and restate the trade-off before producing anything.

Example:

- Original intent: Contact hero visual supporting "AI + professional + service".
- Allowed correction: make the subject more industrial and credible.
- Drift boundary: do not turn the image into a standalone product hero where the three-part advantage disappears.

## Choose the Production Method First

Classify the request before generating anything:

| Request | Default method |
|---|---|
| Product, application, lab, equipment, or atmospheric scene | Use image generation |
| Simple geometric card, icon-like graphic, diagram, label system, or text-led composition | Build as SVG/canvas and export PNG |
| Existing raster image modification | Use image editing |
| Visible Chinese or English copy in a graphic | Generate the visual base without text, then typeset real text programmatically |
| Website implementation or responsive page testing | Use HTML/CSS only when explicitly requested |

Do not use an image model for deterministic geometry or important text when SVG/canvas can produce a cleaner and more controllable result.

When repeatability or later editing matters, prefer a deterministic or hybrid method:

- Use SVG/canvas/Python composition for typography, layout, crops, masks, color variants, and overlays.
- Use image generation only for the non-deterministic visual base when needed.
- Preserve the generated base image and put all repeatable edits in source files or scripts so future changes can run locally with low token use.
- Do not promise exact pixel-identical regeneration from a fresh AI image prompt unless a stable seed, model version, inputs, and generation tool behavior are available and verified. Exact regeneration is expected only for deterministic pipelines using saved source assets.

## Fast Workflow

1. Identify the asset type, crop, purpose, attention owner, image role, and required text.
2. Create the intent lock. Do not continue if the image responsibility and page-copy responsibility are unclear.
3. When the brief contains multiple subjects, confirm their semantic relationship before choosing a visual form.
4. Run a content-sufficiency check before choosing a layout.
5. For any product, equipment, application, lab, hardware, enclosure, PCB, signal-flow, or physical-metaphor visual, run the physical plausibility gate before writing the brief.
6. Decide whether reference research is needed. For brand-defining hero images, motor-control or application-category subject recognition, vague "premium/beautiful/industrial" requests, or failed visual quality, use the reference research gate.
7. Choose a reliable visual structure before choosing rendering style. For high-impact, abstract, multi-subject, or physically metaphorical visuals, use a structure written as relationship model + variable parameters + forbidden boundaries.
8. For a brand-defining hero or ambiguous abstract concept, use the high-impact dual path: offer 2-3 materially different structure directions before production unless the user has already approved a clear structure.
9. Choose a concrete visual concept and state why it preserves the intent lock.
10. Run the brief self-review and brief scoring gates. Do not show the brief for user confirmation if the concept only works by explanation, has weak attention hierarchy, has weak visual design, or fails physical plausibility.
11. Check only directly relevant project assets.
12. Choose image generation, image editing, or deterministic SVG/canvas composition.
13. Create a dedicated task output folder before producing files.
14. Produce one strong draft first. Create variants only when they test a meaningful visual difference.
15. Maintain a reproduction archive for the task and update it after each accepted draft or meaningful revision.
16. Inspect the actual output at full size and thumbnail size using a separate review pass.
17. For revisions, compare the new draft side-by-side against the prior draft or reference. Single-image review is not enough.
18. Treat every user-named defect as a hard regression gate. If the user asked to fix left-right separation, weak brand-color connection, text crowding, product recognition, or similar, the review must explicitly answer whether that defect is visibly improved. If not, reject the draft.
19. If the output fails, run the failure attribution gate before revising.
20. Continue imagegen only for execution failures. Return to planner when the image request brief is strategically wrong.
21. Reject and redo any output that fails intent fidelity, physical plausibility, user-stated regression gates, hits a quality veto, or triggers a design-upgrade rule.
22. Save the accepted asset in the task folder and report its path, dimensions, method, reproduction archive path, and unverified limitations.

For a clear simple request, do not conduct an extended questionnaire. Infer low-risk details, return the concise production brief, and proceed after confirmation. If meaning or subject relationships remain ambiguous, wait for the answer.

## Task Folder And Reproduction Archive

Every imagegen task must create versioned folders under the project outputs area. Organize first by page or content type, then by dated draft/final folders.

```text
outputs/jiangyue-website-images/{content-type}/{YYYY-MM-DD-short-topic-draft-01}/
outputs/jiangyue-website-images/{content-type}/{YYYY-MM-DD-short-topic-draft-02}/
outputs/jiangyue-website-images/{content-type}/{YYYY-MM-DD-short-topic-final}/
```

Recommended first-level content folders:

- `home/`
- `product/`
- `application/`
- `about-us/`
- `contact/`
- `technical-resources/`
- `brand/`
- `shared/`

Examples:

- `outputs/jiangyue-website-images/home/2026-06-18-pmsm-drive-hero-draft-01/`
- `outputs/jiangyue-website-images/home/2026-06-18-pmsm-drive-hero-draft-02/`
- `outputs/jiangyue-website-images/home/2026-06-18-pmsm-drive-hero-final/`
- `outputs/jiangyue-website-images/contact/2026-06-18-ai-service-hero-draft-01/`

Each draft or final folder is a self-contained production record. Put that version's image files, source assets, scripts, and reproduction archive inside the version folder. Do not scatter new task outputs directly into the shared output root unless the user explicitly asks.

When several drafts belong to the same asset, use the same `{YYYY-MM-DD-short-topic}` prefix and increment `draft-01`, `draft-02`, `draft-03` until the accepted version becomes `final`. If a later revision happens after final approval, start a new dated folder such as `2026-06-25-pmsm-drive-hero-revision-01`.

Required files inside each draft/final folder when applicable:

- `README.md` or `REPRODUCTION.md`: the human-readable reproduction archive
- `recipe.json`: compact machine-readable parameters for fast reuse when practical
- `source/`: source images, generated bases, references, masks, SVGs, or editable assets
- `scripts/`: deterministic scripts used to rebuild the image
- `output/`: PNG/JPG/WebP outputs for this draft/final version
- `review/`: optional comparison images or thumbnails used for verification

The reproduction archive must let a future agent modify the image quickly without re-reading the whole conversation. It must record:

- original task and intent lock
- final file paths and dimensions
- source inputs with relative paths
- production method: deterministic, AI-generated, image-edit, or hybrid
- exact public-facing text, fonts, colors, crop boxes, masks, layout constants, and export settings
- prompts, negative prompts, reference images, model/tool names, seed or generation ID if available
- commands to rebuild deterministic outputs locally
- revision history with what changed and why
- known non-reproducible parts and how to regenerate only those parts if needed

Efficiency rule:

- The archive should point to scripts and compact parameters instead of restating long prompts repeatedly.
- Future small edits should change `recipe.json`, an SVG, or a short script parameter, then rerun locally.
- Do not force a new AI generation round for typography, color variants, cropping, masks, composition overlays, or copy changes that can be handled deterministically.
- If the asset depends on an AI-generated base, preserve that base image and make later edits on top of it whenever possible.

Use [references/reproduction-archive-template.md](references/reproduction-archive-template.md) for the recommended archive structure.

## Mixed-Autonomy Design Mode

Use mixed autonomy by default:

- Adjust composition, spacing, scale, crop, asymmetry, material, color balance, abstract lines, and non-semantic brand accents without asking.
- Ask one concise, highest-value question before adding new copy, products, application objects, people, technical symbols, or claim-like meaning.
- When the requested content is too thin for a strong composition, do not hide the weakness with decoration. Propose a specific content addition or structural change.
- If the user declines additional content, solve the asset through proportion, typography, negative space, material contrast, cropping, or a stronger silhouette.
- Ask one question at a time. Explain what visual problem the answer will solve.

Read [references/design-upgrade.md](references/design-upgrade.md) when the asset is based on one simple element, feels visually thin, needs active art direction, or fails the first review.

## Multi-Subject Relationship Gate

Before designing two or more named subjects, determine:

1. **Foundation:** what provides credibility, stability, or input?
2. **Driver:** what creates movement, transformation, or differentiation?
3. **Outcome:** what delivers value, continuation, or closure?
4. **Flow:** what moves between them, in what direction, and whether it returns as a loop?

If the brief does not answer these questions, ask one question first:

> What is the most important relationship or result this image should show?

Offer 2–3 concrete relationship models when useful. Do not begin production until the user chooses or clearly describes the intended relationship.

Do not treat proximity, interlocking geometry, equal-size labels, or a connecting line as proof of collaboration. The visual must show role, direction, and result.

For every named subject, map it to either:

- an explicit image element
- an implicit visual cue
- page copy outside the image

If a named subject has no carrier, the concept is incomplete. Ask one question or revise the brief before production.

## Content-Sufficiency Check

Before production, classify the brief:

- **Sufficient:** clear subject, hierarchy, purpose, and crop. Proceed.
- **Thin but solvable:** few elements, but typography, silhouette, scale, or material can carry the design. Proceed with an intentional minimal composition.
- **Semantically incomplete:** a stronger design requires meaning not supplied by the user. Ask one question before adding it.
- **Overloaded:** too many equal messages or subjects. Recommend what to remove or subordinate before producing.

Minimal does not mean placing a small object in empty space. A minimal asset still needs deliberate scale, tension, rhythm, and hierarchy.

## Concept Fidelity Gate

Before generation, write a one-sentence concept contract:

> This image will show [visual subject] so that [viewer understands/feels X], while [specific message Y] remains carried by [image/page copy].

Reject the concept before production if any of these are true:

- the visual subject is only adjacent to the user's core message
- the chosen subject can replace or hide one of the user's named priorities
- the image would still make sense if the user's company, product category, or message were removed
- the concept depends on an explanation that is not visible in the image or planned HTML copy
- a later requested correction makes the image solve a different job than the original request

## Physical Plausibility Gate

Use this gate before showing the production brief when the image includes real-world objects, industrial equipment, electronics, enclosures, application scenes, energy/signal paths, or physical metaphors.

Reject or revise the concept before user confirmation if any of these are true:

- the object could not be plausibly manufactured, mounted, assembled, wired, enclosed, supported, or handled
- a base, frame, shell, cover, PCB, chip, heat sink, connector, fan, pump, cable, or fixture appears mechanically unrelated to the other parts
- transparent parts lack practical thickness, edges, fastening, clearance, or enclosure logic
- a partial shell, floating frame, decorative cage, unsupported platform, or arbitrary metal base is used only to symbolize an idea
- blue/green light paths look like impossible electricity or energy flowing outside the device
- "service", "AI", or "engineering" is carried by a generic icon, decorative glow, or forced object instead of a physically meaningful layer or relationship

Default terms:

- Use **control signal**, **data path**, **feedback path**, or **support layer** for abstract flows.
- Do not use **energy flow** unless the image explicitly shows a believable power source, load, wiring path, and safety boundary.

For conceptual electronics and controller visuals, prefer physically coherent layers: board or engineered base, control chip/module, thermal path, connectors, enclosure/cover, fasteners, and restrained signal cues. Keep the result conceptual, but do not ask the image model to invent impossible industrial design.

## Brief Self-Review Gate

Run this gate before returning the production brief for confirmation.

First answer:

1. Does the brief preserve the original intent lock?
2. Does every named subject have a visible carrier or a planned HTML/page-copy carrier?
3. Is the attention hierarchy clear enough to guide image generation or page composition?
4. Does the physical structure or metaphor pass the physical plausibility gate?
5. Can the relationship be understood from the planned image, not only from the explanation?

Then check for risks:

- **Visual weakness:** safe but dull, generic, template-like, or no memorable hierarchy, atmosphere, silhouette, crop, or material decision
- **Physical mismatch:** parts look forced together, decorative, unsupported, unmanufacturable, or mechanically unrelated
- **Claim risk:** fake specs, certifications, product architecture, interfaces, customer use, or performance may appear
- **Text risk:** the image model might generate important text, labels, UI values, PCB marks, or nameplates
- **Template risk:** three cards, equal icons, badges, hexagons, generic AI nodes, or stock infographic layout
- **User-defect risk:** the production plan does not name how it will fix the user's stated defect, or it only changes color, opacity, glow, blur, or gradient while leaving the same failing composition

If any answer fails or any risk remains high, revise the brief structurally or ask one focused question. Do not proceed by saying "we will fix it after the draft." A weak brief produces weak images.

For standard or high-impact briefs, score the brief using [references/brief-review-rubric.md](references/brief-review-rubric.md). Intent fidelity, carrier completeness, relationship readability, physical plausibility, and attention hierarchy must all score at least 4 before user confirmation.

## Reference Research Gate

For high-impact hero images, abstract concepts, weak visual direction, motor-control or application-category recognition, or any draft rejected for visual quality, consider reference research before production or revision.

Use [references/reference-research.md](references/reference-research.md) when reference research is needed. Keep this gate conditional: do not search by default for simple cards, deterministic diagrams, text-led graphics, format conversion, or minor image edits.

Reference research must return executable visual principles, not a list of links to copy. Original intent lock overrides every reference.

## Complexity Budget

Use the lightest process that can protect the result:

- **Light path:** clear simple assets. Use intake, brief, production, and review only.
- **Standard path:** most website visuals. Add intent lock, subject carriers, concept fidelity, and brief scoring.
- **High-impact path:** homepage, Contact hero, product hero, abstract advantage visuals, recognition-sensitive assets, or repeated failure. Add the high-impact dual path, reliable visual structure selection, reference research when needed, and stronger design-upgrade review.

Do not load every reference file or run web research just because it exists. More process is only justified when it reduces drift, improves subject recognition, or raises visual quality.

Reliable visual structures are not templates. Use [references/visual-structure-patterns.md](references/visual-structure-patterns.md) to choose a relationship model, vary parameters, and set forbidden boundaries. If a reliable structure becomes visually plain, change crop, scale, silhouette, material, medium, or relationship model rather than adding decoration.

## Brand Floor and Creative Range

The required brand floor:

- calm, precise, credible, modern, technical
- suitable for European B2B industrial buyers, OEMs, product teams, purchasing, and engineering roles
- connected to motor control, industrial control, OEM equipment, or the specific application category when relevant
- restrained enough to feel engineered rather than theatrical

The creative range:

- Use stronger crops, asymmetry, depth, unusual product angles, abstract control layers, application-context fragments, or physical material contrast when they improve meaning.
- Let the image feel designed, not merely safe. A clean but lifeless image is not acceptable for a hero asset.
- AI may be shown through control behavior, feedback, sensing, adaptive flow, or decision layers; do not default to generic glowing nodes and data lines.
- "Professional" may be shown through precision, assembly logic, material credibility, cooling rhythm, test-bench discipline, documentation adjacency, or clear system architecture.
- "Service" may be shown through continuity, accessible support path, feedback loop, maintenance touchpoint, or responsive handoff; do not reduce it to a decorative ring.

Use color as a role system, not a fixed recipe:

- **Base:** white, light gray, graphite, metal gray, controlled shadow.
- **Technical signal:** restrained blue, cyan, or green for control, data, efficiency, or feedback.
- **Application warmth:** small warm or environmental accents when they prevent a cold sterile look.
- Avoid large neon-purple fields, dark cyberpunk palettes, cheap gradients, rainbow tech effects, and excessive glow.

Suggested colors may include `#FFFFFF`, `#F7F9FC`, `#E9EEF4`, `#0F172A`, `#147DFF`, `#18C7D8`, `#61D345`, plus restrained metal or application-context neutrals.

Industrial technology should feel engineered, not theatrical.

## Attention Hierarchy And Image Role

Decide the page-level attention hierarchy before deciding whether the image needs a strong visual hammer.

First identify the attention owner:

- **Image-led:** the image is the primary visual hammer. Use one focal object, compact system symbol, or clear relationship that is noticed first.
- **Headline-led:** the H1 or value proposition owns first attention. The image supports meaning through atmosphere, precision, depth, or subject recognition without competing.
- **CTA-led:** the action path is primary. The image should increase trust and reduce friction, not overpower the CTA.
- **Logo or brand-led:** brand recognition owns first attention. The image builds professional mood, technical credibility, and brand world.
- **Balanced hero:** image, headline, CTA, and logo share the first screen. Use controlled hierarchy so no secondary decoration steals attention.

When the image is not the primary attention owner, do not force a strong image visual hammer. Instead, design for:

- professional atmosphere
- brand mood
- technical credibility
- product or category recognition
- trust support for inquiry or CTA
- clean negative space for headline and actions

When the image is the primary visual hammer, use one focal object or one tightly unified object group. When several subjects jointly form the hammer, their silhouette must read as one compact symbol. Secondary lines, grids, glows, labels, icons, and scenery must remain weaker.

For multiple subjects, make the relationship visible. It may be the visual hammer, or it may be a quieter support structure when headline, CTA, or brand owns attention.

## Text and Chinese Typography

- Use exact user-provided wording.
- Typeset important text with a real installed font.
- Keep text editable in the SVG source when practical.
- Prefer clean sans-serif Chinese fonts such as PingFang SC, Source Han Sans, Noto Sans CJK, or Heiti.
- Avoid bevelled 3D lettering, excessive shadows, outlined display type, or model-generated text.
- Never add unrequested slogans, English labels, numbers, or microcopy.

For WordPress, important SEO copy should remain HTML. Text inside an image is acceptable only when the image itself is a labeled graphic and the same meaning is available in page content or alt text.

## Quality Vetoes

Reject the draft immediately if any of these appear:

- generic honeycomb or hexagon infographic
- glowing pipes, excessive circuitry, or transparent sci-fi tubing
- PowerPoint template, stock-vector, dashboard, or app-button appearance
- generic rounded pills used as the main visual idea
- dark cyberpunk, neon purple, excessive glow, or large decorative gradients
- busy factory scenes, sparks, smoke, clutter, or heavy machinery drama
- generated or distorted Chinese text
- fake device labels, certification marks, specifications, customer logos, or status claims
- several equal focal points with no clear attention hierarchy
- multiple subjects that appear merely adjacent, stacked, or mechanically interlocked without visible cause and effect
- decorative grids or lines that make the image look busier rather than more precise
- a draft that is visually polished but no longer supports the original intent lock
- a revision that changes product/object recognition while losing the requested message relationship

Do not deliver a vetoed draft as a “concept option.” Redo it.

## Design-Upgrade Triggers

Rework the concept when:

- the design is technically clean but generic
- the focal object could belong to any technology company
- every element has similar scale, weight, or spacing
- the composition depends on centered symmetry without a reason
- empty space feels accidental rather than controlled
- added decoration does not increase meaning, hierarchy, or recognition
- the first draft only changes color, shadow, or border treatment from a common template
- a revised draft keeps the same weak silhouette, subject relationship, or composition as the rejected draft
- the self-review can only defend the image by explaining the brief instead of pointing to visible evidence
- brand rules produce a safe but dull image with no memorable crop, silhouette, material decision, or subject relationship
- a user-named layout problem remains visible after a revision, even if typography, color, or file quality improved
- a revision claims improved integration but the thumbnail still reads as separate panels, pasted layers, or independent left-right blocks
- two attempts in a row only adjust gradient, opacity, blur, glow, saturation, or accent lines for a composition problem

Change the composition idea, content relationship, or medium. Do not merely polish the same weak layout.

## Revision Discipline

When a draft fails, name the failure category before changing anything:

- **Intent drift:** the image no longer serves the original request.
- **Semantic weakness:** the subjects or relationship are not visible.
- **Visual weakness:** the message is right, but the form lacks beauty, tension, hierarchy, or craft.
- **Recognition mismatch:** the subject is misread as the wrong object or industry.
- **Claim risk:** the image implies unverified product structure, data, certification, customer use, or performance.
- **Composition integration failure:** the elements are correct, but the layout still reads as separate panels, pasted blocks, or weakly connected regions.
- **Regression failure:** the specific problem the user asked to fix did not visibly improve when compared with the prior version.
- **Strategy failure:** the image request conflicts with page goal, attention hierarchy, image role, claim boundaries, or message ownership.

Then choose the correction:

- Intent drift requires returning to the brief or asking one question. Do not generate.
- Semantic weakness requires changing subject relationship or message carriers.
- Visual weakness requires changing silhouette, crop, scale, medium, or composition.
- Composition integration failure requires changing the spatial structure, mask shape, background continuity, shared lighting, or content overlap logic. Do not treat it as a color or gradient problem.
- Regression failure requires side-by-side comparison, a new hypothesis, and a materially different correction path before another draft.
- Recognition mismatch requires changing the subject cues while preserving the original message.
- Claim risk requires removing or abstracting the risky detail.
- Strategy failure requires returning to `$jiangyue-website-planner` with a rework request. Do not generate another image from the same brief.

After two failed structural image revisions for the same reason, stop production and run the planner return gate. Do not keep changing colors, glow, camera angle, gradient width, opacity, blur, or background atmosphere.

## Planner Return Gate

After a failed draft or failed brief review, decide whether to continue imagegen or return to `$jiangyue-website-planner`.

Continue imagegen when the strategy is sound but execution is weak:

- composition, crop, material, lighting, realism, or visual craft is poor
- image role is correct, but atmosphere or polish is not strong enough
- subject recognition needs clearer visual cues without changing the page message
- physical structure needs rebuilding, but page goal and image task remain valid
- the image can be fixed by changing visual model, silhouette, crop, material, medium, or reference direction

Return to planner when the image request brief is strategically wrong:

- image responsibility is too broad, overloaded, or contradictory
- first-screen attention owner is unclear
- image role conflicts with the page goal, H1, CTA, logo, or conversion path
- a better image would require changing page copy, CTA, section order, positioning, or marketing claim
- the brief asks imagegen to imply unverified product architecture, claims, customer use, installation, certification, or application context
- two structural image revisions failed for the same reason

When returning to planner, output:

```text
Imagegen 返工请求

- 失败归因：执行问题 / 策略问题
- 触发打回 planner 的原因：
- 原图片需求哪里不成立：
- 已尝试但失败的视觉方向：
- 不建议继续尝试的方向：
- 需要 planner 重新决定：
  - 页面目标：
  - 首屏注意力层级：
  - 图片角色：
  - 图片与 HTML / 页面文案的信息分工：
  - claim 边界：
- 给 planner 的问题：
```

Do not produce another draft until planner returns a revised image request brief or the user explicitly narrows the task.

## Review Separation

Review the rendered asset without relying on the production rationale. Start with intent fidelity, then score visual quality.

First answer:

1. Does the draft still support the original intent lock?
2. Can each named subject be traced to a visible image cue or planned HTML copy?
3. Would the draft mislead the user into thinking it is a different type of asset?
4. For every user-stated defect, what visible evidence shows it improved versus the prior version? If there is no clear side-by-side improvement, reject the draft.
5. At thumbnail size, does the composition still show the rejected problem, such as a hard left-right split, pasted panel, weak product recognition, or distracting accent? If yes, reject the draft.

If any answer fails, reject the draft before scoring visual quality.

Then score:

1. attention hierarchy and image role
2. hierarchy and typography
3. brand specificity
4. composition and negative space
5. template resistance
6. legibility at website-card size
7. semantic clarity: foundation, driver, outcome, and flow are understandable without reading the design explanation
8. user-stated regression gates: the specific issues named by the user are visibly improved compared with the prior version

Any score below acceptable requires revision. For an important asset or repeated failure, request permission to use an independent reviewer or additional reference research rather than approving the work through self-justification.

## Composition Integration Gate

Use this gate for hero images, existing image revisions, and any task where the user mentions balance, layout, split, color blocks, integration, cohesion, or brand-color connection.

Hard fail and revise structurally when:

- the left and right sides still read as two independent panels or pasted layers
- a readable text zone is achieved by covering the image with a flat block rather than by shared lighting, depth, or controlled local contrast
- the image depends on a vertical gradient edge that remains visible in thumbnail view
- product edges or important visual mass are weakened by fog used only to hide old content
- brand colors are added as isolated lines, dots, or accents but do not connect logo, focal subject, and technical cues
- the claimed improvement cannot be pointed to in the rendered image without explaining the intention

Preferred fixes:

- change the mask shape, not just mask opacity
- use local text backing instead of a full-height panel when possible
- let background texture, lighting, or product shadow continue across the transition zone
- use brand color through existing carriers such as logo, product highlight, selected data path, or CTA accent rather than extra decoration
- preserve the focal product's contrast while softening only the reading area


## Subject Guidance

### Hero

First decide whether the hero image owns first attention or supports the H1, CTA, logo, or brand atmosphere. If the image owns attention, use one minimal control-core, product form, compact system symbol, or clear relationship. If the H1, CTA, or logo owns attention, keep the image calmer and use it to build professional atmosphere, technical credibility, category recognition, and space for HTML headline and CTA.

### Product

Show a conceptual controller clearly on a light background. Emphasize enclosure, interface, terminals, and thermal design without invented labels or specifications.

### Application

Show a clear controller-to-application relationship. Use fan, pump, HVAC, ventilation, OEM equipment, or other industrial systems only when the brief or page calls for them. Keep the environment clean and secondary.

### Technical Resources

Use organized documents, connectors, diagrams, or abstract unlabeled diagnostic UI. Do not fabricate readable values or compliance marks.

### Geometric Cards and Brand Graphics

Prefer custom silhouettes, asymmetric facets, precise spacing, and controlled material contrast. Avoid default hexagon clusters and ordinary UI badges. Build deterministic geometry directly rather than asking an image model to invent it.

## Product and Claim Safety

When no verified product photo exists, describe the result as a conceptual visual. Do not imply:

- final enclosure design
- exact electrical specifications
- certifications or compliance
- verified test results
- customer installations
- patents, export markets, or mass-production status

Use supplied brand marks or product photos only when the user provides or verifies them.

## Output Rules

- Default to one PNG plus an editable source when the source is SVG or another practical native format.
- Produce a clean image and a full mockup only when both are useful or explicitly requested.
- Use descriptive filenames and never overwrite existing assets without permission.
- Save project-bound assets inside a dedicated task folder under the workspace output area.
- Include or update a reproduction archive for every delivered task so the image can be rebuilt or modified without consuming large prompt context.
- For deterministic or hybrid outputs, include the script/source needed to rebuild the final image from saved local assets.
- For fully AI-generated outputs, archive prompts, inputs, model/tool metadata, and limitations; state clearly when exact pixel-identical regeneration is not verified.
- Inspect dimensions, legibility, spelling, composition, and visible artifacts before delivery.
- Do not claim browser, mobile, SEO, compression, or WordPress behavior that was not checked.

## Delivery

Report:

- final file path
- task folder path
- reproduction archive path
- dimensions and format
- production method
- what was visually verified
- any limitation that remains

Add at most one short visual-only improvement note when it is genuinely useful.
