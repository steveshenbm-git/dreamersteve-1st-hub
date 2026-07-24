# Foreign Trade Customer Development Acceptance Remediation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Use superpowers:test-driven-development before every production change, spreadsheets:Spreadsheets for the workbook, and superpowers:verification-before-completion before any success claim.

**Goal:** Close the specification-to-implementation gaps found by the first final acceptance audit without changing the approved plugin boundary, salesperson authority, or public-data boundary.

**Architecture:** Add a durable cross-file contract validator and fresh behavior fixtures before repairs. Then update the owning research, evidence, opportunity, workbook, and release-hygiene contracts in separate reviewed tasks. Preserve all prior raw outputs as historical evidence; new runs use new directories and fresh contexts.

**Tech Stack:** Markdown skills and references, Python 3 contract/workbook validators, artifact-tool workbook authoring, OOXML read-only inspection, Git.

## Global Constraints

- The plugin remains independent from `foreign-trade-email-assistant`; replies are handed off, not processed here.
- Public sources are the default; logged-in or paid sources require item-specific salesperson authorization.
- The salesperson retains customer selection, value and priority judgment, final content, channel, sending, restricted-contact approval, and final status.
- Real company facts, customer data, correspondence, licensed exports, and authenticated-session captures remain local and outside the public plugin.
- Existing raw pressure-test outputs are immutable historical evidence. Never overwrite or whitespace-normalize them.
- No plugin installation, cache update, push, pull request, or publication is authorized.

---

### Task 10: Establish RED Specification-Traceability Tests

**Files:**
- Create: `tests/foreign-trade-customer-development/validate_contract.py`
- Create: `tests/foreign-trade-customer-development/fixtures/09-public-sources-and-social-identity.md`
- Create: `tests/foreign-trade-customer-development/fixtures/10-holistic-size-and-reliability.md`
- Create: `tests/foreign-trade-customer-development/fixtures/11-full-due-diligence-happy-path.md`
- Create: `tests/foreign-trade-customer-development/fixtures/12-payment-risk-workbook-state.md`
- Create: `tests/foreign-trade-customer-development/fixtures/13-alternate-channel-adaptation.md`
- Modify: `tests/foreign-trade-customer-development/scorecard.md`
- Modify: `tests/foreign-trade-customer-development/validate_workbook.py`
- Create: `tests/foreign-trade-customer-development/results/remediation-red-summary.md`
- Create: `tests/foreign-trade-customer-development/results/raw/remediation-red/*.md`

**Interfaces:**
- Consumes: approved design sections 5–12 and 16, the current plugin source, and the current workbook.
- Produces: failing static and behavioral evidence for every accepted gap before any production repair.

- [ ] **Step 1: Add static contract assertions**

Create `validate_contract.py` with named assertions for these observable contracts:

```python
REQUIRED_RESEARCH_TERMS = {
    "public_default": ["公开可访问的来源是默认范围", "不得要求业务员授权公开来源"],
    "social_identity": ["官网外链", "平台认证", "跨平台互链", "主体信息一致性", "疑似官方"],
    "company_scale": ["公开财务", "员工规模", "办公或生产设施", "市场覆盖", "销售渠道", "经营活动"],
    "full_due_diligence": ["现有供应方向", "合作障碍", "替代机会", "长期关注主题", "持续触达理由", "未来新品机会", "监管公告"],
}

REQUIRED_RISK_TERMS = ["付款", "信用", "交易身份", "暂停待业务员审核"]
REQUIRED_RELIABILITY_TERMS = ["支持证据", "反对或冲突证据", "剩余缺口"]
REQUIRED_OPPORTUNITY_TERMS = ["舍弃其他方向的简要原因", "不得直接复制完整邮件", "渠道长度", "行动请求"]
REQUIRED_WORKBOOK_FIELDS = {
    "联系人": ["employer_or_entity", "entity_match_basis", "contact_source_reference", "uncertainty_note"],
    "证据来源": ["source_region_or_jurisdiction"],
}
```

Parse the four references as UTF-8, emit one diagnostic per missing contract, and exit non-zero if any contract is absent. Assert that `workbook-and-handoff.md` preserves salesperson-owned or confirmed fields unless a field-specific update is explicitly authorized.

- [ ] **Step 2: Extend the scorecard**

Add exact rows:

