---
name: lesson-collab
description: >
  对话式教学设计协作流程。使用 /lesson-collab 命令触发。当用户输入 "/lesson-collab 课时名称" 时，必须使用本skills执行完整的对话式教学设计流程。
  本skills在知识分析、学习目标、评价设计、活动设计四个关键节点设置确认门（Gate），AI 呈现草稿后暂停等待教师审核确认，实现早期纠偏。
  触发关键词：/lesson-collab、对话备课、协作教学设计、课时设计确认、分步确认备课。
  本skills自动读取项目目录下的工作流注册表、AGENTS.md 红线规则、skills调用协议等外部文件，
  并动态读取对应课时的教材原文、课标、练习册题库、学生数据等资源。
---

# `/lesson-collab` 对话式教学设计skills

## 1. 项目根路径

skills运行时，PROJECT_ROOT 为 `E:\OneDrive\math-resource-engine\`。

所有文件引用均相对于 `PROJECT_ROOT`。

## 2. 触发条件

用户输入以下格式的命令：

```text
/lesson-collab 课时名称
```

示例：
```text
/lesson-collab 21.4
/lesson-collab 三角形的中位线
/lesson-collab 21.4 三角形的中位线
```

## 3. 强制前置读取（生成前必须读取）

在开始任何生成步骤前，必须按顺序读取以下文件（相对于 PROJECT_ROOT）：

### 3.1 运行时规则

| 优先级 | 文件 | 原因 |
|--------|------|------|
| 1 | `AGENTS.md` | 全局红线规则（违反任意一条outputs无效） |
| 2 | `orchestrator/workflow-registry.md` | 唯一权威工作流定义 |
| 3 | `orchestrator/skill-protocol.md` | 强制步骤链和禁止事项 |
| 4 | `orchestrator/output-contract.md` | outputs模板和 YAML 元数据规则 |
| 5 | `orchestrator/skill-contract.md` | Skill 间传递接口 |
| 6 | `orchestrator/precheck.md` | 生成前逐项自检 |

### 3.2 核心skills定义

| 文件 | 用途 |
|------|------|
| `skills/knowledge/SKILL.md` | Step01 知识分析 |
| `skills/objectives/SKILL.md` | Step02 学习目标设计 |
| `skills/objectives/checklist.md` | 学习目标自检 |
| `skills/assessment/SKILL.md` | Step03 评价任务设计 |
| `skills/questions/SKILL.md` | 问题链设计 |
| `skills/activities/SKILL.md` | Step05 活动设计 |
| `skills/act-check/SKILL.md` | 活动质量检查 |
| `skills/homework/SKILL.md` | Step06 作业设计 |
| `skills/ask-check/SKILL.md` | 提问质量审查 |
| `skills/ask-check/checklist.md` | 提问质量自检 |

### 3.3 validators定义

| 文件 | 用途 |
|------|------|
| `validators/objectives/rules.md` | 学习目标验证 |
| `validators/assessment/rules.md` | 评价设计验证 |
| `validators/activities/rules.md` | 活动设计验证 |
| `validators/lesson/rules.md` | 教学设计整体验证 |
| `validators/pedagogy/rules.md` | 教学法验证 |
| `validators/math/rules.md` | 数学内容验证 |
| `validators/fit/rules.md` | 学情适配验证 |
| `validators/alignment/rules.md` | 教学评一致性验证 |

### 3.4 课时素材（课题确认后按匹配结果读取）

| 文件 | 路径模式 |
|------|----------|
| 教材课时分配 | `knowledge/textbooks/教材原文_教材课时分配.md` |
| 对应课时教材原文 | `knowledge/textbooks/教材原文_{章节}_{名称}.md` |
| 对应课标 | `knowledge/standards/doc-e0543146.md` |
| 对应课型定义 | `knowledge/types/{课型}.md` |
| 对应练习册题库 | `knowledge/workbooks/` 中匹配的题目 |
| 数学本质分析 | 读取 `knowledge/math-essence/INDEX.yaml`，按 `chapter_refs` 或 `topic_zh` 匹配当前课时；若无匹配则跳过 |
| 对应常见错误 | 读取 `knowledge/common-errors/INDEX.yaml`，按 `domain` 或 `chapter_refs` 匹配；若无匹配则跳过 |
| 对应教学策略 | 读取 `knowledge/teaching-strategies/INDEX.yaml`，按 `domain` 匹配；若无匹配则跳过 |
| 学情行为与反馈 | 读取 `knowledge/learning-theory/learning-behaviors.md`、`knowledge/learning-theory/feedback-strategies.md`、`knowledge/learning-theory/cognitive-layers.md` |
| students | `students/scores.md` |

学情数据读取规则：

- 教学目标、评价设计和活动设计必须读取 `students/scores.md`。
- `knowledge/learning-theory/` 下文件存在时必须全部读取，不得以"未提供"为由跳过。
- `students/example.md` 与 `students/template.md` 仅用于格式说明，不得替代真实学生成绩数据。
- 真实数据文件存在时，禁止以“未提供真实班级近期数据”为由降级使用示例或通用学情。
- 教学设计正文只呈现分层特征和教学适配要求，不写具体学生姓名。

## 4. 课题确认环节

在执行 `/lesson-collab` 强制链之前，必须先完成课题确认。

### 确认流程

```text
解析课时名称（章节号或课时名称）
  ↓
