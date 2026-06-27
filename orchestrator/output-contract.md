# outputs合约

教学设计、教师参考答案、教材参考解答和复习讲义使用 YAML front matter。学生投屏课件为 Typora 纯 Markdown，不设置 YAML front matter。

---

## 1. outputs目录

教学设计、课件、课堂提问参考答案和复习讲义写入 `outputs/`；教材问题参考解答作为knowledge资产写入 `knowledge/solutions/`：

| 产物 | 文件名 |
|------|--------|
| 教学设计 | `outputs/{课时名}_教学设计.md` |
| Markdown 课件 | `outputs/{课时名}_课件.md` |
| 课堂提问参考答案 | `outputs/{课时名}_课堂提问参考答案.md` |
| 教材问题参考解答 | `knowledge/solutions/solution-{lesson_id}.md` |
| 复习讲义 | `outputs/g8-reviews/{讲义编号}_{讲义名称}_复习讲义.md` |
| outputs图片 | `outputs/images/{图片文件名}` |

---

## 2. YAML 元数据

每个outputs Markdown 必须以如下结构开头：

```yaml
---
content_type: lesson | courseware | question_reference | review_lesson
lesson_id: ""
lesson_name: ""
command: lesson-collab | courseware-collab | 复习讲义
workflow_version: v2
review_status: draft | pending_human_review | 审核通过 | rejected
source_files: []
created_at: ""
---
```

其中 `/lesson-collab` 的 `source_files` 至少包含对应教材原文、课标、学情数据和：

```yaml
  - "knowledge/solutions/solution-{lesson_id}.md"
```

教材问题参考解答使用独立元数据：

```yaml
---
content_type: textbook_solution
lesson_id: ""
lesson_name: ""
command: 教材问题解答
workflow_version: v2
source_files: []
created_at: ""
---
```

该knowledge产物不设置 `review_status`。正常题目不设置状态字段。

复习讲义使用独立元数据：

```yaml
---
content_type: review_lesson
lesson_id: ""
lesson_name: ""
command: 复习讲义
workflow_version: v2
source_files: []
created_at: ""
---
```

复习讲义不设置 `review_status`。

### 字段规则

- `content_type`：outputs类型。
- `lesson_id`：课时唯一标识，同一课时的教学设计、课件、课堂提问参考答案必须一致。
- `lesson_name`：课时名称，与文件名主体一致。
- `command`：生成该文件的命令。
- `workflow_version`：当前固定为 `v2`。
- `review_status`：人工审核状态。
- `source_files`：本产物直接读取的上游文件。
- `/lesson-collab`、`/courseware-collab` 产物必须在 `source_files` 中登记对应课时的 `knowledge/solutions/solution-{lesson_id}.md`；缺失时不得生成产物。
- `/复习讲义` 产物必须在 `source_files` 中登记所有被整理的 `knowledge/reviews/` 源文件。
- `created_at`：生成时间，格式建议为 `YYYY-MM-DD HH:mm`。

---

## 3. 内容类型

| content_type | 生成命令 | 用途 |
|--------------|----------|------|
| lesson | `/lesson-collab` | 教学设计 |
| courseware | `/courseware-collab` | Markdown 课件 |
| question_reference | `/courseware-collab` | 教师手持课堂提问参考答案 |
| textbook_solution | `/教材问题解答` | 教材全部问题的参考解答knowledge |
| review_lesson | `/复习讲义` | 综合复习讲义 |

---

## 4. 稳定 ID 规则

关键对象必须携带稳定 ID，供下游引用和validators检查。

| 对象 | ID 格式 | 示例 |
|------|---------|------|
| 基础层学习目标 | `LO-B-序号` | `LO-B-01` |
| 中间层学习目标 | `LO-M-序号` | `LO-M-01` |
| 拓展层学习目标 | `LO-E-序号` | `LO-E-01` |
| 评价任务 | `AS-层级-序号` | `AS-B-01` |
| 学习活动 | `ACT-层级-序号` | `ACT-M-01` |
| 课堂提问 | `ASK-层级-序号` | `ASK-E-01` |

层级代码：

- `B`：基础层
- `M`：中间层
- `E`：拓展层

课堂提问除稳定 ID 外，正文结构强制为：

```yaml
ASK_B_01
提问: ""
备用提示1: "仅在学生停滞或答偏时使用"
备用提示2: "按需增加"
教师参考预期: "供教师判断学习证据，不向学生呈现"
```

禁止把提示写在提问之前，禁止使用旧字段 `提示`、`预期` 代替 `备用提示`、`教师参考预期`。

---

## 5. 题源字段

任何题目、例题、练习、评价任务、作业题都必须携带题源。单题使用：

```yaml
source_id: ""
source_type: textbook | exercise_bank | curriculum_repository
question_id: ""
```

同一任务引用多道题，且 `source_id`、`source_type` 完全相同时，应合并共享字段并使用列表：

