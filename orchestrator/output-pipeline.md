# outputs流水线

定义各阶段outputs文件、顺序、依赖关系与审核状态。

---

## 1. 各阶段outputs文件

| 阶段 | 产出文件 | 格式 |
|------|----------|------|
| 教材分析 | lesson-{id}-textbook-analysis.md | Markdown |
| 学习目标 | lesson-{id}-outcomes.md | Markdown |
| 评价任务 | lesson-{id}-assessment.md | Markdown |
| 教学活动 | lesson-{id}-activities.md | Markdown |
| 课时设计 | lesson-{id}-lesson-plan.md | Markdown |
| Markdown课件 | {课时名}_课件.md | Markdown |
| 审核报告 | lesson-{id}-review-report.md | Markdown |

---

## 2. outputs顺序

1. 教材分析（可并行）
2. 学习目标
3. 评价任务
4. 教学活动
5. 课时设计
6. Markdown课件（`/courseware-collab`，需人工审核通过的教学设计）
7. 审核报告（最终）

---

## 3. outputs依赖关系

- 学习目标依赖教材分析
- 评价任务依赖学习目标
- 教学活动依赖学习目标和评价任务
- 课时设计依赖学习目标、评价任务、教学活动
- Markdown课件依赖人工审核通过的课时设计
- 审核报告依赖所有前置outputs

---

## 4. outputs审核状态

| 状态 | 含义 |
|------|------|
| draft | 初始草稿，尚在生成中 |
| pending_review | 待审核，已提交到对应Validator |
| reviewed_pass | 审核通过 |
| reviewed_conditional | 有条件通过，附修改建议 |
| reviewed_fail | 审核不通过，需回退修正 |
| published | 最终发布版本 |

---

## 5. 最终资源包结构

```
lesson-{id}/
├── metadata.yaml              # 元数据
├── lesson-{id}-textbook-analysis.md
├── lesson-{id}-outcomes.md
├── lesson-{id}-assessment.md
├── lesson-{id}-activities.md
├── lesson-{id}-lesson-plan.md
├── {课时名}_课件.md
├── lesson-{id}-review-report.md
└── assets/
    ├── images/
    └── resources/
```
