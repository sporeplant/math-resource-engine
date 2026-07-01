#!/usr/bin/env python3
"""
Normalize textbook lesson files to standardized YAML front matter.

For each file under textbooks/ch{num}/, write:
---
content_type: textbook_original
textbook_version: JJ2022
semester: 8A / 8B
chapter_name: ...
section_name: ...
lesson_id: ...
---

Usage:
    python tools/normalize_textbook_yaml.py [--dry-run]
"""

import re
import os
import sys
from pathlib import Path

TEXTBOOKS = Path(os.environ.get('MRE_TEXTBOOKS', 'E:\\OneDrive\\MRE_Data\\knowledge\\textbooks'))

CHAPTER_MAP = {
    '12': {'name': '分式和分式运算', 'semester': '8A'},
    '13': {'name': '全等三角形', 'semester': '8A'},
    '18': {'name': '平面直角坐标系', 'semester': '8B'},
    '19': {'name': '函数', 'semester': '8B'},
    '20': {'name': '一次函数', 'semester': '8B'},
    '21': {'name': '四边形', 'semester': '8B'},
    '22': {'name': '数据的收集与整理', 'semester': '8B'},
}

SECTION_MAP = {
    '12.1': '分式',
    '12.2': '分式的乘除',
    '12.3': '分式的加减',
    '12.4': '分式方程',
    '12.5': '分式方程的应用',
    '13.3': '全等三角形的判定',
    '18.1': '位置的确定',
    '18.2': '平面直角坐标系',
    '18.3': '图形的位里与坐标',
    '18.4': '图形的运动与坐标',
    '19.1': '常量与变量',
    '19.2': '函数',
    '19.3': '函数的表示',
    '19.4': '函数的初步应用',
    '20.1': '一次函数',
    '20.2': '一次函数的图像和性质',
    '20.3': '用待定系数法确定一次函数表达式',
    '20.4': '一次函数的应用',
    '20.5': '一次函数与二元一次方程的关系',
    '21.1': '多边形',
    '21.2': '平行四边形的性质',
    '21.3': '平行四边形的判定',
    '21.4': '三角形的中位线',
    '21.5': '矩形',
    '21.6': '菱形',
    '21.7': '正方形',
    '21.8': '梯形',
    '21.9': '四边形与特殊四边形',
    '22.1': '统计的初步认识',
    '22.2': '数据的收集',
    '22.3': '数据的整理与分析',
    '22.4': '频数分布直方图',
    '22.5': '数据变化趋势的刻画',
}

YAML_FIELDS = ['content_type', 'textbook_version', 'semester', 'chapter_name', 'section_name', 'lesson_id']

FRONT_MATTER_RE = re.compile(r'\A---\s*\n.*?\n---\s*\n?', re.DOTALL)


def yaml_scalar(value):
    v = str(value or '').strip()
    v = v.replace('\ufffd', '?')
    if not v:
        return '""'
    if re.search(r'[:#\[\]{}&,*!|>\'"%@`\n\r]', v):
        return repr(v)
    return v


def build_yaml(meta):
    lines = ['---']
    for field in YAML_FIELDS:
        lines.append(f'{field}: {yaml_scalar(meta.get(field, ""))}')
    lines.append('---')
    return '\n'.join(lines) + '\n\n'


def strip_front_matter(text):
    return FRONT_MATTER_RE.sub('', text).lstrip('\n')


def parse_filename(name):
    """Return (type, ch, sec, lesson) from filename stem."""
    stem = name.replace('.md', '')
    # textbook-ch{num}-review-{lesson}.md
    m = re.match(r'textbook-ch(\d+)-review-(\d+)', stem)
    if m:
        return ('review', m.group(1), None, m.group(2))
    # textbook-ch{num}-intro.md
    m = re.match(r'textbook-ch(\d+)-intro', stem)
    if m:
        return ('intro', m.group(1), None, None)
    # textbook-ch{num}-{activity}.md
    m = re.match(r'textbook-ch(\d+)-(.+)', stem)
    if m:
        return ('activity', m.group(1), None, m.group(2))
    # textbook-{ch}.{sec}-{lesson}.md or textbook-{ch}.{sec}.md
    m = re.match(r'textbook-(\d+)\.(\d+)(?:-(\d+))?', stem)
    if m:
        lesson = m.group(3) or '1'
        return ('lesson', m.group(1), m.group(2), lesson)
    return ('unknown', None, None, None)


def process_file(filepath, dry_run):
    name = filepath.name
    try:
        content = filepath.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    body = strip_front_matter(content)

    ftype, ch, sec, lesson = parse_filename(name)

    if ch not in CHAPTER_MAP:
        print(f'  [SKIP] unknown chapter {ch} in {name}')
        return False

    ch_info = CHAPTER_MAP[ch]
    lesson_id = ''
    section_name = ''

    if ftype == 'lesson':
        section_key = f'{ch}.{sec}'
        section_name = SECTION_MAP.get(section_key, '')
        if not section_name:
            for line in body.splitlines():
                s = line.strip().lstrip('#').strip()
                if s and not s.startswith('---'):
                    section_name = s[:30]
                    break
        lesson_id = f'{section_key}.{lesson}'
    elif ftype == 'review':
        section_name = '回顾与反思'
        lesson_id = f'ch{ch}-review-{lesson}'
    elif ftype == 'intro':
        section_name = ch_info['name']
        lesson_id = f'ch{ch}-intro'
    elif ftype == 'activity':
        section_name = lesson or '数学活动'
        # Find activity number from the filename pattern or use a generic id
        safe_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', lesson or 'activity')[:20]
        lesson_id = f'ch{ch}-activity-{safe_name}'
    else:
        print(f'  [SKIP] unrecognized filename: {name}')
        return False

    meta = {
        'content_type': 'textbook_original',
        'textbook_version': 'JJ2022',
        'semester': ch_info['semester'],
        'chapter_name': ch_info['name'],
        'section_name': section_name,
        'lesson_id': lesson_id,
    }

    new_content = build_yaml(meta) + body
    if new_content != content:
        rel = filepath.relative_to(TEXTBOOKS) if TEXTBOOKS in filepath.parents else filepath
        print(f'  [YAML] {rel}')
        if not dry_run:
            filepath.write_text(new_content, encoding='utf-8')
        return True
    return False


def main():
    dry_run = '--dry-run' in sys.argv
    if not TEXTBOOKS.is_dir():
        print(f'Error: textbooks directory not found: {TEXTBOOKS}')
        sys.exit(1)

    ch_dirs = sorted([d for d in TEXTBOOKS.iterdir() if d.is_dir() and d.name.startswith('ch')])
    total_changed = 0
    for ch_dir in ch_dirs:
        files = sorted(ch_dir.glob('textbook-*.md'))
        if not files:
            continue
        print(f'{ch_dir.name}/')
        for f in files:
            if process_file(f, dry_run):
                total_changed += 1

    print(f'\nDone. {total_changed} file(s) would change.' if dry_run else f'\nDone. {total_changed} file(s) updated.')

if __name__ == '__main__':
    main()
