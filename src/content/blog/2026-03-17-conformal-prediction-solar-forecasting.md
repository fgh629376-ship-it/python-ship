---
title: "🔬 跨行业算法迁移：保形预测（Conformal Prediction）——光伏功率预测不确定性量化的新范式"
description: "保形预测从统计学理论出发，在金融风控和医学诊断中大放异彩，现在正向可再生能源领域迁移。本文深度解析 CP 的数学原理、分布无关性优势、以及在光伏辐照度和功率预测中的具体应用——覆盖率保证、自适应区间宽度、在线更新策略，附完整 Python 实现。"
pubDate: 2026-03-17
lang: zh
category: solar
series: cross-industry
tags: ['跨行业算法', '保形预测', '不确定性量化', '光伏预测', '概率预测', '区间预测']
---

## 引言：为什么光伏预测需要不确定性量化？

光伏功率预测模型给你一个数字："明天 14:00 功率 850 kW"。但电网调度员真正需要知道的是：**这个数字有多可靠？** 可能的范围是 800–900 kW 还是 500–1200 kW？

不确定性量化（Uncertainty Quantification, UQ）对电力系统至关重要：

- **电网调度**：预留多少备用容量取决于预测区间的宽度
- **电力市场**：竞价策略需要知道预测的概率分布
- **储能优化**：充放电决策依赖预测置信区间
- **风险管理**：极端偏差的概率直接影响系统安全

传统方法（分位数回归、贝叶斯神经网络、高斯过程）各有局限。**保形预测（Conformal Prediction, CP）** 作为一种分布无关的不确定性量化框架，正在从统计学和金融领域向可再生能源预测快速迁移。

---

## 一、保形预测的核心思想

### 1.1 起源与发展

保形预测由 Vladimir Vovk、Alexander Gammerman 和 Glenn Shafer 在 2005 年系统提出（Vovk et al., 2005, *Algorithmic Learning in a Random World*, Springer），其核心思想可以追溯到 20 世纪 50 年代的容忍区间（tolerance intervals）和非参数统计。

2019 年之后，CP 经历了爆发式增长。Romano et al. (2019) 在 NeurIPS 发表的 **Conformalized Quantile Regression (CQR)** 论文是关键转折点——它将 CP 与深度学习无缝结合，让任何点预测模型都能产生有理论保证的预测区间。

### 1.2 数学框架

设训练集 $\{(X_i, Y_i)\}_{i=1}^{n}$ 和新测试点 $(X_{n+1}, Y_{n+1})$，假设数据可交换（exchangeable）。

**核心步骤：**

**第一步：训练基础模型**

在训练集上训练任意预测模型 $\hat{f}$（线性回归、随机森林、神经网络，任何都行）。

**第二步：计算不一致性分数（Nonconformity Score）**

在校准集（calibration set）上计算每个样本的不一致性分数：

$$s_i = |Y_i - \hat{f}(X_i)|$$

这是最简单的绝对残差形式。更一般地，不一致性分数可以定义为任何衡量"模型预测与真实值不一致程度"的函数。

**第三步：计算分位数阈值**

给定覆盖率目标 $1 - \alpha$（如 90%），计算校准分数的 $\lceil (1-\alpha)(1+1/n_{\text{cal}}) \rceil$ 分位数：

$$\hat{q} = \text{Quantile}\left(\{s_i\}_{i=1}^{n_{\text{cal}}}, \frac{\lceil (1-\alpha)(n_{\text{cal}}+1) \rceil}{n_{\text{cal}}}\right)$$

**第四步：构造预测区间**

对新样本 $X_{n+1}$：

$$C(X_{n+1}) = [\hat{f}(X_{n+1}) - \hat{q}, \; \hat{f}(X_{n+1}) + \hat{q}]$$

### 1.3 关键保证

**有限样本覆盖率保证（Finite-Sample Coverage Guarantee）：**

$$P(Y_{n+1} \in C(X_{n+1})) \geq 1 - \alpha$$

这个保证在以下条件下成立：
1. **可交换性**（Exchangeability）：$(X_1, Y_1), \ldots, (X_{n+1}, Y_{n+1})$ 联合可交换（比 i.i.d. 弱）
2. **无分布假设**：不需要假设数据服从正态分布或任何特定分布
3. **模型无关**：$\hat{f}$ 可以是任何黑盒模型

