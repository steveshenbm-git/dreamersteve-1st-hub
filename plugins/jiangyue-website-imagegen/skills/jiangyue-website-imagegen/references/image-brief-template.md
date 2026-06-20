# Jiangyue Image Brief Template

Use this template before every new image. Its purpose is to collect production requirements and help the requester identify what the image should communicate.

Do not send every question at once. Start with the five core decisions, infer what is safe, and ask one highest-value missing question at a time.

## Copyable User Prompt

The requester can paste this:

```text
请使用 $jiangyue-website-imagegen 帮我制作一张网站图片。

先不要立即生图。请帮助我把模糊想法整理成明确的视觉方案：

1. 先判断我提供的信息是否足够。
2. 每次只问我一个最关键的问题，并说明这个问题会解决什么设计问题。
3. 如果有多个主体，先确认它们的角色、关系、方向和最终结果，不要直接用并列、互锁或连线代替协同。
4. 可以自主调整留白、比例、裁切、构图、材质、色彩和非语义品牌元素。
5. 新增文字、产品、应用对象、人物、技术含义或营销主张前，先征得我的确认。
6. 对关键官网图，可以先联网搜索电机控制、工业控制或当前应用类别相关官网参考；HVAC、通风、风机、泵等只在当前页面或简报相关时使用，只提炼可执行的视觉原则，不复制参考图。
7. 对关键官网图、抽象优势图或多主体图，先给出 2-3 个不同的视觉结构方向；结构要写成“关系模型 + 可变参数 + 禁止边界”，不是只换颜色、光效或角度。
8. 信息明确后，先输出一份简短的“制作简报”，让我确认后再生图。
9. 在输出制作简报前，先给简报评分，检查意图、主体承载、关系可读、物理合理性、注意力层级与图片角色、设计强度、模板风险和 claim 风险；不合格时先修改结构或继续问一个关键问题。
10. 初稿完成后，请按注意力层级、图片角色、品牌匹配、构图、原创性、克制程度、小尺寸表现和语义清晰度进行自审。不合格时进行结构性修改，不要只改颜色、阴影或光效。

我目前的想法：
- 使用位置：
- 目标受众：
- 最想让人第一眼看懂：
- 希望观众形成的判断或感受：
- 必须出现的主体或文字：
- 不希望出现：
- 参考图片或偏好：
- 尺寸或比例：
```

Blank fields are allowed. Ask only what materially affects the concept.

## Failure Pattern To Prevent

Do not let a later visual correction replace the original task.

Bad drift:

1. User asks for a Contact hero about `AI + professional + service`.
2. Draft is too abstract.
3. User says the subject should look more like a drive.
4. Agent changes the image into a motor drive product hero and loses `AI + professional + service`.

Correct handling:

1. Keep the original intent locked.
2. Interpret "make it look more like a drive" as a recognition correction, not a new asset goal.
3. Ask or restate the trade-off if the correction would hide the three-part advantage.
4. Revise subject cues while preserving the original message carriers.

## Execution Misread To Prevent

Do not treat "according to the above suggestion" as a small edit to the latest image when the earlier brief asked for a new image.

Bad downgrade:

1. Planner or prior brief says: make a new red brand hero, brighter industrial lab/test-bench environment, reorganized red data connections, transparent glass UI, less alarm feeling, standard hero size.
2. User says: `根据上面建议制作一张红色的 hero 主图，同时调整网页尺寸，改为 hero 主图的标准尺寸大小。`
3. Agent only color-corrects an old red image, brightens it, reduces pressure, and exports `1920x1080`.

Correct handling:

1. Classify as **brief-based rebuild plus export sizing**, not old-image retouching.
2. Extract the earlier requirements before choosing method.
3. State a short execution understanding before production.
4. Produce a new hero image unless the user explicitly says to keep the existing image.
5. Treat "standard hero size" as image output size by default, such as `1920x1080` or the confirmed 16:9 size. If "web page size" may mean an HTML preview or browser layout, ask one question.

Compact confirmation:

