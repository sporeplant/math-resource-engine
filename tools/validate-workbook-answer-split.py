#!/usr/bin/env python3
"""Validate split workbook answer Markdown files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_IMAGES = REPO_ROOT / "knowledge" / "images"
CDN_PREFIX = "https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/"
FILENAME_RE = re.compile(
    r"^workbook-answer-(?:\d+\.\d+(?:-\d+)?|ch\d+-(?:review|unit-test)|midterm)\.md$"
)
CDN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(" + re.escape(CDN_PREFIX) + r"([^)]+)\)")
REL_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?:\.\.?/)?images/[^)]+\)")


def iter_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(path for path in target.glob("workbook-answer-*.md") if path.is_file())
    raise FileNotFoundError(f"目标不存在: {target}")


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    meta: dict[str, str] = {}
    for line in text[3:end].strip().splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    return meta


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    meta = parse_front_matter(text)

    if not FILENAME_RE.match(path.name):
        errors.append(f"文件名不符合规则: {path.name}")

    if meta.get("content_type") != "workbook_answer":
        errors.append("content_type 不是 workbook_answer")
    if meta.get("source_type") != "exercise_bank":
        errors.append("source_type 不是 exercise_bank")
    if not meta.get("source_id"):
        errors.append("缺少 source_id")
    if meta.get("answer_id") != path.stem:
        errors.append("answer_id 与文件名不一致")

    body_start = text.find("---", 3)
    body = text[body_start + 3 :].lstrip() if body_start != -1 else text
    if not body.startswith("# "):
        errors.append("正文未以一级标题开头")

    if REL_IMAGE_RE.search(text):
        errors.append("存在相对 images/ 图片引用")

    for image_name in CDN_IMAGE_RE.findall(text):
        if not (KNOWLEDGE_IMAGES / image_name).is_file():
            errors.append(f"CDN 图片缺少本地文件: {image_name}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="验证练习册参考答案拆分结果")
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    files = iter_files(args.target.resolve())
    if not files:
        print("未找到 workbook-answer-*.md 文件")
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
