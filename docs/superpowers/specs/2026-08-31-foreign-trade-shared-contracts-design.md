# Foreign-Trade Shared Contracts Design

## Goal

Keep the current installed and tested releases unchanged while preparing one coherent candidate set in source:

- `industry-application-map-builder 0.4.0-beta.6`
- `foreign-trade-workflow-director 0.3.0-beta.4`
- `foreign-trade-customer-development 0.2.0-beta.2`
- `foreign-trade-customer-operations 0.2.0-beta.2`

The candidate set must make marketplace discovery complete, align the industry semantic return with the controller, bind development payloads to operations without cross-company or tamper ambiguity, and keep the three specialist optimization verdicts independent.

## Scope

This change may edit the four plugin sources, the foreign-trade marketplace registry, installation documentation, compatibility documentation, deterministic validation code, and tests. It must not edit installed caches, company workspaces, frozen R4 evidence, or salesperson records. Installation, commit, push, publication, and freeze remain separate actions.

## Shared envelope

Every current customer-development-to-customer-operations handoff uses a machine-owned `handoff_envelope_v1`:

```text
handoff_envelope_v1:
  contract_version: "1.0"
  handoff_id
  company_id
  target_skill
  target_route
  payload_reference
  payload_sha256
  allowed_writes: []
```

`payload_reference` is a canonical relative path from the envelope directory. The receiver rejects an absolute or escaping path, a missing or changed payload, company mismatch, wrong target skill or route, duplicate `handoff_id`, and an unauthorized write scope. The envelope does not replace the route-specific payload.

The current validator allowlists exactly `cold_outreach / outreach_handoff_packet` and `reply_communication / customer_operations_handoff`, rejects duplicate JSON keys, and hashes and parses the same single read of the payload bytes. Other specialist return contracts remain governed by their own exact schemas until they are separately registered.

The development payloads `outreach_handoff_packet` and `customer_operations_handoff` each carry `company_id`. Their stable `handoff_id` comes only from the envelope; an authorized workbook record may copy that value but must not invent another identity.

## Semantic return

The industry skill adopts the controller's full `semantic_specialist_return_packet`. Content-first keeps `semantic_method_validation_state = null`, uses `CONTENT_CALIBRATION_*`, carries all R4 hashes and authorization bindings, and always retains `RESEARCH_ONLY_BLOCKED`. Strict audit alone may use `INCONCLUSIVE / EFFECTIVE / NOT_EFFECTIVE`.

## Marketplace and compatibility

The marketplace lists all required workflow plugins: product knowledge, industry map, customer development, customer operations, and workflow director. README installation commands cover the same set. The compatibility matrix records the exact candidate versions and states that existing beta.5 R4 artifacts remain on their current baseline until that test cycle is closed; the candidate beta.6 is not installed over an active beta.5 run. A same-named plugin already active from another marketplace is an installation blocker until the user separately chooses one source and authorizes migration.

## Independent optimization lanes

- Industry validation keeps its frozen R4 cases, truth, 80-task evidence, six repeats, and research-only stop. Its verdict cannot prove customer-development or communication quality.
- Customer-development validation freezes confirmed route inputs and tests candidate evidence, due diligence, and handoff behavior. Unsupported PASS, ranking, drafting, or sending is a critical failure.
- Customer-operations validation freezes approved customer facts and threads and tests routing and review-ready communication. Invented claims, false actual-send state, wrong reply routing, or sending is a critical failure.
- Integration validation proves only discovery and interface compatibility. It cannot make any specialist optimization `EFFECTIVE`.

## Verification

Tests must first fail against the current baseline, then pass after the minimum implementation. They cover marketplace completeness, exact version set, semantic schema equality, valid envelope acceptance, changed payload, company mismatch, wrong or unregistered target, wrong payload wrapper, duplicate JSON keys, duplicate handoff, and non-empty unauthorized writes. Existing plugin suites and static validators must remain green. Real active-environment installation remains `UNVERIFIED` until separately authorized.

## Rollback

Discard the isolated candidate worktree or return to source commit `e5b4dd5`. The active caches and the current beta.5 industry test workspace are not modified by this work.