```text
本次执行理解：
- 类型：按上面简报重做新 hero，并导出标准 hero 尺寸
- 依据：红色品牌 hero、明亮工业实验室/测试台、透明 UI、红色数据连接、弱化报警感
- 尺寸与交付：1920x1080 / 16:9 图片资产
- 不做：不是基于旧图简单调色和裁切
```

## Five Core Decisions

### 1. Job

Ask:

> 这张图将放在哪里，它在页面上要完成什么任务？

Examples: Hero main visual, product introduction, application explanation, technical resource, contact, card, social preview.

Why it matters: placement determines crop, information density, negative space, and whether text belongs in HTML or inside the image.

### 2. First Understanding

Ask:

> 观众第一眼最应该看懂什么？请尽量用一句话描述，不要只列元素。

Prefer messages such as:

- 专业控制能力是基础，AI 提升诊断效率，服务保障项目落地。
- 控制器连接风机应用，并提供清晰的维护入口。

Avoid treating lists such as `专业 / AI / 服务` as a complete message.

### 3. Intended Response

Ask:

> 看完图片后，希望客户形成什么判断、感受或下一步行动？

Examples: technically credible, suitable for OEM discussion, easier to maintain, worth requesting technical information.

Why it matters: the same subjects need different hierarchy when the desired response changes.

### 4. Content and Relationship

Ask what must appear. For multiple subjects, determine:

- foundation
- driver
- outcome
- flow or feedback
- carrier for each subject: visual element, visual cue, or HTML/page copy

Use:

> 这些主体之间最重要的关系或结果是什么？

Do not proceed while several relationship models remain equally plausible.

If the user chooses not to put text inside the image, ask or infer how each named idea will be carried:

- `AI`: visual signal, light layer, data path, or HTML copy
- `Professional`: industrial form, engineering material, precision structure, or HTML copy
- `Service`: support field, cooperative path, response touchpoint, or HTML copy

If any named idea has no carrier, the brief is incomplete.

### 5. Constraints

Confirm:

- exact required text
- elements that must not appear
- supplied references or real product photos
- known claim boundaries
- crop or dimensions when known
- whether the user means image file dimensions or an HTML/page preview when saying page size, web size, hero size, or browser size

Infer ordinary brand colors and production details rather than asking unnecessarily.

## Conditional Questions

Ask these only when relevant.

### Hero

- Who owns first attention: headline, CTA, logo, image, or the combined hero?
- Should the image act as the main visual hammer, or support professional atmosphere, brand mood, trust, and conversion?
- Where will the headline and CTA sit?
- Should the visual support copy on the left or right?
- Is the image a clean background asset, a complete mockup, or both?
- What is the one headline the visual must reinforce?

Keep H1, body copy, and CTA in HTML unless the user explicitly requests a composed mockup.

### Multiple Subjects

Confirm:

1. What is the stable foundation or input?
2. What is the active driver or transformation?
3. What is the delivered outcome?
4. Does the value move in one direction, converge, or return as a loop?

### High-Impact Structure Direction

For homepage hero, Contact hero, product hero, abstract advantage images, multi-subject relationships, or repeated failure, first offer 2-3 structure directions unless the user already confirmed one.

Each direction should be brief:

```text
方向 A：
- 关系模型：
- 可变参数：
- 禁止边界：
- 注意力主导与图片角色：
- 图片视觉锤（如适用）：
- 适合原因：
```

The directions must differ by relationship and structure, not by color, glow, camera angle, or mood. If all options are just variants of the same layout, revise them before showing the user.

### Text-Led Graphics

- Which text must be inside the image?
- Which copy should remain HTML?
- Which term is primary and which are supporting?

Use real typography. Do not ask the image model to render important Chinese text.

### Product or Technical Meaning

Ask before implying:

- diagnostics
- Bluetooth or cloud access
- monitoring
- safety or protection
- performance
- certification
- customer installation
- final product structure

### Physical Plausibility

For industrial hardware, electronics, equipment, application scenes, enclosures, PCBs, or physical metaphors, check before writing the production brief:

