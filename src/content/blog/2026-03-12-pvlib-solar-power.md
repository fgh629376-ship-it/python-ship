---
title: 'pvlib-python 光伏功率预测完全指南'
description: '用 Python 做光伏发电量预测 — pvlib 库从入门到实战，涵盖物理建模链路、ModelChain、气象数据接入、ML混合方案'
category: solar
pubDate: '2026-03-12'
tags: ['pvlib', '光伏', '能源', '技术干货']
---

## pvlib 是什么？

**pvlib** 是光伏行业的 Python 物理建模标准库。注意：它**不是** ML 预测库，而是基于物理机制的确定性功率预测工具。

核心思路很简单：**给定地点 + 时间 + 气象数据 → 精确计算该时刻电站输出功率**。

```bash
pip install pvlib
# 最新版 v0.15.1（2026年3月）
```

---

## 光伏功率预测的物理链路

pvlib 把功率预测拆成 6 个物理步骤，每一步都有对应的模型：

```
太阳位置（高度角/方位角）
  ↓
晴空辐照度（GHI / DNI / DHI）
  ↓
斜面辐照度（POA — 倾斜面实际接收的辐照）
  ↓
有效辐照度（考虑 AOI 损失 + 光谱修正）
  ↓
组件温度（影响 5-10% 的发电效率）
  ↓
DC 功率 → AC 功率（经逆变器）→ 最终输出
```

理解这条链路，是用好 pvlib 的关键。

---

## 核心模块速查

| 模块 | 职责 | 关键函数 |
|------|------|----------|
| `solarposition` | 太阳高度角/方位角 | `get_solarposition()` |
| `clearsky` | 晴空辐照度模型 | `ineichen()`, `haurwitz()` |
| `irradiance` | 辐照度分解/转换 | `get_total_irradiance()`, `perez()` |
| `temperature` | 组件/电池温度 | `sapm_cell()`, `faiman()` |
| `pvsystem` | DC/AC 功率计算 | `pvwatts_dc()`, `singlediode()` |
| `modelchain` | **全链路封装** | `ModelChain.run_model()` |
| `iotools` | 气象数据接入 | Solcast / ERA5 / NASA Power |

---

## ModelChain — 一站式功率预测

ModelChain 是最高层封装，把 6 步全串起来。只需定义地点、系统参数、喂入气象数据：

```python
import pvlib
import pandas as pd

# 1. 定义地点（上海）
location = pvlib.location.Location(
    latitude=31.2,
    longitude=121.5,
    altitude=10,
    tz='Asia/Shanghai'
)

# 2. 定义光伏系统
module_params = dict(pdc0=10000, gamma_pdc=-0.004)  # 10kW，温度系数-0.4%/℃
inverter_params = dict(pdc0=9500)
temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
    'sapm']['open_rack_glass_glass'
]

system = pvlib.pvsystem.PVSystem(
    surface_tilt=30,        # 倾角 30°
    surface_azimuth=180,    # 正南朝向
    module_parameters=module_params,
    inverter_parameters=inverter_params,
    temperature_model_parameters=temp_params,
    modules_per_string=20,
    strings_per_inverter=2,
)

# 3. 建立 ModelChain
mc = pvlib.modelchain.ModelChain(
    system, location,
    dc_model='pvwatts',
    ac_model='pvwatts',
    aoi_model='physical',
    spectral_model='no_loss',
    temperature_model='sapm',
)

# 4. 准备气象数据（必须含 ghi/dhi/dni）
times = pd.date_range('2026-06-01', '2026-06-07', freq='1h', tz='Asia/Shanghai')
weather = location.get_clearsky(times)  # 晴空假设
weather['temp_air'] = 25
weather['wind_speed'] = 2

# 5. 运行！
mc.run_model(weather)

# 6. 拿结果
ac_power = mc.results.ac  # W，交流功率时序
dc_power = mc.results.dc  # W，直流功率
```

---

## 三种预测场景

### 场景 1：晴空基准预测

晴空 = 无云时的理论最大辐照，常用来做基准线：

```python
clearsky = location.get_clearsky(times, model='ineichen')
# 输出 ghi/dni/dhi
# 实际功率 / 晴空功率 = 晴空指数（0~1）
```

### 场景 2：接入 NWP 气象预报

短期预测最常用的方式，从第三方获取预报数据直接喂模型：

```python
from pvlib.iotools import get_solcast_forecast

df, meta = get_solcast_forecast(
    latitude=31.2,
    longitude=121.5,
    api_key='your_key',
    hours=48,
)
# df 包含 ghi/dni/dhi/temp_air/wind_speed
mc.run_model(df)
```

### 场景 3：已有倾斜面辐照仪

现场有传感器？数据更准，直接用：

```python
mc.run_model_from_poa(poa_data)
# poa_data 需包含 poa_global / poa_direct / poa_diffuse
```

---

## 模型选择指南

### 辐照度转换（GHI → 斜面 POA）

- **`perez`** — 精度最高，默认推荐
- **`haydavies`** — 大多数情况够用
- **`isotropic`** — 快速估算用

### DC 功率模型

- **`pvwatts`** — 只需 `pdc0 + gamma_pdc`，数据少时首选
- **`sapm`** — 需完整 Sandia 参数，精确仿真
- **`singlediode`** — 需 5 参数，最精确

### 温度模型

```python
# SAPM（最常用）
pvlib.temperature.sapm_cell(poa_global, temp_air, wind_speed, a, b, deltaT)

# Faiman（简单线性，效果好）
pvlib.temperature.faiman(poa_global, temp_air, wind_speed, u0=25, u1=6.84)
```

---

## 损耗模型（PVWatts）

实际发电量总比理论值低，pvlib 把各种损耗都考虑到了：

```python
losses = pvlib.pvsystem.pvwatts_losses(
    soiling=2,          # 灰尘 2%
    shading=3,          # 遮挡 3%
    mismatch=2,         # 失配 2%
    wiring=2,           # 线损 2%
    connections=0.5,    # 接头 0.5%
    lid=1.5,            # LID 1.5%
    nameplate_rating=1, # 铭牌误差 1%
    availability=3,     # 可用率 3%
)
# 总损耗约 14.1%
```

---

## pvlib + ML = 业界最佳实践

纯物理模型有天花板，纯 ML 缺乏物理约束。结合起来才是主流：

```
步骤：
1. pvlib 跑出物理基准预测值 P_phys
2. 计算残差：residual = P_actual - P_phys
3. 用 XGBoost / LSTM 学习残差
   输入特征：云量指数、NWP 偏差、历史残差
4. 最终预测：P_final = P_phys + residual_pred
```

物理约束保证预测值合理，ML 修正天气预报带来的误差。

---

## 气象数据来源

| 数据源 | 特点 | 价格 |
|--------|------|------|
| **Solcast** | 最准，支持预报 | 商业 |
| **ERA5** | ECMWF 再分析，全球 | 免费 |
| **NASA Power** | 全球覆盖 | 免费 |
| **PVGIS** | 欧盟维护 | 免费 |

---

## 知识卡片 📌

```
pvlib 核心定位：
  物理建模引擎，不是黑盒 ML

6 步预测链路：
  太阳位置 → 晴空辐照 → 斜面辐照 → 有效辐照 → 组件温度 → 功率

最快上手：
  ModelChain.run_model(weather_dataframe)

实战公式：
  pvlib 物理基准 + ML 残差修正 = 最优方案
```
