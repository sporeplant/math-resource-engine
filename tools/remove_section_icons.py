"""Remove section icon images from textbook markdown files.

Finds image references immediately preceding target section headers,
removes the reference lines from the MD files, and deletes the actual image files.

Usage:
    python tools/remove_section_icons.py <target_dir> [--headers 栏目1,栏目2,...] [--dry-run] [--no-delete-images]
"""

import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_HEADERS = [
    "观察与思考",
    "做一做",
    "练习",
    "一起探究",
    "大家谈谈",
    "读一读",
    "复习题",
]

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
IMAGES_DIR = PROJECT_DIR / "knowledge" / "images"


def build_icon_pattern(headers: list[str]) -> re.Pattern:
    header_pattern = "|".join(re.escape(h) for h in headers)
    return re.compile(
        r"!\[.*?\]\("
        r"(?:https://cdn\.jsdelivr\.net/gh/sporeplant/"
        r"math-resource-engine@main/knowledge/images/"
        r"|(?:\.\./)?images/)"  # CDN URL or relative images/ path
        r"([a-f0-9]+\.jpg)\)\s*\n\s*\n## (?:" + header_pattern + r")",
        re.MULTILINE,
    )


def process_file(filepath: Path, pattern: re.Pattern, dry_run: bool) -> set[str]:
    """Remove icon refs from a file. Returns set of image filenames removed."""
    content = filepath.read_text(encoding="utf-8")
    removed_hashes = set()

    def replace_icon(match):
        image_hash = match.group(1)
        removed_hashes.add(image_hash)
        full_match = match.group(0)
        header_pos = full_match.rfind("\n## ")
        return full_match[header_pos:]  # preserve "\n## 栏目名"

    new_content = pattern.sub(replace_icon, content)

    if new_content != content:
        if not dry_run:
            filepath.write_text(new_content, encoding="utf-8")
        print(f"  {'[DRY-RUN] ' if dry_run else ''}Modified: {filepath.name}")

    return removed_hashes


def main():
    parser = argparse.ArgumentParser(
        description="Remove section icon images from textbook markdown files."
    )
    parser.add_argument(
        "target_dir",
        help="Directory containing textbook MD files",
    )
    parser.add_argument(
        "--headers",
        help="Comma-separated list of target section headers (default: all 7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, do not modify files or delete images",
    )
    parser.add_argument(
        "--no-delete-images",
        action="store_true",
        help="Only remove references from MD files, do not delete image files",
    )
    args = parser.parse_args()

    target_dir = Path(args.target_dir).resolve()
    if not target_dir.is_dir():
        print(f"Error: Directory not found: {target_dir}", file=sys.stderr)
        sys.exit(1)

    headers = (
        [h.strip() for h in args.headers.split(",")]
        if args.headers
        else DEFAULT_HEADERS
    )
    print(f"Target headers: {headers}")
    print(f"Target directory: {target_dir}")
    if args.dry_run:
        print("Mode: DRY-RUN (no changes will be made)")
    print()

    pattern = build_icon_pattern(headers)
    md_files = sorted(target_dir.glob("*.md"))

    if not md_files:
        print("No MD files found in target directory.")
        sys.exit(0)

    print(f"Processing {len(md_files)} files...\n")

    all_removed = set()
    modified_count = 0
    for md_file in md_files:
        removed = process_file(md_file, pattern, args.dry_run)
        if removed:
            modified_count += 1
            for h in removed:
                print(f"    - Icon: {h}")
        all_removed.update(removed)

    print(f"\n--- Summary ---")
    print(f"  Files modified: {modified_count}")
    print(f"  Icon references removed: {len(all_removed)}")

    if args.dry_run or args.no_delete_images:
        if all_removed:
            print(f"  Image files (would be deleted): {len(all_removed)}")
            for h in sorted(all_removed):
                img_path = IMAGES_DIR / h
                exists = "[EXISTS]" if img_path.exists() else "[NOT FOUND]"
                print(f"    {exists} {h}")
        print("  (Image deletion skipped)")
    else:
        deleted = 0
        not_found = 0
        for img_hash in sorted(all_removed):
            img_path = IMAGES_DIR / img_hash
            if img_path.exists():
                img_path.unlink()
                deleted += 1
                print(f"  Deleted image: {img_hash}")
            else:
                not_found += 1
                print(f"  Image not found: {img_hash}")
        print(f"  Images deleted: {deleted}, not found: {not_found}")

    if args.dry_run:
        print("\nDry-run complete. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
