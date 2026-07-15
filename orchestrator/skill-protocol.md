# skills调用协议

定义系统响应教学资源生成请求时的强制调用规则。工作流顺序以 `orchestrator/workflow-registry.md` 为唯一权威来源。

---

## 1. 调用总则

任何涉及 Skill outputs的任务，必须执行：

```text
读取 AGENTS.md
  ↓
读取 orchestrator/workflow-registry.md
  ↓
读取对应 Skill 定义和检查清单
  ↓
按 orchestrator/output-contract.md 与 orchestrator/skill-contract.md 生成
  ↓
执行对应 Validator 与 tools/validate_output.py 硬规则检查
  ↓
通过后outputs
```

禁止：

- 未读取工作流注册表直接生成。
- 跳过对应 Skill 定义。
- 跳过检查清单。
- 跳过题源字段。
- 自检不通过仍outputs。

---

## 2a. `/lesson-collab` 强制链（当前教学设计主链）

`/lesson-collab` 的完整步骤见 `orchestrator/workflow-registry.md` §2a。

`/lesson-collab` 是当前唯一教学设计入口，在知识分析、学习目标、评价设计、活动设计四个关键节点设置确认门。

**前置环节：课题确认**

按课题确认规则执行。

**强制步骤链：**

```text
课题确认（按课题确认规则执行）
  ↓
定位并校验对应课时教材参考解答（缺失、验证失败或 review_status ≠ 审核通过立即终止）
  ↓
定位并校验对应课时练习册题库、答案和逐题索引（练习册可选：缺失不阻断；存在但校验失败报告问题但可继续）
  ↓
知识分析（AI 生成草稿）
  ↓
🛑 确认门1：知识分析确认
  AI 呈现课型判断、知识点拆解、重难点定位
  → 标注关键决策点
  → 暂停等待教师回复
  → 教师确认后继续 / 教师修改后AI修订再呈现
  ↓
学习目标设计（AI 基于确认的知识分析生成草稿）
  ↓
🛑 确认门2：学习目标确认
  AI 呈现三层学习目标及行为动词
  → 标注关键决策点
  → 暂停等待教师回复
  → 教师确认后继续 / 教师修改后AI修订再呈现
  ↓
评价任务设计（AI 基于确认的目标生成草稿）
  ↓
🛑 确认门3：评价设计确认
  AI 呈现评价任务与目标的对应关系、成功标准
  → 标注关键决策点
  → 暂停等待教师回复
  → 教师确认后继续 / 教师修改后AI修订再呈现
  ↓
问题链设计（AI 自动完成，无需确认）
  ↓
活动设计（AI 基于确认的上游生成草稿）
  ↓
🛑 确认门4-1：教材顺序与模块任务确认
  AI 呈现教材原文内容模块列表，标注每个模块对应的任务类型（读懂/思考/交流/书写/操作等）
  → 标注关键决策点
  → 暂停等待教师回复
  → 教师确认后继续 / 教师修改后AI修订再呈现
  ↓
🛑 确认门4-2：活动步骤逐步确认
  AI 按模块逐个呈现活动步骤，标注每个步骤的时间分配
  → 标注关键决策点
  → 暂停等待教师回复
  → 教师确认后继续 / 教师修改后AI修订再呈现
  ↓
🛑 确认门4-3：台阶提问确认
  AI 呈现完整的问题编号列表（如 ASK_B_01, ASK_M_02, ASK_E_03），每个问题按“提问→分级备用提示→教师参考预期”排列
  → 标注关键决策点
  → 暂停等待教师回复
  → 教师确认后继续 / 教师修改后AI修订再呈现
  ↓
🛑 确认门4-4：整体整合确认
  AI 呈现完整的活动设计整合版（含教材对应位置、题源、升华等）
  → 标注关键决策点
  → 暂停等待教师回复
  → 教师确认后继续 / 教师修改后AI修订再呈现
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

**确认门交互规范：**

1. AI 必须以结构化格式呈现草稿（使用 `orchestrator/workflow-registry.md` §2a 中的确认门呈现模板）
2. AI 必须明确标注"需要您确认的关键点"（3-5条）
3. 教师确认后才可进入下一步
4. 教师修改意见必须被完整采纳，AI 修订后重新呈现
5. 确认后的内容作为下游的锁定输入，不可回退修改（除非后续环节发现逻辑矛盾）
6. 每个确认门的确认结果记录在独立日志文件 `{output_dir}/collab-gates.log.md`，不写入教学设计的 YAML front matter

强制读取：

- 读取以下基础强制文件：
- 额外读取 `orchestrator/workflow-registry.md` §2a 中的确认门交互协议和呈现模板
- `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md`
- 对应课时 `knowledge/workbooks/workbook-*.md`
- 对应课时 `knowledge/workbook-answers/workbook-answer-*.md`
- 对应课时 `knowledge/workbook-index/workbook-index-*.yaml`

教材参考解答必须在知识分析前校验文件存在、`content_type: textbook_solution`、`lesson_id` 匹配、`review_status: 审核通过`，并通过教材问题解答validators。缺失或校验失败时终止本次任务，禁止自动生成、降级推导、跳过校验或继续确认门。教学设计的 `source_files` 必须登记该文件，教材题的评价证据、活动预期回答和练习答案必须按 `question_id` 与之核对。

练习册为可选项。存在时必须在评价设计前校验通过。练习册题目进入评价、活动或作业时，必须使用索引中的 `WB-...` 题号，教学设计 `source_files` 必须登记对应题库、答案和索引。缺失时不阻断，相关字段标记 `N/A`。

outputs：

- `outputs/{课时名}_教学设计.md`
- `review_status: pending_human_review`
- `command: lesson-collab`
- 确认门记录写入独立日志 `collab-gates.log.md`（YAML front matter 不得包含 `collab_gates` 字段）

禁止：

- 跳过任何确认门（auto 模式下确认门自动确认，不是跳过）。
- 在标准模式下教师未确认时继续下游环节（auto 模式除外）。
- 忽略教师修改意见直接使用原草稿继续（auto 模式下无教师交互，AI 自查修订）。
- 将确认门交互过程写入最终教学设计正文。
- 生成课件。
- 生成课堂提问调度稿。
- 执行课件validators。
- 自动标记 `审核通过`。
- 在用户未确认课题前直接开始生成教学设计（auto 模式下课题确认仍等待教师回复）。

---

## 3a. `/courseware-collab` 强制链（当前课件主链）

`/courseware-collab` 的完整步骤见 `orchestrator/workflow-registry.md` §4a。

`/courseware-collab` 是当前唯一课件入口，在**课件结构规划**、**课堂提问设计**、**分层提问分配**三个关键节点设置确认门。

**前置环节：课题确认**

按课题确认与教学设计状态检查规则执行。

**强制步骤链：**

```text
课题确认（按课题确认与教学设计状态检查规则执行）
  ↓
