import os, shutil, json

BASE = r"C:\MRE\outputs\exam-json"
JSON_PATH = os.path.join(BASE, "24-25期末试卷.json")
ASSETS_DIR = os.path.join(BASE, "assets")
IMG_SRC_DIR = r"C:\MRE\knowledge\images"

os.makedirs(ASSETS_DIR, exist_ok=True)

with open(JSON_PATH, encoding="utf-8") as f:
    doc = json.load(f)

imgs = set()
for s in doc["slides"]:
    for e in s["elements"]:
        if e.get("type") == "image":
            imgs.add(os.path.basename(e["src"]))

result_lines = []
copied, missing = 0, []
for fn in sorted(imgs):
    src = os.path.join(IMG_SRC_DIR, fn)
    dst = os.path.join(ASSETS_DIR, fn)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        copied += 1
        result_lines.append(f"OK: {fn}")
    else:
        missing.append(fn)
        result_lines.append(f"MISS: {fn}")

result_lines.append(f"\nCopied: {copied}, Missing: {len(missing)}")
for m in missing:
    result_lines.append(f"  MISSING: {m}")

result = "\n".join(result_lines)
print(result)

# Also write to a log file
with open(os.path.join(BASE, "copy_result.txt"), "w", encoding="utf-8") as f:
    f.write(result)
