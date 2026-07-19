#!/usr/bin/env python3
"""md2htmlyishu HTML 硬约束验证器。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List


QUESTION_PATTERN = re.compile(r'^\(?\d+[)）.、]\s*')
IMAGE_PATTERN = re.compile(r'!\[[^\]]*\]\([^)]+\)')
MATH_PATTERN = re.compile(r'\$\$.*?\$\$|\$[^$\n]*?\$', re.S)


def split_pages(text: str) -> List[str]:
    return [page.strip() for page in re.split(r'\n---\s*\n', text) if page.strip()]


def has_multiple_questions(page: str, page_index: int, page_count: int) -> bool:
    """仅把非末两页、含数学表达式的编号行视为应横排的独立小题。"""
    if page_index > page_count - 2:
        return False
    questions = [
        line.strip() for line in page.splitlines()
        if QUESTION_PATTERN.match(line.strip())
        and ('$' in line or re.search(r'[=+\-×÷·]', line))
    ]
    return len(questions) > 1


def has_multiple_images(page: str) -> bool:
    return len(IMAGE_PATTERN.findall(page)) > 1


def has_multiple_solution_blocks(page: str) -> bool:
    """判断页面是否含两个及以上带加粗题目标题的完整解答块。"""
    headings = re.findall(
        r'^\*\*(?:[（(]\d+[）)]\*\*\s*\$|.*小题.*\*\*$|第.*题.*[（(]\d+[）)].*\*\*$)',
        page,
        re.M,
    )
    return len(headings) > 1


def validate(md_path: Path, html_path: Path) -> List[str]:
    errors: List[str] = []
    md_text = md_path.read_text(encoding='utf-8')
    html_text = html_path.read_text(encoding='utf-8')

    # 公式硬约束：仅检查课件内容，排除 CSS/JavaScript 内的 $ 与模板字符串。
    content_html = re.sub(r'<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>', '', html_text, flags=re.I)
    if content_html.count('$') % 2:
        errors.append('存在未配对的 LaTeX $ 定界符。')
    for formula in MATH_PATTERN.findall(content_html):
        if re.search(r'<[^>]+>', formula):
            errors.append(f'LaTeX 数学区间内含 HTML 标签：{formula[:80]}')

    # 模板硬约束：多题、多图和解答块容器必须默认横向 flex 布局。
    for selector, wrap_required in (('.question-row', True), ('.img-row', True), ('.solution-row', False)):
        css_match = re.search(re.escape(selector) + r'\s*\{([^}]*)\}', html_text, re.S)
        css = css_match.group(1) if css_match else ''
        if not css_match or 'display: flex' not in css:
            errors.append(f'{selector} 未配置 display:flex。')
        elif wrap_required and 'flex-wrap: wrap' not in css:
            errors.append(f'{selector} 未配置 flex-wrap:wrap。')
        elif selector == '.solution-row' and 'flex-wrap: nowrap' not in css:
            errors.append('.solution-row 未配置默认横向的 flex-wrap:nowrap。')

    if 'function paginateOverflowingSolutions()' not in html_text:
        errors.append('缺少完整解答溢出分页函数 paginateOverflowingSolutions。')
    if "slide.remove();" not in html_text or "solution-continuation" not in html_text:
        errors.append('完整解答溢出时未配置分页替代逻辑。')
    if 'solution-stack' in html_text:
        errors.append('检测到 solution-stack 纵向回退代码；完整解答溢出必须分页。')

    # 源 MD 的每个含多题/多图页面，必须对应输出 HTML 中的横向容器。
    # 使用每页稳定的 id="sN" 起点切分，避免页面内部嵌套 div 干扰。
    slide_starts = list(re.finditer(r'<div class="[^\"]*\bslide\b[^\"]*"\s+id="s\d+">', html_text))
    html_slides = []
    for index, start in enumerate(slide_starts):
        end = slide_starts[index + 1].start() if index + 1 < len(slide_starts) else len(html_text)
        html_slides.append(html_text[start.end():end])
    source_pages = split_pages(md_text)
    if len(html_slides) != len(source_pages):
        errors.append(f'页面数不一致：MD {len(source_pages)} 页，HTML {len(html_slides)} 页。')
        return errors

    for index, (page, slide) in enumerate(zip(source_pages, html_slides), start=1):
        if has_multiple_questions(page, index, len(source_pages)) and 'class="question-row"' not in slide:
            errors.append(f'第 {index} 页含多个独立编号小题，但未生成 question-row。')
        if has_multiple_images(page) and 'class="img-row"' not in slide:
            errors.append(f'第 {index} 页含多张图片，但未生成 img-row。')
        if has_multiple_solution_blocks(page) and 'class="solution-row"' not in slide:
            errors.append(f'第 {index} 页含多个完整解答块，但未生成 solution-row。')

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='验证 md2htmlyishu HTML 硬约束')
    parser.add_argument('markdown', type=Path)
    parser.add_argument('html', type=Path)
    args = parser.parse_args()

    errors = validate(args.markdown, args.html)
    if errors:
        print('验证失败：')
        for error in errors:
            print(f'- {error}')
        return 1
    print('验证通过：公式、多题横排、多图横排硬约束均满足。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
