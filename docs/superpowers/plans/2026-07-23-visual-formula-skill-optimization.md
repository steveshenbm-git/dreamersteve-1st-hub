# Jiangyue Visual Formula Skill Optimization Implementation Plan

> **For agentic workers:** Execute inline in this task. Do not dispatch subagents or run live image generation; the user will forward-test through later real image tasks.

**Goal:** Make the confirmed Jiangyue five-layer visual formula and `T -> S -> R -> O -> A -> I -> N` execution chain govern planning, prompt preparation, and result review without bloating briefs.

**Architecture:** Keep the formal brand outline as the only semantic authority. Let `brand-system` route to and interpret that authority, let planner own the compact formula decision and image/text/layout responsibility split, let imagegen inherit rather than reinterpret it, and let workflow director own routing only. Replace duplicate inline templates with conditionally loaded references.

**Tech Stack:** Markdown skills, Codex plugin manifests already present, shell-based static validation.

## Global Constraints

- Edit only the GitHub `improve-flow` working tree and the two approved project `brand-system` files.
- Do not edit `~/.codex/plugins/cache/`.
- Do not commit, push, install, reinstall, generate images, edit images, or use the network.
- Keep real product, application, AI, certification, performance, customer, and compliance claims inside verified fact boundaries.
- Preserve all seven formula decisions; reduce duplication through ownership and conditional loading, not deletion.

---

### Task 1: Record baseline and protect rollback

**Files:**
- Read: formal brand outline, current brand-system files, current workflow/planner/imagegen skills.
- Backup: the two non-Git brand-system files to a temporary rollback directory.

- [x] Confirm the formal outline contains the five-layer formula and seven-stage AI execution formula.
- [x] Confirm current skills do not contain the seven-stage execution contract.
- [x] Confirm the current planner inline brief exceeds the compact-brief threshold.
- [x] Create rollback copies before editing brand-system.

### Task 2: Establish authority without a second formula

**Files:**
- Modify: `/Users/lirongjing/Documents/JY TECH WEB/brand-system/00-knowledge-gate/jiangyue-knowledge-gate.md`
- Modify: `/Users/lirongjing/Documents/JY TECH WEB/brand-system/02-brand-visual/brand-visual-standard.md`

- [x] Point formula semantics to the formal outline section 4.
- [x] Reframe `brand-visual-standard.md` as an approved operational interpretation.
- [x] Remove the ambiguous local four-part production formula while preserving its useful atmosphere constraints.
- [x] Define new-semantic-visual versus bounded-technical-edit read behavior.

### Task 3: Make planner the compact formula owner

**Files:**
- Modify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/SKILL.md`
- Modify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/page-brief-template.md`
- Modify: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/design-led-planner.md`
- Create: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/visual-formula-brief.md`
- Create: `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/visual-formula-pressure-scenarios.md`

- [x] Replace the 119-field inline brief with one linked compact contract.
- [x] Keep T/S/R/O/A/I/N, evidence, responsibility allocation, prompt direction, feasibility, and return conditions.
- [x] Load page, brand-Hero, product/application, rework, research, and local-technical modules only on observable triggers.
- [x] Omit irrelevant modules instead of printing empty fields.

### Task 4: Keep workflow director at the routing layer

**Files:**
- Modify: `plugins/jiangyue-website-workflow-director/skills/jiangyue-website-workflow-director/SKILL.md`
- Modify: `plugins/jiangyue-website-workflow-director/skills/jiangyue-website-workflow-director/references/pressure-scenarios.md`

- [x] Require the formal formula source for semantic visual work.
- [x] Allow the director to collect task inputs but prohibit it from deciding S through N.
- [x] Require planner handoff before new semantic image production.

### Task 5: Make imagegen inherit, compile, and verify

**Files:**
- Modify: `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/SKILL.md`
- Modify: `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/visual-self-check-gate.md`
- Modify: `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/intent-brief-result-coordination-gate.md`
- Modify: `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/candidate-delivery-gate.md`
- Modify: `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/execution-gates.md`
- Modify: `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/brief-review-rubric.md`
- Modify: `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/failure-reset-hard-gates.md`
- Create: `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/visual-formula-execution.md`

- [x] Inherit the planner formula decision without semantic rewrite.
- [x] Preserve seven-stage traceability while allowing a natural-language final prompt.
- [x] Verify image-owned versus text/layout-owned responsibilities.
- [x] Attribute professionalism, refinement, affinity, vitality, New Eastern order, and recognition to the correct mechanisms.

### Task 6: Protect curation and the TDD workflow

**Files:**
- Modify: `plugins/jiangyue-knowledge-curator/skills/jiangyue-knowledge-curator/SKILL.md`
- Modify: `plugins/jiangyue-knowledge-curator/skills/jiangyue-knowledge-curator/references/formal-entry-templates.md`
- Modify: `plugins/jiangyue-skill-director/skills/jiangyue-skill-director/SKILL.md`
- Modify: `plugins/jiangyue-skill-director/skills/jiangyue-skill-director/references/pressure-scenarios.md`

- [x] Prevent curated lessons from becoming a second formula definition.
- [x] Record failed formula field, responsibility owner, and observed evidence when applicable.
- [x] Make RED failure scenario -> smallest rule change -> static review -> refactor a required evidence chain.
- [x] Keep deferred live forward tests labeled deferred rather than passed.

### Task 7: Static validation and deferred forward test

**Files:**
- Validate all modified skill folders and Markdown references.

- [x] Run equivalent YAML/frontmatter validation for all five skills. The official `quick_validate.py` remains blocked because the local Python environments lack `PyYAML`.
- [x] Check all relative Markdown references resolve.
- [x] Check the main planner skill no longer embeds the large brief: compact core 12 fields; complete-page module 18 fields only when triggered; legacy image template has zero active links.
- [x] Run static acceptance searches for formula authority, ownership, conditional modules, QA traceability, and correct mechanism attribution.
- [x] Run a separate falsification search; remove reachable legacy composition/reasoning/asset-production contracts found in the first pass.
- [x] Record live product image, abstract pattern, poster, and page-unit tests as deferred to later real image tasks.
- [x] Confirm no cache, manifest, marketplace, commit, push, installation, or image output changed.

## Static Review Evidence

- RED: formula present only in the formal outline; skill chain lacked formula decisions; planner embedded 119 brief fields; legacy high-impact references could re-expand the contract.
- GREEN: sole semantic authority, compact planner ownership, routing-only director, inherited imagegen trace, curation protection, and conditional modules are present.
- Static checks passed: formula source and single full-formula occurrence; route/ownership rules; prompt trace and self-check; frontmatter via Ruby YAML; relative links; plugin JSON; `git diff --check`; cache untouched.
- Falsification correction: reachable legacy `Visual Composition Contract`, `Brief Reasoning`, `Asset Production Section`, and old feasibility-contract requirements were removed or compiled into the Formula Decision.
- UNVERIFIED / deferred: official Python quick validator due missing `PyYAML`; real generated-image behavior and visual quality until later product, pattern, poster, and page-unit tasks.

## Rollback

- Plugin source: revert only this task's working-tree diff before any commit; no installed layer needs rollback.
- Project knowledge files: restore the two copies under `/private/tmp/jiangyue-visual-formula-backup.qZSRHx/`.
