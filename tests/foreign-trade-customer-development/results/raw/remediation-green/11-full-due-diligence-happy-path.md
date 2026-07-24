# HelioMotion Systems B.V. 完整背调与单一开发建议

**研究截止日：** 2026-07-24  
**客户编号（本次内部临时稳定编号）：** `CUSTOMER-HM-001`  
**研究层级：** `full_due_diligence`  
**业务员前置确认：** 已确认 HelioMotion Systems B.V. 为潜力客户，并明确启动完整背调。  
**输出边界：** 本次只交付一个最终推荐和一套对应的对外材料。推荐仍属内部建议，不等于业务员批准、发送决定或客户优先级结论。

## 一、研究计划 / 任务控制

| 项目 | 本次范围 |
|---|---|
| 国家 / 地区 | 荷兰 |
| 当地语言 | 荷兰语；本次提供材料为英语事实摘要，未提供荷兰语原文 |
| 英文名 / 法定名 / 品牌名 | HelioMotion Systems B.V. / HelioMotion Systems B.V. / HelioMotion Systems |
| 商业模式假设 | 工业 B2B 的泵撬系统制造或集成业务；“制造或集成”仍是合理推断，未提供法定经营范围或制造设施证据 |
| 批准产品范围 | `APPROVED-PRODUCT-CTRL48-CAN-2026-06`；`APPROVED-NEW-ECAT-CTRL-2026-07` |
| 已用来源范围 | 仅使用任务提供的本地事实：荷兰登记/监管页面、公司官网产品资料、公司集成说明、公司演示与 webinar、分销商页面、公开职业资料、批准本地产品事实 |
| 未授权来源 | 登录、订阅或付费信用来源；没有使用，也没有把它们写成“已检查” |
| 访问限制 | 未联网；未直接打开原始网页。具体 URL、完整原文、精确地址和部分发布日期未提供，因此保留可追溯性与覆盖缺口 |
| 计划覆盖 | 主体、产品/应用、近期活动、渠道与技术资料、联系人、贸易与体量、登记/监管风险、产品证据链、一个最终项目建议、外联材料、工作簿状态 |

## 二、执行结论

HelioMotion Systems B.V. 的法定主体、官网地址关联、泵撬产品方向和两条当前控制需求均有官方或相互印证的材料支持。现阶段最适合开发的不是尚处原型阶段的 EtherCAT 新控制器，而是：

> **围绕已安装泵撬的 CANopen 改造项目，与 Aftermarket Director Pieter de Vries 启动一次受边界约束的技术适配核验。**

选择该方向的原因是：CANopen 改造需求同时出现在分销商页面和 2026 年 7 月公司 webinar；现有批准产品明确支持 CANopen，且批准应用边界包含 retrofit pump modules。核心限制是尚未拿到电机电气数据、CANopen profile/PDO、机械安装、连接器、卫生/环境和认证要求，因此只能建议“技术适配核验”，不能宣称兼容、可直接替换或可降低柜体空间和调试工作。

新款 EtherCAT 控制器只保留为未来评估选项：它处于 validated prototype status，可对业务员已确认的潜力客户讨论，但没有获批生产日期或性能承诺，也不应用来支撑当前 CANopen 改造提案。

## 三、公司与业务发现

### 3.1 已证实信息与合理推断

