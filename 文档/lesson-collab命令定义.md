# `/lesson-collab` 命令定义

> 最后更新：2026-06-05

---

## 命令名称

`/lesson-collab`

## 输入格式

```text
/lesson-collab 课时名称
```

---

## 权威流程

`/lesson-collab` 的唯一权威流程见：

> `主控/工作流注册表.md` → `2a. /lesson-collab 工作流（对话式设计）`

本文件只说明命令边界，不重复维护步骤链。

---

## 命令边界

- `/lesson-collab` 只生成 `输出/{课时名}_教学设计.md`。
- `/lesson-collab` 是 **对话式设计流程**，需要教师通过 4 个确认门逐步确认设计内容。
- `/lesson-collab` 输出必须包含 YAML front matter。
- `/lesson-collab` 输出的 `command` 字段必须为 `lesson-collab`。
- `/lesson-collab` 输出的 `review_status` 初始为 `pending_human_review`，全部确认门完成且教师确认后，教师手动改为 `human_approved`。
- `/lesson-collab` 不生成课件。
- `/lesson-collab` 不生成课堂提问参考答案。
- `/lesson-collab` 不执行课件验证器或图片资源验证器。
- `/lesson-collab` 中不得写入具体学生姓名，只能标注提问层级。

---

## 输出要求

```yaml
---
content_type: lesson
lesson_id: ""
lesson_name: ""
command: lesson-collab
workflow_version: v2
review_status: pending_human_review
source_files: []
created_at: ""
collab_gates:
  gate_1_knowledge: "confirmed"
  gate_2_goals: "confirmed"
  gate_3_assessment: "confirmed"
  gate_4_1_textbook_order: "confirmed"
  gate_4_2_steps: "confirmed"
  gate_4_3_questions: "confirmed"
  gate_4_4_integration: "confirmed"
---
```

---

## 确认门交互协议

详见 `主控/技能调用协议.md` → `§2a. /lesson-collab 强制步骤链`。

**各确认门关键决策点：**

- **Gate 1 知识分析确认**：课型判断、重难点定位、常见误解、知识生长路径
- **Gate 2 学习目标确认**：三层目标、行为动词、题量、与课标贴合度
- **Gate 3 评价设计确认**：评价-目标对应、成功标准、题目选用
- **Gate 4-1 教材顺序与模块任务确认**：模块顺序与教材一致性、任务类型匹配（读懂/思考/交流/书写/操作）
- **Gate 4-2 活动步骤逐步确认**：活动步骤合理性、时间分配、学生行为、反馈节点
- **Gate 4-3 台阶提问确认**：问题编号（ASK_B_XX / ASK_M_XX / ASK_E_XX）、具体指向性提示、对结论的负责程度
- **Gate 4-4 整体整合确认**：整体连贯性、教材对应位置、题源、升华

---

## 红线规则

`/lesson-collab` 必须遵守 `AGENTS.md` 红线规则，特别注意：

- **第14条**：提问未对结论负责（提问无论学生怎么回答都无法引向核心结论，或缺少具体指向性提示）
- **第9条**：活动顺序打乱了教材原文内容模块的先后顺序
- **第10条**：活动未标注 `教材对应位置` 字段

---

## 后续动作

教师完成所有确认门对话并审核通过教学设计后，将元数据改为：

```yaml
review_status: human_approved
```

只有人工审核通过后的教学设计才能作为 `/courseware` 的输入。
