# 工作簿与技能交接

## 写入前提

只写业务员指定的本地 `.xlsx`。写入后必须重新打开验证；失败时输出结构化待写入包，不得声称成功。

只在业务员明确指定文件并授权本次写入后操作；不得修改其他工作簿、邮件归档或外部系统。`workbook_update_packet` 必须包含目标文件、工作表、操作类型、稳定编号、拟写字段、依据、所需业务员决定和重新打开验证结果。重新打开时核对工作表、编号、变更单元格和保存后的值。

每次更新前，先按稳定编号识别业务员自有字段或业务员已确认字段，包括客户分类、业务员备注、业务员决定、批准状态及其决定日期；这些字段默认保留、不覆盖。只有业务员明确指定字段及新值时才允许改写，并在 `workbook_update_packet` 中逐项记录原值、字段、新值、授权内容和授权时间；对一个字段的授权不得扩展到其他字段。

可见工作表顺序必须为：

1. 客户总览
2. 公司研究
3. 项目机会
4. 联系人
5. 证据来源
6. 海关与贸易
7. 风险核验
8. 触达记录
9. 移交记录

第 1 行是机器字段名，必须精确为：

```text
客户总览: customer_id, company_name, legal_name, website, country, business_model, screening_status, salesperson_classification, information_reliability, risk_gate, recommended_opportunity_id, primary_contact_id, last_research_date, last_touch_date, next_action, next_action_date, handoff_status, salesperson_notes
公司研究: research_id, customer_id, research_level, section, finding_original, finding_zh_summary, evidence_id, evidence_state, source_published_at, observed_at, gap_or_conflict, salesperson_confirmed
项目机会: opportunity_id, customer_id, customer_fact, application_or_purchase_scenario, approved_product_reference, fit_basis, validation_question, primary_contact_id, recommendation_state, salesperson_decision, decision_date
联系人: contact_id, customer_id, name, title, possible_role, role_evidence_id, channel, contact_value, authenticity_state, source_reliability, usage_permission, contact_order, ordering_basis, observed_at, salesperson_approval, employer_or_entity, entity_match_basis, contact_source_reference, uncertainty_note
证据来源: evidence_id, customer_id, source_type, source_title, source_url_or_local_reference, source_owner, source_language, original_excerpt, zh_summary, published_at, observed_at, evidence_state, access_scope, conflict_note, source_region_or_jurisdiction
海关与贸易: trade_record_id, customer_id, data_source, access_scope, coverage_country, coverage_period, observed_entity_name, observed_entity_address, entity_match_basis, trade_direction, shipment_period, visible_frequency, product_description, hs_code, quantity, quantity_unit, weight, weight_unit, declared_value, declared_currency, partner_or_country, limitation_note, observed_at, evidence_id
风险核验: risk_id, customer_id, risk_type, matched_entity, match_basis, allegation_or_record, evidence_id, jurisdiction, record_date, observed_at, evidence_state, false_match_risk, gate_status, reviewer_decision, decision_date
触达记录: touch_id, customer_id, contact_id, channel, touch_stage, content_status, planned_date, actual_sent_at, actual_content_or_local_reference, response_state, response_at, next_action, next_action_date, salesperson_approved
移交记录: handoff_id, customer_id, trigger_channel, trigger_touch_id, response_reference, development_snapshot_reference, open_questions, risk_gate_status, target_skill, handoff_status, salesperson_decision, decision_date
```

第 2 行是业务可读的中文字段说明，必须与第 1 行逐列对应并精确为：

```text
客户总览: 客户编号, 公司常用名称, 法定注册名称, 公司网站, 国家或地区, 商业模式, 筛选状态, 业务员客户分类, 信息可靠性, 风险门状态, 推荐机会编号, 主要联系人编号, 最近研究日期, 最近触达日期, 下一步行动, 下一步行动日期, 移交状态, 业务员备注
公司研究: 研究记录编号, 客户编号, 研究层级, 研究章节, 原文研究发现, 研究发现中文摘要, 证据编号, 证据状态, 来源发布日期, 观察记录时间, 信息缺口或冲突, 业务员确认状态
项目机会: 机会编号, 客户编号, 已确认客户事实, 应用或采购场景, 已批准产品引用, 匹配依据, 待验证问题, 主要联系人编号, 推荐状态, 业务员决定, 决定日期
联系人: 联系人编号, 客户编号, 联系人姓名, 职务名称, 可能承担的角色, 角色证据编号, 联系渠道, 联系方式内容, 真实性状态, 来源可靠性, 使用许可, 联系顺序, 排序依据, 观察记录时间, 业务员批准状态, 所属公司或主体, 主体匹配依据, 联系信息来源或职业页面, 身份职位或联系方式不确定项
证据来源: 证据编号, 客户编号, 来源类型, 来源标题, 来源网址或本地引用, 来源主体, 来源语言, 原文摘录, 中文摘要, 来源发布日期, 观察记录时间, 证据状态, 访问范围, 冲突说明, 来源适用地区或管辖范围
海关与贸易: 贸易记录编号, 客户编号, 数据来源, 访问范围, 覆盖国家或地区, 覆盖期间, 观察到的企业名称, 观察到的企业地址, 主体匹配依据, 贸易方向, 货运期间, 可见交易频次, 产品描述, 海关编码, 数量, 数量单位, 重量, 重量单位, 申报价值, 申报币种, 贸易伙伴或国家, 数据局限说明, 观察记录时间, 证据编号
风险核验: 风险记录编号, 客户编号, 风险类型, 匹配到的主体, 主体匹配依据, 指控或记录内容, 证据编号, 管辖地区, 记录日期, 观察记录时间, 证据状态, 误匹配风险, 风险门状态, 审核人决定, 决定日期
触达记录: 触达记录编号, 客户编号, 联系人编号, 触达渠道, 触达阶段, 内容状态, 计划日期, 实际发送时间, 实发内容或本地引用, 回复状态, 回复时间, 下一步行动, 下一步行动日期, 业务员批准状态
移交记录: 移交记录编号, 客户编号, 触发渠道, 触发触达记录编号, 回复内容引用, 客户开发快照引用, 未解决问题, 风险门状态, 目标技能, 移交状态, 业务员决定, 决定日期
```

