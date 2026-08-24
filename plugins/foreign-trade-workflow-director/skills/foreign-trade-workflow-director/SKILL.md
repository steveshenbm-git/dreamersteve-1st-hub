---
name: foreign-trade-workflow-director
description: Use when a company needs to audit, build, resume, or reproduce the complete foreign-trade workflow across product knowledge, content-first or strict-audit industry semantics, company-industry matching, route decisions, candidate development, and customer operations.
---

# 外贸全流程控制与复刻

## RC2 semantic mode

For a newly prepared RC2 research contract, use `content_first` as the default semantic route. It requires a content envelope, unchanged raw-response hash, visible-input hash, source/truth comparison, itemized scorecard, unknown items, method arm, and separate `platform_audit_state`. Platform run IDs, platform time, or strong model identity are not content-PASS prerequisites and their absence cannot justify deleting a scoreable raw answer.

Use `strict_audit` when it is explicitly selected or a legacy beta.3 contract has no mode field. Preserve its `INCONCLUSIVE / EFFECTIVE / NOT_EFFECTIVE` semantics and every identity, transport, receipt, and admissibility gate unchanged. `CONTENT_CALIBRATION_PASS` is not strict `EFFECTIVE`; it yields only a check for explicit full-scope authorization. `RESEARCH_ONLY_BLOCKED` always prohibits shared-base writes, company matching, route handoff, candidate work, customer work, and sending.

## 核心角色

这是 `portable_workflow_blueprint_beta`：一套可版本化、可审计、可为不同公司重新初始化、可为另一个 Codex 账号准备复刻清单的外贸全流程控制层。

本技能负责识别完整流程中最早未完成或已过期的阶段、调用阶段所有者、验收交接、守住停止点，并把结果投影为业务员能操作的下一动作。它不替代专业技能的事实判断，也不把某一家公司的事实、路线、客户或沟通历史当作可复用框架。

每次开始前完整读取：

1. [workflow-blueprint.md](references/workflow-blueprint.md)
2. [workflow-and-packet-contracts.md](references/workflow-and-packet-contracts.md)

六页 `salesperson_workbench` 继续作为下游业务前台，但不是判断全流程是否完整的事实来源。

## 权威阶段顺序

阶段固定为：

`environment_audit → company_identity → product_knowledge → industry_taxonomy → industry_semantic_expansion → company_industry_match → route_pool_handoff → direction_decision → candidate_development → customer_operations → framework_review`

只有当前阶段的必需产物、来源登记、版本或哈希、验收条件和新鲜度都通过，才能进入下一阶段。后期文件不能证明前期已经完成。

前七段属于公司级 `company_foundation`；`direction_decision` 按 `route_instance`、`candidate_development` 按 `direction_instance`、`customer_operations` 按 `customer_thread` 循环记录。一条路线或一个客户完成，不能把整个公司的后续阶段永久标为完成。

当行业分类骨架已经存在，但RC2研究合同、方法校准、全量浅筛、触发节点证据处置或反向审计任一未通过时，`industry_semantic_expansion` 就是最早未完成阶段。此时必须阻断旧公司地图、旧路线包和客户搜索，不能因目录里已有后期文件而越级。

## 路由

每次只选择一个 `task_route`：

| Route | 使用条件 | 输出与停止点 |
|---|---|---|
| `framework_audit` | 用户问当前流程到了哪里、缺什么、为什么不能继续，或任何继续动作开始前 | 读取真实环境与登记产物，返回 `framework_audit_packet`、最早未完成阶段和一项下一动作；只读请求不得写入 |
| `company_framework_bootstrap` | 用户要为新公司搭建完整框架，且已明确公司边界并授权创建空结构 | 创建独立 `company_id`、空目录/登记和状态文件，重开验证后停止；不得带入另一家公司数据 |
| `framework_resume` | 已有公司工作区需要恢复上下文或继续 | 从蓝图和实际产物重建 `company_workflow_state`，只路由到最早未完成或已过期阶段 |
| `specialist_handoff` | 当前阶段必须由专业技能执行 | 生成一个有边界的 `specialist_handoff_packet`；收到可追溯返回包并验收前不进入下一阶段 |
| `framework_replication_plan` | 用户要在第二家公司或另一个账号复刻流程 | 生成 `workflow_replication_manifest` 与缺失依赖报告；安装、传输和目标账号写入仍需单独授权 |
| `business_decision_record` | 业务员明确给出路线、客户、跟进、草稿或风险字段决定 | 生成并在明确授权后执行 `workbench_update_packet`；保存后重开验证并停止 |

用户直接点名专业技能时，可以把该技能的返回接入当前公司状态，但不能跳过其前置阶段或夺取其证据判断。跨越多个阶段的请求只执行当前已授权阶段；后续阶段必须等待当前验收通过。

## 启动与续作算法

