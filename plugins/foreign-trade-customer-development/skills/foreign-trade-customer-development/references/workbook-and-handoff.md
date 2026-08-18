# 工作簿与技能交接

## 后台工作簿与业务前台

本文件定义的 12 页工作簿是客户开发机器证据后台，不是业务员的日常操作界面。`foreign-trade-workflow-director` 拥有独立六页 `salesperson_workbench`；本技能只通过 `source_record_id`、`source_packet_reference`、`evidence_reference` 和 `specialist_return_packet` 提供业务投影，不直接写该业务工作簿。

后台中的路线评审、方向、证据、研究、贸易、风险、触达和移交字段必须保留，不能为“看起来简单”而删页、改名或压平。业务前台的路线决定、客户分类、下一步、草稿审核和风险处置只有在业务员给出字段级授权后，才由协调器写入并重开验证；本技能接收返回的稳定编号和决定引用，不覆盖业务员字段。

## 写入前提

只写业务员指定的本地 `.xlsx`。写入后必须重新打开验证；失败时输出结构化待写入包，不得声称成功。

只在业务员明确指定文件并授权本次写入后操作；不得修改其他工作簿、邮件归档或外部系统。`workbook_update_packet` 必须包含目标文件、工作表、操作类型、稳定编号、拟写字段、依据、所需业务员决定和重新打开验证结果。重新打开时核对工作表、编号、变更单元格和保存后的值。

每次更新前，先按稳定编号识别业务员自有字段或业务员已确认字段，包括客户分类、业务员备注、业务员决定、批准状态及其决定日期；这些字段默认保留、不覆盖。只有业务员明确指定字段及新值时才允许改写，并在 `workbook_update_packet` 中逐项记录原值、字段、新值、授权内容和授权时间；对一个字段的授权不得扩展到其他字段。

可见工作表顺序必须为：

1. 路线评审
2. 开发方向
3. 方向证据
4. 客户总览
5. 公司研究
6. 项目机会
7. 联系人
8. 证据来源
9. 海关与贸易
10. 风险核验
11. 触达记录
12. 移交记录

第 1 行是机器字段名，必须精确为：

```text
路线评审: route_review_id, source_route_candidate_id, company_id, product_scope, route_packet_reference, route_packet_sha256, producer_registry_reference, map_route_status, research_readiness, readiness_snapshot_reference, knowledge_snapshot_hash, readiness_fact_ids, commercial_readiness_status, readiness_reviewed_at, stale_status, unresolved_business_conditions, salesperson_route_decision, decision_basis, decision_date
开发方向: direction_id, source_route_review_id, source_route_candidate_id, approved_product_reference, product_boundary, observable_enterprise_rule, candidate_direct_evidence_rule, exclusion_boundary, external_validation_status, direction_status, declared_scope, unresolved_conditions, salesperson_decision, decision_date
方向证据: direction_evidence_id, direction_id, source_type, source_title, source_url_or_local_reference, original_excerpt, zh_summary, published_at, observed_at, evidence_state, validation_effect, limitation_note
客户总览: customer_id, company_name, legal_name, website, country, business_model, source_direction_id, screening_status, salesperson_classification, information_reliability, risk_gate, recommended_opportunity_id, primary_contact_id, last_research_date, last_touch_date, next_action, next_action_date, handoff_status, salesperson_notes
公司研究: research_id, customer_id, research_level, section, finding_original, finding_zh_summary, evidence_id, evidence_state, source_published_at, observed_at, gap_or_conflict, salesperson_confirmed
项目机会: opportunity_id, customer_id, customer_fact, application_or_purchase_scenario, approved_product_reference, fit_basis, validation_question, primary_contact_id, recommendation_state, salesperson_decision, decision_date
联系人: contact_id, customer_id, name, title, possible_role, role_evidence_id, channel, contact_value, authenticity_state, source_reliability, usage_permission, contact_order, ordering_basis, observed_at, salesperson_approval, employer_or_entity, entity_match_basis, contact_source_reference, uncertainty_note
证据来源: evidence_id, customer_id, source_type, source_title, source_url_or_local_reference, source_owner, source_language, original_excerpt, zh_summary, published_at, observed_at, evidence_state, access_scope, conflict_note, source_region_or_jurisdiction
海关与贸易: trade_record_id, customer_id, data_source, access_scope, coverage_country, coverage_period, observed_entity_name, observed_entity_address, entity_match_basis, trade_direction, shipment_period, visible_frequency, product_description, hs_code, quantity, quantity_unit, weight, weight_unit, declared_value, declared_currency, partner_or_country, limitation_note, observed_at, evidence_id
风险核验: risk_id, customer_id, risk_type, matched_entity, match_basis, allegation_or_record, evidence_id, jurisdiction, record_date, observed_at, evidence_state, false_match_risk, gate_status, reviewer_decision, decision_date
触达记录: touch_id, customer_id, contact_id, channel, touch_stage, content_status, planned_date, draft_content_or_local_reference, draft_generated_at, draft_for_touch_stage, automation_run_id, actual_sent_at, actual_content_or_local_reference, response_state, response_at, next_action, next_action_date, salesperson_approved
移交记录: handoff_id, customer_id, trigger_channel, trigger_touch_id, response_reference, development_snapshot_reference, open_questions, risk_gate_status, target_skill, handoff_status, salesperson_decision, decision_date
```

