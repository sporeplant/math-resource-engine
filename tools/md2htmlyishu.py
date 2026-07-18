#!/usr/bin/env python3
"""
md2htmlyishu — 将课件 Markdown 转换为一数风格 HTML（1920×1080）

用法：
  python tools/md2htmlyishu.py <input.md>

输出：与输入文件同目录，同名但扩展名为 .html

设计原则：
  - 最大限度覆盖 skills/md2htmlyishu/SKILL.md 的所有规范
  - 自动识别页面类型并应用对应布局
  - 自动添加荧光笔标记、红笔结论、蓝笔思路
  - 零装饰，纯手写板书感
"""

import sys
import os
import re
import pathlib
from typing import List, Tuple, Optional


TEMPLATE_PATH = pathlib.Path(__file__).resolve().parent.parent / 'skills' / 'md2htmlyishu' / 'template.html'

# === 与 SKILL.md §2.2 保持一致 ===
STYLE_CONFIG = {
    'bg': '#FDF6E3',
    'ink': '#1a1a2e',
    'red': '#C62828',
    'blue': '#1565C0',
    'yellow': '#FFEB3B',
    'title_font_size': '64px',
    'body_font_size': '30px',
    'table_font_size': '26px',
}

PAGE_WIDTH = 1920
PAGE_HEIGHT = 1080

# 需要荧光笔标记的关键词（自动识别）
HIGHLIGHT_KEYWORDS = [
    '全面调查', '抽样调查', '普查', '抽查',
    '总体', '个体', '样本', '样本容量',
    '频数', '频率', '极差', '组距', '组数',
    '变化情况', '市场占有率', '占比',
    '折线统计图', '扇形统计图', '条形统计图',
    '简单随机抽样', '代表性', '广泛性',
]

# 红笔结论关键词（自动识别为结论框）
RED_CONCLUSION_KEYWORDS = [
    '口诀', '怎么选', '怎么判断',
    '频率 =', '频数 ÷', '各组频率之和',
    '条形看', '折线看', '扇形看',
]

# 红笔结论正则（更精准匹配）
RED_CONCLUSION_PATTERNS = [
    r'^频率\s*=\s*频数',
    r'^各组频率之和',
    r'^条形看.*折线看.*扇形看',
    r'^怎么选.*[?？]',
]

# 蓝笔思路关键词（自动识别为蓝笔批注）
# 注意：只用于"思路引导"，不用于"操作步骤"
BLUE_HINT_KEYWORDS = [
    '思路', '引导',
]

# 蓝笔思路正则
BLUE_HINT_PATTERNS = [
    r'^[①②③④⑤]\s*[^，。；]*[=→]',  # ① xxx = yyy 或 ① xxx → yyy
]


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


def should_highlight(text: str) -> bool:
    """判断文本是否应该加荧光笔标记"""
    return any(kw in text for kw in HIGHLIGHT_KEYWORDS)


def is_red_conclusion(text: str) -> bool:
    """判断文本是否是红笔结论（更精准匹配）"""
    # 先检查正则
    for pattern in RED_CONCLUSION_PATTERNS:
        if re.search(pattern, text):
            return True
    # 再检查关键词（但需要整行匹配）
    text_clean = text.strip()
    for kw in RED_CONCLUSION_KEYWORDS:
        if kw in text_clean and len(text_clean) < 50:  # 结论通常较短
            return True
    return False


def is_blue_hint(text: str) -> bool:
    """判断文本是否是蓝笔思路（更精准匹配）"""
    # 先检查正则
    for pattern in BLUE_HINT_PATTERNS:
        if re.search(pattern, text):
            return True
    # 再检查关键词
    text_clean = text.strip()
    for kw in BLUE_HINT_KEYWORDS:
        if kw in text_clean:
            return True
    return False


def process_inline(text: str) -> str:
    """处理行内标记：加粗、荧光笔、LaTeX"""
    # 先处理加粗
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # 自动荧光笔标记（按关键词长度降序，避免子串重复标记）
    # 策略：先替换长的，再替换短的；短的在已标记文本中不会被再次匹配
    sorted_keywords = sorted(HIGHLIGHT_KEYWORDS, key=len, reverse=True)
    for kw in sorted_keywords:
        # 只替换未被 <span class="hl"> 包围的实例
        # 使用负向后发断言，避免匹配已在标签内的文本
        pattern = f'(?<!<span class="hl">){re.escape(kw)}(?!</span>)'
        replacement = f'<span class="hl">{kw}</span>'
        text = re.sub(pattern, replacement, text)

    return text


def extract_table(lines: List[str], start_idx: int) -> Tuple[str, int]:
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
        cells = [process_inline(c.strip()) for c in line.split('|')[1:-1]]
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


