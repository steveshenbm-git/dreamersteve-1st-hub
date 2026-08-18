# 工作簿与自动化

## 后台记录与业务前台

客户开发工作簿中的触达、移交和风险记录是机器事实后台；`foreign-trade-workflow-director` 的六页 `salesperson_workbench` 只显示业务摘要和决策。业务前台中的草稿审核或下一步决定由协调器在字段级授权后记录，本技能通过稳定 `customer_id`、`touch_id`、草稿编号、`source_packet_reference` 和 `evidence_reference` 接收该决定。

本技能不得直接覆盖业务前台，也不得把业务前台的批准状态写成实际发送或回复。准备草稿时可向协调器返回 `workbench_update_packet` 建议；只有实际发送/收件证据进入后台后，才可返回新的真实状态投影。

## 草稿记录

自动或人工生成的沟通候选写入时使用：

```text
content_status = 草稿
draft_content_or_local_reference = <完整可审核草稿或本地引用>
draft_generated_at = <带 UTC 偏移的 ISO 8601 时间>
draft_for_touch_stage = <首封/第一次跟进/第二次跟进/事件/定期等>
automation_run_id = <自动化运行编号；人工草稿留空>
actual_sent_at = 空
actual_content_or_local_reference = 空
response_at = 空
```

草稿绝不等于已批准、计划、实际发送或实际回复。只有实际发送事实存在后才写 `actual_sent_at` 和实发内容；任何回复优先停止新草稿。

## 10:00 自动化（未激活配置）

未来本地自动化每个工作日 10:00、Asia/Shanghai 检查一次。它只选择同时满足以下条件的记录：到期或逾期、存在实际发送基准、未回复、未停止、风险门未暂停、没有同一客户/触达阶段/到期节点的未审核草稿、且本轮存在新价值或待验证问题。

自动化必须生成一天一条审核任务，而非每个客户一条弹窗；它不得自动发送或重写客户分类、业务员字段。电脑离线、工作簿被占用、结构不匹配或重新打开验证失败时，不写入并在审核任务中报告失败。节假日只有在本地配置提供日历时才跳过；否则按周一至周五处理。下一次成功运行要包含已逾期但尚未处理的记录。

在执行资格判断前，未来本地运行器必须先把共享工作簿规范化为只读 `due_record`，不得要求工作簿新增一套重复的自动化表：

```text
due_record:
  customer_id: <客户总览.customer_id>
  touch_stage: <依据上一条实发触达和客户总览.next_action确定>
  recommended_next_date: <客户总览.next_action_date；必须能由实发基准复算>
  date_basis_touch_id: <触达记录.touch_id>
  date_basis_actual_sent_at: <对应触达记录.actual_sent_at>
  risk_gate: <客户总览.risk_gate>
  response_state: <该客户最新触达记录.response_state>
  has_unreviewed_draft: <同一客户、阶段、到期节点是否已有 content_status = 草稿>
  stop_requested: <拒绝、停止要求、持续退信、关闭或回复是否存在>
  new_value_or_question: <从项目机会.validation_question、已保存新证据或当前可读待验证问题取得>
```

运行器必须按 `customer_id` 和稳定 `touch_id` 关联，重新计算第 5 个工作日、第 7 个工作日或 10 个自然日加周末顺延；工作簿中的日期与复算结果冲突时，不生成草稿，进入当日审核任务的错误区。`new_value_or_question` 只能来自当前可读记录；没有新价值或待验证问题时，该客户仍可显示为到期，但不得生成占位草稿。

## 写入授权

自动化只有在业务员指定本地工作簿，并明确提供“只写草稿字段”的长期授权后，才可写入。授权不覆盖 `actual_sent_at`、实发内容、回复、客户分类、风险门、业务员决定、备注或日期。没有授权时只输出 `draft_write_packet`，状态为 `待授权`。

## 正式归档与数据隔离

只有实际收件、实际发件及实际附件可进入正式客户邮件档案。AI 分析、草稿、修改原因和版本差异属于内部工作材料，不得标记为正式邮件或已发送。实际发送或实际回复只有在提供可追溯内容、时间和关联客户记录后才可写入。

公司知识、客户资料、联系人、工作簿数据、实际通信、授权配置和自动化运行记录都保留在用户指定的本地公司目录；不同公司使用不同稳定 `company_id` 和数据根目录，不得跨公司读取、引用或写入业务事实。公开插件只包含空白模板、字段合同和通用方法。