第 2 行是业务可读的中文字段说明，必须与第 1 行逐列对应并精确为：

```text
路线评审: 路线评审编号, 来源路线候选编号, 公司编号, 产品范围, 路线包引用, 路线包哈希, 生产者登记引用, 地图路线状态, 研究就绪状态, 承接视图引用, 知识快照哈希, 承接事实编号, 商业承接状态, 承接复核日期, 时效状态, 未解决业务条件, 业务员路线决定, 决定依据, 决定日期
开发方向: 开发方向编号, 来源路线评审编号, 来源路线候选编号, 已批准产品引用, 产品边界, 可观察目标企业规则, 候选公司直接证据规则, 排除边界, 外部核实状态, 方向状态, 本次声明范围, 待核实条件, 业务员方向决定, 决定日期
方向证据: 方向证据编号, 开发方向编号, 来源类型, 来源标题, 来源网址或本地引用, 原文摘录, 中文摘要, 来源发布日期, 观察记录时间, 证据状态, 对方向的验证作用, 局限说明
客户总览: 客户编号, 公司常用名称, 法定注册名称, 公司网站, 国家或地区, 商业模式, 来源开发方向编号, 筛选状态, 业务员客户分类, 信息可靠性, 风险门状态, 推荐机会编号, 主要联系人编号, 最近研究日期, 最近触达日期, 下一步行动, 下一步行动日期, 移交状态, 业务员备注
公司研究: 研究记录编号, 客户编号, 研究层级, 研究章节, 原文研究发现, 研究发现中文摘要, 证据编号, 证据状态, 来源发布日期, 观察记录时间, 信息缺口或冲突, 业务员确认状态
项目机会: 机会编号, 客户编号, 已确认客户事实, 应用或采购场景, 已批准产品引用, 匹配依据, 待验证问题, 主要联系人编号, 推荐状态, 业务员决定, 决定日期
联系人: 联系人编号, 客户编号, 联系人姓名, 职务名称, 可能承担的角色, 角色证据编号, 联系渠道, 联系方式内容, 真实性状态, 来源可靠性, 使用许可, 联系顺序, 排序依据, 观察记录时间, 业务员批准状态, 所属公司或主体, 主体匹配依据, 联系信息来源或职业页面, 身份职位或联系方式不确定项
证据来源: 证据编号, 客户编号, 来源类型, 来源标题, 来源网址或本地引用, 来源主体, 来源语言, 原文摘录, 中文摘要, 来源发布日期, 观察记录时间, 证据状态, 访问范围, 冲突说明, 来源适用地区或管辖范围
海关与贸易: 贸易记录编号, 客户编号, 数据来源, 访问范围, 覆盖国家或地区, 覆盖期间, 观察到的企业名称, 观察到的企业地址, 主体匹配依据, 贸易方向, 货运期间, 可见交易频次, 产品描述, 海关编码, 数量, 数量单位, 重量, 重量单位, 申报价值, 申报币种, 贸易伙伴或国家, 数据局限说明, 观察记录时间, 证据编号
风险核验: 风险记录编号, 客户编号, 风险类型, 匹配到的主体, 主体匹配依据, 指控或记录内容, 证据编号, 管辖地区, 记录日期, 观察记录时间, 证据状态, 误匹配风险, 风险门状态, 审核人决定, 决定日期
触达记录: 触达记录编号, 客户编号, 联系人编号, 触达渠道, 触达阶段, 内容状态, 计划日期, 草稿内容或本地引用, 草稿生成时间, 草稿对应触达阶段, 自动化运行编号, 实际发送时间, 实发内容或本地引用, 回复状态, 回复时间, 下一步行动, 下一步行动日期, 业务员批准状态
移交记录: 移交记录编号, 客户编号, 触发渠道, 触发触达记录编号, 回复内容引用, 客户开发快照引用, 未解决问题, 风险门状态, 目标技能, 移交状态, 业务员决定, 决定日期
```

