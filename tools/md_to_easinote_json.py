"""将 courseware.md 转换为希沃白板可导入的 lesson.json

用法:
  python tools/md_to_easinote_json.py <input.md> [output.json] [--assets-dir DIR]

示例:
  python tools/md_to_easinote_json.py outputs/c21/21.7-courseware.md
  python tools/md_to_easinote_json.py foo.md out.json --assets-dir ./my-imgs

约定:
  - 输入须为按 <div style="page-break-after: always;"></div> 分页的 Markdown
  - 图片路径相对于 MD 文件目录，自动复制到 assets 目录
  - LaTeX $...$ 自动转 Unicode（∠ ° △ ⊥ · 等）
  - Markdown 表格自动渲染为 PNG 图片
  - 超出 740px 的页面自动拆分
"""

import hashlib
import json
import os
import re
import shutil
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ═══ 命令行 ═══
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

md_path = os.path.abspath(sys.argv[1])
if not os.path.isfile(md_path):
    print(f"错误: 文件不存在: {md_path}")
    sys.exit(1)

md_dir = os.path.dirname(md_path)
stem = os.path.splitext(os.path.basename(md_path))[0]

# 输出 JSON
args = sys.argv[2:]
out_json = os.path.join(md_dir, f"{stem}.json")
assets_dir = os.path.join(md_dir, "assets")

i = 0
while i < len(args):
    if args[i] == "--assets-dir" and i + 1 < len(args):
        assets_dir = os.path.abspath(args[i + 1])
        i += 2
    elif not args[i].startswith("--"):
        out_json = args[i]
        i += 1
    else:
        i += 1

os.makedirs(assets_dir, exist_ok=True)

NO_TABLE_IMG = '--no-table-img' in sys.argv
if NO_TABLE_IMG:
    sys.argv.remove('--no-table-img')

# ═══ 常量 ═══
PW, MG = 1120, 70
TFS, BFS = 33, 26
TH, BH = 56, 50
CT = "#12355b"
CS = "#1f4e79"
CB = "#222222"
CD = "#333333"
LIMIT = 740
CN_FONT = "方正小标宋简体"
EN_FONT = "Times New Roman"

LATEX = [
    (r"\\angle", "∠"),
    (r"\\triangle", "△"),
    (r"\\perp", "⊥"),
    (r"\\circ", "°"),
    (r"\\cdot", "·"),
    (r"\\times", "×"),
    (r"\\div", "÷"),
    (r"\\pm", "±"),
    (r"\\approx", "≈"),
    (r"\\neq", "≠"),
    (r"\\leq", "≤"),
    (r"\\geq", "≥"),
    (r"\\because", "∵"),
    (r"\\therefore", "∴"),
    (r"\\sqrt\{([^}]+)\}", r"√(\1)"),
    (r"\\frac\{([^}]+)\}\{([^}]+)\}", r"\1/\2"),
    (r"\\text\{([^}]*)\}", r"\1"),
    (r"\\qquad", ""),
    (r"\\quad", " "),
    (r"\^\{?\\circ\}?", "°"),
    (r"\^\{([^}]+)\}", r"\1"),
    (r"_\{(.+?)\}", r"_\1"),
    (r"\\[a-zA-Z]+", ""),
]

# ═══ 中文字体探测（复用 md2docx.py 方案） ═══
def _setup_mpl_chinese():
    for font_name in ['Microsoft YaHei', 'SimHei', 'STSong']:
        try:
            from matplotlib import font_manager
            if font_manager.findfont(font_name):
                plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False
                return font_name
        except Exception:
            continue
    return None

_setup_mpl_chinese()

# ═══ 工具函数 ═══
def _clean(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)

    def _r(m):
        inner = m.group(1)
        for p, r in LATEX:
            inner = re.sub(p, r, inner)
        return inner.strip()

    text = re.sub(r"\$\$(.+?)\$\$", _r, text)
    text = re.sub(r"\$(.+?)\$", _r, text)
    return re.sub(r"[{}]", "", text).strip()


def _cp(src):
    fn = os.path.basename(src)
    dst = os.path.join(assets_dir, fn)
    if os.path.exists(dst):
        return fn
    src_full = os.path.join(md_dir, src)
    if os.path.exists(src_full):
        try:
            shutil.copy2(src_full, dst)
        except Exception:
            pass
        return fn
    return None


