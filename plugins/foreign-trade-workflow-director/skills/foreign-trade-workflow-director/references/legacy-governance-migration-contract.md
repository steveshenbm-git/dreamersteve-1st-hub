# 历史治理记录限定迁移合同

```yaml
contract_id: FTWG-LEGACY-GOVERNANCE-MIGRATION
contract_version: 1.0.0-draft.2
contract_state: candidate_not_active
parent_contract_id: FTWG-INSPECTOR-GOVERNANCE
parent_contract_version: 1.0.0-draft.3
```

本合同只在用户明确要求迁移时读取。候选版本支持限定来源盘点、逐条映射、干跑、激活前检查和激活后验证；there is **no automatic activation**。它不授权扫描未声明目录、写正式治理登记、修改历史原件、Git、发布或安装。

## 固定边界

每个批次使用新的拒绝覆盖目录。清单必须冻结：

- `discovery_roots`；
- `include_patterns`、`exclude_roots`、`exclude_patterns` 与排除理由；
- `follow_symlinks: false`；
- 每个已声明来源的相对路径、SHA-256、角色、范围和记录数；
- 目标治理根及其预写哈希。

为保持零第三方依赖，`.yaml` 清单使用 JSON 兼容的 YAML 写法；流程控制器从空模板生成，用户不手工改格式。

校验器只遍历这些根，并比较实际符合规则的文件与清单。文件名搜索或清单自报不能证明闭包。符号链接和解析后路径不得逃离授权根。

## 来源与映射

来源角色只有 `authoritative_history / supporting_evidence / context_only / generated_view`。治理范围只有 `framework / company / task`。公司或任务事实不能进入框架正文。

每条具备迁移资格的旧记录必须恰好有一条映射：

```text
create_new_finding
link_existing_finding
create_or_link_improvement
context_only
duplicate_excluded
invalid_excluded
unresolved_conflict
```

排除不能靠遗漏表达；重复项必须引用规范目标；冲突必须保留双方证据。历史“修复/完成/PASS”只能映射到直接证明的验证层，默认 `requires_revalidation: true`，不得自动生成 `verified_closed` 或 `accepted_effective`。

## 阶段

```text
inventory → mapping → dry-run → activation-preflight → post-activation
```

- `inventory`：核对授权根、发现闭包、清单计数和来源哈希。
- `mapping`：核对每条旧记录一次且仅一次映射、重复和冲突。
- `dry-run`：核对候选事件、范围、链、计数和目标预写哈希；不写目标。
- `activation-preflight`：除干跑条件外，要求 `governance_registry_write` 授权引用和单一编辑者；仍不写目标。
- `post-activation`：只读核对激活回执、追加计数、前后哈希和重建结果。

所有阶段只返回 `PASS / FAIL / UNVERIFIED`、计数、问题和一项下一动作。任何阶段都不得修改来源、批次或目标。

如果用户请求的是正式激活，而缺少 `governance_registry_write` 授权，检察处置必须是 `stop`；已通过的干跑不能把它降为 `rehearsal_only`。停止只覆盖正式激活，只读盘点、映射复核或诊断不因此被禁止。

## 停止条件

授权根不明、发现规则未冻结、漏文件、清单外文件、哈希不符、解析失败、合格记录漏映射或重复映射、未解决冲突、公司泄漏、历史越级、目标哈希变化、缺少激活授权或企图覆盖历史时停止受影响迁移。

迁移失败不删除原件、批次或已追加事件。未来失效只能追加失效事件并重建快照；新尝试使用新批次 ID。

## 模板与真实批次

技能内模板均含 `template_record: true`，只是空结构。真实批次必须填入真实来源、哈希和授权并把该字段改为 `false`。仍有必填 `null`、示例值或模板标记的批次必须拒绝。
