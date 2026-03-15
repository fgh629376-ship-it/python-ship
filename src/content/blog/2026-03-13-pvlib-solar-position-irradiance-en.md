---
title: 'pvlib Solar Position and Irradiance Decomposition — The Physical Foundation of PV Forecasting'
description: 'Deep dive into pvlib solar position calculation (SPA) and irradiance decomposition (GHI→DNI/DHI→POA), with complete code demonstrations'
category: solar
series: pvlib
pubDate: '2026-03-13'
lang: en
tags: ["pvlib", "光伏", "辐照度", "技术干货"]
---

## Why Are Solar Position and Irradiance the Foundation of PV Forecasting?

A PV panel's energy output depends on two physical quantities: **how much energy from the sun reaches the panel** (POA irradiance), and **the panel's electrical response under those conditions**.

The very first step in the entire chain is figuring out: where is the sun in the sky, and how much radiation reaches the panel.

---

## I. Solar Position Calculation

### Core Concepts

- **Zenith angle**: The angle between the sun and directly overhead. 0° = directly overhead, 90° = horizon
- **Azimuth angle**: The horizontal direction of the sun. 0° = due north, 90° = due east, 180° = due south
- **Elevation angle**: = 90° - zenith
- **Apparent zenith angle**: Zenith angle corrected for atmospheric refraction

### pvlib Implementation

pvlib uses the **NREL SPA algorithm** (Solar Position Algorithm) by default, with accuracy of ±0.0003° — this is the industry gold standard.

```python
import pvlib
import pandas as pd

# Define location
location = pvlib.location.Location(
    latitude=31.23, longitude=121.47,
    tz="Asia/Shanghai", altitude=5, name="Shanghai"
)

# Time series
times = pd.date_range(
    "2024-06-21 04:00", periods=48,
    freq="30min", tz="Asia/Shanghai"
)

# Calculate solar position
solpos = location.get_solarposition(times)
print(solpos[["zenith", "azimuth", "apparent_elevation"]].head(10))
```

**Key output columns:**
| Column | Meaning | Unit |
|--------|---------|------|
| `zenith` | Zenith angle | ° |
| `apparent_zenith` | Apparent zenith (with refraction) | ° |
| `azimuth` | Azimuth angle | ° |
| `apparent_elevation` | Apparent elevation angle | ° |
| `equation_of_time` | Equation of time | minutes |

### Sunrise/Sunset Detection

```python
# zenith > 90° means nighttime
is_daytime = solpos["zenith"] < 90
sunrise = solpos[is_daytime].index[0]
sunset = solpos[is_daytime].index[-1]
print(f"Sunrise: {sunrise}, Sunset: {sunset}")
```

---

## II. Irradiance Fundamentals

When solar radiation reaches the Earth's surface, it is divided into three components:

| Component | Abbreviation | Meaning |
|-----------|-------------|---------|
| **Global Horizontal Irradiance** | GHI | Total radiation received on a horizontal surface |
| **Direct Normal Irradiance** | DNI | Beam radiation perpendicular to the sun's direction |
| **Diffuse Horizontal Irradiance** | DHI | Scattered radiation received on a horizontal surface |

**Basic relationship:**
```
$\text{GHI} = \text{DNI} \times \cos(\theta_z) + \text{DHI}$
```

Weather stations typically only measure GHI, so models are needed to decompose it into DNI and DHI.

---

## III. Irradiance Decomposition Models

When you only have GHI data, you need to split it into DNI + DHI:

### DISC Model
```python
# GHI → DNI
dni_disc = pvlib.irradiance.disc(
    ghi=clearsky["ghi"],
    solar_zenith=solpos["zenith"],
    datetime_or_doy=times
)
print(dni_disc.head())
```

### DIRINT Model (More Accurate)
```python
# GHI → DNI (considers more atmospheric variables)
dni_dirint = pvlib.irradiance.dirint(
    ghi=clearsky["ghi"],
    solar_zenith=solpos["zenith"],
    times=times
)
```

### Erbs Decomposition
```python
# GHI → DNI + DHI (classic model)
from pvlib.irradiance import clearness_index

# First compute the clearness index kt
kt = clearness_index(
    ghi=measured_ghi,
    solar_zenith=solpos["zenith"],
    extra_radiation=pvlib.irradiance.get_extra_radiation(times)
)
```

---

## IV. Horizontal Irradiance → Panel Irradiance (POA)

Panels are not horizontal — GHI/DNI/DHI must be converted to irradiance on the tilted panel surface (POA = Plane of Array).

### Conversion Process

