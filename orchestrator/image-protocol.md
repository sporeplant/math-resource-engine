# 图片引用协议

本协议是图片路径的orchestrator规则。详细 Skill 规则见 `skills/images/SKILL.md`。

---

## 1. 唯一原则

正式 outputs Markdown 默认引用 `knowledge/images/` 对应的 CDN URL，不在 `outputs/` 下维护长期公共图片池。knowledge 源文件可继续使用自身约定的相对图片目录。

课件标准写法：

```markdown
![图注](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/xxx.jpg)
```

---

## 2. 目录对应关系

| Markdown 文件位置 | 图片目录 | 引用路径 |
|-------------------|----------|----------|
| `knowledge/textbooks/*.md` | `knowledge/textbooks/images/` | `./images/文件名` |
| `knowledge/workbooks/*.md` | `knowledge/workbooks/images/` | `./images/文件名` |
| `knowledge/workbook-answers/*.md` | `knowledge/images/` 的 CDN URL | `![图注](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/文件名)` |
| `outputs/lessons/**/*.md` | `knowledge/images/` 的 CDN URL | `![图注](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/文件名)` |
| `outputs/reviews/**/*.md` | `knowledge/images/` 的 CDN URL | `![图注](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/文件名)` |
| `outputs/packages/**` | 包内 `assets/` | 由目标软件包格式决定 |

---

## 3. `/courseware-collab` 图片处理

`/courseware-collab` 生成课件时，如需使用教材或习题图片：

1. 从源 Markdown 中读取真实图片文件名。
2. 确认图片源文件已存在于 `knowledge/images/` 或可同步到该目录。
3. 在课件中使用对应 CDN URL。

课件中不得引用本机绝对路径、`outputs/images/` 或 `outputs/assets/`。离线软件包需要本地图片时，只能在 `outputs/packages/{package_id}/assets/` 中生成副本。

---

## 4. 禁止写法

- 空图注 `![](path)`
- 课件中的 HTML 图片标签
- 跨目录相对引用knowledge图片
- 引用旧资源目录图片
- `<img src="C:/...">`、`<img src="D:/...">`
- URL 编码后的中文路径

---

## 5. 图片占位符

无法确认图片文件名时，可在草稿中使用占位符：

```text
[图片待确认：请从源教材或习题 Markdown 的 ./images/ 目录核对]
```

最终outputs中不得保留占位符。
