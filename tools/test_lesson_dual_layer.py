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

### （一）导入（3分钟）

学生观察。

### （二）新知（5分钟）

学生表达。
{implementation_extra}

## 六、当堂检测

1. 教材练习第1题，检测目标：能说出方法，限时3分钟。

## 七、课后作业

基础层必做：教材A组第1题，约5分钟。
中间层必做：教材A组第2题，约5分钟。
拓展层选做：教材B组第1题，约5分钟。

## 八、板书设计

测试课板书。

## 九、设计依据简记

测试说明。

<details>
<summary><strong>展开完整结构化设计（目标、评价、活动、题源及审核信息）</strong></summary>

## meta
## knowledge_analysis
## objectives
## assessment
## problem_chain
## lesson_flow
### ACT-B-01 导入（3分钟）
### ACT-M-01 新知（5分钟）
## resource_audit
## practice
## homework
## deferred_exercises
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
        self.assertTrue(any("exposes backend activity ID" in e for e in errors),
                       f"expected 'exposes backend activity ID' in {errors}")

    def test_rejects_question_id_in_implementation_layer(self) -> None:
        errors = self.validate(lesson(implementation_extra="\n- ASK-B-01\n"))
        self.assertTrue(any("exposes backend question ID" in e for e in errors),
                       f"expected 'exposes backend question ID' in {errors}")

    def test_rejects_source_field_in_implementation(self) -> None:
        errors = self.validate(lesson(implementation_extra="\nsource_id: test\n"))
        self.assertTrue(any("exposes backend source field" in e for e in errors),
                       f"expected 'exposes backend source field' in {errors}")

    def test_rejects_missing_structured_section(self) -> None:
        text = lesson().replace("## homework\n", "")
        errors = self.validate(text)
        self.assertTrue(any("missing section: homework" in e for e in errors),
                       f"expected 'missing section: homework' in {errors}")

    def test_rejects_missing_traditional_heading(self) -> None:
        text = lesson().replace("## 八、板书设计\n", "")
        errors = self.validate(text)
        self.assertTrue(
            any("missing heading: ## 八、板书设计" in e for e in errors),
            f"expected 'missing heading: ## 八、板书设计' in {errors}",
        )

    def test_rejects_missing_folded_layer(self) -> None:
        text = lesson().replace("<details>", "<section>").replace("</details>", "</section>")
        errors = self.validate(text)
        self.assertTrue(
            any("required folded 完整结构化设计 layer" in e for e in errors),
            f"expected 'required folded' in {errors}",
        )

    def test_rejects_collab_gates_in_yaml(self) -> None:
        text = lesson().replace(
            'created_at: "2026-06-12 10:00"',
            'created_at: "2026-06-12 10:00"\ncollab_gates:\n  - gate: test\n    status: confirmed\n',
        )
        errors = self.validate(text)
        self.assertTrue(
            any("collab_gates" in e for e in errors),
            f"expected 'collab_gates' violation in {errors}",
        )

    def test_rejects_missing_layered_homework(self) -> None:
        text = lesson().replace("基础层必做：教材A组第1题，约5分钟。\n中间层必做：教材A组第2题，约5分钟。\n拓展层选做：教材B组第1题，约5分钟。", "教材A组第1题。")
        errors = self.validate(text)
        self.assertTrue(
            any("lacks layered homework" in e for e in errors),
            f"expected 'lacks layered homework' in {errors}",
        )

    def test_rejects_headings_out_of_order(self) -> None:
        text = lesson()
        # Swap 六 and 七
        text = text.replace("## 六、当堂检测", "## TEMP").replace("## 七、课后作业", "## 六、当堂检测").replace("## TEMP", "## 七、课后作业")
        errors = self.validate(text)
        self.assertTrue(
            any("out of order" in e for e in errors),
            f"expected 'out of order' in {errors}",
        )


if __name__ == "__main__":
    unittest.main()
