#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compact the reordered review DOCX for two-column printing."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
import posixpath
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree
from PIL import Image
import io


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

W_NS = NS["w"]
DOCUMENT_XML = "word/document.xml"


def parse_xml(data: bytes) -> etree._ElementTree:
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    return etree.ElementTree(etree.fromstring(data, parser=parser))


def xml_bytes(tree: etree._ElementTree) -> bytes:
    return etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)


def body(document: etree._ElementTree) -> etree._Element:
    body = document.getroot().find("w:body", NS)
    if body is None:
        raise RuntimeError("缺少正文 body")
    return body


def remove_nonpage_breaks(root: etree._Element) -> int:
    removed = 0
    for br in list(root.xpath(".//w:br[not(@w:type='page')]", namespaces=NS)):
        parent = br.getparent()
        if parent is not None:
            parent.remove(br)
            removed += 1
    return removed


def set_section_to_two_columns(sect_pr: etree._Element) -> None:
    pg_mar = sect_pr.find("w:pgMar", NS)
    if pg_mar is not None:
        pg_mar.set(f"{{{W_NS}}}top", "720")
        pg_mar.set(f"{{{W_NS}}}bottom", "720")
        pg_mar.set(f"{{{W_NS}}}left", "720")
        pg_mar.set(f"{{{W_NS}}}right", "720")
        pg_mar.set(f"{{{W_NS}}}header", "360")
        pg_mar.set(f"{{{W_NS}}}footer", "360")
        pg_mar.set(f"{{{W_NS}}}gutter", "0")
    cols = sect_pr.find("w:cols", NS)
    if cols is None:
        cols = etree.SubElement(sect_pr, f"{{{W_NS}}}cols")
    cols.set(f"{{{W_NS}}}num", "2")
    cols.set(f"{{{W_NS}}}space", "360")
    cols.set(f"{{{W_NS}}}equalWidth", "1")
    cols.set(f"{{{W_NS}}}sep", "1")


def shrink_paragraph_spacing(root: etree._Element) -> int:
    changed = 0
    for p in root.xpath(".//w:p", namespaces=NS):
        ppr = p.find("w:pPr", NS)
        if ppr is None:
            ppr = etree.Element(f"{{{W_NS}}}pPr")
            p.insert(0, ppr)
        spacing = ppr.find("w:spacing", NS)
        if spacing is None:
            spacing = etree.SubElement(ppr, f"{{{W_NS}}}spacing")
        spacing.set(f"{{{W_NS}}}before", "0")
        spacing.set(f"{{{W_NS}}}after", "0")
        spacing.set(f"{{{W_NS}}}line", "240")
        spacing.set(f"{{{W_NS}}}lineRule", "auto")
        changed += 1
    return changed


def shrink_images(root: etree._Element) -> int:
    changed = 0
    for extent in root.xpath(".//wp:extent", namespaces=NS):
        cx = int(extent.get("cx", "0"))
        cy = int(extent.get("cy", "0"))
        if cx <= 0 or cy <= 0:
            continue
        max_cx = 2600000
        if cx > max_cx:
            scale = max_cx / cx
            extent.set("cx", str(int(cx * scale)))
            extent.set("cy", str(int(cy * scale)))
            changed += 1
    return changed


def relationship_map(entries: dict[str, bytes]) -> dict[str, str]:
    rels_data = entries.get("word/_rels/document.xml.rels")
    if not rels_data:
        return {}
    rels = parse_xml(rels_data).getroot()
    return {
        rel.get("Id"): rel.get("Target", "")
        for rel in rels.findall("rel:Relationship", NS)
        if rel.get("Id")
    }


def media_part_from_target(target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join("word", target))


def is_decorative_red_image(entries: dict[str, bytes], relmap: dict[str, str], embed_id: str) -> bool:
    target = relmap.get(embed_id)
    if not target:
        return False
    part = media_part_from_target(target)
    data = entries.get(part)
    if not data:
        return False
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        return False
    width, height = image.size
    if width > 360 or height > 120:
        return False
    small = image.resize((1, 1))
    red, green, blue = small.getpixel((0, 0))
    return red > green + 30 and red > blue + 30


def remove_decorative_red_images(root: etree._Element, entries: dict[str, bytes]) -> int:
    relmap = relationship_map(entries)
    removed = 0
    for para in list(root.xpath(".//w:p", namespaces=NS)):
        text = "".join(para.xpath(".//w:t/text()", namespaces=NS)).strip()
        embeds = para.xpath(".//a:blip/@r:embed", namespaces=NS)
        if not embeds or text:
            continue
        if any(is_decorative_red_image(entries, relmap, embed) for embed in embeds):
            parent = para.getparent()
            if parent is not None:
                parent.remove(para)
                removed += 1
    return removed


