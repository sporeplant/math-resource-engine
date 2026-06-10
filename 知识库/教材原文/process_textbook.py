#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理教材原文文件：
1. 完善元信息
2. 清理 [TOC]、--- 分隔符、重复标题等多余内容
"""

import os
import re
import yaml
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Administrator\OneDrive\math-resource-engine\知识库\教材原文")

def parse_filename(filename):
    """从文件名解析章节信息"""
    # 移除 "教材原文_" 前缀和 ".md" 后缀
    name = filename.replace("教材原文_", "").replace(".md", "")

    result = {
        "chapter": "",
        "chapter_num": "",
        "topic": "",
        "lesson_type": "教材原文",
        "grade": "八年级",
    }

    # 处理 "第XX章" 格式
    chapter_match = re.match(r"^(第(\d+)章)_(.+)$", name)
    if chapter_match:
        result["chapter"] = chapter_match.group(1)
        result["chapter_num"] = chapter_match.group(1)
        result["topic"] = chapter_match.group(3)
        return result

    # 处理 "XX.XX" 或 "XX.XX.X" 格式 (如 22.1, 21.3.1)
    # 注意：可能没有下划线，如 "21.9数学活动"
    section_match = re.match(r"^(\d+\.\d+(?:\.\d+)?)_?(.+)$", name)
    if section_match:
        num = section_match.group(1)
        topic = section_match.group(2)

        # 提取章节号前缀
        chapter_prefix = num.split(".")[0]
        result["chapter"] = f"第{chapter_prefix}章"
        result["chapter_num"] = num
        result["topic"] = topic
        return result

    # 处理特殊情况如 "21.0第21章_四边形起始页"
    special_match = re.match(r"^(\d+\.\d+)第(\d+)章_(.+)$", name)
    if special_match:
        result["chapter_num"] = special_match.group(1)
        result["chapter"] = f"第{special_match.group(2)}章"
        result["topic"] = special_match.group(3)
        return result

    # 其他情况，整个作为 topic
    result["topic"] = name
    return result

def clean_content(content):
    """清理多余内容"""
    lines = content.split("\n")
    cleaned_lines = []
    prev_line = ""
    i = 0

    while i < len(lines):
        line = lines[i]

        # 跳过 [TOC]
        if line.strip() == "[TOC]":
            i += 1
            continue

        # 跳过提取信息行
        if line.strip().startswith("> 来源：") or \
           line.strip().startswith("> 提取日期：") or \
           line.strip().startswith("> 提取工具："):
            i += 1
            continue

        # 跳过独立的 --- 分隔符（如果在开头几行）
        if line.strip() == "---" and i < 10:
            i += 1
            continue

        # 跳过 BOM
        if line.startswith("\ufeff"):
            line = line[1:]

        # 跳过重复的标题行
        if line.startswith("# ") and line == prev_line:
            i += 1
            continue

        # 跳过连续的空行（超过2个）
        if line.strip() == "":
            # 保留最多2个连续空行
            if cleaned_lines and cleaned_lines[-1].strip() == "":
                if len(cleaned_lines) > 1 and cleaned_lines[-2].strip() == "":
                    i += 1
                    continue
            cleaned_lines.append(line)
            i += 1
            continue

        cleaned_lines.append(line)
        if line.startswith("#"):
            prev_line = line

        i += 1

    # 确保清理末尾空行
    while cleaned_lines and cleaned_lines[-1].strip() == "":
        cleaned_lines.pop()

    return "\n".join(cleaned_lines).strip()

def process_file(filepath):
    """处理单个文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 移除 BOM 字符
    if content.startswith("\ufeff"):
        content = content[1:]

    # 分割 YAML frontmatter 和正文
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_part = parts[1]
            body_part = parts[2]
            # 解析现有元信息
            try:
                meta = yaml.safe_load(yaml_part)
                if meta is None:
                    meta = {}
            except:
                meta = {}
            body_part = body_part.lstrip("\n")
        else:
            meta = {}
            body_part = content
    else:
        meta = {}
        body_part = content

    # 从文件名解析信息
    filename = filepath.name
    parsed = parse_filename(filename)

    # 更新元信息
    meta["title"] = parsed.get("topic", meta.get("title", ""))
    meta["source"] = "冀教版八年级下数学教材"
    meta["date"] = "2026-05-17"
    meta["chapter"] = parsed.get("chapter", meta.get("chapter", ""))
    meta["chapter_num"] = parsed.get("chapter_num", meta.get("chapter_num", ""))
    meta["grade"] = "八年级"
    meta["type"] = "教材原文"
    meta["lesson_type"] = parsed.get("lesson_type", "教材原文")

    # 清理 tags
    tags = set(["教材", "数学"])
    if meta.get("chapter"):
        tags.add(meta["chapter"])
    meta["tags"] = sorted(list(tags))

    # 清理正文中的多余内容
    body_part = clean_content(body_part)

    # 确保正文以标题开始
    if body_part and not body_part.startswith("#"):
        body_part = "# " + meta["title"] + "\n\n" + body_part

    # 重新组装文件
    yaml_str = yaml.dump(meta, allow_unicode=True, default_flow_style=False)
    new_content = f"---\n{yaml_str}---\n\n{body_part}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"处理完成: {filename}")

def main():
    # 获取所有 .md 文件（排除处理脚本自身）
    md_files = [f for f in BASE_DIR.glob("*.md") if f.name != "process_textbook.py"]
    print(f"找到 {len(md_files)} 个文件")

    for filepath in md_files:
        try:
            process_file(filepath)
        except Exception as e:
            print(f"处理失败 {filepath.name}: {e}")
            import traceback
            traceback.print_exc()

    print("全部处理完成")

if __name__ == "__main__":
    main()
