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

## Semantic Compatibility Preflight

Before handoff, decide whether `T-S` serve the same page job, image-owned `S/R` have a public identifiable fact/material basis, the strongest plausible `N` misread remains likely, which fields depend on the primary conflict, and named HTML/text/layout owners support rather than rescue a failed image-owned `S` or triggered `N`.

- `PROCEED`: keep the complete Formula Decision and compile the production handoff.
- `RETURN`: issue no production brief, prompt, or imagegen instruction; record only the primary blocker, no more than two dependent fields, evidence, and next owner.

```text
Planner Handoff Verdict
- Decision: PROCEED / RETURN
- Primary blocker:
- Dependent fields: maximum two
- Evidence:
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
