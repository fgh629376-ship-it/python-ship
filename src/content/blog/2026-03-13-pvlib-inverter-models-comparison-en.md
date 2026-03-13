---
title: 'Deep Comparison of pvlib Inverter Models: Sandia vs ADR vs PVWatts'
description: 'A comprehensive comparison of three major inverter models — parameter systems, efficiency curves, and voltage sensitivity — with real database code samples to help you choose the right model for PV simulation'
pubDate: '2026-03-13'
category: solar
lang: en
tags: ["pvlib", "光伏", "逆变器", "技术干货", "仿真"]
---

pvlib provides three mainstream inverter models: **Sandia**, **ADR (Anton Driesse)**, and **PVWatts**. Choosing the wrong model can cause your annual energy yield prediction to be off by more than 2% — this article uses real code to thoroughly explore all three.

## Why Do Inverter Models Matter?

Inverter efficiency is not a constant — it varies with power and voltage. A nominally 96% efficient inverter might only achieve 92% at 10% load, and drops sharply under overload conditions. The wrong model introduces systematic bias into your system simulation.

## Quick Overview of the Three Models

| Feature | Sandia | ADR | PVWatts |
|---------|--------|-----|---------|
| Parameter source | Measured and fitted | Physics + fitted | Simplified empirical |
| Voltage sensitivity | ✅ Yes | ✅ Yes | ❌ No |
| Database | `SandiaInverter` | `ADRInverter` | No database needed |
| Accuracy | High | High | Medium |
| Use case | Detailed simulation | Research-grade | Quick estimation |

## Code Walkthrough

### Loading the Databases

```python
import pvlib
import numpy as np

# Sandia database (covers mainstream inverters worldwide)
inv_db = pvlib.pvsystem.retrieve_sam('SandiaInverter')
sandia_params = inv_db['SMA_America__SB5000TL_US_22__208V_']

# ADR database
adr_db = pvlib.pvsystem.retrieve_sam('ADRInverter')
adr_params = adr_db['Ablerex_Electronics_Co___Ltd___ES_5000_US_240__240_Vac__240V__CEC_2011_']

print("Sandia rated power:", sandia_params['Paco'], "W")
print("ADR rated power:", adr_params['Pacmax'], "W")
# Output:
# Sandia rated power: 4580.0 W
# ADR rated power: 5240.0 W
```

### Calling the Sandia Model

```python
# Parameters: v_dc (DC voltage), p_dc (DC power), parameter dict
pdc_arr = np.linspace(50, 5500, 200)
v_nom = 400.0  # Operating voltage

ac_sandia = pvlib.inverter.sandia(v_nom, pdc_arr, sandia_params)
# Automatically clips at Paco, returns NaN or Paco when exceeded
```

**Key parameter breakdown:**
- `Paco`: AC rated ceiling (clipping point)
- `Pdco`: DC power corresponding to rated AC output
- `Vdco`: DC voltage corresponding to peak efficiency
- `C0~C3`: 4 fitted coefficients of the efficiency curve
- `Pso`: Self-consumption threshold (AC output is 0 below this DC power)

### Calling the PVWatts Model

```python
# Simplest: only needs rated power and efficiency
pdc0 = 5000  # Rated DC power [W]
eta_nom = 0.96  # Rated efficiency

ac_pvwatts = pvlib.inverter.pvwatts(pdc_arr, pdc0, eta_nom)
# Clips at pdc0 * 1.1 when exceeded
```

PVWatts uses a piecewise polynomial efficiency curve internally and **does not depend on voltage** — one parameter does it all.

### Calling the ADR Model

```python
# ADR parameters come from the ADRInverter database
# Note: In v0.15.0, ADR does not support array input — must loop with scalars
ac_adr = np.array([
    pvlib.inverter.adr(v_nom, float(p), adr_params)
    for p in pdc_arr
])
```

ADR uses a 9-coefficient 2D polynomial that simultaneously describes the effect of both power and voltage on efficiency — making it the most physically meaningful of the three models.

## Measured Efficiency Curve Comparison

```python
eff_sandia  = ac_sandia  / pdc_arr * 100
eff_pvwatts = ac_pvwatts / pdc_arr * 100
eff_adr     = ac_adr     / pdc_arr * 100
```

