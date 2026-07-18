# 工作流注册表

本文件是系统工作流的唯一权威来源。其他orchestrator文件、命令定义、skills调用协议只允许引用本文件，不得重复维护另一套流程。

---

## 1. 全局原则

- `/lesson-collab` 和 `/courseware-collab` 是当前教学资源生成命令，必须分开运行。
- `/lesson-collab` 通过确认门生成完整教学设计，outputs状态为 `pending_human_review`，等待人工审核。
- `/courseware-collab` 只能消费 `review_status: 审核通过` 的教学设计，不重新生成学习目标、评价任务或活动设计。
- 课件和课堂提问调度稿只由 `/courseware-collab` 生成。
- `/lesson` 与 `/courseware` 已归档；收到旧命令时停止执行并提示使用对应协作命令。
- 任意 Markdown 文件引用图片时，只允许引用该文件同级目录下的 `images/` 子目录。
- 所有题目必须来自登记题库，并携带 `source_id`、`source_type`、`question_id`。

---

## 2a. `/lesson-collab` 工作流（当前教学设计主链）

`/lesson-collab` 是当前唯一教学设计入口。它在知识分析、学习目标、评价设计、活动设计四个关键节点设置**确认门**。

输入格式：

```text
/lesson-collab [auto] 课时名称
```

示例：

```text
/lesson-collab 21.4
/lesson-collab 三角形的中位线
/lesson-collab 21.4 三角形的中位线
/lesson-collab auto 21.4
/lesson-collab auto 三角形的中位线
```

带上 `auto` 参数进入**自动确认模式**：课题确认仍等教师回复；确认门照常生成草稿、自检、写入中间 MD 文件后 AI 自动确认并继续，不暂停等待。详见 §2a 末尾「auto 模式」小节。

执行链：

```text
课题确认（解析课时名称 → 匹配教材课时分配表 → 显示确认信息 → 用户确认）
  ↓
定位并校验对应课时教材参考解答
  文件缺失、课时不匹配、验证失败或 review_status ≠ 审核通过 → 立即终止本次任务
  ↓
定位并校验对应课时练习册题库、答案和逐题索引
  练习册为可选项：缺失时不阻断，跳过双资源盘点中练习册相关部分，相关字段标记 N/A
  存在但校验失败 → 报告问题但可继续，仅教材资源可用
  ↓
教材-练习册双资源盘点
  按 `orchestrator/resource-scheduling.md` 形成 resource_audit
  明确当堂检测、课后作业、后移到习题课或讲评课的题目去向
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
  → 同时呈现教材问题解答的台阶分析升格建议（如有），说明 B/C 组是否存在方法断崖
  → 教师审核模块顺序（必须与教材一致）和任务类型匹配
  → 教师确认是否采纳升格建议（采纳 → 后续按 2 个例题展开；不采纳 → 按教材原例题展开）
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

### `/lesson-collab` auto 模式

带上 `auto` 参数的 `/lesson-collab` 进入自动确认模式：

**与标准模式的区别：**

1. **课题确认**：保留，仍等待教师回复确认课题信息
2. **教材参考解答**：存在且校验通过 → 直接使用。缺失或校验失败 → 自动触发 `/教材问题解答` 生成，与知识分析、学习目标设计并行推进；评价设计在教材解答就绪报告返回后方可开始
3. **练习册校验**：同标准模式，练习册可选，缺失不阻断。存在时校验与知识分析并行
4. **确认门**：全部**自动确认** — AI 照常生成草稿、自查、锁定为下游输入，但不暂停等待教师回复，直接进入下一环节
5. **作业设计** ‖ **活动质量检查**：两者仅依赖活动设计，并行执行
6. **Validators 并行**：数学审核、教学法审核、学情适配审核、提问质量审查四者并行；一致性校验汇总上述结果后串行执行

**并行执行流：**

```text
课题确认（等待教师）
  ↓
┌─ 教材解答缺失？触发 /教材问题解答 ──→ 解答生成 ──→ 校验通过 ──┐
├─ 练习册存在？三件套校验 ──────────────────────────────────┤
│                                                          │
└─ 知识分析 → 学习目标 → ────────────────────────→ 评价设计（等解答+练习册就绪）
                                                                ↓
                                                          问题链 → 活动设计
                                                                  ↓
                                                    ┌─ 作业设计 ──┐
                                                    └─ 活动质量检查 ┘
                                                          ↓
                                              ┌─ 数学审核 ─┐
                                              ├─ 教学法审核  ├─→ 一致性校验 → outputs
                                              ├─ 学情适配    │
                                              └─ 提问质量 ──┘
