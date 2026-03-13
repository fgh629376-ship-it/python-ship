---
title: 'pvlib 温度模型与 DC 功率计算 — 从辐照度到瓦特'
description: '深入理解 pvlib 电池温度模型(SAPM/PVsyst/Faiman)和 DC 功率模型(SAPM/CEC/PVWatts)，含完整代码对比'
category: solar
series: pvlib
lang: zh
pubDate: '2026-03-13'
tags: ["pvlib", "光伏", "温度模型", "DC功率", "技术干货"]
---

## 辐照度到了面板上，下一步是什么？

上一篇我们算清楚了 POA 辐照度。但辐照度不等于功率 — 中间还隔着两个关键步骤：**组件温度计算**和**电气模型转换**。

温度越高，组件效率越低。这不是小事 — 夏天高温可以让发电量掉 10% 以上。

---

## 一、为什么温度如此重要？

硅基光伏组件的温度系数一般在 **-0.3% ~ -0.5% /°C**。

- STC 标准条件：电池温度 25°C
- 实际运行：夏天正午电池温度可达 **60-70°C**
- 温升 40°C × (-0.4%/°C) = **发电量下降 16%**

这就是为什么 pvlib 有 4 种温度模型 — 算准温度，预测才准。

---

## 二、四种温度模型对比

### SAPM 模型（Sandia）

业界最常用的经验模型：

```python
import pvlib

# 参数集
params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]
print("可用参数集:", list(params.keys()))
# open_rack_glass_glass, close_mount_glass_glass,
# open_rack_glass_polymer, insulated_back_glass_polymer

# 计算电池温度
temp_params = params["open_rack_glass_glass"]
t_cell = pvlib.temperature.sapm_cell(
    poa_global=1000,   # W/m²
    temp_air=32,       # °C
    wind_speed=1.5,    # m/s
    **temp_params       # a, b, deltaT
)
print(f"SAPM 电池温度: {t_cell:.1f}°C")  # ≈63.6°C
```

**参数含义：**
- `a`, `b`：经验系数，描述 POA 和风速对组件背板温度的影响
- `deltaT`：电池与背板的温差

### PVsyst 模型

基于热平衡的物理模型：

```python
t_pvsyst = pvlib.temperature.pvsyst_cell(
    poa_global=1000,
    temp_air=32,
    wind_speed=1.5,
    u_c=29.0,   # 恒定热损失系数 W/(m²·K)
    u_v=0.0     # 风速相关热损失系数
)
print(f"PVsyst 电池温度: {t_pvsyst:.1f}°C")  # ≈60.1°C
```

### Faiman 模型

简化热平衡，两个参数：

```python
t_faiman = pvlib.temperature.faiman(
    poa_global=1000,
    temp_air=32,
    wind_speed=1.5,
    u0=25.0,    # 恒定散热系数
    u1=6.84     # 风速散热系数
)
print(f"Faiman 电池温度: {t_faiman:.1f}°C")  # ≈60.5°C
```

### Ross 模型

最简单的线性模型：

```python
t_ross = pvlib.temperature.ross(
    poa_global=1000,
    temp_air=32,
    noct=45      # NOCT 标称工作温度
)
print(f"Ross 电池温度: {t_ross:.1f}°C")  # ≈63.4°C
```

### 模型对比总结

| 模型 | 参数数 | 精度 | 计算量 | 适用场景 |
|------|--------|------|--------|---------|
| **SAPM** | 3 | ⭐⭐⭐⭐ | 低 | 通用首选 |
| **PVsyst** | 2 | ⭐⭐⭐⭐ | 低 | PVsyst 用户 |
| **Faiman** | 2 | ⭐⭐⭐⭐ | 最低 | 快速估算 |
| **Ross** | 1 | ⭐⭐⭐ | 最低 | NOCT 已知时 |
| **Fuentes** | 多 | ⭐⭐⭐⭐⭐ | 高 | 高精度需求 |

---

## 三、DC 功率模型

温度算出来了，接下来把辐照度 + 温度转换成直流功率。

### SAPM 模型（最精确）

需要 Sandia 数据库的 14+ 参数。523 个组件可选。

### CEC/单二极管模型（工程标准）

用 5 个电气参数求解单二极管方程：

```python
cec_modules = pvlib.pvsystem.retrieve_sam("CECMod")
module = cec_modules["Canadian_Solar_Inc__CS5P_220M"]

# 计算五参数（随工况变化）
IL, I0, Rs, Rsh, nNsVt = pvlib.pvsystem.calcparams_cec(
    effective_irradiance=1000,
    temp_cell=50,
    alpha_sc=module["alpha_sc"],
    a_ref=module["a_ref"],
    I_L_ref=module["I_L_ref"],
    I_o_ref=module["I_o_ref"],
    R_sh_ref=module["R_sh_ref"],
    R_s=module["R_s"],
    Adjust=module["Adjust"]
)

# 求解 I-V 特性
result = pvlib.pvsystem.singlediode(IL, I0, Rs, Rsh, nNsVt)
print(f"Pmpp: {result['p_mp']:.1f} W")
print(f"Voc:  {result['v_oc']:.2f} V")
print(f"Isc:  {result['i_sc']:.3f} A")
```

### PVWatts 模型（快速估算）

只需两个参数：

```python
dc_power = pvlib.pvsystem.pvwatts_dc(
    g_poa_effective=1000,   # 有效 POA W/m²
    temp_cell=50,           # 电池温度 °C
    pdc0=220,               # STC 额定功率 W
    gamma_pdc=-0.004        # 温度系数 1/°C
)
print(f"PVWatts DC 功率: {dc_power:.1f} W")
# 220 * (1000/1000) * (1 + (-0.004) * (50-25)) = 198 W
```

### 不同工况实测对比

| 工况 | POA | Tc | Pmpp | FF |
|------|-----|-----|------|-----|
| STC标准 | 1000 | 25°C | 220.0W | 0.726 |
| 阴天 | 800 | 25°C | 177.6W | 0.740 |
| 高温 | 1000 | 50°C | 193.0W | 0.695 |
| 冬天低辐照 | 500 | 15°C | 117.0W | 0.770 |
| 黎明黄昏 | 200 | 10°C | 47.2W | 0.792 |

---

## 四、关键洞察

1. **填充因子 FF 随温度上升而下降**：高温时内阻增大，FF 从 0.77 降到 0.70
2. **低辐照下 FF 反而更高**：电流小，电阻损耗比例小
3. **PVWatts 和 CEC 年发电量差异约 10-15%**：CEC 更精确，工程项目推荐 CEC

---

## 知识卡片 📋

| 知识点 | 要点 |
|-------|------|
| **温度影响** | -0.4%/°C，夏天可降 10-16% 发电量 |
| **温度模型** | SAPM 通用首选，PVsyst/Faiman 简化替代 |
| **DC 模型** | SAPM(14参数) > CEC(6参数) > PVWatts(2参数) |
| **单二极管** | IL/I0/Rs/Rsh/nNsVt 五参数，随工况动态变化 |
| **填充因子** | 0.70-0.79，温度升高则FF下降效率降低 |
| **CEC 数据库** | 21535 个组件参数，工程级选择 |

> **下一篇预告：** pvlib 逆变器模型 - Sandia/ADR/PVWatts 三大模型对比实战