# 外贸全流程蓝图

`blueprint_id: foreign-trade-complete-workflow`

`blueprint_version: 0.5.0-beta.2`

## 判定原则

- 固定按本文件的阶段顺序判定，`first_incomplete_stage` 是第一项不满足 `gate_result = PASS` 且 `freshness = current` 的阶段。
- 缺少证据记为 `UNVERIFIED`，明确不合格记为 `FAIL`；过期单独记在 `freshness = stale`，不能用旧 PASS 放行。
- 后期工作簿、候选公司、草稿或实发记录不能反向证明前期阶段完整。
- 每次只把一项当前任务交给阶段所有者，返回包验收前停止。
- 任何跨任务指挥前先执行 `inspector_preflight`：读取当前会话 `memory.md`、可用的公司或框架治理登记与相关任务台账。普通缺陷记录后继续，小幅方向修正留下依据后继续；真值、盲测、哈希/合同、来源时序、拒绝覆盖或授权边界受损时必须暂停。治理是横向门，不增加或改变下列业务阶段。

## 权威阶段图

| 顺序 | Stage | 状态范围 | 所有者 | 必需输入 | 必需输出与 PASS 门 | STOP 条件 |
|---:|---|---|---|---|---|---|
| 1 | `environment_audit` | `company_foundation` | workflow director | 当前环境、插件源、蓝图 | 必需技能可发现，版本/能力可核对，空模板可读，路径和权限已验证 | 缺失、不兼容或兼容性无法验证 |
| 2 | `company_identity` | `company_foundation` | company product knowledge builder | 用户明确的公司边界与来源范围 | 唯一 `company_id`、隔离根目录、批准的来源范围 | 公司不明、与现有公司冲突或来源范围未确认 |
| 3 | `product_knowledge` | `company_foundation` | company product knowledge builder | 批准来源 | 当前产品事实库与 `product_development_fact_packet`，证据和限制可追溯 | 缺包、来源失效、哈希过期或事实冲突未处置 |
| 4 | `industry_taxonomy` | `company_foundation` | industry application map builder | 官方分类来源与版本 | 版本化行业分类骨架、稳定编号和覆盖登记 | 分类来源/版本未核实或结构不完整 |
| 5 | `industry_semantic_expansion` | `company_foundation` | industry application map builder | 当前分类骨架、冻结RC2合同、方法状态和独立授权 | 全部末端节点具备同一合同的可审计浅筛，触发节点已完成证据处置，分层反向审计上界通过且无安全失败 | 合同/校准/全量/证据/审计任一未通过，或仍有 `not_screened` |
| 6 | `company_industry_match` | `company_foundation` | industry application map builder | 当前产品事实包与当前行业语义层 | 公司能力原子与应用需求的逐项匹配、反证和未知；不得直接按行业名称匹配 | 语义层过期、直接名称推断或未知被自动提升 |
| 7 | `route_pool_handoff` | `company_foundation` | industry application map builder | 当前公司地图与覆盖复核 | 已登记为 current 的 `company_route_pool_packet`，输入和生产者哈希一致 | 路线包或源图过期、范围未覆盖 |
| 8 | `direction_decision` | `route_instance` | customer development + salesperson | 当前路线池与业务员选路 | 方向已编译和验证，业务员明确记录是否 `已确认可扫描` | 没有人工选路/确认或方向规则未验证 |
| 9 | `candidate_development` | `direction_instance` | customer development | 已确认方向 | 采集任务、追加原始批次、独立复核、业务员分类和背调阶段保持分离 | 执行器越权判断、证据不足或范围未完成 |
| 10 | `customer_operations` | `customer_thread` | customer operations + customer communication + salesperson | 经选择并允许沟通的客户、前序验收、绑定哈希及完整线程 | 开发验收、运营决策、沟通简报、候选、审核、实发、回复和风险状态逐段硬链接 | 缺少登记转换、前序接收凭证、人工决定、线程证据或严重风险 |
| 11 | `framework_review` | `review_cycle` | workflow director | 全部阶段状态与已验证反馈 | 记录缺口、过期事件、适用教训和版本变化，不改写专业事实 | 未验证结果被当成通用规则或私有数据进入框架 |

阶段顺序是依赖关系，不是把整个公司压成一条一次性进度条：

- 1–7 是公司级 `company_foundation`。其中任一阶段不通过，所有受影响的后续实例暂停。
- 8 按每条 `route_instance` 保存；9 按每个 `direction_instance` 保存；10 按每个 `customer_thread` 保存。
- 一条路线、一个方向或一个客户完成，不能把全公司的同名阶段永久记为完成。
- 基础通过后，控制器必须读取用户明确指定或业务前台当前选中的 `active_work_unit`；没有明确工作单元时，先让业务员选择，不擅自挑选。
- `framework_review` 按一次 `review_cycle` 保存，只在重大失败、依赖变化或已授权里程碑触发；没有新复盘任务本身不阻断下一条业务实例。

