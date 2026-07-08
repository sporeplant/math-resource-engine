#!/usr/bin/env python3
"""Validate split workbook Markdown files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_IMAGES = REPO_ROOT / "knowledge" / "images"
CDN_PREFIX = "https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/"
FILENAME_RE = re.compile(r"^workbook-(?:\d+\.\d+(?:-\d+)?|ch\d+-(?:review|project))\.md$")
CDN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(" + re.escape(CDN_PREFIX) + r"([^)]+)\)")
REL_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?:\.\.?/)?images/[^)]+\)")
LESSON_HEADING_RE = re.compile(r"^#\s+(?:\d+\.\d+\s+.+|回顾与反思)\s*$", re.M)


def iter_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(path for path in target.glob("workbook-*.md") if path.is_file())
    raise FileNotFoundError(f"目标不存在: {target}")


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    if not FILENAME_RE.match(path.name):
        errors.append(f"文件名不符合规则: {path.name}")

    if not text.lstrip().startswith("# "):
        errors.append("正文未以一级标题开头")

    if not LESSON_HEADING_RE.search(text):
        errors.append("未找到合法课时或回顾与反思标题")

    if REL_IMAGE_RE.search(text):
        errors.append("存在相对 images/ 图片引用")

    for image_name in CDN_IMAGE_RE.findall(text):
        if not (KNOWLEDGE_IMAGES / image_name).is_file():
            errors.append(f"CDN 图片缺少本地文件: {image_name}")

    if re.search(r"^##\s*(?:知识点拨|夯实基础|数学思考|解决问题)\s*$", text, re.M):
        errors.append("栏目标题仍为二级标题，未规范为一级标题")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="验证练习册拆分结果")
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    files = iter_files(args.target.resolve())
    if not files:
        print("未找到 workbook-*.md 文件")
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
