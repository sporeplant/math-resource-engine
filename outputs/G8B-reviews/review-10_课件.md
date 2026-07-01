---
content_type: "review_courseware"
command: "复习课件"
lesson_id: "10"
lesson_name: "折叠与动点"
source_files:
  - outputs/g8-reviews/review-10.md
  - outputs/g8-reviews/review-10_教师版解析.md
created_at: "2026-07-01"
---

# 第 10 讲　折叠与动点

---

## 复习目标

| 目标 | 说明 |
|---|---|
| 会识别折叠条件 | 利用折叠的"对应边相等、对应角相等"两条基本性质建立方程 |
| 会分类讨论动点 | 判断动点所在边的区间，列出对应时间段的距离表达式 |
| 会选择辅助线 | 折叠：作折痕垂线、延长折痕；动点：作高、连对角线、面积法 |

---

## 知识网络

```
折叠与动点
├── 折叠问题
│   ├── 平行四边形中的折叠
│   ├── 矩形中的折叠
│   ├── 菱形中的折叠
│   └── 正方形中的折叠
└── 动点问题
    ├── 平行四边形中的动点
    ├── 矩形中的动点
    └── 菱形中的动点
```

**折叠两条铁律**

> ① 折叠前后对应线段相等  
> ② 折叠前后对应角相等（折痕是对称轴）

**动点三步走**

> ① 写运动量（距离 = 速度 × 时间）  
> ② 按区间分段讨论  
> ③ 用图形判定条件列方程

---

## 知识点01　平行四边形中的折叠问题

**核心方法**

- 平行四边形：对边平行 → 内错角相等 → 折叠后利用角度关系确定三角形形状
- 常见辅助线：延长折痕找交点

---

### 例题 1

在平行四边形 $ABCD$ 中，将 $\triangle ABC$ 沿 $AC$ 折叠得到 $\triangle AB'C$，$B'C$ 交 $AD$ 于点 $E$，连接 $B'D$，若 $\angle B=60°$，$\angle ACB=45°$，$AC=\sqrt{6}$，则 $B'D$ 的长是（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/f0a247c5baa5af009bd0ae59ac2a720de4d30ef4a0e64b777df382db6ddc8f36.jpg)

A．1　　　B．$\sqrt{2}$　　　C．$\sqrt{3}$　　　D．$\dfrac{\sqrt{6}}{2}$

---

**【分步解析】**

**第一步　找已知角**

$$\angle ADC = \angle B = 60°,\quad AD \parallel BC$$

$$\therefore \angle CAE = \angle ACB = 45°$$

**第二步　利用折叠性质**

$$\angle ACB' = \angle ACB = 45°,\quad \angle AB'C = \angle B = 60°$$

**第三步　确定直角**

$$\angle AEC = 180° - \angle CAE - \angle ACB' = 180° - 45° - 45° = 90°$$

**第四步　求 AE、CE**

在等腰直角三角形 $AEC$ 中：

$$AE = CE = \frac{\sqrt{2}}{2} \times \sqrt{6} = \sqrt{3}$$

**第五步　求 B'D**

由角度关系得 $\angle B'AD = 30°$，从而 $B'E = DE = 1$

$$B'D = \sqrt{B'E^2 + DE^2} = \sqrt{1+1} = \boxed{\sqrt{2}}$$

**答案：B**

---

## 知识点02　矩形中的折叠问题

**核心方法**

- 矩形：四个角均为 $90°$，对边平行 → 平行线产生相等的内错角
- 折叠后：$\angle ADB = \angle C'BD$（折叠对应角）

---

### 例题 2

矩形 $ABCD$ 沿对角线 $BD$ 折叠，已知 $BC=8\text{ cm}$，$AB=6\text{ cm}$，则折叠后重合部分的面积是（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/fb25a95c41092452f44682e00e0ed0ae39d76433747b2856575f34eb5934eb2e.jpg)

A．$48\text{ cm}^2$　　B．$24\text{ cm}^2$　　C．$18.75\text{ cm}^2$　　D．$18\text{ cm}^2$

---

**【分步解析】**

**第一步　找等角**

$$AD \parallel BC \Rightarrow \angle ADB = \angle DBC$$

折叠后：$\angle C'BD = \angle DBC$

$$\therefore \angle ADB = \angle EBD \Rightarrow DE = BE$$

**第二步　设 DE = x，用勾股定理**

$$C'D = AB = 6,\quad C'E = 8 - x$$