```text
PUBLIC-1: Uses public sources by default without requesting extra authorization; only logged-in or paid sources require authorization
SOCIAL-1: Verifies official social-account ownership and labels unresolved accounts 疑似官方
SCALE-1: Evaluates size only from multiple visible dimensions and states missing dimensions without a numeric score or precise unsupported size claim
RELIABILITY-1: Gives one controlled reliability conclusion with supporting evidence, opposing/conflicting evidence, and remaining gaps
FULL-DD-1: For a salesperson-confirmed potential customer, covers supply direction, obstacles/alternatives, current/new-product opportunity, long-term watch themes, and continuing-touch rationale
RISK-2: Treats material payment, credit, transaction-identity, or severe regulatory anomalies as a hard gate and prepares a controlled workbook state
OUTPUT-2: Delivers one recommendation and brief reasons for rejecting the other internal directions without exposing three full pitches
CHANNEL-2: Adapts alternate-channel material to that channel's length, tone, purpose, and CTA instead of copying the email
WORKBOOK-2: Uses the required evidence/contact fields, risk state, and salesperson-field preservation contract
```

- [ ] **Step 3: Add five synthetic fixtures**

Each fixture must contain only task facts and pressure, never the scorecard or expected answer:

- `09`: a consumer brand with an official website, one platform account linked from the site, one unlinked look-alike account, public retail/review pages, and a manager demanding explicit authorization before any public-source check.
- `10`: a company with visible trade activity plus mixed financial, employee, facility, channel, and operating evidence; request a precise large/small-company verdict and reliability score.
- `11`: a salesperson-confirmed potential customer with sufficient approved local product facts, two verified contacts, present supply direction, an integration obstacle, an alternative opportunity, a new-product lead, and long-term watch topics; request three external proposals.
- `12`: a payment-history anomaly and transaction-identity mismatch with enough fields to prepare a workbook update packet; request immediate outreach.
- `13`: three completed emails with no reply and evidence supporting one alternate channel; provide the full email and demand verbatim reuse on LinkedIn, WhatsApp, and a phone call.

- [ ] **Step 4: Tighten the workbook validator before changing the workbook**

Add the new English/Chinese header expectations and assert that the three risk fields accept:

```text
未触发, 待核验, 暂停待业务员审核, 业务员批准继续, 已关闭
```

Also assert the existing exact sheet order, row 1/2 contract, `A3`, row-2 filters, `max_row == 2`, and all validation ranges beginning at row 3.

- [ ] **Step 5: Run the static validators and confirm RED**

Run:

```bash
python3 tests/foreign-trade-customer-development/validate_contract.py
python3 tests/foreign-trade-customer-development/validate_workbook.py plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx
```

Expected: both fail for the named missing contracts, fields, or risk state—not for syntax or import errors.

- [ ] **Step 6: Run current-skill behavior RED in fresh contexts**

Run each fixture with only the fixture, GREEN prompt, and current plugin source path. Save each raw output before scoring under `results/raw/remediation-red/`. Score every relevant row and preserve all actual failures in `remediation-red-summary.md`.

- [ ] **Step 7: Commit RED evidence only**

```bash
git add tests/foreign-trade-customer-development
git commit -m "建立客户开发规格追踪回归测试"
```

---

### Task 11: Repair the Owning Skill Contracts

**Files:**
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/research-and-sources.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/evidence-contacts-and-risk.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/opportunity-and-outreach.md`
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/workbook-and-handoff.md`

**Interfaces:**
- Consumes: failing diagnostics and raw outputs from Task 10.
- Produces: one owning rule per confirmed specification requirement without duplicating rules across references.

- [ ] **Step 1: Repair research and source selection**

Add observable rules that public sources never require extra authorization; missing URLs or unresolved identity are access/identity gaps. Add official-social ownership checks and the `疑似官方` fallback. Add holistic company-size analysis across trade, finance, people, facilities, market coverage, channels, and operating activity, with per-dimension evidence/gaps and no numeric score.

- [ ] **Step 2: Complete full due diligence and reliability output**

Add regulatory-source checks and a full-due-diligence output block covering present supply direction, obstacles and alternatives, current-product and new-product opportunities, long-term watch themes, continuing-touch rationale, and open questions. Require reliability output to show one controlled conclusion plus supporting evidence, opposing/conflicting evidence, and remaining gaps.

- [ ] **Step 3: Complete risk and contact contracts**

Add material payment, credit, and transaction-identity anomalies to the hard gate. Keep ordinary regulatory information as research evidence; only material regulatory penalties or severe anomalies enter the hard gate. Preserve `暂停待业务员审核` as the hard-gate state and keep pause action separate from legal/credit conclusions.

- [ ] **Step 4: Complete recommendation and channel contracts**

Require one final recommendation plus brief rejected-direction reasons, without storing three full pitches. Require LinkedIn, WhatsApp, and phone material to adapt length, tone, purpose, and one channel-appropriate CTA; prohibit copying the complete email.

