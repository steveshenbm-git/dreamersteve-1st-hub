# Visual Formula Brief

Use this compact contract for every new Jiangyue image, pattern, poster, page visual unit, visual brief, prompt direction, or meaning-changing visual edit.

## Authority

Formula meaning comes only from section 4 of:

```text
/Users/lirongjing/Documents/JY TECH WEB/website-content-brand-plan/网站全案/品牌全案/江樾科技品牌大纲-2026-正式版.md
```

Do not restate or shorten the formula as a new local definition. Use the identifiers below to record decisions in the required order.

## Compact Core

```text
Visual Formula Decision / 视觉公式判断

- Authority source: formal brand outline, section 4
- Intent and fact boundary: original intent / accepted facts / assumptions / claims that must not be implied
- Three-factor decision: purpose fit and required buyer/page outcome / truthfulness-realism mode and evidence boundary / visual-quality mechanism and quality bar / strongest conflict
- T | Task and medium: visual unit, placement, job, first attention, information it does not own
- S | Subject: attention owner, keep/weaken/omit, close-view real detail, fact or material basis
- R | Relationship: visible carrier, what continues, how a person understands or participates, factual basis
- O | Order: reveal first, defer/weaken, density and rhythm, useful whitespace
- A | Amplification: already-established feeling, light/air/material/depth amplifier, controlled intensity or zero
- I | Identity: recognition/status/local-attention purpose, carrier, position, range and intensity
- N | Misread and veto: likely misread, forbidden content, direct rejection trigger
- Responsibility: image / HTML or text / layout; name the exact owner for every non-image field
- Production direction: one prompt-ready visual statement, protected content, deterministic text/layout work
- Feasibility and route: semantic compatibility evidence; main risk; imagegen freedom; pass/fail evidence; final decision `PROCEED` or `RETURN`
```

Every field needs a decision. A field may be carried outside the asset, but `not applicable`, an empty value, or an unnamed "page will handle it" is not a decision. Name the actual text, layout position, UI element, or surrounding visual unit that owns it.

The final model prompt may use natural language and combine sentences. The production record must still map its constraints back to all seven decisions without dropping, replacing, or reinterpreting them.

## Three-Factor Cross-Check

Purpose fit, truthfulness/realism fit, and visual-quality fit are cross-cutting review dimensions, not new formula stages or replacement definitions:

- Purpose begins with `T`, but the full decision must serve the page job, buyer interpretation, image role, and responsibility split.
- Truthfulness/realism is anchored by `S`, fact/material evidence, physical and commercial plausibility, and `N`; also test whether the visible `R/O` mechanisms create a false installation, capability, product, or operating reading.
- Visual quality is shaped by the selected visual hypothesis, `O/A/I`, composition, material, light, depth, rhythm, and craft; it cannot compensate for missing or false `S/R`, and safety alone does not excuse a generic result.

Record `pass` or `fail` for each factor. Do not average scores. Product presence is a role-and-evidence decision: require it when verified product recognition or detail is image-owned, omit it when it conflicts with the accepted image role or lacks the required evidence.

## Semantic Compatibility Preflight

Before handoff, decide whether `T-S` serve the same page job, image-owned `S/R` have a public identifiable fact/material basis, the strongest plausible `N` misread remains likely, which fields depend on the primary conflict, named HTML/text/layout owners support rather than rescue a failed image-owned `S` or triggered `N`, and all three factors pass independently.

- `PROCEED`: keep the complete Formula Decision and compile the production handoff.
- `RETURN`: issue no production brief, prompt, or imagegen instruction; record only the primary blocker, no more than two dependent fields, evidence, and next owner.

```text
Planner Handoff Verdict
- Decision: PROCEED / RETURN
- Primary blocker:
- Dependent fields: maximum two
- Evidence:
- Three-factor status: purpose / truthfulness-realism / visual quality
- Next owner:
```

## Conditional Modules

Load and output a module only when its observable trigger is present. Omit the whole module otherwise; do not print empty fields.

| Trigger | Add |
|---|---|
| Complete page planning | H1, supporting copy, CTA, SEO/AEO, module order, trust path from [page-brief-template.md](page-brief-template.md) |
| Brand-defining or homepage/hero visual | Relevant `brand-system/02-brand-visual/` alignment, approved-material protection, recognition and brand-drift checks |
| Product or application subject | Product fact source, physical/integration logic, unsupported claim and fake-evidence checks |
| Rework, rejection, or repeated failure | Accepted baseline, exact defect, keep/remove/materially-change/avoid, failed formula field, changed production hypothesis |
| Reference research is materially needed | Source and attribution, learnable method, forbidden copying, facts or claims that cannot transfer |
| Bounded technical operation | Source, crop/size/format/export, protected subject and copy space; inherit the accepted formula decision |

If a bounded operation changes attention, subject meaning, relationship, reveal order, atmosphere, identity signal, or misread risk, it is a meaning-changing edit and requires a current core decision.

## Handoff Failure

Return to Workflow Director when intent or task ownership is unresolved. Imagegen returns a handoff that lacks `PROCEED`, is contradictory, unsupported, too abstract to sketch, or assigns a field to text/layout without naming the carrier.
