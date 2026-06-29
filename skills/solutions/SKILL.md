---
name: textbook-question-solutions
description: Generate complete, traceable Chinese reference solutions for every explicit question and task in a selected junior-middle-school mathematics textbook lesson. Use when asked to create or update 教材问题参考解答, 教材答案库, 练习或习题解答, or answers for textbook sections such as 大家谈谈、观察与思考、一起探究、做一做、例题、练习、习题、数学活动 and 回顾与反思.
---

# 教材问题解答

按教材原文顺序，为教材中要求学生回答、判断、计算、证明、操作、作图、交流或表达的全部任务生成可追溯参考解答。

## 强制读取

1. 读取仓库根目录 `AGENTS.md`。
2. 读取 `orchestrator/skill-protocol.md` 和 `orchestrator/workflow-registry.md`。
3. 读取本目录 `skills.md` 和 `检查清单.md`。
4. 读取目标课时对应的完整教材原文及其图片。
5. 读取 `validators/solutions/rules.md`。

## 执行流程

1. 匹配唯一教材课时，不确定时先完成课题确认。
2. 按原文顺序提取全部显式问题和任务指令，拆分大题与小问，绑定相邻图片。
3. 先形成任务清单，核对栏目、顺序、数量、小问和图片依赖。
4. 判断教材是否已经给出解答：使用 `答案来源: 教材原文` 或 `答案来源: AI参考推导`。
5. 按题型模板逐题作答，不改写原题，不改变教材顺序，不补造题目。
6. 对计算、推理、证明、图形和结论进行复核。
7. 执行检查清单与专用validators，通过后写入规定目录。

## 异常处理

正常题目不写审核状态或生成状态。仅当题目残缺、图片缺失或条件无法可靠辨认时写：

```yaml
生成状态: 暂停
异常原因: "具体原因"
```

禁止猜测缺失条件或根据常见题型补题。

