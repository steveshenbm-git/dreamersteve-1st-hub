# Workflow Director Pressure Scenarios

Use these scenarios to validate routing behavior before changing this skill or related Jiangyue skills.

## Required Outcomes

1. **Simple P图**
   - User: "把这张场景图里的人 P 掉。"
   - Required: route to imagegen with source path, remove target, must keep list, draft stage, and visual pass/fail.
   - Forbidden: ask planner for page strategy unless the image role is unclear or output failed repeatedly.

2. **Post-image edit without saying failed**
   - User after draft: "右侧叶片再多一点，小一点。"
   - Required: post-image triage first, then route to imagegen only if strategy remains clear.
   - Forbidden: treat the previous draft as accepted.

3. **Planner problem hidden as edit**
   - User after draft: "这个不像 About Us，客户看了不信任。"
   - Required: route to planner for page role, trust signal, and visual direction attribution.
   - Forbidden: send directly to imagegen as a local retouch.

4. **Two-return simple task**
   - User asks twice to remove an object; the object or residue remains.
   - Required: stop direct imagegen, run Intent Check or systematic debugging, register the defect, then decide next route.
   - Forbidden: "try again" with a looser prompt.

5. **Self-check failure**
   - User: "你的自查系统失效了吗，还是不合格。"
   - Required: run systematic debugging before more production, identify missed gate, update defect register.
   - Forbidden: defend the previous draft or produce another image immediately.

6. **Unclear creative direction**
   - User: "我也说不清，就是感觉这个图不对。"
   - Required: use brainstorming or ask one high-value question before routing.
   - Forbidden: ask a long questionnaire or default to imagegen.

7. **Skill/process change**
   - User: "优化 imagegen 的自查规则。"
   - Required: route to `jiangyue-skill-director` first. Skill-director decides whether `skill-creator`, `superpowers:writing-skills`, pressure scenarios, implementation, validation, and commit are required.
   - Forbidden: patch wording from workflow-director, planner, imagegen, or curator directly; let a downstream skill repair itself; or edit plugin files before skill-director sets the source boundary and owning artifact.

8. **Knowledge capture**
   - User: "这轮失败记录下来，后面别再犯。"
   - Required: route to curator for confirmation card and formal knowledge entry after confirmation.
   - Forbidden: bury the lesson only in chat history.

9. **Final export**
   - User: "这个方向通过，导出 3840x2160。"
   - Required: route to imagegen for deterministic final/export from accepted draft and verify visible output.
   - Forbidden: regenerate a different final unless explicitly requested.

10. **Delivery claim**
    - User asks for commit, final delivery, or says "确认没问题".
    - Required: run verification-before-completion where applicable and state what was verified.
    - Forbidden: claim success from file existence or prompt compliance alone.

11. **No observable change**
    - User: "水纹扩大了三次，没有什么变化。"
    - Required: stop another normal imagegen round, register observable-change failure, require side-by-side delta evidence and method/edit-scope change.
    - Forbidden: produce another draft from small parameter changes or claim the change happened from prompt wording.

12. **Method challenge**
    - User: "你是不是在用脚本/几何色块/Bézier 曲线去模拟。"
    - Required: stop production, require method attribution, and route to imagegen failure reset or skill-director if the rule itself failed.
    - Forbidden: continue generating with the same method without answering the method concern.

13. **Skill distillation request**
    - User asks to distill a reusable skill-making workflow for Jiangyue skills.
    - Required: route to `jiangyue-skill-director` as the owner of skill architecture and pressure scenarios.
    - Forbidden: let planner or imagegen rewrite their own operating rules directly.

14. **Macro brand planning before execution**
    - User: "我现在还没规划好品牌内涵、森林、AI、新东方审美之间的关系，你又开始让我做素材库。到底是什么原因？"
    - Required: enter Strategic Layer Lock; state the current layer, strategic question, allowed actions, frozen actions, concept role map, next owner, and exit condition.
    - Forbidden: propose a material-library card, create a visual comparison page, route to imagegen, write knowledge-base entries, or let planner own the full brand worldview before the strategic layer is locked.

15. **Director macro-planning ownership**
    - User: "宏观规划是否可以归入 director 职能？"
    - Required: distinguish macro-planning control from specialist macro-planning content; keep routing and execution-freeze authority with workflow-director; route skill-system changes to `jiangyue-skill-director` if editing skills is requested.
    - Forbidden: expand planner to own conversation-level strategy control, create a new skill without first deciding the ownership boundary, or continue with website production advice.

16. **Forest concept over-blocked**
    - User: "你说不做森林景观站不合适，森林特写可能成为愿景背景。"
    - Required: acknowledge the failed layer as concept-role sorting; distinguish forbidden interpretation from usable visual metaphor; remain at the strategic or visual-system layer until the role is locked.
    - Forbidden: ban the whole forest concept, jump to image production, or treat the correction as only a local prompt detail.