```

**确认门行为：**

- 每个确认门仍完整生成结构化草稿
- 草稿写入中间 MD 文件（见下方目录结构）
- 确认日志 `collab-gates.log.md` 中记录 `status: auto_confirmed`，`teacher_notes: "auto"`
- 若某环节自查发现问题，AI 自行修订后重新锁定，最多 3 次；3 次仍未通过则终止并报告

**中间产物目录：**

```text
outputs/{课时名}/
├── 01-knowledge-analysis.md      # 确认门1：知识分析
├── 02-objectives.md              # 确认门2：学习目标
├── 03-assessment.md              # 确认门3：评价设计
├── 04-activities.md              # 确认门4-1 ~ 4-4：活动设计（含问题链）
├── 05-homework.md                # 作业设计
├── collab-gates.log.md           # 确认门日志（全部 status: auto_confirmed）
└── {课时名}_教学设计.md           # 最终教学设计
```

**auto 模式 quality check / output 与标准模式完全相同。** 最终教学设计 `review_status` 仍为 `pending_human_review`，必须经人工审核通过后方可用于 `/courseware-collab`。

**执行指引（主 Agent 并行调度）：**

auto 模式下主 Agent 不自行生成所有内容，而是按以下规则派发后台子 Agent：

1. **课题确认后**，同时推进：
   - 教材解答缺失时：`task(run_in_background=true)` 派发子 Agent 执行 `/教材问题解答 {课时}`，子 Agent 写入 `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md`，完成后返回校验摘要
   - 练习册存在时：主 Agent 自行校验三件套（纯文件校验，轻量），与知识分析并行
   - 主 Agent 自行推进知识分析 → 学习目标，写入 `01-knowledge-analysis.md`、`02-objectives.md`

2. **评价设计前 wait 点**：若派发了教材解答子 Agent，调用 `wait` 等待其完成并校验返回报告；子 Agent 间通过中间 MD 文件传递结果，主 Agent 读取校验不通过则终止并报告

3. **活动设计完成后**，同时派发：
   - `task(run_in_background=true)` 派发子 Agent 执行作业设计，子 Agent 写入 `05-homework.md`
   - 主 Agent 自行执行活动质量检查
   - `wait` 作业设计子 Agent 完成后继续

4. **质量检查阶段**，用 `parallel_tasks` 同时派发四个只读审核：
   - 数学正确性审核
   - 教学法审核
   - 学情适配审核
   - 提问质量审查
   - 四者全部返回后主 Agent 串行执行一致性校验，汇总后 output

### 确认门交互协议

每个确认门必须遵循以下交互规范：

1. **呈现草稿**：AI 以结构化格式呈现当前环节的草稿outputs
2. **标注关键决策点**：AI 明确列出"需要您确认的关键点"（3-5条），聚焦该环节最影响下游质量的决策
3. **等待教师回复**：教师可回复：
   - **确认**：回复"确认""是""对""正确"等肯定词 → 进入下一环节
   - **修改意见**：指出需要调整的具体内容 → AI 修订后重新呈现，回到步骤1
   - **补充信息**：提供 AI 未考虑的学情/教学信息 → AI 整合后重新呈现，回到步骤1
4. **锁定确认版本**：教师确认后，该环节outputs作为下游的锁定输入，不可回退修改（除非后续环节发现逻辑矛盾）
5. **确认记录**：每个确认门的确认结果应记录在独立日志文件 `{output_dir}/collab-gates.log.md` 中，不写入教学设计的 YAML front matter

### 确认门呈现模板

每个确认门呈现时，AI 必须使用以下格式：

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

### 各确认门的关键决策点

| 确认门 | 关键决策点示例 |
|--------|---------------|
| 确认门1：知识分析 | 课型判断是否正确；知识点拆解粒度是否合适；重难点定位是否准确；与前续知识的衔接是否完整 |
| 确认门2：学习目标 | 三层目标的层级划分是否合理；行为动词是否准确反映认知层次；目标是否可观察可评价；目标数量是否适当 |
| 确认门3：评价设计 | 评价任务与目标的对应关系是否完整；成功标准是否明确可观察；评价形式是否多样；评价能否区分不同认知层次 |
| 确认门4-1：教材顺序与模块任务 | 模块顺序是否与教材原文一致；每个模块对应的任务类型（读懂/思考/交流/书写/操作）是否匹配教材意图 |
| 确认门4-2：活动步骤 | 每个活动步骤的设计是否合理；时间分配是否符合40分钟课时；学生行为是否明确；反馈节点是否充分 |
| 确认门4-3：台阶提问 | 每个问题是否有编号（ASK_B_XX / ASK_M_XX / ASK_E_XX）；是否先提问、学生停滞后再逐级提示、最后写教师参考预期；问题是否对结论负责 |
| 确认门4-4：整体整合 | 活动整体是否连贯；教材对应位置是否准确标注；题源是否完整；升华是否到位 |

### `/lesson-collab` 课题确认环节

按以下课题确认规则执行：

### 课题确认环节

在执行 `/lesson` 命令时，必须先进行课题确认，防止用户输入错误的章节号或课时名称。

**确认流程：**

1. **解析输入**：识别用户输入的章节号（如 `21.4`）或课时名称（如 `三角形的中位线`）
2. **匹配教材**：从 `knowledge/textbooks/教材原文_教材课时分配.md` 中查找对应课时
3. **显示确认信息**：
   ```text
   📋 请确认课题信息：
   
   章节：第21章 四边形
   节次：21.4 三角形的中位线
   课时：第1课时（共1课时）
   教材文件：教材原文_21.4_三角形的中位线.md
   
   确认无误后，请回复"确认"或"是"继续生成教学设计。
   如需修改，请重新输入正确的课时名称。
   ```
4. **等待用户确认**：用户回复"确认"、"是"、"对"、"正确"等肯定词后继续执行
5. **处理异常**：
   - 如果输入的章节号不存在，提示可用的章节列表
   - 如果输入的课时名称模糊匹配到多个结果，列出所有匹配项让用户选择
   - 如果完全无法匹配，提示用户检查输入或提供正确的课时名称

**匹配规则：**

| 输入类型 | 匹配方式 | 示例 |
|---------|---------|------|
| 纯章节号 | 精确匹配章节号 | `21.4` → 21.4 三角形的中位线 |
| 纯课时名称 | 关键词匹配 | `三角形的中位线` → 21.4 三角形的中位线 |
| 章节+名称 | 组合匹配 | `21.4 三角形的中位线` → 精确匹配 |
| 模糊输入 | 智能匹配+提示 | `中位线` → 提示"是否指21.4 三角形的中位线？" |

**禁止事项：**

- 禁止在用户未确认前直接开始生成教学设计
- 禁止忽略用户输入错误继续执行
- 禁止猜测用户意图而不进行确认

### `/lesson-collab` 强制读取

强制读取以下文件：

### `/lesson` 强制读取

1. `AGENTS.md`
2. `orchestrator/workflow-registry.md`
3. `orchestrator/output-contract.md`
4. `orchestrator/skill-contract.md`
5. `orchestrator/quality-gates.md`
6. `orchestrator/review-protocol.md`
7. `skills/knowledge/SKILL.md`
8. `skills/objectives/SKILL.md` 和 `检查清单.md`
9. `skills/assessment/SKILL.md` 和 `检查清单.md`
10. `skills/questions/SKILL.md`
11. `skills/activities/SKILL.md` 和 `检查清单.md`
12. `skills/act-check/SKILL.md`
13. `skills/homework/SKILL.md` 和 `检查清单.md`
14. `skills/ask-check/SKILL.md` 和 `检查清单.md`
15. `validators/objectives/rules.md`
16. `validators/assessment/rules.md`
17. `validators/activities/rules.md`
18. `validators/lesson/rules.md`
19. `validators/pedagogy/rules.md`
20. `validators/math/rules.md`
21. `validators/fit/rules.md`
22. `validators/alignment/rules.md`
23. 对应课时的课标（knowledge/standards/）、教材原文（knowledge/textbooks/）、练习册题库（knowledge/workbooks/）、students文件（students/）、课型定义（knowledge/types/）

额外增加：

24. `orchestrator/skill-protocol.md` 中 §2a `/lesson-collab` 强制链
25. `orchestrator/resource-scheduling.md`
26. `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md`
27. 对应课时 `knowledge/workbooks/workbook-*.md`
28. 对应课时 `knowledge/workbook-answers/workbook-answer-*.md`
29. 对应课时 `knowledge/workbook-index/workbook-index-*.yaml`

教材参考解答必须在知识分析开始前完成校验：文件存在，`content_type: textbook_solution`，`lesson_id` 与当前课时一致，`review_status: 审核通过`，并通过教材问题解答validators。任一条件不满足时立即终止本次任务，报告预期路径或失败项，并提示执行 `/教材问题解答 {课时}` 后重新发起 `/lesson-collab`。禁止自动补齐、降级读取教材原文临时推导、跳过校验或继续任何确认门。

评价设计和活动设计必须按 `question_id` 使用教材参考解答核对教材任务清单、评价证据、成功标准、预期回答、反馈要点和课堂练习答案。教学设计的 `source_files` 必须登记该教材参考解答文件。

练习册为可选项。存在时必须在评价设计前完成三件套校验：题库文件通过 `tools/validate-workbook-split.py`，答案文件通过 `tools/validate-workbook-answer-split.py`，逐题索引通过 `tools/validate-workbook-index.py`。校验失败时报告问题但可继续，仅教材资源可用。评价、活动和作业中引用练习册题目时，必须使用索引中的 `WB-...` 题号，并在 `source_files` 登记题库、答案和索引。练习册缺失时，相关字段标记 `N/A`，双资源盘点仅基于教材进行。

教材与练习册资源必须先盘点后选题。教学设计必须在后台折叠层输出 `resource_audit`、`practice`、`homework`、`deferred_exercises`：当堂检测优先使用教材练习，练习册“夯实基础”可作为补充；课后作业必须分基础层必做、中间层必做、拓展层选做并标注预计用时；未进入当堂检测或课后作业的练习册题必须登记后移去向，不得静默遗漏。

### `/lesson-collab` outputs

- `outputs/{课时名}_教学设计.md`
- 文件头部必须包含 YAML front matter。
- `content_type: lesson`
- `command: lesson-collab`
- `review_status: pending_human_review`

### `/lesson-collab` 禁止事项

- 禁止跳过任何确认门（auto 模式下确认门自动确认，不是跳过：草稿照常生成、自查、写入中间 MD、锁定）。
- 禁止在标准模式下教师未确认时继续下游环节（auto 模式除外）。
- 禁止忽略教师修改意见直接使用原草稿继续（auto 模式下仅无教师交互，AI 自查修订）。
- 禁止将确认门交互过程写入最终教学设计正文（确认记录写入独立日志 `collab-gates.log.md`）。
- 禁止生成课件。
- 禁止生成课堂提问调度稿。
- 禁止执行课件validators。
- 禁止写入具体学生姓名；教学设计只标注提问层级。
- 禁止将未人工审核的教学设计标记为 `审核通过`。
- 禁止在 auto 模式下跳过中间 MD 文件输出；每个确认门必须将草稿写入对应 MD 文件。

---

## 3. 人工审核边界

`/lesson-collab` 完成后必须由教师人工审核。系统不得自动通过人工审核。

人工审核通过的最小动作：

```yaml
review_status: 审核通过
```

如有审核记录，应写入教学设计元数据中的 `review_notes`，或写入同名审核记录文件。详见 `orchestrator/review-protocol.md`。

---

## 4a. `/courseware-collab` 工作流（当前课件主链）

`/courseware-collab` 是当前唯一课件入口。它在**课件结构规划**、**课堂提问设计**、**分层提问分配**三个关键节点设置**确认门**。

输入格式：

```text
/courseware-collab [auto] 课时名称
```

示例：

```text
/courseware-collab 21.4
/courseware-collab 三角形的中位线
/courseware-collab 21.4 三角形的中位线
/courseware-collab auto 21.4
/courseware-collab auto 三角形的中位线
```

带上 `auto` 参数进入**自动确认模式**：课题确认仍等教师回复；确认门照常生成草稿、自检、写入中间 MD 文件后 AI 自动确认并继续，不暂停等待。详见 §4a 末尾「auto 模式」小节。

执行链：

```text
课题确认（解析课时名称 → 匹配教材课时分配表 → 检查教学设计状态 → 用户确认）
  ↓
