# 视频口播稿生成工具

## 功能介绍

这个工具可以从视频文件中自动提取音频，使用OpenAI Whisper进行语音识别，并生成带有时间戳的口播稿。

## 安装依赖

1. 首先安装PyTorch（Whisper的依赖）：
   ```
   pip install torch
   ```

2. 然后安装OpenAI Whisper：
   ```
   pip install openai-whisper
   ```

## 使用方法

在项目根目录下运行：

```bash
python tools/video_transcribe.py <视频文件路径>
```

### 示例

处理《用统计图描述数据.mp4》：
```bash
python tools/video_transcribe.py video/用统计图描述数据.mp4
```

## 输出结果

脚本会在视频文件所在目录下创建一个 `transcripts` 文件夹，并生成两个文件：

1. `<视频文件名>.wav` - 提取的音频文件
2. `<视频文件名>_口播稿.md` - 带有时间戳的口播稿

## 口播稿格式

生成的口播稿包含：
- 按时间分段的文本，带有[开始时间 - 结束时间]标记
- 完整的视频文字转录

## 模型选择

当前脚本使用 `small` 模型，平衡了识别精度和运行速度。你可以修改脚本中的模型参数：

- `tiny` - 最快，精度较低
- `base` - 较快，精度中等
- `small` - 平衡（推荐）
- `medium` - 较慢，精度较高
- `large` - 最慢，精度最高
