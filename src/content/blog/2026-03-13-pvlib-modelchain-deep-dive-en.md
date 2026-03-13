---
title: 'pvlib ModelChain Deep Dive: The 10-Step Loss Chain and Custom Extensions'
description: 'Explore the internal call chain of pvlib ModelChain, break down 9 replaceable model nodes, implement a custom losses_model for soiling/mismatch/wiring losses, and uncover the inverter undersizing clipping trap.'
category: solar
series: pvlib
pubDate: '2026-03-13'
lang: en
tags: ["pvlib", "光伏", "ModelChain", "仿真", "技术干货"]
---

## Introduction

pvlib's `ModelChain` is the orchestration engine of the entire simulation framework — it chains together a dozen independent models into a single pipeline, and a single `run_model()` call handles everything from weather data to AC output.

But many people only know how to "run the example" without understanding what's happening internally or how to customize it. This article takes ModelChain apart.

---

## The Full Call Chain (pvlib 0.15)

The internal execution order of ModelChain, extracted from the `_run_from_effective_irrad` source:

```
transposition → aoi → spectral → effective_irradiance
    → temperature → dc → dc_ohmic → losses → ac
```

**9 replaceable model nodes**, corresponding to ModelChain attributes:

| Attribute | Default | Role |
|---|---|---|
| `transposition_model` | `haydavies` | GHI/DNI/DHI → POA |
| `aoi_model` | `sapm_aoi_loss` | Angle of incidence correction |
| `spectral_model` | `sapm_spectral_loss` | Spectral correction |
| `temperature_model` | `sapm_temp` | Cell temperature |
| `dc_model` | `sapm` | DC power (I-V curve) |
| `dc_ohmic_model` | `no_dc_ohmic_loss` | DC ohmic losses |
| `losses_model` | `no_extra_losses` | Custom additional losses |
| `ac_model` | `sandia_inverter` | Inverter DC→AC |

Each node is replaceable — pass a string to use a built-in model, or pass a function for full customization.

---

## Quick Standard Simulation Setup

```python
import pvlib
import pandas as pd
import numpy as np

# Location: Shanghai
location = pvlib.location.Location(
    latitude=31.2, longitude=121.5,
    tz='Asia/Shanghai', altitude=5, name='Shanghai'
)

# Module (Sandia database)
module_db = pvlib.pvsystem.retrieve_sam('SandiaMod')
module = module_db['Canadian_Solar_CS5P_220M___2009_']

# Inverter (note: capacity must match!)
inverter_db = pvlib.pvsystem.retrieve_sam('SandiaInverter')
inverter = inverter_db['ABB__PVI_4_2_OUTD_S_US__208V_']  # 4.2kW

# Module temperature parameters
temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
    'sapm']['open_rack_glass_glass']

# Build system (10 series × 2 parallel = 4.39 kWp)
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

# Simulated weather data (Shanghai summer solstice)
times = pd.date_range('2025-06-21', periods=24, freq='1h', tz='Asia/Shanghai')
weather = pd.DataFrame({
    'ghi': [0,0,0,0,0,0,20,120,350,580,780,920,950,890,750,560,350,150,30,0,0,0,0,0],
    'dhi': [0,0,0,0,0,0,15,80,180,250,290,310,300,280,250,200,140,80,20,0,0,0,0,0],
    'dni': [0,0,0,0,0,0,30,180,480,720,880,980,1000,950,820,650,450,200,40,0,0,0,0,0],
    'temp_air': [28.0]*24,
    'wind_speed': [2.5]*24,
}, index=times)

mc.run_model(weather)
print(f'Daily energy: {mc.results.ac.clip(0).sum()/1000:.3f} kWh')
# → Daily energy: 27.072 kWh
```

---

## Intermediate Results: The Loss Chain Data

ModelChain doesn't just output the final AC value — all intermediate steps are recorded in `results`:

```python
poa    = mc.results.total_irrad['poa_global']  # Tilted plane irradiance
eff    = mc.results.effective_irradiance        # Effective irradiance (after AOI+spectral correction)
t_cell = mc.results.cell_temperature           # Cell temperature
dc     = mc.results.dc                         # DC power DataFrame
ac     = mc.results.ac                         # AC output

daytime = poa > 50
print(f'Mean POA:              {poa[daytime].mean():.1f} W/m²')   # 700.2
print(f'Mean effective irrad:  {eff[daytime].mean():.1f} W/m²')   # 689.9
print(f'Transmittance:         {(eff[daytime]/poa[daytime]).mean():.4f}')  # 0.9727
print(f'Mean cell temperature: {t_cell[daytime].mean():.1f}°C')   # 48.9°C
print(f'Inverter efficiency:   {(ac[daytime]/dc["p_mp"][daytime]).mean():.4f}')  # 0.9514
```

Measured loss chain for the summer solstice day (28°C ambient, 700 W/m² mean POA):

