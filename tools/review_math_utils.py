#!/usr/bin/env python3
"""Utilities for review-handout markup normalization and validation."""

from __future__ import annotations

import re


CIRCLED_NUMBERS = {
    str(index): char
    for index, char in enumerate("①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳", 1)
}

UNSUPPORTED_LATEX_COMMANDS = {
    r"\textcircled": "用 Unicode 编号（如 ①）放在公式外，例：① $y = kx+b$",
    r"\begin": "当前 DOCX 导出不支持 LaTeX 环境",
    r"\end": "当前 DOCX 导出不支持 LaTeX 环境",
    r"\overbrace": "当前 DOCX 导出不支持复杂上下标装饰",
    r"\underbrace": "当前 DOCX 导出不支持复杂上下标装饰",
    r"\overset": "当前 DOCX 导出不支持复杂上下标装饰",
    r"\underset": "当前 DOCX 导出不支持复杂上下标装饰",
    r"\tikz": "当前 DOCX 导出不支持 TikZ 图形命令",
    r"\bf": "字体命令会导致 DOCX 残留，请删除并保留普通变量",
    r"\mathbf": "字体命令会导致 DOCX 残留，请删除并保留普通变量",
    r"\mathrm": "字体命令会导致 DOCX 残留，请删除并保留普通变量",
    r"\mathit": "字体命令会导致 DOCX 残留，请删除并保留普通变量",
    r"\mathsf": "字体命令会导致 DOCX 残留，请删除并保留普通变量",
}


def normalize_review_math_markup(text: str) -> str:
    """Normalize review-handout markup before writing Markdown."""

    def replace_circled_formula(match: re.Match[str]) -> str:
        number = match.group(1)
        expression = match.group(2).strip()
        marker = CIRCLED_NUMBERS.get(number, f"({number})")
        if not expression:
            return marker
        return f"{marker} ${expression}$"

    normalized = remove_details_blocks(text)
    normalized = convert_html_tables_to_markdown(normalized)
    normalized = re.sub(
        r"\$\\textcircled\s*\{\s*(\d{1,2})\s*\}\s*([^$]*?)\$",
        replace_circled_formula,
        normalized,
    )
    normalized = re.sub(
        r"\$\$\s*([\s\S]*?)\s*\$\$",
        lambda match: re.sub(r"\s+", " ", match.group(1)).strip(),
        normalized,
    )
    normalized = re.sub(r"\\(?:bf|mathbf|mathrm|mathit|mathsf)\s*\{\s*([^{}]*?)\s*\}", r"\1", normalized)
    normalized = re.sub(r"\\bf\b\s*", "", normalized)
    normalized = re.sub(r"\\scriptstyle\b\s*", "", normalized)
    normalized = re.sub(r"\\\(([\s\S]*?)\\\)", lambda match: normalize_latex_text(match.group(1)), normalized)
    normalized = normalize_latex_text(normalized)
    return normalized