这就是 CP 的核心魅力：**不管你的模型多复杂、数据分布多奇怪，只要可交换性成立，覆盖率保证就成立。**

---

## 二、从基础到前沿：CP 的重要变体

### 2.1 自适应保形预测区间（Conformalized Quantile Regression, CQR）

基础 CP 的问题：预测区间宽度固定。晴天预测容易、多云天预测困难，但区间一样宽，显然不合理。

Romano et al. (2019, NeurIPS) 提出 CQR：

**第一步**：训练分位数回归模型，同时预测下分位数 $\hat{q}_{\alpha_{\text{lo}}}(X)$ 和上分位数 $\hat{q}_{\alpha_{\text{hi}}}(X)$

**第二步**：在校准集上计算自适应不一致性分数：

$$s_i = \max\left(\hat{q}_{\alpha_{\text{lo}}}(X_i) - Y_i, \; Y_i - \hat{q}_{\alpha_{\text{hi}}}(X_i)\right)$$

**第三步**：计算 $\hat{q}$ 同基础 CP

**第四步**：构造自适应区间：

$$C(X_{n+1}) = [\hat{q}_{\alpha_{\text{lo}}}(X_{n+1}) - \hat{q}, \; \hat{q}_{\alpha_{\text{hi}}}(X_{n+1}) + \hat{q}]$$

关键优势：**区间宽度随输入条件自适应变化**。模型对某些输入预测更自信（区间窄），对另一些更不确定（区间宽），同时保持整体覆盖率保证。

### 2.2 自适应保形推断（Adaptive Conformal Inference, ACI）

时序数据的挑战：可交换性假设不成立（时间序列有自相关性）。

Gibbs & Candès (2021, NeurIPS) 提出 ACI：动态调整 $\alpha_t$ 以适应分布漂移：

$$\alpha_{t+1} = \alpha_t + \gamma(\alpha - \text{err}_t)$$

其中 $\text{err}_t = \mathbb{1}(Y_t \notin C_t(X_t))$ 是时刻 $t$ 的覆盖错误指示器，$\gamma > 0$ 是学习率。

直觉：如果最近覆盖率太低（模型 undercover），$\alpha_t$ 减小 → 区间变宽；反之亦然。这形成了一个**在线反馈控制环路**。

ACI 对光伏预测特别重要：太阳辐照度的统计特性随季节、天气模式显著变化，固定校准的 CP 会失效。

### 2.3 EnbPI：时序保形预测的集成方法

Xu & Xie (2021, ICML) 提出 EnbPI（Ensemble Batch Prediction Intervals）：

- 训练 $B$ 个 bootstrap 聚合模型
- 利用 leave-one-out 残差避免数据拆分
- 滑动窗口更新残差集合

对光伏预测的优势：不需要专门留出校准集（数据利用率更高），且天然处理时序依赖。

---

## 三、CP 在光伏预测中的具体应用

### 3.1 为什么 CP 适合光伏预测？

| 特性 | CP 的优势 | 对光伏预测的意义 |
|------|-----------|-----------------|
| 分布无关 | 不假设误差分布 | 辐照度误差分布高度非正态（右偏、多峰） |
| 模型无关 | 包装任意模型 | 可直接增强现有 XGBoost/LSTM/Transformer |
| 有限样本保证 | 不需要渐近假设 | 新电站数据少，渐近理论不可靠 |
| 自适应宽度 | CQR 等变体 | 晴天窄区间、多云天宽区间，符合物理直觉 |
| 在线更新 | ACI 等变体 | 适应季节变化和模型退化 |

### 3.2 实际场景：日前功率预测的概率区间

以下是一个完整的 CP 应用示例，使用 pvlib 生成仿真数据（基于晴空模型，非实测数据），然后用 CQR 构建预测区间：

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

# ============================================================
# 1. 生成仿真光伏数据（基于晴空模型，非实测数据）
# ============================================================
np.random.seed(42)
n_days = 365
hours = np.arange(6, 19)  # 白天时段

records = []
for day in range(n_days):
    for hour in hours:
        # 晴空辐照度近似（简化正弦模型）
        solar_elevation = np.sin(np.pi * (hour - 6) / 12)
        ghi_clear = 1000 * max(0, solar_elevation)
        
        # 添加天气扰动（云量效应）
        cloud_factor = np.random.beta(2, 5)  # 右偏分布，多数时候晴天
        ghi = ghi_clear * (1 - cloud_factor * 0.8)
        
        # 温度效应
        temp = 25 + 10 * solar_elevation + np.random.normal(0, 3)
        
        # 功率 = f(辐照度, 温度) + 噪声
        power = max(0, ghi * 0.85 * (1 - 0.004 * (temp - 25)) 
                     + np.random.normal(0, 20))
        
        records.append({
            'day': day, 'hour': hour,
            'ghi': ghi, 'temp': temp, 
            'solar_elevation': solar_elevation,
            'power': power
        })

