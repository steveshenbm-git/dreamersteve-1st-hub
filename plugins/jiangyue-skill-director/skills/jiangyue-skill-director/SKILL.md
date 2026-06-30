---
name: jiangyue-skill-director
description: Use when creating, redesigning, auditing, or repairing Jiangyue Codex skills or skill-bearing plugins, especially after repeated failures, method-choice confusion, unclear skill boundaries, weak self-checks, or pressure-test gaps.
---

# Jiangyue Skill Director

## Core Role

Own the Jiangyue method for designing, improving, and validating skills. Do not replace `skill-creator` or superpowers skills; decide when they are required and what Jiangyue context must be carried into them.

Do not replace Jiangyue work skills or `jiangyue-website-workflow-director`. This skill governs skill-system design and repair. User-facing multi-skill production work stays owned by the workflow director.

## Source Boundary

For Jiangyue plugin development, edit only the GitHub branch working tree unless the user explicitly asks for local installation or cache work. Do not modify `~/.codex/plugins/cache/`.

Before edits, state:
- exact source path to edit
- files likely affected
- risk level
- rollback path

## Required Companion Skills

Use the first matching required route. If multiple routes apply, use all required routes in the listed order.

| Condition | Required route | Jiangyue context to carry |
|---|---|---|
| New skill, major skill redesign, unclear boundary, or method system not yet agreed | `superpowers:brainstorming` | skill purpose, target failures, candidate boundaries, 2-3 design options |
| Creating or editing any `SKILL.md` | `superpowers:writing-skills` then `skill-creator` | pressure scenarios, trigger wording, degree-of-freedom decisions, resource split |
| User says the agent misunderstood, same issue repeats, or a rule change did not affect behavior | `superpowers:systematic-debugging` before another edit | root-cause layer, failed assumption, evidence, next hypothesis |
| Multi-file implementation or plugin-wide change after design is approved | `superpowers:writing-plans` | approved design, file list, tasks, validation commands |
| New plugin folder, plugin manifest, marketplace entry, install/update flow | `plugin-creator` | plugin name, marketplace path, manifest metadata, install boundary |
| Final delivery, "done" claim, commit, or install recommendation | `superpowers:verification-before-completion` | validation output, remaining unverified items |

Do not copy full superpowers workflows into this skill. Keep only the route trigger, Jiangyue interpretation, and required handoff context.

## Jiangyue Skill Roles

Separate the control layer before designing or editing any Jiangyue skill.

| Role | Owns | Must not own |
|---|---|---|
| `jiangyue-website-workflow-director` | User-facing conversation, intent analysis, intent lock, task decomposition, routing, active task state, failure reset, final delivery gates | Specialist production methods or skill-authoring mechanics |
| Work skills | Specialist execution inside a locked task package, local method choice, local quality check, failure feedback | Full conversation ownership, cross-skill routing, rewriting their own rules |
| `jiangyue-skill-director` | Skill architecture, rule ownership, freedom levels, pressure scenarios, skill repair, plugin/source boundaries | Daily production workflow or downstream domain standards |
| Knowledge curator | Confirmed facts, reusable preferences, approved standards, failures worth remembering | Unconfirmed rules or live production routing |

If a request needs several work skills, design the flow around `jiangyue-website-workflow-director` first. Work skills may perform local ownership checks, but they should not independently re-run the whole intent analysis unless the workflow handoff is missing or contradictory.

## Baseline Design Gates

Every Jiangyue work skill must be designed against these gates. For a single-skill task, the owning skill can handle most gates locally. For a complex multi-skill workflow, `jiangyue-website-workflow-director` owns the conversation-level gates and work skills own only their local checks.

| Gate | Required decision | Conversation-level owner | Work-skill responsibility |
|---|---|---|---|
| Intent analysis | What real job is the user asking for, beyond literal wording? | `workflow-director` for multi-skill work; `skill-director` for skill-system work | Confirm the received subtask matches the local domain |
| Intent lock | What must keep, must change, must avoid, and what counts as accepted? | `workflow-director` | Refuse or return unclear handoffs; do not invent acceptance criteria |
| Task ownership | Which skill, artifact, or knowledge store owns the next decision? | `workflow-director` for production; `skill-director` for skill architecture | Execute only owned work; return non-owned gaps |
| Subtask decomposition | What are the separable subtasks and dependencies? | `workflow-director` for production flow; `skill-director` for skill-edit flow | Handle the assigned subtask only |
| Method gate | Which primary method should be used for each subtask, and what methods are rejected? | `workflow-director` chooses route; specialist chooses domain method if unlocked | Choose specialist method within locked constraints |
| Rule strength | Is the rule hard, low freedom, medium freedom, soft, autonomous, or ask-user? | `skill-director` when writing skills | Follow the declared rule strength; flag mismatch |
| Active inquiry | What missing decision requires one question before execution? | `workflow-director` for user-facing questions | Ask only local clarification or return to `workflow-director` |
| Source boundary | Which source path, cache path, knowledge base, or output root is allowed? | `workflow-director` or `skill-director`, depending on task type | Do not cross source boundaries silently |
| Pre-execution state | What state must be recorded before work starts? | `workflow-director` or `skill-director` | Confirm local input package is sufficient |
| Validation gate | What evidence proves success? | `workflow-director` for final delivery; specialist for local output | Verify local output and report limits |
| Failure reset | What signal stops normal production and triggers root-cause debugging? | `workflow-director` for production; `skill-director` for skill failures | Stop retrying and return failure evidence |
| Self-evolution interface | What improvement candidate should be sent to curator or `skill-director`? | `workflow-director` routes improvement; `skill-director` repairs skills | Produce evidence, failed layer, and proposed owning artifact |

