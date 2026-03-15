---
title: 'pvlib 实战：晴空模型 — 光伏预测的基石'
description: '晴空模型是光伏预测最重要的单一工具。本文用 pvlib 实战对比 Ineichen、Haurwitz、Simplified Solis 三大模型，理解晴空指数 κ 的物理意义与工程应用。'
pubDate: 2026-03-15
lang: zh
category: solar
series: pvlib
tags: ['pvlib', '晴空模型', '光伏预测', 'Clear Sky', 'Ineichen', '晴空指数']
---

## 为什么晴空模型是光伏预测的基石？

GEFCom2014（全球能源预测竞赛）的一个关键事实：**唯一使用晴空模型的团队 = 冠军**。所有其他团队的预测 "黯然失色"。

晴空模型告诉你：**如果今天万里无云，地面应该收到多少太阳辐照度**。有了这个基准，预测问题就从 "明天 GHI 是多少" 简化为 "明天云会遮挡多少"——后者是一个更小、更容易建模的问题。

核心公式：

$$\kappa = \frac{\text{GHI}}{\text{GHI}_{\text{clear}}}$$

晴空指数 $\kappa$ 去除了太阳位置的季节性和日周期，让预测模型只需要关注天气变化。

---

## pvlib 中的三大晴空模型

pvlib 提供三种晴空模型，复杂度和精度递增：

| 模型 | 输入参数 | 精度 | 适用场景 |
|------|----------|------|----------|
| **Haurwitz** | 仅天顶角 | ⭐⭐ | 快速估算、教学 |
| **Simplified Solis** | 天顶角 + 气溶胶 + 水汽 + 气压 | ⭐⭐⭐ | 中等精度需求 |
| **Ineichen-Perez** | 天顶角 + Linke 浑浊度 | ⭐⭐⭐⭐ | 运营预测（推荐） |

---

## 完整代码实战

### 1. 基础设置

```python
import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 上海站点
latitude, longitude = 31.23, 121.47
altitude = 4  # 海拔(m)

# 2024年夏至日
times = pd.date_range(
    '2024-06-21 00:00', '2024-06-21 23:59',
    freq='1min', tz='Asia/Shanghai'
)

# 计算太阳位置
location = pvlib.location.Location(latitude, longitude, altitude=altitude)
solar_position = location.get_solarposition(times)
```

### 2. 三种晴空模型对比

```python
# === Haurwitz（最简单，只需天顶角）===
cs_haurwitz = location.get_clearsky(times, model='haurwitz')

# === Ineichen-Perez（推荐，需要 Linke 浑浊度）===
# pvlib 自动从 SoDa 数据库获取月均 Linke 浑浊度
cs_ineichen = location.get_clearsky(times, model='ineichen')

# === Simplified Solis（需要气溶胶光学深度）===
cs_solis = location.get_clearsky(
    times, model='simplified_solis',
    aod700=0.1,          # 700nm 气溶胶光学深度
    precipitable_water=2.0,  # 可降水量(cm)
    pressure=101325      # 气压(Pa)
)
```

### 3. 可视化对比

```python
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

components = ['ghi', 'dni', 'dhi']
titles = ['GHI (全球水平辐照度)', 'DNI (直射法向辐照度)', 'DHI (散射水平辐照度)']

for ax, comp, title in zip(axes, components, titles):
    ax.plot(cs_haurwitz.index, cs_haurwitz[comp],
            label='Haurwitz', linewidth=1.5, linestyle='--')
    ax.plot(cs_ineichen.index, cs_ineichen[comp],
            label='Ineichen-Perez', linewidth=2)
    ax.plot(cs_solis.index, cs_solis[comp],
            label='Simplified Solis', linewidth=1.5, linestyle='-.')
    ax.set_ylabel(f'{title} (W/m²)')
    ax.legend()
    ax.grid(alpha=0.3)

axes[-1].set_xlabel('时间 (上海, 2024-06-21)')
plt.suptitle('三大晴空模型对比 — 上海夏至日', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('clearsky_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 4. 晴空指数 κ 的计算与应用

```python
# 模拟一天的实际辐照度（加入云的影响）
np.random.seed(42)
cloud_factor = np.ones(len(times))

# 模拟上午晴天、午后多云的场景
for i, t in enumerate(times):
    hour = t.hour + t.minute / 60
    if 12 < hour < 16:
        # 午后云遮挡
        cloud_factor[i] = 0.3 + 0.4 * np.random.random()
    elif 10 < hour < 12:
        # 上午间歇性云
        cloud_factor[i] = 0.7 + 0.3 * np.random.random()

# 实际 GHI = 晴空 GHI × 云因子
ghi_actual = cs_ineichen['ghi'] * cloud_factor

