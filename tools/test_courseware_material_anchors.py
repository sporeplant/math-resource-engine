from __future__ import annotations

import unittest

try:
    from validate_output import Page, check_courseware_material_anchors
except (ModuleNotFoundError, ImportError):
    from tools.validate_output import Page, check_courseware_material_anchors


def one_page(text: str) -> list[Page]:
    return [Page(text, 0, len(text.splitlines()))]


class CoursewareMaterialAnchorTests(unittest.TestCase):
    def validate(self, text: str) -> list[str]:
        errors: list[str] = []
        check_courseware_material_anchors(one_page(text), errors)
        return errors

    def test_rejects_question_without_visible_material(self) -> None:
        errors = self.validate("### 问题页\n\n**问题：**这四类信息分别适合用哪种统计图？")
        self.assertTrue(any("material anchor" in error for error in errors))

    def test_accepts_four_categories_listed_before_question(self) -> None:
        text = """### 四类统计图

| 数量比较 | 部分占比 | 前后变化 | 区间分布 |
|---|---|---|---|

**问题：**上面四类信息分别适合用哪种统计图表示？
"""
        self.assertEqual([], self.validate(text))

    def test_rejects_unidentified_digits(self) -> None:
        text = """### 频率

样本由70个增加到700个。

**问题：**样本增大后，各数字的频率会怎样？
"""
        errors = self.validate(text)
        self.assertTrue(any("digits 0 to 9" in error for error in errors))

    def test_accepts_digits_with_source_context(self) -> None:
        text = """### 频率

教材彩票号码问题统计0至9各数字，样本由70个增加到700个。

**问题：**样本增大后，各数字的频率会怎样？
"""
        self.assertEqual([], self.validate(text))


if __name__ == "__main__":
    unittest.main()