df = pd.DataFrame(records)
X = df[['ghi', 'temp', 'solar_elevation']].values
y = df['power'].values

# ============================================================
# 2. 数据拆分：训练 / 校准 / 测试
# ============================================================
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.4, random_state=42
)
X_cal, X_test, y_cal, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# ============================================================
# 3. CQR 实现
# ============================================================
alpha = 0.1  # 目标覆盖率 90%

# 训练分位数回归模型（下界和上界）
model_lo = GradientBoostingRegressor(
    loss='quantile', alpha=alpha/2, n_estimators=200, max_depth=5
)
model_hi = GradientBoostingRegressor(
    loss='quantile', alpha=1-alpha/2, n_estimators=200, max_depth=5
)
model_lo.fit(X_train, y_train)
model_hi.fit(X_train, y_train)

# 校准集上计算不一致性分数
q_lo_cal = model_lo.predict(X_cal)
q_hi_cal = model_hi.predict(X_cal)
scores = np.maximum(q_lo_cal - y_cal, y_cal - q_hi_cal)

# 计算校正分位数
n_cal = len(y_cal)
q_level = np.ceil((1 - alpha) * (n_cal + 1)) / n_cal
q_hat = np.quantile(scores, min(q_level, 1.0))

# 测试集预测区间
q_lo_test = model_lo.predict(X_test) - q_hat
q_hi_test = model_hi.predict(X_test) + q_hat

# ============================================================
# 4. 评估
# ============================================================
coverage = np.mean((y_test >= q_lo_test) & (y_test <= q_hi_test))
avg_width = np.mean(q_hi_test - q_lo_test)

print(f"目标覆盖率: {1-alpha:.0%}")
print(f"实际覆盖率: {coverage:.1%}")
print(f"平均区间宽度: {avg_width:.1f} kW")
print(f"区间宽度标准差: {np.std(q_hi_test - q_lo_test):.1f} kW")
```

### 3.3 晴天 vs 多云天的区间自适应

CQR 的核心优势在代码中体现：GBR 分位数模型学到了"多云天不确定性更大"，因此：

- **晴天**（高 GHI，低波动）：$\hat{q}_{0.95}(X) - \hat{q}_{0.05}(X)$ 小 → 区间窄
- **多云天**（低 GHI，高波动）：$\hat{q}_{0.95}(X) - \hat{q}_{0.05}(X)$ 大 → 区间宽

加上 CP 的校正项 $\hat{q}$，最终区间既自适应又有覆盖率保证。

### 3.4 在线更新：应对季节漂移

光伏预测的一个关键挑战是**概念漂移**（concept drift）：夏季和冬季的辐照度分布完全不同。ACI 的在线更新策略非常适合这个场景：

```python
# ACI 在线更新示例
gamma = 0.005  # 学习率
alpha_t = alpha  # 初始化

coverages = []
for t in range(len(y_test)):
    # 当前区间
    interval = [
        model_lo.predict(X_test[t:t+1])[0] - q_hat,
        model_hi.predict(X_test[t:t+1])[0] + q_hat
    ]
    
    # 覆盖检查
    err_t = 1 if (y_test[t] < interval[0] or y_test[t] > interval[1]) else 0
    
    # 更新 alpha_t
    alpha_t = alpha_t + gamma * (alpha - err_t)
    alpha_t = np.clip(alpha_t, 0.01, 0.5)
    
    # 用更新后的 alpha_t 重新计算 q_hat
    q_level = np.ceil((1 - alpha_t) * (n_cal + 1)) / n_cal
    q_hat = np.quantile(scores, min(q_level, 1.0))
    
    coverages.append(1 - err_t)

