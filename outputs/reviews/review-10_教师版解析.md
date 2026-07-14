---
content_type: review_solution
source_files:
  - knowledge/reviews/c-21/review-07-2.md
  - knowledge/reviews/c-21/review-08-2.md
student_file: outputs/reviews/review-10.md
title: 第10讲 折叠与动点 教师版解析
---

# 第 10 讲 折叠与动点 教师版解析

## 一、答案速查

| 题号 | 答案 |
|---|---|
| 1 | B |
| 2 | C |
| 3 | D |
| 4 | D |
| 5 | 2 或 6 |
| 6 | D |
| 7 | A |
| 8 | 65° |
| 9 | A |
| 10 | 75° |
| 11 | $2\sqrt3$ |
| 12 | B |
| 13 | $(-2,4)$ 或 $(-3,4)$ 或 $(3,4)$ |
| 14 | 3 |
| 15 | C |
| 16 | B |
| 17 | 75° |
| 18 | C |
| 19 | B |
| 20 | 75° |
| 21 | B |
| 22 | C |
| 23 | $\frac{12}{5}$ |
| 24 | D |
| 25 | 36° |
| 26 | C |
| 27 | （1）90°；（2）$\frac{14}{5}$ |

---

## 二、例题讲解解析

### 1．平行四边形沿对角线折叠求线段

**答案：B**

**解析：**

由平行四边形性质可得：

$$
AD\parallel BC,\quad AB\parallel CD,\quad \angle ADC=60^\circ
$$

又因为 $\angle ACB=45^\circ$，所以：

$$
\angle CAE=\angle ACB=45^\circ
$$

折叠后：

$$
\angle ACB'=\angle ACB=45^\circ,\quad \angle AB'C=\angle B=60^\circ
$$

于是：

$$
\angle AEC=180^\circ-45^\circ-45^\circ=90^\circ
$$

在等腰直角三角形 $AEC$ 中：

$$
AE=CE=\frac{\sqrt2}{2}AC=\frac{\sqrt2}{2}\times\sqrt6=\sqrt3
$$

结合图形角度关系，可得：

$$
\angle B'AD=30^\circ,\quad \angle DCE=30^\circ
$$

从而：

$$
B'E=DE=1
$$

所以：

$$
B'D=\sqrt{B'E^2+DE^2}=\sqrt{1^2+1^2}=\sqrt2
$$

故选 B。

---

### 2．矩形沿对角线折叠求重合面积

**答案：C**

**解析：**

矩形 $ABCD$ 中，$AD\parallel BC$，所以：

$$
\angle ADB=\angle DBC
$$

沿 $BD$ 折叠后：

$$
\angle C'BD=\angle DBC
$$

因此：

$$
\angle ADB=\angle EBD
$$

所以：

$$
DE=BE
$$

设 $DE=x$，则 $C'E=8-x$，又 $C'D=AB=6$。在直角三角形 $DC'E$ 中：

$$
6^2+(8-x)^2=x^2
$$

解得：

$$
x=\frac{25}{4}
$$

重合部分为 $\triangle BDE$，其面积为：

$$
S_{\triangle BDE}=\frac12\times DE\times CD
=\frac12\times\frac{25}{4}\times6=18.75\text{ cm}^2
$$

故选 C。

---

### 3．菱形折叠求角

**答案：D**

**解析：**

连接 $BD$。因为菱形 $ABCD$ 中 $AB=AD$，且 $\angle A=60^\circ$，所以 $\triangle ABD$ 是等边三角形。

因此：

$$
\angle ADC=120^\circ,\quad \angle C=60^\circ
$$

又因为 $DC'$ 是 $AB$ 的垂直平分线，所以 $DP$ 平分 $\angle ADB$，即：

$$
\angle ADP=\angle BDP=30^\circ
$$

从而：

$$
\angle PDC=90^\circ
$$

由折叠性质得：

$$
\angle CDE=\angle PDE=45^\circ
$$

在 $\triangle DEC$ 中：

$$
\angle DEC=180^\circ-45^\circ-60^\circ=75^\circ
$$

故选 D。

---