```
POA 700.2 W/m²
  → AOI+spectral: ×0.9727 → Effective irrad 689.9 W/m²  (-2.73%)
  → Temperature:  48.9°C  → DC Pmpp 2567 W
  → Inverter:     ×0.9514 → AC output 2458 W             (-4.86%)
  → System PR ≈ 79.7%
```

---

## Three Run Entry Points

ModelChain provides three entry points that skip different stages:

```python
# Entry 1: From GHI/DNI/DHI weather data (most common, full pipeline)
mc.run_model(weather)

# Entry 2: From tilted-plane POA data (skips transposition)
# Use when: you have a tilted-plane pyranometer with measured POA
poa_weather = pd.DataFrame({
    'poa_global': ..., 'poa_direct': ..., 'poa_diffuse': ...,
    'temp_air': ..., 'wind_speed': ...
}, index=times)
mc.run_model_from_poa(poa_weather)

# Entry 3: From effective irradiance (skips transposition+AOI+spectral)
# Use when: AOI and spectral corrections are already computed externally
eff_weather = pd.DataFrame({
    'effective_irradiance': ...,
    'temp_air': ..., 'wind_speed': ...
}, index=times)
mc.run_model_from_effective_irradiance(eff_weather)
```

Results from the three entry points differ by <0.05% on identical data — choose based on **where your data starts** in the pipeline.

---

## Custom losses_model: Applying Soiling/Mismatch/Wiring Losses

The losses_model is called **after dc_model, before ac_model** — this is the correct place to insert DC-side system losses.

### Correct Implementation

```python
def custom_dc_losses(mc_obj):
    """Custom losses: soiling 3% + mismatch 2% + wiring 1%"""
    factor = (1 - 0.03) * (1 - 0.02) * (1 - 0.01)  # = 0.9412
    mc_obj.results.dc['p_mp'] *= factor
    mc_obj.results.dc['i_mp'] *= np.sqrt(factor)
    mc_obj.results.dc['v_mp'] *= np.sqrt(factor)

# ✅ Correct: direct assignment, pvlib auto-wraps as functools.partial
mc.losses_model = custom_dc_losses
mc.run_model(weather)

kWh_loss = mc.results.ac.clip(0).sum() / 1000
# Result: 25.484 kWh (actual loss 5.87%, theoretical 5.89% — perfect match)
```

### ⚠️ Three Common Pitfalls

**Pitfall 1: losses_model modifies results.dc, not results.ac**

Losses are applied before AC is calculated. If you try to modify `mc_obj.results.ac`, it's still `None` at that point.

**Pitfall 2: Inverter undersizing can make losses "disappear"**

If the system is 4.39 kWp but the inverter is only 250W (DC/AC ratio of 17.6:1), the AC output is constantly clipped at Paco. Applying a 5.89% DC loss barely changes AC output (only 0.18% difference) — because the clipped power was going to be curtailed anyway. **Always check your DC/AC ratio first!**

```python
# Check DC/AC ratio
stc_power = module['Impo'] * module['Vmpo'] * n_modules
ratio = stc_power / inverter['Paco']
print(f'DC/AC ratio: {ratio:.2f}x')  # Reasonable range: 1.0~1.3
```

**Pitfall 3: haydavies transposition model requires dni_extra**

```python
# ❌ Error
poa = pvlib.irradiance.get_total_irradiance(..., model='haydavies')

# ✅ Correct
from pvlib.irradiance import get_extra_radiation
dni_extra = get_extra_radiation(times)
poa = pvlib.irradiance.get_total_irradiance(..., model='haydavies', dni_extra=dni_extra)
```

---

## Temperature Model Comparison

Under identical conditions, the difference between SAPM and PVsyst temperature models:

```python
# SAPM temperature parameters (open rack, glass-glass)
temp_sapm = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
# PVsyst temperature parameters (freestanding)
temp_pvs  = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['pvsyst']['freestanding']
```

Summer solstice comparison at 28°C ambient:

| Temperature Model | Mean Cell Temp | Daily Energy | Difference |
|---|---|---|---|
| SAPM | 48.9°C | 27.072 kWh | baseline |
| PVsyst | 47.6°C | 27.336 kWh | +0.97% |

PVsyst gives slightly lower cell temperature and marginally higher energy yield. Both are valid — the choice depends on mounting type and data source.

---

## Quick Reference Card

> **ModelChain = LEGO Bricks**
> Each node can be independently replaced while keeping the rest as default. Customize one, inherit the other eight for free.

**Full call chain**:
```
transposition → aoi → spectral → effective_irradiance
  → temperature → dc → dc_ohmic → losses → ac
```

**Quick customization guide**:

| Goal | Method |
|---|---|
| System losses (soiling/mismatch/wiring) | `mc.losses_model = my_func` |
| Temperature model | Change `temperature_model_parameters` in Array |
| Inverter model | `ModelChain(ac_model='pvwatts')` |
| Transposition model | `ModelChain(transposition_model='perez')` |
| Custom DC | `mc.dc_model = my_dc_func` |

**losses_model function signature**: accepts `mc_obj`, modifies `mc_obj.results.dc`, no return value needed. Remember this pipeline, and you'll always know where to insert custom code.
