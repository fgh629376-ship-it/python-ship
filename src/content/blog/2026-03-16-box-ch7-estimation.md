---
title: "Box 时间序列分析 Ch7：参数估计——最大似然与非线性最小二乘"
description: "细读 Box《Time Series Analysis》第7章：条件/无条件似然、非线性迭代估计、参数标准误差与置信区间"
pubDate: 2026-03-16
lang: zh
series: box-timeseries
category: timeseries
tags: ["时间序列", "参数估计", "MLE", "最小二乘", "ARIMA", "教材笔记"]
---

# Box 时间序列分析 Ch7：参数估计——最大似然与非线性最小二乘

> **教材**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 7

## 章节定位

Ch6 给了候选模型和粗略估计。Ch7 做**精确估计**——用 MLE 或等价的非线性最小二乘，得到统计上高效的参数值和标准误差。

---

## 7.1 似然函数

### 条件似然

给定模型 $\phi(B)\nabla^d z_t = \theta(B)a_t$，假设 $a_t \sim N(0, \sigma_a^2)$ 独立同分布：

$$l^*(\phi, \theta, \sigma_a^2) = -\frac{n}{2}\ln(\sigma_a^2) - \frac{S^*(\phi, \theta)}{2\sigma_a^2}$$

其中条件残差平方和：

$$S^*(\phi, \theta) = \sum_{t=1}^{n} a_t^2(\phi, \theta | w^*, a^*, w)$$

**条件 MLE = 条件最小二乘**——最小化 $S^*(\phi, \theta)$ 即可。

### 条件 vs 无条件

- **条件似然**：设 $a^* = 0$，$w^*$ = 实际值；适用于长序列（$n > 50$），简单快速
- **无条件似然**：对初始值积分/回推（backcasting）；适用于短序列或 AR 根接近单位圆

Box 推荐：**一般用条件似然就够了**，但季节模型（Ch9）必须用无条件似然。

---

## 7.2 非线性迭代估计

ARIMA 的似然函数关于 $\theta$ 是**非线性**的（MA 参数进入残差的递推公式）。需要迭代方法：

### Marquardt 算法

结合了牛顿法和最速下降法的优点：

$$(\mathbf{H} + \lambda \mathbf{I})\boldsymbol{\delta} = -\mathbf{g}$$

- $\lambda$ 大时 → 最速下降（安全但慢）
- $\lambda$ 小时 → 牛顿法（快但可能发散）
- 每步自适应调整 $\lambda$

### 参数标准误差

$$\hat{V}(\hat{\xi}) \approx 2\hat{\sigma}_a^2 \mathbf{H}^{-1}$$

其中 $\mathbf{H}$ 是 $S(\phi, \theta)$ 的 Hessian 矩阵在 MLE 处的值。

**置信区间**：$\hat{\xi}_j \pm z_{\alpha/2} \hat{\sigma}(\hat{\xi}_j)$

---

## 7.3 AR 参数的特殊性

**AR 的 Yule-Walker 估计已经近似高效**——因为 AR 模型的似然函数关于 $\phi$ 是近似线性的。

$$\hat{\boldsymbol{\phi}}_{YW} \approx \hat{\boldsymbol{\phi}}_{MLE}$$

### MA 参数不同

MA 的矩估计**不高效**——可能比 MLE 差很多。必须用 Ch7 的迭代 MLE。

---

## 7.4 似然面的几何

### 单参数（如 IMA(0,1,1)）

$S(\theta)$ 是 $\theta$ 的函数，画出来是 U 形曲线，最低点对应 MLE。

### 多参数

$S(\phi, \theta)$ 的等高线可能是椭圆（参数相关性低）或狭长的"山谷"（参数高度相关）。

**参数相关性**：$\phi$ 和 $\theta$ 接近时（如 ARMA(1,1) 的 $\phi_1 \approx \theta_1$），似然面有很长的脊 → 两个参数几乎不可分辨 → 标准误差很大。

---

## 7.5 贝叶斯观点

似然函数 × 先验 = 后验分布。当先验平坦（无信息先验）时，后验 ∝ 似然。

Box 更偏向**似然主义**——让数据说话，不加主观先验。但承认贝叶斯框架在小样本时有优势。

---

## 深度思考

### 1. MLE 的渐近性质

在大样本下，MLE：
- **一致**（consistent）：$\hat{\theta} \to \theta_0$ 
- **渐近正态**：$\sqrt{n}(\hat{\theta} - \theta_0) \to N(0, I^{-1})$
- **渐近有效**：达到 Cramér-Rao 下界

Whittle (1953) 把这些性质从独立观测推广到了平稳时间序列。

### 2. 过参数化的似然面特征

当 ARMA(1,1) 的 $\phi_1 \approx \theta_1$ 时，AR 和 MA 几乎对消 → 模型退化为白噪声。似然面的"脊"意味着**参数不可识别**——这是 ARMA 模型的固有问题，也是为什么简约原则如此重要。

### 3. 对光伏预测的指导

- **用 `statsmodels.tsa.arima.model.ARIMA`**：内部实现了条件和无条件 MLE
- 关注参数的标准误差——如果 $\hat{\sigma}(\hat{\phi})$ 与 $\hat{\phi}$ 同量级，说明参数不显著
- ARMA(1,1) 的 $\phi \approx \theta$ 问题在实际数据中常见 → 可能 AR(1) 或 MA(1) 就够了

---

## 小结

Ch7 = 从粗略估计到精确估计：

$$\text{Ch6 初始估计} \xrightarrow{\text{Marquardt 迭代}} \hat{\phi}_{MLE}, \hat{\theta}_{MLE} \xrightarrow{\text{Hessian}} \text{标准误差}$$

核心结论：
- **MLE = 最小化残差平方和**（正态假设下）
- AR 的 Yule-Walker 已经近似高效
- MA 必须用迭代 MLE
- 参数标准误差 = Hessian 的逆
- 简约原则防止过参数化

---

*📖 [Ch6 笔记](/blog/2026-03-16-box-ch6-model-identification) | [返回教材目录](/textbook/) | 📝 [Box 时间序列系列](/blog/)*
