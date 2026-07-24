# 工作簿与技能交接

## 写入前提

只写业务员指定的本地 `.xlsx`。写入后必须重新打开验证；失败时输出结构化待写入包，不得声称成功。

只在业务员明确指定文件并授权本次写入后操作；不得修改其他工作簿、邮件归档或外部系统。`workbook_update_packet` 必须包含目标文件、工作表、操作类型、稳定编号、拟写字段、依据、所需业务员决定和重新打开验证结果。重新打开时核对工作表、编号、变更单元格和保存后的值。

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

表头必须精确为：

```text
客户总览: customer_id, company_name, legal_name, website, country, business_model, screening_status, salesperson_classification, information_reliability, risk_gate, recommended_opportunity_id, primary_contact_id, last_research_date, last_touch_date, next_action, next_action_date, handoff_status, salesperson_notes
公司研究: research_id, customer_id, research_level, section, finding_original, finding_zh_summary, evidence_id, evidence_state, source_published_at, observed_at, gap_or_conflict, salesperson_confirmed
项目机会: opportunity_id, customer_id, customer_fact, application_or_purchase_scenario, approved_product_reference, fit_basis, validation_question, primary_contact_id, recommendation_state, salesperson_decision, decision_date
联系人: contact_id, customer_id, name, title, possible_role, role_evidence_id, channel, contact_value, authenticity_state, source_reliability, usage_permission, contact_order, ordering_basis, observed_at, salesperson_approval
证据来源: evidence_id, customer_id, source_type, source_title, source_url_or_local_reference, source_owner, source_language, original_excerpt, zh_summary, published_at, observed_at, evidence_state, access_scope, conflict_note
海关与贸易: trade_record_id, customer_id, data_source, access_scope, coverage_country, coverage_period, observed_entity_name, observed_entity_address, entity_match_basis, trade_direction, shipment_period, visible_frequency, product_description, hs_code, quantity, quantity_unit, weight, weight_unit, declared_value, declared_currency, partner_or_country, limitation_note, observed_at, evidence_id
风险核验: risk_id, customer_id, risk_type, matched_entity, match_basis, allegation_or_record, evidence_id, jurisdiction, record_date, observed_at, evidence_state, false_match_risk, gate_status, reviewer_decision, decision_date
触达记录: touch_id, customer_id, contact_id, channel, touch_stage, content_status, planned_date, actual_sent_at, actual_content_or_local_reference, response_state, response_at, next_action, next_action_date, salesperson_approved
移交记录: handoff_id, customer_id, trigger_channel, trigger_touch_id, response_reference, development_snapshot_reference, open_questions, risk_gate_status, target_skill, handoff_status, salesperson_decision, decision_date
```

每个工作表的资产合同是：冻结第 1 行，在表头行启用自动筛选，使用可读列宽，长文本列换行，并应用一致表头样式。模板的所有数据行保持为空。日期使用 ISO `YYYY-MM-DD`；实际发送和回复时间使用带显式 UTC 偏移的 ISO 8601 时间戳。未知值留空，不得猜测。

下列字段只能使用对应受控状态：

```text
screening_status: 待业务员筛选, 已确认, 已暂停, 已关闭
salesperson_classification: 不继续, 普通候选, 潜力客户
information_reliability: 资料充分且一致, 整体可信但存在缺口, 存在重大冲突需要核验, 证据不足无法判断
evidence_state: 官方直接证据, 多来源相互印证, 单一来源待验证, 合理推断, 来源相互冲突, 信息已经过期, 来源不明隔离待核实
usage_permission: 正常使用, 限制使用, 隔离待核实
risk_gate: 未触发, 待核验, 业务员批准继续, 已关闭
content_status: 草稿, 业务员批准, 计划触达, 实际发送, 实际回复
handoff_status: 未触发, 触达已暂停, 待邮件助手, 已移交, 业务员已决定
```

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
