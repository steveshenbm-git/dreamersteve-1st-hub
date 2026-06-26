# Brief Review Rubric

Use this before asking the user to confirm a production brief. The goal is to improve the brief before image generation, not to excuse a weak draft after generation.

## Path Selection

Choose the lightest review path that protects the asset:

| Path | Use when | Required review |
|---|---|---|
| Light | Small card, simple crop, minor edit, deterministic graphic | Quick pass/fail on intent, carrier, physical logic, text risk |
| Standard | Most website visuals | Score the core dimensions below before confirmation |
| High-impact | Homepage hero, Contact hero, product hero, abstract advantage visual, repeated failure, or recognition-sensitive visual | Run the high-impact dual path, then score the selected brief |

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

## Score Dimensions

Score from 1 to 5. A passing brief needs every core dimension at 4 or above. Do not average away a serious weakness.

| Dimension | Pass condition |
|---|---|
| Intent fidelity | The brief still solves the user's original job and does not drift into a different asset |
| Carrier completeness | Every named subject has a visible carrier or a planned HTML/page-copy carrier |
| Relationship readability | The viewer can infer roles, direction, and result without reading a long explanation |
| Physical plausibility | Real-world objects, enclosures, PCBs, paths, materials, and supports make practical sense |
| Attention hierarchy and image role | The brief states who owns first attention and whether the image leads or supports |
| Design strength | The structure has memorable crop, scale, silhouette, material, rhythm, or spatial tension |
| Creative vitality | The image is not merely safe, generic, template-like, or mechanically compliant |
| Brand and buyer fit | It feels calm, technical, credible, and suitable for industrial B2B buyers |
| Claim safety | It avoids fake specs, certifications, customer use, interfaces, performance, and product architecture |
| Text safety | Important text will be typeset directly, kept in HTML, or omitted from image generation |
| Production controllability | The selected method can realistically produce the needed geometry, text, local asset handling, and required visual quality |
| Execution intent | The brief correctly distinguishes new image, brief-based rebuild, local edit, format edit, and page/mockup work |
| Rebuild delta | For remake/rebuild tasks, the brief states what will be kept, removed, materially changed, and avoided |
| User defect closure | For revisions, every user-named defect is registered and has a visible pass/fail check |
| Method fit | The method matches the visual structure; organic natural structures are not planned as final vector/script geometry unless explicitly requested |

## Hard Stops

Stop before user confirmation when any of these score below 4:

- intent fidelity
- carrier completeness
- relationship readability
- physical plausibility
- attention hierarchy and image role

Stop before image generation when any of these are true:

- the brief only works because the explanation is persuasive
- the structure is physically strange but planned to be fixed later
- the visual quality relies mainly on color, glow, gradients, or background atmosphere
- the concept uses a generic AI icon, three equal cards, decorative lines, or an arbitrary enclosure as the core idea
- the user has not approved a new product, application object, human figure, technical meaning, or claim-like addition
- the image request requires changing page strategy, H1, CTA, section order, or marketing claims to work
- a request to make or remake a hero image from an earlier brief has been downgraded into old-image retouching, resizing, or color adjustment
- a requested remake/rebuild keeps the same visual model, composition structure, subject relationship, crop/scale hierarchy, and medium as the rejected draft
- the selected method can produce a local file but cannot reach the required visual grade for the asset
- a photographic, realistic, atmospheric, product, equipment, lab, or brand-defining hero has been downgraded to flat SVG/canvas/Python illustration without explicit user approval
- a natural or organic structure such as leaf, leaf vein, plant, branch, person, realistic scene, or natural material detail is planned as final deterministic vector/Python/SVG geometry without explicit user request for a flat/vector style
- the generation tool cannot expose a local source file and the plan is to crop a screenshot or create a lower-grade substitute instead of stopping to report the limitation
- "web page size", "hero size", or "standard size" is ambiguous between image file output and page/mockup layout, and the ambiguity changes the work
- user-named defects exist but are not copied into a defect register with pass/fail checks
- a proposed revision keeps the same failed method or structure after the same visible defect remained once

## Efficient Review Format

For a standard or high-impact brief, include a compact self-review in the production brief:

```text
简报评分
- 意图锁定：/5
- 主体承载：/5
- 关系可读：/5
- 物理合理性：/5
- 注意力层级与图片角色：/5
- 设计强度：/5
- 创意活性：/5
- 品牌与买家匹配：/5
- 方法与视觉等级：/5
- 方法适配：/5
- 重做结构差异：/5（仅重做/返工任务）
- 用户缺陷闭合：/5（仅返工/投诉/标注问题）
- claim / 文字风险：/5
- 结论：通过 / 需要重构 / 需要再问一个问题
```

Use a one-line reason only for any score below 5. Do not turn the score section into a long design essay.

## If The Brief Fails

Choose one correction:

- **Missing intent:** ask one question about what the viewer must understand.
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
- **Strategy failure:** return to `$jiangyue-website-planner` with an imagegen rework request.

After two failed brief reviews for the same asset, stop and offer 2-3 new structure directions only if the page strategy is still valid. If the failure involves page goal, attention hierarchy, image role, message ownership, or claim boundary, return to planner instead.