定位并校验对应课时教材参考解答
  文件缺失、课时不匹配或验证失败 → 立即终止本次任务
  ↓
定位并校验对应课时练习册题库、答案和逐题索引
  练习册为可选项：缺失时不阻断，相关字段标记 N/A
  存在但校验失败 → 报告问题但可继续
  ↓
读取人工审核通过的教学设计
  ↓
🛑 确认门1：课件结构规划
  AI 呈现课件页面结构框架（含页面内容说明）
  → 教师审核页面顺序和设置
  → 教师确认后继续
  ↓
🛑 确认门2：课堂提问设计
  AI 呈现各页面的问题设计及揭示顺序（问题页→按需备用提示页→答案/归纳页）
  → 教师审核提问质量和覆盖度
  → 教师确认后继续
  ↓
🛑 确认门3：分层提问分配
  AI 呈现学生姓名分配方案（基础层/中间层/拓展层对应哪些学生）
  → 教师审核分配合理性
  → 教师确认后继续
  ↓
生成课堂提问调度稿
  ↓
生成 Markdown 课件（基于确认的结构、提问、选人）
  ↓
课件验证
  ↓
图片验证
  ↓
outputs课件与课堂提问调度稿
```

### `/courseware-collab` auto 模式

带上 `auto` 参数的 `/courseware-collab` 进入自动确认模式：

**与标准模式的区别：**

1. **课题确认**：保留，仍等待教师回复确认课题信息及教学设计状态
2. **教材参考解答**：存在且校验通过 → 直接使用。缺失 → 自动触发 `/教材问题解答` 生成，与课件结构规划并行推进；课堂提问设计在教材解答就绪后方可开始（提问设计中教材题答案需复用解答）
3. **练习册校验**：同标准模式，练习册可选，缺失不阻断。存在时校验与读取教学设计、课件结构规划并行
4. **确认门**：全部**自动确认** — AI 照常生成草稿、自查、锁定为下游输入，但不暂停等待教师回复，直接进入下一环节
5. **课件生成** ‖ **课堂提问调度稿生成**：两者基于相同的已确认结构和提问，并行生成
6. **课件验证** ‖ **图片验证**：互不依赖，并行执行

**并行执行流：**

```text
课题确认（等待教师）
  ↓
