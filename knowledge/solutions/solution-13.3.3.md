---
content_type: textbook_solution
lesson_id: "13.3.3"
lesson_name: "全等三角形的判定（第三课时）"
command: 教材问题解答
workflow_version: v2
source_files:
  - "knowledge/textbooks/textbook-schedule.md"
  - "knowledge/textbooks/ch13/textbook-13.3-3.md"
created_at: "2026-06-30 10:05"
---

# 全等三角形的判定（第三课时）教材问题参考解答

## 教材任务清单

| 教材顺序 | question_id | 教材位置 | 任务类型 | 图片依赖 | 答案来源 |
|---:|---|---|---|---|---|
| 1 | 13.3.3-一起探究-1 | 一起探究 | 探究说明题 | b475cd90...jpg | 教材原文 |
| 2 | 13.3.3-判定定理-1 | 判定定理证明 | 证明题 | cd67c031...jpg | 教材原文 |
| 3 | 13.3.3-例2 | 例2 | 证明题 | 7ae417f6...jpg | 教材原文 |
| 4 | 13.3.3-练习-1 | 练习第1题 | 条件补充题 | 22d33d24...jpg | AI参考推导 |
| 5 | 13.3.3-练习-2 | 练习第2题 | 证明题 | 7c408899...jpg | AI参考推导 |
| 6 | 13.3.3-习题A-1-1 | 习题A组第1题第（1）问 | 反例说明题 | 无 | AI参考推导 |
| 7 | 13.3.3-习题A-1-2 | 习题A组第1题第（2）问 | 反例说明题 | 无 | AI参考推导 |
| 8 | 13.3.3-习题A-1-3 | 习题A组第1题第（3）问 | 反例说明题 | 无 | AI参考推导 |
| 9 | 13.3.3-习题A-2 | 习题A组第2题 | 证明题 | d2513cab...jpg | AI参考推导 |
| 10 | 13.3.3-习题A-3 | 习题A组第3题 | 证明题 | 03dfc238...jpg | AI参考推导 |
| 11 | 13.3.3-习题A-4 | 习题A组第4题 | 证明题 | 65c35c55...jpg | AI参考推导 |
| 12 | 13.3.3-习题B-5 | 习题B组第5题 | 证明题 | e1e6fdb9...jpg；1d5f2f5f...jpg | AI参考推导 |
| 13 | 13.3.3-习题B-6 | 习题B组第6题 | 判断证明题 | 801a2f36...jpg | AI参考推导 |

## 参考解答

### 一起探究

```yaml
question_id: "13.3.3-一起探究-1"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "一起探究"
教材顺序: 1
任务类型: 探究说明题
认知层级: 中间层
答案来源: 教材原文
```

**原题**：如图 $13.3-8$，在 $\triangle ABC$ 和 $\triangle A'B'C'$ 中，$\angle B=\angle B'$，$BC=B'C'$，$\angle C=\angle C'$。把 $\triangle ABC$ 和 $\triangle A'B'C'$ 叠放在一起，它们能够完全重合吗？请提出你的猜想，并试着说明理由。

**参考解答**：能够完全重合。使边 $BC$ 落在边 $B'C'$ 上，由 $BC=B'C'$ 可得 $B$ 与 $B'$、$C$ 与 $C'$ 分别重合；由 $\angle B=\angle B'$，$\angle C=\angle C'$，可得边 $BA$ 落在边 $B'A'$ 上，边 $CA$ 落在边 $C'A'$ 上；两条直线相交只有一个交点，所以点 $A$ 与点 $A'$ 重合。因此 $\triangle ABC\cong\triangle A'B'C'$。

### 判定定理证明

```yaml
question_id: "13.3.3-判定定理-1"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "判定定理证明"
教材顺序: 2
任务类型: 证明题
认知层级: 中间层
答案来源: 教材原文
```

**原题**：已知：如图 $13.3-9$，在 $\triangle ABC$ 和 $\triangle A'B'C'$ 中，$\angle A=\angle A'$，$\angle B=\angle B'$，$BC=B'C'$。求证：$\triangle ABC\cong\triangle A'B'C'$。

**参考解答**：因为 $\angle A+\angle B+\angle C=180^\circ$，$\angle A'+\angle B'+\angle C'=180^\circ$，又 $\angle A=\angle A'$，$\angle B=\angle B'$，所以 $\angle C=\angle C'$。在 $\triangle ABC$ 和 $\triangle A'B'C'$ 中，
$$
\begin{cases}
\angle B=\angle B',\\
BC=B'C',\\
\angle C=\angle C',
\end{cases}
$$
所以 $\triangle ABC\cong\triangle A'B'C'(ASA)$。

