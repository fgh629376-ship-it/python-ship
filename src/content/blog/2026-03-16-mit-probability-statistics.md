---
title: "MIT 概率统计核心：从贝叶斯推断到 MLE——光伏预测的统计基础"
description: "整合 MIT 18.05/18.650 课程体系：概率论基础、参数估计(MLE/矩估计/贝叶斯)、假设检验、回归、PCA、GLM——统计学如何服务于光伏功率预测"
pubDate: 2026-03-16
lang: zh
series: mit-courses
category: algorithm
tags: ["概率统计", "MIT", "MLE", "贝叶斯", "假设检验", "回归", "教材笔记"]
---

# MIT 概率统计核心：从贝叶斯推断到 MLE

> **课程体系**：MIT 18.05 (Intro to Probability & Statistics, Spring 2022) + MIT 18.650 (Statistics for Applications, Fall 2016)
> **参考教材**：Grinstead & Snell *Introduction to Probability*; Murphy *Probabilistic Machine Learning* Book 1

## 为什么概率统计对光伏预测至关重要？

光伏预测的本质是**不确定性量化**：

- "明天中午光伏功率是 500kW" → 确定性预测（不够用）
- "明天中午功率在 400-600kW 之间，概率 90%" → **概率预测**（Yang Ch11 的核心）

概率统计提供了：
1. **建模工具**：概率分布、似然函数、贝叶斯推断
2. **估计方法**：MLE、矩估计、最小二乘
3. **验证框架**：假设检验、置信区间、p 值
4. **降维工具**：PCA（统计版）

---

## Part 1：概率论基础（18.05 前半）

### 概率空间三元组

$$(\Omega, \mathcal{F}, P)$$

- $\Omega$：样本空间（所有可能结果）
- $\mathcal{F}$：事件集合（$\sigma$-代数）
- $P$：概率测度（$P(\Omega) = 1$, 可列可加）

### 条件概率与贝叶斯定理

$$P(A|B) = \frac{P(B|A)P(A)}{P(B)}$$

**三种解读**：
- **频率主义**：$P(A)$ = 长期频率
- **贝叶斯主义**：$P(A)$ = 信念强度，可以更新
- **Box 的立场**：Ch7 讨论了两种，偏好似然主义——"让数据说话"

### 重要分布族

**离散**：
- Bernoulli($p$)：二值结果（晴/阴）
- Binomial($n, p$)：$n$ 次试验中成功次数
- Poisson($\lambda$)：稀有事件计数（设备故障次数）

**连续**：
- Normal($\mu, \sigma^2$)：**中心极限定理的王者**——Box ARIMA 假设 $a_t \sim N(0, \sigma_a^2)$
- Exponential($\lambda$)：等待时间（故障间隔）
- Beta($\alpha, \beta$)：比例/概率的先验（晴天指数 $k_t \in [0,1]$）
- Gamma($\alpha, \beta$)：正值连续量（辐照度、功率）

### 大数定律与中心极限定理

**大数定律**：$\bar{X}_n \xrightarrow{P} \mu$（样本均值收敛到总体均值）

**中心极限定理**：$\sqrt{n}(\bar{X}_n - \mu) \xrightarrow{d} N(0, \sigma^2)$

**CLT 是统计推断的基石**——即使原始数据不是正态的，样本均值的分布也趋近正态。这就是为什么 Box 假设残差正态分布通常是合理的。

---

## Part 2：参数估计（18.650 Lec 1-4）

### 最大似然估计（MLE）

$$\hat{\theta}_{MLE} = \arg\max_\theta \mathcal{L}(\theta) = \arg\max_\theta \prod_{i=1}^n f(x_i|\theta)$$

实践中取对数：$\hat{\theta}_{MLE} = \arg\max_\theta \ell(\theta) = \arg\max_\theta \sum_{i=1}^n \ln f(x_i|\theta)$

**MLE 的优良性质**：
- **一致性**：$\hat{\theta}_n \xrightarrow{P} \theta_0$
- **渐近正态性**：$\sqrt{n}(\hat{\theta}_n - \theta_0) \xrightarrow{d} N(0, I(\theta_0)^{-1})$
- **渐近有效性**：达到 Cramér-Rao 下界

**Fisher 信息**：$I(\theta) = -E\left[\frac{\partial^2 \ell}{\partial \theta^2}\right]$ → 参数估计精度的理论极限

### 与 Box 的完美对接