def normalize_latex_text(text: str) -> str:
    normalized = text
    normalized = re.sub(r"\^\{\s*\\dag\s*\\dag\s*\}\s*\\bigcup\s*([A-Z](?:\s+[A-Z]){3})\s*\^\{\s*\\dag\s*\\prime\s*\}", lambda match: "▱ " + match.group(1).replace(" ", ""), normalized)
    normalized = re.sub(r"\^\{\s*\}\s*([A-Z](?:\s+[A-Z]){3})\s*\^\{\s*\}", lambda match: "▱ " + match.group(1).replace(" ", ""), normalized)
    replacements = {
        r"\parallel": "∥",
        r"\bot": "⊥",
        r"\therefore": "∴",
        r"\triangle": "△",
        r"\bigtriangleup": "△",
        r"\angle": "∠",
        r"\circ": "°",
        r"\le": "≤",
        r"\ge": "≥",
        r"\ne": "≠",
        r"\cdot": "·",
    }
    for latex, unicode in replacements.items():
        normalized = normalized.replace(latex, unicode)
    normalized = re.sub(r"\\sqrt\s*\{\s*([^{}]+?)\s*\}", r"√\1", normalized)
    normalized = re.sub(r"\\frac\s*\{\s*([^{}]+?)\s*\}\s*\{\s*([^{}]+?)\s*\}", r"\1/\2", normalized)
    normalized = re.sub(r"([0-9])\s*\^\{\s*2\s*\}", r"\1²", normalized)
    normalized = re.sub(r"\^\{\s*2\s*\}", "²", normalized)
    normalized = re.sub(r"\^\{\s*\\circ\s*\}", "°", normalized)
    normalized = re.sub(r"\^\{\s*\}", "", normalized)
    normalized = re.sub(r"_\s*\{\s*\}", "", normalized)
    normalized = re.sub(r"_\s*\{\s*(?:\\mathrm\s*)?\{\s*i\s*\}\s*\}", "", normalized)
    normalized = re.sub(r"\\mathrm\s*\{\s*([^{}]*?)\s*\}", r"\1", normalized)
    normalized = re.sub(r"\\[a-zA-Z]+\s*", "", normalized)
    normalized = re.sub(r"\{\s*([^{}]*?)\s*\}", r"\1", normalized)
    normalized = re.sub(r"\b([A-Z])\s+([A-Z])\s+([A-Z])\s+([A-Z])\b", r"\1\2\3\4", normalized)
    normalized = re.sub(r"\b([A-Z])\s+([A-Z])\s+([A-Z])\b", r"\1\2\3", normalized)
    normalized = re.sub(r"\b([A-Z])\s+([A-Z])\b", r"\1\2", normalized)
    normalized = re.sub(r"\bc\s*m\b", "cm", normalized)
    normalized = re.sub(r"\bm\s*m\b", "mm", normalized)
    normalized = normalized.replace("° °", "°")
    normalized = re.sub(r"\s+([，。；：、）])", r"\1", normalized)
    normalized = re.sub(r"([（])\s+", r"\1", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def remove_details_blocks(text: str) -> str:
    """Remove image OCR/helper blocks that duplicate visible images in DOCX."""
    return re.sub(
        r"\n?<details>\s*\n<summary>[^<]*</summary>\s*\n[\s\S]*?\n</details>\s*\n?",
        "\n",
        text,
    )


def convert_html_tables_to_markdown(text: str) -> str:
    """Convert simple HTML tables emitted by source handouts into Markdown tables."""

    def replace_table(match: re.Match[str]) -> str:
        table = match.group(0)
        rows: list[list[str]] = []
        for row_match in re.finditer(r"<tr>([\s\S]*?)</tr>", table, flags=re.I):
            cells = [
                clean_table_cell(cell_match.group(1))
                for cell_match in re.finditer(r"<t[dh]>([\s\S]*?)</t[dh]>", row_match.group(1), flags=re.I)
            ]
            if cells:
                rows.append(cells)
        if not rows:
            return table
        width = max(len(row) for row in rows)
        padded = [row + [""] * (width - len(row)) for row in rows]
        header = padded[0]
        separator = ["---"] * width
        body = padded[1:]
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(separator) + " |",
        ]
        lines.extend("| " + " | ".join(row) + " |" for row in body)
        return "\n".join(lines)

    return re.sub(r"<table>[\s\S]*?</table>", replace_table, text, flags=re.I)


def clean_table_cell(text: str) -> str:
    cell = re.sub(r"<[^>]+>", "", text)
    cell = cell.replace("|", "｜")
    return re.sub(r"\s+", " ", cell).strip()


def validate_math_markup(text: str) -> list[str]:
    """Return human-readable errors for Markdown math markup problems."""
    errors: list[str] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if r"\(" in line or r"\)" in line:
            errors.append(f"存在未规范化的 LaTeX 行内公式分隔符：第 {line_no} 行")
        if re.search(r"\^\{\s*\}|_\s*\{\s*\}|\\bigcup|\\dag|c m\s*\^|m m\b", line):
            errors.append(f"存在疑似 OCR/LaTeX 残留：第 {line_no} 行 `{shorten(line)}`")
    dollar_positions = [match.start() for match in re.finditer(r"(?<!\\)\$(?!\$)", text)]
    if len(dollar_positions) % 2 != 0:
        line = line_number(text, dollar_positions[-1]) if dollar_positions else 1
        errors.append(f"数学公式分隔符未闭合：第 {line} 行存在未配对的 $")

    for match in re.finditer(r"(?<!\\)\$(?!\$)(.*?)(?<!\\)\$(?!\$)", text, flags=re.S):
        formula = match.group(1)
        start_line = line_number(text, match.start())
        if "\n" in formula:
            errors.append(f"行内公式跨行：第 {start_line} 行的 $...$ 不应跨越换行")
        if not braces_are_balanced(formula):
            errors.append(f"LaTeX 花括号未配平：第 {start_line} 行公式 `{shorten(formula)}`")
        for command, suggestion in UNSUPPORTED_LATEX_COMMANDS.items():
            if command in formula:
                errors.append(
                    f"不支持的 LaTeX 命令 {command}：第 {start_line} 行，{suggestion}"
                )
        if re.search(r"\\[A-Za-z]+(?:\s*\{[^{}]*\})?\s*$", formula) and len(formula.split()) == 1:
            errors.append(f"疑似截断公式：第 {start_line} 行公式 `{shorten(formula)}`")
    return errors


def braces_are_balanced(text: str) -> bool:
    depth = 0
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def shorten(text: str, limit: int = 60) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"
