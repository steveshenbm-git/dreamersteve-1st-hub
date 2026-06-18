# Jiangyue Website Plugins

This repository package shares Jiangyue Technology website-planning and image-production Codex plugins with teammates.

The package separates strategy and execution:

- `jiangyue-website-planner` plans B2B page goals, content structure, SEO/AEO direction, CTA path, first-screen attention hierarchy, and image request briefs.
- `jiangyue-website-imagegen` creates, edits, and reviews website visuals from a confirmed image request brief, with physical plausibility, visual structure, and failure-attribution checks.

The user remains the final reviewer for page strategy, claims, and visual approval.

## Package Structure

```text
.agents/plugins/marketplace.json
plugins/jiangyue-website-imagegen/.codex-plugin/plugin.json
plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/SKILL.md
plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/agents/openai.yaml
plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/
plugins/jiangyue-website-planner/.codex-plugin/plugin.json
plugins/jiangyue-website-planner/skills/jiangyue-website-planner/SKILL.md
plugins/jiangyue-website-planner/skills/jiangyue-website-planner/agents/openai.yaml
plugins/jiangyue-website-planner/skills/jiangyue-website-planner/references/
```

## Install From This Repository

1. Clone or unzip this package.
2. Add this repository as a local Codex plugin marketplace:

```bash
codex plugin marketplace add /absolute/path/to/jiangyue-imagegen-marketplace
```

3. Install the plugins:

```bash
codex plugin add jiangyue-website-planner@jiangyue-team
codex plugin add jiangyue-website-imagegen@jiangyue-team
```

4. Start a new Codex thread and use:

```text
Use $jiangyue-website-planner to plan a Jiangyue website page and image brief.
Use $jiangyue-website-imagegen to help me create a Jiangyue website visual.
```

## Recommended Workflow

1. Use `jiangyue-website-planner` to define page strategy, section structure, CTA path, attention hierarchy, and image role.
2. Confirm the planner output with the user.
3. Hand the confirmed image request brief to `jiangyue-website-imagegen`.
4. If imagegen fails because of visual execution, continue structural image revision inside imagegen.
5. If imagegen fails because the image request conflicts with page strategy, attention hierarchy, image role, or claim boundaries, return to planner with an `Imagegen 返工请求`.

## Public Repository Safety

Before publishing this package publicly, confirm that it contains no:

- personal local paths
- private customer names or project names
- unverified product specifications
- certification, compliance, test, patent, or export claims
- private credentials, tokens, or account information

Repository: https://github.com/steveshenbm-git/dreamersteve-1st-hub

## Update Flow

Treat this repository as the source of truth. Do not edit the installed cache as the main working copy.

1. Edit files under `plugins/jiangyue-website-planner/skills/jiangyue-website-planner/` or `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/`.
2. Validate the plugin.
3. Bump the plugin version for intentional releases.
4. Update `CHANGELOG.md`.
5. Ask teammates to reinstall the plugin and start a new Codex thread.

## Local Source Sync

If this package improves the skill, copy the reviewed skill files back into the local Jiangyue skill source before reinstalling your local version.