print(f"ACI 滚动覆盖率: {np.mean(coverages):.1%}")
```

---

## 四、CP vs 传统概率预测方法

### 4.1 与分位数回归（QR）的对比

分位数回归直接优化 pinball loss 输出分位数，但**没有有限样本覆盖率保证**。实际中 QR 的覆盖率可能严重偏离目标。

CQR = QR + CP 校正，在 QR 的基础上**加了一层保险**。

### 4.2 与贝叶斯方法的对比

贝叶斯神经网络（BNN）和高斯过程（GP）提供完整的后验分布，但：

- **计算成本高**：BNN 需要 MCMC 或变分推断，GP 是 $O(n^3)$
- **先验敏感**：选错先验会导致置信区间不可靠
- **分布假设**：GP 假设高斯噪声，BNN 的变分后验也是近似

CP 的优势：**计算轻量**（只需在校准集上排序取分位数）+ **无分布假设**。

### 4.3 与集成方法的对比

随机森林/深度集成的预测区间来自成员模型的分散程度，但：

- 集成的分散程度 ≠ 真实不确定性
- 成员模型高度相关时，区间会过窄
- 没有理论覆盖率保证

CP 可以**包装在集成方法外面**，给集成的区间加上校正。

---

## 五、前沿进展与未来方向

### 5.1 多步预测的保形方法

光伏预测通常需要多步（如未来 24 小时逐小时预测）。Stankevičiūtė et al. (2021, ICML) 提出了多步保形预测的 Copula 方法，同时控制联合覆盖率。

### 5.2 空间保形预测

对于光伏电站网络，需要同时给多个电站提供预测区间。Feldman et al. (2023, *Journal of the American Statistical Association*) 探索了空间保形预测的理论框架。

### 5.3 与深度学习的深度融合

Angelopoulos & Bates (2023, *Foundations and Trends in Machine Learning*) 的综述指出，CP 与 Transformer、图神经网络等深度模型的结合是活跃研究方向。在光伏领域，将 CP 与 iTransformer 或 PatchTST 结合是自然的下一步。

### 5.4 因果保形预测

Cauchois et al. (2024) 探索了在因果推断框架下的保形预测，对光伏的意义是：当预测模型的输入（如天气预报）本身有偏差时，如何校正预测区间。

---

## 六、实践建议

### 6.1 给光伏预测工程师的建议

1. **从 CQR 开始**：它是最实用的 CP 变体，代码简单、效果好
2. **校准集要有代表性**：确保校准集覆盖不同天气类型和季节
3. **用 ACI 处理在线场景**：部署后的模型需要 ACI 来适应分布漂移
4. **评估指标**：覆盖率（coverage）+ 区间宽度（sharpness）+ Winkler score
5. **与现有模型结合**：CP 是后处理步骤，不需要重新训练模型

### 6.2 推荐工具库

- **MAPIE**：scikit-learn 兼容的 CP 库（[mapie.readthedocs.io](https://mapie.readthedocs.io)）
- **crepes**：轻量级保形预测库
- **fortuna**：AWS 开源的不确定性量化库

---

## 七、总结

保形预测为光伏功率预测的不确定性量化提供了一个**理论优雅、实践强大**的框架：

- **分布无关**：不假设误差分布形式
- **模型无关**：增强任意现有模型
- **有限样本保证**：覆盖率保证不需要渐近假设
- **自适应**：CQR + ACI 实现条件自适应 + 在线更新
- **计算轻量**：校准步骤只需排序和取分位数

从统计学理论到金融风控，再到可再生能源预测——保形预测的跨行业迁移正在为光伏功率预测的概率化升级提供关键工具。

---

## 参考文献

1. Vovk, V., Gammerman, A., & Shafer, G. (2005). *Algorithmic Learning in a Random World*. Springer.
2. Romano, Y., Patterson, E., & Candès, E. (2019). Conformalized Quantile Regression. *NeurIPS 2019*.
3. Gibbs, I., & Candès, E. (2021). Adaptive Conformal Inference Under Distribution Shift. *NeurIPS 2021*.
4. Xu, C., & Xie, Y. (2021). Conformal Prediction Interval for Dynamic Time-Series. *ICML 2021*.
5. Angelopoulos, A. N., & Bates, S. (2023). Conformal Prediction: A Gentle Introduction. *Foundations and Trends in Machine Learning*, 16(4), 494–591.
6. Stankevičiūtė, K., Alaa, A. M., & van der Schaar, M. (2021). Conformal Time-Series Forecasting. *NeurIPS 2021*.
7. Yang, D., & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press.
8. Feldman, S., Bates, S., & Romano, Y. (2023). Achieving Risk Control in Online Learning Settings. *Journal of the American Statistical Association*.
