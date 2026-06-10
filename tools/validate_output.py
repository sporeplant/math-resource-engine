#!/usr/bin/env python3
"""Validate hard rules for math-resource-engine Markdown outputs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


FORBIDDEN_TERMS = ["理解", "掌握", "了解", "体会", "感受", "知道"]
REQUIRED_LAYERS = ["基础层", "中间层", "拓展层"]
VALID_REVIEW_STATUS = {"draft", "pending_human_review", "human_approved", "rejected"}
VALID_LESSON_COMMANDS = {"lesson", "lesson-collab"}
QUESTION_HINTS = ["题目", "例题", "练习", "作业", "评价任务"]
VALID_EMOJIS = {"📐", "🎯", "📖", "✏️", "📝", "💡", "🤔", "💬"}
VALID_COURSEWARE_COMMANDS = {"courseware", "courseware-collab"}
PAGE_BREAK = '<div style="page-break-after: always;"></div>'
MAX_EMOJIS_PER_PAGE = 1
MAX_MERMAID_NODES = 6
MAX_LINES_PER_PAGE = 7
MIN_PAGES = 5
MAX_PAGES = 30
INLINE_STUDENT_QUESTION = re.compile(r"请[^\n：:]{1,12}同学(?:回答|代表发言)?[：:]\S+")


class Page(NamedTuple):
    """A single page in the courseware."""
    content: str
    start_line: int
    end_line: int


def split_pages(text: str) -> list[Page]:
    """Split courseware text into individual pages using page breaks."""
    lines = text.splitlines(keepends=True)
    pages: list[Page] = []
    current_start = 0
    for i, line in enumerate(lines):
        if PAGE_BREAK in line:
            pages.append(Page("".join(lines[current_start:i+1]), current_start, i))
            current_start = i + 1
    if current_start < len(lines):
        pages.append(Page("".join(lines[current_start:]), current_start, len(lines)-1))
    return pages


def count_emojis(text: str) -> int:
    """Count emoji characters in text."""
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
    return len(emoji_pattern.findall(text))


def extract_mermaid_diagrams(text: str) -> list[str]:
    """Extract mermaid diagram code blocks from text."""
    mermaid_blocks = re.findall(r'```mermaid\s*([\s\S]*?)\s*```', text)
    return mermaid_blocks


def count_mermaid_nodes(mermaid_code: str) -> int:
    """Count nodes in a mermaid flowchart (approximate)."""
    # Count lines that look like node definitions
    node_lines = re.findall(r'^\s*[A-Za-z0-9_\-]+\s*\[.*?\]', mermaid_code, re.MULTILINE)
    node_lines2 = re.findall(r'^\s*[A-Za-z0-9_\-]+\s*\(.*?\)', mermaid_code, re.MULTILINE)
    return len(node_lines) + len(node_lines2)


def extract_title_emoji(page_content: str) -> str | None:
    """Extract the emoji from the page title (first heading)."""
    heading_match = re.search(r'^#{1,3}\s*([\U00010000-\U0010ffff])', page_content, re.MULTILINE)
    if heading_match:
        return heading_match.group(1)
    return None


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


def strip_front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    return text[end + 4:].lstrip()


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

    if meta.get("content_type") == "lesson" and re.search(r"请\[[^\]]+\]同学", text):
        errors.append("lesson design must not contain concrete student names in questions")


def check_courseware(text: str, meta: dict[str, str], errors: list[str], lesson_file: Path | None) -> None:
    if meta.get("content_type") != "courseware":
        return
    if meta.get("command") not in VALID_COURSEWARE_COMMANDS:
        errors.append("courseware output must have command: courseware or courseware-collab")

    pages = split_pages(text)

    # Check A组结构合规
    check_courseware_group_a(text, pages, errors)

    # Check B组内容合规
    check_courseware_group_b(text, pages, errors)

    # Check upstream lesson file
    if lesson_file:
        lesson_meta = parse_front_matter(read_text(lesson_file))
        if lesson_meta.get("content_type") != "lesson":
            errors.append("upstream lesson file must have content_type: lesson")
        if lesson_meta.get("review_status") != "human_approved":
            errors.append("upstream lesson must be review_status: human_approved")
        if lesson_meta.get("lesson_id") and meta.get("lesson_id") != lesson_meta.get("lesson_id"):
            errors.append("courseware lesson_id does not match upstream lesson")


def check_courseware_group_a(text: str, pages: list[Page], errors: list[str]) -> None:
    """Check courseware Group A rules (structure compliance)."""
    first_page_body = strip_front_matter(pages[0].content) if pages else ""
    # Rule 1: Title page exists with 📐
    if len(pages) < 1 or "📐" not in first_page_body:
        errors.append("courseware missing title page with 📐 emoji")
    else:
        if not any("📐" in line for line in first_page_body.splitlines()[0:10]):
            errors.append("title page should have 📐 emoji near the top")

    # Rule 2: Learning objectives page exists
    has_objectives = any("目标" in page.content for page in pages)
    if not has_objectives:
        errors.append("courseware missing learning objectives page")

    # Rule 3: Four-page example structure check (at least one example)
    example_pattern = re.compile(r'题目.*提问.*推理.*证明', re.DOTALL)
    has_example_structure = bool(example_pattern.search(text))
    # This is a softer check - we don't fail on it but we can warn if needed

    # Rule 4: Summary with three questions (三问三答)
    has_summary_table = bool(re.search(r'层次.*问题', text)) and ("基础层" in text and "中间层" in text and "拓展层" in text)
    if not has_summary_table:
        errors.append("courseware missing 三问三答 summary table (基础层/中间层/拓展层)")

    # Rule 5: Homework page exists (必做/选作/挑战)
    has_homework = "必做" in text and ("选作" in text or "挑战" in text)
    if not has_homework:
        errors.append("courseware missing homework page with 必做/选作/挑战 categories")

    # Rule 6: Page breaks exist
    if PAGE_BREAK not in text:
        errors.append("courseware missing page break dividers")

    # Rule 7: Page count in reasonable range
    if len(pages) < MIN_PAGES:
        errors.append(f"courseware too few pages: {len(pages)}, min {MIN_PAGES}")
    if len(pages) > MAX_PAGES:
        errors.append(f"courseware too many pages: {len(pages)}, max {MAX_PAGES}")


def check_courseware_group_b(text: str, pages: list[Page], errors: list[str]) -> None:
    """Check courseware Group B rules (content compliance)."""
    group_b_violations = 0

    inline_question = INLINE_STUDENT_QUESTION.search(text)
    if inline_question:
        errors.append(
            f"question must appear before student name on separate lines: {inline_question.group(0)}"
        )
        group_b_violations += 1

    for i, page in enumerate(pages, 1):
        # Rule B1: Max 1 emoji per page
        emoji_count = count_emojis(page.content)
        if emoji_count > MAX_EMOJIS_PER_PAGE:
            errors.append(f"page {i}: too many emojis ({emoji_count}), max {MAX_EMOJIS_PER_PAGE}")
            group_b_violations += 1

        # Rule B2: Title has valid emoji
        title_emoji = extract_title_emoji(page.content)
        if title_emoji and title_emoji not in VALID_EMOJIS:
            errors.append(f"page {i}: invalid title emoji {title_emoji}, should be one of {sorted(VALID_EMOJIS)}")
            group_b_violations += 1

        # Rule B3: Mermaid diagram node count <= 6
        mermaid_blocks = extract_mermaid_diagrams(page.content)
        for j, mermaid_code in enumerate(mermaid_blocks, 1):
            node_count = count_mermaid_nodes(mermaid_code)
            if node_count > MAX_MERMAID_NODES:
                errors.append(f"page {i}: mermaid diagram {j} has {node_count} nodes, max {MAX_MERMAID_NODES}")
                group_b_violations += 1

        # Rule B4: No consecutive pure text pages > 3
        # This is checked globally later

        # Rule B5: Time limit format check
        has_time_limit = bool(re.search(r'（\s*限时\s*\d+\s*分钟\s*）', page.content))
        has_activity = any(keyword in page.content for keyword in ["✏️", "🗣️", "小组讨论"])
        if has_activity and not has_time_limit and "课堂检测" not in page.content and "小结" not in page.content:
            # Soft check - don't count as violation for now
            pass

        # Rule B6: Scoring annotation check
        has_scoring = bool(re.search(r'评分[:：]', page.content))
        has_exercise = any(keyword in page.content for keyword in ["练习", "检测", "作业"])
        if has_exercise and not has_scoring:
            # Soft check
            pass

        # Rule B7: Question format check
        question_format_ok = True
        question_matches = re.findall(r'【.*?层提问】', page.content)
        if question_matches:
            for q_match in question_matches:
                if not re.match(r'【(基础|中间|拓展)层提问】', q_match):
                    errors.append(f"page {i}: invalid question format: {q_match}")
                    group_b_violations += 1
                    question_format_ok = False

        # Rule B8: No teacher/student action prompts
        if "教师：" in page.content or "学生：" in page.content:
            errors.append(f'page {i}: contains teacher/student action prompts ("教师：" or "学生：")')
            group_b_violations += 1

    # Check consecutive pure text pages globally
    consecutive_text_pages = 0
    for page in pages:
        has_visual = bool(re.search(r'```mermaid|<img|!\[', page.content))
        if not has_visual:
            consecutive_text_pages += 1
            if consecutive_text_pages > 3:
                errors.append(f"more than 3 consecutive pure text pages (no mermaid/images)")
                group_b_violations += 1
                break
        else:
            consecutive_text_pages = 0

    # Rule B9: No numbered steps in proofs (1. 2. 3.)
    proof_step_pattern = re.compile(r'^\s*\d+\.\s+', re.MULTILINE)
    if proof_step_pattern.search(text):
        errors.append("proof/calculation steps should not use numbered lists (1. 2. 3.)")
        group_b_violations += 1

    # If Group B violations >=3, mark as failed
    if group_b_violations >= 3:
        errors.append(f"Group B violations: {group_b_violations} (>=3)")


def check_reference_answer(text: str, meta: dict[str, str], errors: list[str]) -> None:
    """Check reference answer document rules."""
    if meta.get("content_type") not in ["courseware_reference", "reference_answer"]:
        return

    # Group A: Mandatory checks (fail on any)
    group_a_errors = []

    # Rule A1: Metadata complete
    required_meta = ["content_type", "lesson_id", "lesson_name", "source_files", "created_at"]
    for key in required_meta:
        if key not in meta or not meta[key]:
            group_a_errors.append(f"missing metadata: {key}")

    # Rule A2: Title correct
    title_pattern = re.compile(r'^#\s+.+?\s+课堂提问参考答案', re.MULTILINE)
    if not title_pattern.search(text):
        group_a_errors.append("missing or incorrect title: should be '{lesson_name} 课堂提问参考答案'")

    # Rule A3: Random pool selection record exists and is table
    if "随机池选取记录" not in text:
        group_a_errors.append("missing random pool selection record section")
    else:
        table_pattern = re.compile(r'\|.*选取学生.*\|', re.MULTILINE)
        if not table_pattern.search(text):
            group_a_errors.append("random pool selection record should be a table")

    # Rule A4: Section A exists
    if "板块A" not in text and "【板块A】" not in text:
        group_a_errors.append("missing 【板块A】ASK课堂提问参考答案 section")

    # Rule A5: Section B exists
    if "板块B" not in text and "【板块B】" not in text:
        group_a_errors.append("missing 【板块B】例题与练习解答 section")

    # Rule A6: Scoring rubric exists and is table
    if "评分量规" not in text:
        group_a_errors.append("missing 评分量规 section")
    else:
        rubric_table_pattern = re.compile(r'\|.*维度.*评分标准.*\|', re.MULTILINE)
        if not rubric_table_pattern.search(text):
            group_a_errors.append("scoring rubric should be a table")

    # Rule A7: All questions have source annotations
    question_source_pattern = re.compile(r'source_id.*source_type.*question_id', re.DOTALL)
    if not question_source_pattern.search(text):
        # Check individual questions
        question_count = len(re.findall(r'(题目|例题|练习|问题)', text))
        source_count = len(re.findall(r'source_id|source_type|question_id', text))
        if question_count > 0 and source_count < question_count // 2:
            group_a_errors.append("questions missing source annotations (source_id/source_type/question_id)")

    # Rule A8: Math formulas use LaTeX
    latex_pattern = re.compile(r'\$.*?\$')
    formula_pattern = re.compile(r'[+\-×÷=≠≤≥≈√∑∫∞π]')
    has_formulas = bool(formula_pattern.search(text))
    has_latex = bool(latex_pattern.search(text))
    if has_formulas and not has_latex:
        group_a_errors.append("math formulas should use LaTeX format ($...$)")

    # Add Group A errors to main errors
    for err in group_a_errors:
        errors.append(f"[Group A] {err}")

    # Group B: Quality checks (count violations, fail if >=4)
    group_b_violations = 0

    # Rule B1: Section A has three layers
    has_all_layers = "基础层" in text and "中间层" in text and "拓展层" in text
    if not has_all_layers:
        errors.append("[Group B] missing layer sections in 板块A (基础层/中间层/拓展层)")
        group_b_violations += 1

    # Rule B2: Question ID format correct
    question_ids = re.findall(r'ASK-[BME]-\d+', text)
    for qid in question_ids:
        if not re.match(r'ASK-[BME]-\d{2}', qid):
            errors.append(f"[Group B] invalid question ID format: {qid}, should be ASK-[BME]-XX")
            group_b_violations += 1

    # Rule B3: Answers have clear bullet points
    answer_sections = re.findall(r'参考答案[\s\S]*?(?=\n\n##|\n\n---|$)', text)
    for ans in answer_sections:
        bullet_count = len(re.findall(r'^[-*]\s+', ans, re.MULTILINE))
        if bullet_count < 2 and len(ans.splitlines()) > 5:
            errors.append("[Group B] answer should have clear bullet points (3-5 points recommended)")
            group_b_violations += 1
            break

    # Rule B4: Scoring points are clear and quantifiable
    scoring_sections = re.findall(r'评分要点[\s\S]*?(?=\n\n##|\n\n---|$)', text)
    for scoring in scoring_sections:
        has_points = bool(re.search(r'\d+.*分', scoring))
        if not has_points:
            errors.append("[Group B] scoring points should be clear and quantifiable (with scores)")
            group_b_violations += 1
            break

    # Rule B5: Total pages control (approximate by line count)
    lines = text.splitlines()
    estimated_pages = len(lines) // 40  # Rough estimate
    if estimated_pages > 6:
        errors.append(f"[Group B] document too long (estimated {estimated_pages} pages), should be ≤6 pages")
        group_b_violations += 1

    # Rule B6: Scoring rubric has dimensions
    has_dimensions = all(dim in text for dim in ["准确性", "完整性", "表达力"])
    if not has_dimensions:
        errors.append("[Group B] scoring rubric should have dimensions: 准确性/完整性/表达力")
        group_b_violations += 1

    # Rule B7: Section B covers examples and exercises from lesson flow
    # This is a softer check - we just verify section B exists with some content
    section_b_content = re.search(r'板块B[\s\S]*?(?=评分量规|$)', text, re.DOTALL)
    if section_b_content and len(section_b_content.group(0).strip()) < 100:
        errors.append("[Group B] 板块B content too thin, should cover examples and exercises")
        group_b_violations += 1

    # Rule B8: Answers show complete reasoning for step problems
    # Check for answers that have multiple steps
    multi_step_pattern = re.compile(r'首先|然后|接着|最后|1\.|2\.|3\.|第一步|第二步', re.MULTILINE)
    has_multi_step = bool(multi_step_pattern.search(text))
    if not has_multi_step and len(text) > 1000:
        # Only warn if document is long enough to have multi-step problems
        pass  # Soft check

    # Rule B9: Math terminology is standard
    # This is hard to check automatically, skip for now

    if group_b_violations >= 4:
        errors.append(f"[Group B] violations: {group_b_violations} (>=4)")


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


def check_learning_objectives(text: str, meta: dict[str, str], errors: list[str]) -> None:
    """Check learning objectives rules."""
    # Only check learning objectives for lesson content type
    if meta.get("content_type") != "lesson":
        return
    
    # First, find objectives section
    objectives_section = re.search(r'## objectives[\s\S]*?(?=## assessment|## 问题链设计|$)', text, re.DOTALL)
    if not objectives_section:
        # Try alternative pattern
        objectives_section = re.search(r'(### 基础层[\s\S]*?(?=## assessment|## 问题链设计|$))', text, re.DOTALL)

    if not objectives_section:
        # No objectives section found, skip detailed checks
        # Check if it's a lesson document that should have objectives
        if meta.get("content_type") == "lesson":
            errors.append("missing objectives section not found")
        return

    obj_text = objectives_section.group(0)

    # Valid action verbs by level (from skill definition)
    basic_verbs = {"说出", "辨认", "识别", "回忆", "复述", "写出", "画出", "计算", "模仿", "画出", "陈述", "列举", "匹配", "选择"}
    intermediate_verbs = {"解释", "说明", "归纳", "概括", "比较", "分类", "推断", "转化", "改写", "完成", "解决", "证明", "描述", "阐述", "应用", "演绎"}
    advanced_verbs = {"分析", "评价", "创造", "设计", "构建", "生成", "假设", "论证", "批判", "综合", "鉴赏", "策划", "创新", "发明", "推导"}
    all_valid_verbs = basic_verbs | intermediate_verbs | advanced_verbs

    # Check each layer
    for layer_name, layer_verbs, layer_header in [
        ("基础层", basic_verbs, r'### 基础层'),
        ("中间层", intermediate_verbs, r'### 中间层'),
        ("拓展层", advanced_verbs, r'### 拓展层')
    ]:
        # Find layer section
        layer_match = re.search(rf'{layer_header}[\s\S]*?(?=### |## |$)', obj_text, re.DOTALL)
        if not layer_match:
            errors.append(f"missing {layer_name} objectives section")
            continue

        layer_content = layer_match.group(0)

        # Extract objectives (look for LO-[BME]-XX pattern or bullet points
        objectives = re.findall(r'[-*]\s*(?:LO-[BME]-\d+[：:]\s*([^\n]+)|([^\n]+))', layer_content)
        objectives = [obj[0] or obj[1] for obj in objectives if obj[0] or obj[1]]

        # Check each objective
        obj_count = 0
        for obj in objectives:
            obj_count += 1

            # Rule 1: Contains "能" (can have preamble before it)
            if "能" not in obj:
                errors.append(f"{layer_name} objective should contain '能': {obj[:50]}...")

            # Rule 2: Has valid action verb
            has_valid_verb = any(verb in obj for verb in all_valid_verbs)
            if not has_valid_verb:
                errors.append(f"{layer_name} objective missing valid action verb: {obj[:50]}...")

            # Rule 3: No forbidden terms already checked in check_common

    total_objectives = len(re.findall(r'[-*]\s*`?LO-[BME]-\d+`?[：:]', obj_text))
    if total_objectives > 6:
        errors.append(f"too many learning objectives ({total_objectives}); total must be 6 or fewer")

    # Check overall: Objectives support后续评价 design
    has_assessment = "## assessment" in text or "### 基础层评价" in text
    meta_type = meta.get("content_type")
    if meta_type == "lesson" and not has_assessment:
        errors.append("missing assessment section (should follow objectives)")


def validate_courseware_textbook_consistency(
    courseware_path: Path,
    errors: list[str],
    warnings: list[str]
) -> None:
    """Validate courseware against textbook source for consistency."""
    try:
        # Try to import the consistency validator
        from validate_courseware_consistency import (
            validate as validate_consistency,
        )
        from pathlib import Path

        courseware_text = read_text(courseware_path)
        meta = parse_front_matter(courseware_text)
        if meta.get("content_type") == "courseware":
            # Auto-find textbook
            courseware_dir = courseware_path.parent
            textbook_dir = courseware_dir.parent / "知识库" / "教材原文"
            lesson_name = meta.get("lesson_name", "")

            textbook_path = None
            # Common filename patterns
            patterns = [
                f"*{lesson_name}*.md",
                "*22.1*.md",
                "*统计*.md",
                "*数据*.md"
            ]
            for pattern in patterns:
                matches = list(textbook_dir.glob(pattern))
                if matches:
                    textbook_path = matches[0]
                    break

            if textbook_path and textbook_path.exists():
                cons_errors, cons_warnings = validate_consistency(
                    courseware_path,
                    textbook_path,
                    auto_find=False
                )
                errors.extend([f"[Consistency] {e}" for e in cons_errors])
                warnings.extend([f"[Consistency] {w}" for w in cons_warnings])

    except ImportError:
        pass  # If consistency validator not available, skip
    except Exception as e:
        warnings.append(f"[Consistency check failed: {e}]")


def validate_activity_textbook_order(
    lesson_path: Path,
    errors: list[str],
    warnings: list[str],
    textbook_file: Path | None = None,
) -> None:
    """Validate that teaching activities follow textbook section order.

    If textbook_file is not provided, auto-find from lesson's front matter source_files.
    """
    lesson_text = read_text(lesson_path)
    lesson_meta = parse_front_matter(lesson_text)

    has_lesson_flow = "## lesson_flow" in lesson_text
    has_position_field = "教材对应位置" in lesson_text

    if not has_lesson_flow:
        warnings.append("[ActivityOrder] lesson_flow section not found, skipping textbook order check")
        return

    if not has_position_field:
        warnings.append("[ActivityOrder] 教学设计中未找到'教材对应位置'字段，跳过教材顺序检查")
        return

    project_root = lesson_path.parent.parent

    if textbook_file is None:
        source_files = lesson_meta.get("source_files", "")
        if source_files:
            for src in source_files.split(","):
                src = src.strip().strip('"').strip("'")
                if "教材原文" in src:
                    textbook_path = project_root / src
                    if textbook_path.exists():
                        textbook_file = textbook_path
                        break

    if textbook_file is None:
        textbook_dir = project_root / "知识库" / "教材原文"
        if textbook_dir.exists():
            lesson_name = lesson_meta.get("lesson_name", "")
            patterns = [f"*{lesson_name.replace('.', '').replace('(', '').replace(')', '')}*.md", "*.md"]
            for pattern in patterns:
                matches = sorted(textbook_dir.glob(pattern))
                if matches:
                    textbook_file = matches[0]
                    break

    if textbook_file is None or not textbook_file.exists():
        warnings.append("[ActivityOrder] 无法定位教材原文文件，跳过教材顺序检查")
        return

    try:
        from validate_activity_textbook_order import (
            validate as validate_order,
        )
        order_errors, order_warnings = validate_order(lesson_path, textbook_file)
        errors.extend([f"[ActivityOrder] {e}" for e in order_errors])
        warnings.extend([f"[ActivityOrder] {w}" for w in order_warnings])
    except ImportError:
        pass
    except Exception as e:
        warnings.append(f"[ActivityOrder check failed: {e}]")


def validate(path: Path, lesson_file: Path | None, question_reference: Path | None, students_file: Path | None, textbook_file: Path | None = None) -> tuple[list[str], list[str]]:
    text = read_text(path)
    errors: list[str] = []
    warnings: list[str] = []
    meta = check_common(path, text, errors)
    check_lesson(text, meta, errors)
    check_courseware(text, meta, errors, lesson_file)
    check_reference_answer(text, meta, errors)
    check_learning_objectives(text, meta, errors)

    if question_reference:
        check_question_reference(read_text(question_reference), errors, students_file)
    elif meta.get("content_type") == "question_reference":
        check_question_reference(text, errors, students_file)

    # Add textbook consistency check for courseware
    if meta.get("content_type") == "courseware":
        validate_courseware_textbook_consistency(path, errors, warnings)

    # Add activity-textbook-order check for lesson
    if meta.get("content_type") == "lesson":
        validate_activity_textbook_order(path, errors, warnings, textbook_file)

    return errors, warnings


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

    errors, warnings = validate(args.file, args.lesson_file, args.question_reference, args.students_file, args.textbook_file)

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
        print()

    if errors:
        print("Validation FAILED:")
        for error in errors:
            print(f"  ❌ {error}")
        return 1

    if not warnings:
        print("✅ Validation PASSED")
    else:
        print("⚠️  Validation passed with warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
