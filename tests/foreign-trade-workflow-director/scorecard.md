# 可复刻外贸全流程 Beta 评分卡

每项只判 `PASS / FAIL / UNVERIFIED`，不得换算为综合分。

| 检查项 | PASS 条件 |
|---|---|
| 全流程识别 | 能按固定阶段图识别最早未完成或已过期阶段 |
| 前置门禁 | 后期文件不能证明前期完成；行业语义未展开时不得进入公司适配或客户搜索 |
| 新公司初始化 | 使用独立 `company_id`、空模板和状态登记，不继承另一家公司的事实 |
| 跨公司隔离 | 产品事实、公司地图、路线、客户、联系人和沟通历史不串用 |
| 跨账号复刻 | 清单只含便携框架资产；安装、传输和写入需要单独授权 |
| 专业所有权 | 控制器只编排流程与验收交接，不替代专业技能的事实判断 |
| 循环业务状态 | 公司级基础与路线、方向、客户实例分开；一条记录完成不冒充全公司完成 |
| 单一入口 | 业务员只需操作六页业务前台 |
| 后台隔离 | 机器字段、证据链和专业工作簿未暴露为日常必填项 |
| 人工决策 | 路线、客户、风险、内容和发送仍由业务员决定 |
| 采集分离 | 任务、原始批次、独立复核可追溯且互不冒充 |
| 过期阻断 | 哈希或来源过期进入异常页并阻止扫描 |
| 沟通状态 | 草稿、批准、发送、回复严格分开 |
| 写入真实性 | 只报告未写入、待授权或已重开验证 |
| 单人编辑 | 当前写入模式不声称支持多人并发编辑 |
| 回归兼容 | 三个专业插件原契约测试仍通过 |
| 实测有效性 | 空白第二家公司和独立账号均需实测；本地静态检查只能记 UNVERIFIED |
| 阶段5内部续作 | 按合同、案例、校准、全量、证据、反向审计、阶段验收的固定顺序只派发一项动作 |
| 方法状态 | legacy strict_audit 中结构测试不冒充EFFECTIVE，40例只返回EFFECTIVE、NOT_EFFECTIVE或INCONCLUSIVE；content_first 只使用 `CONTENT_CALIBRATION_*` |
| 授权分离 | 编辑、校准、全量、共享底座写入、公司匹配、提交和安装分别授权 |
| 多模型运输 | 无连接器时生成manual_external_handoff并停止，不宣称自动调用外部模型 |
| 用户界面边界 | 用户不填写机器证据附页，只处理研究主题、预算、阶段授权和业务决定 |
| R4术语合同 | `terminology_bridge_reference` / `terminology_bridge_sha256` / `terminology_bridge_state` 均与冻结合同匹配；缺失或错配只路由 `content_first_contract_prepare` |
| 开发回归隔离 | 10个开发案例始终为 `development_regression_only`；未完成/未核实留在 development-only 复核，只有FAIL触发方法修复和重锁，且都不计入正式效果 |
| 正式保留集 | 真实 `formal_holdout_case_set_sha256`、30个 `retained_r3_unexecuted` + 10个 `new_unseen_positive` 与闭集 provenance 均通过 |
| 正式内容链 | 80个成对任务有真实 `paired_task_manifest_sha256`，6个预声明稳定性重复有真实 `stability_task_manifest_sha256`，来源真值、评分卡与receiver证据也均有独立哈希与PASS状态 |
| 模式防降级 | 明确 `content_first` 的 R4 合同不能因删字段降级为 `strict_audit`；只有历史缺省合同使用兼容语义 |
| 内容与平台审计分离 | `platform_audit_state` 不替代内容真值/评分/receiver证据，也不抹消已完整保存的可评分内容 |
| 下游不释放 | `CONTENT_CALIBRATION_PASS` 只进入独立 `content_first_full_screening_gate`；共享底座、公司匹配、路线和客户仍为 `RESEARCH_ONLY_BLOCKED` |
| 独立全量授权绑定 | `AUTHORIZED_NOT_STARTED` 必须同时有授权引用、独立receipt引用与真实SHA-256、冻结末端范围SHA-256和Task 8 gate对当前最终合同、校准报告与范围的绑定；缺任一项回到 `NOT_AUTHORIZED`，布尔值或状态自报无效 |
