#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reorder a merged review-lesson DOCX into the three-module structure.

The script keeps original Word XML blocks for questions and explanations. It
only adds module headings and continuous question-number prefixes, so inline
images, formula pictures, and embedded objects remain in their original runs.
"""

from __future__ import annotations

import argparse
import copy
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

W_NS = NS["w"]
DOCUMENT_XML = "word/document.xml"
SKIP_AFTER_PATTERN = re.compile(r"原始数量与选用数量对比")


@dataclass
class Block:
    kind: str
    elements: list[etree._Element]
    title: str
    type_title: str | None = None


def parse_xml(data: bytes) -> etree._ElementTree:
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    return etree.ElementTree(etree.fromstring(data, parser=parser))


def xml_bytes(tree: etree._ElementTree) -> bytes:
    return etree.tostring(
        tree,
        xml_declaration=True,
        encoding="UTF-8",
        standalone=True,
    )


def element_text(element: etree._Element) -> str:
    return "".join(element.xpath(".//w:t/text()", namespaces=NS)).strip()


def body_children(document: etree._ElementTree) -> list[etree._Element]:
    body = document.getroot().find("w:body", NS)
    if body is None:
        return []
    return list(body)


def body_without_section(document: etree._ElementTree) -> list[etree._Element]:
    return [child for child in body_children(document) if child.tag != f"{{{W_NS}}}sectPr"]


def first_text_node(element: etree._Element) -> etree._Element | None:
    nodes = element.xpath(".//w:t", namespaces=NS)
    return nodes[0] if nodes else None


def text_nodes(element: etree._Element) -> list[etree._Element]:
    return list(element.xpath(".//w:t", namespaces=NS))


def set_paragraph_text(element: etree._Element, text: str) -> None:
    nodes = text_nodes(element)
    if not nodes:
        return
    nodes[0].text = text
    for node in nodes[1:]:
        node.text = ""


def full_paragraph_text(element: etree._Element) -> str:
    return "".join(node.text or "" for node in text_nodes(element))


def prefix_first_text(element: etree._Element, prefix: str) -> None:
    if text_nodes(element):
        set_paragraph_text(element, prefix + full_paragraph_text(element))


def replace_first_text(element: etree._Element, pattern: str, replacement: str) -> None:
    if text_nodes(element):
        set_paragraph_text(element, re.sub(pattern, replacement, full_paragraph_text(element), count=1))


def rewrite_knowledge_heading(element: etree._Element, number: int) -> None:
    if text_nodes(element):
        set_paragraph_text(
            element,
            re.sub(r"知识点\s*\d+", f"知识点{number:02d}", full_paragraph_text(element), count=1),
        )


def make_paragraph(text: str, style: str | None = None) -> etree._Element:
    paragraph = etree.Element(f"{{{W_NS}}}p")
    if style:
        p_pr = etree.SubElement(paragraph, f"{{{W_NS}}}pPr")
        p_style = etree.SubElement(p_pr, f"{{{W_NS}}}pStyle")
        p_style.set(f"{{{W_NS}}}val", style)
    run = etree.SubElement(paragraph, f"{{{W_NS}}}r")
    text_node = etree.SubElement(run, f"{{{W_NS}}}t")
    text_node.text = text
    return paragraph


def classify(text: str) -> str | None:
    compact = re.sub(r"\s+", "", text)
    if not compact:
        return None
    if re.search(r"知识点\d+", compact):
        return "knowledge"
    if compact.startswith("【即学即练"):
        return "instant"
    if re.search(r"题型\d+", compact):
        return "type"
    if compact.startswith("【典例"):
        return "example"
    if compact.startswith("【变式"):
        return "variant"
    if SKIP_AFTER_PATTERN.search(text):
        return "stop"
    return None


def split_blocks(elements: list[etree._Element]) -> list[Block]:
    blocks: list[Block] = []
    current: Block | None = None
    current_type: str | None = None

    def flush() -> None:
        nonlocal current
        if current and current.elements:
            blocks.append(current)
        current = None

    for element in elements:
        text = element_text(element)
        kind = classify(text)
        if kind == "stop":
            break
        if kind == "type":
            flush()
            current_type = text
            blocks.append(Block("type", [copy.deepcopy(element)], text))
            continue
        if kind in {"knowledge", "instant", "example", "variant"}:
            flush()
            current = Block(kind, [copy.deepcopy(element)], text, current_type)
            continue
        if current is not None:
            current.elements.append(copy.deepcopy(element))

    flush()
    return blocks


def question_markers(blocks: list[Block], kind: str) -> list[Block]:
    return [block for block in blocks if block.kind == kind]


def pair_knowledge_with_instants(blocks: list[Block]) -> list[tuple[Block, Block | None]]:
    pairs: list[tuple[Block, Block | None]] = []
    for index, block in enumerate(blocks):
        if block.kind != "knowledge":
            continue
        next_knowledge = next(
            (pos for pos in range(index + 1, len(blocks)) if blocks[pos].kind == "knowledge"),
            len(blocks),
        )
        instant = next(
            (candidate for candidate in blocks[index + 1 : next_knowledge] if candidate.kind == "instant"),
            None,
        )
        pairs.append((block, instant))
    return pairs


def select_homework_variants(variants: list[Block], count: int = 10) -> list[Block]:
    if len(variants) <= count:
        return variants
    buckets: dict[str, list[Block]] = {}
    order: list[str] = []
    for block in variants:
        key = block.type_title or "未归类"
        if key not in buckets:
            buckets[key] = []
            order.append(key)
        buckets[key].append(block)

    selected: list[Block] = []
    round_index = 0
    while len(selected) < count:
        progressed = False
        for key in order:
            bucket = buckets[key]
            if round_index < len(bucket):
                selected.append(bucket[round_index])
                progressed = True
                if len(selected) == count:
                    break
        if not progressed:
            break
        round_index += 1
    return selected


def append_block(
    target: list[etree._Element],
    block: Block,
    number: int | None = None,
    strip_label: bool = False,
    knowledge_number: int | None = None,
) -> None:
    elements = [copy.deepcopy(element) for element in block.elements]
    if number is not None and elements:
        if strip_label:
            replace_first_text(elements[0], r"^\s*【(?:即学即练|典例|变式)\s*\d*】\s*", "")
        prefix_first_text(elements[0], f"{number}．")
    if knowledge_number is not None and elements:
        rewrite_knowledge_heading(elements[0], knowledge_number)
    target.extend(elements)


def build_reordered_body(document: etree._ElementTree) -> tuple[list[etree._Element], dict[str, int]]:
    original_elements = body_without_section(document)
    blocks = split_blocks(original_elements)

    knowledge_pairs = pair_knowledge_with_instants(blocks)
    instants = question_markers(blocks, "instant")
    examples = question_markers(blocks, "example")
    variants = question_markers(blocks, "variant")
    homework = select_homework_variants(variants, 10)

    result: list[etree._Element] = [
        make_paragraph("第 01-02 讲 平行四边形性质与判定 复习讲义", "Heading1"),
        make_paragraph("知识点与例题", "Heading2"),
    ]

    question_number = 1
    example_count = 0
    for index, (block, instant) in enumerate(knowledge_pairs, start=1):
        append_block(result, block, knowledge_number=index)
        if instant is not None:
            result.append(make_paragraph("例题讲解", "Heading2"))
            append_block(result, instant, question_number, strip_label=True)
            question_number += 1
            example_count += 1

    result.append(make_paragraph("当堂练习", "Heading2"))
    for block in examples:
        append_block(result, block, question_number, strip_label=True)
        question_number += 1

    result.append(make_paragraph("课后作业", "Heading2"))
    for block in homework:
        append_block(result, block, question_number, strip_label=True)
        question_number += 1

    return result, {
        "knowledge": len(knowledge_pairs),
        "examples": example_count,
        "practice": len(examples),
        "homework": len(homework),
        "variants_available": len(variants),
        "total_questions": question_number - 1,
    }


def reorder_docx(input_path: Path, output_path: Path) -> dict[str, int]:
    with ZipFile(input_path, "r") as zf:
        entries = {name: zf.read(name) for name in zf.namelist()}

    document = parse_xml(entries[DOCUMENT_XML])
    body = document.getroot().find("w:body", NS)
    if body is None:
        raise RuntimeError("docs缺少 word/document.xml 的 body")

    sect_pr = body.find("w:sectPr", NS)
    new_elements, stats = build_reordered_body(document)

    for child in list(body):
        body.remove(child)
    for element in new_elements:
        body.append(element)
    if sect_pr is not None:
        body.append(sect_pr)

    entries[DOCUMENT_XML] = xml_bytes(document)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = Path(tmp.name)
    try:
        with ZipFile(tmp_path, "w", ZIP_DEFLATED) as zf:
            for name, data in entries.items():
                zf.writestr(name, data)
        shutil.move(str(tmp_path), output_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reorder merged review DOCX into three modules.")
    parser.add_argument("input", help="Merged DOCX input path.")
    parser.add_argument("--output", required=True, help="Output DOCX path.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not input_path.exists():
        parser.error(f"输入文件不存在: {input_path}")

    stats = reorder_docx(input_path, output_path)
    print(output_path)
    print(
        "知识点 {knowledge}, 例题 {examples}, 当堂练习 {practice}, "
        "课后作业 {homework}, 可用变式 {variants_available}, 总题数 {total_questions}".format(**stats)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
