from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    from validate_lesson_dual_layer import validate
except ModuleNotFoundError:
    from tools.validate_lesson_dual_layer import validate


def lesson() -> str:
    return """---
content_type: lesson
lesson_id: test
lesson_name: 测试课
command: lesson-collab
workflow_version: v2
review_status: pending_human_review
created_at: "2026-07-14"
---

# 测试课教学设计

## 一、教学内容

测试内容。

## 二、教学目标

能说出测试内容。

## 三、教学重点与难点

重点：测试重点。难点：测试难点。

## 四、教学准备

教材、练习本、黑板。

## 五、教学过程

### （一）导入（3分钟）

学生观察。

### （二）新知（5分钟）

学生表达。

## 六、当堂检测

教材练习第1题。检测目标：能说出方法。限时3分钟。

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
## resource_audit
## practice
## homework
## deferred_exercises
## boardwork
## consistency_matrix
## quality_check

</details>
"""


class ValidateLessonDualLayerCliTests(unittest.TestCase):
    def write_lesson(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".md", delete=False
        )
        with handle:
            handle.write(text)
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return Path(handle.name)

    def test_accepts_complete_two_layer_lesson(self) -> None:
        self.assertEqual([], validate(self.write_lesson(lesson())))

    def test_rejects_missing_folded_structured_layer(self) -> None:
        text = lesson().replace("<details>", "<section>").replace(
            "</details>", "</section>"
        )
        errors = validate(self.write_lesson(text))
        self.assertIn(
            "lesson must contain the required folded 完整结构化设计 layer", errors
        )

    def test_rejects_missing_teacher_heading(self) -> None:
        text = lesson().replace("## 八、板书设计\n", "")
        errors = validate(self.write_lesson(text))
        self.assertIn(
            "lesson implementation layer missing heading: ## 八、板书设计", errors
        )

    def test_rejects_backend_ids_in_teacher_layer(self) -> None:
        text = lesson().replace("测试内容。", "测试内容。\n\nASK_B_01", 1)
        errors = validate(self.write_lesson(text))
        self.assertIn("lesson implementation layer exposes backend question ID", errors)

    def test_rejects_collab_gates_in_yaml_front_matter(self) -> None:
        text = lesson().replace(
            'created_at: "2026-07-14"',
            'created_at: "2026-07-14"\ncollab_gates:\n  - gate: test\n',
        )
        errors = validate(self.write_lesson(text))
        self.assertTrue(
            any("collab_gates" in e for e in errors),
            f"expected 'collab_gates' violation in {errors}",
        )


if __name__ == "__main__":
    unittest.main()
