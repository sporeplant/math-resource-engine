---
content_type: textbook_solution
lesson_id: "ch13-review-2"
lesson_name: "第十三章回顾与反思（第二课时）"
command: 教材问题解答
workflow_version: v2
source_files:
  - "knowledge/textbooks/textbook-schedule.md"
  - "knowledge/textbooks/ch13/textbook-ch13-review-2.md"
created_at: "2026-06-30 10:05"
---

# 第十三章回顾与反思（第二课时）教材问题参考解答

## 教材任务清单

| 教材顺序 | question_id | 教材位置 | 任务类型 | 图片依赖 | 答案来源 |
|---:|---|---|---|---|---|
| 1 | ch13-review-2-B-6 | 复习题B组第6题 | 判断证明题 | 358e1e2a...jpg | AI参考推导 |
| 2 | ch13-review-2-B-7 | 复习题B组第7题 | 尺规作图 | 173fb431...jpg；7a20a446...jpg | AI参考推导 |
| 3 | ch13-review-2-B-8 | 复习题B组第8题 | 证明题 | 无 | AI参考推导 |
| 4 | ch13-review-2-B-9-1 | 复习题B组第9题第（1）问 | 判断说明题 | 0a4b7c10...jpg | AI参考推导 |
| 5 | ch13-review-2-B-9-2 | 复习题B组第9题第（2）问 | 判断说明题 | 图9 | AI参考推导 |
| 6 | ch13-review-2-C-10-1 | 复习题C组第10题第（1）问 | 证明题 | 4ee1601e...jpg | AI参考推导 |
| 7 | ch13-review-2-C-10-2 | 复习题C组第10题第（2）问 | 证明题 | 图10 | AI参考推导 |
| 8 | ch13-review-2-C-10-3 | 复习题C组第10题第（3）问 | 方法设计题 | 图10 | AI参考推导 |
| 9 | ch13-review-2-C-11 | 复习题C组第11题 | 作图探究题 | 无 | AI参考推导 |

## 参考解答

### 复习题B组第6题

```yaml
question_id: "ch13-review-2-B-6"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题B组第6题"
教材顺序: 1
任务类型: 判断证明题
认知层级: 拓展层
答案来源: AI参考推导
```

**原题**：如图，在直角三角形 $ABC$ 中，$\angle C=90^\circ$，$\angle BAC=2\angle B$，$AD$ 是 $\angle BAC$ 的平分线，$DE\perp AB$ 于点 $E$。那么，$AE$ 和 $BE$ 相等吗？如果相等，请给出证明。

**参考解答**：相等。设 $\angle B=x$，则 $\angle BAC=2x$。由 $\angle C=90^\circ$ 得 $2x+x+90^\circ=180^\circ$，即 $3x=90^\circ$，$x=30^\circ$。所以 $\angle BAC=60^\circ$，$\angle B=30^\circ$。因为 $AD$ 是 $\angle BAC$ 的平分线，所以 $\angle BAD=\angle DAC=30^\circ$。于是 $\angle B=\angle BAD=30^\circ$，所以 $\triangle ABD$ 中 $AD=BD$。又 $DE\perp AB$，所以 $DE$ 是等腰三角形底边上的高，也是中线，因此 $AE=BE$。

### 复习题B组第7题

```yaml
question_id: "ch13-review-2-B-7"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题B组第7题"
教材顺序: 2
任务类型: 尺规作图
认知层级: 拓展层
答案来源: AI参考推导
```

**原题**：如图，已知直角 $\beta$。利用它作一个直角三角形，使该直角三角形的斜边等于已知线段 $a$，一个锐角等于已知角 $\alpha$。

**参考解答**：

作法：
1. 作 $\angle MBN=90^\circ$。
2. 在 $BM$ 上取一点 $C$；以 $C$ 为顶点、$BC$ 为一边，作 $\angle BCA=\alpha$，交 $BN$ 于点 $A$。
3. 此时 $\triangle ABC$ 是一个直角三角形，但需要保证斜边等于 $a$。可在作 $\angle MBN=90^\circ$ 后，先作线段 $AB=a$ 作为斜边，再以 $AB$ 为一边、$A$ 为顶点作角 $\alpha$ 的补角或直接以 $B$ 为顶点利用直角构造。具体作法：
   - 作线段 $AB=a$。
   - 以 $AB$ 为直径作圆，在圆上取点 $C$ 使 $\angle A=180^\circ-90^\circ-\alpha$... 更简洁地：
   - 作 $\angle BAP=\alpha$。
   - 过点 $B$ 作 $AP$ 的垂线，垂足为 $C$，则 $\triangle ABC$ 即为所求。

作图依据：确定斜边和一个锐角可以唯一确定直角三角形（AAS）。

### 复习题B组第8题

```yaml
question_id: "ch13-review-2-B-8"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题B组第8题"
教材顺序: 3
任务类型: 证明题
认知层级: 中间层
答案来源: AI参考推导
```

**原题**：全等三角形对应边上的高相等吗？如果相等，请写出已知、求证和证明过程。

**参考解答**：相等。

已知：$\triangle ABC\cong\triangle A'B'C'$，$AD\perp BC$ 于点 $D$，$A'D'\perp B'C'$ 于点 $D'$。

求证：$AD=A'D'$。

证明：因为 $\triangle ABC\cong\triangle A'B'C'$，所以 $AB=A'B'$，$\angle B=\angle B'$。又因为 $AD\perp BC$，$A'D'\perp B'C'$，所以 $\angle ADB=\angle A'D'B'=90^\circ$。在 $\triangle ABD$ 和 $\triangle A'B'D'$ 中，$\angle B=\angle B'$，$\angle ADB=\angle A'D'B'$，$AB=A'B'$，所以 $\triangle ABD\cong\triangle A'B'D'(AAS)$。因此 $AD=A'D'$。

