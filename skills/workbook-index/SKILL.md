---
name: workbook-index
description: >
  为已拆分的练习册题库与练习册参考答案建立逐题索引。适用于用户要求把 knowledge/workbooks/ 与
  knowledge/workbook-answers/ 对齐、生成稳定 question_id、校验练习册题源可追溯性，或正式教学设计/课件流程需要
  exercise_bank 题目索引与答案映射时。
---

# 练习册逐题索引技能

## 1. Skill 定位

本 Skill 在 `skills/workbook-split/` 和 `skills/workbook-answer-split/` 之后执行，把课时题库文件、答案文件对齐为 `knowledge/workbook-index/` 下的逐题索引。

索引只记录题源位置和答案位置，不改写题目、不补写答案、不判断答案正误。

## 2. 输入

| 输入 | 路径 |
|------|------|
| 练习册题库 | `knowledge/workbooks/workbook-*.md` |
| 练习册答案 | `knowledge/workbook-answers/workbook-answer-*.md` |

题库文件和答案文件必须一一对应，例如：

- `knowledge/workbooks/workbook-12.1-1.md`
- `knowledge/workbook-answers/workbook-answer-12.1-1.md`

缺少任一文件时不得生成索引。

## 3. 输出

索引写入 `knowledge/workbook-index/`，命名规则：

| 源文件 | 索引文件 |
|--------|----------|
| `workbook-12.1-1.md` | `workbook-index-12.1-1.yaml` |
| `workbook-ch12-review.md` | `workbook-index-ch12-review.yaml` |

每个索引必须包含：

```yaml
---
content_type: workbook_index
source_type: exercise_bank
source_id: workbook-12.1-1
answer_id: workbook-answer-12.1-1
index_id: workbook-index-12.1-1
question_count: 6
subquestion_count: 17
---
questions:
  - question_id: WB-12.1-1-Q001
    source_id: workbook-12.1-1
    source_type: exercise_bank
    question_no: "1"
    section: "夯实基础"
    line_start: 13
    line_end: 36
    answer_ref:
      answer_id: workbook-answer-12.1-1
      answer_line_start: 10
      answer_line_end: 10
```

有小问时，保留父题并登记子题：

```yaml
subquestions:
  - question_id: WB-12.1-1-Q001-S01
    parent_question_id: WB-12.1-1-Q001
    subquestion_no: "1"
```

正式资源可引用父题 `WB-12.1-1-Q001`，也可引用具体小问 `WB-12.1-1-Q001-S01`。

## 4. 调用方式

```bash
python tools/index-workbook.py knowledge/workbooks --chapter 12 --overwrite
python tools/validate-workbook-index.py knowledge/workbook-index
```

## 5. 硬性规则

- 禁止为缺少答案文件的题库生成索引。
- 禁止出现 `answer_ref: null`。
- 禁止修改题库原文和答案原文。
- 禁止把索引写入 `knowledge/workbooks/` 或 `knowledge/workbook-answers/`。
- 禁止使用非 `WB-` 前缀的练习册 `question_id`。

## 6. 正式工作流使用规则

`/lesson-collab` 和 `/courseware-collab` 使用练习册题目时，必须先确认：

1. 对应 `knowledge/workbooks/workbook-*.md` 存在。
2. 对应 `knowledge/workbook-answers/workbook-answer-*.md` 存在。
3. 对应 `knowledge/workbook-index/workbook-index-*.yaml` 存在并通过 `tools/validate-workbook-index.py`。
4. 输出中的 `source_id: workbook-*`、`source_type: exercise_bank`、`question_id` 或 `question_ids` 能在索引中找到。

任一项缺失或校验失败时，正式教学设计、课件和调度稿工作流必须终止，不得降级为文件级引用。
