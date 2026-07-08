import json, os

json_path = r'C:\MRE\outputs\exam-json\24-25期末试卷.json'
img_src_dir = r'C:\MRE\knowledge\images'
output_dir = r'C:\MRE\outputs\exam-json\assets'

with open(json_path, encoding='utf-8') as f:
    doc = json.load(f)

imgs = set()
for s in doc['slides']:
    for e in s['elements']:
        if e.get('type') == 'image':
            imgs.add(os.path.basename(e['src']))

lines = [f'Total images: {len(imgs)}']
for fn in sorted(imgs):
    src = os.path.join(img_src_dir, fn)
    dst = os.path.join(output_dir, fn)
    exists = os.path.exists(src)
    if exists:
        lines.append(f'  OK: {fn}')
    else:
        lines.append(f'  MISS: {fn}')

os.makedirs(output_dir, exist_ok=True)
for fn in sorted(imgs):
    src = os.path.join(img_src_dir, fn)
    dst = os.path.join(output_dir, fn)
    if os.path.exists(src):
        import shutil
        shutil.copy2(src, dst)

result = '\n'.join(lines)
print(result)

# Save to file
with open(os.path.join(output_dir, '..', 'copy_result.txt'), 'w', encoding='utf-8') as f:
    f.write(result)

with open(r'C:\MRE\script_runner_output.txt', 'w', encoding='utf-8') as f:
    f.write(result)
