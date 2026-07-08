#!/usr/bin/env python3
"""Split MinerU workbook answer Markdown into per-lesson answer files."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTDIR = REPO_ROOT / "knowledge" / "workbook-answers"
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

CHAPTER_RE = re.compile(r"^#{1,2}\s*第([一二三四五六七八九十\d]+)章\s*(.*)")
LESSON_RE = re.compile(r"^(?:#{1,2}\s*)?(\d{1,2})\.(\d+)\s+(.+?)\s*$")
REVIEW_RE = re.compile(r"^(?:#{1,2}\s*)?回顾与反思\s*$")
UNIT_TEST_RE = re.compile(r"^(?:#{1,2}\s*)?单元测试卷(?:第([一二三四五六七八九十\d]+)章\s*(.*))?\s*$")
MIDTERM_RE = re.compile(r"^(?:#{1,2}\s*)?期中测试卷\s*$")
TEST_CHAPTER_RE = re.compile(r"^(?:#{1,2}\s*)?第([一二三四五六七八九十\d]+)章\s*(.*)")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


@dataclass(frozen=True)
class Segment:
    title: str
    filename: str
    source_id: str
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


def lesson_suffix(raw_title: str) -> str:
    match = re.search(r"[（(]([一二三四五六七八九十\d]+)[）)]\s*$", raw_title)
    if not match:
        return ""
    return f"-{cn_to_int(match.group(1))}"


def answer_filename_for_lesson(chapter: str, section: str, raw_title: str) -> tuple[str, str]:
    stem = f"{chapter}.{section}{lesson_suffix(raw_title)}"
    return f"workbook-answer-{stem}.md", f"workbook-{stem}"


def make_front_matter(filename: str, source_id: str) -> str:
    answer_id = Path(filename).stem
    return (
        "---\n"
        "content_type: workbook_answer\n"
        "source_type: exercise_bank\n"
        f"source_id: {source_id}\n"
        f"answer_id: {answer_id}\n"
        "---\n\n"
    )


def count_images(lines: list[str]) -> int:
    return len(IMAGE_RE.findall("\n".join(lines)))


def split_segments(text: str) -> list[Segment]:
    lines = normalize_newlines(text).splitlines()
    segments: list[Segment] = []
    current_title: str | None = None
    current_filename: str | None = None
    current_source_id: str | None = None
    current_lines: list[str] = []
    current_chapter: int | None = None
    pending_unit_test = False

    def flush() -> None:
        nonlocal current_title, current_filename, current_source_id, current_lines
        if current_title and current_filename and current_source_id and current_lines:
            segments.append(
                Segment(
                    title=current_title,
                    filename=current_filename,
                    source_id=current_source_id,
                    lines=current_lines,
                    image_count=count_images(current_lines),
                )
            )
        current_title = None
        current_filename = None
        current_source_id = None
        current_lines = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            if current_title:
                current_lines.append(raw_line)
            continue

        chapter_match = CHAPTER_RE.match(stripped)
        lesson_match = LESSON_RE.match(stripped)
        review_match = REVIEW_RE.match(stripped)
        unit_match = UNIT_TEST_RE.match(stripped)
        midterm_match = MIDTERM_RE.match(stripped)

        if midterm_match:
            flush()
            pending_unit_test = False
            current_title = "期中测试卷"
            current_filename = "workbook-answer-midterm.md"
            current_source_id = "workbook-midterm"
            current_lines = ["# 期中测试卷"]
            continue

        if unit_match:
            flush()
            pending_unit_test = True
            if unit_match.group(1):
                current_chapter = cn_to_int(unit_match.group(1))
                current_title = f"第{current_chapter}章 单元测试卷"
                current_filename = f"workbook-answer-ch{current_chapter}-unit-test.md"
                current_source_id = f"workbook-ch{current_chapter}-unit-test"
                current_lines = [f"# 第{current_chapter}章 单元测试卷"]
                pending_unit_test = False
            continue

        if pending_unit_test:
            test_chapter = TEST_CHAPTER_RE.match(stripped)
            if test_chapter:
                current_chapter = cn_to_int(test_chapter.group(1))
                current_title = f"第{current_chapter}章 单元测试卷"
                current_filename = f"workbook-answer-ch{current_chapter}-unit-test.md"
                current_source_id = f"workbook-ch{current_chapter}-unit-test"
                current_lines = [f"# 第{current_chapter}章 单元测试卷"]
                pending_unit_test = False
                continue

        if chapter_match and not pending_unit_test:
            flush()
            current_chapter = cn_to_int(chapter_match.group(1))
            continue

        if lesson_match and not pending_unit_test:
            flush()
            chapter, section, raw_title = lesson_match.groups()
            current_chapter = int(chapter)
            current_title = f"{chapter}.{section} {raw_title.strip()}"
            current_filename, current_source_id = answer_filename_for_lesson(chapter, section, raw_title)
            current_lines = [f"# {current_title}"]
            continue

        if review_match and not pending_unit_test and current_chapter is not None:
            flush()
            current_title = f"第{current_chapter}章 回顾与反思"
            current_filename = f"workbook-answer-ch{current_chapter}-review.md"
            current_source_id = f"workbook-ch{current_chapter}-review"
            current_lines = [f"# 第{current_chapter}章 回顾与反思"]
            continue

        if current_title:
            current_lines.append(raw_line)

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


def normalize_body(segment: Segment, input_file: Path, copy_images: bool) -> str:
    body = "\n".join(line.rstrip() for line in segment.lines).strip() + "\n"
    body = re.sub(r"\n{3,}", "\n\n", body)
    body = rewrite_and_copy_images(body, input_file.parent, copy_images)
    return make_front_matter(segment.filename, segment.source_id) + body


def print_preview(segments: list[Segment]) -> None:
    print("练习册参考答案拆分预览")
    print("=" * 60)
    for index, segment in enumerate(segments, 1):
        print(f"{index:02d}. {segment.filename}")
        print(f"    标题: {segment.title}")
        print(f"    source_id: {segment.source_id}")
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
        output.write_text(normalize_body(segment, input_file, copy_images), encoding="utf-8")
        written.append(output)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="拆分 MinerU 练习册参考答案 Markdown")
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--overwrite", action="store_true", help="允许覆盖已有输出文件")
    parser.add_argument("--no-copy-images", action="store_true", help="不复制图片到 knowledge/images")
    parser.add_argument("-y", "--yes", action="store_true", help="跳过确认直接写入")
    args = parser.parse_args()

    input_file = args.input_file.resolve()
    if not input_file.is_file():
        print(f"输入文件不存在: {input_file}", file=sys.stderr)
        return 1

    segments = split_segments(input_file.read_text(encoding="utf-8"))
    if not segments:
        print("未识别到可拆分答案", file=sys.stderr)
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
