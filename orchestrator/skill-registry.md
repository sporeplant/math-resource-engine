# Skill注册表

系统中所有Skill的登记信息。

---

| 名称 | 职责 | 输入 | outputs | 依赖 | Validator | 状态 | 版本 |
|------|------|------|------|------|-----------|------|------|
| 教材原文拆解skills | 将 MinerU 转换的单章教材 Markdown 大文件按课时拆分，并转换 HTML 表格 | `knowledge/textbooks/` 或其他目录中的单章教材 Markdown、大章文件、学期标识 | `textbook-{章节}.{小节}-{课时号}.md`、`textbook-ch{章号}-{活动名称}.md`、`textbook-ch{章号}-review-{课时号}.md` | 无（独立） | 自检清单 | active | v1.0 |
| 练习册题库拆解skills | 将 MinerU 转换的单章练习册 Markdown 大文件按课时拆分，并迁移图片 | 练习册 Markdown 大章文件 | `workbook-{章节}.{小节}-{课时号}.md`、`workbook-{章节}.{小节}.md`、`workbook-ch{章号}-review.md` | 无（独立） | `tools/validate-workbook-split.py` + 自检清单 | active | v1.0 |
| 练习册参考答案拆解skills | 将 MinerU 转换的练习册参考答案 Markdown 大文件按课时、回顾和测试卷拆分，并迁移图片 | 练习册答案 Markdown 大文件 | `workbook-answer-{章节}.{小节}-{课时号}.md`、`workbook-answer-ch{章号}-review.md`、`workbook-answer-ch{章号}-unit-test.md` | 无（独立） | `tools/validate-workbook-answer-split.py` + 自检清单 | active | v1.0 |
| 练习册逐题索引skills | 对齐练习册题库与答案，生成稳定 `WB-...` 题号和答案映射 | `knowledge/workbooks/` + `knowledge/workbook-answers/` | `knowledge/workbook-index/workbook-index-*.yaml` | 练习册题库拆解skills, 练习册参考答案拆解skills | `tools/validate-workbook-index.py` + 自检清单 | active | v1.0 |
| 学习目标skills | 生成分层学习目标 | 教材章节、课标要求、学情数据、教材问题解答（含台阶分析） | 分层学习目标（基础/中间/拓展层） | 教材分析skills, 教材问题解答skills | 学习目标validators | active | v1.1 |
| 评价设计skills | 设计分层评价任务 | 分层学习目标、评价模式、教材-练习册资源盘点、教材问题解答（含台阶分析） | 分层评价任务 + 成功标准 | 学习目标skills, 双资源调度策略, 教材问题解答skills | 评价validators | active | v1.2 |
| 活动设计skills | 设计分层且时间可执行的教学活动 | 学习目标、评价任务、学情、教学运行画像、教材问题解答（含台阶分析） | 分层教学活动 + 反馈节点 + 分项时间预算 | 学习目标skills, 评价设计skills, 教材问题解答skills | 活动validators, 教学活动时间validators | active | v1.2 |
| 教学设计skills | 生成传统正文 + 后台折叠结构的课时方案 | 目标、评价、活动、课型结构、教材-练习册资源盘点、教材问题解答（含台阶分析） | 传统教学设计正文 + 完整结构化设计 | 学习目标skills, 评价设计skills, 活动设计skills, 双资源调度策略, 教材问题解答skills | 教学设计validators | active | v1.3 |
| 协作式教学设计skills | 通过确认门编排传统正文 + 后台折叠结构教学设计 | 教材、课标、学情、教师逐门确认、教材-练习册资源盘点、教材问题解答（含台阶分析） | 传统教学设计正文 + 完整结构化设计 | 教学设计skills, 提问质量skills, 双资源调度策略, 教材问题解答skills | 教学设计validators | active | v1.3 |
| 教材分析skills | 分析教材知识结构 | 教材章节内容 | 教材分析报告（10个维度） | 无（独立） | 无 | active | v1.0 |
| 习题分析skills | 分析习题与解题 | knowledge/workbooks/ 对应章节 + 常见错误 | 习题分析报告（8个维度） | 无（独立，outputs供给评价、活动、课件） | 无 | active | v1.0 |
| 课件设计skills | 设计 Markdown 课件，内含分层提问 | 人工审核通过的课时设计方案、学生成绩数据 | Markdown 课件（含分层提问） | 教学设计skills, 分层提问skills, 图片资源skills | 课件validators | active | v2.0 |
| 协作式课件skills | 通过确认门生成课件与课堂提问调度稿 | 人工审核通过的教学设计、教材、学生数据、教师逐门确认 | Markdown 课件 + 课堂提问调度稿 | 课件设计skills, 课堂提问调度稿生成skills, 分层提问skills | 课件validators, 课堂提问调度稿validators | active | v1.0 |
| 分层提问skills | 提供分层提问规则，分配学生姓名 | 学生成绩数据、提问历史记录 | 学生选取结果、更新提问历史 | 无 | 无 | active | v1.0 |
| 课堂提问调度稿生成skills | 生成课堂提问调度稿文件 | 教学设计、学生选取结果、题源 | {课时名}_课堂提问调度稿.md | 分层提问skills、习题分析skills | 课堂提问调度稿validators | active | v1.0 |
| 教材问题解答skills | 按教材顺序生成全部问题的参考解答，并执行例题-习题全链台阶分析 | 教材课时原文、教材图片、前置教材知识 | 教材问题参考解答文件（含例题-习题台阶分析） | 无（独立，outputs供给学习目标、评价、活动、教学设计、课件） | 教材问题解答validators | active | v1.1 |
| 复习课讲义整理skills | 合并新授课讲义生成综合复习讲义 | 讲义编号或名称、源讲义文件 | 复习讲义 Markdown 文件 | 复习课讲义整理skills本体规则 | 复习讲义validators | active | v1.0 |
| 图片资源skills | 定义图片引用、路径、布局的全局规则 | 教材源文件 | 图片引用规则集 | 无（独立，被课件设计skills、教材文件、习题文件等多处引用） | 图片资源validators | active | v1.0 |
| 临界生帮扶表skills | 根据学生成绩和学习内容生成临界生分工帮扶表 | 责任教师、任教班级、教材章节、学生成绩数据 | 临界生分工表-YYYY-MM-DD.md | 无（独立） | 无 | active | v1.0 |
| DOCX导出skills | 将 Markdown 复习讲义/教师版解析导出为单栏或 A4 双栏紧凑 DOCX | Markdown 文件路径、输出模式（single/compact/both） | `{文件名}.docx`、`{文件名}_分栏压缩.docx` | tools/review_docx_pipeline.py, tools/md2docx.py, tools/compact_review_docx.py, Pandoc, python-docx, matplotlib | 无 | active | v1.0 |
| 栏目图标清除skills | 清除教材原文 MD 中栏目标题前的图标图片引用及图片文件 | 教材原文 MD 目录、栏目列表（可选） | 修改后的 MD 文件（移除图标引用行）、已删除图片文件 | tools/remove_section_icons.py | 自检清单 | active | v1.0 |
| 一数风格HTML课件skills | 将课件 Markdown 转换为一数风格 HTML 投屏页面（1920×1080，手写板书风） | 课件 MD 文件 | 同目录 `.html` 文件 | tools/md2htmlyishu.py, skills/md2htmlyishu/template.html | 自检清单 (checklist.md) | active | v1.0 |
| HTML转希沃skills | 将 HTML 课件转为希沃白板可导入包（JSON + 逐页PNG截图） | HTML 课件文件路径 | `{HTML主名}.json` + `assets/slide_*.png` | tools/html_to_seewo.py | Playwright 截图验证 | active | v1.0 |

