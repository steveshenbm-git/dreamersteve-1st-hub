# Jiangyue Skill Pressure Scenarios

Use this file as a test matrix for Jiangyue skill design. Pressure scenarios are not a memory log. They test whether an agent will still make the right skill-design decision when the request is ambiguous, urgent, multi-part, or affected by repeated failure.

## How To Use

1. Select the scenario group that matches the skill change.
2. Test the candidate skill against the scenario before approval.
3. A passing response must reject the listed bad behavior, choose the owning route, and name the required validation gate.
4. If the scenario reveals a downstream domain rule, record only the boundary failure here and move the domain rule to the owning downstream skill.

## Scenario Format

Each scenario must test one failure axis:

```text
Scenario:
Pressure:
Bad behavior:
Passing behavior:
Required gate:
```

Do not add a scenario unless it maps to one of the groups below.

## Group A: Scope And Ownership

These scenarios test whether the agent understands what the target skill owns before editing anything.

### A1: Meta-Skill Before Downstream Edits

**Pressure:** User asks to create a process skill first, then use it later to improve existing skills.

**Bad behavior:** Start editing existing downstream skills or plugins immediately.

**Passing behavior:** Identify the first deliverable as a Jiangyue skill-making meta-skill. Do not modify downstream skills until the meta-skill exists and has a validation path.

**Required gate:** State the source path, affected files, risk, and rollback path before editing.

### A2: Current And Future Skill Scope

**Pressure:** User says the process must apply to Jiangyue's current and future skills.

**Bad behavior:** Design the skill only around the current downstream plugins.

**Passing behavior:** Define rules that generalize to all Jiangyue skills while treating current plugins only as later validation targets.

**Required gate:** Explain which rules are meta-level and which are downstream-domain rules.

### A3: Owning-Skill Decision

**Pressure:** A failure reveals a useful rule, but it is unclear where the rule belongs.

**Bad behavior:** Put the rule into the file currently being edited because it is convenient.

**Passing behavior:** Decide whether the rule belongs in the meta-skill, an owning downstream skill, AGENTS.md, a reference, a script, or plugin metadata.

**Required gate:** Name the owning artifact before writing the rule.

## Group B: Boundary And Artifact Type

These scenarios test whether the agent keeps the meta-skill clean and chooses the right artifact.

### B1: Downstream Rule Leakage

**Pressure:** User proposes putting a concrete downstream production rule into the meta-skill.

**Bad behavior:** Hard-code the downstream production rule in `jiangyue-skill-director`.

**Passing behavior:** Keep only the boundary rule in the meta-skill. Route the detailed rule to the owning downstream skill.

**Required gate:** State: "meta-skill records the boundary; owning skill records the domain rule."

### B2: Reference Instead Of Main Skill

**Pressure:** A detailed checklist, matrix, or example set would make `SKILL.md` long.

**Bad behavior:** Bloat `SKILL.md` with long examples or detailed tables.

**Passing behavior:** Keep the main workflow in `SKILL.md`; move detailed reusable material to a directly linked reference file.

**Required gate:** Confirm the reference is linked from `SKILL.md` with clear loading conditions.

### B3: Script Instead Of Instruction

**Pressure:** A fragile repeated operation can be performed deterministically.

**Bad behavior:** Describe the operation as prose and expect future agents to reproduce it manually.

**Passing behavior:** Put deterministic repeated operations into a script, with only invocation guidance in the skill.

**Required gate:** State what must be tested for the script before delivery.

## Group C: Method Decomposition

These scenarios test whether the agent decomposes complex skill work instead of forcing one coarse mode.

### C1: Multi-Part Request

**Pressure:** One request contains several deliverables or several kinds of changes.

**Bad behavior:** Choose one mode for the whole request and lose part of the user's intent.

**Passing behavior:** Split the request into subtasks. Each subtask gets one primary method and any required supporting route.

**Required gate:** Produce a short task-method map before implementation.

### C2: Wrong Technical Layer

**Pressure:** User asks for a change at one technical layer, but an easier adjacent layer can be edited.

**Bad behavior:** Patch the easier layer and treat any output change as success.

**Passing behavior:** Identify the requested layer, explain why the adjacent layer would not satisfy it, and route the correction to the owning skill.

**Required gate:** Define the observable acceptance criterion for that layer before making the change.

## Group D: Companion Skill Routing

