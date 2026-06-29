# 文件注册表

定义项目文件命名和引用规则。工作流边界以 `orchestrator/workflow-registry.md` 为准。

---

## 1. outputs文件命名

| 产物 | 命名规则 |
|------|----------|
| 教学设计 | `outputs/{课时名}_教学设计.md` |
| Markdown 课件 | `outputs/{课时名}_课件.md` |
| 课堂提问调度稿 | `outputs/{课时名}_课堂提问调度稿.md` |
| 教材问题参考解答 | `knowledge/solutions/solution-{lesson_id}.md` |
| outputs图片 | `outputs/images/{图片文件名}` |
| 临界生分工表 | `support/临界生分工表-YYYY-MM-DD.md` |

---

## 2. 模板文件

| 模板 | 位置 |
|------|------|
| 临界生分工表模板 | `students/support/template.md` |
| 临界生分工表填写说明 | `docs/support-guide.md` |

---

## 3. 图片目录规则

任意 Markdown 文件引用图片时，只允许引用同级 `images/` 子目录。

| Markdown 位置 | 图片目录 | 引用写法 |
|---------------|----------|----------|
| `knowledge/textbooks/*.md` | `knowledge/textbooks/images/` | `<img src="./images/文件名" width="35%">` |
| `knowledge/workbooks/*.md` | `knowledge/workbooks/images/` | `<img src="./images/文件名" width="35%">` |
| `outputs/*.md` | `outputs/images/` | `![图注](./images/文件名)` |
| `knowledge/solutions/*.md` | `knowledge/solutions/images/` | `<img src="./images/文件名" width="35%">` |

禁止使用：

- 跨目录引用knowledge图片
- 引用旧资源目录图片
- 绝对路径
- Markdown 图片语法 `![]()`

---

## 3. lesson_id 规则

格式建议：

```text
{chapter}.{section}-{topic_slug}-{yyyymmdd}
```

示例：

```text
21.8-tixing-20260529
```

同一课时的教学设计、课件、课堂提问调度稿必须使用同一个 `lesson_id`。

---

## 4. 跨文件引用

- 引用上游产物时，写入 YAML front matter 的 `source_files`。
- `/courseware-collab` 的 `source_files` 必须包含人工审核通过的教学设计文件。
- 跨 Skill 不再使用 `../../skills/{skill-name}/outputs/{filename}` 路径。
- 不允许循环引用。
