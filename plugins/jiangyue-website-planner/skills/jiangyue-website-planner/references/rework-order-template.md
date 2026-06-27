# Rework Order Template

Use this when imagegen fails for a strategic reason, or when the user reviews a delivered image and planner must turn the feedback into a controlled next-round direction.

```text
返工修订单

- 触发返工的失败类型：
- 是执行问题还是策略问题：
- 用户反馈中的硬性问题：
- Planner 缺陷登记：
  - 用户原话 / 标注：
  - 可见缺陷：
  - planner 分类：
  - 是否阻止交付：
  - 关闭缺陷所需证据：
- 原图片需求哪里不成立：
- 页面目标是否变化：
- 首屏注意力层级修正：
- 图片角色修正：
- 品牌色 / 构图 / 版面融合修正：
- 必须保留的信息：
- 应移出图片、交给 HTML / 页面文案的信息：
- 需要删除或降低优先级的信息：
- 重新定义后的图片任务：
- 推荐的 2-3 个新图片方向：
- 禁止 imagegen 再尝试的旧方向：
- 参考归因：
  - 已用于当前版本：
  - 对话中提到但未用于当前版本：
  - 下一版必须参考：
  - 不得暗示已使用的参考：
- 下一步路由：继续 imagegen / 修改 Planner Brief / 失败重置 / 停止图片工作
- 是否要求 imagegen 执行 failure-reset-hard-gates：
- 是否需要调整 H1 / CTA / 页面模块：
- 下一版验收标准：
- 给 imagegen 的新版图片需求简报：
```

## Rework Standard

Do not return a vague instruction such as "make it better." The rework order must change task boundaries, message ownership, attention hierarchy, image role, forbidden direction, or visible pass/fail criteria.

If the page strategy remains correct and only local visual execution is poor, send the image back to imagegen for execution fixes. If the user feedback concerns brand direction, layout integration, visual hierarchy, color system, or credibility for B2B buyers, use planner to produce a next-round optimization order before imagegen continues.

If the user named a visible defect, marked an image, challenged self-check, or disputed reference use, the rework order must include the defect register and reference attribution fields. If the same blocking defect remains after one imagegen revision, do not send another vague rework order; run planner failure reset or require imagegen hard-gate reset.