| 发现 | 证据引用 | 证据状态 | 使用边界 |
|---|---|---|---|
| 荷兰登记记录 `NL-REG-4417` 显示 HelioMotion Systems B.V. 处于 active 状态，登记地址与官网所示地址一致 | E01 | 官方直接证据 | 未提供具体地址文本，不能独立复核地址细节 |
| 公司官网产品页展示用于食品加工产线的模块化泵撬 | E02 | 官方直接证据 | 支持产品与应用方向，不自动证明销量、产能或市场份额 |
| 当前文档列明第三方 CANopen 电机控制器安装在独立箱体中 | E03 | 官方直接证据 | 支持现有供应方向；不支持该控制器的品牌、价格、故障或替换难度结论 |
| 官方集成说明称，新泵撬买方越来越多地要求通过 EtherCAT 接入工厂网络；现有控制器需独立网关，增加柜体空间和调试工作 | E04 | 官方直接证据 | 属客户官方说明；不等于我方产品已经能解决该问题 |
| 已安装泵撬仍有 CANopen retrofit kit 需求 | E05、E06 | 多来源相互印证 | 分销商页面与公司 webinar 支持“需求持续可见”；不能外推订单量或采购预算 |
| 公司在评估紧凑型、EtherCAT-ready 控制方案，用于计划在 2026 年第四季度开展 pilot review 的新 hygienic skid family | E07 | 官方直接证据 | 仅支持“评估”和“计划”；不表示项目已立项采购、已采用某供应商或一定按期进行 |
| Pieter de Vries 的公开职责与 retrofit programmes 直接匹配；Eva Jansen 的公开职责与 control integration 直接匹配 | E11、E12 | 多来源相互印证 | 支持联系人候选排序，不授权代替业务员决定渠道、内容或发送 |
| 根据泵撬、食品加工产线、控制集成和分销活动，HelioMotion 很可能属于工业 B2B 泵撬系统制造或集成商 | E02、E03、E05、E06 | 合理推断 | 法定经营范围、自产比例、采购主体与生产设施仍待核验 |

### 3.2 法定主体、关联主体与采购主体

- **已解析：** 法定名为 HelioMotion Systems B.V.；登记标识为 `NL-REG-4417`；登记地址与官网地址一致（E01）。
- **未解析：** 母公司、子公司、分支机构、关联品牌、最终受益所有人、合同主体、付款主体及实际采购主体均未提供。
- **影响：** 当前可以形成产品适配开发建议，但在报价、合同或付款安排前必须重新核对交易主体关系。

### 3.3 产品、应用、市场与渠道

- **产品 / 应用：** 模块化泵撬；食品加工产线（E02）。
- **当前控制架构：** 第三方 CANopen 电机控制器位于独立箱体（E03）。
- **新平台方向：** EtherCAT 接入工厂网络；计划中的 hygienic skid family（E04、E07）。
- **售后方向：** 已安装泵撬的 CANopen retrofit kits（E05、E06）。
- **渠道信号：** 存在分销商页面和分销商参与的 retrofit event（E05、E12）。
- **市场覆盖缺口：** 除荷兰主体外，没有提供销售国家、终端客户区域、渠道数量或市场份额。

### 3.4 近期活动

| 时间窗口 | 活动 | 证据 | 结论边界 |
|---|---|---|---|
| 最近 90 天 | 2026 年 7 月公司 webinar 显示 CANopen retrofit kits 的持续需求 | E06 | 支持当前售后改造主题，不支持需求规模 |
| 最近 90 天 | 2026 年 6 月公司演示称正在评估紧凑型 EtherCAT-ready 控制方案，Q4 2026 计划 pilot review | E07 | 支持未来评估窗口，不支持采购或量产承诺 |
| 日期未知 | 分销商页面显示 CANopen retrofit kit 需求仍在持续 | E05 | 因发布日期未知，不单独归入最近 90 天；与 E06 一起支持持续需求判断 |
| 长期观察 | Q4 pilot、季度 retrofit campaigns、hygienic-enclosure 更新、分销商培训活动 | E06、E07 | 作为跟踪主题，不等于已确认采购计划 |

### 3.5 工业客户适配来源覆盖

- **已有：** 官网产品与应用、技术/集成资料、公司 webinar、公司演示、分销商活动、职业联系人资料。
- **未提供：** 专利、招聘、展会名录、完整新闻记录、制造设施资料、客户案例原文。
- **影响：** 不影响 CANopen 改造主题的初步适配判断，但限制对研发能力、采购节奏、生产规模和决策链的判断。

