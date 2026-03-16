---
title: "MIT 18.063 矩阵微积分：从导数的线性算子本质到反向传播"
description: "细读 MIT 18.063 Matrix Calculus (Jan 2026)：导数 = 线性算子、矩阵函数的微分、链式法则的正向/反向模式、自动微分、变分法、Hessian"
pubDate: 2026-03-16
lang: zh
series: mit-courses
category: algorithm
tags: ["矩阵微积分", "MIT", "自动微分", "反向传播", "链式法则", "梯度", "教材笔记"]
---

# MIT 18.063 矩阵微积分：从导数的线性算子本质到反向传播

> **课程**：MIT 18.063 Matrix Calculus for ML and Beyond, IAP January 2026
> **讲师**：Alan Edelman & Steven G. Johnson
> **前置**：18.06 线性代数 + 18.02 多元微积分

## 核心思想：导数不是"数"，是线性算子

### 传统微积分的局限

18.01 告诉我们 $f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$，导数是一个"数"。

18.02 把这推广到向量：梯度 $\nabla f$ 是向量，Jacobian $J$ 是矩阵。

**但当输入和输出都是矩阵时呢？** $f(X) = X^{-1}$ 的"导数"是什么？

### 统一视角：导数 = 线性算子

$$f(x + dx) - f(x) = df = f'(x)[dx] + o(\|dx\|)$$

$f'(x)$ 是一个**线性算子**，输入 $dx$（微小扰动），输出 $df$（微小变化）。

**例子**：
- $f(X) = X^2 \Rightarrow f'(X)[dX] = X \cdot dX + dX \cdot X$
- $f(X) = X^{-1} \Rightarrow f'(X)[dX] = -X^{-1} dX \, X^{-1}$
- $f(X) = \det(X) \Rightarrow f'(X)[dX] = \det(X) \cdot \text{tr}(X^{-1}dX)$

**这些都是对矩阵 $dX$ 的线性运算**——不需要把矩阵"拉直"成向量再乘 Jacobian！

**对深度学习的意义**：神经网络的权重是矩阵。矩阵微积分直接处理矩阵→矩阵的导数，不需要 vectorization 这种低效操作。

---

## Lec 1-2：基本规则

### 乘积法则（矩阵版）

$$d(AB) = (dA)B + A(dB)$$

注意**顺序不能交换**（矩阵乘法不可交换）！

### 标量函数的梯度

对标量函数 $f(X)$，使用 **Frobenius 内积** $\langle A, B \rangle = \text{tr}(A^T B)$：

$$df = f'(X)[dX] = \langle \nabla f, dX \rangle = \text{tr}((\nabla f)^T \, dX)$$

$\nabla f$ 和 $X$ 有**相同形状**——这就是为什么 PyTorch 的 `.grad` 和参数张量形状一样。

**关键梯度公式**：

- $f(A) = \text{tr}(A) \Rightarrow \nabla f = I$
- $f(A) = \|A\|_F \Rightarrow \nabla f = A / \|A\|_F$
- $f(A) = \mathbf{x}^T A \mathbf{y} \Rightarrow \nabla f = \mathbf{x}\mathbf{y}^T$
- $f(A) = \det(A) \Rightarrow \nabla f = \det(A)(A^{-1})^T = \text{adj}(A)^T$
- $f(\mathbf{x}) = \mathbf{x}^T A\mathbf{x} \Rightarrow \nabla f = (A + A^T)\mathbf{x}$（若 $A$ 对称则 $= 2A\mathbf{x}$）

### Kronecker 积与 Vectorization

把 $m \times n$ 矩阵"拉直"为 $mn \times 1$ 向量：$\text{vec}(X)$

$$\text{vec}(AXB) = (B^T \otimes A)\text{vec}(X)$$

$\otimes$ 是 Kronecker 积。这把矩阵函数的 Jacobian 变成了普通矩阵——但维度爆炸，只在理论分析中有用。

---

## Lec 3：链式法则——正向 vs 反向

### 多维链式法则

$$\frac{d}{dx}[g(f(x))] = g'(f(x)) \circ f'(x)$$

