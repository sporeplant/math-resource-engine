#!/usr/bin/env python3
"""
md2htmlyishu — 将课件 Markdown 转换为一数风格 HTML（1920×1080）

用法：
  python tools/md2htmlyishu.py <input.md>

输出：与输入文件同目录，同名但扩展名为 .html

设计原则：
  - 最大限度覆盖 skills/md2htmlyishu/SKILL.md 的所有规范
  - 自动识别页面类型并应用对应布局
  - 自动添加荧光笔标记、红笔结论、蓝笔思路（关键词从 YAML 配置加载）
  - 零装饰，纯手写板书感

配置加载优先级：
  1. MD 同目录的 {文件名}.yaml
  2. skills/md2htmlyishu/configs/ 下按章节匹配
  3. skills/md2htmlyishu/configs/default.yaml
"""

import sys
import os
import re
import random
import pathlib
from typing import List, Tuple, Optional, Dict, Any

import yaml


TEMPLATE_PATH = pathlib.Path(__file__).resolve().parent.parent / 'skills' / 'md2htmlyishu' / 'template.html'
CONFIGS_DIR = pathlib.Path(__file__).resolve().parent.parent / 'skills' / 'md2htmlyishu' / 'configs'

# === 与 SKILL.md §2.2 保持一致 ===
STYLE_CONFIG = {
    'bg': '#FDF6E3',
    'ink': '#1a1a2e',
    'red': '#C62828',
    'blue': '#1565C0',
    'yellow': '#FFEB3B',
    'title_font_size': '64px',
    'body_font_size': '40px',
    'formula_font_size': '44px',
    'table_font_size': '36px',
}

PAGE_WIDTH = 1920
PAGE_HEIGHT = 1080

QUESTION_PATTERN = re.compile(r'^\(?\d+[)）.、]\s*')


# 全局配置变量（由 load_config 填充）
_config: Dict[str, Any] = {}

# 输出目录（用于计算相对路径）
_output_dir: str = '.'


def load_config(md_path: str) -> Dict[str, Any]:
    """
    加载课程配置，按优先级：
    1. MD 同目录的 {文件名}.yaml
    2. configs/ 目录下按章节匹配
    3. configs/default.yaml
    """
    global _config
    md_path = pathlib.Path(md_path)

    # 1. 优先查找 MD 同目录的同名 YAML
    local_config = md_path.with_suffix('.yaml')
    if local_config.exists():
        print(f"加载本地配置: {local_config}")
        _config = yaml.safe_load(local_config.read_text(encoding='utf-8'))
        return _config

    # 2. 从 MD 内容提取章节信息，匹配 configs/ 目录
    md_text = md_path.read_text(encoding='utf-8')
    chapter_match = re.search(r'第([\d.]+)[章节讲]', md_text)
    if chapter_match:
        chapter_num = chapter_match.group(1)
        # 尝试逐级精确匹配：先精确（12.2.1），再次精确（12.2），最后章级（12）
        parts = chapter_num.split('.')
        for i in range(len(parts), 0, -1):
            prefix = '.'.join(parts[:i])
            for config_file in sorted(CONFIGS_DIR.glob(f'ch{prefix}-*.yaml')):
                print(f"加载章节配置: {config_file}")
                _config = yaml.safe_load(config_file.read_text(encoding='utf-8'))
                return _config

    # 3. fallback 到默认配置
    default_config = CONFIGS_DIR / 'default.yaml'
    if default_config.exists():
        print(f"加载默认配置: {default_config}")
        _config = yaml.safe_load(default_config.read_text(encoding='utf-8'))
    else:
        print("警告：未找到任何配置文件，使用空配置")
        _config = {}

    return _config


def get_page_phrases(title: str, field: str) -> List[str]:
    """获取全课及当前页面适用的精确标注短语。"""
    phrases = list(_config.get(field, []))
    for rule in _config.get('page_highlights', []):
        if rule.get('title_contains', '') in title:
            phrases.extend(rule.get(field, []))
    return sorted(set(phrase for phrase in phrases if phrase), key=len, reverse=True)


