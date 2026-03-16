---
title: "🔬 pvlib 深入学习：辐照度分解与转换——从 GHI 到倾斜面的完整建模链"
description: "光伏建模链最容易出错的环节。GHI → DNI + DHI（分解）→ POA（转换），每一步都有多个模型可选。本文深度解析 pvlib 中 8 种分解模型和 7 种转换模型的数学原理、物理假设、适用场景和选择策略。"
pubDate: 2026-03-16
lang: zh
category: solar
series: pvlib
tags: ['pvlib', '辐照度', '分解模型', '转换模型', 'Perez', 'Erbs', 'DISC']
---

## 引言：为什么需要辐照度分解和转换？

光伏组件不是水平放置的——它们通常朝南（北半球）倾斜 20°-40°。但全球绝大多数地面辐照度测量站只测量**水平面总辐照度 GHI**（Global Horizontal Irradiance）。从 GHI 到组件面上的辐照度 POA（Plane of Array），需要经过两步转换：

$$\text{GHI} \xrightarrow{\text{分解}} \text{DNI} + \text{DHI} \xrightarrow{\text{转换}} \text{POA}$$

这两步看似简单，实际上每一步都引入了显著的误差——Gueymard & Ruiz-Arias (2016) 在 *Solar Energy*（中科院 Q1）上的研究表明，分解模型的选择可以导致年发电量估计 2-5% 的差异。对一个 100MW 电站，这意味着数百万元的误差。

---

## 一、基本概念

### 辐照度的三个分量

| 分量 | 符号 | 物理含义 | 测量 |
|------|------|---------|------|
| 总辐照度 | GHI | 水平面接收的全部太阳辐射 | 热电堆日射计（pyranometer） |
| 直射辐照度 | DNI | 来自太阳圆盘方向的辐射 | 直射日射计（pyrheliometer）+跟踪器 |
| 散射辐照度 | DHI | 被大气散射后到达水平面的辐射 | 遮蔽环/球日射计 |

三者的关系：

$$\text{GHI} = \text{DNI} \cdot \cos(\theta_z) + \text{DHI}$$

其中 $\theta_z$ 是太阳天顶角。这个闭合关系是所有分解模型的数学基础。

### 清晰度指数 $k_t$

$$k_t = \frac{\text{GHI}}{I_0 \cdot \cos(\theta_z)}$$

$k_t$ 是 GHI 与水平面外大气辐照度的比值，范围 [0, 1]。它是大气透明度的综合度量：
- $k_t \approx 0.7-0.8$：晴天
- $k_t \approx 0.3-0.5$：多云
- $k_t < 0.2$：阴天/暴风雨

**几乎所有分解模型都是 $k_t$ 的函数**——它们通过经验关系从 $k_t$ 估计散射比例 $k_d = \text{DHI}/\text{GHI}$。

---

## 二、分解模型深度解析

### 2.1 第一代：简单经验关系

#### Orgill & Hollands (1977)

最早的分解模型之一，基于多伦多 4 年小时数据。分段线性关系：

$$k_d = \begin{cases} 1 - 0.249k_t & k_t < 0.35 \\ 1.557 - 1.84k_t & 0.35 \leq k_t \leq 0.75 \\ 0.177 & k_t > 0.75 \end{cases}$$

**物理含义**：
- $k_t$ 低（阴天）：几乎全部是散射，$k_d \approx 1$
- $k_t$ 高（晴天）：散射比例降到 ~18%
- 中间区域：线性过渡

**局限**：只用了一个站点的数据，在热带和干旱地区表现差。

#### Erbs et al. (1982)

pvlib 默认分解模型。改进了 Orgill & Hollands，使用了更多站点数据，用四阶多项式拟合中间段：

$$k_d = \begin{cases} 1 - 0.09k_t & k_t \leq 0.22 \\ 0.9511 - 0.1604k_t + 4.388k_t^2 - 16.638k_t^3 + 12.336k_t^4 & 0.22 < k_t \leq 0.80 \\ 0.165 & k_t > 0.80 \end{cases}$$

