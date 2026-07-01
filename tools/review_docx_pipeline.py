#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unified DOCX export pipeline for review lesson files.

This script is the public entry point for common review-document exports.
It wraps the lower-level tools without changing their implementation:

- md2docx.py: Markdown -> single-column DOCX with formula/image handling
- compact_review_docx.py: DOCX -> two-column compact DOCX

Typical usage:

    python tools/review_docx_pipeline.py export outputs/g8-reviews/review-10_教师版解析.md --mode both
    python tools/review_docx_pipeline.py compact outputs/g8-reviews/review-10_教师版解析.docx
    python tools/review_docx_pipeline.py export outputs/g8-reviews/*.md --mode compact

Notes:
- Paths are resolved relative to the current working directory.
- Existing files are overwritten only when --overwrite is provided.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow this script to be executed either from the project root or directly.
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from compact_review_docx import compact_docx  # noqa: E402
from md2docx import process as md_to_single_docx  # noqa: E402


COMPACT_SUFFIX = "_分栏压缩"


def default_single_output(md_path: Path, output_dir: Path | None = None) -> Path:
    base_dir = output_dir if output_dir is not None else md_path.parent
    return base_dir / f"{md_path.stem}.docx"


def default_compact_output(docx_or_md_path: Path, output_dir: Path | None = None) -> Path:
    base_dir = output_dir if output_dir is not None else docx_or_md_path.parent
    stem = docx_or_md_path.stem
    if stem.endswith(COMPACT_SUFFIX):
        return base_dir / f"{stem}.docx"
    return base_dir / f"{stem}{COMPACT_SUFFIX}.docx"


def ensure_can_write(path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"输出文件已存在，若要覆盖请加 --overwrite：{path}")
    path.parent.mkdir(parents=True, exist_ok=True)


def export_one(
    md_path: Path,
    mode: str,
    output_dir: Path | None,
    overwrite: bool,
) -> list[Path]:
    if not md_path.exists():
        raise FileNotFoundError(f"输入 Markdown 不存在：{md_path}")
    if md_path.suffix.lower() != ".md":
        raise ValueError(f"export 只接受 .md 文件：{md_path}")

    outputs: list[Path] = []
    single_path = default_single_output(md_path, output_dir)

    if mode in {"single", "both", "compact"}:
        # compact mode still needs an intermediate single-column DOCX.
        if not single_path.exists() or overwrite or mode in {"single", "both", "compact"}:
            ensure_can_write(single_path, overwrite=overwrite or mode == "compact")
            md_to_single_docx(str(md_path), str(single_path))
        if mode in {"single", "both"}:
            outputs.append(single_path)

    if mode in {"compact", "both"}:
        compact_path = default_compact_output(md_path, output_dir)
        ensure_can_write(compact_path, overwrite=overwrite)
        stats = compact_docx(single_path, compact_path)
        print(f"已保存: {compact_path}")
        print(
            "  压缩统计: 删除非页硬换行 {nonpage_breaks_removed}, 压缩段落 {paragraphs_compressed}, "
            "缩放图片 {images_shrunk}, 竖排选项组 {vertical_option_groups}".format(**stats)
        )
        outputs.append(compact_path)

    return outputs


def compact_one(docx_path: Path, output_dir: Path | None, overwrite: bool) -> Path:
    if not docx_path.exists():
        raise FileNotFoundError(f"输入 DOCX 不存在：{docx_path}")
    if docx_path.suffix.lower() != ".docx":
        raise ValueError(f"compact 只接受 .docx 文件：{docx_path}")

    output_path = default_compact_output(docx_path, output_dir)
    ensure_can_write(output_path, overwrite=overwrite)
    stats = compact_docx(docx_path, output_path)
    print(f"已保存: {output_path}")
    print(
        "  压缩统计: 删除非页硬换行 {nonpage_breaks_removed}, 压缩段落 {paragraphs_compressed}, "
        "缩放图片 {images_shrunk}, 竖排选项组 {vertical_option_groups}".format(**stats)
    )
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Review DOCX unified export pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser(
        "export",
        help="Convert Markdown review files to DOCX.",
    )
    export_parser.add_argument("inputs", nargs="+", help="Input Markdown file(s).")
    export_parser.add_argument(
        "--mode",
        choices=["single", "compact", "both"],
        default="compact",
        help="single=单栏DOCX, compact=分栏压缩DOCX, both=两者都生成。默认 compact。",
    )
    export_parser.add_argument("--output-dir", help="Output directory. Defaults to each input file's directory.")
    export_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files.")

    compact_parser = subparsers.add_parser(
        "compact",
        help="Compact existing DOCX files into two-column layout.",
    )
    compact_parser.add_argument("inputs", nargs="+", help="Input DOCX file(s).")
    compact_parser.add_argument("--output-dir", help="Output directory. Defaults to each input file's directory.")
    compact_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else None

    try:
        if args.command == "export":
            all_outputs: list[Path] = []
            for raw in args.inputs:
                all_outputs.extend(
                    export_one(
                        Path(raw),
                        mode=args.mode,
                        output_dir=output_dir,
                        overwrite=args.overwrite,
                    )
                )
            print("\n完成输出：")
            for path in all_outputs:
                print(f"- {path}")
            return 0

        if args.command == "compact":
            outputs = [
                compact_one(Path(raw), output_dir=output_dir, overwrite=args.overwrite)
                for raw in args.inputs
            ]
            print("\n完成输出：")
            for path in outputs:
                print(f"- {path}")
            return 0
    except Exception as exc:  # noqa: BLE001 - CLI should print concise actionable error.
        parser.exit(1, f"错误: {exc}\n")

    parser.error("未知命令")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
