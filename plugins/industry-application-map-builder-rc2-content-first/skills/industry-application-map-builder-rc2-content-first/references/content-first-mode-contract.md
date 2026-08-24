# RC2 内容优先候选合同

## 适用边界

本合同只适用于独立候选插件中的 `execution_mode = content_first`。它不能修改、替换或解释为 beta.3 严格审计合同，也不能将结果回填进冻结 RC2-40 合同。缺少模式字段的历史合同一律按 `strict_audit` 处理。

内容优先不是“只看文字写得像不像”。它要求每个被评分对象都有完整可复核证据。平台运行编号、平台时间、模型身份强证明或可复取平台记录保留为可选审计层，不是内容正确性 PASS 的必要条件。

## 最小内容证据

每个 `calibration_case` 或 `terminal_node` 必须一对一保存：

1. 稳定 case/node ID 与 `method_arm`；
2. 固定可见输入及 `visible_input_sha256`；
3. 外部回答的独立原始文件、路径和字节 SHA-256；
4. 可读取的来源或真值对照包及 SHA-256；
5. 指向上述对象的逐项内容评分卡；
6. 评分中明确的 `unknown_items`，可为空数组但字段不得缺失；
7. 独立的 `platform_audit_state` 与可选审计引用。

机器字段固定为：`subject`、`method_arm`、`visible_input`、`visible_input_sha256`、`raw_response_reference`、`raw_response_sha256`、`source_truth_comparison_reference`、`source_truth_comparison_sha256`、`unknown_items` 和 `platform_audit_state`。

原始回答只可追加保存；评分卡不得改写、摘录代替、或删除原始文件。原始回答缺失、哈希改变、输入不一致、来源/真值包缺失、评分项目不完整或未知项字段缺失时，内容状态为 `CONTENT_CALIBRATION_INCOMPLETE` 或对应记录 `UNVERIFIED`。平台审计为 `UNVERIFIED` 或 `NOT_COLLECTED` 时，内容证据仍可评分；但它不能被写成平台验证通过。

## 内容评分与安全规则

评分项固定为 `scope_taxonomy_grounding`、`three_axis_handling`、`source_truth_alignment`、`safety_boundary`、`unknown_disclosure`。每项使用 0/1/2，关键项为 0 立即失败；评分不得包含文风、流畅度或迎合性维度。

评分前先检查：产品中性、正例召回、误导反例、资料稀少、来源循环、跨公司污染、命题膨胀、三状态轴、直接来源证据和反向审计。内容评分不能把 AI 常识、模型共识或分类名称升格为 `supported`；`no_hypothesis_formed` 不等于行业排除。

## 状态机和停止点

```text
CONTENT_CONTRACT_DRAFT
→ CONTENT_CONTRACT_FROZEN
→ CONTENT_CALIBRATION_INCOMPLETE | CONTENT_CALIBRATION_FAIL | CONTENT_CALIBRATION_PASS
→ NOT_AUTHORIZED | AUTHORIZED_NOT_STARTED
→ IN_PROGRESS | COVERAGE_INCOMPLETE | READY_FOR_REVERSE_AUDIT | BLOCKED
→ RESEARCH_ONLY_BLOCKED
```

- 40例只在两臂同用一个冻结案例集、真值包、分类快照、可见输入和评分量表时可评分。
- `CONTENT_CALIBRATION_PASS` 需要全部40例的最小证据、关键安全项、100%已知正例召回和冻结的深度展开节省阈值；它不是 beta.3 `EFFECTIVE`。
- 全量默认 `NOT_AUTHORIZED`。只有内容校准 PASS、`terminal_node_manifest_reference` 与 `terminal_node_manifest_sha256` 仍匹配、零已知安全失败、明确 `full_screening_authorization_reference` 存在时，才变为 `AUTHORIZED_NOT_STARTED`。
- 每批只追加记录；预算、漂移、控制案例、哈希、来源/真值或覆盖缺口触发停止。未处理节点始终 `not_screened`。覆盖检查必须用冻结末端清单逐一比对 `node_evidence`：缺失、额外、重复、无原始回答哈希、无评分卡哈希或无未知项标记均不得生成 `READY_FOR_REVERSE_AUDIT`。
- 全量覆盖、证据展开和反向审计完成后仍是研究结果，保持 `RESEARCH_ONLY_BLOCKED`。

## 字段所有权

外部回答只拥有原始文件内容。接收方写原始文件引用与哈希；评分者写来源/真值对照、评分、未知项和结论；平台审计者写平台审计字段。任何层不得补写其他层的原始内容或把接收时间伪装为模型运行时间。
