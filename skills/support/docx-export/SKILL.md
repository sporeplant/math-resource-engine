---
name: docx-export
description: >
  将复习讲义、教师版解析等 Markdown 文件导出为 DOCX。
  支持单栏完整排版和 A4 双栏紧凑打印两种模式。
  Use when asked to 导出DOCX、转成Word、生成打印版、分栏压缩。
skill_file: skills/support/docx-export/SKILL.md
checklist_file: skills/support/docx-export/checklist.md
tool: tools/review_docx_pipeline.py
status: active
version: v1.0
---

# DOCX 导出 Skill

## 1. 定位

本 Skill 负责将 Markdown 格式的复习讲义、教师版解析或其他教学文档导出为可打印的 Word DOCX 文件。

不涉及内容生成，仅负责**格式转换与排版**。

---

## 2. 调用入口

统一使用：

```bash
python tools/review_docx_pipeline.py <子命令> [选项]
```

不要直接调用 `md2docx.py`、`compact_review_docx.py`、`md_to_docx.py` 等底层脚本。

---

## 3. 输出模式

| 模式 | 命令参数 | 用途 |
|---|---|---|
| 单栏完整版 | `--mode single` | 普通 Word 查看、存档 |
| 双栏紧凑版（默认） | `--mode compact` | A4 双栏打印讲义 |
| 两种都生成 | `--mode both` | 同时生成两份 |

---

## 4. 标准命令

### 4.1 单个文件导出（默认：双栏压缩）

```bash
python tools/review_docx_pipeline.py export outputs/reviews/review-10_教师版解析.md
```

输出：

```text
outputs/reviews/review-10_教师版解析_分栏压缩.docx
```

### 4.2 同时生成单栏和双栏版

```bash
python tools/review_docx_pipeline.py export outputs/reviews/review-10_教师版解析.md --mode both
```

### 4.3 批量导出

```bash
python tools/review_docx_pipeline.py export \
  outputs/reviews/第11讲_教师版解析.md \
  outputs/reviews/第12讲_教师版解析.md \
  outputs/reviews/review-10_教师版解析.md \
  --mode both --overwrite
```

### 4.4 已有 DOCX 转双栏压缩

```bash
python tools/review_docx_pipeline.py compact outputs/reviews/review-10_教师版解析.docx
```

---

## 5. 输出规范

| 字段 | 说明 |
|---|---|
| 存放目录 | 与源文件同目录 |
| 单栏文件名 | `{原文件名}.docx` |
| 双栏压缩文件名 | `{原文件名}_分栏压缩.docx` |
| 页面规格 | A4 |
| 页边距 | 单栏：2cm；双栏：1.27cm（0.5in） |
| 分栏数 | 单栏：1；双栏：2，等宽，带分隔线 |

---

## 6. 依赖

| 依赖项 | 说明 |
|---|---|
| `tools/review_docx_pipeline.py` | 统一调用入口（本 Skill 的执行脚本） |
| `tools/md2docx.py` | 底层：Markdown → 单栏 DOCX（含公式/图片/表格） |
| `tools/compact_review_docx.py` | 底层：单栏 DOCX → 双栏压缩 DOCX |
| Pandoc | Markdown 解析和 DOCX 初稿生成 |
| python-docx | 段落样式、字体、图片处理 |
| matplotlib | 表格渲染为图片 |
| lxml | DOCX XML 结构操作 |

---

## 7. 异常处理

| 情况 | 处理方式 |
|---|---|
| 输入文件不存在 | 报错中止，提示路径 |
| 输出文件已存在 | 默认跳过，需加 `--overwrite` 覆盖 |
| Pandoc 未安装 | `md2docx.py` 会自动在常见路径搜索，未找到时报错提示 |
| 公式无法渲染 | 降级为 Unicode 近似表示，不中断转换 |
| 图片路径不存在 | 跳过图片，继续导出其他内容 |

---

## 8. 不适用场景

- 生成教学设计、课件、评价任务等内容 → 使用对应内容生成 Skill
- 教材问题解答、复习讲义内容整理 → 使用内容 Skill 先生成 Markdown，再调用本 Skill 导出
- 合并多个 DOCX 文件 → 使用 `tools/merge_review_docx.py`