┌─ 教材解答缺失？触发 /教材问题解答 ──→ 解答生成 ──→ 校验通过 ──┐
├─ 练习册存在？三件套校验 ──────────────────────────────────┤
│                                                          │
└─ 读取教学设计 → 课件结构规划 → ──────────────→ 课堂提问设计（等解答+练习册就绪）
                                                          ↓
                                                    分层提问分配
                                                          ↓
                                              ┌─ 课件生成 ──────────┐
                                              └─ 课堂提问调度稿生成 ──┘
                                                          ↓
                                              ┌─ 课件验证 ──┐
                                              └─ 图片验证 ──┘
                                                          ↓
                                                       outputs
```

**确认门行为：**

- 每个确认门仍完整生成结构化草稿
- 草稿写入中间 MD 文件（见下方目录结构）
- 课堂提问调度稿 `collab_gates` 字段记录 `status: auto_confirmed`，`teacher_notes: "auto"`
- 若某环节自查发现问题，AI 自行修订后重新锁定，最多 3 次；3 次仍未通过则终止并报告

**中间产物目录：**

```text
outputs/lessons/ch{章节号}/{lesson_id}/
├── 01-structure.md                           # 确认门1：课件结构规划
├── 02-questions.md                           # 确认门2：课堂提问设计
├── 03-assignment.md                          # 确认门3：分层提问分配
├── lesson-{lesson_id}-courseware.md          # 最终课件
└── lesson-{lesson_id}-question-dispatch.md   # 最终课堂提问调度稿
```

**auto 模式仍必须消费 `review_status: 审核通过` 的教学设计。** 课件验证和图片验证与标准模式完全相同。

**执行指引（主 Agent 并行调度）：**

1. **课题确认后**，同时推进：
   - 教材解答缺失时：`task(run_in_background=true)` 派发子 Agent 执行 `/教材问题解答 {课时}`
   - 练习册存在时：主 Agent 自行校验三件套，与课件结构规划并行
   - 主 Agent 自行读取教学设计并推进课件结构规划，写入 `01-structure.md`

2. **课堂提问设计前 wait 点**：若派发了教材解答子 Agent，调用 `wait` 等待其完成并校验返回报告

3. **分层提问分配完成后**，同时派发：
   - `task(run_in_background=true)` 派发子 Agent 执行课件生成，子 Agent 写入 `lesson-{lesson_id}-courseware.md`
   - `task(run_in_background=true)` 派发子 Agent 执行课堂提问调度稿生成，子 Agent 写入 `lesson-{lesson_id}-question-dispatch.md`
   - `wait` 两者全部完成后继续

4. **验证阶段**，用 `parallel_tasks` 同时派发课件验证 + 图片验证，全部返回后 output

### 确认门交互协议

每个确认门必须遵循以下交互规范：

1. **呈现草稿**：AI 以结构化格式呈现当前环节的草稿outputs
2. **标注关键决策点**：AI 明确列出"需要您确认的关键点"（3-5条），聚焦该环节最影响下游质量的决策
3. **等待教师回复**：教师可回复：
   - **确认**：回复"确认""是""对""正确"等肯定词 → 进入下一环节
   - **修改意见**：指出需要调整的具体内容 → AI 修订后重新呈现，回到步骤1
   - **补充信息**：提供 AI 未考虑的学情/教学信息 → AI 整合后重新呈现，回到步骤1
4. **锁定确认版本**：教师确认后，该环节outputs作为下游的锁定输入，不可回退修改（除非后续环节发现逻辑矛盾）
5. **确认记录**：每个确认门的确认结果记录在课堂提问调度稿 YAML front matter 的 `collab_gates` 字段中；学生课件不写后台元数据

### 确认门呈现模板

每个确认门呈现时，AI 必须使用以下格式：

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

### 各确认门的关键决策点

| 确认门 | 关键决策点 |
|--------|-----------|
| 确认门1：课件结构规划 | 页面顺序是否合理；是否遵循教材原文顺序；关键页面是否完整；复杂例题的分拆方式是否合适 |
| 确认门2：课堂提问设计 | 是否已读取并执行提问质量skills自检；是否先呈现问题、学生停滞后再逐级提示；学生课件是否隐藏教师参考预期；问题是否对结论负责 |
| 确认门3：分层提问分配 | 学生分层是否合理；分配是否符合学情数据；是否避免连续提问同一学生 |

### `/courseware-collab` 课题确认环节

按以下规则执行：解析课时名称 → 匹配教材课时分配表 → 检查教学设计状态 → 用户确认。

### `/courseware-collab` 强制读取

强制读取以下文件，额外增加：

12. `orchestrator/skill-protocol.md` 中 §3a `/courseware-collab` 强制链
13. `skills/ask-check/SKILL.md` 和 `skills/ask-check/checklist.md`（到确认门2前再读取并自检）
14. `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md`
15. 对应课时 `knowledge/workbooks/workbook-*.md`
16. 对应课时 `knowledge/workbook-answers/workbook-answer-*.md`
17. 对应课时 `knowledge/workbook-index/workbook-index-*.yaml`

教材参考解答必须在读取教学设计和进入确认门1前完成校验：文件存在，`content_type: textbook_solution`，`lesson_id` 与当前课时一致，并通过教材问题解答validators。任一条件不满足时立即终止本次任务，报告预期路径或失败项，并提示执行 `/教材问题解答 {课时}` 后重新发起 `/courseware-collab`。禁止自动补齐、降级推导、跳过校验或继续后续确认门。

课堂提问调度稿中直接对应教材任务的板块A答案，以及板块B中的教材例题、练习和习题解答，必须按 `question_id` 复用教材参考解答。允许压缩表达，不得改变数学结论、解题依据和 `答案来源`。练习册题仍按练习册题源处理。课堂提问调度稿的 `source_files` 必须登记教材参考解答和课件所消费的上游文件。

练习册为可选项。存在时必须在确认门1前完成校验。课堂提问调度稿中所有 `source_type: exercise_bank` 的题目必须按 `question_id` 从索引定位题目，并按 `answer_ref` 读取答案文件生成教师参考答案；禁止重新推导后替代答案册边界。课堂提问调度稿的 `source_files` 必须登记题库、答案和索引。练习册缺失时，相关字段标记 `N/A`。

### `/courseware-collab` outputs

- `outputs/lessons/ch{章节号}/{lesson_id}/lesson-{lesson_id}-courseware.md`
- `outputs/lessons/ch{章节号}/{lesson_id}/lesson-{lesson_id}-question-dispatch.md`

课堂提问调度稿必须与课件使用同一教学设计 `lesson_id`，并记录来源教学设计文件。课件通过同名文件和验证命令关联，不在投屏正文写后台字段。

课堂提问调度稿文件头部必须包含 YAML front matter，额外字段 `collab_gates`：

```yaml
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

