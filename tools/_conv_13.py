#!/usr/bin/env python3
"""Convert courseware MD to EasiNote JSON with proper table rendering and image scaling."""
import json, os, re, hashlib, sys

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

# EasiNote slide dimensions
SLIDE_W = 1280
SLIDE_H = 720
CONTENT_X = 70
CONTENT_W = 1100
# Image size limits (per new rule)
IMG_MAX_W_RATIO = 0.25   # max width = 25% of slide width
IMG_MAX_H_RATIO = 0.50   # max height = 50% of slide height

# LaTeX→Unicode
LATEX_PAIRS = [
    (r'\\angle', '\u2220'),
    (r'\\triangle', '\u25b3'),
    (r'\\perp', '\u22a5'),
    (r'\\circ', '\u00b0'),
    (r'\\cdot', '\u00b7'),
    (r'\\times', '\u00d7'),
    (r'\\div', '\u00f7'),
    (r'\\pm', '\u00b1'),
    (r'\\approx', '\u2248'),
    (r'\\neq', '\u2260'),
    (r'\\leq', '\u2264'),
    (r'\\geq', '\u2265'),
    (r'\\because', '\u2235'),
    (r'\\therefore', '\u2234'),
    (r'\\sqrt\{([^}]+)\}', r''),
    (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2'),
    (r'\\text\{([^}]*)\}', r'\1'),
    (r'\\qquad', ''),
    (r'\\quad', ' '),
    (r'\\[a-zA-Z]+', ''),
]

def clean_latex(text):
    for p, r in LATEX_PAIRS:
        text = re.sub(p, r, text)
    text = re.sub(r'[{}]', '', text)
    return text.strip()

def resolve_math(text):
    text = re.sub(r'\$\$(.+?)\$\$', lambda m: clean_latex(m.group(1)), text)
    text = re.sub(r'\$(.+?)\$', lambda m: clean_latex(m.group(1)), text)
    text = clean_latex(text)
    return text


# Image sizing with aspect-ratio constraints
def calc_img_dims(orig_w, orig_h):
    """Calculate display dimensions respecting max width 25% and max height 50%."""
    max_w = int(SLIDE_W * IMG_MAX_W_RATIO)
    max_h = int(SLIDE_H * IMG_MAX_H_RATIO)
    ratio = orig_w / orig_h if orig_h > 0 else 1.0
    w = min(orig_w, max_w)
    h = int(w / ratio)
    if h > max_h:
        h = max_h
        w = int(h * ratio)
    return w, h

def get_img_size(full_path):
    """Return (w, h) for an image file, or None if unreadable."""
    if PILImage:
        try:
            with PILImage.open(full_path) as im:
                return im.size
        except Exception:
            pass
    return None


# Table rendering
def render_table_img(lines, assets_dir, sid, eid):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # Find Chinese font
    try:
        from matplotlib import font_manager
        for fn in ['Microsoft YaHei', 'SimHei', 'STSong']:
            try:
                if font_manager.findfont(fn):
                    plt.rcParams['font.sans-serif'] = [fn, 'DejaVu Sans']
                    plt.rcParams['axes.unicode_minus'] = False
                    break
            except:
                pass
    except:
        pass

    # Parse MD table (skip separator row)
    headers = [c.strip() for c in lines[0].split('|')[1:-1]]
    data = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if cells:
            data.append(cells)
    headers = [clean_latex(h) for h in headers]
    data = [[clean_latex(c) for c in row] for row in data]

    n_cols = len(headers)
    if n_cols == 0:
        return None, 0, 0

    # Pad rows with fewer columns than header
    for ri, row in enumerate(data):
        while len(row) < n_cols:
            row.append('')

    n_rows = len(data) + 1
    cell_text = [headers] + data

    if n_cols <= 4:
        fs, rhf = 9, 1.4
    elif n_cols <= 7:
        fs, rhf = 8, 1.3
    else:
        fs, rhf = 7, 1.2

    fig_w = 10.5 / 2.54
    fig_h = max(n_rows * 0.4, 1.2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis('off')

    tbl = ax.table(cellText=cell_text, cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.scale(1, rhf)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor('#333333')
        cell.set_linewidth(0.5)
        cell.set_fontsize(fs)
        if row == 0:
            cell.set_facecolor('#e8e8e8')
            cell.set_text_props(weight='bold', fontsize=fs)
        else:
            cell.set_facecolor('#ffffff')
            cell.set_text_props(fontsize=fs)

    plt.tight_layout(pad=0.3)
    key = hashlib.md5('||'.join(lines).encode()).hexdigest()[:8]
    fn = f't_{sid}_{eid:03d}_{key}.png'
    dst = os.path.join(assets_dir, fn)
    fig.savefig(dst, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    return fn, int(fig_w * 200), int(fig_h * 200)


def main():
    src_md = r'C:\MRE\outputs\reviews\13讲_统计调查与直方图复习_课件.md'
    out_json = r'C:\MRE\outputs\reviews\13讲_统计调查与直方图复习_课件.json'
    assets_dir = r'C:\MRE\outputs\reviews\images'

    with open(src_md, encoding='utf-8') as f:
        content = f.read()

    raw = [s.strip() for s in re.split(
        r'<div style="page-break-after: always;"></div>', content) if s.strip()]

    slides = []
    for si, text in enumerate(raw):
        lines = text.split('\n')
        el = []
        y = 54
        eid = 0
        sid = f's{si+1:02d}'
        i = 0
        while i < len(lines):
            ln = lines[i].strip()
            if not ln:
                y += 4
                i += 1
                continue

            # Heading
            if ln.startswith('### '):
                txt = ln[4:]
                eid += 1
                el.append({
                    'id': f'{sid}_e{eid:03d}',
                    'type': 'text',
                    'text': txt,
                    'x': 70, 'y': y,
                    'width': 1100, 'height': 56,
                    'fontSize': 32, 'bold': True,
                    'color': '#1f4e79',
                    'fontFamily': 'Microsoft YaHei'
                })
                y += 62
                i += 1
                continue

            # Image(s) — group consecutive images, arrange horizontally
            if ln.startswith('!['):
                # Gather consecutive image lines
                img_lines = []
                while i < len(lines) and lines[i].strip().startswith('!['):
                    img_lines.append(lines[i].strip())
                    i += 1
                i -= 1  # back one for the outer i+=1

                n_imgs = len(img_lines)
                # Calculate dimensions for each image
                img_specs = []
                for iln in img_lines:
                    m = re.match(r'!\[.*\]\((.+)\)', iln)
                    if not m:
                        continue
                    fn = os.path.basename(m.group(1))
                    full = os.path.join(assets_dir, fn)
                    orig = get_img_size(full)
                    if orig:
                        dw, dh = calc_img_dims(orig[0], orig[1])
                    else:
                        # Fallback: use 25% of slide width with 4:3 ratio
                        dw = int(SLIDE_W * IMG_MAX_W_RATIO)
                        dh = int(dw * 0.75)
                    img_specs.append((fn, dw, dh))

                if not img_specs:
                    i += 1
                    continue

                # Layout horizontally: total width + gaps
                gap = 12
                total_w = sum(s[1] for s in img_specs) + gap * (n_imgs - 1)
                # If total exceeds content width, scale down proportionally
                if total_w > CONTENT_W:
                    scale = (CONTENT_W - gap * (n_imgs - 1)) / (total_w - gap * (n_imgs - 1))
                    img_specs = [(fn, int(dw * scale), int(dh * scale)) for fn, dw, dh in img_specs]
                    total_w = CONTENT_W

                start_x = CONTENT_X + (CONTENT_W - total_w) // 2
                row_h = max(s[2] for s in img_specs)

                cur_x = start_x
                for fn, dw, dh in img_specs:
                    eid += 1
                    el.append({
                        'id': f'{sid}_e{eid:03d}',
                        'type': 'image',
                        'src': fn,
                        'x': cur_x,
                        'y': y + (row_h - dh) // 2,
                        'width': dw,
                        'height': dh
                    })
                    cur_x += dw + gap
                y += row_h + 16
                i += 1
                continue

            # Table → render to image
            if ln.startswith('|') and '|' in ln[1:]:
                rs = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    rs.append(lines[i].strip())
                    i += 1
                i -= 1
                if len(rs) >= 2:
                    fn, iw, ih = render_table_img(rs, assets_dir, sid, eid)
                    if fn:
                        eid += 1
                        w_disp = min(iw, 1100)
                        el.append({
                            'id': f'{sid}_e{eid:03d}',
                            'type': 'image',
                            'src': fn,
                            'x': (1280 - w_disp) // 2,
                            'y': y,
                            'width': w_disp,
                            'height': ih
                        })
                        y += ih + 12
                i += 1
                continue

            # Text paragraph
            para = [ln]
            i += 1
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt or nxt.startswith('#') or nxt.startswith('!') or nxt.startswith('|'):
                    break
                para.append(nxt)
                i += 1
            i -= 1

            txt = ' '.join(para)
            txt = re.sub(r'\*\*(.+?)\*\*', lambda m: m.group(1), txt)
            txt = re.sub(r'\*(.+?)\*', lambda m: m.group(1), txt)
            txt = re.sub(r'`(.+?)`', lambda m: m.group(1), txt)
            txt = resolve_math(txt).strip()

            if txt:
                h = max(40, min(200, len(txt) // 32 * 20 + 40))
                eid += 1
                el.append({
                    'id': f'{sid}_e{eid:03d}',
                    'type': 'text',
                    'text': txt,
                    'x': 70, 'y': y,
                    'width': 1100, 'height': h,
                    'fontSize': 26,
                    'color': '#222222',
                    'fontFamily': 'Microsoft YaHei'
                })
                y += h + 4
            i += 1

        slides.append({'id': sid, 'elements': el})

    doc = {'slides': slides}
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    total = sum(len(s['elements']) for s in slides)
    img_count = sum(1 for s in slides for e in s['elements'] if e['type'] == 'image')
    tbl_count = sum(1 for s in slides for e in s['elements'] if e['type'] == 'image' and e['src'].startswith('t_'))
    print(f'OK: slides={len(slides)} elements={total} images={img_count} (tables={tbl_count})')


if __name__ == '__main__':
    main()
