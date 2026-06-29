# `/临界生` 命令定义

> 最后更新：2026-06-01

---

## 命令名称

`/临界生`

## 输入格式

```text
/临界生 [责任教师] [任教班级] [教材章节]
```

默认值：
- 责任教师：李金生
- 任教班级：八（3）班

示例：
```text
/临界生 李金生 八（3）班 chapter_21
/临界生 chapter_21
```

---

## 权威流程

`/临界生` 的唯一权威流程见：

> `orchestrator/workflow-registry.md` → `6. /临界生 工作流`

本文件只说明命令边界，不重复维护步骤链。

---

## 命令边界

- `/临界生` 只生成 `support/临界生分工表-YYYY-MM-DD.md`
- `/临界生` 不得修改 `students/support/template.md`
- `/临界生` outputs必须使用当前日期作为文件名的一部分
- `/临界生` 不需要人工审核，直接outputs可用的帮扶表

---

## 强制读取

1. `AGENTS.md`
2. `orchestrator/workflow-registry.md`
3. `skills/support/SKILL.md`
4. `skills/support/checklist.md`
5. `students/scores.md`
6. `knowledge/[章节]/` 下的知识点信息

---

## outputs要求

```yaml
---
content_type: borderline_students
teacher_name: ""
class_name: ""
chapter: ""
command: 临界生
created_at: ""
---
```

outputs文件：`support/临界生分工表-YYYY-MM-DD.md`

---

## 后续动作

直接使用生成的帮扶表，周期结束后填写"进步或待改进点"并提交教导处。