完整行业骨架不等于行业语义层完成。骨架中的 `not_expanded` 只是旧式覆盖登记，不能代替 RC2 的可审计筛查记录。正式流程覆盖范围必须是 `full registered terminal-node scope`；每个节点需要可审计浅筛，但并非每个节点都强制深度展开。只要还有 `not_screened`、未处置触发节点或未通过反向审计，流程必须停在 `industry_semantic_expansion`，旧公司地图、路线池和客户数据均不能越过这个门。

上述是公司基础层的全局门。业务员已确认的某一命名行业可进入 `business_route_closure_review` 覆盖层，但不将阶段5–7改为PASS。覆盖层必须哈希绑定业务范围、产品中性应用闭合、有限方向验证和跨技能回执；`global_semantic_stage_effect = none`，只允许将该方向呈现给业务员，客户扫描仍需人工另行授权。

用户可以明确授权一个 `pilot` 范围来验证字段和方法，但 pilot 只能标记为局部验证，不能把 `industry_semantic_expansion` 的全量门记为 PASS，也不能据此声称已经完成全行业筛查。

## 阶段5内部状态机

### 严格审计兼容模式

控制器按以下顺序选择一个且仅一个专业路由：

```text
semantic_contract_prepare
→ semantic_calibration_case_prepare
→ semantic_method_calibration
→ full_screening_authorization
→ semantic_full_screening
→ semantic_evidence_expansion
→ semantic_reverse_audit
→ semantic_stage_review
```

前两步包含两个独立门：`semantic_contract_prepare` 产出哈希锁定的 `case_preparation_locked` 输入，案例集哈希与控制案例仍为空；`semantic_calibration_case_prepare` 产出真实40例，再把实际案例集哈希和真实控制案例绑定到新版本最终冻结合同。未最终冻结时，不得进入 `semantic_method_calibration`，也不得生成模型运行任务。

strict_audit 的 `semantic_method_validation_state` 只允许 `INCONCLUSIVE / EFFECTIVE / NOT_EFFECTIVE`。结构测试、文档完整、单模型自评或外部模型多数意见都不能把它改为 strict_audit 的 `EFFECTIVE`。40例通过也不能把 `industry_semantic_expansion` 记为 PASS，更不能自动获得全量筛查或 `application_base_write_authorization`。

当前外部模型运输方式是 `manual_external_handoff`。没有经过另行授权和验证的API/MCP连接器时，控制器不自动调用外部模型；它只生成一份自包含任务包，包内含可见输入、规范化输入哈希、精确返回Schema、字段责任、允许空值和停止点。外部原始返回与receiver-owned接收封套分开保存；手工交接不得伪造执行器运行ID或运行时间。

### 内容优先默认模式

新准备的 RC2 合同默认 `semantic_evaluation_mode = content_first`；缺省或历史 beta.3 合同按 `strict_audit`。内容优先的每个评分对象必须有完整原始回答、可见输入哈希、来源真值对照、逐项评分、未知项和独立 `platform_audit_state`。

当前四阶段已验收，但任一 R4 合同、开发回归、正式保留集、稳定性、全量、证据或反向审计门仍未通过时，动态状态为 `first_incomplete_stage: industry_semantic_expansion`。空白新公司的模板仍从 `environment_audit` 起算。

内容优先固定按以下顺序路由，任何非 PASS 或不完整证据都停在当前步：

```text
content_first_contract_prepare
→ semantic_calibration_case_prepare
→ content_first_calibration_review
→ content_first_full_screening_gate
→ content_first_full_screening
→ semantic_evidence_expansion
→ semantic_reverse_audit
→ semantic_stage_review
```

术语桥引用、真实 SHA-256 或冻结状态缺失/错配时只路由 `content_first_contract_prepare`。10个开发回归必须标记 `development_regression_only` 并单独记录 `development_regression_state`；`not_started / in_progress / UNVERIFIED → content_first_calibration_review (development-only)`，只执行或复核开发集；`FAIL → content_first_contract_prepare`，修复方法并重锁。任何开发结果都不得计入正式效果。正式保留集必须是中性的 30 + 10：30个 `retained_r3_unexecuted` 加10个 `new_unseen`，并以 `formal_holdout_provenance_state` 和真实 `formal_holdout_case_set_sha256` 验收；抽样来源和覆盖类别不得定义真值。正例、反例和未决例只从 `truth_contract_version = 2.1-r4-adjudicated` 的 accepted 裁决记录推导，冻结 `accepted_positive_case_ids_sha256`、`accepted_negative_case_ids_sha256`、`unresolved_case_ids_sha256` 及对应数量；正例分母动态取实际接受集合，但10个 `new_unseen` 必须全部为接受正例。真值 reopened 或 superseded 时，旧任务、评分和校准结果全部失效并退回 `semantic_calibration_case_prepare`。正式80任务链必须绑定真实 `paired_task_manifest_sha256`，预声明的6个稳定性重复必须绑定真实 `stability_task_manifest_sha256`；任务清单、来源真值、评分卡、receiver证据或稳定性任一缺失时，只路由 `content_first_calibration_review`。

