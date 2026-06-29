# 流水线

本文件不再维护独立流程图。系统唯一权威工作流见：

> `orchestrator/workflow-registry.md`

---

## 1. 命令流水线

### `/lesson-collab`

执行教学设计生成流水线，终点是：

- outputs `outputs/{课时名}_完整教学设计.md`
- `review_status: pending_human_review`

`/lesson-collab` 不生成课件、不生成课堂提问参考答案、不执行课件validators。

### `/courseware-collab`

执行课件生成流水线，前置条件是：

- 已存在 `outputs/{课时名}_完整教学设计.md`
- 教学设计元数据为 `review_status: 审核通过`

`/courseware-collab` 只生成：

- `outputs/{课时名}_课件.md`
- `outputs/{课时名}_课堂提问参考答案.md`

---

## 2. 串行规则

- `/lesson-collab` 必须按 `工作流注册表.md` 的协作式教学设计顺序执行。
- `/courseware-collab` 必须在人工审核通过后执行。
- 学习目标、评价设计、活动设计、教学设计必须串行。
- 每个设计 Skill 必须等待上游审核通过后才能启动。
- 提问质量审查属于 `/lesson-collab` 的内嵌质量关卡。
- 分层提问分配属于 `/courseware-collab` 的内嵌子环节。

---

## 3. 并行规则

- `/lesson-collab` 中，教材分析和习题来源探索可作为知识补充并行读取，但不得绕过目标、评价、活动的串行链。
- `/courseware-collab` 中，图片准备和题源清单读取可并行，但必须在课件outputs前完成。

---

## 4. 回退规则

- 学习目标验证不通过 → 回退学习目标skills。
- 评价验证不通过 → 回退评价设计skills。
- 活动验证不通过 → 回退活动设计skills。
- 教学设计、教学法、数学、学情适配任一审核不通过 → 回退教学设计skills或问题来源skills。
- 提问质量审查不通过 → 回退教学设计skills。
- `/courseware-collab` 前置审核状态不满足 → 停止，不回退，不自动审核。
- 课件验证或图片验证不通过 → 回退课件设计skills或图片准备环节。
- 同一节点连续 3 次不通过 → 触发人工介入。

---

## 5. 最终outputs条件

`/lesson-collab`：

- 所有教学设计审核通过。
- 教学设计符合outputs合约。
- 题目来源字段完整。
- 课时总时长不超过 40 分钟。
- outputs状态为 `pending_human_review`。

`/courseware-collab`：

- 上游教学设计为 `审核通过`。
- 课件验证通过。
- 图片验证通过。
- 课堂提问参考答案与课件提问一致。
