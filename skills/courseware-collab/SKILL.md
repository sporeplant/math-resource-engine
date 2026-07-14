---
name: courseware-collab
description: >
  Use for /courseware-collab or equivalent requests to generate a collaborative
  Markdown courseware file and classroom-question dispatch from a human-approved
  lesson design. Runs three confirmation gates: structure, question quality, and
  student assignment.
---

# `/courseware-collab` skills

## 1. 边界

- 只消费 `content_type: lesson` 且 `review_status: 审核通过` 的教学设计。
- 只生成 `outputs/{课时名}_课件.md` 与 `outputs/{课时名}_课堂提问调度稿.md`。
- 不重新生成学习目标、评价任务、活动设计或教学设计。
- 图片只允许引用outputs文件同级 `./images/{文件名}`，禁止 Markdown 图片语法。
- 学生姓名只来自 `students/scores.md`，禁止虚构。
- 课件必须把教材原文中支撑学生作答的材料转化为课件可见内容；禁止只依据教学设计摘要生成页面。
- 每个课堂提问必须有课件内可见材料锚点。若问题依赖教材背景、原始数据、统计表、方案表、图形或练习题干，必须在问题出现前或同页呈现对应材料。

## 2. 分阶段强制读取

### 启动与课题确认前读取

1. `AGENTS.md`
2. `orchestrator/skill-protocol.md`
3. `orchestrator/workflow-registry.md` 的 `/courseware-collab`
4. `orchestrator/output-contract.md`
5. `orchestrator/image-protocol.md`
6. `orchestrator/review-protocol.md`
7. `knowledge/textbooks/教材原文_教材课时分配.md`
8. 对应课时的教学设计、教材原文、练习册题库
9. 对应课时的练习册索引 `knowledge/workbook-index/workbook-index-{lesson}.yaml`（如存在）
10. 对应课时的练习册答案 `knowledge/workbook-answers/workbook-answer-{lesson}.md`（如存在）

### 确认门1前读取

- `skills/courseware/SKILL.md` 与 `skills/courseware/checklist.md`
- 对应教材原文中所有支撑作答的材料：实际问题背景、原始数据、教材步骤、统计表/方案表、教材图片、练习题干或题干摘要

### 确认门2前读取

- `skills/ask-check/SKILL.md` 与 `skills/ask-check/checklist.md`

### 确认门3前读取

- `skills/tier-ask/SKILL.md` 与 `skills/tier-ask/checklist.md`
- 学生成绩数据、提问历史记录

### 生成与验证前读取

- `skills/question-dispatch/SKILL.md` 与 `skills/question-dispatch/checklist.md`
- `skills/images/SKILL.md`
- `validators/question-dispatch/rules.md`
- `validators/courseware/rules.md`
- `validators/images/rules.md`

## 3. 执行流程

1. 课题确认：匹配课时，检查教学设计存在且为 `审核通过`，显示章节、节次、课时、文件、状态，等待教师确认。
1b. 练习册资源就绪检查（详见 orchestrator/quality-gates.md §6）：检查题库/答案/索引三级存在性，有题库+答案但无索引时终止并提示补齐。已存在的索引文件在后续步骤中优先用于练习册题的分层匹配和答案复用。
2. 确认门1：课件结构规划。页面顺序必须对应教学设计 `lesson_flow`，并标注教材对应位置、页面用途和教材材料来源。必须同时呈现“教材材料转化清单”，逐项说明教材原文中的背景、原始数据、表格、图片、练习题干或题干摘要安排到哪一页；缺失任一支撑作答材料时不得进入确认。
3. 确认门2：课堂提问设计。呈现前必须按提问质量skills自检；低质量、冗余或脱节问题必须先删除、合并或改写。每个问题必须标注“材料锚点页”，证明学生在课件内可见材料基础上可以作答；缺少材料锚点的问题必须回退到确认门1补页或补材料。
4. 确认门3：分层提问分配。按学生成绩数据和提问历史记录分配真实学生，遵守 `skip`、`priority` 与不重复规则。
5. 基于已确认的结构、提问、学生分配生成课堂提问调度稿。
6. 基于已确认内容生成 Markdown 课件。生成前必须执行“教材材料锚点复核”：逐页核对确认门1材料清单与确认门2问题锚点是否全部落入课件正文。
7. 依次执行课堂提问调度稿验证、课件验证、图片验证和 `tools/validate_output.py`。

教师未确认当前确认门前，不得进入下一步；教师提出修改意见时，必须修订并重新呈现当前确认门。

## 4. 确认门outputs要求

每个确认门使用orchestrator确认门模板，并列出 3-5 条“需要您确认的关键点”。

确认门2的表格必须包含：

| 编号 | 问题页 | 备用提示页 | 材料锚点页 | 对应教学设计 | 问题内容 | 分级备用提示 | 教师参考预期 | 提问层级 | 产出形式 | 质量自检 |
|---|---:|---|---|---|---|---|---|---|---|---|

课件呈现纪律：

- 学生课件按“问题页 → 按需备用提示页 → 答案/归纳页”排列。
- 问题页不得提前显示提示、答案或教师参考预期。
- 备用提示可另页分级呈现，但学生课件不得显示 `ASK_*` 编号；无须提示时可不生成提示页。
- `教师参考预期`、具体学生姓名、备用学生和即时调整规则只写入课堂提问调度稿，不得写入学生课件。

确认门1必须额外包含“教材材料转化清单”：

| 教材材料 | 教材对应位置 | 课件安排页 | 转化方式 | 是否支撑提问/练习 |
|---|---|---:|---|---|

其中“教材材料”至少检查：

- 实际问题背景或题干背景。
- 原始数据或题目数据。
- 教材关键步骤与计算式。
- 频数表、频率表、方案表等统计表。
- 教材图片或图形。
- 课堂练习/检测所需题干摘要和图表。

## 5. outputs元数据

课件 front matter 必须包含：

```yaml
content_type: courseware
lesson_id: ""
lesson_name: ""
command: courseware-collab
workflow_version: v2
review_status: draft
source_files:
  - "outputs/{课时名}_教学设计.md"
created_at: "YYYY-MM-DD HH:mm"
collab_gates:
  - gate: structure_planning
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
  - gate: question_design
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
  - gate: student_assignment
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
```

课堂提问调度稿必须引用同一 `lesson_id`、`lesson_name` 和同一上游教学设计文件。

## 6. 验证命令

最终outputs前运行：

```powershell
python tools/validate_output.py outputs/{课时名}_课件.md --lesson-file outputs/{课时名}_教学设计.md --question-reference outputs/{课时名}_课堂提问调度稿.md --students-file students/scores.md
```

验证不通过时，回退到对应确认门或生成步骤修正，不得交付不合格文件。

## 7. 教材材料锚点自检

最终交付前必须逐项确认：

- 课件中没有“看教材数据”“根据教材图表”等空引用；若出现，必须同时提供课件内可见的数据、图表或题干摘要。
- 所有结构化提问在出现前或同页已有材料锚点。
- 统计/数据课必须呈现原始数据、频数表/频率表、方案表或题目图表等关键材料。
- 练习/检测页若只出示题号，必须保证学生手边教材可直接使用；若问题需要图表判断，课件需呈现对应图表或简要题干。
- 新增或迁移的图片必须确认已存在于 `knowledge/images/`（详见 `orchestrator/image-protocol.md`），最终课件使用对应 CDN URL。
