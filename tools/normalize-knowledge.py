#!/usr/bin/env python3
"""Normalize MinerU Markdown before it becomes stable knowledge.

The tool is intentionally conservative: it runs in dry-run mode unless --write
is passed. It adds missing front matter, cleans excessive blank lines, and
normalizes Markdown image references to ./images/<file>.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n([\s\S]*?)\n---\s*\n?", re.M)
LESSON_ID_RE = re.compile(r"(?<!\d)(\d{1,2}\.\d+(?:[.-]\d+)?)(?!\d)")


@dataclass(frozen=True)
class NormalizeResult:
    path: Path
    changed: bool
    messages: list[str]
    text: str


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    return meta, text[match.end() :]


def dump_front_matter(meta: dict[str, str], body: str) -> str:
    lines = ["---"]
    for key, value in meta.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body.lstrip("\n")


def infer_source_type(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    if "textbooks" in parts or name.startswith("textbook-"):
        return "textbook"
    if "workbooks" in parts or name.startswith("workbook-"):
        return "workbook"
    if "solutions" in parts or name.startswith("solution-"):
        return "textbook_solution"
    if "reviews" in parts or name.startswith("review-"):
        return "review"
    if "standards" in parts:
        return "curriculum_standard"
    if "types" in parts:
        return "lesson_type"
    return "unknown"


def infer_lesson_id(path: Path, body: str) -> str | None:
    for candidate in (path.stem, body[:1000]):
        match = LESSON_ID_RE.search(candidate)
        if match:
            return match.group(1).replace("-", ".")
    return None


def infer_chapter(lesson_id: str | None, body: str) -> str | None:
    if lesson_id:
        return f"第{lesson_id.split('.')[0]}章"
    match = re.search(r"第\s*([一二三四五六七八九十百千万\d]+)\s*章", body[:1000])
    if match:
        return f"第{match.group(1)}章"
    return None


def infer_title(path: Path, body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            if title:
                return title
    return path.stem


def make_source_id(source_type: str, lesson_id: str | None, path: Path) -> str:
    if lesson_id:
        prefix = {
            "textbook": "textbook",
            "workbook": "workbook",
            "textbook_solution": "solution",
            "review": "review",
        }.get(source_type, source_type)
        return f"{prefix}-{lesson_id}"
    return path.stem


def normalize_image_refs(text: str) -> tuple[str, list[str]]:
    messages: list[str] = []

    def replace(match: re.Match[str]) -> str:
        alt, raw_path = match.group(1), match.group(2).strip()
        if raw_path.startswith(("http://", "https://", "data:")):
            return match.group(0)
        normalized = raw_path.replace("\\", "/")
        image_name = Path(normalized).name
        new_path = f"./images/{image_name}"
        if normalized != new_path:
            messages.append(f"image path: {raw_path} -> {new_path}")
        return f"![{alt}]({new_path})"

    return IMAGE_RE.sub(replace, text), messages


def normalize_file(path: Path, args: argparse.Namespace) -> NormalizeResult:
    original = path.read_text(encoding="utf-8")
    text = normalize_newlines(original)
    meta, body = split_front_matter(text)
    messages: list[str] = []

    source_type = args.source_type or meta.get("source_type") or infer_source_type(path)
    lesson_id = args.lesson_id or meta.get("lesson_id", "").strip('"') or infer_lesson_id(path, body)
    chapter = meta.get("chapter") or infer_chapter(lesson_id, body)
    title = meta.get("title") or infer_title(path, body)

    defaults = {
        "source_id": make_source_id(source_type, lesson_id, path),
        "source_type": source_type,
        "origin": args.origin,
        "needs_review": "true",
    }
    if lesson_id:
        defaults["lesson_id"] = f'"{lesson_id}"'
    if chapter:
        defaults["chapter"] = chapter
    if title:
        defaults["title"] = title
    if args.grade:
        defaults["grade"] = args.grade
    if args.publisher:
        defaults["publisher"] = args.publisher

    for key, value in defaults.items():
        if key not in meta:
            meta[key] = value
            messages.append(f"add front matter: {key}")

    body, image_messages = normalize_image_refs(body)
    messages.extend(image_messages)
    body = re.sub(r"\n{3,}", "\n\n", body).rstrip() + "\n"
    new_text = dump_front_matter(meta, body)

    return NormalizeResult(path=path, changed=new_text != original, messages=messages, text=new_text)


def discover_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        elif path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize MinerU Markdown knowledge files.")
    parser.add_argument("paths", nargs="*", type=Path, default=[DEFAULT_KNOWLEDGE_ROOT])
    parser.add_argument("--write", action="store_true", help="Write changes. Default is dry-run.")
    parser.add_argument("--source-type", choices=["textbook", "workbook", "textbook_solution", "review", "curriculum_standard", "lesson_type", "unknown"])
    parser.add_argument("--lesson-id", help="Override lesson_id for all input files.")
    parser.add_argument("--grade", default="八年级")
    parser.add_argument("--publisher", default="冀教版")
    parser.add_argument("--origin", default="mineru-pdf")
    args = parser.parse_args()

    files = discover_files([path.resolve() for path in args.paths])
    if not files:
        print("[OK] no Markdown files found")
        return 0

    changed = 0
    for file in files:
        result = normalize_file(file, args)
        if not result.changed:
            continue
        changed += 1
        rel = file.relative_to(REPO_ROOT) if file.is_relative_to(REPO_ROOT) else file
        print(f"[CHANGE] {rel}")
        for message in result.messages:
            print(f"  - {message}")
        if args.write:
            file.write_text(result.text, encoding="utf-8")

    mode = "written" if args.write else "dry-run"
    print(f"[OK] {mode}: {changed} file(s) would change" if not args.write else f"[OK] written: {changed} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
