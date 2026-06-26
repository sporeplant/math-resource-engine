#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Merge review-lesson DOCX files while preserving Word inline objects.

This tool intentionally works at the DOCX package level instead of converting
through Markdown. It copies body XML blocks and remaps relationship ids for
images, OLE objects, and other inline resources referenced by the appended
document.
"""

from __future__ import annotations

import argparse
import copy
import posixpath
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


NS = {
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

REL_NS = NS["rel"]
W_NS = NS["w"]
R_NS = NS["r"]

DOCUMENT_XML = "word/document.xml"
DOCUMENT_RELS = "word/_rels/document.xml.rels"
CONTENT_TYPES = "[Content_Types].xml"


CONTENT_TYPE_BY_EXT = {
    "bin": "application/vnd.openxmlformats-officedocument.oleObject",
    "bmp": "image/bmp",
    "emf": "image/x-emf",
    "gif": "image/gif",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "wmf": "image/x-wmf",
}


@dataclass
class SourcePackage:
    path: Path
    entries: dict[str, bytes]
    document: etree._ElementTree
    document_rels: etree._ElementTree


def parse_xml(data: bytes) -> etree._ElementTree:
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    return etree.ElementTree(etree.fromstring(data, parser=parser))


def load_package(path: Path) -> SourcePackage:
    with ZipFile(path, "r") as zf:
        entries = {name: zf.read(name) for name in zf.namelist()}
    return SourcePackage(
        path=path,
        entries=entries,
        document=parse_xml(entries[DOCUMENT_XML]),
        document_rels=parse_xml(entries[DOCUMENT_RELS]),
    )


def xml_bytes(tree: etree._ElementTree) -> bytes:
    return etree.tostring(
        tree,
        xml_declaration=True,
        encoding="UTF-8",
        standalone=True,
    )


def rel_id_number(rel_id: str) -> int:
    match = re.fullmatch(r"rId(\d+)", rel_id)
    return int(match.group(1)) if match else 0


def next_rel_id(rels_root: etree._Element) -> str:
    used = {
        rel_id_number(rel.get("Id", ""))
        for rel in rels_root.findall("rel:Relationship", NS)
    }
    candidate = max(used or {0}) + 1
    while candidate in used:
        candidate += 1
    return f"rId{candidate}"


def relationship_map(rels_root: etree._Element) -> dict[str, etree._Element]:
    return {
        rel.get("Id"): rel
        for rel in rels_root.findall("rel:Relationship", NS)
        if rel.get("Id")
    }


def body_children(document: etree._ElementTree) -> list[etree._Element]:
    body = document.getroot().find("w:body", NS)
    if body is None:
        return []
    return list(body)


def body_without_section(document: etree._ElementTree) -> list[etree._Element]:
    children = body_children(document)
    return [child for child in children if child.tag != f"{{{W_NS}}}sectPr"]


def collect_relationship_ids(elements: list[etree._Element]) -> set[str]:
    ids: set[str] = set()
    for element in elements:
        for node in element.iter():
            for attr_name, value in node.attrib.items():
                if not value:
                    continue
                qname = etree.QName(attr_name)
                if qname.namespace == R_NS and qname.localname in {"id", "embed", "link"}:
                    ids.add(value)
    return ids


def rewrite_relationship_ids(elements: list[etree._Element], id_map: dict[str, str]) -> None:
    for element in elements:
        for node in element.iter():
            for attr_name, value in list(node.attrib.items()):
                if value in id_map:
                    node.set(attr_name, id_map[value])


def normalize_part_path(base_part: str, target: str) -> str:
    base_dir = posixpath.dirname(base_part)
    return posixpath.normpath(posixpath.join(base_dir, target))


def target_from_document_part(part_path: str) -> str:
    return posixpath.relpath(part_path, posixpath.dirname(DOCUMENT_XML))


def unique_part_name(entries: dict[str, bytes], preferred: str) -> str:
    if preferred not in entries:
        return preferred
    folder = posixpath.dirname(preferred)
    stem = posixpath.splitext(posixpath.basename(preferred))[0]
    ext = posixpath.splitext(preferred)[1]
    index = 1
    while True:
        candidate = posixpath.join(folder, f"{stem}_merged{index}{ext}")
        if candidate not in entries:
            return candidate
        index += 1


def ensure_content_type(content_types: etree._ElementTree, part_name: str) -> None:
    ext = posixpath.splitext(part_name)[1].lstrip(".").lower()
    if not ext:
        return
    root = content_types.getroot()
    existing = {
        default.get("Extension", "").lower()
        for default in root.findall("ct:Default", NS)
    }
    if ext in existing:
        return
    content_type = CONTENT_TYPE_BY_EXT.get(ext)
    if not content_type:
        return
    default = etree.Element(f"{{{NS['ct']}}}Default")
    default.set("Extension", ext)
    default.set("ContentType", content_type)
    root.insert(0, default)


def add_page_break(body: etree._Element) -> None:
    paragraph = etree.Element(f"{{{W_NS}}}p")
    run = etree.SubElement(paragraph, f"{{{W_NS}}}r")
    br = etree.SubElement(run, f"{{{W_NS}}}br")
    br.set(f"{{{W_NS}}}type", "page")
    body.append(paragraph)


def append_comparison_note(body: etree._Element, stats: list[dict[str, object]]) -> None:
    def add_para(text: str, style: str | None = None) -> None:
        p = etree.Element(f"{{{W_NS}}}p")
        if style:
            p_pr = etree.SubElement(p, f"{{{W_NS}}}pPr")
            p_style = etree.SubElement(p_pr, f"{{{W_NS}}}pStyle")
            p_style.set(f"{{{W_NS}}}val", style)
        r = etree.SubElement(p, f"{{{W_NS}}}r")
        t = etree.SubElement(r, f"{{{W_NS}}}t")
        t.text = text
        body.append(p)

    add_page_break(body)
    add_para("原始数量与选用数量对比", "Heading2")
    add_para("来源 | 知识点 | 即学即练 | 题型典例 | 题型变式 | 备注")
    for item in stats:
        add_para(
            f"{item['name']} | {item['knowledge']} | {item['instant']} | "
            f"{item['examples']} | {item['variants']} | 保留原 Word 块并合并"
        )


def text_from_paragraph_xml(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS)).strip()


def collect_stats(package: SourcePackage) -> dict[str, object]:
    texts = [text_from_paragraph_xml(p) for p in package.document.xpath("//w:p", namespaces=NS)]
    joined = "\n".join(texts)
    return {
        "name": package.path.stem.split("（", 1)[0],
        "knowledge": len(re.findall(r"知识点\d+", joined)),
        "instant": len(re.findall(r"【即学即练", joined)),
        "examples": len(re.findall(r"【典例", joined)),
        "variants": len(re.findall(r"【变式", joined)),
    }


def merge_docx(inputs: list[Path], output: Path, add_note: bool = True) -> dict[str, object]:
    if len(inputs) < 2:
        raise ValueError("至少需要两个 DOCX 文件")
    packages = [load_package(path) for path in inputs]
    base = packages[0]

    entries = dict(base.entries)
    document = parse_xml(entries[DOCUMENT_XML])
    document_rels = parse_xml(entries[DOCUMENT_RELS])
    content_types = parse_xml(entries[CONTENT_TYPES])

    body = document.getroot().find("w:body", NS)
    if body is None:
        raise RuntimeError("基础文档缺少 word/document.xml 的 body")
    sect_pr = body.find("w:sectPr", NS)
    if sect_pr is not None:
        body.remove(sect_pr)

    rels_root = document_rels.getroot()

    for package in packages[1:]:
        source_rels = relationship_map(package.document_rels.getroot())
        source_elements = [copy.deepcopy(element) for element in body_without_section(package.document)]
        used_ids = collect_relationship_ids(source_elements)
        id_map: dict[str, str] = {}

        for old_id in sorted(used_ids, key=rel_id_number):
            source_rel = source_rels.get(old_id)
            if source_rel is None:
                continue
            new_id = next_rel_id(rels_root)
            id_map[old_id] = new_id

            target = source_rel.get("Target", "")
            target_mode = source_rel.get("TargetMode")
            new_target = target

            if target and target_mode != "External":
                source_part = normalize_part_path(DOCUMENT_XML, target)
                if source_part in package.entries:
                    preferred_part = source_part
                    if preferred_part in entries and entries[preferred_part] != package.entries[source_part]:
                        preferred_part = unique_part_name(entries, preferred_part)
                    entries[preferred_part] = package.entries[source_part]
                    ensure_content_type(content_types, preferred_part)
                    new_target = target_from_document_part(preferred_part)

            new_rel = etree.Element(f"{{{REL_NS}}}Relationship")
            new_rel.set("Id", new_id)
            new_rel.set("Type", source_rel.get("Type", ""))
            new_rel.set("Target", new_target)
            if target_mode:
                new_rel.set("TargetMode", target_mode)
            rels_root.append(new_rel)

        rewrite_relationship_ids(source_elements, id_map)
        add_page_break(body)
        for element in source_elements:
            body.append(element)

    if add_note:
        append_comparison_note(body, [collect_stats(package) for package in packages])

    if sect_pr is not None:
        body.append(sect_pr)

    entries[DOCUMENT_XML] = xml_bytes(document)
    entries[DOCUMENT_RELS] = xml_bytes(document_rels)
    entries[CONTENT_TYPES] = xml_bytes(content_types)

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = Path(tmp.name)
    try:
        with ZipFile(tmp_path, "w", ZIP_DEFLATED) as zf:
            for name, data in entries.items():
                zf.writestr(name, data)
        shutil.move(str(tmp_path), output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return {
        "output": str(output),
        "stats": [collect_stats(package) for package in packages],
        "source_count": len(inputs),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge review lesson DOCX files.")
    parser.add_argument("--output", required=True, help="Output DOCX path.")
    parser.add_argument(
        "--no-note",
        action="store_true",
        help="Do not append the source-count comparison note.",
    )
    parser.add_argument("inputs", nargs="+", help="Input DOCX files in merge order.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    input_paths = [Path(item).expanduser().resolve() for item in args.inputs]
    output = Path(args.output).expanduser().resolve()

    missing = [str(path) for path in input_paths if not path.exists()]
    if missing:
        parser.error("输入文件不存在: " + "; ".join(missing))

    result = merge_docx(input_paths, output, add_note=not args.no_note)
    print(result["output"])
    for item in result["stats"]:
        print(
            f"{item['name']}: 知识点 {item['knowledge']}, 即学即练 {item['instant']}, "
            f"典例 {item['examples']}, 变式 {item['variants']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
