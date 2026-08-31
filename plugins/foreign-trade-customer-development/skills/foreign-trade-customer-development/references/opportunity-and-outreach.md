# 项目推荐与沟通交接

## 产品事实门

只读取本地已批准产品、新品、参数、认证、应用边界和公开状态。缺少批准依据时标记待确认，不进入推荐或沟通交接。

每个匹配引用 `approved_product_reference`，并区分已批准事实、待验证问题和不得对外使用的缺口。业务员确认价值、优先级和最终产品表述。

## 项目证据链

客户事实 → 应用或采购场景 → 已批准产品或新品 → 匹配依据 → 待验证问题 → 适合验证的联系人。

每一环必须能追溯到证据编号或已批准本地引用。核心环节缺失时保留缺口，不用推断补链。联系人必须保留来源、真实性、来源可靠性和使用权限；风险硬门未解除时停止正常推荐。

## `project_recommendation`

`project_recommendation` 只允许在 `research_level = full_due_diligence` 且完整背调双门槛通过后生成；`candidate_scan`、方向发现和 `outreach_handoff` 都不得生成最终项目推荐。

内部比较三个**项目方案**的证据、产品匹配、联系人、差异化、风险和缺口，只交付一个最终推荐或明确“当前没有足够依据推荐具体项目”。这里的项目方案不是 `development_direction`；后者只定义企业筛选规则。

最终输出保留选中方案的项目证据链、主要风险、缺口、待验证问题、所需业务员决定，以及舍弃其他项目方案的一行原因。它不等于业务员批准，也不得直接变成对外邮件。

## `outreach_handoff_packet`

业务员已选择客户并明确要求准备触达时，客户开发技能只输出下列事实包，交给 `foreign-trade-customer-operations`：

```text
outreach_handoff_packet:
  company_id: <当前隔离公司编号>
  customer_id: <稳定编号或待创建>
  company_identity: <主体、品牌、网站、地区及证据>
  source_direction_id: <可选；没有则明确为空>
  product_fit: <已批准产品引用、客户场景、匹配依据、限制>
  allowed_claims: <可对外使用的已批准事实>
  prohibited_claims: <不得对外使用的缺口和未批准说法>
  contact_evidence: <联系人、职责、渠道、真实性、来源可靠性、使用权限>
  outreach_scope: <limited 或 complete>
  actual_send_history: <已有实际发送记录；没有则为空>
  risk_gate_status: <当前受控状态及依据>
  open_questions: <不得自行补全的问题>
  salesperson_request: <本次明确要求>
```

该业务包必须由机器生成的 `handoff_envelope_v1` 绑定后再交给接收技能。信封持有唯一 `handoff_id`、同一 `company_id`、`target_skill = foreign-trade-customer-operations`、`target_route = cold_outreach`、业务包相对引用/原始字节SHA-256和 `allowed_writes = []`。业务包本身不重复填写 `handoff_id`，也不通过信封获得发送、工作簿写入或扩大联系人权限。

`limited` 只允许客户经营与沟通技能依据已有初查和已批准事实准备有限首封；不得借此补做完整背调、增加产品结论或扩大联系权限。`complete` 代表完整背调双门槛已通过，但同样不授权发送。

## 交接后边界

首封开发邮件、两次邮件跟进、渠道切换、返回邮件、潜力客户 10 天节奏、事件触达、收到回复后的邮件处理与客户经营，均由 `foreign-trade-customer-operations` 负责。

本技能不再准备首封邮件、任何跟进或其他渠道材料；它只在客户事实、项目建议或沟通事实包需要补充时被重新明确启动。业务员始终拥有内容、渠道、日期和发送权。
