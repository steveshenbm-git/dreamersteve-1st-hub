# 全流程状态、业务前台与交接合同

## 框架审计包

```text
framework_audit_packet:
  audit_id
  blueprint_id
  blueprint_version
  company_id_or_missing
  inspected_environment
  dependency_results:
    - plugin_name
      observed_version
      required_capabilities
      result: PASS | FAIL | UNVERIFIED
      evidence_reference
  stage_results:
    - stage_id
      gate_result: PASS | FAIL | UNVERIFIED
      freshness: current | stale | unknown
      artifact_reference
      artifact_version_or_hash
      reason
  first_incomplete_stage
  active_work_unit
  one_next_action
  next_action_owner
  allowed_writes
  prohibited_actions
  audited_at
```

`first_incomplete_stage` 必须按蓝图固定顺序计算，不能按聊天中最后提到的文件、工作簿当前页或用户想直接开始的后期动作决定。

## 公司框架初始化包

```text
company_framework_bootstrap_packet:
  bootstrap_id
  blueprint_id
  blueprint_version
  new_company_id
  isolated_company_root
  approved_source_scope
  empty_template_references_and_hashes
  state_registry_path
  system_exchange_paths
  current_single_editor
  copied_company_data: none
  user_authorization
  reopen_validation
  created_at
```

初始化只创建空结构和登记。若 `new_company_id`、根目录、模板来源或用户授权任一项不明确，返回 `UNVERIFIED` 并停止。

## 框架续作包

```text
framework_resume_packet:
  resume_id
  company_id
  blueprint_version
  state_registry_reference
  directly_inspected_artifacts
  stale_or_conflicting_artifacts
  first_incomplete_stage
  active_work_unit
  one_next_action
  next_action_owner
  resume_result: PASS | FAIL | UNVERIFIED
  resumed_at
```

## 复刻清单

```text
workflow_replication_manifest:
  manifest_id
  blueprint_id
  blueprint_version
  required_plugins_and_compatible_versions
  empty_template_references_and_hashes
  contract_and_schema_versions
  r4_semantic_contract_dependencies:
    terminology_bridge_reference
    terminology_bridge_sha256
    terminology_bridge_state
    development_regression_state
    formal_holdout_case_set_sha256
    formal_holdout_provenance_state
    paired_task_manifest_sha256
    formal_paired_task_chain_state
    source_truth_package_sha256
    scorecard_package_sha256
    receiver_evidence_manifest_sha256
    stability_task_manifest_sha256
    stability_repeat_state
    content_method_state
    content_full_screening_state
    content_full_screening_authorization_reference
    content_full_screening_authorization_receipt_reference
    content_full_screening_authorization_receipt_sha256
    content_terminal_scope_sha256
    downstream_release_state: RESEARCH_ONLY_BLOCKED
  authorized_shared_product_neutral_references
  required_permissions
  installation_or_copy_steps
  validation_steps
  recovery_checkpoints
  missing_dependencies
  unverified_items
  excluded_company_data_classes
  target_environment_write_authorization
  created_at
```

清单默认不执行安装、复制或目标环境写入。公司产品事实、公司地图、路线决定、客户、联系人、草稿、实发、回复和凭证必须列入排除类别。

## 目录与文件

每个公司只使用一个业务工作簿：

```text
<company-root>/
├── 06-工作区/
│   └── salesperson-foreign-trade-workbench.xlsx
└── 07-系统交换/
    ├── specialist-handoffs/
    ├── candidate-collection-tasks/
    └── raw-candidate-batches/
```

`salesperson_workbench` 是业务员前台。专业工作簿、机器交接包和采集文件不得伪装成附页塞入该工作簿。系统交换目录对业务前台只提供稳定引用。

框架蓝图、合同与空模板属于便携框架资产；`company_workflow_state` 和全部业务产物属于单一 `company_id`。插件源目录不得保存公司私有事实或客户数据。

## 协调器交接

给同事或专业技能的每项任务先输出一张人能直接执行的任务卡：

```text
operator_task_card:
  stage_id
  why_this_stage_is_now
  owner_role
  one_task
  approved_input_references
  expected_output
  acceptance_check
  stop_condition
  prohibited_actions
  decision_required_after_return
```

任务卡不能只写“继续完善”“同步数据”等抽象动作，也不能要求执行人自己推断前置条件。机器交接包与任务卡必须指向同一 `stage_id` 和同一停止点。

