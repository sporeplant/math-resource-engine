# md2htmlyishu 配置文件说明

## 目录结构

```text
configs/
├── default.yaml              # 默认配置（无匹配时的 fallback）
├── ch12-分式的乘除.yaml       # 12.2.1 配置示例
├── ch13-统计调查与直方图.yaml  # 第13讲配置示例
└── {章节}-{课题}.yaml          # 其他课程配置
```

## 配置文件命名规则

- 格式：`ch{章节}-{课题名称}.yaml`，例如 `ch12.2-分式的乘除.yaml`。
- 脚本按由细到粗的顺序匹配：`ch12.2.1-*` → `ch12.2-*` → `ch12-*`。
- 同目录 `{课件文件名}.yaml` 的本地配置优先级最高。

## 配置加载优先级

1. **MD 同目录配置**：`{课件文件名}.yaml`
2. **configs/ 目录匹配**：按课件中的章节号由细到粗匹配
3. **默认配置**：`configs/default.yaml`

## 视觉标注职责

| 样式 | 字段 | 只标注 | 不标注 |
|------|------|--------|--------|
| 荧光笔 | `highlight_phrases` | 关键条件、易错点 | 学习目标、法则、定义、普通术语 |
| 红笔结论框 | `red_conclusion_phrases` | 法则、定义、策略归纳 | 一般提示、题干、操作步骤 |
| 蓝笔 | `blue_hint_*` | 明确的思路、推导提示 | 常规操作指令 |

每课荧光笔通常控制为 3–6 项，并通过 `page_highlights` 限定到首次建立或重点提醒的页面。

## 配置示例

```yaml
course:
  name: "分式的乘除（第一课时）"
  chapter: "第12章 分式的运算"
  section: "12.2.1"

# 全课通用的条件或易错点；通常为空。
highlight_phrases: []

# 全课通用的法则、定义或策略归纳；通常为空。
red_conclusion_phrases: []

# 按标题精准限定标注所在页面。
page_highlights:
  - title_contains: "分式乘法法则"
    highlight_phrases:
      - "B \\neq 0"
      - "D \\neq 0"
    red_conclusion_phrases:
      - "分式与分式相乘，用分子的积作为积的分子，分母的积作为积的分母。"
  - title_contains: "两种策略对比"
    red_conclusion_phrases:
      - "先乘再约"
      - "先分解再约"

# 仅用于兼容旧配置，优先使用 red_conclusion_phrases。
red_conclusion_patterns: []

blue_hint_keywords:
  - 思路
  - 引导
blue_hint_patterns:
  - "^[①②③④⑤]\\s*[^，。；]*[=→]"
```

## agent 自动生成流程

1. 读取课件 MD，并定位关键条件、易错点、法则、定义和策略归纳。
2. 为每项确定其出现的页面标题，生成精确短语。
3. 写入 `skills/md2htmlyishu/configs/{章节}-{课题}.yaml`。
4. 教师可审核并微调后运行转换。

agent 生成时必须避免把“本课出现的术语”当作荧光笔词库；荧光笔回答的是“学生此处最容易漏掉或误用什么”。