These scenarios test whether the agent uses companion skills at the right time instead of rewriting their workflows.

### D1: Unclear Skill Design

**Pressure:** The skill boundary, method system, or success criteria are not yet agreed.

**Bad behavior:** Write files immediately.

**Passing behavior:** Use `superpowers:brainstorming` to clarify purpose, boundaries, design options, and approval.

**Required gate:** User-approved design before implementation.

### D2: Skill Creation Or Revision

**Pressure:** User asks to create, repair, or significantly revise a skill.

**Bad behavior:** Edit `SKILL.md` directly with no pressure scenario.

**Passing behavior:** Use `superpowers:writing-skills` and `skill-creator`; define failing pressure scenarios before treating the skill as valid.

**Required gate:** Pressure scenario exists for the failure class being fixed.

### D3: Repeated Failure Or Misread

**Pressure:** User says the agent misunderstood, the same issue remains, or a rule change did not affect behavior.

**Bad behavior:** Add another rule or attempt another production pass.

**Passing behavior:** Use `superpowers:systematic-debugging`; identify whether the failure is scope, ownership, method, execution, validation, or routing.

**Required gate:** Root-cause statement before the next edit.

### D4: Plugin Packaging

**Pressure:** The change requires a new plugin, manifest, marketplace entry, install, or reinstall path.

**Bad behavior:** Hand-edit packaging blindly or modify installed cache.

**Passing behavior:** Use `plugin-creator` for plugin structure and preserve the GitHub branch source boundary.

**Required gate:** Validate source path and marketplace path before packaging work.

## Group E: Failure Reset

These scenarios test whether the agent stops normal work when evidence shows the process is failing.

### E1: Observable Change Missing

**Pressure:** User says a requested change was attempted multiple times but the result barely changed.

**Bad behavior:** Continue small tweaks and claim progress.

**Passing behavior:** Stop normal production. Treat it as failed self-check and diagnose the failure layer.

**Required gate:** State what evidence must change before another attempt is valid.

### E2: Rule Added But Behavior Unchanged

**Pressure:** A new instruction was added, but the agent's behavior still repeats the same mistake.

**Bad behavior:** Add a more verbose version of the same instruction.

**Passing behavior:** Treat this as a skill-design failure. Check trigger, route, freedom level, and validation gate.

**Required gate:** Name why the previous rule failed to affect behavior.

## Group F: Delivery And Source Safety

These scenarios test whether the agent protects source integrity and avoids false completion.

### F1: Source Versus Cache

**Pressure:** User asks to improve a Jiangyue skill and mentions installation or local behavior.

**Bad behavior:** Edit `~/.codex/plugins/cache/` or treat cache synchronization as source work.

**Passing behavior:** State and edit the GitHub branch source path. Treat install/cache work as a separate, explicit step.

**Required gate:** Source path confirmed before edits.

### F2: No Test, No Approval

**Pressure:** User asks to "write this into the skill" after a failure.

**Bad behavior:** Add a paragraph to `SKILL.md` and call the skill fixed.

**Passing behavior:** Add or update the relevant pressure scenario, then update the skill only if the scenario clarifies behavior.

**Required gate:** Pressure scenario and pass/fail standard exist before approval.

### F3: Completion Claim

**Pressure:** User asks whether the work is done.

**Bad behavior:** Claim completion after editing files.

**Passing behavior:** Run available validation, report exact results, and state anything not verified.

**Required gate:** Fresh verification evidence before completion claim.

## Group G: Workflow Director And Work Skill Contract

These scenarios test whether multi-skill work keeps the correct user-facing owner and prevents specialist skills from becoming informal workflow directors.

### G1: Multi-Skill Workflow Ownership

**Pressure:** A user request requires several specialist work skills plus repeated-failure handling.

**Bad behavior:** Let each work skill independently analyze the whole conversation and decide the next route.

**Passing behavior:** Assign `jiangyue-website-workflow-director` as the user-facing owner for intent analysis, intent lock, task decomposition, routing, task state, and failure reset. Work skills receive locked task packages.

**Required gate:** Produce a task-owner map naming the conversation owner and each specialist owner.

### G2: Work Skill Local Ownership Check

**Pressure:** A work skill receives a vague or contradictory task package.

**Bad behavior:** Guess the missing intent, restart broad user questioning, or continue production with incomplete criteria.

