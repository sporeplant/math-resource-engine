#!/usr/bin/env python3
"""Validate whether lesson activities can be completed within 40 minutes."""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path


TIME_PARTS = ("instruction", "student_work", "interaction", "feedback", "transition")
VALID_PRIORITIES = {"core", "flex", "backup"}
HARD_LIMIT = 40.0
RISK_THRESHOLD = 37.0
EPSILON = 1e-6


@dataclass
class Activity:
    activity_id: str
    title: str
    title_minutes: float
    activity_type: str = ""
    priority: str = ""
    budget: dict[str, float] = field(default_factory=dict)
    estimated_minutes: float = 0.0
    estimation_source: str = ""


@dataclass
class RuntimeProfile:
    progress_status: str
    factors: dict[str, float]
    class_size: int
    basic_students: int
    intermediate_students: int
    advanced_students: int


@dataclass
class TimingResult:
    status: str
    activities: list[Activity]
    core_minutes: float
    total_minutes: float
    remaining_minutes: float
    deferred: list[str]
    risk_activities: list[str]
    errors: list[str]
    warnings: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_scalar(value: str) -> str | float:
    cleaned = value.strip().strip('"').strip("'")
    try:
        return float(cleaned)
    except ValueError:
        return cleaned


def parse_profile(path: Path) -> RuntimeProfile:
    text = read_text(path)
    required_scalar_fields = [
        "current_week",
        "completed_regular_lessons",
        "remaining_regular_lessons",
        "progress_status",
        "class_size",
        "basic_students",
        "intermediate_students",
        "advanced_students",
        "low_interaction_students",
    ]
    scalar_values: dict[str, str] = {}
    for key in required_scalar_fields:
        match = re.search(rf"(?m)^{key}\s*:\s*(\S+)\s*$", text)
        if not match:
            raise ValueError(f"运行画像缺少字段: {key}")
        scalar_values[key] = match.group(1)
    progress_status = scalar_values["progress_status"]
    factors: dict[str, float] = {}
    block_match = re.search(
        r"(?m)^timing_factors\s*:\s*$([\s\S]*?)(?=^[A-Za-z_][\w-]*\s*:|^---\s*$|\Z)",
        text,
    )
    if block_match:
        for key, value in re.findall(r"(?m)^\s{2}([a-z_]+)\s*:\s*([0-9.]+)\s*$", block_match.group(1)):
            factors[key] = float(value)
    missing = [part for part in TIME_PARTS if part not in factors]
    if missing:
        raise ValueError(f"运行画像缺少耗时系数: {', '.join(missing)}")
    if any(value <= 0 for value in factors.values()):
        raise ValueError("运行画像耗时系数必须大于0")
    try:
        class_size = int(scalar_values["class_size"])
        basic_students = int(scalar_values["basic_students"])
        intermediate_students = int(scalar_values["intermediate_students"])
        advanced_students = int(scalar_values["advanced_students"])
        low_interaction_students = int(scalar_values["low_interaction_students"])
        current_week = int(scalar_values["current_week"])
        completed = int(scalar_values["completed_regular_lessons"])
        remaining = int(scalar_values["remaining_regular_lessons"])
    except ValueError as exc:
        raise ValueError("运行画像中的周次、课时数和学生人数必须为整数") from exc
    if min(class_size, basic_students, intermediate_students, advanced_students, low_interaction_students, current_week, completed, remaining) < 0:
        raise ValueError("运行画像中的周次、课时数和学生人数不得为负数")
    if basic_students + intermediate_students + advanced_students != class_size:
        raise ValueError("运行画像分层人数之和必须等于班级总人数")
    if low_interaction_students > class_size:
        raise ValueError("低互动学生人数不得超过班级总人数")
    return RuntimeProfile(
        progress_status=progress_status,
        factors=factors,
        class_size=class_size,
        basic_students=basic_students,
        intermediate_students=intermediate_students,
        advanced_students=advanced_students,
    )


def parse_history(path: Path | None) -> dict[str, list[float]]:
    ratios: dict[str, list[float]] = {}
    if path is None or not path.exists():
        return ratios
    for line in read_text(path).splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] in {"lesson_id", "---"} or set(cells[0]) == {"-"}:
            continue
        activity_type = cells[2]
        try:
            planned = float(cells[3])
            actual = float(cells[4])
        except ValueError:
            continue
        completed = cells[5].lower()
        if not activity_type or planned <= 0 or actual < 0 or completed not in {"是", "yes", "true", "完成"}:
            continue
        ratios.setdefault(activity_type, []).append(actual / planned)
    return ratios


