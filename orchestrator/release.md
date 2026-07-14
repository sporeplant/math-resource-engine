# 最终发布策略

定义outputs进入 outputs/ 目录的条件和流程。

---

## 发布条件

只有全部 Validator 审核通过，才允许进入 outputs/ 目录。

### 必须满足

- [ ] 学习目标validators 审核通过
- [ ] 评价validators 审核通过
- [ ] 活动validators 审核通过
- [ ] 教学设计validators 审核通过
- [ ] 一致性validators 审核通过
- [ ] 数学严谨性评分 ≥ 90（自评可选，正式发布必须）
- [ ] outputs文件元数据完整（lesson_id, version, review_status）

---

## 发布流程

```
所有Validator通过
   ↓
更新 lesson_lifecycle 状态为"已发布"
   ↓
按 outputs流水线.md 组织资源包
   ↓
写入 outputs/{lesson_id}/ 目录
   ↓
更新 skills注册表.md 中的版本号
   ↓
生成发布记录
```

---

## outputs/ 目录结构

```
outputs/
├── {lesson_id}/
│   ├── lesson-{id}-textbook-analysis.md
│   ├── lesson-{id}-outcomes.md
│   ├── lesson-{id}-assessment.md
│   ├── lesson-{id}-activities.md
│   ├── lesson-{id}-lesson-plan.md
│   ├── lesson-{id}-courseware-structure.md
│   ├── lesson-{id}-exercise-analysis.md
│   ├── lesson-{id}-review-report.md
│   └── assets/
├── reports/
├── archive/
└── templates/
```

---

## 特殊情况

- 人工强制通过的版本不可进入 outputs/，需存放在 `outputs/draft/{lesson_id}/`
- 审核有条件通过且教师确认后，可标记为"有条件发布"
- 有条件发布的版本需要在下一次修订时补全审核流程