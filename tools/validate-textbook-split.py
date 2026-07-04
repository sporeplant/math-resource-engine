"""验证教材拆分结果的完整性和一致性。

检查项：
  1. YAML front matter — 六个字段完整且有效
  2. 图片引用 — 全部使用 CDN 格式，无相对路径
  3. 图片文件 — 每个引用的图片在 knowledge/images/ 下存在
  4. 内容结构 — 以课时标题开头，无孤立内容
  5. 文件命名 — 符合 textbook-{章节}.{小节}-{课时}.md 规则

用法:
    python tools/validate-textbook-split.py <目标目录或文件>
    python tools/validate-textbook-split.py knowledge/textbooks/ch15/
    python tools/validate-textbook-split.py knowledge/textbooks/ch15/textbook-15.1-1.md
"""

import argparse
import os
import re
import sys


CDN_PREFIX = "https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/"

REQUIRED_FIELDS = [
    "content_type",
    "textbook_version",
    "semester",
    "chapter_name",
    "section_name",
    "lesson_id",
]

FILENAME_RE = re.compile(r"^textbook-(\d+)\.(\d+|ch\d+)-(.+)\.md$")

IMG_CDN_RE = re.compile(
    r"!\[.*?\]\(" + re.escape(CDN_PREFIX) + r"([a-f0-9]+\.jpg)\)"
)
IMG_HTML_CDN_RE = re.compile(
    r'src=["\']' + re.escape(CDN_PREFIX) + r'([a-f0-9]+\.jpg)["\']'
)
IMG_RELATIVE_RE = re.compile(r'(?:!\[.*?\]\(|src=["\'])(?:\.\.?/)?images/([a-f0-9]+\.jpg)')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(PROJECT_ROOT, "knowledge", "images")


class ValidationError(Exception):
    pass


def error(msg):
    raise ValidationError(msg)


def validate_front_matter(content, filepath):
    """Check YAML front matter has all required fields."""
    if not content.startswith("---"):
        error("缺少 YAML front matter")

    end = content.find("---", 3)
    if end == -1:
        error("YAML front matter 未闭合")

    fm_text = content[3:end]
    fm = {}
    for line in fm_text.strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")

    for field in REQUIRED_FIELDS:
        if field not in fm:
            error(f"缺少字段: {field}")

    if fm.get("content_type") != "textbook_original":
        error(f"content_type 应为 textbook_original，实际: {fm.get('content_type')}")

    if fm.get("textbook_version") != "JJ2022":
        error(f"textbook_version 应为 JJ2022，实际: {fm.get('textbook_version')}")

    if not fm.get("semester"):
        error("semester 为空")


def validate_images(content, filepath):
    """Check all images use CDN format and referenced files exist."""
    # Must have CDN references (for files with images)
    cdn_hashes = set()
    for m in IMG_CDN_RE.finditer(content):
        cdn_hashes.add(m.group(1))
    for m in IMG_HTML_CDN_RE.finditer(content):
        cdn_hashes.add(m.group(1))

    # Must NOT have relative image references
    relative = IMG_RELATIVE_RE.findall(content)
    if relative:
        error(f"存在相对路径图片引用: {relative[0]}...")

    # Check each image file exists
    for h in cdn_hashes:
        img_path = os.path.join(IMAGES_DIR, h)
        if not os.path.isfile(img_path):
            error(f"图片文件不存在: {h}")


def validate_content_structure(content, filepath):
    """Check content begins with a proper heading."""
    # Find content after YAML front matter
    end = content.find("---", 3)
    if end == -1:
        return
    body = content[end + 3:].lstrip()

    if not body.startswith("## ") and not body.startswith("# "):
        error("正文未以标题开头")


def validate_filename(filepath):
    """Check filename follows convention."""
    basename = os.path.basename(filepath)
    if not FILENAME_RE.match(basename):
        error(f"文件名不符合命名规则: {basename}")


def validate_file(filepath):
    """Run all checks on a single file. Returns list of error messages (empty = ok)."""
    errors = []
    checks = [
        ("文件名", validate_filename),
        ("YAML front matter", validate_front_matter),
        ("图片引用", validate_images),
        ("内容结构", validate_content_structure),
    ]

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    for check_name, check_fn in checks:
        try:
            if check_fn is validate_filename:
                check_fn(filepath)
            else:
                check_fn(content, filepath)
        except ValidationError as e:
            errors.append(f"  [{check_name}] {e}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="验证教材拆分结果")
    parser.add_argument("target", help="目标目录或文件")
    parser.add_argument("--quiet", "-q", action="store_true", help="仅输出错误")
    args = parser.parse_args()

    target = os.path.abspath(args.target)

    if os.path.isfile(target):
        if not target.endswith(".md"):
            print("错误：目标不是 .md 文件", file=sys.stderr)
            sys.exit(1)
        files = [target]
    elif os.path.isdir(target):
        files = sorted(f for f in [
            os.path.join(target, fn) for fn in os.listdir(target)
        ] if f.endswith(".md") and os.path.isfile(f))
        if not files:
            print(f"目标目录中未找到 .md 文件: {target}")
            sys.exit(0)
    else:
        print(f"目标不存在: {target}", file=sys.stderr)
        sys.exit(1)

    total_errors = 0
    total_ok = 0

    for filepath in files:
        basename = os.path.basename(filepath)
        errors = validate_file(filepath)
        if errors:
            total_errors += len(errors)
            print(f"FAIL {basename}")
            for e in errors:
                print(e)
        else:
            total_ok += 1
            if not args.quiet:
                print(f"PASS {basename}")

    print()
    print(f"结果: {total_ok} 通过, {total_errors} 个错误")
    if total_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
