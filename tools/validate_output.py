#!/usr/bin/env python3
"""Validate hard rules for math-resource-engine Markdown outputs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

try:
    from textbook_solution_dependency import validate_dependency
except ModuleNotFoundError:
    from tools.textbook_solution_dependency import validate_dependency

try:
    from workbookindexdependency import validate_dependency as validate_workbook_dependency
except ModuleNotFoundError:
    from tools.workbookindexdependency import validate_dependency as validate_workbook_dependency

try:
    from validate_review_lesson import validate as validate_review_lesson_file
except ModuleNotFoundError:
    from tools.validate_review_lesson import validate as validate_review_lesson_file

try:
    from review_math_utils import validate_math_markup
except ModuleNotFoundError:
    from tools.review_math_utils import validate_math_markup


FORBIDDEN_TERMS = ["理解", "掌握", "了解", "熟悉", "体会", "感受", "知道"]
REQUIRED_LAYERS = ["基础层", "中间层", "拓展层"]
LAYER_REQUIRED_CONTENT_TYPES = {
    "lesson",
    "question_reference",
    "courseware_reference",
    "reference_answer",
    "textbook_solution",
}
VALID_REVIEW_STATUS = {"draft", "pending_human_review", "审核通过", "rejected"}
VALID_LESSON_COMMANDS = {"lesson-collab"}
QUESTION_HINTS = ["题目", "例题", "练习", "作业", "评价任务"]
VALID_EMOJIS = {"📐", "🎯", "📖", "✏️", "📝", "💡", "🤔", "💬"}
VALID_COURSEWARE_COMMANDS = {"courseware-collab"}
PAGE_BREAK = "---"
MAX_EMOJIS_PER_PAGE = 1
MAX_MERMAID_NODES = 6
MAX_LINES_PER_PAGE = 10
MIN_PAGES = 5
MAX_PAGES = 50
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
        if line.strip() == PAGE_BREAK:
            pages.append(Page("".join(lines[current_start : i + 1]), current_start, i))
            current_start = i + 1
    if current_start < len(lines):
        pages.append(
            Page("".join(lines[current_start:]), current_start, len(lines) - 1)
        )
    return pages


LEVEL_EMOJIS = {"🌱", "🌿", "🌳"}


def count_emojis(text: str, exclude_level: bool = False) -> int:
    """Count emoji characters in text.

    When exclude_level is True, level markers (🌱🌿🌳) are not counted;
    they are not page-type emojis per skills/courseware/SKILL.md §2a-1.
    """
    emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
    matches = emoji_pattern.findall(text)
    if exclude_level:
        matches = [m for m in matches if m not in LEVEL_EMOJIS]
    return len(matches)


def extract_mermaid_diagrams(text: str) -> list[str]:
    """Extract mermaid diagram code blocks from text."""
    mermaid_blocks = re.findall(r"```mermaid\s*([\s\S]*?)\s*```", text)
    return mermaid_blocks


def count_mermaid_nodes(mermaid_code: str) -> int:
    """Count nodes in a mermaid flowchart (approximate)."""
    # Count lines that look like node definitions
    node_lines = re.findall(
        r"^\s*[A-Za-z0-9_\-]+\s*\[.*?\]", mermaid_code, re.MULTILINE
    )
    node_lines2 = re.findall(
        r"^\s*[A-Za-z0-9_\-]+\s*\(.*?\)", mermaid_code, re.MULTILINE
    )
    return len(node_lines) + len(node_lines2)


def extract_title_emoji(page_content: str, skip_level: bool = True) -> str | None:
    """Extract the page-type emoji from the page title (first heading).

    When skip_level is True, level markers (🌱🌿🌳) are skipped and the next
    emoji (the page-type emoji) is returned, per skills/courseware/SKILL.md §2a-1.
    """
    heading_match = re.search(
        r"^#{1,3}\s*([\U00010000-\U0010ffff])", page_content, re.MULTILINE
    )
    if not heading_match:
        return None
    first_emoji = heading_match.group(1)
    if skip_level and first_emoji in LEVEL_EMOJIS:
        rest = page_content[heading_match.end():]
        next_match = re.search(r"([\U00010000-\U0010ffff])", rest)
        if next_match:
            return next_match.group(1)
        return None
    return first_emoji


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
    pending_list_key: str | None = None
    for line in block.splitlines():
        if pending_list_key and line.lstrip().startswith("-"):
            meta[pending_list_key] = "list"
            continue
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        meta[key] = value
        pending_list_key = key if not value else None
    return meta


def strip_front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    return text[end + 4 :].lstrip()


def extract_markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s|\Z)", text
    )
    return match.group(1) if match else ""


def extract_lesson_structured_layer(text: str) -> str:
    match = re.search(
        r"<details>\s*<summary>[\s\S]*?</summary>([\s\S]*?)</details>",
        strip_front_matter(text),
    )
    return match.group(1) if match else strip_front_matter(text)


def scoped_forbidden_blocks(text: str, meta: dict[str, str]) -> list[tuple[str, str]]:
    content_type = meta.get("content_type")
    if content_type == "lesson":
        structured = extract_lesson_structured_layer(text)
        blocks = []
        for label, section in [
            ("objectives", extract_markdown_section(structured, "objectives")),
            ("assessment", extract_markdown_section(structured, "assessment")),
            (
                "consistency_matrix",
                extract_markdown_section(structured, "consistency_matrix"),
            ),
        ]:
            if section:
                blocks.append((label, section))
        return blocks
    if content_type in {
        "courseware_reference",
        "reference_answer",
        "question_reference",
    }:
        blocks = []
        for label in ["学习目标", "评价标准", "成功标准", "评分要点"]:
            pattern = rf"(?ms)^#+\s+.*{re.escape(label)}.*$([\s\S]*?)(?=^#+\s|\Z)"
            for match in re.finditer(pattern, text):
                blocks.append((label, match.group(1)))
        return blocks
    if content_type == "textbook_solution":
        checked = re.sub(
            r"\*\*原题\*\*：[\s\S]*?(?=\n\*\*参考解答\*\*：)",
            "",
            text,
        )
        return [("textbook_solution_answer", checked)]
    return []


def check_scoped_forbidden_terms(
    text: str, meta: dict[str, str], errors: list[str]
) -> None:
    for label, block in scoped_forbidden_blocks(text, meta):
        for term in FORBIDDEN_TERMS:
            if term in block:
                if label == "textbook_solution_answer":
                    errors.append(f"forbidden term found: {term}")
                else:
                    errors.append(f"forbidden term found in {label}: {term}")


def check_required_layers(text: str, meta: dict[str, str], errors: list[str]) -> None:
    content_type = meta.get("content_type")
    if content_type not in LAYER_REQUIRED_CONTENT_TYPES:
        return
    scan_text = (
        extract_lesson_structured_layer(text) if content_type == "lesson" else text
    )
    for layer in REQUIRED_LAYERS:
        if layer not in scan_text:
            errors.append(f"missing layer: {layer}")


def source_window(lines: list[str], start: int, size: int = 10) -> str:
    window: list[str] = []
    for line in lines[start : start + size]:
        if window and re.match(r"^#{1,6}\s+", line):
            break
        window.append(line)
    return "\n".join(window)


def has_complete_source_fields(block: str) -> bool:
    has_source_id = bool(re.search(r"(?m)\bsource_id\s*[:：]\s*\S+", block))
    has_source_type = bool(re.search(r"(?m)\bsource_type\s*[:：]\s*\S+", block))
    has_question_id = bool(re.search(r"(?m)\bquestion_id\s*[:：]\s*\S+", block))
    has_question_ids = bool(
        re.search(r"(?m)\bquestion_ids\s*[:：]\s*(?:\S+|\n\s*-\s*\S+)", block)
    )
    comma_joined = bool(
        re.search(r"(?m)\bquestion_id\s*[:：]\s*[\"']?[^\"'\n,]+,\s*[^\"'\n]+", block)
    )
    return (
        has_source_id
        and has_source_type
        and (has_question_id or has_question_ids)
        and not comma_joined
    )


def check_question_source_fields(
    text: str, meta: dict[str, str], errors: list[str]
) -> None:
    if meta.get("content_type") in {"courseware", "review_lesson"}:
        return
    scan_text = (
        extract_lesson_structured_layer(text)
        if meta.get("content_type") == "lesson"
        else text
    )
    lines = scan_text.splitlines()
    question_line_pattern = re.compile(
        r"(?:题目|例题|练习|作业|评价任务|教材练习第\d+题|[AB]组第\d+题|question_text)"
    )
    seen_blocks: set[int] = set()
    for index, line in enumerate(lines):
        if not question_line_pattern.search(line):
            continue
        if "source_id" in line or "source_type" in line:
            continue
        block = source_window(lines, index)
        block_key = hash(block)
        if block_key in seen_blocks:
            continue
        seen_blocks.add(block_key)
        if not has_complete_source_fields(block):
            excerpt = re.sub(r"\s+", " ", block).strip()[:80]
            errors.append(
                f"question-like block missing complete source fields: {excerpt}"
            )


def extract_img_paths(text: str) -> list[str]:
    html_paths = re.findall(
        r"<img\s+[^>]*src=[\"']([^\"']+)[\"'][^>]*>", text, flags=re.I
    )
    markdown_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    return html_paths + markdown_paths


def extract_minutes(text: str) -> list[int]:
    minutes: list[int] = []
    for line in text.splitlines():
        if re.search(r"duration\s*[:：]", line, flags=re.I):
            continue
        match = re.match(
            r"\s*-?\s*(?:time|时间)\s*[:：]\s*(\d+)\s*分钟", line, flags=re.I
        )
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
    names.extend(
        re.findall(
            r"^\|\s*([^|\s]+)\s*\|\s*(?:基础层|中间层|拓展层)\s*\|", text, flags=re.M
        )
    )
    return [name.strip() for name in names if name.strip() and name.strip() != "学生"]


def check_common(path: Path, text: str, errors: list[str]) -> dict[str, str]:
    meta = parse_front_matter(text)
    if not meta:
        if path.name.endswith("_课件.md") or "courseware" in path.stem.lower():
            return {"content_type": "courseware", "command": "courseware-collab"}
        errors.append("missing YAML front matter")
        return meta

    required_keys = [
        "content_type",
        "lesson_id",
        "lesson_name",
        "command",
        "workflow_version",
        "created_at",
    ]
    if meta.get("content_type") not in {"textbook_solution", "review_lesson"}:
        required_keys.append("review_status")
    for key in required_keys:
        if key not in meta or not meta[key]:
            errors.append(f"missing front matter field: {key}")

    if meta.get("content_type") == "textbook_solution" and "review_status" in meta:
        errors.append("textbook_solution must not set review_status")

    if meta.get("content_type") == "review_lesson" and "review_status" in meta:
        errors.append("review_lesson must not set review_status")

    if meta.get("workflow_version") != "v2":
        errors.append("workflow_version must be v2")

    if meta.get("review_status") and meta["review_status"] not in VALID_REVIEW_STATUS:
        errors.append(f"invalid review_status: {meta['review_status']}")

    if "collab_gates" in meta:
        errors.append(
            "YAML front matter contains collab_gates field; "
            "confirmation gate records must be written to collab-gates.log.md instead"
        )

    if meta.get("content_type") not in {"courseware", "review_lesson"} and re.search(
        r"!\[[^\]]*\]\([^)]+\)", text
    ):
        errors.append(
            'Markdown image syntax is forbidden; use <img src="./images/...">'
        )

    for bad in [
        "../knowledge/textbooks/images",
        "../knowledge/workbooks/images",
        "assets/images",
        "outputs/{lesson_id}/assets",
    ]:
        if bad in text:
            errors.append(f"forbidden image path fragment: {bad}")

    if meta.get("content_type") != "review_lesson":
        for img_path in extract_img_paths(text):
            if not img_path.startswith("./images/"):
                errors.append(f"image path must start with ./images/: {img_path}")
                continue
            if not (path.parent / img_path).exists():
                img_name = Path(img_path).name
                knowledge_images = path.resolve().parents[2] / "knowledge" / "images"
                if not (knowledge_images / img_name).exists():
                    errors.append(f"image file does not exist: {img_path}")

    if "图片待确认" in text:
        errors.append("image placeholder remains in final output")

    if meta.get("content_type") == "review_lesson":
        errors.extend(validate_math_markup(strip_front_matter(text)))

    return meta


def check_lesson(text: str, meta: dict[str, str], errors: list[str]) -> None:
    if meta.get("content_type") == "lesson":
        if meta.get("command") not in VALID_LESSON_COMMANDS:
            errors.append("lesson output must have command: lesson-collab")
        if meta.get("review_status") not in {
            "pending_human_review",
            "审核通过",
            "rejected",
        }:
            errors.append(
                "lesson review_status must be pending_human_review, 审核通过, or rejected"
            )

    minutes = extract_minutes(text)
    if minutes and sum(minutes) > 40:
        errors.append(f"lesson time exceeds 40 minutes: {sum(minutes)}")

    if meta.get("content_type") == "lesson" and re.search(r"请\[[^\]]+\]同学", text):
        errors.append(
            "lesson design must not contain concrete student names in questions"
        )


def check_lesson_dual_layer(text: str, meta: dict[str, str], errors: list[str]) -> None:
    """Check the teacher-facing and structured layers of a lesson design.

    Enforces the nine-column traditional format and folded structured layer
    defined in orchestrator/output-contract.md.
    """
    if meta.get("content_type") != "lesson":
        return

    # collab_gates belongs in separate log file, not in lesson YAML
    front = text[: text.find("\n---", 4)] if text.startswith("---\n") else ""
    if "collab_gates:" in front:
        errors.append(
            "lesson YAML front matter contains collab_gates; "
            "confirmation records must only be written to collab-gates.log.md"
        )

    body = strip_front_matter(text)
    details_match = re.search(
        r"<details>\s*<summary>\s*<strong>展开完整结构化设计（目标、评价、活动、题源及审核信息）</strong>\s*</summary>([\s\S]*?)</details>",
        body,
    )
    if not details_match:
        errors.append("lesson must contain the required folded 完整结构化设计 layer")
        return

    implementation = body[: details_match.start()]
    structured = details_match.group(1)

    TRADITIONAL_HEADINGS = [
        "## 一、教学内容",
        "## 二、教学目标",
        "## 三、教学重点与难点",
        "## 四、教学准备",
        "## 五、教学过程",
        "## 六、当堂检测",
        "## 七、课后作业",
        "## 八、板书设计",
        "## 九、设计依据简记",
    ]
    previous_index = -1
    for heading in TRADITIONAL_HEADINGS:
        index = implementation.find(heading)
        if index == -1:
            errors.append(f"lesson implementation layer missing heading: {heading}")
        elif index < previous_index:
            errors.append(f"lesson implementation headings are out of order: {heading}")
        else:
            previous_index = index

    BACKEND_PATTERNS = {
        "learning objective ID": r"\bLO-[BME]-\d{2}\b",
        "assessment ID": r"\bAS-[BME]-\d{2}\b",
        "activity ID": r"\bACT-[BME]-\d{2}\b",
        "question ID": r"\bASK[_-][BME][_-]\d{2}\b",
        "source field": r"\b(?:source_id|source_type|question_ids?)\s*[:：]",
    }
    for label, pattern in BACKEND_PATTERNS.items():
        if re.search(pattern, implementation):
            errors.append(f"lesson implementation layer exposes backend {label}")

    STRUCTURED_SECTIONS = [
        "meta",
        "knowledge_analysis",
        "objectives",
        "assessment",
        "problem_chain",
        "lesson_flow",
        "resource_audit",
        "practice",
        "homework",
        "deferred_exercises",
        "boardwork",
        "consistency_matrix",
        "quality_check",
    ]
    for section in STRUCTURED_SECTIONS:
        if not re.search(rf"(?m)^##\s+{re.escape(section)}\s*$", structured):
            errors.append(f"lesson structured layer missing section: {section}")

    if not re.search(
        r"(?m)^##\s+五、教学过程\s*$[\s\S]*?^###\s+.+（\s*\d+(?:\.\d+)?\s*分钟\s*）\s*$",
        implementation,
    ):
        errors.append("lesson implementation layer lacks timed teaching-process steps")

    if not re.search(r"(?m)^##\s+六、当堂检测\s*$[\s\S]*?(?:检测目标|限时)", implementation):
        errors.append(
            "lesson implementation layer lacks a timed or goal-aligned 当堂检测"
        )

    if not re.search(
        r"(?m)^##\s+七、课后作业\s*$[\s\S]*?基础层必做[\s\S]*?中间层必做[\s\S]*?拓展层选做",
        implementation,
    ):
        errors.append("lesson implementation layer lacks layered homework")


def check_courseware(
    text: str, meta: dict[str, str], errors: list[str], lesson_file: Path | None
) -> None:
    if meta.get("content_type") != "courseware":
        return
    rendered_body = strip_front_matter(text)
    if parse_front_matter(text):
        errors.append("Typora courseware must not contain YAML front matter")
    # Strip LaTeX math before checking for HTML (avoid false positives on $x<70$)
    no_math = re.sub(r"\$[^$]*\$", "", rendered_body)
    if re.search(r"<[^>]+>", no_math):
        errors.append("Typora courseware must not contain HTML tags")
    if re.search(r"(?m)^```", rendered_body):
        errors.append("Typora courseware must not contain fenced code blocks")
    if re.search(r"<!--[\s\S]*?-->", rendered_body):
        errors.append("student-facing courseware must not contain HTML comments")
    for production_label in [
        "遮盖区",
        "点击显示",
        "教师操作",
        "reveal-step",
        "图片待确认",
        "占位符",
        "source_id",
        "source_type",
        "question_id",
    ]:
        if production_label in rendered_body:
            errors.append(
                f"student-facing courseware contains production-control label: {production_label}"
            )
    if re.search(r"ASK[_-][BME][_-]\d{2}", rendered_body):
        errors.append("student-facing courseware must not display backend ASK IDs")
    if meta.get("command") not in VALID_COURSEWARE_COMMANDS:
        errors.append("courseware output must have command: courseware-collab")

    pages = split_pages(text)

    # Check A组结构合规
    check_courseware_group_a(text, pages, errors)

    # Check B组内容合规
    check_courseware_group_b(text, pages, errors)
    check_courseware_material_anchors(pages, errors)
    check_required_practice_pages(text, lesson_file, errors)

    # Check upstream lesson file
    if lesson_file:
        lesson_meta = parse_front_matter(read_text(lesson_file))
        if lesson_meta.get("content_type") != "lesson":
            errors.append("upstream lesson file must have content_type: lesson")
        if lesson_meta.get("review_status") != "审核通过":
            errors.append("upstream lesson must be review_status: 审核通过")
        if (
            meta.get("lesson_id")
            and lesson_meta.get("lesson_id")
            and meta.get("lesson_id") != lesson_meta.get("lesson_id")
        ):
            errors.append("courseware lesson_id does not match upstream lesson")


def check_courseware_material_anchors(pages: list[Page], errors: list[str]) -> None:
    """Require every projected question page to contain enough visible material to stand alone."""
    for page_number, page in enumerate(pages, 1):
        question_match = re.search(r"\*\*问题[：:]\*\*", page.content)
        if not question_match:
            continue

        visible_before = page.content[: question_match.start()]
        anchor_text = re.sub(r"^#{1,6}\s+.*$", "", visible_before, flags=re.MULTILINE)
        anchor_text = re.sub(r"\s+", "", anchor_text)
        question = page.content[question_match.end() :].splitlines()[0].strip()

        if len(anchor_text) < 12:
            errors.append(
                f"courseware page {page_number}: question lacks same-page visible material anchor"
            )
            continue

        if re.search(r"这四类|上面四类", question):
            cells = [
                cell.strip() for cell in re.findall(r"\|([^|\n]+)", visible_before)
            ]
            meaningful_cells = [
                cell for cell in cells if cell and not set(cell) <= {"-", ":"}
            ]
            if len(meaningful_cells) < 4:
                errors.append(
                    f"courseware page {page_number}: four-category question must list all four categories before the question"
                )

        if "各数字" in question:
            has_digits = bool(re.search(r"0\s*(?:至|到|~|～|-|—)\s*9", visible_before))
            has_context = bool(re.search(r"彩票|号码|数字", visible_before))
            if not (has_digits and has_context):
                errors.append(
                    f"courseware page {page_number}: '各数字' must identify digits 0 to 9 and the source context"
                )

        if "前一个环节" in question and not re.search(
            r"→|收集数据.*整理数据", visible_before, re.DOTALL
        ):
            errors.append(
                f"courseware page {page_number}: process-reference question must show the process before the question"
            )

        if "哪两个读数" in question and len(re.findall(r"\d{3,4}", visible_before)) < 2:
            errors.append(
                f"courseware page {page_number}: reading-comparison question must show the relevant readings"
            )


def check_required_practice_pages(
    text: str, lesson_file: Path | None, errors: list[str]
) -> None:
    """Ensure every lesson practice item has an explicit student task page."""
    if not lesson_file or not lesson_file.exists():
        return
    lesson_text = read_text(lesson_file)
    practice_match = re.search(r"(?ms)^## practice\s+(.*?)(?=^## |\Z)", lesson_text)
    if not practice_match:
        return
    practice_text = practice_match.group(1)
    required = sorted(
        set(
            re.findall(
                r"(?:教材)?练习第\d+题(?:第（\d+）问)?|[AB]组第\d+题(?:第（\d+）问)?",
                practice_text,
            )
        )
    )
    pages = split_pages(text)
    if required and len(required) < 4:
        errors.append(
            f"courseware practice/check task count too low: {len(required)}, min 4"
        )
    for item in required:
        matching_pages = [
            (index, page.content)
            for index, page in enumerate(pages)
            if item in page.content
            and "### 📝" in page.content
            and "参考答案" not in page.content
        ]
        if not matching_pages:
            errors.append(f"courseware missing explicit practice task page for {item}")
            continue
        task_index, task_page = matching_pages[0]
        for marker in ["限时", "评分：", "产出："]:
            if marker not in task_page:
                errors.append(f"practice task page for {item} missing {marker}")
        answer_pages = [
            page.content
            for page in pages[task_index + 1 :]
            if item in page.content and "参考答案" in page.content
        ]
        if not answer_pages:
            errors.append(f"courseware missing reference answer page for {item}")


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
    # (soft check - pattern presence is noted but not strictly enforced)

    # Rule 4: Summary with three questions (三问三答)
    has_summary_table = bool(re.search(r"层次.*问题", text)) and (
        ("基础层" in text and "中间层" in text and "拓展层" in text)
        or ("🌱" in text and "🌿" in text and "🌳" in text)
    )
    if not has_summary_table:
        errors.append(
            "courseware missing 三问三答 summary table (基础层/中间层/拓展层)"
        )

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

    # Emoji allowed in body text as output-type markers (§13)
    OUTPUT_MARKER_EMOJIS = {"✏️", "🗣️"}
    for i, page in enumerate(pages, 1):
        # Rule B1: Max 1 page-type emoji per page
        # Exclude level markers (🌱🌿🌳, via exclude_level) and output-type markers
        emoji_count = count_emojis(page.content, exclude_level=True)
        for marker in OUTPUT_MARKER_EMOJIS:
            emoji_count -= page.content.count(marker)
        if emoji_count > MAX_EMOJIS_PER_PAGE:
            errors.append(
                f"page {i}: too many emojis ({emoji_count}), max {MAX_EMOJIS_PER_PAGE}"
            )
            group_b_violations += 1

        # Rule B2: Title has valid emoji
        title_emoji = extract_title_emoji(page.content)
        if title_emoji and title_emoji not in VALID_EMOJIS:
            errors.append(
                f"page {i}: invalid title emoji {title_emoji}, should be one of {sorted(VALID_EMOJIS)}"
            )
            group_b_violations += 1

        # Rule B3: Mermaid diagram node count <= 6
        mermaid_blocks = extract_mermaid_diagrams(page.content)
        for j, mermaid_code in enumerate(mermaid_blocks, 1):
            node_count = count_mermaid_nodes(mermaid_code)
            if node_count > MAX_MERMAID_NODES:
                errors.append(
                    f"page {i}: mermaid diagram {j} has {node_count} nodes, max {MAX_MERMAID_NODES}"
                )
                group_b_violations += 1

        # Rule B4: No consecutive pure text pages > 3
        # This is checked globally later

        # Rule B5: Time limit format check
        has_time_limit = bool(re.search(r"（\s*限时\s*\d+\s*分钟\s*）", page.content))
        has_activity = any(
            keyword in page.content for keyword in ["✏️", "🗣️", "小组讨论"]
        )
        if (
            has_activity
            and not has_time_limit
            and "课堂检测" not in page.content
            and "小结" not in page.content
        ):
            # Soft check - don't count as violation for now
            pass

        # Rule B6: Scoring annotation check
        has_scoring = bool(re.search(r"评分[:：]", page.content))
        has_exercise = any(
            keyword in page.content for keyword in ["练习", "检测", "作业"]
        )
        if has_exercise and not has_scoring:
            # Soft check
            pass

        # Rule B7: Question format check
        question_matches = re.findall(r"【.*?层提问】", page.content)
        if question_matches:
            for q_match in question_matches:
                if not re.match(r"【(基础|中间|拓展)层提问】", q_match):
                    errors.append(f"page {i}: invalid question format: {q_match}")
                    group_b_violations += 1

        # Rule B8: No teacher/student action prompts
        if "教师：" in page.content or "学生：" in page.content:
            errors.append(
                f'page {i}: contains teacher/student action prompts ("教师：" or "学生：")'
            )
            group_b_violations += 1

        # Rule B8.5: Max 10 lines per page (including blank lines, excluding image refs)
        content_lines = [
            l for l in page.content.split('\n')
            if not l.strip().startswith('![') and not l.strip().startswith('|---')
        ]
        if len(content_lines) > MAX_LINES_PER_PAGE:
            errors.append(
                f'page {i}: {len(content_lines)} lines exceeds max {MAX_LINES_PER_PAGE}'
            )
            group_b_violations += 1


    # Rule B9: No numbered steps in proofs (1. 2. 3.)
    proof_step_pattern = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
    if proof_step_pattern.search(text):
        errors.append(
            "proof/calculation steps should not use numbered lists (1. 2. 3.)"
        )
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
    required_meta = [
        "content_type",
        "lesson_id",
        "lesson_name",
        "source_files",
        "created_at",
    ]
    for key in required_meta:
        if key not in meta or not meta[key]:
            group_a_errors.append(f"missing metadata: {key}")

    # Rule A2: Title correct
    title_pattern = re.compile(r"^#\s+.+?\s+课堂提问参考答案", re.MULTILINE)
    if not title_pattern.search(text):
        group_a_errors.append(
            "missing or incorrect title: should be '{lesson_name} 课堂提问参考答案'"
        )

    # Rule A3: Random pool selection record exists and is table
    if "随机池选取记录" not in text:
        group_a_errors.append("missing random pool selection record section")
    else:
        table_pattern = re.compile(r"\|.*选取学生.*\|", re.MULTILINE)
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
        rubric_table_pattern = re.compile(r"\|.*维度.*评分标准.*\|", re.MULTILINE)
        if not rubric_table_pattern.search(text):
            group_a_errors.append("scoring rubric should be a table")

    # Rule A7: All questions have source annotations
    question_source_pattern = re.compile(
        r"source_id.*source_type.*question_id", re.DOTALL
    )
    if not question_source_pattern.search(text):
        # Check individual questions
        question_count = len(re.findall(r"(题目|例题|练习|问题)", text))
        source_count = len(re.findall(r"source_id|source_type|question_id", text))
        if question_count > 0 and source_count < question_count // 2:
            group_a_errors.append(
                "questions missing source annotations (source_id/source_type/question_id)"
            )

    # Rule A8: Math formulas use LaTeX
    latex_pattern = re.compile(r"\$.*?\$")
    formula_pattern = re.compile(r"[+\-×÷=≠≤≥≈√∑∫∞π]")
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
        errors.append(
            "[Group B] missing layer sections in 板块A (基础层/中间层/拓展层)"
        )
        group_b_violations += 1

    # Rule B2: Question ID format correct
    question_ids = re.findall(r"ASK-[BME]-\d+", text)
    for qid in question_ids:
        if not re.match(r"ASK-[BME]-\d{2}", qid):
            errors.append(
                f"[Group B] invalid question ID format: {qid}, should be ASK-[BME]-XX"
            )
            group_b_violations += 1

    # Rule B3: Answers have clear bullet points
    answer_sections = re.findall(r"参考答案[\s\S]*?(?=\n\n##|\n\n---|$)", text)
    for ans in answer_sections:
        bullet_count = len(re.findall(r"^[-*]\s+", ans, re.MULTILINE))
        if bullet_count < 2 and len(ans.splitlines()) > 5:
            errors.append(
                "[Group B] answer should have clear bullet points (3-5 points recommended)"
            )
            group_b_violations += 1
            break

    # Rule B4: Scoring points are clear and quantifiable
    scoring_sections = re.findall(r"评分要点[\s\S]*?(?=\n\n##|\n\n---|$)", text)
    for scoring in scoring_sections:
        has_points = bool(re.search(r"\d+.*分", scoring))
        if not has_points:
            errors.append(
                "[Group B] scoring points should be clear and quantifiable (with scores)"
            )
            group_b_violations += 1
            break

    # Rule B5: Total pages control (approximate by line count)
    lines = text.splitlines()
    estimated_pages = len(lines) // 40  # Rough estimate
    if estimated_pages > 6:
        errors.append(
            f"[Group B] document too long (estimated {estimated_pages} pages), should be ≤6 pages"
        )
        group_b_violations += 1

    # Rule B6: Scoring rubric has dimensions
    has_dimensions = all(dim in text for dim in ["准确性", "完整性", "表达力"])
    if not has_dimensions:
        errors.append(
            "[Group B] scoring rubric should have dimensions: 准确性/完整性/表达力"
        )
        group_b_violations += 1

    # Rule B7: Section B covers examples and exercises from lesson flow
    # This is a softer check - we just verify section B exists with some content
    section_b_content = re.search(r"板块B[\s\S]*?(?=评分量规|$)", text, re.DOTALL)
    if section_b_content and len(section_b_content.group(0).strip()) < 100:
        errors.append(
            "[Group B] 板块B content too thin, should cover examples and exercises"
        )
        group_b_violations += 1

    # Rule B8: Answers show complete reasoning for step problems
    # Check for answers that have multiple steps
    multi_step_pattern = re.compile(
        r"首先|然后|接着|最后|1\.|2\.|3\.|第一步|第二步", re.MULTILINE
    )
    has_multi_step = bool(multi_step_pattern.search(text))
    if not has_multi_step and len(text) > 1000:
        # Only warn if document is long enough to have multi-step problems
        pass  # Soft check

    # Rule B9: Math terminology is standard
    # This is hard to check automatically, skip for now

    if group_b_violations >= 4:
        errors.append(f"[Group B] violations: {group_b_violations} (>=4)")


def check_question_reference(
    text: str, errors: list[str], students_file: Path | None
) -> None:
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


def check_lesson_ask_prompt_order(text: str, errors: list[str]) -> None:
    """Require lesson ASK blocks to preserve independent thinking before scaffolding."""
    ask_pattern = re.compile(r"(?m)^\s*-?\s*(ASK[_-][BME][_-]\d{2})\s*$")
    matches = list(ask_pattern.finditer(text))
    for index, match in enumerate(matches):
        block_end = (
            matches[index + 1].start() if index + 1 < len(matches) else len(text)
        )
        block = text[match.end() : block_end]
        question = re.search(r"(?m)^\s*-?\s*提问[：:]", block)
        hint = re.search(r"(?m)^\s*-?\s*备用提示(?:\d+)?[：:]", block)
        expected = re.search(r"(?m)^\s*-?\s*教师参考预期[：:]", block)

        if not question:
            errors.append(f"{match.group(1)} missing 提问 field")
        if not hint:
            errors.append(f"{match.group(1)} missing 分级备用提示 field")
        if not expected:
            errors.append(f"{match.group(1)} missing 教师参考预期 field")
        if (
            question
            and hint
            and expected
            and not (question.start() < hint.start() < expected.start())
        ):
            errors.append(
                f"{match.group(1)} field order must be 提问 -> 备用提示 -> 教师参考预期"
            )
        if re.search(r"(?m)^\s*-?\s*提示[：:]", block):
            errors.append(f"{match.group(1)} uses legacy 提示 field; use 备用提示1/2/3")
        if re.search(r"(?m)^\s*-?\s*预期[：:]", block):
            errors.append(f"{match.group(1)} uses legacy 预期 field; use 教师参考预期")


def check_courseware_question_reveal_order(text: str, errors: list[str]) -> None:
    """Keep student-facing courseware question-first and teacher-only content out."""
    if re.search(r"(?m)^\s*-?\s*教师参考预期[：:]", text):
        errors.append("student-facing courseware must not contain 教师参考预期")

    seen_question: set[str] = set()
    for page_number, page in enumerate(split_pages(text), 1):
        ids = set(re.findall(r"ASK[_-][BME][_-]\d{2}", page.content))
        if not ids:
            continue
        has_question = bool(
            re.search(r"(?m)^\s*(?:\*\*)?(?:问题|提问)(?:\*\*)?[：:]", page.content)
            or re.search(r"【(?:基础|中间|拓展)层提问】", page.content)
        )
        has_hint = bool(
            re.search(r"(?:\*\*)?备用提示(?:\d+)?(?:\*\*)?[：:]", page.content)
        )
        if has_question and has_hint:
            question_pos = min(
                (m.start() for m in re.finditer(r"(?:问题|提问)[：:]", page.content)),
                default=-1,
            )
            hint_pos = min(
                (
                    m.start()
                    for m in re.finditer(r"备用提示(?:\d+)?[：:]", page.content)
                ),
                default=-1,
            )
            answer_positions = [
                m.start() for m in re.finditer(r"(?:答案|归纳)[：:]", page.content)
            ]
            if question_pos < 0 or hint_pos < 0 or question_pos >= hint_pos:
                errors.append(
                    f"courseware page {page_number}: same-page content must order question before backup hints"
                )
            if answer_positions and hint_pos >= min(answer_positions):
                errors.append(
                    f"courseware page {page_number}: same-page answers/conclusions must follow backup hints"
                )
        for ask_id in ids:
            if has_hint and not has_question and ask_id not in seen_question:
                errors.append(
                    f"courseware page {page_number}: {ask_id} backup hint appears before its question page"
                )
            if has_question:
                seen_question.add(ask_id)


def check_reference_ask_prompt_order(text: str, errors: list[str]) -> None:
    """Require teacher reference ASK blocks to place hints before answers."""
    pattern = re.compile(
        r"(?m)^\s*(?:#{1,6}\s*)?\*{0,2}(ASK[_-][BME][_-]\d{2})\*{0,2}(?=\s|（|\(|$)"
    )
    matches = list(pattern.finditer(text))
    for index, match in enumerate(matches):
        block_end = (
            matches[index + 1].start() if index + 1 < len(matches) else len(text)
        )
        block = text[match.end() : block_end]
        question = re.search(r"(?m)^\s*\*{0,2}(?:问题|提问)\*{0,2}[：:]", block)
        hint = re.search(r"(?m)^\s*\*{0,2}备用提示(?:\d+)?\*{0,2}[：:]", block)
        answer = re.search(r"(?m)^\s*\*{0,2}参考答案\*{0,2}[：:]", block)
        scoring = re.search(r"(?m)^\s*\*{0,2}评分要点\*{0,2}[：:]", block)
        if not question:
            errors.append(f"{match.group(1)} reference block missing 问题 field")
        if not hint:
            errors.append(
                f"{match.group(1)} reference block missing 分级备用提示 field"
            )
        if not answer:
            errors.append(f"{match.group(1)} reference block missing 参考答案 field")
        if not scoring:
            errors.append(f"{match.group(1)} reference block missing 评分要点 field")
        if (
            question
            and hint
            and answer
            and scoring
            and not (question.start() < hint.start() < answer.start() < scoring.start())
        ):
            errors.append(
                f"{match.group(1)} reference field order must be 问题 -> 备用提示 -> 参考答案 -> 评分要点"
            )


def check_ask_prompt_order(text: str, meta: dict[str, str], errors: list[str]) -> None:
    content_type = meta.get("content_type")
    if content_type == "lesson":
        check_lesson_ask_prompt_order(text, errors)
    elif content_type == "courseware":
        check_courseware_question_reveal_order(text, errors)
    elif content_type in {
        "question_reference",
        "courseware_reference",
        "reference_answer",
    }:
        check_reference_ask_prompt_order(text, errors)


def check_learning_objectives(
    text: str, meta: dict[str, str], errors: list[str]
) -> None:
    """Check learning objectives rules."""
    # Only check learning objectives for lesson content type
    if meta.get("content_type") != "lesson":
        return

    # First, find objectives section
    objectives_section = re.search(
        r"## objectives[\s\S]*?(?=## assessment|## 问题链设计|$)", text, re.DOTALL
    )
    if not objectives_section:
        # Try alternative pattern
        objectives_section = re.search(
            r"(### 基础层[\s\S]*?(?=## assessment|## 问题链设计|$))", text, re.DOTALL
        )

    if not objectives_section:
        # No objectives section found, skip detailed checks
        # Check if it's a lesson document that should have objectives
        if meta.get("content_type") == "lesson":
            errors.append("missing objectives section not found")
        return

    obj_text = objectives_section.group(0)

    # Valid action verbs by level (from skill definition)
    basic_verbs = {
        "说出",
        "辨认",
        "识别",
        "回忆",
        "复述",
        "写出",
        "画出",
        "计算",
        "模仿",
        "画出",
        "陈述",
        "列举",
        "匹配",
        "选择",
    }
    intermediate_verbs = {
        "解释",
        "说明",
        "归纳",
        "概括",
        "比较",
        "分类",
        "推断",
        "转化",
        "改写",
        "完成",
        "解决",
        "证明",
        "描述",
        "阐述",
        "应用",
        "演绎",
    }
    advanced_verbs = {
        "分析",
        "评价",
        "创造",
        "设计",
        "构建",
        "生成",
        "假设",
        "论证",
        "批判",
        "综合",
        "鉴赏",
        "策划",
        "创新",
        "发明",
        "推导",
    }
    all_valid_verbs = basic_verbs | intermediate_verbs | advanced_verbs

    # Check each layer
    for layer_name, layer_verbs, layer_header in [
        ("基础层", basic_verbs, r"### 基础层"),
        ("中间层", intermediate_verbs, r"### 中间层"),
        ("拓展层", advanced_verbs, r"### 拓展层"),
    ]:
        # Find layer section
        layer_match = re.search(
            rf"{layer_header}[\s\S]*?(?=### |## |$)", obj_text, re.DOTALL
        )
        if not layer_match:
            errors.append(f"missing {layer_name} objectives section")
            continue

        layer_content = layer_match.group(0)

        # Extract objectives (look for LO-[BME]-XX pattern or bullet points
        objectives = re.findall(
            r"[-*]\s*(?:LO-[BME]-\d+[：:]\s*([^\n]+)|([^\n]+))", layer_content
        )
        objectives = [obj[0] or obj[1] for obj in objectives if obj[0] or obj[1]]

        # Check each objective
        obj_count = 0
        for obj in objectives:
            obj_count += 1

            # Rule 1: Contains "能" (can have preamble before it)
            if "能" not in obj:
                errors.append(
                    f"{layer_name} objective should contain '能': {obj[:50]}..."
                )

            # Rule 2: Has valid action verb
            has_valid_verb = any(verb in obj for verb in all_valid_verbs)
            if not has_valid_verb:
                errors.append(
                    f"{layer_name} objective missing valid action verb: {obj[:50]}..."
                )

            # Rule 3: No forbidden terms already checked by scoped validator

    total_objectives = len(re.findall(r"[-*]\s*`?LO-[BME]-\d+`?[：:]", obj_text))
    if total_objectives > 6:
        errors.append(
            f"too many learning objectives ({total_objectives}); total must be 6 or fewer"
        )

    # Check overall: Objectives support后续评价 design
    has_assessment = "## assessment" in text or "### 基础层评价" in text
    meta_type = meta.get("content_type")
    if meta_type == "lesson" and not has_assessment:
        errors.append("missing assessment section (should follow objectives)")


def validate_courseware_textbook_consistency(
    courseware_path: Path,
    errors: list[str],
    warnings: list[str],
    textbook_file: Path | None = None,
) -> None:
    """Validate courseware against textbook source for consistency."""
    try:
        # Try to import the consistency validator

        from validate_courseware_consistency import (
            validate as validate_consistency,
        )

        courseware_text = read_text(courseware_path)
        meta = parse_front_matter(courseware_text)
        if not meta and courseware_path.name.endswith("_课件.md"):
            meta = {
                "content_type": "courseware",
                "lesson_name": courseware_path.stem.removesuffix("_课件"),
            }
        if meta.get("content_type") == "courseware":
            # Auto-find textbook
            courseware_dir = courseware_path.parent
            textbook_dir = courseware_dir.parent / "knowledge" / "教材原文"
            lesson_name = meta.get("lesson_name", "")

            textbook_path = (
                textbook_file if textbook_file and textbook_file.exists() else None
            )
            # Common filename patterns
            patterns = [f"*{lesson_name}*.md", "*22.1*.md", "*统计*.md", "*数据*.md"]
            if textbook_path is None:
                for pattern in patterns:
                    matches = list(textbook_dir.glob(pattern))
                    if matches:
                        textbook_path = matches[0]
                        break

            if textbook_path and textbook_path.exists():
                cons_errors, cons_warnings = validate_consistency(
                    courseware_path, textbook_path, auto_find=False
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
        warnings.append(
            "[ActivityOrder] lesson_flow section not found, skipping textbook order check"
        )
        return

    if not has_position_field:
        warnings.append(
            "[ActivityOrder] 教学设计中未找到'教材对应位置'字段，跳过教材顺序检查"
        )
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
        textbook_dir = project_root / "knowledge" / "教材原文"
        if textbook_dir.exists():
            lesson_name = lesson_meta.get("lesson_name", "")
            patterns = [
                f"*{lesson_name.replace('.', '').replace('(', '').replace(')', '')}*.md",
                "*.md",
            ]
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


def validate_lesson_timing(
    lesson_path: Path,
    errors: list[str],
    warnings: list[str],
    runtime_profile: Path | None = None,
    timing_log: Path | None = None,
) -> None:
    """Run the independent teaching-activity timing validator."""
    try:
        from validate_lesson_timing import validate_timing
    except ImportError:
        from tools.validate_lesson_timing import validate_timing

    project_root = lesson_path.parent.parent
    profile_path = runtime_profile or project_root / "students" / "教学运行画像.md"
    log_path = timing_log or project_root / "students" / "课堂活动耗时日志.md"
    result = validate_timing(lesson_path, profile_path, log_path)
    errors.extend([f"[LessonTiming] {error}" for error in result.errors])
    warnings.extend([f"[LessonTiming] {warning}" for warning in result.warnings])
    if result.status == "有条件通过":
        deferred = ", ".join(result.deferred) if result.deferred else "未确定"
        warnings.append(
            f"[LessonTiming] 有条件通过：核心{result.core_minutes:.1f}分钟，"
            f"全部{result.total_minutes:.1f}分钟；建议后移 {deferred}"
        )


def validate(
    path: Path,
    lesson_file: Path | None,
    question_reference: Path | None,
    students_file: Path | None,
    textbook_file: Path | None = None,
    textbook_solution: Path | None = None,
    runtime_profile: Path | None = None,
    timing_log: Path | None = None,
) -> tuple[list[str], list[str]]:
    text = read_text(path)
    errors: list[str] = []
    warnings: list[str] = []
    meta = check_common(path, text, errors)
    if meta.get("content_type") == "courseware" and lesson_file:
        lesson_meta = parse_front_matter(read_text(lesson_file))
        meta.setdefault("lesson_id", lesson_meta.get("lesson_id", ""))
        meta.setdefault("lesson_name", lesson_meta.get("lesson_name", ""))
    check_scoped_forbidden_terms(text, meta, errors)
    check_required_layers(text, meta, errors)
    check_question_source_fields(text, meta, errors)
    check_lesson(text, meta, errors)
    check_lesson_dual_layer(text, meta, errors)
    check_courseware(text, meta, errors, lesson_file)
    check_reference_answer(text, meta, errors)
    check_learning_objectives(text, meta, errors)
    check_ask_prompt_order(text, meta, errors)
    # Typora courseware MUST NOT have YAML front matter (SKILL.md §6);
    # skip source_files dependency check for raw courseware files.
    if not (meta.get("content_type") == "courseware" and not parse_front_matter(text)):
        errors.extend(validate_dependency(path, text, meta, textbook_solution))
    errors.extend(validate_workbook_dependency(path, text, meta))

    if meta.get("content_type") == "review_lesson":
        errors.extend(validate_review_lesson_file(path))

    if question_reference:
        check_question_reference(read_text(question_reference), errors, students_file)
    elif meta.get("content_type") == "question_reference":
        check_question_reference(text, errors, students_file)

    # Add textbook consistency check for courseware
    if meta.get("content_type") == "courseware":
        validate_courseware_textbook_consistency(path, errors, warnings, textbook_file)

    # Add activity-textbook-order check for lesson
    if meta.get("content_type") == "lesson":
        validate_lesson_timing(path, errors, warnings, runtime_profile, timing_log)
        validate_activity_textbook_order(path, errors, warnings, textbook_file)

    return errors, warnings


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except AttributeError:
        pass
    parser = argparse.ArgumentParser(description="Validate Markdown output hard rules.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--lesson-file", type=Path)
    parser.add_argument("--question-reference", type=Path)
    parser.add_argument("--students-file", type=Path)
    parser.add_argument("--textbook-file", type=Path)
    parser.add_argument("--textbook-solution", type=Path)
    parser.add_argument("--runtime-profile", type=Path)
    parser.add_argument("--timing-log", type=Path)
    args = parser.parse_args()

    errors, warnings = validate(
        args.file,
        args.lesson_file,
        args.question_reference,
        args.students_file,
        args.textbook_file,
        args.textbook_solution,
        args.runtime_profile,
        args.timing_log,
    )

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
