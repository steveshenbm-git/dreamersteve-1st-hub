# 路线池交接合同

## 输出结构

```text
company_route_pool_packet:
  export_id
  company_id
  product_scope
  product_scopes
  input_snapshot
  producer_snapshot
  declared_scope
  route_candidates
  route_leads
  route_closures
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

导出前必须验证：公司一致、输入哈希当前、事实ID属于该路线 `product_scope` 的事实包并解析为获准使用的E3自有事实、共享ID存在、来源不循环、应用证据支持且没有已知限制冲突。严格 `路线候选` 仍要求技术匹配满足；`business_validated_route_closure` 只能作为 `route_leads` 导出，并必须携带唯一PASS闭合、有限方向动作与完整禁止声明。

导出目标必须位于 `04-公司地图/<company_id>/`，且不得覆盖已有文件。导出后必须校验登记中的包哈希、公司、`export_id`、生产者引用和输入快照；任一不一致都使交接失败。

交接包不得包含客户名称、客户名单、综合评分、最终国家优先级、采购角色结论、已使用公司产品的结论或 `direction_status = 已确认可扫描`。

## 下游使用

`foreign-trade-customer-development` 先校验路线包及其生产者登记，再向业务员呈现路线组合评审。严格路线候选在业务员选定后进入完整方向编译。`ready_for_limited_direction_validation` 的路线线索只可编译并验证企业识别规则，不得推荐产品、声称适配/合规或采集客户。两条路都只有在业务员另行记录 `direction_status = 已确认可扫描` 并声明国家、语言、应用细分、产品范围和来源范围后，才可启动按方向的 `candidate_scan`。

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

## 行业语义专业返回

阶段5每个路由返回同一合同版本的 `semantic_specialist_return_packet`：

```text
semantic_specialist_return_packet:
  handoff_id
  research_contract_id
  contract_version
  source_route
  result_state: PASS | FAIL | UNVERIFIED
  semantic_method_validation_state: null | INCONCLUSIVE | EFFECTIVE | NOT_EFFECTIVE (strict_audit only; content_first = null)
  terminology_bridge_reference
  terminology_bridge_sha256
  terminology_bridge_state
  development_regression_state
  formal_holdout_case_set_sha256
  formal_holdout_provenance_state
  paired_task_manifest_reference
  paired_task_manifest_sha256
  formal_paired_task_chain_state
  source_truth_package_sha256
  scorecard_package_sha256
  receiver_evidence_manifest_sha256
  stability_task_manifest_reference
  stability_task_manifest_sha256
  stability_repeat_state
  content_method_state: CONTENT_CALIBRATION_INCOMPLETE | CONTENT_CALIBRATION_PASS | CONTENT_CALIBRATION_FAIL
  content_full_screening_state: NOT_AUTHORIZED | AUTHORIZED_NOT_STARTED | IN_PROGRESS | COVERAGE_INCOMPLETE | READY_FOR_REVERSE_AUDIT | BLOCKED
  content_full_screening_authorization_reference
  content_full_screening_authorization_receipt_reference
  content_full_screening_authorization_receipt_sha256
  content_terminal_scope_sha256
  active_semantic_work_unit
  artifact_references_and_hashes
  coverage_summary
  evidence_gate_summary
  reverse_audit_summary
  blockers
  one_next_action
  next_authorization_required
  prohibited_downstream_actions
```

`content_first` 必须令 `semantic_method_validation_state = null`，使用 `CONTENT_CALIBRATION_*` 和完整R4哈希/授权绑定，并保持 `prohibited_downstream_actions` 中的 `RESEARCH_ONLY_BLOCKED`。只有明确的历史 `strict_audit` 合同可以填写 `INCONCLUSIVE / EFFECTIVE / NOT_EFFECTIVE`。40例返回只更新对应模式的方法状态，不把阶段5记为PASS。全量筛查、正式底座写入、公司匹配和客户搜索分别需要自己的门。协调器只投影当前为什么停、唯一下一动作和需要用户批准什么，不把模型包、查询记录或机器证据附页交给业务员维护。
