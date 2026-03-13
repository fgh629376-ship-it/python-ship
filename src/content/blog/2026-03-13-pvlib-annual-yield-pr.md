---
title: 'pvlib 年度发电量评估与 PR 计算 — 从公式到全年仿真'
description: '用 pvlib 对上海 5kWp 系统做 8760 小时仿真，系统讲解 PR、比发电量、容量因子的计算方法，以及为什么夏天 PR 反而最低'
category: solar
lang: zh
pubDate: '2026-03-13'
tags: ["pvlib", "光伏", "PR计算", "发电量评估", "技术干货"]
---

> ⚠️ **数据声明**：本文所有仿真数据均基于 **pvlib 晴空模型（clearsky）** 计算，非真实电站实测数据。晴空模型假设全年无云无雾霾，因此 GHI、发电量、PR 等数值会高于实际。真实电站数据请以实测为准。

## 为什么你的光伏系统发电量总比预期少？

装了 5kWp 的光伏系统，理论上每年能发多少电？翻遍厂商手册，你会发现一个词反复出现：**PR**（Performance Ratio，系统效率比）。

PR 是光伏行业衡量系统"健康度"的核心指标。一套 PR = 92% 的系统和 PR = 78% 的系统，装机容量一样，年发电量可能差出 15%。

本文用 pvlib 对上海某 5kWp 住宅光伏系统做全年小时级仿真，手把手算清楚 PR、比发电量、容量因子——以及为什么夏天的 PR 反而最低。

---

## 一、核心指标公式

在开始写代码之前，先把三个公式烂熟于心：

### PR（Performance Ratio）

$$PR = \frac{E_{ac}}{P_{peak} \times H_{POA}}$$

- $E_{ac}$：年 AC 发电量（kWh）
- $P_{peak}$：装机容量（kWp）
- $H_{POA}$：面板平面（POA）年辐照量（kWh/m²）

**重点**：分母用的是 POA 辐照量，不是水平面 GHI！

### 比发电量（Specific Yield）

$$SY = \frac{E_{ac}}{P_{peak}} \quad \text{[kWh/kWp]}$$

理解成"每装 1kW 峰值容量，一年能发多少度电"。

### 容量因子（Capacity Factor）

$$CF = \frac{E_{ac}}{P_{peak} \times 8760} \times 100\%$$

---

## 二、全年小时级仿真

### 环境准备

```bash
pip install pvlib pandas numpy
```

### 步骤 1：生成全年模拟气象数据

```python
import pvlib
import pandas as pd
import numpy as np
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import warnings
warnings.filterwarnings('ignore')

# 上海：北纬 31.2°，东经 121.5°
site = Location(31.2, 121.5, tz='Asia/Shanghai', altitude=10, name='上海')

# 全年 8760 个小时
times = pd.date_range('2025-01-01', '2025-12-31 23:00', freq='h', tz='Asia/Shanghai')

# 晴空辐照度作为基准
cs = site.get_clearsky(times, model='ineichen')

# 加入随机云量扰动，模拟真实天气
np.random.seed(42)
cloud_factor = np.clip(np.random.beta(3, 1, len(times)), 0.1, 1.0)
day_mask = cs['ghi'] > 0

ghi = cs['ghi'].copy() * np.where(day_mask, cloud_factor, 1.0)
dni = cs['dni'].copy() * np.where(day_mask, cloud_factor, 1.0)
dhi = cs['dhi'].copy() * np.where(day_mask, cloud_factor, 1.0)

weather = pd.DataFrame({
    'ghi': ghi, 'dni': dni, 'dhi': dhi,
    # 气温：年均 15°C，夏热冬冷
    'temp_air': 15 + 10*np.sin(2*np.pi*(times.dayofyear-80)/365)
                   + np.random.normal(0, 3, len(times)),
    'wind_speed': np.clip(3 + np.random.exponential(2, len(times)), 0, 20),
}, index=times)

print(f"年 GHI: {weather['ghi'].sum()/1000:.0f} kWh/m²")
# 年 GHI: 1640 kWh/m²
```

