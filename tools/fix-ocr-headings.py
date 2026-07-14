"""
Fix MinerU OCR-corrupted section headings in textbook chapter files.

Usage:
    python tools/fix_ocr_headings.py outputs/ch01.md [--dry-run]
"""

import re
import sys
import os

# Known correct sections per chapter (from textbook TOC)
CHAPTER_SECTIONS = {
    1: ["1.1 正数和负数", "1.2 数轴", "1.3 绝对值与相反数",
        "1.4 有理数的大小", "1.5 有理数的加法", "1.6 有理数的减法",
        "1.7 有理数的加减混合运算", "1.8 有理数的乘法",
        "1.9 有理数的除法", "1.10 有理数的乘方", "1.11 有理数的混合运算"],
    2: ["2.1 从生活中认识几何图形", "2.2 线段、射线、直线",
        "2.3 线段长短的比较", "2.4 线段的和与差",
        "2.5 角和角的度量", "2.6 角大小的比较",
        "2.7 角的和与差", "2.8 平面图形的旋转"],
    3: ["3.1 用字母表示数", "3.2 代数式",
        "3.3 数量之间的关系", "3.4 代数式的值"],
    4: ["4.1 整式", "4.2 合并同类项",
        "4.3 去括号", "4.4 整式的加减"],
    5: ["5.1 等式与方程", "5.2 一元一次方程",
        "5.3 解一元一次方程", "5.4 一元一次方程的应用"],
}


def fix_chapter(content, ch_num):
    """Fix OCR-corrupted section headings for a chapter."""
    lines = content.split('\n')
    fixed_lines = []
    fixed_count = 0
    expected_sections = CHAPTER_SECTIONS.get(ch_num, [])

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith('## '):
            heading = stripped[3:].strip()
            new_heading = fix_heading(heading, ch_num, expected_sections)

            if new_heading != heading:
                line = '## ' + new_heading
                fixed_count += 1
                print(f"  Line {i+1}: '{heading}' -> '{new_heading}'")

        fixed_lines.append(line)

    # Find and insert missing section headings
    fixed_lines, inserted = insert_missing_headings(
        fixed_lines, expected_sections, ch_num
    )
    fixed_count += inserted

    return '\n'.join(fixed_lines), fixed_count


def fix_heading(heading, ch_num, expected_sections):
    """Fix a single corrupted heading."""

    # Pattern: "1.01" -> "1.1" (extra leading zero)
    m = re.match(r'^(\d+)\.0(\d+)\s+(.*)', heading)
    if m and int(m.group(2)) > 0:
        return f"{m.group(1)}.{m.group(2)} {m.group(3)}"

    # Pattern: ".1 从生活中认识几何图形" -> "2.1 ..." (missing chapter prefix)
    m = re.match(r'^\.(\d+)\s+(.*)', heading)
    if m:
        return f"{ch_num}.{m.group(1)} {m.group(2)}"

    # Pattern: "01 用字母表示数" -> "3.1 ..." (chapter prefix became zero)
    m = re.match(r'^0(\d+)\s+(.*)', heading)
    if m and 1 <= int(m.group(1)) <= 20:
        name = m.group(2)
        for s in expected_sections:
            if s.endswith(f".{m.group(1)} {name}") or f".{m.group(1)} " in s:
                return f"{ch_num}.{m.group(1)} {name}"

    # Pattern: "Lo1 整式" -> "4.1 整式" (OCR corruption)
    m = re.match(r'^[Ll][Oo0](\d+)\s+(.*)', heading)
    if m:
        return f"{ch_num}.{m.group(1)} {m.group(2)}"

    # Pattern: "9 有理数的除法" -> "1.9 ..." (bare digit = section number)
    m = re.match(r'^(\d+)\s+(.*)', heading)
    if m:
        num = int(m.group(1))
        name = m.group(2)
        if 2 <= num <= 20:
            for s in expected_sections:
                parts = s.split(' ', 1)
                if len(parts) == 2:
                    sec_num = parts[0]
                    sec_name = parts[1]
                    if sec_num.endswith(f".{num}") and name == sec_name:
                        return s

    # Pattern: "1.2数轴" -> "1.2 数轴" (missing space after number)
    m = re.match(r'^(\d+\.\d+)([^\s].*)', heading)
    if m:
        # Verify this is a section heading
        sec = m.group(1)
        rest = m.group(2)
        for s in expected_sections:
            if s.startswith(sec) and rest in s:
                return s

    return heading