### 例2

```yaml
question_id: "13.3.3-例2"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "例2"
教材顺序: 3
任务类型: 证明题
认知层级: 基础层
答案来源: 教材原文
```

**原题**：已知：如图 $13.3-10$，$AD=BE$，$\angle A=\angle FDE$，$BC\parallel EF$。求证：$\triangle ABC\cong\triangle DEF$。

**参考解答**：因为 $AD=BE$，所以 $AD+BD=BE+BD$，即 $AB=DE$。因为 $BC\parallel EF$，所以 $\angle ABC=\angle E$。在 $\triangle ABC$ 和 $\triangle DEF$ 中，
$$
\begin{cases}
\angle A=\angle FDE,\\
AB=DE,\\
\angle ABC=\angle E,
\end{cases}
$$
所以 $\triangle ABC\cong\triangle DEF(ASA)$。

### 练习第1题

```yaml
question_id: "13.3.3-练习-1"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "练习第1题"
教材顺序: 4
任务类型: 条件补充题
认知层级: 基础层
答案来源: AI参考推导
```

**原题**：如图，$AB$，$CD$ 相交于点 $O$，$OA=OD$。要使 $\triangle OAC\cong\triangle ODB$ 还需要添加一个条件，这个条件是什么？

**参考解答**：可添加 $OC=OB$。因为 $\angle AOC=\angle DOB$，且 $OA=OD$，$OC=OB$，所以 $\triangle OAC\cong\triangle ODB(SAS)$。也可添加适合图形对应关系的一组角相等，用 $ASA$ 或 $AAS$ 判定。

### 练习第2题

```yaml
question_id: "13.3.3-练习-2"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "练习第2题"
教材顺序: 5
任务类型: 证明题
认知层级: 基础层
答案来源: AI参考推导
```

**原题**：已知：如图，$AB$，$CD$ 相交于点 $E$，$EC=ED$，$\angle C=\angle D$。求证：$\triangle AEC\cong\triangle BED$。

**参考解答**：因为 $AB$ 与 $CD$ 相交于点 $E$，所以 $\angle AEC=\angle BED$。在 $\triangle AEC$ 和 $\triangle BED$ 中，
$$
\begin{cases}
\angle AEC=\angle BED,\\
EC=ED,\\
\angle C=\angle D,
\end{cases}
$$
所以 $\triangle AEC\cong\triangle BED(ASA)$。

### 习题A组第1题第（1）问

```yaml
question_id: "13.3.3-习题A-1-1"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "习题A组第1题第（1）问"
教材顺序: 6
任务类型: 反例说明题
认知层级: 基础层
答案来源: AI参考推导
```

**原题**：有两个角和一条边分别相等的两个三角形全等。

**参考解答**：该命题是假命题。如果没有说明相等边与相等角的对应位置，可能不是同一对应关系，不能直接判定全等。反例可取两个三角形中有两个角数值相等、一条边数值相等，但这条边在两个三角形中对应位置不同，三角形不一定完全重合。

### 习题A组第1题第（2）问

```yaml
question_id: "13.3.3-习题A-1-2"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "习题A组第1题第（2）问"
教材顺序: 7
任务类型: 反例说明题
认知层级: 基础层
答案来源: AI参考推导
```

**原题**：有三个角分别相等的两个三角形全等。

**参考解答**：该命题是假命题。两个三角形可以三个角分别相等，但一个是另一个按比例放大的图形，形状相同、大小不同，不能完全重合，所以不全等。

### 习题A组第1题第（3）问

```yaml
question_id: "13.3.3-习题A-1-3"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "习题A组第1题第（3）问"
教材顺序: 8
任务类型: 反例说明题
认知层级: 基础层
答案来源: AI参考推导
```

**原题**：有一条边和一个锐角分别相等的两个直角三角形全等。

**参考解答**：该命题是假命题。如果只给出一条边和一个锐角相等，但未说明这条边与这个锐角的对应位置，不能保证两个直角三角形完全重合。例如一个直角三角形中相等的边是锐角的邻边，另一个中相等的边是锐角的对边，就可能不全等。

### 习题A组第2题

```yaml
question_id: "13.3.3-习题A-2"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "习题A组第2题"
教材顺序: 9
任务类型: 证明题
认知层级: 中间层
答案来源: AI参考推导
```

