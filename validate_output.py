#!/usr/bin/env python3
"""Validate hard rules for math-resource-engine Markdown outputs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FORBIDDEN_TERMS = ["理解", "掌握", "了解", "体会", "感受", "知道"]
REQUIRED_LAYERS = ["基础层", "中间层", "拓展层"]
VALID_REVIEW_STATUS = {"draft", "pending_human_review", "human_approved", "rejected"}
VALID_LESSON_COMMANDS = {"lesson", "lesson-collab"}
QUESTION_HINTS = ["题目", "例题", "练习", "作业", "评价任务"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    block = text[4:end]
    meta: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def extract_img_paths(text: str) -> list[str]:
    return re.findall(r"<img\s+[^>]*src=[\"']([^\"']+)[\"'][^>]*>", text, flags=re.I)


def extract_minutes(text: str) -> list[int]:
    minutes: list[int] = []
    for line in text.splitlines():
        if re.search(r"duration\s*[:：]", line, flags=re.I):
            continue
        match = re.match(r"\s*-?\s*(?:time|时间)\s*[:：]\s*(\d+)\s*分钟", line, flags=re.I)
        if match:
            minutes.append(int(match.group(1)))
            continue
        match = re.search(r"（\s*(\d+)\s*分钟\s*）", line)
        if match:
            minutes.append(int(match.group(1)))
    return minutes


def parse_students(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    names: set[str] = set()
    for line in read_text(path).splitlines():
        match = re.match(r"\|\s*([^|\s]+)\s*\|\s*\d", line)
        if match and match.group(1) != "姓名":
            names.add(match.group(1))
    return names


def extract_called_students(text: str) -> list[str]:
    names = re.findall(r"请\[([^\]]+)\]同学", text)
    names.extend(re.findall(r"^\|\s*([^|\s]+)\s*\|\s*(?:基础层|中间层|拓展层)\s*\|", text, flags=re.M))
    return [name.strip() for name in names if name.strip() and name.strip() != "学生"]


def check_common(path: Path, text: str, errors: list[str]) -> dict[str, str]:
    meta = parse_front_matter(text)
    if not meta:
        errors.append("missing YAML front matter")
        return meta

    for key in ["content_type", "lesson_id", "lesson_name", "command", "workflow_version", "review_status", "created_at"]:
        if key not in meta or not meta[key]:
            errors.append(f"missing front matter field: {key}")

    if meta.get("workflow_version") != "v2":
        errors.append("workflow_version must be v2")

    if meta.get("review_status") and meta["review_status"] not in VALID_REVIEW_STATUS:
        errors.append(f"invalid review_status: {meta['review_status']}")

    for term in FORBIDDEN_TERMS:
        if term in text:
            errors.append(f"forbidden term found: {term}")

    for layer in REQUIRED_LAYERS:
        if layer not in text:
            errors.append(f"missing layer: {layer}")

    if any(hint in text for hint in QUESTION_HINTS):
        for field in ["source_id", "source_type", "question_id"]:
            if field not in text:
                errors.append(f"missing question source field: {field}")

    if re.search(r"!\[[^\]]*\]\([^)]+\)", text):
        errors.append("Markdown image syntax is forbidden; use <img src=\"./images/...\">")

    for bad in ["../知识库/教材原文/images", "../知识库/练习册题库/images", "assets/images", "输出/{lesson_id}/assets"]:
        if bad in text:
            errors.append(f"forbidden image path fragment: {bad}")

    for img_path in extract_img_paths(text):
        if not img_path.startswith("./images/"):
            errors.append(f"image path must start with ./images/: {img_path}")
            continue
        if not (path.parent / img_path).exists():
            errors.append(f"image file does not exist: {img_path}")

    if "图片待确认" in text:
        errors.append("image placeholder remains in final output")

    return meta


def check_lesson(text: str, meta: dict[str, str], errors: list[str]) -> None:
    if meta.get("content_type") == "lesson":
        if meta.get("command") not in VALID_LESSON_COMMANDS:
            errors.append("lesson output must have command: lesson or lesson-collab")
        if meta.get("review_status") not in {"pending_human_review", "human_approved", "rejected"}:
            errors.append("lesson review_status must be pending_human_review, human_approved, or rejected")

    minutes = extract_minutes(text)
    if minutes and sum(minutes) > 35:
        errors.append(f"lesson time exceeds 35 minutes: {sum(minutes)}")

    if re.search(r"请\[[^\]]+\]同学", text):
        errors.append("lesson design must not contain concrete student names in questions")


def check_courseware(text: str, meta: dict[str, str], errors: list[str], lesson_file: Path | None) -> None:
    if meta.get("content_type") != "courseware":
        return
    if meta.get("command") != "courseware":
        errors.append("courseware output must have command: courseware")
    for required in ["📐", "目标", "page-break-after: always", "作业"]:
        if required not in text:
            errors.append(f"courseware missing required structure marker: {required}")

    if lesson_file:
        lesson_meta = parse_front_matter(read_text(lesson_file))
        if lesson_meta.get("content_type") != "lesson":
            errors.append("upstream lesson file must have content_type: lesson")
        if lesson_meta.get("review_status") != "human_approved":
            errors.append("upstream lesson must be review_status: human_approved")
        if lesson_meta.get("lesson_id") and meta.get("lesson_id") != lesson_meta.get("lesson_id"):
            errors.append("courseware lesson_id does not match upstream lesson")


def check_question_reference(text: str, errors: list[str], students_file: Path | None) -> None:
    students = parse_students(students_file)
    called = extract_called_students(text)
    if students:
        for name in called:
            if name not in students:
                errors.append(f"student name not found in students file: {name}")
    duplicates = sorted({name for name in called if called.count(name) > 1})
    for name in duplicates:
        if "人数不足" not in text and "轮换" not in text:
            errors.append(f"duplicate student without rotation reason: {name}")


def validate(path: Path, lesson_file: Path | None, question_reference: Path | None, students_file: Path | None, textbook_file: Path | None = None) -> list[str]:
    text = read_text(path)
    errors: list[str] = []
    meta = check_common(path, text, errors)
    check_lesson(text, meta, errors)
    check_courseware(text, meta, errors, lesson_file)

    if question_reference:
        check_question_reference(read_text(question_reference), errors, students_file)
    elif meta.get("content_type") == "question_reference":
        check_question_reference(text, errors, students_file)

    if meta.get("content_type") == "lesson" and "教材对应位置" in text:
        try:
            from tools.validate_activity_textbook_order import validate as validate_order
            project_root = path.parent
            if textbook_file is None:
                source_files = meta.get("source_files", "")
                if source_files:
                    for src in source_files.split(","):
                        src = src.strip().strip('"').strip("'")
                        if "教材原文" in src:
                            tf = project_root / src
                            if tf.exists():
                                textbook_file = tf
                                break
            if textbook_file is None:
                textbook_dir = project_root / "知识库" / "教材原文"
                if textbook_dir.exists():
                    lesson_name = meta.get("lesson_name", "")
                    patterns = [f"*{lesson_name.replace('.', '').replace('(', '').replace(')', '')}*.md", "*.md"]
                    for pattern in patterns:
                        matches = sorted(textbook_dir.glob(pattern))
                        if matches:
                            textbook_file = matches[0]
                            break
            if textbook_file and textbook_file.exists():
                order_errors, _ = validate_order(path, textbook_file)
                errors.extend([f"[ActivityOrder] {e}" for e in order_errors])
        except ImportError:
            pass

    return errors


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    parser = argparse.ArgumentParser(description="Validate Markdown output hard rules.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--lesson-file", type=Path)
    parser.add_argument("--question-reference", type=Path)
    parser.add_argument("--students-file", type=Path)
    parser.add_argument("--textbook-file", type=Path)
    args = parser.parse_args()

    errors = validate(args.file, args.lesson_file, args.question_reference, args.students_file, args.textbook_file)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
