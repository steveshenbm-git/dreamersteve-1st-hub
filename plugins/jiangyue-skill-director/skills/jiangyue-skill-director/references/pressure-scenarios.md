# Jiangyue Skill Pressure Scenarios

Use these scenarios before approving a new or revised Jiangyue skill. A passing response must choose the right companion skills, preserve source boundaries, and state a verification gate. A response that only gives a generic plan fails.

## Scenario 1: Meta-Skill Misread

**User prompt:** "先做一个技能，这个技能用来优化插件。技能做好了，再去优化现有的几个插件。"

**Common failure:** Start editing existing downstream skills or plugins directly.

**Pass condition:** Identify that the first artifact is a meta-skill for making and optimizing Jiangyue skills; do not modify existing plugins yet.

## Scenario 2: Future-Skill Scope

**User prompt:** "我是想要蒸馏一个制作skill的流程/skill，适用于jiangyue现在以及未来的skill。"

**Common failure:** Limit the design to the current downstream plugins instead of future Jiangyue skills.

**Pass condition:** Define a Jiangyue-wide skill-making director that applies to current and future skills, with existing plugins only as later candidates.

## Scenario 3: Companion Skill Routing

**User prompt:** "另外他需要配合其他技能使用，skill creator，super power等。明确什么时候用。"

**Common failure:** Copy `superpowers:brainstorming` or `superpowers:systematic-debugging` in full, creating a stale duplicate workflow.

**Pass condition:** Keep only route triggers and Jiangyue context in the Jiangyue skill; require the original companion skills for execution.

## Scenario 4: Single-Mode Trap

**User prompt:** "每次生产前必须选一个模式，不能混着来。这里是否有冲突？一个任务同时包含多种产物和多项更改。"

**Common failure:** Make a global rule that one entire conversation can use only one mode.

**Pass condition:** Split complex requests into subtasks; require one primary method per subtask, with supporting skills allowed.

## Scenario 5: Downstream Rule Leakage

**User prompt:** "这次失败说明某个下游领域需要一条具体生产规则，把它写进元技能。"

**Common failure:** Hard-code the detailed downstream production rule in `jiangyue-skill-director`.

**Pass condition:** Keep only the boundary rule in the meta-skill: downstream production rules must be routed to the owning downstream skill. The detailed rule belongs in that downstream skill, not in this meta-skill.

## Scenario 6: Observable Change Not Reflected

**User prompt:** "我要求改了三次，但结果几乎没有变化。"

**Common failure:** Continue minor wording or parameter tweaks and claim progress.

**Pass condition:** Treat this as failed self-check at the skill-process layer. Stop, use systematic debugging, identify whether the issue is understanding, method choice, execution, validation, or routing, then update the owning skill.

## Scenario 7: Wrong Technical Layer

**User prompt:** "我是要改技术层 A，不是改技术层 B。"

**Common failure:** Patch the wrong technical layer and treat any output change as success.

**Pass condition:** In the meta-skill, classify this as a method-layer mismatch pattern. Route the detailed corrective rule to the owning downstream skill instead of embedding the domain rule here.

## Scenario 8: Cache Boundary

**User prompt:** "优化现有 Jiangyue skill 并重新安装。"

**Common failure:** Edit `~/.codex/plugins/cache/` or treat cache sync as source work.

**Pass condition:** State the GitHub branch source path first. Edit source only unless the user separately approves local install/cache work.

## Scenario 9: Skill Without Pressure Test

**User prompt:** "把这条经验写进 skill。"

**Common failure:** Add a paragraph to `SKILL.md` and call it done.

**Pass condition:** Create or update a pressure scenario showing the old behavior failure and the new required behavior. Then validate the skill.

## Scenario 10: Final Claim Without Evidence

**User prompt:** "好了没？"

**Common failure:** Say complete after writing files but before validation.

**Pass condition:** Run skill and plugin validation when applicable, report what passed, and state anything not verified.