读取 knowledge/textbooks/教材原文_教材课时分配.md
  ↓
匹配对应课时信息
  ↓
显示确认信息（章节、节次、课时、教材文件）
  ↓
等待用户确认（用户回复"确认"、"是"、"对"、"正确"等）
  ↓
用户确认 → 进入强制链
用户否认 → 提示重新输入正确的课时名称
```

### 显示格式

```text
📋 请确认课题信息：

章节：第21章 四边形
节次：21.4 三角形的中位线
课时：第1课时（共1课时）
教材文件：教材原文_21.4_三角形的中位线.md

确认无误后，请回复"确认"或"是"继续生成教学设计。
如需修改，请重新输入正确的课时名称。
```

### 匹配规则

| 输入类型 | 匹配方式 | 示例 |
|---------|---------|------|
| 纯章节号 | 精确匹配章节号 | `21.4` → 21.4 三角形的中位线 |
| 纯课时名称 | 关键词匹配 | `三角形的中位线` → 21.4 三角形的中位线 |
| 章节+名称 | 组合匹配 | `21.4 三角形的中位线` → 精确匹配 |
| 模糊输入 | 智能匹配+提示 | `中位线` → 提示"是否指21.4 三角形的中位线？" |

### 处理异常

- 如果输入的章节号不存在，提示可用的章节列表
- 如果输入的课时名称模糊匹配到多个结果，列出所有匹配项让用户选择
- 如果完全无法匹配，提示用户检查输入或提供正确的课时名称

### 禁止事项

- 禁止在用户未确认前直接开始生成教学设计
- 禁止忽略用户输入错误继续执行
- 禁止猜测用户意图而不进行确认

## 5. 强制步骤链（执行链）

课题确认通过后，严格按以下步骤链执行：

```text
课题确认（按orchestrator登记的课题匹配规则执行）
  ↓
知识分析（AI 生成草稿）
  ↓
🛑 确认门1：知识分析确认
  AI 呈现课型判断、知识点拆解、重难点定位
  → 教师审核/修改/补充
  → 教师确认后继续
  ↓
学习目标设计（AI 基于确认的知识分析生成草稿）
  ↓
🛑 确认门2：学习目标确认
  AI 呈现三层学习目标及行为动词
  → 教师审核层级划分和动词准确性
  → 教师确认后继续
  ↓
评价任务设计（AI 基于确认的目标生成草稿）
  ↓
