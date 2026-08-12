# Brief Review Rubric

Use this before asking the user to confirm a production brief. The goal is to improve the brief before image generation, not to excuse a weak draft after generation.

## Path Selection

Choose the lightest review path that protects the asset:

| Path | Use when | Required review |
|---|---|---|
| Light | Small card, simple crop, minor edit, deterministic graphic | Quick pass/fail on intent, carrier, physical logic, text risk |
| Standard | Most website visuals | Run the compact pass/fail review below before confirmation |
| High-impact | Homepage hero, Contact hero, product hero, abstract advantage visual, repeated failure, or recognition-sensitive visual | Run the high-impact dual path, then the compact pass/fail review |

Do not use the high-impact path to make every asset slow. Use it when a weak structure would damage brand credibility or waste generation rounds.

## High-Impact Dual Path

For high-impact or ambiguous concepts, do not jump from fuzzy intent to one production brief. First produce 2-3 materially different visual structure directions, unless the user already provided a clear structure.

Each direction must state:

- **Relationship model:** foundation, driver, outcome, and flow or feedback.
- **Visible carriers:** what carries each named subject in the image or in page copy.
- **Attention owner and image role:** whether the image, headline, CTA, logo, or combined hero owns first attention.
- **Image visual hammer, if applicable:** the first shape or relationship the viewer notices when the image is meant to lead.
- **Physical credibility:** why the structure could exist or why it is safely abstract.
- **Forbidden boundary:** what this direction must not become.

The options must differ by structure, not by color, glow, camera angle, or mood. After the user chooses or confirms a direction, write the normal production brief and score it.

## Compact Review Dimensions

Review each dimension as pass/fail. Do not average away a serious weakness or output a second long scoring contract.

| Dimension | Pass condition |
|---|---|
| Intent fidelity | The brief still solves the user's original job and does not drift into a different asset |
| Formula authority and currency | The brief cites the formal outline section 4 and the Formula Decision matches the active intent/baseline |
| Whole-image synthesis | The triggered contract contains one sketchable mother statement, one compatible scope frame, three to six supporting credibility anchors, and bounded `Fixed / Adaptive / Forbidden` freedom |
| `S` credibility | Subject, selection, close-view detail, fact/material basis, and physical plausibility are production-ready |
| `R` readability | The assigned relationship, direction, continuing process, and human understanding/participation carrier are observable without a long defense |
| `O` usefulness | Attention, reveal, hierarchy, rhythm, depth, and actual text/layout space are clear |
| `A/I` control | Atmosphere and identification amplify established content and do not substitute for `S/R/O` |
| `N` and claim safety | Misreads, unsupported facts, fake evidence, important text handling, and vetoes are explicit |
| Responsibility and prompt readiness | Every field has an exact image/text/layout/UI owner; image-owned parts compile into visible instructions and checks |
| Feasibility and method fit | The method can reach the needed grade; risks, protected content, preconditions, and conditional rework controls are clear |

## Hard Stops

Stop before image generation when any of these are true:

- the brief only works because the explanation is persuasive
- a semantic task lacks a current Formula Decision, formula authority, decided field, or named responsibility owner
- a semantic new, meaning-changing, high-impact, or repeated-failure task lacks a current Whole-Image Synthesis Contract and is not a bounded local edit inheriting an accepted contract
- the mother statement cannot be sketched as one scene and one core moment, becomes an object or repair checklist, contains multiple stories, or conflicts with the scope frame, anchors, formula decisions, or responsibility owners
- the production brief replaces, reinterprets, or transfers planner formula decisions instead of executing them
- the structure is physically strange but planned to be fixed later
- the visual quality relies mainly on color, glow, gradients, or background atmosphere
- the concept uses a generic AI icon, three equal cards, decorative lines, or an arbitrary enclosure as the core idea
- the user has not approved a new product, application object, human figure, technical meaning, or claim-like addition
- the image request requires changing page strategy, H1, CTA, section order, or marketing claims to work
- a request to make or remake a hero image from an earlier brief has been downgraded into old-image retouching, resizing, or color adjustment
- a requested remake/rebuild keeps the same visual model, composition structure, subject relationship, crop/scale hierarchy, and medium as the rejected draft
- the selected method can produce a local file but cannot reach the required visual grade for the asset
- high-impact, cost-bearing, or repeated-failure production has no production success strategy or attempt stop rule
- a photographic, realistic, atmospheric, product, equipment, lab, or brand-defining hero has been downgraded to flat SVG/canvas/Python illustration without explicit user approval
- a natural or organic structure such as leaf, leaf vein, plant, branch, person, realistic scene, or natural material detail is planned as final deterministic vector/Python/SVG geometry without explicit user request for a flat/vector style
- the generation tool cannot expose a local source file and the plan is to crop a screenshot or create a lower-grade substitute instead of stopping to report the limitation
- "web page size", "hero size", or "standard size" is ambiguous between image file output and page/mockup layout, and the ambiguity changes the work
- user-named defects exist but are not copied into a defect register with pass/fail checks
- a proposed revision keeps the same failed method or structure after the same visible defect remained once

