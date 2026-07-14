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

阅读建议：建议结合教材例题和学生练习本进行教学。

## 课堂实施导航

### 本课要解决的问题

怎样解决这个问题？

### 课堂实施要点

- 注意使用教材和练习本。
- 关注不同层次学生的学习进展。

### 核心提问

1. 你能说出方法吗？

### 课堂练习与作业

- 教材练习第1题：当堂检测
- 教材A组第1题：基础层必做
- 教材B组第2题：中间层必做
- 练习册第1题：基础层必做

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

### 10分钟流程总览

| 时间 | 教学环节 | 学生主要任务 | 教师支持 | 达成结果 |
|------|---------|-------------|---------|---------|
| 4分钟 | 环节一 | 观察 | 引导 | 理解概念 |
| 6分钟 | 环节二 | 表达 | 反馈 | 掌握方法 |

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
        # Now tests that ASK (question) backend IDs leak → error
        errors = self.validate(lesson(implementation_extra="\n- ASK-B-01\n"))
        self.assertTrue(any("exposes backend question ID" in error for error in errors), 
                       f"expected 'exposes backend question ID' in {errors}")

    def test_rejects_activity_time_mismatch(self) -> None:
        text = lesson().replace("### ACT-M-01 环节二（6分钟）", "### ACT-M-01 环节二（5分钟）")
        errors = self.validate(text)
        self.assertTrue(any("activity time/order mismatch" in error for error in errors))

    def test_rejects_missing_structured_section(self) -> None:
        text = lesson().replace("## homework\n", "")
        errors = self.validate(text)
        self.assertTrue(any("missing section: homework" in error for error in errors),
                       f"expected 'missing section: homework' in {errors}")

    def test_rejects_missing_implementation_heading(self) -> None:
        text = lesson().replace("## 课堂实施导航\n", "")
        errors = self.validate(text)
        self.assertTrue(any("missing heading: ## 课堂实施导航" in error for error in errors),
                       f"expected 'missing heading: ## 课堂实施导航' in {errors}")

    def test_rejects_missing_reading_suggestion(self) -> None:
        text = lesson().replace("阅读建议：建议结合教材例题和学生练习本进行教学。", "")
        errors = self.validate(text)
        self.assertTrue(any("missing 阅读建议" in error for error in errors))

    def test_rejects_missing_flow_table(self) -> None:
        text = lesson().replace("| 时间 | 教学环节 | 学生主要任务 | 教师支持 | 达成结果 |", "")
        errors = self.validate(text)
        self.assertTrue(any("missing the required five-column flow table" in error for error in errors))

    def test_rejects_core_question_mismatch(self) -> None:
        # Only replace in implementation layer, not structured
        text = lesson().replace("### 本课要解决的问题\n\n怎样解决这个问题？",
                                "### 本课要解决的问题\n\n另一问题？")
        errors = self.validate(text)
        self.assertTrue(any("dual-layer core question mismatch" in error for error in errors))

    def test_rejects_source_field_in_implementation(self) -> None:
        errors = self.validate(lesson(implementation_extra="\nsource_id: test\n"))
        self.assertTrue(any("exposes backend source field" in error for error in errors),
                       f"expected 'exposes backend source field' in {errors}")

    def test_rejects_activity_count_mismatch(self) -> None:
        # Remove all flow table rows → count mismatch
        text = lesson().replace("| 4分钟 | 环节一 | 观察 | 引导 | 理解概念 |\n| 6分钟 | 环节二 | 表达 | 反馈 | 掌握方法 |", "| 4分钟 | 环节一 | 观察 | 引导 | 理解概念 |")
        errors = self.validate(text)
        self.assertTrue(any("dual-layer activity count mismatch" in error for error in errors),
                       f"expected 'dual-layer activity count mismatch' in {errors}")


if __name__ == "__main__":
    unittest.main()