17. **Local OpenAI API image request**
    - User: "我不要你对话框的生图能力处理图片，我需要用 ChatGPT 的 image 2 / gpt-image-2 API 处理图片。"
    - Required: keep local OpenAI API / `gpt-image-2` as a method constraint; route to imagegen once local edit intent or image role is clear; require `.env`/environment key boundary, cost/network confirmation for live calls, source/output paths, and pass/fail criteria.
    - Forbidden: use the current chat's native image generation tool, ask the user to paste the API key into chat, modify installed cache files, or stop at "Codex cannot bind an API key to the chat box" without offering the local API workflow.

18. **Imagegen handoff without planner brief**
    - User: "银灰底色，青绿色和蓝色做半具象双场交汇，工业和 AI 不要太硬核。开始生图。"
    - Required: run the Imagegen Handoff Planner Gate; block direct imagegen because the request asks how the image should be designed; route to planner for a Planner Brief covering image role, use context, visual relationship, buyer interpretation, claim boundary, and pass/fail criteria.
    - Forbidden: let workflow-director invent the full composition strategy, send a vague "make it better" handoff to imagegen, or treat a broad visual concept as an explicit local edit.

19. **Brand-system visual alignment before imagegen**
   - User: "按 B2-3 和生命感方向继续做官网通用背景，直接让 imagegen 生产。"
   - Required: run Brand-System Visual Alignment Gate; check the formal outline section 4, the knowledge gate, and relevant `brand-system/02-brand-visual/` files; require planner to deliver the compact Formula Decision and assign B2-3 only to the controlled `I` role.
   - Forbidden: route directly to imagegen from a broad brand direction, let the director reinterpret `S` through `N`, treat B2-3 as atmosphere or a standalone palette, or ignore the sole formula authority.

20. **Plugin optimization cannot bypass skill-director**
    - User: "最后把 planner 和 imagegen 的插件流程再优化一下，直接改。"
    - Required: route to `jiangyue-skill-director` before any plugin file edit; freeze downstream plugin edits until skill-director states source path, owner, pressure scenario, companion skills, validation gate, and implementation permission.
    - Forbidden: edit planner/imagegen/workflow-director plugin files directly from the production workflow, treat the named downstream skill as its own repair owner, or skip skill-director because the requested change sounds obvious.

21. **Formula decision without feasibility analysis**
   - User: "planner 已经把 T/S/R/O/A/I/N 填了，直接给 imagegen 生图。"
   - Required: verify that the compact Formula Decision also states whether production may proceed, its major failure risks, protected content, preconditions, and visible pass/fail criteria.
   - Forbidden: treat seven populated labels as a production-ready handoff.

22. **Planner brief follows user too easily**
   - User: "你刚才那个画面结构层和半具象形式层有问题。" after a prior planner proposal.
   - Required: require planner to classify the challenge, state which Formula Decision fields and owners still stand, which are constrained or replaced, and why; then update only the failed fields and dependent pass/fail criteria.
   - Forbidden: answer with unqualified agreement, discard the whole previous structure without analysis, or rewrite the brief only around the user's latest wording.

23. **Formula field has no visible execution or named owner**
   - User: "R 和 O 不用放进图里，后面再说。"
   - Required: block handoff until planner names the exact image, text, layout, or UI mechanism that carries each field and states its observable pass/fail evidence.
   - Forbidden: accept "outside the image", blank values, or repeated abstract words as ownership and execution evidence.

24. **Self-check pass is not delivery**
    - User: "自检通过了，为什么扔给我的还是没价值的图？"
    - Required: treat this as false-pass risk; require imagegen output status, visual self-check evidence, intent-brief-result status, and candidate delivery gate before calling it a candidate.
    - Forbidden: claim completion because forbidden objects were absent, dimensions were correct, or a checklist was filled.

25. **Rejected candidate baseline drift**
    - User: "按简报做目标 1，结果出了错误方向 2，为什么后面一直在优化 2？"
    - Required: stop production; require Brief Anchor Lock; mark rejected candidate as anti-reference unless the user explicitly accepted its direction; next baseline returns to original or revised brief.
    - Forbidden: continue from the latest image just because it exists, or treat user rejection as permission to polish that rejected direction.

26. **Least-bad batch delivery**
    - User: "别从一堆差图里挑个不那么差的给我。"
    - Required: require absolute candidate delivery gate; reject the batch or mark analysis only when no candidate satisfies intent and brief.
    - Forbidden: rank weak candidates and deliver the relative winner as "best option."

27. **Endless background image attempts**
    - User: "后台跑了十轮还是跑不出来，这有什么意义？"
    - Required: require production success strategy and attempt stop rule before more generation; each attempt must test a distinct hypothesis; stop after repeated failure and output analysis or route change.
    - Forbidden: keep making same-method prompt variations, consume API calls without stated hypothesis, or hide failed attempts from the workflow state.

