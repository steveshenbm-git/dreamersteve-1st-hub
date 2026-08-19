# 行业语义研究合同

## 目录

1. 适用范围
2. 三条状态轴
3. 冻结合同
4. 产品中性主题
5. 合同版本与授权
6. 可观察检索门

## 1. 适用范围

本合同只管理 `industry_semantic_expansion`：把版本化行业分类骨架转化为可审计的浅筛记录、选择性证据展开、反向审计和阶段验收。它不判断公司产品适配，不生成路线，不搜索客户。

完整分类骨架只证明行业活动节点存在，不证明产出产品、过程、应用或需求已经研究。方法在40例配对校准前固定为 `method_validation_state = INCONCLUSIVE`。

## 2. 三条状态轴

每条节点记录同时保存且不得互相代替：

```text
screening_result: hypothesis_formed | ambiguous | no_hypothesis_formed
semantic_work_state: not_screened | screened | evidence_expansion_required | evidence_expanded | audit_reopened
evidence_state: supported | hypothesis | unknown | conflicted
```

`no_hypothesis_formed` 只表示在冻结视角和最低检索范围内尚未形成可检验假设，不是行业排除结论。预算停止的未处理节点保持 `not_screened`，不得补写筛查结果。

过程状态另行保存：

```text
contract_state: draft | frozen | superseded | invalidated
method_validation_state: INCONCLUSIVE | EFFECTIVE | NOT_EFFECTIVE
run_state: planned | running | stopped | completed | invalidated
blind_review_state: pending | PASS | FAIL | UNVERIFIED | escalated
retrieval_status: complete | partial | failed | source_scarce | source_inaccessible
```

## 3. 冻结合同

从 `../assets/semantic-method/research-contract.template.json` 创建 `semantic_research_contract`。冻结前至少核对：

- 合同ID、版本、用户授权引用和当前Git提交；
- 两个插件版本；
- 末端节点快照路径、数量和SHA-256；
- 研究主题三要素及独立去公司化结果；
- 模型配置、身份依据最低等级、允许的身份依据类型、提示词文件及哈希；
- 来源范围、检索工具、语言、地区和最低检索规则；
- 证据门、基线臂、候选臂和40例真值包哈希；
- 批次、控制案例、预算停止、风险分层、随机种子和统计公式；
- 硬门、允许写入和禁止动作；
- `full_screening_authorization` 与 `application_base_write_authorization`，两者默认均为 `false`。

合同不得保存密钥、密码、私人凭证或登录会话。缺字段、未冻结、快照不匹配或模型身份依据未达到冻结门槛都返回 `UNVERIFIED` 并停止受影响动作。手工交接中的用户确认可以按合同记为 `operator_attested`，但不能写成连接器验证。

## 4. 产品中性主题

主题必须同时写明：

1. 功能或作用机理；
2. 材料形态、加工位置或作用点；
3. 明确排除领域和边界。

独立检查者只能看到主题文本和检查标准，不得看到生成主题时使用的公司资料。主题不得包含公司、品牌、型号、公司适配结论或只能反推某一公司的独特参数组合，也不得宽泛到大多数工业行业均可套用。结果只允许 `PASS / FAIL / UNVERIFIED`；未PASS不得冻结。

## 5. 合同版本与授权

以下任一变化都创建新合同版本，旧结果不得直接合并：

- 模型配置、身份依据策略、提示词、检索动作或来源权限变化；
- 研究主题、状态定义、触发规则或证据门变化；
- 分类快照、40例真值包、批次、控制案例或预算规则变化；
- 风险层、随机种子规则、统计方法或阈值变化；
- 技能Git提交变化。

授权相互独立：源编辑、40例运行、全量筛查、正式底座写入、公司匹配、客户搜索、Git提交和插件安装不得互相推定。

## 6. 可观察检索门

形成 `no_hypothesis_formed` 前必须完成两组检索：

1. 行业产出物或工艺；
2. 研究机理、作用点及跨领域同义词。

每组保存查询词、工具、语言、地区和观察时间。有至少5个可用结果时必须检查排序最前的5个不同结果；不足5个时全部检查并记录不足原因。发现线索必须打开核查，单组最多2个；更多线索按冻结排序规则选择，并保留未打开引用。

任一检索组未完成、工具失败、来源大面积不可访问、术语冲突或官方说明过于抽象时，只能记为 `ambiguous`。完成两组检索后，合计少于3个不同、可访问且包含节点特定产出物或工艺信息的结果时，默认 `retrieval_status = source_scarce`；该数字是校准前冻结的候选参数，不是已验证事实。
