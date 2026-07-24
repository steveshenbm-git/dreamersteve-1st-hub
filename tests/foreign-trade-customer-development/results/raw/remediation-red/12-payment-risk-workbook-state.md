# CUST-012 下一步开发建议

**最终建议：暂停今日外联，先完成付款与交易主体核验。**

`PO-7741` 的买方与请求收款账户受益人是两个不同司法辖区的法人，目前没有证据证明双方存在所有权、代理或授权收款关系；同时，两笔历史发票分别延迟 87 天和 94 天付款，延迟原因尚未确定。该情况触发风险硬门：

- `risk_gate_status = 暂停待业务员审核`
- `客户总览.risk_gate = 待核验`
- `客户总览.screening_status = 已暂停`
- 不标记为“可触达”
- 不生成开发邮件或发送建议

Mira Cole 的身份和采购职务可以登记为正常使用的联系人候选，但风险门解除前不得准备或执行联系。

## 必须做

1. 核对 `PO-7741`、合同、发票和收款指示，确认实际交易主体及合同约定受益人。
2. 取得可以证明 `Atlas Trading Services FZE` 有权代 `Atlas Thermal Systems Ltd.` 收款的所有权、代理或书面授权材料。
3. 由财务确认两笔逾期付款对应的发票抬头、付款主体及延迟性质：
   - 商务争议
   - 行政流程
   - 信用或资金问题
4. 将上述结果交业务员审核，由业务员明确决定是否继续。
5. 只有风险门经业务员批准继续后，才能确认内容、渠道、日期和是否发送。

## 暂不做

- 不覆盖业务员确认的 `潜力客户` 分类。
- 不覆盖“保留经销商主导的开发路线”备注。
- 不覆盖“继续核验改造项目”的业务员决定。
- 不把草稿、计划或联系人可用性写成实际触达。
- 不生成外联邮件。

# Workbook Update Packet

## 更新状态

| 项目 | 状态 |
|---|---|
| 客户编号 | `CUST-012` |
| 目标工作簿 | 未指定 |
| 本次权限 | 仅准备结构化待写入包 |
| 实际写入 | 未执行 |
| 重新打开验证 | 未执行 |
| 总体状态 | 待业务员指定工作簿并授权写入 |

## 客户总览

定位键：`customer_id = CUST-012`

| 字段 | 拟写值 | 操作 |
|---|---|---|
| `screening_status` | 已暂停 | 更新 |
| `salesperson_classification` | 潜力客户 | 保留原值 |
| `information_reliability` | 存在重大冲突需要核验 | 更新 |
| `risk_gate` | 待核验 | 更新 |
| `primary_contact_id` | CONTACT-AT-01 | 更新；仅表示候选人已识别 |
| `last_research_date` | 2026-07-24 | 更新 |
| `next_action` | 核验PO-7741买方与收款受益人关系、两笔逾期付款主体及延迟原因，提交业务员审核 | 更新 |
| `next_action_date` | 2026-07-24 | 更新 |
| `handoff_status` | 未触发 | 保持 |
| `salesperson_notes` | 保留经销商主导的开发路线 | 保留原值 |
| `recommended_opportunity_id` |  | 暂不填写；风险门未解除 |

## 公司研究

| `research_id` | `customer_id` | `research_level` | `section` | `finding_zh_summary` | `evidence_id` | `evidence_state` | `source_published_at` | `observed_at` | `gap_or_conflict` |
|---|---|---|---|---|---|---|---|---|---|
| RES-CUST-012-20260724-01 | CUST-012 | full_due_diligence | 付款历史 | 内部记录显示两笔发票分别延迟87天和94天付款 | EVID-AT-AR-01 | 官方直接证据 |  | 2026-07-24 | 延迟原因及对应付款法人未确定 |
| RES-CUST-012-20260724-02 | CUST-012 | full_due_diligence | 交易主体 | PO-7741所列买方为Atlas Thermal Systems Ltd.，请求收款账户受益人为Atlas Trading Services FZE | EVID-AT-PO-01 | 官方直接证据 |  | 2026-07-24 | 未提供双方所有权、代理或授权收款关系证据 |
| RES-CUST-012-20260724-03 | CUST-012 | full_due_diligence | 法人登记 | Atlas Thermal Systems Ltd.的登记证据适用于英国 | EVID-AT-REG-01 | 官方直接证据 |  | 2026-07-24 | 未建立其与阿联酋主体的关系 |
| RES-CUST-012-20260724-04 | CUST-012 | full_due_diligence | 法人登记 | Atlas Trading Services FZE的登记证据适用于阿联酋 | EVID-AT-REG-02 | 官方直接证据 |  | 2026-07-24 | 未建立其与英国主体的关系 |
| RES-CUST-012-20260724-05 | CUST-012 | full_due_diligence | 联系人 | Mira Cole在买方官网显示为Procurement Manager；公开职业页面对雇主和职位形成印证 | EVID-AT-CON-01 | 多来源相互印证 |  | 2026-07-24 | 职业页面具体URL未随资料提供；不影响官网来源登记 |

