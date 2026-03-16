---
title: "Box 时间序列分析 Ch9：季节性模型——SARIMA 的乘积结构"
description: "细读 Box《Time Series Analysis》第9章：乘积季节模型 SARIMA、季节差分、航空旅客实例、Box-Cox 变换"
pubDate: 2026-03-16
lang: zh
series: box-timeseries
category: timeseries
tags: ["时间序列", "SARIMA", "季节性", "航空旅客", "Box-Cox", "教材笔记"]
---

# Box 时间序列分析 Ch9：季节性模型——SARIMA 的乘积结构

> **教材**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 9

## 核心思想

Ch3-8 只处理非季节性序列。但大量实际数据有**周期性模式**（月度销量、季度 GDP、小时辐照度）。Ch9 的解决方案：

> **乘积 SARIMA 模型**——在 $B$ 和 $B^s$ 两个尺度上分别建模。

---

## 9.1 为什么需要专门的季节模型？

### 拟合 vs 预测的陷阱

Box 首先警告：用傅里叶级数或确定性函数"拟合"季节模式很容易，但预测可能很差。IBM 股价看起来有趋势，但最优预测就是今天的价格——确定性拟合会误导。

### 乘积模型的直觉

月度数据有**两种时间关系**：
1. **相邻月份**（$B$）：3月和4月的联系
2. **同月不同年**（$B^{12}$）：今年4月和去年4月的联系

自然做法：分别在两个尺度建模，然后**乘起来**。

---

## 9.2 一般乘积季节模型

$$\phi_p(B) \Phi_P(B^s) \nabla^d \nabla_s^D z_t = \theta_q(B) \Theta_Q(B^s) a_t$$

- $\phi_p(B)$：非季节 AR(p)，例如 $(1 - \phi_1 B)$
- $\Phi_P(B^s)$：季节 AR(P)，例如 $(1 - \Phi_1 B^{12})$
- $\nabla^d = (1-B)^d$：非季节差分，例如 $d = 1$
- $\nabla_s^D = (1-B^s)^D$：季节差分，例如 $D = 1, s = 12$
- $\theta_q(B)$：非季节 MA(q)，例如 $(1 - \theta_1 B)$
- $\Theta_Q(B^s)$：季节 MA(Q)，例如 $(1 - \Theta_1 B^{12})$

记为 **ARIMA$(p,d,q) \times (P,D,Q)_s$**。

### 航空旅客经典实例

Series G：月度国际航空旅客（1949-1960），$s = 12$

最终模型：$(0,1,1) \times (0,1,1)_{12}$

$$(1 - B)(1 - B^{12}) \ln z_t = (1 - \theta B)(1 - \Theta B^{12}) a_t$$

$\hat{\theta} = 0.40, \hat{\Theta} = 0.60$

**乘积结构的含义**：模型的 MA 部分展开为 $a_t - \theta a_{t-1} - \Theta a_{t-12} + \theta\Theta a_{t-13}$，只需 3 个参数就描述了月内和年际的复杂依赖结构。

---

## 9.3 季节模型的识别、估计与诊断

### 识别流程

1. **检查非平稳性**：原始序列和季节差分后的 ACF
2. **季节差分**：$\nabla_{12} z_t = z_t - z_{t-12}$（或先取对数/Box-Cox）
3. **检查非季节非平稳性**：再看是否需要 $\nabla$ 差分
4. **ACF/PACF 在 lag $s, 2s, 3s, \ldots$** 的行为 → 季节 $P, Q$
5. **ACF/PACF 在 lag $1, 2, 3, \ldots$** 的行为 → 非季节 $p, q$

### Box-Cox 变换

$$z_t^{(\lambda)} = \begin{cases} (z_t^\lambda - 1)/\lambda & \lambda \neq 0 \\ \ln z_t & \lambda = 0 \end{cases}$$

航空旅客数据用 $\lambda = 0$（对数变换），因为变异性随水平成比例增加。

---

## 深度思考

### 1. 乘积假设的合理性

乘积季节模型假设：季节效应与非季节动态是**可分离的**。这相当于说"4月和3月的关系"不取决于"今年的整体水平"。

对很多数据这是合理的，但不总是——例如光伏辐照度的云影响在夏季和冬季可能有不同的时间结构。

### 2. 对光伏预测的核心启示

**辐照度有两种周期**：
- **日周期**（$s = 24$ 或 $s = 48$ 对半小时数据）
- **年周期**（$s = 365$ 或 $s = 12$ 对月度）

SARIMA 可以直接处理日周期：
$$\text{ARIMA}(p,d,q) \times (P,D,Q)_{24}$$

但 $s = 24$ 时乘积模型有 24 个季节根，实际中通常用：
1. **物理去季节**（clearsky 模型）→ 残差建 ARMA
2. **傅里叶项 + ARMA 残差**
3. **STL 分解 + ARMA 残差**

### 3. 简约原则在季节模型中更重要

$(0,1,1) \times (0,1,1)_{12}$ 只有 3 个参数（$\theta, \Theta, \sigma_a^2$）却描述了 144 个月度数据的完整动态。这是简约原则的极致体现。

---

## 小结

Ch9 = ARIMA 的季节扩展。核心公式：

$$\phi(B)\Phi(B^s)\nabla^d\nabla_s^D z_t = \theta(B)\Theta(B^s) a_t$$

**乘积结构**让少量参数描述复杂的多尺度时间依赖。

---

*📖 [Ch8 笔记](/blog/2026-03-16-box-ch8-diagnostics) | [返回教材目录](/textbook/) | 📝 [Box 时间序列系列](/blog/)*
