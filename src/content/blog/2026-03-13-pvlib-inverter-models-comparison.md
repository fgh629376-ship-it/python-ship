---
title: 'pvlib 逆变器模型深度对比：Sandia vs ADR vs PVWatts'
description: '三大逆变器模型的参数体系、效率曲线、电压敏感性全面对比，含真实数据库调用代码，助你在光伏仿真中选对模型'
pubDate: '2026-03-13'
tags: ["pvlib", "光伏", "逆变器", "技术干货", "仿真"]
---

pvlib 提供了三种主流的逆变器模型：**Sandia**、**ADR（Anton Driesse）** 和 **PVWatts**。选错模型可能让你的年发电量预测偏差超过 2%——这篇文章用真实代码把它们摸透。

## 为什么逆变器模型很重要？

逆变器的效率不是常数，它随功率和电压变化。一台标称 96% 效率的逆变器，在 10% 负载时可能只有 92%，在过载时更是断崖式下降。错误的模型会让你的系统仿真产生系统性偏差。

## 三大模型速览

| 特性 | Sandia | ADR | PVWatts |
|------|--------|-----|---------|
| 参数来源 | 实测拟合 | 物理+拟合 | 简化经验 |
| 电压敏感性 | ✅ 有 | ✅ 有 | ❌ 无 |
| 数据库 | `SandiaInverter` | `ADRInverter` | 无需数据库 |
| 精度 | 高 | 高 | 中 |
| 适用场景 | 详细仿真 | 研究级 | 快速估算 |

## 代码实战

### 加载数据库

```python
import pvlib
import numpy as np

# Sandia 数据库（包含全球主流逆变器）
inv_db = pvlib.pvsystem.retrieve_sam('SandiaInverter')
sandia_params = inv_db['SMA_America__SB5000TL_US_22__208V_']

# ADR 数据库
adr_db = pvlib.pvsystem.retrieve_sam('ADRInverter')
adr_params = adr_db['Ablerex_Electronics_Co___Ltd___ES_5000_US_240__240_Vac__240V__CEC_2011_']

print("Sandia 额定功率:", sandia_params['Paco'], "W")
print("ADR 额定功率:", adr_params['Pacmax'], "W")
# 输出:
# Sandia 额定功率: 4580.0 W
# ADR 额定功率: 5240.0 W
```

### Sandia 模型调用

```python
# 参数：v_dc（直流电压）, p_dc（直流功率）, 参数字典
pdc_arr = np.linspace(50, 5500, 200)
v_nom = 400.0  # 工作电压

ac_sandia = pvlib.inverter.sandia(v_nom, pdc_arr, sandia_params)
# 超过 Paco 自动限幅，返回 NaN 或 Paco
```

**关键参数解读：**
- `Paco`：AC 额定上限（限幅点）
- `Pdco`：对应额定 AC 输出时的 DC 功率
- `Vdco`：对应最高效率的 DC 电压
- `C0~C3`：效率曲线的 4 个拟合系数
- `Pso`：自消耗门限（低于此 DC 功率，AC 输出为 0）

### PVWatts 模型调用

```python
# 最简单：只需额定功率和效率
pdc0 = 5000  # 额定 DC 功率 [W]
eta_nom = 0.96  # 额定效率

ac_pvwatts = pvlib.inverter.pvwatts(pdc_arr, pdc0, eta_nom)
# 超出 pdc0 * 1.1 时限幅
```

PVWatts 内部使用分段多项式效率曲线，**不依赖电压**，一个参数搞定。

### ADR 模型调用

```python
# ADR 参数来自 ADRInverter 数据库
# 注意：v0.15.0 中 ADR 不支持数组输入，需要标量循环
ac_adr = np.array([
    pvlib.inverter.adr(v_nom, float(p), adr_params)
    for p in pdc_arr
])
```

ADR 使用 9 个系数的二维多项式，同时描述功率和电压对效率的影响，是三个模型中物理意义最明确的。

## 效率曲线实测对比

```python
eff_sandia  = ac_sandia  / pdc_arr * 100
eff_pvwatts = ac_pvwatts / pdc_arr * 100
eff_adr     = ac_adr     / pdc_arr * 100
```

