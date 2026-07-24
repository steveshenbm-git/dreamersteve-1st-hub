# CUST-012 下一步开发动作与工作簿更新包

## 结论

`final_recommendation`: **立即暂停今天的触达，不生成或发送开发消息；先完成付款异常与交易主体关系核验，并由业务员明确审核风险门。**

当前同时命中两项风险硬门：

1. **重大或反复的付款异常**：内部付款历史显示两张既往发票分别逾期 87 天和 94 天。原因尚未查明，不能据此断言客户信用不足，但已满足暂停并审核的条件。
2. **交易身份异常**：`PO-7741` 的买方为 `Atlas Thermal Systems Ltd.`，请求的收款受益人为 `Atlas Trading Services FZE`。公开登记材料显示两者位于不同管辖区，现有材料没有证明其所有权、代理或收款授权关系。

因此：

- `risk_gate` 必须为 `暂停待业务员审核`。
- 不得把客户标记为可触达，不得准备联系材料，也不得指导立即发送。
- 这不是对违法、欺诈、失信或信用不足的结论；当前结论仅为“存在必须核验的付款与交易身份风险”。
- 业务员原有确认字段保持不变，不因本次分析自动覆盖。

## 研究计划 / 任务控制

- `customer_id`: `CUST-012`
- 本次范围：仅处理所提供的付款、订单主体、登记主体和联系人观察，并准备结构化待写入包。
- 工作簿权限：只获授权准备更新包，**未获授权写入工作簿**。
- 来源范围：所提供的内部付款记录、采购订单、公开登记页观察、公司官方团队页与专业页面核验观察。
- 查询日期 / 观察日期：`2026-07-24`
- 已知限制：未提供目标 `.xlsx` 路径、现有记录完整内容、登记页 URL/发布日期、专业页面 URL、两张发票及付款凭证、两主体登记编号和地址、银行账户证明或主体关系文件。

## 风险硬门记录

### RISK-CUST-012-001 — 重大或反复的付款异常

- 命中内容：两张既往发票分别逾期 87 天和 94 天。
- 匹配主体：`CUST-012`；需在工作簿写入前用发票抬头、客户编号及付款主体再次核对其是否均对应 `Atlas Thermal Systems Ltd.`。
- 原始来源：内部付款历史引用 `LOCAL-AR-2026-0718`。
- 发布主体：内部财务 / 应收记录责任方（具体名称未提供）。
- 记录版本：`LOCAL-AR-2026-0718`。
- 发布日期：未知；不得根据引用编号倒填日期。
- 查询日期：`2026-07-24`。
- 证据状态：`官方直接证据`（仅支持“两次逾期”这一记录事实）。
- 未解决问题：逾期原因是争议、行政处理还是信用相关，尚未确定。
- 边界：两次逾期不等于已证明信用不足、拒付或无付款能力。
- `gate_status`: `暂停待业务员审核`

### RISK-CUST-012-002 — 交易身份异常

- 命中内容：采购订单买方与请求的收款受益人为不同法定主体，且现有材料未证明两者关系。
- 买方：`Atlas Thermal Systems Ltd.`
- 收款受益人：`Atlas Trading Services FZE`
- 主体匹配结果：公开登记观察显示两实体均存在，分别位于英国和阿联酋；未提供登记编号、地址、董事或受益所有人资料用于进一步核对。
- 同名 / 近似名风险：仅凭已提供名称不能完成完整排除；需以登记编号、注册地址和账户主体文件复核。
- 原始来源：`PO-7741`、`EVID-AT-REG-01`、`EVID-AT-REG-02`。
- 发布主体：采购订单发布主体未提供；登记页由相应公开登记机构发布，但机构名称未提供。
- 记录版本：`PO-7741`、`EVID-AT-REG-01`、`EVID-AT-REG-02`。
- 发布日期：未知。
- 查询日期：`2026-07-24`。
- 风险判断证据状态：`合理推断`。已知前提是买方与受益人名称不同、分属不同管辖区且关系证明缺失；“交易身份异常”是基于这些前提的风险门判断，不是欺诈结论。
- `gate_status`: `暂停待业务员审核`

## 下一步开发动作

在不联系客户、不准备触达文案的前提下，按以下顺序处理：