🛑 确认门3：评价设计确认
  AI 呈现评价任务与目标的对应关系、成功标准
  → 教师审核对应关系和成功标准
  → 教师确认后继续
  ↓
问题链设计（AI 自动完成，无需确认）
  ↓
活动设计（AI 基于确认的上游生成草稿）
  ↓
🛑 确认门4-1：教材顺序与模块任务确认
  AI 呈现教材原文内容模块列表，标注每个模块对应的任务类型（读懂/思考/交流/书写/操作等）
  → 教师审核模块顺序（必须与教材一致）和任务类型匹配
  → 教师确认后继续
  ↓
🛑 确认门4-2：活动步骤逐步确认
  AI 按模块逐个呈现活动步骤，标注每个步骤的时间分配
  → 教师逐模块确认活动步骤合理性
  → 教师确认后继续
  ↓
🛑 确认门4-3：台阶提问确认
  AI 呈现完整的问题编号列表（如 ASK_B_01, ASK_M_02, ASK_E_03），每个问题按“提问→分级备用提示→教师参考预期”排列
  → 教师确认每个问题的指向性、对结论的负责程度
  → 教师确认后继续
  ↓
🛑 确认门4-4：整体整合确认
  AI 呈现完整的活动设计整合版（含教材对应位置、题源、升华等）
  → 教师审核整体连贯性
  → 教师确认后继续
  ↓
活动质量检查（AI 自动完成）
  ↓
作业设计（AI 自动完成）
  ↓
质量检查（教学设计审核+教学法审核+数学审核+学情适配审核+提问质量审查+一致性校验）
  ↓
outputs完整教学设计
  ↓
标记 pending_human_review
```

## 6. 各步骤执行细则

### 6.1 知识分析

| 项目 | 内容 |
|------|------|
| 执行方式 | AI 基于强制读取的skills定义生成草稿，outputs风格为对话预览 |
| 输入 | 课题确认信息 + 教材原文 + INDEX.yaml匹配结果（math-essence、common-errors、teaching-strategies）+ learning-theory文件 |
| outputs | 课型判断、知识点拆解、重难点定位、常见误解、知识生长路径、活动设计上下文（见 skills/knowledge/SKILL.md） |

读取 `skills/knowledge/SKILL.md` 获取完整分析框架。

### 6.2 学习目标设计

| 项目 | 内容 |
|------|------|
| 执行方式 | AI 基于确认门1确认的知识分析生成草稿 |
| 输入 | 确认后的知识分析 + 课标对应内容 |
| outputs | 三层学习目标（基础层 LO-B、中间层 LO-M、拓展层 LO-E，每层 1-2 条） |

读取 `skills/objectives/SKILL.md` 获取行为动词规则和分层规则。

**关键约束：**
- 行为动词必须可观察（禁止：理解、掌握、了解、体会、感受、知道）
- 基础层：观察/辨认/说出/指出/模仿/列举/复述
- 中间层：解释/归纳/描述/区分/表达/概括
- 拓展层：分析/评价/设计/创造/论证/优化/变式

### 6.3 评价任务设计

| 项目 | 内容 |
|------|------|
| 执行方式 | AI 基于确认的目标生成草稿 |
| 输入 | 确认后的学习目标 + 知识分析 |
| outputs | 分层评价任务（AS-B/M/E，每条目标至少对应一个评价任务） |

### 6.4 问题链设计

| 项目 | 内容 |
|------|------|
| 执行方式 | AI 自动完成（无需确认门） |
| 输入 | 知识分析 + 学习目标 + 学情分析 |
| outputs | 问题链（核心问题 + 子问题递进 + 认知冲突 + 最终结论） |

### 6.5 活动设计

| 项目 | 内容 |
|------|------|
| 执行方式 | AI 基于确认的上游生成草稿 |
| 输入 | 确认后的学习目标 + 评价任务 + 问题链 + 知识分析（含活动设计上下文） |
| outputs | 各环节活动设计（按课型标准流程组织） |

**关键约束：**
- 活动顺序必须严格遵循教材原文内容模块的先后顺序（练习和习题除外）
- 每个活动必须标注 `教材对应位置` 字段
- 活动以学生为中心，有反馈节点，支持分层

### 6.6 作业设计

| 项目 | 内容 |
|------|------|
| 负责skills | `skills/homework/SKILL.md` |
| 执行方式 | AI 自动完成 |
| 输入 | 学习目标 + 评价任务 + 知识分析 + `knowledge/workbooks/` + 对应课时教材参考解答 |
| outputs | 分层作业（基础层必做 ≤ 3 题、中间层必做 ≤ 2 题、拓展层选做 ≤ 1 题） |

### 6.7 质量检查

依次执行以下validators，全部通过后方可outputs：

1. 学习目标validators
2. 评价validators
3. 活动validators
4. 教学设计validators
5. 教学法validators
6. 数学validators
7. 学情适配validators
8. 提问质量审查
9. 一致性validators

另需用对应skills的检查清单逐项自检。

## 7. 确认门交互协议

每个确认门必须遵循以下交互规范：

### 7.1 呈现模板

每个确认门呈现时，必须使用以下结构化格式：

```markdown
---
🛑 确认门[N]：[环节名称]

