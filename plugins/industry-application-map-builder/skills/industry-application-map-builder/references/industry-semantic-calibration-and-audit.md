# 行业语义校准、全量运行与反向审计

## 目录

1. 40例配对校准
2. 校准硬门
3. 全量浅筛
4. 选择性证据展开
5. 反向审计
6. 漏判恢复
7. 阶段PASS门

## 1. 40例配对校准

### content_first R4正式案例政策

R4不重找另一组40例。从已冻结候选中保留30个 `retained_r3_unexecuted`（合同兼容标识为 `30 unexecuted`）且未被开发调试使用的案例，再加入10个 `new_unseen` 案例，构成新的正式40例。这两个 `selection_origin` 只说明案例来源，不定义真值。任何标记 `development_regression_only = true` 的案例都只用于开发回归，不得计入正式40例、接受正例集合或稳定性统计。此政策必须冻结案例ID、选择来源、开发排除集和真实字节哈希；不以聊天记忆或文件名判定。10个 `new_unseen` 必须在最终冻结前全部通过直接证据独立裁决为接受正例；这是冻结质量门，不是选样时预先写入的答案。

正式任务包是 `40 pairs`：`baseline_full_depth_v1` 和 `screen_then_expand_v2` 各有40个独立任务，共享同一冻结可见输入，不共享上下文、输出文件或对方臂结果。另冻结 `6 predeclared high-risk single-case repeats`：候选臂的6个高风险案例各重复1次，不是6组40例，也不是复制ID或汇总。

评估器必须实际打开并核对全80个任务的task、原回答、回答封套、六项scorecard、receiver-owned资源观察与收据，以及6个重复的新鲜上下文、预授权和独立文件。汇总自报、路径别名、符号链接、硬链接、跨案例/跨臂文件复用或只换repeat ID都必须拒绝。

候选池与案例准备只能读取通过哈希校验的 `case_preparation_locked` 合同。该阶段允许在隔离目录中追加候选、排除记录、案例和答案键，但不得生成模型任务；案例集哈希和控制案例必须保持为空，直到40个案例真实完成并通过真值门。空模板、零记录头或占位案例集哈希都不能充当已准备案例集。

案例集冻结后，用其实际案例集哈希、40个唯一案例ID、真实控制案例和批次大小生成新合同版本的最终 `frozen` 合同。准备合同与最终合同的不可变输入投影必须匹配 `locked_input_sha256`；若主题、快照、提示词、来源、预算或抽样规则漂移，停止并重新锁定。只有最终冻结合同可以进入模型运行。

40例冻结抽样覆盖使用以下产品中性研究难点；`sampling_category` 只定义要覆盖的检索或安全压力，不定义正例、反例或未决结论：

| sampling_category | 数量 | 覆盖目的 |
|---|---:|---|
| `direct_evidence_candidate` | 8 | 检查直接来源候选的捕获与核查，不预设其结论。 |
| `terminology_mismatch_candidate` | 6 | 检查术语差异下的发现能力，不预设实际相关性。 |
| `misleading_name_control` | 6 | 检查名称误导风险，不以名称指定答案。 |
| `source_scarce` | 5 | 检查资料稀少或来源不可访问时的未知处理。 |
| `incomplete_conditions` | 5 | 检查条件、限制或边界不完整时的保守处理。 |
| `source_independence_risk` | 4 | 检查循环转载或来源独立性不足。 |
| `vacuous_hypothesis_control` | 3 | 检查空洞泛化假设和命题膨胀。 |
| `contamination_or_structure_control` | 3 | 检查跨公司污染、批次漂移或结构错误。 |

正式真值只从 `truth_contract_version = 2.1-r4-adjudicated` 的独立裁决记录生成。只有满足当前真值合同的 accepted 记录才能进入 `accepted_positive_case_ids` 或接受反例集合；其余案例进入未决集合并阻止旧评分沿用。冻结包必须保存三个编号集合、数量及哈希。证据不足的 `open_case` 可观察行为，但不进入接受正例召回分母。

同一新版技能定义两个R4同级方法臂：

- `baseline_full_depth_v1`：40个节点逐一尝试完整深度链；
- `screen_then_expand_v2`：先浅筛，再按触发规则展开。

两臂使用同一案例、A/B/C配置、来源权限、搜索工具、时间窗口、证据规则和预算口径；运行目录和运行ID分开，使用新鲜独立上下文。评估器必须核对研究合同ID/版本、分类快照哈希、40例案例ID与案例集哈希、模型配置ID以及正确的方法臂标签；任一不一致只能返回 `INCONCLUSIVE`。旧Git提交只负责回退，不是实验基线。

## 2. 校准硬门

### content_first R4

R4门顺序固定为安全、当前接受正例集合100%进入展开、接收方证据完整、6个单案例稳定重复、效率。`accepted_positive_case_ids`、`accepted_positive_count` 和 `accepted_positive_case_ids_sha256` 必须从当前 accepted 独立真值重算并与两臂一致；`accepted_positive_count` 是动态召回分母，不得写死为14。真值被 reopened 或 superseded 时，旧任务、评分和校准结论全部失效。前门未通过时，后门不评估，效率数值为null。冻结阈值为深度展开至少减少 `20 percent`、查询数最多增加 `10 percent`、`zero source-open increase`。R4 CLI不得放宽这些阈值。

