#!/usr/bin/env python3
"""Validate the two-layer structure required for a lesson plan.

Usage:
    python tools/validate_lesson_dual_layer.py path/to/lesson.md

This is a thin CLI wrapper around ``validate_output.check_lesson_dual_layer``,
which is the single source of truth for the lesson-collab output contract.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from validate_output import check_lesson_dual_layer, parse_front_matter, read_text
except ModuleNotFoundError:
    from tools.validate_output import (
        check_lesson_dual_layer,
        parse_front_matter,
        read_text,
    )


def validate(path: Path) -> list[str]:
    text = read_text(path)
    meta = parse_front_matter(text)
    errors: list[str] = []
    check_lesson_dual_layer(text, meta, errors)
    return errors


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(
        description="Validate a lesson's two-layer Markdown structure."
    )
    parser.add_argument("file", type=Path, help="Lesson Markdown file")
    args = parser.parse_args()

    if not args.file.is_file():
        print(f"Validation FAILED:\n  ❌ file not found: {args.file}")
        return 1

    errors = validate(args.file)
    if errors:
        print("Validation FAILED:")
        for error in errors:
            print(f"  ❌ {error}")
        return 1

    print("✅ Lesson dual-layer validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
