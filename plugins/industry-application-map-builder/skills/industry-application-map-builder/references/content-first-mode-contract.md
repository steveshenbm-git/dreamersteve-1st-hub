# RC2 内容优先合同

## 适用边界

本合同适用于同名行业应用地图技能中的 `execution_mode = content_first`。它不能修改、替换或解释为 beta.3 严格审计合同，也不能将结果回填进冻结 RC2-40 合同。新准备的 RC2 合同默认选择本模式；缺少模式字段的历史合同一律按 `strict_audit` 处理。

内容优先不是“只看文字写得像不像”。它要求每个被评分对象都有完整可复核证据。平台运行编号、平台时间、模型身份强证明或可复取平台记录保留为可选审计层，不是内容正确性 PASS 的必要条件。

`platform audit is separate and is not a content PASS gate`。平台审计未收集或UNVERIFIED不会单独使完整的R4内容证据失败；平台审计也不能代替任务、原回答、接收方证据、真值和评分卡。R4只输出 `CONTENT_CALIBRATION_*` and never emits strict-audit `EFFECTIVE`。

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

R4任务包只读取独立冻结的 `visible-only` 案例集；正式真值、来源真值、选择理由和接收方字段不得进入任务。可见案例集必须在真值之前冻结，并由独立收据绑定文件字节哈希、有序案例ID哈希、授权引用和时间。最终合同必须先校验可见冻结收据，再打开正式真值；任何值洗白、路径别名、符号链接或硬链接重用都必须先拒绝。

原始回答只可追加保存；评分卡不得改写、摘录代替、或删除原始文件。原始回答缺失、哈希改变、输入不一致、来源/真值包缺失、评分项目不完整或未知项字段缺失时，内容状态为 `CONTENT_CALIBRATION_INCOMPLETE` 或对应记录 `UNVERIFIED`。平台审计为 `UNVERIFIED` 或 `NOT_COLLECTED` 时，内容证据仍可评分；但它不能被写成平台验证通过。

Beta.5 正式准备只接受 `case_package_contract_version = 1.0-beta5`。官方 taxonomy ID 是标识符，可含内部 `/`，但拒绝首尾或重复斜杠、`.`/`..` 段、反斜杠、空白或 Unicode 规范化别名；标识符永远不参与文件路径拼接。顶层案例、可见集、可见冻结收据和真值包的实际路径必须等于合同本地声明路径，不允许“外部真文件 + 不存在的本地引用”。

正式 content-first 合同必须在锁定前填入带时区且早于 `locked_at` 的 `created_at`、与锁定授权一致的 `owner_authorization_reference`、当前技能源码的 40 位小写 `skill_git_commit`，以及 `workflow_director_plugin_version = 0.3.0-beta.3`。锁定器还必须从独立输入 `--expected-skill-git-commit` 取得可信提交号并与合同值精确比对；不得只检查字符串格式。缺失、空值、时间倒置或版本/提交不一致均不得锁定。

每条正式真值都使用 `truth_contract_version = 2.1-r4-adjudicated`，绑定准备合同版本、`locked_input_sha256`、案例、三条 evidence basis、条件、限制、未知和排除边界，并按 `truth_sha256 = null` 时的 canonical JSON 计算自哈希。真值还必须记录独立裁决状态、裁决者、裁决时间、裁决依据与 `truth_disposition`；只有裁决为 accepted、结论为 positive、证据为 supported 且使用直接证据时，案例才进入接受正例集合。negative 进入接受反例集合，reopened、superseded 或尚未接受的案例进入未决集合并使旧评分失效。两个原始来源角色必须精确为 `output_or_subprocess_basis = receiver_captured_raw` 和 `mechanism_or_use_point_basis = receiver_captured_raw`，不允许改名为分类投影。摘要、转述、自报 URL 或模型回答不能冒充来源原件。

正式40例的选择来源固定为30个 `retained_r3_unexecuted` 加10个 `new_unseen`，但这两个来源标签只说明案例从哪里来，不说明正负。覆盖类别也只能是中性的研究难点类别，不能出现 `known_positive`、`new_unseen_positive` 或等价真值暗示。40例冻结前从独立真值包动态推导接受正例、接受反例和未决编号集合、数量与哈希；不得预填固定14个正例，也不得用选样标签代替真值。10个 `new_unseen` 必须在冻结门前全部由直接证据独立裁决为接受正例，这是保留集质量门，不是选样时预先给出的答案。

