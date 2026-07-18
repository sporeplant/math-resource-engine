# 依赖图

定义Skill之间的依赖关系和执行顺序。

---

## 依赖链条

```
教材问题解答skills ──┐
                     ├──→ 学习目标skills
教材分析skills ──────┘         ↓
                          评价设计skills
                               ↓
                          活动设计skills
                               ↓
                          教学设计skills
                               ↓
                          课件设计skills
                               ↓
                          一致性validators
```

---

## 详细依赖关系

```
                        ┌─────────────────────────┐
                        │  math-textbook-analysis  │ ← 独立，并行
                        └─────────────────────────┘

                        ┌─────────────────────────┐
                        │  math-exercise-analysis  │ ← 独立，并行
                        └─────────────────────────┘

                        ┌──────────────────────────────────┐
                        │  textbook-question-solutions      │ ← 独立生成，含台阶分析
                        │  （含例题-习题全链台阶分析）        │    供给下游5个技能
                        └──────────────────────────────────┘
                                          ↓
learning-outcome ──→ assessment ──→ activity ──→ lesson-design ──→ courseware
       │                  │              │              │
       ↓                  ↓              ↓              ↓
  outcome-valid      assess-valid    activity-valid   lesson-valid
       │                  │              │              │
       └──────────────────┴──────────────┴──────────────┘
                              ↓
                     一致性validators
                              ↓
                         最终outputs
```

---

## 哪些节点允许并行

- 教材分析skills：与主流程完全并行
- 习题分析skills：与主流程完全并行
- 教材问题解答skills：独立生成，但必须在学习目标开始前完成（含台阶分析）
- 课件设计skills：在 lesson-design 完成并人工审核后执行
- 多个审核节点不能并行：每个审核必须等上游审核完成

---

## 哪些节点禁止跳过

- 学习目标skills：禁止跳过（所有下游依赖目标）
- 评价设计skills：禁止跳过（活动设计依赖评价）
- 活动设计skills：禁止跳过（课时设计依赖活动）
- 所有审核节点：禁止跳过（质量控制必需）
- 一致性validators：禁止跳过（最终校验）
- 课件设计skills：仅在需要生成课件时执行

