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

### 2.8 来源标注

右下角，红色圆点前缀，灰色小字：`八年级 · 第十章 数据的收集、整理与描述`

### 2.9 页码

底部居中，`— N —` 格式。

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
| 正文段落 | `.body-text`，30px，行高 2.0 |
| 加粗 `**xxx**` | `.hw-bold` |
| 表格 | `.sketch-table`，黑线手绘风 |
| LaTeX `$...$` | MathJax 3 渲染 |
| 图片 `![...](...)` | `<img>`，居中，最大高度限制 |
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

#### 3.5.1 荧光笔关键词自动标记

脚本内置关键词库，自动为以下术语添加 `.hl` 荧光笔标记：

- **统计术语**：全面调查、抽样调查、普查、抽查、总体、个体、样本、样本容量
- **数据术语**：频数、频率、极差、组距、组数
- **图表术语**：条形统计图、折线统计图、扇形统计图、变化情况、市场占有率、占比
- **抽样方法**：简单随机抽样、代表性、广泛性

**标记规则**：
- 按关键词长度降序匹配，避免子串嵌套（如"样本容量"优先于"样本"）
- 使用负向后发断言，已标记文本不会被重复嵌套
- 长关键词优先，确保"样本容量"正确标记为整体

#### 3.5.2 红笔结论自动识别

脚本自动识别以下模式为红笔结论框：

| 模式 | 示例 |
|------|------|
| 口诀类 | "条形看数量，折线看变化，扇形看占比" |
| 公式类 | "频率 = 频数 ÷ 总数" |
| 选择类 | "怎么选？看范围、看破坏性、看精度" |
| 规律类 | "各组频率之和 = 1" |

**识别方式**：关键词匹配 + 正则模式（`^频率\s*=\s*频数`、`^条形看.*折线看.*扇形看` 等）

#### 3.5.3 蓝笔思路保守识别

脚本对蓝笔思路采取**保守策略**，仅识别明确的"思路""引导"关键词，避免误标操作步骤。蓝笔批注建议由教师手动添加。

#### 3.5.4 关键词库扩展

可在脚本顶部 `HIGHLIGHT_KEYWORDS` 列表中添加新关键词：

```python
HIGHLIGHT_KEYWORDS = [
    '全面调查', '抽样调查', '普查', '抽查',
    '总体', '个体', '样本', '样本容量',
    '频数', '频率', '极差', '组距', '组数',
    '变化情况', '市场占有率', '占比',
    '折线统计图', '扇形统计图', '条形统计图',
    '简单随机抽样', '代表性', '广泛性',
    # 添加新关键词...
]
```

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

### 3.7 页面导航

右下角浮动小圆点导航，不占顶部空间，投屏时自动隐藏：

- 位置：`position: fixed; bottom: 20px; right: 20px`
- 样式：12px 圆点，纵向排列，半透明奶油底背景
- 交互：hover 放大，active 变黑放大
- 投屏隐藏：`@media print { display: none; }`
- 超过 60vh 时可滚动

```css
.nav-dots {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 9999;
  max-height: 60vh;
  overflow-y: auto;
  padding: 8px;
  background: rgba(253, 246, 227, 0.9);
  border-radius: 20px;
  border: 1.5px solid #d4c9a8;
}
```

### 3.8 翻页笔与键盘支持

支持翻页笔和键盘翻页，覆盖主流翻页笔按键映射：

| 操作 | 按键 |
|------|------|
| 下一页 | 空格、PageDown、→、↓、Enter、单击页面 |
| 上一页 | PageUp、←、↑、Backspace、右键 |
| 第一页 | Home |
| 最后一页 | End |

**实现细节**：
- `keydown` 监听所有翻页键，`preventDefault()` 阻止默认行为
- 单击页面 = 下一页（模拟翻页笔单击）
- 右键 = 上一页（模拟翻页笔功能键）
- 点击导航圆点时不触发全局翻页
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
- 禁止页面内容溢出 1920×1080 边界
- 禁止添加动画效果（保持静态板书感）
