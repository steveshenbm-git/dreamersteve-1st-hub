# Jiangyue Team Codex Plugins

This public repository shares reusable Codex plugins for Jiangyue website work and foreign-trade communication.

The package currently includes:

- `jiangyue-website-planner` plans B2B page goals, content structure, SEO/AEO direction, CTA path, first-screen attention hierarchy, and image request briefs.
- `jiangyue-website-imagegen` creates, edits, and reviews website visuals from a confirmed image request brief, with physical plausibility, visual structure, and failure-attribution checks.
- `jiangyue-website-workflow-director` routes Jiangyue website work across planning, image production, and knowledge curation.
- `jiangyue-knowledge-curator` maintains reusable Jiangyue website knowledge and approved-material references.
- `jiangyue-skill-director` governs Jiangyue skill design, repair, and release checks.
- `foreign-trade-email-assistant` remains an optional compatibility plugin for standalone complete-email-thread analysis. Do not run it alongside `foreign-trade-customer-operations` for the same reply.
- `foreign-trade-customer-development` starts with product-led direction discovery, validates a direction before scanning, returns all qualified candidate companies in the declared scope, and prepares an evidence-bound communication handoff without drafting or sending messages.
- `foreign-trade-customer-operations` is the primary communication plugin for selected prospects and existing customers: first cold outreach, unanswered follow-up, replies, and customer-operation materials.

The user remains the final reviewer for page strategy, claims, visual approval, business judgment, email wording, and sending.

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
plugins/foreign-trade-email-assistant/.codex-plugin/plugin.json
plugins/foreign-trade-email-assistant/skills/foreign-trade-email-assistant/SKILL.md
plugins/foreign-trade-email-assistant/skills/foreign-trade-email-assistant/agents/openai.yaml
plugins/foreign-trade-email-assistant/skills/foreign-trade-email-assistant/references/
plugins/foreign-trade-customer-development/.codex-plugin/plugin.json
plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/SKILL.md
plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/agents/openai.yaml
plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/
plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx
plugins/foreign-trade-customer-operations/.codex-plugin/plugin.json
plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/SKILL.md
plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/agents/openai.yaml
plugins/foreign-trade-customer-operations/skills/foreign-trade-customer-operations/references/
```

## Install From This Repository

1. Clone or unzip this package.
2. Add this repository as a local Codex plugin marketplace:

```bash
codex plugin marketplace add /absolute/path/to/dreamersteve-1st-hub
```

3. Install the recommended foreign-trade pair and any Jiangyue plugins you use:

```bash
codex plugin add jiangyue-website-planner@jiangyue-team
codex plugin add jiangyue-website-imagegen@jiangyue-team
codex plugin add foreign-trade-customer-development@jiangyue-team
codex plugin add foreign-trade-customer-operations@jiangyue-team
```

If you need only the older standalone email workflow, install `foreign-trade-email-assistant` as an optional compatibility plugin instead of using it together with customer operations for the same task:

```bash
codex plugin add foreign-trade-email-assistant@jiangyue-team
```

4. Start a new Codex thread and use:

```text
Use $jiangyue-website-planner to plan a Jiangyue website page and image brief.
Use $jiangyue-website-imagegen to help me create a Jiangyue website visual.
Use $foreign-trade-customer-development to create a product-led development direction, validate it, or scan a confirmed direction for qualified candidates.
Use $foreign-trade-customer-operations to prepare the first outreach, a due follow-up, or a reply from a complete customer thread.
```

## Recommended Workflow

1. Use `jiangyue-website-planner` to define page strategy, section structure, CTA path, attention hierarchy, and image role.
2. Confirm the planner output with the user.
3. Hand the confirmed image request brief to `jiangyue-website-imagegen`.
4. If imagegen fails because of visual execution, continue structural image revision inside imagegen.
5. If imagegen fails because the image request conflicts with page strategy, attention hierarchy, image role, or claim boundaries, return to planner with an `Imagegen 返工请求`.

## Foreign Trade Customer Development Workflow

1. Run `direction_discovery` from approved local product facts; validate the rule and obtain the salesperson's `已确认可扫描` decision before scanning a direction.
2. For a confirmed direction or named prospect, run `candidate_scan`, return all qualified candidates in the declared scope, and stop for salesperson selection.
3. Run full due diligence only after potential-customer classification and explicit start are both recorded.
4. When the salesperson asks to start communication, output an `outreach_handoff_packet`; do not draft or send a message in customer development.
5. Use `foreign-trade-customer-operations` for first outreach, no-reply follow-up, replies, and customer-operation work. Write only to a user-designated local workbook.

## Standalone Compatibility Email Workflow

1. Supply the complete customer email thread, readable attachments, and any approved local facts needed for the reply.
2. Use `foreign-trade-email-assistant` only when you intentionally choose the standalone compatibility workflow; otherwise use `foreign-trade-customer-operations`.
3. Give revision instructions in natural language when the first draft is not acceptable.
4. Keep importance, business decisions, final wording, and sending authority with the salesperson.
5. Keep company knowledge, customer records, mailbox data, test cases, and actual correspondence outside this public plugin repository.

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

1. Edit files under the relevant `plugins/<plugin-name>/skills/<skill-name>/` source folder.
2. Validate the plugin.
3. Bump the plugin version for intentional releases.
4. Update `CHANGELOG.md`.
5. Ask teammates to reinstall the plugin and start a new Codex thread.

## Local Source Sync

If this package improves a skill, copy the reviewed files back into that skill's maintained local source before reinstalling the local version.
