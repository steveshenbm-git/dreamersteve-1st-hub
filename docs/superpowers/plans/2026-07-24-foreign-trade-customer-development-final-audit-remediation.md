# 外贸客户开发技能最终验收缺口修复计划

**日期：** 2026-07-24  
**分支：** `ft-customer-dev`  
**目标：** 修复 Task 20 独立验收确认的四个源码/测试缺口，同时保持当前 Git 历史的公开发布阻断，不安装、不推送、不发布、不改写历史。

## 验收结论与边界

Task 20 的 Acceptance、Falsification 与 whole-branch review 均判定当前源码尚未批准完成。已确认的材料性缺口为：

1. 工作簿 13 个受控字段不允许空白，与“未知值留空”冲突。
2. 没有可用邮箱时，技能可能自动绕过三轮邮件并把其他渠道作为首次触达。
3. 发件人身份与邮件头未核验的入站邮件被过度标为“官方直接证据”。
4. 有效事件触发被写成可选额外触达，而非必须准备待业务员审核的候选材料。

当前开发分支早期历史含个人绝对路径。发布清单已正确阻断公开发布；本计划不授权 squash、rebase、push、PR、合并或任何历史改写。

## Task 21：先建立四类 RED 合同与反例

**修改：**

- `tests/foreign-trade-customer-development/validate_contract.py`
- `tests/foreign-trade-customer-development/validate_workbook.py`
- `tests/foreign-trade-customer-development/test_validate_workbook_mutations.py`
- `tests/foreign-trade-customer-development/scorecard.md`
- 新增必要的无邮箱、入站证据和有效事件 fixture/RED evidence

**要求：**

1. 工作簿验证器要求 13 个受控验证同时满足 `allowBlank=True`、`showErrorMessage=True`、`errorStyle=stop`。
2. mutation 独立关闭一个字段的 `allowBlank`，验证器必须只报对应诊断；现有列表和错误提示反例继续通过。
3. 静态合同要求：没有可正常使用的邮箱时不得自动把其他渠道作为首次触达；必须记录邮件缺口并等待业务员决定。
4. 静态合同要求：未核验入站邮件不得标为官方直接证据；收到回复仍立即停止并移交邮件助手。
5. 静态合同要求：发现有效事件时必须准备一份待业务员审核的额外触达候选；不得自动发送，且事件不重置定期锚点。
6. 增加相反语义反例，避免“正确条款与矛盾条款同时存在”被 presence matcher 误判。
7. 先运行并保存真实 RED；不得修改旧 raw，不得把答案写进盲测输入。

**提交：** `建立客户开发最终验收缺口回归测试`

## Task 22：修复工作簿允许空白合同

**修改：**

- `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/assets/prospect-development-workbook.xlsx`
- `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/workbook-and-handoff.md`

**要求：**

1. 必须使用 `spreadsheets:Spreadsheets` 与 `@oai/artifact-tool` 设置 13 个验证允许空白；不得用 openpyxl 创作源工作簿。
2. 同时保留精确列表、范围、停止式错误拦截、9 张表、第 1 行英文、第 2 行中文解释、第 3 行数据起点、空数据边界、`A3` 与第 2 行筛选。
3. 若 artifact-tool 不能持久化允许空白属性，停止并报告；未经控制代理明确授权，不得扩大 OOXML 兼容修正。
4. 运行工作簿验证器、全部 mutation、ZIP、artifact-tool 重开、公式错误扫描及 9 表渲染目检。

**提交：** `允许客户开发受控字段留空`

## Task 23：修复首次触达、入站证据与事件触达

**修改：**

- `plugins/foreign-trade-customer-development/skills/foreign-trade-customer-development/references/opportunity-and-outreach.md`
- 必要时最小修改 `evidence-contacts-and-risk.md` 或 `SKILL.md`
- Task 21 新增 fixtures 的 GREEN raw 与评分总结

**要求：**

1. 邮件仍为默认首要渠道。没有可正常使用的邮箱时，只输出邮件渠道缺口与候选处置包；不得由 AI 自动改用其他渠道首次触达。业务员可决定继续找邮箱、明确批准一个合格的其他渠道例外，或暂停。
2. 未核验发件人身份/邮件头的入站邮件内容不得标为“官方直接证据”；使用适当受控状态并保留客户主张、来源与真实性缺口。无论证据状态如何，回复硬停和邮件助手移交优先。
3. 发现有效事件时，AI必须准备一份待业务员审核的额外触达候选材料；业务员保留内容、渠道和发送权。事件触达独立记录且不重置定期锚点。
4. 保留原有失败 raw 并如实改判；用 fresh isolated executor 生成新 raw，先保存再评分。
5. 验证三轮邮件、其他渠道、返回邮件、10 日节奏、回复硬停与邮件助手边界未回归。

**提交：** `收紧客户首次触达与事件证据规则`

## Task 24：重新执行最终验收

1. 运行 JSON、官方 skill/plugin、合同、工作簿、mutation、行为、ZIP、whitespace、路径、凭据和 Git 状态检查。
2. 使用 fresh Acceptance、Falsification 与 whole-branch reviewer；所有 Critical/Important 必须修复并重新复核。
3. 以下继续标记 `UNVERIFIED`：安装后运行、真实登录/付费来源、生产工作簿写入、长期真实业务结果、公开历史清理。
4. 停在安装、push、PR、发布、merge、squash、rebase 或历史改写之前。

