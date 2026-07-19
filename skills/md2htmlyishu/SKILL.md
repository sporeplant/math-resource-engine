---
name: md2htmlyishu
description: 将课件 Markdown 转换为一数风格 HTML 投屏页面（1920×1080，手写板书风）
---

# md2htmlyishu — 课件 Markdown 转一数风格 HTML

## 1. 定位

将课件 Markdown 文件转换为可在浏览器中直接播放的 HTML 投屏页面，复刻一数视频的"手写板书"风格。

**输入**：课件 MD 文件（`---` 分页，LaTeX 公式，图片引用）
**输出**：单个 HTML 文件，与源文件同目录，每页 1920×1080，自动缩放适配屏幕

## 2. 风格规范

### 2.1 整体基调

不是设计出来的 PPT，是老师拿笔在平板上写板书的感觉。**静态底版 + 动态手写批注**。零装饰，无卡片、无边框、无阴影、无圆角。

### 2.2 视觉参数

| 项目 | 值 | 说明 |
|------|-----|------|
| 背景色 | `#FDF6E3` | 奶油黄，像纸张 |
| 正文字色 | `#1a1a2e` | 深蓝黑 |
| 红笔 | `#C62828` | 只用于结论、关键答案 |
| 蓝笔 | `#1565C0` | 用于推导过程、思路引导 |
| 荧光黄 | `#FFEB3B` 半透明 | 标题底色、关键词标记 |
| 字体 | `'Noto Serif SC', 'Kaiti SC', 'KaiTi', 'STKaiti', serif` | 楷体/手写体 |
| 页面尺寸 | 1920×1080 | 标准 16:9 课件投影 |
| 缩放 | `transform: scale()` | 自动适配屏幕 |

### 2.3 标题

- 字号 64px，粗体 900，楷体
- 底部黄色荧光笔涂抹效果（`linear-gradient` 实现，轻微歪斜 `rotate(-0.5deg)`）
- 不用 emoji 装饰标题

### 2.4 荧光笔标记

关键词用荧光黄半透明底色标记：

```css
background: linear-gradient(180deg, transparent 60%, #FFEB3B 60%, #FFEB3B 90%, transparent 90%);
```

### 2.5 手写体层级

| 层级 | 字体 | 颜色 | 用途 |
|------|------|------|------|
| 标题 | 楷体 900 | `#1a1a2e` | 页面标题 |
| 正文 | 楷体 400 | `#1a1a2e` | 题目、叙述 |
| 蓝笔批注 | 楷体 400 | `#1565C0` | 推导过程、思路 |
| 红笔结论 | 楷体 700 | `#C62828` | 最终结论、口诀 |

### 2.6 红笔结论框

```css
border: 3px solid #C62828;
border-radius: 4px;
padding: 20px 36px;
```

就是红笔画了个框，不是设计出来的卡片。

### 2.7 表格

黑线手绘风格：`border: 2.5px solid #1a1a2e`，表头加粗，无斑马纹。

### 2.8 行距

| 内容类型 | 行距 | 说明 |
|---------|------|------|
| 普通正文 | 2.0 倍 | 题目、叙述、列表 |
| 行间 LaTeX 公式 | 2.4 倍 | 独立成行的公式，上下留白充分 |

### 2.9 来源标注

右下角，红色圆点前缀，灰色小字：`八年级 · 第十章 数据的收集、整理与描述`

### 2.10 页码

底部居中，`— N —` 格式。

### 2.11 封面

- 背景：从 `knowledge/images/bg/` 目录中**随机选取一张油画**
- 引用路径：`./images/bg/{随机文件名}.jpg`（相对路径，不依赖 CDN）
- 封面文字：**仅保留课题与课时**（即 `###` 标题行），不添加副标题、作者、日期等其他信息
- 移除封面图片版权标注（`.cover-credit`）

### 2.12 教学目标页

- 布局：**上下左右四向居中**
- 实现：`.slide.objective-page { display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; }`
- **正文序号必须左对齐**：页面内的列表项、编号段落保持 `text-align: left`，避免序号错位