### `/courseware-collab` 禁止事项

- 禁止跳过任何确认门（auto 模式下确认门自动确认，不是跳过：草稿照常生成、自查、写入中间 MD、锁定）。
- 禁止在标准模式下教师未确认时继续下游环节（auto 模式除外）。
- 禁止忽略教师修改意见直接使用原草稿继续（auto 模式下仅无教师交互，AI 自查修订）。
- 禁止将确认门交互过程、YAML、HTML、代码块或后台字段写入最终课件正文；确认记录只写入课堂提问调度稿元数据。
- 禁止重新生成学习目标。
- 禁止重新生成评价任务。
- 禁止重新生成活动设计。
- 禁止消费未人工审核的教学设计。
- 禁止使用非同级 `images/` 的图片路径。
- 禁止虚构学生姓名。
- 禁止在 auto 模式下跳过中间 MD 文件输出；每个确认门必须将草稿写入对应 MD 文件。

---

## 6. `/临界生` 工作流

输入格式：

```text
/临界生 [责任教师] [任教班级] [教材章节]
```

示例：
```text
/临界生 李金生 八（3）班 chapter_21
```

执行链：

```text
规则确认
  ↓
读取学生近期成绩数据
  ↓
读取近期学习章节知识点
  ↓
识别临界生（5名左右）
  ↓
结合知识点填写"本周期待提高内容"
  ↓
根据学生特点勾选帮扶核心方向
  ↓
outputs临界生分工表
```

