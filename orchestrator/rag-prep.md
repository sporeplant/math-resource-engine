# RAG准备

为未来RAG系统定义所需的数据结构和接口规范。

---

## embedding对象

每个knowledge chunk 作为一个独立的 embedding 对象：
- chunk_content：文本内容
- metadata：元数据（来源、标题路径、内容类型）
- embedding_vector：向量表示（预留字段）
- 维度：取决于所选embedding模型

---

## chunk对象

```json
{
  "chunk_id": "函数本质.md-01",
  "source_file": "数学本质/函数本质.md",
  "heading_path": "函数本质 > 核心定义",
  "content": "chunk的文本内容...",
  "token_count": 450,
  "content_type": "definition",
  "embedding": null
}
```

---

## 检索入口

- 输入：知识点名称 + 任务类型（目标/评价/活动/教材分析）
- outputs：相关性排序的chunk列表
- 检索策略：先精确匹配知识点，再语义匹配相关概念
- 单次检索返回chunk数量：5-10个

---

## rerank规则

- 第一排序：知识点精确匹配（优先返回完全匹配的chunk）
- 第二排序：内容类型匹配（根据任务类型优先返回对应类型的chunk）
- 第三排序：相关性分数（待emb edding模型就绪后启用）
- 最终outputs：按排序取前N个chunk