def get_red_conclusion_keywords() -> List[str]:
    """获取红笔结论关键词列表"""
    return _config.get('red_conclusion_keywords', [])


def get_red_conclusion_patterns() -> List[str]:
    """获取红笔结论正则列表"""
    return _config.get('red_conclusion_patterns', [])


def get_blue_hint_keywords() -> List[str]:
    """获取蓝笔思路关键词列表"""
    return _config.get('blue_hint_keywords', [])


def get_blue_hint_patterns() -> List[str]:
    """获取蓝笔思路正则列表"""
    return _config.get('blue_hint_patterns', [])


def load_template() -> str:
    """加载 template.html"""
    if TEMPLATE_PATH.exists():
        return TEMPLATE_PATH.read_text(encoding='utf-8')
    raise FileNotFoundError(f"模板文件未找到: {TEMPLATE_PATH}")


def split_pages(md_text: str) -> List[str]:
    """按 --- 分割为页面（SKILL.md §3.1）"""
    raw_pages = re.split(r'\n---\s*\n', md_text)
    return [p.strip() for p in raw_pages if p.strip()]


def parse_title(page_text: str) -> str:
    """提取页面标题行（第一个 ### 行）"""
    for line in page_text.split('\n'):
        line = line.strip()
        if line.startswith('### '):
            return line[4:].strip()
    return ''


def detect_page_type(page_text: str, title: str) -> str:
    """
    判断页面类型，用于应用不同布局策略
    返回: cover, objective, knowledge, example, practice, answer, homework, summary, normal
    """
    t = title.lower()
    text = page_text.lower()

    if '统计调查' in t and '直方图' in t and '复习' in text:
        return 'cover'
    if '复习目标' in t or '本课目标' in t or '学习目标' in t:
        return 'objective'
    if '知识点' in t and ('vs' in t or '对比' in text or '全面调查' in text):
        return 'knowledge_compare'
    if '知识点' in t:
        return 'knowledge'
    if '例题' in t and '精讲' in t:
        return 'example_detail'
    if '例题' in t or ('第' in t and '题' in t and '练习' not in t):
        return 'example'
    if '当堂练习' in t and '参考答案' not in t:
        return 'practice_intro'
    if '参考答案' in t:
        return 'answer'
    if '课后作业' in t or ('作业' in t and '必做' in text):
        return 'homework'
    if '课堂小结' in t and '参考答案' not in t:
        return 'summary'
    if '课堂小结' in t and '参考答案' in t:
        return 'summary_answer'
    if '练习' in t or '检测' in t:
        return 'practice'
    return 'normal'


def strip_markdown(text: str) -> str:
    """移除用于精确匹配的 Markdown 强调标记。"""
    return re.sub(r'\*\*(.+?)\*\*', r'\1', text).strip()


def normalize_match_text(text: str) -> str:
    """规范化 Markdown 和空白，供配置短语精确匹配。"""
    return re.sub(r'\s+', '', strip_markdown(text))


def is_red_conclusion(text: str, phrases: List[str]) -> bool:
    """判断文本是否为法则、定义或策略归纳的红笔结论。"""
    text_clean = normalize_match_text(text)
    if text_clean in {normalize_match_text(phrase) for phrase in phrases}:
        return True
    for pattern in get_red_conclusion_patterns():
        if re.search(pattern, text_clean):
            return True
    return False


def is_blue_hint(text: str) -> bool:
    """判断文本是否是蓝笔思路（更精准匹配）"""
    # 先检查正则
    for pattern in get_blue_hint_patterns():
        if re.search(pattern, text):
            return True
    # 再检查关键词
    text_clean = text.strip()
    for kw in get_blue_hint_keywords():
        if kw in text_clean:
            return True
    return False


def process_inline(text: str, highlight_phrases: List[str]) -> str:
    """处理行内标记，且绝不向 LaTeX 数学区间内插入 HTML。"""
    # 保留 $...$ / $$...$$ 完整数学区间，只处理其外部的普通文本。
    segments = re.split(r'(\$\$.*?\$\$|\$[^$\n]*?\$)', text)
    for i in range(0, len(segments), 2):
        segment = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', segments[i])
        for phrase in highlight_phrases:
            pattern = f'(?<!<span class="hl">){re.escape(phrase)}(?!</span>)'
            segment = re.sub(pattern, f'<span class="hl">{phrase}</span>', segment)
        segments[i] = segment
    return ''.join(segments)