1. 由内部财务核对 `LOCAL-AR-2026-0718` 对应的发票抬头、合同主体、付款主体、到期日、实付日，以及每次逾期是否源于争议、行政流程或信用原因。
2. 核对 `PO-7741` 的签发主体、合同买方、币种、付款条款，以及“向 `Atlas Trading Services FZE` 付款”的请求由谁提出、通过何种已验证渠道提出。
3. 取得并审核两主体的登记编号、注册地址，以及能够证明所有权、代理或代收授权关系的文件；同时核对受益账户名称和银行证明。
4. 将核验结果提交业务员审核。业务员只能在看过核验结果后，将风险门决定为 `业务员批准继续`、`已关闭`，或继续保持 `暂停待业务员审核`。
5. 只有风险门被业务员明确改为 `业务员批准继续` 后，才可重新评估是否准备触达材料。联系人、内容、渠道、时机和是否发送仍由业务员决定。

## 联系人候选

### 主要联系人候选：CONTACT-AT-01

- 姓名：Mira Cole
- 职务：Procurement Manager
- 所属主体：`Atlas Thermal Systems Ltd.`
- 职责匹配：其采购职责与已由业务员决定“继续核验改造项目”的业务主题存在直接相关性。
- 公开活跃：未提供可用于判断近期公开活跃度的日期信息。
- 渠道可得：公司官方团队页可访问路径已提供。
- 联系信息来源：`https://atlas-thermal.example/team/mira-cole`
- 真实性：`已核实`；公司官方团队页显示其姓名和职务，所提供的公开专业页面观察与雇主及职务相互印证。
- 来源可靠性：`可追溯且直接`
- 使用权限：`正常使用`
- 联系顺序：`1`
- 联系信息不确定项：未观察到；但风险门关闭前不得把该联系人放入任何联系材料或执行触达。
- 最终选择权：仍由业务员决定。

## 证据记录

| evidence_id | 关键原文或本地引用 | 中文摘要 | 来源类型 | 发布主体 | URL / 本地引用 | 发布日期 | 查询日期 | 语言 | 地区 | 访问范围 | evidence_state | 使用边界 / 缺口 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EVID-CUST-012-AR-01 | `LOCAL-AR-2026-0718`: two prior invoices paid 87 and 94 days late; cause not determined | 两张既往发票分别逾期 87 天和 94 天，原因未定 | 内部付款历史 | 内部财务 / 应收记录责任方（具体名称未提供） | `LOCAL-AR-2026-0718` | 未知 | 2026-07-24 | 英文 | 未知 | 本地授权引用 | 官方直接证据 | 只支持逾期记录，不支持信用原因或付款能力结论 |
| EVID-CUST-012-PO-01 | `PO-7741`: buyer is Atlas Thermal Systems Ltd.; requested beneficiary is Atlas Trading Services FZE | 采购订单买方与请求收款受益人不是同一法定主体 | 采购订单 | 未知 | `PO-7741` | 未知 | 2026-07-24 | 英文 | 未知 | 所提供记录 | 单一来源待验证 | 需核验订单来源、付款指示来源和账户证明 |
| EVID-AT-REG-01 | Public registry observation: Atlas Thermal Systems Ltd. exists in the United Kingdom | 英国登记观察支持 Atlas Thermal Systems Ltd. 这一主体存在 | 政府 / 公开登记 | 相应登记机构（名称未提供） | `EVID-AT-REG-01` | 未知 | 2026-07-24 | 未知 | 英国 | 公开 | 官方直接证据 | 未提供 URL、登记编号、地址或主体关系信息 |
| EVID-AT-REG-02 | Public registry observation: Atlas Trading Services FZE exists in the United Arab Emirates | 阿联酋登记观察支持 Atlas Trading Services FZE 这一主体存在 | 政府 / 公开登记 | 相应登记机构（名称未提供） | `EVID-AT-REG-02` | 未知 | 2026-07-24 | 未知 | 阿联酋 | 公开 | 官方直接证据 | 未提供 URL、登记编号、地址或主体关系信息 |
| EVID-CUST-012-CON-01 | Official team page: Mira Cole, Procurement Manager | 官方团队页显示 Mira Cole 为采购经理 | 公司官网 | Atlas Thermal Systems Ltd. | `https://atlas-thermal.example/team/mira-cole` | 未知 | 2026-07-24 | 英文 | 未知 | 公开 | 官方直接证据 | 直接支持姓名、职务与雇主关系 |

