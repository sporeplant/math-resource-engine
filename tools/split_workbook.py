#!/usr/bin/env python3
"""Split a MinerU workbook Markdown file into knowledge/workbooks files."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTDIR = REPO_ROOT / "knowledge" / "workbooks"
KNOWLEDGE_IMAGES = REPO_ROOT / "knowledge" / "images"
CDN_PREFIX = "https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/"

CN_DIGIT = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
    "十一": 11,
    "十二": 12,
    "十三": 13,
    "十四": 14,
    "十五": 15,
    "十六": 16,
    "十七": 17,
    "十八": 18,
    "十九": 19,
    "二十": 20,
}

CHAPTER_RE = re.compile(r"^#\s*第([一二三四五六七八九十\d]+)章\s*(.*)")
LESSON_RE = re.compile(r"^##\s*(\d+)\.(\d+)\s+(.+?)\s*$")
REVIEW_RE = re.compile(r"^#{1,2}\s*回顾与反思\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


@dataclass(frozen=True)
class Segment:
    title: str
    filename: str
    lines: list[str]
    image_count: int


def cn_to_int(value: str) -> int:
    if value.isdigit():
        return int(value)
    if value in CN_DIGIT:
        return CN_DIGIT[value]
    raise ValueError(f"无法识别中文数字: {value}")


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def detect_chapter(lines: list[str], override: str | None) -> int:
    if override:
        return int(override)
    for line in lines[:80]:
        match = CHAPTER_RE.match(line.strip())
        if match:
            return cn_to_int(match.group(1))
    raise ValueError("未识别到章标题，请使用 --chapter 指定章号")


def lesson_filename(chapter: str, section: str, raw_title: str) -> str:
    match = re.search(r"[（(]([一二三四五六七八九十\d]+)[）)]\s*$", raw_title)
    if not match:
        return f"workbook-{chapter}.{section}.md"
    lesson_no = cn_to_int(match.group(1))
    return f"workbook-{chapter}.{section}-{lesson_no}.md"


def normalize_heading(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("## "):
        return "# " + stripped[3:].strip()
    return line.rstrip()


def normalize_body(lines: list[str]) -> str:
    normalized = [normalize_heading(line) for line in lines]
    text = "\n".join(normalized)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def count_images(lines: list[str]) -> int:
    return len(IMAGE_RE.findall("\n".join(lines)))


def split_segments(text: str, chapter_no: int) -> list[Segment]:
    lines = normalize_newlines(text).splitlines()
    segments: list[Segment] = []
    current_title: str | None = None
    current_filename: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_filename, current_lines
        if current_title and current_filename and current_lines:
            segments.append(
                Segment(
                    title=current_title,
                    filename=current_filename,
                    lines=current_lines,
                    image_count=count_images(current_lines),
                )
            )
        current_title = None
        current_filename = None
        current_lines = []

    for line in lines:
        stripped = line.strip()
        lesson_match = LESSON_RE.match(stripped)
        review_match = REVIEW_RE.match(stripped)

        if lesson_match:
            flush()
            chapter, section, raw_title = lesson_match.groups()
            current_title = f"{chapter}.{section} {raw_title}"
            current_filename = lesson_filename(chapter, section, raw_title)
            current_lines = [f"# {current_title}"]
            continue

        if review_match:
            flush()
            current_title = "回顾与反思"
            current_filename = f"workbook-ch{chapter_no}-review.md"
            current_lines = ["# 回顾与反思"]
            continue

        if current_title:
            current_lines.append(line)

    flush()
    return segments


def rewrite_and_copy_images(text: str, source_dir: Path, copy_images: bool) -> str:
    source_images = source_dir / "images"

    def replace(match: re.Match[str]) -> str:
        alt, raw_path = match.group(1), match.group(2).strip()
        if raw_path.startswith(CDN_PREFIX):
            return match.group(0)
        if raw_path.startswith(("http://", "https://", "data:")):
            return match.group(0)

        image_name = Path(raw_path.replace("\\", "/")).name
        if copy_images:
            src = source_images / image_name
            if not src.is_file():
                raise FileNotFoundError(f"图片文件不存在: {src}")
            KNOWLEDGE_IMAGES.mkdir(parents=True, exist_ok=True)
            dst = KNOWLEDGE_IMAGES / image_name
            if not dst.exists():
                shutil.copy2(src, dst)

        return f"![{alt}]({CDN_PREFIX}{image_name})"

    return IMAGE_RE.sub(replace, text)


def print_preview(segments: list[Segment]) -> None:
    print("练习册拆分预览")
    print("=" * 60)
    for index, segment in enumerate(segments, 1):
        print(f"{index:02d}. {segment.filename}")
        print(f"    标题: {segment.title}")
        print(f"    图片: {segment.image_count}")
    print("=" * 60)
    print(f"共 {len(segments)} 个输出文件")


def write_segments(
    segments: list[Segment],
    input_file: Path,
    outdir: Path,
    overwrite: bool,
    copy_images: bool,
) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for segment in segments:
        output = outdir / segment.filename
        if output.exists() and not overwrite:
            raise FileExistsError(f"输出文件已存在，未覆盖: {output}")

        body = normalize_body(segment.lines)
        body = rewrite_and_copy_images(body, input_file.parent, copy_images)
        output.write_text(body, encoding="utf-8")
        written.append(output)

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="拆分 MinerU 练习册 Markdown 大文件")
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--chapter", help="手动指定章号，如 12")
    parser.add_argument("--overwrite", action="store_true", help="允许覆盖已有输出文件")
    parser.add_argument("--no-copy-images", action="store_true", help="不复制图片到 knowledge/images")
    parser.add_argument("-y", "--yes", action="store_true", help="跳过确认直接写入")
    args = parser.parse_args()

    input_file = args.input_file.resolve()
    if not input_file.is_file():
        print(f"输入文件不存在: {input_file}", file=sys.stderr)
        return 1

    text = input_file.read_text(encoding="utf-8")
    lines = normalize_newlines(text).splitlines()
    chapter_no = detect_chapter(lines, args.chapter)
    segments = split_segments(text, chapter_no)
    if not segments:
        print("未识别到可拆分课时", file=sys.stderr)
        return 1

    print_preview(segments)
    if not args.yes:
        answer = input("确认写入以上文件？输入 yes 继续: ").strip().lower()
        if answer not in {"yes", "y"}:
            print("已取消")
            return 0

    written = write_segments(
        segments=segments,
        input_file=input_file,
        outdir=args.outdir.resolve(),
        overwrite=args.overwrite,
        copy_images=not args.no_copy_images,
    )
    print()
    print("已写入:")
    for path in written:
        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

