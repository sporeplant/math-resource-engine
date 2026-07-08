---
content_type: textbook_original
textbook_version: JJ2022
semester: 8A
chapter_name: 特殊三角形
section_name: 反证法
lesson_id: 17.5.1
---

## 17.5 反证法

在证明命题为真命题时，一般用直接证明的方法，但有时用间接证明的方法可能更方便。反证法就是一种常用的间接证明方法。 

在第十章中，我们已经知道“一个三角形中最多有一个直角”这个结论．那么，怎样证明它呢？ 

已知：如图 17.5-1， $\triangle ABC$ . 

求证：在 $\triangle ABC$ 中，如果它含有直角，那么它只能有一个直角. 

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/29195f10a36e20409cd81872b12087c4a4f651d1c25b0f81f6f65ab3714ac848.jpg)


证明：假设 $\triangle ABC$ 中有两个(或三个)直角，不妨设 $\angle A = \angle B = 90^{\circ}$ . 

图17.5-1 

$$
\because \angle A + \angle B = 1 8 0 ^ {\circ},
$$

$$
\therefore \angle A + \angle B + \angle C > 1 8 0 ^ {\circ}.
$$

这与“三角形的内角和等于 $180^{\circ}$ ”相矛盾. 

因此，一个三角形中有两个(或三个)直角的假设是不成立的. 

所以，如果一个三角形中含有直角，那么它只能有一个直角. 

上面的证明过程，是先假设原命题的结论不正确，再从这个假设出发，经过逐步推理论证，最后推出与学过的三角形内角和定理相矛盾的结果。因此，假设是错误的，原结论是正确的。 

这种证明命题的方法叫作反证法(proof by contradiction). 反证法是一种间接证明的方法. 

用反证法证明一个命题是真命题的一般步骤是： 

第一步，假设命题的结论不成立. 

第二步，从这个假设和其他已知条件出发，经过推理论证，得出与学过的概念、基本事实，已证明的定理、性质或题设条件相矛盾的结果. 

第三步，由矛盾的结果，判定假设不成立，从而说明命题的结论是正确的. 

例 1* 用反证法证明平行线的性质定理：两条平行线被第三条直线所截，同位角相等. 

已知：如图 17.5-2，直线 $AB \parallel CD$ ，直线 $EF$ 分别与直线 $AB$ ， $CD$ 交于点 $G$ ， $H$ ， $\angle 1$ 和 $\angle 2$ 是同位角。 

求证： $\angle 1 = \angle 2$ 

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/9e8390f33a5c27633f2013a0a704743a45b83b78676beaa94e61d55f40b75d55.jpg)



图17.5-2


证明：假设 $\angle 1 \neq \angle 2$ 

过点 G 作直线 MN，使得 $\angle EGN = \angle 1$ . 

$$
\because \angle E G N = \angle 1,
$$

∴ $MN \parallel CD$ （基本事实）. 

又∵ $AB \parallel CD$ （已知）， 

∴ 过点 G，有两条不同的直线 AB 和 MN 都与直线 CD 平行。这与 “过直线外一点有且只有一条直线与这条直线平行” 相矛盾。 

∴ $\angle1\neq\angle2$ 的假设是不成立的. 

因此， $\angle 1 = \angle 2$ 

例 2 用反证法证明直角三角形全等的“斜边、直角边”定理. 

已知：如图 17.5-3，在 $\triangle ABC$ 和 $\triangle A^{\prime}B^{\prime}C^{\prime}$ 中， $\angle C=\angle C^{\prime}=90^{\circ}$ ， 

$$
A B = A ^ {\prime} B ^ {\prime}, A C = A ^ {\prime} C ^ {\prime}.
$$

求证： $\triangle ABC \cong \triangle A'B'C'$ . 

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/f95f8d08b4cc3df8819c02e2d51d63d1ac229b66f6512d278b229908977dfbb1.jpg)



图17.5-3


证明：假设 $\triangle ABC$ 与 $\triangle A'B'C'$ 不全等，即 $BC \neq B'C'$ 。不妨设 $BC < B'C'$ 。如图17.5-3，在 $B'C'$ 上截取 $C'D = CB$ ，连接 $A'D$ 。 

在 $\triangle ABC$ 和 $\triangle A^{\prime}DC^{\prime}$ 中， 

$$
\because A C = A ^ {\prime} C ^ {\prime}, \angle C = \angle C ^ {\prime}, C B = C ^ {\prime} D,
$$

∴ $\triangle ABC \cong \triangle A'DC'$ (SAS). 

∴ $AB = A'D$ （全等三角形的对应边相等）. 

∵ $AB = A'B'$ （已知）， 

∴ $A^{\prime}B^{\prime}=A^{\prime}D$ （等量代换）. 

∴ $\angle B' = \angle A'DB'$ (等边对等角). 

∴ $\angle A^{\prime}DB^{\prime}<90^{\circ}$ （三角形的内角和定理）， 

即 $\angle C' < \angle A'DB' < 90^\circ$ （三角形的外角大于和它不相邻的内角）. 

这与 $\angle C^{\prime}=90^{\circ}$ 相矛盾. 

因此， $BC \neq B'C'$ 的假设不成立，即 $\triangle ABC$ 与 $\triangle A'B'C'$ 不全等的假设不成立. 

所以， $\triangle ABC \cong \triangle A'B'C'$ . 

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/79393e2ecad1872f3e792ab1d0111961adc7d7391bed3c24c8c20c0b3904578b.jpg)


## 做一做

用反证法证明： 

（1）如果 $a \cdot b = 0$ ，那么 a，b 中至少有一个等于 0. 

(2) 两条直线相交，有且只有一个交点. 

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/3a4f2cd67118dae8e7812782615c06284b71663b34bf46ec34772a880ba6461d.jpg)


## 练习

已知：直线 $a \perp b$ ，直线 $c$ 与 $b$ 相交，且 $c$ 与 $b$ 不垂直。请用反证法证明： $a$ 与 $c$ 相交。 

## 习题

## A组

1. 用反证法证明 “ $\sqrt{2}$ 是无理数”，最恰当的方法是先假设 ____. 

2. 填空： 

小明尝试用反证法证明 “一个三角形中不能含有两个直角”，他写出了以下三个步骤： 

①假设在 $\triangle ABC$ 中， $\angle A$ 和 $\angle B$ 都是直角； 

②则 $\angle A+\angle B+\angle C>180^{\circ}$ ，____； 

③假设不成立，所以一个三角形中____含有两个直角。（填“能”或“不能”） 

## B组

3. 已知：在 $\triangle ABC$ 中， $AB \neq AC$ 。用反证法证明： $\angle B \neq \angle C$ 

4. 用反证法证明：垂直于同一条直线的两条直线平行. 

## C组

5. 用反证法证明：一个三角形中最大的内角不小于 $60^{\circ}$ . 

6. 用反证法证明：如果两条直线都平行于第三条直线，那么这两条直线也互相平行. 

![](https://cdn.jsdelivr.net/gh/sporeplant/math-resource-engine@main/knowledge/images/4c437b12f24584cbbd37e8ecec8b02656f70aa7789ae45aea691982ed19a033b.jpg)
