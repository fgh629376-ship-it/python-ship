---
title: 'The Complete Guide to Solar Power Forecasting with pvlib-python'
description: 'PV power forecasting with Python — pvlib from basics to production, covering the physics modeling chain, ModelChain, weather data integration, and hybrid ML approaches'
pubDate: '2026-03-12'
category: solar
series: pvlib
lang: en
tags: ['pvlib', '光伏', '能源', '技术干货']
---

## What Is pvlib?

**pvlib** is the standard Python library for physics-based PV modeling in the solar industry. Important: it is **not** a machine learning prediction library — it's a deterministic power forecasting tool grounded in physical principles.

The core idea is simple: **given a location + time + weather data → calculate the exact power output of a PV system at that moment**.

```bash
pip install pvlib
# Latest: v0.15.1 (March 2026)
```

---

## The Physics Chain Behind PV Forecasting

pvlib breaks power forecasting into 6 physical steps, each with corresponding models:

```
Solar Position (altitude / azimuth)
  ↓
Clear-Sky Irradiance (GHI / DNI / DHI)
  ↓
Plane-of-Array (POA) Irradiance (actual irradiance on the tilted surface)
  ↓
Effective Irradiance (accounting for AOI losses + spectral correction)
  ↓
Module Temperature (affects efficiency by 5–10%)
  ↓
DC Power → AC Power (via inverter) → Final Output
```

Understanding this chain is the key to getting the most out of pvlib.

---

## Core Module Reference

| Module | Responsibility | Key Functions |
|--------|---------------|---------------|
| `solarposition` | Solar altitude / azimuth | `get_solarposition()` |
| `clearsky` | Clear-sky irradiance models | `ineichen()`, `haurwitz()` |
| `irradiance` | Irradiance decomposition / transposition | `get_total_irradiance()`, `perez()` |
| `temperature` | Module / cell temperature | `sapm_cell()`, `faiman()` |
| `pvsystem` | DC / AC power calculation | `pvwatts_dc()`, `singlediode()` |
| `modelchain` | **Full pipeline wrapper** | `ModelChain.run_model()` |
| `iotools` | Weather data ingestion | Solcast / ERA5 / NASA Power |

---

## ModelChain — End-to-End Power Forecasting

ModelChain is the highest-level abstraction, chaining all 6 steps together. Just define a location, system parameters, and feed in weather data:

```python
import pvlib
import pandas as pd

# 1. Define location (Shanghai)
location = pvlib.location.Location(
    latitude=31.2,
    longitude=121.5,
    altitude=10,
    tz='Asia/Shanghai'
)

# 2. Define PV system
module_params = dict(pdc0=10000, gamma_pdc=-0.004)  # 10kW, temperature coeff -0.4%/°C
inverter_params = dict(pdc0=9500)
temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
    'sapm']['open_rack_glass_glass'
]

system = pvlib.pvsystem.PVSystem(
    surface_tilt=30,        # 30° tilt
    surface_azimuth=180,    # south-facing
    module_parameters=module_params,
    inverter_parameters=inverter_params,
    temperature_model_parameters=temp_params,
    modules_per_string=20,
    strings_per_inverter=2,
)

# 3. Build ModelChain
mc = pvlib.modelchain.ModelChain(
    system, location,
    dc_model='pvwatts',
    ac_model='pvwatts',
    aoi_model='physical',
    spectral_model='no_loss',
    temperature_model='sapm',
)

# 4. Prepare weather data (must include ghi/dhi/dni)
times = pd.date_range('2026-06-01', '2026-06-07', freq='1h', tz='Asia/Shanghai')
weather = location.get_clearsky(times)  # clear-sky assumption
weather['temp_air'] = 25
weather['wind_speed'] = 2

# 5. Run!
mc.run_model(weather)

# 6. Get results
ac_power = mc.results.ac  # W, AC power time series
dc_power = mc.results.dc  # W, DC power
```

---

## Three Forecasting Scenarios

### Scenario 1: Clear-Sky Baseline Forecast

Clear-sky = theoretical maximum irradiance under cloudless conditions, often used as a baseline:

```python
clearsky = location.get_clearsky(times, model='ineichen')
# Outputs ghi/dni/dhi
# Actual power / clear-sky power = clear-sky index (0~1)
```

### Scenario 2: NWP Weather Forecast Integration

The most common approach for short-term forecasting — fetch forecast data from a third party and feed it directly into the model:

```python
from pvlib.iotools import get_solcast_forecast

df, meta = get_solcast_forecast(
    latitude=31.2,
    longitude=121.5,
    api_key='your_key',
    hours=48,
)
# df includes ghi/dni/dhi/temp_air/wind_speed
mc.run_model(df)
```

### Scenario 3: On-Site POA Sensor Data

Have sensors on site? The data is more accurate — use it directly:

```python
mc.run_model_from_poa(poa_data)
# poa_data must include poa_global / poa_direct / poa_diffuse
```

---

## Model Selection Guide

### Irradiance Transposition (GHI → POA)

- **`perez`** — highest accuracy, recommended by default
- **`haydavies`** — sufficient for most cases
- **`isotropic`** — for quick estimates

### DC Power Models

- **`pvwatts`** — only requires `pdc0 + gamma_pdc`; best when data is limited
- **`sapm`** — requires full Sandia parameters; for accurate simulation
- **`singlediode`** — requires 5 parameters; most accurate

### Temperature Models

```python
# SAPM (most commonly used)
pvlib.temperature.sapm_cell(poa_global, temp_air, wind_speed, a, b, deltaT)

# Faiman (simple linear, works well)
pvlib.temperature.faiman(poa_global, temp_air, wind_speed, u0=25, u1=6.84)
```

---

## Loss Model (PVWatts)

Real-world output is always lower than theoretical. pvlib accounts for all common loss factors:

```python
losses = pvlib.pvsystem.pvwatts_losses(
    soiling=2,          # dust: 2%
    shading=3,          # shading: 3%
    mismatch=2,         # mismatch: 2%
    wiring=2,           # wiring: 2%
    connections=0.5,    # connections: 0.5%
    lid=1.5,            # LID: 1.5%
    nameplate_rating=1, # nameplate tolerance: 1%
    availability=3,     # availability: 3%
)
# Total losses ~14.1%
```

---

## pvlib + ML = Industry Best Practice

Pure physics models have a ceiling; pure ML lacks physical constraints. Combining them is the mainstream approach:

1. Run pvlib to get physics-based baseline forecast $P_{\text{phys}}$
2. Compute residuals: $\text{residual} = P_{\text{actual}} - P_{\text{phys}}$
3. Train XGBoost / LSTM on the residuals (features: cloud index, NWP bias, historical residuals)
4. Final forecast: $P_{\text{final}} = P_{\text{phys}} + \text{residual}_{\text{pred}}$

Physics constraints keep forecasts physically plausible; ML corrects errors introduced by weather forecast uncertainty.

---

## Weather Data Sources

| Source | Highlights | Cost |
|--------|-----------|------|
| **Solcast** | Most accurate, supports forecasting | Commercial |
| **ERA5** | ECMWF reanalysis, global coverage | Free |
| **NASA Power** | Global coverage | Free |
| **PVGIS** | EU-maintained | Free |

---

## Quick Reference Card 📌

```
pvlib core positioning:
  Physics modeling engine — not a black-box ML model

6-step forecasting chain:
  Solar position → Clear-sky irradiance → POA irradiance
  → Effective irradiance → Module temperature → Power

Fastest way to get started:
  ModelChain.run_model(weather_dataframe)

Production formula:
  pvlib physics baseline + ML residual correction = optimal solution
```