```text
specialist_handoff_packet:
  handoff_id
  company_id
  stage_id
  target_skill
  target_route
  business_question
  source_record_id
  source_packet_reference
  evidence_reference
  declared_scope
  allowed_writes
  prohibited_actions
  expected_return_packet
  operator_task_card_reference
  requested_at
```

`target_skill` 只允许 `company-product-knowledge-builder`、`industry-application-map-builder`、`foreign-trade-customer-development` 或 `foreign-trade-customer-operations`。包必须说明本次允许写什么；没有写入授权时 `allowed_writes = none`。

专业技能返回时使用：

```text
specialist_return_packet:
  handoff_id
  source_skill
  source_route
  result_state: PASS | FAIL | UNVERIFIED
  business_summary
  source_record_id
  source_packet_reference
  evidence_reference
  blockers
  salesperson_decision_required
  proposed_workbench_updates
  specialist_write_status
  returned_at
```

协调器只保留 `PASS / FAIL / UNVERIFIED` 三态及逐项理由，不得把 `result_state` 换算成综合分，也不得在缺少返回包时自行补齐专业结论。

## 阶段5行业语义交接

`semantic_evaluation_mode` 必须与研究合同一致：新准备 RC2 合同默认 `content_first`；缺省历史合同是 `strict_audit`。当前四阶段已验收但 R4 链仍不完整时，返回包必须保留 `first_incomplete_stage: industry_semantic_expansion`。`CONTENT_CALIBRATION_PASS` 只能继续到独立全量授权门，不能被写成 beta.3 `EFFECTIVE` 或阶段 PASS。

内容优先的接收包：

```text
content_first_semantic_return:
  semantic_evaluation_mode: content_first
  terminology_bridge_reference
  terminology_bridge_sha256
  terminology_bridge_state: not_prepared | frozen_empty_cold_start | frozen_reviewed | hash_mismatch | invalidated
  development_regression_only: true
  development_regression_state: not_started | in_progress | PASS | FAIL | UNVERIFIED | invalidated
  formal_holdout_selection_origin_counts:
    retained_r3_unexecuted: 30
    new_unseen: 10
  formal_holdout_provenance_state: not_prepared | PASS | FAIL | UNVERIFIED | invalidated
  formal_holdout_case_set_sha256
  truth_contract_version: 2.1-r4-adjudicated
  truth_scorecard_contract_version: 2.1-r4
  truth_adjudication_state: not_started | in_progress | accepted | reopened | superseded | invalidated
  accepted_positive_case_ids_sha256
  accepted_positive_count
  accepted_negative_case_ids_sha256
  accepted_negative_count
  unresolved_case_ids_sha256
  unresolved_count
  truth_revision_invalidates_prior_scoring: true
  paired_task_manifest_reference
  paired_task_manifest_sha256
  formal_paired_task_chain_state: not_started | in_progress | PASS | FAIL | UNVERIFIED | invalidated
  source_truth_package_sha256
  scorecard_package_sha256
  receiver_evidence_manifest_sha256
  stability_task_manifest_reference
  stability_task_manifest_sha256
  stability_repeat_state: not_started | in_progress | PASS | FAIL | UNVERIFIED | invalidated
  content_method_state: CONTENT_CALIBRATION_INCOMPLETE | CONTENT_CALIBRATION_PASS | CONTENT_CALIBRATION_FAIL
  content_full_screening_state: NOT_AUTHORIZED | AUTHORIZED_NOT_STARTED | IN_PROGRESS | COVERAGE_INCOMPLETE | READY_FOR_REVERSE_AUDIT | BLOCKED
  content_full_screening_authorization_reference
  content_full_screening_authorization_receipt_reference
  content_full_screening_authorization_receipt_sha256
  content_terminal_scope_sha256
  raw_answer_references_and_hashes
  source_truth_references_and_hashes
  scorecard_references_and_hashes
  unknown_items_references
  platform_audit_state
  downstream_release_state: RESEARCH_ONLY_BLOCKED
```

术语桥引用、真实 SHA-256 或冻结状态缺失/错配时，返回 `content_first_contract_prepare`。`development_regression_state` 为 not_started / in_progress / UNVERIFIED 时，返回 `content_first_calibration_review (development-only)` 执行或复核开发集；只有 `FAIL → content_first_contract_prepare`，修复方法并重锁。所有开发结果仍为 `development_regression_only`，不计入正式评分。30 + 10 中性来源比例、闭集 provenance、真实案例集哈希、独立真值裁决、接受正例/反例/未决集合及哈希任一缺失时，返回 `semantic_calibration_case_prepare`。10个 `new_unseen` 必须全部由直接证据独立裁决为接受正例；这是一道冻结门，不是选样答案。真值 reopened 或 superseded 时，旧任务、评分、臂汇总和校准结论全部 invalidated。80个正式任务链必须绑定 `paired_task_manifest_reference` 和真实 `paired_task_manifest_sha256`；6个稳定性重复必须绑定 `stability_task_manifest_reference` 和真实 `stability_task_manifest_sha256`。这些清单、来源真值、评分卡或receiver证据任一不完整时，返回 `content_first_calibration_review`。

