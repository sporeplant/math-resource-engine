#!/usr/bin/env python3
"""
前置校验脚本

校验教学资源生成前必须满足的前置条件。
通过 → 退出码 0；失败 → 退出码 1 + 明确错误信息。

用法:
    python tools/validate_prerequisites.py <章节号> <lesson_id>           # /lesson-collab 用
    python tools/validate_prerequisites.py <章节号> <lesson_id> --courseware  # /courseware-collab 用

示例:
    python tools/validate_prerequisites.py 22 22.4
    python tools/validate_prerequisites.py 22 22.4 --courseware
"""
import sys
import re
import yaml
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_front_matter(path: Path) -> dict | None:
    """提取 YAML front matter，失败返回 None。"""
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return None
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except Exception:
        return None


def check_solution(chapter: str, lesson_id: str) -> list[str]:
    """校验教材参考解答（必选）。"""
    errors = []
    sol_path = ROOT / 'knowledge' / 'solutions' / f'ch{chapter}' / f'solution-{lesson_id}.md'

    if not sol_path.exists():
        errors.append(f"教材参考解答缺失: {sol_path}")
        return errors

    fm = parse_front_matter(sol_path)
    if fm is None:
        errors.append(f"教材参考解答 YAML front matter 无法解析: {sol_path}")
        return errors

    if fm.get('content_type') != 'textbook_solution':
        errors.append(f"content_type 不是 textbook_solution (实际: {fm.get('content_type')})")
    if str(fm.get('lesson_id', '')).strip() != lesson_id.strip():
        errors.append(f"lesson_id 不匹配 (期望: {lesson_id}, 实际: {fm.get('lesson_id')})")

    if errors:
        errors.insert(0, f"教材参考解答校验失败: {sol_path}")
    return errors


def check_textbook(chapter: str, lesson_id: str) -> list[str]:
    """校验教材原文是否存在（必选）。"""
    errors = []
    tb_dir = ROOT / 'knowledge' / 'textbooks' / f'ch{chapter}'

    if not tb_dir.exists():
        errors.append(f"教材原文目录缺失: {tb_dir}")
        return errors

    # 按 lesson_id 匹配教材原文文件
    prefix = f'textbook-{lesson_id}'
    matches = list(tb_dir.glob(f'{prefix}*.md'))
    if not matches:
        errors.append(f"教材原文缺失: {tb_dir}/{prefix}*.md")
    return errors


def check_standards(chapter: str) -> list[str]:
    """校验课标文件是否存在（必选）。"""
    errors = []
    std_path = ROOT / 'knowledge' / 'standards' / 'curriculum-standards.md'
    if not std_path.exists():
        errors.append(f"课标文件缺失: {std_path}")
    return errors


def check_lesson_plan(chapter: str, lesson_id: str) -> list[str]:
    """校验教学设计是否已审核通过（/courseware-collab 必选）。"""
    errors = []
    lp_path = (ROOT / 'outputs' / 'lessons' / f'ch{chapter}' / lesson_id /
               f'lesson-{lesson_id}-lesson-plan.md')

    if not lp_path.exists():
        errors.append(f"教学设计缺失: {lp_path}")
        return errors

    fm = parse_front_matter(lp_path)
    if fm is None:
        errors.append(f"教学设计 YAML front matter 无法解析: {lp_path}")
        return errors

    if fm.get('review_status') != '审核通过':
        errors.append(f"教学设计 review_status 不是 审核通过 (实际: {fm.get('review_status')})，"
                       "请先完成 /lesson-collab 并人工审核通过")
    return errors


