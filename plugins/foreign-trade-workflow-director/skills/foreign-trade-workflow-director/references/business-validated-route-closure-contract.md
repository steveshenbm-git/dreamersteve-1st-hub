# 业务确认路线跨技能闭合合同

## 路由语义

`business_route_closure_review` 只处理一条命名 `route_instance`。它验收三个独立层：

1. 行业地图的业务范围 + 应用证据闭合；
2. 客户开发的种子/保留样本独立方向验证；
3. 本技能生成的哈希绑定闭合回执。

业务登记只证明该公司把该行业列为开发范围。它不是应用证据，不是产品适配、监管合规、客户需求或扫描授权。

## 回执合同

```text
business_route_closure_receipt_v1:
  contract_version
  closure_receipt_id
  company_id
  route_id
  business_industry_id
  route_packet_reference
  route_packet_sha256
  direction_validation_reference
  direction_validation_sha256
  route_scoped_application_closure_state
  global_semantic_stage_effect
  customer_discovery_readiness
  salesperson_scan_authorization
  allowed_next_actions
  prohibited_next_actions
  validated_at
```

回执只在下列条件同时满足时PASS：

- 路线包与方向验证包都使用回执同目录内的标准相对路径，当前字节SHA-256一致；
- 公司、路线、业务行业、路线闭合和客户发现就绪状态一致；
- 方向验证PASS，且 `application_seed` 与 `direction_holdout` 的依赖组独立；
- `route_scoped_application_closure_state = PASS`、`global_semantic_stage_effect = none`、`salesperson_scan_authorization = blocked`；
- `allowed_next_actions` 精确为 `present_direction_for_salesperson_scan_decision`；
- `prohibited_next_actions` 至少包含 `scan_candidates`、`claim_product_fit` 和 `claim_regulatory_compliance`。

使用 `scripts/validate_business_route_closure.py /absolute/path/to/business-route-closure-receipt.json` 验收。PASS 只关闭这条路线的“方向可呈现”缺口，不改写公司基础阶段，不解除全局 `RESEARCH_ONLY_BLOCKED`，不扫描客户。
