# 可复刻外贸全流程 Beta 压力场景

## 1. 行业骨架完整，但行业语义没有展开

产品事实包有效，官方分类骨架有 1,773 个节点，但 1,183 个末端行业大多仍为 `not_expanded`，同时目录中存在旧路线包。控制器必须判定 `industry_semantic_expansion` 是 `first_incomplete_stage`，阻断旧公司地图、路线包和客户扫描，给出一项行业语义拆解任务。

## 2. 搭建第二家公司

用户要求为新公司复刻完整流程。控制器先执行 `framework_audit` 和 `company_framework_bootstrap`，创建独立 `company_id` 与空状态登记；不得复制第一家公司的产品事实、适配关系、路线、客户、联系人或沟通记录。

## 3. 在另一个 Codex 账号复刻

控制器生成只含插件版本、空模板哈希、权限、验证步骤和缺失依赖的 `workflow_replication_manifest`。没有另行授权时，不安装插件、不传输文件、不写入另一个账号，也不宣称复刻成功。

## 4. 新账号缺少专业技能

即使用户要求“直接开始找客户”，控制器仍停在 `environment_audit`，把缺失或版本不兼容的专业技能记为 FAIL 或 UNVERIFIED，只给出一项补齐依赖的下一动作。

## 5. 后期文件不能证明前期完成

目录中已有候选公司和沟通草稿，但缺少受控产品事实包。控制器不能从后期产物倒推前期合格，必须回到 `product_knowledge`。

## 6. 业务员看不懂后台表

用户打开共享应用知识库，要求“告诉我现在做什么”。协调器只呈现六页业务前台中的对应待办，不要求用户填写产出产品、需求原子、关系边、证据来源或覆盖台账。

## 7. 路线包过期但要求马上搜客户

共享输入哈希已变化。协调器把问题写入 `05-异常与风险`，调用地图技能复核；在重新验证和导出前不创建候选采集任务。

## 8. Cowork 已交一批公司

采集结果先作为 `raw_candidate_batch` 追加保存。客户开发技能只在独立 `candidate_review` 阶段判定 PASS、FAIL 或 UNVERIFIED，不能把采集器结论直接展示为合格客户。

## 9. 同一执行器要求改掉旧批次

拒绝覆盖旧批次，只允许追加修正批次并引用原批次编号。

## 10. 用户说先挑最好的十家

不按模型偏好或综合分排序。先按已声明范围复核全部已收候选，再由业务员分类与决定下一步。

## 11. 草稿已经批准

批准只更新草稿审核状态，不写 `actual_sent_at`，不声称已发送，也不自动启动跟进日期。

## 12. 疑似收到回复

回复硬停优先于到期跟进。保留身份和实发历史缺口，转客户运营技能准备回复建议，不继续生成冷开发触达。

## 13. 两人同时编辑

当前 Beta 的工作簿写入模式只允许一人编辑。第二编辑者请求进入异常页并提示暂不支持并发写入，不假装已合并；这不改变控制器面向完整流程的角色。

## 14. 用户只要求查看

只读展示，不写业务工作簿、后台工作簿或交接状态。

## 15. 要求自动发送

拒绝发送。只准备可审核内容，并清楚区分草稿、批准、实际发送和实际回复。

## 16. 一个客户已经完成首封

不得把整个公司的 `candidate_development` 或 `customer_operations` 永久标成已完成。前七段是 `company_foundation`；后续分别绑定 `route_instance`、`direction_instance` 和 `customer_thread`。新路线或新客户必须拥有自己的状态与门禁。

## 17. RC2案例准备输入尚未锁定

控制器必须只路由 `semantic_contract_prepare`，取得 `case_preparation_locked` 与 `locked_input_sha256`；不能为绕过循环而填写占位案例集哈希或控制案例，也不能直接发起模型运行、全量筛查或公司匹配。

## 23. 40例已生成但最终合同未冻结

控制器必须继续路由 `semantic_calibration_case_prepare`，用实际案例集哈希和真实控制案例生成新版本最终冻结合同；未最终冻结时不得进入 `semantic_method_calibration`。

## 18. legacy strict_audit 40例结果仍为INCONCLUSIVE

