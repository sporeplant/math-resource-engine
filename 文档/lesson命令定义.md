# `/lesson` 命令定义

> 最后更新：2026-05-29

---

## 命令名称

`/lesson`

## 输入格式

```text
/lesson 课时名称
```

---

## 权威流程

`/lesson` 的唯一权威流程见：

> `主控/工作流注册表.md` → `2. /lesson 工作流`

本文件只说明命令边界，不重复维护步骤链。

---

## 命令边界

- `/lesson` 只生成 `输出/{课时名}_教学设计.md`。
- `/lesson` 输出必须包含 YAML front matter。
- `/lesson` 输出的 `review_status` 必须为 `pending_human_review`。
- `/lesson` 完成后必须等待人工审核。
- `/lesson` 不生成课件。
- `/lesson` 不生成课堂提问参考答案。
- `/lesson` 不执行课件验证器或图片资源验证器。
- `/lesson` 中不得写入具体学生姓名，只能标注提问层级。

---

## 输出要求

```yaml
---
content_type: lesson
lesson_id: ""
lesson_name: ""
command: lesson
workflow_version: v2
review_status: pending_human_review
source_files: []
created_at: ""
---
```

---

## 后续动作

教师人工审核通过后，将教学设计元数据改为：

```yaml
review_status: human_approved
```

只有人工审核通过后的教学设计才能作为 `/courseware` 的输入。
