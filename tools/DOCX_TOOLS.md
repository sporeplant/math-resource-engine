# DOCX 导出工具整理说明

> 建议以后优先使用 `tools/review_docx_pipeline.py`。旧脚本暂不删除，作为底层能力或历史兼容保留。

**Skill 入口**：`skills/support/docx-export/SKILL.md`（已在 `orchestrator/skill-registry.md` 登记为 `DOCX导出skills`）

## 推荐入口

### 1. Markdown 直接导出分栏压缩 DOCX

```bash
python tools/review_docx_pipeline.py export outputs/g8-reviews/review-10_教师版解析.md
```

默认输出：

```text
outputs/g8-reviews/review-10_教师版解析_分栏压缩.docx
```

### 2. 同时生成单栏版和分栏压缩版

```bash
python tools/review_docx_pipeline.py export outputs/g8-reviews/review-10_教师版解析.md --mode both
```

输出：

```text
outputs/g8-reviews/review-10_教师版解析.docx
outputs/g8-reviews/review-10_教师版解析_分栏压缩.docx
```

### 3. 批量导出

```bash
python tools/review_docx_pipeline.py export outputs/g8-reviews/第11讲_教师版解析.md outputs/g8-reviews/第12讲_教师版解析.md outputs/g8-reviews/review-10_教师版解析.md --mode both
```

### 4. 已有 DOCX 转分栏压缩版

```bash
python tools/review_docx_pipeline.py compact outputs/g8-reviews/review-10_教师版解析.docx
```

### 5. 覆盖已有输出

默认不覆盖已有输出文件。需要覆盖时添加：

```bash
--overwrite
```

例如：

```bash
python tools/review_docx_pipeline.py export outputs/g8-reviews/review-10_教师版解析.md --mode both --overwrite
```

---

## 旧脚本定位

| 脚本 | 当前定位 | 是否推荐直接用 |
|---|---|---|
| `review_docx_pipeline.py` | 统一入口：导出单栏、分栏压缩、批量处理 | 推荐 |
| `md2docx.py` | Markdown → 单栏 DOCX，支持 Pandoc、公式、图片、表格 | 作为底层工具 |
| `compact_review_docx.py` | DOCX → 双栏压缩版，压缩段落、图片和选项 | 作为底层工具 |
| `md_to_docx.py` | 简化版 Markdown → DOCX，功能较少；已加弃用提示 | 不建议新任务使用 |
| `clean_review_docx_spacing.py` | 清理 DOCX 中多余空格/硬换行 | 特殊修复时使用 |
| `legacy/fix_docx_layout.py` | 早期硬编码修复脚本，路径固定；已归档 | 不建议使用 |
| `merge_review_docx.py` | 多个 DOCX 合并，保留图片和公式对象 | 合并场景使用 |
| `reorder_review_docx.py` | 旧复习讲义重排结构 | 特定工作流使用 |

---

## 建议后续整理方向

1. 已将 `md_to_docx.py` 加入弃用提示，避免和 `md2docx.py` 混淆。
2. 已将硬编码路径的 `fix_docx_layout.py` 移动到 `tools/legacy/`。
3. 长期可将 `md2docx.py` 与 `compact_review_docx.py` 的公共 XML 工具抽出为共享模块。
4. 对常用导出命令增加简单测试，避免脚本重构后破坏导出流程。
