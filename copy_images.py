import json, os, shutil

# 读取 JSON
with open('outputs/exam-json/24-25期末试卷.json', 'r') as f:
    doc = json.load(f)

# 收集图片
img_files = set()
for slide in doc['slides']:
    for elem in slide['elements']:
        if elem['type'] == 'image':
            src_path = elem['src']
            if src_path.startswith('assets/'):
                img_files.add(src_path[7:])

print(f'需要复制 {len(img_files)} 张图片')

# 创建目标目录
dst_dir = 'outputs/exam-json/assets'
os.makedirs(dst_dir, exist_ok=True)

# 复制图片
missing = []
for fname in sorted(img_files):
    src = os.path.join('knowledge/images', fname)
    dst = os.path.join(dst_dir, fname)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f'OK: {fname}')
    else:
        print(f'MISSING: {fname}')
        missing.append(fname)

print(f'完成。成功复制 {len(img_files)-len(missing)} 张，缺失 {len(missing)} 张')
