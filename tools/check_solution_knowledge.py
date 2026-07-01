"""检查教材参考解答是否使用了本章核心知识点。

用法:
    python tools/check_solution_knowledge.py              # 检查所有章节
    python tools/check_solution_knowledge.py --chapter 12 # 只检查第12章
    python tools/check_solution_knowledge.py --strict     # 同时检查 required_methods
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


def find_project_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here, *here.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / "knowledge").is_dir():
            return candidate
    return here.parent


def load_knowledge_points(root: Path) -> dict[int, dict]:
    config_path = root / "knowledge" / "chapter-knowledge-points.yaml"
    if not config_path.exists():
        print(f"ERROR: {config_path} not found", file=sys.stderr)
        sys.exit(1)
    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return {int(k): v for k, v in raw.items()}


def find_solution_files(root: Path, chapter: int | None = None) -> list[Path]:
    solutions_dir = root / "knowledge" / "solutions"
    if not solutions_dir.is_dir():
        return []
    results = []
    for fp in sorted(solutions_dir.glob("solution-*.md")):
        name = fp.stem.replace("solution-", "")
        if chapter is not None:
            prefix = str(chapter) + "."
            ch_prefix = f"ch{chapter}-"
            if not (name.startswith(prefix) or name.startswith(ch_prefix)):
                continue
        results.append(fp)
    return results


def extract_answers(text: str) -> list[tuple[str, str]]:
    """提取每道题的 question_id 和参考解答文本。"""
    answers = []
    blocks = re.split(r"(?=###\s)", text)
    for block in blocks:
        qid_match = re.search(r'question_id:\s*["\']?([^"\'}\n]+)', block)
        if not qid_match:
            continue
        qid = qid_match.group(1).strip()
        ans_match = re.search(
            r"\*\*参考解答\*\*[：:]\s*([\s\S]*?)(?=\n###\s|\n##\s|\Z)", block
        )
        if ans_match:
            answers.append((qid, ans_match.group(1).strip()))
    return answers


def check_answer(
    answer_text: str,
    key_terms: list[str],
    required_methods: list[str] | None = None,
    strict: bool = False,
) -> tuple[list[str], list[str]]:
    """返回 (命中的关键词, 缺失的必选方法词)。"""
    hit_terms = [t for t in key_terms if t in answer_text]
    missing_methods = []
    if strict and required_methods:
        missing_methods = [m for m in required_methods if m not in answer_text]
    return hit_terms, missing_methods


def main() -> None:
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="检查答案库是否使用本章知识点")
    parser.add_argument("--chapter", type=int, default=None, help="只检查指定章节")
    parser.add_argument(
        "--strict", action="store_true", help="同时检查 required_methods 是否出现"
    )
    args = parser.parse_args()

    root = find_project_root()
    kp = load_knowledge_points(root)

    chapters = [args.chapter] if args.chapter else sorted(kp.keys())
    total_issues = 0

    for ch in chapters:
        if ch not in kp:
            print(f"⚠️  第{ch}章未在注册表中登记，跳过")
            continue
        info = kp[ch]
        ch_name = info.get("name", "")
        key_terms = info.get("key_terms", [])
        required_methods = info.get("required_methods", [])

        files = find_solution_files(root, ch)
        if not files:
            print(f"\n📂 第{ch}章（{ch_name}）：无答案库文件")
            continue

        print(f"\n📂 第{ch}章（{ch_name}）— 检查 {len(files)} 个文件")
        print(f"   关键词: {', '.join(key_terms)}")
        if required_methods:
            print(f"   必选方法: {', '.join(required_methods)}")
        print("─" * 60)

        ch_issues = 0
        for fp in files:
            text = fp.read_text(encoding="utf-8")
            answers = extract_answers(text)
            file_issues = []
            for qid, ans_text in answers:
                hits, missing = check_answer(
                    ans_text, key_terms, required_methods, args.strict
                )
                if not hits:
                    file_issues.append(
                        f"  ❌ {qid}: 未命中任何本章关键词"
                    )
                elif args.strict and missing:
                    file_issues.append(
                        f"  ⚠️  {qid}: 命中 {hits}，但缺少必选方法 {missing}"
                    )
            if file_issues:
                print(f"\n  📄 {fp.name}")
                for issue in file_issues:
                    print(issue)
                ch_issues += len(file_issues)
            else:
                print(f"  ✅ {fp.name}: {len(answers)} 题全部命中")

        if ch_issues == 0:
            print(f"\n  ✅ 第{ch}章全部通过")
        else:
            print(f"\n  ⚠️  第{ch}章有 {ch_issues} 题疑似偏离本章知识点")
        total_issues += ch_issues

    print("\n" + "═" * 60)
    if total_issues == 0:
        print("✅ 全部章节检查通过")
    else:
        print(f"⚠️  共 {total_issues} 题疑似偏离，请人工复核")
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
