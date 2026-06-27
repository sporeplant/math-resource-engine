# Routing Rules

## 输入分类

### lesson request
→ lesson-generation-skill

### exercise request
→ 习题分析skills

### mixed request
→ workflow DAG

---

## 决策规则

IF contains "讲解 / 教学 / 设计"
→ lesson-generation-skill

IF contains "题 / 练习 / 解题"
→ 习题分析skills

IF multiple intents
→ workflow engine

---

## 禁止规则

- 禁止直接调用 workflow step
- 必须先 routing 再 skill dispatch

---

## Global Rule

If task involves "question / exercise / problem":

→ MUST route through retrieval-based Skill only
→ MUST NOT allow generative question creation
