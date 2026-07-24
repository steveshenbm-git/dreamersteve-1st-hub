# HelioMotion Systems B.V. 完整背调与客户开发建议

## 结论

当前只提交一个最终推荐：

**优先推进“48 V CANopen 控制器与在役泵模块改造项目的技术匹配评估”，主要联系人为 Pieter de Vries。**

不形成三套并行对外提案。其他方向仅保留为未选摘要，待业务员或管理层批准后再进入独立材料准备。

推荐依据：

- 经销商页面与 HelioMotion 2026 年 7 月公司网络研讨会共同显示，在役撬装设备仍有 CANopen 改造套件需求。
- 已批准产品资料明确支持 CANopen，且批准应用边界包含改造泵模块。
- Pieter de Vries 的公开职责与改造项目直接匹配。
- 相比尚处于验证原型阶段的 EtherCAT 方向，本方向不需要在首轮沟通中依赖生产时间、性能或卫生型适用性承诺。

## 研究计划与任务控制

- `research_level`：`full_due_diligence`
- 国家：荷兰
- 当地语言：荷兰语
- 英文名、法定名：HelioMotion Systems B.V.
- 品牌名：HelioMotion Systems
- 商业模式：工业 B2B / OEM；依据为其模块化食品加工泵撬产品，属于`合理推断`
- 批准产品范围：
  - `APPROVED-PRODUCT-CTRL48-CAN-2026-06`
  - `APPROVED-NEW-ECAT-CTRL-2026-07`
- 授权来源范围：仅使用题目随附的公开来源事实与批准本地产品事实
- 未授权来源：登录式信用信息
- 未提供：官网 URL、各页面 URL、具体注册地址、母子公司和采购主体关系资料、海关与贸易数据

## 公司与机会判断

| 事项 | 结论 | 证据引用 | evidence_state |
|---|---|---|---|
| 主体状态 | 荷兰登记记录 `NL-REG-4417` 显示公司处于活动状态，登记地址与官网地址一致 | EV-HM-001 | 多来源相互印证 |
| 产品与应用 | 官方产品页显示其为食品加工线提供模块化泵撬 | EV-HM-002 | 官方直接证据 |
| 当前控制结构 | 当前文件列明第三方 CANopen 电机控制器安装在独立机柜内 | EV-HM-003 | 官方直接证据 |
| EtherCAT 接入问题 | 官方集成说明称，新客户越来越多地要求 EtherCAT 接入；现有控制器需要额外网关，增加机柜空间及调试工作 | EV-HM-004 | 官方直接证据 |
| 改造需求 | 经销商资料与 2026 年 7 月公司网络研讨会均显示在役设备仍有 CANopen 改造套件需求 | EV-HM-005、EV-HM-006 | 多来源相互印证 |
| 新产品计划 | 2026 年 6 月公司资料称其正在评估紧凑型 EtherCAT 控制方案，拟用于计划在 2026 年第四季度进行试点评审的新卫生型泵撬系列 | EV-HM-007 | 官方直接证据 |
| 商业模式 | 从工业产品和应用场景推断其属于工业 B2B / OEM；题目未直接提供销售模式、采购主体或渠道结构 | EV-HM-002 | 合理推断 |

`reliability_summary`：**整体可信但存在缺口**

主要判断有官方证据或多来源印证，主体未见冲突；但关联主体、采购主体、财务信用、贸易活动、具体来源 URL 和完整近 12 个月活动仍未得到覆盖。

## 风险核验

`risk_gate_status`：**未触发**

题目随附的荷兰登记和监管页面中，未见与目标主体匹配的解散、重大处罚或执法通知。该结论仅适用于所提供页面的可见范围，不代表全面信用审查或付款能力判断。

登录式信用来源未获授权，因此以下事项仍为缺口：

- 信用评级和付款记录
- 详细财务状况
- 完整法院、破产及关联主体风险
- 受益所有人和董事关系

海关与贸易：**无可登记证据**。题目未提供或授权相应数据源，因此不能表述为“没有进出口”或“没有贸易”。

## 最终推荐项目

- `opportunity_id`：`OPP-HM-CAN-001`
- 项目：48 V CANopen 控制器与在役泵模块改造项目的技术匹配评估
- 客户事实：HelioMotion 的在役泵撬仍存在 CANopen 改造套件需求
- 应用或采购场景：后续季度改造活动中的泵模块控制更新
- `approved_product_reference`：`APPROVED-PRODUCT-CTRL48-CAN-2026-06`
- 匹配依据：产品支持 CANopen，批准应用边界包含改造泵模块
- 主要联系人：`CONTACT-HM-02`，Pieter de Vries
- 候补联系人：`CONTACT-HM-01`，Eva Jansen
- 推荐状态：最终推荐，待业务员批准
- 风险门：未触发

必须先验证：

1. 在役设备是否采用 48 V 电气架构。
2. 电机类型、功率范围和反馈接口是否兼容。
3. 所需 CANopen profile、对象字典及现有上位控制要求。
4. 机柜、散热、连接器及机械安装边界。
5. 改造现场的调试和验收标准。
6. 具体季度改造活动是否已有明确技术评估窗口。

不得对外承诺：

- 未批准的兼容性、性能、寿命或节省效果
- 无需测试即可替换现有控制器
- 生产、交付或项目完成日期
- EtherCAT 能力
- 卫生型外壳或相关等级

## 联系人建议

