# 行业应用数据结构

## 真实关系链

```text
industry_node
-> output_product
-> use_point_or_process
-> application_node
-> requirement_atom
```

公司侧关系链为：

```text
approved_product_fact
-> capability_atom
-> requirement_atom_match
-> application_node
-> output_product
-> industry_node
-> target_enterprise_activity
```

不得建立 `industry_node -> company_product` 的直接结论边。行业分类描述生产活动，不等于终端产品、应用需求或采购角色。

## 稳定编号

- 行业节点：`<taxonomy-system>-<version>-<code>`
- 产出产品：`OUT-<stable-id>`
- 应用节点：`APP-<stable-id>`
- 需求原子：`REQ-<stable-id>`
- 能力原子：`<company_id>-CAP-<stable-id>`
- 路线候选：`<company_id>-R-<stable-id>`

最小路线键是 `company_id + product_scope + application_node_id`。行业代码、产品名或公司名都不能单独充当路线唯一键。

## 需求原子

所有领域共用：

```text
requirement_atom_id
application_node_id
dimension
operator
value
unit
conditions
hardness
evidence_state
evidence_ids
limitations
```

领域词表可以不同，但核心字段不能因材料、驱动器或其他产品而分裂为互不兼容的结构。

## 作用点类型

受控首批类型包括：`formulation_or_composition`、`surface_or_layer`、`manufacturing_input`、`equipment_control_or_detection`、`packaging_or_marking`、`operation_or_maintenance`。新类型必须有应用证据和定义，不能从公司产品名称直接产生。

## 工作簿字段

共享应用底座保存产出产品、应用节点、需求原子、关系边、证据来源和覆盖台账。公司地图保存输入快照、产品能力、路线候选、逐项匹配、排除暂缓、公司覆盖、路线交接和变更记录。列表字段使用JSON字符串数组，未知值留空或使用明确的状态字段，不写“可能没问题”等模糊文本。

路线中的 `geography_hypotheses` 只保存待验证的国家或地区假设，`geography_evidence_ids` 保存支撑这些假设的公开证据编号。前者非空而后者为空、证据不可解析或证据状态不是 `supported` 时，路线不得导出为路线候选；这两个字段都不构成国家优先级。

## 行业语义研究记录与正式底座边界

行业语义研究工作区保存 `semantic_screening_record`、`semantic_evidence_packet` 和 `semantic_reverse_audit_record`。筛查记录至少包含合同、Git提交、提示词、分类快照、模型运行、节点、两组查询、检查结果、筛查/进度/证据三条状态轴、风险层输入、最小命题、未知和停止原因。

研究记录不能直接成为共享底座中的产出产品、应用节点、需求原子或关系边。只有通过直接来源、原始位置、可验证现场或快照、模型B复核、命题范围、循环来源、反证和自动合同校验的关系，才能由另行授权的 `application_knowledge_update` 转入正式链。