缺失原始回答、来源真值、评分卡或未知项时，接收结果只能为 `UNVERIFIED`。平台审计缺失单独记录为 `platform_audit_state`，不得删除字节完整的可评分回答，也不得把平台 PASS 换成内容 PASS。授权引用、Task 8 gate绑定、独立receipt引用与真实SHA-256、冻结末端范围SHA-256任一缺失或错配 → content_first_full_screening_gate (NOT_AUTHORIZED)。`full_screening_authorization` 布尔值或 `content_full_screening_state` 自报不构成授权；只有Task 8 gate验证receipt绑定当前最终合同、校准报告与末端范围后，才允许 `AUTHORIZED_NOT_STARTED`。

阶段5仍使用 `specialist_handoff_packet`，但 `target_route` 只按以下顺序取一个：

```text
content_first_contract_prepare
semantic_calibration_case_prepare
content_first_calibration_review
content_first_full_screening_gate
content_first_full_screening
semantic_contract_prepare (strict_audit only)
semantic_method_calibration
semantic_full_screening
semantic_evidence_expansion
semantic_reverse_audit
semantic_stage_review
```

`content_first_contract_prepare` 是 R4 内容优先的唯一合同准备名称；`semantic_contract_prepare` 只供 `strict_audit` 兼容。合同准备返回必须包含 `contract_state = case_preparation_locked`、`locked_input_sha256`、术语桥引用/哈希/状态、准备授权引用和隔离写入范围，同时证明案例集哈希、批次大小和控制案例尚未伪造。`semantic_calibration_case_prepare` 的返回必须包含 30 + 10 类别与来源计数、闭集 provenance、40例案例集的实际哈希、真实控制案例以及新版本最终冻结合同。未最终冻结时，控制器只能重派当前准备/修复动作；不得创建 `semantic_model_handoff_packet`。

需要外部模型时，附加只读运输包：

```text
semantic_model_handoff_packet:
  handoff_id
  research_contract_id
  contract_version
  semantic_work_unit_id
  target_role: A | B | C
  declared_model_name
  identity_evidence_policy
  transport: manual_external_handoff
  visible_input
  input_sha256
  input_hash_algorithm: sha256_canonical_json_v1
  expected_return_schema
  field_ownership
  manual_transport_rules
  prohibited_inputs
  prohibited_actions
  source_permissions
  stop_condition
```

运输包必须自包含，不能只写 `expected_return_contract` 名称再让用户寻找另一个模板。控制器只生成和校验包，不自动调用当前未接入的外部模型。用户只传递完整任务包和原始返回，不填写查询、证据、哈希或机器附页。

外部模型原始返回与Codex接收记录分层保存：

```text
semantic_model_return:
  task_id
  research_contract_id
  contract_version
  input_sha256
  declared_model_name
  actual_model_id_or_unknown
  provider_or_unknown
  model_reported_run_id: null | model-reported value
  model_reported_started_at: null | model-reported value
  result_state: PASS | FAIL | UNVERIFIED
  reason_codes
  source_access_results
  structured_findings
  unknowns
  model_reported_returned_at: null | model-reported value

semantic_model_receipt:
  receipt_id
  task_id
  research_contract_id
  contract_version
  transport
  raw_return_reference
  raw_return_sha256
  received_at
  identity_evidence
  executor_metadata
  acceptance_state: PASS | FAIL | UNVERIFIED
  reason_codes
```

`semantic_model_return`属于外部模型，`semantic_model_receipt`属于接收方。手工交接时，receiver-owned `executor_metadata` 的运行ID和起止时间必须为空；`codex_task` 或 `authorized_api` 必须从真实平台记录填写并注明provenance。任何一层都不得把Codex收件时间冒充模型运行时间。

控制器以两轴验收：

```text
review_result: PASS | FAIL | UNVERIFIED
admissibility_state: PASS | FAIL | UNVERIFIED
```