```yaml
source_id: ""
source_type: textbook | exercise_bank | curriculum_repository
question_ids:
  - ""
  - ""
```

`question_id` 与 `question_ids` 二选一。禁止把多个编号写入一个逗号分隔的 `question_id` 字符串，也禁止重复outputs相同的 `source_id`、`source_type`。

禁止出现无来源题目。禁止将 LLM 生成题、仿题、类题、改写题作为新题使用。

---

## 6. 分层命名

全系统只允许使用以下层级名称：

- 基础层
- 中间层
- 拓展层

禁止使用旧的中间层别名作为系统层级名称。

---

## 7. 图片引用

任意 Markdown 文件引用图片时，只允许引用该文件同级目录下的 `images/` 子目录。学生课件使用 Typora 原生 Markdown：

```markdown
![图注](./images/xxx.jpg)
```

禁止：

- 空图注 Markdown 图片 `![]()`
- 学生课件中的 HTML 图片标签
- 跨目录引用knowledge图片
- 引用旧资源目录图片
- 绝对路径

复习讲义使用 Markdown 图片语法：

```markdown
![](images/xxx.jpg)
```

图片必须位于复习讲义文件同级 `images/` 目录；禁止跨目录引用。

---

## 8. `/lesson-collab` 模板

教学设计正文必须采用"双层结构"，在同一个 Markdown 文件中同时服务课堂实施和系统审核：

| 层级 | 使用者 | 作用 | 内容边界 |
|------|--------|------|----------|
| 第一层：课堂实施导航 | 任课教师 | 备课速览、课堂执行 | 只保留核心问题、时间流程、实施要点、核心提问、课堂练习与作业 |
| 第二层：完整结构化设计 | 审核者、validators、课件生成流程 | 教学评审核、题源追踪、下游复用 | 保留目标、评价、问题链、活动、题源、作业、一致性矩阵和质量记录 |

### 8.1 第一层：课堂实施导航

一级标题之后先给出阅读建议，再按以下固定顺序outputs：

```markdown
> **阅读建议**：日常备课先看"课堂实施导航"和"课堂实施要点"；需要审核目标、评价、题源或提问细节时，再展开文末的"完整结构化设计"。

## 课堂实施导航

### 本课要解决的问题

### {duration}分钟流程总览

| 时间 | 教学环节 | 学生主要任务 | 教师支持 | 达成结果 |

### 课堂实施要点

### 核心提问

### 课堂练习与作业
```

第一层规则：

- 流程总览每行对应第二层一个 `ACT-*` 活动，顺序、时间和任务含义必须一致。
- 使用教师可直接执行的自然语言，不出现 `LO-*`、`AS-*`、`ACT-*`、`ASK_*`、`source_id`、`source_type`、`question_id` 等后台标记。
- 课堂实施要点只保留本课最关键的操作、易错点和反馈策略，不重复完整活动步骤。
- 课堂练习与作业必须分别列明，不得用"见下文"代替。

### 8.2 第二层：完整结构化设计

第一层之后使用 HTML 折叠块包裹第二层：

```markdown
<details>
<summary><strong>展开完整结构化设计（目标、评价、活动、题源及审核信息）</strong></summary>

> 以下内容供教学审核、题源追踪和后续课件生成使用。英文编号与字段为系统识别标记，不要求教师在课堂中呈现。

## meta

- module:
- grade:
- topic:
- duration: 40分钟以内

## knowledge_analysis

## objectives

### 基础层
- LO-B-01：...

### 中间层
- LO-M-01：...

### 拓展层
- LO-E-01：...

## assessment

- AS-B-01：
  - aligned_objective: LO-B-01
  - source_id:
  - source_type:
  - question_id:

## problem_chain

## lesson_flow

## practice

## homework

## boardwork

## consistency_matrix

## quality_check

</details>
```

第二层继续遵守全部稳定 ID、题源和教学评一致性规则，不因折叠而省略字段。

`lesson_flow` 中每个活动还必须包含 `time_priority` 和完整 `time_budget`。教学设计outputs前必须运行教学活动时间validators；不通过时回退活动设计，有条件通过时在课堂实施要点中明确可后移任务。

### 8.3 双层一致性

- 第一层"本课要解决的问题"必须与第二层核心问题一致。
- 第一层流程总览与第二层 `lesson_flow` 的活动数量、顺序和总时长一致。
- 第一层课堂练习、作业必须能在第二层 `practice`、`homework` 中找到对应任务，不新增无题源任务。
- 修改任一层后必须同步检查另一层；禁止第一层便于阅读但失真，也禁止第二层完整但第一层无法直接执行。

---

## 9. `/courseware-collab` 模板

```markdown
### 📐 标题页

学生可见内容

---

### 🎯 本课目标
```

课件只使用 Typora 可直接渲染的标题、段落、列表、表格、公式、水平线和 Markdown 图片；不写 YAML、HTML、代码块或后台字段。
