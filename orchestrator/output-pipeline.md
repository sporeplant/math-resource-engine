# outputs流水线

定义各阶段outputs文件、顺序、依赖关系与审核状态。

---

## 1. 各阶段outputs文件

`/lesson-collab` 的知识分析、学习目标、评价设计、活动设计为会话内中间环节，不产生独立文件，最终汇入教学设计。

| 阶段 | 产出文件 | 格式 |
|------|----------|------|
| 课时设计 | lesson-{id}-lesson-plan.md | Markdown |
| Markdown课件 | lesson-{id}-courseware.md | Markdown |
| 课堂提问调度稿 | lesson-{id}-dispatch.md | Markdown |

---

## 2. outputs顺序

1. 课时设计（`/lesson-collab`，内部含知识分析→学习目标→评价设计→活动设计流水线）
2. Markdown课件（`/courseware-collab`，需人工审核通过的教学设计）
3. 课堂提问调度稿（`/courseware-collab`，与课件同步生成）

---

## 3. outputs依赖关系

- 课时设计依赖知识分析→学习目标→评价任务→教学活动（均为会话内环节，不产生独立文件）
- Markdown课件依赖人工审核通过的课时设计
- 课堂提问调度稿与课件同步生成（`build_courseware.py`）

---

## 4. outputs审核状态

| 状态 | 含义 |
|------|------|
| draft | 初始草稿，尚在生成中 |
| pending_review | 待审核，已提交到对应Validator |
| reviewed_pass | 审核通过 |
| reviewed_conditional | 有条件通过，附修改建议 |
| reviewed_fail | 审核不通过，需回退修正 |
| published | 最终发布版本 |

---

## 5. 最终资源包结构

```
outputs/lessons/ch{章节号}/{id}/
├── metadata.yaml              # 元数据
├── lesson-{id}-lesson-plan.md
├── lesson-{id}-courseware.md
├── lesson-{id}-dispatch.md
└── exports/
    ├── lesson-{id}-courseware.html
    ├── lesson-{id}-courseware.json
    └── assets/
        └── slide_01.png ~ slide_N.png
```

正式 Markdown 图片默认使用 CDN URL，不在资源包内常驻 `images/`。离线资源（截图、JSON 等）统一归入 `exports/`。