[结构化草稿内容]

**需要您确认的关键点：**
1. ...
2. ...
3. ...

请审核以上内容。确认无误请回复"确认"，如需修改请指出具体调整意见。
---
```

### 7.2 交互流程

1. **呈现草稿**：以结构化格式呈现当前环节的草稿outputs
2. **标注关键决策点**：明确列出"需要您确认的关键点"（3-5条），聚焦该环节最影响下游质量的决策
3. **等待教师回复**：教师可回复：
   - **确认**：回复"确认""是""对""正确"等肯定词 → 进入下一环节
   - **修改意见**：指出需要调整的具体内容 → AI 修订后重新呈现，回到步骤1
   - **补充信息**：提供 AI 未考虑的学情/教学信息 → AI 整合后重新呈现，回到步骤1
4. **锁定确认版本**：教师确认后，该环节outputs作为下游的锁定输入，不可回退修改（除非后续环节发现逻辑矛盾）
5. **确认记录**：每个确认门的确认结果记录在教学设计 YAML front matter 的 `collab_gates` 字段中

### 7.3 各确认门的关键决策点

| 确认门 | 关键决策点示例 |
|--------|---------------|
| 确认门1：知识分析 | 课型判断是否正确；知识点拆解粒度是否合适；重难点定位是否准确；与前续知识的衔接是否完整 |
| 确认门2：学习目标 | 三层目标的层级划分是否合理；行为动词是否准确反映认知层次；目标是否可观察可评价；目标数量是否适当 |
| 确认门3：评价设计 | 评价任务与目标的对应关系是否完整；成功标准是否明确可观察；评价形式是否多样；评价能否区分不同认知层次 |
| 确认门4-1：教材顺序与模块任务 | 模块顺序是否与教材原文一致；每个模块对应的任务类型（读懂/思考/交流/书写/操作）是否匹配教材意图 |
| 确认门4-2：活动步骤 | 每个活动步骤的设计是否合理；时间分配是否符合40分钟课时；学生行为是否明确；反馈节点是否充分 |
| 确认门4-3：台阶提问 | 每个问题是否有编号（ASK_B_XX / ASK_M_XX / ASK_E_XX）；是否先提问、再给分级备用提示、最后写教师参考预期；问题是否对结论负责 |
| 确认门4-4：整体整合 | 活动整体是否连贯；教材对应位置是否准确标注；题源是否完整；升华是否到位 |

### 7.4 禁止事项（确认门相关）

- 禁止跳过任何确认门
- 禁止在教师未确认时继续下游环节
- 禁止忽略教师修改意见直接使用原草稿继续
- 禁止将确认门交互过程写入最终教学设计正文（仅记录在 YAML front matter 的 `collab_gates` 字段）
- 禁止将运行时读取文件清单、路径列表或溯源过程写入最终教学设计正文或 YAML front matter。

## 8. outputs要求

### 8.1 文件路径

`E:\OneDrive\math-resource-engine\outputs\{课时名}_教学设计.md`

### 8.2 YAML 元数据

```yaml
---
content_type: lesson
lesson_id: ""
lesson_name: ""
command: lesson-collab
workflow_version: v2
review_status: pending_human_review
created_at: ""
collab_gates:
  - gate: knowledge_analysis
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
  - gate: learning_objectives
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
  - gate: assessment_design
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
  - gate: activity_4_1_textbook_order
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
  - gate: activity_4_2_steps
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
  - gate: activity_4_3_questions
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
  - gate: activity_4_4_integration
    status: confirmed
    confirmed_at: "YYYY-MM-DD HH:mm"
    teacher_notes: ""
