#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create a trial DOCX with non-underlined filler spaces cleaned up."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

W_NS = NS["w"]
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
DOCUMENT_XML = "word/document.xml"


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


def has_underline(text_node: etree._Element) -> bool:
    run = text_node.getparent()
    while run is not None and run.tag != f"{{{W_NS}}}r":
        run = run.getparent()
    if run is None:
        return False
    return run.find("w:rPr/w:u", NS) is not None


def text_looks_like_answer_blank(text: str) -> bool:
    return bool(re.search(r"[＿_]{2,}|[　 ]{4,}", text))


def clean_text(text: str, keep_blank: bool) -> str:
    if keep_blank:
        return text
    text = text.replace("\u00a0", "")
    text = text.replace("\u3000", "")
    text = text.replace(" ", "")
    text = text.replace("\t", "")
    return text


def clean_document(document: etree._ElementTree) -> dict[str, int]:
    stats = {
        "text_nodes_changed": 0,
        "line_breaks_removed": 0,
        "underlined_or_blank_nodes_kept": 0,
    }
    root = document.getroot()

    for br in list(root.xpath(".//w:br[not(@w:type='page')]", namespaces=NS)):
        parent = br.getparent()
        if parent is not None:
            parent.remove(br)
            stats["line_breaks_removed"] += 1

    for text_node in root.xpath(".//w:t", namespaces=NS):
        old = text_node.text or ""
        keep_blank = has_underline(text_node) or text_looks_like_answer_blank(old)
        if keep_blank:
            stats["underlined_or_blank_nodes_kept"] += 1
            continue
        new = clean_text(old, keep_blank=False)
        if new != old:
            text_node.text = new
            stats["text_nodes_changed"] += 1
        if new.startswith(" ") or new.endswith(" "):
            text_node.set(XML_SPACE, "preserve")
        elif XML_SPACE in text_node.attrib:
            del text_node.attrib[XML_SPACE]

    for paragraph in list(root.xpath(".//w:p", namespaces=NS)):
        has_text = any((node.text or "").strip() for node in paragraph.xpath(".//w:t", namespaces=NS))
        has_drawing = bool(paragraph.xpath(".//w:drawing | .//w:pict | .//w:object", namespaces=NS))
        has_break = bool(paragraph.xpath(".//w:br", namespaces=NS))
        if not has_text and not has_drawing and not has_break:
            parent = paragraph.getparent()
            if parent is not None:
                parent.remove(paragraph)

    return stats


def clean_docx(input_path: Path, output_path: Path) -> dict[str, int]:
    with ZipFile(input_path, "r") as zf:
        entries = {name: zf.read(name) for name in zf.namelist()}

    document = parse_xml(entries[DOCUMENT_XML])
    stats = clean_document(document)
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
    parser = argparse.ArgumentParser(description="Clean non-underlined spacing in a DOCX.")
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
    stats = clean_docx(input_path, output_path)
    print(output_path)
    print(
        "修改文本节点 {text_nodes_changed}, 删除硬换行 {line_breaks_removed}, "
        "保留留空节点 {underlined_or_blank_nodes_kept}".format(**stats)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