```python
# 1. Extraterrestrial radiation (needed for Perez model)
dni_extra = pvlib.irradiance.get_extra_radiation(times)

# 2. Panel parameters
surface_tilt = 31.23    # Tilt angle (typically ≈ latitude)
surface_azimuth = 180   # South-facing

# 3. Calculate POA
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"],
    dni=clearsky["dni"],
    ghi=clearsky["ghi"],
    dhi=clearsky["dhi"],
    dni_extra=dni_extra,
    model="perez"  # Perez diffuse model recommended
)
print(poa[["poa_global", "poa_direct", "poa_diffuse"]].head())
```

### POA Output Components

| Component | Meaning |
|-----------|---------|
| `poa_global` | Total panel irradiance |
| `poa_direct` | Beam component on panel |
| `poa_diffuse` | Diffuse component on panel (sky + ground reflection) |
| `poa_sky_diffuse` | Sky diffuse |
| `poa_ground_diffuse` | Ground-reflected diffuse |

### Diffuse Model Comparison

pvlib provides several diffuse models:

| Model | Function | Accuracy | Use Case |
|-------|----------|----------|---------|
| **Perez** | `pvlib.irradiance.perez()` | ⭐⭐⭐⭐⭐ | General first choice |
| **Hay-Davies** | `pvlib.irradiance.haydavies()` | ⭐⭐⭐⭐ | Lower computation |
| **Reindl** | `pvlib.irradiance.reindl()` | ⭐⭐⭐⭐ | Middle ground |
| **Klucher** | `pvlib.irradiance.klucher()` | ⭐⭐⭐ | Cloudy conditions |
| **Isotropic** | `pvlib.irradiance.isotropic()` | ⭐⭐ | Simplest |

**The Perez model is the industry first choice** — highest accuracy, requires `dni_extra` (extraterrestrial radiation) as an additional input.

---

## V. Angle of Incidence (AOI) Calculation

Sunlight doesn't hit the panel perpendicularly — the angle of incidence affects reflection losses:

```python
aoi = pvlib.irradiance.aoi(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"]
)
print(f"Solar noon AOI: {aoi.iloc[len(aoi)//2]:.1f}°")
```

The larger the AOI, the greater the reflection loss. pvlib provides several IAM (Incident Angle Modifier) models:

```python
# Physical IAM model
iam_loss = pvlib.iam.physical(aoi, n=1.526, K=4.0, L=0.002)
# Returns a transmittance coefficient between 0 and 1
```

---

## VI. Clear-Sky Models

When measured data is unavailable, use a clear-sky model to estimate ideal irradiance:

```python
# Ineichen clear-sky model (default)
clearsky = location.get_clearsky(times, model="ineichen")

# Outputs GHI, DNI, DHI
print(clearsky.columns)  # ghi, dni, dhi
```

Clear-sky models supported by pvlib:
- **Ineichen-Perez** (default) — most widely used
- **Haurwitz** — simple, GHI output only
- **Simplified Solis** — supports aerosol optical depth

---

## VII. Complete Example: Full Pipeline from Location to POA

```python
import pvlib
import pandas as pd

# Location: Shanghai
loc = pvlib.location.Location(31.23, 121.47, "Asia/Shanghai", 5)
times = pd.date_range("2024-06-21", periods=48, freq="30min", tz="Asia/Shanghai")

# Solar position
solpos = loc.get_solarposition(times)

# Clear-sky irradiance
cs = loc.get_clearsky(times)

# Extraterrestrial radiation
dni_extra = pvlib.irradiance.get_extra_radiation(times)

# Panel POA (tilt = latitude, south-facing)
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=31.23, surface_azimuth=180,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"],
    dni=cs["dni"], ghi=cs["ghi"], dhi=cs["dhi"],
    dni_extra=dni_extra, model="perez"
)

# Print solar noon results
noon = poa.between_time("11:30", "12:30")
print("Solar Noon POA Irradiance (W/m²):")
print(noon[["poa_global", "poa_direct", "poa_diffuse"]].round(1))

# Daily irradiation (kWh/m²)
daily_irradiation = poa["poa_global"].sum() * 0.5 / 1000  # 30-minute intervals
print(f"\nDaily irradiation: {daily_irradiation:.2f} kWh/m²")
```

---

## Quick Reference Card 📋

| Key Point | Details |
|-----------|---------|
| **Solar position** | pvlib uses SPA algorithm, accuracy ±0.0003°, outputs zenith/azimuth |
| **The irradiance trio** | $\text{GHI} = \text{DNI} \times \cos(z) + \text{DHI}$; weather stations measure GHI, models decompose it |
| **Decomposition models** | DISC, DIRINT — extract DNI from GHI |
| **POA conversion** | Horizontal → tilted panel irradiance; Perez model recommended |
| **AOI** | Affects reflection losses; corrected with IAM models |
| **Clear-sky models** | Ideal irradiance estimate when measured data is unavailable |

> **Next article preview:** pvlib Module Temperature Models and DC Power Calculation — Converting Irradiance to Watts