| DC 功率 | 额定比例 | Sandia | PVWatts | ADR |
|---------|---------|--------|---------|-----|
| 296 W | 5% | 92.25% | 88.19% | 87.36% |
| 543 W | 10% | 94.99% | 92.61% | 92.27% |
| 1036 W | 20% | 96.43% | 95.03% | 94.91% |
| 2515 W | 50% | **96.92%** | 96.22% | 96.07% |
| 3747 W | 75% | 96.70% | 96.21% | 95.91% |
| 4980 W | 100% | 91.97% | 96.00% | 95.54% |

**重要发现：**

1. **Sandia 在 100% 负载时效率陡降**：因为测试逆变器的 Pdco=4747W < Pac=4580W，即在接近额定时 AC 已经被限幅，效率数字失真。这是数据库参数和实际逆变器不对齐的常见问题。

2. **PVWatts 过于乐观**：在 100% 负载时仍报 96%，而实际逆变器接近满载时效率通常下降。

3. **ADR 最平滑**：过载到 110% 时仍能给出合理的 95.27%，说明模型外推性能好。

## 电压敏感性：被忽视的关键因素

```python
# PDC=3000W 时，改变 DC 电压
for v in [300, 350, 384, 400, 450]:
    ac_s = pvlib.inverter.sandia(v, 3000.0, sandia_params)
    ac_a = pvlib.inverter.adr(v, 3000.0, adr_params)
    ac_p = pvlib.inverter.pvwatts(3000.0, pdc0, eta_nom)  # 不变
    print(f"V={v}V: Sandia={ac_s:.1f}W, ADR={ac_a:.1f}W, PVWatts={ac_p:.1f}W")

# V=300V: Sandia=2897.6W, ADR=2866.0W, PVWatts=2887.6W (固定)
# V=450V: Sandia=2912.0W, ADR=2893.8W, PVWatts=2887.6W (固定)
```

在 300V→450V 的范围内，Sandia 输出变化约 **14W**，ADR 变化约 **28W**。对于冬夏直流电压可能相差 100V 的系统，这个差异会积累成显著误差。**PVWatts 完全忽略了电压，是其主要缺点。**

## CEC 加权效率计算

CEC（California Energy Commission）用 6 个功率点的加权平均评估逆变器，也叫"CEC 效率"：

```python
weights = [0.04, 0.05, 0.12, 0.21, 0.53, 0.05]  # 10/20/30/50/75/100%
pcts = [10, 20, 30, 50, 75, 100]

cec_sandia  = sum(w * eff_sandia[int(p/110*199)]  for w, p in zip(weights, pcts))
cec_pvwatts = sum(w * eff_pvwatts[int(p/110*199)] for w, p in zip(weights, pcts))
cec_adr     = sum(w * eff_adr[int(p/110*199)]     for w, p in zip(weights, pcts))

# 结果：
# Sandia CEC效率:  96.44%
# PVWatts CEC效率: 95.95%
# ADR CEC效率:     95.71%
```

## 选型指南

**用 Sandia，当：**
- 你能找到该逆变器的 Sandia 数据库记录
- 需要最高仿真精度（匹配实测数据）
- 做能量审计或性能保证分析

**用 ADR，当：**
- 做研究或对比多款逆变器的特性
- 逆变器不在 Sandia 数据库，但在 ADR 库中
- 需要好的电压外推能力

**用 PVWatts，当：**
- 快速估算，不需要精确逆变器数据
- 早期可行性研究
- 数据库里找不到对应逆变器

## 实际应用提示

```python
# 在 ModelChain 中指定逆变器模型
system = pvlib.pvsystem.PVSystem(
    ...,
    inverter_parameters=sandia_params,
    inverter='sandia'  # 或 'pvwatts', 'adr'
)
mc = pvlib.modelchain.ModelChain(system, location)
```

如果你的逆变器不在数据库里，可以用制造商提供的效率曲线反推 Sandia 参数（pvlib 有 `pvlib.inverter.fit_sandia` 函数）。

---

📋 **知识卡片**

| 要点 | 结论 |
|------|------|
| 最高精度 | Sandia（实测拟合，有限幅处理） |
| 最适合研究 | ADR（物理意义明确，外推性好） |
| 最简快速 | PVWatts（单参数，无电压依赖） |
| 电压敏感性 | Sandia > ADR >> PVWatts（=0） |
| 低负载精度 | 三者差异最大处，Sandia 最优 |
| 推荐数据库 | `pvlib.pvsystem.retrieve_sam('SandiaInverter')` |
| ADR 注意事项 | pvlib 0.15 不支持数组输入，需逐点计算 |