### 2.13 多图与多题排列

- 默认**横向排列**：使用 flex 布局，图片/题目平分页面宽度
- **溢出自动纵向**：通过 `flex-wrap: wrap` + `flex: 1 1 45%` 实现，当横向空间不足时自动换行为纵向排列
- 不再使用固定宽度的 `.img-col`，改用自适应的 `.img-item`

## 3. 转换规则

### 3.1 分页

Markdown 中 `---` 水平线 = 一个 HTML `.slide` 页面。

### 3.2 标题映射

MD 标题 → HTML 标题：

| MD 写法 | HTML 处理 |
|---------|----------|
| `### 📐 xxx` | `.title`，荧光笔效果 |
| `### 🎯 xxx` | `.title`，荧光笔效果 |
| `### 📖 xxx` | `.title`，荧光笔效果 |
| `### ✏️ xxx` | `.title`，荧光笔效果 |
| `### 📝 xxx` | `.title`，荧光笔效果 |
| `### 💡 xxx` | `.title`，荧光笔效果 |

**emoji 保留在标题文字中**，因为源 MD 已有 emoji 规范。

### 3.3 内容映射

| MD 元素 | HTML 处理 |
|---------|----------|
| 正文段落 | `.body-text`，40px，行高 2.0 |
| LaTeX 公式 | MathJax 44px，独立公式增加上下留白 |
| 公式推导步骤 | `.formula-line`，段落间距 36px |
| 表格文字 | `.sketch-table`，36px |
| 加粗 `**xxx**` | `.hw-bold` |
| 表格 | `.sketch-table`，黑线手绘风 |
| LaTeX `$...$` | MathJax 3 渲染 |
| 图片 `![...](...)` | 单图居中；同页多图默认横排，空间不足自动换行 |
| 多个编号数学小题 | 默认横排 `.question-row`，空间不足自动换行；末两页作业清单保持纵向 |
| 多个完整解答块 | 默认横排 `.solution-row`；实测发生溢出时自动分页，禁止纵排回退 |
| 列表 | 保留缩进，楷体 |

### 3.4 公式

MathJax 3 配置：

```html
<script>
  MathJax = {
    tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] },
    startup: { typeset: true }
  };
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
```

### 3.5 自动标记能力（脚本实现）

脚本 `tools/md2htmlyishu.py` 已实现以下自动标记：

#### 3.5.1 荧光笔：关键条件与易错点

荧光笔 `.hl` **只用于关键条件和易错点**，不用于学习目标、法则、定义或普通数学术语。

- **关键条件**：适用范围、取值限制、必要前提，如“分母不为 0”。
- **易错点**：容易漏写、误用或颠倒的操作，如“约去分子分母的公因式”。
- **数量控制**：每课通常 3–6 个，且仅出现在其首次建立或提醒的指定页面。

#### 3.5.2 红笔结论：法则、定义与策略归纳

红笔结论框 `.conclusion` **只用于法则、定义和策略归纳**：

| 类型 | 示例 |
|------|------|
| 法则 | “分式与分式相乘，用分子的积作为积的分子，分母的积作为积的分母。” |
| 定义 | “最简分式：分子与分母没有公因式的分式。” |
| 策略归纳 | “先乘再约”“先分解再约” |

识别以 YAML 中的精确短语 `red_conclusion_phrases` 为主，`red_conclusion_patterns` 仅用于兼容补充。

#### 3.5.3 蓝笔思路保守识别

脚本对蓝笔思路采取**保守策略**，仅识别明确的"思路""引导"关键词，避免误标操作步骤。蓝笔批注建议由教师手动添加。

#### 3.5.4 关键词库配置（YAML）

**关键词不再硬编码在 Python 脚本中**，改为从 YAML 配置文件动态加载。

配置加载优先级：

1. **MD 同目录配置**：`{课件文件名}.yaml`（如 `13讲_统计调查与直方图复习_课件.yaml`）
2. **configs/ 目录匹配**：根据 MD 内容中的章节信息自动匹配 `configs/ch{章节}-*.yaml`
3. **默认配置**：`configs/default.yaml`

