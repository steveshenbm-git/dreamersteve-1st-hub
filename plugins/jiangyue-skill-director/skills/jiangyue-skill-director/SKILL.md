---
name: jiangyue-skill-director
description: Use when creating, redesigning, auditing, or repairing Jiangyue Codex skills or skill-bearing plugins, especially after repeated failures, method-choice confusion, unclear skill boundaries, weak self-checks, or pressure-test gaps.
---

# Jiangyue Skill Director

## Core Role

Own the Jiangyue method for designing, improving, and validating skills. Do not replace `skill-creator` or superpowers skills; decide when they are required and what Jiangyue context must be carried into them.

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

## Workflow

1. **Classify the request.**
   Decide whether the user needs a new skill, an existing skill edit, plugin packaging, an AGENTS rule, a reference file, a script, a template, or only analysis.

2. **Build the task ledger.**
   Record the target skill/plugin, source path, user goal, accepted design, open failures, and next required gate.

   ```text
   Jiangyue Skill Work State
   - Target:
   - Source path:
   - Work type:
   - User-approved intent:
   - Open failure(s):
   - Companion skills required:
   - Next gate:
   ```

3. **Decompose the skill problem.**
   Every Jiangyue skill design must separate these layers:

   | Layer | Question |
   |---|---|
   | User intent | What is the real job the user is asking future agents to perform? |
   | Domain boundary | Which Jiangyue skill or domain owns this, and is this skill only routing to it or defining its rules? |
   | Method choice | Which production methods must future agents choose among? |
   | Companion route | Which other skill or superpower is mandatory at each point? |
   | Freedom level | Which steps are high, medium, or low freedom? |
   | Failure gate | What observable or behavioral failure forces a reset? |
   | Validation | What proves the skill worked rather than merely sounding correct? |

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

6. **Set freedom levels.**

   | Freedom level | Use for | Jiangyue examples |
   |---|---|---|
   | High | Strategy exploration where several answers are acceptable | 2-3 skill architecture options |
   | Medium | Reusable templates with limited variation | brief templates, decision tables, handoff checklists |
   | Low | Fragile behavior, repeated failures, source boundaries, final gates | no cache edits, approval gates, pressure tests before skill approval |

7. **Write pressure scenarios before approving the skill.**
   Use [references/pressure-scenarios.md](references/pressure-scenarios.md) when creating or revising Jiangyue skills. If subagents are not explicitly authorized, use observed failures from the current conversation as baseline evidence and state that live subagent forward-testing was not run.

8. **Validate before delivery.**
   A Jiangyue skill is not complete until:
   - frontmatter has only `name` and `description`
   - description describes triggers, not workflow shortcuts
   - required companion skills are named with clear conditions
   - pressure scenarios exist for the skill-design failure class being fixed
   - no scaffold placeholders remain
   - skill validation and plugin validation pass when applicable

## Domain Rule Boundary

Keep this skill focused on how Jiangyue skills are designed, routed, tested, and repaired. Do not embed detailed production rules from downstream domains.

| Rule type | Belongs here? | Where the detailed rule belongs |
|---|---|---|
| Complex request must be split into subtasks, each with one primary method | Yes | `jiangyue-skill-director` |
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
- must keep / must change / must avoid
- artifact type selected
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
- no pressure scenario for a new or revised skill
- claiming a skill is fixed without validation
