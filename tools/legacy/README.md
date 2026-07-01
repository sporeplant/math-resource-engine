# Legacy DOCX tools

本目录存放历史脚本或硬编码脚本。它们保留用于追溯和特殊修复，不建议新任务直接调用。

## 文件

| 文件 | 说明 | 推荐替代 |
|---|---|---|
| `fix_docx_layout.py` | 早期 DOCX 布局修复脚本，内部写死了 `outputs/reviews/docx-90d59119.docx` | `tools/review_docx_pipeline.py compact ...` 或 `tools/compact_review_docx.py` |

## 当前推荐入口

```bash
python tools/review_docx_pipeline.py export path/to/file.md --mode compact
python tools/review_docx_pipeline.py compact path/to/file.docx
```
