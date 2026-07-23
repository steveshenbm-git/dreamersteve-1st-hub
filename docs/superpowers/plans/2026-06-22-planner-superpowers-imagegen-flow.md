# Planner Superpowers Imagegen Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tighten the Jiangyue Website Planner skill so it coordinates cleanly with superpowers process gates and the lightweight Imagegen execution skill.

**Architecture:** Keep planner as a concise strategy skill. Add explicit flow ownership, define the Planner Brief as the strategy contract for imagegen, route feedback through planner/imagegen boundaries, and move detailed cross-skill workflow notes into one reference file.

**Tech Stack:** Codex skill Markdown, plugin skill references, agents/openai.yaml metadata.

---

### Task 1: Update Planner Skill Role And Handoff Contract

**Files:**
- Modify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/SKILL.md`

- [ ] **Step 1: Add superpowers/imagegen system positioning**

Add a short section explaining:

```text
superpowers = process gates
planner = strategy gate
imagegen = visual execution gate
verification-before-completion = evidence gate
```

- [ ] **Step 2: Add Planner Brief contract**

Define:

```text
Planner Brief = strategy contract
Imagegen Production Brief = execution contract
```

Planner must not specify pixel-level rendering, but it must define page goal, attention hierarchy, image role, message ownership, claim boundary, and pass/fail criteria.

### Task 2: Strengthen Planner/Imagegen Routing

**Files:**
- Modify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/SKILL.md`

- [ ] **Step 1: Update workflow modes**

Initial Planning Mode must hand off only after user approval. Post-Image Review Mode must decide whether imagegen can continue or planner must revise the brief.

- [ ] **Step 2: Tighten Image Request Brief**

Make the image request brief strategy-only and compatible with imagegen's production brief.

- [ ] **Step 3: Add systematic-debugging trigger**

If repeated imagegen revisions fail for the same reason and the cause is unclear, planner should stop cycling prompts and trigger root-cause analysis before another image round.

### Task 3: Add Cross-Skill Workflow Reference

**Files:**
- Create: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/workflow-with-imagegen.md`

- [ ] **Step 1: Add end-to-end flow**

Document:

```text
fuzzy request -> superpowers:brainstorming -> planner -> imagegen -> planner review -> verification
```

- [ ] **Step 2: Add routing table**

Document when to use planner, imagegen, systematic-debugging, and verification-before-completion.

### Task 4: Update Planner Agent Metadata

**Files:**
- Modify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/agents/openai.yaml`

- [ ] **Step 1: Align metadata with new role**

Update the short description and default prompt so the UI surfaces planner as the strategy and imagegen handoff owner.

### Task 5: Verify

**Files:**
- Check all modified planner files.

- [ ] **Step 1: Check line counts**

Run:

```bash
wc -l plugins/jiangyue-website-planner/skills/jiangyue-website-planner/SKILL.md plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/*.md
```

Expected: planner remains lightweight; no excessive expansion.

- [ ] **Step 2: Check references**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path('plugins/jiangyue-website-planner/skills/jiangyue-website-planner')
missing = []
for line in (root / 'SKILL.md').read_text().splitlines():
    if '(references/' in line:
        start = line.find('(references/') + 1
        end = line.find(')', start)
        rel = line[start:end]
        if not (root / rel).exists():
            missing.append(rel)
print(missing)
raise SystemExit(bool(missing))
PY
```

Expected: no missing references.

- [ ] **Step 3: Check unfinished markers**

Run:

```bash
rg -n "TBD|TODO|fill in|PLACEHOLDER_MARKER" plugins/jiangyue-website-planner
```

Expected: no accidental unfinished markers.

- [ ] **Step 4: Check Markdown diff whitespace**

Run:

```bash
git diff --check
```

Expected: no whitespace errors.
