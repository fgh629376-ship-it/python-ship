---
title: "🔬 跨行业算法迁移：时序基础模型（Foundation Model）如何改变光伏功率预测？"
description: "从 NLP 的 GPT 到时序的 Chronos/Timer-S1/SPIRIT，基础模型正在颠覆传统预测范式。本文深度分析 2024-2026 年最新进展，探讨它们如何迁移到光伏辐照度和功率预测——零样本泛化、多模态融合、因果图注意力，以及它们的根本局限。"
pubDate: 2026-03-16
lang: zh
category: solar
series: cross-industry
tags: ['跨行业算法', '基础模型', 'Transformer', '时序预测', '光伏预测', '零样本学习']
---

## 引言：为什么光伏预测需要关注"基础模型"？

传统光伏预测的工作流是：收集目标电站 3-5 年历史数据 → 训练 LSTM/XGBoost/ARIMA → 部署。**新电站没有历史数据怎么办？** 这是光伏产业快速扩张中的核心痛点。

时序基础模型（Time Series Foundation Model, TSFM）正在从根本上改变这个范式：在海量跨领域时序数据上预训练 → 零样本迁移到新场景。就像 GPT 不需要针对每个任务重新训练一样，TSFM 的目标是**不需要目标电站的历史数据就能预测**。

本文基于 2024-2026 年最新论文，深度分析这个方向的进展、方法论、以及对光伏预测的具体启示。

---

## 一、时序基础模型的核心思想

### 1.1 从 NLP 的成功经验说起

GPT/BERT 的成功公式：
1. **大规模预训练**：在互联网文本上学习语言的通用规律
2. **通用表征**：学到的 embedding 编码了语义/语法/世界知识
3. **下游微调/零样本**：迁移到具体任务

时序基础模型试图复制这个模式：
1. **在海量时序数据上预训练**：股票、天气、交通、能源、医疗...
2. **学习时序的通用模式**：趋势、季节性、突变、自相关、跨变量依赖
3. **零样本或少样本迁移**：直接预测从未见过的时序

### 1.2 关键技术路线

当前 TSFM 有三大技术路线：

| 路线 | 代表模型 | 核心思想 | 预训练数据 |
|------|---------|---------|-----------|
| **Token化 + Transformer** | Chronos (Amazon, 2024) | 时序值量化为 token，用 T5 架构做 next-token prediction | 多领域公开数据集 |
| **Patch + MoE** | Timer-S1 (清华, 2026) | 时序切片为 patch，8.3B 参数 MoE，Serial-Token Prediction | TimeBench（1万亿时间点） |
| **领域特化** | SPIRIT (2025) | 针对太阳辐照度，用 Lag-Llama/TimesFM 等通用模型做零样本迁移 | 多站点辐照度数据 |

---

## 二、关键论文深度解析

### 2.1 Timer-S1：十亿参数的时序基础模型

**来源**：Liu et al. (2026), 清华大学, GIFT-Eval 排行榜 SOTA

Timer-S1 的三个核心创新：

**① Serial-Token Prediction (STP)**

传统 next-token prediction 的问题：预测长时序需要自回归滚动，误差逐步累积。Timer-S1 提出 STP——将预测目标串行化为多个 token 序列，每个 token 包含一个时间片段的信息，通过序列化计算避免滚动推理。

这解决了一个根本矛盾：**预测精度 vs 预测效率**。自回归模型（GPT 式）精度高但慢且累积误差；直接多步输出（direct multi-step）快但忽略步间依赖。STP 在两者之间找到了平衡。

**② Mixture-of-Experts (MoE)**

8.3B 总参数，但每个 token 只激活 0.75B。这意味着：
- 模型容量足够大，能记住各种时序模式
- 推理时计算量可控（只用 1/11 的参数）
- 不同的 expert 可能学到了不同类型时序的专业知识

**对光伏的启示**：辐照度时序有独特的特征——日变化周期强烈、云遮蔽导致突变、季节性缓慢漂移。MoE 架构中，可能会有专门的 expert 学会处理"有强日变化 + 突变叠加"的模式——这正是辐照度的特征。

**③ TimeBench 数据集**

1 万亿时间点的预训练语料。关键问题：数据混合比例（data mixture）。如果预训练数据中能源/天气数据占比太低，模型对辐照度的零样本能力就会受限。

### 2.2 Chronos 的内部机制：SAE 解剖

**来源**：Mishra (2026), ICLR 2026 Workshop (TSALM)

这篇论文用 Sparse Autoencoder (SAE) 解剖了 Chronos-T5-Large（710M 参数）的内部表征，揭示了 TSFM 到底学到了什么：

**深度依赖的层次结构**：
- **早期编码器层**：编码低级频率特征（周期性、趋势）
- **中间编码器层**：集中了因果关键的**突变检测特征**（max single-feature ΔCRPS = 38.61）
- **最终编码器层**：丰富但因果不重要的时序概念分类