### 4．正方形折叠求角

**答案：D**

**解析：**

正方形中 $AB\parallel CD$，所以：

$$
\angle BEF+\angle EFC=180^\circ
$$

已知：

$$
\angle EFC=120^\circ
$$

则：

$$
\angle BEF=60^\circ
$$

沿 $EF$ 折叠后：

$$
\angle FEB'=\angle BEF=60^\circ
$$

所以：

$$
\angle AEB'=180^\circ-60^\circ-60^\circ=60^\circ
$$

故选 D。

---

### 5．平行四边形中的动点构造

**答案：2 或 6**

**解析：**

点 $P$ 从 $A$ 出发沿射线 $AD$ 运动，速度为 2；点 $Q$ 从 $C$ 出发沿 $CB$ 运动，速度为 1。设运动时间为 $t$。

分两种情况讨论。

**情况一：$CD$ 为平行四边形的一边。**

此时 $P$ 在 $D$ 左侧：

$$
PD=6-2t,\quad CQ=t
$$

要使以 $P,D,C,Q$ 为顶点的四边形为平行四边形，应有：

$$
PD=CQ
$$

即：

$$
6-2t=t
$$

解得：

$$
t=2
$$

**情况二：$CD$ 为平行四边形的对角线。**

此时 $P$ 在 $D$ 右侧：

$$
PD=2t-6,\quad CQ=t
$$

同理：

$$
2t-6=t
$$

解得：

$$
t=6
$$

综上，$t=2$ 或 $6$。

---

### 6．矩形中的双动点判断错误项

**答案：D**

**解析：**

逐项判断：

A．点 $P$ 速度为 $2\text{ cm/s}$，运动时间为 $t$，所以运动路程为 $2t\text{ cm}$，正确。

B．点 $Q$ 速度为 $4\text{ cm/s}$，从 $B$ 向 $C$ 运动，所以：

$$
CQ=16-4t
$$

正确。

C．当 $t=\frac43$ 时：

$$
PB=8-2t=8-\frac83=\frac{16}{3}
$$

$$
BQ=4t=\frac{16}{3}
$$

所以 $PB=BQ$，正确。

D．若点 $P$ 追上点 $Q$，则当 $P$ 到达 $BC$ 后应满足：

$$
2t-4=4t
$$

解得：

$$
t=-2
$$

不符合实际，所以点 $P$ 不可能追上点 $Q$。D 错误。

故选 D。

---

### 7．菱形中动点到两边距离和

**答案：A**

**解析：**

连接 $AC$ 交 $BD$ 于点 $O$。

菱形中对角线互相垂直，且 $AC$ 平分 $\angle A$。已知 $\angle A=120^\circ$，所以：

$$
\angle BAO=60^\circ
$$

在直角三角形 $ABO$ 中，$AB=4$，所以：

$$
AO=2,\quad BO=2\sqrt3
$$

因此：

$$
BD=2BO=4\sqrt3
$$

连接 $AE$。由面积分割：

$$
S_{\triangle ABD}=S_{\triangle ABE}+S_{\triangle ADE}
$$

即：

$$
\frac12\times BD\times AO=\frac12\times AB\times EF+\frac12\times AD\times EG
$$

代入 $BD=4\sqrt3, AO=2, AB=AD=4$：

$$
\frac12\times4\sqrt3\times2=\frac12\times4(EF+EG)
$$

解得：

$$
EF+EG=2\sqrt3
$$

故选 A。

---

## 三、当堂练习解析

### 8．平行四边形折叠求角

**答案：65°**

**解析：**

由平行四边形性质：

$$
AB\parallel CD
$$

折叠后，折痕 $MN$ 平行于 $AE$，且：

$$
\angle FMN=\angle DMN
$$

又因为：

$$
\angle AMF=50^\circ
$$

所以：

$$
\angle DMF=180^\circ-50^\circ=130^\circ
$$

折叠使 $\angle DMF$ 被平分，故：

$$
\angle FMN=\angle DMN=65^\circ
$$

而该角与 $\angle A$ 对应，所以：

$$
\angle A=65^\circ
$$

---

### 9．长方形二次折叠求角

