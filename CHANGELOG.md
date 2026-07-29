# Changelog

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
