from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from tools import validate_output as tools_validator


ROOT = Path(__file__).resolve().parents[1]


def load_root_validator():
    spec = importlib.util.spec_from_file_location(
        "root_validate_output", ROOT / "tools" / "validate_output.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


TEXTBOOK_SOLUTION = """---
content_type: textbook_solution
lesson_id: "test"
lesson_name: "test"
command: 教材问题解答
workflow_version: v2
created_at: "2026-06-11 10:12"
---

基础层 中间层 拓展层

question_id: "test-1"
source_id: "教材原文_test"
source_type: textbook

**原题**：请调查并了解实际情况。

**参考解答**：按实际调查数据作答。
"""


class TextbookSolutionForbiddenTermsTest(unittest.TestCase):
    def test_original_question_is_exempt_in_both_validators(self) -> None:
        for validator in (load_root_validator(), tools_validator):
            errors: list[str] = []
            meta = validator.check_common(Path("test.md"), TEXTBOOK_SOLUTION, errors)
            validator.check_scoped_forbidden_terms(TEXTBOOK_SOLUTION, meta, errors)
            self.assertNotIn("forbidden term found: 了解", errors)

    def test_generated_answer_is_still_checked(self) -> None:
        text = TEXTBOOK_SOLUTION.replace(
            "按实际调查数据作答。", "需要了解实际调查数据。"
        )
        for validator in (load_root_validator(), tools_validator):
            errors: list[str] = []
            meta = validator.check_common(Path("test.md"), text, errors)
            validator.check_scoped_forbidden_terms(text, meta, errors)
            self.assertIn("forbidden term found: 了解", errors)


if __name__ == "__main__":
    unittest.main()
