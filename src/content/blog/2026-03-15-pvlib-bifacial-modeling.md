---
title: 'pvlib 双面组件建模实战 — 背面多收 10-20% 的物理逻辑'
description: '用 pvlib.bifacial 模块对双面光伏组件进行建模：infinite_sheds 辐照计算、视角因子分析、失配损耗量化，附完整代码'
category: solar
series: pvlib
lang: zh
pubDate: '2026-03-15'
tags: ["pvlib", "双面组件", "bifacial", "光伏建模", "视角因子"]
---

## 双面组件：光伏行业的「新标配」

2024 年全球新增光伏装机中，**双面组件占比已超过 70%**（ITRPV 2024 Roadmap）。道理很简单 —— 背面也能发电，同样的地面面积多收 10-20% 的电。

但「多收多少」并不是一个简单的数字。它取决于地面反照率、安装高度、行间距、倾角、甚至组件在阵列中的位置。**pvlib 的 `bifacial` 模块提供了完整的物理建模工具**，让你能精确量化每一个因素的影响。

> ⚠️ 本文所有数据基于晴空模型仿真，非实测数据

---

## 一、双面发电的物理原理

双面组件的背面接收三种辐照：

1. **地面反射辐照**：GHI 照到地面，按反照率 ρ 反射到背面 —— 这是主要来源
2. **天空散射辐照**：天空半球散射光照到背面
3. **直射分量**：低太阳高度角时（早晚），直射光可能绕过组件照到背面

核心方程：

```
E_back = ρ × GHI × VF(back→ground) + DHI × VF(back→sky)
```

其中 **VF（视角因子）** 是几何关系的定量描述，决定了背面「看到」多少地面和天空。

---

## 二、infinite_sheds 模型

pvlib 提供 `infinite_sheds` 模型 —— 假设组件阵列无限长（消除边缘效应），计算正面和背面的辐照度。

### 基本用法

```python
import pvlib
import pandas as pd

# 地点和时间
loc = pvlib.location.Location(31.23, 121.47, tz='Asia/Shanghai', altitude=5)
times = pd.date_range('2024-06-21 05:00', '2024-06-21 19:00',
                       freq='10min', tz='Asia/Shanghai')

# 太阳位置 + 晴空辐照
solpos = loc.get_solarposition(times)
cs = loc.get_clearsky(times)

# 双面辐照计算
result = pvlib.bifacial.infinite_sheds.get_irradiance(
    surface_tilt=30,                              # 组件倾角
    surface_azimuth=180,                          # 朝南
    solar_zenith=solpos['apparent_zenith'],
    solar_azimuth=solpos['azimuth'],
    gcr=0.4,                                      # 地面覆盖率
    height=1.5,                                   # 组件中心高度(m)
    pitch=2.5,                                    # 行间距(m)
    ghi=cs['ghi'], dhi=cs['dhi'], dni=cs['dni'],
    albedo=0.25,                                  # 地面反照率
    iam_front=1.0, iam_back=1.0,                  # 入射角修正（简化）
)
```

### 返回结果

`get_irradiance` 返回 13 列 DataFrame：

| 列名 | 含义 |
|------|------|
| `poa_front` | 正面总 POA |
| `poa_front_direct` | 正面直射分量 |
| `poa_front_diffuse` | 正面散射总量 |
| `poa_front_ground_diffuse` | 正面接收的地面反射 |
| `poa_front_sky_diffuse` | 正面接收的天空散射 |
| `shaded_fraction_front` | 正面被遮挡比例 |
| `poa_back` | 背面总 POA |
| `poa_back_direct` / `diffuse` / ... | 背面各分量（同上） |
| `poa_global` | 正面 + 背面总辐照 |

---

## 三、关键参数敏感性分析

### 3.1 反照率（albedo）—— 影响最大的单一因素

上海夏至日（6月21日），固定 GCR=0.4、tilt=30°：

