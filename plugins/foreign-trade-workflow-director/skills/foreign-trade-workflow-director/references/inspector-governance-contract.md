# 跨技能检察治理运行合同

```yaml
contract_id: FTWG-INSPECTOR-GOVERNANCE
contract_version: 1.0.0-draft.3
contract_state: candidate_not_active
owner: foreign-trade-workflow-director
```

本合同是横向预检和记录协议，不是新业务阶段。它不改变 `first_incomplete_stage` 的计算，也不扩张任何授权。

## 何时读取

跨任务指挥、`framework_resume`、`specialist_handoff`、依据修复恢复流程、建议提交/推送/安装，或从演练转正式前读取本合同。普通概念解释不必新建治理记录。

## 权威边界

- 用户的最新明确指令决定目标、范围和授权。
- 专业技能拥有专业事实、证据与结论；控制器不得改写专业真值或补造 PASS。
- 完整性校验通过的追加事件是治理历史；快照与摘要只是可重建投影。
- 会话 `memory.md` 只保存当前目标和方法，不是永久漏洞台账。
- 框架记录只保存通用技能工程事实；公司记录只保存公司影响并只读引用框架 finding。两者不得互相复制私有事实。

## 预检输入与结果

依次读取当前会话记忆、可用的公司或框架治理快照、相关任务台账、实际技能版本/提交/安装身份和本次授权。只计算与 `target_action`、`affected_scope` 相交的开放问题。

处置优先级：

```text
stop > rehearsal_only > continue_with_correction > continue
```

| 处置 | 使用条件 | 当前动作 |
|---|---|---|
| `continue` | 记录或效率问题不影响当前证据 | 记录后继续 |
| `continue_with_correction` | 可直接核对的小幅路径、取源或指令偏差 | 保留失败，纠偏后继续 |
| `rehearsal_only` | 可以安全演练但正式接受条件缺失 | 只演练，不提升正式状态 |
| `stop` | 真值、盲测、哈希/合同、来源时序、历史只读、授权或闭包受损 | 停止受影响动作，保全证据 |

输出必须只有一个最高处置和一个 `one_next_action`。停止只覆盖受影响范围；安全只读诊断仍可继续。

### 三个可观察的处置边界

- **纠偏顺序**：使用 `continue_with_correction` 时，先把失败证据写入不可覆盖的记录，并给出该记录引用；完成保留后才执行纠偏。不得用“边改边保留”替代这个先后顺序。
- **公司局部纠偏**：直接证据只支持当前公司和当前任务，且当前动作可在边界内安全修正时，返回 `continue_with_correction`。纠正当前任务后可以继续当前范围，但不得提升为便携规则或第二家公司事实；跨公司推广仍保持阻断。
- **演练与激活**：当用户请求的目标动作本身只是隔离演练，且缺口仅是正式接受条件时，返回 `rehearsal_only`。当目标动作本身是正式激活或正式治理写入，且缺少 `governance_registry_write` 时，对该目标动作返回 `stop`；只读诊断仍可继续，并作为唯一下一动作候选。不得因为存在安全演练路线而把正式激活的处置降为 `rehearsal_only`。

## 记录与验证层

公司或框架治理根包含：

```text
governance-registry.yaml
findings.jsonl
improvement-events.jsonl
validation-events.jsonl
evidence-index.jsonl
governance-summary.md
```

为保持零第三方依赖，`governance-registry.yaml` 使用 JSON 兼容的 YAML 写法；复制技能模板后由流程控制器填充真实值，用户不手工转换格式。

四个 JSONL 日志只追加。`governance-registry.yaml` 与 `governance-summary.md` 只能从日志重建。当前 Beta 只允许登记中的 `single_editor_id` 写入；预期快照哈希、编辑者或前序事件链不一致时停止。

每条事件使用严格递增 `sequence`、上一事件哈希和排除 `event_sha256` 字段后的规范 JSON SHA-256。不同日志分别维护链。

验证层分别是：

```text
contract_consistency
deterministic_regression
full_test_suite
source_release
installed_artifact_identity
task_forward_validation
cross_company_validation
real_effectiveness
```

状态只能为 `NOT_STARTED / PASS / FAIL / UNVERIFIED / STALE / NOT_APPLICABLE`。任何一层不推出下一层；`verified_closed` 必须绑定当前版本、全部必需层、直接证据和追加关闭事件。

## 写入界面

`scripts/workflow-governance.py validate` 严格只读。`append` 只在现有授权根通过完整校验、快照哈希与单一编辑者匹配、授权引用非空时追加一条事件，再重建快照和摘要。`rebuild` 只替换派生快照和摘要。工具不初始化目录、不搜索其他位置、不执行 Git、不推进业务阶段。

若追加已接受但重建失败，保留事件并返回 `FAIL`，之后只能显式 `rebuild`；不得删除或改写已接受行。

## 授权

只读治理审计、治理登记写入、任务本地台账、技能源、Git 提交、推送/发布、安装、正式案例/模型、全量筛查、共享底座、公司匹配、路线/候选和发送是独立授权。前一项不能代替后一项。

## 当前边界

此候选合同的结构或确定性测试 PASS 只证明规则可解析，不能证明已发布、已安装、真实任务有效、跨公司通用或真实效果成立。