## 四、公司体量综合分析

| 维度 | 可见事实 | 结论 |
|---|---|---|
| 海关 / 贸易活动 | 未提供海关或贸易数据 | 无法判断；不得写成“没有贸易” |
| 公开财务 | 未提供 | 无法判断营收、预算、盈利或信用能力 |
| 员工规模 | 未提供 | 无法判断 |
| 办公 / 生产设施 | 仅知登记地址与官网地址一致；未提供设施性质或面积 | 无法判断制造规模或产能 |
| 市场覆盖 | 确认食品加工产线应用；未提供国家或渠道覆盖规模 | 只能确认应用方向，不能判断市场规模 |
| 销售渠道 | 有分销商活动信号 | 可见分销协作，但不能判断渠道数量或销售贡献 |
| 经营活动 | 2026 年 6 月演示、7 月 webinar、retrofit 活动和 Q4 pilot 计划 | 支持公司近期存在可见经营与产品活动，不等于体量结论 |

**有边界的体量描述：** HelioMotion 有持续可见的工业产品、售后改造和新平台评估活动，但缺少财务、员工、设施、贸易和覆盖规模数据，当前无法把它可靠地分类为大型、中型或小型企业，也不能推算采购预算或产能。

## 五、海关与贸易数据

**customs_findings：无可登记贸易证据。**

- 本次没有提供海关或贸易数据源，也没有授权登录/付费信用来源。
- 已知可用于后续匹配的键只有法定名 `HelioMotion Systems B.V.`、登记编号 `NL-REG-4417` 和“登记地址与官网地址一致”这一关系；具体地址、名称变体、关联主体、HS 编码和采购主体未提供。
- 因此不能形成覆盖国家、时间段、贸易方向、货运频次、产品描述或主体匹配结论，也不能表述为“未发现贸易记录”。

## 六、风险核验

**risk_gate_status：** `未触发`

### 已有风险材料

- 提供的荷兰登记与监管页面在其已查范围内没有匹配的注销、重大处罚或执法通知（E08）。
- 上述结论只覆盖所提供页面及其可见范围，不等于全面信用、诉讼、破产、制裁或监管审查通过。

### 剩余风险缺口

- 未提供制裁清单、法院、破产、公开财务、受益所有人和完整监管检索结果。
- 登录信用来源未获授权，未访问；不能据此判断付款能力或信用状况。
- 合同方、付款方、受益人和采购主体关系尚未解析；进入交易阶段前必须核对。

### 风险结论边界

在当前提供材料中没有观察到触发风险硬门的条件，因此保持 `未触发`，可以继续内部推荐和准备候选外联材料。但该状态不是“信用已通过”或“风险已排除”；若后续出现主体冲突、重大诉讼、制裁、严重监管或付款异常，应立即改为 `暂停待业务员审核`。

## 七、联系人候选

### 主要联系人：`CONTACT-HM-02` — Pieter de Vries

| 字段 | 记录 |
|---|---|
| 职务 / 可能角色 | Aftermarket Director；负责 retrofit programmes |
| 职责匹配 | 与本次 CANopen installed-skid retrofit 主题直接匹配 |
| 公开活跃 | 出现在分销商 retrofit event |
| 渠道可得 | 公开职业资料；具体平台名称和 URL 未提供 |
| 联系信息来源 | 官方 team page、分销商 retrofit event、公开职业资料；本地引用 E12 |
| 真实性 | 已核实；官方团队页与公开职业资料确认同一雇主和职责 |
| 来源可靠性 | 可追溯但间接；本地事实说明了原始来源类型，但未给出具体 URL |
| 使用权限 | 正常使用；仅限公开职业渠道，且发送前应核对具体资料链接与账号主体 |
| 排序依据 | 当前推荐聚焦售后改造，职责匹配度高于新平台集成联系人 |

### 候补联系人：`CONTACT-HM-01` — Eva Jansen