| 地面类型 | 反照率 | 背面日辐照 | 双面增益 |
|---------|--------|-----------|---------|
| 深色沥青 | 0.15 | 0.77 kWh/m² | **11.3%** |
| 浅色土壤 | 0.25 | 1.22 kWh/m² | **18.0%** |
| 浅色混凝土 | 0.35 | 1.67 kWh/m² | **24.5%** |
| 白色碎石 | 0.50 | 2.35 kWh/m² | **34.3%** |
| 新雪 | 0.70 | 3.25 kWh/m² | **47.2%** |

**结论**：反照率从 0.15→0.50，双面增益翻了 3 倍。这就是为什么很多电站铺白色防水卷材或碎石 —— **投入几万块地面处理，多收 10-15% 的电，2-3 年就回本**。

> 参考文献：Deline et al. (2020) "Bifacial PV System Performance: Separating Fact from Fiction", IEEE JPVSC. Q1 期刊.

### 3.2 GCR（地面覆盖率）—— 密度 vs 增益的博弈

| GCR | 行间距(m) | 背面增益 |
|-----|----------|---------|
| 0.25 | 4.0 | **21.7%** |
| 0.30 | 3.3 | **20.4%** |
| 0.35 | 2.9 | **19.2%** |
| 0.40 | 2.5 | **18.0%** |
| 0.50 | 2.0 | **15.5%** |
| 0.60 | 1.7 | **13.1%** |

**规律**：GCR 每增加 0.1，双面增益下降约 2-3 个百分点。行间遮挡减少了地面反射到背面的辐照。

**工程启示**：双面组件的最优 GCR 比单面组件更低（典型 0.30-0.40 vs 0.40-0.50），因为牺牲一点密度换来的双面增益更划算。

### 3.3 月度变化 —— 夏高冬低

上海全年晴空模型下（GCR=0.4, albedo=0.25）：

| 季节 | 月份 | 双面增益 |
|------|------|---------|
| 冬季 | 12月 | **5.4%** |
| 春季 | 3月 | **11.0%** |
| 夏季 | 6月 | **17.9%** |
| 秋季 | 9月 | **12.5%** |

**年均双面增益：11.9%**，年总辐照从 2437 增加到 2726 kWh/m²（+289 kWh/m²）。

**为什么夏高冬低？** 夏季太阳高度角大，地面接收的 GHI 强，反射到背面的辐照也多。冬季太阳低，前排遮挡严重，背面增益缩水。

---

## 四、视角因子（View Factor）—— 几何的力量

视角因子描述一个表面「看到」另一个表面的比例。pvlib 提供了 2D 解析解：

```python
from pvlib.bifacial import utils

# x 是组件上的相对位置（0=底边, 1=顶边）
# 背面看天空
vf_sky = utils.vf_row_sky_2d(surface_tilt=30, gcr=0.4, x=0.5)
# 背面看地面
vf_gnd = utils.vf_row_ground_2d(surface_tilt=30, gcr=0.4, x=0.5)
```

### 倾角对视角因子的影响

| 倾角 | VF(→sky) | VF(→ground) | 总和 |
|------|----------|-------------|------|
| 0° | 1.0000 | 0.0000 | 1.0000 |
| 15° | 0.9737 | 0.0119 | 0.9856 |
| 30° | 0.8999 | 0.0473 | 0.9472 |
| 45° | 0.7914 | 0.1057 | 0.8970 |
| 60° | 0.6637 | 0.1857 | 0.8494 |
| 90° | 0.4019 | 0.4019 | 0.8039 |

**关键发现**：
- 水平（0°）时背面完全看不到地面 → 双面增益为零
- 垂直（90°）时两面对称，VF 完全相等 → 东西向双面幕墙的物理基础
- **总和 < 1**：说明有一部分视角被相邻组件行遮挡了

### 沿组件位置的非均匀性

倾角 30°、GCR=0.4 时：

