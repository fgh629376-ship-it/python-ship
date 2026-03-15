---
title: 'pvlib ModelChain 源码精读：10步损耗链与自定义扩展实战'
description: '深入 pvlib ModelChain 的调用链原理，拆解 9 个可替换模型节点，实战自定义 losses_model 施加污渍/失配/线路损耗，揭示逆变器欠配截幅陷阱。'
category: solar
series: pvlib
lang: zh
pubDate: '2026-03-13'
tags: ["pvlib", "光伏", "ModelChain", "仿真", "技术干货"]
---

## 前言

pvlib 的 `ModelChain` 是整个仿真框架的调度引擎——它把十几个独立模型串成一条流水线，一行 `run_model()` 就搞定从气象数据到 AC 输出的全流程。

但很多人只会「跑通示例」，不清楚内部在干什么，也不知道怎么定制。本文把 ModelChain 拆开来看。

---

## 调用链全貌（pvlib 0.15）

ModelChain 内部的执行顺序，从 `_run_from_effective_irrad` 源码提炼：

```
transposition → aoi → spectral → effective_irradiance
    → temperature → dc → dc_ohmic → losses → ac
```

**9 个可替换的模型节点**，对应 ModelChain 的属性：

| 属性名 | 默认值 | 作用 |
|---|---|---|
| `transposition_model` | `haydavies` | GHI/DNI/DHI → POA |
| `aoi_model` | `sapm_aoi_loss` | 入射角修正 |
| `spectral_model` | `sapm_spectral_loss` | 光谱修正 |
| `temperature_model` | `sapm_temp` | 电池温度 |
| `dc_model` | `sapm` | DC 功率（I-V 曲线） |
| `dc_ohmic_model` | `no_dc_ohmic_loss` | 直流欧姆损耗 |
| `losses_model` | `no_extra_losses` | 自定义额外损耗 |
| `ac_model` | `sandia_inverter` | 逆变器 DC$\rightarrow$AC |

每个节点都可以替换——传字符串用内置模型，传函数实现完全自定义。

---

## 快速搭建标准仿真

```python
import pvlib
import pandas as pd
import numpy as np

# 地点：上海
location = pvlib.location.Location(
    latitude=31.2, longitude=121.5,
    tz='Asia/Shanghai', altitude=5, name='Shanghai'
)

# 组件（Sandia 数据库）
module_db = pvlib.pvsystem.retrieve_sam('SandiaMod')
module = module_db['Canadian_Solar_CS5P_220M___2009_']

# 逆变器（注意：容量要匹配！）
inverter_db = pvlib.pvsystem.retrieve_sam('SandiaInverter')
inverter = inverter_db['ABB__PVI_4_2_OUTD_S_US__208V_']  # 4.2kW

# 组件温度参数
temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
    'sapm']['open_rack_glass_glass']

# 构建系统（10串×2并 = 4.39kWp）
array = pvlib.pvsystem.Array(
    mount=pvlib.pvsystem.FixedMount(surface_tilt=30, surface_azimuth=180),
    module_parameters=module,
    temperature_model_parameters=temp_params,
    modules_per_string=10,
    strings=2
)
system = pvlib.pvsystem.PVSystem(arrays=[array], inverter_parameters=inverter)

# ModelChain
mc = pvlib.modelchain.ModelChain(
    system=system, location=location,
    aoi_model='sapm', spectral_model='sapm'
)

# 模拟气象数据（上海夏至日）
times = pd.date_range('2025-06-21', periods=24, freq='1h', tz='Asia/Shanghai')
weather = pd.DataFrame({
    'ghi': [0,0,0,0,0,0,20,120,350,580,780,920,950,890,750,560,350,150,30,0,0,0,0,0],
    'dhi': [0,0,0,0,0,0,15,80,180,250,290,310,300,280,250,200,140,80,20,0,0,0,0,0],
    'dni': [0,0,0,0,0,0,30,180,480,720,880,980,1000,950,820,650,450,200,40,0,0,0,0,0],
    'temp_air': [28.0]*24,
    'wind_speed': [2.5]*24,
}, index=times)

mc.run_model(weather)
print(f'日发电量: {mc.results.ac.clip(0).sum()/1000:.3f} kWh')
# → 日发电量: 27.072 kWh
```

---

## 中间结果：损耗链数据

ModelChain 不只输出最终 AC，所有中间步骤都记录在 `results`：

```python
poa    = mc.results.total_irrad['poa_global']  # 倾斜面辐照
eff    = mc.results.effective_irradiance        # 有效辐照（AOI+光谱修正后）
t_cell = mc.results.cell_temperature           # 电池温度
dc     = mc.results.dc                         # DC 功率 DataFrame
ac     = mc.results.ac                         # AC 输出

daytime = poa > 50
print(f'POA 均值:      {poa[daytime].mean():.1f} W/m²')   # 700.2
print(f'有效辐照均值:  {eff[daytime].mean():.1f} W/m²')   # 689.9
print(f'透过率:        {(eff[daytime]/poa[daytime]).mean():.4f}')  # 0.9727
print(f'电池温度均值:  {t_cell[daytime].mean():.1f}°C')   # 48.9°C
print(f'逆变器效率:    {(ac[daytime]/dc["p_mp"][daytime]).mean():.4f}')  # 0.9514
```