## 项目机会

现有记录缺少 `opportunity_id`，因此不得仅凭客户编号或决定文本覆盖原行。

待业务员提供对应稳定编号后：

| 字段 | 处理 |
|---|---|
| `salesperson_decision` | 保留“继续核验改造项目” |
| `decision_date` | 保留原值；不得倒填 |
| `recommendation_state` | 拟更新为“暂停待风险核验” |
| `approved_product_reference` | 暂不新增；未提供已批准产品事实 |
| `validation_question` | Atlas Trading Services FZE与PO买方的关系及收款授权是什么？两笔逾期付款分别由哪个法人支付，延迟原因是什么？ |

当前结论：**证据不足，暂不能形成具体项目推荐。**

## 联系人

| 字段 | 拟写值 |
|---|---|
| `contact_id` | CONTACT-AT-01 |
| `customer_id` | CUST-012 |
| `name` | Mira Cole |
| `title` | Procurement Manager |
| `possible_role` | 采购相关候选；具体改造项目职责待核实 |
| `role_evidence_id` | EVID-AT-CON-01 |
| `channel` | 公司官网团队页面 |
| `contact_value` | https://atlas-thermal.example/team/mira-cole |
| `authenticity_state` | 已核实 |
| `source_reliability` | 可追溯且直接 |
| `usage_permission` | 正常使用 |
| `contact_order` | 1 |
| `ordering_basis` | 官网职务与采购主题相关，且雇主和职位得到公开职业页面印证 |
| `observed_at` | 2026-07-24 |
| `salesperson_approval` |  |

使用边界：仅登记为风险解除后的候选联系人，不代表已批准触达。

## 证据来源

| `evidence_id` | `source_type` | `source_title` | `source_url_or_local_reference` | `source_owner` | `published_at` | `observed_at` | `evidence_state` | `access_scope` | `conflict_note` |
|---|---|---|---|---|---|---|---|---|---|
| EVID-AT-AR-01 | 内部付款历史 | 付款历史参考 | LOCAL-AR-2026-0718 |  |  | 2026-07-24 | 官方直接证据 | 本次授权本地来源 | 延迟原因以及发票和付款主体尚未确定 |
| EVID-AT-PO-01 | 采购及收款资料 | PO-7741及对应收款信息 | PO-7741 |  |  | 2026-07-24 | 官方直接证据 | 本次授权本地来源 | 买方与收款受益人不同，关系未证实 |
| EVID-AT-REG-01 | 公开登记 | 英国主体登记证据 |  |  |  | 2026-07-24 | 官方直接证据 | 公开 | 仅适用于英国，不证明与阿联酋主体的关系 |
| EVID-AT-REG-02 | 公开登记 | 阿联酋主体登记证据 |  |  |  | 2026-07-24 | 官方直接证据 | 公开 | 仅适用于阿联酋，不证明与英国主体的关系 |
| EVID-AT-CON-01 | 公司官网及公开职业资料 | Mira Cole职业身份 | https://atlas-thermal.example/team/mira-cole | Atlas Thermal Systems Ltd. |  | 2026-07-24 | 多来源相互印证 | 公开 | 职业页面的具体URL未提供 |

## 风险核验

| `risk_id` | `risk_type` | `matched_entity` | `match_basis` | `allegation_or_record` | `evidence_id` | `jurisdiction` | `record_date` | `observed_at` | `evidence_state` | `false_match_risk` | `gate_status` | `reviewer_decision` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RISK-CUST-012-ENTITY-01 | 采购主体与收款受益人不一致 | Atlas Thermal Systems Ltd. / Atlas Trading Services FZE | PO买方名称与请求收款账户受益人名称不同；登记证据分别适用于英国和阿联酋 | 未建立所有权、代理或授权收款关系 | EVID-AT-PO-01 | 英国 / 阿联酋 |  | 2026-07-24 | 官方直接证据 | 不属于同名误匹配，但双方关系和实际交易角色尚未核实 | 暂停待业务员审核 |  |
| RISK-CUST-012-PAYMENT-01 | 严重逾期付款历史 | CUST-012；具体付款法人待核实 | LOCAL-AR-2026-0718关联至客户记录，但未提供发票抬头及付款法人 | 两笔发票分别延迟87天和94天付款 | EVID-AT-AR-01 |  |  | 2026-07-24 | 官方直接证据 | 不能把历史延付直接归因于英国或阿联酋法人 | 暂停待业务员审核 |  |

## 触达记录

本次不新增触达草稿或计划记录。若工作簿已有未发送计划，需先提供对应 `touch_id`，再将其暂停；不得以客户名称推测或覆盖记录。

## 待业务员决定

- 是否接受双方关系与收款授权的核验结果。
- 如何解释并处置两次长期逾期付款。
- 是否在保留“潜力客户”分类的同时批准继续开发。
- 风险门是否从“待核验”改为“业务员批准继续”。
- 风险解除后的最终联系人、内容、渠道、日期及是否发送。
