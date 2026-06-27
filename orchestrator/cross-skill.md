# 跨Skill契约

定义各Skill之间的输入outputs接口。

---

## 1. learning-outcome outputs给谁

**outputs内容**：分层学习目标（基础层、中间层、拓展层）

**下游消费方**：
- 评价设计skills（作为输入）
- 活动设计skills（作为参考）
- 教学设计skills（作为输入）
- 一致性validators（作为校验基准）

**outputs格式**：按 skills.md 中的outputs模板，每条目标以"能……"开头

---

## 2. assessment outputs给谁

**outputs内容**：分层评价任务（目标-任务-成功标准）

**下游消费方**：
- 活动设计skills（评价方式约束活动设计）
- 教学设计skills（嵌入课时方案）
- 一致性validators（校验目标-评价一致性）

**outputs格式**：按 skills.md 中的outputs模板，每项评价有明确成功标准

---

## 3. activity outputs给谁

**outputs内容**：分层教学活动（活动名称、类型、步骤、反馈节点）

**下游消费方**：
- 教学设计skills（嵌入课时流程）
- 一致性validators（校验评价-活动一致性）
- 课件设计skills（转化为PPT活动页）

**outputs格式**：按 skills.md 中的outputs模板

---

## 4. lesson-design 如何引用前置结果

- 直接引用 学习目标skills 的outputs作为课时目标
- 直接引用 评价设计skills 的outputs作为评价环节
- 直接引用 活动设计skills 的outputs作为课堂活动
- 引用方式：在对应文件头部注明 source 和 lesson_id

---

## 5. validator 如何读取前置状态

- 从 会话记忆.md 读取当前课时状态
- 从 会话记忆.md 读取已完成的Skill列表
- 从对应Skill的outputs文件读取待审核内容
- 从 元数据模式.md 读取目标文件的元数据
- 从 质量门.md 获取审核标准