---
title: "MIT 18.06 线性代数 Part 3：特征值、SVD 与数据科学"
description: "细读 MIT 18.06 Lecture 15-27：行列式、特征值分解、谱定理、SVD、低秩近似、图像压缩——从纯数学到光伏预测的桥梁"
pubDate: 2026-03-16
lang: zh
series: mit-courses
category: algorithm
tags: ["线性代数", "MIT", "特征值", "SVD", "PCA", "低秩近似", "教材笔记"]
---

# MIT 18.06 线性代数 Part 3：特征值、SVD 与数据科学

> **课程**：MIT 18.06 Linear Algebra, Spring 2025
> **范围**：Lecture 15-27（行列式、特征值、SVD、低秩近似）

## Lec 15-19：行列式

### 行列式 = 体积的有符号缩放因子

$$\det A = \text{线性变换 } A \text{ 对 } n \text{ 维体积的缩放倍数（带符号）}$$

**关键性质**：
- 乘积公式：$\det(AB) = (\det A)(\det B)$
- $\det A \neq 0 \Leftrightarrow A$ 可逆
- 上三角矩阵：$\det = $ 对角线元素之积

### 大公式（Lec 16）

$$\det A = \sum_{\sigma} (\text{sgn}\,\sigma) \prod_{i=1}^n a_{i,\sigma(i)}$$

$n!$ 个排列求和——虽然理论上美丽，但计算用高斯消元更高效。

### Laplace 展开与伴随矩阵（Lec 17, 19）

余因子 $C_{ij} = (-1)^{i+j}\det M_{ij}$（$M_{ij}$ 是去掉第 $i$ 行第 $j$ 列的子矩阵）

$$A^{-1} = \frac{1}{\det A}C^T$$

**Cramer 法则**：$x_j = \frac{\det A_j}{\det A}$（$A_j$ 是 $A$ 的第 $j$ 列替换为 $\mathbf{b}$）

**实际价值**：行列式在理论推导中很美（特征方程 $\det(A - \lambda I) = 0$），但大规模数值计算中几乎不直接用。

---

## Lec 20-22：特征值与对角化

### 特征值问题

$$A\mathbf{v} = \lambda\mathbf{v}, \quad \mathbf{v} \neq \mathbf{0}$$

矩阵 $A$ 在特征方向上只做缩放（$\lambda$），不改变方向。

### 特征多项式

$$p_A(\lambda) = \det(A - \lambda I) = (-1)^n\lambda^n + (-1)^{n-1}\alpha\lambda^{n-1} + \cdots + \det A$$

其中 $\alpha = \text{tr}(A)$。$n$ 个根（含复数和重根）= $n$ 个特征值。

### 对角化

$$A = EDE^{-1}$$

$E$ 的列 = 特征向量，$D$ 的对角线 = 特征值。

**对角化条件**：当且仅当每个特征值的几何重数 = 代数重数。

- 所有特征值不同 → 一定可对角化
- 有重根 → 不一定（如 Jordan 块）

### 与 Box ARIMA 的深度联系

Box Ch3 的 AR(p) 特征方程 $\phi(B) = 0$ 本质就是求 $\phi$ 算子的特征值：

- 根在单位圆外 → $|\lambda| < 1$ → 平稳（衰减）
- 根在单位圆上 → $|\lambda| = 1$ → 非平稳（ARIMA 的 $d$ 个单位根）
- 根在单位圆内 → $|\lambda| > 1$ → 爆炸

AR(2) 的复数特征值产生**伪周期行为**（阻尼正弦波）——太阳黑子数据就是 AR(2) 的经典例子。

Warner NWP Ch5 的声波/重力波分析也是特征值问题：大气方程组线性化后的特征值决定了波的传播速度和稳定性。

---

## Lec 23：复数特征值与谱定理

### 实矩阵的复特征值成共轭对出现

如果 $\lambda = a + bi$ 是特征值，那 $\bar{\lambda} = a - bi$ 也是。

### 谱定理（对称矩阵）

> **如果 $A$ 是实对称矩阵（$A = A^T$），则：**
> 1. 所有特征值都是**实数**
> 2. 特征向量形成**正交归一基**
> 3. $A = E D E^T$（$E$ 正交矩阵）

**这是线性代数最优美的定理之一。** 对称矩阵的特征分解 = 旋转 + 缩放 + 反旋转。

**光伏中的应用**：协方差矩阵 $\Sigma = \frac{1}{n}X^TX$ 一定是对称半正定的 → 一定有正交特征分解 → 这就是 PCA 的数学基础。

---

## Lec 24：正定矩阵与 SVD 引入

### 正定性

对称矩阵 $A$ **正定（PD）** $\Leftrightarrow$ 所有特征值 > 0 $\Leftrightarrow$ $\mathbf{x}^T A\mathbf{x} > 0, \forall \mathbf{x} \neq 0$

