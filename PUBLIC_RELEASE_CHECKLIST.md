# Public Release Checklist

Run this before pushing the package to a public repository.

- No personal absolute paths are present.
- Personal macOS user-path scans use the actual username shape `/Users/[[:alnum:]_.-]+/`, so the scan catches real absolute paths without matching its own regular-expression text.
- No private customer names, private project names, or private quotations are present.
- No credentials, API keys, cookies, tokens, or account IDs are present.
- Automated sensitive-data scans target credential-shaped assignments or headers rather than standalone prohibition words such as `Cookie`; check cookie or authorization headers with values, token or password assignments with values, and private-key blocks.
- Before release, run `git diff -U0 origin/main..HEAD | rg '^\+.*(/Users/[[:alnum:]_.-]+/|Cookie[=:][^[:space:]]|access_token[=:][^[:space:]]|refresh_token[=:][^[:space:]]|BEGIN[[:space:]]+(RSA[[:space:]]+|EC[[:space:]]+|OPENSSH[[:space:]]+)?PRIVATE[[:space:]]+KEY)'`.
- Every sensitive-data scan match is manually reviewed before release; a pattern match is a lead, not proof that a secret is present.
- No unverified certifications, compliance marks, test results, patents, export markets, or customer cases are present.
- No licensed customs, trade, credit, social, or commercial-database export is included.
- No screenshot, export, or copied content from an authenticated session is included.
- Empty workbook assets contain headers and formatting only, with no real company or contact rows.
- No local-only instructions depend on one person's machine.
- The repository URL is added to `plugin.json` only after the final public URL is known.
- Plugin validation passes.
- The ZIP package and source folder contain the same intended release files.
