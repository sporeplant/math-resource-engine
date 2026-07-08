# 练习册参考答案拆解技能 检查清单

## Step01 类型确认

- [ ] 输入是否为练习册参考答案
- [ ] 是否不把答案写入 `knowledge/workbooks/`
- [ ] 是否与题库原文拆分结果保持文件名对应关系

## Step02 边界识别

- [ ] 是否识别标准课时标题
- [ ] 是否兼容裸课时标题
- [ ] 是否识别回顾与反思
- [ ] 是否识别单元测试卷和期中测试卷

## Step03 元数据

- [ ] `content_type` 是否为 `workbook_answer`
- [ ] `source_type` 是否为 `exercise_bank`
- [ ] `source_id` 是否对应题库源文件
- [ ] `answer_id` 是否对应答案文件名

## Step04 内容保真

- [ ] 答案、步骤、公式是否完整保留
- [ ] “略”“答案不唯一”等边界说明是否保留
- [ ] 没有补写、改写或自行校正答案

## Step05 验证

- [ ] 是否运行 `tools/validate-workbook-answer-split.py`
- [ ] 验证是否通过