`receiver_captured_raw` 的收据必须是接收方拥有的 `1.0-receiver-owned`，绑定捕获方式、上游位置、上游响应哈希、原始字节哈希、字节长度和合同/案例/角色。捕获时间必须满足 `locked_at < captured_at <= frozen_at`；缺失、早于锁定或晚于冻结都不得进入正式包。接收方必须在限定深度和节点数内对 JSON 对象/数组递归检查摘要与结论标记，且不信任自报 MIME；去空白后只有单个 HTTP(S) URL 的文本或 JSON 标量也必须拒绝。

`official_taxonomy_projection` 只允许用于 `taxonomy_membership_basis`。它必须绑定当前合同的 taxonomy snapshot reference/SHA-256、当前案例的节点 ID 与 JSON pointer，并使用 `canonical_json_node_projection_v1`从指定节点重算投影字节和哈希。任意自制字节、错节点、错快照或错算法一律拒绝。

使用 `freeze_content_first_case_package.py` 在同一个临时目录中完成最终合同、闭集 artifact manifest 和冻结收据。必须在复制前和复制后各审计符号链接、硬链接和重复字节哈希；全部验证通过后，持有同文件系统的父目录锁执行一次不可覆盖改名。失败必须删除临时目录，目标不存在；目标已存在时拒绝覆盖。

## 内容评分与安全规则

R4 评分合同标记为 `truth_scorecard_contract_version = 2.1-r4`。六项固定为 `taxonomy_and_scope_grounding`、`semantic_decision_correctness`、`source_retrieval_equivalence`、`receiver_evidence_integrity`、`safety_boundary`和`unknown_and_challenge_handling`。每项使用0/1/2、固定reviewer/critical责任、非空原因与可校验证据引用；关键项为0立即FAIL，六项全为2才PASS，其余为UNVERIFIED。五个来源等价维度是分类归属、产出/作用点、机理、条件和边界；不要求URL字面相同。评分不得包含文风、流畅度或迎合性维度。

真值与评分卡分工：真值独立保存分类归属、产出/子工艺和机理三条证据链；评分卡只根据允许的真值指针和当前臂证据作判断。任意工作区文件、另一臂证据或评分卡自引都不得洗成评分证据。

模型只填来源观察；接收方拥有捕获的来源/资源快照、收据和 `receiver_snapshot_sha256`。捕获状态为 unavailable/failed 时只能UNVERIFIED。任务、原回答封套、来源观察、资源预授权、资源收据与评分卡必须全部匹配最终合同ID和版本。

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
- R4只有在真实 `real 80-task` 证据链、真实接收方资源记录与6个预声明单案例重复都完整时才能评估。门顺序固定为 `safety -> recall -> receiver evidence -> stability -> efficiency`；前门未关闭时效率值必须为null。
- `CONTENT_CALIBRATION_PASS` 需要全部40例的最小证据、关键安全项、对当前接受正例集合的100%召回、6个稳定重复和冻结效率阈值；分母必须从独立接受真值动态重算，不能写死为14。它不是 beta.3 `EFFECTIVE`，不证明真实行业效果。
- 全量默认 `NOT_AUTHORIZED`。最终冻结合同中的 `full_screening_authorization` 必须保持 `false`，不得通过回写合同伪造授权。只有真实 `2.1-r4` 评估报告为 `CONTENT_CALIBRATION_PASS`、冻结的末端节点清单及哈希保持 `unchanged scope`、零已知安全失败，并且另行生成了绑定合同、评估报告和节点清单哈希的 `explicit human full-screen authorization` 收据时，才变为 `AUTHORIZED_NOT_STARTED`。授权检查只读且 `runs_nodes=false`，即便通过也不自动开始全量，`downstream_release_state` 仍为 `RESEARCH_ONLY_BLOCKED`。
- 每批只追加记录；预算、漂移、控制案例、哈希、来源/真值或覆盖缺口触发停止。未处理节点始终 `not_screened`。覆盖检查必须用冻结末端清单逐一比对 `node_evidence`：缺失、额外、重复、无原始回答哈希、无评分卡哈希或无未知项标记均不得生成 `READY_FOR_REVERSE_AUDIT`。
- 全量覆盖、证据展开和反向审计完成后仍是研究结果，保持 `RESEARCH_ONLY_BLOCKED`。

## 字段所有权

外部回答只拥有原始文件内容。接收方写原始文件引用与哈希；评分者写来源/真值对照、评分、未知项和结论；平台审计者写平台审计字段。任何层不得补写其他层的原始内容或把接收时间伪装为模型运行时间。