def check_cdn_images(chapter: str, lesson_id: str) -> list[str]:
    """校验教材原文引用的图片是否存在于 knowledge/images/ 且被 git 跟踪。"""
    import subprocess
    errors = []
    img_dir = ROOT / 'knowledge' / 'images'
    tb_dir = ROOT / 'knowledge' / 'textbooks' / f'ch{chapter}'

    if not tb_dir.exists():
        return errors

    prefix = f'textbook-{lesson_id}'
    md_files = list(tb_dir.glob(f'{prefix}*.md'))
    if not md_files:
        return errors

    # 获取 git 跟踪的文件列表（只查一次）
    try:
        result = subprocess.run(
            ['git', 'ls-files', '--', 'knowledge/images/'],
            capture_output=True, text=True, cwd=str(ROOT), timeout=10
        )
        git_tracked = set(Path(f).name for f in result.stdout.splitlines())
    except Exception:
        git_tracked = set()

    missing = []
    untracked = []
    for md_path in md_files:
        text = md_path.read_text(encoding='utf-8')
        for m in re.finditer(r'!\[.*?\]\(([^)]+)\)', text):
            fname = Path(m.group(1)).name
            if not fname:
                continue
            if not (img_dir / fname).exists():
                missing.append(f"  {fname} (来源: {md_path.name})")
            elif git_tracked and fname not in git_tracked:
                untracked.append(f"  {fname}")

    if missing:
        errors.append(f"教材图片缺失 ({len(missing)} 个):")
        errors.extend(missing[:20])
        if len(missing) > 20:
            errors.append(f"  ... 还有 {len(missing) - 20} 个")
    if untracked:
        errors.append(f"图片未提交到 git，CDN 不可用 ({len(untracked)} 个，请 commit 后 push):")
        errors.extend(untracked[:20])
        if len(untracked) > 20:
            errors.append(f"  ... 还有 {len(untracked) - 20} 个")
    return errors


def check_workbook(chapter: str, lesson_id: str) -> list[str]:
    """校验练习册三件套（可选）。"""
    msgs = []
    wb_dir = ROOT / 'knowledge' / 'workbooks'
    wa_dir = ROOT / 'knowledge' / 'workbook-answers'
    wi_dir = ROOT / 'knowledge' / 'workbook-index'

    base = lesson_id.replace('.', '-')
    pattern = f'workbook-{base}'

    wb_files = sorted(wb_dir.glob(f'{pattern}*.md'))
    wa_files = sorted(wa_dir.glob(f'workbook-answer-{base}*.md'))
    wi_files = sorted(wi_dir.glob(f'workbook-index-{base}*.yaml'))

    if not wb_files and not wa_files and not wi_files:
        msgs.append(f"练习册资源未找到 (可选，不阻断): {wb_dir}/{pattern}*.md")
        return msgs

    if not wb_files:
        msgs.append(f"练习册题库缺失 (可选): {wb_dir}/{pattern}*.md")
    if not wa_files:
        msgs.append(f"练习册答案缺失 (可选): {wa_dir}/workbook-answer-{base}*.md")
    if not wi_files:
        msgs.append(f"练习册索引缺失 (可选): {wi_dir}/workbook-index-{base}*.yaml")

    if wb_files and wa_files and wi_files:
        msgs.append(f"练习册三件套完整: {len(wb_files)} 题库 + {len(wa_files)} 答案 + {len(wi_files)} 索引")

    return msgs


def main():
    parser = argparse.ArgumentParser(description='前置校验')
    parser.add_argument('chapter', help='章节号，如 22')
    parser.add_argument('lesson_id', help='课时编号，如 22.4')
    parser.add_argument('--courseware', action='store_true',
                        help='校验 /courseware-collab 所需的前置条件')
    args = parser.parse_args()

    chapter = args.chapter
    lesson_id = args.lesson_id

    all_errors = []
    all_infos = []

    # ========== 共同必选项 ==========
    errors = check_solution(chapter, lesson_id)
    all_errors.extend(errors)

    errors = check_textbook(chapter, lesson_id)
    all_errors.extend(errors)

    errors = check_standards(chapter)
    all_errors.extend(errors)

    errors = check_cdn_images(chapter, lesson_id)
    all_errors.extend(errors)

    # ========== /courseware-collab 专有 ==========
    if args.courseware:
        errors = check_lesson_plan(chapter, lesson_id)
        all_errors.extend(errors)

    # ========== 可选项 ==========
    infos = check_workbook(chapter, lesson_id)
    all_infos.extend(infos)

    # ========== 输出 ==========
    for info in all_infos:
        print(f"[信息] {info}")
    for err in all_errors:
        print(f"[错误] {err}")

    if all_errors:
        cmd = '/courseware-collab' if args.courseware else '/lesson-collab'
        print(f"\n[终止] 前置校验未通过。请先修复上述错误后重新发起 {cmd}。")
        if any("教材参考解答缺失" in e for e in all_errors):
            print("[提示] 缺失教材参考解答时，请先执行 /教材问题解答 {课时}")
        if any("教学设计" in e and "缺失" in e for e in all_errors):
            print("[提示] 缺失教学设计时，请先执行 /lesson-collab 并人工审核通过")
        sys.exit(1)

    print("\n[通过] 前置校验全部通过。")


if __name__ == '__main__':
    main()
