---
title: "MIT 18.06 线性代数 Part 2：投影、最小二乘与 QR 分解"
description: "细读 MIT 18.06 Lecture 8-14：四大子空间的完整图景、正交投影公式、最小二乘法、Gram-Schmidt 与 QR、伪逆"
pubDate: 2026-03-16
lang: zh
series: mit-courses
category: algorithm
tags: ["线性代数", "MIT", "最小二乘", "QR分解", "投影", "伪逆", "教材笔记"]
---

# MIT 18.06 线性代数 Part 2：投影、最小二乘与 QR 分解

> **课程**：MIT 18.06 Linear Algebra, Spring 2025
> **范围**：Lecture 8-14（四大子空间、投影、最小二乘、QR、伪逆）

## Lec 8-9：四大子空间——线性代数的完整图景

### 矩阵的四大子空间

对 $m \times n$ 矩阵 $A$，通过 RREF $R = GA$：

- **列空间** $C(A) = G^{-1}C(R)$，$\subseteq \mathbb{R}^m$，维度 $r$
- **零空间** $N(A) = N(R)$，$\subseteq \mathbb{R}^n$，维度 $n - r$
- **行空间** $C(A^T) = C(R^T)$，$\subseteq \mathbb{R}^n$，维度 $r$
- **左零空间** $N(A^T) = G^T N(R^T)$，$\subseteq \mathbb{R}^m$，维度 $m - r$

### 正交互补关系

$$\mathbb{R}^n = C(A^T) \oplus N(A), \quad \mathbb{R}^m = C(A) \oplus N(A^T)$$

行空间和零空间是 $\mathbb{R}^n$ 中的正交互补；列空间和左零空间是 $\mathbb{R}^m$ 中的正交互补。

**这是线性代数最深刻的结构定理。** 它说明了：
- 对 $A\mathbf{x} = \mathbf{b}$，$\mathbf{b}$ 可以唯一分解为列空间分量 + 左零空间分量
- 列空间分量是"$A$ 能解释的部分"，左零空间分量是"残差"

**光伏预测中的四大子空间**：

设 $A$ 是气象特征矩阵（$m$ 个时间步 × $n$ 个特征）：
- $C(A)$：特征组合能解释的功率变化空间
- $N(A^T)$：特征无法解释的功率变化（"纯噪声"方向）
- $C(A^T)$：有效特征方向
- $N(A)$：冗余特征组合（多重共线性！）

当 $N(A)$ 维度大时，说明特征间高度共线——需要正则化或降维（PCA/Ridge）。

---

## Lec 10-11：正交投影

### 投影的几何意义

$$\mathbf{v} = \text{proj}_V(\mathbf{x}) = V \text{ 中距 } \mathbf{x} \text{ 最近的点}$$

等价条件：$(\mathbf{x} - \mathbf{v}) \perp V$

### 投影矩阵公式

设 $V = C(A)$，$A$ 是 $n \times r$ 且 $\text{rank}(A) = r$：

$$P_V = A(A^T A)^{-1}A^T$$

**性质**：
- $P_V^2 = P_V$（幂等：投影两次 = 投影一次）
- $P_V^T = P_V$（对称）
- $\text{rank}(P_V) = r$（列空间 = $V$）

### 为什么 $A^T A$ 可逆？

当 $A$ 列满秩时，$A^T A$ 是 $r \times r$ 正定矩阵。直觉：$A^T A$ 的零空间 = $A$ 的零空间 = $\{\mathbf{0}\}$。

**与 Box 的联系**：Box Ch7 的正规方程 $A^T A \hat{\boldsymbol{\phi}} = A^T \mathbf{z}$ 就是在做正交投影——将数据 $\mathbf{z}$ 投影到设计矩阵的列空间。Yule-Walker 方程 $\mathbf{P}_p \boldsymbol{\phi} = \boldsymbol{\rho}_p$ 的 $\mathbf{P}_p$ 就是 Toeplitz 结构的 $A^T A$。

---

## Lec 12：最小二乘法

### 核心公式

$$\hat{\mathbf{x}} = (A^T A)^{-1} A^T \mathbf{b}$$

最小化 $\|A\mathbf{x} - \mathbf{b}\|^2 = \sum_i [(A\mathbf{x})_i - b_i]^2$。

### 实际应用

**无截距直线拟合**：$b = xa$
- 设计矩阵 $A = \mathbf{a}$（单列），$\hat{x} = \frac{\mathbf{a}^T \mathbf{b}}{\mathbf{a}^T \mathbf{a}}$

**有截距直线拟合**：$b = x_0 + x_1 a$
- 设计矩阵 $A = [\mathbf{1} | \mathbf{a}]$（两列）

**多项式拟合**：$b = x_0 + x_1 a + x_2 a^2 + x_3 a^3$
- 设计矩阵 $A = [\mathbf{1} | \mathbf{a} | \mathbf{a}^2 | \mathbf{a}^3]$（Vandermonde 矩阵）