---
```

### 8.3 教学设计正文结构

正文必须采用双层教学设计：第一层供教师直接实施，第二层供审核、溯源和下游课件生成。两层必须位于同一文件中，且内容一致。

```markdown
> **阅读建议**：日常备课先看“课堂实施导航”和“课堂实施要点”；需要审核目标、评价、题源或提问细节时，再展开文末的“完整结构化设计”。

## 课堂实施导航

### 本课要解决的问题

### {duration}分钟流程总览

| 时间 | 教学环节 | 学生主要任务 | 教师支持 | 达成结果 |

### 课堂实施要点

### 核心提问

### 课堂练习与作业

<details>
<summary><strong>展开完整结构化设计（目标、评价、活动、题源及审核信息）</strong></summary>

> 以下内容供教学审核、题源追踪和后续课件生成使用。英文编号与字段为系统识别标记，不要求教师在课堂中呈现。

## meta

- module:
- grade:
- topic:
- duration: 40分钟以内

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

## lesson_flow

## practice

## homework

## boardwork

## consistency_matrix

## quality_check

</details>
```

双层强制规则：

- 第一层不得出现 `LO-*`、`AS-*`、`ACT-*`、`ASK_*`、`source_id`、`source_type`、`question_id` 等后台字段。
- 第一层流程总览每行对应第二层一个活动，活动数量、顺序和时间一致。
- 第一层核心问题与第二层 `core_question` 一致。
- 第一层练习和作业只能压缩表达第二层已有任务，不得新增无题源任务。
- 每个 `ACT-*` 必须包含 `time_priority` 和六字段 `time_budget`，并通过 `tools/validate_lesson_timing.py`。
- 时间验证“有条件通过”时，第一层课堂实施要点必须写明可后移的 `flex` 或 `backup` 活动；“不通过”时不得outputs教学设计。

### 8.4 题源字段

教学设计中任何例题、练习、评价任务、作业题都必须携带题源。单题使用：

```yaml
source_id: ""
source_type: textbook | exercise_bank | curriculum_repository
question_id: ""
```

同一评价任务、活动或作业包含多道同源题时，合并共享字段：

```yaml
source_id: ""
source_type: textbook | exercise_bank | curriculum_repository
question_ids:
  - ""
  - ""
