# 元数据模式

统一所有outputs文件的元数据格式。

---

## 字段定义

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| lesson_id | string | 课时唯一标识 | 81-4-2-20260525 |
| chapter | string | 教材章节 | 第四章 一次函数 |
| grade | string | 年级 | 八年级 |
| topic | string | 课题 | 一次函数的概念 |
| lesson_type | string | 课型 | 新授课 |
| core_literacy | string[] | 核心素养 | [数学抽象, 直观想象] |
| cognitive_level | string | 认知层 | 基础层/中间层/拓展层 |
| difficulty | string | 难度 | 基础/中等/挑战 |
| review_status | string | 审核状态 | 未审核/初审通过/已发布 |
| version | string | 版本号 | v1.0.0 |

---

## 使用规则

- 每个outputs文件头部必须包含元数据块
- lesson_id 按 文件注册表.md 规则生成
- core_literacy 从课标中提取对应素养
- cognitive_level 标注本课时主要针对的认知层
- review_status 随审核流程自动更新
- version 按 版本控制.md 规则递增