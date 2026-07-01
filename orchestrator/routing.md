# Routing Rules

## 输入分类

### lesson request
→ lesson-generation-skill

### exercise request
→ 习题分析skills

### mixed request
→ workflow DAG

---

## 决策规则

### 教材原文拆解优先规则

IF 用户请求包含以下任一特征：

- 动词包含“分割 / 拆分 / 切分 / 拆解 / 按课时拆 / 教材原文处理”
- 路径或文件名包含 `knowledge/textbooks/`、`textbooks`、`教材原文`、`MinerU`
- 目标文件是单章教材 Markdown 大文件，如 `第X章 ... .md`

AND 任务目标是把教材 Markdown 大文件拆成课时文件

→ MUST route to `skills/textbook-split/SKILL.md`
→ MUST read `skills/textbook-split/checklist.md`
→ MUST use `tools/split_textbook.py` when writing split files

执行要求：

- 拆分前必须呈现章节结构、输出文件清单和 YAML 元信息预览。
- 未提供 `semester` 时必须向用户索取，不得猜测。
- 不得把“练习”“习题”“观察与思考”“做一做”“大家谈谈”等子标题拆成独立课时。
- 章引言必须归入第一个小节的第一课时。
- 若输出目标在当前运行模式无写入权限，必须先提示切换模式，不得写入。

---

IF contains "讲解 / 教学 / 设计"
→ lesson-generation-skill

IF contains "题 / 练习 / 解题"
→ 习题分析skills

IF multiple intents
→ workflow engine

---

## 禁止规则

- 禁止直接调用 workflow step
- 必须先 routing 再 skill dispatch

---

## Global Rule

If task involves "question / exercise / problem":

→ MUST route through retrieval-based Skill only
→ MUST NOT allow generative question creation
