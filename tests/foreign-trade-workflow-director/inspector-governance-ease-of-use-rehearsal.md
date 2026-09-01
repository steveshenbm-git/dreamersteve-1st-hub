# Inspector Governance Ease-of-Use Rehearsal

- Candidate: `foreign-trade-workflow-director 0.4.0-beta.2`
- Scope: disposable framework fixture only
- Business stage changes: none
- Migration activation: not performed

## Ordinary read-only audit

The normal route reads conversation state, the governance registry when present, and the relevant task ledger. It returns one disposition and one next action. It does not initialize a governance root or load the legacy-migration contract.

## One authorized non-blocking finding

The operator sees one logical event and makes one decision: whether to authorize `governance_registry_write` for that event. The workflow supplies the governance path, event ID, sequence, previous hash, event hash, expected registry hash, and single-editor identity internally.

- User-maintained JSONL rows: `0`
- User-supplied IDs or hashes: `0`
- User-run commands: `0`
- User authorization decisions for one logical append: `1`
- Changed files after the authorized append: the matching append-only log, the derived registry, and the derived summary
- Service, database, daemon, network, migration setup, or third-party package required: none

The deterministic rehearsal is covered by `test_governance_tool.py`. It proves the local interaction and mutation boundary only. Agent-level paired behavior, installation identity, a new forward task, cross-company behavior, and real effectiveness remain `UNVERIFIED` until their separately authorized gates run.
