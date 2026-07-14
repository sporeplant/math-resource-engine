# outputs 目录

`outputs/` 只存放生成产物，不存放脚本、knowledge 源资料或长期公共图片池。

## 当前结构

```text
outputs/
├── README.md
├── _demo/                         # 演示与样本
│   └── lesson-12.1.1-traditional-style-sample.md
├── lessons/                       # 新授课、常规课时资源包
│   ├── ch12/
│   │   ├── 12.1.1/                # 12.1.1 课时
│   │   ├── 12.1.2/                # 12.1.2 课时
│   │   ├── 12.2.1/                # 12.2.1 课时
│   │   └── students/              # 学生画像
│   ├── ch21/
│   │   ├── 21.6/                  # 21.6 菱形
│   │   ├── 21.7/                  # 21.7 正方形
│   │   └── ex-taxonomy.md         # 习题分类
│   └── ch22/
│       ├── 22.1/                  # 22.1 一元二次方程
│       ├── 22.2/                  # 22.2 配方法
│       ├── 22.3/                  # 22.3 公式法
│       ├── 22.4/                  # 22.4 因式分解法
│       ├── 22.5/                  # 22.5 根与系数关系
│       └── 22.6/                  # 22.6 应用
├── packages/                      # 希沃、EasiNote、PPTX 等离线/机器可读包
│   └── exam-24-25-final/          # 24-25 期末试卷
│       ├── 24-25期末试卷.json
│       ├── lesson.json
│       └── assets/
└── reviews/                       # 复习讲义、讲评课资源
    ├── review-01-02/相关          # 第01-02章复习
    ├── review-02 ~ review-12      # 第02-12讲复习（含教师版解析、课件）
    ├── 12讲_多边形与梯形复习      # 专题复习
    ├── 13讲_统计调查与直方图复习  # 专题复习（含课件、调度稿）
    └── 模拟卷讲评课               # 模拟卷讲评讲义
```

## 资源包内部

新授/课时资源包以课时为单位，每个目录可包含：

```text
{lesson_id}/
├── metadata.yaml
├── lesson-{lesson_id}-lesson-plan.md
├── lesson-{lesson_id}-courseware.md
├── lesson-{lesson_id}-question-dispatch.md
├── lesson-{lesson_id}-review-report.md
└── exports/
```

复习/讲评资源以讲次为单位，可包含：

```text
{review_id}/
├── metadata.yaml
├── teacher-handout.md
├── student-handout.md
├── courseware.md
├── question-dispatch.md
└── exports/
```

## 图片规则

正式 Markdown 默认引用 CDN：

```markdown
![图注](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/xxx.jpg)
```

图片源文件统一维护在 `knowledge/images/`。离线软件包需要本地图片时，在 `outputs/packages/{package_id}/assets/` 中生成副本。

## 禁止

- 在 `outputs/` 根目录新增正式资源文件。
- 在 `outputs/` 下放 Python、PowerShell、批处理等脚本。
- 新增 `outputs/images/`、`outputs/assets/` 作为公共图片池。
- 新增嵌套的 `outputs/outputs/`。
