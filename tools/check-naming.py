#!/usr/bin/env python3
"""Check file/dir naming and content references for math-resource-engine.

Can be run directly or as a pre-commit/pre-push hook.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uff00-\uffef]")
HASH_ONLY_PATTERN = re.compile(r"^doc?-?[0-9a-f]{8,}$", re.IGNORECASE)
UPPERCASE_EXCEPTIONS = {
    "SKILL.md",
    "checklist.md",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "Makefile",
    "posture_break_guard_README.md",
}

# File extensions that follow platform conventions, exempt from naming rules
EXTENSION_EXEMPTIONS = {".exe", ".ps1", ".sln"}
OLD_DIRS = [
    "知识库/",
    "输出/",
    "学生近期数据/",
    "主控/",
    "技能/",
    "验证器/",
]

CHINESE_IMG_RE = re.compile(r"!\[.*?\]\(.*?[\u4e00-\u9fff].*?\)")


def staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        print(f"git error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return [REPO_ROOT / f for f in result.stdout.splitlines() if f]


def added_staged_files() -> set[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        print(f"git error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return {(REPO_ROOT / f).resolve() for f in result.stdout.splitlines() if f}


def check_name(name: str) -> list[str]:
    errors = []
    suffix = Path(name).suffix.lower()
    if suffix in EXTENSION_EXEMPTIONS:
        return errors
    if CHINESE_PATTERN.search(name):
        errors.append(f"  contains Chinese characters: {name}")
    if " " in name:
        errors.append(f"  contains space: {name}")
    if "_" in name:
        errors.append(f"  contains underscore: {name}")
    if name != name.lower() and name not in UPPERCASE_EXCEPTIONS:
        errors.append(f"  contains uppercase: {name}")
    stem = Path(name).stem
    if HASH_ONLY_PATTERN.match(stem):
        errors.append(f"  hash-only name (no semantic identifier): {name}")
    return errors


def check_content(path: Path) -> list[str]:
    errors = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    for old in OLD_DIRS:
        if old in text:
            errors.append(f"  references old path '{old}' in {path}")
    if CHINESE_IMG_RE.search(text):
        errors.append(f"  image reference contains Chinese characters in {path}")
    return errors


def check_all(paths: list[Path]) -> list[str]:
    errors = []
    checked = set()
    added_paths = added_staged_files()
    for path in paths:
        if not path.exists():
            continue
        resolved = path.resolve()
        if resolved in checked:
            continue
        checked.add(resolved)

        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        if resolved in added_paths:
            for part in rel.parts:
                errors.extend(check_name(part))
        if path.is_file() and path.suffix == ".md":
            errors.extend(check_content(path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check file naming and content references."
    )
    parser.add_argument(
        "files", nargs="*", type=Path, help="Files to check (default: staged files)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Check all tracked files instead of staged"
    )
    args = parser.parse_args()

    if args.all:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            print(f"git error: {result.stderr.strip()}", file=sys.stderr)
            return 1
        files = [REPO_ROOT / f for f in result.stdout.splitlines() if f]
    elif args.files:
        files = args.files
    else:
        files = staged_files()

    if not files:
        print("[OK] No files to check")
        return 0

    errors = check_all(files)
    if errors:
        print("[FAIL] Naming/content check failed:")
        for e in errors:
            print(e)
        return 1
    print("[OK] Naming/content check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
