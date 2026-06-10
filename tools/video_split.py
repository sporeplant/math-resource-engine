#!/usr/bin/env python3
"""
视频分割工具 - 步骤3：根据时间点分割视频

使用方法:
python tools/video_split.py video/用统计图描述数据.mp4
"""
import sys
from pathlib import Path
import subprocess


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


def parse_time_to_seconds(time_str):
    """将时间字符串转换为秒"""
    parts = time_str.split(":")
    if len(parts) == 2:  # MM:SS
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        try:
            return float(time_str)
        except ValueError:
            return None


def split_video(video_path, segments, ffmpeg_exe):
    """
    分割视频
    
    Args:
        video_path: 视频文件路径
        segments: 片段列表，每个元素是 (start_time, end_time, output_name)
        ffmpeg_exe: FFmpeg可执行文件路径
    """
    video_path = Path(video_path)
    output_dir = video_path.parent / "segments"
    output_dir.mkdir(exist_ok=True)
    
    print(f"开始分割视频: {video_path}")
    print(f"输出目录: {output_dir}")
    print(f"共 {len(segments)} 个片段\n")
    
    for i, (start_time, end_time, output_name) in enumerate(segments, 1):
        output_path = output_dir / output_name
        print(f"[{i}/{len(segments)}] 处理: {output_name}")
        print(f"  时间范围: {start_time} - {end_time}")
        
        cmd = [
            ffmpeg_exe,
            "-y",
            "-ss", start_time,
            "-to", end_time,
            "-i", str(video_path),
            "-c", "copy",
            str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ 成功: {output_path}")
            else:
                print(f"  ✗ 失败: {result.stderr}")
        except Exception as e:
            print(f"  ✗ 错误: {e}")
        
        print()
    
    print("分割完成！")
    return output_dir


def main():
    if len(sys.argv) < 2:
        print("视频分割工具")
        print("=" * 40)
        print("\n使用方法:")
        print("  python tools/video_split.py <视频文件路径>")
        print("\n示例:")
        print("  python tools/video_split.py video/用统计图描述数据.mp4")
        print("\n该工具会使用预定义的时间点分割视频。")
        print("您也可以编辑此文件来自定义分割点。")
        return
    
    video_path = Path(sys.argv[1])
    if not video_path.exists():
        print(f"错误: 文件不存在: {video_path}")
        return
    
    ffmpeg_exe = check_ffmpeg()
    if not ffmpeg_exe:
        print("错误: 找不到FFmpeg")
        return
    
    # 预定义的分割点（以"用统计图描述数据"为例）
    segments = [
        ("00:00:00", "00:00:24", f"{video_path.stem}_01_知识点引入.mp4"),
        ("00:00:24", "00:01:24", f"{video_path.stem}_02_条形统计图.mp4"),
        ("00:01:24", "00:02:49", f"{video_path.stem}_03_折线统计图.mp4"),
        ("00:02:49", "00:05:28", f"{video_path.stem}_04_扇形统计图.mp4"),
        ("00:05:28", "00:05:44", f"{video_path.stem}_05_知识点小结.mp4"),
    ]
    
    output_dir = split_video(video_path, segments, ffmpeg_exe)
    
    print("\n" + "=" * 40)
    print("生成的文件:")
    for f in output_dir.glob("*.mp4"):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
