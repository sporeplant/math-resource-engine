from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    from validate_output import check_required_practice_pages
except (ModuleNotFoundError, ImportError):
    from tools.validate_output import check_required_practice_pages


LESSON = """## practice

1. 教材练习第1题，限时2分钟。
2. 教材练习第2题，限时2分钟。
3. A组第4题第（2）问，限时2分钟。
4. B组第1题，限时3分钟。
"""


class CoursewarePracticePageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.lesson = Path(self.temp_dir.name) / "lesson.md"
        self.lesson.write_text(LESSON, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate(self, courseware: str) -> list[str]:
        errors: list[str] = []
        check_required_practice_pages(courseware, self.lesson, errors)
        return errors

    def test_rejects_question_only_page(self) -> None:
        text = """### 🤔 频率边界

A组第4题第（2）问

**问题：**频率会怎样？
"""
        self.assertTrue(any("explicit practice task page" in error for error in self.validate(text)))

    def test_accepts_explicit_task_page(self) -> None:
        text = """### 📝 教材练习第1题

请在练习本上完成。

（限时2分钟）

评分：判断1分，依据2分。

产出：判断和依据。

---

### 📝 参考答案

教材练习第1题 参考答案：略。

---

### 📝 教材练习第2题

请在练习本上完成。

（限时2分钟）

评分：判断1分，依据2分。

产出：判断和依据。

---

### 📝 参考答案

教材练习第2题 参考答案：略。

---

### 📝 A组第4题第（2）问

请在练习本上完成。

（限时2分钟）

评分：判断1分，依据2分。

产出：判断和依据。

---

### 📝 参考答案

A组第4题第（2）问 参考答案：略。

---

### 📝 B组第1题

请在练习本上完成。

（限时2分钟）

评分：判断1分，依据2分。

产出：判断和依据。

---

### 📝 参考答案

B组第1题 参考答案：略。
"""
        self.assertEqual([], self.validate(text))

    def test_rejects_missing_reference_answer_page(self) -> None:
        text = """### 📝 教材练习第1题

请在练习本上完成。

（限时2分钟）

评分：判断1分，依据2分。

产出：判断和依据。
"""
        self.assertTrue(any("reference answer page" in error for error in self.validate(text)))


if __name__ == "__main__":
    unittest.main()
