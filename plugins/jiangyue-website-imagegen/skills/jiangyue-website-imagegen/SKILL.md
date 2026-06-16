---
name: jiangyue-website-imagegen
description: Use when creating, editing, or reviewing website visuals for Jiangyue Technology, including Chinese or English page graphics, industrial product imagery, AI-assisted motor-control concepts, application scenes, technical-resource images, card graphics, hero images, and WordPress-ready visual assets.
---

# Jiangyue Website Imagegen

## Core Standard

Create industrial B2B visuals that support technical credibility while leaving room for real creative range. Every image needs one clear visual hammer and must avoid unsupported product, certification, customer, or performance claims.

Treat brand guidance as a floor, not a cage: the image may be inventive in composition, crop, material, space, and metaphor as long as it remains credible for motor-drive, HVAC, ventilation, and OEM industrial buyers.

Use the shortest production path that preserves quality. Do not create an HTML preview, browser mockup, design document, competitor review, or multiple deliverables unless the user asks for them or they are necessary to judge the requested asset.

## Brief Intake

For every new image, use [references/image-brief-template.md](references/image-brief-template.md).

- Do not dump the full questionnaire on the user.
- Ask only the highest-value missing question, one at a time.
- Infer low-risk production details from the brand rules and existing assets.
- Before production, return a concise production brief that states the original intent, intended message, subject relationship, visual hammer, copy placement, method, and constraints.
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

## Fast Workflow

1. Identify the asset type, crop, purpose, visual hammer, and required text.
2. Create the intent lock. Do not continue if the image responsibility and page-copy responsibility are unclear.
3. When the brief contains multiple subjects, confirm their semantic relationship before choosing a visual form.
4. Run a content-sufficiency check before choosing a layout.
5. Decide whether reference research is needed. For brand-defining hero images, motor-drive/HVAC/ventilation subject recognition, vague "premium/beautiful/industrial" requests, or failed visual quality, use the reference research gate.
6. Choose a concrete visual concept and state why it preserves the intent lock. For a brand-defining hero or ambiguous abstract concept, offer 2-3 materially different visual directions before production.
7. Check only directly relevant project assets.
8. Choose image generation, image editing, or deterministic SVG/canvas composition.
9. Produce one strong draft first. Create variants only when they test a meaningful visual difference.
10. Inspect the actual output at full size and thumbnail size using a separate review pass.
11. Reject and redo any output that fails intent fidelity, hits a quality veto, or triggers a design-upgrade rule.
12. Save the accepted asset in the project and report its path, dimensions, method, and unverified limitations.

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

## Reference Research Gate

For high-impact hero images, abstract concepts, weak visual direction, motor-drive/HVAC/ventilation recognition, or any draft rejected for visual quality, consider reference research before production or revision.

Use [references/reference-research.md](references/reference-research.md) when reference research is needed. Keep this gate conditional: do not search by default for simple cards, deterministic diagrams, text-led graphics, format conversion, or minor image edits.

Reference research must return executable visual principles, not a list of links to copy. Original intent lock overrides every reference.

## Complexity Budget

Use the lightest process that can protect the result:

- **Light path:** clear simple assets. Use intake, brief, production, and review only.
- **Standard path:** most website visuals. Add intent lock, subject carriers, and concept fidelity.
- **High-impact path:** homepage, Contact hero, product hero, abstract advantage visuals, or repeated failure. Add reference research and stronger design-upgrade review.

Do not load every reference file or run web research just because it exists. More process is only justified when it reduces drift, improves subject recognition, or raises visual quality.

## Brand Floor and Creative Range

The required brand floor:

- calm, precise, credible, modern, technical
- suitable for European B2B industrial buyers, OEMs, product teams, purchasing, and engineering roles
- connected to motor control, motor drives, HVAC, ventilation equipment, or industrial control when those categories are relevant
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

Change the composition idea, content relationship, or medium. Do not merely polish the same weak layout.

## Revision Discipline

When a draft fails, name the failure category before changing anything:

- **Intent drift:** the image no longer serves the original request.
- **Semantic weakness:** the subjects or relationship are not visible.
- **Visual weakness:** the message is right, but the form lacks beauty, tension, hierarchy, or craft.
- **Recognition mismatch:** the subject is misread as the wrong object or industry.
- **Claim risk:** the image implies unverified product structure, data, certification, customer use, or performance.

Then choose the correction:

- Intent drift requires returning to the brief or asking one question. Do not generate.
- Semantic weakness requires changing subject relationship or message carriers.
- Visual weakness requires changing silhouette, crop, scale, medium, or composition.
- Recognition mismatch requires changing the subject cues while preserving the original message.
- Claim risk requires removing or abstracting the risky detail.

After two failed drafts for the same asset, stop production and return a short failure analysis plus 2-3 new concept directions for confirmation.

## Review Separation

Review the rendered asset without relying on the production rationale. Start with intent fidelity, then score visual quality.

First answer:

1. Does the draft still support the original intent lock?
2. Can each named subject be traced to a visible image cue or planned HTML copy?
3. Would the draft mislead the user into thinking it is a different type of asset?

If any answer fails, reject the draft before scoring visual quality.

Then score:

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