每个工作表的资产合同是：第 1 行使用一致的机器/结构表头样式，第 2 行使用明显区分的中文业务表头样式；冻结前两行（`A3`），在第 2 行启用工作表级自动筛选，使用同时容纳英文字段名和中文说明的可读列宽，必要时换行。数据从第 3 行开始，公开模板不含任何数据行，因此最大行号必须为 2。日期使用 ISO `YYYY-MM-DD`；实际发送和回复时间使用带显式 UTC 偏移的 ISO 8601 时间戳。未知值留空，不得猜测。所有受控状态的数据验证范围从第 3 行开始，不得覆盖第 2 行中文说明。

下列字段只能使用对应受控状态：

```text
screening_status: 待业务员筛选, 已确认, 已暂停, 已关闭
direction_status: 草案, 待外部核实, 待业务员确认, 已确认可扫描, 暂缓, 淘汰
external_validation_status: 支持, 存在反证, 证据有限, 尚未核实, 来源不可访问
salesperson_classification: 不继续, 普通候选, 潜力客户
information_reliability: 资料充分且一致, 整体可信但存在缺口, 存在重大冲突需要核验, 证据不足无法判断
evidence_state: 官方直接证据, 多来源相互印证, 单一来源待验证, 合理推断, 来源相互冲突, 信息已经过期, 来源不明隔离待核实
usage_permission: 正常使用, 限制使用, 隔离待核实
risk_gate: 未触发, 待核验, 暂停待业务员审核, 业务员批准继续, 已关闭
content_status: 草稿, 业务员批准, 计划触达, 实际发送, 实际回复
handoff_status: 未触发, 待客户经营与沟通, 已移交, 业务员已决定
map_route_status: 路线线索, 路线候选, 待外部核实, 暂缓, 排除
research_readiness: 可编译方向, 需补路线证据, 待外部核实, 不可进入
commercial_readiness_status: 可承接, 有条件, 未知, 已确认冲突
stale_status: 当前, 临近复核, 已过期, 无法判断
salesperson_route_decision: 选择编译, 继续核实, 暂缓, 淘汰
```

以上受控字段都必须启用停止式错误拦截并允许空白：信息未知时可以留空，空白不违反数据验证；只要填入非空值，就必须来自对应受控列表。业务员输入列表外的非空值时，工作簿显示错误提示并拒绝写入。不得仅提供下拉候选但继续接受无效值，也不得用自造状态代替未知值。