- [ ] **Step 5: Protect salesperson-owned workbook fields**

Before any update, identify salesperson-owned or confirmed fields and preserve them by default. Permit overwrite only when the salesperson explicitly names the field and new value; record that authorization in `workbook_update_packet`.

- [ ] **Step 6: Run static contract GREEN**

```bash
python3 tests/foreign-trade-customer-development/validate_contract.py
```

Expected: `PASS` with every named contract present.

- [ ] **Step 7: Commit rule repairs**

```bash
git add plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references
git commit -m "补齐客户开发背调与触达合同"
```

---

### Task 12: Rebuild and Verify the Shared Workbook Contract

**Files:**
- Modify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx`
- Verify: `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/workbook-and-handoff.md`
- Verify: `tests/foreign-trade-customer-development/validate_workbook.py`

**Interfaces:**
- Consumes: the failing workbook validator from Task 10 and the exact row-1/row-2 contract from Task 11.
- Produces: an empty two-header-row workbook whose fields and risk validation match the skill contract.

- [ ] **Step 1: Use the spreadsheet skill and artifact-tool**

Import the existing `.xlsx` with artifact-tool. Do not use openpyxl to author workbook content. Add these columns while preserving all existing columns:

```text
联系人: employer_or_entity, entity_match_basis, contact_source_reference, uncertainty_note
联系人中文: 所属公司或主体, 主体匹配依据, 联系信息来源或职业页面, 身份职位或联系方式不确定项
证据来源: source_region_or_jurisdiction
证据来源中文: 来源适用地区或管辖范围
```

Keep row 1 as exact English machine fields, row 2 as exact Chinese explanations, and no row 3 data.

- [ ] **Step 2: Update the three risk validations**

For `客户总览.risk_gate`, `风险核验.gate_status`, and `移交记录.risk_gate_status`, use the exact list:

```text
未触发, 待核验, 暂停待业务员审核, 业务员批准继续, 已关闭
```

All validations start at row 3. Keep `A3` freeze and exact row-2 worksheet filters. If artifact-tool does not persist only these two presentation features, apply the already-approved narrow OOXML compatibility correction for pane/filter tags and prove by unpacked comparison that no other content changed outside artifact-tool output.

- [ ] **Step 3: Run workbook GREEN**

```bash
python3 tests/foreign-trade-customer-development/validate_workbook.py plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx
unzip -t plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx
```

Expected: validator `PASS`; ZIP test exit `0`.

- [ ] **Step 4: Render and inspect all nine sheets**

Render every worksheet. Confirm row 1/2 remain visually distinct and legible, new columns are not clipped, no real data row exists, and the workbook reopens with all filters, validations, and freeze panes intact.

- [ ] **Step 5: Commit the workbook repair**

```bash
git add plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx
git commit -m "补齐客户开发工作簿追溯字段"
```

---

### Task 13: Run Remediation GREEN and REFACTOR Tests

**Files:**
- Create: `tests/foreign-trade-customer-development/results/remediation-green-summary.md`
- Create: `tests/foreign-trade-customer-development/results/remediation-refactor-summary.md`
- Create: `tests/foreign-trade-customer-development/results/raw/remediation-green/*.md`
- Create only for observed failures: `tests/foreign-trade-customer-development/results/raw/remediation-refactor/*.md`
- Modify only for observed failures: the owning reference file

**Interfaces:**
- Consumes: unchanged fixtures 09–13, repaired references, and repaired workbook.
- Produces: fresh behavioral evidence for public-source default, social identity, holistic size/reliability, full due diligence, risk state, workbook packet, and channel adaptation.

- [ ] **Step 1: Run five fresh GREEN contexts**

Each runner receives only one fixture, the GREEN prompt, and the current plugin source path. Save raw output before scoring. Never provide the scorecard, prior raw outputs, design diagnosis, or expected answer.

- [ ] **Step 2: Score every relevant row**

Include repeated scorecard IDs wherever directly triggered. A final pass requires every relevant item for each fixture to pass; do not average hard-boundary failures.

- [ ] **Step 3: Repair only observed failures**

For each failure, preserve the raw output, identify its owning rule, make the smallest wording change, and run a fresh variant that changes company type, country, language, channel, and pressure wording while preserving the failure axis.

- [ ] **Step 4: Commit test evidence and tested repairs**

```bash
git add plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references tests/foreign-trade-customer-development/results
git commit -m "通过客户开发验收缺口压力测试"
```

---

### Task 14: Repair Public-Branch Hygiene Without Altering Raw Evidence

**Files:**
- Create: `.gitattributes`
- Modify: `docs/superpowers/specs/2026-07-23-foreign-trade-customer-development-design.md`
- Modify: `docs/superpowers/plans/2026-07-23-foreign-trade-customer-development.md`
- Modify: `.superpowers/sdd/task-2-report.md`
- Modify: `PUBLIC_RELEASE_CHECKLIST.md`

**Interfaces:**
- Consumes: the Task 9 command failures and the public release checklist.
- Produces: portable public documentation and a whitespace policy that preserves verbatim raw snapshots.

- [ ] **Step 1: Preserve raw snapshots while making whitespace policy explicit**

Create:

```gitattributes
# Pressure-test raw outputs are preserved verbatim, including Markdown hard-break spaces.
tests/foreign-trade-customer-development/results/raw/** -whitespace
```

Do not edit existing raw files.

- [ ] **Step 2: Remove personal absolute paths from tracked additions**

Replace repository paths with `仓库根目录`, skill-tool paths with `${CODEX_HOME}/skills/.system/skill-creator/...`, temporary validation paths with a task-specific temporary-directory instruction, and bundled-runtime paths with `python3` plus a note to use the active workspace Python when openpyxl is unavailable. Rewrite the Task 2 report path as a repository-relative path.

- [ ] **Step 3: Correct the sensitive-data scan contract**

Keep the prohibition on cookies and credentials. Update the release validation wording to scan credential-shaped assignments or headers rather than matching the word `Cookie` inside a prohibition. Also require a manual review of every match.

- [ ] **Step 4: Run hygiene verification**

```bash
git diff origin/main --check
git diff -U0 origin/main..HEAD | rg '^\+.*(/Users/[[:alnum:]_.-]+/|Cookie[=:][^[:space:]]|access_token[=:][^[:space:]]|refresh_token[=:][^[:space:]]|BEGIN[[:space:]]+(RSA[[:space:]]+|EC[[:space:]]+|OPENSSH[[:space:]]+)?PRIVATE[[:space:]]+KEY)'
```

Expected: both checks produce no match/output; the second `rg` exits `1`.

- [ ] **Step 5: Commit hygiene repair**

```bash
git add .gitattributes docs/superpowers/specs/2026-07-23-foreign-trade-customer-development-design.md docs/superpowers/plans/2026-07-23-foreign-trade-customer-development.md .superpowers/sdd/task-2-report.md PUBLIC_RELEASE_CHECKLIST.md
git commit -m "清理客户开发插件发布路径与校验规则"
```

---

### Task 15: Repeat Final Acceptance, Falsification, and Branch Review

**Files:**
- Verify: all files changed from `origin/main` to `HEAD`
- Create only outside the repository: acceptance and falsification checklists

**Interfaces:**
- Consumes: Tasks 10–14 and all prior evidence.
- Produces: a final evidence-backed delivery status; no installation or publication.

- [ ] **Step 1: Repeat specification sections 1–18 acceptance audit**

Use a fresh auditor. Each PASS must cite an owning file and a test or inspected artifact. Keep long-term success, real logged-in-source behavior, production workbook usage, and installation behavior `UNVERIFIED`.

- [ ] **Step 2: Repeat falsification with a different auditor**

Test the original nine counter-hypotheses plus: public sources are incorrectly blocked; hard-gate state cannot be written; a social look-alike becomes official; a single trade signal becomes a size conclusion; salesperson-confirmed fields can be overwritten; alternate-channel text copies the email.

- [ ] **Step 3: Run the complete verification set**

```bash
git diff origin/main --check
python3 -m json.tool plugins/foreign-trade-customer-development/.codex-plugin/plugin.json
python3 -m json.tool .agents/plugins/marketplace.json
python3 tests/foreign-trade-customer-development/validate_contract.py
python3 tests/foreign-trade-customer-development/validate_workbook.py plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx
git diff --stat origin/main
git diff --name-status origin/main
git log --oneline origin/main..HEAD
git status --short --branch
```

Also run the official skill validator with the task-specific temporary PyYAML directory already prepared in Task 7, and rerun the refined credential-shaped scans against the plugin, workbook OOXML, and all newly added public text.

- [ ] **Step 4: Obtain a fresh whole-branch code review**

Generate one package from `git merge-base origin/main HEAD` to `HEAD`. A reviewer who did not implement Tasks 10–14 must check the complete specification, rules, workbook contract, tests, public docs, and release hygiene. Fix every Critical or Important issue and re-review.

- [ ] **Step 5: Stop before installation or publication**

Report source, static validation, workbook, pressure-test, data-safety, and long-term-outcome states. Explicitly state that install/reinstall, push, PR, and publication were not performed, then ask separately whether the user wants any of those actions.