def force_text_black(root: etree._Element) -> int:
    changed = 0
    for color in root.xpath(".//w:color", namespaces=NS):
        value = color.get(f"{{{W_NS}}}val")
        if value and value.upper() != "000000":
            color.set(f"{{{W_NS}}}val", "000000")
            changed += 1
    return changed


def compact_option_paragraphs(root: etree._Element) -> int:
    changed = 0
    for p in root.xpath(".//w:p", namespaces=NS):
        text = "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()
        if not text:
            continue
        if not re.match(r"^[ABCD]．", text):
            continue
        nodes = p.xpath(".//w:t", namespaces=NS)
        if not nodes:
            continue
        cells = [part.strip() for part in re.split(r"\t+|\\t+", text) if part.strip()]
        if len(cells) <= 1:
            continue
        # Keep tabs, but compress surrounding whitespace.
        nodes[0].text = re.sub(r"\s+", " ", nodes[0].text or "").strip()
        for node in nodes[1:]:
            node.text = re.sub(r"\s+", " ", node.text or "").strip()
        changed += 1
    return changed


def paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS)).strip()


def make_option_paragraph(options: list[str]) -> etree._Element:
    paragraph = etree.Element(f"{{{W_NS}}}p")
    ppr = etree.SubElement(paragraph, f"{{{W_NS}}}pPr")
    tabs = etree.SubElement(ppr, f"{{{W_NS}}}tabs")
    for pos in (1300, 2600, 3900):
        tab = etree.SubElement(tabs, f"{{{W_NS}}}tab")
        tab.set(f"{{{W_NS}}}val", "left")
        tab.set(f"{{{W_NS}}}pos", str(pos))
    spacing = etree.SubElement(ppr, f"{{{W_NS}}}spacing")
    spacing.set(f"{{{W_NS}}}before", "0")
    spacing.set(f"{{{W_NS}}}after", "0")
    spacing.set(f"{{{W_NS}}}line", "240")
    spacing.set(f"{{{W_NS}}}lineRule", "auto")

    for index, option in enumerate(options):
        if index:
            tab_run = etree.SubElement(paragraph, f"{{{W_NS}}}r")
            etree.SubElement(tab_run, f"{{{W_NS}}}tab")
        run = etree.SubElement(paragraph, f"{{{W_NS}}}r")
        text_node = etree.SubElement(run, f"{{{W_NS}}}t")
        text_node.text = option
    return paragraph


def merge_vertical_options(body_elem: etree._Element) -> int:
    changed = 0
    children = list(body_elem)
    index = 0
    while index < len(children):
        group: list[etree._Element] = []
        options: list[str] = []
        expected = "A"
        cursor = index
        while cursor < len(children):
            child = children[cursor]
            if child.tag != f"{{{W_NS}}}p":
                break
            text = paragraph_text(child)
            match = re.match(rf"^{expected}．\s*(.+)$", text)
            if not match:
                break
            group.append(child)
            options.append(f"{expected}．{match.group(1).strip()}")
            expected = chr(ord(expected) + 1)
            cursor += 1
            if expected > "D":
                break
        if len(group) >= 2:
            merged = make_option_paragraph(options)
            insert_at = body_elem.index(group[0])
            for item in group:
                body_elem.remove(item)
            body_elem.insert(insert_at, merged)
            changed += 1
            children = list(body_elem)
            index = max(insert_at + 1, 0)
            continue
        index += 1
    return changed


def compact_docx(input_path: Path, output_path: Path) -> dict[str, int]:
    with ZipFile(input_path, "r") as zf:
        entries = {name: zf.read(name) for name in zf.namelist()}

    document = parse_xml(entries[DOCUMENT_XML])
    root = document.getroot()
    body_elem = body(document)
    sect_pr = body_elem.find("w:sectPr", NS)
    stats = {
        "nonpage_breaks_removed": remove_nonpage_breaks(root),
        "paragraphs_compressed": shrink_paragraph_spacing(root),
        "images_shrunk": shrink_images(root),
        "decorative_images_removed": remove_decorative_red_images(root, entries),
        "text_colors_blackened": force_text_black(root),
        "option_paragraphs": compact_option_paragraphs(root),
        "vertical_option_groups": merge_vertical_options(body_elem),
    }
    if sect_pr is not None:
        set_section_to_two_columns(sect_pr)
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
    parser = argparse.ArgumentParser(description="Compact a reordered review DOCX.")
    parser.add_argument("input", help="Input DOCX path.")
    parser.add_argument("--output", required=True, help="Output DOCX path.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not input_path.exists():
        parser.error(f"输入文件不存在: {input_path}")
    stats = compact_docx(input_path, output_path)
    print(output_path)
    print(
        "删除非页硬换行 {nonpage_breaks_removed}, 压缩段落 {paragraphs_compressed}, "
        "缩放图片 {images_shrunk}, 装饰图删除 {decorative_images_removed}, 文字改黑 {text_colors_blackened}, 选项段落 {option_paragraphs}, "
        "竖排选项组 {vertical_option_groups}".format(**stats)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