夏至日实测损耗链（28°C 环境，$700 \text{W/m}^2$ POA 均值）：

```
POA 700.2 W/m²
  → AOI+光谱: ×0.9727 → 有效辐照 689.9 W/m²  (-2.73%)
  → 温度效应: 48.9°C  → DC Pmpp 2567 W
  → 逆变器:   ×0.9514 → AC 输出 2458 W         (-4.86%)
  → 系统 PR ≈ 79.7%
```

---

## 三种运行入口

ModelChain 提供三个入口，跳过不同阶段：

```python
# 入口1：从 GHI/DNI/DHI 气象数据（最常用，完整链路）
mc.run_model(weather)

# 入口2：从倾斜面 POA 数据（跳过转置步骤）
# 适用：有倾斜面辐射仪，已知 POA 实测值
poa_weather = pd.DataFrame({
    'poa_global': ..., 'poa_direct': ..., 'poa_diffuse': ...,
    'temp_air': ..., 'wind_speed': ...
}, index=times)
mc.run_model_from_poa(poa_weather)

# 入口3：从有效辐照度（跳过转置+AOI+光谱）
# 适用：已外部计算好 AOI 和光谱修正
eff_weather = pd.DataFrame({
    'effective_irradiance': ...,
    'temp_air': ..., 'wind_speed': ...
}, index=times)
mc.run_model_from_effective_irradiance(eff_weather)
```

三种入口在相同数据下结果差异 <0.05%，选择依据是**数据从哪一步开始**。

---

## 自定义 losses_model：施加污渍/失配/线路损耗

losses_model 的调用时机：**dc_model 之后，ac_model 之前**——这是加载 DC 段系统损耗的正确位置。

### 正确写法

```python
def custom_dc_losses(mc_obj):
    """自定义损耗：污渍3% + 失配2% + 线路1%"""
    factor = (1 - 0.03) * (1 - 0.02) * (1 - 0.01)  # = 0.9412
    mc_obj.results.dc['p_mp'] *= factor
    mc_obj.results.dc['i_mp'] *= np.sqrt(factor)
    mc_obj.results.dc['v_mp'] *= np.sqrt(factor)

# ✅ 正确：直接赋值，pvlib 自动包装为 functools.partial
mc.losses_model = custom_dc_losses
mc.run_model(weather)

kWh_loss = mc.results.ac.clip(0).sum() / 1000
# 结果：25.484 kWh（实际损耗 5.87%，理论 5.89%，完美吻合）
```

### ⚠️ 三个坑

**坑1：losses_model 修改的是 results.dc，不是 results.ac**

损耗在 AC 计算之前施加。如果你试图修改 `mc_obj.results.ac`，此时它还是 `None`。

**坑2：逆变器欠配会让损耗「失效」**

如果系统是 4.39 kWp，逆变器只有 250W（容配比 17.6:1），AC 长期在 Paco 截幅。施加 5.89% DC 损耗后，AC 输出几乎不变（只差 0.18%）——因为截掉的是本来就会被限幅的那部分功率。**务必先检查容配比！**

```python
# 检查容配比
stc_power = module['Impo'] * module['Vmpo'] * n_modules
ratio = stc_power / inverter['Paco']
print(f'容配比: {ratio:.2f}x')  # 合理范围：1.0~1.3
```

**坑3：haydavies 转置模型需要 dni_extra**

```python
# ❌ 报错
poa = pvlib.irradiance.get_total_irradiance(..., model='haydavies')

# ✅ 正确
from pvlib.irradiance import get_extra_radiation
dni_extra = get_extra_radiation(times)
poa = pvlib.irradiance.get_total_irradiance(..., model='haydavies', dni_extra=dni_extra)
```

---

## 温度模型对比

同等条件下，SAPM 和 PVsyst 温度模型的差异：

```python
# SAPM 温度参数（开放支架，玻璃-玻璃封装）
temp_sapm = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
# PVsyst 温度参数（自由独立安装）
temp_pvs  = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['pvsyst']['freestanding']
```

夏至日 28°C 实测对比：

| 温度模型 | 电池温均值 | 日发电量 | 差异 |
|---|---|---|---|
| SAPM | 48.9°C | 27.072 kWh | 基准 |
| PVsyst | 47.6°C | 27.336 kWh | +0.97% |

PVsyst 模型温度稍低，发电量略高。两者都合理，选择取决于安装方式和厂商数据来源。

---

## 知识卡片

> **ModelChain = 乐高积木**
> 每个节点可以独立替换，其余保持默认。定制一个，其余八个免费继承。

**完整调用链**：
```
transposition → aoi → spectral → effective_irradiance
  → temperature → dc → dc_ohmic → losses → ac
```

**快速定制参考**：

| 定制目标 | 方法 |
|---|---|
| 系统损耗（污渍/失配/线路） | `mc.losses_model = my_func` |
| 温度模型 | 在 Array 里换 `temperature_model_parameters` |
| 逆变器模型 | `ModelChain(ac_model='pvwatts')` |
| 转置模型 | `ModelChain(transposition_model='perez')` |
| 自定义 DC | `mc.dc_model = my_dc_func` |

**losses_model 函数签名**：接受 `mc_obj`，修改 `mc_obj.results.dc`，无需返回值。记住这条流水线，你就知道在哪里插入自定义代码。