在直角三角形 $DC'E$ 中：

$$6^2 + (8-x)^2 = x^2$$

$$36 + 64 - 16x + x^2 = x^2$$

$$x = \frac{100}{16} = \frac{25}{4}$$

**第三步　求面积**

$$S_{\triangle BDE} = \frac{1}{2} \times DE \times CD = \frac{1}{2} \times \frac{25}{4} \times 6 = \boxed{18.75\text{ cm}^2}$$

**答案：C**

---

## 知识点03　菱形中的折叠问题

**核心方法**

- 菱形的 $\angle A = 60°$ → $\triangle ABD$ 是等边三角形
- 折叠找对称轴，利用垂直平分线产生的角平分关系

---

### 例题 3

在菱形 $ABCD$ 中，$\angle A=60°$，点 $E$ 在 $BC$ 边上，将菱形沿 $DE$ 折叠，点 $C$ 对应为 $C'$，且 $DC'$ 是 $AB$ 的垂直平分线，则 $\angle DEC$ 的大小为（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/31bcce56dc8e9474cdd8c5a99f16e87a314b3b11883c4ae573a87beff095bd0f.jpg)

A．$30°$　　B．$45°$　　C．$60°$　　D．$75°$

---

**【分步解析】**

**第一步　确定等边三角形**

$$AB = AD,\quad \angle A = 60° \Rightarrow \triangle ABD \text{ 是等边三角形}$$

$$\therefore \angle ADC = 120°,\quad \angle C = 60°$$

**第二步　利用垂直平分线**

$DC'$ 是 $AB$ 的垂直平分线，设交点为 $P$，则 $P$ 为 $AB$ 中点

$$\therefore DP \text{ 平分 } \angle ADB \Rightarrow \angle ADP = \angle BDP = 30°$$

$$\therefore \angle PDC = 90°$$

**第三步　折叠求 ∠CDE**

由折叠对称性：$\angle CDE = \angle PDE = 45°$

**第四步　求 ∠DEC**

$$\angle DEC = 180° - \angle CDE - \angle C = 180° - 45° - 60° = \boxed{75°}$$

**答案：D**

---

## 知识点04　正方形中的折叠问题

**核心方法**

- 正方形：$\angle A = 90°$，$AB \parallel CD$
- 折叠后：$\angle FEB' = \angle BEF$（折叠角相等）

---

### 例题 4

在正方形 $ABCD$ 中，点 $E$、$F$ 分别在 $AB$、$CD$ 上，$\angle EFC=120°$，将四边形 $EBCF$ 沿 $EF$ 折叠，点 $B$ 恰好落在 $AD$ 上，则 $\angle AEB'$ 为（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/7020a6f6d37324a914e3074ed34bf6fd4be0d3a8b6a7f2cfb7bd31e60f1cab58.jpg)

A．$70°$　　B．$65°$　　C．$30°$　　D．$60°$

---

**【分步解析】**

**第一步　由平行求 ∠BEF**

$$AB \parallel CD \Rightarrow \angle BEF + \angle EFC = 180°$$

$$\angle BEF = 180° - 120° = 60°$$

**第二步　折叠求 ∠FEB'**

$$\angle FEB' = \angle BEF = 60°$$

**第三步　求 ∠AEB'**

$$\angle AEB' = 180° - \angle BEF - \angle FEB' = 180° - 60° - 60° = \boxed{60°}$$

**答案：D**

---

## 知识点05　平行四边形中的动点问题

**核心方法**

- 平行四边形：$AD \parallel BC$，$PD \parallel QC$
- 构成平行四边形的条件：**一组对边平行且相等**
- 注意：动点是否越过端点，需**分区间讨论**

---

### 例题 5

在四边形 $ABCD$ 中，$AD \parallel BC$，$\angle A=90°$，$AD=6$，$BC=9$，点 $P$ 从 $A$ 沿射线 $AD$ 以 $2$ 单位/秒向右运动，点 $Q$ 从 $C$ 沿 $CB$ 方向以 $1$ 单位/秒向 $B$ 运动，设运动时间为 $t$ 秒，当 $t=$ ______ 时，$PDCQ$ 为平行四边形？

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/6e1eaf449733aabe475a4b4a1c60be5c545d2d497dc2a467b7ac78f6d4569662.jpg)

---

**【分步解析】**

**第一步　写运动量**

$$AP = 2t,\quad CQ = t$$

**第二步　分两种位置**

**情形一：$CD$ 作为平行四边形的边**（$P$ 在 $D$ 左侧）

