# 路线池交接合同

## 输出结构

```text
company_route_pool_packet:
  export_id
  company_id
  product_scope
  input_snapshot
  producer_snapshot
  declared_scope
  route_candidates
  route_leads
  deferred_routes
  excluded_routes
  coverage_summary
  prohibited_inference
  target_skill: foreign-trade-customer-development
  producer_registry_reference
  exported_at
```

每条路线候选保留 `route_candidate_id`、产品事实ID、产品来源ID、应用节点、需求与应用证据、行业节点、产出产品、作用点或工艺、目标企业活动、四类状态、限制冲突、反证、未知、推导链、待验证国家地区假设及其证据ID。

## 生产者登记

每个公司地图目录必须含 `route-pool-export-registry.json`。每次成功导出新增一条不可复用的 `export_id`，并记录 `company_id`、公司目录内的包路径、包文件 SHA-256、输入快照、`producer_snapshot.company_map_path`、`producer_snapshot.company_map_sha256`、路线 ID 集合、验证器版本、验证日期、状态与失效原因。

`producer_registry_reference` 必须反向指向同一地图根、同一公司登记文件和同一 `export_id`。登记状态只有 `current`、`stale`、`superseded`；只有 `current` 可作为当前下游输入。复制、改名或编辑 JSON 不产生新的有效交接；公司地图工作簿哈希发生变化时，旧包即使未被编辑也不得继续使用，必须由本技能复核并重新导出。

## 导出门

导出前必须验证：公司一致、输入哈希当前、事实ID属于事实包并解析为获准使用的E3自有事实、共享ID存在、来源不循环、技术匹配满足、应用证据支持、没有已知限制冲突。

导出目标必须位于 `04-公司地图/<company_id>/`，且不得覆盖已有文件。导出后必须校验登记中的包哈希、公司、`export_id`、生产者引用和输入快照；任一不一致都使交接失败。

交接包不得包含客户名称、客户名单、综合评分、最终国家优先级、采购角色结论、已使用公司产品的结论或 `direction_status = 已确认可扫描`。

## 下游使用

`foreign-trade-customer-development` 先校验路线包及其生产者登记，再向业务员呈现路线组合评审。业务员选定路线后，下游才能将其编译为 `development_direction_packet` 并执行 `direction_validation`。只有业务员记录 `direction_status = 已确认可扫描` 并声明国家、语言、应用细分、产品范围和来源范围后，才可启动按方向的 `candidate_scan`。

命名公司初查仍是独立入口；它不需要预建完整路线池，但不能据此把产品适配、行业路线或采购角色升级为事实。
