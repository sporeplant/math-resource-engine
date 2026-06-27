#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复习讲义整理脚本

要求：
1. 输入knowledge中的知识点讲解不能丢
2. 每个题目必须源自给定的knowledge文件内容
3. 生成的文件需要通过配图validators

讲义结构：
1. 知识点讲解与对应例题（有几个知识点配几个例题）
2. 当堂练习（约10题）
3. 课后作业（约10题）
4. 题目详情表（题目ID、所属知识考察点、难度等级、入选理由、参考答案）
"""

import os
import re
import yaml
import glob
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

try:
    from review_math_utils import normalize_review_math_markup
except ModuleNotFoundError:
    from tools.review_math_utils import normalize_review_math_markup

class ReviewLessonProcessor:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.knowledge_dir = self.base_dir / "knowledge" / "复习讲义"
        self.output_dir = self.base_dir / "outputs" / "八下复习讲义"
        self.images_dir = self.output_dir / "images"
        self.rules_file = self.knowledge_dir / "复习讲义编写规则.md"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
    def load_rules(self):
        if self.rules_file.exists():
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def list_available_lessons(self):
        lesson_files = glob.glob(str(self.knowledge_dir / "*.md"))
        lessons = []
        for f in lesson_files:
            filename = os.path.basename(f)
            if filename == "复习讲义编写规则.md":
                continue
            lessons.append(filename)
        return sorted(lessons)
    
    def find_lesson(self, input_text):
        lessons = self.list_available_lessons()
        input_text = input_text.strip()
        
        if input_text.endswith(".md"):
            input_text = input_text[:-3]
        
        exact_matches = [l for l in lessons if input_text == l.replace(".md", "")]
        if exact_matches:
            return exact_matches[0]
        
        contains_matches = [l for l in lessons if input_text in l]
        if contains_matches:
            return contains_matches[0]
        
        if input_text.startswith("第") and input_text.endswith("讲"):
            num_part = input_text[1:-1]
            if num_part.isdigit():
                padded_num = f"{int(num_part):02d}"
                match = f"{padded_num}讲.md"
                if match in lessons:
                    return match
        
        return None
    
    def copy_image_to_output(self, img_path):
        """复制图片到outputs目录，返回新的相对路径"""
        if not img_path.exists():
            return None
        
        dest_path = self.images_dir / img_path.name
        
        try:
            shutil.copy2(img_path, dest_path)
            return f"./images/{img_path.name}"
        except Exception as e:
            print(f"复制图片失败: {e}")
            return None
    
    def convert_markdown_image_to_html(self, match):
        """将markdown图片语法转换为HTML格式"""
        alt_text = match.group(1) if match.group(1) else "图片"
        img_path = match.group(2)
        
        if img_path.startswith("./images/"):
            return f'<img src="{img_path}" alt="{alt_text}">'
        elif img_path.startswith("images/"):
            return f'<img src="./{img_path}" alt="{alt_text}">'
        else:
            filename = os.path.basename(img_path)
            return f'<img src="./images/{filename}" alt="{alt_text}">'
    
    def collect_all_images(self, source_files):
        """收集所有源文件中的图片"""
        images_map = {}
        
        for source_file in source_files:
            if not source_file.exists():
                continue
            
            source_images_dir = source_file.parent / "images"
            if source_images_dir.exists():
                for img_file in source_images_dir.glob("*"):
                    if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                        images_map[img_file.name] = img_file
        
        common_images_dir = self.knowledge_dir / "images"
        if common_images_dir.exists():
            for img_file in common_images_dir.glob("*"):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                    images_map[img_file.name] = img_file
        
        return images_map
    
    def validate_output(self, output_path):
        """运行复习讲义专用validators和通用outputsvalidators。"""
        validators = [
            ("复习课讲义结构验证", self.base_dir / "tools" / "validate_review_lesson.py"),
            ("复习讲义兼容验证", self.base_dir / "tools" / "validate_review_handout.py"),
            ("通用outputs验证", self.base_dir / "tools" / "validate_output.py"),
        ]
        messages = []
        passed = True

        for label, validate_script in validators:
            if not validate_script.exists():
                messages.append(f"{label}脚本不存在，跳过")
                continue
            try:
                result = subprocess.run(
                    ['python', str(validate_script), str(output_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(self.base_dir)
                )
            except Exception as e:
                passed = False
                messages.append(f"{label}过程出错: {str(e)}")
                continue

            output = (result.stdout + "\n" + result.stderr).strip()
            if result.returncode == 0:
                messages.append(f"{label}通过")
            else:
                passed = False
                messages.append(f"{label}失败:\n{output}")

        return passed, "\n".join(messages)
    
    def extract_content_blocks(self, file_path):
        """
        从源文件中提取所有内容块（知识点、例题、练习等）
        完整保留原始内容，不做任何修改
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = []
        lines = content.split('\n')
        
        current_block_type = None
        current_block_content = []
        current_title = None
        
        for line in lines:
            if line.startswith("## ") and not line.startswith("### "):
                if current_block_content:
                    blocks.append({
                        'type': current_block_type,
                        'title': current_title,
                        'content': '\n'.join(current_block_content),
                        'source': str(file_path)
                    })
                
                current_title = line.strip()
                current_block_content = [line]
                
                if '学习目标' in line:
                    current_block_type = 'learning_objectives'
                elif '思维导图' in line:
                    current_block_type = 'mind_map'
                elif '知识点' in line:
                    current_block_type = 'knowledge_point'
                elif '即学即练' in line:
                    current_block_type = 'instant_practice'
                elif '题型精讲' in line:
                    current_block_type = 'type_exercises'
                elif '课后练习' in line:
                    current_block_type = 'after_class'
                elif '例题' in line:
                    current_block_type = 'example'
                else:
                    current_block_type = 'other'
            else:
                current_block_content.append(line)
        
        if current_block_content:
            blocks.append({
                'type': current_block_type,
                'title': current_title,
                'content': '\n'.join(current_block_content),
                'source': str(file_path)
            })
        
        return blocks
    
    def extract_blocks_from_sources(self, source_files):
        """从多个源文件中提取内容块"""
        all_blocks = []
        for source_file in source_files:
            if source_file.exists():
                blocks = self.extract_content_blocks(source_file)
                all_blocks.extend(blocks)
        return all_blocks
    
    def generate_review_lesson(self, lesson_num, lesson_name, source_files):
        """
        生成复习讲义
        模块1：知识点讲解与对应例题
        模块2：当堂练习（约10题）
        模块3：课后作业（约10题）
        模块4：题目详情表
        """
        all_blocks = self.extract_blocks_from_sources(source_files)
        images_map = self.collect_all_images(source_files)
        
        for img_name, img_path in images_map.items():
            self.copy_image_to_output(img_path)
        
        content = []
        
        content.append(f"## 第 {lesson_num} 讲 {lesson_name}")
        content.append("")
        
        knowledge_blocks = [b for b in all_blocks if b['type'] == 'knowledge_point']
        type_exercise_blocks = [b for b in all_blocks if b['type'] == 'type_exercises']
        instant_practice_blocks = [b for b in all_blocks if b['type'] == 'instant_practice']
        after_class_blocks = [b for b in all_blocks if b['type'] == 'after_class']
        
        # ========== 模块1：知识点讲解与对应例题 ==========
        content.append("## 模块1 知识点与典型分析")
        content.append("")
        
        kp_counter = 1
        example_counter = 1
        question_details = []
        
        for kb in knowledge_blocks[:5]:
            title = kb['title']
            new_title = re.sub(r'## 知识点\s*(\d+)', f'## 知识点 {kp_counter:02d}', title)
            content.append(new_title)
            content.append("")
            
            kb_content = kb['content'].strip()
            if kb_content.startswith(title):
                kb_content = kb_content[len(title):].strip()
            elif title in kb_content:
                kb_content = kb_content[kb_content.index(title) + len(title):].strip()
            content.append(kb_content)
            content.append("")
            
            matching_examples = []
            for tb in type_exercise_blocks:
                if tb['content'].strip():
                    examples = re.findall(r'【典例[\s\S]*?】', tb['content'])
                    if examples:
                        matching_examples.extend(examples)
            
            if kp_counter <= len(matching_examples):
                ex = matching_examples[kp_counter - 1]
                clean_ex = ex.replace('【典例', '').replace('】', '').strip()
                if clean_ex:
                    content.append("**对应例题：**")
                    content.append(f"{example_counter}．{clean_ex}")
                    content.append("")
                    
                    question_details.append({
                        'question_id': f'EX-{example_counter:02d}',
                        'type': '例题',
                        'knowledge_point': title.replace('## 知识点', '').strip(),
                        'difficulty': '基础',
                        'reason': f'来源于知识点{kp_counter}的典例',
                        'answer': ''
                    })
                    example_counter += 1
            
            kp_counter += 1
        
        # ========== 模块2：当堂练习 ==========
        content.append("## 模块2 课堂实践")
        content.append("")
        
        practice_counter = 1
        all_instant_practice = []
        for ipb in instant_practice_blocks:
            if ipb['content'].strip():
                lines = ipb['content'].strip().split('\n')
                current_question = None
                current_lines = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('#'):
                        continue
                    if re.match(r'^\d+．', line):
                        if current_question:
                            all_instant_practice.append('\n'.join(current_lines))
                        current_question = line
                        current_lines = [line]
                    elif re.match(r'^[A-D]．', line) and current_lines:
                        current_lines.append(line)
                    else:
                        if current_lines:
                            current_lines.append(line)
                        else:
                            current_question = line
                            current_lines = [line]
                if current_lines:
                    all_instant_practice.append('\n'.join(current_lines))
        
        practice_to_use = all_instant_practice[:10]
        for p in practice_to_use:
            content.append(p)
            content.append("")
            question_details.append({
                'question_id': f'IP-{practice_counter:02d}',
                'type': '当堂练习',
                'knowledge_point': '综合',
                'difficulty': '基础',
                'reason': '来源于即学即练',
                'answer': ''
            })
            practice_counter += 1
        
        if len(practice_to_use) < 10:
            for tb in type_exercise_blocks:
                if len(practice_to_use) >= 10:
                    break
                variants = re.findall(r'【变式[\s\S]*?】', tb['content'])
                for var in variants:
                    if len(practice_to_use) >= 10:
                        break
                    clean_var = var.replace('【变式', '').replace('】', '').strip()
                    if clean_var:
                        practice_to_use.append(clean_var)
                        content.append(f"{practice_counter}．{clean_var}")
                        content.append("")
                        question_details.append({
                            'question_id': f'IP-{practice_counter:02d}',
                            'type': '当堂练习',
                            'knowledge_point': '综合',
                            'difficulty': '中等',
                            'reason': '来源于变式练习',
                            'answer': ''
                        })
                        practice_counter += 1
        
        # ========== 模块3：课后作业 ==========
        content.append("## 模块3 拓展任务")
        content.append("")
        
        homework_counter = 1
        all_after_class = []
        for acb in after_class_blocks:
            if acb['content'].strip():
                lines = acb['content'].strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        all_after_class.append(line)
        
        homework_to_use = all_after_class[:10]
        for hw in homework_to_use:
            content.append(f"{homework_counter}．{hw}")
            content.append("")
            question_details.append({
                'question_id': f'HW-{homework_counter:02d}',
                'type': '课后作业',
                'knowledge_point': '综合',
                'difficulty': '中等',
                'reason': '来源于课后练习',
                'answer': ''
            })
            homework_counter += 1
        
        # ========== 模块4：题目详情表 ==========
        content.append("## 模块4 信息档案")
        content.append("")
        content.append("| ID | 类别 | 知识考察点 | 难度 | 来源说明 | 备选 |")
        content.append("|----|------|------------|------|----------|------|")
        for qd in question_details:
            difficulty_label = {
                '基础': '⭐',
                '中等': '⭐⭐',
                '困难': '⭐⭐⭐'
            }.get(qd['difficulty'], qd['difficulty'])
            
            content.append(f"| {qd['question_id']} | {qd['type']} | {qd['knowledge_point']} | {difficulty_label} | {qd['reason']} | - |")
            content.append("")
        
        yaml_front = {
            'content_type': 'review_lesson',
            'command': '复习讲义',
            'lesson_id': f'review_{lesson_num}',
            'lesson_name': lesson_name,
            'workflow_version': 'v2',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source_files': [str(f) for f in source_files if f.exists()]
        }
        
        front_matter = "---\n" + yaml.dump(yaml_front, allow_unicode=True) + "---\n"
        full_content = front_matter + '\n'.join(content)
        
        full_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', self.convert_markdown_image_to_html, full_content)
        full_content = normalize_review_math_markup(full_content)
        
        return full_content
    
    def process(self, lesson_input):
        """主处理流程"""
        lesson_file = self.find_lesson(lesson_input)
        
        if not lesson_file:
            available = self.list_available_lessons()
            return f"未找到匹配的讲义文件。可用讲义：{', '.join(available)}"
        
        lesson_path = self.knowledge_dir / lesson_file
        
        lesson_num = lesson_file.replace(".md", "").replace("讲", "")
        lesson_name = f"复习讲义第{lesson_num}讲"
        
        with open(lesson_path, 'r', encoding='utf-8') as f:
            content = f.read()
            title_match = re.search(r'## 第\s*(\d+)\s*讲\s+(.+)', content)
            if title_match:
                lesson_num = title_match.group(1)
                lesson_name = title_match.group(2)
        
        source_files = [lesson_path]
        other_lessons = [self.knowledge_dir / l for l in self.list_available_lessons() 
                         if l != lesson_file and l != "复习讲义编写规则.md"]
        source_files.extend(other_lessons)
        
        print(f"正在处理讲义：{lesson_name}")
        print(f"源文件数量：{len(source_files)}")
        
        review_content = self.generate_review_lesson(lesson_num, lesson_name, source_files)
        
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', lesson_name)
        output_filename = f"{lesson_num}讲_{safe_name}_复习讲义.md"
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(review_content)
        
        print(f"复习讲义已生成：{output_path}")
        
        valid_passed, valid_msg = self.validate_output(output_path)
        if valid_passed:
            print(f"✓ {valid_msg}")
        else:
            print(f"✗ {valid_msg}")
            print("请检查outputs文件中的结构、题源、图片和公式标记")
        
        return f"复习讲义已生成：{output_path}\n验证结果：{valid_msg}"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python review_lesson_processor.py <讲义编号或名称>")
        print("示例：python review_lesson_processor.py 01讲")
        print("      python review_lesson_processor.py 坐标方法简单应用")
        print("      python review_lesson_processor.py 第14讲")
        sys.exit(1)
    
    processor = ReviewLessonProcessor()
    result = processor.process(sys.argv[1])
    print(result)
