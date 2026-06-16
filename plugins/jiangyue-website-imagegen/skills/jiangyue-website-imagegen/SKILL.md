---
name: jiangyue-website-imagegen
description: Use when creating, editing, or reviewing website visuals for Jiangyue Technology, including Chinese or English page graphics, industrial product imagery, AI-assisted motor-control concepts, application scenes, technical-resource images, card graphics, hero images, and WordPress-ready visual assets.
---

# Jiangyue Website Imagegen

## Core Standard

Create bright, minimal, precise industrial B2B visuals that support technical credibility. Every image needs one clear visual hammer and must avoid unsupported product, certification, customer, or performance claims.

Use the shortest production path that preserves quality. Do not create an HTML preview, browser mockup, design document, competitor review, or multiple deliverables unless the user asks for them or they are necessary to judge the requested asset.

## Brief Intake

For every new image, use [references/image-brief-template.md](references/image-brief-template.md).

- Do not dump the full questionnaire on the user.
- Ask only the highest-value missing question, one at a time.
- Infer low-risk production details from the brand rules and existing assets.
- Before production, return a concise production brief that states the intended message, subject relationship, visual hammer, copy placement, method, and constraints.
- Generate only after the user confirms the brief or has already provided equivalent clear instructions.

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

## Fast Workflow

1. Identify the asset type, crop, purpose, visual hammer, and required text.
2. When the brief contains multiple subjects, confirm their semantic relationship before choosing a visual form.
3. Run a content-sufficiency check before choosing a layout.
4. Check only directly relevant project assets.
5. Choose image generation, image editing, or deterministic SVG/canvas composition.
6. Produce one strong draft first. Create variants only when they test a meaningful visual difference.
7. Inspect the actual output at full size using a separate review pass.
8. Reject and redo any output that hits a quality veto or design-upgrade trigger.
9. Save the accepted asset in the project and report its path, dimensions, method, and unverified limitations.

For a clear simple request, do not conduct an extended questionnaire. Infer low-risk details, return the concise production brief, and proceed after confirmation. If meaning or subject relationships remain ambiguous, wait for the answer.

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

## Content-Sufficiency Check

Before production, classify the brief:

- **Sufficient:** clear subject, hierarchy, purpose, and crop. Proceed.
- **Thin but solvable:** few elements, but typography, silhouette, scale, or material can carry the design. Proceed with an intentional minimal composition.
- **Semantically incomplete:** a stronger design requires meaning not supplied by the user. Ask one question before adding it.
- **Overloaded:** too many equal messages or subjects. Recommend what to remove or subordinate before producing.

Minimal does not mean placing a small object in empty space. A minimal asset still needs deliberate scale, tension, rhythm, and hierarchy.

## Visual Direction

- Mood: calm, precise, credible, modern, technical.
- Brand feel: bright, minimal, focused, AI-native, quietly ambitious.
- Palette: white and very light gray, graphite, sparse vivid blue, cyan, and green.
- Suggested colors: `#FFFFFF`, `#F7F9FC`, `#E9EEF4`, `#0F172A`, `#147DFF`, `#18C7D8`, `#61D345`.
- Lighting: bright studio or clean industrial lighting with restrained reflections.
- Composition: generous negative space, strong hierarchy, few objects.
- Materials: matte coated metal, anodized aluminum, ceramic, precise glass details used sparingly.
- AI cues: a few energy nodes, fine data lines, or controlled luminous edges.

Industrial technology should feel engineered, not theatrical.

## Visual Hammer

The visual hammer is the first and dominant form the viewer notices.

- Use one focal object or one tightly unified object group.
- When several subjects jointly form the hammer, their silhouette must read as one compact symbol.
- Secondary lines, grids, glows, labels, icons, and scenery must remain weaker.
- If a decorative effect attracts attention before the subject, remove it.
- For multiple subjects, make the relationship itself the visual hammer, not merely the collection of objects.

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
- several equal focal points with no clear visual hammer
- multiple subjects that appear merely adjacent, stacked, or mechanically interlocked without visible cause and effect
- decorative grids or lines that make the image look busier rather than more precise

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

Change the composition idea, content relationship, or medium. Do not merely polish the same weak layout.

## Review Separation

Review the rendered asset without relying on the production rationale. Score:

1. visual hammer
2. hierarchy and typography
3. brand specificity
4. composition and negative space
5. template resistance
6. legibility at website-card size
7. semantic clarity: foundation, driver, outcome, and flow are understandable without reading the design explanation

Any score below acceptable requires revision. For an important asset or repeated failure, request permission to use an independent reviewer or additional reference research rather than approving the work through self-justification.


## Subject Guidance

### Hero

Use one minimal control-core, product form, or compact system symbol. Keep space for HTML headline and CTA.

### Product

Show a conceptual controller clearly on a light background. Emphasize enclosure, interface, terminals, and thermal design without invented labels or specifications.

### Application

Show a clear controller-to-fan, pump, OEM equipment, or industrial system relationship. Keep the environment clean and secondary.

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
- Save project-bound assets inside the workspace.
- Inspect dimensions, legibility, spelling, composition, and visible artifacts before delivery.
- Do not claim browser, mobile, SEO, compression, or WordPress behavior that was not checked.

## Delivery

Report:

- final file path
- dimensions and format
- production method
- what was visually verified
- any limitation that remains

Add at most one short visual-only improvement note when it is genuinely useful.
