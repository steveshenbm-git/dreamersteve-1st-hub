# Changelog

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
