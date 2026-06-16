# Contributing

Use this workflow when improving the skill with teammates.

## Principles

- Keep the skill concise.
- Put detailed reusable guidance in `references/`, not in a long `SKILL.md`.
- Do not add README, changelog, or collaboration documents inside the skill folder.
- Do not add unsupported product, certification, performance, customer, or compliance claims.
- Preserve the one-question-at-a-time brief workflow unless there is a strong reason to change it.

## What To Include In Each Change

Each improvement should include:

- the user request or failure scenario that motivated the change
- the file changed
- the intended behavior after the change
- one short example prompt for testing
- any public-release risk, if relevant

## Versioning

Use semantic versioning:

- Patch: wording fixes, typo fixes, small clarification
- Minor: new workflow, new reference file, improved prompt template
- Major: breaking structure, renamed skill, incompatible install change

## Review Checklist

Before merging:

- `SKILL.md` still has valid YAML frontmatter with only `name` and `description`
- the skill folder contains only runtime skill files
- public repository safety checklist is still satisfied
- plugin validation passes
- at least one realistic prompt has been tested in a fresh thread when behavior changes

## Suggested Test Prompt

```text
Use $jiangyue-website-imagegen to design a hero image for Jiangyue Technology's homepage. The image should express professional motor-control capability, AI-assisted improvement, and service feedback as one coordinated system. Ask me only the most important missing question before creating the production brief.
```
