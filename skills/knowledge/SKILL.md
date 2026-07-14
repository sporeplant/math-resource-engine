# 知识分析skills

## skills目标

在教学设计前分析知识本质、知识生长路径和数学思想。

禁止直接进入活动设计。

---

## 输入

* 教材内容（由 `skills/textbook/SKILL.md` 提供分析素材）
* 学习主题
* 章节内容
* 习题分析结果（由 `skills/exercises/SKILL.md` 提供分析结果）
* 数学本质分析（由 `knowledge/math-essence/INDEX.yaml` 定位的对应文件）
* 常见错误（由 `knowledge/common-errors/INDEX.yaml` 定位的对应文件）
* 教学策略（由 `knowledge/teaching-strategies/INDEX.yaml` 定位的对应文件）
* 学情行为与反馈（`knowledge/learning-theory/` 下文件）

---

## 课型判断规则

从课时名称中提取关键词，匹配对应课型定义文件，确定标准流程框架。

| 课时名称特征 | 课型 | 读取文件 |
|-------------|------|----------|
| 含"复习课"且含"第X章"（非"单元"） | 复习课 | `knowledge/types/复习课.md` |
| 含"单元复习" | 单元复习课 | `knowledge/types/单元复习课.md` |
| 含"期中复习" | 期中复习课 | `knowledge/types/期中复习课.md` |
| 含"期末复习" | 期末复习课 | `knowledge/types/期末复习课.md` |
| 含"活动课"或"项目学习" | 数学活动课 | `knowledge/types/数学活动课.md` |
| 含"习题课"或"练习课" | 习题课 | `knowledge/types/习题课.md` |
| 含"试卷讲评"或"考试讲评" | 试卷讲评课 | `knowledge/types/试卷讲评课.md` |
| 其他（新概念/性质/定理第一课时） | 新授课 | `knowledge/types/new.md` |

---

## outputs

知识分析使用**结构化 Markdown** 输出，**禁止使用代码块**（` ```yaml ` 等）。代码块内的 LaTeX 公式（`$...$`）不会被 Typora 渲染。

```markdown
**知识主题**：

**知识本质**：（含核心数学关系，使用 $...$ 行内公式）

**知识来源**：

**知识生长路径**：

> 前置：...
> ↓ ...
> 本课核心 ...
> ↓ ...
> 后续：...

**前置知识**：
- 
- 

**后续知识**：
- 
- 

**核心思想**：
- 类比思想：...
- 转化思想：...
- 

**学习难点**：
- 
- 

**常见误解**：
- 
- 

### 活动设计上下文

**math_essence**：（从 math-essence 文件提炼，简明扼要）

**critical_aspects**：（学生必须辨识的关键方面）
- 
- 

**cognitive_obstacles**：（已有认识、典型错误和认知障碍，综合 math-essence + common-errors + learning-theory）
- 
- 

**target_cognitive_changes**：（希望学生从何种理解转变为何种理解）
- 从... → ...

**variation_dimensions**：（哪些量需要变化，哪些量保持不变）
- 变：...
- 不变：...

**activity_constraints**：（活动必须做到或必须避免的事项，综合 teaching-strategies + learning-theory + feedback-strategies）
- 
- 

**source_refs**：（本次使用的知识文件路径列表）
- "knowledge/textbooks/..."
- "knowledge/standards/..."
```

---

## 分析流程

### Step1 知识本质分析

回答：

* 学生到底要学什么？
* 本节课最重要的数学关系是什么？

---

### Step2 知识生长分析

回答：

* 这个知识从哪里来？
* 为什么会产生？
* 如何形成？

优先体现：

观察 → 猜想 → 验证 → 归纳

---

### Step3 前后联系分析

分析：

* 前置知识
* 后续知识

形成知识网络。

---

### Step4 数学思想分析

识别：

* 分类思想
* 转化思想
* 数形结合
* 归纳思想
* 演绎思想
* 一般到特殊
* 特殊到一般

---

### Step5 学习困难分析

识别：

* 学生易错点
* 学生常见误解
* 容易混淆概念

---

### Step6 提炼活动设计上下文

综合读取的全部知识文件，提炼出供下游活动设计使用的结构化中间结果。每条必须具体、可操作，不空泛。

回答：
* math_essence：本节课核心数学关系的本质是什么？不要复述教材定义。
* critical_aspects：学生必须辨识哪些方面才能理解这个概念？什么特征必须注意，什么可以忽略？
* cognitive_obstacles：学生的已有认识中哪些会成为障碍？典型错误有哪些？预判错误率高的类型是什么？
* target_cognitive_changes：希望学生从什么理解转变到什么理解？（如：从靠外观判断到靠条件判断）
* variation_dimensions：设计例子时，哪些属性要变（大小、方向、位置），哪些要保持不变（关键定义属性）？
* activity_constraints：活动必须做到什么（如：包含反例、对比原型与非原型），必须避免什么（如：不强制两步判定、不超过3分钟连续讲授）？
* source_refs：列出本次实际读取的所有知识文件路径，用于可追溯性。

---

## outputs要求

禁止直接设计活动。

仅outputs知识分析结果。

**格式规则**：知识分析在 lesson plan 的 `## knowledge_analysis` 节中必须使用结构化 Markdown（加粗标签 `**字段名**：` + 列表 + `>` 引用块），**禁止使用代码块**。代码块内的 LaTeX 公式（`$...$`）不会被 Typora 渲染。