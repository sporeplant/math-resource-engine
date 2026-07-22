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
- 禁止 LLM 绕过 `build_courseware.py` 手写最终课件 MD 或调度稿 MD。

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

- `outputs/{课时名}_课件规划.yaml`（确认门产出，LLM 填充）
- `outputs/{课时名}_课件.md`（由 `build_courseware.py` 从 YAML 机械生成）
- `outputs/{课时名}_课堂提问调度稿.md`（由 `build_courseware.py` 从 YAML 机械生成）

禁止：

- 不重新生成学习目标、评价任务、活动设计或教学设计。
- 不在用户未确认课题前直接开始生成。
- 禁止 LLM 绕过 `build_courseware.py` 手写最终课件 MD 或调度稿 MD。

---

## 2. 局部任务

用户只要求生成或审核某一局部资源时，可调用对应 Skill 或 Validator，但必须遵守：

- 先读取 `orchestrator/workflow-registry.md` 确认边界。
- 先读取对应 Skill 定义和检查清单。
- outputs仍需符合 `orchestrator/output-contract.md`。
- 涉及题目时必须执行题源探索并标注 `source_id`、`source_type`、`question_id`。

局部任务包括：

- 教材原文拆解类任务：当用户要求“分割/拆分/切分/拆解”教材 Markdown 大文件，或路径包含 `knowledge/textbooks/`、`textbooks`、`教材原文`、`MinerU` 时，必须优先路由到 `skills/textbook-split/SKILL.md`，读取其检查清单，并按该技能先呈现结构和元信息预览。
- 练习册题库拆解类任务：当用户要求“分割/拆分/切分/拆解”练习册、习题册、练习册题库 Markdown 大文件，或路径/文件名包含 `knowledge/workbooks/`、`workbooks`、`练习册`、`习题册` 时，必须优先路由到 `skills/workbook-split/SKILL.md`，读取其检查清单，并按该技能先呈现结构和输出文件预览。
- 练习册参考答案拆解类任务：当用户要求“分割/拆分/切分/拆解”练习册答案、参考答案、答案册 Markdown 大文件，或路径/文件名包含 `练习册答案`、`参考答案`、`答案册`、`workbook-answers` 时，必须优先路由到 `skills/workbook-answer-split/SKILL.md`，读取其检查清单，并按该技能先呈现结构和输出文件预览。
- 练习册逐题索引类任务：当用户要求“索引/建索引/逐题编号/题号映射/答案对齐”练习册题库或答案，或路径/文件名包含 `workbook-index` 时，必须优先路由到 `skills/workbook-index/SKILL.md`，读取其检查清单，并使用 `tools/index-workbook.py` 和 `tools/validate-workbook-index.py`。
- 学习目标类任务
- 评价设计类任务
- 活动设计类任务
- 教材分析类任务
- 习题分析类任务
- 审核类任务
- 图片资源检查类任务

---

## 3. 工具类任务

### 希沃课件生成（MD → HTML → JSON+PNG）— 主路径

特征：

- 用户要求"生成希沃课件"、"导出希沃"、"生成希沃白板"等。
- 用户提供或指向一个 `*课件.md` / `*-courseware.md` 文件。

路由：

1. 确认目标 Markdown 文件路径。
2. 执行一数风格 HTML 生成：
   ```bash
   python tools/md2htmlyishu.py "path/to/课件.md" --output-dir "path/to/exports/"
   ```
3. 输出同名 `.html` 至 `exports/`。
4. 自动继续执行 HTML 转希沃导入包：
   ```bash
   python tools/html_to_seewo.py "{HTML 文件路径}" --output-dir "{exports/路径}"
   ```
5. 完成后告知用户导入方式。

前置条件：

- Markdown 文件必须存在，且符合课件 MD 规范（`---` 分页）。
- Playwright + Chromium 已安装。

outputs：

- `{路径}/exports/{文件名}.html`：1920×1080 一数风格投屏课件
- `{路径}/exports/{文件名}.json` — MrePlugin 课件描述文件
- `{路径}/exports/assets/slide_01.png` ~ `slide_N.png` — 逐页截图

---

### 一数风格 HTML 课件生成（MD → HTML）— 仅 HTML

特征：

- 用户**仅**要求"生成一数风格 HTML"、"转成投屏课件"、"MD 转 HTML 课件"，且**未提希沃**。
- 用户提供或指向一个 `*课件.md` 文件。

路由：`skills/md2htmlyishu/SKILL.md`

1. 确认目标 Markdown 文件路径。
2. 执行：
   ```bash
   python tools/md2htmlyishu.py "path/to/课件.md" --output-dir "path/to/exports/"
   ```
3. 输出同名 `.html` 至 `exports/`。
4. **必须询问用户**是否继续生成希沃白板导入包。

前置条件：

- Markdown 文件必须存在，且符合课件 MD 规范（`---` 分页）。

outputs：

- `{路径}/exports/{文件名}.html`：1920×1080 一数风格投屏课件。

---

### HTML 转希沃导入包（HTML → JSON + PNG）— 独立转换

特征：

- 用户**已有 HTML 文件**，要求"HTML 转希沃"、"把这个 HTML 导成希沃课件"、"生成希沃导入包"。
- 用户提供或指向一个 HTML 课件文件（路径含 `.html`）。

路由：`skills/html-to-seewo/SKILL.md`

1. 确认目标 HTML 文件路径。
2. 执行：
   ```bash
   python tools/html_to_seewo.py "{HTML 文件路径}" --output-dir "exports/"
   ```
3. 完成后告知用户导入方式。

前置条件：

- HTML 文件必须存在，且包含 `.slide` 元素。
- Playwright + Chromium 已安装。

outputs：

- `{目录}/exports/{文件名}.json` — MrePlugin 课件描述文件
- `{目录}/exports/assets/slide_01.png` ~ `slide_N.png` — 逐页截图

---

### 希沃白板 JSON 生成（MD → JSON）[已归档]

> **已归档**：此管线已被「希沃课件生成（MD → HTML → JSON+PNG）主路径」取代。
> 旧工具 `tools/md_to_easinote_json.py` 保留但不再作为默认推荐路径。
> 归档原因：直接 JSON 管线产出的文本/公式对象在希沃端兼容性不稳定，截图版（HTML → PNG）视觉一致性更好。

特征：

- 用户**明确**要求"生成希沃 JSON"、"MD 直接转希沃 JSON"（显式指定 JSON 格式）。

路由：

1. 确认目标 Markdown 文件路径。
2. 执行：
   ```bash
   python tools/md_to_easinote_json.py <courseware.md> [output.json]
   ```
3. 输出 `<stem>.json` 至 MD 同级目录（默认）。
4. 告知用户用希沃插件导入。

前置条件：

- Markdown 文件必须存在。

outputs：

- `{路径}/{文件名}.json`：可直接导入希沃白板 5 的 MrePlugin 格式课件。

---

## 4. 冲突处理

当用户输入与历史docs中的旧流程冲突时，以 `orchestrator/workflow-registry.md` 为准。

典型旧流程冲突：

- 把课件生成放入 `/lesson-collab`。
- 使用旧的外部课件生成表述。
- 让 `/courseware-collab` 重新生成目标、评价或活动。
- 使用旧的中间层别名。
- 使用非同级 `images/` 的图片路径。