定位并校验对应课时教材参考解答（缺失或失败立即终止）
  ↓
定位并校验对应课时练习册题库、答案和逐题索引（练习册可选：缺失不阻断；存在但校验失败报告问题但可继续）
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

**确认门交互规范：**

1. AI 必须以结构化格式呈现草稿（使用 `orchestrator/workflow-registry.md` §4a 中的确认门呈现模板）
2. AI 必须明确标注"需要您确认的关键点"（3-5条）
3. 教师确认后才可进入下一步
4. 教师修改意见必须被完整采纳，AI 修订后重新呈现
5. 确认后的内容作为下游的锁定输入，不可回退修改（除非后续环节发现逻辑矛盾）
6. 每个确认门的确认结果记录在课堂提问调度稿 YAML front matter 的 `collab_gates` 字段；学生课件保持 Typora 纯 Markdown

强制读取：

- 读取以下基础强制文件：
- 额外读取 `orchestrator/workflow-registry.md` §4a 中的确认门交互协议和呈现模板
- `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md`
- 对应课时 `knowledge/workbooks/workbook-*.md`
- 对应课时 `knowledge/workbook-answers/workbook-answer-*.md`
- 对应课时 `knowledge/workbook-index/workbook-index-*.yaml`

教材参考解答必须在读取教学设计和进入确认门1前校验文件存在、`content_type: textbook_solution`、`lesson_id` 匹配并通过教材问题解答validators。缺失或校验失败时终止本次任务。教材题答案按 `question_id` 复用，练习册题继续使用原题源；课堂提问调度稿的 `source_files` 必须登记该文件。

练习册为可选项。存在时必须在进入确认门1前校验通过。调度稿中所有练习册题目的 `question_id` 必须能在逐题索引中找到，并按索引的 `answer_ref` 读取答案文件。缺失时不阻断，相关字段标记 `N/A`。

outputs：

- 按课件与课堂提问调度稿outputs规范执行
- 课堂提问调度稿 YAML front matter 包含 `collab_gates` 字段；学生课件不设置 YAML

禁止：

