# Data Source Policy

## 1. 数据源优先级

1. textbook corpus（最高优先级）
2. exercise bank（第二优先级）
3. archived exam questions（第三优先级）

---

## 2. 禁止数据来源

- ❌ LLM生成内容
- ❌ 外部未标注题库
- ❌ 模拟题
- ❌ 类题生成

---

## 3. 数据使用规则

### Strict Retrieval Mode

所有题目必须：

- 先检索
- 再引用
- 不允许生成

---

## 4. Skill 数据访问权限

| Skill | 是否允许访问题库 |
|------|----------------|
| 习题分析skills | YES |
| lesson-generation-skill | YES (only examples) |