| 字段 | 记录 |
|---|---|
| 职务 / 可能角色 | Product Integration Manager；负责 control integration |
| 职责匹配 | 适合核验电机、协议、柜体、连接器及未来 EtherCAT 集成要求 |
| 公开活跃 | 出现在 2026 年 7 月公司 webinar |
| 渠道可得 | 公开职业资料；具体平台名称和 URL 未提供 |
| 联系信息来源 | 官方 team page、2026 年 7 月 webinar、公开职业资料；本地引用 E11 |
| 真实性 | 已核实；官方团队页、webinar 与公开职业资料确认同一雇主和职责 |
| 来源可靠性 | 可追溯但间接；本地事实说明了原始来源类型，但未给出具体 URL |
| 使用权限 | 正常使用；仅限公开职业渠道，且发送前应核对具体资料链接与账号主体 |
| 排序依据 | 技术职责高度相关，但本次主题首先是 aftermarket retrofit，因此列为技术候补 |

**联系人缺口：** 未提供任何邮箱、电话或具体职业资料 URL；不得猜测联系方式。业务员仍需确认实际使用的公开职业渠道及页面主体。

## 八、full_due_diligence_output

| 栏目 | 内部结论 | 证据 / 缺口 |
|---|---|---|
| 现有供应方向 | 第三方 CANopen 电机控制器，独立箱体安装 | E03；品牌、型号、价格与合同关系未知 |
| 合作障碍 | 当前产品只支持 CANopen，不能覆盖新泵撬的 EtherCAT 需求；具体电机、协议对象字典、机械、连接器、卫生与认证要求未知 | E04、P01；不得宣称直接替换 |
| 替代机会 | 对已安装泵撬的 CANopen retrofit modules 做技术适配核验 | E05、E06、P01 |
| 当前产品机会 | `APPROVED-PRODUCT-CTRL48-CAN-2026-06`：48 V BLDC、支持 CANopen、批准应用边界含 retrofit pump modules | P01；不包含 EtherCAT |
| 未来新品机会 | `APPROVED-NEW-ECAT-CTRL-2026-07` 可作为未来 hygienic skid 的评估选项 | E07、P02；仅 validated prototype，不承诺性能或生产日期 |
| 长期关注主题 | Q4 pilot、季度 retrofit campaigns、hygienic-enclosure 更新、分销商培训活动 | E06、E07；需按新事件重新取证 |
| 持续触达理由 | 每个上述事件都可能带来新的技术要求或评估窗口 | 合理推断；不能用旧话术机械重复触达 |
| 待解决问题 | 48 V 系统边界、电机参数、CANopen profile/PDO、柜体和连接器、卫生/环境、认证、改造数量和时间、采购/合同主体 | 当前均缺少客户确认 |

## 九、项目机会与唯一最终推荐

### final_recommendation

**机会编号：** `OPPORTUNITY-HM-001`  
**项目名称：** 已安装泵撬 CANopen retrofit 控制器技术适配核验  
**推荐状态：** 最终推荐（待业务员决定）  
**主要联系人：** `CONTACT-HM-02` Pieter de Vries  
**技术候补：** `CONTACT-HM-01` Eva Jansen

### 项目证据链

1. **客户事实：** 分销商页面和 2026 年 7 月公司 webinar 均显示已安装泵撬仍有 CANopen retrofit kit 需求（E05、E06）。
2. **应用 / 采购场景：** 售后团队为 installed skids 开展 retrofit programmes；具体采购数量和节点待确认（E12）。
3. **批准产品：** `APPROVED-PRODUCT-CTRL48-CAN-2026-06`（P01）。
4. **匹配依据：** 产品支持 CANopen，批准应用边界包含 retrofit pump modules；这是协议和应用边界层面的初步匹配，不是完整兼容性结论。
5. **待验证问题：** 48 V 电源边界、电机类型与电气数据、CANopen 版本/profile/PDO、控制逻辑、柜体尺寸、连接器、IP/卫生要求、认证、现有网关/控制器接口、改造数量、时间及采购主体。
6. **适合验证的联系人：** Pieter 负责 retrofit programmes；Eva 可参与 control integration 技术核验（E11、E12）。