- 禁止跳过任何确认门（auto 模式下确认门自动确认，不是跳过）。
- 禁止在标准模式下教师未确认时继续下游环节（auto 模式除外）。
- 禁止忽略教师修改意见直接使用原草稿继续（auto 模式下无教师交互，AI 自查修订）。
- 禁止将确认门交互过程写入最终课件正文。
- 禁止重新生成学习目标、评价任务、活动设计。
- 禁止消费未人工审核的教学设计。
- 禁止使用非同级 `images/` 的图片路径。
- 禁止虚构学生姓名。
- 禁止在用户未确认课题前直接开始生成课件（auto 模式下课题确认仍等待教师回复）。

---

## 4. `/临界生` 强制链

`/临界生` 的完整步骤见 `orchestrator/workflow-registry.md`。

强制读取：

- `AGENTS.md`
- `orchestrator/workflow-registry.md`
- `skills/support/SKILL.md` 和 `检查清单.md`
- `students/scores.md`
- `knowledge/[章节]/` 下的知识点信息
- `students/support/template.md`

outputs：

- `support/临界生分工表-YYYY-MM-DD.md`

禁止：

- 修改 `students/support/template.md`
- 生成其他类型的文件（课件、教学设计等）
- 使用非真实学生姓名

---

## 5. `/教材问题解答` 强制链

完整流程见 `orchestrator/workflow-registry.md` §7。

强制读取：

- `AGENTS.md`
- `orchestrator/workflow-registry.md`
- `orchestrator/output-contract.md`
- `orchestrator/skill-contract.md`
- `skills/solutions/SKILL.md`
- `skills/solutions/spec.md` 和 `检查清单.md`
- `validators/solutions/rules.md`
- 教材课时分配表、对应完整教材原文、图片及必要前置教材原文

outputs：

- `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md`
- `content_type: textbook_solution`
- 不设置 `review_status`

禁止：

- 漏掉任何教材问题或任务指令。
- 改写题目、补造题目或猜测图片条件。
- 打乱教材原文顺序。
- 将 AI 推导答案标记为教材原文。

---

## 6. `/复习讲义` 强制链

完整流程见 `orchestrator/workflow-registry.md` §8。

强制读取：

- `AGENTS.md`
- `orchestrator/workflow-registry.md`
- `orchestrator/output-contract.md`
- `skills/reviews/SKILL.md`
- `skills/reviews/checklist.md`
- `knowledge/types/复习课.md`
- `validators/reviews/rules.md`
- 用户确认的 `knowledge/reviews/{讲义编号}.md` 源文件

执行链：

```text
讲义确认（解析讲义编号或名称 → 匹配源文件 → 显示确认信息 → 用户确认）
  ↓
读取复习讲义 Skill、检查清单和复习课规则
  ↓
读取用户确认的源讲义文件
  ↓
按源文顺序提取知识点、例题、即学即练、题型精讲、强化训练和课后题
  ↓
按 24 题左右、知识点均衡、题型和难度接近原文比例整理
  ↓
搬运被选用题目的图片到outputs同级 images/
  ↓
生成复习讲义
  ↓
执行复习讲义validators与 tools/validate_output.py
  ↓
验证通过后outputs
```

outputs：

- `outputs/reviews/{讲义编号}_{讲义名称}_复习讲义.md`
- `content_type: review_lesson`
- `command: 复习讲义`

禁止：

- 修改 `knowledge/reviews/` 源文件。
- 虚构题目、改写题目或用仿题替代原题。
- 只偏向某一个知识点选题。
- 总览行数与正文题目数不一致。
- 图片未搬运到outputs文件同级 `images/`。
- 自检或验证不通过仍outputs为正式产物。

---

## 7. 局部 Skill 任务

局部任务可以单独调用某个 Skill，但仍需：

- 读取 `orchestrator/workflow-registry.md` 确认边界。
- 读取对应 Skill 定义和检查清单。
- 使用基础层、中间层、拓展层。
- 涉及题目时标注 `source_id`、`source_type`、`question_id`。
- 涉及图片时只使用 `./images/文件名`。

---

## 8. 违规处理

| 违规类型 | 处理方式 |
|---------|----------|
| 未读取工作流注册表 | outputs无效，回到规则确认 |
| `/lesson` 或 `/courseware` | 命令已归档，停止并提示使用对应 `-collab` 命令 |
| `/lesson-collab` 生成课件 | outputs无效，删除课件环节 |
| `/courseware-collab` 读取未审核教学设计 | 停止，提示人工审核 |
| 使用禁止词汇 | 回退生成步骤 |
| 缺少三层结构 | 回退生成步骤 |
| 缺少题源字段 | 回退题源探索 |
| 图片路径不合规 | 回退图片准备 |
| 自检不通过仍outputs | 标记为 draft，不得发布 |
