# 证据与推导合同

## 三层事实

1. 分类事实：官方来源证明行业代码、名称、层级、版本和说明。
2. 应用事实：产品中性公开来源证明产出产品、作用点、工艺、应用节点或需求。
3. 公司产品事实：公司产品资料库中获准使用的E3自有公司事实。

三层事实独立保存。匹配结论是可追溯推断，不得写回任一事实层。

## 证据状态

- `supported`：来源直接支持该产品中性应用关系，并保留适用条件和限制。
- `hypothesis`：AI常识、机理、语义相似、行业惯例或待搜索线索。
- `unknown`：当前资料不能判断。
- `conflicted`：可追溯来源互相冲突。

AI常识和理论推导只能形成 `hypothesis`，不能因表述顺畅、来源数量多或模型置信度高而升级。

行业语义初筛状态不是证据状态。`hypothesis_formed` 只触发证据展开；`ambiguous` 保留未知并强制处置；`no_hypothesis_formed` 只进入反向审计总体。三者都不能单独产生 `supported`。

## 正式支持门

```text
direct_source_support == true
AND source_location_present == true
AND snapshot_or_live_source_verified == true
AND model_b_review == PASS
AND claim_scope_within_source == true
AND circular_source == false
AND unresolved_counterevidence == false
AND automated_contract_validation == PASS
```

模型A不得审查自己的证据。模型B必须重新读取原始来源或校验后的快照；不可访问且重试失败时返回 `UNVERIFIED`，不能用自身知识补齐。模型C只处理争议、反证和反向审计；多数模型同意不构成证据。

命题必须先于搜索并保持最小范围。来源只支持某个材料、过程、作用点、条件或应用时，不得扩大到整个行业或相邻技术。`conditions` 和 `limitations` 必须包含可观察边界；空洞套话不算完成。

## 四值技术匹配

每个硬性 `requirement_atom` 分别匹配：

- `satisfied`：同一产品范围下的E3事实在可比单位、条件和接口内满足要求。
- `violated`：E3事实或已知限制明确不满足要求。
- `unknown`：缺少单位、方法、条件、接口、产品范围或相容性证据。
- `conflicted`：相关事实或适用条件互相冲突。

路线聚合顺序固定为：任一硬要求违反则 `violated`；否则任一关键项冲突则 `conflicted`；否则任一硬要求未知则 `unknown`；其余才是 `satisfied`。

禁止综合评分、加权平均、用多数满足掩盖一个硬性未知或冲突。不得用路线数量、来源数量或行业规模替代技术匹配。

## 路线升级

```text
route_candidate
= application_link_evidence == supported
AND technical_match_state == satisfied
AND required_conditions_compatible == true
AND process_interface_compatible == true
AND known_limit_conflict == false
```

应用关系只有假设、任一硬要求未知或来源无法独立时，保留为 `路线线索`。明确违反时进入路线级排除。存在冲突时暂缓并提出复核任务。

## 来源独立性

公司产品来源与产品中性应用来源分别记录。一个混合公司宣传资料不能同时作为公司能力事实和独立应用需求证据。共享来源使用 `source_dependency_group` 标识同源转载、同一底层研究或同一商业主体；同一依赖组的多页面不能算独立相互印证。若共享应用材料直接来自或依赖某条公司产品来源，`source_dependency_group` 必须使用该产品 `source_id`，以便循环来源检查能够阻断自证。

路线候选引用的应用证据必须属于该 `application_node`；该应用节点必须引用路线中的产出产品，而产出产品必须引用路线中的行业节点。每个硬性需求原子都必须有同路线的逐项匹配记录，不能只匹配一部分硬要求后把聚合状态写成 `satisfied`。