### 主要风险和限制

- 不能宣称能直接替代现有第三方控制器。
- 不能把新泵撬的 EtherCAT 痛点转化为当前 CANopen 产品卖点。
- 不能承诺减少柜体空间、缩短调试、提供样品、报价、交期或认证，除非另有批准事实和业务员确认。
- 若客户把项目限定为 EtherCAT，本推荐需停止，转为未来原型评估判断。

### 未选方向简要取舍

- **未来 EtherCAT hygienic skid：** 有明确评估信号，但我方产品仍是 validated prototype，且无生产日期或性能承诺；保留为未来评估选项，不作为当前主推荐。
- **泛化的新泵撬控制替换：** 需求范围和兼容性证据不足，容易把“客户痛点”误写成“我方已解决”，本次不展开。

## 十、唯一外部方案（英文候选稿）

### Proposal: CANopen Retrofit Controller Fit Evaluation

**Prepared for:** HelioMotion Systems B.V.  
**Proposed contact:** Pieter de Vries, Aftermarket Director

**Objective**  
Evaluate whether an approved 48 V BLDC controller with CANopen support could fit selected retrofit pump-module requirements for HelioMotion’s installed skids.

**Why this evaluation is relevant**  
HelioMotion’s recent retrofit activity indicates continued use of CANopen kits on installed skids. Our current controller supports CANopen, and its approved application boundary includes retrofit pump modules. This creates a basis for a focused fit review, but not yet a compatibility or replacement conclusion.

**Proposed review scope**

1. 48 V supply and motor electrical requirements.
2. Required CANopen version, device profile, PDO mapping and control functions.
3. Existing controller, gateway, connector and cabinet constraints.
4. Environmental, hygienic-enclosure and certification requirements.
5. Retrofit programme timing, expected application variants and the internal technical approval process.

**Proposed outcome**  
A joint requirements checklist identifying confirmed matches, unresolved gaps and a go/no-go decision for any next technical evaluation stage.

**Product boundary**  
This proposal concerns the approved CANopen controller only. It does not claim EtherCAT capability, direct drop-in compatibility, reduced cabinet space, shorter commissioning time, production readiness for a new platform, or any commercial commitment. Any next step remains subject to technical validation and mutual confirmation.

**Suggested next step**  
A 20-minute scoping discussion with Pieter de Vries, with Eva Jansen included if detailed control-integration questions need to be reviewed.

## 十一、首触达材料

**建议渠道：** 公开职业平台站内消息；具体平台、资料 URL 和账号主体需业务员在发送前核对。  
**触达阶段：** 首次触达候选稿  
**建议日期：** 2026-07-27，依据为研究完成后的下一个工作日；未应用荷兰节假日日历，业务员可调整。  
**新价值：** 不是泛泛介绍产品，而是提出一份围绕 CANopen retrofit 的边界明确的适配清单。  
**证据引用：** E05、E06、P01、E12。  
**状态：** 草稿；未批准、未发送。

### Finished outreach message

> Hello Pieter — I noticed HelioMotion’s continued work on CANopen retrofit kits for installed pump skids. We have a 48 V BLDC controller with CANopen support whose approved application scope includes retrofit pump modules.
>
> Rather than assume compatibility, I would like to compare your requirements for motor electrical data, CANopen profile/PDO mapping, connectors, cabinet constraints and hygienic or certification needs with our current product boundary.
>
> Would a 20-minute scoping discussion next week be useful? If the basics align, we could document a focused requirements checklist and decide together whether a further technical evaluation makes sense.
>
> Best regards,  
> [Salesperson name]  
> [Company]

