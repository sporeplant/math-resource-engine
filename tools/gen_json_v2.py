"""将 courseware.md 转换为 MRE lesson.json（v2 — LaTeX 处理版）"""

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

PAGE_W, MARGIN = 1120, 70
TITLE_FS, BODY_FS = 28, 22
TITLE_H, BODY_H = 56, 44
COLOR_TITLE = "#12355b"
COLOR_SUB = "#1f4e79"
COLOR_BODY = "#222222"
COLOR_DIM = "#333333"

LATEX_MAP = [
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


def clean(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)

    def _rep(m):
        inner = m.group(1)
        for pat, rep in LATEX_MAP:
            inner = re.sub(pat, rep, inner)
        return inner.strip()

    text = re.sub(r"\$\$(.+?)\$\$", _rep, text)
    text = re.sub(r"\$(.+?)\$", _rep, text)
    text = re.sub(r"[{}]", "", text)
    return text.strip()


def cpi(src_rel):
    fname = os.path.basename(src_rel)
    dest = os.path.join(ASSETS_DIR, fname)
    if os.path.exists(dest):
        return fname
    for c in [os.path.join(MD_DIR, src_rel), os.path.join(KNOWLEDGE_IMAGES, fname)]:
        if os.path.exists(c):
            try:
                shutil.copy2(c, dest)
            except:
                pass
            return fname
    return None


def process_slide(si, raw):
    elements, lines, y, eid = [], raw.split("\n"), 54, 0
    sid = f"21.7_s{si + 1:02d}"

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
        copied = cpi(src_rel)
        if copied:
            eid += 1
            elements.append(
                {
                    "id": f"{sid}_e{eid:03d}",
                    "type": "image",
                    "src": copied,
                    "x": (1280 - w) // 2,
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
        if re.match(r"^#\s", line):
            add_text(re.sub(r"^#+\s*", "", line), fs=32, bold=True, color=COLOR_TITLE)
        elif re.match(r"^##\s", line):
            add_text(
                re.sub(r"^##\s+", "", line), fs=TITLE_FS, bold=True, color=COLOR_TITLE
            )
        elif re.match(r"^###\s", line):
            add_text(re.sub(r"^###\s+", "", line), fs=25, bold=True, color=COLOR_SUB)
        elif re.match(r"^!\[.*\]\((.+)\)", line):
            m = re.match(r"^!\[.*\]\((.+)\)", line)
            add_image(m.group(1))
        elif line == "```mermaid":
            blocks = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                blocks.append(lines[i].rstrip())
                i += 1
            i += 1
            add_text("📊 " + " | ".join(blocks), fs=20, color=COLOR_DIM)
        elif line in ("---", "***", "___"):
            y += 8
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                r = lines[i].strip()
                if not re.match(r"^\|[: \-\|]+\|$", r):
                    cells = [c.strip() for c in r.split("|") if c.strip()]
                    rows.append("  ".join(cells))
                i += 1
            i -= 1
            for tr in rows:
                add_text(tr, fs=20, color=COLOR_DIM)
        else:
            para = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not re.match(r"^[#!|`\-]", lines[i].strip())
                and not lines[i].strip().startswith("```")
                and lines[i].strip() not in ("---", "***", "___")
            ):
                para.append(lines[i].strip())
                i += 1
            i -= 1
            text = " ".join(para)
            if len(text) > 3:
                add_text(text)
        i += 1

    return {"id": sid, "elements": elements}


slides_out = [process_slide(si, raw) for si, raw in enumerate(raw_slides)]

# 移除 frontmatter 空白页
slides_out = [
    s
    for s in slides_out
    if s["elements"]
    and any(
        e.get("text", "").strip()
        and not re.match(
            r"^(title:|source:|date:|chapter:|section:|lesson:|type:)",
            e.get("text", ""),
        )
        for e in s["elements"]
    )
]
for i, s in enumerate(slides_out):
    s["id"] = f"21.7_s{i + 1:02d}"

doc = {"slides": slides_out}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

total = sum(len(s["elements"]) for s in slides_out)
totimg = sum(1 for s in slides_out for e in s["elements"] if e["type"] == "image")
print(f"OK slides={len(slides_out)} text={total - totimg} image={totimg} total={total}")

# 抽查 LaTeX
for s in slides_out:
    for e in s["elements"]:
        t = e.get("text", "")
        if sum(1 for ch in "∠°△⊥·×" if ch in t) >= 2:
            print(f"  LaTeX→Unicode: {t[:90]}")
            break
