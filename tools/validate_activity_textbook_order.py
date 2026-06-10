#!/usr/bin/env python3
"""Validate that teaching activities follow textbook section order (excluding practice/exercises)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


EXCLUDED_SECTION_PATTERNS = [
    re.compile(r"^练习", re.IGNORECASE),
    re.compile(r"^习题", re.IGNORECASE),
    re.compile(r"^A\s*组", re.IGNORECASE),
    re.compile(r"^B\s*组", re.IGNORECASE),
    re.compile(r"^C\s*组", re.IGNORECASE),
    re.compile(r"^小结", re.IGNORECASE),
    re.compile(r"^复习", re.IGNORECASE),
    re.compile(r"^数学活动", re.IGNORECASE),
    re.compile(r"^第[一二三四五六七八九十\d]+章", re.IGNORECASE),
    re.compile(r"^\d+\.\d+"),
    re.compile(r"^知识结构", re.IGNORECASE),
    re.compile(r"^总结与反思", re.IGNORECASE),
    re.compile(r"^注意事项", re.IGNORECASE),
    re.compile(r"[。.]$"),
    re.compile(r"^\(\d+\)"),
]

KNOWN_MODULE_NAMES = {
    "观察与思考", "做一做", "大家谈谈", "一起探究",
    "观察与猜想", "实验与探究", "阅读与思考", "数学活动",
}

CHAPTER_HEADING_PATTERNS = [
    re.compile(r"^第[一二三四五六七八九十]+章"),
    re.compile(r"^\d+\.\d+"),
    re.compile(r"^[一二三四五六七八九十]、"),
    re.compile(r"第\d+课时|第[一二三四五六七八九十]课时"),
    re.compile(r"^数据的收集|^数据的整理|^统计的初步|^频数分布|^数据变化趋势"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_textbook_sections(text: str) -> list[str]:
    """Extract ordered textbook anchors, including正文 steps and section headers."""
    sections: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if "阶梯电价" in stripped and "正文开头" not in sections:
            sections.append("正文开头")

        step_match = re.match(r"^(?:#{1,2}\s*)?\((\d+)\)\s*(.+)", stripped)
        if step_match:
            title = step_match.group(2).strip().rstrip("。. ")
            sections.append(f"步骤({step_match.group(1)}) {title}")
            continue

        match = re.match(r"^#{1,2}\s+(.+)", line)
        if not match:
            continue
        title = match.group(1).strip()

        if any(pat.search(title) for pat in EXCLUDED_SECTION_PATTERNS):
            continue

        if any(pat.search(title) for pat in CHAPTER_HEADING_PATTERNS):
            continue

        sections.append(title)
    return sections


class ActivityInfo(NamedTuple):
    activity_id: str
    name: str
    textbook_position: str
    line_number: int


def extract_activities(text: str) -> list[ActivityInfo]:
    """Extract activities and their textbook positions from lesson design."""
    activities: list[ActivityInfo] = []
    activity_pattern = re.compile(
        r"^###\s+(ACT-[BME]-\d+)(?:[：:]\s*|\s+)(.+)",
        re.MULTILINE,
    )
    position_pattern = re.compile(r"^\s*-?\s*教材对应位置[：:]\s*(.+)", re.MULTILINE)

    matches = list(activity_pattern.finditer(text))
    for match in matches:
        activity_id = match.group(1).strip()
        activity_name = match.group(2).strip()
        start_pos = match.start()
        line_number = text[:start_pos].count("\n") + 1

        next_activity_match = activity_pattern.search(text, match.end())
        end_pos = next_activity_match.start() if next_activity_match else len(text)

        activity_block = text[match.start():end_pos]
        pos_match = position_pattern.search(activity_block)
        textbook_position = pos_match.group(1).strip() if pos_match else ""

        activities.append(ActivityInfo(activity_id, activity_name, textbook_position, line_number))

    return activities


def build_position_index(sections: list[str]) -> dict[str, int]:
    """Build a mapping from section name to its 1-based index."""
    return {name: i + 1 for i, name in enumerate(sections)}


def find_section_match(position_value: str, sections: list[str]) -> int | None:
    """Find which textbook section index a position value maps to."""
    position_value = position_value.strip()
    if position_value == "非教材原文" or position_value == "全课整理":
        return None
    if position_value.startswith("练习") or position_value.startswith("A组") or position_value.startswith("B组"):
        return None

    def normalize(value: str) -> str:
        value = re.sub(r"\s+", "", value)
        value = re.sub(r"[，,。.．:：；;、]", "", value)
        return value.replace("数据分组的", "")

    for i, section in enumerate(sections):
        if section in position_value or position_value in section:
            return i + 1
        if normalize(section) in normalize(position_value) or normalize(position_value) in normalize(section):
            return i + 1

    for i, section in enumerate(sections):
        if any(char in section for char in position_value if len(char) >= 2):
            return i + 1

    return None


def should_warn_unmatched_position(position_value: str) -> bool:
    position_value = position_value.strip()
    if position_value in {"非教材原文", "全课整理"}:
        return False
    if position_value.startswith(("练习", "A组", "B组", "C组")):
        return False
    return True


def validate_order(
    activities: list[ActivityInfo],
    sections: list[str],
) -> tuple[list[str], list[str]]:
    """Validate activity order follows textbook section order.

    Returns (errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []

    position_index = build_position_index(sections)

    textbook_activities: list[tuple[int, ActivityInfo]] = []
    missing_position: list[ActivityInfo] = []

    for act in activities:
        if not act.textbook_position:
            missing_position.append(act)
            continue

        section_idx = find_section_match(act.textbook_position, sections)
        if section_idx is None:
            if should_warn_unmatched_position(act.textbook_position):
                warnings.append(
                    f"活动 {act.activity_id} 的教材对应位置 '{act.textbook_position}' "
                    f"在教材原文中未找到匹配的正文锚点"
                )
            continue

        textbook_activities.append((section_idx, act))

    if missing_position:
        act_ids = [a.activity_id for a in missing_position]
        errors.append(f"以下活动缺少 '教材对应位置' 字段: {', '.join(act_ids)}")

    if not textbook_activities:
        if not missing_position:
            warnings.append("未找到与教材原文正文关联的活动，无法验证顺序")
        return errors, warnings

    order_errors: list[str] = []
    for i in range(len(textbook_activities) - 1):
        curr_idx, curr_act = textbook_activities[i]
        next_idx, next_act = textbook_activities[i + 1]

        if curr_idx > next_idx:
            curr_section = sections[curr_idx - 1] if curr_idx <= len(sections) else "?"
            next_section = sections[next_idx - 1] if next_idx <= len(sections) else "?"
            order_errors.append(
                f"活动顺序倒置: {curr_act.activity_id} (对应'{curr_section}', 教材第{curr_idx}模块) "
                f"排在 {next_act.activity_id} (对应'{next_section}', 教材第{next_idx}模块) 之前，"
                f"但教材中'{curr_section}'出现在'{next_section}'之后"
            )

    errors.extend(order_errors)

    return errors, warnings


def validate(
    lesson_path: Path,
    textbook_path: Path,
) -> tuple[list[str], list[str]]:
    """Main validation entry point.

    Returns (errors, warnings).
    """
    if not lesson_path.exists():
        return [f"教学设计文件不存在: {lesson_path}"], []
    if not textbook_path.exists():
        return [f"教材原文文件不存在: {textbook_path}"], []

    lesson_text = read_text(lesson_path)
    textbook_text = read_text(textbook_path)

    sections = extract_textbook_sections(textbook_text)
    if not sections:
        return [], ["教材原文中未找到##级标题（可能全部被排除或格式不正确）"]

    activities = extract_activities(lesson_text)
    if not activities:
        return [], ["教学设计中未找到活动定义（### ACT-...）"]

    return validate_order(activities, sections)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(
        description="验证教学活动是否遵循教材原文文本的先后顺序"
    )
    parser.add_argument("lesson_file", type=Path, help="教学设计文件路径")
    parser.add_argument("textbook_file", type=Path, help="教材原文文件路径")
    args = parser.parse_args()

    errors, warnings = validate(args.lesson_file, args.textbook_file)

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  ⚠️  {w}")
        print()

    if errors:
        print("教材顺序验证 FAILED:")
        for e in errors:
            print(f"  ❌ {e}")
        return 1

    print("✅ 教材顺序验证 PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