### 步骤 2：建立 PV 系统模型

```python
# 加载 CEC 组件数据库（内置，无需下载）
cec_mods = pvlib.pvsystem.retrieve_sam('CECMod')
module = cec_mods['Canadian_Solar_Inc__CS6P_250P']

print(f"组件 STC 功率: {module['STC']:.0f}W")
print(f"温度系数(Pmax): {module['gamma_r']:.3f}%/°C")
# 组件 STC 功率: 250W
# 温度系数(Pmax): -0.424%/°C

# SAPM 温度模型参数（开放式支架，玻璃-玻璃封装）
temp_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

N_MOD = 20          # 组件数量
KWP = N_MOD * module['STC'] / 1000  # = 5.0 kWp

# pvlib 0.15.0 需要通过 Array + FixedMount 传入安装参数
array = Array(
    mount=FixedMount(surface_tilt=30, surface_azimuth=180),  # 南向 30° 固定倾角
    module_parameters=module,
    temperature_model_parameters=temp_params,
    modules_per_string=N_MOD,
    strings=1,
)

system = PVSystem(
    arrays=[array],
    inverter_parameters={'pdc0': KWP * 1000, 'eta_inv_nom': 0.96},  # PVWatts 逆变器
)
```

### 步骤 3：运行 ModelChain，提取结果

```python
mc = ModelChain(system, site, aoi_model='physical', spectral_model='no_loss')
mc.run_model(weather)

# ⚠️ pvlib 0.15.0 的坑：results.ac 是 DataFrame，功率在 p_mp 列！
ac_power = mc.results.ac['p_mp'].clip(0)   # AC 功率，单位 W
dc_power = mc.results.dc['p_mp'].clip(0)   # DC 功率，单位 W
poa = mc.results.total_irrad['poa_global'] # 面板平面辐照度，W/m²
cell_temp = mc.results.cell_temperature    # 电池温度，°C

# 转换为年度总量
ann_ac_kwh = float(ac_power.sum() / 1000)
ann_dc_kwh = float(dc_power.sum() / 1000)
poa_kwh_m2 = float(poa.sum() / 1000)

print(f"年 POA (30°南向): {poa_kwh_m2:.0f} kWh/m²")
print(f"DC 发电量: {ann_dc_kwh:.0f} kWh/年")
print(f"AC 发电量: {ann_ac_kwh:.0f} kWh/年")
# 年 POA (30°南向): 1883 kWh/m²
# DC 发电量: 9069 kWh/年
# AC 发电量: 8694 kWh/年
```

### 步骤 4：计算关键指标

```python
# PR：注意分母是 KWP × poa_kwh_m2，单位已经对齐
pr = ann_ac_kwh / (KWP * poa_kwh_m2)
sy = ann_ac_kwh / KWP               # 比发电量
cf = ann_ac_kwh / (KWP * 8760)      # 容量因子

print(f"PR: {pr:.3f} ({pr*100:.1f}%)")
print(f"比发电量: {sy:.0f} kWh/kWp")
print(f"容量因子: {cf*100:.1f}%")
# PR: 0.923 (92.3%)
# 比发电量: 1739 kWh/kWp
# 容量因子: 19.8%
```

---

## 三、月度 PR 分析：为什么夏天 PR 最低？

```python
m_ac  = (ac_power.resample('ME').sum() / 1000).values
m_poa = (poa.resample('ME').sum() / 1000).values
m_ct  = cell_temp.resample('ME').mean().values
m_pr  = m_ac / (KWP * m_poa)

months = ['1月','2月','3月','4月','5月','6月',
          '7月','8月','9月','10月','11月','12月']
for i, mo in enumerate(months):
    print(f"{mo}: AC={m_ac[i]:.0f}kWh | 电池温={m_ct[i]:.1f}°C | PR={m_pr[i]:.3f}")
```

输出结果：