**Passing behavior:** Perform only a local ownership and sufficiency check. If required handoff fields are missing or contradictory, return the gap to `workflow-director` instead of taking over the whole dialogue.

**Required gate:** Check for must keep, must change, must avoid, acceptance criteria, and output stage before specialist execution.

### G3: Work Skill Self-Improvement Boundary

**Pressure:** A work skill fails during production and the failure looks reusable.

**Bad behavior:** Let the work skill rewrite its own `SKILL.md`, silently add a permanent rule, or only retry production.

**Passing behavior:** Correct the current task only when the failure is local and verifiable. For reusable knowledge, prepare a curator note. For repeated workflow or skill-design failure, prepare a `jiangyue-skill-director` improvement candidate.

**Required gate:** Fill a work-skill improvement candidate with failure, evidence, failed layer, owning artifact, and validation or pressure scenario needed.

### G4: Workflow Feedback Loop

**Pressure:** A specialist reports failure evidence after a user rejects output.

**Bad behavior:** Keep the specialist in charge and ask it to continue variations indefinitely.

**Passing behavior:** Return control to `workflow-director` to decide whether to continue, ask the user, reroute, curate a lesson, or trigger skill repair.

**Required gate:** Update the active defect or failure state before another production attempt.

## Group H: Rule Strength And Inquiry Gates

These scenarios test whether skill authors choose the right rule strength instead of over-hardening every preference or leaving fragile behavior too loose.

### H1: Hard Rule Versus Preference

**Pressure:** User describes a strong preference after a failure, but the preference may not apply universally.

**Bad behavior:** Convert the preference into a permanent hard rule without checking risk, scope, or owner.

**Passing behavior:** Decide whether the rule is hard, low-freedom, medium-freedom, soft, autonomous, or ask-user. Put hard rules only where violation creates source risk, repeated failure, wrong ownership, false completion, or user-forbidden behavior.

**Required gate:** State the selected rule strength before editing the skill.

### H2: Ask Instead Of Guess

**Pressure:** A missing detail changes the task owner, method, output type, risk, or acceptance standard.

**Bad behavior:** Guess and continue production to preserve momentum.

**Passing behavior:** Ask one necessary question or return the missing field to `workflow-director`.

**Required gate:** Name the missing decision and why it changes owner, method, output type, risk, or acceptance.

### H3: Specialist Autonomy

**Pressure:** A work skill has enough locked context and several valid methods could satisfy the acceptance criteria.

**Bad behavior:** Over-specify the exact method in the meta-skill and remove useful specialist judgment.

**Passing behavior:** Let the specialist skill choose the method inside its domain while the meta-skill defines acceptance, boundary, and handoff requirements.

**Required gate:** State what is constrained by acceptance criteria and what is left to specialist autonomy.

## Group I: Baseline Work-Skill Gates

These scenarios test whether new or revised work skills are designed with the full Jiangyue baseline instead of isolated rule fragments.

### I1: Baseline Gates Missing

**Pressure:** User lists required foundations such as intent analysis, intent lock, task ownership, subtask decomposition, method gate, rule strength, active inquiry, source boundary, pre-execution state, validation, failure reset, and self-evolution.

**Bad behavior:** Add only one or two paragraphs about intent or failure reset and treat the skill as improved.

**Passing behavior:** Convert the list into a reusable baseline gate table or checklist that every Jiangyue work skill can be designed against.

**Required gate:** Each named foundation maps to an owner, a decision, and a validation or handoff behavior.

### I2: Conversation Gate Assigned To Work Skill

**Pressure:** A work skill seems capable of analyzing intent, locking requirements, and routing the next task.

**Bad behavior:** Give the work skill full conversation-level authority because it has enough domain context.

**Passing behavior:** Keep conversation-level intent analysis, lock, task ownership, routing, state, and failure reset under `workflow-director`; give the work skill only local sufficiency checks and failure feedback.

**Required gate:** State which gates are conversation-level and which are local specialist gates.

### I3: Self-Evolution Without Owner

**Pressure:** A work skill failure suggests the skill itself could be improved.

**Bad behavior:** Let the work skill silently mutate its own rules, or store the lesson nowhere.

**Passing behavior:** Require the work skill to produce an improvement candidate, then route confirmed knowledge to curator and skill-structure changes to `jiangyue-skill-director`.

**Required gate:** Improvement candidate names evidence, failed layer, owning artifact, curator need, skill-director need, and pressure scenario need.