def is_formula_line(text: str) -> bool:
    """判断一行是否只包含单个 LaTeX 数学区间。"""
    stripped = text.strip()
    return bool(
        re.fullmatch(r'\$[^$\n]+\$', stripped)
        or re.fullmatch(r'\$\$[^\n]+\$\$', stripped)
    )


def render_body_paragraph(text: str, highlight_phrases: List[str]) -> str:
    """渲染正文；独立公式步骤使用专用间距类。"""
    class_name = 'body-text hw formula-line' if is_formula_line(text) else 'body-text hw'
    return f'<p class="{class_name}">{process_inline(text, highlight_phrases)}</p>'


def extract_table(
    lines: List[str],
    start_idx: int,
    highlight_phrases: List[str],
    red_conclusion_phrases: List[str],
) -> Tuple[str, int]:
    """
    提取表格并转为 HTML
    返回: (html, next_idx)
    """
    table_lines = []
    i = start_idx
    while i < len(lines) and '|' in lines[i]:
        table_lines.append(lines[i])
        i += 1

    html = '<table class="sketch-table">\n'
    for j, line in enumerate(table_lines):
        line = line.strip()
        if not line or not line.startswith('|'):
            continue
        # 跳过分隔行
        if re.match(r'^\|[\s\-:]+\|', line):
            continue
        raw_cells = [c.strip() for c in line.split('|')[1:-1]]
        cells = [process_inline(cell, highlight_phrases) for cell in raw_cells]
        cells = [
            f'<span class="hw-red">{cell}</span>'
            if normalize_match_text(raw_cell) in {
                normalize_match_text(phrase) for phrase in red_conclusion_phrases
            } else cell
            for raw_cell, cell in zip(raw_cells, cells)
        ]
        tag = 'th' if j == 0 else 'td'
        html += '  <tr>\n'
        for cell in cells:
            html += f'    <{tag}>{cell}</{tag}>\n'
        html += '  </tr>\n'
    html += '</table>'
    return html, i


def convert_image(src: str, alt: str = '') -> str:
    """转换图片路径为 CDN URL（SKILL.md §3.3）"""
    if src.startswith('http'):
        return f'<img src="{src}" alt="{alt}" />'
    filename = os.path.basename(src)
    cdn_src = f"https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/{filename}"
    return f'<img src="{cdn_src}" alt="{alt}" />'


def is_question_line(text: str, page_idx: int, total_pages: int) -> bool:
    """判断是否为应横排的独立数学小题，末两页作业清单除外。"""
    if page_idx >= total_pages - 2:
        return False
    return bool(QUESTION_PATTERN.match(text)) and (
        '$' in text or bool(re.search(r'[=+\-×÷·]', text))
    )


def render_question_row(question_lines: List[str], highlight_phrases: List[str]) -> str:
    """将同级独立编号小题渲染为默认横排的容器。"""
    items = ''.join(
        f'<div class="question-item"><p class="body-text hw">'
        f'{process_inline(question, highlight_phrases)}</p></div>'
        for question in question_lines
    )
    return f'<div class="question-row">{items}</div>'


def is_solution_heading(text: str) -> bool:
    """判断一行是否为完整解答块的题目标题。"""
    plain = strip_markdown(text)
    return bool(
        re.match(r'^\*\*[（(]\d+[）)]\*\*\s*\$', text)
        or (
            text.startswith('**') and text.endswith('**')
            and ('小题' in plain or re.search(r'第.*题.*[（(]\d+[）)]', plain))
        )
    )


def render_solution_row(
    solution_blocks: List[List[str]], highlight_phrases: List[str]
) -> str:
    """将多个完整解答块默认渲染为横向排列。"""
    items = []
    for block in solution_blocks:
        heading = strip_markdown(block[0])
        body = ''.join(render_body_paragraph(line, highlight_phrases) for line in block[1:])
        items.append(
            f'<div class="solution-item"><p class="hw-bold solution-heading">'
            f'{heading}</p>{body}</div>'
        )
    return f'<div class="solution-row">{"".join(items)}</div>'


