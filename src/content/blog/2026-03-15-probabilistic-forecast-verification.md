---
title: '概率预测验证 — 校准、锐度与严格适当评分规则'
description: '深入学习概率预测验证：PIT/Rank直方图、Reliability Diagram、CRPS/Brier Score/IGN评分规则、校准-锐度范式'
category: solar
series: solar-book
lang: zh
pubDate: '2026-03-15'
tags: ["概率预测", "CRPS", "Brier Score", "校准", "光伏预测"]
---

## 从「预测一个数」到「预测一个分布」

确定性预测告诉你「明天 GHI 是 $500 \text{W/m}^2$」；概率预测告诉你「明天 GHI 有 90% 概率在 350-$650 \text{W/m}^2$ 之间」。后者对电网运营更有用 —— 因为调度员需要知道**不确定性有多大**，才能决定备用容量。

但概率预测的验证比确定性预测难得多。你不能简单地算 RMSE，因为预测不是一个数，而是一个分布。本文基于 Yang & Kleissl (2024) 教材 Chapter 10，梳理概率预测验证的核心框架。

> 基于 *Solar Irradiance and Photovoltaic Power Forecasting* (CRC Press, 2024) Chapter 10

---

## 一、核心范式：最大化锐度，同时保持校准

### 1.1 校准（Calibration）

**定义**：预测分布与观测之间的统计一致性。

直觉理解：如果你发了 100 次「有 70% 概率下雨」的预测，那么实际下雨的次数应该接近 70 次。

数学上，完美校准意味着 PIT（Probability Integral Transform）服从均匀分布：

$$p_t = F_t(y_t) \sim U(0,1)$$

**三种校准形式**（Gneiting et al., 2007）：
- **概率校准（Probabilistic）**：对所有 $\tau$，$F^{-1}(\tau)$ 处的 $G$ 值平均趋近 $\tau$
- **超越校准（Exceedance）**：定义在阈值而非概率上
- **边缘校准（Marginal）**：预测 CDF 的长期平均 = 观测 CDF 的长期平均

### 1.2 锐度（Sharpness）

**定义**：预测分布的集中程度 —— 越窄越锐利。

**关键区别**：锐度是预测自身的属性，不涉及观测。

### 1.3 为什么两者必须同时评估

- **只要校准**：永远发气候态分布 → 完美校准但零信息量
- **只要锐度**：发一个极窄的分布 → 锐利但可能完全偏离观测

> **Gneiting 范式**：最大化锐度，**同时保持校准**。这是概率预测的最高原则。

---

## 二、严格适当评分规则（Strictly Proper Scoring Rules）

评分规则给概率预测和观测分配一个数值。**严格适当**意味着：预测者如果按真实信念出预测，得到的期望分数最优。换言之，**不鼓励作弊（hedging）**。

### 2.1 Brier Score（二元事件）

$$\text{bs}(p, y) = (p - y)^2$$

- p = 预测概率，y = 0 或 1
- 范围 [0, 1]，越小越好
- **可分解为**：可靠性 + 分辨率 + 不确定性

### 2.2 CRPS（连续变量的核心评分）

$$\text{crps}(F, y) = \int_{-\infty}^{\infty} [F(x) - \mathbb{1}(x \geq y)]^2 \, dx$$

**关键性质**：
- 严格适当
- 当 $F$ 退化为点预测时，$\text{CRPS} = \text{MAE}$
- $\text{CRPS}$ = Brier Score 对所有阈值的积分
- 同时评估校准和锐度

**计算方法**：
- 参数分布（正态/截断正态等）→ 有解析公式
- 集合预测 → 用排序成员公式（O(m log m)）
- R 包 `scoringRules` 提供全套实现

**CRPS 可分解为**：

$$\text{CRPS} = \text{可靠性} - \text{分辨率} + \text{不确定性}$$

### 2.3 IGN（Ignorance Score / 对数评分）

$$\text{ign}(f, y) = -\log f(y)$$

- 只评估预测 PDF 在观测点的值（局部性质）
- 对尾部事件不敏感（与 CRPS 的全局性互补）
- 集合预测需要 KDE 估计密度，对带宽敏感

### 2.4 Quantile Score（分位数评分 / Pinball Loss）

$$qs_\tau(F, y) = \begin{cases} (y - q_\tau) \cdot \tau & \text{if } y \geq q_\tau \\ (q_\tau - y) \cdot (1 - \tau) & \text{if } y < q_\tau \end{cases}$$

