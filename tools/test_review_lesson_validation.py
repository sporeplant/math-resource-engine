from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    import validate_output
    import validate_review_lesson
    from review_math_utils import normalize_review_math_markup, validate_math_markup
except (ModuleNotFoundError, ImportError):
    from tools import validate_output, validate_review_lesson
    from tools.review_math_utils import (
        normalize_review_math_markup,
        validate_math_markup,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
GOOD_SAMPLE = REPO_ROOT / "outputs" / "G8B-reviews" / "review-04.md"


def make_review_lesson(
    question_count: int = 24,
    overview_count: int | None = None,
    unbalanced: bool = False,
    image: str = "",
) -> str:
    overview_count = question_count if overview_count is None else overview_count
    lines = [
        "---",
        "content_type: review_lesson",
        'lesson_id: "test"',
        'lesson_name: "测试复习讲义"',
        "command: 复习讲义",
        "workflow_version: v2",
        "source_files:",
        '  - "knowledge/reviews/03讲.md"',
        '  - "knowledge/reviews/04.md"',
        'created_at: "2026-06-16 08:00"',
        "---",
        "",
        "## 第 03-04 讲 测试复习讲义",
        "",
        "## 知识点01 坐标表示位置",
        "",
        "坐标表示位置。",
        "",
        "## 例题讲解",
        "",
    ]
    for number in range(1, 4):
        lines.append(f"{number}．例题 {number}")
        lines.append("")
    lines.extend(
        [
            "## 知识点02 坐标表示平移",
            "",
            "坐标表示平移。",
            "",
            "## 知识点03 坐标规律探索",
            "",
            "坐标规律探索。",
            "",
        ]
    )
    lines.extend(["## 当堂练习", ""])
    for number in range(4, 13):
        lines.append(f"{number}．当堂练习 {number}")
        if image and number == 4:
            lines.extend(["", image])
        lines.append("")
    lines.extend(["## 课后作业", ""])
    for number in range(13, question_count + 1):
        lines.append(f"{number}．课后作业 {number}")
        lines.append("")
    lines.extend(
        [
            "## 题目信息总览",
            "",
            "| 题目ID | 知识考察点 | 难度 | 入选理由 |",
            "|--------|-----------|------|---------|",
        ]
    )
    labels = ["坐标表示位置", "坐标表示平移", "坐标规律探索"]
    difficulties = ["★★", "★★★", "★★★★"]
    for index in range(1, overview_count + 1):
        label = labels[0] if unbalanced else labels[(index - 1) % 3]
        difficulty = difficulties[(index - 1) % 3]
        prefix = "03讲" if index <= 16 else "04讲"
        lines.append(f"| {prefix}-测试-{index} | {label} | {difficulty} | 测试覆盖 |")
    return "\n".join(lines) + "\n"


class ReviewLessonValidationTests(unittest.TestCase):
    def test_current_good_sample_passes_review_validator(self) -> None:
        self.assertEqual([], validate_review_lesson.validate(GOOD_SAMPLE))

    def test_current_good_sample_passes_output_validator(self) -> None:
        errors, warnings = validate_output.validate(GOOD_SAMPLE, None, None, None)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_too_few_questions_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.md"
            path.write_text(make_review_lesson(question_count=17), encoding="utf-8")
            errors = validate_review_lesson.validate(path)
        self.assertTrue(any("question count out of range" in error for error in errors))

    def test_review_status_fails_for_review_lesson(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.md"
            text = make_review_lesson().replace(
                "created_at:", "review_status: draft\ncreated_at:"
            )
            path.write_text(text, encoding="utf-8")
            errors = validate_review_lesson.validate(path)
        self.assertTrue(any("must not set review_status" in error for error in errors))

    def test_missing_image_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.md"
            path.write_text(
                make_review_lesson(image="![](images/missing.jpg)"), encoding="utf-8"
            )
            errors = validate_review_lesson.validate(path)
        self.assertTrue(any("image file does not exist" in error for error in errors))

    def test_empty_question_stem_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.md"
            text = make_review_lesson().replace("4．当堂练习 4", "4．")
            path.write_text(text, encoding="utf-8")
            errors = validate_review_lesson.validate(path)
        self.assertTrue(any("question 4 has empty stem" in error for error in errors))

    def test_unclosed_math_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review.md"
            text = make_review_lesson() + "\n补充：$y = kx + b\n"
            path.write_text(text, encoding="utf-8")
            errors = validate_review_lesson.validate(path)
        self.assertTrue(any("未闭合" in error for error in errors))

    def test_circled_latex_is_normalized_outside_formula(self) -> None:
        text = r"4．函数 $\textcircled{1} y = k x + b$；$\textcircled { 2 } y = 2x$"
        normalized = normalize_review_math_markup(text)
        self.assertIn("① $y = k x + b$", normalized)
        self.assertIn("② $y = 2x$", normalized)
        self.assertNotIn(r"\textcircled", normalized)

    def test_unsupported_circled_latex_fails_math_validation(self) -> None:
        errors = validate_math_markup(r"4．函数 $\textcircled{1} y = k x + b$")
        self.assertTrue(any(r"\textcircled" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