**光伏中的最小二乘**：
- 温度模型参数拟合：$T_{cell} = T_{amb} + \alpha \cdot GHI + \beta \cdot WS + \gamma$
- Box Ch7 的条件 MLE = 条件最小二乘
- Yang Ch7 的 MOS（模式输出统计）后处理 = 多元线性回归

### ⚠️ 最小二乘 vs PCA

**最小二乘**最小化**垂直距离**（$y$ 方向残差）：适合 $y = f(x)$ 回归

**PCA**最小化**正交距离**（到子空间的最短距离）：适合数据压缩/降维

教材称 PCA 为"perpendicular least squares"——两者不是一回事！

---

## Lec 13：Gram-Schmidt 与 QR 分解

### Gram-Schmidt 正交化

输入：基 $(v_1, \ldots, v_r)$
输出：正交归一基 $(u_1, \ldots, u_r)$

$$u_k = \frac{v_k - \sum_{j=1}^{k-1}(v_k \cdot u_j)u_j}{\|v_k - \sum_{j=1}^{k-1}(v_k \cdot u_j)u_j\|}$$

### QR 分解

$$A = QR$$

- $Q$：$n \times r$，列正交归一
- $R$：$r \times r$，上三角

**QR 的数值优势**：
- 直接用正规方程 $(A^T A)\hat{\mathbf{x}} = A^T\mathbf{b}$ 数值不稳定（条件数平方）
- 用 QR：$\hat{\mathbf{x}} = R^{-1}Q^T\mathbf{b}$，条件数不变

**实际应用**：NumPy 的 `np.linalg.lstsq()` 内部就用 QR 分解，不是正规方程。

---

## Lec 14：伪逆

### 最小范数解

当 $A$ 是 $r \times n$（$r < n$，欠定系统）：解有无穷多个。**最小范数解** = 行空间分量 $\mathbf{x}^\perp$。

### 矩阵伪逆 $A^+$

对任意 $m \times n$ 矩阵 $A$：
1. 将 $\mathbf{y}$ 投影到 $C(A)$ 得 $\mathbf{b}$
2. 解 $A\mathbf{x} = \mathbf{b}$ 的最小范数解

$$A^+ : \mathbb{R}^m \to \mathbb{R}^n$$

**两种特殊情况**：
- $A$ 列满秩（$m \geq n = r$）：$A^+ = (A^T A)^{-1} A^T$（左逆，最小二乘）
- $A$ 行满秩（$n \geq m = r$）：$A^+ = A^T(AA^T)^{-1}$（右逆，最小范数）

**通过 SVD 计算**（Lec 26）：$A = U\Sigma V^T \Rightarrow A^+ = V\Sigma^{-1}U^T$

**光伏中的伪逆**：
- 当气象特征多于观测（$n > m$）时，直接最小二乘无唯一解 → 伪逆给出最小范数解
- 等价于 Ridge 回归 $\lambda \to 0$ 的极限
- NWP 数据同化中，观测算子 $H$ 通常是"宽矩阵"（观测少于状态变量），需要伪逆

---

## 深度思考：最小二乘的统一视角

| 领域 | 矩阵方程 | $A$ 的含义 | $\mathbf{b}$ 的含义 |
|------|----------|-----------|-------------------|
| **线性回归** | $A\mathbf{x} = \mathbf{b}$ | 设计矩阵（特征） | 响应变量 |
| **Box ARIMA** | $\Phi\hat{\boldsymbol{\phi}} = \boldsymbol{\rho}$ | Toeplitz ACF 矩阵 | ACF 向量 |
| **NWP 同化** | $H\mathbf{x} = \mathbf{y}_{obs}$ | 观测算子 | 观测值 |
| **pvlib 温度** | $A\boldsymbol{\beta} = T_{cell}$ | 气象特征矩阵 | 电池温度 |
| **图像压缩** | $\approx U_k\Sigma_k V_k^T$ | 左奇异向量 | — |

**所有这些问题的数学本质都是：在列空间中找到最接近 $\mathbf{b}$ 的点。**

---

## 模块小结

Lecture 8-14 是 18.06 的精华——投影和最小二乘是理解一切回归方法的几何基础。

**核心公式链**：
1. 四大子空间的正交互补 → 任何向量唯一分解
2. 正交投影 $P = A(A^TA)^{-1}A^T$ → 最佳近似
3. 最小二乘 $\hat{\mathbf{x}} = (A^TA)^{-1}A^T\mathbf{b}$ → 参数估计
4. QR 分解 → 数值稳定实现
5. 伪逆 → 统一处理超定/欠定系统

**下一篇预告**：Lec 15-19 行列式 + Lec 20-23 特征值——ARIMA 特征方程的数学基础。

---

*📖 [MIT 课程系列](/blog/) | [Part 1: 向量空间](/blog/2026-03-16-mit-1806-part1-foundations) | 🧠 MIT 18.06 Spring 2025*
