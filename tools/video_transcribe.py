#!/usr/bin/env python3
"""
视频口播稿生成工具
使用FFmpeg提取音频，使用OpenAI Whisper进行语音识别
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_ffmpeg():
    """检查FFmpeg是否可用"""
    ffmpeg_path = Path(__file__).parent / "ffmpeg" / "bin" / "ffmpeg.exe"
    if ffmpeg_path.exists():
        return str(ffmpeg_path)
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return "ffmpeg"
    except FileNotFoundError:
        return None

def extract_audio(video_path, output_audio_path, ffmpeg_exe):
    """从视频中提取音频为WAV格式"""
    print(f"正在从视频中提取音频: {video_path}")
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_audio_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg错误: {result.stderr}")
        return False
    print(f"音频已提取到: {output_audio_path}")
    return True

def transcribe_with_cli(audio_path, output_json_path):
    """使用Whisper命令行工具进行语音识别"""
    print("正在进行语音识别（使用Whisper CLI）...")
    cmd = [
        sys.executable, "-m", "whisper",
        str(audio_path),
        "--model", "small",
        "--language", "zh",
        "--output_format", "json",
        "--output_dir", str(output_json_path.parent),
        "--fp16", "False"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Whisper CLI输出: {result.stdout}")
        if result.stderr:
            print(f"Whisper CLI信息: {result.stderr}")
        # 查找生成的JSON文件
        json_file = output_json_path.parent / f"{audio_path.stem}.json"
        if json_file.exists():
            print(f"找到转录文件: {json_file}")
            return json_file
        else:
            print("警告: 未找到JSON输出文件，尝试查找VTT文件")
            vtt_file = output_json_path.parent / f"{audio_path.stem}.vtt"
            if vtt_file.exists():
                return vtt_file
            return None
    except Exception as e:
        print(f"Whisper CLI错误: {e}")
        return None

def parse_vtt_to_markdown(vtt_path, output_md_path):
    """从VTT文件解析出口播稿"""
    print(f"正在解析VTT文件: {vtt_path}")
    with open(vtt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    segments = []
    current_time = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("WEBVTT") or line.isdigit() or "-->" not in line:
            if line and "-->" not in line and not line.startswith("WEBVTT") and not line.isdigit() and line:
                if current_time:
                    current_text.append(line)
            continue
        
        if "-->" in line:
            if current_time and current_text:
                segments.append((current_time[0], current_time[1], " ".join(current_text)))
            parts = line.split("-->")
            start = parts[0].strip()
            end = parts[1].split()[0].strip() if len(parts[1].split()) > 0 else parts[1].strip()
            # 简化时间格式
            start = start.split(".")[0]
            end = end.split(".")[0]
            current_time = (start, end)
            current_text = []
    
    if current_time and current_text:
        segments.append((current_time[0], current_time[1], " ".join(current_text)))
    
    # 生成Markdown
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(f"视频口播稿\n")
        f.write(f"{'='*50}\n\n")
        
        for start, end, text in segments:
            f.write(f"[{start} - {end}]\n")
            f.write(f"{text}\n\n")
        
        # 生成完整文本
        f.write(f"\n{'='*50}\n")
        f.write(f"完整文本:\n")
        full_text = " ".join(text for _, _, text in segments)
        f.write(full_text)
    
    print(f"口播稿已生成: {output_md_path}")
    return True

def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python video_transcribe.py <视频文件路径>")
        print("\n示例:")
        print("  python video_transcribe.py ../video/用统计图描述数据.mp4")
        return
    
    video_path = Path(sys.argv[1])
    if not video_path.exists():
        print(f"错误: 文件不存在: {video_path}")
        return
    
    ffmpeg_exe = check_ffmpeg()
    if not ffmpeg_exe:
        print("错误: 找不到FFmpeg")
        return
    
    # 设置FFmpeg环境变量，让Whisper使用我们的FFmpeg
    ffmpeg_dir = str(Path(__file__).parent / "ffmpeg" / "bin")
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    
    # 创建输出目录
    output_dir = video_path.parent / "transcripts"
    output_dir.mkdir(exist_ok=True)
    
    # 提取音频
    audio_path = output_dir / f"{video_path.stem}.wav"
    if not extract_audio(video_path, audio_path, ffmpeg_exe):
        return
    
    # 使用Whisper CLI进行识别
    json_path = output_dir / f"{video_path.stem}.json"
    transcript_file = transcribe_with_cli(audio_path, json_path)
    
    if transcript_file:
        # 解析结果生成口播稿
        text_path = output_dir / f"{video_path.stem}_口播稿.md"
        if transcript_file.suffix == ".vtt":
            if parse_vtt_to_markdown(transcript_file, text_path):
                print("\n完成！")
                print(f"口播稿位置: {text_path}")
        elif transcript_file.suffix == ".json":
            # 从JSON解析
            import json
            with open(transcript_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(f"视频口播稿\n")
                f.write(f"{'='*50}\n\n")
                for segment in data["segments"]:
                    start = segment["start"]
                    end = segment["end"]
                    start_str = f"{int(start//60):02d}:{int(start%60):02d}"
                    end_str = f"{int(end//60):02d}:{int(end%60):02d}"
                    f.write(f"[{start_str} - {end_str}]\n")
                    f.write(f"{segment['text'].strip()}\n\n")
                f.write(f"\n{'='*50}\n")
                f.write(f"完整文本:\n")
                f.write(data["text"])
            print("\n完成！")
            print(f"口播稿位置: {text_path}")
    else:
        print("语音识别失败")

if __name__ == "__main__":
    main()