- Can the object be plausibly manufactured, mounted, assembled, wired, enclosed, supported, or handled?
- Do the enclosure, base, PCB, chip, heat sink, connectors, shell, fasteners, and signal paths have a practical relationship?
- Are transparent parts complete enough to make physical sense, with thickness, edges, screw points, clearance, and realistic reflections?
- Could a blue/green path be mistaken for impossible electrical power flow?
- Is any object used only as a forced symbol rather than a believable industrial layer?

Prefer terms such as `control signal`, `data path`, `feedback path`, and `support layer`. Avoid `energy flow` unless the image is intentionally showing a plausible power path with source, load, wiring, and safety boundary.

If the physical logic is uncertain, ask one question or change the concept before showing the brief. Do not postpone this problem to image review.

### References

When the user says only “高级、科技、简洁”, ask:

> 有没有一张你喜欢或不喜欢的参考图？它最值得保留或避免的是什么？

The reason is more useful than the reference alone.

For high-impact hero images, abstract advantage images, or motor-control / application-category subject recognition, use reference research instead of guessing the style. Search official websites first with broad category terms such as `motor drive`, `motor controller`, `PMSM motor controller`, `BLDC motor controller`, `industrial motor controller`, `industrial control electronics`, plus the current page's application terms when relevant, such as `HVAC motor drive`, `fan motor drive`, `pump drive`, `ventilation fan motor controller`, or other user-provided application keywords. Use Chinese `电机驱动器` only when useful for internal terminology.

Reference research should answer:

- what makes the subject read as an electric motor drive/controller
- what makes the context feel related to the current application category, if one is specified
- what composition, crop, and material treatment can raise visual quality
- what common template or stock-tech patterns must be avoided

Do not turn reference research into broad competitor analysis unless the user asks.

## Assistant Production Brief

Before generation, return this concise brief:

```text
制作简报

- 使用位置：
- 图片任务：
- 原始意图锁定：
  - 原始目标：
  - 图片必须支持的信息：
  - 图片本身负责表达：
  - HTML / 页面文案负责表达：
  - 不可漂移成：
- 目标受众：
- 核心信息：
- 希望产生的判断或行动：
- 主体与关系：
  - 基础：
  - 驱动：
  - 结果：
  - 流向 / 反馈：
  - 主体承载方式：
- 物理合理性：
  - 结构 / 装配逻辑：
  - 信号 / 数据 / 反馈路径：
  - 避免误读为：
- 注意力层级与图片角色：
  - 首屏第一注意力由谁承担：
  - 图片角色：主视觉锤 / 专业氛围 / 品牌氛围 / 信任支撑 / CTA 辅助 / 其他
  - 图片需要避免抢走：
- 可靠视觉结构：
  - 关系模型：
  - 可变参数：
  - 禁止边界：
  - 不采用的结构及原因：
- 图片视觉策略：
  - 图片视觉锤（如适用）：
  - 氛围与专业度策略（如图片不承担主视觉锤）：
- 概念契约：
- 构图与文案留白：
- 图片内文字：
- 保留在 HTML 的文字：
- 参考研究结论（如已触发）：
- 视觉方向：
- 制作方法：图像生成 / 图像编辑 / SVG 或混合制作
- 必须避免：
- 输出尺寸与文件：
- 尚未验证或不可暗示的内容：
- 简报自查：
  - 意图是否锁定：
  - 主体承载是否完整：
  - 关系是否可读：
  - 物理合理性是否通过：
  - 注意力层级与图片角色是否明确：
  - 模板 / claim / 文字风险：
- 简报评分：
  - 意图锁定：/5
  - 主体承载：/5
  - 关系可读：/5
  - 物理合理性：/5
  - 注意力层级与图片角色：/5
  - 设计强度：/5
  - 创意活性：/5
  - 品牌与买家匹配：/5
  - claim / 文字风险：/5
  - 结论：通过 / 需要重构 / 需要再问一个问题
```

Keep it short. State decisions rather than repeating the conversation.

The concept contract must be visible and testable, not decorative:

> This image will show [visual subject] so that [viewer understands/feels X], while [message Y] is carried by [image/page copy].

Reject the brief before asking for user confirmation if the concept contract could apply to any generic technology company, if the physical logic is weak, or if the visual design only works after a long explanation.

The brief self-review must be factual, not reassuring. If it finds a problem, revise the concept or ask one focused question instead of listing the problem and still proceeding.

For high-impact visuals, a reliable structure is not enough. If the brief is plausible but visually plain, revise the relationship model, crop, scale, silhouette, material, or medium before asking for confirmation.

## Information-Sufficiency Gate

Proceed when all are true:

- the image job is clear
- one primary message is clear
- the main subject or relationship is clear
- the desired viewer response is clear enough to set hierarchy
- required copy and claim boundaries are known
- crop can be inferred or is supplied
- the page-level attention owner and image role are clear enough for the asset type
- the original intent lock is explicit
- each named subject has an explicit carrier in the image or page copy
- the visual concept has a drift boundary
- physical structure or metaphor is plausible enough for an industrial buyer
- brief self-review has passed before the user is asked to confirm
- for high-impact or recognition-sensitive images, reference research has either been used or explicitly judged unnecessary
- for high-impact or abstract images, a structure direction has been selected or explicitly judged unnecessary
- standard or high-impact brief scoring has passed before the user is asked to confirm

Do not proceed when:

- the requester supplies only a list of objects
- multiple relationship models remain plausible
- a stronger visual requires unapproved meaning
- Hero copy placement is unknown and materially affects composition
- supplied technical claims or product details are uncertain
- a proposed visual direction solves a different job than the original request
- physical parts, enclosures, frames, bases, paths, or materials look forced together or mechanically unrelated
- removing the production rationale would make the image's connection to the message unclear
- the concept relies on fixed brand colors, generic AI lines, or decorative glow as the main evidence of quality
- all proposed structure directions are only style variants of the same weak idea
- a good image would require changing page strategy, H1, CTA, section order, or marketing claims

## Question Priority

When several details are missing, ask in this order:

1. What should the viewer understand?
2. What should the viewer conclude or do?
3. For hero assets, who owns first attention: headline, CTA, logo, image, or the combined hero?
4. How do multiple subjects relate?
5. Which parts must be shown by the image and which may be carried by HTML/page copy?
6. What physical structure or metaphor can carry the message credibly?
7. For high-impact visuals, which structure direction best fits the intended buyer judgment?
8. Where will the image be used and where will copy sit?
9. What exact content and constraints must be preserved?
10. Is this a high-impact or recognition-sensitive image that needs official website reference research?
11. What visual references help distinguish preference?

Do not ask about color, camera angle, materials, or minor styling before message and relationship are clear.

## Example

Weak input:

> 做一张专业、创新 AI、服务的图片。

Useful clarification:

> 这三个词可以表达多种关系。你最想展现哪一种结果：  
> A. 专业是基础，创新 AI 是驱动，服务形成落地与反馈闭环；  
> B. 三项能力平等汇聚为一套解决方案；  
> C. 专业评估、AI 分析、持续服务构成客户流程？

Confirmed internal sentence:

> 专业控制能力支撑创新 AI，创新 AI 提升分析与控制价值，服务将能力落地并把现场反馈带回专业基础。

Only then choose the visual form.

## Correction Handling Example

User:

> 图片主体不像驱动器，调整一下。

Incorrect response:

> Make a product-like motor drive hero and drop the original three-part advantage.

Correct response:

> This is a recognition correction. Keep the original intent: Contact hero supporting AI + professional + service. Revise the subject so it borrows motor-drive cues such as low enclosure mass, heat-sink rhythm, mounting geometry, or restrained terminal hints, while AI/professional/service remain carried by the agreed image cues and HTML copy.

## Planner Return Example

If imagegen fails because the brief is strategically wrong, do not keep generating. Return this:

```text
Imagegen 返工请求

- 失败归因：策略问题
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

Use this when the issue is not visual execution, but unclear or conflicting page strategy.