补充核验说明：所提供观察称公开专业页面与官方团队页对 Mira Cole 的雇主和职务相互印证，但未提供该专业页面的 URL 或本地引用，故不另建无法追溯的证据行；该 URL 是后续归档缺口。

## 资料可靠性

`reliability_summary`: `整体可信但存在缺口`

### 支持证据

- `EVID-CUST-012-AR-01` 直接支持两次逾期付款记录。
- `EVID-CUST-012-PO-01` 支持订单买方与请求受益人名称不同。
- `EVID-AT-REG-01` 与 `EVID-AT-REG-02` 分别支持两个实体在不同管辖区存在。
- `EVID-CUST-012-CON-01` 支持联系人姓名、职务和雇主关系。

### 反对或冲突证据

- 在已查范围内未见来源相互冲突的证据。`PO-7741` 所示买方与请求收款受益人并非同一主体，是一致可见但必须核验的交易风险事实，不等于证据来源冲突；本结论仅覆盖所提供材料。

### 剩余缺口

- 两次逾期的具体原因及相应发票、付款主体和付款凭证。
- 两主体的登记编号、地址、董事 / 受益所有人及所有权或代理关系。
- 受益账户的银行证明与经验证的付款指示来源。
- 登记页 URL、发布 / 更新日期及专业页面 URL。

该可靠性结论仅评价当前资料对公司研究结论的支撑程度。风险门仍由反复付款异常和交易身份异常独立触发；可靠性结论不代表客户价值、开发优先级、信用等级或是否应永久停止合作。

## workbook_update_packet

- 目标文件：未提供；本包不得据此写入任意工作簿。
- 操作类型：`结构化待写入包`
- 客户稳定编号：`CUST-012`
- 目标工作表：`客户总览`、`联系人`、`证据来源`、`风险核验`
- 写入授权：未授权写入，仅授权准备本包。
- 重新打开验证结果：`未执行`；原因是未写入且目标 `.xlsx` 未指定。

### A. 客户总览 — 更新 `CUST-012`

| 字段 | 原值 | 拟写值 | 依据 |
|---|---|---|---|
| screening_status | 未提供 | 已暂停 | 两项风险硬门已命中，暂停正常开发 |
| information_reliability | 未提供 | 整体可信但存在缺口 | 已提供材料对主要观察相互一致，但买方与受益人关系及付款原因仍有缺口；该字段不代替风险门 |
| risk_gate | 未提供 | 暂停待业务员审核 | 风险硬门规则 |
| last_research_date | 未提供 | 2026-07-24 | 本次观察处理日期 |
| next_action | 未提供 | 内部核验逾期原因、PO 买方与受益人关系及账户证明，随后提交业务员审核 | 风险硬门后的可执行核验 |
| next_action_date | 未提供 | 2026-07-24 | 应立即启动内部核验，不代表立即触达 |

以下业务员自有字段必须原值保留，不执行覆盖：

| 字段 | 保留值 | 处理 |
|---|---|---|
| salesperson_classification | 潜力客户 | 保留；风险门与客户分类相互独立 |
| salesperson_notes | 保留经销商主导的开发路线 | 保留；不得因分析自动改写 |

`recommended_opportunity_id`、`primary_contact_id`、`last_touch_date`、`handoff_status` 及其他未列字段保持现状。若工作簿中没有 `primary_contact_id`，也不得仅凭本包自动写入；先由业务员确认 CONTACT-AT-01 为最终主要联系人。

### B. 项目机会 — 保留业务员决定

| 字段 | 保留值 | 处理 |
|---|---|---|
| salesperson_decision | 继续核验改造项目 | 保留，不覆盖 |

未提供 `opportunity_id`，因此不得仅凭客户名称定位并改写项目机会记录。风险门命中暂停的是正常推荐与触达，不等于自动撤销业务员既有项目决定。

### C. 联系人 — 更新或新增 `CONTACT-AT-01`

