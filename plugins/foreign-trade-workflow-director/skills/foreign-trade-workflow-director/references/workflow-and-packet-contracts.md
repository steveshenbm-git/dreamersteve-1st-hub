# 业务前台与交接合同

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

## 协调器交接

```text
specialist_handoff_packet:
  handoff_id
  company_id
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
  requested_at
```

`target_skill` 只允许 `industry-application-map-builder`、`foreign-trade-customer-development` 或 `foreign-trade-customer-operations`。包必须说明本次允许写什么；没有写入授权时 `allowed_writes = none`。

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
