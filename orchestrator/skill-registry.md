# Skill注册表

系统中所有Skill的登记信息。

---

| 名称 | 职责 | 输入 | outputs | 依赖 | Validator | 状态 | 版本 |
|------|------|------|------|------|-----------|------|------|
| 学习目标skills | 生成分层学习目标 | 教材章节、课标要求、学情数据 | 分层学习目标（基础/中间/拓展层） | 教材分析skills | 学习目标validators | active | v1.0 |
| 评价设计skills | 设计分层评价任务 | 分层学习目标、评价模式 | 分层评价任务 + 成功标准 | 学习目标skills | 评价validators | active | v1.0 |
| 活动设计skills | 设计分层且时间可执行的教学活动 | 学习目标、评价任务、学情、教学运行画像 | 分层教学活动 + 反馈节点 + 分项时间预算 | 学习目标skills, 评价设计skills | 活动validators, 教学活动时间validators | active | v1.1 |
| 教学设计skills | 生成双层完整课时方案 | 目标、评价、活动、课型结构 | 课堂实施导航 + 完整结构化设计 | 学习目标skills, 评价设计skills, 活动设计skills | 教学设计validators | active | v1.1 |
| 协作式教学设计skills | 通过确认门编排双层教学设计 | 教材、课标、学情、教师逐门确认 | 课堂实施导航 + 完整结构化设计 | 教学设计skills, 提问质量skills | 教学设计validators | active | v1.1 |
| 教材分析skills | 分析教材知识结构 | 教材章节内容 | 教材分析报告（10个维度） | 无（独立） | 无 | active | v1.0 |
| 习题分析skills | 分析习题与解题 | knowledge/workbooks/ 对应章节 + 常见错误 | 习题分析报告（8个维度） | 无（独立，outputs供给评价、活动、课件） | 无 | active | v1.0 |
| 课件设计skills | 设计 Markdown 课件，内含分层提问 | 人工审核通过的课时设计方案、学生成绩数据 | Markdown 课件（含分层提问） | 教学设计skills, 分层提问skills, 图片资源skills | 课件validators | active | v2.0 |
| 协作式课件skills | 通过确认门生成课件与课堂提问参考答案 | 人工审核通过的教学设计、教材、学生数据、教师逐门确认 | Markdown 课件 + 课堂提问参考答案 | 课件设计skills, 参考答案生成skills, 分层提问skills | 课件validators, 参考答案validators | active | v1.0 |
| 分层提问skills | 提供分层提问规则，分配学生姓名 | 学生成绩数据、提问历史记录 | 学生选取结果、更新提问历史 | 无 | 无 | active | v1.0 |
| 参考答案生成skills | 生成课堂提问参考答案文件 | 教学设计、学生选取结果、题源 | {课时名}_课堂提问参考答案.md | 分层提问skills、习题分析skills | 参考答案validators | active | v1.0 |
| 教材问题解答skills | 按教材顺序生成全部问题的参考解答 | 教材课时原文、教材图片、前置教材知识 | 教材问题参考解答文件 | 无（独立） | 教材问题解答validators | active | v1.0 |
| 复习课讲义整理skills | 合并新授课讲义生成综合复习讲义 | 讲义编号或名称、源讲义文件 | 复习讲义 Markdown 文件 | 复习课讲义整理skills本体规则 | 复习讲义validators | active | v1.0 |
| 板书设计skills | 设计板书布局 | 课时设计方案 | 板书布局方案 | 教学设计skills | 无 | archived | v1.0 |
| 图片资源skills | 定义图片引用、路径、布局的全局规则 | 教材源文件 | 图片引用规则集 | 无（独立，被课件设计skills、教材文件、习题文件等多处引用） | 图片资源validators | active | v1.0 |
| 数学活动课设计skills | 为综合与实践领域生成项目式学习活动方案 | 核心知识领域、年级、课时 | 活动方案（含四阶段流程、评价量规、任务单） | 无（独立应用，替代标准课时流程） | 无 | archived | v1.0 |
| 临界生帮扶表skills | 根据学生成绩和学习内容生成临界生分工帮扶表 | 责任教师、任教班级、教材章节、学生成绩数据 | 临界生分工表-YYYY-MM-DD.md | 无（独立） | 无 | active | v1.0 |
| DOCX排版导出skills | 将 Markdown 讲义导出为 A4 双栏 DOCX | Markdown 讲义文件路径 | DOCX 文件 | Pandoc, python-docx, matplotlib | 无 | active | v1.0 |
