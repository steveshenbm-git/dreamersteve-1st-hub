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

## 业务前台投影

当任务由 `foreign-trade-workflow-director` 发起时，机器交接包仍直接交给 `foreign-trade-customer-development` 校验；另向协调器返回只读 `route_workbench_projection`：

```text
route_workbench_projection:
  handoff_id
  company_id
  source_record_id: <route_candidate_id>
  source_packet_reference
  evidence_reference
  result_state: PASS | FAIL | UNVERIFIED
  product_scope
  application_industry_route_summary
  why_review_now
  material_evidence_summary
  unknowns_and_limits
  geography_hypothesis
  current_status
  salesperson_decision_required
```

该投影只供 `salesperson_workbench` 的 `01-路线选择` 和 `05-异常与风险` 使用。它不得复制共享行业骨架、产出产品、应用节点、需求原子、关系边、完整证据来源、覆盖台账或变更记录，也不得成为新的事实来源。

若出现 `COMPANY_TAXONOMY_SNAPSHOT_STALE`、`COMPANY_APPLICATION_SNAPSHOT_STALE`、`ROUTE_EXPORT_NOT_CURRENT`、`INPUT_SNAPSHOT_HASH_MISMATCH` 或 `ROUTE_EXPORT_SOURCE_MAP_STALE`，返回 `shared_input_stale_event`，明确受影响路线、当前哈希/登记状态和所需复核动作。协调器必须把它投影到异常页并阻断受影响的方向编译与候选采集；业务员手工改状态不能解除该阻断。