- $\text{CRPS} = 2\int_0^1 qs_\tau \, d\tau$（对所有分位数的积分）
- 可以评估分布的不同部分（尾部等）

### 2.5 一致性与适当性

训练概率预测模型时：
- 如果用 CRPS 评估 → 用 CRPS 训练（最小化 CRPS）
- 如果用 IGN 评估 → 用似然训练（最大化 log-likelihood）
- **混用会导致次优结果**（与 Ch9 的一致性原则完全一致）

---

## 三、可视化评估工具

### 3.1 Rank 直方图（集合预测）

把观测插入排序后的集合成员中，统计观测的排名。

- **平坦** → 校准良好
- **U 形** → 欠分散（under-dispersed）—— NWP 集合预测最常见的问题
- **倒 U 形** → 过分散
- **左偏/右偏** → 偏差

### 3.2 PIT 直方图（分布预测）

$\text{PIT} = F_t(y_t)$，完美校准时服从 $U(0,1)$。

- 概念上等价于 Rank 直方图的连续版本
- 建议配合自相关图检查 PIT 序列的独立性

### 3.3 Reliability Diagram（可靠性图）

最推荐的可视化工具（Lauret et al., 2019）：

- 横轴：名义概率 τ
- 纵轴：实际观测比例 z̄_τ
- 完美校准 → 点在对角线上
- 可添加一致性带（consistency band）量化抽样不确定性

**两种计算一致性带的方法**：
1. **Bröcker & Smith (2007)**：重抽样方法
2. **Pinson et al. (2010)**：直接用二项分布 $B(n, \tau)$ 的分位数 → 更简洁

### 3.4 Sharpness Diagram（锐度图）

箱线图显示不同名义覆盖率下的预测区间宽度。

- 只涉及预测，不涉及观测
- 箱线图比单纯的均值/中位数更有信息量
- 异常值丰富 + 正偏 → GHI 的太阳高度角依赖方差导致

---

## 四、案例研究：ECMWF 50 成员集合预测后处理

教材用 ECMWF EPS 50 成员集合 GHI 预测，在三个 SURFRAD 站点进行验证。

### 4.1 原始集合 → 欠分散

Rank 直方图呈典型 U 形 → 集合展开度不够 → 需要 P2P 后处理。

### 4.2 四种后处理方法

| 方法 | 类型 | CRPS 表现 |
|------|------|----------|
| NGR1（EMOS，CRPS 优化） | 参数化（正态） | **最优** |
| NGR2（EMOS，IGN 优化） | 参数化（正态） | 次优 |
| BMA（贝叶斯模型平均） | 半参数化 | 较差 |
| QR（分位数回归） | 非参数化 | **接近最优** |

### 4.3 关键发现

1. **NGR1 在 CRPS 上最优，NGR2 在 IGN 上最优** → 适当性理论的经验验证
2. **QR 的 PIT 直方图最平坦** → 非参数方法的校准优势
3. **BMA 的锐度图缺乏变化** → 预测分布不够 resolved
4. **没有一种方法在所有方面占优** → 老结论了

---

## 五、实用要点

| 要做 | 不要做 |
|------|--------|
| 用 CRPS 做主评分规则 | 用非适当评分（如 CWC） |
| 画 PIT/Rank 直方图检查校准 | 只看 CRPS 不看校准 |
| 画 Reliability Diagram + 一致性带 | 不加一致性带就下结论 |
| 训练和评估用同一个评分规则 | CRPS 训练 + IGN 评估 |
| 评估锐度时条件于覆盖率 | 只报告均值区间宽度 |
| NWP 集合预测一定要做 P2P 后处理 | 直接用原始集合 |

---

## 参考文献

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press. Chapter 10.
- Gneiting, T. et al. (2007). "Probabilistic forecasts, calibration and sharpness." *JRSS-B*, 69(2), 243-268. (Q1)
- Gneiting, T. & Raftery, A.E. (2007). "Strictly Proper Scoring Rules, Prediction, and Estimation." *JASA*, 102(477), 359-378. (Q1)
- Hersbach, H. (2000). "Decomposition of the CRPS for ensemble prediction systems." *Weather and Forecasting*, 15, 559-570. (Q1)
- Lauret, P. et al. (2019). "Verification of solar irradiance probabilistic forecasts." *Solar Energy*, 194, 254-271. (Q1)
- Bröcker, J. & Smith, L.A. (2007). "Increasing the Reliability of Reliability Diagrams." *Weather and Forecasting*, 22, 651-661. (Q1)
