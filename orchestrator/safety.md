# 安全规则

定义系统中必须遵守的安全约束。

---

## 1. 禁止覆盖原始教材

- 教材分析Skill只能读取教材文件，禁止写入或修改
- 原始教材文件所在的目录设置为只读
- 系统生成的outputs文件必须存放在独立的 outputs/ 目录

---

## 2. 禁止覆盖审核结果

- 审核报告生成后锁定，不可被后续流程覆盖或修改
- 需要修改时生成新版本，保留历史版本
- 审核结果版本号按 版本控制.md 递增

---

## 3. 禁止Skill互相写入

- 每个Skill只能写入自己的outputs文件
- Skill A 不能修改 Skill B 的outputs
- 跨Skill数据传递通过标准接口（文件读取），不直接写入
- outputs文件权限：生成Skill可写，其它Skill只读

---

## 4. 禁止跳过Validator

- 所有设计Skill的outputs必须经过对应Validator
- 禁止配置快速通道绕过审核
- 一致性校验是最终发布的必要条件
- 任何绕过行为视为严重违规

---

## 5. 禁止无状态outputs

- 所有outputs文件头部必须包含 元数据模式.md 定义的元数据
- 元数据必须包含 lesson_id、version、review_status
- 无元数据的outputs视为无效outputs，不被下游接收