**后续节奏边界：** 第一次跟进只能按首封的实际发送日期加 5 个工作日计算；目前没有实际发送记录，因此不生成跟进日期或后续成稿。任一渠道收到回复后，应立即暂停原触达计划并准备 `foreign-trade-email-assistant` 移交。

## 十二、证据记录

所有记录的本地引用均为：`tests/foreign-trade-customer-development/fixtures/11-full-due-diligence-happy-path.md`。查询日期均为 2026-07-24；访问范围均为“本次提供的本地材料，未直接访问外部网页”。

| 编号 | 最小必要原文 / 本地证据引用 | 中文摘要 | 来源类型 / 发布主体 | 发布日期 | 语言 / 地区 | evidence_state |
|---|---|---|---|---|---|---|
| E01 | “Dutch registry record `NL-REG-4417`…shows HelioMotion Systems B.V. active at the same address as its website.” | 荷兰登记显示该法定主体 active，且地址与官网一致 | 政府登记 / 荷兰登记机构 | 未知；观察日期 2026-07-20 | 英语摘要 / 荷兰 | 官方直接证据 |
| E02 | “official product pages show modular pump skids for food-processing lines” | 官网展示食品加工产线用模块化泵撬 | 公司官网 / HelioMotion | 未知 | 英语摘要 / 未知 | 官方直接证据 |
| E03 | “Current documentation names a third-party CANopen motor controller in a separate enclosure.” | 当前文档列明第三方 CANopen 电机控制器位于独立箱体 | 公司技术资料 / HelioMotion | 未知 | 英语摘要 / 未知 | 官方直接证据 |
| E04 | “new skid buyers increasingly request EtherCAT…existing controller requires a separate gateway, adding cabinet space and commissioning work” | 新泵撬买方出现 EtherCAT 接入需求；现有方案需额外网关 | 公司集成说明 / HelioMotion | 未知 | 英语摘要 / 未知 | 官方直接证据 |
| E05 | “A distributor page…show continued demand for CANopen retrofit kits on installed skids.” | 分销商页面显示 installed skids 的 CANopen retrofit kit 需求仍可见 | 分销商页面 / 未提供名称 | 未知 | 英语摘要 / 未知 | 单一来源待验证 |
| E06 | “a July 2026 company webinar…show continued demand for CANopen retrofit kits on installed skids” | 公司 webinar 显示 CANopen retrofit kit 的持续需求 | 公司 webinar / HelioMotion | 2026-07 | 英语摘要 / 未知 | 官方直接证据 |
| E07 | “A June 2026 company presentation says it is evaluating compact EtherCAT-ready controls…pilot review in Q4 2026.” | 公司正在评估紧凑型 EtherCAT-ready 控制，计划 Q4 pilot review | 公司演示 / HelioMotion | 2026-06 | 英语摘要 / 未知 | 官方直接证据 |
| E08 | “Dutch registry and regulator pages…show no matching dissolution, material penalty, or enforcement notice.” | 所提供登记和监管页面在其覆盖内未见匹配的注销、重大处罚或执法通知 | 政府登记及监管页面 / 荷兰相关机构 | 未知 | 英语摘要 / 荷兰 | 多来源相互印证 |
| E11 | “Eva Jansen…official team page and July webinar…public professional profile confirms the same employer and responsibility for control integration.” | Eva 的身份、雇主及控制集成职责由多个职业来源印证 | 公司团队页、公司 webinar、公开职业资料 / HelioMotion 与个人职业资料发布者 | 2026-07（webinar）；其他未知 | 英语摘要 / 未知 | 多来源相互印证 |
| E12 | “Pieter de Vries…official team page and distributor retrofit event…public professional profile confirms responsibility for retrofit programmes.” | Pieter 的身份、雇主及 retrofit programme 职责由多个职业来源印证 | 公司团队页、分销商活动、公开职业资料 / HelioMotion、分销商与个人职业资料发布者 | 未知 | 英语摘要 / 未知 | 多来源相互印证 |
| P01 | `APPROVED-PRODUCT-CTRL48-CAN-2026-06`: 48 V BLDC, CANopen, approved for retrofit pump modules; no approved EtherCAT capability | 当前批准产品支持 CANopen，应用边界含 retrofit pump modules，不支持获批 EtherCAT 表述 | 批准本地产品事实 / 本方批准资料 | 2026-06 | 英语摘要 / 本方产品范围 | 官方直接证据 |
| P02 | `APPROVED-NEW-ECAT-CTRL-2026-07`: compact 48 V EtherCAT controller, validated prototype; future evaluation only; no approved production date or performance promise | EtherCAT 新品仅可作为未来评估选项，不得承诺生产日期或性能 | 批准本地新品事实 / 本方批准资料 | 2026-07 | 英语摘要 / 本方产品范围 | 官方直接证据 |

