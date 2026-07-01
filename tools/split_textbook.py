"""
将 MinerU 转换的教材 Markdown 文件按课时拆分为独立文件。

处理步骤：
  1. 将 HTML 表格转换为 Markdown 原生表格格式
  2. 分析章节结构与课时分配，等待用户确认
  3. 按课时拆分（章引言归入第一课时，数学活动单独统计）

用法:
    python split_textbook.py <输入文件> [--outdir <输出目录>]
"""

import argparse
import os
import re
import sys
from html.parser import HTMLParser

# ============================================================
# 1. HTML 表格 → Markdown 表格
# ============================================================


class TableToMD(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.rows = []
        self.row = []
        self.cell = ""
        self.in_cell = False
        self.attrs = {}

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.active = True
            self.rows = []
        elif self.active and tag == "tr":
            self.row = []
        elif self.active and tag in ("td", "th"):
            self.in_cell = True
            self.cell = ""
            self.attrs = dict(attrs)

    def handle_endtag(self, tag):
        if tag == "table":
            self.active = False
        elif self.active and tag == "tr":
            self.rows.append(self.row)
        elif self.active and tag in ("td", "th"):
            self.in_cell = False
            cs = int(self.attrs.get("colspan", 1))
            rs = int(self.attrs.get("rowspan", 1))
            text = fix_cell_formula(self.cell.strip().replace("\n", " "))
            self.row.append((text, cs, rs))

    def handle_data(self, data):
        if self.in_cell:
            self.cell += data

    def to_markdown(self):
        if not self.rows:
            return ""

        # Build a grid with resolved colspan/rowspan
        # First, determine column count
        max_cols = 0
        for row in self.rows:
            cols = sum(cs for _, cs, _ in row)
            if cols > max_cols:
                max_cols = cols
        n_rows = len(self.rows)

        # Initialize grid
        grid = [["" for _ in range(max_cols)] for _ in range(n_rows)]
        occupied = [[False for _ in range(max_cols)] for _ in range(n_rows)]

        # Fill grid
        for r, row in enumerate(self.rows):
            c = 0
            for text, cs, rs in row:
                # Find next vacant column
                while c < max_cols and occupied[r][c]:
                    c += 1
                # Fill cells (expand colspan and rowspan)
                for dr in range(rs):
                    for dc in range(cs):
                        if r + dr < n_rows and c + dc < max_cols:
                            grid[r + dr][c + dc] = text
                            occupied[r + dr][c + dc] = True
                c += cs

        # Build Markdown table
        lines = []
        # Header row
        header = "| " + " | ".join(grid[0]) + " |"
        lines.append(header)
        # Separator
        sep = "|" + "|".join([" --- " for _ in range(max_cols)]) + "|"
        lines.append(sep)
        # Body rows
        for row in grid[1:]:
            body = "| " + " | ".join(row) + " |"
            lines.append(body)

        return "\n".join(lines)


def fix_cell_formula(cell):
    """Wrap LaTeX formulas in $...$ within a table cell if not already wrapped.

    Handles both single-formula cells and multi-formula cells where formulas
    are concatenated without separators (common MinerU OCR artifact).
    Formula boundaries are: (1) before \\command, (2) before new Var=equation,
    only when preceded by a formula-ending character (prime, paren, brace).
    """
    cell = cell.strip()
    if not cell or "$" in cell:
        return cell

    # Only process cells that contain LaTeX commands or math equations
    has_latex = "\\" in cell
    has_equation = bool(re.search(r"[A-Za-z]+\s*=", cell))
    if not has_latex and not has_equation:
        return cell

    # Split multi-formula cells at formula boundaries.
    # A new formula starts with either \command or Var=, but only after
    # a formula-ending character: prime ('), close paren ()), close brace (}).
    parts = re.split(
        r"(?<=[\'\)\}])(?=\\[a-zA-Z])|"  # ...'\angle...
        r"(?<=[\'\)\}])(?=[A-Z][A-Za-z]*=)",  # ...'BC=...
        cell,
    )
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) == 1:
        return f"${parts[0]}$"
    else:
        return " ".join(f"${p}$" for p in parts)


def convert_html_tables(text):
    """Find and convert all HTML tables in text to Markdown tables."""
    table_re = re.compile(r"(<table>.*?</table>)", re.DOTALL | re.IGNORECASE)

    def replace_table(m):
        html = m.group(1)
        parser = TableToMD()
        parser.feed(html)
        return parser.to_markdown()

    return table_re.sub(replace_table, text)