| 位置 x | VF(→sky) | VF(→ground) |
|--------|----------|-------------|
| 0（底边）| 0.8409 | 0.0670 |
| 0.25 | 0.8747 | 0.0560 |
| 0.50（中心）| 0.8999 | 0.0473 |
| 0.75 | 0.9187 | 0.0405 |
| 1.00（顶边）| 0.9330 | 0.0350 |

**底边看到更多地面、更少天空；顶边相反。** 这种非均匀性导致背面辐照沿组件长度方向分布不均 —— 直接影响失配损耗。

---

## 五、Deline 功率失配模型

双面组件背面辐照不均匀，会导致电池串之间电流不匹配。pvlib 实现了 Deline 等人的经验模型：

```python
loss = pvlib.bifacial.power_mismatch_deline(
    rmad=0.10,  # 背面辐照的相对平均绝对偏差
    fill_factor=0.79  # 组件填充因子
)
# 返回: 0.0462 (即 4.62% 的功率损失)
```

### RMAD vs 失配损耗

| RMAD（辐照不均匀度）| 功率损耗 |
|------------------|---------|
| 2% | 0.41% |
| 5% | 1.51% |
| 10% | **4.62%** |
| 15% | **9.33%** |
| 20% | **15.64%** |
| 30% | **33.06%** |

**结论**：不均匀度 ≤5% 时损耗可忽略；超过 10% 后损耗急剧上升（近似二次关系）。

> 参考：Deline et al. (2020) "Assessment of Bifacial PV Mismatch Losses", NREL Technical Report. NREL-TP-5K00-74831.

### Fill Factor 的影响

| Fill Factor | RMAD=10% 时的损耗 |
|-------------|-----------------|
| 0.70 | 4.09% |
| 0.75 | 4.39% |
| 0.79 | 4.62% |
| 0.85 | 4.97% |

FF 越高的组件对失配越敏感 —— 因为高 FF 意味着 I-V 曲线更「方」，一旦有电池被限制，功率下降更陡。

---

## 六、完整建模流程：双面系统发电量

把以上模块串联起来，计算一个 5kWp 双面系统的日发电量：

```python
import pvlib
import pandas as pd
import numpy as np

# 1. 环境设置
loc = pvlib.location.Location(31.23, 121.47, tz='Asia/Shanghai', altitude=5)
times = pd.date_range('2024-06-21 05:00', '2024-06-21 19:00',
                       freq='10min', tz='Asia/Shanghai')
solpos = loc.get_solarposition(times)
cs = loc.get_clearsky(times)

# 2. 双面辐照
bifi_irr = pvlib.bifacial.infinite_sheds.get_irradiance(
    surface_tilt=30, surface_azimuth=180,
    solar_zenith=solpos['apparent_zenith'],
    solar_azimuth=solpos['azimuth'],
    gcr=0.4, height=1.5, pitch=2.5,
    ghi=cs['ghi'], dhi=cs['dhi'], dni=cs['dni'],
    albedo=0.25, iam_front=1.0, iam_back=1.0,
)

# 3. 有效辐照度 = 正面 + 背面 × 双面系数 × (1 - 失配)
bifaciality = 0.70  # 背面效率 / 正面效率（典型值 0.65-0.80）
rmad = 0.08  # 背面辐照不均匀度
mismatch = pvlib.bifacial.power_mismatch_deline(rmad=rmad)

effective_irradiance = (
    bifi_irr['poa_front']
    + bifi_irr['poa_back'] * bifaciality * (1 - mismatch)
).clip(lower=0)

# 4. 组件温度（用正面 POA 近似，因为温度主要由正面决定）
temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
cell_temp = pvlib.temperature.sapm_cell(
    bifi_irr['poa_front'].clip(lower=0), 28, 1.5,
    **temp_params
)

# 5. DC 功率（PVWatts 简化模型）
pdc0 = 5000  # 5kWp
gamma_pdc = -0.004  # 温度系数 -0.4%/°C
dc_power = pvlib.pvsystem.pvwatts_dc(effective_irradiance, cell_temp,
                                      pdc0, gamma_pdc)

# 6. AC 功率
ac_power = pvlib.inverter.pvwatts(dc_power, pdc0=5500, eta_inv_nom=0.96)

# 7. 对比单面
single_irr = pvlib.irradiance.get_total_irradiance(
    30, 180, solpos['apparent_zenith'], solpos['azimuth'],
    cs['dni'], cs['ghi'], cs['dhi'], model='isotropic'
)
dc_single = pvlib.pvsystem.pvwatts_dc(
    single_irr['poa_global'].clip(lower=0), cell_temp, pdc0, gamma_pdc
)
ac_single = pvlib.inverter.pvwatts(dc_single, pdc0=5500, eta_inv_nom=0.96)

dt = 10/60
print(f"双面日发电量: {ac_power.clip(lower=0).sum()*dt/1000:.2f} kWh")
print(f"单面日发电量: {ac_single.clip(lower=0).sum()*dt/1000:.2f} kWh")
print(f"双面增益: {(ac_power.sum()-ac_single.sum())/ac_single.sum()*100:.1f}%")
```

