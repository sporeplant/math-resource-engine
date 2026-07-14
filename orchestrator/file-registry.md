# 文件注册表

定义项目文件命名和引用规则。工作流边界以 `orchestrator/workflow-registry.md` 为准。

---

## 1. outputs文件命名

| 产物 | 命名规则 |
|------|----------|
| 教学设计 | `outputs/{课时名}_教学设计.md` |
| Markdown 课件 | `outputs/{课时名}_课件.md` |
| 课堂提问调度稿 | `outputs/{课时名}_课堂提问调度稿.md` |
| 教材问题参考解答 | `knowledge/solutions/ch{章节号}/solution-{lesson_id}.md` |
| 练习册逐题索引 | `knowledge/workbook-index/workbook-index-{课时编号}.yaml` |
| 软件或离线导出包 | `outputs/packages/{package_id}/` |
| 临界生分工表 | `support/临界生分工表-YYYY-MM-DD.md` |

---

## 2. 模板文件

| 模板 | 位置 |
|------|------|
| 临界生分工表模板 | `students/support/template.md` |
| 临界生分工表填写说明 | `docs/support-guide.md` |

---

## 2.1 策略文件

| 策略 | 位置 | 用途 |
|------|------|------|
| 教材-练习册双资源调度策略 | `orchestrator/resource-scheduling.md` | `/lesson-collab` 生成前盘点教材与练习册题目，决定当堂检测、课后作业和后移题 |

---

## 3. 图片目录规则

正式 outputs Markdown 默认引用 `knowledge/images/` 对应 CDN URL。knowledge 源文件可继续使用自身约定的相对图片目录。

| Markdown 位置 | 图片目录 | 引用写法 |
|---------------|----------|----------|
| `knowledge/textbooks/*.md` | `knowledge/textbooks/images/` | `<img src="./images/image.jpg" width="35%">` |
| `knowledge/workbooks/*.md` | `knowledge/workbooks/images/` | `<img src="./images/image.jpg" width="35%">` |
| `knowledge/workbook-answers/*.md` | `knowledge/images/` 的 CDN URL | `![caption](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/image.jpg)` |
| `outputs/lessons/**/*.md` | `knowledge/images/` 的 CDN URL | `![caption](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/image.jpg)` |
| `outputs/reviews/**/*.md` | `knowledge/images/` 的 CDN URL | `![caption](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/image.jpg)` |
| `outputs/packages/**` | 包内 `assets/` | 由目标软件包格式决定 |
| `knowledge/solutions/ch*/*.md` | `knowledge/solutions/ch{章节号}/images/` | `<img src="./images/image.jpg" width="35%">` |

禁止使用：

- 跨目录相对引用knowledge图片
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
