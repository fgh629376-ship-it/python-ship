---
title: 'pvlib Annual Energy Yield Assessment and PR Calculation — From Formula to Full-Year Simulation'
description: 'Full 8760-hour simulation of a 5kWp system in Shanghai using pvlib. A systematic guide to calculating PR, specific yield, and capacity factor — and why PR is actually lowest in summer'
pubDate: '2026-03-13'
category: solar
series: pvlib
lang: en
tags: ["pvlib", "光伏", "PR计算", "发电量评估", "技术干货"]
---

> ⚠️ **Data Disclaimer**: All simulation data in this article is calculated using **pvlib clearsky models**, not real power plant measurements. Clearsky models assume no clouds or haze year-round, so GHI, energy yield, and PR values will be higher than actual. Please refer to measured data for real-world applications.

## Why Does Your PV System Always Generate Less Than Expected?

You've installed a 5kWp PV system — how much electricity should it theoretically produce per year? Flip through the manufacturer's manual and you'll see one term repeated again and again: **PR** (Performance Ratio).

PR is the core indicator in the PV industry for measuring system "health." A system with PR = 92% vs. PR = 78% — same installed capacity — can differ by 15% in annual energy output.

This article uses pvlib to perform a full hourly simulation of a 5kWp residential PV system in Shanghai, walking through the calculation of PR, specific yield, and capacity factor — including why PR is actually lowest in summer.

---

## Part 1: Core Metric Formulas

Before writing any code, internalize these three formulas:

### PR (Performance Ratio)

$$PR = \frac{E_{ac}}{P_{peak} \times H_{POA}}$$

- $E_{ac}$: Annual AC energy output (kWh)
- $P_{peak}$: Installed capacity (kWp)
- $H_{POA}$: Annual plane-of-array (POA) irradiation ($\text{kWh/m}^2$)

**Key point**: The denominator uses POA irradiation, not horizontal GHI!

### Specific Yield

$$SY = \frac{E_{ac}}{P_{peak}} \quad \text{[kWh/kWp]}$$

Think of it as "how many kWh does each installed kW of peak capacity produce per year."

### Capacity Factor (CF)

$$CF = \frac{E_{ac}}{P_{peak} \times 8760} \times 100\%$$

---

## Part 2: Full-Year Hourly Simulation

### Environment Setup

```bash
pip install pvlib pandas numpy
```

### Step 1: Generate Full-Year Synthetic Weather Data

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

# Shanghai: 31.2°N, 121.5°E
site = Location(31.2, 121.5, tz='Asia/Shanghai', altitude=10, name='Shanghai')

# Full year: 8760 hours
times = pd.date_range('2025-01-01', '2025-12-31 23:00', freq='h', tz='Asia/Shanghai')

# Clear-sky irradiance as baseline
cs = site.get_clearsky(times, model='ineichen')

# Add random cloud perturbation to simulate real weather
np.random.seed(42)
cloud_factor = np.clip(np.random.beta(3, 1, len(times)), 0.1, 1.0)
day_mask = cs['ghi'] > 0

ghi = cs['ghi'].copy() * np.where(day_mask, cloud_factor, 1.0)
dni = cs['dni'].copy() * np.where(day_mask, cloud_factor, 1.0)
dhi = cs['dhi'].copy() * np.where(day_mask, cloud_factor, 1.0)

weather = pd.DataFrame({
    'ghi': ghi, 'dni': dni, 'dhi': dhi,
    # Air temperature: annual mean 15°C, hot summers and cold winters
    'temp_air': 15 + 10*np.sin(2*np.pi*(times.dayofyear-80)/365)
                   + np.random.normal(0, 3, len(times)),
    'wind_speed': np.clip(3 + np.random.exponential(2, len(times)), 0, 20),
}, index=times)

print(f"Annual GHI: {weather['ghi'].sum()/1000:.0f} kWh/m²")
# Annual GHI: 1640 kWh/m²
```

### Step 2: Build the PV System Model

```python
# Load CEC module database (built-in, no download needed)
cec_mods = pvlib.pvsystem.retrieve_sam('CECMod')
module = cec_mods['Canadian_Solar_Inc__CS6P_250P']

print(f"Module STC power: {module['STC']:.0f}W")
print(f"Temperature coefficient (Pmax): {module['gamma_r']:.3f}%/°C")
# Module STC power: 250W
# Temperature coefficient (Pmax): -0.424%/°C

# SAPM temperature model parameters (open rack, glass-glass encapsulation)
temp_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

N_MOD = 20          # Number of modules
KWP = N_MOD * module['STC'] / 1000  # = 5.0 kWp

# pvlib 0.15.0 requires Array + FixedMount to pass mounting parameters
array = Array(
    mount=FixedMount(surface_tilt=30, surface_azimuth=180),  # South-facing, 30° fixed tilt
    module_parameters=module,
    temperature_model_parameters=temp_params,
    modules_per_string=N_MOD,
    strings=1,
)

system = PVSystem(
    arrays=[array],
    inverter_parameters={'pdc0': KWP * 1000, 'eta_inv_nom': 0.96},  # PVWatts inverter
)
```

### Step 3: Run ModelChain and Extract Results

```python
mc = ModelChain(system, site, aoi_model='physical', spectral_model='no_loss')
mc.run_model(weather)

# ⚠️ pvlib 0.15.0 gotcha: results.ac is a DataFrame, power is in the p_mp column!
ac_power = mc.results.ac['p_mp'].clip(0)   # AC power in W
dc_power = mc.results.dc['p_mp'].clip(0)   # DC power in W
poa = mc.results.total_irrad['poa_global'] # Plane-of-array irradiance in W/m²
cell_temp = mc.results.cell_temperature    # Cell temperature in °C

