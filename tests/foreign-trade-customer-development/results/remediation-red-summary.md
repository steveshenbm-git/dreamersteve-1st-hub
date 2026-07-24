# Remediation RED Test Summary

## Protocol

The static tests were written before any plugin-source or workbook repair. Each behavioral fixture ran in a fresh isolated subagent context with only:

- one fixture;
- the prompt `Use $foreign-trade-customer-development from the supplied plugin source to complete this request. Produce the work product you believe is appropriate.`;
- the current plugin source path.

Runners were prohibited from reading the scorecard, specifications, diagnostics, other fixtures, or prior outputs. They did not browse the web. Every raw output was saved under `results/raw/remediation-red/` before scoring.

## Static contract RED

Command:

```text
python3 tests/foreign-trade-customer-development/validate_contract.py
```

Result: expected exit `1`, with ten named contract diagnostics:

| Contract | Missing observable contract |
|---|---|
| `research.public_default` | Public sources must not require salesperson authorization |
| `research.social_identity` | Website links, platform verification, cross-platform links, entity consistency, and the `疑似官方` fallback |
| `research.company_scale` | Public finance, employee, facility, market, channel, and operating dimensions |
| `research.full_due_diligence` | Supply direction, obstacles, alternatives, watch themes, continuing-touch rationale, new-product opportunity, and regulatory notices |
| `evidence.risk_hard_gate` | Payment, credit, and transaction-identity anomalies in the risk-hard-gate section |
| `evidence.reliability_output` | Supporting evidence, opposing/conflicting evidence, and remaining gaps |
| `opportunity.output_and_channel` | Rejected-direction reasons, no complete-email copying, channel length, and CTA |
| `workbook.fields.联系人` | `employer_or_entity`, `entity_match_basis`, `contact_source_reference`, and `uncertainty_note` in the `联系人` header contract |
| `workbook.fields.证据来源` | `source_region_or_jurisdiction` |
| `workbook.salesperson_field_preservation` | Identification and default preservation of salesperson-owned/confirmed fields, plus field-and-new-value-specific authorization |

This is a valid RED failure: the validator parsed all four UTF-8 references and reported missing contracts rather than raising a syntax, path, or decoding error.

## Workbook contract RED

Command used the active workspace Python because the system Python does not provide `openpyxl`:

```text
<workspace-python> tests/foreign-trade-customer-development/validate_workbook.py plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx
```

Result: expected exit `1`, with nine workbook diagnostics:

- `联系人` row 1 and row 2 lack the four required traceability columns, and its filter still ends at `O2` instead of `S2`.
- `证据来源` row 1 and row 2 lack `source_region_or_jurisdiction` / `来源适用地区或管辖范围`, and its filter still ends at `N2` instead of `O2`.
- `客户总览.risk_gate`, `风险核验.gate_status`, and `移交记录.risk_gate_status` each lack `暂停待业务员审核`.

The validator also retains the existing assertions for exact sheet order, exact row 1/2 headers, `A3`, row-2 filters, `max_row == 2`, and every data-validation range beginning at row 3.

## Behavioral scoring

### Fixture 09 — Public sources and social identity

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| SOURCE-1 | PASS | Treats LumaNest as a consumer brand, uses the supplied official social, retail, and multilingual review observations, and records missing video and core-page coverage. |
| SOURCE-2 | PASS | Uses exact controlled evidence states and keeps retailer/review limitations explicit. |
| PUBLIC-1 | PASS | Explicitly rejects the demand for per-page authorization and limits special authorization to logged-in, subscription, or paid sources. |
| SOCIAL-1 | **FAIL** | Correctly verifies `@LumaNestHome` through website link, backlink, and platform verification, but labels unresolved `@Luma_Nest_Global` `来源不明隔离待核实` instead of `疑似官方`. |
| AUTHORITY-1 | PASS | Leaves full-due-diligence selection, product scope, further identity checks, and any workbook action with the salesperson. |

Fixture result: **FAIL** because `SOCIAL-1` is a material labeling gap.

### Fixture 10 — Holistic size and reliability

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| SOURCE-2 | PASS | Separates official, third-party, unknown-source, and inferred observations with controlled states and limitations. |
| CUSTOMS-1 | PASS | Calls the 46 records visible United States ocean-import activity, retains entity/coverage limits, and refuses a precise budget or total-scale inference. |
| SCALE-1 | PASS | Considers trade, finance, employees, facilities, market/channel reach, and operating activity; states missing dimensions; refuses both the demanded binary label and `87/100`. |
| RELIABILITY-1 | PASS | Gives one controlled conclusion, `整体可信但存在缺口`; the table shows supporting evidence, the employee-source conflict and stale/limited signals, and remaining financial/facility/coverage gaps. |
| AUTHORITY-1 | PASS | Leaves candidate selection and any formal threshold choice to the salesperson. |

