# 依赖图

定义Skill之间的依赖关系和执行顺序。

---

## 依赖链条

```
学习目标skills
       ↓
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

## 已归档节点

- 板书设计skills：已归档到 `archive/skills_暂停使用/`，不属于当前主链。
- 数学活动课设计skills：已归档到 `archive/skills_暂停使用/`，不属于当前主链。
