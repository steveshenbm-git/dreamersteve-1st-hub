# Public Release Checklist

Run this before pushing the package to a public repository.

## Public-history hard gate

- A final-tree or final-diff scan is necessary but not sufficient: deleted content may remain in Git history.
- The current development branch is known to contain personal absolute local paths in early commit history. Do not push it to a public remote until that history has been cleaned and rechecked.
- Before any public push, obtain separate explicit user approval to create a clean squash/rebase release history. Do not rewrite the current development branch history as part of this checklist update.
- Inspect the contents of every commit intended for publication, then run sensitive-data and personal-path scans against both those commit contents and the final tree.
- Treat any uncleaned commit, unreviewed commit, or unresolved scan match as a publication blocker.
- Approval of the written specification or completion of this checklist does not authorize installation, push, pull request creation, publication, merge, squash, rebase, or any other history rewrite.

## Package checks

- No personal absolute paths are present.
- Personal macOS user-path scans use the actual username shape `/Users/[[:alnum:]_.-]+/`, so the scan catches real absolute paths without matching its own regular-expression text.
- No private customer names, private project names, or private quotations are present.
- No credentials, API keys, cookies, tokens, or account IDs are present.
- Automated sensitive-data scans target credential-shaped assignments or headers rather than standalone prohibition words such as `Cookie`; check cookie or authorization headers with values, token or password assignments with values, and private-key blocks.
- Before release, run `git diff -U0 origin/main..HEAD | rg --pcre2 '^\+.*(/[U]sers/[[:alnum:]_.-]+/|C[o]okie[[:space:]]*[:=][[:space:]]*[^[:space:]]+|(?:[a]ccess_token|[r]efresh_token|[a]pi[_-]key|[p]assword)[[:space:]]*[:=][[:space:]]*[^[:space:]]+|A[u]thorization[[:space:]]*:[[:space:]]*(?:Bearer|Basic)[[:space:]]+[^[:space:]]+|B[E]GIN[[:space:]]+(?:(?:RSA|EC|DSA|OPENSSH|ENCRYPTED)[[:space:]]+)?PRIVATE[[:space:]]+KEY)'`.
- Every sensitive-data scan match is manually reviewed before release; a pattern match is a lead, not proof that a secret is present.
- No unverified certifications, compliance marks, test results, patents, export markets, or customer cases are present.
- No licensed customs, trade, credit, social, or commercial-database export is included.
- No screenshot, export, or copied content from an authenticated session is included.
- Empty workbook assets contain headers and formatting only, with no real company or contact rows.
- No local-only instructions depend on one person's machine.
- The repository URL is added to `plugin.json` only after the final public URL is known.
- Plugin validation passes.
- The ZIP package and source folder contain the same intended release files.