def convert_list_item(text: str, list_type: str = 'bullet') -> str:
    """转换列表项"""
    text = process_inline(text)
    if list_type == 'bullet':
        return f'<p class="body-text hw">• {text}</p>'
    elif list_type == 'number':
        return f'<p class="body-text hw">{text}</p>'
    else:
        return f'<p class="body-text hw">{text}</p>'


def convert_page_to_html(page_text: str, page_idx: int, total_pages: int) -> str:
    """将单页 MD 转换为 HTML slide"""
    title = parse_title(page_text)
    page_type = detect_page_type(page_text, title)
    lines = page_text.split('\n')

    content_parts = []
    i = 0
    in_list = False
    list_type = 'bullet'

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
            html_table, i = extract_table(lines, i)
            content_parts.append(html_table)
            continue

        # 独立图片行
        img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', stripped)
        if img_match:
            if in_list:
                content_parts.append('</div>')
                in_list = False
            alt, src = img_match.group(1), img_match.group(2)
            content_parts.append(convert_image(src, alt))
            i += 1
            continue

        # 行内图片
        if '![' in stripped:
            if in_list:
                content_parts.append('</div>')
                in_list = False
            # 提取文字和图片
            parts = []
            last_end = 0
            for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', stripped):
                text_before = stripped[last_end:m.start()].strip()
                if text_before:
                    parts.append(process_inline(text_before))
                parts.append(convert_image(m.group(2), m.group(1)))
                last_end = m.end()
            remaining = stripped[last_end:].strip()
            if remaining:
                parts.append(process_inline(remaining))
            content_parts.append(f'<p class="body-text hw">{"".join(parts)}</p>')
            i += 1
            continue

        # 引用块（口头回答/练习本上完成等）
        if stripped.startswith('> '):
            if in_list:
                content_parts.append('</div>')
                in_list = False
            text = process_inline(stripped[2:])
            # 识别特殊标记
            if '口头回答' in text or '练习本上完成' in text:
                content_parts.append(f'<p class="body-text hw" style="color:#888;">✏️ {text}</p>')
            else:
                content_parts.append(f'<p class="body-text hw" style="color:#666;">{text}</p>')
            i += 1
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
            content_parts.append(convert_list_item(text))
            i += 1
            continue

        # 加粗行（子标题）
        if stripped.startswith('**') and stripped.endswith('**') and len(stripped) > 4:
            if in_list:
                content_parts.append('</div>')
                in_list = False
            text = stripped[2:-2]
            content_parts.append(f'<p class="hw-bold" style="font-size:28px;margin-top:16px;">{text}</p>')
            i += 1
            continue

        # 普通正文行
        if in_list:
            content_parts.append('</div>')
            in_list = False

        text = process_inline(stripped)

        # 判断是否为红笔结论
        if is_red_conclusion(stripped):
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
            content_parts.append(f'<p class="body-text hw">{text}</p>')

        i += 1

    if in_list:
        content_parts.append('</div>')

    content_html = '\n'.join(content_parts)

    # 组合页面
    html = f'<div class="slide" id="s{page_idx}">\n'
    if title:
        html += f'  <div class="title">{title}</div>\n'
    html += f'  {content_html}\n'
    html += f'  <div class="pagenum">— {page_idx + 1} —</div>\n'
    html += '</div>'

    return html


def build_nav(pages: List[str]) -> str:
    """构建右下角浮动圆点导航"""
    buttons = []
    for i in range(len(pages)):
        cls = 'active' if i == 0 else ''
        buttons.append(f'  <button class="{cls}" onclick="show({i})" title="第{i+1}页"></button>')

    return '<div class="nav-dots">\n' + '\n'.join(buttons) + '\n</div>\n'


def convert(md_path: str) -> str:
    """主转换函数"""
    md_path = pathlib.Path(md_path)
    if not md_path.exists():
        print(f"错误：文件未找到 {md_path}")
        sys.exit(1)

    md_text = md_path.read_text(encoding='utf-8')

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

    # 构建导航
    nav_html = build_nav(pages)

    # 替换模板占位符
    title = parse_title(pages[0]) if pages else '课件'
    output_html = template.replace('{{TITLE}}', title)
    output_html = output_html.replace('{{NAV}}', nav_html)
    output_html = output_html.replace('{{SLIDES}}', '\n\n'.join(slides_html))

    # 输出到同目录
    output_path = md_path.with_suffix('.html')
    output_html = output_html.replace('$$', '$')
    output_path.write_text(output_html, encoding='utf-8')
    print(f"输出：{output_path}")
    return str(output_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python tools/md2htmlyishu.py <input.md>")
        sys.exit(1)
    convert(sys.argv[1])
