#!/usr/bin/env python3
"""Validate workbook per-question index YAML files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKBOOK_DIR = REPO_ROOT / "knowledge" / "workbooks"
ANSWER_DIR = REPO_ROOT / "knowledge" / "workbook-answers"
FILENAME_RE = re.compile(r"^workbook-index-(?:\d+\.\d+(?:-\d+)?|ch\d+-(?:review|unit-test)|midterm)\.yaml$")
QUESTION_ID_RE = re.compile(r"\bquestion_id:\s*([A-Za-z0-9_.-]+)")


def iter_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(path for path in target.glob("workbook-index-*.yaml") if path.is_file())
    raise FileNotFoundError(f"目标不存在: {target}")


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, text[end + 4 :]


def numeric_fields(text: str, field: str) -> list[int]:
    return [int(value) for value in re.findall(rf"\b{re.escape(field)}:\s*(\d+)", text)]


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)

    if not FILENAME_RE.match(path.name):
        errors.append(f"文件名不符合规则: {path.name}")

    if meta.get("content_type") != "workbook_index":
        errors.append("content_type 不是 workbook_index")
    if meta.get("source_type") != "exercise_bank":
        errors.append("source_type 不是 exercise_bank")

    source_id = meta.get("source_id", "")
    answer_id = meta.get("answer_id", "")
    expected_index_id = path.stem
    if meta.get("index_id") != expected_index_id:
        errors.append("index_id 与文件名不一致")
    if not source_id.startswith("workbook-"):
        errors.append("source_id 不符合 workbook-* 规则")
    if not answer_id.startswith("workbook-answer-"):
        errors.append("answer_id 不符合 workbook-answer-* 规则")

    workbook_path = WORKBOOK_DIR / f"{source_id}.md"
    answer_path = ANSWER_DIR / f"{answer_id}.md"
    if not workbook_path.is_file():
        errors.append(f"缺少题库源文件: {workbook_path}")
    if not answer_path.is_file():
        errors.append(f"缺少答案源文件: {answer_path}")

    expected_source_suffix = path.stem.removeprefix("workbook-index-")
    if source_id and source_id != f"workbook-{expected_source_suffix}":
        errors.append("source_id 与索引文件名不匹配")
    if answer_id and answer_id != f"workbook-answer-{expected_source_suffix}":
        errors.append("answer_id 与索引文件名不匹配")

    if "questions:" not in body:
        errors.append("缺少 questions 列表")

    if re.search(r'\bsection:\s*"?知识点拨"?', body):
        errors.append("知识点拨学习目标不得进入逐题索引")
    if re.search(r'\bsection:\s*""', body):
        errors.append("存在未归入练习栏目的题目")

    question_ids = QUESTION_ID_RE.findall(body)
    if not question_ids:
        errors.append("未登记任何 question_id")
    if len(question_ids) != len(set(question_ids)):
        errors.append("question_id 存在重复")
    for question_id in question_ids:
        if not question_id.startswith("WB-"):
            errors.append(f"question_id 未使用 WB- 前缀: {question_id}")

    if re.search(r"answer_ref:\s*null", body):
        errors.append("存在未匹配答案的题目")

    if workbook_path.is_file():
        max_line = line_count(workbook_path)
        for field in ["line_start", "line_end"]:
            for value in numeric_fields(body, field):
                if value < 1 or value > max_line:
                    errors.append(f"{field} 超出题库文件行数: {value}")

    if answer_path.is_file():
        max_answer_line = line_count(answer_path)
        for field in ["answer_line_start", "answer_line_end"]:
            for value in numeric_fields(body, field):
                if value < 1 or value > max_answer_line:
                    errors.append(f"{field} 超出答案文件行数: {value}")

    return errors


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="验证练习册逐题索引")
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    files = iter_files(args.target.resolve())
    if not files:
        print("未找到 workbook-index-*.yaml 文件")
        return 1

    total_errors = 0
    total_ok = 0
    for path in files:
        errors = validate_file(path)
        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        if errors:
            total_errors += len(errors)
            print(f"FAIL {rel}")
            for error in errors:
                print(f"  - {error}")
        else:
            total_ok += 1
            print(f"PASS {rel}")

    print()
    print(f"结果: {total_ok} 通过, {total_errors} 个错误")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