R4结果只能为 `PASS / FAIL / INCOMPLETE` 与对应 `CONTENT_CALIBRATION_*`。`CONTENT_CALIBRATION_PASS` 只表示这一内容合同的冻结门已满足；它不等于 `EFFECTIVE`，不证明真实产业效果，不授权full screening。全量、共享底座、公司匹配、路线和客户继续 `RESEARCH_ONLY_BLOCKED`。

### legacy strict_audit

先执行安全硬门，再计算效率：

- 已知正例100%进入证据展开；
- 无直接证据、循环来源、跨公司污染进入正式证据均为0；
- 行业名称形成范围排除、命题膨胀、空洞条件、结构断链、状态轴混用均为0；
- B未重新读取来源却PASS为0；
- 合同、模型、提示词或来源权限混用为0；
- 原始输出和运行条件可复现；
- 候选臂深度展开节点数比基线至少减少20%。

结果只允许：

- `EFFECTIVE`：全部硬门和效率门通过；
- `NOT_EFFECTIVE`：任一安全门、正例召回或效率门失败；
- `INCONCLUSIVE`：模型、来源、真值、运行条件、基线或复现证据不足。

40例不证明全量被筛节点的漏判率低于5%，也不自动授权全量运行。

## 3. 全量浅筛

### content_first R4 full-screen gate

`CONTENT_CALIBRATION_PASS` 只能进入授权检查。只有独立的 `explicit human full-screen authorization` 存在、冻结末端范围的引用和哈希保持 `unchanged scope`、安全失败为零时，才可从 `NOT_AUTHORIZED` 进入 `AUTHORIZED_NOT_STARTED`。这一状态仍不是 `EFFECTIVE`，不会自动开始筛查，也不解除 `RESEARCH_ONLY_BLOCKED`。

### legacy strict_audit

只有方法 `EFFECTIVE`、用户另行批准全量、Git/插件/合同仍匹配、末端节点清单重新冻结、三模型可用性通过且预算规则冻结后，才能启动。

批次大小由40例实测确定。每批使用冻结控制案例并记录触发率、搜索量、Token、时间和来源访问。触发率没有预设业务正确区间，只用于漂移诊断；控制案例状态、命题或来源结果漂移时立即暂停。

预算停止保留已完成记录，剩余节点保持 `not_screened`。多个冻结控制来源在至少两个独立域名同时不可访问时，当前批次返回 `UNVERIFIED`，不得把系统性访问故障拆成大量单条未知后继续。

## 4. 选择性证据展开

以下节点进入证据展开：

- 全部 `hypothesis_formed`；
- 全部 `ambiguous`；
- 检索信号与浅筛冲突的节点；
- N.E.C.和其他高风险抽样节点；
- 反向审计命中节点；
- 与已发现漏判同原因的受影响分支。

每条关系先写最小命题。进入 `supported` 必须同时满足：直接来源、原始位置、可验证现场或快照、B PASS、命题不超出来源、非循环来源、无未解决反证和自动合同校验PASS。

型号、定量性能、材料相容性、法规、安全或重大成本结论创建 `technical_escalation_required`，不得只由模型裁决。

## 5. 反向审计

全部 `no_hypothesis_formed` 节点按固定优先顺序进入一个且仅一个风险层：

1. `signal_conflict`；
2. `nec_or_miscellaneous`；
3. `source_scarce`；
4. `semantic_ambiguity`；
5. `ordinary`。

统计样本在各层执行无放回简单随机抽样。若统计样本没有覆盖某个顶层行业大类，另取行业覆盖补充样本；补充样本不进入统计分母，但发现漏判同样触发FAIL。

冻结 `N_h`、`n_h`、随机种子、抽样算法、纳入概率、总体 `alpha = 0.05`、漏判定义和多层校正。每层用超几何分布反演计算精确单侧上界；非空层使用Bonferroni校正，`alpha_h = 0.05 / H`。总体上界为：

```text
U = Σ (N_h / N) × U_h
```

要求 `U <= 0.05`。样本量由 `sample_semantic_reverse_audit.py` 在抽样前计算；59例只可作为无分层简单随机的理论说明，不能硬编码为正式样本数。

脚本第一次运行只产生 `audit_state = PLANNED`。完成复核后，`--audit-results` 必须逐一覆盖全部统计样本和行业补充样本；每条保存 `industry_node_id`、`audit_result = PASS | FAIL | UNVERIFIED` 与布尔值 `confirmed_miss`。少一条、多一条、重复ID、未验证结论或字段互相矛盾均返回 `INCONCLUSIVE`。只有全体结果完整且无漏判时才生成 `audit_state = PASS`，不能把“抽样计划生成成功”误作审计通过。

## 6. 漏判恢复

任一统计样本或行业覆盖补充样本发现真实漏判，即使计算上界仍低于5%，当前合同也立即FAIL：

1. 停止未开始批次；
2. 保留原记录；
3. 记录漏判节点、原因和风险层；
4. 确定受影响分支和同原因节点；
5. 标记 `audit_reopened`；
6. 创建新合同版本；
7. 重跑受影响范围；
8. 使用新种子和新样本重新审计。

不得只修正被抽中节点后沿用失败合同。

## 7. 阶段PASS门

`industry_semantic_expansion` 只有同时满足以下条件才能PASS：

- 当前末端节点快照全部有可审计筛查记录；
- 所有记录来自同一有效合同版本；
- 所有触发节点已完成证据处置；
- 反向审计加权单侧上界不高于5%；
- 实际审计没有漏判；
- 无安全硬门失败；
- 来源快照、哈希、运行条件和验证报告齐全。

阶段PASS不自动包含正式底座写入、公司匹配、路线池或客户搜索授权。
