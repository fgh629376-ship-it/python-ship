---
title: 'pvlib 太阳位置与辐照度分解 — 光伏预测的物理基石'
description: '深入理解 pvlib 太阳位置计算(SPA)和辐照度分解(GHI→DNI/DHI→POA)，附完整代码演示'
category: solar
lang: zh
pubDate: '2026-03-13'
tags: ["pvlib", "光伏", "辐照度", "技术干货"]
---

## 为什么太阳位置和辐照度是光伏预测的根基？

光伏面板的发电量取决于两个物理量：**太阳照到面板上的能量有多少**（POA 辐照度），以及**组件在这个条件下的电气响应**。

整个链路的第一步，就是算清楚：太阳在天空的哪个位置、有多少辐射能到达面板。

---

## 一、太阳位置计算

### 核心概念

- **天顶角 (zenith)**：太阳与正上方的夹角。0° = 头顶正上方，90° = 地平线
- **方位角 (azimuth)**：太阳的水平方向。0° = 正北，90° = 正东，180° = 正南
- **高度角 (elevation)**：= 90° - zenith
- **视天顶角 (apparent_zenith)**：经大气折射修正后的天顶角

### pvlib 实现

pvlib 默认使用 **NREL SPA 算法**（Solar Position Algorithm），精度达到 ±0.0003°，这是行业金标准。

```python
import pvlib
import pandas as pd

# 定义地点
location = pvlib.location.Location(
    latitude=31.23, longitude=121.47,
    tz="Asia/Shanghai", altitude=5, name="上海"
)

# 时间序列
times = pd.date_range(
    "2024-06-21 04:00", periods=48,
    freq="30min", tz="Asia/Shanghai"
)

# 计算太阳位置
solpos = location.get_solarposition(times)
print(solpos[["zenith", "azimuth", "apparent_elevation"]].head(10))
```

**关键输出列：**
| 列名 | 含义 | 单位 |
|------|------|------|
| `zenith` | 天顶角 | ° |
| `apparent_zenith` | 视天顶角（含折射） | ° |
| `azimuth` | 方位角 | ° |
| `apparent_elevation` | 视高度角 | ° |
| `equation_of_time` | 时差方程 | 分钟 |

### 日出日落判断

```python
# zenith > 90° 即为夜间
is_daytime = solpos["zenith"] < 90
sunrise = solpos[is_daytime].index[0]
sunset = solpos[is_daytime].index[-1]
print(f"日出: {sunrise}, 日落: {sunset}")
```

---

## 二、辐照度基础概念

太阳辐射到达地面时分为三个分量：

| 分量 | 英文缩写 | 含义 |
|------|---------|------|
| **总水平辐照度** | GHI | 水平面接收的总辐射 |
| **直接法向辐照度** | DNI | 垂直于太阳方向的直射辐射 |
| **散射水平辐照度** | DHI | 水平面接收的散射辐射（天空散射） |

**基本关系：**
```
GHI = DNI × cos(zenith) + DHI
```

气象站通常只测 GHI，需要用模型分解出 DNI 和 DHI。

---

## 三、辐照度分解模型

当你只有 GHI 数据时，需要把它拆成 DNI + DHI：

### DISC 模型
```python
# GHI → DNI
dni_disc = pvlib.irradiance.disc(
    ghi=clearsky["ghi"],
    solar_zenith=solpos["zenith"],
    datetime_or_doy=times
)
print(dni_disc.head())
```

### DIRINT 模型（更精确）
```python
# GHI → DNI（考虑更多大气变量）
dni_dirint = pvlib.irradiance.dirint(
    ghi=clearsky["ghi"],
    solar_zenith=solpos["zenith"],
    times=times
)
```

### Erbs 分解
```python
# GHI → DNI + DHI（经典模型）
from pvlib.irradiance import clearness_index

# 先算晴空指数 kt
kt = clearness_index(
    ghi=measured_ghi,
    solar_zenith=solpos["zenith"],
    extra_radiation=pvlib.irradiance.get_extra_radiation(times)
)
```

---

## 四、水平辐照度 → 面板辐照度 (POA)

面板不是水平放的，需要把 GHI/DNI/DHI 转换到面板倾斜面上的辐照度（POA = Plane of Array）。

### 转换过程

```python
# 1. 大气外辐射（Perez 模型需要）
dni_extra = pvlib.irradiance.get_extra_radiation(times)

# 2. 面板参数
surface_tilt = 31.23    # 倾角（通常 ≈ 纬度）
surface_azimuth = 180   # 朝南

# 3. 计算 POA
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"],
    dni=clearsky["dni"],
    ghi=clearsky["ghi"],
    dhi=clearsky["dhi"],
    dni_extra=dni_extra,
    model="perez"  # 推荐 Perez 散射模型
)
print(poa[["poa_global", "poa_direct", "poa_diffuse"]].head())
```