```

`question_id` 与 `question_ids` 二选一。禁止用逗号拼接多个编号；禁止为每个编号重复outputs相同的 `source_id`、`source_type`。

禁止无来源题目进入教学设计。

### 8.5 稳定 ID 规则

| 对象 | ID 格式 | 示例 |
|------|---------|------|
| 基础层学习目标 | `LO-B-序号` | `LO-B-01` |
| 中间层学习目标 | `LO-M-序号` | `LO-M-01` |
| 拓展层学习目标 | `LO-E-序号` | `LO-E-01` |
| 评价任务 | `AS-层级-序号` | `AS-B-01` |
| 学习活动 | `ACT-层级-序号` | `ACT-M-01` |
| 课堂提问 | `ASK-层级-序号` | `ASK-E-01` |

## 9. 全局红线规则（违反任意一条outputs无效）

以下规则来源于 `AGENTS.md`，本skills必须严格遵守：

1. ❌ 未读取 skills调用协议.md 直接生成
2. ❌ outputs中出现"理解""掌握""了解""体会""感受""知道"等禁止词汇
3. ❌ outputs结构中缺少基础/中间/拓展任意一层
4. ❌ 使用了非题库来源的题目（LLM自行生成）
5. ❌ 数学概念、公式、定理出现错误
6. ❌ 未注入课标要求（教学目标、评价设计、教学设计类任务）
7. ❌ 未注入学情数据（教学目标、活动设计类任务）
8. ❌ 存在看图说话/事实复读/封闭确认型提问（平均分<3.0）
9. ❌ 活动顺序打乱了教材原文内容模块的先后顺序（练习和习题除外）
10. ❌ 活动未标注 `教材对应位置` 字段
11. ❌ 课堂练习/检测未选用教材练习栏目全部题目（遗漏或跳题）
12. ❌ 课堂练习/检测题目总数量不足 4 道
13. ❌ 课堂练习/检测题目缺少调度稿页
14. ❌ 提问未对结论负责（提问无论学生怎么回答都无法引向核心结论，或缺少具体指向性提示）
15. ❌ 使用超出教材原文、课标要求或学生当前认知水平的概念术语

## 10. 全局禁止事项

- 禁止生成课件
- 禁止生成课堂提问调度稿
- 禁止执行课件validators
- 禁止执行图片资源validators
- 禁止写入具体学生姓名；教学设计只标注提问层级
- 禁止将未人工审核的教学设计标记为 `审核通过`
- 禁止跳过课题确认直接开始生成
- 禁止一次性outputs完整教学设计（必须通过确认门分步确认）
- 禁止 LLM 自行生成新题（所有题目必须来自教材或题库）
- 禁止打乱教材原文内容模块的先后顺序
- 禁止使用不可观察行为动词（理解、掌握、了解、体会、感受、知道）
- 禁止用超出教材进度的学科化术语替代教材表达；必要时改写为学生可观察、可操作的教材语言

## 11. 后续动作

教师完成所有确认门对话并审核通过教学设计后，手动将元数据改为：

```yaml
review_status: 审核通过
```

只有 `审核通过` 的教学设计才能作为 `/courseware-collab` 的输入。

## 12. 归档兼容说明

- `/lesson` 已归档，不再作为可执行入口。
- 收到 `/lesson` 时停止并提示用户改用 `/lesson-collab`，不得静默执行。
- 新生成的教学设计必须写入 `command: lesson-collab` 和完整 `collab_gates`。

## 13. 前检查清单（生成前必须执行）

生成开始前，必须逐项确认以下内容。**所有检查项必须通过方可开始。**

### 通用检查

- [ ] 已读取 `orchestrator/skill-protocol.md`，确认当前任务的强制步骤链
- [ ] 已读取 `AGENTS.md`，确认红线规则
- [ ] 已读取 `orchestrator/workflow-registry.md`，确认 `/lesson-collab` 完整流程
- [ ] 已读取 `orchestrator/output-contract.md`，确认outputs模板
- [ ] 已读取 `orchestrator/precheck.md`，完成逐项自检
- [ ] 已确认课型，读取对应课型定义文件
- [ ] 已读取对应课时教材原文
- [ ] 已注入课标要求
- [ ] 已注入学情数据

### 确认门专项检查

- [ ] 已明确当前处于哪个确认门
- [ ] 已使用确认门呈现模板（包含 🛑 标记、结构化草稿、关键决策点）
- [ ] 确认门交互过程不会写入最终教学设计正文
- [ ] 教师确认后才进入下游环节
- [ ] 教师修改意见已完整采纳并修订
