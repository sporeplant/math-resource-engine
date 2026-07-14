# outputs合约

教学设计、教师调度稿、教材参考解答和复习讲义使用 YAML front matter。学生投屏课件为 Typora 纯 Markdown，不设置 YAML front matter。

---

## 1. outputs目录

`outputs/` 只存放生成产物，不存放工作流脚本、源知识库资料或长期公共图片池。教学设计、课件、课堂提问调度稿和复习讲义必须按资源包目录写入；教材问题参考解答作为 knowledge 资产写入 `knowledge/solutions/ch{章节号}/`。

### 1.1 正式资源包

| 产物 | 文件位置 |
|------|----------|
| 新授/课时资源包 | `outputs/lessons/ch{章节号}/{lesson_id}/` |
| 复习/讲评资源包 | `outputs/reviews/{review_id}/` |
| 软件或离线导出包 | `outputs/packages/{package_id}/` |
| 教材问题参考解答 | `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md` |

新授/课时资源包建议结构：

```text
outputs/lessons/ch{章节号}/{lesson_id}/
├── metadata.yaml
├── lesson-{lesson_id}-lesson-plan.md
├── lesson-{lesson_id}-courseware.md
├── lesson-{lesson_id}-question-dispatch.md
├── lesson-{lesson_id}-review-report.md
└── exports/
```

复习/讲评资源包建议结构：

```text
outputs/reviews/{review_id}/
├── metadata.yaml
├── teacher-handout.md
├── student-handout.md
├── courseware.md
├── question-dispatch.md
└── exports/
```

`exports/` 仅存放从源 Markdown 导出的 `.docx`、`.pdf`、`.pptx` 等成品文件。导出工具能够嵌入 CDN 图片时，不再生成本地图片副本。

`outputs/packages/{package_id}/` 用于希沃、EasiNote、PPTX 等需要离线打包的机器可读资源。此类目录可按目标格式生成 `assets/`，但 `assets/` 是导出包的一部分，不作为通用图片目录。

### 1.2 临时与演示产物

渲染截图、演示输出、临时中间文件只允许放入：

- `outputs/_demo/`
- `outputs/_tmp/`

`outputs/_tmp/` 建议加入 `.gitignore`；`outputs/_demo/` 仅保存确有复现价值的演示结果。

---

## 2. YAML 元数据

除学生投屏课件外，教学设计、课堂提问调度稿和复习讲义等 outputs Markdown 必须以如下结构开头：

```yaml
---
content_type: lesson | courseware | question_dispatch | review_lesson
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
  - "knowledge/solutions/ch{章节号}/solution-{lesson_id}.md"
```

若本课时使用练习册题库，`source_files` 还必须登记对应的题库、答案和逐题索引：

```yaml
  - "knowledge/workbooks/workbook-{课时编号}.md"
  - "knowledge/workbook-answers/workbook-answer-{课时编号}.md"
  - "knowledge/workbook-index/workbook-index-{课时编号}.yaml"
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
- `lesson_id`：课时唯一标识，同一课时的教学设计、课件、课堂提问调度稿必须一致。
- `lesson_name`：课时名称，与文件名主体一致。
- `command`：生成该文件的命令。
- `workflow_version`：当前固定为 `v2`。
- `review_status`：人工审核状态。
- `source_files`：本产物直接读取的上游文件。
- `/lesson-collab`、`/courseware-collab` 产物必须在 `source_files` 中登记对应课时的 `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md`；缺失时不得生成产物。
- `/复习讲义` 产物必须在 `source_files` 中登记所有被整理的 `knowledge/reviews/` 源文件。
- `created_at`：生成时间，格式建议为 `YYYY-MM-DD HH:mm`。

---

## 3. 内容类型

| content_type | 生成命令 | 用途 |
|--------------|----------|------|
| lesson | `/lesson-collab` | 教学设计 |
| courseware | `/courseware-collab` | Markdown 课件 |
| question_dispatch | `/courseware-collab` | 教师手持课堂提问调度稿 |
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

### 5.1 练习册题源强约束

当 `source_type: exercise_bank` 时：

- `source_id` 必须为对应 `knowledge/workbooks/workbook-*.md` 的文件名主体。
- `question_id` 或 `question_ids` 必须存在于 `knowledge/workbook-index/workbook-index-*.yaml`。
- 同一 `source_id` 必须能对应到 `knowledge/workbook-answers/workbook-answer-*.md`。
- `source_files` 必须同时登记题库、答案和索引三件套。
- 缺少索引或答案时，正式产物不得生成。

---

## 6. 分层命名

全系统只允许使用以下层级名称：

- 基础层
- 中间层
- 拓展层

禁止使用旧的中间层别名作为系统层级名称。

---

## 7. 图片引用

正式 Markdown 默认使用 CDN 图片 URL。图片源文件统一维护在 `knowledge/images/`，推送远程仓库后通过 CDN 引用；`outputs/` 不常驻 `images/` 公共目录。

学生课件和复习讲义使用 Typora 原生 Markdown 图片语法：

```markdown
![图注](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/xxx.jpg)
```

禁止：

- 空图注 Markdown 图片 `![]()`
- 学生课件中的 HTML 图片标签
- 引用本机绝对路径
- 引用 `outputs/images/`、`outputs/assets/` 等旧公共资源目录
- 将 CDN 可用图片重复复制到正式 Markdown 同级目录作为常驻资源

导出规则：

- `.docx`、`.pdf` 导出优先从 CDN 拉取图片并嵌入成品文件。
- `.pptx`、希沃、EasiNote 或其他离线软件包如需本地资源，只在 `outputs/packages/{package_id}/assets/` 中生成本地副本。
- 仅在离线审阅、网络不可用或目标工具不支持远程图片时，才允许为单个资源包临时生成本地图片缓存；缓存不得作为正式 Markdown 的默认引用方式。

---

## 8. `/lesson-collab` 模板

教学设计正文必须采用"传统正文 + 后台折叠结构"，在同一个 Markdown 文件中同时服务教师日常备课和系统审核：

| 层级 | 使用者 | 作用 | 内容边界 |
|------|--------|------|----------|
| 第一层：传统教学设计正文 | 任课教师 | 日常备课、课堂执行、导出 Word | 采用传统清爽教案栏目，保留教学内容、目标、重难点、过程、当堂检测、作业、板书 |
| 第二层：完整结构化设计 | 审核者、validators、课件生成流程 | 教学评审核、题源追踪、下游复用 | 保留目标、评价、资源盘点、问题链、活动、题源、作业、后移题、一致性矩阵和质量记录 |

### 8.1 第一层：传统教学设计正文

一级标题之后按以下固定顺序outputs：

```markdown
## 一、教学内容

