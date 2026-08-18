# 路由、交接与客户状态

## 协调器入口与返回

`foreign-trade-workflow-director` 可提交 `specialist_handoff_packet`，但它不能代替本技能需要的 `outreach_handoff_packet`、完整线程、实际发送历史或风险事实。协调器包必须带 `handoff_id`、`company_id`、业务问题、`source_record_id`、`source_packet_reference`、`evidence_reference`、允许写入范围和禁止动作；缺少专业输入时仍返回原所有者补齐，不得由协调器叙述替代证据。

返回协调器的 `specialist_return_packet` 只允许投影到 `salesperson_workbench` 的客户跟进、沟通草稿或异常风险页。结果必须分开保存草稿状态、业务员审核、实际发送、实际回复和风险门。不得把 `业务员批准` 解释为实际发送，也不得因下一步日期到期自动写成触达事实。

## `outreach_handoff_packet` 接受条件

`cold_outreach` 只接受业务员已选定客户并明确要求准备触达的交接包。包中必须可读到客户身份、至少一条直接适配证据、已批准产品引用、允许和禁止表述、联系人权限、`outreach_scope`、风险状态和本次业务员请求。

- `outreach_scope = limited`：只依据初查证据准备有限首封；不得补做完整背调或改变推品。
- `outreach_scope = complete`：可使用完整背调已批准内容；仍不得把未确认问题写成事实。
- 缺少核心字段：输出 `development_return_packet`，逐项说明所缺事实；不得用互联网搜索、经验或客户画像补齐。

## `customer_operations_handoff` 接受条件

开发技能发现回复或疑似回复时，`reply_communication` 必须接受同名 `customer_operations_handoff`，不得要求先回到冷开发路线。交接包至少包含：

```text
customer_operations_handoff:
  customer_id: <稳定编号或待创建>
  trigger_channel: <触发渠道>
  trigger_touch_id: <对应实发触达编号或缺口>
  response_reference: <当前保存的入站原文或本地引用>
  sender_identity_status: <发件人、邮件头、主体关系的核验状态与缺口>
  confirmed_context: <已确认客户、产品和项目事实及证据引用>
  actual_send_history: <可追溯实发记录；没有则明示缺口>
  open_questions: <未解决问题>
  risk_gate_status: <当前风险状态与依据>
  target_skill: foreign-trade-customer-operations
  salesperson_request: <本次明确要求或待确认>
```

当前入站内容已足以建立回复任务时，立即进入 `reply_communication`；发件人身份、邮件头或对应实发历史未核验，只影响证据状态，不得延迟交接或继续生成冷开发草稿。缺少会实质改变回复立场的字段时，只输出 `reply_return_packet`，列出缺失字段、影响和一项最小补充请求；不得启动客户搜索、补做背调或把疑似回复记为已核验实际回复。

## 状态优先级

按以下顺序判定：回复或疑似回复 → 风险暂停 → 拒绝/停止 → 持续退信 → 开发交接范围 → 到期跟进 → 普通经营建议。

回复优先于任何计划日期。收到或疑似收到回复时，切换 `reply_communication`，停止新的冷开发触达草稿；未核验的来信保留身份、邮件头、主体关系和历史实发缺口，不得写成实际回复或触达成功。

## 业务员权限

AI可以给出一个推荐渠道、一个候选内容和一个建议日期；业务员决定是否使用。管理层、上级、自动化计划或日期到期不等于业务员对发送、渠道、客户状态、受限联系人或工作簿业务字段的批准。

## `account_operation` 输出

`account_operation` 只处理已有客户的内部下一步建议，不自行生成外部草稿。输出当前已确认状态、最近一次实际互动、可追溯项目或关系信号、一个推荐动作、主要风险与缺口，以及业务员仍需决定的客户状态、价值、优先级、产品、渠道和日期。若任务实际要求对外文本，按可观察状态重新路由到 `cold_outreach`、`unanswered_follow_up` 或 `reply_communication`，不得在一个输出中并行执行多个路由。
