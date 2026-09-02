# 业务确认路线闭合合同

## 目的

`business_validated_route_closure` 用于一个公司已明确确认的行业范围。它从“业务范围”与“产品中性应用证据”两端同时收敛，只补齐服务开发所需的中间链。业务登记决定范围和优先级，不代替应用证据、技术适配或监管资格。

## 入口条件

- 当前 `business_validated_industry_register` 中存在同一 `company_id` 和 `business_industry_id`，文件哈希已冻结。
- 当前产品输入为单一事实包，或由 `freeze_company_product_packet_manifest.py` 生成的多产品清单。
- 路线中的公司事实只来自同一 `product_scope`。
- 共享应用节点、产出产品、行业节点和应用证据链均可解析，应用证据为 `supported` 且不以本公司产品来源循环自证。
- `technical_match_state` 和 `regulatory_qualification_state` 可以是 `unknown`，但不能是 `violated` 或 `conflicted`；`known_limit_conflict = false`。

## 路线结果

```text
map_route_status: 路线线索
research_disposition: business_validated_route_closure
customer_discovery_readiness: ready_for_limited_direction_validation
allowed_downstream_actions:
  - compile_and_validate_direction
prohibited_downstream_actions:
  - recommend_product
  - claim_product_fit
  - claim_regulatory_compliance
  - scan_candidates
```

`路线闭合` 必须与路线的公司、业务行业、应用证据、来源依赖组、发现就绪状态和监管状态一致。`review_result = PASS` 还需复核日期与授权引用。任一引用或哈希变化都使闭合失效。

## 状态隔离

路线闭合是 `route_instance` 级的独立桥。它的 `global_semantic_stage_effect` 固定为 `none`：不修改全局 `industry_semantic_expansion`，不取消 `RESEARCH_ONLY_BLOCKED`，不释放未命名的行业或其他产品轨。它只允许客户开发把该路线编译成可观察企业规则，并用独立保留样本验证方向。扫描仍需业务员另行确认。
