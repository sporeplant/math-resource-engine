---
name: html-to-seewo
description: 将 HTML 课件转为希沃白板可导入包（lesson.json + 逐页 PNG 截图）
---

# html-to-seewo — HTML 课件转希沃白板导入包

## 1. 定位

将任意符合课件规范的 HTML 文件（含 `.slide` 元素的 1920×1080 投屏页面）转换为希沃白板5 可导入的课件包。

**输入**：HTML 课件文件路径
**输出**：在 HTML 同级目录生成 `lesson.json` + `assets/slide_01.png` ~ `slide_N.png`

**可独立触发**：用户可以说"把这个 HTML 转成希沃课件"、"导出希沃格式"、"生成希沃导入包"等，不依赖 `md2htmlyishu` 上游。

## 2. 使用方式

### 2.1 脚本转换

```bash
python tools/html_to_seewo.py "{HTML 文件路径}"
```

脚本自动完成：
- 启动 Playwright（Chromium）加载 HTML（设 viewport 为 1920×1080）
- 等待 MathJax 渲染完成后，逐页截取每张 `.slide` 元素
- 图片存入 `assets/` 子目录
- 生成 MrePlugin 格式的 `lesson.json`

### 2.2 前置条件

- 需要安装 Playwright：`pip install playwright && playwright install chromium`
- HTML 必须包含 `.slide` 元素（`md2htmlyishu` 模板自动满足）
- HTML 同级目录可写

## 3. 输出结构

```
{HTML同级目录}/
├── lesson.json           — MrePlugin 课件描述文件
└── assets/
    ├── slide_01.png      — 第1页截图（1920×1080）
    ├── slide_02.png      — 第2页截图
    └── ...
```

### 3.1 lesson.json 格式

遵循 `support/easinote/MRE-Plugin/` 的 MrePlugin 规范，每页引用一张对应 PNG 图片。

### 3.2 截图参数

| 项目 | 值 |
|------|-----|
| 宽度 | 1920px |
| 高度 | 1080px |
| 格式 | PNG |
| 方式 | `element.screenshot()` 截取 `.slide` 元素 |

## 4. 检查清单

生成后逐项检查：

- [ ] `lesson.json` 文件存在且为合法 JSON
- [ ] `assets/` 目录存在
- [ ] `assets/slide_01.png` ~ `slide_N.png` 数量与 HTML 中 `.slide` 数量一致
- [ ] 每张截图尺寸为 1920×1080（允许 ±1px 渲染偏差）
- [ ] JSON 中每页引用路径正确指向 `assets/slide_*.png`

## 5. 禁止事项

- 禁止跳过 Playwright 截图环节，直接用手工截图代替
- 禁止在 viewport 未设为 1920×1080 时截图（会导致 `fitSlides()` 缩小页面）
- 禁止截图前不等待 MathJax 渲染（会导致公式显示为 `$` 源码）
- 禁止修改 `lesson.json` 的输出路径，必须与 HTML 同级

## 6. 后续引导

生成后告知用户导入方式：

> 📦 希沃导入包已生成：
> - `{目录}/lesson.json`
> - `{目录}/assets/slide_01.png` ~ `slide_N.png`
>
> 导入方式：希沃白板5 → 打开或新建课件 → 右键空白页 → 插件菜单 → MRE导入 → 选择 `lesson.json`