# Section icon headers (same as remove_section_icons.py)
SECTION_ICON_HEADERS = [
    "观察与思考",
    "做一做",
    "练习",
    "一起探究",
    "大家谈谈",
    "读一读",
    "复习题",
]

# Pattern: image ref (CDN or relative) followed by blank lines, then ## target header
_SECTION_ICON_RE = re.compile(
    r"!\[.*?\]\("
    r"(?:https://cdn\.jsdelivr\.net/gh/sporeplant/"
    r"math-resource-engine@main/knowledge/images/"
    r"|(?:\.\./)?images/)"  # CDN URL or relative images/ path
    r"([a-f0-9]+\.jpg)\)\s*\n\s*\n## (?:"
    + "|".join(re.escape(h) for h in SECTION_ICON_HEADERS)
    + r")",
    re.MULTILINE,
)


def remove_section_icons_from_text(text):
    """Remove section icon image references from textbook markdown text.

    Returns (cleaned_text, set_of_image_hashes_removed).
    The image hashes can be used later to delete actual files from knowledge/images/.
    """
    removed_hashes = set()

    def replace_icon(m):
        removed_hashes.add(m.group(1))
        full = m.group(0)
        header_pos = full.rfind("\n## ")
        return full[header_pos:]  # preserve "\n## 栏目名"

    cleaned = _SECTION_ICON_RE.sub(replace_icon, text)
    return cleaned, removed_hashes


# ============================================================
# 2. 章节结构分析
# ============================================================

CN_DIGIT = {
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
    "十": "10",
    "十一": "11",
    "十二": "12",
    "十三": "13",
    "十四": "14",
    "十五": "15",
    "十六": "16",
    "十七": "17",
    "十八": "18",
    "十九": "19",
    "二十": "20",
}


def _cn(s):
    return CN_DIGIT.get(s, s)


CHAPTER_RE = re.compile(r"^##\s*第([一二三四五六七八九十]+)章\s+(.*)")
SECTION_RE = re.compile(
    r"^##\s*(\d+)[.](\d+)\s*(.*?)[（(]第([一二三四五六七八九十]+)课时[）)]"
)
OCR_SECTION_RE = re.compile(
    r"^##\s*(0?\d+)\s+(.*?)[（(]第([一二三四五六七八九十]+)课时[）)]"
)
REVIEW_RE = re.compile(
    r"^##\s*(?:(?:第)?(?:\d+|[一二三四五六七八九十]+)章)?回顾与反思[（(]第([一二三四五六七八九十]+)课时[）)]"
)

SUB_PATTERNS = [
    re.compile(
        r"^##\s*(做一做|大家谈谈|观察与思考|练习|习题|读一读|一起探究|复习题)\s*$"
    ),
    re.compile(r"^##\s*[ABC]\s*组\s*$"),
    re.compile(r"^##\s*[一二三四五六七八九十]+[、]"),
    re.compile(r"^##\s*\d+\.[\s　]"),
    re.compile(r"^##\s*(知识结构|总结与反思|注意事项|复习题)\s*$"),
    re.compile(r"^##\s*[^ ]*法则\s*$"),
    re.compile(r"^##\s*(分式的基本性质|分式的运算|分式方程|分式方程的增根)\s*$"),
    re.compile(r"^##\s*基本事实[一二三四五六七八九十]"),
    re.compile(r"^##\s*全等三角形的对应边相等"),
    re.compile(r"^##\s*全等三角形的判定定理"),
    re.compile(r"^##\s*两角分别相等"),
]


def is_sub_heading(s):
    return any(p.match(s) for p in SUB_PATTERNS)


def yaml_value(value):
    """Return a compact YAML scalar for simple metadata values."""
    value = str(value or "").strip()
    if not value:
        return '""'
    if re.search(r'[:#\[\]{}&,*!|>\'"%@`\n\r]', value):
        return repr(value)
    return value


