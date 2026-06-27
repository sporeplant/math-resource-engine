# 审核协议

本协议定义自动审核与人工审核边界。工作流以 `orchestrator/workflow-registry.md` 为准。

---

## 1. 自动审核

自动审核由 Skill 检查清单、Validator 规则和 `tools/validate_output.py` 共同完成。

自动审核可以判定：

- `通过`
- `有条件通过`
- `不通过`

自动审核不得把 `review_status` 改为 `审核通过`。

---

## 2. 人工审核边界

`/lesson-collab` outputs教学设计后，状态必须为：

```yaml
review_status: pending_human_review
```

教师人工审核通过的最小动作是将其改为：

```yaml
review_status: 审核通过
```

教师退回修改时使用：

```yaml
review_status: rejected
```

系统、Agent、validators不得代替教师完成该状态变更。

---

## 3. 审核意见记录

建议在 YAML front matter 中追加：

```yaml
review_notes:
  - reviewer: ""
    date: "YYYY-MM-DD"
    result: approved | rejected
    comment: ""
```

若意见较长，可另建同名审核记录文件：

```text
outputs/{课时名}_审核记录.md
```

---

## 4. `/courseware-collab` 审核识别

`/courseware-collab` 读取教学设计时，必须检查：

```yaml
content_type: lesson
review_status: 审核通过
```

不满足时必须停止。

状态处理：

| review_status | `/courseware-collab` 行为 |
|---------------|--------------------|
| draft | 停止，提示先生成正式教学设计 |
| pending_human_review | 停止，提示先人工审核 |
| rejected | 停止，提示先修改并重新审核 |
| 审核通过 | 允许继续 |

---

## 5. 教学设计修改后的处理

人工审核通过后若再次修改教学设计正文，应执行以下任一操作：

- 保持 `审核通过`，并在 `review_notes` 记录修改者、日期、修改说明。
- 或改回 `pending_human_review`，重新人工审核。

若课件已经生成，教学设计发生实质修改后，必须重新运行 `/courseware-collab`。

---

## 6. 人工复核触发条件

- 同一自动审核节点连续 3 次不通过。
- 自动审核发现数学概念、公式、定理错误。
- 题源缺失且无法从题库补全。
- 学情数据缺失或与分层提问冲突。
- outputs涉及国家、民族、历史、地图、社会事件、公共政策、人物机构或统计数据等敏感材料。
- outputs可能存在价值导向、政策合规或公共表达风险。
- 教师主动要求复核。

---

## 7. 价值导向与政策合规审核

正式教学资源必须符合中国义务教育课程与教材管理要求，坚持正确价值导向。数学资源生成不得为追求形式而生硬注入无关口号；涉及价值导向内容时，应服务课程材料、真实情境或教材任务。

以下内容必须审慎核对来源与表述，必要时转人工复核：

- 国家、民族、历史、地图、疆域、行政区划相关表述
- 社会事件、公共政策、公共机构、人物相关材料
- 统计数据、调查数据、新闻材料或现实情境引用
- 可能引发争议、误读或不适合初中课堂呈现的案例

审核重点：

- 是否符合国家课程方案、教材管理和义务教育课堂表达要求
- 是否存在事实错误、来源不明、断章取义或过度推断
- 是否与数学学习任务自然相关，避免形式化、口号化、无关化表达
- 是否需要教师人工确认后再进入课件或正式发布
