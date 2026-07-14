# DOCX 导出 Skill 检查清单

## 调用前

- [ ] 确认源 Markdown 文件路径正确，文件存在
- [ ] 确认 Markdown 文件包含 YAML front matter（`content_type` 等字段），若无则跳过不报错
- [ ] 确认图片路径使用相对路径（`images/文件名`），不使用绝对路径或 `knowledge/` 路径
- [ ] 明确所需输出模式：`single`（单栏）、`compact`（双栏压缩）、`both`（两者）

## 调用命令

- [ ] 使用 `tools/review_docx_pipeline.py`，不直接调用底层脚本
- [ ] 若需覆盖已有文件，已加 `--overwrite` 参数
- [ ] 批量导出时文件列表已逐一确认，没有路径拼写错误

## 输出核验

- [ ] 单栏版文件名为 `{原文件名}.docx`
- [ ] 双栏压缩版文件名为 `{原文件名}_分栏压缩.docx`
- [ ] 两个文件均存放在与源 Markdown 相同的目录
- [ ] DOCX 文件可正常打开，内容无乱码
- [ ] 数学公式已渲染（行内公式为 Unicode 或 Word 公式对象，不显示为 `$...$` 原始文本）
- [ ] 图片已嵌入，宽度不超过单栏可用宽度
- [ ] 表格已渲染（以图片形式嵌入，标题行有底色区分）
- [ ] 压缩版已确认为双栏布局，页边距紧凑

## 常见问题确认

- [ ] 若脚本报"Pandoc 未找到"，确认 Pandoc 已安装并在 PATH 中，或在常见路径下（`%LOCALAPPDATA%\Pandoc\pandoc.exe`）
- [ ] 若公式显示异常，检查 Markdown 中公式是否使用 `$...$` 或 `$$...$$` 格式
- [ ] 若图片未嵌入，检查图片文件是否存在于 `outputs/reviews/images/` 等同级 `images/` 目录