1. 先区分只读检查、结构写入、业务写入、安装/传输和外部动作；一种授权不能代替另一种。
2. 执行 `framework_audit`：核对蓝图版本、四个必需专业技能、模板、路径、权限、公司隔离和实际登记产物。缺少依赖或无法证明版本兼容时停在 `environment_audit`。
3. 确认唯一稳定的 `company_id` 与隔离的公司根目录。发现跨公司标识、路径或产物时记为 `FAIL` 并停止。
4. 按权威阶段顺序逐项读取直接证据。每阶段分别记录 `gate_result: PASS | FAIL | UNVERIFIED` 和 `freshness: current | stale | unknown`。
5. 第一项非 `PASS + current` 的阶段就是 `first_incomplete_stage`。只给出由该阶段所有者执行的一项当前动作。
6. 前七段全部通过后，读取明确的 `active_work_unit`；后续状态分别绑定 `route_instance`、`direction_instance` 或 `customer_thread`。没有明确工作单元时先让业务员选择，不自动挑选。
7. 专业返回必须核对公司、工作单元、来源、版本/哈希、声明范围、结果状态和禁止动作。仅凭文件名、存在一个工作簿或已有候选公司，不得判定阶段完成。
8. 当前阶段通过后更新对应公司基础或业务实例，再重新从第一阶段计算；不依赖聊天记忆直接跳到后期。

用于全行业筛查时，全部登记末端节点必须具有同一冻结合同下的可审计浅筛记录；所有触发节点完成证据处置，反向审计通过且无安全失败后，才可把阶段记为PASS。小范围pilot或40例只能验证方法，不能代替全量门。

## 阶段5内部续作

当 `first_incomplete_stage = industry_semantic_expansion` 时，读取：

- `semantic_method_validation_state`；
- `active_research_contract_id` 和版本；
- `active_semantic_work_unit`；
- `full_screening_authorization`；
- `application_base_write_authorization`；
- 最新 `semantic_specialist_return_packet` 及其哈希。

Also read `semantic_evaluation_mode`. If it is `content_first`, read `content_method_state`, `content_full_screening_state`, `content_full_screening_authorization_reference`, `content_terminal_scope_sha256`, and `downstream_release_state`. Select exactly one content-first route:

```text
content contract not final frozen or rubric incomplete → content_first_contract_prepare
40 content evidence incomplete → content_first_calibration_review
CONTENT_CALIBRATION_FAIL or CONTENT_CALIBRATION_INCOMPLETE → stop for repair or evidence
CONTENT_CALIBRATION_PASS but authorization missing → content_first_full_screening_gate (NOT_AUTHORIZED)
authorization present but no batches → content_first_full_screening_gate (AUTHORIZED_NOT_STARTED)
authorized batches incomplete → content_first_full_screening
coverage complete → semantic_evidence_expansion then semantic_reverse_audit
any attempted downstream release → FAIL and keep RESEARCH_ONLY_BLOCKED
```

No controller action may change `RESEARCH_ONLY_BLOCKED` to a downstream PASS. A future bridge from content-first research into the official workflow requires a separately authored migration contract and user authorization; this skill does not implement that bridge.

固定路由顺序为：

```text
候选/案例准备输入未锁为 case_preparation_locked → semantic_contract_prepare
40例或新版本最终冻结合同未准备 → semantic_calibration_case_prepare
未最终冻结 → 继续停在 semantic_calibration_case_prepare
方法未EFFECTIVE → semantic_method_calibration
未获全量授权 → 等待用户决定
全量未筛完 → semantic_full_screening
触发节点未处置 → semantic_evidence_expansion
反向审计未通过 → semantic_reverse_audit
阶段尚未验收 → semantic_stage_review
```

`semantic_contract_prepare` 只验收产品中性主题、节点快照、模型/提示词、检索、证据、预算、抽样和隔离写入边界，并产生 `locked_input_sha256`；不得要求尚未生成的案例集哈希或控制案例，也不得称为模型运行合同。`semantic_calibration_case_prepare` 只有在该锁有效时才能准备候选与40例，完成后必须用实际案例集哈希和真实控制案例生成新版本最终冻结合同。任何A/B/C任务都继续要求最终 `contract_state = frozen`。

每次只生成一个 `specialist_handoff_packet` 和一项下一动作。步骤返回 `FAIL` 或 `UNVERIFIED` 时只路由该步的修复，不越过它。40例结果即使 `EFFECTIVE`，也不能把 `industry_semantic_expansion` 记为 PASS。

外部模型当前使用 `manual_external_handoff`：控制器只接收专业技能生成的一份自包含 `semantic_model_handoff_packet`，其中必须已有可见输入、规范化输入哈希、精确返回Schema、字段责任、允许空值和停止点。用户只传递完整任务包和原始返回，不寻找额外模板、不填写机器证据附页。原始返回由专业技能原样保存；收件时间、原件哈希、身份依据和真实运输元数据写入独立receiver-owned `semantic_model_receipt`。不得把Codex收件时间或自造编号回填成外部模型运行事实。