$$PD = 6 - 2t,\quad CQ = t$$

$$PD = CQ \Rightarrow 6 - 2t = t \Rightarrow t = 2$$

**情形二：$CD$ 作为平行四边形的对角线**（$P$ 在 $D$ 右侧）

$$PD = 2t - 6,\quad CQ = t$$

$$PD = CQ \Rightarrow 2t - 6 = t \Rightarrow t = 6$$

$$\boxed{t = 2 \text{ 或 } t = 6}$$

---

## 知识点06　矩形中的动点问题

**核心方法**

- 点在折线上运动：注意路程分段（$A \to B$ 和 $B \to C$ 是两段）
- 判断说法是否正确：逐项代入验证，反例法找错误项

---

### 例题 6

在长方形 $ABCD$ 中，$AD=16\text{ cm}$，$AB=8\text{ cm}$，点 $P$ 从 $A$ 沿 $A \to B \to C$ 运动，速度 $2\text{ cm/s}$；点 $Q$ 从 $B$ 沿 $BC$ 向 $C$ 运动，速度 $4\text{ cm/s}$，同时出发，一方到终点时另一方停止，设运动时间为 $t$ 秒，下列说法**错误**的是（　　）

A．点 $P$ 运动路程为 $2t\text{ cm}$

B．$CQ=(16-4t)\text{ cm}$

C．当 $t=\dfrac{4}{3}$ 时，$PB=BQ$

D．运动中，点 $P$ 可以追上点 $Q$

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/924b56429427e437fa7cb3c517136f1e2727905731e8a7b3ea7871a7dfe09803.jpg)

---

**【分步解析】**

**逐项验证**

- **A**：路程 $= 2t$，正确

- **B**：$Q$ 速度 $4\text{ cm/s}$，$BQ = 4t$，$CQ = BC - BQ = 16 - 4t$，正确

- **C**：$t=\dfrac{4}{3}$ 时，$PB = 8 - 2 \times \dfrac{4}{3} = \dfrac{16}{3}$，$BQ = 4 \times \dfrac{4}{3} = \dfrac{16}{3}$，正确

- **D**：假设 $P$ 在 $BC$ 上追上 $Q$，则 $2t - 4 = 4t$，解得 $t = -2$，不合实际

$$\therefore \text{D 错误} \Rightarrow \boxed{D}$$

---

## 知识点07　菱形中的动点问题

**核心方法**

- 菱形对角线互相垂直平分
- **面积法**：连辅助线分割三角形，用同一图形面积的两种表达方式建立方程

---

### 例题 7

在菱形 $ABCD$ 中，$AB=4$，$\angle A=120°$，点 $E$ 是 $BD$ 上不与 $B$、$D$ 重合的动点，过 $E$ 分别作 $AB$、$AD$ 的垂线，垂足为 $F$、$G$，则 $EF+EG$ 的值为（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/0406cae7a36c4428e5c00f60ac10e450feb56f9d82c993e7b8cf3655100c1446.jpg)

A．$2\sqrt{3}$　　B．$2$　　C．$4\sqrt{3}$　　D．$4$

---

**【分步解析】**

**第一步　求对角线长度**

$$\angle BAO = \frac{1}{2} \angle A = 60°,\quad AB = 4$$

$$AO = \frac{1}{2} AB = 2,\quad OB = \sqrt{AB^2 - AO^2} = 2\sqrt{3}$$

$$BD = 2OB = 4\sqrt{3}$$

**第二步　面积法**

连接 $AE$，将 $\triangle ABD$ 分为 $\triangle ABE$ 和 $\triangle ADE$：

$$S_{\triangle ABD} = S_{\triangle ABE} + S_{\triangle ADE}$$

$$\frac{1}{2} \times BD \times AO = \frac{1}{2} \times AB \times EF + \frac{1}{2} \times AD \times EG$$

$$\frac{1}{2} \times 4\sqrt{3} \times 2 = \frac{1}{2} \times 4 \times (EF + EG)$$

$$EF + EG = \boxed{2\sqrt{3}}$$

**答案：A**

---

## 当堂练习

> 以下题目请独立完成，完成后对照答案讲解。

---

**8．** 如图，将 $\text{▱}ABCD$ 折叠，使点 $D$、$C$ 分别落在点 $F$、$E$ 处，折痕为 $MN$，若 $\angle AMF=50°$，则 $\angle A=$ ______。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/8d308126d18998d59cad779d0575d20a7bcf4cbfecd80f2cd499c7d9d3e1e118.jpg)

