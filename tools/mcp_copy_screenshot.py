#!/usr/bin/env python3
"""
MCP辅助：调用chrome-devtools MCP的截图功能，批量搬运临时文件。
此脚本配合chrome-devtools MCP server使用，不是独立运行的。
"""

# 这个脚本不需要独立运行，MCP截图到临时目录后，
# 我们通过bash循环复制。

import subprocess
import os
import shutil
from pathlib import Path

TMP_BASE = Path(os.environ.get('LOCALAPPDATA', '')) / 'reasonix/mcp-state'
OUTPUT_DIR = Path('C:/MRE/outputs/reviews/slides')

# 找到最新的 chrome-devtools 临时目录
def find_latest_tmp():
    candidates = []
    for root in TMP_BASE.glob('*/chrome-devtools/tmp/chrome-devtools-mcp-*'):
        if root.is_dir():
            candidates.append((root.stat().st_mtime, root))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]

def copy_screenshot(index: int):
    tmp_dir = find_latest_tmp()
    if not tmp_dir:
        print(f"  [错误] 找不到临时目录")
        return False
    src = tmp_dir / 'screenshot.png'
    if not src.exists():
        print(f"  [错误] 临时文件不存在: {src}")
        return False
    dst = OUTPUT_DIR / f'slide_{index:02d}.png'
    shutil.copy2(src, dst)
    size_kb = dst.stat().st_size / 1024
    print(f"  [{index:2d}] {dst.name} ({size_kb:.0f} KB)")
    return True

if __name__ == '__main__':
    import sys
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    copy_screenshot(idx)
