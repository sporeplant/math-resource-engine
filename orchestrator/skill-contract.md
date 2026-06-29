# skillsoutputs合约

本文件定义 Skill 之间传递内容的最小接口。最终落盘文件仍必须符合 `orchestrator/output-contract.md`。

---

## 1. 通用返回结构

所有 Skill outputs必须包含：

- `content_type`
- `payload`
- `source_files`
- `must_be_valid_markdown: true`

`payload` 必须是 Markdown 片段，不outputs JSON 作为最终正文。

---

## 2. 分层与 ID

所有涉及分层的 Skill 必须使用：

- 基础层
- 中间层
- 拓展层

禁止使用旧的中间层别名。

所有关键对象必须带稳定 ID：

- 学习目标：`LO-B-01`、`LO-M-01`、`LO-E-01`
- 评价任务：`AS-B-01`、`AS-M-01`、`AS-E-01`
- 学习活动：`ACT-B-01`、`ACT-M-01`、`ACT-E-01`
- 课堂提问：`ASK-B-01`、`ASK-M-01`、`ASK-E-01`

---

## 3. 题源强约束

以下 Skill 涉及题目使用，必须执行题源探索并携带来源字段：

- 习题分析skills
- 评价设计skills
- 活动设计skills
- 教学设计skills
- 课件设计skills
- 教材问题解答skills

单题必须携带：

```yaml
source_id: ""
source_type: textbook | exercise_bank | curriculum_repository
question_id: ""
```

同一评价、活动或作业引用多道同源题时，必须合并共享题源：

```yaml
source_id: ""
source_type: textbook | exercise_bank | curriculum_repository
question_ids:
  - ""
  - ""
```

`question_id` 与 `question_ids` 二选一；禁止逗号拼接多个编号，禁止重复相同题源字段。

禁止：

- LLM 自行生成新题
- 改写后当作新题使用
- 仿题、类题、变式题替代题库题
- 无来源题目进入outputs

教材问题解答skills沿用同等题源强约束，并额外使用中文“答案来源”字段：

```yaml
source_id: ""
source_type: textbook
question_id: ""
教材位置: ""
答案来源: 教材原文 | AI参考推导 | AI参考推导补充
```

---

## 4. `/lesson-collab` 上游片段

### 学习目标skills

outputs：

- `content_type: objectives`
- 三层目标
- 每条目标带 `LO-*` ID

### 评价设计skills

outputs：

- `content_type: assessment`
- 每项评价带 `AS-*` ID
- 每项评价引用 `aligned_objective`
- 涉及单题时带 `source_id/source_type/question_id`；涉及多道同源题时带 `source_id/source_type/question_ids`

### 活动设计skills

outputs：

- `content_type: activities`
- 每个活动带 `ACT-*` ID
- 每个活动引用目标和评价任务
- 每个活动包含反馈节点
- 每个 `ASK_*` 按 `提问 → 备用提示1/2/3 → 教师参考预期` 排列；备用提示仅在学生停滞或答偏时逐级使用

### 教学设计skills

outputs：

- `content_type: lesson`
- 完整课时设计 Markdown
- 总时长不超过 40 分钟
- 只标注提问层级，不写学生姓名

---

## 5. `/courseware-collab` 下游片段

### 分层提问skills

outputs：

- 学生选取结果
- 问题-学生映射表
- 每个提问带 `ASK-*` ID
- 学生姓名来自 `students/scores.md`
- 同一课时同一学生不重复，除非该层人数不足并记录原因

### 课件设计skills

outputs：

- `content_type: courseware`
- Markdown 课件
- 使用 `./images/{文件名}` 引用图片
- 不重新生成目标、评价、活动，只转化人工审核通过的教学设计
- 学生课件按“问题页→按需备用提示页→答案/归纳页”揭示，且不得出现 `教师参考预期`

### 课堂提问调度稿生成skills

- 教师手持课堂提问调度稿中的每个 `ASK_*` 按“问题→分级备用提示→参考答案→评分要点”排列

---

## 6. validatorsoutputs

validatorsoutputs必须包含：

- result: `通过 | 有条件通过 | 不通过`
- checked_file
- failed_rules
- fix_suggestions
- rollback_target

validators不得修改 `review_status` 为 `审核通过`。

---

## 7. 教材问题解答skills

outputs：

- `content_type: textbook_solution`
- 完整教材任务清单
- 按教材原文顺序排列的逐题参考解答
- 每题携带标准题源字段、认知层级和中文答案来源
- 覆盖统计

本产物不设置 `review_status`。正常题目不设置状态字段；仅异常题设置 `生成状态: 暂停` 和 `异常原因`。