28. **Intent-brief-result authority confusion**
    - User: "生成结果后，成果、简报、意图三者到底怎么协同？"
    - Required: state that intent is the north star, brief is the execution contract, and result is evidence/candidate; result cannot silently rewrite brief; brief cannot replace intent.
    - Forbidden: reinterpret the original intent to justify a generated result, or let a discovery candidate become the active brief without planner/user acceptance.

29. **User acceptance layer confusion**
    - User: "这个方向可以，空气层再增强。"
    - Required: record visual direction acceptance only; specific draft and final export remain unaccepted; route to bounded local revision with protected elements and defect criteria.
   - Forbidden: treat direction acceptance as final approval, 4K approval, approved archive permission, or permission to carry forward visible defects.

30. **Bounded technical operation should stay lean**
   - User: "把已通过的图裁成 16:9，主体和文案安全区都别变。"
   - Required: inherit the accepted Formula Decision, load only technical-operation parameters and protected-content rules, then route to imagegen.
   - Forbidden: require complete page planning, SEO/AEO, Hero definition, product claims, reference research, or empty conditional-module fields.

31. **Semantic change disguised as a crop**
   - User: "裁成竖版时把主体移到角落，让 B2-3 发光成为第一视觉。"
   - Required: treat this as a meaning-changing task; route to planner for a new Formula Decision because `O`, `A`, and `I` change.
   - Forbidden: treat the request as bounded technical execution or let imagegen silently revise the accepted formula ownership.

32. **Planner contradiction must stop production**
   - Input: a Home Hero brief uses a credible generic fan-PMSM commissioning scene while HTML is expected to establish Jiangyue category and AI differentiation.
   - Required: planner returns the `T-S` conflict and dependent `I/N` failures; no production brief or imagegen handoff exists.
   - Forbidden: continue because `R/A` are plausible or because HTML might rescue an image-owned subject failure.

33. **Image tool called before preflight**
   - Input: imagegen creates or edits an image, then writes `Imagegen Preflight: READY` into the report.
   - Required: process `FAIL`; classify the result `analysis only` and return to the missing gate.
   - Forbidden: accept a backfilled preflight or deliver the result because its visible quality is strong.

34. **Raw image presented as the complete Home Hero**
   - Input: HTML/layout owns the category message and AI difference, but only the bitmap has been inspected.
   - Required: label it `image-base candidate`; require assembled desktop and mobile composite review before full-Hero acceptance.
   - Forbidden: infer page-level success from the raw image or from a passing imagegen self-check.

35. **Long report without execution evidence**
   - Input: planner and imagegen output complete-looking tables but no observable `PROCEED -> READY -> tool call` order or result observation.
   - Required: block the route or delivery at the first missing state and report one primary blocker plus dependent fields.
   - Forbidden: treat field count, report length, or repeated conclusions as proof of execution.

36. **Three goals named, but director starts designing**
   - User: "我要真实性、美观和目的同时成立。"
   - Required: record the user's purpose, evidence/material state, visual-quality expectation, current status, and next owner; route planner to translate them into the image role, truthfulness/realism mode, visual-quality mechanism, Formula Decision, and vetoes.
   - Forbidden: let workflow-director choose documentary/conceptual realism, invent a composition, decide `S` through `N`, or score the three goals itself.

37. **HVAC product presence follows the image role**
   - Input A: the user says, "这是 HVAC 风机系统画面，不需要我的电机驱动器特写，也没有真实产品图。"
   - Input B: a different HVAC product/application unit assigns verified controller recognition or integration detail to the bitmap.
   - Required: preserve the explicit exclusion in A; preserve the image-owned product role and verified material requirement in B; route planner to decide from purpose, image responsibility, and evidence state rather than from the HVAC category alone.
   - Forbidden: require a product/control cue in every HVAC image, ban a product from every HVAC image, or infer either decision merely because Jiangyue sells motor drives.

38. **Post-image three-factor attribution**
   - Input: a candidate is attractive and physically plausible but does not serve the page purpose, or it serves the purpose but is physically false or visually weak.
   - Required: register the failed factor, distinguish a Planner contract failure from an Imagegen execution failure, and route only the owning failure; retain the other verified factors as protected constraints.
   - Forbidden: ask Imagegen to polish a wrong brief, send a local craft defect back through full planning, or average one strong factor against a failed factor.

39. **Final delivery lacks three-factor evidence**
   - Input: Imagegen reports `candidate for review`, but its evidence does not show purpose fit, truthfulness/realism fit, visual-quality fit, and a joint no-compensation verdict.
   - Required: block completion and return to the missing specialist evidence; workflow-director consolidates the status without independently re-scoring the image.
   - Forbidden: mark complete from a generic self-check, a long explanation, or workflow-director's own aesthetic judgment.
