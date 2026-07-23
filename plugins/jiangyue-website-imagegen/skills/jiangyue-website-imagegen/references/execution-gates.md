# Execution Gates

Use this reference when producing, editing, or reviewing a Jiangyue website visual. Keep the gates practical; do not turn simple exports into full strategy work.

## Execution Intent Gate

Classify the latest user instruction before choosing a production method:

- **New image:** create a new visual from a planner brief or clear user request.
- **Brief-based rebuild:** remake the image from an approved planner brief, image brief, or earlier suggestion.
- **Local edit:** modify an existing image without changing the concept.
- **Format edit:** resize, crop, compress, export, or adapt dimensions only.
- **Page/mockup work:** adjust an HTML/page preview or layout, not just the image file.

If production and format language are combined, treat it as image production plus export sizing unless the user explicitly asks only to resize an existing file.

When the user says "according to the above suggestion", "according to planner", "according to the brief", "rebuild", or similar, extract the referenced requirements first. State the execution understanding for high-impact hero work:

```text
Execution understanding:
- Type:
- Basis:
- Key requirements:
- Must keep:
- Must remove:
- Must materially change:
- Must avoid:
- Size and delivery:
- Not doing:
```

Ask one question only when two or more classifications remain plausible.

## Intent Lock

Before visual form, lock:

- the user's original job for the image
- the core message the image must support
- what the image itself must communicate without explanation
- what HTML/page copy carries instead of the image
- drift boundaries: what the image must not become

A later correction must not replace the original job. If the correction would change the job, stop and restate the trade-off.

## Production Readiness Check

Before generation or editing, confirm:

1. A bounded technical operation cites an accepted baseline and inherited Formula Decision and cannot change meaning; otherwise it is a semantic task.
2. A semantic new image or meaning-changing edit has one current planner Formula Decision citing the formal brand outline section 4.
3. `T/S/R/O/A/I/N` all contain decisions, and every non-image responsibility names an exact text, layout, or UI carrier.
4. Image-owned decisions are concrete enough to compile into subject, relationship, composition, atmosphere, identity, negative constraints, and observable checks.
5. Product facts, physical logic, required deterministic text, protected content, risks, preconditions, and pass/fail criteria are clear.

If these fail because of page strategy, formula judgment, or ownership, return to planner. If they fail because of one local execution parameter, ask one question.

## Method Quality Gate

Choose the method because it can reach the visible result.

- Use image generation or image editing for photographic, realistic, atmospheric, product, lab, equipment, application, or brand-defining hero bases.
- Use deterministic SVG/canvas/Python composition for typography, geometry, diagrams, masks, overlays, crops, color variants, and repeatable layouts.
- Use a hybrid workflow when the visual base needs generation but text, CTA, logo placement, crop, or review thumbnails need deterministic control.
- Do not crop screenshots or deliver a lower-grade flat illustration only because it is easier to save locally.
- Do not promise exact pixel-identical regeneration unless stable inputs, tool behavior, and deterministic source assets make that true.

For high-impact, cost-bearing, or repeated-failure image work, read [production-success-strategy-gate.md](production-success-strategy-gate.md) and [attempt-stop-and-method-escalation-gate.md](attempt-stop-and-method-escalation-gate.md) before production. Do not use repeated generation as the strategy.

## Subtask Method Lock

Use this lock for high-impact visuals, approved-material edits, realistic natural texture, repeated failure, or method disputes. Do not force one method for the whole conversation; split the work into subtasks and choose one primary method per subtask.

| Subtask | Primary method | Supporting method | Forbidden shortcut |
|---|---|---|---|
| Realistic natural texture, water ripple, leaf vein, wet light, organic material, or atmospheric base | Image generation, image editing, or real-source compositing | Reference research, mask cleanup, color match | Final visual made from scripts, geometric blocks, SVG/Python curves, or Bezier simulation |
| Preserve approved subject, color, texture, position, or composition | Mask-protected local edit | Color match, local blur, cleanup, deterministic crop | Full-image regeneration that changes protected approved material |
| Local artifact, edge residue, small blend issue, or tonal mismatch | Mask / opacity / blur / local color correction | Clone, heal, crop, export | Rebuilding the whole concept |
| Structural relationship failure, weak space, fake contact, or unrealistic scene logic | Rebuild visual model, source basis, composition structure, or subject carrier | Planner return when image role is wrong | Only changing brightness, glow, blur, opacity, gradient, or export size |
| Important text, logo, CTA, labels, or exact layout | Programmatic typesetting / HTML / deterministic composition | Generated textless base | Asking the image model to render important readable text |
| Final size, compression, crop, archive, or review thumbnail | Deterministic export | Visual inspection | Regenerating a different image after approval |

Record the lock only as much as needed:

```text
Subtask Method Lock
- Subtask:
- Primary method:
- Protected inputs:
- Forbidden shortcut:
- Visible pass/fail:
```

If the user questions whether the wrong method was used, answer with method attribution before producing another draft.

## Physical Plausibility Gate

Use this gate when the image includes real-world objects, electronics, enclosures, equipment, connectors, airflow, data/control paths, service layers, or physical metaphors.

Reject or revise before production if:

- the object could not be plausibly manufactured, mounted, assembled, wired, enclosed, supported, or handled
- a board, chip, heat sink, shell, connector, cable, fan, pump, fixture, or cover is mechanically unrelated to nearby parts
- transparent parts lack thickness, edges, fastening, clearance, or enclosure logic
- frames, covers, rings, platforms, or bases exist only as decoration
- blue/green/red paths look like impossible electricity outside a believable device boundary
- service, AI, or engineering is shown only as a generic icon, glow, or abstract badge

Use terms such as control signal, data path, feedback path, support layer, or service layer. Use energy flow only when a believable power source, load, wiring path, and safety boundary are visible.

## Visible Result Gate

Judge the rendered result first:

1. Does it still support the intent lock and planner brief?
2. Is it visibly suitable for Jiangyue's European B2B industrial buyer context?
3. If a reference or prior draft exists, is it better on the named concern while preserving what worked?
4. At thumbnail size, are the focal subject, hierarchy, and major relationship still readable?
5. Are user-stated defects visibly improved, not merely explained?

If the result is weaker, say so and revise or reject it. Do not defend it with prompt logic, palette logic, method logic, or archive completeness.

If the result passes visible defect checks but still lacks delivery value, run [candidate-delivery-gate.md](candidate-delivery-gate.md). A clean but weak result is not a delivery-ready candidate.