# 计算晴空指数 κ
kappa = ghi_actual / cs_ineichen['ghi'].replace(0, np.nan)

# 可视化
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

ax1.plot(times, cs_ineichen['ghi'], label='晴空 GHI', color='orange', linewidth=2)
ax1.plot(times, ghi_actual, label='实际 GHI', color='steelblue', alpha=0.8)
ax1.fill_between(times, ghi_actual, cs_ineichen['ghi'],
                  alpha=0.2, color='red', label='云遮挡损失')
ax1.set_ylabel('GHI (W/m²)')
ax1.legend()
ax1.set_title('晴空模型 vs 实际辐照度')

ax2.plot(times, kappa, color='green', linewidth=1)
ax2.axhline(y=1.0, color='orange', linestyle='--', alpha=0.5, label='κ=1 (完美晴天)')
ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='κ=0.5 (半阴)')
ax2.set_ylabel('晴空指数 κ')
ax2.set_xlabel('时间')
ax2.set_ylim(0, 1.3)
ax2.legend()
ax2.set_title('晴空指数 κ = GHI / GHI_clear')

plt.tight_layout()
plt.savefig('clearsky_index.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 5. Linke 浑浊度的影响

```python
# Linke 浑浊度：大气透明度指标
# 值越大 → 大气越浑浊 → 晴空辐照度越低
linke_values = [2.0, 3.5, 5.0, 7.0]
labels = ['极清洁 (TL=2)', '典型 (TL=3.5)', '污染 (TL=5)', '重度污染 (TL=7)']

fig, ax = plt.subplots(figsize=(12, 5))

for tl, label in zip(linke_values, labels):
    cs = pvlib.clearsky.ineichen(
        solar_position['apparent_zenith'],
        airmass_absolute=location.get_airmass(times)['airmass_absolute'],
        linke_turbidity=tl,
        altitude=altitude
    )
    ax.plot(times, cs['ghi'], label=label, linewidth=2)

ax.set_ylabel('GHI (W/m²)')
ax.set_xlabel('时间')
ax.set_title('Linke 浑浊度对晴空 GHI 的影响')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('linke_turbidity.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 6. 多站点晴空比较

```python
# 不同气候区的晴空模型差异
sites = {
    '上海 (湿润亚热带)': (31.23, 121.47, 4),
    '敦煌 (干旱沙漠)': (40.14, 94.68, 1139),
    '拉萨 (高原)': (29.65, 91.10, 3650),
}

fig, ax = plt.subplots(figsize=(12, 5))

for name, (lat, lon, alt) in sites.items():
    loc = pvlib.location.Location(lat, lon, altitude=alt)
    cs = loc.get_clearsky(times, model='ineichen')
    ax.plot(times, cs['ghi'], label=name, linewidth=2)

ax.set_ylabel('GHI (W/m²)')
ax.set_xlabel('时间 (2024-06-21)')
ax.set_title('不同站点的晴空 GHI 对比')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('multi_site_clearsky.png', dpi=150, bbox_inches='tight')
plt.show()
```

---

## 晴空模型选择指南

> **教材结论（Yang & Kleissl, Ch5.4）**：不同晴空模型之间的性能差异，**远小于**不同站点之间的差异。晴空模型的选择只有边际重要性。

实际建议：

1. **运营预测** → **Ineichen-Perez**（不受时间限制，几行代码搞定）
2. **研究验证** → **REST2**（需要 MERRA-2 气溶胶数据，精度最高）
3. **快速原型** → **Haurwitz**（零外生参数，但不输出 DNI/DHI）

---

## 关键认识

- $\kappa$ 分布通常**双峰**：晴天峰 $\approx 1.0$，阴天峰 $\approx 0.3$–$0.5$
- **乘法分解**（$\kappa = \text{GHI}/\text{GHI}_{\text{clear}}$）优于加法分解
- $\kappa > 1$ 是合法的！**云增强效应**可使瞬时 GHI 超过晴空值约 50%
- 晴空指数不是 GHI 专属——可以定义 $\kappa_{\text{BNI}}, \kappa_{\text{POA}}, \kappa_{\text{PV}}$
- 用 $\kappa$ 做预测**必须先做晴空归一化**，否则模型在学太阳升落而非天气变化

---

## 参考文献

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and PV Power Forecasting*, Ch4.5 & Ch5.4. CRC Press.
- Ineichen, P. & Perez, R. (2002). A new airmass independent formulation for the Linke turbidity coefficient. *Solar Energy*, 73(3), 151-157.
- Sun, X. et al. (2019). Worldwide performance assessment of 75 global clear-sky irradiance models. *Solar Energy*, 187, 392-404.
- Gueymard, C.A. (2008). REST2: High-performance solar radiation model. *Solar Energy*, 82(3), 272-285.
