#!/usr/bin/env python3
"""
HTML课件 → 逐页PNG截图（Playwright）

用法:
    python tools/html_screenshot.py "outputs/reviews/review-01-02_课件.html"

输出:
    outputs/reviews/slides/slide_01.png ~ slide_27.png

依赖:
    pip install playwright
    playwright install chromium
"""

import sys
import os
from pathlib import Path

# UTF-8 输出
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def screenshot_html(html_path: str, output_dir: str = None):
    html_path = Path(html_path).resolve()
    if not html_path.exists():
        print(f"[错误] 文件不存在: {html_path}")
        sys.exit(1)

    if output_dir is None:
        output_dir = html_path.parent / 'slides'
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[读取] {html_path}")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        print("[启动] Chromium 无头浏览器...")
        # 优先用环境变量 CHROME_PATH，其次用本地 chrome
        chrome_path = os.environ.get('CHROME_PATH')
        if not chrome_path:
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
        # viewport 稍宽以消除 body padding 对缩放的干扰
        page = browser.new_page(
            viewport={'width': 1960, 'height': 1120},
            device_scale_factor=1
        )

        # 使用 file:// 协议加载
        file_url = html_path.as_uri()
        print(f"[加载] {file_url}")
        page.goto(file_url, wait_until='domcontentloaded')

        # ── 等待关键资源 ──
        print("[等待] MathJax 渲染...")
        try:
            # MathJax 3 异步渲染
            page.wait_for_function(
                '() => window.MathJax && typeof MathJax.typesetPromise === "function"',
                timeout=15000
            )
            page.evaluate('MathJax.typesetPromise()')
        except Exception as e:
            print(f"  [警告] MathJax 等待超时: {e}")

        print("[等待] 图片加载...")
        page.wait_for_load_state('networkidle', timeout=30000)

        # 额外等待：让所有 img 完成加载
        page.wait_for_function(
            '() => Array.from(document.querySelectorAll("img")).every(i => i.complete)',
            timeout=15000
        )

        # ── 重置样式：取消 body padding/gap、移除缩放 ──
        print("[准备] 重置页面样式...")
        page.evaluate('''
            // 隐藏导航圆点
            var nav = document.querySelector('.nav-dots');
            if (nav) nav.style.display = 'none';

            // 取消body的padding和gap
            document.body.style.padding = '0';
            document.body.style.gap = '0';
            document.body.style.background = '#fff';

            // 重置所有slide的transform和margin
            document.querySelectorAll('.slide').forEach(function(s) {
                s.style.transform = 'none';
                s.style.marginBottom = '0';
                s.style.boxShadow = 'none';
            });
        ''')

        # ── 获取幻灯片总数 ──
        slide_count = page.evaluate('document.querySelectorAll(".slide").length')
        print(f"[幻灯片] 共 {slide_count} 张，开始截图...\n")

        # ── 逐张截图 ──
        for i in range(slide_count):
            slide_id = f's{i}'
            el = page.query_selector(f'#{slide_id}')
            if el is None:
                print(f"  [跳过] #{slide_id} 未找到")
                continue

            filename = f'slide_{i+1:02d}.png'
            filepath = output_dir / filename

            # 截图元素本身（1920×1080）
            el.screenshot(path=str(filepath), type='png')
            size_kb = filepath.stat().st_size / 1024
            print(f"  [{i+1:2d}/{slide_count}] {filename}  ({size_kb:.0f} KB)")

        browser.close()

    print(f"\n[完成] 截图已保存到: {output_dir}")
    print(f"[总数] {slide_count} 张 PNG 图片")
    return output_dir, slide_count


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python tools/html_screenshot.py <HTML文件路径> [输出目录]")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    screenshot_html(src, dst)
