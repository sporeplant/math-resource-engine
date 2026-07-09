"""Index workbook questions into structured YAML for downstream task routing.

For each workbook lesson (with matching answer file), produce a
knowledge/workbook-index/workbook-index-{lesson}.yaml that records every
question and sub-question with stable identifiers, section labels, tier hints,
image presence, answer location, and a text snippet so that lesson-collab and
courseware skills can reference indexed questions directly.

Usage:
    python tools/index_workbook.py knowledge/workbooks/ knowledge/workbook-answers/ [--outdir knowledge/workbook-index] [--chapter 12]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ANSWERS = REPO_ROOT / "knowledge" / "workbook-answers"
DEFAULT_INDEX = REPO_ROOT / "knowledge" / "workbook-index"

SECTION_TIERS: dict[str, str] = {
    "知识点拨": "知识",
    "夯实基础": "基础",
    "数学思考": "提升",
    "解决问题": "应用",
    "能力拓展": "拓展",
}

QUESTION_TYPE_HINTS: dict[str, str] = {
    "选择": "选择题",
    "填空": "填空题",
    "判断": "判断题",
    "计算": "计算题",
    "化简": "计算题",
    "解": "解答题",
    "证明": "证明题",
    "画": "作图题",
}


def iter_workbooks(workbook_dir: Path, chapter: str | None = None) -> list[Path]:
    """Return sorted workbook-*.md paths, optionally filtered by chapter."""
    paths = sorted(workbook_dir.glob("workbook-*.md"))
    if chapter:
        prefix = f"workbook-{chapter}"
        paths = [p for p in paths if p.stem.startswith(prefix) or p.stem.startswith(f"workbook-ch{chapter}")]
    return paths


def find_answer(workbook_path: Path, answers_dir: Path) -> Path | None:
    """Find matching answer file for a workbook."""
    stem = workbook_path.stem  # e.g. "workbook-12.1-1"
    answer_stem = stem.replace("workbook-", "workbook-answer-", 1)
    answer_path = answers_dir / f"{answer_stem}.md"
    if answer_path.is_file():
        return answer_path
    # Handle ch12-review style
    if "-ch" in stem and "-review" in stem:
        alt_stem = stem.replace("workbook-", "workbook-answer-", 1)
        alt = answers_dir / f"{alt_stem}.md"
        if alt.is_file():
            return alt
    return None


def normalize_lesson_id(stem: str) -> str:
    """Extract normalized lesson id from workbook stem.

    'workbook-12.1-1' -> '12.1-1'
    'workbook-ch12-review' -> 'ch12-review'
    """
    name = stem.replace("workbook-", "", 1)
    return name


def parse_workbook(text: str) -> list[dict]:
    """Parse workbook markdown into a flat list of question descriptors.

    Each descriptor has:
        section: str       - 栏目 name (知识点拨, 夯实基础, etc.)
        q_number: str      - question number (e.g. '1', '2')
        sub_number: str    - sub-question label (e.g. '(1)', '(2)') or ''
        q_type: str        - inferred question type
        text_snippet: str  - first ~80 chars of question body
        has_image: bool
    """
    sections: list[dict] = []  # [{title, start_line, end_line}]
    current_section: dict | None = None
    lines = text.splitlines()

    # Phase 1: split into sections by '# ' headings,
    # but skip question-type labels (e.g. "2. 填空题。" or "3. 计算题。").
    QTYPE_LABEL_RE = re.compile(r"^\d+\.\s+\S+[。.]$")

    for i, line in enumerate(lines):
        if line.startswith("# "):
            heading = line[2:].strip()
            # Skip the lesson title (e.g. "12.1 分式(一)")
            if re.match(r"^\d+\.\d+", heading) or heading.startswith("回顾与反思"):
                if current_section:
                    current_section["end_line"] = i
                    sections.append(current_section)
                current_section = None
                continue
            # Skip question-type labels that belong to their parent section
            if QTYPE_LABEL_RE.match(heading):
                continue
            if current_section:
                current_section["end_line"] = i
                sections.append(current_section)
            current_section = {"title": heading, "start_line": i, "end_line": len(lines)}
    if current_section:
        sections.append(current_section)

    # Phase 2: extract questions from each section
    questions: list[dict] = []
    for sec in sections:
        sec_text = "\n".join(lines[sec["start_line"]:sec["end_line"]])
        # Find numbered questions: lines starting with digit(s) followed by '. '
        q_pattern = re.compile(r"^(\d+)\.\s+(.+)", re.MULTILINE)
        q_matches = list(q_pattern.finditer(sec_text))

        for j, m in enumerate(q_matches):
            q_num = m.group(1)
            q_intro = m.group(2).strip()
            # Determine next question's start position
            next_pos = q_matches[j + 1].start() if j + 1 < len(q_matches) else len(sec_text)
            q_body = sec_text[m.start():next_pos].strip()

            # Detect question type from intro line
            q_type = _infer_type(q_intro.lower())

            # Has image in question body?
            has_image = bool(re.search(r"!\[[^\]]*\]\([^)]+\)", q_body))

            # Extract sub-questions: (1), (2), (3), ①, ② etc.
            sub_pattern = re.compile(r"(?:^|\n)\s*(\(([\d]+)\)|([①②③④⑤⑥⑦⑧]))\s+")
            sub_matches = list(sub_pattern.finditer(q_body))

            if sub_matches:
                for k, sm in enumerate(sub_matches):
                    sub_label = sm.group(2) if sm.group(2) else sm.group(3)
                    # Extract sub-question text
                    sub_next = sub_matches[k + 1].start() if k + 1 < len(sub_matches) else len(q_body)
                    sub_body = q_body[sm.start():sub_next].strip()
                    sub_has_image = bool(re.search(r"!\[[^\]]*\]\([^)]+\)", sub_body))

                    questions.append({
                        "section": sec["title"],
                        "q_number": q_num,
                        "sub_number": sub_label,
                        "q_type": q_type,
                        "text_snippet": sub_body[:120].replace("\n", " "),
                        "has_image": has_image or sub_has_image,
                    })
            else:
                questions.append({
                    "section": sec["title"],
                    "q_number": q_num,
                    "sub_number": "",
                    "q_type": q_type,
                    "text_snippet": q_body[:(q_body.index("\n") + 80) if "\n" in q_body else 80].replace("\n", " "),
                    "has_image": has_image,
                })

    return questions


def _infer_type(intro: str) -> str:
    """Infer question type from intro text."""
    for keyword, qtype in QUESTION_TYPE_HINTS.items():
        if keyword in intro:
            return qtype
    # Check for structured sub-questions that indicate a 解答题
    if re.search(r"[\(（]\d+[\)）]", intro):
        return "解答题"
    return "解答题"


def parse_answers(text: str) -> dict[str, str]:
    """Parse answer file into a dict mapping question keys to answer text.

    Keys are like '1', '1(1)', '2', '2(1)', etc.
    Detects open-ended answers ('略', '答案不唯一').
    """
    # Remove YAML front matter
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL).strip()
    lines = text.splitlines()
    answers: dict[str, str] = {}

    # Pattern for answer blocks: line starts with digit, followed by '. '
    q_line = re.compile(r"^(\d+)\.\s+(.*)")
    sub_line = re.compile(r"^\((\d+)\)\s+(.*)")
    circ_line = re.compile(r"^([①②③④⑤⑥⑦⑧])\s+(.*)")

    current_q = ""
    in_answer = False
    answer_buffer: list[str] = []

    def flush_answer(qkey: str, value: str):
        nonlocal answer_buffer
        if qkey and value.strip():
            answers[qkey] = value.strip()
        answer_buffer = []

    for line in lines:
        # Skip section headings
        if line.startswith("# "):
            continue

        m_q = q_line.match(line)
        m_sub = sub_line.match(line)
        m_circ = circ_line.match(line)

        if m_q:
            flush_answer(current_q, " ".join(answer_buffer))
            current_q = m_q.group(1)
            answer_buffer = [m_q.group(2)]
            # Also record the top-level answer
            answers[current_q] = m_q.group(2).strip()
        elif m_sub and current_q:
            # Flush previous sub-answer
            sub_key = f"{current_q}({m_sub.group(1)})"
            answers[sub_key] = m_sub.group(2).strip()
        elif m_circ and current_q:
            circ_map = {"①": "1", "②": "2", "③": "3", "④": "4", "⑤": "5", "⑥": "6", "⑦": "7", "⑧": "8"}
            sub_key = f"{current_q}({circ_map[m_circ.group(1)]})"
            answers[sub_key] = m_circ.group(2).strip()
        elif current_q and line.strip():
            answer_buffer.append(line.strip())

    flush_answer(current_q, " ".join(answer_buffer))

    # Post-process: expand inline sub-answers like "(1)B (2)C" from top-level answers
    inline_sub_re = re.compile(r'\((\d+)\)\s*([^)]+?)(?=\s*\(|$)')
    expanded: dict[str, str] = {}
    for key, val in list(answers.items()):
        if re.search(r'\(\d+\)', val):
            for m in inline_sub_re.finditer(val):
                sub_key = f'{key}({m.group(1)})'
                sub_val = m.group(2).strip()
                if sub_key not in answers:
                    expanded[sub_key] = sub_val
    answers.update(expanded)

    return answers


def is_open_answer(text: str) -> bool:
    """Check if an answer is open-ended."""
    t = text.strip()
    return not t or t in ("略", "答案不唯一") or "略" in t.split("。")[0] or "答案不唯一" in t


def build_index(workbook_path: Path, answer_path: Path | None, outdir: Path) -> list[dict]:
    """Build index entries for one workbook-answer pair."""
    wb_text = workbook_path.read_text(encoding="utf-8")
    questions = parse_workbook(wb_text)

    answers: dict[str, str] = {}
    if answer_path and answer_path.is_file():
        ans_text = answer_path.read_text(encoding="utf-8")
        answers = parse_answers(ans_text)

    lesson_id = normalize_lesson_id(workbook_path.stem)
    source_id = workbook_path.stem  # e.g. "workbook-12.1-1"
    answer_id = f"workbook-answer-{lesson_id}"

    # Determine chapter prefix for question_id
    ch_part = lesson_id.split("-")[0]  # "12.1" or "ch12"
    if ch_part.startswith("ch"):
        ch_prefix = ch_part[2:]  # "12"
    else:
        ch_prefix = ch_part.split(".")[0]  # "12"

    entries: list[dict] = []
    seq = 0

    for q in questions:
        seq += 1
        qid = f"WB-{ch_prefix}-Q{seq:04d}"
        q_key = q["q_number"]
        if q["sub_number"]:
            q_key = f"{q['q_number']}({q['sub_number']})"

        ans_text = answers.get(q_key, "")
        tier = SECTION_TIERS.get(q["section"], "综合")

        entries.append({
            "question_id": qid,
            "source_id": source_id,
            "answer_id": answer_id,
            "section": q["section"],
            "q_number": q["q_number"],
            "sub_number": q["sub_number"],
            "q_type": q["q_type"],
            "tier": tier,
            "has_image": q["has_image"],
            "has_answer": bool(ans_text and not is_open_answer(ans_text)),
            "is_open_answer": bool(is_open_answer(ans_text)),
            "answer_preview": ans_text[:80] if ans_text and not is_open_answer(ans_text) else "",
            "text_snippet": q["text_snippet"],
        })

    return entries


def write_index(entries: list[dict], lesson_id: str, outdir: Path) -> Path:
    """Write index entries to a YAML file."""
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / f"workbook-index-{lesson_id}.yaml"
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(
            {"lesson_id": lesson_id, "questions": entries},
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Index workbook questions into structured YAML")
    parser.add_argument("workbook_dir", type=str, help="Path to knowledge/workbooks/")
    parser.add_argument("answers_dir", type=str, nargs="?", default=None,
                        help="Path to knowledge/workbook-answers/ (default: auto)")
    parser.add_argument("--outdir", type=str, default=None,
                        help="Output directory (default: knowledge/workbook-index/)")
    parser.add_argument("--chapter", type=str, default=None,
                        help="Limit to a specific chapter (e.g. '12')")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    # Ensure UTF-8 output on Windows
    sys.stdout.reconfigure(encoding="utf-8")

    wb_dir = Path(args.workbook_dir)
    if not wb_dir.is_dir():
        print(f"Error: workbook dir not found: {wb_dir}", file=sys.stderr)
        sys.exit(1)

    ans_dir = Path(args.answers_dir) if args.answers_dir else DEFAULT_ANSWERS
    if not ans_dir.is_dir():
        print(f"Error: answers dir not found: {ans_dir}", file=sys.stderr)
        sys.exit(1)

    outdir = Path(args.outdir) if args.outdir else DEFAULT_INDEX

    workbooks = iter_workbooks(wb_dir, args.chapter)
    if not workbooks:
        print(f"No workbook files found (chapter={args.chapter or 'all'})")
        sys.exit(0)

    print(f"Found {len(workbooks)} workbook files")
    print(f"Output dir: {outdir}")
    print()

    indexed = 0
    skipped = 0
    missing_answers: list[str] = []

    for wb_path in workbooks:
        lesson_id = normalize_lesson_id(wb_path.stem)
        ans_path = find_answer(wb_path, ans_dir)

        if ans_path is None:
            missing_answers.append(lesson_id)
            print(f"  WARN {wb_path.name} - no matching answer file, skipped")
            skipped += 1
            continue

        entries = build_index(wb_path, ans_path, outdir)
        out_path = write_index(entries, lesson_id, outdir)
        q_count = len(entries)
        open_count = sum(1 for e in entries if e.get("is_open_answer"))
        print(f"  OK {out_path.name} - {q_count} questions" + (f" ({open_count} open-answer)" if open_count else ""))
        indexed += 1

    print()
    print(f"Done: {indexed} indexed, {skipped} skipped")
    if missing_answers:
        print(f"Missing answers: {', '.join(missing_answers)}")


if __name__ == "__main__":
    main()