---

## 七、工程设计要点

### 反照率提升方案

| 方案 | 反照率 | 成本 | 维护 |
|------|--------|------|------|
| 原始土地 | 0.15-0.25 | 零 | 需除草 |
| 白色碎石 | 0.40-0.50 | ¥5-10/m² | 极低 |
| 白色防水卷材 | 0.55-0.70 | ¥15-30/m² | 需清洁 |
| 白色涂料 | 0.50-0.65 | ¥8-15/m² | 需补涂 |

### GCR 选择

- **单面组件**：GCR=0.40-0.50（经济最优）
- **双面组件**：GCR=0.30-0.40（更低密度，释放双面增益）
- **竖直双面**：GCR=0.15-0.25（农光互补，东西向）

### 常见双面系数（bifaciality factor）

| 电池技术 | 双面系数 |
|---------|---------|
| p-PERC | 0.65-0.70 |
| n-PERT | 0.75-0.85 |
| n-TOPCon | 0.80-0.85 |
| HJT | 0.85-0.95 |

> 参考：ITRPV (2024) "International Technology Roadmap for Photovoltaic", 14th Edition.

---

## 八、关键发现总结

1. **反照率是双面增益的第一决定因素**：0.15→0.50，增益从 11%→34%
2. **年均双面增益约 10-12%**（上海，albedo=0.25），夏季最高（18%），冬季最低（5%）
3. **GCR 每增加 0.1，双面增益下降 2-3%** —— 双面电站需要更低密度
4. **失配损耗在 RMAD<5% 时可忽略**（<1.5%），超过 10% 后急剧上升
5. **视角因子沿组件非均匀分布**：底边比顶边多看 90% 的地面 → 背面辐照不均
6. **FF 越高的组件对失配越敏感** —— HJT 组件（FF≈0.83）需要更注意行间距设计

---

## 参考文献

- Deline, C. et al. (2020). "Bifacial PV System Performance: Separating Fact from Fiction." *IEEE Journal of Photovoltaics*, 10(4), 1090-1098. (Q1)
- Deline, C. et al. (2020). "Assessment of Bifacial PV Mismatch Losses." NREL Technical Report, NREL/TP-5K00-74831.
- Stein, J.S. et al. (2021). "Bifacial PV Performance Models: A Comparison of Ray Tracing and View Factor Approaches." *Solar Energy*, 225, 310-326. (Q1)
- ITRPV (2024). *International Technology Roadmap for Photovoltaic*, 14th Edition.
- pvlib 官方文档：[bifacial module](https://pvlib-python.readthedocs.io/en/stable/reference/bifacial.html)
