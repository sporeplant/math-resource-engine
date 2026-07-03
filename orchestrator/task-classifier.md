# 任务分类器

任务分类器只负责把用户输入路由到 `orchestrator/workflow-registry.md` 中登记的工作流，不维护独立步骤链。

---

## 1. 命令类任务

### `/lesson-collab`

特征：

- 用户输入以 `/lesson-collab` 开头。
- 用户要求生成完整教学设计。

路由：

1. **课题确认阶段**：
   - 解析用户输入的课时名称（章节号或课时名称）
   - 从 `knowledge/textbooks/教材原文_教材课时分配.md` 匹配对应课时
   - 显示确认信息，等待用户确认
   - 用户确认后才进入下一阶段

2. **执行阶段**：
   - 用户确认后，执行 `工作流注册表.md` → `/lesson-collab` 工作流

outputs：

- `outputs/{课时名}_完整教学设计.md`
- `review_status: pending_human_review`

禁止：

- 不生成课件。
- 不生成课堂提问调度稿。
- 不在用户未确认课题前直接开始生成。

### `/courseware-collab`

特征：

- 用户输入以 `/courseware-collab` 开头。
- 用户要求生成课件或课堂提问调度稿。

路由：

1. **课题确认阶段**：
   - 解析用户输入的课时名称（章节号或课时名称）
   - 从 `knowledge/textbooks/教材原文_教材课时分配.md` 匹配对应课时
   - 检查对应的教学设计文件是否存在且状态为 `review_status: 审核通过`
   - 显示确认信息，等待用户确认
   - 用户确认后才进入下一阶段

2. **执行阶段**：
   - 用户确认后，执行 `工作流注册表.md` → `/courseware-collab` 工作流

前置条件：

- 已存在人工审核通过的教学设计。
- 教学设计 `review_status: 审核通过`。

outputs：

- `outputs/{课时名}_课件.md`
- `outputs/{课时名}_课堂提问调度稿.md`

禁止：

- 不重新生成学习目标、评价任务、活动设计或教学设计。
- 不在用户未确认课题前直接开始生成。

### 已归档命令

- `/lesson`：已归档，不执行；提示改用 `/lesson-collab`。
- `/courseware`：已归档，不执行；提示改用 `/courseware-collab`。
- 禁止把归档命令静默改写为协作命令后直接执行，仍须由用户明确发起协作命令。

---

## 2. 局部任务

用户只要求生成或审核某一局部资源时，可调用对应 Skill 或 Validator，但必须遵守：

- 先读取 `orchestrator/workflow-registry.md` 确认边界。
- 先读取对应 Skill 定义和检查清单。
- outputs仍需符合 `orchestrator/output-contract.md`。
- 涉及题目时必须执行题源探索并标注 `source_id`、`source_type`、`question_id`。

局部任务包括：

- 教材原文拆解类任务：当用户要求“分割/拆分/切分/拆解”教材 Markdown 大文件，或路径包含 `knowledge/textbooks/`、`textbooks`、`教材原文`、`MinerU` 时，必须优先路由到 `skills/textbook-split/SKILL.md`，读取其检查清单，并按该技能先呈现结构和元信息预览。
- 学习目标类任务
- 评价设计类任务
- 活动设计类任务
- 教材分析类任务
- 习题分析类任务
- 审核类任务
- 图片资源检查类任务

---

## 3. 工具类任务

### 希沃白板 JSON 生成

特征：

- 用户要求"生成希沃 JSON"、"转成希沃课件"、"导出希沃格式"等。
- 用户提供或指向一个 `*-courseware.md` 文件。

路由：

1. 确认目标 Markdown 文件路径（如果用户未明确，列出候选并请用户选择）。
2. 执行：
   ```bash
   python tools/md_to_easinote_json.py <courseware.md> [output.json]
   ```
3. 输出 `<stem>.json` 至 MD 同级目录（默认），或用户指定路径。
4. 告知用户用希沃插件导入：右键空白页 → `MRE导入` → 选择 JSON。

前置条件：

- Markdown 文件必须存在。

outputs：

- `{路径}/{文件名}.json`：可直接导入希沃白板 5 的 lesson.json。

---

## 4. 冲突处理

当用户输入与历史docs中的旧流程冲突时，以 `orchestrator/workflow-registry.md` 为准。

典型旧流程冲突：

- 把课件生成放入 `/lesson-collab`。
- 使用旧的外部课件生成表述。
- 让 `/courseware-collab` 重新生成目标、评价或活动。
- 使用旧的中间层别名。
- 使用非同级 `images/` 的图片路径。