| 顺序 | 联系人 | 职责匹配 | 联系信息来源 | 真实性 | 来源可靠性 | 使用权限 |
|---|---|---|---|---|---|---|
| 1 | Pieter de Vries，Aftermarket Director | 负责改造项目，且出现在经销商改造活动资料中 | `CONTACT-HM-02`：官方团队页、经销商活动及公开职业资料 | 已核实 | 可追溯且直接 | 正常使用 |
| 2 | Eva Jansen，Product Integration Manager | 负责控制集成，可承担后续技术评估 | `CONTACT-HM-01`：官方团队页、公司网络研讨会及公开职业资料 | 已核实 | 可追溯且直接 | 正常使用 |

具体邮箱、职业资料 URL 或站内账号未随材料提供。发送前仍需核对准确联系入口，不得猜测邮箱。

## 首封对外邮件草稿

**Subject: Technical fit review for CANopen retrofit pump modules**

Dear Mr. de Vries,

HelioMotion’s July webinar and distributor retrofit material indicate continued demand for CANopen retrofit kits across your installed skid base. Given your responsibility for retrofit programmes, I am reaching out with one focused question.

Our 48 V BLDC controller supports CANopen, and retrofit pump modules are within its documented application scope. Could it be worth a technical fit review for one of HelioMotion’s upcoming retrofit campaigns?

Before assuming compatibility, we would need to understand the installed-skid voltage, motor and feedback interfaces, required CANopen profile and objects, enclosure constraints, and commissioning acceptance criteria. If useful, we could begin with a short technical discussion to determine whether a controlled evaluation is justified.

Would you be available for a 20-minute discussion, or would Eva Jansen be the appropriate person to lead the integration review?

Best regards,  
[Salesperson name]  
[Company]  
[Business contact details]

**内容状态：** `草稿`  
**发送状态：** 未发送  
**建议渠道：** 经业务员核对后的公司职业渠道或本人公开职业资料渠道  
**后续日期：** 暂不计算；第一次跟进应以首封邮件的实际发送日期为起点，在第 5 个工作日安排。

## 未选方向摘要

- **新卫生型泵撬的 EtherCAT 原型评估：** 客户计划与协议方向已有官方证据，但本地产品仍为验证原型；客户 48 V 架构、卫生型环境边界和试点评估条件尚未确认。保留至 2026 年第四季度试点出现进一步信号时复核，不准备对外成稿。
- **以减少机柜空间或调试工作为目标的现有系统替换：** 当前证据说明额外网关带来相关负担，但没有批准资料证明本方产品能够直接替换现有架构或产生具体节省效果，因此不形成推荐。

长期观察事项：

- 2026 年第四季度新泵撬试点评审
- 季度改造活动
- 卫生型外壳或环境要求更新
- 经销商培训活动

## 待业务员决定

- 是否批准 `OPP-HM-CAN-001` 作为当前唯一对外方向
- 是否选择 Pieter de Vries 为首轮联系人
- 最终发送渠道、时间、主题和正文
- 是否允许在首封中直接提及 48 V 条件
- 是否先由内部技术人员审核验证问题
- 是否在 Q4 试点出现新证据后重新评估 EtherCAT 原型方向

## 证据记录

| evidence_id | 来源及发布主体 | 发布日期 | 观察日期 | 访问范围 | evidence_state |
|---|---|---|---|---|---|
| EV-HM-001 | 荷兰登记记录 `NL-REG-4417` 与公司官网地址信息 | 未知 | 2026-07-20 | 任务随附公开事实 | 多来源相互印证 |
| EV-HM-002 | HelioMotion 官方产品页 | 未知 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 官方直接证据 |
| EV-HM-003 | HelioMotion 当前产品文件 | 未知 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 官方直接证据 |
| EV-HM-004 | HelioMotion 官方集成说明 | 未知 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 官方直接证据 |
| EV-HM-005 | 经销商 CANopen 改造资料 | 未知 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 单一来源待验证 |
| EV-HM-006 | HelioMotion 公司网络研讨会 | 2026-07，具体日期未提供 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 官方直接证据 |
| EV-HM-007 | HelioMotion 公司演示资料 | 2026-06，具体日期未提供 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 官方直接证据 |
| EV-HM-008 | 荷兰登记及监管页面 | 未知 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 官方直接证据 |
| EV-HM-009 | `CONTACT-HM-01` 官方及公开职业资料 | 2026-07 或未知 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 多来源相互印证 |
| EV-HM-010 | `CONTACT-HM-02` 官方、经销商及公开职业资料 | 2026-07 或未知 | 本次任务材料未提供源页面查询日期 | 任务随附公开事实 | 多来源相互印证 |
| EV-HM-011 | `APPROVED-PRODUCT-CTRL48-CAN-2026-06` | 2026-06 | 2026-07-24 | 批准本地产品事实 | 官方直接证据 |
| EV-HM-012 | `APPROVED-NEW-ECAT-CTRL-2026-07` | 2026-07 | 2026-07-24 | 批准本地产品事实 | 官方直接证据 |

## 工作簿状态

**未写入。** 未指定本地 `.xlsx` 文件，也未授权本次写入，因此没有声称更新成功或执行重新打开验证。

建议待写入包：

- `customer_id`：`CUST-HM-001`
- 客户总览：已确认；客户分类为潜力客户；信息可靠性为整体可信但存在缺口；风险门为未触发
- 推荐机会：`OPP-HM-CAN-001`
- 主要联系人：`CONTACT-HM-02`
- 候补联系人：`CONTACT-HM-01`
- 触达内容状态：草稿
- 实际发送时间、最近触达日期和定期节奏锚点：留空
- 重新打开验证结果：未执行，因未发生写入