def build_front_matter(metadata):
    fields = [
        "content_type",
        "textbook_version",
        "semester",
        "chapter_name",
        "section_name",
        "lesson_id",
    ]
    lines = ["---"]
    for field in fields:
        lines.append(f"{field}: {yaml_value(metadata.get(field, ''))}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + "\n"


def fix_image_paths(content):
    """Make image references work from a chapter subdirectory."""
    replacements = [
        ("](./images/", "](../images/"),
        ("](images/", "](../images/"),
        ('src="./images/', 'src="../images/'),
        ('src="images/', 'src="../images/'),
        ("src='./images/", "src='../images/"),
        ("src='images/", "src='../images/"),
    ]
    for old, new in replacements:
        content = content.replace(old, new)
    return content


def analyze_structure(lines):
    """Analyze chapter structure from headings."""
    chapter = {"num": "", "title": "", "intro_end": 0}
    sections = {}  # {section_key: {'name': str, 'lessons': [str]}}
    section_order = []  # ordered keys
    activities = []  # [(heading_text, start_line)]
    reviews = []  # [{'lesson': str, 'start_line': int}]
    current_section = None

    for i, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        s = line.strip()

        # Chapter heading
        m = CHAPTER_RE.match(s)
        if m:
            chapter["num"] = _cn(m.group(1))
            chapter["title"] = m.group(2).strip()
            continue

        # Find chapter intro end (first non-sub ## after chapter heading)
        if chapter["intro_end"] == 0 and not chapter.get("_found_first_lesson"):
            if i > 0 and not is_sub_heading(s) and not CHAPTER_RE.match(s):
                chapter["intro_end"] = i
                chapter["_found_first_lesson"] = True

        # Section lesson
        m = SECTION_RE.match(s)
        if m:
            ch, sec, name, lesson = (
                m.group(1),
                m.group(2),
                m.group(3).strip(),
                _cn(m.group(4)),
            )
            key = f"{ch}.{sec}"
            if key not in sections:
                sections[key] = {"name": name, "lessons": []}
                section_order.append(key)
            sections[key]["lessons"].append(lesson)
            current_section = key
            continue

        m = OCR_SECTION_RE.match(s)
        if m:
            prefix = m.group(1).lstrip("0")
            name = m.group(2).strip()
            lesson = _cn(m.group(3))
            if (
                chapter["num"]
                and prefix.isdigit()
                and int(prefix) < int(chapter["num"])
            ):
                ch, sec = chapter["num"], prefix
            else:
                ch, sec = prefix, ""
            key = f"{ch}.{sec}" if sec else ch
            if key not in sections:
                sections[key] = {"name": name, "lessons": []}
                section_order.append(key)
            sections[key]["lessons"].append(lesson)
            current_section = key
            continue

        # Review
        m = REVIEW_RE.match(s)
        if m:
            reviews.append({"lesson": _cn(m.group(1)), "start_line": i})
            continue

        # Sub-headings are skipped
        if is_sub_heading(s):
            continue

        # Otherwise it's an activity or other special block
        activities.append({"heading": s.lstrip("#").strip(), "start_line": i})

    return chapter, sections, section_order, activities, reviews


# ============================================================
# 3. 按课时拆分
# ============================================================


def build_splits(
    lines, chapter, sections, section_order, activities, reviews, metadata_base
):
    """Build the file split plan based on confirmed structure."""
    splits = []

    # Chapter intro → merge into first lesson of first section
    intro_lines = (0, chapter.get("intro_end", 0))

    # Build section splits
    all_section_headings = []
    # Find actual line numbers of section headings
    section_map = {}
    activity_start_lines = {a["start_line"] for a in activities}
    review_start_lines = {r["start_line"] for r in reviews}

    for i, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        s = line.strip()
        if SECTION_RE.match(s) or OCR_SECTION_RE.match(s):
            all_section_headings.append((i, s))
        elif REVIEW_RE.match(s):
            pass  # handled separately
        elif CHAPTER_RE.match(s):
            pass  # handled separately

    # Now create the actual lesson files
    # First, find all "lesson boundary" indices
    lesson_boundaries = [{"start": 0, "type": "intro"}]  # placeholder

    for i, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        s = line.strip()
        m = SECTION_RE.match(s)
        if m:
            lesson_boundaries.append(
                {
                    "start": i,
                    "type": "lesson",
                    "section_key": f"{m.group(1)}.{m.group(2)}",
                    "lesson": _cn(m.group(4)),
                }
            )
            continue
        m = OCR_SECTION_RE.match(s)
        if m:
            prefix = m.group(1).lstrip("0")
            lesson = _cn(m.group(3))
            if (
                chapter["num"]
                and prefix.isdigit()
                and int(prefix) < int(chapter["num"])
            ):
                ch, sec = chapter["num"], prefix
            else:
                ch, sec = prefix, ""
            key = f"{ch}.{sec}" if sec else ch
            lesson_boundaries.append(
                {"start": i, "type": "lesson", "section_key": key, "lesson": lesson}
            )
            continue
        m = REVIEW_RE.match(s)
        if m:
            lesson_boundaries.append(
                {"start": i, "type": "review", "lesson": _cn(m.group(1))}
            )
            continue
        if not is_sub_heading(s) and not CHAPTER_RE.match(s):
            lesson_boundaries.append(
                {"start": i, "type": "activity", "heading": s.lstrip("#").strip()}
            )

    # Filter out the intro (it's merged into first lesson)
    # The boundaries from index 1 onwards are actual sections
    real_boundaries = [b for b in lesson_boundaries if b["type"] != "intro"]

    # Now build splits: each boundary is a start, next boundary is the end
    activity_count = 0

    for idx, b in enumerate(real_boundaries):
        start = b["start"]
        end = (
            real_boundaries[idx + 1]["start"]
            if idx + 1 < len(real_boundaries)
            else len(lines)
        )
        typ = b["type"]
        section_name = ""
        lesson_id = ""

        if typ == "lesson":
            filename = f"textbook-{b['section_key']}-{b['lesson']}.md"
            section_name = sections.get(b["section_key"], {}).get("name", "")
            lesson_id = f"{b['section_key']}.{b['lesson']}"
        elif typ == "review":
            filename = f"textbook-ch{chapter['num']}-review-{b['lesson']}.md"
            section_name = "回顾与反思"
            lesson_id = f"ch{chapter['num']}-review-{b['lesson']}"
        elif typ == "activity":
            activity_count += 1
            safe = re.sub(r'[\\/:*?"<>|]', "_", b["heading"])[:25]
            filename = f"textbook-ch{chapter['num']}-{safe}.md"
            section_name = b["heading"]
            lesson_id = f"ch{chapter['num']}-activity-{activity_count}"
        else:
            continue

        metadata = dict(metadata_base)
        metadata.update(
            {
                "section_name": section_name,
                "lesson_id": lesson_id,
            }
        )

        is_first_lesson = idx == 0 and typ == "lesson"
        splits.append(
            {
                "start": start,
                "end": end,
                "filename": filename,
                "is_first_lesson": is_first_lesson,
                "type": typ,
                "section_name": section_name,
                "lesson_id": lesson_id,
                "metadata": metadata,
                "intro_start": intro_lines[0],
                "intro_end": intro_lines[1] if is_first_lesson else None,
            }
        )

    return splits


def format_structure(chapter, sections, section_order, activities, reviews):
    """Pretty-print the chapter structure."""
    out = []
    out.append("=" * 60)
    out.append(f"  第{chapter['num']}章  {chapter['title']}")
    out.append("=" * 60)

    first_section = section_order[0] if section_order else "第一小节"
    if chapter.get("intro_end", 0) > 0:
        out.append(
            f"  章节引言: 0～{chapter['intro_end']} 行 (将归入 {first_section} 第一课时)"
        )
        out.append("")

    lesson_count = 0
    for key in section_order:
        s = sections[key]
        out.append(f"  {key} {s['name']}")
        for lesson in s["lessons"]:
            out.append(f"    第{lesson}课时")
            lesson_count += 1

    if activities:
        out.append("")
        out.append("  --- 数学活动 / 其他 ---")
        for a in activities:
            out.append(f"    {a['heading']}")

    if reviews:
        out.append("")
        out.append("  --- 回顾与反思 ---")
        for r in reviews:
            out.append(f"    第{r['lesson']}课时")

    out.append("")
    out.append("=" * 60)
    out.append(
        f"  共 {lesson_count} 个课时 + {len(activities)} 个活动 + {len(reviews)} 个复习课时"
    )
    out.append(f"  输出文件: {lesson_count + len(activities) + len(reviews)} 个")

    return "\n".join(out)


def format_metadata_preview(splits, metadata_base):
    out = []
    out.append("[元信息预览]")
    out.append(f"  content_type: {metadata_base['content_type']}")
    out.append(f"  textbook_version: {metadata_base['textbook_version']}")
    out.append(f"  semester: {metadata_base['semester']}")
    out.append(f"  chapter_name: {metadata_base['chapter_name']}")
    out.append("")
    for sp in splits:
        out.append(f"  {sp['filename']}")
        out.append(f"    section_name: {sp['section_name']}")
        out.append(f"    lesson_id: {sp['lesson_id']}")
    return "\n".join(out)


# ============================================================
# Main
# ============================================================


def main():
    parser = argparse.ArgumentParser(description="按课时拆分 MinerU 教材 Markdown 文件")
    parser.add_argument("input_file", help="MinerU 输出的 Markdown 文件路径")
    parser.add_argument("--outdir", help="输出目录（默认与输入文件同目录）")
    parser.add_argument("--yes", "-y", action="store_true", help="跳过确认，直接拆分")
    parser.add_argument(
        "--flat",
        action="store_true",
        help="平铺输出（不创建 ch{N}/ 子目录，图片路径保持 images/）",
    )
    parser.add_argument(
        "--content-type",
        default="textbook_original",
        help="YAML content_type（默认：textbook_original）",
    )
    parser.add_argument(
        "--textbook-version", default="JJ2022", help="教材版本标识（默认：JJ2022）"
    )
    parser.add_argument("--semester", help="学期标识，如 8A、8B、9A")
    parser.add_argument("--chapter-name", help="章名称（默认使用识别到的章标题）")
    parser.add_argument(
        "--remove-icons",
        action="store_true",
        help="移除栏目标题前的图标图片引用（做一做、观察与思考等）",
    )
    args = parser.parse_args()

    input_path = os.path.abspath(args.input_file)
    if not os.path.isfile(input_path):
        print(f"错误：文件不存在 {input_path}", file=sys.stderr)
        sys.exit(1)

    outdir = (
        os.path.abspath(args.outdir) if args.outdir else os.path.dirname(input_path)
    )
    os.makedirs(outdir, exist_ok=True)

    subdir = not args.flat

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Step 1: Convert HTML tables to Markdown
    table_count = len(re.findall(r"<table>", text, re.IGNORECASE))
    if table_count > 0:
        text = convert_html_tables(text)
        print(f"[步骤 1] 发现 {table_count} 个 HTML 表格，已转换为 Markdown 原生格式")
    else:
        print("[步骤 1] 未发现 HTML 表格")
    print()

    lines = text.splitlines(keepends=True)

    # Step 2: Analyze structure
    chapter, sections, section_order, activities, reviews = analyze_structure(lines)

    if not chapter["num"]:
        print("错误：未找到章标题", file=sys.stderr)
        sys.exit(1)

    # Fix intro_end if not found
    if chapter["intro_end"] == 0:
        chapter["intro_end"] = 0

    print("[步骤 2] 章节结构分析")
    print(format_structure(chapter, sections, section_order, activities, reviews))
    print()

    semester = args.semester
    if not semester:
        if args.yes:
            print(
                "错误：使用 -y/--yes 时必须提供 --semester，如 --semester 8A",
                file=sys.stderr,
            )
            sys.exit(1)
        semester = input("请输入学期标识（如 8A、8B、9A）: ").strip()
        if not semester:
            print("错误：学期标识不能为空", file=sys.stderr)
            sys.exit(1)

    metadata_base = {
        "content_type": args.content_type,
        "textbook_version": args.textbook_version,
        "semester": semester,
        "chapter_name": args.chapter_name or chapter["title"],
    }
    splits = build_splits(
        lines, chapter, sections, section_order, activities, reviews, metadata_base
    )

    print("[步骤 3] 拆分文件与元信息预览")
    print(format_metadata_preview(splits, metadata_base))
    print()

    # Step 3: Confirm with user
    if not args.yes:
        resp = (
            input("是否确认以上章节结构和元信息并开始拆分? (y/确认/回车): ")
            .strip()
            .lower()
        )
        if resp not in ("y", "yes", "确认", ""):
            print("已取消。")
            sys.exit(0)

    print()

    # Step 4: Split
    print("[步骤 4] 正在拆分...")

    chapter_outdir = outdir
    if subdir:
        chapter_outdir = os.path.join(outdir, f"ch{chapter['num']}")
        os.makedirs(chapter_outdir, exist_ok=True)

    written = []
    all_icon_hashes = set()
    for sp in splits:
        content_parts = []
        if sp["is_first_lesson"] and sp.get("intro_start", 0) < sp.get("intro_end", 0):
            intro = "".join(lines[sp["intro_start"] : sp["intro_end"]])
            if intro.strip():
                content_parts.append(intro)

        content_parts.append("".join(lines[sp["start"] : sp["end"]]))

        content = "".join(content_parts).rstrip("\n") + "\n"
        content = build_front_matter(sp["metadata"]) + content

        if subdir:
            content = fix_image_paths(content)

        if args.remove_icons:
            content, icon_hashes = remove_section_icons_from_text(content)
            all_icon_hashes.update(icon_hashes)

        outpath = os.path.join(chapter_outdir, sp["filename"])
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(sp["filename"])

    print(f"完成！拆分 {len(written)} 个文件 → {chapter_outdir}")
    if args.remove_icons and all_icon_hashes:
        print(f"  已移除 {len(all_icon_hashes)} 个图标图片引用")
    for f in written:
        print(f"  {f}")


if __name__ == "__main__":
    main()
