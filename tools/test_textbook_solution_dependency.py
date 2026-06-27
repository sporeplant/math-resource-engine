from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    from textbook_solution_dependency import parse_front_matter, validate_dependency
except ModuleNotFoundError:
    from tools.textbook_solution_dependency import parse_front_matter, validate_dependency


SOLUTION = """---
content_type: textbook_solution
lesson_id: "22.4"
lesson_name: "频数分布与直方图"
command: 教材问题解答
workflow_version: v2
source_files: []
created_at: "2026-06-10 10:45"
---

## 教材任务清单

| 教材顺序 | question_id | 教材位置 |
|---:|---|---|
| 1 | 22.4-练习-1 | 练习第（1）题 |

## 参考解答

```yaml
question_id: "22.4-练习-1"
source_type: textbook
答案来源: AI参考推导
```

## 覆盖统计
"""


def downstream(source_path: str, question_id: str = "22.4-练习-1", source_type: str = "textbook") -> str:
    return f"""---
content_type: lesson
lesson_id: "22.4"
lesson_name: "频数分布与直方图"
command: lesson-collab
workflow_version: v2
review_status: pending_human_review
source_files:
  - "{source_path}"
created_at: "2026-06-10 12:00"
---

```yaml
question_id: "{question_id}"
source_type: {source_type}
```
"""


class TextbookSolutionDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "AGENTS.md").write_text("test", encoding="utf-8")
        self.solution_dir = self.root / "knowledge" / "solutions"
        self.solution_dir.mkdir(parents=True)
        self.solution = self.solution_dir / "solution-22.4.md"
        self.solution.write_text(SOLUTION, encoding="utf-8")
        self.output_dir = self.root / "outputs"
        self.output_dir.mkdir()
        self.output = self.output_dir / "22.4_教学设计.md"
        self.relative_solution = "knowledge/solutions/solution-22.4.md"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate(self, text: str) -> list[str]:
        self.output.write_text(text, encoding="utf-8")
        meta, _ = parse_front_matter(text)
        return validate_dependency(self.output, text, meta)

    def test_valid_dependency_passes(self) -> None:
        self.assertEqual([], self.validate(downstream(self.relative_solution)))

    def test_missing_registration_fails(self) -> None:
        errors = self.validate(downstream("outputs/其他文件.md"))
        self.assertTrue(any("source_files must register" in error for error in errors))

    def test_missing_file_fails(self) -> None:
        errors = self.validate(downstream("knowledge/solutions/solution-22.4-missing.md"))
        self.assertTrue(any("does not exist" in error for error in errors))

    def test_lesson_id_mismatch_fails(self) -> None:
        self.solution.write_text(SOLUTION.replace('lesson_id: "22.4"', 'lesson_id: "22.3"'), encoding="utf-8")
        errors = self.validate(downstream(self.relative_solution))
        self.assertTrue(any("lesson_id does not match" in error for error in errors))

    def test_missing_textbook_question_id_fails(self) -> None:
        errors = self.validate(downstream(self.relative_solution, "22.4-练习-99"))
        self.assertTrue(any("练习-99" in error for error in errors))

    def test_workbook_question_is_not_required_in_textbook_solution(self) -> None:
        self.assertEqual(
            [],
            self.validate(downstream(self.relative_solution, "WB-22.4-01", "exercise_bank")),
        )

    def test_filename_must_match_lesson(self) -> None:
        wrong_name = self.solution_dir / "solution-22.4-other.md"
        wrong_name.write_text(SOLUTION, encoding="utf-8")
        errors = self.validate(downstream("knowledge/solutions/solution-22.4-other.md"))
        self.assertTrue(any("filename does not match" in error for error in errors))

    def test_reference_answer_must_preserve_answer_source(self) -> None:
        text = downstream(self.relative_solution).replace(
            "content_type: lesson", "content_type: question_reference"
        )
        errors = self.validate(text)
        self.assertTrue(any("must preserve 答案来源" in error for error in errors))

    def test_reference_answer_with_answer_source_passes(self) -> None:
        text = downstream(self.relative_solution).replace(
            "content_type: lesson", "content_type: question_reference"
        ) + "\n答案来源: AI参考推导\n"
        self.assertEqual([], self.validate(text))


if __name__ == "__main__":
    unittest.main()
