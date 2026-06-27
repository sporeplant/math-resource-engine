# 图片引用协议

本协议是图片路径的orchestrator规则。详细 Skill 规则见 `skills/images/SKILL.md`。

---

## 1. 唯一原则

任意 Markdown 文件引用图片时，只允许引用该文件同级目录下的 `images/` 子目录。

课件标准写法：

```markdown
![图注](./images/xxx.jpg)
```

---

## 2. 目录对应关系

| Markdown 文件位置 | 图片目录 | 引用路径 |
|-------------------|----------|----------|
| `knowledge/textbooks/*.md` | `knowledge/textbooks/images/` | `./images/文件名` |
| `knowledge/workbooks/*.md` | `knowledge/workbooks/images/` | `./images/文件名` |
| `outputs/*_课件.md` | `outputs/images/` | `![图注](./images/文件名)` |

---

## 3. `/courseware-collab` 图片处理

`/courseware-collab` 生成课件时，如需使用教材或习题图片：

1. 从源 Markdown 中读取真实图片文件名。
2. 将图片复制或登记到 `outputs/images/`。
3. 在课件中使用 `![图注](./images/文件名)`。

课件中不得直接引用knowledge目录。

---

## 4. 禁止写法

- 空图注 `![](path)`
- 课件中的 HTML 图片标签
- 跨目录引用knowledge图片
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