**答案：A**

**解析：**

由折叠性质：

$$
\angle AED=\angle AED',\quad \angle CEB=\angle C'EB
$$

设：

$$
\angle CEB=x
$$

已知：

$$
\angle AEC=\alpha
$$

由图形关系可得：

$$
\angle AED'=\alpha+x
$$

又因为点 $D'$ 在线段 $BE$ 上，直线角关系给出：

$$
2\angle AED'=180^\circ-x
$$

代入：

$$
2(\alpha+x)=180^\circ-x
$$

解得：

$$
3x=180^\circ-2\alpha
$$

所以：

$$
x=60^\circ-\frac{2}{3}\alpha
$$

故选 A。

---

### 10．菱形折叠求 $\angle BFC$

**答案：75°**

**解析：**

菱形中 $AB=BC$，且邻角互补。已知：

$$
\angle A=120^\circ
$$

所以：

$$
\angle ABC=60^\circ
$$

菱形对角线 $BD$ 平分 $\angle ABC$，因此：

$$
\angle FBC=30^\circ
$$

折叠后 $A$ 落在 $F$，所以：

$$
AB=BF
$$

又 $AB=BC$，故：

$$
BF=BC
$$

在等腰三角形 $BFC$ 中：

$$
\angle BFC=\angle BCF=\frac{180^\circ-30^\circ}{2}=75^\circ
$$

---

### 11．正方形纸片折叠求边长

**答案：$2\sqrt3$**

**解析：**

设正方形边长为 $x$。

由折叠性质：

$$
BF=AB=x
$$

折痕 $MN$ 是对边中点连线，所以：

$$
BN=\frac12 x
$$

在直角三角形 $BFN$ 中：

$$
FN=\sqrt{BF^2-BN^2}=\sqrt{x^2-\left(\frac{x}{2}\right)^2}=\frac{\sqrt3}{2}x
$$

已知 $FN=3$，所以：

$$
\frac{\sqrt3}{2}x=3
$$

解得：

$$
x=2\sqrt3
$$

---

### 12．平行四边形边上往返动点

**答案：B**

**解析：**

在平行四边形中：

$$
PD\parallel BQ
$$

要使以 $P,D,Q,B$ 为顶点的四边形为平行四边形，需要：

$$
PD=BQ
$$

设运动时间为 $t$。

当 $0<t\le4$ 时，点 $Q$ 从 $C$ 向 $B$ 运动：

$$
PD=10-t,\quad BQ=10-2.5t
$$

方程：

$$
10-t=10-2.5t
$$

得 $t=0$，舍去。

当 $4<t\le8$ 时，点 $Q$ 从 $B$ 往 $C$ 返回：

$$
BQ=2.5t-10
$$

所以：

$$
10-t=2.5t-10
$$

解得：

$$
t=\frac{40}{7}
$$

当 $8<t\le10$ 时：

$$
BQ=30-2.5t
$$

方程：

$$
10-t=30-2.5t
$$

得：

$$
t=\frac{40}{3}
$$

不在该时间段内，舍去。

故选 B。

---

### 13．矩形坐标系中动点与等腰三角形

**答案：$(-2,4)$ 或 $(-3,4)$ 或 $(3,4)$**

**解析：**

由坐标可知：

$$
A(5,0),\quad B(5,4),\quad C(-5,4)
$$

矩形 $ABCD$ 中 $D(-5,0)$。点 $O$ 是 $AD$ 中点，所以：

$$
O(0,0),\quad OD=5
$$

点 $P$ 在 $BC$ 上，设 $P(x,4)$。

**情况一：$DP=DO=5$。**

在直角三角形中，竖直距离为 4，所以水平距离为：

$$
\sqrt{5^2-4^2}=3
$$

从 $D(-5,0)$ 向右 3 个单位，得：

$$
P(-2,4)
$$

**情况二：$OP=OD=5$。**

此时：

$$
x^2+4^2=5^2
$$

解得：

$$
x=\pm3
$$

所以：

$$
P(-3,4)\text{ 或 }(3,4)
$$

综上，点 $P$ 的坐标为：

