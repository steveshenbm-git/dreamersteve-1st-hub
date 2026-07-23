# 记录与集成边界

## 正式归档

只归档实际收件和实际发件及其附件。AI 分析、预稿、修改原因和版本差异不得进入正式客户邮件档案。

- 在手动测试阶段，业务员实际发送后，再导入实际发件内容以完整邮件线程。
- 不将 AI 预稿标记为“已发送”。
- 不使用正式档案之外的 AI 中间产物进行自动训练或自动修改公司标准。

## 测试公司隔离

测试公司资料与江樾资料必须使用不同根目录；不得跨根目录读取、引用或写入业务事实。

- 将测试公司的公司知识、客户资料、联系人资料和邮件档案限定在测试根目录内。
- 默认排除江樾资料；未来迁移时，为江樾重新建立数据配置，不复制测试公司的业务事实。
- 在接入邮箱 API 或客户关系技能时，将数据层作为可替换依赖，不改变邮件助手的核心使用方式。

## 未来新客户背调只读接口

- company_identity
- website_and_region
- business_type
- main_products
- fit_hypotheses
- contact_identity_and_possible_role
- development_angles
- source_url_or_local_reference
- observed_at
- evidence_state

待验证线索不能作为确定事实写入邮件。第一版不生产上述数据，不实现自动搜索、评分、开发序列或 CRM 写入。

- 仅读取由未来客户关系能力提供的数据，不在邮件助手内创建、修改或版本化客户画像。
- 要求每条线索同时提供 `source_url_or_local_reference`、`observed_at` 和 `evidence_state`；缺失时保持未确认，不自行补全。
- 只使用有证据的可观察沟通信号，不写入缺乏证据的心理标签。
