from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    from validate_lesson_timing import validate_timing
except (ModuleNotFoundError, ImportError):
    from tools.validate_lesson_timing import validate_timing


def activity(activity_id: str, minutes: float, priority: str = "core", activity_type: str = "独立练习") -> str:
    return f"""### {activity_id} 测试活动（{minutes:g}分钟）

- activity_type: {activity_type}
- time_priority: {priority}
- time_budget:
    instruction: 0.5
    student_work: {minutes - 2:g}
    interaction: 0.5
    feedback: 0.5
    transition: 0.5
    total: {minutes:g}
"""


def lesson(specs: list[tuple[str, float, str, str]]) -> str:
    rows = "\n".join(f"| {minutes:g}分钟 | 活动 | 做题 | 支持 | 结果 |" for _, minutes, _, _ in specs)
    blocks = "\n".join(activity(*spec) for spec in specs)
    total = sum(spec[1] for spec in specs)
    return f"""# 测试

## 课堂实施导航

### {total:g}分钟流程总览

| 时间 | 教学环节 | 学生主要任务 | 教师支持 | 达成结果 |
|---:|---|---|---|---|
{rows}

<details>
<summary>结构化设计</summary>

## lesson_flow

{blocks}
</details>
"""


PROFILE = """---
current_week: 16
completed_regular_lessons: 41
remaining_regular_lessons: 8
progress_status: 紧张
class_size: 47
basic_students: 30
intermediate_students: 11
advanced_students: 6
low_interaction_students: 13
timing_factors:
  instruction: 1.0
  student_work: 1.0
  interaction: 1.0
  feedback: 1.0
  transition: 1.0
---
"""


class LessonTimingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.lesson_path = root / "lesson.md"
        self.profile_path = root / "profile.md"
        self.log_path = root / "log.md"
        self.profile_path.write_text(PROFILE, encoding="utf-8")
        self.log_path.write_text("", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate(self, text: str, log: str = ""):
        self.lesson_path.write_text(text, encoding="utf-8")
        self.log_path.write_text(log, encoding="utf-8")
        return validate_timing(self.lesson_path, self.profile_path, self.log_path)

    def test_exactly_40_minutes_passes(self) -> None:
        result = self.validate(lesson([("ACT-B-01", 20, "core", "讲练"), ("ACT-M-01", 20, "core", "检测")]))
        self.assertEqual("通过", result.status)
        self.assertAlmostEqual(40, result.total_minutes)

    def test_core_over_40_fails(self) -> None:
        result = self.validate(lesson([("ACT-B-01", 20, "core", "讲练"), ("ACT-M-01", 21, "core", "检测")]))
        self.assertEqual("不通过", result.status)
        self.assertTrue(any("核心任务预计耗时" in error for error in result.errors))

    def test_flex_overflow_is_conditional(self) -> None:
        result = self.validate(lesson([("ACT-B-01", 34, "core", "讲练"), ("ACT-E-01", 8, "flex", "拓展")]))
        self.assertEqual("有条件通过", result.status)
        self.assertEqual(["ACT-E-01"], result.deferred)

    def test_rejects_overview_title_mismatch(self) -> None:
        text = lesson([("ACT-B-01", 5, "core", "讲练")]).replace("| 5分钟 |", "| 4分钟 |")
        result = self.validate(text)
        self.assertEqual("不通过", result.status)
        self.assertTrue(any("第一层时间" in error for error in result.errors))

    def test_rejects_missing_and_negative_budget(self) -> None:
        text = lesson([("ACT-B-01", 5, "core", "讲练")])
        text = text.replace("    feedback: 0.5\n", "").replace("    interaction: 0.5", "    interaction: -0.5")
        result = self.validate(text)
        self.assertEqual("不通过", result.status)
        self.assertTrue(any("缺少字段: feedback" in error for error in result.errors))
        self.assertTrue(any("不得为负数" in error for error in result.errors))

    def test_under_three_history_records_uses_profile(self) -> None:
        log = """| lesson_id | activity_id | activity_type | 计划耗时 | 实际耗时 | 是否完成 |
|---|---|---|---:|---:|---|
| a | A | 讲练 | 5 | 6 | 是 |
| b | B | 讲练 | 5 | 7 | 是 |
"""
        result = self.validate(lesson([("ACT-B-01", 5, "core", "讲练")]), log)
        self.assertIn("运行画像默认系数", result.activities[0].estimation_source)

    def test_three_history_records_use_median_ratio(self) -> None:
        log = """| lesson_id | activity_id | activity_type | 计划耗时 | 实际耗时 | 是否完成 |
|---|---|---|---:|---:|---|
| a | A | 讲练 | 5 | 6 | 是 |
| b | B | 讲练 | 5 | 7 | 是 |
| c | C | 讲练 | 5 | 8 | 是 |
"""
        result = self.validate(lesson([("ACT-B-01", 5, "core", "讲练")]), log)
        self.assertAlmostEqual(7, result.total_minutes)
        self.assertIn("历史中位数系数", result.activities[0].estimation_source)

    def test_backup_is_deferred_before_flex(self) -> None:
        result = self.validate(
            lesson([
                ("ACT-B-01", 34, "core", "核心"),
                ("ACT-M-01", 4, "flex", "弹性"),
                ("ACT-E-01", 4, "backup", "备用"),
            ])
        )
        self.assertEqual("有条件通过", result.status)
        self.assertEqual(["ACT-E-01"], result.deferred)

    def test_missing_profile_fails(self) -> None:
        self.lesson_path.write_text(lesson([("ACT-B-01", 5, "core", "讲练")]), encoding="utf-8")
        result = validate_timing(self.lesson_path, Path(self.temp_dir.name) / "missing.md", self.log_path)
        self.assertEqual("不通过", result.status)
        self.assertTrue(any("缺少教学运行画像" in error for error in result.errors))

    def test_rejects_non_half_minute_and_total_mismatch(self) -> None:
        text = lesson([("ACT-B-01", 5, "core", "讲练")])
        text = text.replace("    interaction: 0.5", "    interaction: 0.3")
        result = self.validate(text)
        self.assertEqual("不通过", result.status)
        self.assertTrue(any("必须使用0.5分钟精度" in error for error in result.errors))
        self.assertTrue(any("分项之和不一致" in error for error in result.errors))

    def test_progress_pressure_changes_same_priority_order(self) -> None:
        text = lesson([
            ("ACT-B-01", 36, "core", "核心"),
            ("ACT-E-01", 6, "backup", "大备用"),
            ("ACT-E-02", 3, "backup", "小备用"),
        ])
        tight = self.validate(text)
        self.assertEqual(["ACT-E-01"], tight.deferred)
        normal_profile = PROFILE.replace("progress_status: 紧张", "progress_status: 正常")
        self.profile_path.write_text(normal_profile, encoding="utf-8")
        normal = self.validate(text)
        self.assertEqual(["ACT-E-02", "ACT-E-01"], normal.deferred)

    def test_profile_layer_counts_must_match_class_size(self) -> None:
        self.profile_path.write_text(PROFILE.replace("advanced_students: 6", "advanced_students: 5"), encoding="utf-8")
        result = self.validate(lesson([("ACT-B-01", 5, "core", "讲练")]))
        self.assertEqual("不通过", result.status)
        self.assertTrue(any("分层人数之和" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
