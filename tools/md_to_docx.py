#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Legacy Markdown-to-DOCX converter.

Deprecated: prefer `tools/review_docx_pipeline.py` for review exports.
This file is kept only for backward compatibility with older commands.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}
W_NS = NS["w"]
REL_NS = NS["rel"]
CT_NS = NS["ct"]
R_NS = NS["r"]

DOCUMENT_XML = "word/document.xml"
DOCUMENT_RELS = "word/_rels/document.xml.rels"
CONTENT_TYPES = "[Content_Types].xml"
STYLES_XML = "word/styles.xml"
SETTINGS_XML = "word/settings.xml"

# ---------- XML builders ----------

def _elem(tag: str, parent: etree._Element | None = None, **attrs) -> etree._Element:
    """Create a WordprocessingML element."""
    el = etree.Element(f"{{{W_NS}}}{tag}")
    for k, v in attrs.items():
        el.set(f"{{{W_NS}}}{k}", v)
    if parent is not None:
        parent.append(el)
    return el


XML_SPACE = "http://www.w3.org/XML/1998/namespace"


def _run(parent: etree._Element, text: str = "", bold: bool = False) -> etree._Element:
    r = _elem("r", parent)
    if bold:
        rpr = _elem("rPr", r)
        _elem("b", rpr)
    t = etree.SubElement(r, f"{{{W_NS}}}t")
    t.set(f"{{{XML_SPACE}}}space", "preserve")
    t.text = text
    return r


def _para(parent: etree._Element, texts: list[tuple[str, bool]], alignment: str = "left") -> etree._Element:
    """Add a paragraph with mixed bold/normal runs."""
    p = _elem("p", parent)
    ppr = _elem("pPr", p)
    if alignment != "left":
        jc = _elem("jc", ppr, val=alignment)
    spacing = _elem("spacing", ppr, before="0", after="40", line="240", lineRule="auto")
    for text, bold in texts:
        _run(p, text, bold=bold)
    return p


def _heading_para(parent: etree._Element, text: str, level: int = 1) -> etree._Element:
    p = _elem("p", parent)
    ppr = _elem("pPr", p)
    pstyle = _elem("pStyle", ppr, val=f"Heading{level}")
    _run(p, text, bold=True)
    return p


# ---------- skeleton DOCX ----------

SKELETON_FILES: dict[str, bytes] = {}

def _build_skeleton() -> None:
    """Build a minimal DOCX skeleton in memory."""
    if SKELETON_FILES:
        return

    # [Content_Types].xml
    ct_root = etree.Element(f"{{{CT_NS}}}Types")
    for ext, ctype in [
        ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
        ("xml", "application/xml"),
    ]:
        etree.SubElement(ct_root, f"{{{CT_NS}}}Default", Extension=ext, ContentType=ctype)
    etree.SubElement(ct_root, f"{{{CT_NS}}}Override",
                     PartName="/word/document.xml",
                     ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml")
    SKELETON_FILES[CONTENT_TYPES] = etree.tostring(ct_root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # _rels/.rels
    rels_root = etree.Element(f"{{{REL_NS}}}Relationships")
    for rid, rtype, target in [
        ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument", "word/document.xml"),
    ]:
        etree.SubElement(rels_root, f"{{{REL_NS}}}Relationship", Id=rid, Type=rtype, Target=target)
    SKELETON_FILES["_rels/.rels"] = etree.tostring(rels_root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # word/_rels/document.xml.rels
    doc_rels = etree.Element(f"{{{REL_NS}}}Relationships")
    SKELETON_FILES[DOCUMENT_RELS] = etree.tostring(doc_rels, xml_declaration=True, encoding="UTF-8", standalone=True)

    # word/styles.xml (minimal)
    styles_root = etree.Element(f"{{{W_NS}}}styles")
    doc_defaults = etree.SubElement(styles_root, f"{{{W_NS}}}docDefaults")
    rpr_default = etree.SubElement(doc_defaults, f"{{{W_NS}}}rPrDefault")
    rpr = etree.SubElement(rpr_default, f"{{{W_NS}}}rPr")
    etree.SubElement(rpr, f"{{{W_NS}}}sz", **{f"{{{W_NS}}}val": "21"})  # 10.5pt
    etree.SubElement(rpr, f"{{{W_NS}}}rFonts", **{f"{{{W_NS}}}eastAsia": "宋体"})
    ppr_default = etree.SubElement(doc_defaults, f"{{{W_NS}}}pPrDefault")
    ppr = etree.SubElement(ppr_default, f"{{{W_NS}}}pPr")
    etree.SubElement(ppr, f"{{{W_NS}}}spacing", **{f"{{{W_NS}}}line": "240", f"{{{W_NS}}}lineRule": "auto"})
    SKELETON_FILES[STYLES_XML] = etree.tostring(styles_root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # word/settings.xml
    settings_root = etree.Element(f"{{{W_NS}}}settings")
    SKELETON_FILES[SETTINGS_XML] = etree.tostring(settings_root, xml_declaration=True, encoding="UTF-8", standalone=True)


# ---------- conversion ----------

def parse_frontmatter(text: str) -> tuple[str, str]:
    """Strip YAML frontmatter, return (frontmatter_raw, body)."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[:end + 3], text[end + 3:]
    return "", text


def convert_md_to_docx(md_path: str, docx_path: str) -> str:
    _build_skeleton()

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    _, body = parse_frontmatter(content)

    # Build document XML
    document = etree.Element(f"{{{W_NS}}}document")
    body_elem = _elem("body", document)

    # Page setup
    sect_pr = _elem("sectPr", body_elem)
    _elem("pgMar", sect_pr, top="1440", bottom="1440", left="1440", right="1440", header="720", footer="720", gutter="0")
    _elem("cols", sect_pr, num="1", space="360")

    blocks = re.split(r"\n---\n", body.strip())

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Title
        if block.startswith("# "):
            _heading_para(body_elem, block[2:].strip(), level=1)
            continue

        # Process each line
        for line in block.split("\n"):
            line = line.strip()
            if not line:
                continue

            texts: list[tuple[str, bool]] = []
            parts = re.split(r"(\*\*.*?\*\*)", line)
            for seg in parts:
                if seg.startswith("**") and seg.endswith("**"):
                    texts.append((seg[2:-2], True))
                elif seg:
                    texts.append((seg, False))
            if texts:
                _para(body_elem, texts)

    entries = dict(SKELETON_FILES)
    entries[DOCUMENT_XML] = etree.tostring(document, xml_declaration=True, encoding="UTF-8", standalone=True)

    docx_path = Path(docx_path)
    docx_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = Path(tmp.name)
    try:
        with ZipFile(tmp_path, "w", ZIP_DEFLATED) as zf:
            for name, data in entries.items():
                zf.writestr(name, data)
        shutil.move(str(tmp_path), docx_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    print(docx_path)
    return str(docx_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert reference-answer Markdown to DOCX.")
    parser.add_argument("input", help="Input Markdown path.")
    parser.add_argument("--output", required=True, help="Output DOCX path.")
    return parser


def main() -> int:
    print(
        "警告: tools/md_to_docx.py 是旧版简化转换器；新任务请使用 "
        "tools/review_docx_pipeline.py。",
        file=sys.stderr,
    )
    parser = build_parser()
    args = parser.parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not input_path.exists():
        parser.error(f"输入文件不存在: {input_path}")
    convert_md_to_docx(str(input_path), str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
