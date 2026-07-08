import json, os

json_path = r'C:\MRE\outputs\exam-json\24-25期末试卷.json'
img_src_dir = r'C:\MRE\knowledge\images'

with open(json_path, encoding='utf-8') as f:
    doc = json.load(f)

imgs = set()
for s in doc['slides']:
    for e in s['elements']:
        if e.get('type') == 'image':
            imgs.add(os.path.basename(e['src']))

lines = []
lines.append(f'Total images: {len(imgs)}')
for fn in sorted(imgs):
    src = os.path.join(img_src_dir, fn)
    if os.path.exists(src):
        lines.append(f'  OK: {fn}')
    else:
        lines.append(f'  MISS: {fn}')

with open(r'C:\MRE\script_output.txt', 'w', encoding='utf-8') as out:
    out.write('\n'.join(lines))
