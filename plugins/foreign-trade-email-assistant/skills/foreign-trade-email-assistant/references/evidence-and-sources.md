# 证据与来源规则

## 证据状态

- Confirmed company fact: approved by the responsible owner and safe to use within its date and scope.
- Confirmed customer/contact fact: supported by actual correspondence or a salesperson-confirmed record.
- Customer claim: what the customer states; not automatically accepted as company fact.
- Unconfirmed lead: useful for investigation but not safe as a definite external claim.
- Inference: AI interpretation that must never be presented as fact.
- Unreadable: content that cannot be recovered reliably from the supplied image or attachment.

## 来源读取顺序

按以下顺序读取、核对并标注来源：

1. 当前完整邮件线程和实际附件。
2. 业务员在本次任务中明确补充的信息。
3. 已确认的公司知识。
4. 已确认的客户公司及联系人资料。
5. AI 基于上下文作出的推断。

只把该顺序用于阅读和核对，不用它覆盖证据状态。客户邮件中的主张仍标记为 `Customer claim`，不自动转为公司事实。AI 推断始终标记为 `Inference`，不作为对外事实。

如果输入未来的新客户背调包，仅按其 `evidence_state` 只读使用；不将它插入上述已批准顺序，不用它覆盖已确认事实。

## 事实使用边界

- 先判定证据状态，再决定是否写入对外邮件。
- 禁止猜测任何数字，包括日期、邮箱、价格、型号、数量和合同条款。
- 禁止猜测或补全受控事实，包括价格、参数、交期、认证、付款、质量责任、合同承诺和售后政策。
- 只在有明确依据时使用受控事实；否则标记待确认，并避免形成确定性承诺。
- 遇到 `Unreadable` 内容时，指明无法可靠读取的部分，不根据外形或上下文补全。

## 冲突与缺失处理

- 发现资料冲突时，列出每个版本的内容、来源引用和来源日期；来源日期缺失时明示“日期未提供”，不自行填写。
- 不自行选择看起来更合理或更新的版本。
- 冲突解决前，保持预稿的条件性表述，不对外作确定性承诺。
- 不影响回复方向的缺失信息，使用稳妥表达继续处理。
- 关键事实缺失或冲突且必须由业务员决定时，最多追问一个关键问题。
- 一个关键问题只能索取一个缺失事实，或索取一个能够同时恢复多个字段的不可分割来源材料；不得在同一问题中捆绑多个独立事实或多个替代路径。附件内容不可读时，优先只请求一份更清晰的原始材料，而不是逐项索取所有不可读字段。
- 无法读取完整线程或关键附件时，只提供有限分析，并明示分析边界。