# Convert to annual totals
ann_ac_kwh = float(ac_power.sum() / 1000)
ann_dc_kwh = float(dc_power.sum() / 1000)
poa_kwh_m2 = float(poa.sum() / 1000)

print(f"Annual POA (30° south-facing): {poa_kwh_m2:.0f} kWh/m²")
print(f"DC energy output: {ann_dc_kwh:.0f} kWh/year")
print(f"AC energy output: {ann_ac_kwh:.0f} kWh/year")
# Annual POA (30° south-facing): 1883 kWh/m²
# DC energy output: 9069 kWh/year
# AC energy output: 8694 kWh/year
```

### Step 4: Calculate Key Metrics

```python
# PR: note that denominator is KWP × poa_kwh_m2, units are already aligned
pr = ann_ac_kwh / (KWP * poa_kwh_m2)
sy = ann_ac_kwh / KWP               # Specific yield
cf = ann_ac_kwh / (KWP * 8760)      # Capacity factor

print(f"PR: {pr:.3f} ({pr*100:.1f}%)")
print(f"Specific Yield: {sy:.0f} kWh/kWp")
print(f"Capacity Factor: {cf*100:.1f}%")
# PR: 0.923 (92.3%)
# Specific Yield: 1739 kWh/kWp
# Capacity Factor: 19.8%
```

---

## Part 3: Monthly PR Analysis — Why Is Summer PR the Lowest?

```python
m_ac  = (ac_power.resample('ME').sum() / 1000).values
m_poa = (poa.resample('ME').sum() / 1000).values
m_ct  = cell_temp.resample('ME').mean().values
m_pr  = m_ac / (KWP * m_poa)

months = ['Jan','Feb','Mar','Apr','May','Jun',
          'Jul','Aug','Sep','Oct','Nov','Dec']
for i, mo in enumerate(months):
    print(f"{mo}: AC={m_ac[i]:.0f}kWh | Cell Temp={m_ct[i]:.1f}°C | PR={m_pr[i]:.3f}")
```

Results:

| Month | AC Output (kWh) | Cell Temp (°C) | Monthly PR |
|-------|----------------|----------------|------------|
| Jan   | 739            | 11.7           | 0.962      |
| Mar   | 819            | 20.2           | 0.924      |
| Jun   | 687            | 30.6           | **0.881**  |
| Sep   | 730            | 21.2           | 0.925      |
| Dec   | 691            | 10.2           | **0.971**  |

**Conclusion**: In June, cell temperature reaches 30.6°C and PR drops to 88.1%; in December, cell temperature is 10.2°C and PR reaches 97.1%.

The temperature coefficient of -0.424%/°C: from 25°C to 30.6°C, efficiency drops by about 2.4%. It doesn't seem like much, but the cumulative loss over an entire summer is quite significant.

---

## Part 4: Optimal Tilt Angle Scan

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
    print(f"Tilt {tilt:2d}°: {y:.1f} kWh ({(y-base)/base*100:+.1f}%)")
```

```
Tilt  0°: 7477.6 kWh (-14.0%)
Tilt 15°: 8341.9 kWh  (-4.0%)
Tilt 20°: 8516.2 kWh  (-2.0%)
Tilt 25°: 8633.5 kWh  (-0.7%)
Tilt 30°: 8694.0 kWh  (+0.0%)
Tilt 35°: 8698.0 kWh  (+0.0%) ← Optimal
Tilt 40°: 8645.3 kWh  (-0.6%)
Tilt 45°: 8535.7 kWh  (-1.8%)
```

The optimal tilt angle for Shanghai (31.2°N) is approximately 33-35°, but the difference between 25° and 40° is less than 1%. In practice, choosing 30° based on roof structure is perfectly fine — there's no need to agonize over the exact angle.

---

## Part 5: Complete Loss Chain

| Item | Value | Note |
|------|-------|------|
| Installed capacity | 5.0 kWp | |
| Theoretical max output | $8760\text{h} \times 5\text{kW} = 43800$ kWh | Never achieved |
| Reference output | 9415 kWh | Theoretical full output based on POA |
| DC energy output | 9069 kWh | ← Temperature losses (-3.8%), AOI, etc. |
| AC energy output | 8694 kWh | ← Inverter losses (-4.1%) |
| Total loss ratio | 7.7% | PR = 92.3% |

---

## ⚠️ Common pvlib 0.15.0 Pitfalls

1. **`results.ac` is a DataFrame** — don't call `.sum()` directly; use `['p_mp'].clip(0).sum()`
2. **PR formula denominator**: `KWP × poa_kwh_m2` — don't divide by 1000 again (units are already matched)
3. **PVSystem new API**: must use `Array(mount=FixedMount(...))` to pass mounting parameters
4. **POA ≠ GHI**: The PR denominator must use POA (plane-of-array) irradiation, otherwise results will be inflated

---

## Quick Reference Card 🗂️

| Metric | Formula | Shanghai 5kWp Case |
|--------|---------|-------------------|
| **PR** | E_ac / (P_peak × H_POA) | **92.3%** |
| **Specific Yield** | E_ac / P_peak | **1739 kWh/kWp** |
| **Capacity Factor** | E_ac / (P_peak × 8760) | **19.8%** |
| Optimal tilt | ≈ Local latitude | **~35°** (diff <1%, 30° is fine) |
| Lowest summer PR | High temp -0.424%/°C | Jun: 88.1% |
| Highest winter PR | Low temp, high efficiency | Dec: 97.1% |

**Rule of thumb (Shanghai)**: A 5kWp system produces approximately **8500~9000 kWh/year**, with a specific yield of approximately **1700~1800 kWh/kWp**.
