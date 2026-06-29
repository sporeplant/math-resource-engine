from __future__ import annotations

import unittest
from pathlib import Path

try:
    import validate_output as validator
except (ModuleNotFoundError, ImportError):
    from tools import validate_output as validator


LESSON_META = {
    "content_type": "lesson",
    "command": "lesson-collab",
}


def lesson_with_structured(structured: str) -> str:
    return f"""---
content_type: lesson
lesson_id: test
lesson_name: test
command: lesson-collab
workflow_version: v2
review_status: pending_human_review
created_at: "2026-06-14"
---

教师说明：这里可以讨论“理解”这个词为什么不适合写进目标。

<details>
<summary><strong>展开完整结构化设计（目标、评价、活动、题源及审核信息）</strong></summary>

{structured}

</details>
"""


class ScopedValidationTests(unittest.TestCase):
    def test_forbidden_terms_fail_inside_objectives(self) -> None:
        text = lesson_with_structured("""## objectives
### 基础层
- LO-B-01：能理解频数的意义。
### 中间层
- LO-M-01：能解释频数表。
### 拓展层
- LO-E-01：能分析数据分布。
""")
        errors: list[str] = []
        validator.check_scoped_forbidden_terms(text, LESSON_META, errors)
        self.assertTrue(any("forbidden term found in objectives: 理解" in e for e in errors))

    def test_forbidden_terms_do_not_fail_in_teacher_notes(self) -> None:
        text = lesson_with_structured("""## objectives
### 基础层
- LO-B-01：能说出频数表中的信息。
### 中间层
- LO-M-01：能解释频数表。
### 拓展层
- LO-E-01：能分析数据分布。
""")
        errors: list[str] = []
        validator.check_scoped_forbidden_terms(text, LESSON_META, errors)
        self.assertEqual([], errors)

    def test_question_like_block_requires_own_source_fields(self) -> None:
        text = lesson_with_structured("""## practice
source_id: TEXTBOOK-TEST
source_type: textbook
question_id: Q-TEST-00

- 题目：教材练习第1题。
""")
        errors: list[str] = []
        validator.check_question_source_fields(text, LESSON_META, errors)
        self.assertTrue(any("missing complete source fields" in e for e in errors))

    def test_question_ids_list_is_valid_source_format(self) -> None:
        text = lesson_with_structured("""## practice
- 题目：教材练习第1题与第2题。
  source_id: TEXTBOOK-TEST
  source_type: textbook
  question_ids:
    - Q-TEST-01
    - Q-TEST-02
""")
        errors: list[str] = []
        validator.check_question_source_fields(text, LESSON_META, errors)
        self.assertEqual([], errors)

    def test_courseware_without_yaml_is_detected_from_filename(self) -> None:
        errors: list[str] = []
        meta = validator.check_common(Path("测试_课件.md"), "# 📐 标题\n", errors)
        validator.check_required_layers("# 📐 标题\n", meta, errors)
        self.assertEqual({"content_type": "courseware", "command": "courseware-collab"}, meta)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
