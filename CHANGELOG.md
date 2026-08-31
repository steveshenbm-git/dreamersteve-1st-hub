# Changelog

## Unreleased - 2026-08-31

- Prepared the compatible source candidate set: `industry-application-map-builder 0.4.0-beta.6`, `foreign-trade-customer-development 0.2.0-beta.2`, `foreign-trade-customer-operations 0.2.0-beta.2`, and `foreign-trade-workflow-director 0.3.0-beta.4`; kept `company-product-knowledge-builder 0.1.0` unchanged.
- Added one read-only, hash-bound `handoff_envelope_v1` validator with exact company, target, route, payload-byte, duplicate-ID, path and empty-write-scope checks.
- Aligned the industry semantic return schema with the workflow director and bound customer-development handoffs to customer operations without duplicate handoff IDs.
- Added separate optimization-validation contracts for industry research, customer development, and customer operations so integration readiness cannot be mistaken for business effectiveness.
- Completed source preparation only. Installation, publication, freezing, live workflow validation, and external sending remain separately authorized stages.

## Unreleased - 2026-08-24

- Advanced `industry-application-map-builder` to `0.3.0-beta.3` and `foreign-trade-workflow-director` to `0.2.0-beta.3` for the RC2 contract-cycle repair.
- Added a hash-bound `case_preparation_locked` gate that permits isolated candidate/case preparation while case-set hashes, batch size, and control IDs remain genuinely empty.
- Added deterministic, refuse-overwrite scripts that lock preparation inputs and bind a real frozen 40-case set into a new final contract version.
- Kept model workspace initialization final-`frozen` only and added regression pressure for placeholders, lock drift, incomplete case sets, and premature model runs.
- Kept this repair source-only pending separate Git commit, plugin installation, and candidate-pool resumption authorization.

## Unreleased - 2026-08-18

- Reframed `foreign-trade-workflow-director` as a portable full-workflow Beta controller that audits the environment, initializes isolated company workflows, resumes from the earliest incomplete stage, and prepares bounded cross-account replication manifests.
- Added an authoritative stage gate between the official industry taxonomy and company matching: unexpanded product-neutral industry/application semantics now block stale company maps, route packets, and customer scanning.
- Kept the six-sheet single-editor workbench as the downstream salesperson interface while excluding company facts, routes, customers, communications, and credentials from portable framework assets.
- Marked blank second-company cold start and independent-account replication as live validation gates that remain unverified by source tests.
- Added the Beta `foreign-trade-workflow-director` plugin and a six-sheet, single-salesperson business workbench for tasks, route decisions, candidate screening, follow-up, communication drafts, and exceptions/risks.
- Kept the existing industry/application and customer-development workbooks as machine evidence backends rather than renaming their technical sheets into a salesperson interface.
- Split direction-led candidate collection into a bounded task export, append-only raw batch intake, and independent evidence review while retaining `candidate_scan` as a compatibility entry.
- Added controlled coordinator projections to industry mapping, customer development, and customer operations without transferring their evidence ownership or the salesperson's decision and sending authority.
- Kept this Beta as source-only until a separately authorized commit, push, installation, and real-business test.

## Unreleased - 2026-07-29

- Added `industry-application-map-builder` with a shared official-taxonomy skeleton, product-neutral application knowledge, per-company route maps, four-state technical matching, coverage control, Excel templates, workspace validation, and `company_route_pool_packet` export.
- Changed `company-product-knowledge-builder` to hand approved product facts to industry/application mapping rather than directly to customer-development direction discovery.
- Changed `foreign-trade-customer-development` to compile salesperson-selected route candidates from a validated route-pool packet while preserving the independent named-company initial-check entry.
- Added `source_route_candidate_id` to the customer-development workbook and retained salesperson ownership of `direction_status = 已确认可扫描`.
- Kept real company data, customer names, complete official catalogues, and installed-plugin cache changes outside this source update.

## 0.4.0 - 2026-07-23

- Prepared `foreign-trade-customer-development` as an independent Codex plugin for a future public release; public release remains blocked until the release-history gate is cleared.
- Added business-model-specific prospect research across official, industrial, social, retail, review, customs, and authorized logged-in sources.
- Added salesperson gates for candidate selection, potential-customer due diligence, restricted contacts, final recommendations, channels, and sending.
- Added an empty local Excel workbook template and a handoff contract for `foreign-trade-email-assistant`.
- Kept company facts, customer data, licensed database exports, correspondence, and logged-in captures outside the public plugin.

## 0.3.0 - 2026-07-23

- Added `foreign-trade-email-assistant` as a public Codex plugin.
- Added evidence-bound standard reply, natural-language revision, and serious-issue handling contracts.
- Kept business importance, final wording, and sending authority with the salesperson.
- Excluded company knowledge, customer records, mailbox data, and test-company materials from the public package.

## 0.2.2 - 2026-06-20

- Changed imagegen output handling so exploratory trial images only need local test images and optional short notes.
- Full reproduction archives are now required only after a draft is initially usable, accepted, final, or a meaningful reusable revision.
- Updated delivery reporting to allow `not created yet` for reproduction archives on trial-only outputs.

## 0.2.1 - 2026-06-20

- Added an execution intent gate for `jiangyue-website-imagegen` to distinguish new image creation, brief-based rebuilds, old-image local edits, format-only edits, and page/mockup work.
- Added explicit handling for requests such as "according to the above suggestion" so approved planner or image briefs are extracted before production.
- Added safeguards against downgrading a hero rebuild into simple color correction, resizing, or retouching.
- Clarified ambiguous "hero size", "web page size", and "standard size" wording before it changes the work type.

## 0.2.0 - 2026-06-18

- Added `jiangyue-website-planner` as a separate plugin for page strategy, B2B messaging, SEO/AEO direction, CTA planning, attention hierarchy, and image request briefs.
- Added planner reference templates for page briefs and imagegen rework orders.
- Updated `jiangyue-website-imagegen` with a planner return gate for failed visual work.
- Added explicit rules for when imagegen should continue structural revision versus return to planner.
- Updated the team marketplace to include both planner and imagegen plugins.

## 0.1.0 - 2026-06-16

- Packaged the existing `jiangyue-website-imagegen` skill as a Codex plugin.
- Added a team marketplace manifest named `jiangyue-team`.
- Added public-sharing, contribution, versioning, and validation guidance.
- Excluded local system files from the packaged skill.