### POA 输出分量

| 分量 | 含义 |
|------|------|
| `poa_global` | 面板总辐照度 |
| `poa_direct` | 面板上的直射分量 |
| `poa_diffuse` | 面板上的散射分量（天空 + 地面反射） |
| `poa_sky_diffuse` | 天空散射 |
| `poa_ground_diffuse` | 地面反射散射 |

### 散射模型对比

pvlib 提供多种散射模型：

| 模型 | 函数 | 精度 | 适用场景 |
|------|------|------|---------|
| **Perez** | `pvlib.irradiance.perez()` | ⭐⭐⭐⭐⭐ | 通用首选 |
| **Hay-Davies** | `pvlib.irradiance.haydavies()` | ⭐⭐⭐⭐ | 计算量小 |
| **Reindl** | `pvlib.irradiance.reindl()` | ⭐⭐⭐⭐ | 折中方案 |
| **Klucher** | `pvlib.irradiance.klucher()` | ⭐⭐⭐ | 多云环境 |
| **Isotropic** | `pvlib.irradiance.isotropic()` | ⭐⭐ | 最简单 |

**工业界首选 Perez 模型**，精度最高，需要额外传入 `dni_extra`（大气外辐射）。

---

## 五、入射角 (AOI) 计算

太阳光不是垂直打到面板上的，入射角影响反射损失：

```python
aoi = pvlib.irradiance.aoi(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"]
)
print(f"正午入射角: {aoi.iloc[len(aoi)//2]:.1f}°")
```

AOI 越大，反射损失越大。pvlib 提供多种 IAM（入射角修正）模型：

```python
# 物理 IAM 模型
iam_loss = pvlib.iam.physical(aoi, n=1.526, K=4.0, L=0.002)
# 返回 0~1 之间的透射率系数
```

---

## 六、晴空模型

没有实测数据时，用晴空模型估算理想辐照度：

```python
# Ineichen 晴空模型（默认）
clearsky = location.get_clearsky(times, model="ineichen")

# 输出 GHI、DNI、DHI
print(clearsky.columns)  # ghi, dni, dhi
```

pvlib 支持的晴空模型：
- **Ineichen-Perez**（默认）— 最常用
- **Haurwitz** — 简单，只输出 GHI
- **Simplified Solis** — 支持气溶胶光学厚度

---

## 七、完整示例：从位置到 POA 全链路

```python
import pvlib
import pandas as pd

# 地点：上海
loc = pvlib.location.Location(31.23, 121.47, "Asia/Shanghai", 5)
times = pd.date_range("2024-06-21", periods=48, freq="30min", tz="Asia/Shanghai")

# 太阳位置
solpos = loc.get_solarposition(times)

# 晴空辐照度
cs = loc.get_clearsky(times)

# 大气外辐射
dni_extra = pvlib.irradiance.get_extra_radiation(times)

# 面板 POA（倾角=纬度，朝南）
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=31.23, surface_azimuth=180,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"],
    dni=cs["dni"], ghi=cs["ghi"], dhi=cs["dhi"],
    dni_extra=dni_extra, model="perez"
)

# 打印正午结果
noon = poa.between_time("11:30", "12:30")
print("正午 POA 辐照度 (W/m²):")
print(noon[["poa_global", "poa_direct", "poa_diffuse"]].round(1))

# 日辐照量 (kWh/m²)
daily_irradiation = poa["poa_global"].sum() * 0.5 / 1000  # 30分钟间隔
print(f"\n日辐照量: {daily_irradiation:.2f} kWh/m²")
```

---

## 知识卡片 📋

| 知识点 | 要点 |
|-------|------|
| **太阳位置** | pvlib 用 SPA 算法，精度 ±0.0003°，输出 zenith/azimuth |
| **辐照度三兄弟** | GHI = DNI×cos(z) + DHI，气象站测 GHI，需要模型分解 |
| **分解模型** | DISC、DIRINT — 从 GHI 拆出 DNI |
| **POA 转换** | 水平面辐照度 → 面板倾斜面辐照度，首选 Perez 模型 |
| **入射角 AOI** | 影响反射损失，IAM 模型修正 |
| **晴空模型** | 无实测数据时的理想辐照度估计 |

> **下一篇预告：** pvlib 组件温度模型与 DC 功率计算 — 从辐照度到瓦特的转换