#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import MinerU quadrilateral handouts into the review-handout knowledge base."""

from __future__ import annotations

import argparse
from html import unescape
from html.parser import HTMLParser
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


@dataclass(frozen=True)
class SourceDoc:
    source_dir: Path
    md_path: Path
    lesson_no: str
    short_title: str
    version: str

    @property
    def file_stem(self) -> str:
        return f"{self.short_title}（{self.version}）"

    @property
    def image_prefix(self) -> str:
        return f"{self.lesson_no}-{self.version}"


def parse_source_dir(path: Path) -> SourceDoc | None:
    full_md = path / "full.md"
    if not full_md.exists():
        return None

    clean_name = re.sub(r"\.pdf-[0-9a-fA-F-]+$", "", path.name)
    match = re.match(r"^(第\d{2}讲)\s+(.+?)（(原卷版|解析版)）$", clean_name)
    if not match:
        return None

    lesson_no, raw_title, version = match.group(1), match.group(2), match.group(3)
    raw_title = re.sub(r"（[^）]*(知识点|热点题型|习题巩固)[^）]*）", "", raw_title)
    raw_title = re.sub(r"\s+", " ", raw_title).strip()
    short_title = f"{lesson_no} {raw_title}"
    return SourceDoc(path, full_md, lesson_no, short_title, version)


def discover_sources(mineru_root: Path) -> list[SourceDoc]:
    sources = [doc for item in mineru_root.iterdir() if item.is_dir() for doc in [parse_source_dir(item)] if doc]
    return sorted(sources, key=lambda doc: (doc.lesson_no, doc.version != "原卷版"))


def normalize_latex_inner(inner: str) -> str:
    text = inner.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(?<=\d)\s+(?=\d)", "", text)
    text = re.sub(r"\s*_\s*\{\s*([^{}]+?)\s*\}", r"_{\1}", text)
    text = re.sub(r"\s*\^\s*\{\s*([^{}]+?)\s*\}", r"^{\1}", text)
    text = re.sub(r"\s*\{\s*=\s*\}\s*", " = ", text)
    text = re.sub(r"\s*/\s*/\s*", r" \\parallel ", text)
    text = re.sub(r"\\\s*bot\b", r"\\bot", text)
    text = re.sub(r"\\\s*(because|therefore|angle|triangle|parallel|bot|circ|frac|sqrt)\b", r"\\\1", text)
    text = re.sub(r"\s*,\s*", ", ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_formula_markup(text: str, report: list[str], filename: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\\\[\s*([\s\S]*?)\s*\\\]", lambda m: f"\n$$\n{normalize_latex_inner(m.group(1))}\n$$\n", text)
    text = re.sub(r"\\\(\s*([\s\S]*?)\s*\\\)", lambda m: rf"\({normalize_latex_inner(m.group(1))}\)", text)

    def display_repl(match: re.Match[str]) -> str:
        inner = normalize_latex_inner(match.group(1))
        if not inner:
            report.append(f"- {filename}: 删除空 display 公式块。")
            return ""
        return f"\n$$\n{inner}\n$$\n"

    text = re.sub(r"(?<!\\)\$\$\s*([\s\S]*?)\s*(?<!\\)\$\$", display_repl, text)

    def inline_repl(match: re.Match[str]) -> str:
        inner = normalize_latex_inner(match.group(1))
        line = text.count("\n", 0, match.start()) + 1
        if "\n" in match.group(1):
            report.append(f"- {filename}:{line}: 行内公式跨行，已压缩为空格。")
        if not inner:
            report.append(f"- {filename}:{line}: 删除空行内公式。")
            return ""
        return rf"\({inner}\)"

    text = re.sub(r"(?<!\\)\$(?!\$)(.*?)(?<!\\)\$(?!\$)", inline_repl, text, flags=re.S)
    return text


class SimpleTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self.current_row: list[str] | None = None
        self.current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "tr":
            self.current_row = []
        elif tag.lower() in {"td", "th"}:
            self.current_cell = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"td", "th"} and self.current_cell is not None and self.current_row is not None:
            cell = re.sub(r"\s+", " ", "".join(self.current_cell)).strip()
            self.current_row.append(cell)
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            self.rows.append(self.current_row)
            self.current_row = None

    def handle_data(self, data: str) -> None:
        if self.current_cell is not None:
            self.current_cell.append(data)