Box Ch7 的参数估计**就是** MLE：
- 条件 MLE = 条件最小二乘（最小化残差平方和 $S^*(\phi, \theta)$）
- Fisher 信息矩阵 = Hessian → 参数标准误差 $\hat{V}(\hat{\xi}) \approx 2\hat{\sigma}_a^2 H^{-1}$
- Marquardt 算法 = 正则化的 Newton 法（矩阵微积分 Lec 9！）

### 矩估计（Method of Moments）

$$\hat{\mu}_k = \frac{1}{n}\sum_{i=1}^n X_i^k \quad \text{（样本矩 = 总体矩）}$$

解方程组得参数估计。

**Box Ch6 的 Yule-Walker 估计就是矩估计的特例**：用样本 ACF（矩）匹配理论 ACF（矩）来估计 AR 参数。

矩估计简单但不如 MLE 高效——Box 强调 MA 参数的矩估计**不高效**，必须用迭代 MLE。

### 贝叶斯估计

$$p(\theta|x) = \frac{p(x|\theta)p(\theta)}{p(x)} \propto \text{似然} \times \text{先验}$$

- **先验** $p(\theta)$：估计前的信念
- **似然** $p(x|\theta)$：数据给出的证据
- **后验** $p(\theta|x)$：更新后的信念

**MAP 估计**：$\hat{\theta}_{MAP} = \arg\max_\theta p(\theta|x)$

**无信息先验时 MAP = MLE**（Box Ch7 确认）

**对光伏预测的意义**：
- **先验知识**：物理约束（功率 $\geq 0$、$\leq$ 装机容量）可以编码为先验
- **在线更新**：每天新数据到达 → 贝叶斯更新后验 → 模型自适应
- **不确定性量化**：后验分布直接给出预测区间（比 Box Ch5 的等宽区间更灵活）

---

## Part 3：假设检验（18.650 Lec 5-6）

### 基本框架

$$H_0: \theta = \theta_0 \quad \text{vs} \quad H_1: \theta \neq \theta_0$$

- **第一类错误**（$\alpha$）：$H_0$ 真时拒绝（虚报）
- **第二类错误**（$\beta$）：$H_1$ 真时不拒绝（漏报）
- **功效**（power）= $1 - \beta$

### 似然比检验

$$\Lambda = 2(\ell(\hat{\theta}_{MLE}) - \ell(\theta_0)) \xrightarrow{d} \chi^2(k)$$

**Box Ch8 的 Ljung-Box Q 检验就是似然比检验的变体**：
- $H_0$：残差是白噪声（模型充分）
- $\tilde{Q}(K) = n(n+2)\sum_{k=1}^K \frac{r_k^2}{n-k} \sim \chi^2(K-p-q)$

### 拟合优度检验

**Kolmogorov-Smirnov 检验**：比较经验 CDF 和理论 CDF 的最大差距

**Box Ch8 的累积周期图检验**就是 KS 检验在频域的版本——检验残差频谱是否均匀（白噪声的特征）。

### 信息准则

$$AIC = -2\ell(\hat{\theta}) + 2k, \quad BIC = -2\ell(\hat{\theta}) + k\ln n$$

**Box Ch6** 用 AIC/BIC 选择 $p, q$——权衡拟合度和模型复杂度。

---

## Part 4：回归分析（18.650 Lec 7）

### 线性回归的概率视角

$$Y_i = \mathbf{x}_i^T\boldsymbol{\beta} + \epsilon_i, \quad \epsilon_i \sim N(0, \sigma^2)$$

**MLE = 最小二乘**（当误差正态时）：

$$\hat{\boldsymbol{\beta}} = (X^TX)^{-1}X^T\mathbf{y}$$

这就是 MIT 18.06 Part 2 的正交投影公式！

### 统计推断

- **$\hat{\beta}_j$ 的分布**：$\hat{\beta}_j \sim N(\beta_j, \sigma^2(X^TX)^{-1}_{jj})$
- **t 检验**：$t = \hat{\beta}_j / \text{se}(\hat{\beta}_j) \sim t(n-p)$
- **F 检验**：模型整体显著性

### 多重共线性

当 $X^TX$ 接近奇异（条件数大）时，$\hat{\boldsymbol{\beta}}$ 的方差爆炸。

**解决方案**：
- Ridge 回归：$\hat{\boldsymbol{\beta}}_{ridge} = (X^TX + \lambda I)^{-1}X^T\mathbf{y}$（贝叶斯解读：正态先验）
- Lasso：$L_1$ 正则化 → 稀疏解（特征选择）
- PCA 回归：先降维再回归

