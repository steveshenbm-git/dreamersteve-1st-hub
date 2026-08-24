# RC2 Content-First Unified Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the two existing foreign-trade skills in place so new RC2 work defaults to content-first while strict beta.3 contracts remain compatible.

**Architecture:** Add one explicit mode field to the existing contract surface. Move candidate-only material into the matching existing plugin, update the normal manifests and marketplace records, and delete the duplicate candidate plugin trees. Git history, not duplicate installed skills, provides beta.3 rollback.

**Tech Stack:** Markdown skill contracts, JSON/YAML templates, Python 3 standard-library validators/evaluators, `unittest`, Git.

**Spec:** `docs/superpowers/specs/2026-08-24-rc2-content-first-unified-upgrade.md`

## Global Constraints

- Preserve the original strict scripts and semantic-method prompt assets byte-for-byte.
- Treat a legacy contract without `semantic_evaluation_mode` as `strict_audit`.
- Default a newly created workflow/content-first contract to `content_first`.
- Do not modify the installation cache, RC2-40 frozen artifacts, beta.3 commits, or downstream company/route/customer boundaries.
- Do not run live models, 40 cases, or full-node work.

### Task 1: Prove the current duplicate-plugin design fails the unified contract

**Files:**
- Create: `tests/industry-application-map-builder/test_content_first_unified_upgrade.py`

- [ ] Write tests requiring only the two original marketplace names, original skill names with next-version manifests, new-template content-first default, legacy strict selection, and the content evidence/downstream fields under the original directories.
- [ ] Run only this test and confirm it fails because the base plugins are still beta.3 and the duplicate candidate entries exist.

### Task 2: Move map-skill content-first resources into the original package

**Files:**
- Modify: `plugins/industry-application-map-builder/.codex-plugin/plugin.json`
- Modify: `plugins/industry-application-map-builder/skills/industry-application-map-builder/SKILL.md`
- Modify: `plugins/industry-application-map-builder/skills/industry-application-map-builder/agents/openai.yaml`
- Modify: `plugins/industry-application-map-builder/skills/industry-application-map-builder/references/pressure-scenarios.md`
- Create: original skill `assets/content-first/`, two content-first references, and five deterministic content-first scripts.

- [ ] Move candidate-only files without rewriting their contents.
- [ ] Update the original manifest and skill instructions to make content-first the new-contract default and strict-audit the explicit/legacy compatibility mode.
- [ ] Run the unified test and the content-first test suite.

### Task 3: Move workflow controller mode support into the original package

**Files:**
- Modify: `plugins/foreign-trade-workflow-director/.codex-plugin/plugin.json`
- Modify: original workflow `SKILL.md`, agents metadata, state and replication templates, blueprint, and packet contract.

- [ ] Make workflow templates default new semantic work to `content_first` while accepting legacy strict contracts.
- [ ] Preserve the existing stage order, strict route, ownership rules, and downstream stop.
- [ ] Run the unified test and the workflow regression suite.

### Task 4: Retire duplicate source entries and prove the release boundary

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Move: candidate tests into `tests/industry-application-map-builder/`
- Delete: both `*-rc2-content-first` plugin directories and superseded candidate design/plan documents.

- [ ] Remove only the two redundant marketplace records and source copies after verifying their unique material has moved.
- [ ] Run strict regression tests, content-first normal/incomplete/adversarial tests, JSON/frontmatter/marketplace consistency checks, and frozen-artifact/cache diff checks.
- [ ] Record structural/behavioral PASS separately from live optimization effectiveness `INCONCLUSIVE`.
