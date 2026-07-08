# 命名规范

统一系统中各类资源的命名规则。

---

## Skill命名

- 格式：`{领域}-{功能}-skill`
- 全部小写，连字符连接
- 示例：`学习目标skills`, `评价设计skills`

## Validator命名

- 格式：`{领域}-{功能}-validator`
- 全部小写，连字符连接
- 示例：`学习目标validators`, `一致性validators`

## Knowledge命名

- knowledge目录：使用 snake_case，多个单词用下划线连接
- 知识文件：使用中文命名，清晰表达内容
- 示例：`knowledge/learning-theory/class-profile.md`, `math-essence/functions.md`

## outputs文件命名

- 格式：`lesson-{lesson_id}-{功能描述}.md`
- 全部小写，连字符连接
- 示例：`lesson-8-1-04-02-01-2505-outcomes.md`

## outputs资源包命名

- 新授/课时资源包：`outputs/lessons/ch{章节号}/{lesson_id}/`
- 复习/讲评资源包：`outputs/reviews/{review_id}/`
- 软件或离线导出包：`outputs/packages/{package_id}/`
- 临时中间文件：`outputs/_tmp/`
- 演示和渲染验证：`outputs/_demo/`

`outputs/` 根目录不直接放正式 Markdown、脚本或图片公共池。

## 图片命名

- 格式：`{lesson_id}-{序号}-{描述}.png`
- 序号从 01 开始
- 描述使用英文或拼音
- 示例：`8-1-04-02-01-2505-01-function-graph.png`
- 正式 Markdown 默认引用 `knowledge/images/` 对应 CDN URL；仅离线软件包在 `outputs/packages/{package_id}/assets/` 中生成本地图片副本。
