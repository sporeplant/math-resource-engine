# `/courseware` 命令定义

> 最后更新：2026-05-29

---

## 命令名称

`/courseware`

## 输入格式

```text
/courseware 课时名称
```

---

## 权威流程

`/courseware` 的唯一权威流程见：

> `主控/工作流注册表.md` → `4. /courseware 工作流`

本文件只说明命令边界，不重复维护步骤链。

---

## 前置条件

`/courseware` 必须读取 `输出/{课时名}_教学设计.md`，且该文件头部必须满足：

```yaml
content_type: lesson
review_status: human_approved
```

若教学设计状态为 `draft`、`pending_human_review` 或 `rejected`，必须停止，并提示先完成人工审核。

---

## 命令边界

- `/courseware` 只生成课件和课堂提问参考答案。
- `/courseware` 不重新生成学习目标、评价任务、活动设计或教学设计。
- `/courseware` 必须使用人工审核通过的教学设计作为唯一上游方案。
- `/courseware` 可调用分层提问技能，为课件填入学生姓名，并同步生成教师手持参考答案。
- `/courseware` 生成的图片引用只允许使用 `./images/{文件名}`。

---

## 输出要求

```yaml
---
content_type: courseware
lesson_id: ""
lesson_name: ""
command: courseware
workflow_version: v2
review_status: draft
source_files:
  - "输出/{课时名}_教学设计.md"
created_at: ""
---
```

同时输出：

- `输出/{课时名}_课件.md`
- `输出/{课时名}_课堂提问参考答案.md`
- `输出/images/{图片文件名}`

---

## 验证要求

输出前必须通过：

- `验证器/课件验证器/验证规则.md`
- `验证器/图片资源验证器/验证规则.md`
- `tools/validate_output.py`