$$
(-2,4),\quad (-3,4),\quad (3,4)
$$

---

### 14．菱形对角线上动点成正方形

**答案：3**

**解析：**

由题意：

$$
OE=OF=t
$$

所以：

$$
EF=2t
$$

菱形对角线互相垂直且互相平分，所以四边形 $DEBF$ 是菱形。

当菱形 $DEBF$ 的两条对角线相等时，它为正方形，即：

$$
EF=BD
$$

已知 $\triangle ABD$ 是边长为 6 cm 的等边三角形，所以：

$$
BD=6
$$

于是：

$$
2t=6
$$

解得：

$$
t=3
$$

---

### 15．平行四边形沿对角线折叠求 $\angle B$

**答案：C**

**解析：**

平行四边形中：

$$
AB\parallel CD
$$

所以：

$$
\angle ACD=\angle BAC
$$

由折叠性质：

$$
\angle BAC=\angle B'AC
$$

已知 $\angle1=44^\circ$，因此：

$$
\angle BAC=\angle ACD=\angle B'AC=\frac12\times44^\circ=22^\circ
$$

又已知 $\angle2=44^\circ$，所以：

$$
\angle B=180^\circ-44^\circ-22^\circ=114^\circ
$$

故选 C。

---

### 16．长方形纸片折出 $45^\circ$

**答案：B**

**解析：**

**甲的折法：**

将点 $B$ 折到 $AD$ 上，折痕 $AE$ 平分对应角，因此：

$$
\angle EAD=45^\circ
$$

甲正确。

**乙的折法：**

沿 $AE,AF$ 折叠后，$B,D$ 分别落到同一直线上，两个折痕相当于把直角 $\angle DAB$ 的两部分分别对折，因此：

$$
\angle EAF=\frac12\times90^\circ=45^\circ
$$

乙也正确。

故选 B。

---

### 17．菱形翻折到对角线求角

**答案：75°**

**解析：**

菱形中：

$$
AD=DC=BC=AB,\quad CD\parallel AB
$$

已知：

$$
\angle D=120^\circ
$$

在等腰三角形 $ADC$ 中：

$$
\angle DAC=\angle DCA=\frac{180^\circ-120^\circ}{2}=30^\circ
$$

又 $CD\parallel AB$，所以：

$$
\angle BAD'=\angle DCA=30^\circ
$$

翻折后：

$$
AD=AD'
$$

而菱形中 $AD=AB$，所以：

$$
AB=AD'
$$

在等腰三角形 $ABD'$ 中：

$$
\angle AD'B=\angle ABD'=\frac{180^\circ-30^\circ}{2}=75^\circ
$$

---

## 四、课后作业解析

### 18．平行四边形折叠求角

**答案：C**

**解析：**

本题与第 15 题相同。

由平行与折叠可得：

$$
\angle BAC=\angle ACD=\angle B'AC=22^\circ
$$

所以：

$$
\angle B=180^\circ-44^\circ-22^\circ=114^\circ
$$

故选 C。

---

### 19．折出 $45^\circ$ 的判断

**答案：B**

**解析：**

本题与第 16 题相同。

甲通过一次折叠平分直角，能得到 $45^\circ$；乙通过两次折叠把直角的两部分对折后合成，也能得到 $45^\circ$。

故选 B。

---

### 20．菱形翻折求 $\angle AD'B$

**答案：75°**

**解析：**

本题与第 17 题相同。

由 $\angle D=120^\circ$ 可得：

$$
\angle DAC=\angle DCA=30^\circ
$$

又因为 $CD\parallel AB$，所以：

$$
\angle BAD'=30^\circ
$$

翻折与菱形边长关系给出：

$$
AB=AD'
$$

因此：

$$
\angle AD'B=\frac{180^\circ-30^\circ}{2}=75^\circ
$$

---

### 21．正方形折叠求 $\angle CAE$

**答案：B**

**解析：**

正方形对角线与边的夹角为 $45^\circ$，所以：

$$
\angle ACE=45^\circ
$$

已知：

$$
\angle EFC=69^\circ
$$

由三角形外角关系可得：