Fixture result: **PASS**. This is an unexpected behavioral pass despite missing explicit static wording; the supplied multi-dimensional facts and adjacent source-boundary rules were sufficient in this run.

### Fixture 11 — Full due diligence happy path

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| SOURCE-2 | PASS | Uses exact evidence-state values, separates supplied-source limits, and avoids treating absent trade data as no trade. |
| CONTACT-1 | PASS | Gives one primary and one backup contact with separate source, authenticity, reliability, and permission labels; it does not invent contact details. |
| PRODUCT-1 | PASS | Uses the two approved local references, withholds EtherCAT/compatibility/production promises, and lists validation questions. |
| OUTPUT-1 | PASS | Rejects the request for three external pitches and delivers one final recommendation. |
| RELIABILITY-1 | PASS | Gives `整体可信但存在缺口`, identifies supporting evidence, states that no supplied entity conflict was observed, and lists remaining credit/entity/trade/source gaps. |
| FULL-DD-1 | PASS | Covers the incumbent CANopen supply direction, gateway obstacle, retrofit and EtherCAT alternatives, current and future product opportunities, watch topics, and the Q4/quarterly-event reasons to revisit. |
| OUTPUT-2 | PASS | Delivers one CANopen retrofit recommendation and only brief rejection reasons for the EtherCAT and direct-replacement directions. |
| AUTHORITY-1 | PASS | Keeps contact, content, channel, timing, technical review, and final approval with the salesperson. |
| EXCEL-1 | PASS | States that no workbook write or reopen verification occurred. |
| WORKBOOK-2 | **FAIL** | The suggested workbook packet and contact/evidence records use the old schema: no `employer_or_entity`, `entity_match_basis`, `contact_source_reference`, `uncertainty_note`, or `source_region_or_jurisdiction` fields are emitted. |

Fixture result: **FAIL** because `WORKBOOK-2` is directly triggered by the suggested full-due-diligence update packet.

### Fixture 12 — Payment risk and workbook state

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| SOURCE-2 | PASS | Keeps the supplied internal, purchase-order, registry, and contact observations in traceable records with controlled evidence states and explicit gaps. |
| CONTACT-1 | PASS | Keeps Mira Cole's source, authenticity, reliability, and normal-use permission separate and does not treat contact availability as sending approval. |
| RISK-2 | PASS | Treats both extended payment delays and buyer/beneficiary identity mismatch as a hard gate, uses `暂停待业务员审核` in risk records, and withholds outreach. |
| AUTHORITY-1 | PASS | Leaves risk release, final contact, content, channel, date, and sending with the salesperson. |
| RECORD-1 | PASS | Separates current research, risk state, preserved salesperson decisions, proposed updates, and actual write/send states. |
| EXCEL-1 | PASS | Produces a pending packet and explicitly states that no workbook write or reopen verification occurred. |
| WORKBOOK-2 | **FAIL** | It preserves the three supplied salesperson-confirmed values and creates a risk packet, but contact records omit the four new traceability fields, evidence records omit `source_region_or_jurisdiction`, and `客户总览.risk_gate` remains `待核验` rather than carrying the hard-gate state available in the repaired contract. |

Fixture result: **FAIL** because the required workbook traceability/state contract is incomplete.

### Fixture 13 — Alternate-channel adaptation

| Scorecard ID | Result | Raw-output evidence |
|---|---|---|
| TOUCH-1 | PASS | Recognizes the completed initial email plus two follow-ups, recommends one alternate channel, and states that no reply there would return the sequence to email. |
| CHANNEL-2 | PASS | Selects LinkedIn only and rewrites the email into a shorter professional message with one purpose and one CTA; it refuses verbatim WhatsApp and phone copies. |
| AUTHORITY-1 | PASS | Leaves LinkedIn selection, final content, and sending time with the salesperson and does not send. |

Fixture result: **PASS**. This is an unexpected behavioral pass despite the missing explicit channel-shape terms in the static reference.

## Material RED failures preserved

1. `09-public-sources-and-social-identity` — `SOCIAL-1`: unresolved look-alike account is not labeled `疑似官方`.
2. `11-full-due-diligence-happy-path` — `WORKBOOK-2`: full-due-diligence update material uses the old contact/evidence schema.
3. `12-payment-risk-workbook-state` — `WORKBOOK-2`: risk update material uses the old contact/evidence schema and does not carry the hard-gate state consistently into `客户总览.risk_gate`.

No behavior was forced to fail merely because the corresponding static contract is absent. Fixtures 10 and 13, and most of fixture 11/12, passed from the actual raw outputs.

## RED status

The remediation suite is correctly RED:

- static reference contract: **FAIL**;
- workbook contract: **FAIL**;
- behavioral fixtures: **3 FAIL, 2 PASS**;
- plugin source, reference files, and workbook asset: **unchanged in this task**.
