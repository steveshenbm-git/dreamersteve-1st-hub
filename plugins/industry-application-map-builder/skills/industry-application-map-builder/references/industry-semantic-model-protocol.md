# 行业语义多模型协议

## 目录

1. 模型配置
2. 模型A
3. 模型B
4. 模型C
5. 手工接力
6. 返回验收

## 1. 模型配置

首个候选 `model_profile_id = rc2-pilot-v1`：

| 角色 | 用户指定模型 | 当前运输方式 | 启动条件 |
|---|---|---|---|
| A | GPT-5.6 Terra | 可固定实际模型的Codex任务或另行授权API | 合同和输入哈希已冻结 |
| B | Claude Sonnet 5 | `manual_external_handoff` | A已形成最小命题和来源包 |
| C | Grok 4.5 | `manual_external_handoff` | 出现争议、反证、系统偏差或反向审计样本 |

每次保存提供商、声明模型名、实际模型ID或 `unknown`、运输方式、检索工具、来源权限、运行ID和时间。精确模型无法确认时不得静默替换；方法结论保持 `INCONCLUSIVE`，除非用户批准新配置并新建合同。

当前技能没有Claude或Grok连接器，不能声称Codex已经自动调用外部模型。API/MCP只允许在单独授权的集成任务中替换运输方式，不改变包结构、可见字段和验收门。

## 2. 模型A

A读取官方节点、说明、父级路径、冻结主题、来源范围和检索规则，负责浅筛、最小命题、来源搜索、证据封装、未知和反证记录。

A不得自行审查或升级自己的证据，不得根据行业名称形成公司适配或行业排除，也不得把自身知识写成 `supported`。

## 3. 模型B

B只接收：合同/任务/命题ID、最小命题、来源URL或校验后快照、原始位置、A的有限摘录、条件、限制、反证和统一量表。

B不得接收：A的完整推理、A的置信度、A的行业或商业推荐、公司名、公司产品、业务优先级或其他模型投票。

B必须按顺序验证：

1. 原始URL；
2. 校验哈希后的HTML/PDF快照；
3. 最多两次有限重试；
4. 仍不可读则 `UNVERIFIED`。

B只能输出 `PASS / FAIL / UNVERIFIED` 和结构化原因码。自身知识不能补齐不可访问来源。

## 4. 模型C

C只在A/B分歧、来源冲突、命题可能膨胀、系统性术语偏差、独立反证或反向审计时启动。

任务包的 `trigger_reason` 只允许 `a_b_dispute / source_conflict / claim_inflation_risk / systematic_term_bias / independent_counterevidence / reverse_audit_sample`。`reverse_audit` 模式必须使用 `reverse_audit_sample`；争议模式不得借用该原因。缺少或不匹配时任务包校验失败。

- 争议模式：看标准化命题、原始来源和B的结构化异议，不看A完整推理或置信度。
- 反向审计模式：只看研究合同、节点、官方路径和允许来源，不看A的结论、理由或查询词。

C的意见不能因三模型多数同意而升级证据。只有直接来源和B的来源审查可以满足正式证据门。

## 5. 手工接力

使用 `../assets/semantic-method/model-task.template.json` 和 `model-return.template.json`：

1. Codex生成只读任务包和输入SHA-256；
2. 用户只负责把完整任务包交给指定模型；
3. 用户把原始返回文件交回；
4. Codex校验合同、任务、输入哈希、声明模型、实际模型和返回结构；
5. 不完整或不一致的返回进入 `08-隔离失败返回/`，不进入正式结果。

用户不填写证据字段或机器附页。后台字段、哈希、查询记录和审查记录由本技能维护。

## 6. 返回验收

每个 `semantic_model_return` 必须匹配对应任务的：

- `task_id`；
- `research_contract_id` 和版本；
- `input_sha256`；
- 声明模型和可核实的实际模型；
- 角色允许的输出类型；
- 来源访问结果和结构化原因码。

单条B返回 `UNVERIFIED` 时，该关系保留 `unknown` 或 `hypothesis`，不能升级为 `supported`。它不自动阻断无关记录；批次是否暂停只按冻结的系统访问、控制案例和预算规则判断。