**与 18.06 的连接**：条件数 $\kappa(X^TX) = \sigma_1^2/\sigma_r^2$ → Ridge 相当于截断小奇异值

---

## Part 5：贝叶斯统计（18.650 Lec 8）

### 共轭先验

当先验和似然的乘积仍属同一分布族时：

- Normal 似然 + Normal 先验 → Normal 后验
- Bernoulli 似然 + Beta 先验 → Beta 后验
- Poisson 似然 + Gamma 先验 → Gamma 后验

### MCMC 采样

当后验无法解析计算时（大多数情况）：
- **Metropolis-Hastings**：提议-接受/拒绝
- **Gibbs 采样**：逐维条件采样
- **Hamiltonian MC**：利用梯度信息高效探索（PyMC/Stan）

### 贝叶斯预测

$$p(y_{new}|x_{new}, \text{data}) = \int p(y_{new}|x_{new}, \theta) p(\theta|\text{data}) d\theta$$

不只给点预测，而是**完整的预测分布**！

**这就是 Yang Ch11 概率预测的数学基础**。

---

## Part 6：PCA 与 GLM（18.650 Lec 9-10）

### PCA 的统计视角

- 18.06 的 PCA = SVD 的几何视角
- 18.650 的 PCA = **样本协方差矩阵的特征分解**

$$\hat{\Sigma} = \frac{1}{n-1}X^TX, \quad \hat{\Sigma}\mathbf{v}_k = \lambda_k\mathbf{v}_k$$

选择前 $k$ 个特征向量 → 保留 $\frac{\sum_{i=1}^k \lambda_i}{\sum_{i=1}^p \lambda_i}$ 的总方差

### 广义线性模型（GLM）

$$g(E[Y]) = \mathbf{x}^T\boldsymbol{\beta}$$

- **线性回归**：$g$ = 恒等函数，$Y$ 正态
- **Logistic 回归**：$g$ = logit，$Y$ 二值
- **Poisson 回归**：$g$ = log，$Y$ 计数

**对光伏的意义**：
- 天气分型（晴/多云/阴）→ 多项 Logistic 回归
- 设备故障计数 → Poisson 回归
- 功率上限截断 → Tobit 模型（截断回归）

---

## 大统一：概率统计与三教材的知识网络

### Box 时间序列

| 统计概念 | Box 中的应用 |
|----------|-------------|
| MLE | Ch7 参数估计 |
| Fisher 信息 | 参数标准误差 |
| 似然比检验 | Ch8 模型诊断 |
| AIC/BIC | Ch6 模型选择 |
| 正态假设 | 白噪声 $a_t \sim N(0, \sigma_a^2)$ |
| 条件期望 | Ch5 最优预测 |

### Warner NWP

| 统计概念 | Warner 中的应用 |
|----------|----------------|
| 贝叶斯推断 | Ch12 数据同化（先验=背景场，似然=观测，后验=分析场）|
| 协方差矩阵 | 背景误差协方差 $B$ + 观测误差协方差 $R$ |
| PCA (EOF) | 气象场的主模态分析 |
| 集合统计 | Ch14 集合预报的均值/离散度 |

### Yang Solar

| 统计概念 | Yang 中的应用 |
|----------|-------------|
| 概率预测 | Ch11 预测区间、可靠性图 |
| 回归 | Ch7 MOS 后处理 |
| 交叉验证 | Ch9 预测验证 |
| 分位数回归 | 概率预测的分位数 |

---

## 对光伏预测项目的行动指南

1. **MLE 是默认方法**：模型参数估计首选 MLE，简单有效
2. **贝叶斯做不确定性量化**：后验分布直接给预测区间
3. **AIC/BIC 选模型**：不只是 ARIMA 的 $p,d,q$，也适用于 ML 模型的超参数
4. **Ljung-Box 必做**：每个模型都检验残差白噪声
5. **PCA 降维**：气象特征矩阵条件数大时先 PCA
6. **GLM 框架**：不同预测目标选不同链接函数
7. **交叉验证**：时间序列用 rolling window CV，不是随机 split

---

*📖 [MIT 课程系列](/blog/tags/MIT) | [18.06 线性代数](/blog/2026-03-16-mit-1806-part1-foundations) | [矩阵微积分](/blog/2026-03-16-mit-matrixcalc-deep-dive) | 🧠 MIT 概率统计完成*
