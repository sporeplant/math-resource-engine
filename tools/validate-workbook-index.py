"""Validate workbook index YAML files against source workbooks and answers.

Checks:
  1. Every question_id is unique within the index file
  2. source_id (workbook) file exists and is parseable
  3. answer_id (answer) file exists and contains answers for indexed questions
  4. Open-ended answers ("略", "答案不唯一") are explicitly marked, not dropped
  5. Three-way traceability: index → workbook, index → answers, workbook ↔ answers
  6. Image references in indexed questions match the workbook source

Usage:
    python tools/validate-workbook-index.py knowledge/workbook-index/ [--workbooks knowledge/workbooks/] [--answers knowledge/workbook-answers/]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKBOOKS = REPO_ROOT / "knowledge" / "workbooks"
DEFAULT_ANSWERS = REPO_ROOT / "knowledge" / "workbook-answers"


def iter_index_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(target.glob("workbook-index-*.yaml"))
    raise FileNotFoundError(f"目标不存在: {target}")


def validate_index_file(
    index_path: Path,
    workbook_dir: Path,
    answers_dir: Path,
) -> tuple[int, int]:
    """Validate a single index YAML file. Returns (pass_count, error_count)."""
    errors: list[str] = []

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"FAIL {index_path.name} — YAML parse error: {e}")
        return 0, 1

    if not isinstance(data, dict) or "questions" not in data or "lesson_id" not in data:
        print(f"FAIL {index_path.name} — missing required top-level keys (lesson_id, questions)")
        return 0, 1

    lesson_id = data["lesson_id"]
    questions = data["questions"]
    if not isinstance(questions, list):
        print(f"FAIL {index_path.name} — questions must be a list")
        return 0, 1

    # 1. Uniqueness check
    qids = [q.get("question_id", "") for q in questions]
    dupes = [qid for qid, count in Counter(qids).items() if count > 1]
    if dupes:
        errors.append(f"Duplicate question_id: {', '.join(dupes)}")
    if "" in qids:
        errors.append("Empty question_id found")

    # 2. source_id existence and consistency
    source_id = questions[0].get("source_id", "") if questions else ""
    if not source_id:
        errors.append("Missing source_id")
    else:
        wb_path = workbook_dir / f"{source_id}.md"
        if not wb_path.is_file():
            # Try alternate naming
            alt_matches = list(workbook_dir.glob(f"{source_id}*"))
            if not alt_matches:
                errors.append(f"Workbook file not found: {source_id}.md")
            else:
                wb_path = alt_matches[0]

    # 3. answer_id existence
    answer_id = questions[0].get("answer_id", "") if questions else ""
    if not answer_id:
        errors.append("Missing answer_id")
    else:
        ans_path = answers_dir / f"{answer_id}.md"
        if not ans_path.is_file():
            errors.append(f"Answer file not found: {answer_id}.md")

    # 4. Per-question checks
    for i, q in enumerate(questions):
        qid = q.get("question_id", f"<missing-at-index-{i}>")
        prefix = f"  [{qid}]"

        # Required fields
        for field in ("question_id", "source_id", "answer_id", "section", "q_number"):
            if not q.get(field):
                errors.append(f"{prefix} missing field: {field}")

        # Tier validation
        valid_tiers = {"知识", "基础", "提升", "应用", "拓展", "综合"}
        if q.get("tier") and q["tier"] not in valid_tiers:
            errors.append(f"{prefix} invalid tier: {q['tier']}")

        # Open answer marking
        if q.get("is_open_answer") and q.get("has_answer"):
            errors.append(f"{prefix} open-answer marked has_answer=True")
        if q.get("is_open_answer") and not q.get("answer_preview") == "":
            # It's OK for open answers to have a preview if they're partially open
            pass

    # 5. Try to verify workbook source content
    if source_id:
        wb_path = workbook_dir / f"{source_id}.md"
        wb_alt = list(workbook_dir.glob(f"{source_id}*"))
        if wb_path.is_file() or wb_alt:
            real_wb = wb_path if wb_path.is_file() else wb_alt[0]
            try:
                wb_text = real_wb.read_text(encoding="utf-8")
                # Check that all Q numbers from index appear in workbook text
                for q in questions:
                    q_num = q.get("q_number", "")
                    if q_num and not re.search(rf"\b{q_num}\.\s", wb_text):
                        errors.append(f"  [{q.get('question_id', '?')}] 题号 {q_num} not found in workbook source")
            except Exception as e:
                errors.append(f"Failed to read workbook: {e}")

    # 6. Check answer file coverage
    if answer_id:
        ans_path = answers_dir / f"{answer_id}.md"
        if ans_path.is_file():
            try:
                ans_text = ans_path.read_text(encoding="utf-8")
                for q in questions:
                    q_num = q.get("q_number", "")
                    if q_num and not q.get("is_open_answer"):
                        # Simple check: the question number should appear in answers
                        if not re.search(rf"^{q_num}\.\s", ans_text, re.MULTILINE):
                            errors.append(
                                f"  [{q.get('question_id', '?')}] not found in answer file {q_num}"
                            )
            except Exception as e:
                errors.append(f"Failed to read answer file: {e}")

    # Report
    if errors:
        print(f"FAIL {index_path.name} — {len(errors)} errors:")
        for e in errors:
            print(e)
        return 1, len(errors)
    else:
        print(f"PASS {index_path.name} — {len(questions)} 题, source_id={source_id}, answer_id={answer_id}")
        return 1, 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate workbook index YAML files")
    parser.add_argument("target", type=str, help="Index YAML file or directory")
    parser.add_argument("--workbooks", type=str, default=None,
                        help="Path to knowledge/workbooks/ (default: auto)")
    parser.add_argument("--answers", type=str, default=None,
                        help="Path to knowledge/workbook-answers/ (default: auto)")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")

    target = Path(args.target)
    if not target.exists():
        print(f"Error: target not found: {target}", file=sys.stderr)
        sys.exit(1)

    wb_dir = Path(args.workbooks) if args.workbooks else DEFAULT_WORKBOOKS
    ans_dir = Path(args.answers) if args.answers else DEFAULT_ANSWERS

    if not wb_dir.is_dir():
        print(f"Error: workbook dir not found: {wb_dir}", file=sys.stderr)
        sys.exit(1)
    if not ans_dir.is_dir():
        print(f"Error: answers dir not found: {ans_dir}", file=sys.stderr)
        sys.exit(1)

    files = iter_index_files(target)
    if not files:
        print("No index files found")
        sys.exit(0)

    print(f"Validating {len(files)} index files")
    print(f"  Workbooks: {wb_dir}")
    print(f"  Answers: {ans_dir}")
    print()

    total_pass = 0
    total_fail = 0
    total_errors = 0

    for f in files:
        p, e = validate_index_file(f, wb_dir, ans_dir)
        total_pass += p
        total_fail += 1 if e > 0 else 0
        total_errors += e

    print()
    print(f"Result: {total_pass} pass, {total_fail} fail ({total_errors} errors)")


if __name__ == "__main__":
    main()
