# 练习册逐题索引检查清单

- [ ] 已确认题库文件位于 `knowledge/workbooks/`
- [ ] 已确认答案文件位于 `knowledge/workbook-answers/`
- [ ] 题库文件和答案文件的课时编号一一对应
- [ ] 索引文件写入 `knowledge/workbook-index/`
- [ ] 每个父题均有稳定 `WB-...-Qxxx` 编号
- [ ] 每个可独立引用的小问均有稳定 `WB-...-Qxxx-Sxx` 编号
- [ ] 每个题目均包含 `source_id: workbook-*` 与 `source_type: exercise_bank`
- [ ] 每个题目均有非空 `answer_ref`
- [ ] 未改写题库原文和答案原文
- [ ] 已运行 `python tools/validate-workbook-index.py <索引文件或目录>`
