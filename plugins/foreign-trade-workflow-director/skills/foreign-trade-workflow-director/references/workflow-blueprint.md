# 外贸全流程蓝图

`blueprint_id: foreign-trade-complete-workflow`

`blueprint_version: 0.1.0-beta.1`

## 判定原则

- 固定按本文件的阶段顺序判定，`first_incomplete_stage` 是第一项不满足 `gate_result = PASS` 且 `freshness = current` 的阶段。
- 缺少证据记为 `UNVERIFIED`，明确不合格记为 `FAIL`；过期单独记在 `freshness = stale`，不能用旧 PASS 放行。
- 后期工作簿、候选公司、草稿或实发记录不能反向证明前期阶段完整。
- 每次只把一项当前任务交给阶段所有者，返回包验收前停止。

## 权威阶段图

| 顺序 | Stage | 状态范围 | 所有者 | 必需输入 | 必需输出与 PASS 门 | STOP 条件 |
|---:|---|---|---|---|---|---|
| 1 | `environment_audit` | `company_foundation` | workflow director | 当前环境、插件源、蓝图 | 必需技能可发现，版本/能力可核对，空模板可读，路径和权限已验证 | 缺失、不兼容或兼容性无法验证 |
| 2 | `company_identity` | `company_foundation` | company product knowledge builder | 用户明确的公司边界与来源范围 | 唯一 `company_id`、隔离根目录、批准的来源范围 | 公司不明、与现有公司冲突或来源范围未确认 |
| 3 | `product_knowledge` | `company_foundation` | company product knowledge builder | 批准来源 | 当前产品事实库与 `product_development_fact_packet`，证据和限制可追溯 | 缺包、来源失效、哈希过期或事实冲突未处置 |
| 4 | `industry_taxonomy` | `company_foundation` | industry application map builder | 官方分类来源与版本 | 版本化行业分类骨架、稳定编号和覆盖登记 | 分类来源/版本未核实或结构不完整 |
| 5 | `industry_semantic_expansion` | `company_foundation` | industry application map builder | 当前分类骨架、明确覆盖范围 | 全量筛查时，全部登记末端节点具备产品中立的产出、过程/使用点、应用、需求、证据、限制和覆盖处置 | 任一应覆盖节点仍为 `not_expanded` 或只有行业名称推测 |
| 6 | `company_industry_match` | `company_foundation` | industry application map builder | 当前产品事实包与当前行业语义层 | 公司能力原子与应用需求的逐项匹配、反证和未知；不得直接按行业名称匹配 | 语义层过期、直接名称推断或未知被自动提升 |
| 7 | `route_pool_handoff` | `company_foundation` | industry application map builder | 当前公司地图与覆盖复核 | 已登记为 current 的 `company_route_pool_packet`，输入和生产者哈希一致 | 路线包或源图过期、范围未覆盖 |
| 8 | `direction_decision` | `route_instance` | customer development + salesperson | 当前路线池与业务员选路 | 方向已编译和验证，业务员明确记录是否 `已确认可扫描` | 没有人工选路/确认或方向规则未验证 |
| 9 | `candidate_development` | `direction_instance` | customer development | 已确认方向 | 采集任务、追加原始批次、独立复核、业务员分类和背调阶段保持分离 | 执行器越权判断、证据不足或范围未完成 |
| 10 | `customer_operations` | `customer_thread` | customer operations + salesperson | 经选择并允许沟通的客户及完整线程 | 草稿、审核、实发、回复、跟进和风险状态分离 | 没有授权、线程不完整、回复硬停或严重风险 |
| 11 | `framework_review` | `review_cycle` | workflow director | 全部阶段状态与已验证反馈 | 记录缺口、过期事件、适用教训和版本变化，不改写专业事实 | 未验证结果被当成通用规则或私有数据进入框架 |

阶段顺序是依赖关系，不是把整个公司压成一条一次性进度条：

- 1–7 是公司级 `company_foundation`。其中任一阶段不通过，所有受影响的后续实例暂停。
- 8 按每条 `route_instance` 保存；9 按每个 `direction_instance` 保存；10 按每个 `customer_thread` 保存。
- 一条路线、一个方向或一个客户完成，不能把全公司的同名阶段永久记为完成。
- 基础通过后，控制器必须读取用户明确指定或业务前台当前选中的 `active_work_unit`；没有明确工作单元时，先让业务员选择，不擅自挑选。
- `framework_review` 按一次 `review_cycle` 保存，只在重大失败、依赖变化或已授权里程碑触发；没有新复盘任务本身不阻断下一条业务实例。