| 月份 | AC发电量(kWh) | 电池温度(°C) | 月PR |
|------|-------------|------------|------|
| 1月  | 739         | 11.7       | 0.962 |
| 3月  | 819         | 20.2       | 0.924 |
| 6月  | 687         | 30.6       | **0.881** |
| 9月  | 730         | 21.2       | 0.925 |
| 12月 | 691         | 10.2       | **0.971** |

**结论**：6月电池温度 30.6°C，PR 跌到 88.1%；12月电池温度 10.2°C，PR 高达 97.1%。

温度系数 -0.424%/°C 的威力：从 25°C 到 30.6°C，效率下降约 2.4%。看似不多，但整个夏季积累下来损失相当可观。

---

## 四、最优倾角扫描

```python
def simulate_tilt(tilt):
    arr = Array(
        mount=FixedMount(tilt, 180),
        module_parameters=module,
        temperature_model_parameters=temp_params,
        modules_per_string=N_MOD, strings=1,
    )
    sys = PVSystem(arrays=[arr], inverter_parameters={'pdc0': KWP*1000, 'eta_inv_nom': 0.96})
    mc = ModelChain(sys, site, aoi_model='physical', spectral_model='no_loss')
    mc.run_model(weather)
    return float(mc.results.ac['p_mp'].clip(0).sum() / 1000)

base = simulate_tilt(30)
for tilt in [0, 15, 20, 25, 30, 35, 40, 45]:
    y = simulate_tilt(tilt)
    print(f"倾角 {tilt:2d}°: {y:.1f} kWh ({(y-base)/base*100:+.1f}%)")
```

```
倾角  0°: 7477.6 kWh (-14.0%)
倾角 15°: 8341.9 kWh  (-4.0%)
倾角 20°: 8516.2 kWh  (-2.0%)
倾角 25°: 8633.5 kWh  (-0.7%)
倾角 30°: 8694.0 kWh  (+0.0%)
倾角 35°: 8698.0 kWh  (+0.0%) ← 最优
倾角 40°: 8645.3 kWh  (-0.6%)
倾角 45°: 8535.7 kWh  (-1.8%)
```

上海（北纬 31.2°）最优倾角约 33-35°，但 25°~40° 之间差异不到 1%。实际工程中按屋顶结构选 30° 完全没问题，不必纠结精确角度。

---

## 五、完整损耗链

```
装机容量:       5.0 kWp
理论最大发电量: 8760h × 5kW = 43800 kWh（永不达到）
参考发电量:    9415 kWh  （按POA辐照理论满发）
DC 发电量:     9069 kWh  ← 温度损耗 (-3.8%)、AOI 损耗等
AC 发电量:     8694 kWh  ← 逆变器损耗 (-4.1%)
总损耗比例:    7.7%（PR = 92.3%）
```

---

## ⚠️ pvlib 0.15.0 常见陷阱

1. **`results.ac` 是 DataFrame**，不要直接 `.sum()`，要 `['p_mp'].clip(0).sum()`
2. **PR 公式分母**：`KWP × poa_kwh_m2`，不要再除以 1000（单位已匹配）
3. **PVSystem 新 API**：必须用 `Array(mount=FixedMount(...))` 传安装参数
4. **POA ≠ GHI**：PR 分母务必用 POA（面板倾斜平面）辐照量，否则结果偏高

---

## 知识卡片 🗂️

| 指标 | 公式 | 上海5kWp案例 |
|------|------|------------|
| **PR** | E_ac / (P_peak × H_POA) | **92.3%** |
| **比发电量** | E_ac / P_peak | **1739 kWh/kWp** |
| **容量因子** | E_ac / (P_peak × 8760) | **19.8%** |
| 最优倾角 | 约等于当地纬度 | **~35°**（差异<1%，选30°足够）|
| 夏季PR最低 | 高温 -0.424%/°C | 6月 88.1% |
| 冬季PR最高 | 低温高效 | 12月 97.1% |

**经验值（上海）**：5kWp 系统年发电量 ≈ **8500~9000 kWh**，比发电量 ≈ **1700~1800 kWh/kWp**。