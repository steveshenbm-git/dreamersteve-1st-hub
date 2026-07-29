# 行业应用地图构建设计

## 目标

在 `company-product-knowledge-builder` 与 `foreign-trade-customer-development` 之间增加独立的 `industry-application-map-builder`。它读取一个公司的受控产品事实包，连接共享的行业骨架和产品中性应用事实，生成公司专属的行业应用地图与路线候选池；不搜索具体客户，不给国家、行业或客户做综合评分，也不替业务员确认可扫描方向。

## 职责边界

完整链路固定为：

```text
company-product-knowledge-builder
  -> product_development_fact_packet
industry-application-map-builder
  -> company_route_pool_packet
foreign-trade-customer-development
  -> development_direction_packet / direction_validation_packet
salesperson
  -> direction_status = 已确认可扫描
foreign-trade-customer-development
  -> candidate_scan
```

产品知识技能只维护公司产品事实。行业应用地图技能只维护共享行业应用知识、公司匹配关系、覆盖台账和路线候选。客户开发技能把被选中的路线候选编译为开发方向并执行外部核实、候选扫描和背调。命名公司初查仍可直接进入客户开发，但不能据此补写行业路线或产品适配事实。

## 数据架构

行业地图资料库与公司产品资料库分离。产品资料库是只读输入；行业地图资料库包含一个共享底座和按 `company_id` 分开的公司目录：

```text
industry-application-map-root/
├── AGENTS.md
├── 00-管理/
│   ├── map-registry.json
│   └── change-log.json
├── 01-共享行业骨架/
│   └── industry-taxonomy.xlsx
├── 02-共享应用知识/
│   └── industry-application-base.xlsx
├── 03-共享来源封存/
├── 04-公司地图/
│   └── <company_id>/
│       ├── company-industry-application-map.xlsx
│       ├── company-route-pool-packet.json
│       └── review-log.json
├── 05-工作区/
└── 06-风险隔离/
```

共享底座不得包含公司产品事实。公司地图不得包含另一家公司的事实、路线、状态或示例。根索引只保存标识、路径和版本。

## 工作簿合同

`industry-taxonomy.xlsx` 保存官方分类骨架、版本、代码、名称、层级、父节点、有效状态和来源，不声称行业分类本身等于终端应用分类。

`industry-application-base.xlsx` 的可见工作表顺序为：

1. 版本与范围
2. 产出产品
3. 应用节点
4. 需求原子
5. 关系边
6. 证据来源
7. 覆盖台账
8. 变更记录

`company-industry-application-map.xlsx` 的可见工作表顺序为：

1. 公司与输入
2. 产品能力
3. 路线候选
4. 匹配明细
5. 排除暂缓
6. 覆盖台账
7. 路线交接
8. 变更记录

第1行使用机器字段名，第2行使用中文业务说明，数据从第3行开始。冻结前两行，在第2行启用筛选；分类状态使用停止式数据验证并允许空白。工作簿是业务员可读的主工作面，JSON只用于稳定的机器交接。

## 推导模型

行业到公司产品之间不允许直接连边。共享知识链为：

```text
industry_node
-> output_product
-> use_point_or_process
-> application_node
-> requirement_atom
```

公司匹配链为：

```text
approved_product_fact
-> capability_atom
-> requirement_atom_match
-> application_node
-> output_product
-> industry_node
-> target_enterprise_activity
```

最小路线主键为 `company_id + product_scope + application_node_id`。同一行业可以对产品A形成路线、对产品B不成立；排除结论只作用于路线边，不能自动排除整个行业。

每个需求原子统一使用：`dimension, value, operator, unit, conditions, hardness, evidence_ids`。材料、驱动器等领域可以有不同词表和视图，但不得创建互不兼容的核心结构。

## 四值匹配公式

每个需求原子的匹配状态只允许：`satisfied`、`violated`、`unknown`、`conflicted`。

路线技术状态按下列顺序确定：

1. 任一硬要求或已知限制明确冲突，状态为 `violated`。
2. 没有违反，但任一关键证据互相冲突，状态为 `conflicted`。
3. 没有违反或冲突，但存在未解决的硬要求、条件或接口，状态为 `unknown`。
4. 所有硬要求、必要条件和工艺接口都有相容的受控产品事实，状态为 `satisfied`。

禁止把多个未知或冲突压缩为综合分数。`route_candidate` 仅在应用关系证据为 `supported`、技术状态为 `satisfied` 且没有已知限制冲突时成立。AI常识、机理或语义相似只能生成 `route_lead` 和搜索词。

## 状态分离

- `evidence_state`: `supported`, `hypothesis`, `unknown`, `conflicted`
- `technical_match_state`: `satisfied`, `violated`, `unknown`, `conflicted`
- `research_disposition`: `active`, `deferred`, `closed`
- `map_route_status`: `路线线索`, `路线候选`, `待外部核实`, `暂缓`, `排除`

行业地图技能不得写入 `direction_status = 已确认可扫描`。该状态只属于业务员控制的客户开发工作流。

## 输入与交接

公司地图输入必须包含 `company_id`、`company_library_root`、产品事实包路径、`product_scope`、共享底座路径、声明行业范围、声明应用范围和授权来源范围。开始推导前必须运行产品资料库校验，解析事实包ID到 `facts.json`，确认其属于同一公司且是获准使用的E3事实，并记录事实包、事实库和共享底座的SHA-256。

输出 `company_route_pool_packet`，至少包含输入快照、声明范围、路线候选、排除与暂缓、覆盖摘要、事实与应用证据引用、推导链、反证、未知、待验证国家或地区假设及 `target_skill = foreign-trade-customer-development`。国家或地区可以是有来源的待验证假设，不得在本技能内变成最终优先级。

## 覆盖标准

共享行业骨架可以完整保存一个明确版本的官方分类，但应用知识按实际研究逐步扩展。公司地图只对声明范围负责：每条已确认能力、效果、应用和明确冻结项都必须对应路线、暂缓、排除或未解决处置；未进入声明范围的分类分支是 `out_of_scope`，不是“不相关”。路线数量不能证明覆盖完成。

## 证据标准

官方分类只证明行业活动分类。产品中性应用事实需要独立的公开来源。公司产品事实来自产品知识库。应用来源与产品来源不得通过同一个未经拆分的来源循环证明匹配结论。公开来源记录标题、发布者、URL或本地引用、发布日期或未知、观察日期、原文位置、中文摘要、适用范围、冲突和访问限制。

## 失败处理

产品事实包缺失、ID无法解析、公司不一致、哈希变化、共享底座版本不明或关键硬要求冲突时停止路线升级并输出缺口。分类版本变化必须新增版本和迁移记录，不得静默覆盖旧代码。应用知识更新影响现有路线时，将依赖路线标记为待复核，不自动改写业务员状态。

## 验收

验收包括技能和插件验证、脚本单元测试、两个领域的合成公司隔离测试、Excel结构与视觉检查、上下游静态合同测试、压力场景静态复核和差异检查。未授权子代理时，真实新上下文前测标记为 `UNVERIFIED`。