`review_result`来自模型内容结论；`admissibility_state`来自任务、输入哈希、返回结构、原件哈希、身份依据与运输检查。只有 `strict_audit` 要求两者均为PASS才能计入它的正式校准。`content_first` 将身份/运输缺口留在 `platform_audit_state`，另行核对原始字节、内容哈希、真值、评分卡和receiver证据；两轴不得相互覆盖。

阶段5专业返回使用：

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

返回包必须与当前合同、输入哈希和工作单元一致。`CONTENT_CALIBRATION_PASS` 只允许进入 `content_first_full_screening_gate`；不改变阶段5为PASS，也不取消 `RESEARCH_ONLY_BLOCKED`。仅 `strict_audit` 的40例 `EFFECTIVE` 可请求它的独立 `full_screening_authorization`。全量筛查、`application_base_write_authorization`、公司匹配、客户搜索、Git提交和插件安装都是分开的用户授权。

## 业务工作簿更新包

```text
workbench_update_packet:
  update_id
  company_id
  workbook_path
  expected_workbook_sha256
  sheet_name
  stable_record_id
  field_name
  old_value
  new_value
  decision_basis
  source_record_id
  source_packet_reference
  evidence_reference
  user_authorization
  requested_at
```

一个包只描述本次明确决定。需要改多个字段时逐项列出，不能用“同步状态”等模糊措辞扩大范围。写入后重开并核对，才可返回 `workbook_status = 已重开验证`。

## 候选采集任务

客户开发技能生成只读任务：

```text
candidate_collection_task:
  task_id
  company_id
  source_direction_id
  direction_packet_reference
  direction_packet_sha256
  declared_countries_or_regions
  declared_languages
  application_segment
  approved_product_scope
  allowed_source_scope
  search_scope
  observable_enterprise_rule
  candidate_direct_evidence_rule
  exclusion_boundary
  prohibited_inference
  output_contract: raw_candidate_batch
  issued_at
```

任务本身不包含“合格客户”结论。方向包哈希或声明范围变化后，旧任务失效，不能继续追加批次。

## 原始候选批次

采集执行器只追加 `raw_candidate_batch`：

```text
raw_candidate_batch:
  batch_id
  task_id
  executor_id
  executor_run_id
  append_only: true
  collected_at
  declared_queries
  observed_companies:
    - observed_company_id
      observed_name
      observed_website
      observed_country_or_region
      observed_product_or_activity
      source_url_or_local_reference
      source_publisher
      source_date_or_unknown
      observed_at
      access_scope
      collector_note
  access_failures
  scope_not_covered
```

采集执行器不得填写 PASS、FAIL、UNVERIFIED、业务员分类、方向状态、产品适配结论或客户优先级。修正只能新增一个批次并引用被修正的 `batch_id`；不得覆盖历史批次。

## 独立候选复核

客户开发技能在 `candidate_review` 中核对任务哈希、批次归属、重复项、公司主体、来源真实性、公司或品牌特定直接产品证据、反证和未知。每条结果只允许：

- `PASS`：满足候选直接证据门，进入业务前台等待业务员分类；
- `FAIL`：有明确排除依据，保留原因和证据；
- `UNVERIFIED`：证据不足、主体不清、来源不可访问或范围未覆盖，不能伪装成合格客户。

复核不得生成综合分、自动排名或自动方向决定。候选数量不证明方向有效；没有发现候选也不证明市场不存在。

## 共享输入过期

下列任一状态都创建或更新 `05-异常与风险` 记录，并阻断受影响的路线选择、方向编译或候选采集：

- taxonomy/application/product fact 输入哈希变化；
- 路线包登记不是 `current`；
- 路线包或源公司地图哈希不一致；
- 稳定编号无法解析或跨公司；
- 工作簿结构不兼容；
- 当前业务工作簿哈希与写入前预期不同。

解除阻断需要对应所有者重新验证或重新导出，并由协调器接收新的可追溯返回包；不能手工把异常状态改成通过。

## 工作表映射

| 专业返回 | 业务页 | 业务员字段 |
|---|---|---|
| 路线评审/路线过期 | `01-路线选择`、`05-异常与风险` | 业务员决定、决定依据、决定日期 |
| 候选复核 | `02-候选客户` | 业务员分类、下一步 |
| 背调/经营建议 | `03-客户跟进` | 业务员决定、下一步日期、备注 |
| 沟通草稿 | `04-沟通草稿` | 业务员审核、审核意见 |
| 风险、冲突、未核实 | `05-异常与风险` | 业务员决定、处理备注 |

协调器只投影业务必要摘要，不复制整个后台证据库。
