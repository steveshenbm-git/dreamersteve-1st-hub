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
   - Required: use skill-creator and writing-skills; define pressure scenarios before editing.
   - Forbidden: patch wording without validation criteria.

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