def html_table_to_markdown(match: re.Match[str]) -> str:
    parser = SimpleTableParser()
    parser.feed(match.group(0))
    rows = [row for row in parser.rows if row]
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    escaped = [[unescape(cell).replace("|", r"\|") for cell in row] for row in normalized]
    lines = ["| " + " | ".join(escaped[0]) + " |"]
    lines.append("| " + " | ".join(["---"] * width) + " |")
    for row in escaped[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def remove_text_image_blocks(text: str) -> str:
    return re.sub(
        r"\n?<details>\s*<summary>\s*text_image\s*</summary>[\s\S]*?</details>\s*",
        "\n\n",
        text,
        flags=re.I,
    )


def normalize_markdown_only(text: str) -> str:
    text = remove_text_image_blocks(text)
    text = re.sub(r"<table[\s\S]*?</table>", html_table_to_markdown, text, flags=re.I)
    text = re.sub(r"</?(?:tbody|thead)>", "", text, flags=re.I)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def normalize_math_symbols(text: str) -> str:
    math_span = re.compile(r"(\\\(.*?\\\)|(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$)", re.S)

    def normalize_plain_segment(segment: str) -> str:
        segment = re.sub(r"(\\\([^)]*\^\{?\\circ\}?[^)]*\\\))\s*°", r"\1", segment)
        segment = re.sub(r"∠\s*([A-Za-z][A-Za-z0-9]*)", lambda m: rf"\(\angle {m.group(1)}\)", segment)
        segment = re.sub(r"△\s*([A-Za-z][A-Za-z0-9]*)", lambda m: rf"\(\triangle {m.group(1)}\)", segment)
        segment = re.sub(
            r"([A-Za-z][A-Za-z0-9]*)\s*⊥\s*([A-Za-z][A-Za-z0-9]*)",
            lambda m: rf"\({m.group(1)} \bot {m.group(2)}\)",
            segment,
        )
        segment = re.sub(
            r"([A-Za-z][A-Za-z0-9]*)\s*∥\s*([A-Za-z][A-Za-z0-9]*)",
            lambda m: rf"\({m.group(1)} \parallel {m.group(2)}\)",
            segment,
        )
        segment = re.sub(r"([<>])?=\s*", lambda m: m.group(0), segment)
        segment = re.sub(r"(\d+)\s*°", lambda m: rf"\({m.group(1)}^\circ\)", segment)
        segment = segment.replace("≤", r"\(\le\)")
        segment = segment.replace("≥", r"\(\ge\)")
        segment = segment.replace("≠", r"\(\ne\)")
        return segment

    parts: list[str] = []
    last = 0
    for match in math_span.finditer(text):
        parts.append(normalize_plain_segment(text[last : match.start()]))
        parts.append(match.group(0))
        last = match.end()
    parts.append(normalize_plain_segment(text[last:]))
    return "".join(parts)


def image_files(source_dir: Path) -> list[Path]:
    img_dir = source_dir / "images"
    if not img_dir.exists():
        return []
    return sorted([p for p in img_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS])


def rewrite_image_references(text: str, image_map: dict[str, str]) -> str:
    def replace_path(path_text: str) -> str:
        normalized = path_text.replace("\\", "/")
        name = Path(normalized).name
        return f"images/{image_map.get(name, name)}"

    text = re.sub(
        r"!\[([^\]]*)\]\((?:\./)?images/([^)]+)\)",
        lambda m: f"![{m.group(1)}]({replace_path(m.group(2))})",
        text,
    )
    text = re.sub(
        r'(<img\b[^>]*?\bsrc=["\'])(?:\./)?images/([^"\']+)(["\'])',
        lambda m: f"{m.group(1)}{replace_path(m.group(2))}{m.group(3)}",
        text,
        flags=re.I,
    )
    return text


def braces_balanced(text: str) -> bool:
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


def screen_formulas(text: str, filename: str) -> list[str]:
    findings: list[str] = []
    if len(re.findall(r"(?<!\\)\$(?!\$)", text)) % 2:
        findings.append(f"- {filename}: 存在未配对的单 `$`。")
    if len(re.findall(r"(?<!\\)\$\$", text)) % 2:
        findings.append(f"- {filename}: 存在未配对的 `$$`。")
    if len(re.findall(r"\\\(", text)) != len(re.findall(r"\\\)", text)):
        findings.append(f"- {filename}: `\\(` 与 `\\)` 数量不一致。")

    formula_pattern = re.compile(r"\\\((.*?)\\\)|(?<!\\)\$\$\s*([\s\S]*?)\s*(?<!\\)\$\$", re.S)
    for match in formula_pattern.finditer(text):
        formula = (match.group(1) if match.group(1) is not None else match.group(2)).strip()
        line = text.count("\n", 0, match.start()) + 1
        if not formula:
            findings.append(f"- {filename}:{line}: 空公式。")
            continue
        if not braces_balanced(formula):
            findings.append(f"- {filename}:{line}: LaTeX 花括号未配平：`{formula[:80]}`")
        if re.search(r"\d\s+\d", formula):
            findings.append(f"- {filename}:{line}: 疑似 OCR 拆开的数字：`{formula[:80]}`")
        if re.search(r"\\[A-Za-z]+(?:\s*\{[^{}]*\})?\s*$", formula) and len(formula.split()) == 1:
            findings.append(f"- {filename}:{line}: 疑似截断公式：`{formula[:80]}`")
        if any(token in formula for token in [r"\dag", r"\bigcup", r"\prime"]):
            findings.append(f"- {filename}:{line}: 疑似 OCR 错识图形/符号：`{formula[:80]}`")
    return findings


def import_doc(doc: SourceDoc, target_dir: Path, report: list[str]) -> tuple[int, int]:
    images_dir = target_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    copied_images = 0
    image_map: dict[str, str] = {}
    for img in image_files(doc.source_dir):
        new_name = f"{doc.image_prefix}-{img.name}"
        shutil.copy2(img, images_dir / new_name)
        image_map[img.name] = new_name
        copied_images += 1

    content = doc.md_path.read_text(encoding="utf-8")
    content = rewrite_image_references(content, image_map)
    content = normalize_markdown_only(content)
    content = normalize_formula_markup(content, report, f"{doc.file_stem}.md")
    content = normalize_math_symbols(content)
    content = content.strip() + "\n"

    output_path = target_dir / f"{doc.file_stem}.md"
    output_path.write_text(content, encoding="utf-8")
    report.extend(screen_formulas(content, output_path.name))
    return 1, copied_images


def run_pandoc_check(target_dir: Path, files: list[str]) -> list[str]:
    findings: list[str] = []
    pandoc = shutil.which("pandoc")
    if not pandoc:
        findings.append("- Pandoc 未在 PATH 中找到，已跳过 dry run。")
        return findings
    for name in files:
        path = target_dir / name
        if not path.exists():
            findings.append(f"- Pandoc 检查跳过，文件不存在：{name}")
            continue
        result = subprocess.run(
            [pandoc, str(path), "--from", "markdown+tex_math_dollars+tex_math_single_backslash", "--to", "native"],
            cwd=str(target_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            findings.append(f"- Pandoc dry run 通过：{name}")
        else:
            findings.append(f"- Pandoc dry run 失败：{name}\n  {result.stderr.strip()}")
    return findings


def validate_outputs(target_dir: Path, expected_docs: int, expected_images: int) -> list[str]:
    findings: list[str] = []
    docs = sorted(target_dir.glob("第*.md"))
    images = sorted((target_dir / "images").glob("*")) if (target_dir / "images").exists() else []
    findings.append(f"- Markdown 文件数：{len(docs)} / 预期 {expected_docs}")
    findings.append(f"- 图片文件数：{len([p for p in images if p.is_file()])} / 预期 {expected_images}")

    for md in docs:
        content = md.read_text(encoding="utf-8")
        if "C:\\Users\\Administrator\\MinerU" in content or "MinerU" in content:
            findings.append(f"- {md.name}: 仍包含 MinerU 源路径。")
        for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", content):
            path = match.group(1)
            if not path.startswith("images/"):
                findings.append(f"- {md.name}: 非同级 images 图片路径：{path}")
                continue
            if not (target_dir / path).exists():
                findings.append(f"- {md.name}: 图片不存在：{path}")
    return findings


def write_report(target_dir: Path, report: list[str], validation: list[str], pandoc: list[str]) -> None:
    lines = [
        "# 公式筛查记录",
        "",
        "## 自动处理说明",
        "",
        "- 已将 `$...$` 行内公式转换为 `\\(...\\)`。",
        "- 已将 `$$...$$` 与 `\\[...\\]` 独立公式统一为 `$$` 块。",
        "- 已清理空 display 公式块，并记录到本文件。",
        "- 已对明显 OCR 产生的数字空格、下标、上标、平行、垂直等格式做轻量规范化。",
        "",
        "## 可疑公式与处理记录",
        "",
    ]
    lines.extend(report or ["- 未发现自动筛查项。"])
    lines.extend(["", "## 结构与资源检查", ""])
    lines.extend(validation)
    lines.extend(["", "## Pandoc Dry Run", ""])
    lines.extend(pandoc)
    (target_dir / "公式筛查记录.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mineru-root", default=r"C:\Users\Administrator\MinerU")
    parser.add_argument(
        "--target-dir",
        default=r"C:\Users\Administrator\OneDrive\math-resource-engine\knowledge\reviews\quadrilaterals",
    )
    args = parser.parse_args()

    mineru_root = Path(args.mineru_root)
    target_dir = Path(args.target_dir)
    if not mineru_root.exists():
        raise SystemExit(f"MinerU directory does not exist: {mineru_root}")

    sources = discover_sources(mineru_root)
    if len(sources) != 20:
        raise SystemExit(f"Expected 20 source docs, found {len(sources)}")

    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "images").mkdir(parents=True, exist_ok=True)

    report: list[str] = []
    doc_count = 0
    image_count = 0
    for source in sources:
        docs, images = import_doc(source, target_dir, report)
        doc_count += docs
        image_count += images

    validation = validate_outputs(target_dir, doc_count, image_count)
    pandoc = run_pandoc_check(
        target_dir,
        ["第01讲 平行四边形的性质（原卷版）.md", "第05讲 正方形（解析版）.md"],
    )
    write_report(target_dir, report, validation, pandoc)

    print(f"Imported Markdown: {doc_count}")
    print(f"Copied images: {image_count}")
    print(f"Target: {target_dir}")
    print("Report: 公式筛查记录.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
