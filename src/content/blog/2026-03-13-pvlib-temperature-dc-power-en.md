---
title: 'pvlib Temperature Models and DC Power Calculation — From Irradiance to Watts'
description: 'Deep dive into pvlib cell temperature models (SAPM/PVsyst/Faiman) and DC power models (SAPM/CEC/PVWatts), with complete code comparisons'
category: solar
series: pvlib
pubDate: '2026-03-13'
lang: en
tags: ["pvlib", "光伏", "温度模型", "DC功率", "技术干货"]
---

## What Comes After Irradiance Reaches the Panel?

In the previous article, we calculated POA irradiance. But irradiance is not power — there are two critical intermediate steps: **cell temperature calculation** and **electrical model conversion**.

Higher temperatures reduce module efficiency. This is not trivial — summer heat can cause energy output to drop by more than 10%.

---

## I. Why Does Temperature Matter So Much?

Silicon-based PV modules have a temperature coefficient of approximately **-0.3% ~ -0.5% /°C**.

- STC (Standard Test Conditions): cell temperature 25°C
- Actual operation: summer midday cell temperature can reach **60-70°C**
- Temperature rise of 40°C × (-0.4%/°C) = **16% drop in energy output**

This is why pvlib has 4 temperature models — accurate temperature means accurate predictions.

---

## II. Comparison of Four Temperature Models

### SAPM Model (Sandia)

The most commonly used empirical model in the industry:

```python
import pvlib

# Parameter sets
params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]
print("Available parameter sets:", list(params.keys()))
# open_rack_glass_glass, close_mount_glass_glass,
# open_rack_glass_polymer, insulated_back_glass_polymer

# Calculate cell temperature
temp_params = params["open_rack_glass_glass"]
t_cell = pvlib.temperature.sapm_cell(
    poa_global=1000,   # W/m²
    temp_air=32,       # °C
    wind_speed=1.5,    # m/s
    **temp_params       # a, b, deltaT
)
print(f"SAPM cell temperature: {t_cell:.1f}°C")  # ≈63.6°C
```

**Parameter meanings:**
- `a`, `b`: Empirical coefficients describing the effect of POA and wind speed on module back-surface temperature
- `deltaT`: Temperature difference between cell and back surface

### PVsyst Model

Physics-based model using thermal balance:

```python
t_pvsyst = pvlib.temperature.pvsyst_cell(
    poa_global=1000,
    temp_air=32,
    wind_speed=1.5,
    u_c=29.0,   # Constant heat loss coefficient W/(m²·K)
    u_v=0.0     # Wind speed-related heat loss coefficient
)
print(f"PVsyst cell temperature: {t_pvsyst:.1f}°C")  # ≈60.1°C
```

### Faiman Model

Simplified thermal balance with two parameters:

```python
t_faiman = pvlib.temperature.faiman(
    poa_global=1000,
    temp_air=32,
    wind_speed=1.5,
    u0=25.0,    # Constant heat dissipation coefficient
    u1=6.84     # Wind speed heat dissipation coefficient
)
print(f"Faiman cell temperature: {t_faiman:.1f}°C")  # ≈60.5°C
```

### Ross Model

The simplest linear model:

```python
t_ross = pvlib.temperature.ross(
    poa_global=1000,
    temp_air=32,
    noct=45      # Nominal Operating Cell Temperature (NOCT)
)
print(f"Ross cell temperature: {t_ross:.1f}°C")  # ≈63.4°C
```

### Model Comparison Summary

| Model | Parameters | Accuracy | Computation | Use Case |
|-------|-----------|----------|-------------|---------|
| **SAPM** | 3 | ⭐⭐⭐⭐ | Low | General first choice |
| **PVsyst** | 2 | ⭐⭐⭐⭐ | Low | PVsyst users |
| **Faiman** | 2 | ⭐⭐⭐⭐ | Lowest | Quick estimation |
| **Ross** | 1 | ⭐⭐⭐ | Lowest | When NOCT is known |
| **Fuentes** | Multiple | ⭐⭐⭐⭐⭐ | High | High-precision needs |

---

## III. DC Power Models

With temperature calculated, the next step is converting irradiance + temperature into DC power.

### SAPM Model (Most Accurate)

Requires 14+ parameters from the Sandia database. 523 modules available.

### CEC / Single-Diode Model (Engineering Standard)

Solves the single-diode equation using 5 electrical parameters:

```python
cec_modules = pvlib.pvsystem.retrieve_sam("CECMod")
module = cec_modules["Canadian_Solar_Inc__CS5P_220M"]

# Calculate five parameters (varies with operating conditions)
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

# Solve I-V characteristics
result = pvlib.pvsystem.singlediode(IL, I0, Rs, Rsh, nNsVt)
print(f"Pmpp: {result['p_mp']:.1f} W")
print(f"Voc:  {result['v_oc']:.2f} V")
print(f"Isc:  {result['i_sc']:.3f} A")
```

### PVWatts Model (Quick Estimation)

Only requires two parameters:

```python
dc_power = pvlib.pvsystem.pvwatts_dc(
    g_poa_effective=1000,   # Effective POA W/m²
    temp_cell=50,           # Cell temperature °C
    pdc0=220,               # Rated power at STC (W)
    gamma_pdc=-0.004        # Temperature coefficient 1/°C
)
print(f"PVWatts DC power: {dc_power:.1f} W")
# 220 * (1000/1000) * (1 + (-0.004) * (50-25)) = 198 W
```

### Measured Comparison Under Different Conditions

| Condition | POA | Tc | Pmpp | FF |
|-----------|-----|-----|------|-----|
| STC | 1000 | 25°C | 220.0W | 0.726 |
| Overcast | 800 | 25°C | 177.6W | 0.740 |
| High temp | 1000 | 50°C | 193.0W | 0.695 |
| Winter low irradiance | 500 | 15°C | 117.0W | 0.770 |
| Dawn/dusk | 200 | 10°C | 47.2W | 0.792 |

---

## IV. Key Insights

1. **Fill factor (FF) decreases as temperature rises**: At high temperatures, internal resistance increases, dropping FF from 0.77 to 0.70
2. **FF is actually higher at low irradiance**: Smaller current means proportionally lower resistive losses
3. **Annual energy difference between PVWatts and CEC is about 10-15%**: CEC is more accurate; recommended for engineering projects

---

## Quick Reference Card 📋

| Key Point | Details |
|-----------|---------|
| **Temperature impact** | -0.4%/°C; summer can reduce output by 10-16% |
| **Temperature models** | SAPM is general first choice; PVsyst/Faiman for simplified alternatives |
| **DC models** | SAPM (14 params) > CEC (6 params) > PVWatts (2 params) |
| **Single-diode** | IL/I0/Rs/Rsh/nNsVt — five parameters that vary dynamically with conditions |
| **Fill factor** | 0.70-0.79; efficiency drops as FF decreases with rising temperature |
| **CEC database** | 21,535 module parameter sets available; engineering-grade selection |

> **Next article preview:** pvlib Inverter Models — Practical comparison of Sandia/ADR/PVWatts three major models