`CONTENT_CALIBRATION_PASS` 只能证明内容门已通过；它不是 legacy strict_audit 的 `EFFECTIVE`，也不能让 `industry_semantic_expansion` 变为 `PASS`。静态结构测试或 `platform_audit_state = PASS` 都不能生成内容 PASS；平台审计缺失也不得删除字节完整且可评分的内容。全量默认 `NOT_AUTHORIZED`；授权引用、Task 8 gate绑定、独立receipt引用与真实SHA-256、冻结末端范围SHA-256任一缺失或错配 → content_first_full_screening_gate (NOT_AUTHORIZED)。只有这些证据全部非空且互相匹配、Task 8 gate验证其绑定当前最终合同/校准报告/末端范围且零安全失败，才允许 `AUTHORIZED_NOT_STARTED`；布尔值或状态自报无效。全量、证据展开和反向审计完成后仍保持 `RESEARCH_ONLY_BLOCKED`：不得写共享应用底座、公司匹配、路线包、候选客户或对外沟通。

## 必需能力依赖

| Skill | 蓝图要求的能力 |
|---|---|
| `company-product-knowledge-builder` | 公司隔离、来源接收、产品事实维护、受控产品事实包 |
| `industry-application-map-builder` | 官方分类骨架、产品中立行业语义展开、多产品公司匹配、业务路线应用闭合、覆盖复核、路线池导出 |
| `foreign-trade-customer-development` | 完整路线编译、有限方向验证、候选任务、原始批次接收、独立复核、背调和沟通前交接 |
| `foreign-trade-customer-operations` | 客户线程、实际互动、状态、下一动作、商业边界和沟通简报；不生成对外正文 |
| `foreign-trade-customer-communication` | 只基于已验收沟通简报生成对外候选正文；不决定客户状态、商业条件、批准或发送 |

只看到技能名称或安装目录不能证明能力兼容。`environment_audit` 必须核对实际版本、技能合同、来源市场和所需路由；没有兼容矩阵或直接证据时记为 `UNVERIFIED`。同一技能名来自两个已启用市场时记为 `FAIL`，在用户单独选定唯一来源并授权迁移前不安装、卸载或继续路由。

当前待验证候选集固定为：`company-product-knowledge-builder 0.1.0`、`industry-application-map-builder 0.4.0-beta.7`、`foreign-trade-customer-development 0.3.0-beta.2`、`foreign-trade-customer-operations 0.3.0-beta.1`、`foreign-trade-customer-communication 0.1.0-beta.1`和 `foreign-trade-workflow-director 0.5.0-beta.2`。其中任一版本不符只能记为 `UNVERIFIED`。接口集成通过只证明字段、哈希、路由和停止门可交接，不证明业务技能的真实效果。

`customer_operations` 是业务大阶段，不等于一个技能独占全部工作。它的客户线程内部固定按 `DEVELOPMENT_READY → THREAD_ACCEPTED / INTERACTION_ACCEPTED → OPERATION_DECISION_READY → COMMUNICATION_BRIEF_ACCEPTED → COMMUNICATION_CANDIDATE_READY → CANDIDATE_REVIEW_PENDING` 前进，精确转换以 `customer-flow-transition-registry.v1.json` 为准。控制器只接受组合验证器 PASS 的一段交接；不得把后段文件存在、草稿生成或人工批准当作前段已经完成，更不得把批准写成实际发送。

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
  semantic_method:
    semantic_evaluation_mode: content_first | strict_audit
    semantic_method_validation_state
    terminology_bridge_reference
    terminology_bridge_sha256
    terminology_bridge_state
    development_regression_only
    development_regression_state
    case_package_contract_version
    truth_contract_version
    truth_scorecard_contract_version
    formal_holdout_case_set_sha256
    retained_r3_unexecuted_case_count
    new_unseen_case_count
    truth_adjudication_state
    accepted_positive_case_ids_sha256
    accepted_positive_count
    accepted_negative_case_ids_sha256
    accepted_negative_count
    unresolved_case_ids_sha256
    unresolved_count
    truth_revision_invalidates_prior_scoring
    inspector_preflight_required
    inspector_memory_reference
    inspector_preflight_state
    deferred_findings_reference
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
    content_method_state
    content_full_screening_state
    content_full_screening_authorization_reference
    content_full_screening_authorization_receipt_reference
    content_full_screening_authorization_receipt_sha256
    content_terminal_scope_sha256
    downstream_release_state
    active_research_contract_id
    active_research_contract_version
    active_semantic_work_unit
    full_screening_authorization
    application_base_write_authorization
    latest_semantic_return_reference
    latest_semantic_receipt_reference
    latest_review_result
    latest_admissibility_state
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
  r4_semantic_contract_dependencies
  authorized_shared_product_neutral_references
  required_permissions
  installation_or_copy_steps
  validation_steps
  recovery_checkpoints
  missing_dependencies
  unverified_items
  excluded_company_data_classes
```

`r4_semantic_contract_dependencies` 必须闭集保留 `content_full_screening_state`、`content_full_screening_authorization_reference`、`content_full_screening_authorization_receipt_reference`、`content_full_screening_authorization_receipt_sha256` 与 `content_terminal_scope_sha256`。空白复刻清单默认为 `NOT_AUTHORIZED` 且四项绑定字段均为 null；复制布尔值或状态不能获得授权。

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