def convert_list_item(text: str, highlight_phrases: List[str], list_type: str = 'bullet') -> str:
    """转换列表项"""
    text = process_inline(text, highlight_phrases)
    if list_type == 'bullet':
        return f'<p class="body-text hw">• {text}</p>'
    elif list_type == 'number':
        return f'<p class="body-text hw">{text}</p>'
    else:
        return f'<p class="body-text hw">{text}</p>'


def convert_cover_page(page_text: str, page_idx: int, output_dir: str = '.') -> str:
    """将第一页转换为油画封面专用 HTML：随机油画 + 仅课题/课时"""
    # 封面背景：从 knowledge/images/bg/ 随机选一张油画
    bg_dir = pathlib.Path(__file__).resolve().parent.parent / 'knowledge' / 'images' / 'bg'
    img_src = './images/bg/default.jpg'  # 兜底默认
    if bg_dir.exists():
        bg_images = [f for f in os.listdir(bg_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if bg_images:
            selected = random.choice(bg_images)
            # 计算从输出 HTML 到 bg 目录的相对路径
            abs_bg_dir = str(bg_dir.resolve())
            img_rel_path = os.path.relpath(abs_bg_dir, output_dir).replace('\\', '/')
            img_src = f'{img_rel_path}/{selected}'

    lines = [l.strip() for l in page_text.split('\n') if l.strip()]

    # 提取标题（去掉 emoji 和 ###）
    title = ''
    for line in lines:
        if line.startswith('### '):
            title = line[4:].strip()
            # 去掉 emoji
            title = re.sub(r'^[^\w\u4e00-\u9fff]+\s*', '', title)
            break

    html = f'''<div class="slide cover-slide" id="s{page_idx}">
  <img class="cover-bg" src="{img_src}" alt="封面油画" />
  <div class="cover-card">
    <div class="cover-title">{title}</div>
  </div>
  <div class="pagenum">— {page_idx + 1} —</div>
</div>'''
    return html


def convert_page_to_html(page_text: str, page_idx: int, total_pages: int) -> str:
    """将单页 MD 转换为 HTML slide"""
    title = parse_title(page_text)
    page_type = detect_page_type(page_text, title)
    highlight_phrases = get_page_phrases(title, 'highlight_phrases')
    red_conclusion_phrases = get_page_phrases(title, 'red_conclusion_phrases')

    # 第一页（封面）使用专用渲染
    if page_idx == 0:
        return convert_cover_page(page_text, page_idx, _output_dir)

    lines = page_text.split('\n')

    content_parts = []
    i = 0
    in_list = False
    list_type = 'bullet'

    # 根据页面类型决定 slide 的 class
    slide_class = 'slide'
    if page_type == 'objective':
        slide_class = 'slide objective-page'

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 跳过标题行
        if i == 0 and stripped.startswith('### '):
            i += 1
            continue

        # 跳过空行
        if not stripped:
            if in_list:
                content_parts.append('</div>')
                in_list = False
            i += 1
            continue

        # 表格
        if '|' in stripped and stripped.startswith('|'):
            if in_list:
                content_parts.append('</div>')
                in_list = False
            html_table, i = extract_table(
                lines, i, highlight_phrases, red_conclusion_phrases
            )
            content_parts.append(html_table)
            continue

        # 独立图片行 — 连续多张自动横排
        img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', stripped)
        if img_match:
            if in_list:
                content_parts.append('</div>')
                in_list = False

            # 收集所有连续图片
            imgs = []
            while i < len(lines):
                stripped_i = lines[i].strip()
                m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', stripped_i)
                if not m:
                    # 允许图片间有空行
                    if not stripped_i:
                        i += 1
                        continue
                    break
                imgs.append((m.group(1), m.group(2)))
                i += 1

            if len(imgs) > 1:
                cols = ''.join(
                    f'<div class="img-item">{convert_image(src, alt)}</div>'
                    for alt, src in imgs
                )
                content_parts.append(f'<div class="img-row">{cols}</div>')
            else:
                content_parts.append(convert_image(imgs[0][1], imgs[0][0]))
            continue

        # 行内图片：多个图片默认横向排列，文字保留在图片行前后。
        if '![' in stripped:
            if in_list:
                content_parts.append('</div>')
                in_list = False
            image_matches = list(re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', stripped))
            if len(image_matches) > 1:
                prefix = stripped[:image_matches[0].start()].strip()
                suffix = stripped[image_matches[-1].end():].strip()
                if prefix:
                    content_parts.append(f'<p class="body-text hw">{process_inline(prefix, highlight_phrases)}</p>')
                items = ''.join(
                    f'<div class="img-item">{convert_image(m.group(2), m.group(1))}</div>'
                    for m in image_matches
                )
                content_parts.append(f'<div class="img-row">{items}</div>')
                if suffix:
                    content_parts.append(f'<p class="body-text hw">{process_inline(suffix, highlight_phrases)}</p>')
            else:
                m = image_matches[0]
                text_before = stripped[:m.start()].strip()
                remaining = stripped[m.end():].strip()
                parts = []
                if text_before:
                    parts.append(process_inline(text_before, highlight_phrases))
                parts.append(convert_image(m.group(2), m.group(1)))
                if remaining:
                    parts.append(process_inline(remaining, highlight_phrases))
                content_parts.append(f'<p class="body-text hw">{"".join(parts)}</p>')
            i += 1
            continue

        # 引用块（口头回答/练习本上完成等）
        if stripped.startswith('> '):
            if in_list:
                content_parts.append('</div>')
                in_list = False
            text = process_inline(stripped[2:], highlight_phrases)
            # 识别特殊标记
            if '口头回答' in text or '练习本上完成' in text:
                content_parts.append(f'<p class="body-text hw" style="color:#888;">✏️ {text}</p>')
            else:
                content_parts.append(f'<p class="body-text hw" style="color:#666;">{text}</p>')
            i += 1
            continue

        # 连续独立编号小题默认横向排列；普通列表仍保留原有纵向结构。
        if is_question_line(stripped, page_idx, total_pages):
            if in_list:
                content_parts.append('</div>')
                in_list = False
            questions = []
            while i < len(lines):
                candidate = lines[i].strip()
                if not candidate:
                    i += 1
                    continue
                if is_question_line(candidate, page_idx, total_pages):
                    questions.append(candidate)
                    i += 1
                    continue
                # 题目之间的括号提示属于前一小题，不能打断横排分组。
                if questions and candidate.startswith(('（', '(')):
                    questions[-1] += f'<br><span class="question-note">{candidate}</span>'
                    i += 1
                    continue
                break
            if len(questions) > 1:
                content_parts.append(render_question_row(questions, highlight_phrases))
            else:
                content_parts.append(f'<p class="body-text hw">{process_inline(questions[0], highlight_phrases)}</p>')
            continue

        # 列表项
        is_bullet = stripped.startswith('- ') or stripped.startswith('* ')
        is_number = re.match(r'^\d+[.、]\s*', stripped)
        is_circle = stripped.startswith(('①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩'))

        if is_bullet or is_number or is_circle:
            if not in_list:
                content_parts.append('<div class="indent">')
                in_list = True
            if is_bullet:
                text = stripped[2:]
            elif is_number:
                text = stripped
            else:
                text = stripped
            content_parts.append(convert_list_item(text, highlight_phrases))
            i += 1
            continue

        # 多个完整解答块：默认横向排列；浏览器检测实质溢出后才纵排。
        if is_solution_heading(stripped):
            if in_list:
                content_parts.append('</div>')
                in_list = False
            solution_blocks = []
            while i < len(lines):
                candidate = lines[i].strip()
                if not candidate:
                    i += 1
                    continue
                if not is_solution_heading(candidate):
                    break
                block = [candidate]
                i += 1
                while i < len(lines):
                    body_line = lines[i].strip()
                    if not body_line:
                        i += 1
                        continue
                    if is_solution_heading(body_line):
                        break
                    block.append(body_line)
                    i += 1
                solution_blocks.append(block)
            if len(solution_blocks) > 1:
                content_parts.append(render_solution_row(solution_blocks, highlight_phrases))
            else:
                heading = strip_markdown(solution_blocks[0][0])
                content_parts.append(f'<p class="hw-bold" style="font-size:28px;margin-top:16px;">{heading}</p>')
                for body_line in solution_blocks[0][1:]:
                    content_parts.append(render_body_paragraph(body_line, highlight_phrases))
            continue

        # 加粗行：法则、定义等精确结论优先渲染为红笔结论框。
        if stripped.startswith('**') and stripped.endswith('**') and len(stripped) > 4:
            if in_list:
                content_parts.append('</div>')
                in_list = False
            text = stripped[2:-2]
            if is_red_conclusion(stripped, red_conclusion_phrases):
                content_parts.append(f'''
<div style="text-align: center; margin-top: 40px;">
  <div class="conclusion">
    <span class="hw-red">{text}</span>
  </div>
</div>''')
            else:
                content_parts.append(f'<p class="hw-bold" style="margin-top:16px;">{text}</p>')
            i += 1
            continue

        # 普通正文行
        if in_list:
            content_parts.append('</div>')
            in_list = False

        text = process_inline(stripped, highlight_phrases)

        # 判断是否为红笔结论
        if is_red_conclusion(stripped, red_conclusion_phrases):
            content_parts.append(f'''
<div style="text-align: center; margin-top: 40px;">
  <div class="conclusion">
    <span class="hw-red">{text}</span>
  </div>
</div>''')
        # 判断是否为蓝笔思路
        elif is_blue_hint(stripped):
            content_parts.append(f'<p class="body-text hw-blue">{text}</p>')
        else:
            content_parts.append(render_body_paragraph(stripped, highlight_phrases))

        i += 1

    if in_list:
        content_parts.append('</div>')

    content_html = '\n'.join(content_parts)

    # 组合页面
    html = f'<div class="{slide_class}" id="s{page_idx}">\n'
    if title:
        html += f'  <div class="title">{title}</div>\n'
    html += f'  {content_html}\n'
    html += f'  <div class="pagenum">— {page_idx + 1} —</div>\n'
    html += '</div>'

    return html




def convert(md_path: str) -> str:
    """主转换函数"""
    md_path = pathlib.Path(md_path)
    if not md_path.exists():
        print(f"错误：文件未找到 {md_path}")
        sys.exit(1)

    # 加载课程配置（关键词、正则等）
    load_config(str(md_path))

    md_text = md_path.read_text(encoding='utf-8')

    # 记录输出目录（用于封面图片相对路径计算）
    global _output_dir
    _output_dir = str(md_path.parent.resolve())

    # 分页
    pages = split_pages(md_text)
    print(f"共检测到 {len(pages)} 页")

    # 加载模板
    template = load_template()

    # 逐页转换
    slides_html = []
    for i, page in enumerate(pages):
        slide = convert_page_to_html(page, i, len(pages))
        slides_html.append(slide)

    # 替换模板占位符
    title = parse_title(pages[0]) if pages else '课件'
    output_html = template.replace('{{TITLE}}', title)
    output_html = output_html.replace('{{SLIDES}}', '\n\n'.join(slides_html))

    # 输出到同目录
    output_path = md_path.with_suffix('.html')
    output_html = output_html.replace('$$', '$')
    output_path.write_text(output_html, encoding='utf-8')

    # 硬约束验证失败即删除输出，退回课件修改。
    from validate_md2htmlyishu import validate
    errors = validate(md_path, output_path)
    if errors:
        output_path.unlink(missing_ok=True)
        print('HTML 硬约束验证失败，已删除不合格输出：')
        for error in errors:
            print(f'- {error}')
        sys.exit(1)

    print(f"输出：{output_path}")
    return str(output_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python tools/md2htmlyishu.py <input.md>")
        sys.exit(1)
    convert(sys.argv[1])
