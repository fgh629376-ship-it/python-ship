---
title: "Box 时间序列分析 Ch3：AR、MA、ARMA 模型的完整解剖"
description: "细读 Box《Time Series Analysis》第3章：从 Wold 分解到 AR/MA 对偶性，掌握 PACF 截断判阶、Yule-Walker 方程、可逆性条件"
pubDate: 2026-03-16
lang: zh
series: box-timeseries
category: timeseries
tags: ["时间序列", "ARIMA", "AR模型", "MA模型", "PACF", "Yule-Walker", "教材笔记"]
---

# Box 时间序列分析 Ch3：AR、MA、ARMA 模型的完整解剖

> **教材**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 3

## 章节定位

Ch2 给了描述工具（ACF/谱），Ch3 给出了**可操作的参数模型**。这一章是全书最核心的理论章节——后续所有的建模、预测、控制都建立在这里的 AR/MA/ARMA 框架上。

---

## 3.1 一般线性过程

### Wold 分解定理

**任何**零均值纯非确定性平稳过程都可以表示为：

$$\tilde{z}_t = \sum_{j=0}^{\infty} \psi_j a_{t-j}, \quad \psi_0 = 1, \quad \sum_{j=0}^{\infty} \psi_j^2 < \infty$$

这是 Wold (1938) 的基本结果。意义：**线性模型不是一种"假设"，而是平稳过程的通用表示**。

### ψ 权重与 π 权重的对偶

- **ψ 形式**（MA 表示）：$\tilde{z}_t = \psi(B)a_t$（当前值 = 过去冲击的加权和）
- **π 形式**（AR 表示）：$\pi(B)\tilde{z}_t = a_t$（当前冲击 = 当前值与过去值的线性组合）

关系：$\psi(B)\pi(B) = 1$，即 $\pi(B) = \psi^{-1}(B)$

### 自协方差生成函数

$$\gamma(B) = \sigma_a^2 \psi(B)\psi(B^{-1})$$

**谱与滤波器增益**：$p(f) = 2\sigma_a^2 |\psi(e^{-i2\pi f})|^2$

输出谱 = 白噪声谱 × 滤波器增益的平方。

### 平稳性与可逆性

- **平稳**：要求 $\sum|\psi_j| < \infty$，等价表述为 $\psi(B)$ 在 $|B| \leq 1$ 收敛
- **可逆**：要求 $\sum|\pi_j| < \infty$，等价表述为 $\pi(B)$ 在 $|B| \leq 1$ 收敛

**可逆性的物理意义**：当前值可以用过去值（而非未来值）来表达。如果 $|\theta| \geq 1$，MA 模型的 π 权重会发散——当前值取决于无穷远过去且权重越来越大，这不合理。

---

## 3.2 自回归过程 AR(p)

### 平稳条件

$\phi(B) = 0$ 的所有根在**单位圆外**。等价地，特征方程 $m^p - \phi_1 m^{p-1} - \cdots - \phi_p = 0$ 的根在**单位圆内**。

### ACF 的差分方程

$$\rho_k = \phi_1\rho_{k-1} + \phi_2\rho_{k-2} + \cdots + \phi_p\rho_{k-p}, \quad k > 0$$

通解：$\rho_k = A_1 G_1^k + A_2 G_2^k + \cdots + A_p G_p^k$

- **实数根** → 指数衰减
- **复数共轭根** → 阻尼正弦波（伪周期行为）

### AR(1)：马尔可夫过程

$$\tilde{z}_t = \phi_1 \tilde{z}_{t-1} + a_t, \quad |\phi_1| < 1$$

- ACF：$\rho_k = \phi_1^k$（指数衰减）
- 方差：$\sigma_z^2 = \sigma_a^2 / (1 - \phi_1^2)$
- 谱：$p(f) = 2\sigma_a^2 / (1 + \phi_1^2 - 2\phi_1\cos 2\pi f)$
- $\phi_1 > 0$ → 光滑趋势、低频主导
- $\phi_1 < 0$ → 锯齿振荡、高频主导

### AR(2)：伪周期行为

平稳条件（三角形区域）：$\phi_2 + \phi_1 < 1$, $\phi_2 - \phi_1 < 1$, $-1 < \phi_2 < 1$

复数根时的 ACF：$\rho_k = D^k \sin(2\pi f_0 k + F) / \sin F$

其中阻尼因子 $D = \sqrt{-\phi_2}$，频率 $f_0 = \cos^{-1}(\phi_1 / 2\sqrt{-\phi_2}) / (2\pi)$

**对光伏的启示**：辐照度序列经常显示伪周期行为（天气系统周期 3-7 天），AR(2) 可以捕获这种行为。

### Yule-Walker 方程

$$\boldsymbol{P}_p \boldsymbol{\phi} = \boldsymbol{\rho}_p$$

线性方程组，用 ACF 估计值 $r_k$ 代入即可求解 AR 参数。

### PACF（偏自相关函数）

$$\phi_{kk} = \text{corr}[z_t - \hat{z}_t, z_{t-k} - \hat{z}_{t-k}]$$

**核心性质：AR(p) 的 PACF 在 lag $p$ 后截断为零。**

- AR(1)：$\phi_{11} = \rho_1$, $\phi_{kk} = 0$ ($k \geq 2$)
- AR(2)：$\phi_{22} = (\rho_2 - \rho_1^2)/(1 - \rho_1^2)$, $\phi_{kk} = 0$ ($k \geq 3$)

