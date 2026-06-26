from __future__ import annotations

import unittest

try:
    from validate_output import check_lesson_dual_layer
except (ModuleNotFoundError, ImportError):
    from tools.validate_output import check_lesson_dual_layer


def lesson(implementation_extra: str = "", structured_extra: str = "") -> str:
    return f"""---
content_type: lesson
lesson_id: "test"
lesson_name: "测试课"
command: lesson-collab
workflow_version: v2
review_status: pending_human_review
created_at: "2026-06-12 10:00"
---

# 测试课教学设计

> **阅读建议**：日常备课先看课堂实施导航，需要审核时展开完整结构化设计。

## 课堂实施导航

### 本课要解决的问题

怎样解决这个问题？

### 10分钟流程总览

| 时间 | 教学环节 | 学生主要任务 | 教师支持 | 达成结果 |
|---:|---|---|---|---|
| 4分钟 | 环节一 | 观察 | 提示 | 发现 |
| 6分钟 | 环节二 | 表达 | 反馈 | 归纳 |

### 课堂实施要点

- 学生先做。

### 核心提问

- 为什么？

### 课堂练习与作业

- 课堂：完成练习。
- 作业：完成作业。
{implementation_extra}

<details>
<summary><strong>展开完整结构化设计（目标、评价、活动、题源及审核信息）</strong></summary>

## meta
- core_question: 怎样解决这个问题？
## knowledge_analysis
## objectives
## assessment
## problem_chain
## lesson_flow
### ACT-B-01 环节一（4分钟）
### ACT-M-01 环节二（6分钟）
## practice
## homework
## boardwork
## consistency_matrix
## quality_check
{structured_extra}
</details>
"""


class LessonDualLayerTests(unittest.TestCase):
    def validate(self, text: str) -> list[str]:
        errors: list[str] = []
        check_lesson_dual_layer(text, {"content_type": "lesson"}, errors)
        return errors

    def test_accepts_complete_dual_layer_lesson(self) -> None:
        self.assertEqual([], self.validate(lesson()))

    def test_rejects_backend_fields_in_implementation_layer(self) -> None:
        errors = self.validate(lesson(implementation_extra="\n- ACT-B-01\n"))
        self.assertTrue(any("exposes backend activity ID" in error for error in errors))

    def test_rejects_activity_time_mismatch(self) -> None:
        text = lesson().replace("### ACT-M-01 环节二（6分钟）", "### ACT-M-01 环节二（5分钟）")
        errors = self.validate(text)
        self.assertTrue(any("activity time/order mismatch" in error for error in errors))

    def test_rejects_missing_structured_section(self) -> None:
        text = lesson().replace("## homework\n", "")
        errors = self.validate(text)
        self.assertTrue(any("missing section: homework" in error for error in errors))

    def test_rejects_untracked_implementation_task(self) -> None:
        text = lesson(implementation_extra="\n- 课堂补充：A组第7题。\n")
        errors = self.validate(text)
        self.assertTrue(any("missing from structured layer: A组第7题" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
