---
title: '光伏预测验证完全指南 — 你的模型真的好吗？Murphy 三维度告诉你答案'
description: '深入学习确定性预测验证：Skill Score 与 CLIPER 参考方法、Murphy-Winkler 分布导向框架、MSE 分解、质量-一致性-价值三维度评估'
category: solar
series: solar-book
lang: zh
pubDate: '2026-03-15'
tags: ["预测验证", "skill score", "Murphy-Winkler", "MSE分解", "光伏预测"]
---

## 你的预测模型好不好？这个问题比你想的难 100 倍

做光伏预测的人都会算 RMSE。但你可能不知道：**RMSE 最低的预测不一定是最好的**。在一个经典的模拟实验中（Yang & Kleissl, 2024），三个预测者分别在 MBE、MAE、RMSE 上「最优」—— 每个人都能声称自己是「最好的」。

这就是为什么预测验证（forecast verification）值得单独用一整章来讲。本文基于 Yang & Kleissl (2024) 教材 Chapter 9，带你建立系统化的验证思维。

> 本文内容基于 *Solar Irradiance and Photovoltaic Power Forecasting* (CRC Press, 2024) Chapter 9

---

## 一、Skill Score —— 不是算误差，是算「超越了多少」

### 1.1 为什么需要 Skill Score

直接报 RMSE 有一个致命问题：**不同地点、不同时段的预测难度不同**。沙漠地区 RMSE=$50 \text{W/m}^2$ 可能很差（因为几乎全是晴天），而多云地区 RMSE=$100 \text{W/m}^2$ 可能很优秀。

Skill Score 的核心思想：**用你的预测和一个「傻瓜预测」比较**，看你超越了多少：

$$S^* = 1 - \frac{S_{\text{fcst}}}{S_{\text{ref}}}$$

- $S^* > 0$ → 你比傻瓜好
- $S^* = 0$ → 你跟傻瓜一样
- $S^* < 0$ → 你比傻瓜还差（该反思了）

### 1.2 三种参考方法

| 方法 | 原理 | 适用 |
|------|------|------|
| **Persistence** | 用最近的观测当预测 | 短时效（<3h） |
| **Climatology** | 用历史均值当预测 | 长时效（>6h） |
| **CLIPER** | 两者的最优凸组合 | **所有时效（推荐）** |

CLIPER 的权重有解析解：$\alpha_{\text{optimal}} = \gamma_h$（lag-h 自相关系数）。

数学证明：

$$\text{MSE}_{\text{CLIPER}} = (1 - \gamma_h^2) \cdot \sigma_K^2$$

$$\text{MSE}_{\text{CLIPER}} \leq \text{MSE}_{\text{CLIM}} \quad \text{且} \quad \text{MSE}_{\text{CLIPER}} \leq \text{MSE}_{\text{PERS}}$$

**CLIPER 严格不差于 persistence 和 climatology**。无论什么数据、什么时效，它都是最优参考。

> 这个结论由 Yang (2019) 引入太阳预测界，但到 2024 年大部分论文还在用 smart persistence 做参考。学术惯性的力量令人叹息。

### 1.3 必须在 $\kappa$ 上操作

这一点在之前学 Ch8 时已经知道了，再强调一遍：

- $\kappa$（clear-sky index）= 实测值 / 晴空模型值
- 在 $\kappa$ 上做 persistence/climatology/CLIPER，结果回乘晴空值得到辐照预测
- 直接在 GHI 上做 persistence 会**高估 skill score**（因为日变化规律太容易「预测」）

---

## 二、Measure-Oriented 验证的致命局限

### 2.1 经典实验：三个预测者，三个「冠军」

Yang & Kleissl 用条件异方差模型生成 55 小时模拟数据，三个预测者分别出预测：

| 预测者 | 策略 | MBE ($\text{W/m}^2$) | MAE ($\text{W/m}^2$) | RMSE ($\text{W/m}^2$) |
|--------|------|-----------|-----------|------------|
| Novice | 持续性 | **-2.85** ✓ | 79.63 | 142.36 |
| Optimist | 常数 0.95 | 36.19 | **57.68** ✓ | 119.81 |
| Statistician | 条件均值 | 8.72 | 63.02 | **111.77** ✓ |

**三个人分别在三个指标上「最优」。** 如果你用 MAE 评判，Optimist 赢；用 RMSE 评判，Statistician 赢。结论完全取决于你选哪个指标。

### 2.2 为什么会这样

因为不同指标对误差分布的不同特征敏感：

- **MBE**：只看偏差方向，正负相消 → 不反映精度
- **MAE**：等权重对待所有误差 → 对大误差不敏感
- **RMSE**：惩罚大误差 → 电网运营更关心这个
- **MAPE**：对近零值爆炸 → **光伏预测中禁用**

### 2.3 解决方案

**报告预测-观测对（forecast-observation pairs）**，不只报告汇总指标。让读者可以自行验证。

---

## 三、Murphy-Winkler 分布导向验证框架

这是本章的精华。联合分布 f(x,y) 包含验证所需的**全部信息**。

### 3.1 两种分解

#### Calibration-Refinement 分解

$$f(x,y) = f(y|x) \cdot f(x)$$

