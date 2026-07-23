# Visual Formula Execution

Use this for semantic new images and meaning-changing edits. Formula meanings come only from section 4 of:

```text
/Users/lirongjing/Documents/JY TECH WEB/website-content-brand-plan/网站全案/品牌全案/江樾科技品牌大纲-2026-正式版.md
```

This file defines execution traceability, not formula semantics.

## Input Contract

Accept production only when planner supplies one current Formula Decision containing:

- authority and visual-unit intent;
- judgments for `T/S/R/O/A/I/N`;
- one exact image, text, layout, or UI owner for each decision;
- production direction, feasibility, protected content, risks, preconditions, and visible pass/fail checks.

Do not fill missing strategic decisions inside imagegen. Return ownerless, stale, contradictory, or abstract decisions to Workflow Director.

## Production Trace

Maintain one compact internal trace. Do not expose it as a second brief.

```text
Formula Production Trace
- Formula Decision source/version:
- T: accepted task and excluded information
- S: planner decision / image evidence / external owner / prompt clause / result observation
- R: planner decision / image evidence / external owner / prompt clause / result observation
- O: planner decision / image evidence / external owner / prompt clause / result observation
- A: planner decision / image evidence / external owner / prompt clause / result observation
- I: planner decision / image evidence / external owner / prompt clause / result observation
- N: negative constraint / result observation
- Post-processing responsibility:
- Trace status: ready / return to planner / fail result check
```

Every field receives a judgment. A field need not become an object in the bitmap when its named text/layout/UI mechanism carries it, but imagegen must preserve the required area, hierarchy, contrast, or integration condition.

## Prompt Compilation Order

Compile decisions in this order:

1. `T`: output role, context, stage, aspect ratio, and exclusions.
2. `S`: subject, truthful detail, material/physical constraints, and proximity standard.
3. `R`: visible interaction, state change, feedback, analysis, judgment, adjustment, or understandable participation assigned to the image.
4. `O`: hierarchy, reveal, density rhythm, depth, and functional negative-space requirement assigned to the image.
5. `A`: restrained light, atmosphere, and tonal amplification only after the earlier mechanisms are concrete.
6. `I`: exact identification use, carrier, position, range, and intensity.
7. `N`: forbidden readings, unsupported claims, failure patterns, and hard vetoes.

The final model prompt should read as coherent natural instructions. Do not paste seven labels as slogans, repeat the same decision under multiple headings, or ask the model to render decisions owned by text/layout/UI. Convert `N` to explicit negative constraints and QA checks. Keep important copy and deterministic overlays outside the image model.

## Bounded Technical Operations

Crop, resize, compress, format conversion, deterministic typesetting, and export may use a light trace that cites the accepted baseline and Formula Decision. Load only source, target, protected elements, technical parameters, and checks.

Return to planner if the operation can change attention ownership, subject credibility, relationship meaning, spatial order, atmosphere role, identification dominance, claim boundary, or forbidden interpretation.

## Result Check

After rendering, record observed evidence rather than prompt intent:

- inspect image-owned `S/R/O/A/I` mechanisms at full size and review size;
- confirm named text/layout/UI owners still have a usable carrier;
- confirm `A` and `I` did not replace missing `S/R/O` mechanisms;
- apply `N` as a misread and veto check;
- classify any changed decision or owner as formula drift and return it to planner.
