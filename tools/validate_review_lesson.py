#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate review-lesson handouts for the MRE workflow."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Ensure the project root is importable when this script runs directly.
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from tools.review_math_utils import validate_math_markup


REQUIRED_SECTIONS = [
    "例题讲解",
    "当堂练习",
    "课后作业",
    "原始数量与选用数量对比",
]
VALID_DIFFICULTIES = {"★", "★★", "★★★", "★★★★", "★★★★★"}
REQUIRED_HOMEWORK_COUNT = 10


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_yaml_frontmatter(text: str) -> list[str]:
    errors = []
    if not text.startswith("---"):
        errors.append("缺少 YAML 前置元数据（以 --- 开头）")
        return errors
    end = text.find("---", 3)
    if end == -1:
        errors.append("YAML 前置元数据未闭合（缺少结尾 ---）")
        return errors
    frontmatter = text[3:end]
    required = ["content_type", "lesson_id", "lesson_name", "command", "workflow_version", "source_files", "created_at"]
    for key in required:
        if key not in frontmatter:
            errors.append(f"YAML 缺少必填字段: {key}")
    if "homework_count" in frontmatter:
        m = re.search(r"homework_count:\s*(\d+)", frontmatter)
        if m and int(m.group(1)) != REQUIRED_HOMEWORK_COUNT:
            errors.append(f"homework_count 应为 {REQUIRED_HOMEWORK_COUNT}，实际为 {m.group(1)}")
    return errors


def check_required_sections(text: str) -> list[str]:
    errors = []
    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in text:
            errors.append(f"缺少必要章节: ## {section}")
    return errors


def check_question_numbering(text: str) -> list[str]:
    errors = []
    # 提取所有题号（阿拉伯数字 + 全角句号格式）
    pattern = re.compile(r"^(\d+)．", re.MULTILINE)
    numbers = [int(m.group(1)) for m in pattern.finditer(text)]
    if not numbers:
        errors.append("未找到任何题号（格式：数字 + 全角句号）")
        return errors
    # 检查连续编号
    for i, num in enumerate(numbers):
        expected = i + 1
        if num != expected:
            errors.append(f"题号不连续：期望第 {expected} 题为 {expected}．，实际为 {num}．")
            break
    return errors


def check_image_paths(text: str, md_path: Path) -> list[str]:
    errors = []
    images_dir = md_path.parent / "images"
    pattern = re.compile(r"!\[\]\((images/[^)]+)\)")
    for m in pattern.finditer(text):
        rel_path = m.group(1)
        img_path = md_path.parent / rel_path
        if not img_path.exists():
            errors.append(f"图片文件不存在: {rel_path}")
    return errors


def check_homework_count(text: str) -> list[str]:
    errors = []
    # 在课后作业章节中统计题号
    homework_match = re.search(r"## 课后作业\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not homework_match:
        errors.append("无法定位课后作业章节")
        return errors
    homework_section = homework_match.group(1)
    count = len(re.findall(r"^\d+．", homework_section, re.MULTILINE))
    if count != REQUIRED_HOMEWORK_COUNT:
        errors.append(f"课后作业数量应为 {REQUIRED_HOMEWORK_COUNT}，实际为 {count}")
    return errors


def check_comparison_table(text: str) -> list[str]:
    errors = []
    table_match = re.search(r"## 原始数量与选用数量对比\n(.*?)(?=\Z)", text, re.DOTALL)
    if not table_match:
        errors.append("缺少原始数量与选用数量对比表")
        return errors
    table_content = table_match.group(1)
    # 检查表格行
    rows = re.findall(r"^\|.*\|$", table_content, re.MULTILINE)
    if len(rows) < 4:  # 表头 + 分隔 + 至少1行数据 + 合计
        errors.append("对比表行数不足")
    # 检查是否有合计行
    if "合计" not in table_content:
        errors.append("对比表缺少合计行")
    return errors


def check_math_markup(text: str) -> list[str]:
    errors = []
    # 检查 $$ 块级公式（不应使用）
    if "$$" in text:
        errors.append("不应使用 $$ 块级公式，请统一使用 $...$ 行内公式")
    # 检查未闭合的 $
    dollars = text.count("$")
    if dollars % 2 != 0:
        errors.append("$ 符号数量为奇数，可能存在未闭合的公式")
    return errors


def validate(path: str | Path) -> list[str]:
    md_path = Path(path).expanduser().resolve()
    if not md_path.exists():
        return [f"文件不存在: {md_path}"]

    text = read_text(md_path)
    all_errors: list[str] = []
    all_errors.extend(check_yaml_frontmatter(text))
    all_errors.extend(check_required_sections(text))
    all_errors.extend(check_question_numbering(text))
    all_errors.extend(check_image_paths(text, md_path))
    all_errors.extend(check_homework_count(text))
    all_errors.extend(check_comparison_table(text))
    all_errors.extend(check_math_markup(text))
    all_errors.extend(validate_math_markup(text))
    question_lines = re.findall(r"(?m)^\s*(\d+)．(.*)$", text)
    question_count = len(question_lines)
    if question_count and not (18 <= question_count <= 30):
        all_errors.append(f"question count out of range: {question_count}")
    for number, stem in question_lines:
        if not stem.strip():
            all_errors.append(f"question {number} has empty stem")
    frontmatter = text[3:text.find("---", 3)] if text.startswith("---") and text.find("---", 3) != -1 else ""
    if re.search(r"(?m)^review_status\s*:", frontmatter):
        all_errors.append("review_lesson must not set review_status")
    for image_path in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        normalized = image_path.strip().replace("\\", "/")
        if normalized.startswith("images/") and not (md_path.parent / normalized).exists():
            all_errors.append(f"image file does not exist: {normalized}")
    return all_errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate review-lesson handout")
    parser.add_argument("input", help="Path to review lesson Markdown file")
    args = parser.parse_args()

    md_path = Path(args.input).expanduser().resolve()
    if not md_path.exists():
        print(f"错误：文件不存在: {md_path}", file=sys.stderr)
        return 1

    all_errors = validate(md_path)

    if all_errors:
        print(f"验证失败 ({len(all_errors)} 个错误):")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("验证通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
