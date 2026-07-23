# Attempt Stop And Method Escalation Gate

Use this for high-impact, cost-bearing, repeated-failure, or unclear image work. The goal is to prevent endless background attempts and repeated failed methods.

## Core Rule

Set a stop rule, not a fixed universal attempt count. Each attempt must test a distinct production hypothesis.

## Required Record

```text
Attempt Stop Rule
- Task risk: low / standard / high-impact / cost-bearing / repeated-failure
- Multiple attempts allowed: yes/no
- Attempt 1 hypothesis:
- Attempt 2 hypothesis, if allowed:
- What counts as same-method repetition:
- Stop trigger:
- After stop, required output:
- Route after stop: imagegen failure analysis / planner / Workflow Director
```

## Suggested Defaults

| Task type | Stop rule |
|---|---|
| Format export, crop, compression | No attempt limit needed; verify the deterministic output |
| Small local edit | One main attempt plus one correction if the defect is local and visible |
| High-impact brand, homepage, product, or new direction image | Up to two distinct production hypotheses; then stop and analyze |
| API or cost-bearing image work | Each live call must have a stated purpose; repeated failure stops production |
| User says no visible change, still wrong, or self-check failed | No same-method attempt allowed; run failure reset first |

## Distinct Hypothesis Requirement

A new attempt counts only when at least one changes:

- visual model;
- composition structure;
- subject carrier;
- crop/scale hierarchy;
- source/reference basis;
- production method;
- mask/edit scope.

Changing only prompt adjectives, color, glow, blur, opacity, line weight, border, shadow, or export size does not count as a distinct attempt for structural failure.

## Stop Output

When the stop trigger fires, output analysis rather than another image:

```text
Attempt Stop Analysis
- Attempts made:
- Repeated failure:
- Failed hypothesis:
- Evidence:
- Why another same-method attempt is blocked:
- Next route:
```
