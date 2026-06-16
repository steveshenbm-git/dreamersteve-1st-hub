# Jiangyue Website Imagegen Plugin

This repository package shares the `jiangyue-website-imagegen` Codex skill with teammates.

The skill helps Codex create, edit, and review Jiangyue Technology website visuals with a clear image brief, industrial B2B brand direction, and safer handling of text, claims, and visual hierarchy.

## Package Structure

```text
.agents/plugins/marketplace.json
plugins/jiangyue-website-imagegen/.codex-plugin/plugin.json
plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/SKILL.md
plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/agents/openai.yaml
plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/references/
```

## Install From This Repository

1. Clone or unzip this package.
2. Add this repository as a local Codex plugin marketplace:

```bash
codex plugin marketplace add /absolute/path/to/jiangyue-imagegen-marketplace
```

3. Install the plugin:

```bash
codex plugin add jiangyue-website-imagegen@jiangyue-team
```

4. Start a new Codex thread and use:

```text
Use $jiangyue-website-imagegen to help me create a Jiangyue website visual.
```

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

1. Edit files under `plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen/`.
2. Validate the plugin.
3. Bump the plugin version for intentional releases.
4. Update `CHANGELOG.md`.
5. Ask teammates to reinstall the plugin and start a new Codex thread.

## Local Source Sync

If this package improves the skill, copy the reviewed skill files back into the local Jiangyue skill source before reinstalling your local version.