配置示例（`configs/ch13-统计调查与直方图.yaml`）：

```yaml
course:
  name: "统计调查与直方图复习"
  chapter: "第十章 数据的收集、整理与描述"
  section: "第13讲"

# 全课通用的关键条件或易错点；通常为空，优先按页面精确配置。
highlight_phrases: []

# 全课通用的法则、定义或策略归纳；通常为空，优先按页面精确配置。
red_conclusion_phrases: []

page_highlights:
  - title_contains: "分式乘法法则"
    highlight_phrases:
      - "B \\neq 0"
      - "D \\neq 0"
    red_conclusion_phrases:
      - "分式与分式相乘，用分子的积作为积的分子，分母的积作为积的分母。"

red_conclusion_patterns: []

blue_hint_keywords:
  - 思路
  - 引导

blue_hint_patterns:
  - "^[①②③④⑤]\\s*[^，。；]*[=→]"
```

#### 3.5.5 agent 自动生成配置

当 agent 处理新课程课件时，应自动执行以下流程：

1. **读取课件 MD**，定位关键条件、易错点、法则、定义和策略归纳所在页面。
2. **生成 YAML 配置**到 `skills/md2htmlyishu/configs/{章节}-{课题}.yaml`，使用精确短语和页面标题限制。
3. **教师审核微调**（可选），确认每项视觉强调是否符合本课教学重点。
4. **运行转换**，脚本自动加载对应配置。

agent 生成配置的原则：
- **荧光笔 `highlight_phrases`**：仅关键条件和易错点，每课通常 3–6 个；不列基础术语、学习目标、法则或定义。
- **红笔 `red_conclusion_phrases`**：仅法则、定义、策略归纳；优先精确匹配整行文本。
- **页面限制 `page_highlights`**：用 `title_contains` 限定短语出现的页面，避免全文重复标记。
- **蓝笔思路**：解题思路、推导提示（保守策略，仅标记明确提示处）。

### 3.6 页面缩放

```javascript
function fitSlides() {
  const scale = Math.min(window.innerWidth / 1920, 1);
  slides.forEach(s => {
    s.style.transform = `scale(${scale})`;
    s.style.marginBottom = `${1080 * (scale - 1)}px`;
  });
}
window.addEventListener('resize', fitSlides);
fitSlides();
```

### 3.7 翻页笔与键盘支持

支持翻页笔和键盘翻页，覆盖主流翻页笔按键映射：

| 操作 | 按键 |
|------|------|
| 下一页 | 空格、PageDown、→、↓、Enter、单击页面 |
| 上一页 | PageUp、←、↑、Backspace、右键 |
| 第一页 | Home |
| 最后一页 | End |

**说明**：已移除左下角全屏按钮和右下角导航圆点，仅保留键盘/翻页笔/单击/右键翻页。

**实现细节**：
- `keydown` 监听所有翻页键，`preventDefault()` 阻止默认行为
- 单击页面 = 下一页（模拟翻页笔单击）
- 右键 = 上一页（模拟翻页笔功能键）
- 有选中文字时不翻页（避免复制误触）

```javascript
let currentSlide = 0;
const totalSlides = document.querySelectorAll('.slide').length;

function goToSlide(i) { /* 边界检查 + show(i) */ }
function nextSlide() { goToSlide(currentSlide + 1); }
function prevSlide() { goToSlide(currentSlide - 1); }

document.addEventListener('keydown', function(e) {
  if (e.key === ' ' || e.key === 'PageDown' || e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'Enter') {
    e.preventDefault(); nextSlide();
  }
  if (e.key === 'PageUp' || e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'Backspace') {
    e.preventDefault(); prevSlide();
  }
  if (e.key === 'Home') { e.preventDefault(); goToSlide(0); }
  if (e.key === 'End') { e.preventDefault(); goToSlide(totalSlides - 1); }
});
```

## 4. 使用方式

### 4.1 脚本转换（推荐）

```bash
python tools/md2htmlyishu.py "path/to/课件.md"
```

输出：与源文件同目录的 `.html` 文件，38 页秒出。