---

**9．** 如图，长方形 $ABCD$，$E$ 为 $CD$ 上一点，沿 $BE$ 折叠点 $C$ 落在 $C'$，沿 $AE$ 折叠点 $D$ 落在 $D'$ 且 $D'$ 在线段 $BE$ 上，若 $\angle AEC=\alpha$，则 $\angle CEB=$ （　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/6e00fb97caba3f083a9d05eb7f91acec2e4a4194a45e47453adffa67c85e487a.jpg)

A．$60°-\dfrac{2\alpha}{3}$　　B．$60°-\dfrac{\alpha}{3}$　　C．$60°+\dfrac{2\alpha}{3}$　　D．$60°+\dfrac{\alpha}{3}$

---

**10．** 如图，菱形 $ABCD$ 中，$\angle A=120°$，$E$ 是 $AD$ 上的点，沿 $BE$ 折叠 $\triangle ABE$，点 $A$ 恰好落在 $BD$ 上的点 $F$，则 $\angle BFC$ 的度数是______。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/5b33ea62303296dc3e706c62f8e54b725527fe604cab5753707e486b0ef463f8.jpg)

---

**11．** 如图，正方形 $ABCD$ 沿对边中点连线折叠后展开，折痕为 $MN$，再过点 $B$ 折叠，使点 $A$ 落在 $MN$ 上的点 $F$，折痕为 $BE$，若 $FN=3$，则正方形边长为______。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/a3a35fc32fcc6049d069e8cc7e58850ca272f2051aaa8cbde6d40af4afb86a33.jpg)

---

**12．** 如图，在平行四边形 $ABCD$ 中，$AB=6\text{ cm}$，$AD=10\text{ cm}$，点 $P$ 在 $AD$ 边上以 $1\text{ cm/s}$ 从 $A$ 向 $D$ 运动，点 $Q$ 在 $BC$ 边上以 $2.5\text{ cm/s}$ 从 $C$ 出发，在 $CB$ 间往返运动。设时间为 $t$，当 $t$ 为何值时，以 $P,D,Q,B$ 为顶点的四边形是平行四边形？（　　）

A．$\dfrac{20}{3}$　　B．$\dfrac{40}{7}$　　C．$\dfrac{20}{3}$ 或 $\dfrac{40}{7}$　　D．$\dfrac{40}{3}$ 或 $\dfrac{40}{7}$

**思考提示：** 先写 $PD=10-t$，再按 $Q$ 在 $BC$ 上往返的位置分段表示 $BQ$。

---

**13．** 在平面直角坐标系中，长方形 $ABCD$ 如图放置，$O$ 是 $AD$ 的中点，且 $A(5,0)$，$B(5,4)$，$C(-5,4)$，点 $P$ 是 $BC$ 上的动点，当 $\triangle ODP$ 是腰长为 $5$ 的等腰三角形时，点 $P$ 的坐标为______。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/e5c84097eb3362f3434a73f800279ca35043c7ac23ec1245378a7024a2c1f612.jpg)

**思考提示：** 先确定 $D(-5,0)$、$O(0,0)$，再分别讨论 $OP=5$、$DP=5$、$OD=5$。

---

**14．** 如图，菱形 $ABCD$ 的对角线 $AC,BD$ 相交于点 $O$，点 $E,F$ 同时从 $O$ 出发在线段 $AC$ 上以 $1\text{ cm/s}$ 反向运动。已知 $\triangle ABD$ 是边长为 $6\text{ cm}$ 的等边三角形，当 $t=$ ______ s 时，四边形 $DEBF$ 为正方形。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/7a7c90ccf5ce009d5e4d65f05ed5e826c8f1a3fc0c8e4217bf115a0c0fc39ddf.jpg)

**思考提示：** 菱形对角线互相垂直，若 $DEBF$ 为正方形，则两条对角线应相等。

---

**15．** 如图，将 $\text{▱}ABCD$ 沿对角线 $AC$ 折叠，使点 $B$ 落在 $B'$ 处，若 $\angle1=\angle2=44°$，则 $\angle B$ 为（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/473766db2ed05f1464dfe3c4311c9fb1285a0fd4f4a8482e3bc7f60d1b3dce7f.jpg)

A．$66°$　　B．$104°$　　C．$114°$　　D．$124°$

---

**16．** 数学老师要求学生用一张长方形纸片 $ABCD$ 折出一个 $45°$ 的角。甲、乙两人的折法如下，下列说法正确的是（　　）

