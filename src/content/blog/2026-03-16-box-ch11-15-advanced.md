---
title: "Box 时间序列分析 Ch11-15：传递函数、干预分析、多变量、过程控制"
description: "细读 Box《Time Series Analysis》第11-15章：传递函数模型、交叉相关、干预分析、异常值检测、VAR 模型、反馈控制"
pubDate: 2026-03-16
lang: zh
series: box-timeseries
category: timeseries
tags: ["时间序列", "传递函数", "干预分析", "VAR", "过程控制", "教材笔记"]
---

# Box 时间序列分析 Ch11-15：高级主题

> **教材**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapters 11-15

---

## Ch11：传递函数模型

### 核心概念

当有**输入 $X_t$**（如温度、辐照度）和**输出 $Y_t$**（如功率）时：

$$Y_t = v(B)X_t + N_t = \frac{\omega(B)}{\delta(B)} B^b X_t + N_t$$

- $v(B) = \sum v_j B^j$：传递函数（脉冲响应）
- $b$：纯滞后（输入影响输出的延迟）
- $\omega(B)/\delta(B)$：有理函数参数化（简约！）
- $N_t$：噪声（自身 ARMA 过程）

### 稳定性

传递函数稳定 ⟺ $\delta(B) = 0$ 的根在单位圆外 ⟺ $v_j$ 绝对可和。

### 对光伏的意义

辐照度 → 功率的物理关系就是传递函数！pvlib 的 Model Chain 本质上是确定性传递函数，但实际中还有随机噪声 $N_t$。

---

## Ch12：传递函数的识别、估计与检验

### 预白化 + 交叉相关（CCF）

1. 用 ARIMA 模型"预白化"输入 $X_t$ → $\alpha_t$
2. 用同一个 ARIMA 对 $Y_t$ 做相同变换 → $\beta_t$
3. $\hat{v}_k = r_{\alpha\beta}(k) \cdot \hat{\sigma}_\beta / \hat{\sigma}_\alpha$
4. 从估计的脉冲响应判断 $b, s, r$ → 有理传递函数参数

### 联合估计

$\phi(B), \theta(B)$（噪声）和 $\omega(B), \delta(B)$（传递函数）联合 MLE。

---

## Ch13：干预分析与异常值检测

### 干预分析

当序列受到**已知外部事件**影响时（如政策变化、设备故障）：

$$Y_t = \frac{\omega(B)}{\delta(B)} B^b \xi_t + N_t$$

其中 $\xi_t$ 是干预变量：
- **阶跃函数**（Step）：$S_t^{(T)} = 0$ ($t < T$), $= 1$ ($t \geq T$)
- **脉冲函数**（Pulse）：$P_t^{(T)} = 0$ ($t \neq T$), $= 1$ ($t = T$)

### 异常值检测

- **AO（附加异常值）**：影响单个观测
- **IO（创新异常值）**：影响后续所有观测
- Chen & Liu (1993) 的迭代检测算法

### 对光伏的意义

**设备故障、面板遮蔽、逆变器限功率**都是干预事件 → 自动检测并修正。

---

## Ch14：多变量时间序列

### VAR(p) 模型

$$\mathbf{z}_t = \boldsymbol{\Phi}_1 \mathbf{z}_{t-1} + \cdots + \boldsymbol{\Phi}_p \mathbf{z}_{t-p} + \mathbf{a}_t$$

- $\mathbf{z}_t$ 是 $m \times 1$ 向量（多个序列）
- $\boldsymbol{\Phi}_i$ 是 $m \times m$ 参数矩阵
- $\mathbf{a}_t \sim N(\mathbf{0}, \boldsymbol{\Sigma})$

### Granger 因果性

$X$ **Granger 因果** $Y$ ⟺ $X$ 的过去值有助于预测 $Y$（在已知 $Y$ 的过去的条件下）。

### 协整（Cointegration）

多个非平稳序列的某个线性组合是平稳的 → VECM（向量误差修正模型）。

### 对光伏的意义

**多站点预测**就是多变量时序问题——相邻电站的辐照度相关 → VAR 可以捕获空间-时间依赖。

---

## Ch15：过程控制

### 反馈控制

$$X_t = g(e_t, e_{t-1}, \ldots)$$

控制变量 $X_t$ 是偏差 $e_t = Y_t - T_t$（输出与目标的差）的函数。

### 最小方差控制

$$X_t = -\frac{\psi(B) - \theta(B)}{v(B)\theta(B)} Y_t$$

等价于让输出的方差最小化。

### Box-Jenkins 控制 vs 经典 PID

Box-Jenkins 方法：先建模（传递函数 + 噪声模型）→ 再设计控制器。比盲调 PID 更优。

### 对光伏的意义

**储能调度**、**逆变器功率控制**都是反馈控制问题——预测偏差 → 调整储能充放电策略。

---

## 全书总结

| Part | 章节 | 主题 |
|------|------|------|
| I | Ch1-5 | 线性模型与预测 |
| II | Ch6-9 | 模型建立（识别/估计/诊断/季节） |
| III | Ch10-15 | 高级主题（非线性/传递函数/多变量/控制） |

**Box-Jenkins 框架的永恒贡献**：
1. 迭代建模方法论（识别→估计→诊断→修改）
2. 简约原则的统计学证明
3. 指数平滑的 ARIMA 基础
4. 预测误差 = 信息增量的理解

---

*📖 [Ch10 笔记](/blog/2026-03-16-box-ch10-nonlinear) | [返回教材目录](/textbook/) | 📝 [Box 时间序列系列](/blog/tags/时间序列)*