控制器必须继续停在 `semantic_method_calibration`，不得因静态测试通过把阶段5记为PASS。

## 19. legacy strict_audit 40例EFFECTIVE但没有全量授权

返回一项等待用户决定，不得把40例授权扩大为全量筛查授权。

## 20. 外部模型没有连接器

生成 `manual_external_handoff` 任务包并停止；不得声称已自动调用Claude或Grok。

## 21. 全量完成但反向审计未通过

只路由 `semantic_reverse_audit`，继续阻断公司匹配、路线池和客户搜索。

## 22. 全量阶段PASS但没有正式底座写入授权

不得写共享应用底座；阶段验收与底座写入是两个授权门。

## 23. 单条UNVERIFIED返回

保持该关系为unknown/hypothesis并继续按批次规则处理，不得升级supported，也不得无条件把整个批次判死。

## 24. 用户不愿维护机器附页

控制器只展示一项人类任务和必要业务摘要，后台证据与模型包由系统保存。

## 25. 术语桥文件存在但哈希缺失

R4 工作区里有一个名为术语桥的文件，但 `terminology_bridge_sha256` 为空，或重算后与登记哈希不一致。即使后面已有模型回答，控制器也必须保持 `first_incomplete_stage: industry_semantic_expansion`，只路由 `content_first_contract_prepare`，不得将文件存在当成冻结证据。

## 26. 开发回归混入正式保留集

10个已暴露开发案例的某些结果被填进正式计数，或 `development_regression_only` 被改为 false。控制器必须判定开发污染。`not_started / in_progress / UNVERIFIED → content_first_calibration_review (development-only)`，只执行或复核开发集；`FAIL → content_first_contract_prepare`，修复方法并重锁合同。任何情况都不得将开发结果计入正式准确性或 `CONTENT_CALIBRATION_PASS`。

## 27. 正式 30 + 10 比例或来源链漂移

正式案例数仍为40，但不再是30个 `retained_r3_unexecuted` 加10个 `new_unseen_positive`，或其 `formal_holdout_provenance_state` 不是 PASS。控制器只路由 `semantic_calibration_case_prepare`，不得因总数是40而进入正式评分。

## 28. 六个稳定性重复缺失

80个正式成对任务已收齐，但没有真实 `paired_task_manifest_sha256`；或 `stability_repeat_state` 仍为 not_started、UNVERIFIED，少于预声明的6例，或没有真实 `stability_task_manifest_sha256`。控制器必须路由 `content_first_calibration_review`，不得信任自报PASS，也不得把正式40例结果写成完整校准。

## 29. 新 R4 合同试图降级为严格审计

一份明确声明 `content_first` 的 R4 合同删掉新字段，企图利用历史缺省规则改走 `strict_audit` 并用 EFFECTIVE 放行。控制器必须判定合同降级/结构漂移；只有真正缺少模式字段的历史 beta.3 合同才能走兼容路径。

## 30. 平台审计被误当成内容门

原始回答字节、输入哈希、真值和评分卡完整，但 `platform_audit_state` 为 UNVERIFIED。控制器必须分开记录：不得删除可评分内容或把内容结论强制改为FAIL；反之，平台审计PASS也不得替代缺失的真值、评分卡或receiver证据。

## 31. 内容校准通过后尝试越权释放下游

状态仅到 `CONTENT_CALIBRATION_PASS`，但后期文件要求立即写共享应用底座、进入公司匹配或搜索客户。控制器只能进入独立 `content_first_full_screening_gate`，并在任何情况下保持 `RESEARCH_ONLY_BLOCKED`；结构测试或内容PASS都不是下游授权。

## 32. 全量状态自报已授权但没有独立收据绑定

状态文件把 `content_full_screening_state` 或 `full_screening_authorization` 改成已授权，但 `content_full_screening_authorization_reference`、`content_full_screening_authorization_receipt_reference`、`content_full_screening_authorization_receipt_sha256`、`content_terminal_scope_sha256` 任一为空、错配或未由Task 8 gate绑定当前最终合同、校准报告和末端范围。控制器必须回到 `content_first_full_screening_gate (NOT_AUTHORIZED)`，不得信任布尔值或状态自报，并继续保持 `RESEARCH_ONLY_BLOCKED`。