## 二、教学目标

## 三、教学重点与难点

## 四、教学准备

## 五、教学过程

## 六、当堂检测

## 七、课后作业

## 八、板书设计

## 九、设计依据简记
```

第一层规则：

- 教学过程中的主要环节必须与第二层 `lesson_flow` 的活动顺序和时间含义一致。
- 使用教师可直接执行的自然语言，不出现 `LO-*`、`AS-*`、`ACT-*`、`ASK_*`、`source_id`、`source_type`、`question_id` 等后台标记。
- 当堂检测必须单独列明，写出题目来源的教师可读名称、检测目标和限时。
- 课后作业必须单独列明，分为基础层必做、中间层必做、拓展层选做，并标注预计用时。
- 必须在正文中说明后移题安排，可写入“设计依据简记”，但不得用后台字段替代教师可读说明。
- 板书设计不得使用代码块；应采用普通 Markdown 段落、列表或公式排版。

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

## resource_audit

- textbook_items:
- workbook_items:
- scheduling_decisions:

## practice

- 当堂检测题：
  - 检测目标:
  - 限时:
  - source_id:
  - source_type:
  - question_id:

## homework

- 基础层必做（约20分钟）:
- 中间层必做（约25分钟）:
- 拓展层选做（增加1题）:

## deferred_exercises

- 题目:
  - 去向: 习题课 | 讲评课 | 周练 | 单元整理 | 暂不处理
  - 理由:
  - source_id:
  - source_type:
  - question_id:

## boardwork

## consistency_matrix

## quality_check

</details>
```

第二层继续遵守全部稳定 ID、题源和教学评一致性规则，不因折叠而省略字段。

`lesson_flow` 中每个活动还必须包含 `time_priority` 和完整 `time_budget`。教学设计outputs前必须运行教学活动时间validators；不通过时回退活动设计，有条件通过时在课堂实施要点中明确可后移任务。

`resource_audit`、`practice`、`homework`、`deferred_exercises` 必须执行 `orchestrator/resource-scheduling.md`。练习册题若未进入 `practice` 或 `homework`，必须在 `deferred_exercises` 中登记去向或取舍理由。

### 8.3 双层一致性

- 第一层"本课要解决的问题"必须与第二层核心问题一致。
- 第一层教学过程与第二层 `lesson_flow` 的活动数量、顺序和总时长一致。
- 第一层课堂练习、作业必须能在第二层 `practice`、`homework` 中找到对应任务，不新增无题源任务。
- 第一层后移题安排必须能在第二层 `deferred_exercises` 中找到对应记录。
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

## 9. 数学表达式格式

所有 outputs Markdown（教学设计、课堂提问调度稿、教材问题参考解答、复习讲义、课件）中的数学表达式必须使用 Markdown 可渲染的 LaTeX 格式：

- 行内公式使用 `$...$`，如 `$\frac{x+3}{5}$`、`$x \neq 1$`
- 独立多步推导使用 `$$...$$` 或 `aligned` 环境
- 不得将 `a^2/b`、`(x+1)/(x-1)`、`x=2`、`20 km/h` 等数学表达以裸文本呈现
- 课件中 LaTeX 须兼容 Typora 渲染
- `boardwork` 代码块内的板书示意图模拟黑板书写，不受此规则约束

此规则为全局出口约束，各 Skill 的检查清单在此基础上可补充各自特殊要求（如教材问题解答要求 `aligned` 环境用于多步推导）。
