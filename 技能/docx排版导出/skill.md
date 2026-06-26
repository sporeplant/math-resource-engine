# DOCX 排版导出技能

将 Markdown 教学讲义导出为 DOCX，支持 LaTeX 公式渲染为 Word 原生公式。分栏等复习讲义专用格式由 `compact_review_docx.py` 后处理完成。

---

## 一、适用场景

- 任何含 `$...$` 行内 LaTeX 公式的 Markdown 讲义需要导出为 DOCX。
- 复习讲义（`复习课讲义整理` 技能产物）的排版输出（配合 `compact_review_docx.py` 后处理）。
- 需要 A4 单栏 + 章节分隔线 + 表格渲染的场景。

---

## 二、输入与输出

**输入**：Markdown 讲义文件路径。
**输出**：单栏 DOCX 文件路径（建议与 md 同目录、同主名）。

---

## 三、核心规则

### 3.1 页面设置

| 项 | 值 |
|----|-----|
| 纸张 | A4（21 × 29.7 cm） |
| 上下左右边距 | 2 cm |
| 默认字体 | 仿宋 / 四号（14pt） |
| 主体内容 | 单栏 |
| 对齐 | 全部左对齐 |
| 颜色 | 全部黑色 |

### 3.2 字体与字号规范

| 元素 | 中文字体 | 英文/数字字体 | 字号 |
|------|----------|---------------|------|
| 一级标题（`#`） | 黑体 | Times New Roman | 小二（18pt） |
| 二级标题（`##`） | 方正小标宋简体 | Times New Roman | 三号（16pt） |
| 三级及以下标题 | 仿宋 | Times New Roman | 四号（14pt） |
| 正文 | 仿宋 | Times New Roman | 四号（14pt） |
| 表格 | 仿宋 | Times New Roman | 小四（12pt） |
| 英文/数字 | — | Times New Roman（**字母倾斜**） | — |

字体通过 `w:eastAsia`（中文）+ `w:ascii` + `w:hAnsi`（西文）双属性同时设置。

### 3.3 LaTeX 渲染策略

**方案：用 Unicode + Word 原生上下标**（不依赖 MathML/OMath）

| LaTeX | Word 渲染 |
|-------|----------|
| `^x` / `^{x}` | 上标（`w:vertAlign=superscript`） |
| `_x` / `_{x}` | 下标（`w:vertAlign=subscript`） |
| `\frac{a}{b}` | `(a)/(b)` |
| `\sqrt{x}` | `√(x)` |
| `\prime` | `′` |
| `\circ` | `°` |
| `\triangle` | `△` |
| `\angle` | `∠` |
| `\pi \alpha \beta` | `π α β` |
| `\le \ge \ne` | `≤ ≥ ≠` |
| `\pm \times \div` | `± × ÷` |
| `\to \Rightarrow` | `→ ⇒` |

### 3.4 内容块识别

| 块类型 | 识别特征 | 渲染方式 |
|-------|---------|---------|
| 一级标题 | `# ` 开头 | 黑体小二 + 左对齐 |
| 二级标题 | `## ` 开头 | 方正小标宋简体三号 + 左对齐 + 上下分隔线 |
| 表格 | `|...|` 开头 | 渲染为图片嵌入 |
| 图片 | `![](images/...)` 开头 | 左对齐 + 宽度 8cm |
| 选择题选项 | `^[A-D]．` 开头 | 自动重组为同行或双行排列 |
| 公式段落 | 含 `$...$` | 拆分文本与公式分别渲染 |
| 普通段落 | 其余 | 仿宋四号 + 左对齐 |

---

## 四、流程

1. **环境检查**：`python-docx`、Pandoc 是否可用。
2. **预处理**：YAML 元信息剥离、表格渲染为图片。
3. **Pandoc 转换**：Markdown → DOCX（含 OMML 公式）。
4. **排版调整**：选项重组、字体字号设置、图片宽度调整。
5. **保存**：写入单栏 DOCX 文件。

---

## 五、复习讲义专用后处理

如需复习讲义双栏打印格式，在上述流程完成后运行：

```bash
python tools/compact_review_docx.py {输入}.docx --output {输出}.docx
```

该工具负责：
- 双栏布局 + 分隔线
- 段落间距压缩
- 大图缩放
- 装饰性红色图片删除
- 文字颜色统一改黑
- 竖排选项合并为同行

---

## 六、工具脚本位置

| 用途 | 脚本位置 | 调用建议 |
|------|----------|----------|
| MD→DOCX 转换 | `tools/md2docx.py` | 通用 MD→DOCX 转换；`process(input_path, output_path)` |
| DOCX 命令行入口（轻量） | `tools/md_to_docx.py` | 轻量 MD→DOCX（纯 XML，无 Pandoc 依赖） |
| 复习讲义双栏压缩 | `tools/compact_review_docx.py` | 复习讲义专用后处理 |
| 复习讲义专用验证 | `技能/复习课讲义整理/validate_review_lesson.py` | 导出前运行，确认 Markdown 结构、题量、图片和对比表合规 |
| 通用输出验证 | `tools/validate_output.py` | 导出前运行，确认全系统硬规则合规 |

推荐流程（复习讲义）：

```bash
# 1. 验证
python 技能/复习课讲义整理/validate_review_lesson.py 输出/八下复习讲义/{文件名}.md
python tools/validate_output.py 输出/八下复习讲义/{文件名}.md

# 2. 通用 MD→DOCX（单栏）
python -c "import sys; sys.path.insert(0, 'tools'); from md2docx import process; process('输出/八下复习讲义/{文件名}.md', '输出/八下复习讲义/{文件名}.docx')"

# 3. 复习专用双栏压缩
python tools/compact_review_docx.py 输出/八下复习讲义/{文件名}.docx --output 输出/八下复习讲义/{文件名}.docx
```

---

## 七、禁止事项

- 禁止使用 MathML→OMath 复杂转换（兼容性差）。
- 禁止把图片放到表格单元格内。
- 禁止保留 LaTeX 原始字符串（必须转换或替换）。
- 禁止在通用 MD→DOCX 阶段做双栏处理（由 `compact_review_docx.py` 统一负责）。

---

## 八、可扩展点

- 字号自适应：根据主体内容长度调整基础字号。
- 表格列宽自适应：根据列内容动态设置列宽。
- 自定义分隔线样式：双线、点线等。
- 多级标题支持：扩展 `##` 以外的其他级别。