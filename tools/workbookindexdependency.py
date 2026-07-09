"""Validate workbook index dependencies used by formal outputs."""

from __future__ import annotations

import re
from pathlib import Path


DEPENDENT_CONTENT_TYPES = {
    "lesson",
    "question_dispatch",
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


def extract_exercise_bank_refs(text: str) -> dict[str, set[str]]:
    refs: dict[str, set[str]] = {}
    lines = text.splitlines()
    for index, line in enumerate(lines):
        source_match = re.search(r"source_id\s*:\s*[\"']?(workbook-[^\s\"']+)", line)
        if not source_match:
            continue
        window = "\n".join(lines[index : min(len(lines), index + 16)])
        if not re.search(r"source_type\s*:\s*[\"']?exercise_bank\b", window):
            continue
        source_id = source_match.group(1)
        refs.setdefault(source_id, set())
        single = re.search(r"question_id\s*:\s*[\"']?([A-Za-z0-9_.-]+)", window)
        if single:
            refs[source_id].add(single.group(1))
        list_match = re.search(r"(?m)^(\s*)-?\s*question_ids\s*:\s*$", window)
        if list_match:
            base_indent = len(list_match.group(1))
            for item in window.splitlines()[window[: list_match.start()].count("\n") + 1 :]:
                item_match = re.match(r"^(\s*)-\s*[\"']?([A-Za-z0-9_.-]+)", item)
                if not item_match or len(item_match.group(1)) <= base_indent:
                    break
                refs[source_id].add(item_match.group(2))
    return refs


def extract_index_question_ids(text: str) -> set[str]:
    return set(re.findall(r"\bquestion_id:\s*([A-Za-z0-9_.-]+)", text))


def validate_index_file(path: Path, source_id: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    if not path.exists():
        return set(), [f"workbook index file does not exist: {path}"]
    text = path.read_text(encoding="utf-8")
    meta, _ = parse_front_matter(text)
    if meta.get("content_type") != "workbook_index":
        errors.append("workbook index must have content_type: workbook_index")
    if meta.get("source_type") != "exercise_bank":
        errors.append("workbook index must have source_type: exercise_bank")
    if meta.get("source_id") != source_id:
        errors.append(
            "workbook index source_id does not match downstream reference: "
            f"expected {source_id!r}, got {meta.get('source_id', '')!r}"
        )
    if re.search(r"answer_ref:\s*null", text):
        errors.append("workbook index contains null answer_ref")
    ids = extract_index_question_ids(text)
    if not ids:
        errors.append("workbook index contains no question_id")
    return ids, errors


def validate_dependency(output_path: Path, output_text: str, output_meta: dict[str, str]) -> list[str]:
    if output_meta.get("content_type") not in DEPENDENT_CONTENT_TYPES:
        return []

    exercise_refs = extract_exercise_bank_refs(output_text)
    if not exercise_refs:
        return []

    errors: list[str] = []
    project_root = find_project_root(output_path)
    _, lists = parse_front_matter(output_text)
    source_files = {item.replace("\\", "/") for item in lists.get("source_files", [])}

    for source_id, question_ids in sorted(exercise_refs.items()):
        suffix = source_id.removeprefix("workbook-")
        expected_workbook = f"knowledge/workbooks/{source_id}.md"
        expected_answer = f"knowledge/workbook-answers/workbook-answer-{suffix}.md"
        expected_index = f"knowledge/workbook-index/workbook-index-{suffix}.yaml"

        if expected_workbook not in source_files:
            errors.append(f"source_files must register workbook source: {expected_workbook}")
        if expected_answer not in source_files:
            errors.append(f"source_files must register workbook answer: {expected_answer}")
        if expected_index not in source_files:
            errors.append(f"source_files must register workbook index: {expected_index}")

        for relative in [expected_workbook, expected_answer]:
            if not (project_root / relative).is_file():
                errors.append(f"workbook dependency file does not exist: {project_root / relative}")

        index_ids, index_errors = validate_index_file(project_root / expected_index, source_id)
        errors.extend(index_errors)
        missing_ids = sorted(question_ids - index_ids)
        if missing_ids:
            errors.append(
                "exercise_bank question_id missing from workbook index: "
                + ", ".join(missing_ids)
            )

    return errors
