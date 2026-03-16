---
title: "Box 时间序列分析 Ch4：ARIMA——差分使非平稳变平稳"
description: "细读 Box《Time Series Analysis》第4章：差分算子的物理意义、ARIMA(p,d,q) 三种显式形式、IMA 过程与指数平滑的等价性"
pubDate: 2026-03-16
lang: zh
series: box-timeseries
category: timeseries
tags: ["时间序列", "ARIMA", "差分", "非平稳", "IMA", "指数平滑", "教材笔记"]
---

# Box 时间序列分析 Ch4：ARIMA——差分使非平稳变平稳

> **教材**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 4

## 核心思想

Ch3 的 ARMA 只处理平稳序列。但大量实际序列（股价、销量、温度）**没有固定均值**。Ch4 的关键洞察：

> **差分 $d$ 次可以将"齐次非平稳"序列转化为平稳序列。**

$$\phi(B)\nabla^d z_t = \theta(B)a_t$$

这就是 ARIMA(p,d,q) 模型，其中 $\nabla = 1 - B$ 是差分算子。

---

## 4.1 ARIMA 过程的定义

### 为什么不是"根在圆内"的非平稳？

Box 首先排除了 $\phi(B) = 0$ 根在单位圆**内**的情况——这会产生**爆炸性过程**（如 $z_t = 2z_{t-1} + a_t$，序列指数爆炸）。这不是我们要建模的类型。

我们要的非平稳是**齐次的（homogeneous）**——没有固定水平，但局部行为处处相似。数学上，这对应 $\phi(B) = 0$ 有 $d$ 个根**恰好在单位圆上**（等于 1）。

### ARIMA 的两种理解

1. **差分视角**：$w_t = \nabla^d z_t$ 是平稳 ARMA 过程，$z_t$ 是对 $w_t$ 的 $d$ 次累积求和（"积分"）
2. **齐次性视角**：
   - $d = 1$：$z_t$ 的水平可以自由漂移，但 $\nabla z_t$ 平稳 → **随机水平**
   - $d = 2$：$z_t$ 的水平和斜率都可以自由变化，但 $\nabla^2 z_t$ 平稳 → **随机水平 + 随机趋势**

### 常数项 $\theta_0$ 的含义

$$\phi(B)\nabla^d z_t = \theta_0 + \theta(B)a_t$$

当 $d \geq 1$ 时，$\theta_0 \neq 0$ 意味着**确定性趋势**：
- $d = 1, \theta_0 \neq 0$：$z_t$ 有线性确定性趋势，斜率 $\mu_w = \theta_0/(1 - \phi_1 - \cdots - \phi_p)$

**Box 的建议**：除非数据或物理原因明确支持，通常假设 $\theta_0 = 0$（随机趋势比确定性趋势更灵活）。

---

## 4.2 三种显式形式

### 形式 1：差分方程形式

$$z_t = \varphi_1 z_{t-1} + \cdots + \varphi_{p+d} z_{t-p-d} + a_t - \theta_1 a_{t-1} - \cdots - \theta_q a_{t-q}$$

其中 $\varphi(B) = \phi(B)(1-B)^d$。**计算预测时最方便**。

### 形式 2：随机冲击形式

$$z_t = a_t + \psi_1 a_{t-1} + \psi_2 a_{t-2} + \cdots$$

$\psi$ 权重由 $\varphi(B)\psi(B) = \theta(B)$ 递推求解。**计算预测误差方差时需要**。

### 形式 3：反转形式（π 权重）

$$z_t = \pi_1 z_{t-1} + \pi_2 z_{t-2} + \cdots + a_t$$

$\pi$ 权重由 $\theta(B)\pi(B) = \varphi(B)$ 递推。**表示为无穷 AR 的形式，指数加权移动平均（EWMA）就是特例**。

---

## 4.3 IMA 过程——指数平滑的理论基础

### IMA(0,1,1)

$$\nabla z_t = (1 - \theta_1 B)a_t$$

反转形式：$z_t = (1-\theta_1) z_{t-1} + \theta_1(1-\theta_1) z_{t-2} + \cdots + a_t$

令 $\lambda = 1 - \theta_1$，这就是**指数加权移动平均（EWMA）**！权重以 $\theta_1^j$ 的速率指数衰减。

**历史意义**：Holt/Brown/Winters 的指数平滑方法在 Box-Jenkins 之前就被广泛使用了。Box 证明了这些方法**恰好是 IMA(0,1,1) 的最优预测**——给经验方法提供了严格的统计基础。

### IMA(0,2,2)

$$\nabla^2 z_t = (1 - \theta_1 B - \theta_2 B^2)a_t$$

最优预测沿**直线**变化（水平 + 斜率持续更新）。对应 **Holt 双参数指数平滑**。

---

## 深度思考

### 1. 差分 vs 去趋势

- **差分 $\nabla^d$**：消除 $d$ 阶多项式趋势；假设趋势是随机的；适用于大多数经济/工业序列
- **回归去趋势**：$z_t = f(t) + \epsilon_t$；假设趋势是确定性的；适用于有物理趋势的序列
- **物理模型去趋势**：$z_t - \text{clearsky}_t$；假设物理模型已知；适用于光伏辐照度

**对光伏**：先用晴空模型物理去趋势（Yang Ch7），残差如果仍非平稳，再差分一次。

### 2. d 的实际选择

Box 反复强调：$d$ 通常取 0、1、最多 2。
- $d = 0$：平稳序列
- $d = 1$：水平漂移（最常见）
- $d = 2$：趋势漂移（较少见）
- $d \geq 3$：几乎不需要

### 3. 单位根与非平稳的现代检验

Box 时代主要靠 ACF 判断是否需要差分（ACF 缓慢衰减 → 可能需要差分）。现代方法有：
- **ADF 检验**（Augmented Dickey-Fuller）
- **KPSS 检验**
- **Phillips-Perron 检验**

这些将在 Ch6（模型识别）中间接涉及。

### 4. 过度差分的危险

差分 $d$ 次后如果序列本来就平稳，会**引入不必要的 MA 单位根**，导致参数估计不稳定。Box 的建议：宁可少差分，用 ACF/PACF 判断。

---

## 小结

Ch4 = Ch3 的非平稳扩展。核心公式只有一个：

$$\phi(B)(1-B)^d z_t = \theta_0 + \theta(B)a_t$$

但它的威力巨大——几乎所有非季节性时间序列都可以用 $p, d, q \leq 2$ 的 ARIMA 来描述。

**下一章预告**：Ch5 将展示如何用 ARIMA 模型进行最优预测（最小 MSE 预测函数）。

---

*📖 [Ch3 笔记](/blog/2026-03-16-box-ch3-linear-stationary-models) | [返回教材目录](/textbook/) | 📝 [Box 时间序列系列](/blog/)*
