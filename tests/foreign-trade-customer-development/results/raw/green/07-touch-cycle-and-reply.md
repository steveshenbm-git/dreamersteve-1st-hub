## 邮件助手移交包

- `handoff_id`：待生成
- `customer_id`：未提供
- `trigger_channel`：LinkedIn
- `trigger_touch_id`：未提供
- `target_skill`：`foreign-trade-email-assistant`
- `handoff_status`：触达已暂停
- `risk_gate_status`：未提供，待核对既有记录

**触发回复原文**

> not this quarter, contact me later.

**已知触达历史**

1. 初始邮件：已发送，日期与记录编号未提供。
2. 第一次邮件跟进：初始邮件后第 5 个工作日，已发送。
3. 第二次邮件跟进：第一次跟进后第 7 个工作日，已发送。
4. LinkedIn：已尝试；收到上述回复。
5. 返回邮件：案例仅说明已返回邮件，实际发送日期、内容和记录编号待从既有记录核对。

**当前处理状态**

- 因 LinkedIn 已收到真实回复，暂停所有原有及自动触达计划。
- 不准备“10 天后”的自动邮件，也不设定新的定期触达日期。
- “not this quarter, contact me later”表示当前季度暂不推进；具体可再次联系的时间、对方所指季度及业务议题均待邮件助手处理和业务员确认。

**邮件助手待处理事项**

- 根据回复准备合适的回应建议，确认是否需要询问可再次联系的具体月份或季度。
- 核对客户身份、既有邮件实发记录、返回邮件是否实际发送，以及风险门状态。
- 将当前开发状态交由业务员决定：明确商机、暂时无项目后进入长期触达、或关闭。

## 工作簿待写入包

- 目标文件/工作表：未指定，未写入。
- 操作类型：更新触达暂停状态；新增移交记录。
- 稳定编号：`customer_id`、`handoff_id`、`trigger_touch_id` 均待提供或从既有工作簿核对。

| 工作表 | 拟写字段 | 拟写值 |
|---|---|---|
| 客户总览 | handoff_status | 触达已暂停 |
| 客户总览 | next_action | 邮件助手处理 LinkedIn 回复；待业务员决定客户分类与后续节奏 |
| 客户总览 | next_action_date | 留空 |
| 触达记录 | content_status | 实际回复 |
| 触达记录 | channel | LinkedIn |
| 触达记录 | response_state | 已回复 |
| 触达记录 | response_at | 待补真实时间戳 |
| 触达记录 | actual_content_or_local_reference | `not this quarter, contact me later.` |
| 触达记录 | next_action | 移交邮件助手；暂停后续触达 |
| 移交记录 | trigger_channel | LinkedIn |
| 移交记录 | response_reference | `not this quarter, contact me later.` |
| 移交记录 | target_skill | foreign-trade-email-assistant |
| 移交记录 | handoff_status | 触达已暂停 |

**业务员仍需决定**

- 是否将该客户标记为“qualified opportunity / 明确商机”。
- 若后续保留，何时恢复触达及恢复前需补充的客户需求信息。
- 是否发送对当前 LinkedIn 回复的回应。