线性算子的复合 = 矩阵乘法。

### 正向模式（Forward Mode）

从输入到输出，逐层计算 $f'(x)[dx]$：

$$dx \to df_1 = f_1'[dx] \to df_2 = f_2'[df_1] \to \cdots \to df_n$$

**每次只能对一个输入方向求导。** 如果有 $n$ 个输入，需要 $n$ 次正向传播。

### 反向模式（Reverse Mode）= 反向传播

从输出到输入，逐层计算"伴随"（adjoint）：

$$\bar{f}_n = 1 \gets \bar{f}_{n-1} = f_n'^T[\bar{f}_n] \gets \cdots \gets \bar{f}_0 = \nabla f$$

**每次对所有输入同时求导！** 一次反向传播就得到完整梯度。

### 关键洞察

- **输入多、输出少**（如损失函数 $\mathbb{R}^{10^6} \to \mathbb{R}$）→ **反向模式高效**
- **输入少、输出多**（如前向模拟）→ **正向模式高效**

**这就是为什么深度学习用反向传播**：参数 $10^6+$，损失是标量。

**对光伏预测的意义**：
- 训练神经网络预测模型 → 反向传播（PyTorch/JAX 自动做）
- 敏感性分析（一个参数的变化如何影响预测）→ 正向模式
- 物理约束优化（PINN）→ 需要混合模式

---

## Lec 5-6：自动微分

### 对偶数（Dual Numbers）— 正向 AD

定义 $a + b\epsilon$，其中 $\epsilon^2 = 0$（不是零，而是"无穷小"）：

$$f(a + b\epsilon) = f(a) + f'(a) \cdot b\epsilon$$

**只要把程序中的浮点数换成对偶数，就自动得到导数！**

```python
# 概念示意（Python）
class Dual:
    def __init__(self, val, deriv=0):
        self.val = val
        self.deriv = deriv
    def __mul__(self, other):
        return Dual(self.val * other.val,
                     self.val * other.deriv + self.deriv * other.val)
```

### 计算图上的反向 AD

神经网络 = 有向无环图（DAG）。每个节点是一个运算。

**前向传播**：从输入到输出，计算每个节点的值
**反向传播**：从输出到输入，计算每个节点的"伴随"（vJP = vector-Jacobian product）

**关键**：现代 AD 是**编译器技术**，不是符号微分也不是有限差分。JAX 的 `jax.grad()` 和 PyTorch 的 `loss.backward()` 背后都是这个。

---

## Lec 4：广义梯度与内积

### 梯度需要内积来定义

在任意向量空间 $V$ 上，标量函数 $f: V \to \mathbb{R}$ 的导数 $f'(x)$ 是线性泛函。

由 **Riesz 表示定理**：任何线性泛函都可以写成和某个向量的内积：

$$f'(x)[dx] = \langle \nabla f, dx \rangle$$

$\nabla f \in V$——梯度和输入"同形状"。

### 梯度 = 最速上升方向

$$\nabla f = \arg\max_{\|v\|=1} f'(x)[v]$$

**但"最速上升"依赖于范数的选择！** 不同的内积给出不同的梯度方向。

这就是为什么**预条件**（preconditioning）和**自然梯度**（natural gradient）有效——它们相当于用更好的内积来定义梯度。

**光伏中的例子**：如果特征的量纲差异大（温度 ~300K vs 辐照度 ~1000 W/m²），标准梯度下降会在不同方向以不同速度收敛。特征标准化 = 改变内积使各方向等权。

---

## Lec 6：变分法

### 函数空间上的微积分

当"变量"是函数 $u(x)$ 时，导数变成**变分导数**：

$$\delta f[u] = f(u + \delta u) - f(u) = f'(u)[\delta u]$$

极值条件 $\nabla f = 0$ → **Euler-Lagrange 方程**

**经典例子**：
- 最短路径 → 测地线方程
- 最小作用量 → Lagrange 力学
- 最优控制 → Hamilton-Jacobi-Bellman 方程

**对光伏预测的意义**：
- Box Ch15 的最优控制理论就是变分法的离散版本
- PINN（物理信息神经网络）的损失函数 = PDE 残差的积分 → 变分问题
- 储能最优调度 = 离散时间的最优控制问题