$$
\angle BEF=69^\circ+45^\circ=114^\circ
$$

折叠后，$AE$ 平分对应角：

$$
\angle BEA=\frac12\angle BEF=57^\circ
$$

在直角三角形 $ABE$ 中：

$$
\angle BAE=90^\circ-57^\circ=33^\circ
$$

所以：

$$
\angle CAE=45^\circ-33^\circ=12^\circ
$$

故选 B。

---

### 22．平行四边形双动点求时间

**答案：C**

**解析：**

在平行四边形中：

$$
CD=AB=22,\quad AD=BC=8\sqrt2
$$

过 $D$ 作 $DG\perp AB$ 于 $G$。因为 $\angle A=45^\circ$，所以 $\triangle ADG$ 是等腰直角三角形：

$$
AG=DG=8
$$

过 $F$ 作 $FH\perp AB$ 于 $H$，则：

$$
FH=8
$$

已知 $EF=10$，所以：

$$
EH=\sqrt{10^2-8^2}=6
$$

设运动时间为 $t$，则：

$$
AE=2t,\quad CF=t,\quad DF=22-t
$$

当 $F$ 在 $E$ 右侧时：

$$
GH=GE+EH=(2t-8)+6=2t-2
$$

又 $GH=DF$，所以：

$$
2t-2=22-t
$$

解得：

$$
t=8
$$

另一种位置会得到 $t=12$，但点 $E$ 到达 $B$ 时停止，需 $2t\le22$，即 $t\le11$，所以 $t=12$ 舍去。

故选 C。

---

### 23．矩形中动点到两对角线距离和

**答案：$\frac{12}{5}$**

**解析：**

连接矩形对角线交点 $O$ 与点 $P$。

矩形 $ABCD$ 中：

$$
AB=3,\quad AD=4
$$

所以：

$$
S_{矩形}=3\times4=12
$$

对角线长为：

$$
AC=BD=\sqrt{3^2+4^2}=5
$$

因此：

$$
OA=OD=\frac52
$$

又：

$$
S_{\triangle AOD}=\frac14S_{矩形}=3
$$

点 $P$ 在 $AD$ 上，且 $PE\perp AC, PF\perp BD$，所以：

$$
S_{\triangle AOD}=S_{\triangle AOP}+S_{\triangle DOP}
$$

$$
=\frac12OA\cdot PE+\frac12OD\cdot PF
$$

$$
=\frac12\cdot\frac52(PE+PF)=3
$$

解得：

$$
PE+PF=\frac{12}{5}
$$

---

### 24．菱形动点形成等边三角形

**答案：D**

**解析：**

连接 $BD$。

菱形中 $AB=AD$，且 $\angle ADC=120^\circ$，所以：

$$
\angle ADB=60^\circ
$$

于是 $\triangle ABD$ 是等边三角形，故：

$$
AD=BD
$$

若 $\triangle DEF$ 是等边三角形，则：

$$
\angle EDF=60^\circ
$$

结合 $\angle ADB=60^\circ$ 可得：

$$
\angle ADE=\angle BDF
$$

可证：

$$
\triangle ADE\cong\triangle BDF
$$

所以：

$$
AE=BF
$$

由题意：

$$
AE=t,\quad CF=2t,\quad BF=BC-CF=5-2t
$$

因此：

$$
t=5-2t
$$

解得：

$$
t=\frac53
$$

故选 D。

---

### 25．平行四边形折叠求角

**答案：36°**

**解析：**

平行四边形中：

$$
\angle D=\angle B=52^\circ
$$

由折叠性质：

$$
\angle D'=\angle D=52^\circ,\quad \angle EAD'=\angle DAE=20^\circ
$$

因为 $F$ 在 $AD'$ 与 $CE$ 的交点处，可得：

$$
\angle AEF=\angle D+\angle DAE=52^\circ+20^\circ=72^\circ
$$

在 $\triangle AED'$ 中：

$$
\angle AED'=180^\circ-20^\circ-52^\circ=108^\circ
$$

所以：

$$
\angle FED'=108^\circ-72^\circ=36^\circ
$$

---

