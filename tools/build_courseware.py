#!/usr/bin/env python3
"""
build_courseware — 课件后处理脚本

用法：
  python tools/build_courseware.py \\
    --courseware-md outputs/lessons/ch12/12.1.1/lesson-12.1.1-courseware-draft.md \\
    --lesson-file outputs/lessons/ch12/12.1.1/lesson-12.1.1-lesson-plan.md \\
    --students-file students/scores.md \\
    --output-dir outputs/lessons/ch12/12.1.1/

输入：
  - 课件 MD 草稿（LLM 手写）
  - 教学设计（从中解析 ASK 数组）
  - 学生成绩数据（从中分配提问学生）

输出：
  - {output_dir}/lesson-{lesson_id}-courseware.md（修正后课件）
  - {output_dir}/lesson-{lesson_id}-dispatch.md（调度稿）

处理：
  1. LaTeX \\ -> \ 去转义
  2. 禁止词扫描（ASK_*、学生姓名、source_id — 写盘前阻断）
  3. 从教学设计解析 ASK 数组
  4. 自动匹配 ASK → 课件页码
  5. 从学生数据分配提问学生
  6. 机械拼装调度稿 MD
"""

from __future__ import annotations

import sys
import re
import argparse
import datetime
from pathlib import Path
from typing import NamedTuple

# ── 常量 ──────────────────────────────────────────────────

PAGE_BREAK = "---"

# 前台禁止模式（学生课件中不得出现，写盘前阻断）
FORBIDDEN_PATTERNS_STUDENT = [
    (re.compile(r"\bASK_[A-Z]_\d{2,3}\b", re.IGNORECASE), "ASK_* 编号"),
    (re.compile(r'(?:^|\n)\s*source_id\s*:', re.MULTILINE), "source_id 字段"),
    (re.compile(r'(?:^|\n)\s*source_type\s*:', re.MULTILINE), "source_type 字段"),
    (re.compile(r'(?:^|\n)\s*question_id[s]?\s*:', re.MULTILINE), "question_id 字段"),
    (re.compile(r'```(?!mermaid)', re.MULTILINE), "围栏代码块"),
    (re.compile(r'<details'), "HTML details 标签"),
    (re.compile(r'^\s*---\s*\n\s*\w+\s*:', re.MULTILINE), "YAML front matter"),
]

LEVEL_LABEL = {"B": "基础层入口", "M": "中间层推理", "E": "拓展层探究"}


# ── 数据结构 ──────────────────────────────────────────────

class AskQuestion(NamedTuple):
    ask_id: str
    level: str          # B / M / E
    question_text: str
    hints: list[str]
    expected_answer: str
    activity_ref: str   # 所属活动板块名称


class QuestionDispatch(NamedTuple):
    ask_id: str
    level: str
    page_num: int
    question_text: str
    hints: list[str]
    expected_answer: str
    activity_ref: str
    assigned_student: str
    backup_student: str


# ── LaTeX 去转义 ──────────────────────────────────────────

def _clean_latex(text: str) -> str:
    """修正 LLM 常见 LaTeX 过度转义：\\dfrac -> \\dfrac 等。"""
    if not text:
        return text
    # \\ 后紧跟字母 → 去一个反斜杠（覆盖 \\frac \\dfrac \\neq ..）
    text = re.sub(r'\\\\([a-zA-Z])', r'\\\1', text)
    # \" → "  (Markdown 中不需要转义双引号)
    text = text.replace('\\"', '"')
    return text


# ── 禁止词扫描 ────────────────────────────────────────────

def _forbidden_check(content: str, student_names: list[str]) -> list[str]:
    """扫描课件全文中的禁止项，返回错误列表（非空 = 阻断写盘）。"""
    errors: list[str] = []
    for pattern, label in FORBIDDEN_PATTERNS_STUDENT:
        if pattern.search(content):
            errors.append(f"禁止出现 {label}")
    for name in student_names:
        if name and name in content:
            errors.append(f"禁止出现学生姓名「{name}」")
    return errors


# ── 从教学设计解析 ASK 数组 ───────────────────────────────

