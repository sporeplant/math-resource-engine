# Validator执行顺序

定义系统中所有Validator的执行顺序。

---

## 标准执行顺序

```
学习目标Validator（学习目标validators）
   ↓
评价Validator（评价validators）
   ↓
活动Validator（活动validators）
   ↓
教学活动时间Validator（教学活动时间validators）
   ↓
课时设计Validator（教学设计validators）
   ↓
教学法Validator（教学法validators）
   ↓
数学Validator（数学validators）
   ↓
学情适配Validator（学情适配validators）
   ↓
课件Validator（课件validators）——仅在课件生成启用时执行
   ↓
一致性Validator（一致性validators）
```

---

## 执行规则

- Validator必须按顺序执行
- 前置Validator未通过时，后续Validator不执行
- 前置Validator返回"有条件通过"时，后续Validator继续执行
- 教学活动时间validators的“有条件通过”必须同时给出可后移的 `flex` 或 `backup` 活动
- 同一Validator在同一时间只执行一个审核任务
- 所有Validator通过后才能进入发布流程
- `/教材问题解答` 独立执行“教材问题解答validators”，不进入教学设计与课件验证链。
- `/复习讲义` 独立执行“复习讲义validators”，不进入教学设计与课件验证链。

---

## 优先级说明

- 数学Validator（数学validators）优先级高：在最终发布前必须确保数学正确性
- 教学法Validator（教学法validators）优先级中：确保教学法合规
- 教学活动时间Validator优先级高：确保核心活动能够在40分钟内完成
- 学情适配Validator（学情适配validators）优先级中：确保方案适配学生
- 课件Validator（课件validators）优先级中：仅当课件生成启用时执行，确保课件符合模板结构
- 一致性Validator（一致性validators）优先级最高：最终把关
- 生产模式下Validator不可跳过
- 开发模式下可配置跳过部分Validator
