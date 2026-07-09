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
    - Required: run Brand-System Visual Alignment Gate; check `brand-system/00-knowledge-gate/jiangyue-knowledge-gate.md` and relevant `brand-system/02-brand-visual/` files; require planner brief to state how the direction complies with calm industrial New Eastern style, B2-3 controlled status color, negative-space composition, material/lighting behavior, and negative visual directions.
    - Forbidden: route directly to imagegen from a broad brand direction, treat B2-3 as a standalone palette, ignore brand-system visual planning, or produce a visual that conflicts with formal brand-system files.

20. **Plugin optimization cannot bypass skill-director**
    - User: "最后把 planner 和 imagegen 的插件流程再优化一下，直接改。"
    - Required: route to `jiangyue-skill-director` before any plugin file edit; freeze downstream plugin edits until skill-director states source path, owner, pressure scenario, companion skills, validation gate, and implementation permission.
    - Forbidden: edit planner/imagegen/workflow-director plugin files directly from the production workflow, treat the named downstream skill as its own repair owner, or skip skill-director because the requested change sounds obvious.
