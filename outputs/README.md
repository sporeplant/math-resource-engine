# outputs 目录规则

`outputs/` 只存放生成产物，不存放脚本、knowledge 源资料或长期公共图片池。

## 推荐结构

```text
outputs/
├── lessons/                 # 新授课、常规课时资源包
│   └── ch22/
│       └── 22.6/
├── reviews/                 # 复习讲义、讲评课、试卷讲评资源包
│   └── review-01-02/
├── packages/                # 希沃、EasiNote、PPTX 等离线/机器可读包
│   └── exam-24-25-final/
├── _demo/                   # 演示、渲染验证、截图留档
└── _tmp/                    # 临时中间文件
```

## 资源包内部

新授/课时资源包：

```text
metadata.yaml
lesson-{lesson_id}-lesson-plan.md
lesson-{lesson_id}-courseware.md
lesson-{lesson_id}-question-dispatch.md
lesson-{lesson_id}-review-report.md
exports/
```

复习/讲评资源包：

```text
metadata.yaml
teacher-handout.md
student-handout.md
courseware.md
question-dispatch.md
exports/
```

`exports/` 放 `.docx`、`.pdf`、`.pptx` 等导出成品。源 Markdown 留在资源包根部，便于继续编辑。

## 图片规则

正式 Markdown 默认引用 CDN：

```markdown
![图注](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/xxx.jpg)
```

图片源文件统一维护在 `knowledge/images/`。导出 `.docx`、`.pdf` 时优先从 CDN 拉取并嵌入；希沃、EasiNote、PPTX 等需要离线打包时，才在 `outputs/packages/{package_id}/assets/` 中生成本地副本。

## 禁止

- 在 `outputs/` 根目录新增正式资源文件。
- 在 `outputs/` 下放 Python、PowerShell、批处理等脚本。
- 新增 `outputs/images/`、`outputs/assets/` 作为公共图片池。
- 新增嵌套的 `outputs/outputs/`。
