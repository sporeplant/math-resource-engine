import os, shutil, json

json_path = r'C:\MRE\outputs\exam-json\24-25期末试卷.json'
img_src_dir = r'C:\MRE\knowledge\images'
img_dst_dir = r'C:\MRE\outputs\exam-json\assets'

with open(json_path, encoding='utf-8') as f:
    doc = json.load(f)

imgs = set()
for s in doc['slides']:
    for e in s['elements']:
        if e.get('type') == 'image':
            imgs.add(os.path.basename(e['src']))

os.makedirs(img_dst_dir, exist_ok=True)

copied = 0
missing = []
for fn in sorted(imgs):
    src = os.path.join(img_src_dir, fn)
    dst = os.path.join(img_dst_dir, fn)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        copied += 1
    else:
        missing.append(fn)

print(f'Total images: {len(imgs)}')
print(f'Copied: {copied}')
print(f'Missing: {len(missing)}')
for m in missing:
    print(f'  MISS: {m}')
for fn in sorted(imgs):
    if fn not in missing:
        print(f'  OK: {fn}')
