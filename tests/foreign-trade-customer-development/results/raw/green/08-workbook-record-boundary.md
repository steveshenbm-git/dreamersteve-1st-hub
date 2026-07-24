## 工作簿待写入包

写入状态：未写入。未提供指定 `.xlsx` 文件、工作表定位信息或本次写入授权；不得声称已更新。

最终建议：仅将“推荐邮件”作为一条正式触达草稿记录；三套内部策略不写入正式触达历史。所有记录保持“草稿/待业务员决定”，不得标记为“计划触达”或“实际发送”。

来源与日期：案例文本《08 Workbook Record Boundary》；观察日期：2026-07-24；证据状态：单一来源待验证。

| 目标表 | 操作 | 稳定编号 | 拟写字段 | 值/处理 |
|---|---|---|---|---|
| 客户总览 | 按 `customer_id` 更新 | 待提供 | `next_action` | 待业务员审核推荐邮件并决定是否批准发送 |
| 客户总览 | 按 `customer_id` 更新 | 待提供 | `next_action_date` | 留空；未提供可确认日期 |
| 客户总览 | 按 `customer_id` 更新 | 待提供 | `last_touch_date` | 留空；尚未实际发送 |
| 触达记录 | 新增 | 待分配 `touch_id` | `customer_id`、`contact_id` | 待提供/按既有稳定编号关联 |
| 触达记录 | 新增 | 待分配 `touch_id` | `channel` | 邮件（如原草稿明确为邮件） |
| 触达记录 | 新增 | 待分配 `touch_id` | `touch_stage` | 首封开发邮件（如原草稿属于首封） |
| 触达记录 | 新增 | 待分配 `touch_id` | `content_status` | 草稿 |
| 触达记录 | 新增 | 待分配 `touch_id` | `planned_date` | 填入案例中已有的计划发送日期；未提供具体日期则留空 |
| 触达记录 | 新增 | 待分配 `touch_id` | `actual_sent_at`、`actual_content_or_local_reference` | 留空；不得倒填实发 |
| 触达记录 | 新增 | 待分配 `touch_id` | `response_state`、`response_at` | 留空 |
| 触达记录 | 新增 | 待分配 `touch_id` | `next_action` | 待业务员批准或修改草稿 |
| 触达记录 | 新增 | 待分配 `touch_id` | `salesperson_approved` | 留空/未批准 |

业务员仍需决定：确认客户与联系人稳定编号、确认邮件阶段与渠道、审核草稿、决定是否批准发送。