## Efficient Review Format

For a standard or high-impact brief, include only this compact self-review:

```text
Brief Readiness
- Intent and formula source: pass/fail
- Whole-image synthesis: pass/fail/inherited accepted contract
- S/R/O executable: pass/fail
- A/I controlled: pass/fail
- N, fact, and claim safety: pass/fail
- Responsibility and prompt readiness: pass/fail
- Feasibility and method fit: pass/fail
- Triggered rework/defect checks: pass/fail/not triggered
- Conclusion: proceed / return to planner / ask one execution question
```

Use a one-line reason only for a failure. Omit the whole-image synthesis or rework line when its trigger is absent.

## If The Brief Fails

Choose one correction:

- **Missing intent:** ask one question about what the viewer must understand.
- **Missing Formula Decision or owner:** return to Workflow Director / planner; do not invent or transfer formula judgments inside imagegen.
- **Missing or conflicting whole-image synthesis:** return to Workflow Director / planner with the primary contract conflict and at most two dependent formula fields; do not read memory, choose a scene silently, or generate for clarification.
- **Missing carrier:** assign the subject to image, visual cue, or HTML copy.
- **Weak relationship:** switch relationship model before changing style.
- **Physical failure:** rebuild the structure using plausible layers, enclosure, mounting, workflow, or abstract geometry.
- **Dull but reliable:** change crop, scale, silhouette, material contrast, or structure family.
- **Overloaded:** demote or move a message into HTML/page copy.
- **Misread execution type:** restate whether the task is new image, brief-based rebuild, local edit, format edit, or page/mockup work before producing.
- **Method downgrade:** stop and report the limitation, or switch to a method that can reach the required visual quality before producing.
- **No rebuild delta:** change the visual model, composition structure, subject relationship, crop/scale hierarchy, medium, or production method before producing.
- **User defect remains:** reject internally; do not deliver. If it remains twice, run `failure-reset-hard-gates.md`.
- **Method mismatch:** change production method before producing; do not rely on export convenience.
- **No success strategy:** define likely failure points, prevention, controlled variables, and distinct attempt hypotheses before producing.
- **Strategy failure:** return to `$jiangyue-website-planner` with an imagegen rework request.

After two failed brief reviews for the same asset, stop and offer 2-3 new structure directions only if the page strategy is still valid. If the failure involves page goal, attention hierarchy, image role, message ownership, or claim boundary, return to planner instead.

## Pressure Scenario

- **Formula Decision missing:** User or workflow asks imagegen to create a silver-gray B2-3 semi-concrete visual but provides only mood and color. Required: return to Workflow Director / planner for the compact Formula Decision with all fields, exact owners, feasibility, and visible checks. Forbidden: let imagegen infer `S/R/O` from style words or use `A/I` as substitutes.
- **Fields complete but whole missing:** User or workflow supplies populated `T/S/R/O/A/I/N` fields whose people, equipment, environment, action, light, and copy-space notes do not form one sketchable scene. Required: return for one Whole-Image Synthesis Contract. Forbidden: concatenate fields into a prompt or let locally detailed instructions count as overall coherence.