**原题**：已知：如图，$AD=AE$，$\angle ADC=\angle AEB$。求证：$BD=CE$。

**参考解答**：因为 $\angle ADC=\angle AEB$，且 $\angle A$ 为公共角，所以 $\triangle ADC$ 与 $\triangle AEB$ 有两角分别相等。又 $AD=AE$，所以 $\triangle ADC\cong\triangle AEB(AAS)$。因此 $AC=AB$。于是 $BD=AB-AD$，$CE=AC-AE$，又 $AB=AC$，$AD=AE$，所以 $BD=CE$。

### 习题A组第3题

```yaml
question_id: "13.3.3-习题A-3"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "习题A组第3题"
教材顺序: 10
任务类型: 证明题
认知层级: 中间层
答案来源: AI参考推导
```

**原题**：已知：如图，$l_1\parallel l_2$，$AC\perp l_1$，$AC\perp l_2$，垂足分别为 $A,C$，点 $B$ 在 $AC$ 上，且 $AB=BC$，过点 $B$ 的任一直线与 $l_1$，$l_2$ 分别交于点 $M,N$。求证：$MB=NB$。

**参考解答**：因为 $l_1\parallel l_2$，所以 $\angle MAB=\angle BCN=90^\circ$，且 $\angle AMB=\angle CNB$。又 $AB=BC$，所以 $\triangle ABM\cong\triangle CBN(AAS)$。因此 $MB=NB$。

### 习题A组第4题

```yaml
question_id: "13.3.3-习题A-4"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "习题A组第4题"
教材顺序: 11
任务类型: 证明题
认知层级: 中间层
答案来源: AI参考推导
```

**原题**：已知：如图，$AB\perp AD$，$AC\perp AE$，$AB=AD$，$\angle B=\angle D$。求证：$BC=DE$。

**参考解答**：因为 $AB\perp AD$，$AC\perp AE$，所以 $\angle BAD=90^\circ$，$\angle CAE=90^\circ$，从而 $\angle BAC=\angle DAE$。在 $\triangle ABC$ 和 $\triangle ADE$ 中，$\angle B=\angle D$，$AB=AD$，$\angle BAC=\angle DAE$，所以 $\triangle ABC\cong\triangle ADE(ASA)$。因此 $BC=DE$。

### 习题B组第5题

```yaml
question_id: "13.3.3-习题B-5"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "习题B组第5题"
教材顺序: 12
任务类型: 证明题
认知层级: 拓展层
答案来源: AI参考推导
```

**原题**：已知：如图，在 $\triangle ABC$ 和 $\triangle DEF$ 中，$AB=DE$，$BC=EF$，$AC=DF$，$\angle ABM=\angle CBM$，$\angle DEN=\angle FEN$。求证：$BM=EN$。

**参考解答**：由 $AB=DE$，$BC=EF$，$AC=DF$，得 $\triangle ABC\cong\triangle DEF(SSS)$，所以 $\angle ABC=\angle DEF$。又 $\angle ABM=\angle CBM$，$\angle DEN=\angle FEN$，可知 $BM$ 与 $EN$ 分别是对应角的平分线。结合 $AB=DE$，$\angle ABM=\angle DEN$，且对应角相等，可得相关小三角形全等，从而 $BM=EN$。

### 习题B组第6题

```yaml
question_id: "13.3.3-习题B-6"
source_id: "教材原文_13.3.3_全等三角形的判定"
source_type: textbook
教材位置: "习题B组第6题"
教材顺序: 13
任务类型: 判断证明题
认知层级: 拓展层
答案来源: AI参考推导
```

**原题**：已知：如图，点 $D$ 在 $\triangle ABC$ 的边 $BC$ 上，$BE\perp AD$，$CF\perp AD$，垂足分别为 $E,F$，$BE=CF$。请判断 $AD$ 是不是 $\triangle ABC$ 的中线。如果是，请给出证明。

**参考解答**：是。因为 $BE\perp AD$，$CF\perp AD$，所以 $\angle BED=\angle CFD=90^\circ$。又因为 $\angle BDE=\angle CDF$，$BE=CF$，所以 $\triangle BDE\cong\triangle CDF(AAS)$。因此 $BD=DC$。点 $D$ 在 $BC$ 上且 $BD=DC$，所以 $D$ 是 $BC$ 的中点，$AD$ 是 $\triangle ABC$ 的中线。

## 覆盖统计

| 项目 | 数量 |
|---|---:|
| 教材任务清单条目 | 13 |
| 参考解答条目 | 13 |
| 暂停生成条目 | 0 |