**pvlib 源码实现要点**：
- `min_cos_zenith=0.065`（天顶角 > 86.3° 时截断，避免除以零）
- `max_zenith=87`（太阳接近地平线时 DNI 设为 0）
- 最后用闭合关系 $\text{DNI} = (\text{GHI} - \text{DHI})/\cos(\theta_z)$ 反算 DNI

**关键问题**：$k_t = 0.22$ 和 $k_t = 0.80$ 处有不连续性（函数值连续但导数不连续）。这在优化算法中可能导致问题。

#### Erbs-Driesse (2024 改进)

Driesse 重新参数化了 Erbs 模型，用光滑函数替换分段函数，确保**函数及其一阶导数在转折点连续**。这对梯度优化和自动微分（PyTorch/JAX）至关重要。

```python
import pvlib
# 传统 Erbs（分段，有导数不连续）
result_erbs = pvlib.irradiance.erbs(ghi, zenith, doy)

# Erbs-Driesse（连续，可微分）
result_driesse = pvlib.irradiance.erbs_driesse(ghi, zenith, doy)
```

### 2.2 第二代：物理增强

#### DISC (Maxwell 1987)

Direct Insolation Simulation Code。不再直接估计散射比例，而是通过**直射清晰度指数 $k_n$** 估计 DNI：

$$k_n = \frac{\text{DNI}}{I_0}$$

然后用闭合关系反算 DHI。DISC 模型用的是 $k_t$ 和气团质量 AM 的二维关系，比纯 $k_t$ 模型多了一个物理维度——考虑了大气光学路径长度的影响。

#### DIRINT (Perez et al. 1992)

DISC 的改进版，增加了两个额外输入：
1. **时序 GHI 变化**：前后时刻的 $k_t$ 变化率（云的动态信息）
2. **露点温度**：大气水汽含量的代理变量

这两个信息让模型能区分"薄云均匀散射"和"厚云破碎通道效应"——两者有相同的瞬时 $k_t$ 但完全不同的 DNI/DHI 比例。

**pvlib 实现**：
```python
# DIRINT 需要更多输入但精度更高
dni = pvlib.irradiance.dirint(
    ghi, zenith, times,
    pressure=101325,      # 气压
    use_delta_kt_prime=True,  # 使用时序稳定性指标
    temp_dew=10            # 露点温度
)
```

#### DIRINDEX (Perez 2002)

在 DIRINT 基础上再加入**晴空模型信息**。用 Ineichen 晴空 GHI 计算晴空清晰度指数，和实际 $k_t$ 对比——偏差大说明有云，偏差小说明是气溶胶或水汽导致的衰减。

**为什么这很重要**：云和气溶胶都降低 GHI，但对 DNI/DHI 比例的影响完全不同——云主要增加散射，气溶胶同时增加散射和吸收。

### 2.3 第三代：逻辑回归

#### Boland (2008/2013)

用逻辑回归替代分段函数：

$$k_d = \frac{1}{1 + e^{-a(k_t - b)}}$$

只有两个参数 $a$ 和 $b$，天然光滑连续。Boland 模型的优雅在于：
- 自动满足 $k_d \in [0, 1]$ 的物理约束
- 参数可以针对不同气候区重新拟合
- 导数处处存在，适合优化

---

## 三、转换模型深度解析

分解完成后，有了 DNI、DHI 和 GHI。下一步是计算倾斜面上的辐照度 POA：

$$\text{POA} = \text{POA}_{beam} + \text{POA}_{diffuse} + \text{POA}_{ground}$$

直射分量 $\text{POA}_{beam} = \text{DNI} \cdot \cos(\text{AOI})$ 是纯几何计算。地面反射 $\text{POA}_{ground} = \text{GHI} \cdot \rho \cdot (1 - \cos\beta)/2$ 也相对简单。**核心挑战在于散射分量的天空分布模型**。