Never design a work skill so it owns the whole multi-skill conversation. It can detect missing input, reject a bad handoff, and report failure evidence, but `workflow-director` decides the next user-facing route.

## Workflow

1. **Classify the request.**
   Decide whether the user needs a new skill, an existing skill edit, plugin packaging, an AGENTS rule, a reference file, a script, a template, or only analysis.

2. **Build the task ledger.**
   Record the target skill/plugin, source path, user goal, accepted design, open failures, role owners, and next required gate.

   ```text
   Jiangyue Skill Work State
   - Target:
   - Source path:
   - Work type:
   - Conversation owner:
   - Specialist owner:
   - User-approved intent:
   - Intent lock:
     - Must keep:
     - Must change:
     - Must avoid:
     - Acceptance:
   - Open failure(s):
   - Companion skills required:
   - Rule strength / inquiry gate:
   - Next gate:
   ```

3. **Run the baseline design gates.**
   Do not begin writing or editing a skill until the relevant gates are answered. Use the table above, then summarize the result as:

   ```text
   Gate Summary
   - Intent:
   - Locked acceptance:
   - Conversation owner:
   - Specialist owner:
   - Owning artifact:
   - Subtasks:
   - Method gates:
   - Rule strength:
   - Ask-user trigger:
   - Source boundary:
   - Validation:
   - Failure reset trigger:
   - Self-evolution route:
   ```

4. **Choose the artifact type.**
   Do not force every improvement into `SKILL.md`.

   | Artifact | Use when | Avoid when |
   |---|---|---|
   | `SKILL.md` | Future agents need judgment, routing, or a repeatable workflow | A simple static project rule is enough |
   | `references/*.md` | Detailed tables, templates, examples, pressure scenarios, or owning-skill domain rules would bloat that skill's `SKILL.md` | The content is core enough to fit in the main workflow |
   | `scripts/` | Deterministic, repeated, error-prone operations should be executable | Judgment or creative method choice is required |
   | `assets/` | Reusable templates, fonts, examples, or boilerplate are copied into outputs | The asset is one-off |
   | AGENTS.md | Stable project-wide policy applies before skill routing | The rule is domain-specific and should trigger only sometimes |
   | Plugin | The skill needs marketplace packaging, installation, or plugin metadata | A local personal skill is enough |

5. **Set the method mode per skill subtask.**
   A complex request can contain multiple subtasks. Each subtask must choose one primary method and may name supporting skills. Do not require one mode for the whole conversation. This is a general skill-design rule, not a downstream production rule.

   | Subtask type | Primary method | Supporting route |
   |---|---|---|
   | Skill boundary or design | Structured design discussion | `superpowers:brainstorming` |
   | Skill writing or revision | Skill TDD with pressure scenarios | `superpowers:writing-skills`, `skill-creator` |
   | Repeated failure or instruction not reflected in output | Root-cause debugging | `superpowers:systematic-debugging` |
   | Plugin package or marketplace change | Plugin scaffold/update | `plugin-creator` |
   | Downstream domain skill design | Method-selection gate before downstream work | Route to the owning specialist skill for domain rules |
   | Deterministic repeated operation | Scripted operation | Include or call a script only when exact and repeatable |

6. **Set rule strength and freedom level.**
   Every rule added to a Jiangyue skill must declare how strict it is. Do not turn every preference into a hard rule.

   | Rule strength | Use when | Skill-writing behavior |
   |---|---|---|
   | Hard rule | Violation causes source risk, repeated failure, wrong owner, false completion, or user-forbidden behavior | Use MUST/STOP language and add pressure scenario coverage |
   | Low freedom | Fragile repeated sequence has a correct order but small parameters may vary | Use short checklist, required fields, or script with limited parameters |
   | Medium freedom | A preferred pattern exists but context still matters | Use decision table, template, or bounded options |
   | Soft rule | It is a style, quality, or strategic preference with multiple acceptable answers | Use preference language and require judgment |
   | Skill autonomy | The specialist skill has enough context and multiple valid methods | Define acceptance criteria, not the method |
   | Ask user | Missing information changes owner, method, output type, risk, or acceptance | Ask one necessary question or return to workflow director |