控制器必须分别读取 `review_result` 与 `admissibility_state`。即使内容审查为 `PASS`，只要身份、运输、输入或原件哈希仍为 `UNVERIFIED`，就停在当前模型交接，不得升级证据、计入40例或进入下一阶段。

## 专业所有权

- `company-product-knowledge-builder`：公司身份边界、来源接收、产品事实库和受控产品事实包；不得自行推断行业路线。
- `industry-application-map-builder`：官方行业骨架、RC2方法合同与校准、产品中立浅筛/证据/反向审计、公司能力匹配、覆盖复核和路线池交接；它不搜索具体客户。
- `foreign-trade-customer-development`：路线编译与验证、候选采集任务、原始批次接收、独立候选复核、完整背调和沟通前交接。
- `foreign-trade-customer-operations`：首封、未回复跟进、完整线程回复、严重问题和既有客户经营材料；不得发送。
- 获批准的采集执行器：只执行 `candidate_collection_task` 并追加 `raw_candidate_batch`；不判断客户合格，不写业务工作簿。

专业技能拥有各自事实、证据和结论。本技能拥有阶段图、环境审计、初始化、交接门禁、状态登记、复刻清单和业务摘要。若专业技能缺少蓝图要求的路由或返回合同，标为 `UNVERIFIED`，不能由控制器临时编造专业结论。

## 新公司与跨账号复刻

- 新公司只能从空模板和显式输入启动。新的 `company_id`、根目录、状态登记、来源范围和当前编辑者必须独立建立。
- 空状态与复刻清单分别从 `assets/company-workflow-state.template.yaml` 和 `assets/workflow-replication-manifest.template.yaml` 创建，不凭聊天临时发明字段。
- 可复用的是蓝图、合同、空模板、插件依赖说明、验证方法和经授权的产品中立共享知识引用。
- 不可复用的是公司产品事实、公司适配图、路线决定、客户记录、联系人、草稿、实发记录、回复和凭证。
- `framework_replication_plan` 只说明需要什么和如何验证。没有单独授权，不安装插件、不复制文件、不写目标账号，也不声称复刻成功。
- 复制目录或安装成功都不是完整复刻证据；目标环境仍要重新执行 `framework_audit` 并找到自己的 `first_incomplete_stage`。

## 六页业务前台

- `00-我的待办`：只放需要人处理或确认的一项当前动作。
- `01-路线选择`：一行一条路线，由业务员记录路线决定和依据。
- `02-候选客户`：一行一家公司，由业务员记录分类和下一步。
- `03-客户跟进`：只呈现真实互动基准、当前状态和下一动作。
- `04-沟通草稿`：保存可审核草稿、中文译文、边界和审核决定；草稿或批准不等于发送。
- `05-异常与风险`：保存过期、失败、未核实、风险暂停和并发冲突。

不得要求业务员日常编辑共享行业骨架、产出产品、应用节点、需求原子、关系边、证据来源、覆盖台账或变更记录。通过稳定编号和来源引用查看后台证据。当前 Beta 只允许一人编辑；第二编辑者或锁冲突进入异常页，不自动合并。

## 状态与硬门

- 专业复核只接受 `PASS / FAIL / UNVERIFIED` 及逐项理由；不得生成综合分、模型排名或自动优先级。
- 路线决定、客户分类、跟进决定、风险处置、最终文案、渠道和发送始终属于业务员。
- 回复或疑似回复 → 风险暂停 → 停止/拒绝/持续退信 → 输入过期 → 到期跟进 → 普通待办。
- 共享输入、公司地图或路线包版本/哈希过期时，返回对应所有者重新验证；不得手工改成通过。
- 源编辑、40例、全量筛查、正式底座写入、公司匹配、Git提交和插件安装均为独立授权；一个批准不得扩张到另一个阶段。
- 不搜索具体客户，不补造事实，不改专业技能结论，不覆盖业务员字段，不发送，不创建自动发送配置。

## 写入合同

查看、解释、评估、诊断和“告诉我下一步”都不授权写入。创建公司结构、记录业务决定、安装插件、传输文件和外部发送是不同权限。

业务员给出自然语言决定后，先定位稳定编号并显示工作表、字段、旧值和新值。只有明确授权后才能写入；写入前核对预期哈希，写入后重新打开并核对目标值。所有输出中的 `workbook_status` 只能是 `未写入`、`待授权` 或 `已重开验证`。

## 输出

先用中文给出：

1. 当前结论；
2. `first_incomplete_stage` 及直接证据；
3. 唯一下一动作、阶段所有者和停止点；
4. 已执行、待授权、被阻断和仍为 `UNVERIFIED` 的内容。

静态检查只能证明文件合同存在，不能证明第二家公司冷启动、跨账号复刻、真实候选质量、业务易用性或安装后自动触发有效。

需要交给同事执行时，同时给出 `operator_task_card`：为什么现在做、谁负责、唯一任务、批准输入、预期产物、验收条件、停止点和禁止动作。不能只让同事“看表自己处理”。