---

## Lec 7：复数微积分（CR Calculus）

### 问题：$f(z) = |z|^2 = z\bar{z}$ 不可微？

传统复分析要求 Cauchy-Riemann 条件（全纯函数），$|z|^2$ 不满足。

### Wirtinger 导数

定义 $\frac{\partial}{\partial z} = \frac{1}{2}\left(\frac{\partial}{\partial x} - i\frac{\partial}{\partial y}\right)$，$\frac{\partial}{\partial \bar{z}} = \frac{1}{2}\left(\frac{\partial}{\partial x} + i\frac{\partial}{\partial y}\right)$

这让我们可以**对非全纯函数也定义"梯度"**。

**对 ML 的意义**：复数值神经网络（用于信号处理/量子ML）的梯度就需要 CR 微积分。JAX 的复数 AD 就是基于 Wirtinger 导数。

---

## Lec 7+9：约束导数与特征值微分

### 特征值的导数

设 $A(t)$ 是参数化矩阵族，$\lambda(t)$ 是特征值，$\mathbf{v}(t)$ 是特征向量：

$$\frac{d\lambda}{dt} = \frac{\mathbf{v}^T \frac{dA}{dt} \mathbf{v}}{\mathbf{v}^T \mathbf{v}}$$

（对称矩阵情况，即 **Hellmann-Feynman 定理**）

**注意**：当特征值重合时，导数可能不存在！这是优化中的难点。

### Hessian 矩阵与二阶近似

$$f(x + \delta x) \approx f(x) + \nabla f^T \delta x + \frac{1}{2}\delta x^T H \delta x$$

$H$ 正定 → 局部最小值；$H$ 不定 → 鞍点

**Newton 法**：$\delta x = -H^{-1}\nabla f$（二阶收敛，但需要 Hessian）

**拟 Newton 法（BFGS）**：逐步逼近 $H^{-1}$，不需要完整 Hessian

---

## 全课程大统一：矩阵微积分的知识图谱

```
导数 = 线性算子 f'(x)[dx]
    ↓
标量函数 → 梯度 ∇f（需要内积）
矩阵函数 → Jacobian（需要 Kronecker 积/vectorization）
    ↓
链式法则 = 线性算子复合
    ↓
正向模式（输入少）  ←→  反向模式（输出少）
    ↓                       ↓
对偶数 AD            反向传播 / vJP
    ↓                       ↓
正向 AD 库           PyTorch / JAX
    ↓
二阶导数 → Hessian → Newton 法 / BFGS
    ↓
变分法 → Euler-Lagrange → 最优控制 / PINN
```

---

## 与三教材的交叉连接

- **Box Ch7**：ARIMA 参数的 MLE = 最小化 $S(\phi, \theta)$，Marquardt 算法 = Hessian 近似的梯度下降
- **Warner Ch12**：数据同化的变分方法（4D-Var）= 变分法在 NWP 中的应用，损失函数是观测残差 + 背景约束
- **Yang Ch7**：后处理模型的参数优化 = 梯度下降
- **PINN 框架**：物理约束 + 数据拟合 → 混合损失函数 → 需要高效的自动微分

## 对光伏预测项目的行动指南

1. **用 JAX 而非纯 NumPy**：JAX = NumPy + 自动微分 + JIT 编译，完美支持梯度计算
2. **理解 `loss.backward()`**：反向传播不是魔法——是链式法则的反向模式
3. **敏感性分析**：用正向 AD 算单个气象参数对预测的影响
4. **特征标准化 = 修改内积**：确保梯度下降各方向收敛速度一致
5. **Hessian 诊断**：条件数大 → 用 Adam/BFGS；条件数小 → SGD 就够
6. **PINN 的数学基础就在这里**：PDE 约束 + 数据拟合 = 变分问题 + 自动微分

---

*📖 [MIT 课程系列](/blog/tags/MIT) | [18.06 线性代数](/blog/2026-03-16-mit-1806-part1-foundations) | 🧠 MIT 18.063 Matrix Calculus 全课程完成*
