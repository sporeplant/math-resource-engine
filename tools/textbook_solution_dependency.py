"""Validate the textbook-solution dependency used by lesson/courseware outputs."""

from __future__ import annotations

import re
from pathlib import Path


DEPENDENT_CONTENT_TYPES = {
    "lesson",
    "courseware",
    "question_reference",
    "courseware_reference",
    "reference_answer",
}


def parse_front_matter(text: str) -> tuple[dict[str, str], dict[str, list[str]]]:
    if not text.startswith("---\n"):
        return {}, {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}, {}

    scalars: dict[str, str] = {}
    lists: dict[str, list[str]] = {}
    current_list: str | None = None
    for line in text[4:end].splitlines():
        if re.match(r"^\s+-\s+", line) and current_list:
            value = re.sub(r"^\s+-\s+", "", line).strip().strip('"').strip("'")
            lists.setdefault(current_list, []).append(value)
            continue
        if ":" not in line or line.startswith((" ", "\t")):
            current_list = None
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        scalars[key] = value
        current_list = key if not value else None
        if current_list:
            lists.setdefault(current_list, [])
    return scalars, lists


def find_project_root(path: Path) -> Path:
    start = path if path.is_dir() else path.parent
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / "knowledge").is_dir():
            return candidate
    return start


def extract_question_ids(text: str) -> set[str]:
    ids = set(re.findall(r"question_id\s*:\s*[\"']?([^\s\"']+)", text))
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^(\s*)-?\s*question_ids\s*:\s*$", line)
        if not match:
            continue
        base_indent = len(match.group(1))
        for item in lines[index + 1:]:
            item_match = re.match(r"^(\s*)-\s*[\"']?([^\s\"']+)", item)
            if not item_match or len(item_match.group(1)) <= base_indent:
                break
            ids.add(item_match.group(2))
    return ids


def extract_textbook_question_ids(text: str) -> set[str]:
    ids: set[str] = set()
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.search(r"question_id\s*:\s*[\"']?([^\s\"']+)", line)
        if not match:
            continue
        window = "\n".join(lines[max(0, index - 8): min(len(lines), index + 9)])
        if re.search(r"source_type\s*:\s*[\"']?(?:textbook|TEXTBOOK)\b", window):
            ids.add(match.group(1))
    for index, line in enumerate(lines):
        list_match = re.match(r"^(\s*)-?\s*question_ids\s*:\s*$", line)
        if not list_match:
            continue
        window = "\n".join(lines[max(0, index - 8): index + 1])
        if not re.search(r"source_type\s*:\s*[\"']?(?:textbook|TEXTBOOK)\b", window):
            continue
        base_indent = len(list_match.group(1))
        for item in lines[index + 1:]:
            item_match = re.match(r"^(\s*)-\s*[\"']?([^\s\"']+)", item)
            if not item_match or len(item_match.group(1)) <= base_indent:
                break
            ids.add(item_match.group(2))
    return ids


def textbook_question_ids_missing_answer_source(text: str) -> set[str]:
    missing: set[str] = set()
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.search(r"question_id\s*:\s*[\"']?([^\s\"']+)", line)
        if not match:
            continue
        window = "\n".join(lines[max(0, index - 8): min(len(lines), index + 21)])
        if not re.search(r"source_type\s*:\s*[\"']?(?:textbook|TEXTBOOK)\b", window):
            continue
        if "答案来源" not in window:
            missing.add(match.group(1))
    return missing


def validate_textbook_solution(path: Path, expected_lesson_id: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    if not path.exists():
        return set(), [f"textbook solution file does not exist: {path}"]

    text = path.read_text(encoding="utf-8")
    meta, _ = parse_front_matter(text)
    if meta.get("content_type") != "textbook_solution":
        errors.append("textbook solution must have content_type: textbook_solution")
    if meta.get("command") != "教材问题解答":
        errors.append("textbook solution must have command: 教材问题解答")
    if meta.get("workflow_version") != "v2":
        errors.append("textbook solution must have workflow_version: v2")
    if meta.get("lesson_id") != expected_lesson_id:
        errors.append(
            "textbook solution lesson_id does not match downstream output: "
            f"expected {expected_lesson_id!r}, got {meta.get('lesson_id', '')!r}"
        )
    if "review_status" in meta:
        errors.append("textbook solution must not set review_status")
    for section in ["## 教材任务清单", "## 参考解答", "## 覆盖统计"]:
        if section not in text:
            errors.append(f"textbook solution missing required section: {section}")

    answer_ids = extract_question_ids(text)
    task_ids = set(
        re.findall(r"^\|\s*\d+\s*\|\s*([^|\s]+)\s*\|", text, flags=re.MULTILINE)
    )
    if not answer_ids:
        errors.append("textbook solution contains no question_id")
    if not task_ids:
        errors.append("textbook solution task list contains no question_id")
    missing_answers = sorted(task_ids - answer_ids)
    extra_answers = sorted(answer_ids - task_ids)
    if missing_answers:
        errors.append("textbook solution tasks missing answers: " + ", ".join(missing_answers))
    if extra_answers:
        errors.append("textbook solution answers missing from task list: " + ", ".join(extra_answers))
    if "答案来源:" not in text:
        errors.append("textbook solution contains no 答案来源 field")
    return answer_ids, errors


def validate_dependency(
    output_path: Path,
    output_text: str,
    output_meta: dict[str, str],
    explicit_solution: Path | None = None,
) -> list[str]:
    if output_meta.get("content_type") not in DEPENDENT_CONTENT_TYPES:
        return []

    errors: list[str] = []
    _, lists = parse_front_matter(output_text)
    source_files = lists.get("source_files", [])
    registered = next(
        (item for item in source_files if "knowledge/solutions/" in item.replace("\\", "/")),
        None,
    )
    if not registered and not (
        output_meta.get("content_type") == "courseware" and explicit_solution is not None
    ):
        errors.append("source_files must register the matching textbook solution")

    project_root = find_project_root(output_path)
    solution_path = explicit_solution
    if solution_path is None and registered:
        candidate = Path(registered)
        solution_path = candidate if candidate.is_absolute() else project_root / candidate
    if solution_path is None:
        return errors

    if not solution_path.exists():
        errors.append(f"textbook solution file does not exist: {solution_path}")
        return errors
    if solution_path.parent.name != "solutions" or not solution_path.name.startswith("solution-"):
        errors.append(f"invalid textbook solution path: {solution_path}")

    expected_name = f"solution-{output_meta.get('lesson_id', '')}.md"
    if solution_path.name != expected_name:
        errors.append(
            "textbook solution filename does not match lesson_id and lesson_name: "
            f"expected {expected_name}, got {solution_path.name}"
        )

    solution_ids, solution_errors = validate_textbook_solution(
        solution_path, output_meta.get("lesson_id", "")
    )
    errors.extend(solution_errors)

    missing_ids = sorted(extract_textbook_question_ids(output_text) - solution_ids)
    if missing_ids:
        errors.append(
            "textbook question_id missing from textbook solution: " + ", ".join(missing_ids)
        )
    if output_meta.get("content_type") in {
        "question_reference",
        "courseware_reference",
        "reference_answer",
    }:
        missing_sources = sorted(textbook_question_ids_missing_answer_source(output_text))
        if missing_sources:
            errors.append(
                "textbook answers must preserve 答案来源 for question_id: "
                + ", ".join(missing_sources)
            )
    return errors