估计的 PACF 标准误差：$\text{SE}[\hat{\phi}_{kk}] \approx 1/\sqrt{n}$ ($k \geq p+1$)

---

## 3.3 移动平均过程 MA(q)

### 可逆性条件

$\theta(B) = 0$ 的根在单位圆外。

### ACF 的截断性

$$\rho_k = \begin{cases} \frac{-\theta_k + \theta_1\theta_{k+1} + \cdots + \theta_{q-k}\theta_q}{1 + \theta_1^2 + \cdots + \theta_q^2} & k = 1, \ldots, q \\ 0 & k > q \end{cases}$$

**核心性质：MA(q) 的 ACF 在 lag $q$ 后截断为零。**

### MA(1) 详解

- ACF：$\rho_1 = -\theta_1 / (1 + \theta_1^2)$, $\rho_k = 0$ ($k > 1$)
- $|\rho_1| \leq 0.5$（MA(1) 的理论上限！）
- 给定 $\rho_1$，$\theta_1$ 有两个解（$\theta_1$ 和 $\theta_1^{-1}$），取 $|\theta_1| < 1$ 的可逆解

### AR ↔ MA 的完美对偶

- **ACF**：AR(p) 无穷延伸（指数衰减/阻尼正弦）；MA(q) **lag $q$ 后截断**
- **PACF**：AR(p) **lag $p$ 后截断**；MA(q) 无穷延伸（指数衰减/阻尼正弦）
- **平稳条件**：AR(p) 要求 $\phi(B) = 0$ 根在圆外；MA(q) 恒平稳
- **可逆条件**：AR(p) 恒可逆；MA(q) 要求 $\theta(B) = 0$ 根在圆外
- **谱**：AR(p) $p(f) \propto 1/|\phi(e^{-i2\pi f})|^2$；MA(q) $p(f) \propto |\theta(e^{-i2\pi f})|^2$

这个对偶性是模型识别（Ch6）的核心工具：
- **ACF 截断 → MA 模型**
- **PACF 截断 → AR 模型**
- **两者都拖尾 → ARMA 混合模型**

---

## 3.4 ARMA(p,q) 混合过程

$$\phi(B)\tilde{z}_t = \theta(B)a_t$$

- 平稳：$\phi(B) = 0$ 的根在圆外
- 可逆：$\theta(B) = 0$ 的根在圆外
- ACF：前 $q-p+1$ 个值由 $\theta$ 参数直接影响，之后满足差分方程 $\phi(B)\rho_k = 0$ → 指数衰减/阻尼正弦
- PACF：前 $p-q+1$ 个值受 $\phi$ 影响，之后类似 MA 的 PACF → 指数衰减
- 谱：$p(f) = 2\sigma_a^2 |\theta(e^{-i2\pi f})|^2 / |\phi(e^{-i2\pi f})|^2$

### ARMA(1,1) 详解

$$(1 - \phi_1 B)\tilde{z}_t = (1 - \theta_1 B)a_t$$

- $\psi_j = (\phi_1 - \theta_1)\phi_1^{j-1}$ ($j \geq 1$)
- $\rho_1 = (1 - \phi_1\theta_1)(\phi_1 - \theta_1)/(1 + \theta_1^2 - 2\phi_1\theta_1)$
- $\rho_k = \phi_1 \rho_{k-1}$ ($k \geq 2$)——从 $\rho_1$ 开始指数衰减

---

## 深度思考

### 1. 简约原则的数学实现

Ch3 回答了"为什么 ARMA 够用"：
- Wold 定理保证任何平稳过程有 $\psi(B)$ 表示
- $\psi(B) = \phi^{-1}(B)\theta(B)$ 是**有理函数逼近**（Padé 近似）
- 低阶有理函数（$p, q \leq 2$）可以高精度逼近无穷级数
- 这就是简约原则的数学基础

### 2. ACF/PACF 截断 = 模型识别的指纹

- ACF 在 lag $q$ 截断，PACF 拖尾 → **MA(q)**
- ACF 拖尾，PACF 在 lag $p$ 截断 → **AR(p)**
- 两者都拖尾 → **ARMA(p,q)**
- 两者都截断 → 不可能（矛盾）

### 3. 对光伏预测的具体指导

- **辐照度日变化去除后的残差**：通常 ACF 拖尾但快速衰减 → AR(1) 或 AR(2) 候选
- **云遮蔽事件**：导致突变，AR 模型的 ψ 权重过于光滑 → 可能需要 MA 项
- **多站点空间相关**：Ch14 的 VAR 模型是 AR 的多变量推广

---

## 小结

Ch3 建立了 ARMA 模型族的完整理论：

**三大模型** = AR（过去值回归）+ MA（冲击加权和）+ ARMA（混合）

**两大识别工具** = ACF（截断→MA）+ PACF（截断→AR）

**两大合法性条件** = 平稳性（$\phi(B)=0$ 根在圆外）+ 可逆性（$\theta(B)=0$ 根在圆外）

**下一章预告**：Ch4 引入非平稳——差分算子 $\nabla^d$ 将 ARMA 推广为 ARIMA。

---

*📖 [Ch2 笔记](/blog/2026-03-16-box-ch2-acf-spectrum) | [返回教材目录](/textbook/) | 📝 [Box 时间序列系列](/blog/tags/时间序列)*