- $f(y|x)$ → **校准性（Calibration）**：给定预测值 $x$，观测值分布如何？
  - 理想状态：$E(Y|X=x) = x$（预测多少，平均观测就是多少）
  - 量化：**Type 1 条件偏差** $= E_X[X - E(Y|X)]^2$（越小越好）

- $f(x)$ → **精细度/分辨率（Resolution）**：预测值有多多样？
  - 气候态预测（常数）→ 零分辨率
  - 量化：$E_X[E(Y|X) - E(Y)]^2$（越大越好）

#### Likelihood-Base Rate 分解

$$f(x,y) = f(x|y) \cdot f(y)$$

- $f(x|y)$ → **一致性（Consistency）**：给定观测值 $y$，预测值分布如何？
  - 理想状态：$E(X|Y=y) = y$
  - 量化：**Type 2 条件偏差** $= E_Y[Y - E(X|Y)]^2$（越小越好）

- $f(y)$ → **基准率（Base Rate）**：观测的边缘分布

### 3.2 MSE 的三种分解

所有这些统计量都可以关联到 MSE：

**COF 分解**（conditioning on forecast）：

$$\text{MSE} = V(Y) + E_X[X - E(Y|X)]^2 - E_X[E(Y|X) - E(Y)]^2$$

即：$\text{MSE} = \text{方差} + \text{Type 1 条件偏差} - \text{分辨率}$

**COX 分解**（conditioning on observation）：

$$\text{MSE} = V(X) + E_Y[Y - E(X|Y)]^2 - E_Y[E(X|Y) - E(X)]^2$$

即：$\text{MSE} = \text{方差} + \text{Type 2 条件偏差} - \text{辨别力}$

**四个维度，四个目标**：

| 维度 | 来源 | 目标 |
|------|------|------|
| Type 1 条件偏差（Calibration） | COF | 最小化 |
| 分辨率（Resolution） | COF | 最大化 |
| Type 2 条件偏差（Consistency） | COX | 最小化 |
| 辨别力（Discrimination） | COX | 最大化 |

---

## 四、案例研究：ECMWF HRES vs NCEP NAM

教材用 SURFRAD 三站（BON/DRA/PSU）2020 年数据，对比两个 NWP 模型的日前 GHI 预测。

### 4.1 质量评估

| 指标 | HRES 胜 | NAM 胜 |
|------|---------|--------|
| MAE/RMSE（精度） | ✅ | |
| 边缘分布相似度 | | ✅ |
| 校准性 | ✅ | |
| Type 2 条件偏差 | | ✅ |
| 分辨率 | ✅ | |
| 辨别力 | | ✅ |

**没有一个模型在所有维度上占优。** 这是常见结论，也是为什么多维度评估不可或缺。

### 4.2 一致性实验

用三种目标函数对 NWP 预测做线性校正（MAE最小化 / MSE最小化 / MAPE最小化），然后交叉评估：

**结论**：训练用什么目标函数，评估时那个指标就最优。

这验证了 Kolassa (2020) 的核心论点：**「最好的」点预测取决于你用什么评估指标**。所以：

> 如果电网运营商的惩罚基于 RMSE，你就必须用 MSE 做训练目标。训练和评估不一致是浪费算力。

### 4.3 价值评估

最震撼的发现：**质量和价值的对应关系是非线性的**。

- MAE 差 9%（23% vs 32%）→ 惩罚金额差 **5 倍**
- MAPE 最优的预测反而收到**最高惩罚**

**结论**：技术指标好 ≠ 经济价值高。做预测的最终目的是**为决策服务**，不是发论文。

---

## 五、实用检查清单

验证光伏预测时，按这个顺序做：

1. **选参考方法**：用 CLIPER，不用 smart persistence
2. **在 $\kappa$ 上操作**：所有计算基于 clear-sky index
3. **画散点图**：检查时间对齐、异常值、整体偏差
4. **报告 f-o pairs**：让别人能复现你的验证
5. **做 Murphy-Winkler 分解**：校准/分辨率/条件偏差/辨别力
6. **确保一致性**：训练目标 = 评估指标 = 电网惩罚规则
7. **量化价值**：用实际惩罚方案算经济损失

---

## 参考文献

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press. Chapter 9.
- Murphy, A.H. & Winkler, R.L. (1987). "A General Framework for Forecast Verification." *Monthly Weather Review*, 115, 1330-1338. (Q1)
- Murphy, A.H. (1993). "What Is a Good Forecast?" *Weather and Forecasting*, 8(2), 281-293. (Q1)
- Yang, D. (2019). "A universal benchmarking method for probabilistic solar irradiance forecasting." *Solar Energy*, 184, 410-416. (Q1)
- Yang, D. et al. (2020). "Verification of deterministic solar forecasts." *Solar Energy*, 210, 20-37. (Q1)
- Kolassa, S. (2020). "Why the 'best' point forecast depends on the error or accuracy measure." *International Journal of Forecasting*, 36(1), 208-211. (Q1)
- Mayer, M.J. & Yang, D. (2023). "Calibration of deterministic NWP forecasts and its impact on verification." *International Journal of Forecasting*, 39(2), 981-997. (Q1)