| DC Power | % of Rated | Sandia | PVWatts | ADR |
|----------|-----------|--------|---------|-----|
| 296 W | 5% | 92.25% | 88.19% | 87.36% |
| 543 W | 10% | 94.99% | 92.61% | 92.27% |
| 1036 W | 20% | 96.43% | 95.03% | 94.91% |
| 2515 W | 50% | **96.92%** | 96.22% | 96.07% |
| 3747 W | 75% | 96.70% | 96.21% | 95.91% |
| 4980 W | 100% | 91.97% | 96.00% | 95.54% |

**Key findings:**

1. **Sandia efficiency drops sharply at 100% load**: This is because the test inverter's Pdco=4747W < Pac=4580W — the AC output is already clipped near rated power, distorting the efficiency figure. This is a common issue when database parameters don't match the actual inverter.

2. **PVWatts is overly optimistic**: Still reports 96% at 100% load, while real inverters typically see efficiency dip near full load.

3. **ADR is smoothest**: Gives a reasonable 95.27% even at 110% overload, showing good extrapolation capability.

## Voltage Sensitivity: The Often-Overlooked Key Factor

```python
# At PDC=3000W, varying DC voltage
for v in [300, 350, 384, 400, 450]:
    ac_s = pvlib.inverter.sandia(v, 3000.0, sandia_params)
    ac_a = pvlib.inverter.adr(v, 3000.0, adr_params)
    ac_p = pvlib.inverter.pvwatts(3000.0, pdc0, eta_nom)  # Unchanged
    print(f"V={v}V: Sandia={ac_s:.1f}W, ADR={ac_a:.1f}W, PVWatts={ac_p:.1f}W")

# V=300V: Sandia=2897.6W, ADR=2866.0W, PVWatts=2887.6W (fixed)
# V=450V: Sandia=2912.0W, ADR=2893.8W, PVWatts=2887.6W (fixed)
```

Over a range of 300V to 450V, the Sandia output varies by about **14W** and ADR varies by about **28W**. For systems where DC voltage can differ by 100V between summer and winter, this difference accumulates into significant error. **PVWatts completely ignores voltage — this is its main weakness.**

## CEC Weighted Efficiency Calculation

CEC (California Energy Commission) evaluates inverters using a weighted average of 6 power points — also called "CEC efficiency":

```python
weights = [0.04, 0.05, 0.12, 0.21, 0.53, 0.05]  # 10/20/30/50/75/100%
pcts = [10, 20, 30, 50, 75, 100]

cec_sandia  = sum(w * eff_sandia[int(p/110*199)]  for w, p in zip(weights, pcts))
cec_pvwatts = sum(w * eff_pvwatts[int(p/110*199)] for w, p in zip(weights, pcts))
cec_adr     = sum(w * eff_adr[int(p/110*199)]     for w, p in zip(weights, pcts))

# Results:
# Sandia CEC efficiency:  96.44%
# PVWatts CEC efficiency: 95.95%
# ADR CEC efficiency:     95.71%
```

## Selection Guide

**Use Sandia when:**
- You can find the inverter's record in the Sandia database
- You need the highest simulation accuracy (matched to measured data)
- You're doing an energy audit or performance guarantee analysis

**Use ADR when:**
- Doing research or comparing the characteristics of multiple inverters
- The inverter isn't in the Sandia database, but is in the ADR database
- You need good voltage extrapolation capability

**Use PVWatts when:**
- Quick estimation, no precise inverter data needed
- Early-stage feasibility study
- Can't find the corresponding inverter in either database

## Practical Application Notes

```python
# Specifying the inverter model in ModelChain
system = pvlib.pvsystem.PVSystem(
    ...,
    inverter_parameters=sandia_params,
    inverter='sandia'  # or 'pvwatts', 'adr'
)
mc = pvlib.modelchain.ModelChain(system, location)
```

If your inverter is not in any database, you can back-fit Sandia parameters from the manufacturer's efficiency curve (pvlib has the `pvlib.inverter.fit_sandia` function).

---

📋 **Quick Reference Card**

| Key Point | Conclusion |
|-----------|-----------|
| Highest accuracy | Sandia (measured and fitted, with clipping handling) |
| Best for research | ADR (clear physical meaning, good extrapolation) |
| Simplest and fastest | PVWatts (single parameter, no voltage dependency) |
| Voltage sensitivity | Sandia > ADR >> PVWatts (= 0) |
| Low-load accuracy | Largest differences between models — Sandia is best |
| Recommended database | `pvlib.pvsystem.retrieve_sam('SandiaInverter')` |
| ADR note | pvlib 0.15 doesn't support array input — must calculate point by point |