甲：沿 $AE$ 折叠，使点 $B$ 落在 $AD$ 上的点 $B'$ 处，$\angle EAD$ 即为所求。

![](images/第07讲-原卷版-b1d08302b123958af9412fbee75284329554d481a5a32636f8c510dfcec7af03.jpg)

乙：沿 $AE,AF$ 折叠，使 $B,D$ 两点分别落在 $B',D'$ 处，且 $AB'$ 与 $AD'$ 在同一直线上，$\angle EAF$ 即为所求。

![](images/第07讲-原卷版-0a1fe694b4833355a68ca7912a36ac5a4e31feb711ec3f7a6a1af870e629364a.jpg)

A．只有甲正确　　B．甲和乙都正确　　C．只有乙正确　　D．甲和乙都不正确

---

**17．** 如图，菱形 $ABCD$ 中，$\angle D=120°$，点 $E$ 在边 $CD$ 上，将菱形沿直线 $AE$ 翻折，使点 $D$ 恰好落在对角线 $AC$ 上，连接 $BD'$，则 $\angle AD'B=$ ______。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/ec8b58a77eed8deb4552ff0ac41271444f00056e946e7eac7f162de88b8be0d2.jpg)

---

## 当堂练习答案速查

| 题号 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|
| 答案 | $65°$ | A | $75°$ | $2\sqrt3$ | B |

| 题号 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|
| 答案 | $(-2,4)$ 或 $(-3,4)$ 或 $(3,4)$ | 3 | C | B | $75°$ |

---

## 当堂练习讲评重点

1. **第 8–11 题：折叠求角、求长**
   - 抓住“对应角相等、对应边相等”。
   - 正方形、菱形题优先找 $45°$、$60°$、$120°$ 等特殊角。

2. **第 12–14 题：动点与图形判定**
   - 先写运动量，再将“成为平行四边形/正方形/等腰三角形”转化为边长关系。
   - 往返运动题必须分段。

3. **第 15–17 题：综合折叠**
   - 折叠线是对称轴，能带来角平分、垂直平分或等边关系。

---

## 课后作业

> 完成后要求写出关键理由：折叠题写“对应关系”，动点题写“时间范围”。

---

**18．** 如图，将 $\text{▱}ABCD$ 沿对角线 $AC$ 折叠，使点 $B$ 落在 $B'$ 处，若 $\angle1=\angle2=44°$，则 $\angle B$ 为（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/473766db2ed05f1464dfe3c4311c9fb1285a0fd4f4a8482e3bc7f60d1b3dce7f.jpg)

A．$66°$　　B．$104°$　　C．$114°$　　D．$124°$

---

**19．** 用长方形纸片 $ABCD$ 折出一个 $45°$ 的角，判断甲、乙两种折法是否正确。（选项同第 16 题）

![](images/第07讲-原卷版-b1d08302b123958af9412fbee75284329554d481a5a32636f8c510dfcec7af03.jpg)

![](images/第07讲-原卷版-0a1fe694b4833355a68ca7912a36ac5a4e31feb711ec3f7a6a1af870e629364a.jpg)

A．只有甲正确　　B．甲和乙都正确　　C．只有乙正确　　D．甲和乙都不正确

---

**20．** 如图，菱形 $ABCD$ 中，$\angle D=120°$，点 $E$ 在边 $CD$ 上，将菱形沿 $AE$ 翻折，使点 $D$ 落在对角线 $AC$ 上，连接 $BD'$，则 $\angle AD'B=$ ______。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/ec8b58a77eed8deb4552ff0ac41271444f00056e946e7eac7f162de88b8be0d2.jpg)

---

**21．** 如图，在正方形 $ABCD$ 中，$E$ 为 $BC$ 上一点，将 $\triangle ABE$ 沿 $AE$ 折叠至 $\triangle AB'E$，$BE$ 与 $AC$ 交于点 $F$，若 $\angle EFC=69°$，则 $\angle CAE$ 的大小为（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/c0d13e2b09ac00b201db36aca44ccc32085bd258f4cd4383a4f7a2b136a6e722.jpg)

A．$10°$　　B．$12°$　　C．$14°$　　D．$15°$

---