## 十三、reliability_summary

**整体可信但存在缺口**

### 支持证据

- E01 支持主体 active 状态及登记地址与官网地址的一致关系。
- E02–E07 支持产品应用、现有控制架构、CANopen retrofit 需求和 EtherCAT 未来评估方向。
- E11、E12 通过多个来源支持两名联系人的身份、雇主与职责。
- E08 支持在所提供登记/监管页面覆盖内未见指定负面记录。

### 反对或冲突证据

在本次已提供材料范围内未见反对或冲突证据；该表述不覆盖未提供、未授权或未直接访问的来源。

### 剩余缺口

- 原始 URL、荷兰语原文、精确地址、部分发布日期和页面版本未提供。
- 母子公司、关联主体、受益所有人、合同/付款/采购主体未解析。
- 财务、信用、法院、破产、制裁、完整监管、专利、招聘、设施和海关/贸易资料未提供。
- 产品兼容性所需的客户技术参数与认证边界未提供。
- 联系人具体职业资料 URL 与可用联系方式未提供。

## 十四、业务员仍需决定

### Must do

1. 确认是否接受 `OPPORTUNITY-HM-001` 作为本次唯一开发方向。
2. 发送前核对 Pieter 的具体公开职业资料链接、账号主体和实际渠道。
3. 审阅并批准最终外联措辞、建议日期和是否发送；AI 不发送。
4. 若客户回应，立即暂停原触达，并保存真实发送与回复记录后移交邮件助手。

### Recommended

1. 在技术沟通前准备上述待验证问题清单，避免把初步协议匹配说成完整兼容。
2. 将 2026 Q4 pilot、季度 retrofit campaigns、hygienic-enclosure 更新和分销商培训活动设为证据更新节点。
3. 交易推进前补齐采购、合同和付款主体，以及必要的信用、法院、破产、制裁和监管核验。

## 十五、工作簿更新状态

**workbook_update_status：未写入。** 业务员未指定本地 `.xlsx` 文件，也未授权本次写入，因此没有创建或修改工作簿，亦未声称重新打开验证成功。

**如需后续写入：** 业务员应指定目标文件、工作表和允许写入的字段；随后按稳定编号 `CUSTOMER-HM-001`、`OPPORTUNITY-HM-001`、`CONTACT-HM-01`、`CONTACT-HM-02` 及 E/P 证据编号生成待写入包，写入后重新打开核对工作表、编号、变更单元格和保存值。

## 十六、完成检查与未验证项

- **已核对：** 仅使用提供事实；证据状态采用受控值；客户事实、任务控制、风险、联系人权限、产品事实和缺口保持分离；只形成一个最终推荐；未生成发送或工作簿成功声明。
- **独立反查：** 重点检查了最可能造成误导的三处——把 EtherCAT 原型写成现货能力、把 CANopen 协议匹配写成直接兼容、把有限监管覆盖写成全面风险通过；成品均保留了相应限制。
- **UNVERIFIED：** 外部原始页面、具体联系人 URL、完整风险/贸易覆盖、技术兼容性和任何商业条款均未在当前材料中验证。
