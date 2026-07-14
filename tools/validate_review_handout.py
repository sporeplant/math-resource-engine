#!/usr/bin/env python3
"""Validate review handout Markdown outputs."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from review_math_utils import validate_math_markup
except ModuleNotFoundError:
    from tools.review_math_utils import validate_math_markup


EXPECTED_OUTPUT_PARTS = ("outputs", "八下复习讲义")
REQUIRED_META = {
    "content_type": "review_lesson",
    "command": "复习讲义",
}
FORBIDDEN_PHRASES = [
    "合并知识点",
    "整合为5个知识点",
    "整合为 5 个知识点",
    "压缩为5个知识点",
    "压缩为 5 个知识点",
    "合并为5个左右知识点",
    "合并为 5 个左右知识点",
]


@dataclass
class ValidationResult:
    status: str
    errors: list[str]
    warnings: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_front_matter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 4 :].lstrip()


def parse_front_matter(block: str) -> dict[str, str | list[str]]:
    meta: dict[str, str | list[str]] = {}
    current_key: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if current_key and line.lstrip().startswith("-"):
            item = line.lstrip()[1:].strip().strip('"').strip("'")
            value = meta.setdefault(current_key, [])
            if isinstance(value, list):
                value.append(item)
            continue
        current_key = None
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            meta[key] = value.strip('"').strip("'")
        else:
            meta[key] = []
            current_key = key
    return meta


def is_under_expected_output(path: Path) -> bool:
    normalized = [part.lower() for part in path.resolve().parts]
    expected = [part.lower() for part in EXPECTED_OUTPUT_PARTS]
    for index in range(0, len(normalized) - len(expected) + 1):
        if normalized[index : index + len(expected)] == expected:
            return True
    return False


def extract_numbered_questions(body: str) -> list[int]:
    numbers: list[int] = []
    for match in re.finditer(r"(?m)^\s*(\d+)．", body):
        numbers.append(int(match.group(1)))
    return numbers


def check_question_sequence(numbers: list[int], errors: list[str]) -> None:
    if not numbers:
        errors.append("未找到正文题号（形如 1．、2．）")
        return
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        errors.append(f"正文题号不连续或重置：实际 {numbers[:30]}，期望从 1 连续到 {len(numbers)}")


def extract_info_table(body: str) -> tuple[list[str], list[list[str]]]:
    heading = re.search(r"(?m)^##\s+题目信息总览(?:表格)?\s*$", body)
    if not heading:
        return [], []
    section = body[heading.end() :]
    next_heading = re.search(r"(?m)^##\s+", section)
    if next_heading:
        section = section[: next_heading.start()]
    table_lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return [], []
    header = split_table_row(table_lines[0])
    rows: list[list[str]] = []
    for line in table_lines[2:]:
        cells = split_table_row(line)
        if cells:
            rows.append(cells)
    return header, rows


def extract_comparison_table(body: str) -> tuple[list[str], list[list[str]]]:
    heading = re.search(r"(?m)^##\s+原始数量与选用数量对比\s*$", body)
    if not heading:
        return [], []
    section = body[heading.end() :]
    next_heading = re.search(r"(?m)^##\s+", section)
    if next_heading:
        section = section[: next_heading.start()]
    table_lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return [], []
    header = split_table_row(table_lines[0])
    rows = [split_table_row(line) for line in table_lines[2:] if split_table_row(line)]
    return header, rows


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def check_info_table(body: str, question_count: int, errors: list[str], warnings: list[str]) -> list[list[str]]:
    header, rows = extract_info_table(body)
    if not header:
        return []
    required = ["题目ID", "知识考察点", "难度", "入选理由"]
    missing = [name for name in required if name not in header]
    if missing:
        errors.append(f"题目信息总览缺少列：{', '.join(missing)}")
    if len(rows) < question_count:
        warnings.append(f"题目信息总览题目数少于正文题目数：表格 {len(rows)}，正文 {question_count}")
    return rows


def check_comparison_table(body: str, errors: list[str]) -> None:
    header, rows = extract_comparison_table(body)
    if not header:
        errors.append("缺少题目信息总览表格或原始数量与选用数量对比表格")
        return
    required = ["来源", "类别", "原始数量", "选用数量", "备注"]
    missing = [name for name in required if name not in header]
    if missing:
        errors.append(f"原始数量与选用数量对比表缺少列：{', '.join(missing)}")
    if not rows:
        errors.append("原始数量与选用数量对比表没有数据行")
        return
    if not any(row and row[0].strip("*") == "合计" for row in rows):
        errors.append("原始数量与选用数量对比表缺少合计行")


def source_prefix_from_file(source_file: str) -> str | None:
    name = Path(source_file).stem
    if not name:
        return None
    if re.fullmatch(r"\d{2}", name):
        return f"{name}讲"
    if re.fullmatch(r"\d{2}讲", name):
        return name
    match = re.match(r"(\d{2})", name)
    if match:
        return f"{match.group(1)}讲"
    return name


def check_source_balance(
    rows: list[list[str]],
    source_files: list[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    prefixes = [prefix for prefix in (source_prefix_from_file(item) for item in source_files) if prefix]
    if len(prefixes) < 2 or not rows:
        return
    counts = {prefix: 0 for prefix in prefixes}
    unknown_ids: list[str] = []
    for row in rows:
        if not row:
            continue
        question_id = row[0]
        matched = False
        for prefix in prefixes:
            if question_id.startswith(prefix) or question_id.startswith(prefix.replace("讲", "")):
                counts[prefix] += 1
                matched = True
                break
        if not matched:
            unknown_ids.append(question_id)
    if unknown_ids:
        warnings.append(f"存在无法匹配来源讲义的题目ID：{', '.join(unknown_ids[:10])}")
    values = list(counts.values())
    if len(values) >= 2:
        diff = max(values) - min(values)
        detail = ", ".join(f"{key}: {value}" for key, value in counts.items())
        if diff > 4:
            errors.append(f"来源题量严重失衡（差距 {diff}）：{detail}")
        elif diff > 2:
            warnings.append(f"来源题量不够均衡（差距 {diff}）：{detail}")


def extract_markdown_images(body: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body)


def check_images(path: Path, body: str, errors: list[str], warnings: list[str]) -> None:
    for image_path in extract_markdown_images(body):
        cleaned = image_path.strip()
        if not cleaned:
            errors.append("存在空图片路径")
            continue
        normalized = cleaned.replace("\\", "/")
        if re.match(r"^[A-Za-z]:/", normalized) or normalized.startswith("/") or normalized.startswith("../"):
            errors.append(f"图片路径不得使用绝对路径或跨目录路径：{cleaned}")
            continue
        if not normalized.startswith("images/"):
            errors.append(f"图片路径必须指向同级 images/ 目录：{cleaned}")
            continue
        target = path.parent / normalized
        if not target.exists():
            warnings.append(f"图片文件不存在：{normalized}")


def check_forbidden_phrases(body: str, errors: list[str]) -> None:
    for phrase in FORBIDDEN_PHRASES:
        if phrase in body:
            errors.append(f"出现禁用表述：{phrase}")


def check_math(body: str, errors: list[str]) -> None:
    errors.extend(validate_math_markup(body))


def validate(path: Path) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return ValidationResult("不通过", [f"文件不存在：{path}"], [])
    text = read_text(path)
    front_matter, body = split_front_matter(text)
    if not front_matter:
        errors.append("缺少 YAML front matter")
        meta: dict[str, str | list[str]] = {}
    else:
        meta = parse_front_matter(front_matter)

    if not is_under_expected_output(path):
        errors.append("outputs路径必须位于 outputs/reviews/")

    for key, expected in REQUIRED_META.items():
        actual = meta.get(key)
        if actual != expected:
            errors.append(f"YAML 字段 {key} 应为 {expected}，实际为 {actual or '缺失'}")

    source_files_value = meta.get("source_files", [])
    source_files = source_files_value if isinstance(source_files_value, list) else []
    if len(source_files) < 2:
        errors.append("source_files 至少需要登记 2 个来源讲义文件")

    numbers = extract_numbered_questions(body)
    check_question_sequence(numbers, errors)
    rows = check_info_table(body, len(numbers), errors, warnings)
    if rows:
        check_source_balance(rows, source_files, errors, warnings)
    else:
        check_comparison_table(body, errors)
    check_images(path, body, errors, warnings)
    check_forbidden_phrases(body, errors)
    check_math(body, errors)

    status = "不通过" if errors else "有条件通过" if warnings else "通过"
    return ValidationResult(status, errors, warnings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a review handout Markdown file.")
    parser.add_argument("handout", type=Path, help="Path to the generated review handout Markdown file.")
    args = parser.parse_args(argv)

    result = validate(args.handout)
    print(f"验证结果：{result.status}")
    if result.errors:
        print("\n错误：")
        for item in result.errors:
            print(f"- {item}")
    if result.warnings:
        print("\n警告：")
        for item in result.warnings:
            print(f"- {item}")
    return 1 if result.status == "不通过" else 0


if __name__ == "__main__":
    sys.exit(main())