**22．** 如图，$\text{▱}ABCD$ 中，$AB=22\text{ cm}$，$BC=8\sqrt2\text{ cm}$，$\angle A=45°$，动点 $E$ 从 $A$ 出发，以 $2\text{ cm/s}$ 沿 $AB$ 向 $B$ 运动，动点 $F$ 从 $C$ 出发，以 $1\text{ cm/s}$ 沿 $CD$ 向 $D$ 运动。当 $EF=10\text{ cm}$ 时，点 $E$ 的运动时间是（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/1eb088a442247a38b5615f265d679b539d41565c03afdd553fef1f772012bb2e.jpg)

A．$6\text{ s}$　　B．$6\text{ s}$ 或 $10\text{ s}$　　C．$8\text{ s}$　　D．$8\text{ s}$ 或 $12\text{ s}$

---

**23．** 如图，在矩形 $ABCD$ 中，$AB=3$，$AD=4$，$P$ 是 $AD$ 上不与 $A,D$ 重合的动点，过点 $P$ 分别作 $AC$ 和 $BD$ 的垂线，垂足为 $E,F$，求 $PE+PF=$ ______。

---

**24．** 如图，在菱形 $ABCD$ 中，$AB=5\text{ cm}$，$\angle ADC=120°$，点 $E,F$ 同时由 $A,C$ 两点出发，分别沿 $AB,CB$ 向 $B$ 匀速移动，点 $E$ 速度为 $1\text{ cm/s}$，点 $F$ 速度为 $2\text{ cm/s}$，经过 $t$ 秒 $\triangle DEF$ 为等边三角形，则 $t$ 的值为（　　）

A．$\dfrac34$　　B．$\dfrac43$　　C．$\dfrac32$　　D．$\dfrac53$

---

**25．** 如图，在 $\text{▱}ABCD$ 中，$E$ 为边 $CD$ 上一点，将 $\triangle ADE$ 沿 $AE$ 折叠至 $\triangle AD'E$，$AD'$ 与 $CE$ 交于点 $F$。若 $\angle B=52°$，$\angle DAE=20°$，则 $\angle FED'$ 的大小为______。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/ecfa737c45c1ec18e94b9bff2f751726daea0d31b0244a24ed9cc3f5f70ad0b3.jpg)

---

**26．** 如图，在矩形 $ABCD$ 中，$M$ 是 $BC$ 上一点，将 $\triangle ABM$ 沿 $AM$ 折叠，使点 $B$ 落在 $B'$ 处，若 $\angle AMB=\alpha$，则 $\angle B'AD$ 等于（　　）

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/67f8429b6b356253690efa5fe3fa1ad9ba2004f0012057065717926cea7458f5.jpg)

A．$\alpha-90°$　　B．$\alpha-45°$　　C．$90°-2\alpha$　　D．$90°-\alpha$

---

**27．** 如图，在菱形 $ABCD$ 中，$\angle A=120°$，$AB=2$，点 $E$ 是边 $AB$ 上一点，以 $DE$ 为对称轴将 $\triangle DAE$ 折叠得到 $\triangle DGE$，再折叠 $BE$ 使 $BE$ 落在直线 $EG$ 上，点 $B$ 的对应点为 $H$，折痕为 $EF$ 且交 $BC$ 于点 $F$。

（1）$\angle DEF=$ ______。

（2）若点 $E$ 是 $AB$ 中点，则 $DF=$ ______。

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/e96ea9bc8122dd1f9a8e55101d577d7a07a360c498890382193ca9843a0c5d58.jpg)

---

## 课后作业答案

| 题号 | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|
| 答案 | C | B | $75°$ | B | C |

| 题号 | 23 | 24 | 25 | 26 | 27 |
|---|---|---|---|---|---|
| 答案 | $\dfrac{12}{5}$ | D | $36°$ | C | （1）$90°$；（2）$\dfrac{14}{5}$ |

---

## 课堂小结

### 1. 折叠问题

- 找折叠前后的**对应点、对应边、对应角**。
- 折痕常带来：角平分、垂直平分、等腰三角形。
- 特殊四边形中优先利用：平行、直角、等边、对角线性质。

### 2. 动点问题

- 先写运动量：$s=vt$。
- 再判断位置：是否需要分段、是否往返。
- 最后把目标图形转化为方程：
  - 平行四边形：一组对边平行且相等；
  - 正方形：先有垂直，再比较对角线或边长；
  - 等腰三角形：分类讨论哪两边相等。

---

## 下节课准备

请整理本讲错题，按以下格式记录：

| 题号 | 错因 | 正确抓手 |
|---|---|---|
|  | 折叠对应关系 / 动点分段 / 特殊图形性质 |  |