每个工作表的资产合同是：第 1 行使用一致的机器/结构表头样式，第 2 行使用明显区分的中文业务表头样式；冻结前两行（`A3`），在第 2 行启用工作表级自动筛选，使用同时容纳英文字段名和中文说明的可读列宽，必要时换行。数据从第 3 行开始，公开模板不含任何数据行，因此最大行号必须为 2。日期使用 ISO `YYYY-MM-DD`；实际发送和回复时间使用带显式 UTC 偏移的 ISO 8601 时间戳。未知值留空，不得猜测。所有受控状态的数据验证范围从第 3 行开始，不得覆盖第 2 行中文说明。

下列字段只能使用对应受控状态：

```text
screening_status: 待业务员筛选, 已确认, 已暂停, 已关闭
salesperson_classification: 不继续, 普通候选, 潜力客户
information_reliability: 资料充分且一致, 整体可信但存在缺口, 存在重大冲突需要核验, 证据不足无法判断
evidence_state: 官方直接证据, 多来源相互印证, 单一来源待验证, 合理推断, 来源相互冲突, 信息已经过期, 来源不明隔离待核实
usage_permission: 正常使用, 限制使用, 隔离待核实
risk_gate: 未触发, 待核验, 暂停待业务员审核, 业务员批准继续, 已关闭
content_status: 草稿, 业务员批准, 计划触达, 实际发送, 实际回复
handoff_status: 未触发, 触达已暂停, 待邮件助手, 已移交, 业务员已决定
```

`客户总览.risk_gate`、`风险核验.gate_status` 和 `移交记录.risk_gate_status` 必须使用同一组 `risk_gate` 受控值。风险硬门命中时，在同一待写入包或获授权的写入中，将 `客户总览.risk_gate` 与对应 `风险核验.gate_status` 都设为 `暂停待业务员审核`；在业务员明确审核并将风险门批准为 `业务员批准继续` 前，不得恢复推荐、准备触达材料或继续触达。

只有在实际创建移交快照时，才写入该条 `移交记录.risk_gate_status`，并保存快照创建时的同一受控风险状态。不得只为同步风险门而新建或改写移交记录；尚未发生移交时，风险状态只传播到客户总览和对应风险记录。

## 稳定编号

使用 customer_id、research_id、opportunity_id、contact_id、evidence_id、trade_record_id、risk_id、touch_id 和 handoff_id。公司名称不是唯一键。

更新前先用稳定编号定位记录，再核对 `customer_id` 的引用关系。不得仅凭公司名、品牌名或联系人名称合并记录。

## 状态分离

内部候选、最终推荐、业务员批准、计划触达、实际发送和实际回复必须分开。AI草稿不得标为实发。证据记录追加，不覆盖旧来源。

- `项目机会.recommendation_state` 明示区分内部候选、最终推荐和证据不足结论；只允许保存候选摘要，不保存三个完整内部推演。
- `项目机会.salesperson_decision` 和 `decision_date` 单独记录业务员决定，不得因存在最终推荐而自动填写。
- `触达记录.content_status` 只使用受控状态。进入“业务员批准”需真实批准；进入“实际发送”需实际发送证据、`actual_sent_at` 和实发内容或本地引用；进入“实际回复”需实际回复、`response_at` 和回复引用。
- 计划触达不得倒填为实际发送，实际回复不得由打开、阅读或点击信号推定。实发与实际回复使用独立记录和稳定编号，保留对应时间戳与内容引用。

## 回复硬停

任一渠道收到回复即暂停原触达计划。保存实际回复，输出客户编号、已确认资料、实发记录、回复、未解决问题、风险和证据引用。

收到回复时，先将 `handoff_status` 设为“触达已暂停”，取消未发送的后续计划，不再生成新触达内容。只有保存真实回复和发送历史后，才可准备 `email_assistant_handoff`；未获得工作簿写入授权时，输出待写入包和交接包，不声称已写入。

## 邮件助手移交

target_skill 固定为 foreign-trade-email-assistant。邮件助手处理当前回复后，由业务员决定明确商机、暂时无项目返回长期触达、或关闭。

`email_assistant_handoff` 使用新 `handoff_id`，必须包含 `customer_id`、`trigger_channel`、`trigger_touch_id`、已确认资料、实发记录、回复原文或本地引用、未解决问题、风险门状态、证据引用、`target_skill` 和待业务员决定项。交接是对当前真实回复的处理入口，不授权邮件助手决定客户价值、优先级、发送、受限联系方式或最终状态。

## 现有接口兼容

交接包至少包含 company_identity、website_and_region、business_type、main_products、fit_hypotheses、contact_identity_and_possible_role、development_angles、source_url_or_local_reference、observed_at 和 evidence_state。额外字段不得改变邮件助手的职责。

上述字段必须基于已保存证据；多来源时保留各自的 `source_url_or_local_reference`、`observed_at` 和 `evidence_state`。`development_angles` 只包含最终推荐或明确的证据不足结论，不包含三个完整内部推演。
