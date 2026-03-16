---
title: "Box 时间序列分析 Ch8：模型诊断检验——残差是白噪声吗？"
description: "细读 Box《Time Series Analysis》第8章：过度拟合、残差 ACF、Ljung-Box Q 检验、累积周期图、Score 检验"
pubDate: 2026-03-16
lang: zh
series: box-timeseries
category: timeseries
tags: ["时间序列", "模型诊断", "Ljung-Box", "残差分析", "ARIMA", "教材笔记"]
---

# Box 时间序列分析 Ch8：模型诊断检验——残差是白噪声吗？

> **教材**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 8

## 核心问题

模型估完了（Ch7），怎么知道它**够好**？

> "No model form ever represents the truth absolutely." — Box

但我们可以检验模型是否**严重不足**，以及如果不足，**往哪个方向修改**。

---

## 8.1 过度拟合（Overfitting）

**方法**：拟合一个比候选模型更复杂的模型，看额外参数是否显著。

**例子**：Series B（IBM 股价）识别为 IMA(0,1,1)。过度拟合到 IMA(0,3,3)，检验 $\lambda_1, \lambda_2$ 是否显著≠0。

结果：$\hat{\lambda}_1 \approx 0, \hat{\lambda}_2 \approx 0$ → IMA(0,1,1) 足够，**不需要二次或线性趋势预测**。

---

## 8.2 残差诊断

### 残差 ACF

如果模型正确，残差 $\hat{a}_t$ 应近似白噪声 → 残差 $r_k(\hat{a})$ 应在 $\pm 2/\sqrt{n}$ 以内。

**Durbin 的警告**：$r_k(\hat{a})$ 的方差可能比 $1/n$ **小得多**（尤其低 lag），直接用 $1/\sqrt{n}$ 标准误会**低估显著性**。

### Ljung-Box Q 检验（核心工具）

$$\tilde{Q}(K) = n(n+2) \sum_{k=1}^{K} \frac{r_k^2(\hat{a})}{n-k}$$

- 渐近分布：$\chi^2(K - p - q)$
- $\tilde{Q}$ 显著 → 残差非白噪声 → 模型不足
- **推荐 $K$ 取 15-25**

Box-Pierce 原始统计量 $Q = n\sum r_k^2$ 在小样本偏低，Ljung-Box 修正了这个偏差。

### 累积周期图

残差的标准化累积周期图应近似沿对角线。偏离 → 残差在某个频率有能量集中 → 模型遗漏了该频率成分。

用 **Kolmogorov-Smirnov** 带检验偏离是否显著。

---

## 8.3 诊断后怎么办？

### 残差 ACF 有结构 → 修改模型

- $r_1(\hat{a})$ 显著 → 遗漏 MA(1) 项，加 $\theta_1$
- $r_1, r_2$ 显著 → 遗漏 AR(2) 或 MA(2)，加 AR 或 MA 项
- lag 12 显著 → 季节性未处理，使用 Ch9 季节模型
- 多个 lag 显著 → 严重模型不足，需重新识别

### 参数随时间变化

Ch8 发现 IBM 数据前后半段的 $\lambda$ 和 $\sigma_a^2$ **显著不同** → 模型结构没变但参数漂移了。这是 GARCH（条件异方差）和变点检测的伏笔（Ch10）。

---

## 8.4 Score 检验（Lagrange Multiplier）

**优势**：只需拟合零假设模型，不需重新拟合备择模型。

$$\Lambda = \frac{\hat{a}'\mathbf{X}(\mathbf{X}'\mathbf{X})^{-1}\mathbf{X}'\hat{a}}{\hat{\sigma}_a^2} \sim \chi^2(r)$$

等价于辅助回归的 $nR^2$。可用来检验是否需要额外的 AR 或 MA 项。

---

## 深度思考

### 1. 迭代建模的完整闭环

Ch6-8 构成了 Box-Jenkins 方法论的核心循环：

$$\text{识别(Ch6)} \to \text{估计(Ch7)} \to \text{诊断(Ch8)} \to \text{修改} \to \text{重新估计} \to \cdots$$

**诊断不是"终点"，而是"反馈"。** 每次诊断发现问题，回到识别步骤修改模型。

### 2. Ljung-Box 在光伏中的应用

训练完 ARIMA 模型预测辐照度后：
- 对残差做 Ljung-Box 检验（$K = 24$ 对小时数据）
- 如果 lag 24 显著 → 日周期没去干净
- 如果 lag 1-3 显著 → 短期相关没捕获完

`statsmodels.stats.diagnostic.acorr_ljungbox()` 直接用。

### 3. "All models are wrong, some are useful"

Box 在 Ch8 表达了他最著名的哲学：不追求"正确模型"，追求"足够好的模型"。

---

## 小结

Ch8 = 质量控制。三大工具：

| 工具 | 检验什么 | 何时用 |
|------|---------|-------|
| 过度拟合 | 额外参数是否需要 | 有明确"怕什么"方向时 |
| Ljung-Box Q | 残差整体是否白噪声 | **每次建模必做** |
| 累积周期图 | 残差是否有周期结构 | 怀疑遗漏周期时 |

---

*📖 [Ch7 笔记](/blog/2026-03-16-box-ch7-estimation) | [返回教材目录](/textbook/) | 📝 [Box 时间序列系列](/blog/tags/时间序列)*
