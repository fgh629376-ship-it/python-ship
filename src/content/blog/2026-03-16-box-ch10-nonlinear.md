---
title: "Box 时间序列分析 Ch10：非线性模型与长记忆——GARCH、TAR、ARFIMA"
description: "细读 Box《Time Series Analysis》第10章：ARCH/GARCH 条件异方差、门限自回归 TAR、长记忆 ARFIMA"
pubDate: 2026-03-16
lang: zh
series: box-timeseries
category: timeseries
tags: ["时间序列", "GARCH", "非线性", "长记忆", "ARFIMA", "教材笔记"]
---

# Box 时间序列分析 Ch10：非线性与长记忆

> **教材**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 10

## 核心主题

Ch3-9 的 ARIMA 是**线性 + 等方差**的。Ch10 打破这两个假设。

---

## 10.1 ARCH/GARCH：条件异方差

### 问题

金融数据的"波动率聚集"：大波动后跟大波动（方向随机），平静期后跟平静期。ARMA 假设 $\text{var}(a_t) = \sigma_a^2$ 恒定，无法捕获这种现象。

### ARCH(s) 模型

$$h_t = \text{var}[a_t | a_{t-1}, \ldots] = \omega_0 + \sum_{i=1}^{s} \omega_i a_{t-i}^2$$

条件方差依赖于过去的**冲击平方**。

### GARCH(s,r) 模型

$$h_t = \omega_0 + \sum_{i=1}^{s} \omega_i a_{t-i}^2 + \sum_{i=1}^{r} \beta_i h_{t-i}$$

GARCH(1,1) = 金融领域最常用的波动率模型。

### 关键性质

- $a_t$ 仍然零均值、不相关——但**不独立**
- 条件方差 $h_t$ 随时间变化，但无条件方差 $\sigma_a^2 = \omega_0/(1 - \omega_1 - \beta_1)$ 恒定（弱平稳）
- 预测误差方差随过去波动调整 → **自适应预测区间**

---

## 10.2 非线性模型

### TAR（门限自回归）

$$z_t = \begin{cases} \phi_1^{(1)} z_{t-1} + \cdots + a_t & \text{if } z_{t-d} \leq r \\ \phi_1^{(2)} z_{t-1} + \cdots + a_t & \text{if } z_{t-d} > r \end{cases}$$

在不同"区制"（regime）下用不同 AR 模型。可以产生**极限环**（limit cycle）行为。

### 双线性模型

$$z_t = \sum \phi_i z_{t-i} + \sum \theta_j a_{t-j} + \sum \beta_{ij} z_{t-i} a_{t-j} + a_t$$

过去的值和过去的冲击有交互作用。

---

## 10.3 长记忆 ARFIMA

### 问题

有些序列的 ACF 衰减极慢（幂律衰减 $\rho_k \sim k^{2d-1}$），但差分一次又过度 → 需要**分数差分**。

### ARFIMA(p,d,q)

$$\phi(B)(1-B)^d z_t = \theta(B) a_t, \quad -0.5 < d < 0.5$$

当 $d$ 是非整数时，$(1-B)^d = \sum_{k=0}^{\infty} \binom{d}{k}(-B)^k$

- $0 < d < 0.5$：长记忆，ACF 幂律衰减（可加和！）
- $d = 0$：短记忆 ARMA
- $-0.5 < d < 0$：反持续性

---

## 深度思考

### 对光伏预测的启示

1. **GARCH for 辐照度**：云遮蔽导致的波动率聚集 → 辐照度残差可能有 ARCH 效应 → 用 GARCH 做自适应预测区间
2. **TAR for 天气区制**：晴天 vs 多云天可能需要不同的 AR 模型 → 门限模型或马尔可夫切换
3. **ARFIMA for 长期记忆**：辐照度的年际变化可能有长记忆特征（气候变化的慢动态）

---

*📖 [Ch9 笔记](/blog/2026-03-16-box-ch9-seasonal) | [返回教材目录](/textbook/) | 📝 [Box 时间序列系列](/blog/tags/时间序列)*
