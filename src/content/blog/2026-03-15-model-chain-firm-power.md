---
title: '从辐照度到电力：Model Chain 全解 + Firm Power 终极目标'
description: '教材完结篇 — Ch11 物理 Model Chain 七大环节（分离/转置/反射/温度/PV/损耗）+ Ch12 层次预测与 Firm Power Delivery'
category: solar
series: solar-book
lang: zh
pubDate: '2026-03-15'
tags: ["Model Chain", "pvlib", "层次预测", "Firm Power", "光伏预测"]
---

## 🎉 教材完结！全书 12 章学完

本文是 *Solar Irradiance and Photovoltaic Power Forecasting* (Yang & Kleissl, 2024) 的最后两章笔记。Ch11 讲「辐照度怎么变成电」，Ch12 讲「预测怎么服务电网」。

---

## Ch11: 辐照度→功率转换

### 核心论点：两阶段 > 一阶段

- **一阶段**（ML 直接预测功率）：需要大量历史数据 + 每个电站重新训练 → 不可扩展
- **两阶段**（预测辐照度 → Model Chain → 功率）：新电站也能用 → 电网级方案的唯一选择
- GEFCom2014 冠军团队是唯一用了晴空模型的 → 晴空信息永远是最重要的特征

### Model Chain 七大环节

| 环节 | 输入 → 输出 | 当前最优模型 | pvlib 函数 |
|------|-------------|-------------|-----------|
| 太阳定位 | 时间+经纬度 → Z, θ | SPA (±0.0003°) | `pvlib.solarposition.get_solarposition` |
| 分离 | GHI → DHI + BNI | YANG4 (temporal cascade) | `pvlib.irradiance.erbs` / 自定义 |
| 转置 | 水平辐照 → 倾斜面辐照 | Perez 1990 | `pvlib.irradiance.perez` |
| 反射损失 | AOI → 有效辐照 | PHYSICAL / Martin-Ruiz | `pvlib.iam.physical` |
| 温度 | Gc + Tamb + W → Tcell | KING (Sandia) | `pvlib.temperature.sapm_cell` |
| PV 建模 | Gc + Tcell → Pdc | CEC 单二极管 / PVWATTS | `pvlib.pvsystem.singlediode` |
| 损耗 | Pdc → Pac | 逆变器+线缆+污垢+遮阴 | `pvlib.inverter.sandia` |

### 分离建模的演进

150+ 个分离模型，YANG4 当前最优（126 站 DM 检验确认）：

> ERBS (1982, 单变量) → BRL (2010, logistic+多变量) → ENGERER2 (2015, 云增强检测) → YANG4 (2021, temporal resolution cascade)

**Temporal resolution cascade** 的思想：先用 ENGERER2 在小时尺度算 k_hourly，再用它作为 YANG4 的额外输入在分钟尺度算精细 k。低频→高频的级联。

### 概率 Model Chain

最终结论（Mayer & Yang, 2023b）：**概率天气输入 + 集成 Model Chain + P2P 后处理** 是最优工作流。即使最终只需要确定性预测，先做概率再提取确定性，效果仍然更好。

---

## Ch12: 层次预测与 Firm Power

### 层次预测

电力系统天然是层次结构（互联网→输电区→电站→逆变器）。各层独立预测 → 聚合不一致。

**最优调和方法：MinT-shrink**
- 原理：最小化调和误差的迹，用收缩估计器处理高维协方差
- CAISO 案例：34 个变电站、405 个电站，MinT-shrink 在确定性和概率验证中都最优

### Firm Power: 光伏预测的终极目标

| 概念 | 目标 | 成本乘数 |
|------|------|---------|
| Firm Forecasting | 发电精确跟随预测 | ~2x |
| Firm Generation | 发电精确跟随负荷 | ~3x |

**四种 Firm Power Enablers**：

1. **储能** — 最直观，但单靠储能成本极高
2. **地理平滑** — 分散布局降低总波动
3. **负荷塑形** — 需求响应，让用电适应发电
4. **超配+主动弃电** — **反直觉但所有实证研究都表明这是必要的**

> 不能只靠储能。最优方案 = 超配 1.5x + 适量储能 + 地理平滑。加州案例：firm forecasting premium $100/kW/年，firm generation premium $205/kW/年。

### 关键启示

**预测越准 → firm 成本越低**。这就是为什么前面 10 章花那么多篇幅讲预测方法和验证——它不是学术游戏，而是直接影响几十亿美元的成本。

---

## 全书总结

| 章 | 主题 | 一句话总结 |
|----|------|-----------|
| 1-2 | 为什么预测 + 思维工具 | Murphy 三维度 + 奥卡姆剃刀 |
| 3 | 概率预测 | 混沌→不确定性→必须量化 |
| 4 | 光伏特殊性 | 晴空模型是最大武器 |
| 5 | 数据处理 | QC + 归一化 + 时间对齐 |
| 6 | 数据源 | NWP > 卫星 > 地面，三者互补 |
| 7 | 基础方法 | NWP 日前不可替代 |
| 8 | 后处理 | D2D/P2D/D2P/P2P 四象限 |
| 9 | 确定性验证 | Skill Score + Murphy-Winkler |
| 10 | 概率验证 | CRPS + 校准-锐度范式 |
| 11 | Model Chain | 七环节 + 概率 chain |
| 12 | 层次预测 + Firm Power | MinT-shrink + 超配+储能 |

**全书核心思想**：光伏预测是一个完整的工程系统，从 NWP 到后处理到验证到转换到电网集成，每个环节都有物理和统计的最佳实践。简单、可复现、有物理依据的方法 > 花哨的深度学习黑箱。

---

## 参考文献

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press. Chapters 11-12.
- Mayer, M.J. & Yang, D. (2022, 2023b). Model-chain ensemble for PV power forecasting. *Solar Energy*. (Q1)
- Yang, D. (2022b). YANG4 separation model review. *Renewable and Sustainable Energy Reviews*. (Q1)
- Perez, R. et al. (2020, 2021). Firm power delivery framework. *Solar Energy*. (Q1)
- Wickramasuriya, S.L. et al. (2019). Optimal forecast reconciliation. *JASA*. (Q1)