def _parse_ask_from_lesson(lesson_text: str) -> list[AskQuestion]:
    """从教学设计的「核心提问（ASK格式）」板块提取结构化 ASK 数组。"""
    questions: list[AskQuestion] = []

    # 定位 ASK 区块
    ask_section_match = re.search(
        r'### 核心提问[^\n]*\n(.*?)(?=\n### |\n## 40分钟|\Z)',
        lesson_text, re.DOTALL
    )
    if not ask_section_match:
        return questions
    section = ask_section_match.group(1)

    # 匹配每个 ASK 条目
    # 格式: **ASK_X_NN**（层级）——问题文本
    #        - 备用提示①：...
    #        - 备用提示②：...
    #        - 教师参考预期：...
    ask_pattern = re.compile(
        r'\*\*(ASK_[BME]_\d{2})\*\*[（(](基础层|中间层|拓展层)[）)]——(.*?)\n'
        r'(.*?)(?=\n\*\*ASK_|\n### |\Z)',
        re.DOTALL
    )
    level_map = {"基础层": "B", "中间层": "M", "拓展层": "E"}

    for match in ask_pattern.finditer(section):
        ask_id = match.group(1)
        level_label = match.group(2)
        question_text = match.group(3).strip()
        detail_block = match.group(4)

        level = level_map.get(level_label, "B")

        hints: list[str] = []
        for hint_match in re.finditer(r'-\s*备用提示[①②③④⑤]?[：:]\s*(.*)', detail_block):
            hints.append(hint_match.group(1).strip())

        expected = ""
        expected_match = re.search(r'-\s*教师参考预期[：:]\s*(.*)', detail_block)
        if expected_match:
            expected = expected_match.group(1).strip()

        questions.append(AskQuestion(
            ask_id=ask_id, level=level, question_text=question_text,
            hints=hints, expected_answer=expected, activity_ref=""
        ))

    return questions


def _parse_activity_map(lesson_text: str) -> dict[str, str]:
    """从教学设计的 problem_chain 表格提取 ASK → 活动板块映射。"""
    mapping: dict[str, str] = {}

    table_match = re.search(
        r'\| 层级 \| 问题编号 \| 核心问题 \| 所属板块 \|.*?\n(.*?)(?=\n\n|\Z)',
        lesson_text, re.DOTALL
    )
    if not table_match:
        return mapping

    for line in table_match.group(1).strip().splitlines():
        parts = [c.strip() for c in line.split('|') if c.strip()]
        if len(parts) >= 4:
            ask_id = parts[1]
            activity = parts[3]
            mapping[ask_id] = activity

    return mapping


# ── ASK → 课件页码自动匹配 ────────────────────────────────

def _match_ask_to_pages(
    courseware_text: str, questions: list[AskQuestion]
) -> dict[str, int]:
    """根据 ASK 问题文本在课件 MD 中找到所在页码。"""
    pages = re.split(r'(?m)^---\s*$', courseware_text)
    mapping: dict[str, int] = {}

    for q in questions:
        # 提取问题中的核心词用于匹配（跳过 LaTeX 和标点）
        raw = re.sub(r'[\$\\\s\(\)（）\?\?!！,，。]', '', q.question_text)
        # 尝试多个关键词片段
        candidates = [raw[:6], raw[:10], raw[-8:]] if len(raw) >= 8 else [raw]

        matched_page = 0
        for page_idx, page_content in enumerate(pages, 1):
            for kw in candidates:
                if kw and len(kw) >= 3 and kw in page_content:
                    matched_page = page_idx
                    break
            if matched_page:
                break

        mapping[q.ask_id] = matched_page

    return mapping


# ── 学生数据解析 ──────────────────────────────────────────

def _parse_students(students_text: str) -> dict[str, list[str]]:
    """从 students/scores.md 提取分层学生姓名列表。
    返回: {"B": [...], "M": [...], "E": [...]}
    """
    students: dict[str, list[str]] = {"B": [], "M": [], "E": []}
    layer_map = {
        "基础层学生": "B", "中间层学生": "M", "拓展层学生": "E",
    }

    for layer_header, layer_key in layer_map.items():
        section = re.search(
            rf'### {layer_header}[^\n]*\n(.*?)(?=\n### |\n## |\Z)',
            students_text, re.DOTALL
        )
        if not section:
            continue
        for line in section.group(1).splitlines():
            name_match = re.match(r'\|\s*([^|\s]+)\s*\|', line)
            if name_match:
                name = name_match.group(1)
                if name not in ("姓名", "待录入") and not set(name) <= {"-", ":"}:
                    students[layer_key].append(name)

    return students


def _assign_students(
    questions: list[AskQuestion], students: dict[str, list[str]]
) -> dict[str, tuple[str, str]]:
    """为每个 ASK 分配主答学生和备用学生。
    返回: {ask_id: (主答, 备用)}
    """
    pool = {k: list(v) for k, v in students.items()}
    assigned: dict[str, tuple[str, str]] = {}

    for q in questions:
        layer_pool = pool.get(q.level, [])
        primary = layer_pool.pop(0) if layer_pool else "（未分配）"
        backup = layer_pool.pop(0) if layer_pool else "（未分配）"
        # 用完后放回队尾
        if primary != "（未分配）":
            layer_pool.append(primary)
        if backup != "（未分配）":
            layer_pool.append(backup)
        assigned[q.ask_id] = (primary, backup)
        pool[q.level] = layer_pool

    return assigned