### `/临界生` 强制读取

1. `AGENTS.md`
2. `orchestrator/workflow-registry.md`
3. `skills/support/SKILL.md`
4. `skills/support/checklist.md`
5. `students/scores.md`
6. `knowledge/[章节]/` 下的知识点信息
7. `students/support/template.md`

### `/临界生` outputs

- `support/临界生分工表-YYYY-MM-DD.md`
- `support/临界生分工表-YYYY-MM-DD.xlsx` (可选，Excel格式)
- 文件头部必须包含 YAML front matter。
- `content_type: borderline_students`
- `command: 临界生`

### `/临界生` Excel导出

可以使用以下命令将Markdown表格导出为Excel格式：

```bash
python tools/export_excel.py support/临界生分工表-YYYY-MM-DD.md
```

Excel格式要求：
- A4纸张，横向排版
- 合适的列宽和行高
- 表格边框和标题样式
- 可直接打印

### `/临界生` 禁止事项

- 禁止修改 `students/support/template.md`
- 禁止生成其他类型的文件（课件、教学设计等）
- 禁止使用非真实学生姓名

---

## 7. `/教材问题解答` 工作流

输入格式：

```text
/教材问题解答 [课时编号或课时名称]
```

执行链：

```text
课题匹配与确认
  ↓
读取完整教材原文及相关图片
  ↓
按原文顺序提取全部问题和任务指令
  ↓
生成并核对教材任务清单
  ↓
区分教材原文解答与AI参考推导
  ↓
按题型生成逐题参考解答
  ↓
数学复核、覆盖检查、顺序检查和认知边界检查
  ↓
执行教材问题解答validators
  ↓
写入教材参考解答knowledge
```