**脚本自动完成**：分页、标题荧光笔、正文荧光笔关键词标记、表格、图片 CDN、LaTeX、红笔结论识别、页码。

### 4.2 手动修正（可选）

脚本输出后，教师可手动添加：

- 蓝笔思路引导（`<span class="hw-blue">`）
- 额外的红笔结论框
- 页面布局微调

### 4.3 输出文件

- 文件名：`{源文件名}.html`（与源 MD 同目录）
- 单文件，内嵌全部 CSS + JS，无需外部依赖（除 MathJax CDN 和 Google Fonts）
- 支持浏览器直接打开，支持打印（每页一页）

## 5. 检查清单

生成后逐项检查：

### 基础项
- [ ] 每页是 1920×1080，无溢出
- [ ] LaTeX 公式正确渲染（无 `$` 源码残留）
- [ ] 表格线清晰可见
- [ ] 图片正常显示
- [ ] 页面缩放正常
- [ ] 来源标注和页码位置正确

### 风格项
- [ ] 荧光笔标记正确显示（关键词有黄色半透明底）
- [ ] 红笔结论框格式正确（红色边框，非卡片）
- [ ] 无卡片、圆角、阴影等装饰元素
- [ ] 整体感觉是"手写板书"，不是"PPT 模板"

### 自动标记项（脚本输出后检查）
- [ ] 荧光笔关键词无嵌套标记（如"样本容量"不被拆成"样本"+"容量"）
- [ ] 红笔结论仅出现在真正的结论/口诀行，不误标正文步骤
- [ ] 蓝笔思路仅出现在"思路""引导"等明确提示处，不过度标记

## 6. 禁止事项

- 禁止添加卡片、圆角、阴影、渐变背景等设计元素
- 禁止使用 emoji 装饰正文（标题中已有的除外）
- 禁止把 LaTeX 源码直接显示（必须 MathJax 渲染）
- 禁止向 `$...$` 或 `$$...$$` 数学区间内部插入 HTML 标签
- 禁止多题、多图页面缺少横向 flex 容器；横向布局必须配置 `flex-wrap: wrap` 防溢出
- 禁止多个完整解答块无理由纵排；发生实质性溢出时必须分页，禁止改为纵排
- 禁止页面内容溢出 1920×1080 边界
- 禁止添加动画效果（保持静态板书感）
- 禁止在封面添加除课题/课时以外的任何文字（如副标题、作者、日期、版权标注）
- 禁止恢复左下角全屏按钮和右下角导航圆点

## 7. 后续步骤：导入希沃白板

HTML 生成完成后的行为取决于调用来源：

| 调用来源 | 行为 |
|----------|------|
| **希沃课件主路径**（用户要求"生成希沃课件"等） | **自动继续**执行 §7.2，不询问 |
| **仅 HTML**（用户仅要求"生成一数风格 HTML"） | **必须询问**用户是否需要继续（§7.1） |

### 7.1 询问（仅 HTML 路径）

```
✅ HTML 课件已生成：`{路径}.html`

是否继续生成希沃白板导入包？
这将自动完成：
  - 逐页高清截图（assets/slide_01.png ~ slide_N.png）
  - MrePlugin lesson.json

确认后可在希沃白板5 中通过 MrePlugin 一键导入。
```

### 7.2 执行（主路径自动 / 仅 HTML 路径用户确认后）

```bash
python tools/html_to_seewo.py "{HTML 文件路径}"
```

该脚本一步完成截图 + lesson.json 生成，输出在 HTML 同级目录：
- `lesson.json` — MrePlugin 课件描述文件
- `assets/slide_01.png` ~ `slide_N.png` — 逐页截图

底层通过 Playwright（Chromium）精确截取每张 `.slide` 元素。

### 7.3 输出后告知导入方式

> 📦 希沃导入包已生成：
> - `{目录}/lesson.json`
> - `{目录}/assets/slide_01.png` ~ `slide_N.png`
>
> 导入方式：希沃白板5 → 打开或新建课件 → 右键空白页 → 插件菜单 → MRE导入 → 选择 `lesson.json`
