#!/usr/bin/env python3
"""
HTML课件 → MrePlugin JSON + 逐页PNG截图（JSON 与源 HTML 文件同名）

输出格式遵循 MrePlugin (support/easinote/MRE-Plugin) 规范。
图片存入 assets/ 子目录，JSON 引用相对路径。

用法:
    pip install playwright
    playwright install chromium
    python tools/html_to_seewo.py "outputs/reviews/review-01-02_课件.html"
    python tools/html_to_seewo.py "file.html" --output-dir "exports/"

输出（在 HTML 同级目录）:
    {stem}.json           — MrePlugin 课件描述文件（与 HTML 同名）
    assets/slide_01.png   — 第1页全页截图
    assets/slide_02.png   — 第2页全页截图
    ...
    assets/slide_27.png   — 第27页全页截图

导入方式:
    1. 安装 MrePlugin.enp 到希沃白板5
    2. 在希沃白板5中打开或新建任意课件
    3. 插件菜单 → MRE导入 → 选择生成的 .json 文件
"""

import sys
import os
import json
import argparse
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 希沃白板 16:9 页面坐标系（内部单位）
PAGE_W = 1280
PAGE_H = 720


def screenshot_and_json(html_path: str, output_dir: str = None):
    html_path = Path(html_path).resolve()
    if not html_path.exists():
        print(f"[错误] 文件不存在: {html_path}")
        sys.exit(1)

    if output_dir is None:
        output_dir = html_path.parent
    output_dir = Path(output_dir)

    # assets 子目录
    assets_dir = output_dir / 'assets'
    assets_dir.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        print("[启动] Chromium 无头浏览器...")
        # 优先用环境变量 CHROME_PATH，其次用本地 chrome-headless-shell
        chrome_path = os.environ.get('CHROME_PATH')
        if not chrome_path:
            # 自动探测可能的 chrome 路径（不依赖 playwright 自带浏览器）
            candidates = [
                r'C:\chrome-headless-shell-win64\chrome-headless-shell.exe',
                r'E:\chrome-win64\chrome.exe',
            ]
            for c in candidates:
                if Path(c).exists():
                    chrome_path = c
                    break
        if chrome_path:
            print(f"[浏览器] {chrome_path}")
            browser = p.chromium.launch(headless=True, executable_path=chrome_path)
        else:
            browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={'width': 1960, 'height': 1120},
            device_scale_factor=2
        )

        file_url = html_path.as_uri()
        print(f"[加载] {file_url}")
        page.goto(file_url, wait_until='domcontentloaded', timeout=30000)

        print("[等待] MathJax 渲染...")
        try:
            page.wait_for_function(
                '() => window.MathJax && typeof MathJax.typesetPromise === "function"',
                timeout=20000
            )
            page.evaluate('MathJax.typesetPromise()')
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"  [警告] MathJax: {e}")

        print("[等待] 图片加载...")
        try:
            page.wait_for_load_state('networkidle', timeout=30000)
        except:
            pass
        page.wait_for_timeout(500)
        try:
            page.wait_for_function(
                '() => [...document.querySelectorAll("img")].every(i => i.complete)',
                timeout=15000
            )
        except:
            pass

        # 重置样式
        page.evaluate('''
            var nav = document.querySelector('.nav-dots');
            if (nav) nav.style.display = 'none';
            document.body.style.padding = '0';
            document.body.style.gap = '0';
            document.body.style.background = '#fff';
            document.querySelectorAll('.slide').forEach(function(s) {
                s.style.transform = 'none';
                s.style.marginBottom = '0';
                s.style.boxShadow = 'none';
                s.style.display = 'none';
            });
        ''')

        slide_count = page.evaluate('document.querySelectorAll(".slide").length')
        print(f"[幻灯片] 共 {slide_count} 张\n")

        for i in range(slide_count):
            slide_id = f's{i}'
            page.evaluate(f'''
                document.querySelectorAll('.slide').forEach(function(s) {{
                    s.style.display = 'none';
                }});
                var cur = document.querySelector('#{slide_id}');
                if (cur) cur.style.display = 'block';
            ''')
            page.wait_for_timeout(300)

            filename = f'slide_{i+1:02d}.png'
            filepath = assets_dir / filename

            try:
                el = page.query_selector(f'#{slide_id}')
                if el:
                    el.screenshot(path=str(filepath), type='png')
                    size_kb = filepath.stat().st_size / 1024
                    print(f"  [{i+1:2d}/{slide_count}] {filename}  ({size_kb:.0f} KB)")
                else:
                    print(f"  [{i+1:2d}/{slide_count}] 跳过: #{slide_id} 未找到")
            except Exception as e:
                print(f"  [{i+1:2d}/{slide_count}] 失败: {e}")
                page.screenshot(path=str(filepath), type='png')

        browser.close()

    # ── 生成 JSON（MrePlugin 格式，与 HTML 同名，参考 Models.cs） ──
    json_path = output_dir / (html_path.stem + '.json')

    # 从 HTML 提取标题
    title_text = "统计调查与直方图"
    try:
        from bs4 import BeautifulSoup
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        cover_title = soup.select_one('.cover-title')
        if cover_title:
            title_text = cover_title.get_text(strip=True)
        cover_sub = soup.select_one('.cover-subtitle')
        if cover_sub:
            subtitle = cover_sub.get_text(' ', strip=True)
    except:
        subtitle = "第 01-02 讲 复习"

    slides_json = []
    for i in range(slide_count):
        slides_json.append({
            "id": f"s{i+1:02d}",
            "elements": [
                {
                    "id": f"s{i+1:02d}_img",
                    "type": "image",
                    "src": f"slide_{i+1:02d}.png",
                    "x": 0,
                    "y": 0,
                    "width": PAGE_W,
                    "height": PAGE_H
                }
            ]
        })

    lesson = {
        "slides": slides_json
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)

    print(f"\n[完成] 截图: {assets_dir}/  ({slide_count} 张 PNG)")
    print(f"[完成] JSON: {json_path}")
    print(f"\n[导入] 希沃白板5 → MRE插件 → 导入 {json_path.name}")
    print(f"[结构] {output_dir}/")
    print(f"       ├── {json_path.name}")
    print(f"       └── assets/")
    for i in range(min(slide_count, 5)):
        print(f"           ├── slide_{i+1:02d}.png")
    if slide_count > 5:
        print(f"           │   ...")
        print(f"           └── slide_{slide_count:02d}.png")

    return output_dir, slide_count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTML课件 → MrePlugin JSON + 逐页PNG截图')
    parser.add_argument('input', help='输入 HTML 文件路径')
    parser.add_argument('--output-dir', '-o', default=None,
                        help='输出目录（默认与输入文件同目录）')
    args = parser.parse_args()
    screenshot_and_json(args.input, args.output_dir)