`客户总览.risk_gate`、`风险核验.gate_status` 和 `移交记录.risk_gate_status` 必须使用同一组 `risk_gate` 受控值。风险硬门命中时，在同一待写入包或获授权的写入中，将 `客户总览.risk_gate` 与对应 `风险核验.gate_status` 都设为 `暂停待业务员审核`；在业务员明确审核并将风险门批准为 `业务员批准继续` 前，不得恢复推荐、准备触达材料或继续触达。

只有在实际创建移交快照时，才写入该条 `移交记录.risk_gate_status`，并保存快照创建时的同一受控风险状态。不得只为同步风险门而新建或改写移交记录；尚未发生移交时，风险状态只传播到客户总览和对应风险记录。

## 稳定编号

使用 route_review_id、direction_id、customer_id、research_id、opportunity_id、contact_id、evidence_id、trade_record_id、risk_id、touch_id 和 handoff_id。公司名称不是唯一键。

更新前先用稳定编号定位记录，再核对 `customer_id` 的引用关系。不得仅凭公司名、品牌名或联系人名称合并记录。

## 路线评审、方向推导与结果反馈如何落表

`路线评审` 是路线包、商业承接只读视图与业务员选择之间的唯一落表层。路线包引用、哈希、生产者登记、地图状态、承接快照、知识快照、事实编号、时效和未知必须分列保存；不得把 `development_readiness_view` 复制成第二事实库。`salesperson_route_decision`、`decision_basis` 和 `decision_date` 是业务员自有字段，AI 不得自动填写或覆盖。

`direction_compilation` 只读取 `salesperson_route_decision = 选择编译` 的记录。新方向的 `source_route_review_id` 与 `source_route_candidate_id` 必须同时写入。`direction_derivation_chain` 按字段拆分保存：产品事实引用写入 `approved_product_reference`；效果、功能、适用和禁止边界写入 `product_boundary`；应用节点、产出产品、行业活动、可观察产品信号与目标企业规则写入 `observable_enterprise_rule`；候选准入证据门写入 `candidate_direct_evidence_rule`；排除条件写入 `exclusion_boundary`；承接条件、反证和未知写入 `unresolved_conditions`。不得丢失两级来源编号，也不得把整条链压缩成无法追溯的一段结论。

如果指定工作簿仍是旧的 11 表结构，或缺少 `路线评审`、`source_route_review_id` 与当前验证规则，返回 `workbook_schema_migration_required`，先制作备份并获得迁移授权；不得静默移动旧列、覆盖业务员字段或把旧结构误报为已写入。

每次候选扫描的声明范围、查询语言、覆盖来源、访问限制和观察日期必须保留在交付的结构化候选表及对应 `证据来源` 记录中；合格候选逐行进入 `客户总览` 并保留同一 `source_direction_id`。未合格或待核实公司不伪装成客户记录，保留在本次结构化候选表和证据记录中，供业务员审阅。若业务员尚未授权写入，则只输出 `workbook_update_packet`。

三段式候选采集还必须保留 `candidate_collection_task.task_id`、`raw_candidate_batch.batch_id`、执行器与运行编号、方向包哈希、追加关系和本次 `candidate_review` 结果。`candidate_batch_intake` 只登记原始批次，不将观察项写成合格客户；只有独立 `candidate_review = PASS` 的企业才可形成待业务员筛选的候选投影。`FAIL` 和 `UNVERIFIED` 留在批次/复核记录及证据引用中，不伪装为客户总览中的合格客户。

`direction_feedback_packet` 的支持结果、反证结果和未覆盖范围分别追加为 `方向证据` 行，使用 `validation_effect` 和 `limitation_note` 区分；只有业务员对 `direction_status`、`salesperson_decision` 或 `decision_date` 给出字段级新值授权后，才可更新 `开发方向`。扫描结果本身不得自动改写方向状态。

## 状态分离

