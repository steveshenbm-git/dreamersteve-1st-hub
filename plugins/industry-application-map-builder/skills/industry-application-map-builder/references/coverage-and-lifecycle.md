# 覆盖与路线生命周期

## 覆盖对象

覆盖检查同时面向：产品事实包中的能力、效果、应用和冻结项；本次声明的行业分支、产出产品、应用节点和来源范围。每个对象必须记录稳定编号、声明范围、覆盖状态、处置、关联路线、缺口和复核日期。

受控覆盖状态：`mapped`、`deferred`、`excluded`、`unknown`、`out_of_scope`、`not_expanded`。

- `out_of_scope`：本轮明确未纳入，不表示不相关。
- `not_expanded`：保留了分类骨架，但尚未研究产品或应用层。
- `excluded`：只针对明确的产品范围和应用节点，不得直接排除整个行业分支。

路线数量不是覆盖标准。即使有大量路线，只要一个已确认能力没有路线、暂缓、排除或未知处置，覆盖仍不通过。

最小机器校验要求每个 `capability_id` 都有一条 `coverage_object_type = capability` 的覆盖记录，并明确 `mapped / deferred / excluded / unknown` 之一。声明范围内的行业分支、产出产品和应用节点还需在人工复核中逐项确认；静态校验不能代替完整范围审计。

## 状态轴

- `evidence_state`: `supported / hypothesis / unknown / conflicted`
- `technical_match_state`: `satisfied / violated / unknown / conflicted`
- `research_disposition`: `active / deferred / closed`
- `map_route_status`: `路线线索 / 路线候选 / 待外部核实 / 暂缓 / 排除`

这些字段不能互相代替。`supported` 不表示技术满足，技术满足不表示市场存在，路线候选不表示业务员确认可扫描。

## 变更影响

产品事实包、事实库、行业骨架或应用底座哈希变化时，标记所有依赖路线待复核。分类版本变化时保留旧节点、添加新节点和对应关系；未能确定对应关系时记录迁移未知。不得静默改写路线ID、业务员决定或下游扫描历史。

候选扫描结果可以通过 `direction_feedback_packet` 反向形成应用知识修订候选，但不能自动改变共享事实、公司路线状态或覆盖处置。