### 强制读取

1. `AGENTS.md`
2. `orchestrator/skill-protocol.md`
3. `orchestrator/workflow-registry.md`
4. `orchestrator/output-contract.md`
5. `skills/solutions/SKILL.md`
6. `skills/solutions/spec.md`
7. `skills/solutions/checklist.md`
8. `validators/solutions/rules.md`
9. `knowledge/textbooks/教材原文_教材课时分配.md`
10. 对应课时完整教材原文、教材图片及必要的前置教材原文

### outputs

- `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md`
- `content_type: textbook_solution`
- 不设置 `review_status`
- 正常题目不设置审核状态或生成状态

### 禁止事项

- 禁止只解答练习和习题而遗漏正文及栏目任务。
- 禁止改写、补写或猜测教材题目。
- 禁止打乱教材问题顺序。
- 禁止虚构调查、班级、学校或实验数据。
- 禁止为开放题制造唯一答案。
- 禁止使用超出教材进度的概念或术语作为主解法。
- 禁止将 AI 推导标记为教材原文。

---

## 8. `/复习讲义` 工作流

输入格式：

```text
/复习讲义 [讲义编号或讲义名称]
```

示例：
```text
/复习讲义 01讲
/复习讲义 坐标方法简单应用
/复习讲义 第14讲
```

