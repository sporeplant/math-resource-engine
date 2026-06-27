# 教学活动时间validators

## 验证项

- [ ] 第一层流程总览、第二层活动标题和 `time_budget.total` 是否一致
- [ ] 每个活动是否标记 `time_priority: core | flex | backup`
- [ ] 每个活动是否完整分配指令、学生作答、互动、反馈和转换时间
- [ ] 时间是否非负、使用0.5分钟精度，且分项之和等于总时间
- [ ] 是否按教学运行画像或至少3条同类实测记录估算现场耗时
- [ ] 核心任务预计耗时是否不超过40分钟
- [ ] 全部任务超时时，是否能按 `backup → flex` 后移而保留核心任务

## 结果规则

- 通过：全部计划任务预计耗时不超过40分钟
- 有条件通过：核心任务不超过40分钟，但需后移弹性或备用任务
- 不通过：核心任务超过40分钟、后移弹性任务后仍超时，或必要时间字段缺失
- 高风险提示：预计总耗时超过32分钟，但不单独改变结论

## 执行命令

```powershell
python tools/validate_lesson_timing.py 教学设计.md `
  --runtime-profile students/profile.md `
  --timing-log students/timing.md
```
