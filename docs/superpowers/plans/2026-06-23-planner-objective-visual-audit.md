# Planner Objective Visual Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strengthen the Jiangyue Website Planner skill so it locks task intent, requires visual evidence for visual work, audits the whole workflow after repeated failures, and triggers failure reset after two failed rework rounds.

**Architecture:** Keep essential hard gates in `SKILL.md` so they are always loaded. Put the detailed operating procedure in a new reference file and link it from `SKILL.md` for progressive disclosure.

**Tech Stack:** Markdown skill files inside the Jiangyue Codex plugin marketplace repository.

---

### Task 1: Add Objective And Visual Audit Rules

**Files:**
- Modify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/SKILL.md`
- Create: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/objective-and-visual-audit.md`

- [ ] **Step 1: Add core gates to SKILL.md**

Add four short sections after the `Planner Brief Contract` section:

```markdown
## Task Intent Lock
...

## Mandatory Visual Evidence Gate
...

## Whole Workflow Audit
...

## Two-Failure Reset Rule
...
```

Expected behavior: every planner run must lock the real task objective and evidence before producing recommendations.

- [ ] **Step 2: Add detailed reference**

Create `references/objective-and-visual-audit.md` with:

```markdown
# Objective And Visual Audit

## Purpose
...
```

Expected behavior: the reference defines the complete procedure for task intent, visual evidence, whole workflow audit, failure reset, and prohibited shortcuts.

- [ ] **Step 3: Link the reference from SKILL.md**

Add a sentence near the system workflow section:

```markdown
Read [references/objective-and-visual-audit.md](references/objective-and-visual-audit.md) when the task involves visual judgment, repeated rework, brand direction, image review, or user correction about process quality.
```

Expected behavior: the detailed procedure is discoverable without bloating the main skill.

### Task 2: Verify And Commit

**Files:**
- Verify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/SKILL.md`
- Verify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/objective-and-visual-audit.md`

- [ ] **Step 1: Verify required terms exist**

Run:

```bash
grep -R "Task Intent Lock\\|Mandatory Visual Evidence Gate\\|Whole Workflow Audit\\|Two-Failure Reset Rule\\|Failure Reset" plugins/jiangyue-website-planner/skills/jiangyue-website-planner
```

Expected: all gate names appear in the planner skill files.

- [ ] **Step 2: Verify repository diff**

Run:

```bash
git diff -- plugins/jiangyue-website-planner/skills/jiangyue-website-planner docs/superpowers/plans/2026-06-23-planner-objective-visual-audit.md
```

Expected: only planner skill files and this plan are changed.

- [ ] **Step 3: Commit without push**

Run:

```bash
git add plugins/jiangyue-website-planner/skills/jiangyue-website-planner/SKILL.md plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/objective-and-visual-audit.md docs/superpowers/plans/2026-06-23-planner-objective-visual-audit.md
git commit -m "强化 planner 目标锁定与视觉审计" -m "加入任务意图锁定、强制视觉依据、整体流程审计和两次失败重置规则。明确视觉类任务不能用文字说明、文件存在或逻辑解释替代可见结果判断。"
```

Expected: one local commit on `improve-flow`; no push.

