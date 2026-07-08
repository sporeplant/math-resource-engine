# 练习册参考答案拆解技能

## 1. Skill 定位

将 MinerU 转换的整本或整章练习册参考答案 Markdown 按课时、章节回顾和测试卷拆分为独立答案文件。

本 Skill 只处理练习册参考答案，不处理练习册题库原文。题库原文拆解使用 `skills/workbook-split/SKILL.md`。

## 2. 输出要求

拆分结果写入 `knowledge/workbook-answers/`：

| 文件类型 | 命名规则 | 示例 |
|----------|----------|------|
| 课时答案 | `workbook-answer-{章节}.{小节}-{课时号}.md` | `workbook-answer-12.1-1.md` |
| 单课时答案 | `workbook-answer-{章节}.{小节}.md` | `workbook-answer-12.4.md` |
| 回顾与反思答案 | `workbook-answer-ch{章号}-review.md` | `workbook-answer-ch12-review.md` |
| 单元测试卷答案 | `workbook-answer-ch{章号}-unit-test.md` | `workbook-answer-ch12-unit-test.md` |
| 期中测试卷答案 | `workbook-answer-midterm.md` | `workbook-answer-midterm.md` |

每个文件应包含 YAML front matter：

```yaml
---
content_type: workbook_answer
source_type: exercise_bank
source_id: workbook-12.1-1
answer_id: workbook-answer-12.1-1
---
```

## 3. 处理要求

- 识别 `## 12.1 分式(一)` 等标准课时标题
- 兼容 OCR 丢失标题符号的裸标题，如 `12.3 分式的加减(一)`
- 识别 `回顾与反思`
- 识别 `单元测试卷`、`期中测试卷`
- 保留答案原文，不改写数学结论、步骤和开放题答案边界
- 图片迁移到 `knowledge/images/`，Markdown 引用改为 CDN 路径

## 4. 禁止事项

- 禁止把参考答案混入 `knowledge/workbooks/` 题库原文
- 禁止把答案文件标记为教材答案或出版社标准答案以外的来源
- 禁止改写答案、补写答案或修正数学过程，除非用户明确要求校对
- 禁止遗漏开放题中的“答案不唯一”“略”等边界说明

## 5. 调用方式

```bash
python tools/split_workbook_answers.py <MinerU答案Markdown> [--outdir knowledge/workbook-answers] [-y]
```

## 6. 自检流程

- [ ] 是否识别全部课时答案
- [ ] 是否识别章节回顾答案
- [ ] 是否识别测试卷答案
- [ ] 输出文件是否带 `content_type: workbook_answer`
- [ ] `source_id` 是否能对应题库文件名
- [ ] 图片路径是否为 CDN
- [ ] 是否运行 `python tools/validate-workbook-answer-split.py <输出目录或文件>`