def structured_layer(text: str) -> str:
    match = re.search(r"<details>[\s\S]*?<summary>[\s\S]*?</summary>([\s\S]*?)</details>", text)
    return match.group(1) if match else text


def parse_overview_minutes(text: str) -> list[float]:
    body = text.split("<details>", 1)[0]
    match = re.search(r"(?m)^###\s*[0-9.]+分钟流程总览\s*$([\s\S]*?)(?=^###\s|\Z)", body)
    if not match:
        return []
    return [float(value) for value in re.findall(r"(?m)^\|\s*([0-9]+(?:\.5)?)\s*分钟\s*\|", match.group(1))]


def parse_activities(text: str) -> list[Activity]:
    layer = structured_layer(text)
    headings = list(
        re.finditer(
            r"(?m)^###\s+(ACT-[A-Z]+-\d{2})\s+(.+?)（\s*([0-9]+(?:\.5)?)\s*分钟\s*）\s*$",
            layer,
        )
    )
    activities: list[Activity] = []
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(layer)
        block = layer[match.end():end]
        activity = Activity(match.group(1), match.group(2).strip(), float(match.group(3)))
        type_match = re.search(r"(?m)^-\s*activity_type\s*:\s*(.+?)\s*$", block)
        priority_match = re.search(r"(?m)^-\s*time_priority\s*:\s*(\S+)\s*$", block)
        budget_match = re.search(
            r"(?m)^-\s*time_budget\s*:\s*$([\s\S]*?)(?=^\S|^\s*-\s*[A-Za-z_\u4e00-\u9fff]+\s*:|\Z)",
            block,
        )
        activity.activity_type = type_match.group(1).strip() if type_match else ""
        activity.priority = priority_match.group(1).strip() if priority_match else ""
        if budget_match:
            for key, value in re.findall(
                r"(?m)^\s{2,}([a-z_]+)\s*:\s*(-?[0-9]+(?:\.[0-9]+)?)\s*$", budget_match.group(1)
            ):
                activity.budget[key] = float(value)
        activities.append(activity)
    return activities


def is_half_minute(value: float) -> bool:
    return abs(value * 2 - round(value * 2)) < EPSILON