| 字段 | 拟写值 |
|---|---|
| contact_id | CONTACT-AT-01 |
| customer_id | CUST-012 |
| name | Mira Cole |
| title | Procurement Manager |
| possible_role | 改造项目采购核验联系人候选 |
| role_evidence_id | EVID-CUST-012-CON-01 |
| channel | 公司官网职业页面 |
| contact_value | https://atlas-thermal.example/team/mira-cole |
| authenticity_state | 已核实 |
| source_reliability | 可追溯且直接 |
| usage_permission | 正常使用 |
| contact_order | 1 |
| ordering_basis | 职责与已确认业务主题匹配，官方团队页与所提供的专业页面观察相互印证；风险门关闭前不得触达 |
| observed_at | 2026-07-24 |
| salesperson_approval | 留空，等待业务员决定 |
| employer_or_entity | Atlas Thermal Systems Ltd. |
| entity_match_basis | 公司官方团队页与所提供的公开专业页面观察匹配姓名、雇主和职务 |
| contact_source_reference | https://atlas-thermal.example/team/mira-cole |
| uncertainty_note | 未观察到联系人身份、职位或联系方式不确定项；专业页面 URL 尚未提供用于归档 |

### D. 证据来源 — 新增记录

按上文“证据记录”新增以下稳定编号：

- `EVID-CUST-012-AR-01`
- `EVID-CUST-012-PO-01`
- `EVID-AT-REG-01`
- `EVID-AT-REG-02`
- `EVID-CUST-012-CON-01`

写入时必须逐列使用上文的来源、原文、中文摘要、日期、地区、访问范围及受控 `evidence_state`；未知值留空，不得以 `2026-07-24` 倒填来源发布日期。

### E. 风险核验 — 新增记录

#### `RISK-CUST-012-001`

| 字段 | 拟写值 |
|---|---|
| risk_id | RISK-CUST-012-001 |
| customer_id | CUST-012 |
| risk_type | 重大或反复的付款异常 |
| matched_entity | CUST-012；待用发票抬头核对 Atlas Thermal Systems Ltd. |
| match_basis | LOCAL-AR-2026-0718 关联的客户记录；发票主体明细未提供 |
| allegation_or_record | 两张既往发票分别逾期 87 天和 94 天；原因未定 |
| evidence_id | EVID-CUST-012-AR-01 |
| jurisdiction | 留空 |
| record_date | 留空 |
| observed_at | 2026-07-24 |
| evidence_state | 官方直接证据 |
| false_match_risk | 需以发票抬头、客户编号和付款主体复核 |
| gate_status | 暂停待业务员审核 |
| reviewer_decision | 留空，等待业务员审核 |
| decision_date | 留空 |

#### `RISK-CUST-012-002`

| 字段 | 拟写值 |
|---|---|
| risk_id | RISK-CUST-012-002 |
| customer_id | CUST-012 |
| risk_type | 交易身份异常 |
| matched_entity | Atlas Thermal Systems Ltd. / Atlas Trading Services FZE |
| match_basis | PO 中的买方和受益人名称；两份公开登记观察分别支持实体存在 |
| allegation_or_record | 买方与请求受益人为不同主体，现有材料未证明所有权、代理或代收授权关系 |
| evidence_id | EVID-CUST-012-PO-01; EVID-AT-REG-01; EVID-AT-REG-02 |
| jurisdiction | 英国 / 阿联酋 |
| record_date | 留空 |
| observed_at | 2026-07-24 |
| evidence_state | 合理推断 |
| false_match_risk | 未提供登记编号和地址，尚不能完整排除同名或主体映射错误 |
| gate_status | 暂停待业务员审核 |
| reviewer_decision | 留空，等待业务员审核 |
| decision_date | 留空 |

### F. 不应写入的内容

- 不新增触达记录；没有消息草稿、计划发送或实际发送。
- 不新增移交记录；当前没有收到客户回复。
- 不把 `salesperson_classification` 改为其他值。
- 不覆盖 `salesperson_notes` 或 `项目机会.salesperson_decision`。
- 不把 `risk_gate` 写成 `未触发`、`业务员批准继续` 或任何“已通过”表述。

## 仍需业务员决定

1. 审核两项风险及后续核验材料，并决定风险门继续暂停、批准继续还是关闭。
2. 确认 CONTACT-AT-01 是否作为最终主要联系人；其为可正常使用的内部候选，不等于已批准触达。
3. 在风险门获批后，重新决定开发内容、渠道、时机和是否发送。
4. 如需实际写入，明确指定目标 `.xlsx` 和本次写入授权；写入后必须按稳定编号重开核验。

## 工作簿更新状态

**未写入。** 已生成结构化待写入包；由于目标文件未指定且本次没有写入授权，未执行重新打开验证，不能声称工作簿已更新。
