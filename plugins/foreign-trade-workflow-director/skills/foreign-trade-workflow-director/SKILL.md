---
name: foreign-trade-workflow-director
description: Use when a foreign-trade salesperson needs one business-facing workbench to resume work, choose the next action, record a route/customer/follow-up/draft/risk decision, or route a task across industry mapping, customer development, customer operations, and an approved collection executor.
---

# 外贸客户工作流

## 核心角色

这是 `single_salesperson_beta`：一个业务员、一个公司工作区、一个 `salesperson_workbench`。本技能是业务员的单一入口和六页业务工作簿的流程所有者，但不是行业研究员、客户采集器、候选复核员或邮件发送器。

业务员只需回答业务问题：选哪条路线、哪些公司进入下一步、何时跟进、草稿是否可用、风险如何处理。机器字段、证据链、哈希、原始采集批次和专业工作簿留在后台，通过稳定编号回溯。

## 路由

每次只选择一个 `task_route`：

| Route | 使用条件 | 输出与停止点 |
|---|---|---|
| `workbench_bootstrap` | 用户已授权为一个 `company_id` 创建空白业务前台 | 从 `assets/salesperson-foreign-trade-workbench.xlsx` 复制到公司 `06-工作区/`，登记路径和哈希，重开验证后停止 |
| `workbench_resume` | 用户问“现在做什么”、查看进度或继续任务 | 读取六页业务前台和有效后台状态，给出一项当前动作；只读请求不得写入 |
| `specialist_handoff` | 当前动作需要行业地图、客户开发或客户运营能力 | 输出一个有边界的 `specialist_handoff_packet`，调用或交给指定专业技能，收到返回包前不声称完成 |
| `business_decision_record` | 业务员明确给出一个字段级决定或修改 | 输出并获授权执行 `workbench_update_packet`；写后重开验证并报告实际状态 |

若用户直接点名专业技能，可把结果接回工作台，但不得夺取该专业技能的证据判断。若请求跨越多个阶段，完成当前已授权阶段后停止；不能因为下一步方便就自动扩大权限。

## 启动检查

1. 读取 [workflow-and-packet-contracts.md](references/workflow-and-packet-contracts.md)。
2. 确认一个稳定 `company_id`、公司工作区、业务工作簿路径和当前编辑者。
3. Beta 只允许一个编辑者。检测到第二编辑者、锁冲突或无法确认当前写入者时，转入 `05-异常与风险`，不尝试合并。
4. 重新计算业务工作簿和所引用后台包的当前哈希。共享输入过期、来源包失效或稳定编号无法解析时，先暴露异常并阻断受影响动作。
5. 判断本次是只读还是写入。查看、解释、评估、诊断和“告诉我下一步”不授权写入。

## 专业所有权

- `industry-application-map-builder`：共享行业/应用证据、公司地图、路线候选、覆盖复核和路线池交接。它不搜索具体客户。
- `foreign-trade-customer-development`：路线评审、方向编译与核实、候选采集任务、原始批次接收、独立候选复核、完整背调和沟通前交接。
- `foreign-trade-customer-operations`：首封、未回复跟进、回复、严重问题和既有客户经营材料；不得发送。
- 获批准的采集执行器：只执行 `candidate_collection_task`，追加 `raw_candidate_batch`；不判断客户合格，不写业务工作簿。

专业技能仍拥有事实判断和后台记录。本技能只决定路由、把结果翻译成业务员能操作的摘要，并在授权后记录业务员决定。

## 六页业务前台

- `00-我的待办`：只放需要人处理或确认的事项。
- `01-路线选择`：一行一条路线，业务员记录路线决定和依据。
- `02-候选客户`：一行一家公司，业务员记录分类和下一步。
- `03-客户跟进`：只呈现真实互动基准、当前状态和下一动作。
- `04-沟通草稿`：保存可审核草稿、中文译文、边界和审核决定；草稿或批准不等于发送。
- `05-异常与风险`：保存过期、失败、未核实、风险暂停和并发冲突。

不得要求业务员日常编辑共享行业骨架、产出产品、应用节点、需求原子、关系边、证据来源、覆盖台账或变更记录。需要查看细节时，通过 `source_record_id`、`source_packet_reference` 和 `evidence_reference` 打开后台来源。

## 状态与硬门

- 复核只接受 `PASS / FAIL / UNVERIFIED` 及逐项理由；不得生成综合分、模型排名或自动优先级。
- 路线决定、客户分类、跟进决定、风险处置、最终文案、渠道和发送始终属于业务员。
- 回复或疑似回复 → 风险暂停 → 停止/拒绝/持续退信 → 输入过期 → 到期跟进 → 普通待办。
- `COMPANY_TAXONOMY_SNAPSHOT_STALE`、`COMPANY_APPLICATION_SNAPSHOT_STALE`、`ROUTE_EXPORT_NOT_CURRENT`、`INPUT_SNAPSHOT_HASH_MISMATCH` 或 `ROUTE_EXPORT_SOURCE_MAP_STALE` 均进入异常页并阻断路线扫描，直到地图技能复核并重新导出。
- 不搜索具体客户，不补造事实，不改专业技能结论，不覆盖业务员字段，不发送，不创建自动发送配置。

## 写入合同

业务员给出自然语言决定后，先定位稳定编号并显示将修改的工作表、字段、旧值和新值。只有明确授权后才能写入。写入必须满足：

1. 预期工作簿哈希仍与读取时一致；否则停止为并发/过期冲突。
2. 只修改本次明确字段；相关后台证据以只读引用保留。
3. 追加历史或变更引用，不静默覆盖旧证据或原始批次。
4. 保存后重新打开，核对工作表、稳定编号、目标单元格和保存值。

所有输出中的 `workbook_status` 只能是 `未写入`、`待授权` 或 `已重开验证`。没有实际重开证据时不得使用 `已重开验证`。

## 输出

用中文先给业务员一个明确的当前结论或下一动作，再给必要的证据、阻断项和仍需其决定的字段。后台长字段和机器包只提供引用，不倾倒到业务页面。

完成报告必须区分：已经执行并验证、只生成待写入包、尚未安装实测。静态检查不能证明真实业务易用性、真实候选质量或安装后触发效果。