**最惊人的发现**：Chronos 依赖的是**突变动态检测（abrupt-dynamics detection）**而非周期模式识别。逐步消融最终编码器层的特征，预测质量反而**提升**了。

**对光伏的深层启示**：
- 辐照度预测的核心难点正是**云遮蔽导致的突变**（ramp 事件）
- 如果 TSFM 天然擅长检测突变，它们可能特别适合辐照度 nowcasting
- 但周期模式（日变化、季节）也很重要——TSFM 把这部分放在了早期层，说明它们被视为"简单特征"
- 实践意义：微调 TSFM 时，**冻结早期层（保留周期检测）+ 微调中间层（适应辐照度特有的突变模式）** 可能是最优策略

### 2.3 SPIRIT：面向太阳辐照度的零样本迁移

**来源**：Mishra et al. (2025)

SPIRIT 直接验证了 TSFM 在光伏领域的零样本能力：
- 使用通用 TSFM（Lag-Llama、TimesFM 等）
- **零样本迁移到新站点，误差降低约 70%**（相比传统方法在无历史数据时的表现）
- 微调后进一步提升

70% 的改善非常显著，但需要谨慎解读：
- 基线是"完全没有历史数据"的情况——如果有 1-2 年数据，传统方法可能追上来
- 零样本性能高度依赖预训练数据中太阳辐照度的覆盖度
- 论文没有和基于物理模型的晴空 + 卫星云图方法对比——后者也不需要历史数据

### 2.4 SolarCAST：因果图 + Transformer 的时空预测

**来源**：Niu et al. (2025), CIKM 2025

SolarCAST 的创新在于**只用地面站 GHI 数据**（不需要天空相机或卫星图像）实现了时空预测。核心设计：

**三类混淆因素的显式建模**：
1. **可观测同步变量**（时间、站点身份）→ Embedding 模块
2. **隐变量同步因素**（区域天气模式）→ 时空图神经网络（GNN）
3. **时滞影响**（云团跨站移动）→ 门控 Transformer 学习时间偏移

比 Solcast（商业领先服务）误差降低 25.9%。

**对光伏的关键启示**：
- **多站点协同预测 >> 单站点独立预测**——相邻站点的辐照度变化包含了云运动信息
- 不需要昂贵的天空相机或高分辨率卫星——**公共气象站网络就够了**
- 因果图结构让模型知道"A 站的云 → 30 分钟后影响 B 站"，而非纯相关

### 2.5 FusionSF：多模态融合的向量量化框架

**来源**：Ma et al. (2024), 阿里达摩院

FusionSF 融合三种模态：历史功率数据 + NWP + 卫星图像。核心挑战是**信息密度不匹配**：
- 历史功率：密集、1 维
- NWP：稀疏、多变量、有系统偏差
- 卫星图像：高维、空间信息丰富

向量量化（VQ）框架将不同模态对齐到统一的离散表征空间——类似 VQ-VAE 的思想。

**已部署规模**：300+ 光伏电站，总容量 15GW+。这不是纯学术论文，而是已经在生产环境验证的系统。

---

## 三、跨行业迁移的深层逻辑

### 3.1 为什么"时序通用规律"可能存在？

不同领域的时序虽然物理机制完全不同，但在**数学结构**上有共性：
- **趋势 + 季节 + 残差**分解（STL decomposition 的普适性）
- **自相关结构**（ARIMA 的核心假设）
- **突变/变点检测**（regime switching）
- **多尺度特征**（分钟级噪声 → 小时级波动 → 日变化 → 季节变化）

基础模型的预训练就是在学习这些**与领域无关的数学结构**。

### 3.2 辐照度时序的独特性

但辐照度有其他领域罕见的特征：
1. **硬上界约束**：GHI ≤ 外大气辐照度 × 清晰度指数，不可能超过这个物理极限
2. **日变化的确定性成分**：太阳角度是精确已知的（天文计算）
3. **双模态分布**：晴天 vs 阴天，不是连续高斯分布
4. **空间相关性有方向**：云团沿风向移动，不是各向同性

这些特征意味着：**通用 TSFM 的零样本能力有天花板**。最优方案可能是：
$$\text{预测} = \underbrace{\text{晴空模型}}_{\text{物理确定性}} + \underbrace{\text{TSFM}}_{\text{数据驱动残差}}$$

即先用 pvlib 的晴空模型（Ineichen/Perez）计算确定性基线，再用 TSFM 预测偏差（clearsky index 或 cloud modification factor）。这和 Warner 教材 Ch13 的 MOS 后处理思想完全一致——物理模型提供基线，统计方法修正残差。

### 3.3 FutureBoosting 范式的启示

电力价格预测的 FutureBoosting 论文（Qiu et al. 2026）提出了一个优雅的混合框架：
1. 冻结的 TSFM 生成"预测特征"（forecasted features）
2. 注入到下游回归模型（XGBoost/LightGBM）作为额外输入
3. MAE 降低 30%+

