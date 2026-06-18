# Rework Order Template

Use this when imagegen fails for a strategic reason, or when the user reviews a delivered image and planner must turn the feedback into a controlled next-round direction.

```text
返工修订单

- 触发返工的失败类型：
- 是执行问题还是策略问题：
- 用户反馈中的硬性问题：
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
- 是否需要调整 H1 / CTA / 页面模块：
- 下一版验收标准：
- 给 imagegen 的新版图片需求简报：
```

## Rework Standard

Do not return a vague instruction such as "make it better." The rework order must change task boundaries, message ownership, attention hierarchy, image role, forbidden direction, or visible pass/fail criteria.

If the page strategy remains correct and only local visual execution is poor, send the image back to imagegen for execution fixes. If the user feedback concerns brand direction, layout integration, visual hierarchy, color system, or credibility for B2B buyers, use planner to produce a next-round optimization order before imagegen continues.