执行链：

```text
讲义确认（解析讲义编号或名称 → 匹配knowledge/reviews/目录下的文件 → 显示确认信息 → 用户确认）
  ↓
规则确认（读取复习课讲义整理 Skill 与检查清单）
  ↓
读取用户确认的全部knowledge复习讲义源文件
  ↓
源文件统计（对每个源文件统计：知识点数、即学即练题数、各题型N 典例数、各题型N 变式数）
  ↓
🛑 统计确认（呈现统计表格 → 用户确认统计数据；课后作业固定 10 题 → 锁定继续）
  ↓
知识点提取（从源讲义中提取全部知识点，保持源文知识顺序）
  ↓
例题选取（每个知识点配 1 道源题，优先来自「即学即练」）
  ↓
当堂练习选取（全部 题型N 典例全量纳入，不做筛选）
  ↓
课后作业选取（从变式中固定选取 10 题，优先级：例题变式 > 其他变式 > 有图综合题 > 原课后练习）
  ↓
搬运被选用题目的图片到outputs同级 images/
  ↓
生成复习讲义（按复习课格式整理，全讲义一套顺序编号）
  ↓
生成原始数量与选用数量对比表（置于docs末尾）
  ↓
执行复习讲义validators与 tools/validate_output.py
  ↓
outputs复习讲义到outputs目录
```

### `/复习讲义` 讲义确认环节

在执行 `/复习讲义` 命令时，必须先进行讲义确认，防止用户输入错误的讲义编号或名称。

**确认流程：**

1. **解析输入**：识别用户输入的讲义编号（如 `01讲`）或讲义名称（如 `坐标方法简单应用`）
2. **匹配文件**：从 `knowledge/reviews/` 目录中查找对应文件
3. **显示确认信息**：
   ```text
   📋 请确认讲义信息：
   
   讲义编号：第01讲
   讲义名称：坐标方法简单应用
   源文件：knowledge/reviews/01讲.md
   
   确认无误后，请回复"确认"或"是"继续整理复习讲义。
   如需修改，请重新输入正确的讲义编号或名称。
   ```
4. **等待用户确认**：用户回复"确认"、"是"、"对"、"正确"等肯定词后继续执行
5. **处理异常**：
   - 如果输入的讲义编号不存在，提示可用的讲义列表
   - 如果输入的讲义名称模糊匹配到多个结果，列出所有匹配项让用户选择
   - 如果完全无法匹配，提示用户检查输入或提供正确的讲义编号/名称

**匹配规则：**

| 输入类型 | 匹配方式 | 示例 |
|---------|---------|------|
| 讲义编号 | 精确匹配文件名 | `01讲` → 01讲.md |
| 讲义名称 | 关键词匹配文件内容 | `坐标方法` → 01讲.md |
| 第XX讲格式 | 组合匹配 | `第14讲` → 14讲.md |

### `/复习讲义` 强制读取

1. `AGENTS.md`
2. `orchestrator/workflow-registry.md`
3. `orchestrator/output-contract.md`
4. `skills/reviews/SKILL.md`
5. `skills/reviews/checklist.md`
6. `knowledge/types/复习课.md`
7. `validators/reviews/rules.md`
8. `knowledge/reviews/{讲义编号}.md`（源文件）

### `/复习讲义` outputs

- `outputs/reviews/{讲义编号}_{讲义名称}_复习讲义.md`
- 文件头部必须包含 YAML front matter。
- `content_type: review_lesson`
- `command: 复习讲义`
- `source_files`: 记录来源的新授课讲义文件列表
- `review_lesson` 不设置 `review_status`

### `/复习讲义` 禁止事项

- 禁止修改源文件（knowledge中的复习讲义）。
- 禁止打乱知识点顺序。
- 禁止虚构题目。
- 禁止不按规则选取例题、当堂练习和课后作业。
- 禁止使用非同级 `images/` 的图片路径。
- 禁止遗漏任何题型N 典例（当堂练习必须全量纳入）。
- 禁止在统计确认前直接开始生成讲义。
- 禁止原始数量与选用数量对比表行数与统计项不一致。