### 复习题B组第9题第（1）问

```yaml
question_id: "ch13-review-2-B-9-1"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题B组第9题第（1）问"
教材顺序: 4
任务类型: 判断说明题
认知层级: 中间层
答案来源: AI参考推导
```

**原题**：如图，已知线段 $AB$，小明用三角板画出了如下的图形。$(1)$ 直线 $MN$ 与线段 $AB$ 垂直吗？为什么？

**参考解答**：垂直。因为小明以 $A$ 和 $B$ 为圆心、相同半径画弧，交点 $M$、$N$ 到 $A$、$B$ 的距离分别相等。由全等三角形的性质和线段中垂线的判定可知，$MN$ 是 $AB$ 的垂直平分线，所以 $MN\perp AB$。

### 复习题B组第9题第（2）问

```yaml
question_id: "ch13-review-2-B-9-2"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题B组第9题第（2）问"
教材顺序: 5
任务类型: 判断说明题
认知层级: 基础层
答案来源: AI参考推导
```

**原题**：$AD$ 与 $BD$ 相等吗？为什么？

**参考解答**：相等。因为 $MN$ 是 $AB$ 的垂直平分线，$D$ 是 $MN$ 与 $AB$ 的交点，即垂足和中点，所以 $AD=BD$。

### 复习题C组第10题第（1）问

```yaml
question_id: "ch13-review-2-C-10-1"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题C组第10题第（1）问"
教材顺序: 6
任务类型: 证明题
认知层级: 拓展层
答案来源: AI参考推导
```

**原题**：已知：如图，$AB=AC$，$AD=AE$，$BE$ 与 $CD$ 相交于点 $P$。$(1)$ 求证：$PC=PB$。

**参考解答**：在 $\triangle ADC$ 和 $\triangle AEB$ 中，$AD=AE$，$\angle DAC=\angle EAB$（公共角），$AC=AB$，所以 $\triangle ADC\cong\triangle AEB(SAS)$。因此 $\angle ACD=\angle ABE$。又因为 $AB=AC$，$AD=AE$，所以 $BD=CE$。在 $\triangle BDP$ 和 $\triangle CEP$ 中，$\angle BPD=\angle CPE$，$\angle PBD=\angle PCE$，$BD=CE$，所以 $\triangle BDP\cong\triangle CEP(AAS)$。因此 $PC=PB$。

### 复习题C组第10题第（2）问

```yaml
question_id: "ch13-review-2-C-10-2"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题C组第10题第（2）问"
教材顺序: 7
任务类型: 证明题
认知层级: 拓展层
答案来源: AI参考推导
```

**原题**：$(2)$ 求证：$\angle CAP=\angle BAP$。

**参考解答**：由 $(1)$ 已得 $\triangle ADC\cong\triangle AEB$，所以 $\angle ADC=\angle AEB$。再由 $AD=AE$，$AP=AP$，可证 $\triangle ADP\cong\triangle AEP(SSS)$ 或 $\triangle ACP\cong\triangle ABP(SAS)$，得到 $\angle CAP=\angle BAP$。

### 复习题C组第10题第（3）问

```yaml
question_id: "ch13-review-2-C-10-3"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题C组第10题第（3）问"
教材顺序: 8
任务类型: 方法设计题
认知层级: 拓展层
答案来源: AI参考推导
```

**原题**：由 $(2)$ 的结论，你能设计出一种画角平分线的方法吗？

**参考解答**：可在 $\angle BAC$ 的两边上分别截取 $AD=AE$，$AB=AC$；连接 $BE$、$CD$，交于点 $P$；连接 $AP$，则 $AP$ 即为 $\angle BAC$ 的平分线。原理是 $(2)$ 已证明 $\angle CAP=\angle BAP$。

### 复习题C组第11题

```yaml
question_id: "ch13-review-2-C-11"
source_id: "教材原文_第十三章回顾与反思_第二课时"
source_type: textbook
教材位置: "复习题C组第11题"
教材顺序: 9
任务类型: 作图探究题
认知层级: 拓展层
答案来源: AI参考推导
```

**原题**：先画一个三边互不相等的 $\triangle ABC$，然后再作一个三角形，使所作的三角形和 $\triangle ABC$ 有一个公共的顶点 $C$，且与 $\triangle ABC$ 全等。请以尽可能多的方法作出图形，并说明全等的理由。

**参考解答**：方法不唯一，以下是几种：

- 将 $\triangle ABC$ 绕点 $C$ 旋转一定角度，得到 $\triangle A'B'C$。由旋转不改变图形形状和大小，得 $\triangle A'B'C\cong\triangle ABC$。
- 延长 $AC$ 至 $A'$ 使 $A'C=AC$，延长 $BC$ 至 $B'$ 使 $B'C=BC$，连接 $A'B'$。由 $SAS$ 得 $\triangle A'B'C\cong\triangle ABC$。
- 以 $C$ 为圆心、$CA$ 为半径画弧，再以 $C$ 为圆心、$CB$ 为半径画弧，适当选取 $\angle A'CB'=\angle ACB$，用 $SAS$ 构造全等。

## 覆盖统计

| 项目 | 数量 |
|---|---:|
| 教材任务清单条目 | 9 |
| 参考解答条目 | 9 |
| 暂停生成条目 | 0 |