完整行业骨架不等于行业语义层完成。用于“从行业骨架中筛选潜在行业”的正式流程，覆盖范围必须是 `full registered terminal-node scope`；只要其中仍有 `not_expanded`，流程必须停在 `industry_semantic_expansion`，旧公司地图、路线池和客户数据均不能越过这个门。

用户可以明确授权一个 `pilot` 范围来验证字段和方法，但 pilot 只能标记为局部验证，不能把 `industry_semantic_expansion` 的全量门记为 PASS，也不能据此声称已经完成全行业筛查。

## 必需能力依赖

| Skill | 蓝图要求的能力 |
|---|---|
| `company-product-knowledge-builder` | 公司隔离、来源接收、产品事实维护、受控产品事实包 |
| `industry-application-map-builder` | 官方分类骨架、产品中立行业语义展开、公司匹配、覆盖复核、路线池导出 |
| `foreign-trade-customer-development` | 路线编译/验证、候选任务、原始批次接收、独立复核、背调和沟通前交接 |
| `foreign-trade-customer-operations` | 首封、未回复跟进、完整线程回复、严重问题和经营建议，不发送 |

只看到技能名称或安装目录不能证明能力兼容。`environment_audit` 必须核对实际版本、技能合同和所需路由；没有兼容矩阵或直接证据时记为 `UNVERIFIED`。

## `workflow_blueprint`

便携蓝图只包含：

```text
workflow_blueprint:
  blueprint_id
  blueprint_version
  ordered_stages
  stage_dependencies
  stage_owner_skills
  required_inputs_and_outputs
  acceptance_and_stop_conditions
  portable_template_references
  schema_references
  prohibited_actions
  company_data_boundaries
```

当前空模板：

- `../assets/company-workflow-state.template.yaml`
- `../assets/workflow-replication-manifest.template.yaml`

## `company_workflow_state`

每家公司独立保存：

```text
company_workflow_state:
  company_id
  company_root
  blueprint_id
  blueprint_version
  first_incomplete_stage
  company_foundation:
    - stage_id
      gate_result: PASS | FAIL | UNVERIFIED
      freshness: current | stale | unknown
      artifact_references
      artifact_versions
      artifact_hashes
      blockers
  pending_handoff
  pending_human_decision
  active_work_unit
  work_units:
    - work_unit_type: route_instance | direction_instance | customer_thread | review_cycle
      work_unit_id
      parent_work_unit_id
      stage_id
      gate_result: PASS | FAIL | UNVERIFIED
      freshness: current | stale | unknown
      artifact_references
      blockers
  next_action
  last_audited_at
```

`company_id`、根目录和所有公司产物必须一一对应。发现另一家公司的标识或证据时立即 `FAIL`，隔离该产物，不自动修复或合并。

## `workflow_replication_manifest`

跨公司或跨账号的清单只包含便携框架材料：

```text
workflow_replication_manifest:
  blueprint_id
  blueprint_version
  required_plugins_and_compatible_versions
  empty_template_paths_and_hashes
  contract_and_schema_versions
  authorized_shared_product_neutral_references
  required_permissions
  installation_or_copy_steps
  validation_steps
  recovery_checkpoints
  missing_dependencies
  unverified_items
  excluded_company_data_classes
```

每条获授权共享的产品中立知识引用还必须保留来源、访问范围和可转移权限；“产品中立”不自动等于允许跨账号复制。

清单不得包含 `private company data`：公司产品事实、公司地图、路线决定、客户记录、联系人、草稿、实发、回复和凭证。共享的产品中立知识也只有在明确授权后才能进入清单。

生成清单、安装插件、复制文件、写入目标账号、验证目标环境是不同动作，均遵守 `separate authorization`。目标环境只有在重新完成 `environment_audit` 并找到自己的 `first_incomplete_stage` 后，才算具备可续作状态。

## 新公司空白初始化

`company_framework_bootstrap` 只允许创建：

- 新的稳定 `company_id` 与隔离根目录；
- 空的 `company_workflow_state`；
- 经核对哈希的空模板副本；
- 只包含来源范围和待办的登记项；
- 系统交接目录与当前单一编辑者声明。

它不得填入产品事实、行业适配、路线、候选客户或沟通历史。初始化完成只证明结构可用；`product_knowledge` 仍需从新公司的批准来源开始。

## 验收边界

- 静态合同测试 PASS：只证明蓝图、字段和门禁被写入技能源文件。
- 第二家公司冷启动 PASS：必须在空公司根目录完成初始化且无跨公司数据。
- 跨账号复刻 PASS：必须在另一账号核对依赖、模板哈希、权限并正确识别首个未完成阶段。
- 安装成功、文件复制成功或一次对话回答正确，均不能单独证明完整复刻有效。
