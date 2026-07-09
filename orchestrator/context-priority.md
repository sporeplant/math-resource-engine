# 上下文优先级

定义分环节的注入知识优先级顺序和超长时的裁剪规则。

---

## 1. 分环节优先级

不再使用全局单一优先级链，改为按 Skill 所处的环节使用对应的优先级层。

### 1.1 教学主线层（objectives / assessment / activities / lesson）

```
课标 ＞ 学情 ＞ 数学本质 ＞ 教学策略 ＞ 教材 ＞ 练习册
```

| 优先级 | 内容 | 来源 |
|--------|------|------|
| 最高 | 课标要求 | 国家课程标准 |
| 高 | 学情数据 | students/ |
| 中高 | 数学本质分析 | math-essence/ |
| 中 | 教学策略建议 | teaching-strategies/ |
| 中低 | 教材内容结构 | 教材分析 |
| 低 | 练习册信息 | 习题分析 |

### 1.2 评价 / 练习 / 作业层（assessment / homework / question-dispatch）

```
教材原文 ＞ 练习册索引 ＞ 练习册题库 ＞ 练习册答案
```

| 优先级 | 内容 | 来源 |
|--------|------|------|
| 最高 | 教材原文题目（练习、习题A/B组） | knowledge/textbooks/ |
| 高 | 练习册逐题索引（含分层建议、题型、是否含图） | knowledge/workbook-index/ |
| 中 | 练习册题库原文 | knowledge/workbooks/ |
| 中低 | 练习册参考答案 | knowledge/workbook-answers/ |

- 练习册索引是选题的**首选入口**：通过 `tier`（基础/提升/应用）分层匹配，通过 `q_type`、`has_image`、`is_open_answer` 筛选
- 索引缺失时降级为直接扫描题库原文，但应提示补齐索引

### 1.3 课件 / 调度稿层（courseware / question-dispatch）

```
教学设计 ＞ 教材原文材料 ＞ 题源 ＞ 答案 ＞ 索引
```

| 优先级 | 内容 | 来源 |
|--------|------|------|
| 最高 | 审核通过的教学设计 | outputs/*_教学设计.md |
| 高 | 教材原文支撑材料（背景、数据、图表） | knowledge/textbooks/ |
| 中 | 题源字段（source_id / source_type / question_id） | outputs 中的题源标注 |
| 中低 | 参考答案（教材解答 / 练习册答案） | knowledge/solutions/ / knowledge/workbook-answers/ |
| 低 | 练习册索引 | knowledge/workbook-index/ |

---

## 2. 上下文超长裁剪规则

当注入内容超出上下文长度限制时，按以下顺序裁剪：

### 2.1 裁剪步骤

1. 首先裁剪当前环节最低优先级层
2. 其次裁剪教材层级的非核心内容
3. 再裁剪教学策略中的非直接相关内容
4. 保留课标和学情的原始内容（核心不可裁剪）
5. 保留数学本质的核心定义（仅保留最相关的部分）

### 2.2 保留底线

- 课标中学业要求部分必须保留
- 学情中的分层数据（三层比例和特征）必须保留
- 练习册索引中的 `question_id` / `tier` / `q_type` 必须保留（可裁剪 `text_snippet`）
- 裁剪后必须保证有足够信息支撑当前 Skill 的正常执行

### 2.3 分 Skill 裁剪策略

| Skill | 优先保留 | 可裁剪 |
|-------|---------|--------|
| learning-outcome | 课标、学情 | 练习册索引、教学策略 |
| assessment-design | 课标、数学本质、练习册索引 | 教学策略细节 |
| activity-design | 学情、教学策略 | 练习册答案 |
| homework | 练习册索引、题库 | 教学策略 |
| courseware | 教学设计、教材材料 | 练习册索引细节 |
| question-dispatch | 题源、答案 | 练习册索引 |
