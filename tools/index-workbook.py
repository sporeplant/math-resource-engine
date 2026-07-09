#!/usr/bin/env python3
"""Build per-question indexes for split workbook files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKBOOK_DIR = REPO_ROOT / "knowledge" / "workbooks"
DEFAULT_ANSWER_DIR = REPO_ROOT / "knowledge" / "workbook-answers"
DEFAULT_OUTDIR = REPO_ROOT / "knowledge" / "workbook-index"

QUESTION_RE = re.compile(r"^\s*(\d+)\.(?!\d)\s*(.*)")
SUBQUESTION_RE = re.compile(r"^\s*[（(](\d+)[）)]")
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$")


@dataclass
class SubQuestion:
    no: str
    line_start: int
    line_end: int
    preview: str
    answer_line_start: int | None = None
    answer_line_end: int | None = None


@dataclass
class Question:
    no: str
    section: str
    line_start: int
    line_end: int
    preview: str
    answer_line_start: int | None = None
    answer_line_end: int | None = None
    subquestions: list[SubQuestion] = field(default_factory=list)


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def preview(line: str, limit: int = 80) -> str:
    clean = re.sub(r"!\[[^\]]*\]\([^)]+\)", "[图片]", line).strip()
    clean = re.sub(r"\s+", " ", clean)
    return clean[:limit]


def iter_workbook_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(path for path in target.glob("workbook-*.md") if path.is_file())
    raise FileNotFoundError(f"目标不存在: {target}")


def answer_path_for(workbook_path: Path, answer_dir: Path) -> Path:
    if not workbook_path.stem.startswith("workbook-"):
        raise ValueError(f"不是练习册题库文件: {workbook_path.name}")
    suffix = workbook_path.stem.removeprefix("workbook-")
    return answer_dir / f"workbook-answer-{suffix}.md"


def index_path_for(workbook_path: Path, outdir: Path) -> Path:
    suffix = workbook_path.stem.removeprefix("workbook-")
    return outdir / f"workbook-index-{suffix}.yaml"


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
    return meta, text[end + 4 :].lstrip()


def parse_questions(text: str) -> list[Question]:
    lines = normalize_newlines(text).splitlines()
    questions: list[Question] = []
    current_section = ""
    current: Question | None = None

    def close_question(end_line: int) -> None:
        nonlocal current
        if current is None:
            return
        current.line_end = end_line
        if current.subquestions:
            for index, sub in enumerate(current.subquestions):
                next_start = (
                    current.subquestions[index + 1].line_start
                    if index + 1 < len(current.subquestions)
                    else current.line_end + 1
                )
                sub.line_end = max(sub.line_start, next_start - 1)
        questions.append(current)
        current = None

    for index, line in enumerate(lines, 1):
        heading = HEADING_RE.match(line)
        content = re.sub(r"^#+\s*", "", line).strip()
        question = QUESTION_RE.match(content)

        if heading and not question:
            close_question(index - 1)
            current_section = heading.group(1)
            continue

        if current_section == "知识点拨":
            continue

        if question:
            close_question(index - 1)
            no, text_after_no = question.groups()
            current = Question(
                no=no,
                section=current_section,
                line_start=index,
                line_end=index,
                preview=preview(text_after_no or line),
            )
            sub = SUBQUESTION_RE.match(text_after_no)
            if sub:
                current.subquestions.append(
                    SubQuestion(
                        no=sub.group(1),
                        line_start=index,
                        line_end=index,
                        preview=preview(text_after_no),
                    )
                )
            continue

        if current:
            sub = SUBQUESTION_RE.match(line)
            if sub:
                current.subquestions.append(
                    SubQuestion(
                        no=sub.group(1),
                        line_start=index,
                        line_end=index,
                        preview=preview(line),
                    )
                )

    close_question(len(lines))
    return questions


def find_inline_answer_ref(answer_text: str, question_no: str) -> tuple[int, int] | None:
    _, body = parse_front_matter(answer_text)
    pattern = re.compile(
        rf"(?:^|[\s。]){re.escape(question_no)}\.(?:\s|[（(]|\$|[\u4e00-\u9fff]|-|\d)"
    )
    for index, line in enumerate(normalize_newlines(body).splitlines(), 1):
        if pattern.search(line):
            return index, index
    return None


def map_answers(answer_text: str) -> dict[tuple[str, str | None], tuple[int, int]]:
    _, body = parse_front_matter(answer_text)
    answers = parse_questions(body)
    mapping: dict[tuple[str, str | None], tuple[int, int]] = {}
    for answer in answers:
        mapping[(answer.no, None)] = (answer.line_start, answer.line_end)
        for sub in answer.subquestions:
            mapping[(answer.no, sub.no)] = (sub.line_start, sub.line_end)
    return mapping


def attach_answer_refs(questions: list[Question], answer_text: str) -> None:
    answer_map = map_answers(answer_text)
    for question in questions:
        top_ref = answer_map.get((question.no, None)) or find_inline_answer_ref(
            answer_text, question.no
        )
        if top_ref:
            question.answer_line_start, question.answer_line_end = top_ref
        for sub in question.subquestions:
            sub_ref = answer_map.get((question.no, sub.no)) or top_ref
            if sub_ref:
                sub.answer_line_start, sub.answer_line_end = sub_ref


def has_images(text: str, start: int, end: int) -> bool:
    lines = normalize_newlines(text).splitlines()
    block = "\n".join(lines[start - 1 : end])
    return bool(re.search(r"!\[[^\]]*\]\([^)]+\)", block))


def build_index_text(
    workbook_path: Path,
    answer_path: Path,
    questions: list[Question],
    workbook_text: str,
) -> str:
    source_id = workbook_path.stem
    answer_id = answer_path.stem
    index_id = index_path_for(workbook_path, DEFAULT_OUTDIR).stem
    id_suffix = source_id.removeprefix("workbook-")
    sub_count = sum(len(question.subquestions) for question in questions)

    lines: list[str] = [
        "---",
        "content_type: workbook_index",
        "source_type: exercise_bank",
        f"source_id: {source_id}",
        f"answer_id: {answer_id}",
        f"index_id: {index_id}",
        f"question_count: {len(questions)}",
        f"subquestion_count: {sub_count}",
        "---",
        "",
        "questions:",
    ]

    for q_index, question in enumerate(questions, 1):
        qid = f"WB-{id_suffix}-Q{q_index:03d}"
        lines.extend(
            [
                f"  - question_id: {qid}",
                f"    source_id: {source_id}",
                "    source_type: exercise_bank",
                f"    question_no: {q(question.no)}",
                f"    section: {q(question.section)}",
                f"    line_start: {question.line_start}",
                f"    line_end: {question.line_end}",
                f"    has_image: {str(has_images(workbook_text, question.line_start, question.line_end)).lower()}",
                f"    preview: {q(question.preview)}",
            ]
        )
        if question.answer_line_start is not None and question.answer_line_end is not None:
            lines.extend(
                [
                    "    answer_ref:",
                    f"      answer_id: {answer_id}",
                    f"      answer_line_start: {question.answer_line_start}",
                    f"      answer_line_end: {question.answer_line_end}",
                ]
            )
        else:
            lines.append("    answer_ref: null")

        if question.subquestions:
            lines.append("    subquestions:")
            for sub_index, sub in enumerate(question.subquestions, 1):
                sub_id = f"{qid}-S{sub_index:02d}"
                lines.extend(
                    [
                        f"      - question_id: {sub_id}",
                        f"        parent_question_id: {qid}",
                        f"        question_no: {q(question.no)}",
                        f"        subquestion_no: {q(sub.no)}",
                        f"        line_start: {sub.line_start}",
                        f"        line_end: {sub.line_end}",
                        f"        has_image: {str(has_images(workbook_text, sub.line_start, sub.line_end)).lower()}",
                        f"        preview: {q(sub.preview)}",
                    ]
                )
                if sub.answer_line_start is not None and sub.answer_line_end is not None:
                    lines.extend(
                        [
                            "        answer_ref:",
                            f"          answer_id: {answer_id}",
                            f"          answer_line_start: {sub.answer_line_start}",
                            f"          answer_line_end: {sub.answer_line_end}",
                        ]
                    )
                else:
                    lines.append("        answer_ref: null")

    return "\n".join(lines).rstrip() + "\n"


def build_one(workbook_path: Path, answer_dir: Path, outdir: Path, overwrite: bool) -> Path:
    answer_path = answer_path_for(workbook_path, answer_dir)
    if not answer_path.is_file():
        raise FileNotFoundError(f"缺少练习册答案文件: {answer_path}")

    workbook_text = workbook_path.read_text(encoding="utf-8")
    answer_text = answer_path.read_text(encoding="utf-8")
    questions = parse_questions(workbook_text)
    if not questions:
        raise ValueError(f"未识别到题目: {workbook_path}")

    attach_answer_refs(questions, answer_text)
    outdir.mkdir(parents=True, exist_ok=True)
    output = index_path_for(workbook_path, outdir)
    if output.exists() and not overwrite:
        raise FileExistsError(f"索引文件已存在，未覆盖: {output}")
    output.write_text(build_index_text(workbook_path, answer_path, questions, workbook_text), encoding="utf-8")
    return output


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="生成练习册逐题索引")
    parser.add_argument("target", type=Path, nargs="?", default=DEFAULT_WORKBOOK_DIR)
    parser.add_argument("--answer-dir", type=Path, default=DEFAULT_ANSWER_DIR)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--chapter", help="仅处理指定章号，如 12")
    parser.add_argument("--overwrite", action="store_true", help="允许覆盖已有索引")
    args = parser.parse_args()

    files = iter_workbook_files(args.target.resolve())
    if args.chapter:
        chapter_prefix = f"workbook-{args.chapter}."
        review_name = f"workbook-ch{args.chapter}-review.md"
        files = [
            path
            for path in files
            if path.name.startswith(chapter_prefix) or path.name == review_name
        ]

    if not files:
        print("未找到可索引的练习册文件", file=sys.stderr)
        return 1

    written: list[Path] = []
    try:
        for path in files:
            written.append(build_one(path, args.answer_dir.resolve(), args.outdir.resolve(), args.overwrite))
    except (FileNotFoundError, FileExistsError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("已写入练习册索引:")
    for path in written:
        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