### 3.1 各向同性模型（Isotropic / Liu-Jordan 1963）

最简单假设：天空散射均匀分布。

$$\text{POA}_{diffuse} = \text{DHI} \cdot \frac{1 + \cos\beta}{2}$$

**物理局限**：真实天空的散射不是均匀的——太阳周围有环日辐射（circumsolar），地平线附近有增亮（horizon brightening）。各向同性模型系统性低估 POA，误差可达 5-10%。

### 3.2 Klucher (1979)

在各向同性基础上增加了环日和地平线增亮的调制因子：

$$\text{POA}_{diffuse} = \text{DHI} \cdot \frac{1 + \cos\beta}{2} \cdot \left[1 + F\sin^3\left(\frac{\beta}{2}\right)\right] \cdot \left[1 + F\cos^2(\theta)\sin^3(\theta_z)\right]$$

其中 $F = 1 - (k_d)^2$ 是各向异性强度因子。晴天 $F$ 大（各向异性强），阴天 $F$ 小（趋向各向同性）。

### 3.3 Hay-Davies (1980)

引入**各向异性指数** $A_I$：

$$A_I = \frac{\text{DNI}}{I_0}$$

将散射分为两部分：环日辐射（按 $A_I$ 比例，方向和直射相同）+ 各向同性背景（按 $1-A_I$ 比例）。

$$\text{POA}_{diffuse} = \text{DHI} \left[A_I \cdot R_b + (1 - A_I) \cdot \frac{1 + \cos\beta}{2}\right]$$

$R_b = \cos(\text{AOI})/\cos(\theta_z)$ 是直射的几何转换因子。

### 3.4 Perez (1987/1990)

最复杂也最准确的模型。将天空散射分为**三部分**：

$$\text{POA}_{diffuse} = \text{DHI} \left[(1 - F_1)\frac{1 + \cos\beta}{2} + F_1\frac{a}{b} + F_2\sin\beta\right]$$

- $(1-F_1)$：各向同性背景
- $F_1 \cdot a/b$：环日辐射（$a = \max(0, \cos\text{AOI})$, $b = \max(\cos 85°, \cos\theta_z)$）
- $F_2 \cdot \sin\beta$：地平线增亮

$F_1$、$F_2$ 由两个天空亮度参数（$\varepsilon$ 和 $\Delta$）通过查表确定——8 个天空类型 × 6 个系数 = 48 个经验系数。

**Perez-Driesse (2024)** 改进：用二次样条替换查找表，消除天空类型切换时的不连续性。

### 3.5 模型选择建议

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 快速估算/教学 | Isotropic | 最简单，理解物理 |
| 一般工程设计 | Hay-Davies | 精度与复杂度的平衡 |
| 精确能产估计 | Perez 1990 | 业界标准，被 PVsyst 等商业软件采用 |
| 优化/自动微分 | Perez-Driesse | 连续可微，适合 PyTorch/JAX |
| 数据极少 | Erbs + Isotropic | 输入要求最低 |

---

## 四、完整代码示例