def validate_timing(
    lesson_path: Path,
    runtime_profile: Path,
    timing_log: Path | None,
) -> TimingResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not runtime_profile.exists():
        return TimingResult("不通过", [], 0, 0, HARD_LIMIT, [], [], [f"缺少教学运行画像: {runtime_profile}"], [])

    try:
        profile = parse_profile(runtime_profile)
    except (OSError, ValueError) as exc:
        return TimingResult("不通过", [], 0, 0, HARD_LIMIT, [], [], [str(exc)], [])

    text = read_text(lesson_path)
    activities = parse_activities(text)
    overview = parse_overview_minutes(text)
    if not activities:
        errors.append("未找到带分钟标记的 ACT 活动")
    if not overview:
        errors.append("第一层流程总览缺少活动时间")
    elif len(overview) != len(activities):
        errors.append(f"双层活动数量不一致: 第一层{len(overview)}项，第二层{len(activities)}项")

    history = parse_history(timing_log)
    if timing_log is None or not timing_log.exists():
        warnings.append("缺少课堂活动耗时日志，使用运行画像默认系数")

    for index, activity in enumerate(activities):
        prefix = activity.activity_id
        if index < len(overview) and abs(overview[index] - activity.title_minutes) > EPSILON:
            errors.append(
                f"{prefix} 第一层时间{overview[index]:g}分钟与活动标题{activity.title_minutes:g}分钟不一致"
            )
        if activity.priority not in VALID_PRIORITIES:
            errors.append(f"{prefix} 缺少合法 time_priority: core | flex | backup")
        if not activity.activity_type:
            errors.append(f"{prefix} 缺少 activity_type")
        required_budget_parts = (*TIME_PARTS, "total")
        missing = [part for part in required_budget_parts if part not in activity.budget]
        if missing:
            errors.append(f"{prefix} time_budget 缺少字段: {', '.join(missing)}")
        for part, value in activity.budget.items():
            if value < 0:
                errors.append(f"{prefix} {part} 不得为负数")
            if not is_half_minute(value):
                errors.append(f"{prefix} {part} 必须使用0.5分钟精度")
        if missing:
            continue
        parts_total = sum(activity.budget[part] for part in TIME_PARTS)
        declared_total = activity.budget["total"]
        if abs(parts_total - declared_total) > EPSILON:
            errors.append(f"{prefix} time_budget.total 与分项之和不一致: {declared_total:g} != {parts_total:g}")
        if abs(declared_total - activity.title_minutes) > EPSILON:
            errors.append(
                f"{prefix} time_budget.total 与活动标题时间不一致: {declared_total:g} != {activity.title_minutes:g}"
            )

        samples = history.get(activity.activity_type, [])
        if len(samples) >= 3:
            ratio = statistics.median(samples)
            activity.estimated_minutes = declared_total * ratio
            activity.estimation_source = f"历史中位数系数 {ratio:.2f}（{len(samples)}条）"
        else:
            activity.estimated_minutes = sum(
                activity.budget[part] * profile.factors[part] for part in TIME_PARTS
            )
            activity.estimation_source = "运行画像默认系数"
            warnings.append(
                f"{prefix} 同类活动实测记录不足3条（当前{len(samples)}条），使用默认系数"
            )

    core_minutes = sum(a.estimated_minutes for a in activities if a.priority == "core" and a.budget)
    total_minutes = sum(a.estimated_minutes for a in activities if a.budget)
    deferred: list[str] = []
    status = "通过"
    if errors or core_minutes > HARD_LIMIT + EPSILON:
        status = "不通过"
        if core_minutes > HARD_LIMIT + EPSILON:
            errors.append(f"核心任务预计耗时{core_minutes:.1f}分钟，超过40分钟")
    elif total_minutes > HARD_LIMIT + EPSILON:
        status = "有条件通过"
        removable = [a for a in activities if a.priority in {"backup", "flex"}]
        progress_rank = {"正常": {"backup": 0, "flex": 1}, "紧张": {"backup": 0, "flex": 1}, "严重滞后": {"backup": 0, "flex": 1}}
        rank = progress_rank.get(profile.progress_status, progress_rank["正常"])
        activity_order = {activity.activity_id: index for index, activity in enumerate(activities)}
        if profile.progress_status == "正常":
            removable.sort(key=lambda a: (rank[a.priority], -activity_order[a.activity_id]))
        else:
            removable.sort(key=lambda a: (rank[a.priority], -a.estimated_minutes, -activity_order[a.activity_id]))
        kept = total_minutes
        for activity in removable:
            if kept <= HARD_LIMIT + EPSILON:
                break
            deferred.append(activity.activity_id)
            kept -= activity.estimated_minutes
        if kept > HARD_LIMIT + EPSILON:
            status = "不通过"
            errors.append("后移全部弹性与备用任务后仍无法在40分钟内完成")
        else:
            warnings.append("全部计划任务预计超时，需后移: " + ", ".join(deferred))

    if status != "不通过" and total_minutes > RISK_THRESHOLD + EPSILON:
        warnings.append(f"预计总耗时{total_minutes:.1f}分钟，处于37至40分钟高风险区或以上")

    risk_activities = [
        activity.activity_id
        for activity in activities
        if activity.estimated_minutes > activity.title_minutes + EPSILON
    ]

    return TimingResult(
        status=status,
        activities=activities,
        core_minutes=core_minutes,
        total_minutes=total_minutes,
        remaining_minutes=HARD_LIMIT - total_minutes,
        deferred=deferred,
        risk_activities=risk_activities,
        errors=errors,
        warnings=warnings,
    )


def format_result(result: TimingResult) -> str:
    lines = ["教学活动时间验证结果", ""]
    for activity in result.activities:
        lines.append(
            f"- {activity.activity_id} {activity.title}: 计划{activity.title_minutes:g}分钟，"
            f"预计{activity.estimated_minutes:.1f}分钟，{activity.priority or '未标记'}，{activity.estimation_source or '未估算'}"
        )
    lines.extend(
        [
            "",
            f"核心任务预计耗时: {result.core_minutes:.1f}分钟",
            f"全部任务预计耗时: {result.total_minutes:.1f}分钟",
            f"相对40分钟余量: {result.remaining_minutes:.1f}分钟",
        ]
    )
    if result.deferred:
        lines.append("建议后移任务: " + ", ".join(result.deferred))
    if result.risk_activities:
        lines.append("风险活动: " + ", ".join(result.risk_activities))
    if result.warnings:
        lines.append("警告:")
        lines.extend(f"- {warning}" for warning in result.warnings)
    if result.errors:
        lines.append("错误:")
        lines.extend(f"- {error}" for error in result.errors)
    lines.append(f"最终结论: {result.status}")
    return "\n".join(lines)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    parser = argparse.ArgumentParser(description="验证教学活动能否在40分钟内完成")
    parser.add_argument("lesson", type=Path)
    parser.add_argument("--runtime-profile", type=Path, required=True)
    parser.add_argument("--timing-log", type=Path)
    args = parser.parse_args()
    result = validate_timing(args.lesson, args.runtime_profile, args.timing_log)
    print(format_result(result))
    return 1 if result.status == "不通过" else 0


if __name__ == "__main__":
    sys.exit(main())