内部候选、最终推荐、业务员批准、计划触达、实际发送和实际回复必须分开。AI草稿不得标为实发。证据记录追加，不覆盖旧来源。

- `项目机会.recommendation_state` 明示区分内部候选、最终推荐和证据不足结论；只允许保存候选摘要，不保存三个完整内部推演。
- `项目机会.salesperson_decision` 和 `decision_date` 单独记录业务员决定，不得因存在最终推荐而自动填写。
- `触达记录.content_status` 只使用受控状态。进入“业务员批准”需真实批准；进入“实际发送”需实际发送证据、`actual_sent_at` 和实发内容或本地引用；进入“实际回复”需实际回复、`response_at` 和回复引用。
- 计划触达不得倒填为实际发送，实际回复不得由打开、阅读或点击信号推定。实发与实际回复使用独立记录和稳定编号，保留对应时间戳与内容引用。

## 回复硬停

任一渠道收到回复或看似回复的入站内容即暂停原触达计划。已核验时保存实际回复；尚未核验时保存当前文本或本地引用并标明身份、邮件头和来源缺口。输出客户编号、已确认资料、实发记录、当前入站内容、未解决问题、风险和证据引用。

收到任何看似回复的入站内容时，立即暂停原触达计划，取消未发送的后续计划，不再生成新开发触达内容，并立即准备有边界的 `customer_operations_handoff`。若发件人身份、邮件头、原始消息或对应实发历史未核验，交接包使用当前已保存文本或本地引用和现有上下文，逐项标明身份与历史缺口；不得把它记成已核验的“实际回复”或“官方直接证据”，也不得因等待核验或补齐记录而延迟移交。未获得工作簿写入授权时，只输出待写入包和交接包，不得声称已写入、已创建移交记录或已更新状态。

开始准备上述受控交接后，输出与待写入包中的移交状态只使用 `handoff_status = 待客户经营与沟通`。原触达计划“已暂停”是独立流程状态，不得与 `handoff_status` 用斜杠、并列值或自造值合并。未核验入站内容仍不得记为已核验的实际回复、官方直接证据、实际回复状态或触达成功。

## 客户经营与沟通移交

target_skill 固定为 foreign-trade-customer-operations。客户经营与沟通技能处理首封、未回复跟进和收到回复后的沟通；业务员决定项目状态、长期经营或关闭。

`customer_operations_handoff` 在实际写入时使用新 `handoff_id`；仅准备未写入的交接包时，将缺失编号标为待创建，不得伪造。发送给接收技能的字段名必须与下列合同一致，不得只给一段综合叙述：

```text
customer_operations_handoff:
  customer_id: <稳定编号或待创建>
  trigger_channel: <触发渠道>
  trigger_touch_id: <对应实发触达编号或缺口>
  response_reference: <当前保存的入站原文或本地引用>
  sender_identity_status: <发件人、邮件头、主体关系的核验状态与缺口>
  confirmed_context: <已确认客户、产品和项目事实及证据引用>
  actual_send_history: <可追溯实发记录；没有则明示缺口>
  open_questions: <未解决问题>
  risk_gate_status: <当前风险状态与依据>
  target_skill: foreign-trade-customer-operations
  salesperson_request: <本次明确要求或待确认>
```

交接是对当前入站内容的回复处理入口，不授权客户经营与沟通技能决定客户价值、优先级、发送、受限联系方式或最终状态。

## 现有接口兼容

交接包至少包含 company_identity、website_and_region、business_type、main_products、fit_hypotheses、contact_identity_and_possible_role、development_angles、source_url_or_local_reference、observed_at 和 evidence_state。额外字段不得改变邮件助手的职责。

上述字段必须基于已保存证据；多来源时保留各自的 `source_url_or_local_reference`、`observed_at` 和 `evidence_state`。`development_angles` 只包含最终推荐或明确的证据不足结论，不包含三个完整内部推演。
