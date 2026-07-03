"""将 courseware.md 转换为 MRE lesson.json"""

import json
import os
import re
import shutil

MD_PATH = r"C:\Users\Administrator\OneDrive\MRE_Data\outputs\c21\21.7-courseware.md"
OUT_JSON = "support/easinote/MRE-Plugin/21.7-lesson.json"
ASSETS_DIR = "support/easinote/MRE-Plugin/assets"
KNOWLEDGE_IMAGES = "knowledge/images"
MD_DIR = os.path.dirname(MD_PATH)
os.makedirs(ASSETS_DIR, exist_ok=True)

with open(MD_PATH, "r", encoding="utf-8") as f:
    md = f.read()

raw_slides = re.split(r'<div style="page-break-after: always;"></div>', md)
raw_slides = [s.strip() for s in raw_slides if s.strip()]

PAGE_W = 1120
MARGIN = 70
TITLE_FS = 28
TITLE_H = 56
BODY_FS = 22
BODY_H = 44
COLOR_TITLE = "#12355b"
COLOR_SUB = "#1f4e79"
COLOR_BODY = "#222222"
COLOR_DIM = "#333333"


# LaTeX → Unicode 映射表
_LATEX_UNICODE = [
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
    (r"\\sim", "∼"),
    (r"\\because", "∵"),
    (r"\\therefore", "∴"),
    (r"\\sqrt\{([^}]+)\}", r"√(\1)"),
    (r"\\frac\{([^}]+)\}\{([^}]+)\}", r"\1/\2"),
    (r"\\text\{([^}]*)\}", r"\1"),
    (r"\\qquad", ""),
    (r"\\quad", " "),
    (r"\^{\circ}", "°"),
    (r"\^\{([^}]+)\}", r"\1"),  # 上标保留内容
    (r"_\{([^}]+)\}", r"_\1"),  # 下标保留下划线
    (r"\\[a-zA-Z]+", ""),  # 其他未知命令清掉
]


def clean(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    # 处理 $$ 块 → 保留内部内容，去掉 $$ 标记
    text = re.sub(r"\$\$", "", text)

    # 处理 $...$ 块 → 剥离 $ 并做 Unicode 替换
    def _replace_math(m):
        inner = m.group(1)
        for pat, rep in _LATEX_UNICODE:
            inner = re.sub(pat, rep, inner)
        return inner.strip()

    text = re.sub(r"\$(.+?)\$", _replace_math, text)
    # 清理多余的 { }
    text = re.sub(r"[{}]", "", text)
    return text.strip()


def copy_image(src_rel):
    fname = os.path.basename(src_rel)
    candidates = [
        os.path.join(MD_DIR, src_rel),
        os.path.join(KNOWLEDGE_IMAGES, fname),
    ]
    for c in candidates:
        if os.path.exists(c):
            dest = os.path.join(ASSETS_DIR, fname)
            shutil.copy2(c, dest)
            return fname
    return None


slides_out = []


def process_slide(si, raw):
    elements = []
    lines = raw.split("\n")
    y = 54
    sid = f"21.7_s{si + 1:02d}"
    eid = 0

    def add_text(text, fs=BODY_FS, bold=False, color=COLOR_BODY, extra_h=0):
        nonlocal y, eid
        text = clean(text)
        if not text:
            return
        eid += 1
        h = max(BODY_H, len(text) // 28 * (BODY_H + 2) + BODY_H)
        elements.append(
            {
                "id": f"{sid}_e{eid:03d}",
                "type": "text",
                "text": text,
                "x": MARGIN,
                "y": y,
                "width": PAGE_W,
                "height": h,
                "fontSize": fs,
                "bold": bold,
                "color": color,
            }
        )
        y += h + 4 + extra_h

    def add_image(src_rel, w=720, h=420):
        nonlocal y, eid
        copied = copy_image(src_rel)
        if copied:
            eid += 1
            x = (1280 - w) // 2
            elements.append(
                {
                    "id": f"{sid}_e{eid:03d}",
                    "type": "image",
                    "src": copied,
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                }
            )
            y += h + 12

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            y += 4
            i += 1
            continue

        # 标题
        if re.match(r"^#\s", line):
            add_text(re.sub(r"^#+\s*", "", line), fs=32, bold=True, color=COLOR_TITLE)
        elif re.match(r"^##\s", line):
            add_text(
                re.sub(r"^##\s+", "", line), fs=TITLE_FS, bold=True, color=COLOR_TITLE
            )
        elif re.match(r"^###\s", line):
            add_text(re.sub(r"^###\s+", "", line), fs=25, bold=True, color=COLOR_SUB)

        # 图片
        elif re.match(r"^!\[.*\]\((.+)\)", line):
            m = re.match(r"^!\[.*\]\((.+)\)", line)
            add_image(m.group(1))

        # mermaid 代码块
        elif line == "```mermaid":
            blocks = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                blocks.append(lines[i].rstrip())
                i += 1
            i += 1
            add_text("📊 " + " | ".join(blocks), fs=20, color=COLOR_DIM)

        # 水平线
        elif line in ("---", "***", "___"):
            y += 8

        # 表格
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                r = lines[i].strip()
                if not re.match(r"^\|[:\-\s|]+\|$", r):
                    cells = [c.strip() for c in r.split("|") if c.strip()]
                    rows.append("  ".join(cells))
                i += 1
            i -= 1  # will increment at loop end
            for tr in rows:
                add_text(tr, fs=20, color=COLOR_DIM)

        # 普通段落
        else:
            para = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not re.match(r"^[#!|`\-]", lines[i].strip())
                and not lines[i].strip().startswith("```")
                and not lines[i].strip() in ("---", "***", "___")
            ):
                para.append(lines[i].strip())
                i += 1
            i -= 1
            text = " ".join(para)
            # 跳过纯 emoji/短注释行
            if len(text) > 3:
                add_text(text)

        i += 1

    slides_out.append({"id": sid, "elements": elements})


for si, raw in enumerate(raw_slides):
    process_slide(si, raw)

doc = {"slides": slides_out}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

total_el = sum(len(s["elements"]) for s in slides_out)
total_img = sum(1 for s in slides_out for e in s["elements"] if e["type"] == "image")
total_text = sum(1 for s in slides_out for e in s["elements"] if e["type"] == "text")
print(
    f"✅ slides={len(slides_out)}  text={total_text}  image={total_img}  total={total_el}"
)
for s in slides_out:
    imgs = [e["src"] for e in s["elements"] if e.get("type") == "image"]
    if imgs:
        print(f"  {s['id']}: images={imgs}")
