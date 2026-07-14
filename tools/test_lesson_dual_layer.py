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

## 一、教学内容

测试课内容。

## 二、教学目标

1. 能说出测试内容。

## 三、教学重点与难点

重点：测试重点。难点：测试难点。

## 四、教学准备

教材、练习本。

## 五、教学过程

### （一）环节一（4分钟）

学生观察。

### （二）环节二（6分钟）

学生表达。

## 六、当堂检测

1. 教材练习第1题，检测学生能否说出方法，限时3分钟。

## 七、课后作业

基础层必做：教材A组第1题、练习册第1题，预计20分钟。
中间层必做：教材B组第2题，预计25分钟。
拓展层选做：练习册第5题，增加1道。

## 八、板书设计

测试课板书。

## 九、设计依据简记

练习册第6题后移到习题课处理。
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
## resource_audit
- 教材练习第1题：当堂检测
- A组第1题：基础层必做
- B组第2题：中间层必做
- 练习册第1题：基础层必做
  source_id: workbook-test
  source_type: exercise_bank
  question_id: WB-TEST-001
- 练习册第5题：拓展层选做
  source_id: workbook-test
  source_type: exercise_bank
  question_id: WB-TEST-005
- 练习册第6题：后移到习题课
  source_id: workbook-test
  source_type: exercise_bank
  question_id: WB-TEST-006
## practice
- 题目：教材练习第1题
  检测目标: 能说出方法
  限时: 3分钟
  source_id: TEXTBOOK-TEST
  source_type: textbook
  question_id: T-001
## homework
- 基础层必做（约20分钟）：教材A组第1题、练习册第1题
  source_id: workbook-test
  source_type: exercise_bank
  question_id: WB-TEST-001
- 中间层必做（约25分钟）：教材B组第2题
  source_id: TEXTBOOK-TEST
  source_type: textbook
  question_id: T-B-002
- 拓展层选做（增加1题，约5分钟）：练习册第5题
  source_id: workbook-test
  source_type: exercise_bank
  question_id: WB-TEST-005
## deferred_exercises
- 题目：练习册第6题
  去向: 习题课
  理由: 综合度较高，留到阶段整理
  source_id: workbook-test
  source_type: exercise_bank
  question_id: WB-TEST-006
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

    def test_rejects_workbook_id_in_implementation_layer(self) -> None:
        errors = self.validate(lesson(implementation_extra="\n- WB-TEST-001\n"))
        self.assertTrue(any("exposes backend workbook question ID" in error for error in errors))

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

    def test_rejects_missing_traditional_heading(self) -> None:
        text = lesson().replace("## 六、当堂检测\n", "")
        errors = self.validate(text)
        self.assertTrue(any("missing heading: ## 六、当堂检测" in error for error in errors))

    def test_rejects_missing_deferred_plan(self) -> None:
        text = lesson().replace("练习册第6题后移到习题课处理。", "")
        errors = self.validate(text)
        self.assertTrue(any("missing 后移题安排" in error for error in errors))

    def test_rejects_workbook_audit_without_destination(self) -> None:
        text = lesson().replace("question_id: WB-TEST-006", "question_id: WB-TEST-009", 1)
        errors = self.validate(text)
        self.assertTrue(any("missing practice/homework/deferred_exercises" in error for error in errors))

    def test_rejects_homework_without_layer_time(self) -> None:
        text = lesson().replace("基础层必做（约20分钟）", "基础层必做")
        errors = self.validate(text)
        self.assertTrue(any("基础层必做 missing estimated time" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