# ── 课件 MD 后处理 ────────────────────────────────────────

def process_courseware(
    courseware_text: str,
    student_names: list[str],
) -> tuple[str, list[str]]:
    """后处理课件 MD：LaTeX 去转义 + 禁止词扫描。"""
    errors: list[str] = []

    # 1. LaTeX 去转义
    processed = _clean_latex(courseware_text)

    # 2. 禁止词扫描（阻断）
    ferrors = _forbidden_check(processed, student_names)
    errors.extend(ferrors)

    return processed, errors


# ── 调度稿 MD 生成 ────────────────────────────────────────

def _build_dispatch_front_matter(
    lesson_id: str, lesson_name: str, lesson_plan_path: str
) -> str:
    created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""---
content_type: question_dispatch
lesson_id: "{lesson_id}"
lesson_name: "{lesson_name}"
command: courseware-collab
workflow_version: v2
review_status: draft
source_files:
  - "{lesson_plan_path}"
created_at: "{created}"
---
"""


def _build_question_table(dispatches: list[QuestionDispatch]) -> str:
    if not dispatches:
        return "（无课堂提问）"
    lines = [
        "## 提问对象建议表",
        "",
        "| 问题编号 | 课件页码 | 问题层级 | 建议提问学生 | 备用学生 | 意图 | 证据 |",
        "|:---|:---:|:---|:---|:---|:---|:---|",
    ]
    for d in dispatches:
        label = LEVEL_LABEL.get(d.level, d.level)
        lines.append(
            f"| {d.ask_id} | 第{d.page_num}页 | {label} | "
            f"{d.assigned_student} | {d.backup_student} | — | — |"
        )
    return "\n".join(lines) + "\n"


def _build_section_a(dispatches: list[QuestionDispatch]) -> str:
    if not dispatches:
        return "## 【板块A】ASK课堂提问调度稿\n\n（本课时无结构化课堂提问）\n"

    lines = ["## 【板块A】ASK课堂提问调度稿", ""]
    for d in dispatches:
        activity_line = (
            f"（第{d.page_num}页，{d.activity_ref}）"
            if d.activity_ref else f"（第{d.page_num}页）"
        )
        lines.append(f"### {d.ask_id} {activity_line}")
        lines.append(f"**学生**：{d.assigned_student}")
        if d.backup_student and d.backup_student != "（未分配）":
            lines.append(f"**备用学生**：{d.backup_student}")
        lines.append(f"**问题**：{d.question_text}")

        if d.hints:
            lines.append("**分级备用提示**：")
            for h in d.hints:
                lines.append(f"- {h}")

        if d.expected_answer:
            lines.append(f"**参考答案**：{d.expected_answer}")

        lines.append("**即时调整规则**：")
        lines.append("- 若答不出：给支架或请备用学生补充后复述。")
        lines.append("- 若答出基本点：追加理由追问。")
        lines.append("- 若答得完整：追加比较、评价或迁移追问。")

        lines.append("")
        lines.append(PAGE_BREAK)
        lines.append("")

    return "\n".join(lines)


def build_dispatch_md(
    dispatches: list[QuestionDispatch],
    lesson_id: str,
    lesson_name: str,
    lesson_plan_path: str,
) -> str:
    fm = _build_dispatch_front_matter(lesson_id, lesson_name, lesson_plan_path)
    body = "\n".join([
        f"# {lesson_name} 课堂提问调度稿",
        "",
        _build_question_table(dispatches),
        "",
        _build_section_a(dispatches),
        "",
        "## 评分量规",
        "",
        "| 维度 | 评分标准 | 分 |",
        "|:---|:---|:---|",
        "| **准确性** | 答案完全正确/基本正确/错误 | 2/1/0 |",
        "| **完整性** | 逻辑完整有条理/基本完整/不完整 | 2/1/0 |",
        "| **表达力** | 使用规范数学术语/语言不够规范 | 1/0 |",
        "",
        "*本调度稿配合学生课件使用，供教师课堂点名、支架、追问和评价参考。*",
        "",
    ])
    return fm + "\n" + body


# ── CLI 入口 ──────────────────────────────────────────────

def _parse_lesson_meta(lesson_text: str) -> dict[str, str]:
    """从教学设计 YAML front matter 提取 lesson_id 等。"""
    if not lesson_text.startswith("---\n"):
        return {}
    end = lesson_text.find("\n---", 4)
    if end == -1:
        return {}
    meta: dict[str, str] = {}
    for line in lesson_text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(
        description="课件后处理：修正 LaTeX + 禁止词扫描 + 生成调度稿"
    )
    parser.add_argument(
        "--courseware-md", type=Path, required=True,
        help="课件 MD 草稿路径（LLM 手写）"
    )
    parser.add_argument(
        "--lesson-file", type=Path, required=True,
        help="教学设计文件路径（从中解析 ASK 数组）"
    )
    parser.add_argument(
        "--students-file", type=Path, default=None,
        help="学生成绩数据路径（从中分配提问学生）"
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="输出目录（课件 + 调度稿写入此处）"
    )
    parser.add_argument(
        "--courseware-only", action="store_true",
        help="只处理后输出课件 MD，不生成调度稿"
    )
    parser.add_argument(
        "--dispatch-only", action="store_true",
        help="只生成调度稿 MD，不输出课件"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅检查不写入文件"
    )
    args = parser.parse_args()

    cw_path: Path = args.courseware_md.resolve()
    lesson_path: Path = args.lesson_file.resolve()
    out_dir: Path = args.output_dir.resolve()

    # 检查输入
    if not cw_path.exists():
        print(f"❌ 课件草稿不存在: {cw_path}", file=sys.stderr)
        return 1
    if not lesson_path.exists():
        print(f"❌ 教学设计不存在: {lesson_path}", file=sys.stderr)
        return 1

    courseware_text = cw_path.read_text(encoding="utf-8")
    lesson_text = lesson_path.read_text(encoding="utf-8")
    lesson_meta = _parse_lesson_meta(lesson_text)
    lesson_id = lesson_meta.get("lesson_id", "")
    lesson_name = lesson_meta.get("lesson_name", "")

    # ── 解析学生数据 ──
    student_names: list[str] = []
    students_by_layer: dict[str, list[str]] = {"B": [], "M": [], "E": []}
    if args.students_file:
        students_path: Path = args.students_file.resolve()
        if students_path.exists():
            students_text = students_path.read_text(encoding="utf-8")
            students_by_layer = _parse_students(students_text)
            for names in students_by_layer.values():
                student_names.extend(names)

    # ── 后处理课件 MD ──
    all_errors: list[str] = []

    if not args.dispatch_only:
        processed_cw, cw_errors = process_courseware(courseware_text, student_names)
        all_errors.extend(cw_errors)
        if cw_errors:
            for e in cw_errors:
                print(f"  ❌ {e}")

        cw_out = out_dir / f"lesson-{lesson_id}-courseware.md"
        print(f"📄 后处理课件: {cw_out}")
        if not cw_errors and not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            cw_out.write_text(processed_cw, encoding="utf-8")
            print(f"  ✅ 课件已写入 ({cw_out.stat().st_size} bytes)")

    # ── 生成调度稿 ──
    if not args.courseware_only:
        # 解析 ASK
        ask_questions = _parse_ask_from_lesson(lesson_text)
        if not ask_questions:
            print("  ⚠️  未从教学设计中解析到 ASK 问题")
        else:
            print(f"  📋 解析到 {len(ask_questions)} 个 ASK 问题")

        # 匹配活动板块
        activity_map = _parse_activity_map(lesson_text)
        ask_with_activity: list[AskQuestion] = []
        for aq in ask_questions:
            ref = activity_map.get(aq.ask_id, "")
            ask_with_activity.append(AskQuestion(
                ask_id=aq.ask_id, level=aq.level,
                question_text=aq.question_text, hints=aq.hints,
                expected_answer=aq.expected_answer,
                activity_ref=ref
            ))

        # 匹配页码
        # 使用已处理的课件文本（如果有）或原始文本
        cw_for_match = processed_cw if not args.dispatch_only and not cw_errors else courseware_text
        page_map = _match_ask_to_pages(cw_for_match, ask_with_activity)

        # 分配学生
        student_assign = _assign_students(ask_with_activity, students_by_layer)

        # 组装调度数据
        dispatches: list[QuestionDispatch] = []
        for aq in ask_with_activity:
            primary, backup = student_assign.get(aq.ask_id, ("（未分配）", "（未分配）"))
            dispatches.append(QuestionDispatch(
                ask_id=aq.ask_id, level=aq.level,
                page_num=page_map.get(aq.ask_id, 0),
                question_text=aq.question_text, hints=aq.hints,
                expected_answer=aq.expected_answer,
                activity_ref=aq.activity_ref,
                assigned_student=primary, backup_student=backup,
            ))

        dispatch_md = build_dispatch_md(
            dispatches, lesson_id, lesson_name,
            str(lesson_path.relative_to(lesson_path.parent.parent.parent))
        )

        dispatch_out = out_dir / f"lesson-{lesson_id}-dispatch.md"
        print(f"📄 生成调度稿: {dispatch_out}")
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            dispatch_out.write_text(dispatch_md, encoding="utf-8")
            print(f"  ✅ 调度稿已写入 ({dispatch_out.stat().st_size} bytes)")

    if all_errors:
        print(f"\n❌ 后处理失败，共 {len(all_errors)} 个阻断错误")
        return 1

    print("\n✅ 课件后处理完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
