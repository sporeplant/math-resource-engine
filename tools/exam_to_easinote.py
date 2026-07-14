"""将期末试卷 Markdown 转换为希沃白板课件 JSON

用法:
  python tools/exam_to_easinote.py <exam.md> [output_dir]

示例:
  python tools/exam_to_easinote.py knowledge/reviews/24-25期末试卷.md
  python tools/exam_to_easinote.py knowledge/reviews/24-25期末试卷.md outputs/packages/exam-24-25-final

每页展示一题 + 配图，不含解答过程。
"""

import json
import os
import re
import shutil
import sys


# ═══ 常量 ═══
PW = 1120  # 页面宽度
MG = 70    # 左/右边距
TFS = 34   # 标题字体大小
SFS = 28   # 副标题字体大小
BFS = 24   # 正文字体大小
LFS = 22   # 选项/小号文字
COLOR_TITLE = "#1f4e79"   # 深蓝
COLOR_SUB = "#12355b"     # 更深深蓝
COLOR_BODY = "#222222"    # 正文黑色
COLOR_LIGHT = "#555555"   # 浅色
COLOR_TYPE = "#c0392b"    # 红色用于题型标注

FONT = "Microsoft YaHei"

TITLE_Y = 54
SUB_Y_OFFSET = 56
BODY_START_Y = 140
ELEM_GAP = 8


def parse_exam(md_text):
    """解析试卷 Markdown，返回结构化数据"""
    lines = md_text.split("\n")
    
    # 提取标题
    title = ""
    for line in lines:
        line = line.strip()
        if line.startswith("# ") and not line.startswith("#"):
            title = re.sub(r"^#\s+", "", line)
            break
        elif line.startswith("#"):
            m = re.match(r"^#+\s+(.+)", line)
            if m:
                title = m.group(1)
                break
    
    # 提取大题分区
    sections = []  # [(section_type, label, [(q_num, q_text, images, is_mc)])]
    current_type = ""
    current_label = ""
    current_questions = []
    question_texts = []  # 暂存正在累积的题目文本
    current_image = None
    current_qnum = ""
    in_question = False
    in_mc = False
    mc_options = []
    
    def flush_question():
        nonlocal current_qnum, question_texts, current_image, in_question, in_mc, mc_options
        if current_qnum:
            full_text = "\n".join(question_texts)
            if mc_options:
                full_text += "\n" + "\n".join(mc_options)
            current_questions.append((current_qnum, full_text, current_image, in_mc))
            current_qnum = ""
            question_texts = []
            current_image = None
            in_question = False
            in_mc = False
            mc_options = []
    
    for line in lines:
        stripped = line.strip()
        
        # 跳过空行和注释行
        if not stripped or stripped.startswith("<!--"):
            # 空行也是文本的一部分，除非是新题开始
            if in_question and current_qnum:
                question_texts.append("")
            continue
        
        # 大题标题：一、二、三、等
        m_section = re.match(r"^##\s+[一二三四五六七八九十]+[、.．]\s*(.*)$", stripped)
        if m_section:
            flush_question()
            if current_questions:
                sections.append((current_type, current_label, current_questions))
                current_questions = []
            
            section_header = m_section.group(0).lstrip("#").strip()
            current_label = section_header
            
            if "选择" in section_header:
                current_type = "选择题"
            elif "填空" in section_header:
                current_type = "填空题"
            elif "解答" in section_header or "计算" in section_header or "证明" in section_header:
                current_type = "解答题"
            else:
                current_type = section_header
            
            # 标记进度
            question_texts = []
            continue
        
        # 跳过栏目信息行
        if "本大题有" in stripped and "小题" in stripped and "分" in stripped:
            continue
        if "考生注意" in stripped or "答题前" in stripped or "考生务必" in stripped:
            continue
        if stripped.startswith("| 题") and "组别" in stripped:
            continue
        if stripped.startswith("| -") and "---" in stripped:
            continue
        
        # 图片行
        m_img = re.match(r"^!\[.*?\]\((.+?)\)", stripped)
        if m_img:
            img_path = m_img.group(1)
            # 标准化路径：../images/xxx.jpg -> images/xxx.jpg
            img_path = re.sub(r"^\.\./", "", img_path)
            current_image = img_path
            continue
        
        # 图注行
        if re.match(r"^\*图", stripped):
            continue
        
        # 题目编号检测：选择题
        # "1. " "2. " 等
        m_q = re.match(r"^(\d+)[.．、]\s*(.*)", stripped)
        
        # 大题内的小题编号检测（如 17. (本小题6分)）
        m_q2 = re.match(r"^##?\s*(\d+)[.．、]\s*(.*)", stripped)
        
        if m_q:
            flush_question()
            qnum = m_q.group(1)
            rest = m_q.group(2)
            current_qnum = qnum
            question_texts = [rest] if rest else []
            in_question = True
            in_mc = False
            mc_options = []
            # 检测是否完全由选项构成
            continue
        elif m_q2:
            flush_question()
            qnum = m_q2.group(1)
            rest = m_q2.group(2)
            current_qnum = qnum
            question_texts = [rest] if rest else []
            in_question = True
            in_mc = False
            mc_options = []
            continue
        
        # 选择题选项 A. B. C. D.
        m_opt = re.match(r"^([A-Da-d])[.．、]\s*(.*)", stripped)
        if m_opt and in_question:
            mc_options.append(stripped)
            in_mc = True
            continue
        
        # 图片可能出现在任何行（包括没有![]语法时）
        # 但通常已经通过上面的正则匹配了
        
        # 普通行，属于当前题目
        if in_question and current_qnum:
            question_texts.append(stripped)
    
    # 刷新最后一题
    flush_question()
    if current_questions:
        sections.append((current_type, current_label, current_questions))
    
    return title, sections