7. **Design work-skill self-improvement hooks.**
   Work skills must not rewrite themselves during production. Give each work skill a local hook that can:
   - correct the current task when the failure is local and verifiable
   - return missing or contradictory task-package fields to `workflow-director`
   - prepare a curator note when the failure reveals reusable confirmed knowledge
   - prepare a `jiangyue-skill-director` handoff when the failure reveals skill-design or repeated workflow failure

   Use this handoff shape:

   ```text
   Work Skill Improvement Candidate
   - Failure:
   - Evidence:
   - Failed layer:
   - Current rule or gap:
   - Suggested owning artifact:
   - Needs curator entry: yes/no
   - Needs skill-director repair: yes/no
   - Validation or pressure scenario needed:
   ```

8. **Write pressure scenarios before approving the skill.**
   Use [references/pressure-scenarios.md](references/pressure-scenarios.md) when creating or revising Jiangyue skills. If subagents are not explicitly authorized, use observed failures from the current conversation as baseline evidence and state that live subagent forward-testing was not run.

9. **Validate before delivery.**
   A Jiangyue skill is not complete until:
   - frontmatter has only `name` and `description`
   - description describes triggers, not workflow shortcuts
   - required companion skills are named with clear conditions
   - role ownership is clear when the skill participates in multi-skill workflows
   - hard rules, low-freedom rules, soft rules, autonomy, and user-inquiry gates are separated where relevant
   - pressure scenarios exist for the skill-design failure class being fixed
   - no scaffold placeholders remain
   - skill validation and plugin validation pass when applicable

## Self-Optimization Loop

Treat every skill failure as a process failure until proven otherwise. Do not rely on memory, apology, or intent.

1. **Detect the failure signal.**
   Use this loop when the user says the agent misunderstood, a change had no effect, the same issue repeats, or the skill routed work to the wrong place.

2. **Name the failed layer.**
   Classify the failure as scope, conversation owner, domain ownership, method choice, companion routing, artifact type, rule strength, freedom level, inquiry gate, validation, or source boundary.

3. **Change the smallest owning artifact.**
   Update only the artifact that owns the failed layer: `workflow-director`, this skill, an owning downstream skill, a reference, a script, AGENTS.md, plugin metadata, the knowledge base, or a pressure scenario.

4. **Run the matching pressure scenario.**
   If no scenario covers the failure, write the scenario first. Do not approve the skill change from explanation alone.

5. **Report residual risk.**
   State what was verified, what could not be verified, and whether the change needs live forward-testing.

## Domain Rule Boundary

Keep this skill focused on how Jiangyue skills are designed, routed, tested, and repaired. Do not embed detailed production rules from downstream domains.

| Rule type | Belongs here? | Where the detailed rule belongs |
|---|---|---|
| Complex request must be split into subtasks, each with one primary method | Yes | `jiangyue-skill-director` |
| Multi-skill production flow must be user-facing through `workflow-director` | Yes | `jiangyue-skill-director` and `jiangyue-website-workflow-director` |
| Work skills need a local self-improvement handoff, not self-rewrite authority | Yes | `jiangyue-skill-director`; each owning work skill implements its local hook |
| Specific downstream domain or production rule | No, only as a routing target or boundary test | The owning downstream skill |
| Specific downstream quality criteria | No, only route and handoff | The owning downstream skill |
| Source/cache boundary for Jiangyue plugin work | Yes | `jiangyue-skill-director` and Jiangyue workflow skills |

When a repeated failure reveals a downstream rule, this skill may record the boundary failure, but the actual domain rule must be added to the owning downstream skill.

## Failure Reset

Stop normal production and use `superpowers:systematic-debugging` when any condition is true:
- user says the task was misunderstood
- same named defect remains after two attempts
- a requested observable change does not appear in the result
- a rule was added but behavior did not change
- the agent continues with the same method after the user rejected that method
- a complex task was flattened into one mode and lost part of the request
- a work skill starts owning the whole conversation instead of returning control to `workflow-director`
- the agent cannot say whether a new rule is hard, low-freedom, soft, autonomous, or requires asking

Root-cause statement format:

```text
Failure layer:
Evidence:
Wrong assumption:
Why the previous method could not solve it:
Next method gate:
Validation that must pass:
```

## Handoff Package

Every handoff from this skill to another skill must include:
- user original words or concrete failure quote
- target skill/plugin and source path
- conversation owner and specialist owner
- must keep / must change / must avoid
- artifact type selected
- rule strength or inquiry gate selected
- companion skills required
- pressure scenarios or validation gates
- whether the next step is design, edit, validation, install, or commit

## Red Flags

If any of these appear, stop and re-route:
- "Just add a rule" without identifying the failure layer
- "Use one mode for the whole request" applied to a multi-subtask request
- "It is basically the same" when the user asked for an observable change
- editing installed plugin cache instead of source
- rewriting a superpower workflow instead of invoking it
- making a work skill responsible for user-facing multi-skill orchestration
- allowing a work skill to rewrite itself during production instead of producing an improvement candidate
- adding a rule without deciding hard rule, low freedom, medium freedom, soft rule, autonomy, or ask-user gate
- no pressure scenario for a new or revised skill
- claiming a skill is fixed without validation