# ═══ 表格渲染（复用 md2docx.py 方案） ═══
def _clean_cell_text(text):
    text = re.sub(r'\$', '', text)
    text = re.sub(r'\^\{([^}]*)\}', r'^\1', text)
    text = re.sub(r'\_\{([^}]*)\}', r'_\1', text)
    text = re.sub(r'[{}]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _parse_md_table(lines):
    """解析 MD 表格，返回 (headers, data_rows)"""
    headers = [c.strip() for c in lines[0].split('|')[1:-1]]
    data = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if cells:
            data.append(cells)
    return headers, data

def _wrap_text(text, max_chars_per_line):
    """手动换行：在 max_chars 处插入 \\n（在标点或空格后断行）"""
    if len(text) <= max_chars_per_line:
        return text
    # 中文标点 unicode 范围 + 空格
    punct_set = set('\uff0c\u3002\uff1b\u3001\uff01\uff1f\uff09\u3011\u300d\u300f ')
    lines = []
    remaining = text
    while len(remaining) > max_chars_per_line:
        cut = max_chars_per_line
        for offset in range(3, -6, -1):
            pos = max_chars_per_line + offset
            if 0 <= pos < len(remaining) and remaining[pos] in punct_set:
                cut = pos + 1
                break
        if cut <= 0:
            cut = max_chars_per_line
        lines.append(remaining[:cut])
        # 去掉下一行开头的标点
        remaining = remaining[cut:]
        while remaining and remaining[0] in punct_set:
            remaining = remaining[1:]
    if remaining:
        lines.append(remaining)
    return '\n'.join(lines)

def _render_table(rows, slide_id, ei):
    """用 matplotlib 渲染表格为 PNG（复用 md2docx.py 方案），返回 (fn, w, h)"""
    raw = rows
    headers, data_rows = _parse_md_table(raw)
    headers = [_clean_cell_text(h) for h in headers]
    data_rows = [[_clean_cell_text(c) for c in row] for row in data_rows]

    # 补齐列数
    n_cols = max(len(headers), max((len(r) for r in data_rows), default=1))
    headers += [''] * (n_cols - len(headers))
    for r in data_rows:
        r += [''] * (n_cols - len(r))

    n_rows = len(data_rows) + 1
    cell_text = [headers] + data_rows

    raw_key = "||".join(raw)
    max_width_inch = 10.5 / 2.54

    if n_cols <= 4:
        font_size = 9
        row_height_factor = 1.4
    elif n_cols <= 7:
        font_size = 8
        row_height_factor = 1.3
    else:
        font_size = 7
        row_height_factor = 1.2

    # 估算每列字符数：中文字宽 ≈ font_size * 0.07cm，英文 ≈ font_size * 0.04cm
    col_width_cm = 10.5 / n_cols
    cn_cw = font_size * 0.07  # cm per Chinese char
    chars_per_line = max(8, int(col_width_cm / cn_cw * 0.92))  # 92% 留边距

    # 对窄列（≤2列）且文本长的表格做换行
    if n_cols <= 2:
        for i in range(n_rows):
            for j in range(n_cols):
                cell_text[i][j] = _wrap_text(cell_text[i][j], chars_per_line)

    # 重新估算高度
    max_lines = 1
    for row in cell_text:
        for cell in row:
            max_lines = max(max_lines, cell.count('\n') + 1)

    fig_w = max_width_inch
    fig_h = max(n_rows * 0.4 * max(1, max_lines * 0.7), 1.2)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis('off')
    ax.set_xlim(0, max_width_inch)
    ax.set_ylim(0, n_rows * 0.4 * max(1, max_lines * 0.7))

    tbl = ax.table(cellText=cell_text, cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.scale(1, row_height_factor * max(1, max_lines * 0.5))

    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor('#333333')
        cell.set_linewidth(0.5)
        cell.set_fontsize(font_size)
        if row == 0:
            cell.set_facecolor('#e8e8e8')
            cell.set_text_props(weight='bold', fontsize=font_size)
        else:
            cell.set_facecolor('#ffffff')
            cell.set_text_props(fontsize=font_size)

    plt.tight_layout(pad=0.3)
    key = hashlib.md5((raw_key + str(__import__('time').time())).encode()).hexdigest()[:8]
    fn = f"t_{slide_id}_{ei:03d}_{key}.png"
    dst = os.path.join(assets_dir, fn)
    fig.savefig(dst, dpi=200, facecolor='white', edgecolor='none')
    plt.close(fig)
    return fn, min(int(fig_w * 200), 1120), int(fig_h * 200)


# ═══ 解析一页 ═══
def _slide(si, raw):
    el, ls, y, ei = [], raw.split("\n"), 54, 0
    sid = f"s{si + 1:02d}"

    def _t(txt, fs=BFS, b=False, c=CB, eh=0, it=False, ff=CN_FONT):
        nonlocal y, ei
        txt = _clean(txt)
        if not txt:
            return
        ei += 1
        h = max(BH, len(txt) // 28 * (BH + 2) + BH)
        elem = {
            "id": f"{sid}_e{ei:03d}",
            "type": "text",
            "text": txt,
            "x": MG,
            "y": y,
            "width": PW,
            "height": h,
            "fontSize": fs,
            "bold": b,
            "color": c,
            "fontFamily": ff,
        }
        if it:
            elem["italic"] = True
        el.append(elem)
        y += h + 4 + eh

    def _i(src, w=720, h=420):
        nonlocal y, ei
        fn = _cp(src)
        if fn:
            ei += 1
            el.append({
                "id": f"{sid}_e{ei:03d}",
                "type": "image",
                "src": fn,
                "x": max(0, (1280 - w) // 2),
                "y": y,
                "width": min(w, 1120),
                "height": h,
            })
            y += h + 12

    i = 0
    while i < len(ls):
        ln = ls[i].strip()
        if not ln:
            y += 4
            i += 1
            continue
        if re.match(r"^#\s", ln):
            _t(re.sub(r"^#+\s*", "", ln), fs=38, b=True, c=CT)
        elif re.match(r"^##\s", ln):
            _t(re.sub(r"^##\s+", "", ln), fs=TFS, b=True, c=CT)
        elif re.match(r"^###\s", ln):
            _t(re.sub(r"^###\s+", "", ln), fs=33, b=True, c=CS)
        elif re.match(r"^!\[.*\]\((.+)\)", ln):
            m = re.match(r"^!\[.*\]\((.+)\)", ln)
            if m:
                _i(m.group(1))
        elif ln == "```mermaid":
            bl = []
            i += 1
            while i < len(ls) and not ls[i].strip().startswith("```"):
                bl.append(ls[i].rstrip())
                i += 1
            i += 1
            _t(">> " + " | ".join(bl), fs=20, c=CD)
        elif ln in ("---", "***", "___"):
            y += 8
        elif ln.startswith("|"):
            rs = []
            while i < len(ls) and ls[i].strip().startswith("|"):
                rs.append(ls[i].strip())
                i += 1
            i -= 1
            if NO_TABLE_IMG:
                for tr in rs:
                    if not re.match(r"^\|[: \-\|]+\|$", tr):
                        _t("  ".join(c.strip() for c in tr.split("|") if c.strip()), fs=22, c=CD)
            elif len(rs) >= 2:
                fn, iw, ih = _render_table(rs, sid, ei)
                if fn:
                    ei += 1
                    el.append({
                        "id": f"{sid}_e{ei:03d}",
                        "type": "image",
                        "src": fn,
                        "x": max(0, (1280 - iw) // 2),
                        "y": y,
                        "width": min(iw, 1120),
                        "height": ih,
                    })
                    y += ih + 12
        else:
            pa = [ln]
            i += 1
            while (
                i < len(ls)
                and ls[i].strip()
                and not re.match(r"^[#!|`\-]", ls[i].strip())
                and not ls[i].strip().startswith("```")
                and ls[i].strip() not in ("---", "***", "___")
            ):
                pa.append(ls[i].strip())
                i += 1
            i -= 1
            tx = " ".join(pa)
            if len(tx) > 3:
                _is_en = bool(re.match(r'^[\x00-\x7f\s\(\)\[\]\{\}<>≈≠≤≥±×÷·°∠△⊥∵∴√⅓½²³\-\+\=]+$', _clean(tx)))
                _t(tx, it=_is_en, ff=EN_FONT if _is_en else CN_FONT)
        i += 1
    return {"id": sid, "elements": el}


# ═══ 溢出拆分 ═══
def _split(ss):
    res, ch = [], False
    for s in ss:
        el = s["elements"]
        if not el:
            res.append(s)
            continue
        my = max(e["y"] + e.get("height", 0) for e in el)
        if my <= LIMIT:
            res.append(s)
            continue
        oi = next(
            (idx for idx, e in enumerate(el) if e["y"] + e.get("height", 0) > LIMIT),
            None,
        )
        sa = max(len(el) // 2, 2) if oi is None or oi <= 1 else oi
        if oi is not None and oi > 1:
            while sa > 1:
                pv = el[sa - 1]
                if el[sa]["y"] - (pv["y"] + pv.get("height", 0)) > 15 or (
                    pv.get("bold") and pv.get("fontSize", 20) >= 24
                ):
                    break
                sa -= 1
        if sa <= 1:
            sa = max(len(el) // 2, 2)
        a, b = el[:sa], el[sa:]
        by = b[0]["y"] if b else 54
        for e in b:
            e["y"] = e["y"] - by + 54
        res.append({"id": s["id"] + "a", "elements": a})
        res.append({"id": s["id"] + "b", "elements": b})
        ch = True
    return res, ch


# ═══ 主 ═══
with open(md_path, encoding="utf-8") as f:
    md = f.read()
raw = [
    s.strip()
    for s in re.split(r'<div style="page-break-after: always;"></div>', md)
    if s.strip()
]
slides = [_slide(si, r) for si, r in enumerate(raw)]

# 去 frontmatter
slides = [
    s
    for s in slides
    if s["elements"]
    and any(
        e.get("text", "").strip()
        and not re.match(
            r"^(title|source|date|chapter|section|lesson|type):", e.get("text", "")
        )
        for e in s["elements"]
    )
]

# 拆分溢出
while True:
    slides, ch = _split(slides)
    if not ch:
        break

for i, s in enumerate(slides):
    s["id"] = f"s{i + 1:02d}"

doc = {"slides": slides}
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

tot = sum(len(s["elements"]) for s in slides)
im = sum(1 for s in slides for e in s["elements"] if e["type"] == "image")
print(f"OK {out_json}")
print(f"   slides={len(slides)}  text={tot - im}  image={im}  total={tot}")
over = [
    (s["id"], max(e["y"] + e.get("height", 0) for e in s["elements"])) for s in slides
]
over = [x for x in over if x[1] > LIMIT]
if over:
    print(f"   WARN {len(over)} pages overflow: {over}")
else:
    print(f"   all pages <= {LIMIT}px")