def insert_missing_headings(lines, expected_sections, ch_num):
    """Find and insert completely missing section headings.

    Strategy: use content clues (like sub-headings '读一读', 回顾与反思)
    and adjacency to determine where missing headings belong.
    """
    # Build a map of seen sections
    seen = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('## '):
            heading = stripped[3:]
            m = re.match(r'^(\d+)\.(\d+)\s', heading)
            if m:
                seen[f"{m.group(1)}.{m.group(2)}"] = True

    # Content anchors for missing sections
    # Format: section -> (anchor_text_before, offset_lines)
    MISSING_ANCHORS = {
        # Chapter 1
        "1.4": ("有理数的大小", -3),   # content starts near this text
        "1.7": ("有理数的加减混合运算", -2),
        # Chapter 2
        "2.2": ("由第二种情况得到", -3),
        # Chapter 4
        "4.3": ("去括号与合并同类项是整式加减的基础", -2),
        "4.4": ("某旅行社一旅游项目的收费标准为", -1),
    }

    inserted = 0

    for sec_key, (anchor_text, offset) in MISSING_ANCHORS.items():
        # Parse section
        m = re.match(r'^(\d+)\.(\d+)', sec_key)
        if not m:
            continue
        ch = int(m.group(1))
        if ch != ch_num:
            continue
        if sec_key in seen:
            continue

        # Find the full section name
        section_full = None
        for s in CHAPTER_SECTIONS.get(ch_num, []):
            if s.startswith(sec_key):
                section_full = s
                break
        if not section_full:
            continue

        # Find anchor position
        anchor_pos = None
        for i, line in enumerate(lines):
            if anchor_text in line:
                anchor_pos = i
                break

        if anchor_pos is None:
            continue

        insert_pos = anchor_pos + offset
        if insert_pos < 0:
            insert_pos = 0

        # Find a good insertion point (at a paragraph boundary before content)
        # Walk backwards to find blank line or previous section end
        while insert_pos > 0:
            if lines[insert_pos].strip() == '':
                break
            insert_pos -= 1

        new_heading = f"## {section_full}"
        lines.insert(insert_pos, new_heading)
        lines.insert(insert_pos, "")  # blank line before
        inserted += 1
        seen[sec_key] = True
        print(f"    Inserted '## {section_full}' before '{anchor_text}'")

    # For sections we couldn't find an anchor for
    for s in expected_sections:
        m = re.match(r'^(\d+)\.(\d+)\s', s)
        if m and m.group(0).strip() not in seen:
            print(f"    WARNING: Could not locate missing section: {s}")

    return lines, inserted


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/fix_ocr_headings.py <chapter_file> [--dry-run]")
        sys.exit(1)

    filepath = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    basename = os.path.basename(filepath)
    m = re.match(r'ch0?(\d+)', basename)
    if not m:
        print(f"Error: Cannot detect chapter number from filename: {basename}")
        sys.exit(1)

    ch_num = int(m.group(1))

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Fixing {basename} (Chapter {ch_num})...")
    fixed_content, count = fix_chapter(content, ch_num)

    if count == 0:
        print("  No fixes needed.")
        return

    print(f"  Total fixes: {count}")

    if dry_run:
        print("  (--dry-run: no changes written)")
        return

    # Backup original
    backup = filepath + '.bak'
    os.rename(filepath, backup)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"  Written: {filepath}")
    print(f"  Backup:  {backup}")


if __name__ == '__main__':
    main()