def clean_text(text):
    """清理文本：移除标记、保持 LaTeX"""
    # 替换可能的换行问题
    text = text.replace("\\n", "\n")
    # 移除多余空白
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def make_slide_title(question_num, section_type):
    """生成题目幻灯片标题"""
    type_map = {
        "选择题": "选择题",
        "填空题": "填空题",
        "解答题": "解答题",
    }
    t = type_map.get(section_type, section_type)
    return f"{t} 第{question_num}题"


def build_slides(title, sections, assets_dir, md_dir):
    """构建幻灯片列表"""
    slides = []
    si = 0
    
    # ========== 标题页 ==========
    si += 1
    slide_id = f"s{si:02d}"
    elements = [
        {
            "id": f"{slide_id}_e001",
            "type": "text",
            "text": f"📐 {title}",
            "x": MG,
            "y": TITLE_Y,
            "width": PW,
            "height": 60,
            "fontSize": TFS,
            "bold": True,
            "color": COLOR_TITLE,
            "fontFamily": FONT,
        },
        {
            "id": f"{slide_id}_e002",
            "type": "text",
            "text": "八年级数学 · 期末试卷",
            "x": MG,
            "y": TITLE_Y + 70,
            "width": PW,
            "height": 50,
            "fontSize": SFS,
            "color": COLOR_BODY,
            "fontFamily": FONT,
        },
        {
            "id": f"{slide_id}_e003",
            "type": "text",
            "text": "希沃白板课件 · 题目展示（无解答）",
            "x": MG,
            "y": TITLE_Y + 130,
            "width": PW,
            "height": 40,
            "fontSize": 22,
            "color": COLOR_LIGHT,
            "fontFamily": FONT,
        },
    ]
    slides.append({"id": slide_id, "elements": elements})
    
    # ========== 各题幻灯片 ==========
    for section_type, section_label, questions in sections:
        for qnum, qtext, img_path, is_mc in questions:
            si += 1
            slide_id = f"s{si:02d}"
            elements = []
            ei = 0
            
            # 题目标题行
            display_num = qnum
            slide_title = make_slide_title(display_num, section_type)
            
            ei += 1
            y_pos = TITLE_Y
            elements.append({
                "id": f"{slide_id}_e{ei:03d}",
                "type": "text",
                "text": slide_title,
                "x": MG,
                "y": y_pos,
                "width": PW,
                "height": 50,
                "fontSize": SFS,
                "bold": True,
                "color": COLOR_TITLE,
                "fontFamily": FONT,
            })
            
            # 题目正文
            body_text = clean_text(qtext)
            if body_text:
                ei += 1
                y_pos = BODY_START_Y
                
                # 估算高度：每行约 30px
                lines_count = body_text.count("\n") + 1
                # 加上 LaTeX 行可能占用更多
                latex_lines = body_text.count("$")
                est_lines = lines_count + latex_lines
                height = max(40, est_lines * 32)
                # 限制最大高度，给图片留空间
                height = min(height, 360)
                
                elements.append({
                    "id": f"{slide_id}_e{ei:03d}",
                    "type": "text",
                    "text": body_text,
                    "x": MG,
                    "y": y_pos,
                    "width": PW,
                    "height": height,
                    "fontSize": BFS,
                    "color": COLOR_BODY,
                    "fontFamily": FONT,
                })
            
            # 图片（如果有）
            if img_path:
                # 复制图片到 assets
                src_img = os.path.join(md_dir, img_path)
                if not os.path.exists(src_img):
                    # 尝试从 knowledge/images 直接找文件名
                    img_name = os.path.basename(img_path)
                    # 也试试 ../images/xxx.jpg
                    src_img_alt = os.path.join(os.path.dirname(md_dir), img_path)
                    if os.path.exists(src_img_alt):
                        src_img = src_img_alt
                    else:
                        # 尝试 knowledge/images/
                        src_img = os.path.join(md_dir, "..", "images", img_name)
                        if not os.path.exists(src_img):
                            src_img = os.path.join(md_dir, "..", "..", "images", img_name)
                
                if os.path.exists(src_img):
                    dst_name = os.path.basename(img_path)
                    dst_img = os.path.join(assets_dir, dst_name)
                    try:
                        shutil.copy2(src_img, dst_img)
                        ei += 1
                        # 图片从正文下方开始
                        img_y = y_pos + height + 12 if body_text else BODY_START_Y
                        # 控制图片大小
                        elements.append({
                            "id": f"{slide_id}_e{ei:03d}",
                            "type": "image",
                            "src": dst_name,
                            "x": MG,
                            "y": img_y,
                            "width": 700,
                            "height": 380,
                        })
                    except Exception as e:
                        print(f"  警告: 无法复制图片 {src_img} -> {dst_img}: {e}")
                else:
                    print(f"  警告: 图片不存在 {src_img}")
                    # 文本替代
                    ei += 1
                    elements.append({
                        "id": f"{slide_id}_e{ei:03d}",
                        "type": "text",
                        "text": f"[图片: {os.path.basename(img_path)}]",
                        "x": MG,
                        "y": BODY_START_Y + 200,
                        "width": PW,
                        "height": 40,
                        "fontSize": 20,
                        "italic": True,
                        "color": COLOR_LIGHT,
                        "fontFamily": FONT,
                    })
            
            slides.append({"id": slide_id, "elements": elements})
    
    return slides


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    md_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(md_path):
        print(f"错误: 文件不存在: {md_path}")
        sys.exit(1)
    
    # 输出目录
    if len(sys.argv) >= 3:
        out_dir = os.path.abspath(sys.argv[2])
    else:
        out_dir = os.path.dirname(md_path)
    os.makedirs(out_dir, exist_ok=True)
    
    # 试卷文件名
    stem = os.path.splitext(os.path.basename(md_path))[0]
    out_json = os.path.join(out_dir, f"{stem}.json")
    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # 读取试卷
    with open(md_path, encoding="utf-8") as f:
        md_text = f.read()
    
    # 解析
    print(f"解析试卷: {md_path}")
    title, sections = parse_exam(md_text)
    print(f"  标题: {title}")
    total_q = sum(len(qs) for _, _, qs in sections)
    print(f"  大题: {len(sections)}, 总题数: {total_q}")
    for st, sl, qs in sections:
        print(f"    {st}: {len(qs)}题")
        for qn, qt, qi, _ in qs:
            img_info = f" [有图: {os.path.basename(qi)}]" if qi else ""
            print(f"      {qn}: {qt[:40]}...{img_info}")
    
    # 构建幻灯片
    md_dir = os.path.dirname(md_path)
    slides = build_slides(title, sections, assets_dir, md_dir)
    print(f"\n生成幻灯片: {len(slides)}页")
    
    # 写入 JSON
    doc = {"slides": slides}
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    
    # 统计
    tot_elems = sum(len(s["elements"]) for s in slides)
    tot_imgs = sum(1 for s in slides for e in s["elements"] if e["type"] == "image")
    print(f"\nOK: {out_json}")
    print(f"   幻灯片: {len(slides)}页")
    print(f"   文本元素: {tot_elems - tot_imgs}")
    print(f"   图片元素: {tot_imgs}")
    print(f"   资源目录: {assets_dir}")


if __name__ == "__main__":
    main()