**迁移到光伏**：用 Chronos/Timer-S1 对 NWP 的辐照度预报做"增强"——TSFM 提取 NWP 未捕捉的时序模式，作为特征输入到后处理回归模型。这比端到端替换 NWP 更实际、更可解释、更容易部署。

---

## 四、2D 状态空间模型：Mamba 的多变量扩展

### 4.1 置换等变性的理论必要性

VI 2D SSM（Jeong & Suk 2026）指出了一个被广泛忽视的问题：**多变量时序中，变量之间没有自然顺序**。

传统方法（包括 Mamba）将多个变量排成一列做序列建模，隐含假设了变量顺序——但交换变量顺序会改变预测结果。这在物理上是不合理的。

数学上，他们证明了**任何满足置换等变性的线性 2D 状态空间系统**都自然分解为：
$$\mathbf{x}_{t+1}^{(i)} = \mathbf{A}\mathbf{x}_t^{(i)} + \mathbf{B}\bar{\mathbf{x}}_t$$

其中 $\mathbf{x}_t^{(i)}$ 是第 $i$ 个变量的局部状态，$\bar{\mathbf{x}}_t$ 是所有变量的全局池化。**局部自动力学 + 全局池化交互**——不需要变量间的有序递归。

### 4.2 对光伏多站点预测的意义

- 多站点辐照度预测中，站点之间没有自然顺序
- SolarCAST 用图结构（GNN）处理站点关系，VI 2D SSM 用置换不变聚合
- 两者的哲学一致：**站点间的交互应该是对称的**（除非有明确的因果方向，如风向导致的时滞）

---

## 五、实践路线图：从论文到部署

基于以上分析，光伏预测项目可以按以下路径引入跨行业方法：

### 阶段一：立竿见影（1-2 周）
- 用 Chronos-T5-Small（8M 参数）做零样本辐照度预测基线
- 对比传统持续性预报和晴空模型
- 评估：零样本 TSFM 能否在无历史数据时超过晴空+持续性？

### 阶段二：物理增强（2-4 周）
- 晴空模型 + TSFM 残差预测的混合架构
- FutureBoosting 式：TSFM 提取 NWP 辐照度预报的增强特征 → LightGBM 后处理
- 需要 NWP 历史预报和地面站观测的配对数据

### 阶段三：多站点时空（1-2 月）
- SolarCAST 式因果图 Transformer
- 或 VI 2D SSM 的置换等变架构
- 需要多站点同步数据

### 阶段四：微调 TSFM（长期）
- 在中国辐照度数据上微调 Timer-S1 或 Chronos
- 冻结早期层（保留通用时序特征）+ 微调中间层（适应辐照度突变）

---

## 六、局限性与清醒认识

1. **TSFM 不理解物理**：它不知道太阳角度、气溶胶光学厚度、云微物理——这些必须由物理模型或 NWP 提供
2. **数据偏差**：预训练数据以金融/交通/医疗为主，辐照度占比极小——零样本能力有上界
3. **计算成本**：Timer-S1 8.3B 参数，即使 MoE 也需要 A100 级别 GPU。BOSS 的 RTX 4050 6GB 只能跑小模型（Chronos-Small/Tiny）
4. **可解释性差**：Chronos SAE 解剖是重要进步，但距离"理解模型在做什么"还很远
5. **不替代 NWP**：TSFM 是 NWP 的补充（后处理/残差修正），不是替代

---

## 参考文献

1. Liu, Y. et al. (2026). Timer-S1: A Billion-Scale Time Series Foundation Model with Serial Scaling. *arXiv:2603.04791*.
2. Mishra, A. (2026). Dissecting Chronos: Sparse Autoencoders Reveal Causal Feature Hierarchies in Time Series Foundation Models. *ICLR 2026 Workshop (TSALM)*. arXiv:2603.10071.
3. Mishra, A. et al. (2025). SPIRIT: Short-term Prediction of solar IRradIance for zero-shot Transfer learning. *arXiv:2502.10307*.
4. Niu, Y. et al. (2025). Solar Forecasting with Causality: A Graph-Transformer Approach. *CIKM 2025*. arXiv:2509.15481.
5. Ma, Z. et al. (2024). FusionSF: Fuse Heterogeneous Modalities in a Vector Quantized Framework for Robust Solar Power Forecasting. *arXiv:2402.05823*.
6. Qiu, Y. et al. (2026). Regression Models Meet Foundation Models: A Hybrid-AI Approach to Practical Electricity Price Forecasting. *arXiv:2603.06726*.
7. Jeong, S. & Suk, H.-I. (2026). Permutation-Equivariant 2D State Space Models for Multivariate Time Series. *arXiv:2603.08753*.
8. Niu, Y. et al. (2025). Solar Multimodal Transformer: Intraday Solar Irradiance Predictor using Public Cameras and Time Series. *WACV 2025*. arXiv:2503.00250.
9. Lanzilao, L. & Meyer, A. (2026). Intraday spatiotemporal PV power prediction at national scale. *arXiv:2601.04751*.
