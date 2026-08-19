# Portable Foreign-Trade Workflow Director Design

## Goal

Redefine `foreign-trade-workflow-director` as the versioned, portable control layer that can build, resume, audit, and reproduce the complete foreign-trade workflow for a new company or another Codex account without carrying one company's private facts into another.

The skill coordinates specialist skills and validates their handoffs. It does not replace their domain judgment.

## Problem

The current Beta is centered on one salesperson, one company workspace, and one six-sheet business workbench. It can resume downstream business work and relay specialist packets, but it does not know how to:

- audit whether the required skills, templates, shared layers, and company inputs exist;
- identify the earliest incomplete stage in the complete workflow;
- initialize a clean company-specific workflow instance;
- distinguish portable framework assets from private company data;
- reproduce the framework in another account;
- verify each stage before allowing the next stage to begin.

This allowed the workflow to jump from a stale route packet directly to route validation while the industry semantic layer was still incomplete.

## Product Definition

The revised skill is a `portable_workflow_blueprint_beta`.

It owns:

- the authoritative stage graph;
- environment and dependency audit;
- company workflow initialization;
- current-stage detection from actual artifacts;
- bounded specialist handoffs;
- stage acceptance and STOP gates;
- framework replication manifests;
- business-facing summaries and the downstream salesperson workbench.

It must not own:

- product-fact extraction or evidence promotion;
- industry or application research conclusions;
- company or contact research conclusions;
- customer selection or prioritization;
- message approval or sending;
- installation, writing, or publication without the corresponding authorization.

## Authoritative Stage Graph

The first incomplete stage owns the next action. A later artifact never proves an earlier stage complete.

Stages 1–7 are the company-level foundation. Stages 8–10 are recurring business instances: route decision per route, candidate development per direction, and customer operations per customer thread. Completing one instance never marks the whole company's recurring work complete.

| Stage | Owner | Required output and gate |
|---|---|---|
| `environment_audit` | workflow director | Required plugin versions, templates, paths, and permissions are `PASS` or explicitly `UNVERIFIED` |
| `company_identity` | company product knowledge builder | Stable `company_id`, isolated company root, approved source scope |
| `product_knowledge` | company product knowledge builder | Valid product library and development fact packet |
| `industry_taxonomy` | industry application map builder | Versioned official classification skeleton and registry |
| `industry_semantic_expansion` | industry application map builder | Declared industry scope has product-neutral output, process/use-point, application, requirement, evidence, limitation, and coverage dispositions |
| `company_industry_match` | industry application map builder | Company capability atoms are matched to the current shared application layer without direct industry-name inference |
| `route_pool_handoff` | industry application map builder | Current registered route-pool packet with valid input and producer hashes |
| `direction_decision` | customer development plus salesperson | Route is compiled and validated; salesperson explicitly decides whether scanning may begin |
| `candidate_development` | customer development | Candidate task, raw collection batches, independent review, and salesperson classification remain separate |
| `customer_operations` | customer operations plus salesperson | Draft, approval, actual sending, reply, follow-up, and risk states remain separate |
| `framework_review` | workflow director | Gaps, stale dependencies, lessons, and version changes are recorded without rewriting specialist facts |

If the shared taxonomy exists but the declared application scope remains `not_expanded`, the workflow must stop at `industry_semantic_expansion`. It must not resume an old company map, route pool, or customer scan.

## Core Routes

| Route | Purpose | Stop point |
|---|---|---|
| `framework_audit` | Inspect required skills, versions, templates, shared assets, company inputs, permissions, and current artifact state | Return the earliest incomplete stage and one next action |
| `company_framework_bootstrap` | Prepare a clean company workflow instance from approved templates and explicit inputs | Stop after structure and registrations validate; no business facts are inferred |
| `framework_resume` | Reconstruct the current state from artifacts and registries | Route only to the earliest incomplete or stale stage |
| `specialist_handoff` | Send one bounded task to the owning specialist skill | Stop until a traceable return packet is received |
| `framework_replication_plan` | Prepare a portable manifest for another company or Codex account | Produce a plan and missing-dependency report; do not install or copy private data automatically |
| `business_decision_record` | Record an explicitly authorized salesperson decision in the downstream workbench | Stop after reopening and verifying the exact write |

The existing six-sheet workbench remains a downstream asset. It is not the source of truth for framework completeness.

## Artifact Contracts

### `workflow_blueprint`

Contains:

- `blueprint_version`
- ordered stage IDs and dependencies
- owning skill and route for each stage
- required inputs and outputs
- acceptance and STOP conditions
- portable templates and schema references
- prohibited actions and company-data boundaries

### `company_workflow_state`

Contains one company's:

- `company_id` and isolated root
- blueprint version
- current stage and stage status
- artifact paths, versions, hashes, and validation states
- blockers, stale events, pending decisions, and next action
- an explicit active work unit plus separate route, direction, and customer-thread instance states

It must not combine facts, routes, customers, or communication history from another company.

### `workflow_replication_manifest`

Contains only portable framework material:

- blueprint and contract versions
- required plugin names and compatible versions
- empty templates and their hashes
- shared product-neutral knowledge references when transfer is authorized
- required permissions and installation steps
- validation commands and recovery checkpoints
- missing dependencies and `UNVERIFIED` items

It must exclude company product facts, company maps, route decisions, customer records, contacts, drafts, sent messages, replies, and credentials.

## Cross-Account Boundary

The skill may audit and describe what another account needs. It may create a replication manifest after authorization. Installing plugins, transferring files, or writing into another account remains a separate authorized action.

A copied directory is not proof of successful replication. The receiving account must independently verify plugin discovery, versions, template hashes, paths, permissions, and the first incomplete workflow stage.

## Failure Handling

- Missing or incompatible plugin: stop at `environment_audit`.
- Missing company identity or source scope: stop at `company_identity`.
- Full taxonomy with unexpanded application scope: stop at `industry_semantic_expansion`.
- Stale shared input or producer registry: return to the owning map stage; do not trust filenames.
- Cross-company identifier or artifact: `FAIL` and isolate it.
- Missing evidence or incomplete research: `UNVERIFIED`, never auto-promote.
- User asks for a later stage: report the missing prerequisite and the single current action.

## Validation

### RED scenario from this conversation

Given a valid product fact packet, a complete official taxonomy skeleton, 1,183 terminal industries mostly marked `not_expanded`, and an old route packet, the current skill followed the old route path. The required behavior is to identify `industry_semantic_expansion` as the earliest incomplete stage and block route/customer work.

### Static acceptance

- Contract tests require all authoritative stage IDs, routes, artifact contracts, data boundaries, and the first-incomplete-stage rule.
- Pressure prompts cover incomplete industry semantics, new-company bootstrap, cross-company contamination, and cross-account replication without private data.
- Existing specialist contract tests continue to pass.

### Live acceptance

Static tests do not prove portability. The skill remains Beta until both tests pass:

1. Cold-start a blank second company without copying the first company's facts.
2. In a separate Codex account, use the replication manifest to restore dependencies and identify the correct first incomplete stage.

## Scope of This Optimization

This optimization changes the skill definition, workflow blueprint reference, packet contract, prompt metadata, pressure tests, and static contract tests. It does not build the missing industry semantic knowledge, create a second company, transfer data, install the plugin, or run a cross-account live test.