```python
import pvlib
import pandas as pd
import numpy as np
from pvlib.location import Location

# 定义地点：北京
site = Location(39.9, 116.4, tz='Asia/Shanghai', altitude=50)

# 生成一天的时间序列
times = pd.date_range('2025-06-21 04:00', '2025-06-21 20:00',
                       freq='1min', tz='Asia/Shanghai')
solpos = site.get_solarposition(times)

# 晴空 GHI（Ineichen-Perez 模型）
cs = site.get_clearsky(times, model='ineichen')
ghi = cs['ghi']

# === 步骤1：分解（GHI → DNI + DHI）===
# 方法A：Erbs（简单，默认）
erbs_result = pvlib.irradiance.erbs(ghi, solpos['zenith'], times)

# 方法B：DIRINT（精确，需要额外输入）
dirint_dni = pvlib.irradiance.dirint(
    ghi, solpos['zenith'], times,
    pressure=101325, temp_dew=15
)

# === 步骤2：转换（DNI + DHI → POA）===
surface_tilt = 30
surface_azimuth = 180  # 朝南

# 方法A：各向同性（最简单）
poa_iso = pvlib.irradiance.get_total_irradiance(
    surface_tilt, surface_azimuth,
    solpos['apparent_zenith'], solpos['azimuth'],
    erbs_result['dni'], ghi, erbs_result['dhi'],
    model='isotropic'
)

# 方法B：Perez（最精确）
poa_perez = pvlib.irradiance.get_total_irradiance(
    surface_tilt, surface_azimuth,
    solpos['apparent_zenith'], solpos['azimuth'],
    erbs_result['dni'], ghi, erbs_result['dhi'],
    model='perez', airmass=site.get_airmass(times)['airmass_relative']
)

# 比较差异
diff_pct = (poa_perez['poa_global'] - poa_iso['poa_global']) / poa_iso['poa_global'] * 100
print(f"Perez vs Isotropic 日均差异: {diff_pct.mean():.1f}%")
print(f"Perez POA 日总辐射量: {poa_perez['poa_global'].sum() / 60 / 1000:.2f} kWh/m²")
```

---

## 五、误差传播分析

分解和转换的误差是**乘性传播**的：

$$\sigma_{\text{POA}}^2 \approx \sigma_{\text{decomp}}^2 + \sigma_{\text{trans}}^2 + 2\rho\sigma_{\text{decomp}}\sigma_{\text{trans}}$$

Yang (2016) 在 *Solar Energy*（Q1）上的分析表明：
- 分解模型的典型 MBE：±2-5%（取决于气候区）
- 转换模型的典型 MBE：±1-3%
- **组合误差**：最差情况下可达 ±8%

**最危险的场景**：高纬度冬季低太阳角 + 多云 → 分解模型对低 $k_t$ 区间的不确定性最大，同时 AOI 大导致转换误差放大。

---

## 六、与 Warner 教材的联系

Warner Ch4 讲了辐射参数化方案——NWP 模型在每个网格点计算辐射传输，输出就是 GHI/DNI/DHI。但 NWP 的分辨率是 3-25km，而光伏电站关心的是**组件面上**的辐照度。

pvlib 的分解+转换模型正是连接 NWP 输出和光伏建模的桥梁：
- NWP 输出 GHI → pvlib 分解为 DNI + DHI → 转换到 POA → 功率模型
- Warner Ch13 的 MOS 后处理可以应用于 GHI 预报（消除系统偏差）
- 分解模型的误差是 NWP → PV 预测链中的一个**不可忽视的误差源**

---

## 参考文献

1. Erbs, D.G., Klein, S.A. & Duffie, J.A. (1982). Estimation of the diffuse radiation fraction for hourly, daily and monthly-average global radiation. *Solar Energy*, 28(4), 293-302.
2. Perez, R. et al. (1990). Modeling daylight availability and irradiance components from direct and global irradiance. *Solar Energy*, 44(5), 271-289.
3. Maxwell, E.L. (1987). A quasi-physical model for converting hourly GHI to DNI. *SERI/TR-215-3087*.
4. Perez, R. et al. (1992). Dynamic global-to-direct irradiance conversion models (DIRINT). *ASHRAE Trans.*, 98, 354-369.
5. Boland, J. et al. (2008). Modelling the diffuse fraction of global solar radiation on a horizontal surface. *Environmetrics*, 19, 120-136.
6. Gueymard, C.A. & Ruiz-Arias, J.A. (2016). Extensive worldwide validation and climate sensitivity analysis of direct irradiance predictions from 1-min global irradiance. *Solar Energy*, 128, 1-30.
7. Yang, D. (2016). Solar radiation on inclined surfaces: Corrections and benchmarks. *Solar Energy*, 136, 288-302.
8. Driesse, A. & Stein, J.S. (2024). Reformulation of the Erbs and Perez diffuse irradiance models for improved continuity. *pvlib documentation*.