**半正定（PSD）**：所有特征值 $\geq 0$

关键事实：**对任意矩阵 $M$，$M^TM$ 和 $MM^T$ 都是半正定的。**

### SVD 奇异值分解

对任意 $n \times p$ 矩阵 $M$（不要求方阵！）：

$$M = U\Sigma V^T$$

- $U$：$n \times r$，左奇异向量（$M$ 列空间的正交基）
- $\Sigma$：$r \times r$，奇异值对角矩阵（$\sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_r > 0$）
- $V$：$p \times r$，右奇异向量（$M$ 行空间的正交基）

**SVD 同时揭示了矩阵的四大子空间的正交基！**

---

## Lec 25-26：SVD 计算与几何解释

### 计算步骤

1. $A = M^TM$ 的特征分解：$A = EDE^T$
2. $V$ = $E$ 的前 $r$ 列（$d_i > 0$ 对应的特征向量）
3. $\sigma_i = \sqrt{d_i}$
4. $U = MV\Sigma^{-1}$

### 几何意义

- **算子范数** $\|M\|_{op} = \sigma_1$：$M$ 能将单位球拉伸的最大倍数
- **伪逆通过 SVD**：$M^+ = V\Sigma^{-1}U^T$
- **条件数** $\kappa = \sigma_1/\sigma_r$：越大越病态

---

## Lec 27：低秩近似与图像压缩

### Eckart-Young 定理

$$M_k = U_k\Sigma_k V_k^T = \text{最佳秩-}k\text{ 近似}$$

在谱范数、Frobenius 范数、核范数下都是最优的。

### 图像压缩

原始图像 $M$：$n \times p$ 个像素（存 $np$ 个值）
压缩后 $M_k$：存 $(n + p)k + k$ 个值

当 $k \ll \min(n,p)$ 时，**压缩比巨大**。

### 对光伏预测的启示

**多站点功率数据矩阵**（$m$ 个时间步 × $n$ 个电站）：

如果秩 $r \ll n$（因为相邻电站高度相关），则：
- 低秩近似 $M_k$ 去噪
- $U_k$ 的列 = "典型功率模式"（晴天、多云、阴天等）
- $V_k$ 的列 = "空间模式"（哪些电站行为类似）
- $\Sigma_k$ = 每种模式的"能量"

Yang Ch12 的层次预测（hierarchical forecasting）本质上就是利用多站点功率矩阵的低秩结构。

**气象特征矩阵降维**：
- 原始特征：温度、湿度、气压、风速、风向、云量、辐照度……（$p$ 维）
- SVD/PCA 降到 $k$ 维 → 去除冗余 → 减少过拟合

---

## 深度联系：SVD 统一了一切

SVD 是线性代数的"终极武器"——几乎所有重要概念都可以通过 SVD 理解：

- **四大子空间**：$U$ 的列 = $C(M)$ 基，$V$ 的列 = $C(M^T)$ 基
- **秩**：$\sigma_i > 0$ 的个数
- **最小二乘**：$\hat{\mathbf{x}} = M^+\mathbf{b} = V\Sigma^{-1}U^T\mathbf{b}$
- **PCA**：数据矩阵的右奇异向量 = 主成分方向
- **低秩近似**：Eckart-Young → 数据压缩/去噪
- **条件数**：$\sigma_1/\sigma_r$ → 数值稳定性诊断
- **正则化**：Tikhonov 正则 = 截断小奇异值

### 三教材中的 SVD

| 教材 | SVD 的角色 |
|------|-----------|
| **Box** | 残差协方差矩阵的特征分解 → 主成分残差分析 |
| **Warner** | EOF（经验正交函数）= 气象场的 PCA = 对 气候数据矩阵做 SVD |
| **Yang** | 多站点预测的空间模式提取 |

---

## 模块小结

Lecture 15-27 从行列式→特征值→SVD，逐步揭示了矩阵的内在结构。

**核心思想链**：

$$\underbrace{\det(A-\lambda I) = 0}_{\text{特征方程}} \to \underbrace{A = EDE^{-1}}_{\text{对角化}} \to \underbrace{A = EDE^T}_{\text{谱定理（对称）}} \to \underbrace{M = U\Sigma V^T}_{\text{SVD（任意矩阵）}}$$

每一步都是前一步的推广。SVD 是最终形态——适用于任意矩阵，同时给出最优近似。

**下一篇预告**：Lec 28-36 进入 PCA、DFT、循环矩阵——信号处理和时间序列分析的数学核心。

---

*📖 [MIT 课程系列](/blog/) | [Part 2: 投影与最小二乘](/blog/2026-03-16-mit-1806-part2-projection-leastsquares) | 🧠 MIT 18.06 Spring 2025*