### 26．矩形折叠求 $\angle B'AD$

**答案：C**

**解析：**

矩形中：

$$
\angle ABC=90^\circ,\quad AD\parallel BC
$$

已知：

$$
\angle AMB=\alpha
$$

由平行线性质：

$$
\angle DAM=\alpha
$$

在直角三角形 $ABM$ 中：

$$
\angle BAM=90^\circ-\alpha
$$

折叠后：

$$
\angle B'AM=\angle BAM=90^\circ-\alpha
$$

因此：

$$
\angle B'AD=\angle B'AM-\angle DAM=(90^\circ-\alpha)-\alpha=90^\circ-2\alpha
$$

故选 C。

---

### 27．菱形连续折叠综合题

**答案：**

（1）$90^\circ$；  
（2）$\frac{14}{5}$。

**解析：**

#### （1）求 $\angle DEF$

由第一次折叠：

$$
\angle AED=\angle DEG
$$

由第二次折叠：

$$
\angle BEF=\angle HEF
$$

两次折叠后，相关角正好分割平角：

$$
\angle DEG+\angle HEF+\angle AED+\angle BEF=180^\circ
$$

且：

$$
\angle DEG+\angle HEF=\angle AED+\angle BEF
$$

所以：

$$
\angle DEG+\angle HEF=90^\circ
$$

即：

$$
\angle DEF=90^\circ
$$

#### （2）点 $E$ 是 $AB$ 中点时求 $DF$

菱形 $ABCD$ 中：

$$
AD\parallel BC,\quad AB=AD=BC=CD=2
$$

且 $\angle A=120^\circ$，所以：

$$
\angle DCM=60^\circ
$$

过点 $D$ 作 $DM\perp BC$，交 $BC$ 延长线于 $M$，则：

$$
CM=1,\quad DM=\sqrt3
$$

由折叠性质与 $E$ 是 $AB$ 中点可知，点 $D,G,F$ 共线，且：

$$
DG=AD=2,\quad BF=FG
$$

设：

$$
BF=x
$$

则：

$$
MF=3-x,\quad DF=2+x
$$

在直角三角形 $DMF$ 中：

$$
DF^2=DM^2+MF^2
$$

即：

$$
(2+x)^2=(\sqrt3)^2+(3-x)^2
$$

解得：

$$
x=\frac45
$$

所以：

$$
DF=2+\frac45=\frac{14}{5}
$$

---

## 五、教师讲评建议

### 1. 折叠问题核心抓手

1. **对应边相等**：折叠前后对应线段相等。
2. **对应角相等**：折叠前后对应角相等。
3. **折痕是垂直平分线**：连接原点与对应点，折痕垂直平分该连线。
4. **角平分转化**：折叠常产生角平分关系，如第 4、9、11、16、26 题。
5. **构造直角三角形**：涉及长度时，常通过作高或找垂直关系后用勾股定理。

### 2. 动点问题核心抓手

1. **先写运动量**：如 $AP=vt$、$CQ=vt$。
2. **分段讨论**：往返运动或沿折线路径运动必须按所在边分段。
3. **用图形判定转方程**：
   - 平行四边形：一组对边平行且相等；
   - 菱形：邻边相等的平行四边形；
   - 正方形：菱形且对角线相等，或矩形且邻边相等。
4. **舍去不合范围的解**：如第 12、22 题。

### 3. 易错点提醒

| 易错点 | 典型题号 | 讲评提醒 |
|---|---|---|
| 折叠后对应角、对应边找错 | 1、3、4、9、25、26 | 先标出原图点与对应点 |
| 忘记折痕垂直平分性质 | 11、17、20、27 | 折痕不仅是对称轴，还产生垂直与中点 |
| 动点不分段 | 5、12、13、22 | 先确定点在哪条边、哪个区间 |
| 方程解未检验范围 | 12、22 | 得到时间后必须回代检查运动区间 |
| 距离和问题不会转面积 | 7、23 | 用同一三角形面积的不同表示法求距离和 |
| 正方形/菱形判定条件混淆 | 14、24 | 正方形需比菱形多“直角”或“对角线相等”等条件 |
