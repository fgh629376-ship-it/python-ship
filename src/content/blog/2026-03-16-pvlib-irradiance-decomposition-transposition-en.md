---
title: "🔬 Deep Dive into pvlib: Irradiance Decomposition and Transposition — The Complete Modeling Chain from GHI to Tilted Surface"
description: "The most error-prone step in the PV modeling chain. GHI → DNI + DHI (decomposition) → POA (transposition): each step offers multiple model choices. This article gives an in-depth analysis of 8 decomposition models and 7 transposition models in pvlib — covering mathematical principles, physical assumptions, applicable scenarios, and selection strategies."
pubDate: 2026-03-16
lang: en
category: solar
series: pvlib
tags: ['pvlib', 'irradiance', 'decomposition model', 'transposition model', 'Perez', 'Erbs', 'DISC']
---

## Introduction: Why Do We Need Irradiance Decomposition and Transposition?

PV modules are not mounted horizontally — they are typically tilted 20°–40° facing south (in the Northern Hemisphere). Yet the vast majority of ground-based irradiance monitoring stations only measure **Global Horizontal Irradiance (GHI)**. Getting from GHI to the irradiance on the module surface — the Plane of Array (POA) — requires two conversion steps:

$$\text{GHI} \xrightarrow{\text{decomposition}} \text{DNI} + \text{DHI} \xrightarrow{\text{transposition}} \text{POA}$$

These two steps seem straightforward, but each introduces significant error. Gueymard & Ruiz-Arias (2016), published in *Solar Energy* (CAS Q1), showed that the choice of decomposition model alone can cause 2–5% differences in annual energy yield estimates. For a 100 MW plant, that translates to millions of dollars in error.

---

## I. Basic Concepts

### The Three Irradiance Components

| Component | Symbol | Physical Meaning | Measurement |
|-----------|--------|-----------------|-------------|
| Global Horizontal Irradiance | GHI | Total solar radiation received on a horizontal surface | Thermopile pyranometer |
| Direct Normal Irradiance | DNI | Radiation from the solar disk direction | Pyrheliometer + solar tracker |
| Diffuse Horizontal Irradiance | DHI | Radiation scattered by the atmosphere reaching a horizontal surface | Shading disk/ball pyranometer |

The relationship among the three:

$$\text{GHI} = \text{DNI} \cdot \cos(\theta_z) + \text{DHI}$$

where $\theta_z$ is the solar zenith angle. This closure equation is the mathematical foundation of all decomposition models.

### Clearness Index $k_t$

$$k_t = \frac{\text{GHI}}{I_0 \cdot \cos(\theta_z)}$$

$k_t$ is the ratio of GHI to the extraterrestrial irradiance on a horizontal surface, ranging over [0, 1]. It is an integrated measure of atmospheric transparency:
- $k_t \approx 0.7$–$0.8$: clear sky
- $k_t \approx 0.3$–$0.5$: partly cloudy
- $k_t < 0.2$: overcast / stormy

**Nearly all decomposition models are functions of $k_t$** — they estimate the diffuse fraction $k_d = \text{DHI}/\text{GHI}$ from $k_t$ via empirical relationships.

---

## II. In-Depth Analysis of Decomposition Models

### 2.1 First Generation: Simple Empirical Relationships

#### Orgill & Hollands (1977)

One of the earliest decomposition models, based on four years of hourly data from Toronto. It uses a piecewise linear relationship:

$$k_d = \begin{cases} 1 - 0.249k_t & k_t < 0.35 \\ 1.557 - 1.84k_t & 0.35 \leq k_t \leq 0.75 \\ 0.177 & k_t > 0.75 \end{cases}$$

**Physical interpretation**:
- Low $k_t$ (overcast): nearly all radiation is diffuse, $k_d \approx 1$
- High $k_t$ (clear): diffuse fraction drops to ~18%
- Intermediate range: linear transition

**Limitation**: based on a single station; performs poorly in tropical and arid regions.

#### Erbs et al. (1982)

The default decomposition model in pvlib. An improvement over Orgill & Hollands using data from more stations, with a fourth-order polynomial fit for the intermediate range:

$$k_d = \begin{cases} 1 - 0.09k_t & k_t \leq 0.22 \\ 0.9511 - 0.1604k_t + 4.388k_t^2 - 16.638k_t^3 + 12.336k_t^4 & 0.22 < k_t \leq 0.80 \\ 0.165 & k_t > 0.80 \end{cases}$$

**Key implementation details in pvlib**:
- `min_cos_zenith=0.065` (truncates at zenith > 86.3° to avoid division by zero)
- `max_zenith=87` (sets DNI to 0 when the sun is near the horizon)
- DNI is back-calculated using the closure relation: $\text{DNI} = (\text{GHI} - \text{DHI})/\cos(\theta_z)$

**Key issue**: discontinuities in the derivative at $k_t = 0.22$ and $k_t = 0.80$ (the function is continuous but its first derivative is not). This can cause problems in optimization algorithms.

#### Erbs-Driesse (2024 Improvement)

Driesse re-parameterized the Erbs model, replacing the piecewise function with a smooth function to ensure **both the function and its first derivative are continuous at the breakpoints**. This is critical for gradient-based optimization and automatic differentiation (PyTorch/JAX).

```python
import pvlib
# Classic Erbs (piecewise, derivative discontinuous)
result_erbs = pvlib.irradiance.erbs(ghi, zenith, doy)

# Erbs-Driesse (smooth, differentiable)
result_driesse = pvlib.irradiance.erbs_driesse(ghi, zenith, doy)
```

### 2.2 Second Generation: Physics-Enhanced

#### DISC (Maxwell 1987)

Direct Insolation Simulation Code. Instead of estimating the diffuse fraction directly, DISC estimates DNI through the **direct clearness index $k_n$**:

$$k_n = \frac{\text{DNI}}{I_0}$$

DHI is then back-calculated from the closure relation. DISC uses a two-dimensional relationship between $k_t$ and air mass (AM), adding a physical dimension over pure $k_t$ models — it accounts for the effect of the atmospheric optical path length.

#### DIRINT (Perez et al. 1992)

An improvement over DISC that incorporates two additional inputs:
1. **Temporal GHI variability**: the rate of change in $k_t$ over adjacent time steps (dynamic cloud information)
2. **Dew point temperature**: a proxy for atmospheric water vapor content

These two inputs allow the model to distinguish between "thin cloud uniform scattering" and "thick cloud broken-channel effect" — two situations that may share the same instantaneous $k_t$ but have completely different DNI/DHI ratios.

**pvlib implementation**:
```python
# DIRINT requires more inputs but delivers higher accuracy
dni = pvlib.irradiance.dirint(
    ghi, zenith, times,
    pressure=101325,           # atmospheric pressure
    use_delta_kt_prime=True,   # use temporal stability index
    temp_dew=10                # dew point temperature
)
```

#### DIRINDEX (Perez 2002)

Extends DIRINT by incorporating **clear-sky model information**. It uses the Ineichen clear-sky GHI to compute a clear-sky clearness index and compares it with the actual $k_t$ — a large deviation indicates clouds, while a small deviation indicates attenuation from aerosols or water vapor.

**Why this matters**: both clouds and aerosols reduce GHI, but their effects on the DNI/DHI ratio are completely different — clouds primarily increase scattering, while aerosols simultaneously increase scattering and absorption.

### 2.3 Third Generation: Logistic Regression

#### Boland (2008/2013)

Replaces the piecewise function with logistic regression:

$$k_d = \frac{1}{1 + e^{-a(k_t - b)}}$$

Only two parameters, $a$ and $b$, and the function is naturally smooth and continuous. The elegance of the Boland model lies in:
- Automatically satisfying the physical constraint $k_d \in [0, 1]$
- Parameters that can be re-fitted for different climate zones
- Derivatives that exist everywhere, making it suitable for optimization

---

## III. In-Depth Analysis of Transposition Models

After decomposition, we have DNI, DHI, and GHI. The next step is to compute the irradiance on the tilted surface — POA:

$$\text{POA} = \text{POA}_{beam} + \text{POA}_{diffuse} + \text{POA}_{ground}$$

The beam component $\text{POA}_{beam} = \text{DNI} \cdot \cos(\text{AOI})$ is pure geometry. Ground reflection $\text{POA}_{ground} = \text{GHI} \cdot \rho \cdot (1 - \cos\beta)/2$ is also relatively straightforward. **The core challenge lies in modeling the angular distribution of sky diffuse radiation.**

### 3.1 Isotropic Model (Liu-Jordan 1963)

The simplest assumption: sky diffuse radiation is uniformly distributed.

$$\text{POA}_{diffuse} = \text{DHI} \cdot \frac{1 + \cos\beta}{2}$$

**Physical limitation**: real sky diffuse radiation is not uniform — there is circumsolar radiation around the sun and horizon brightening near the horizon. The isotropic model systematically underestimates POA by 5–10%.

### 3.2 Klucher (1979)

Adds modulating factors for circumsolar and horizon brightening on top of the isotropic model:

$$\text{POA}_{diffuse} = \text{DHI} \cdot \frac{1 + \cos\beta}{2} \cdot \left[1 + F\sin^3\left(\frac{\beta}{2}\right)\right] \cdot \left[1 + F\cos^2(\theta)\sin^3(\theta_z)\right]$$

where $F = 1 - (k_d)^2$ is the anisotropy factor. Under clear skies $F$ is large (strong anisotropy); under overcast skies $F$ is small (approaching isotropy).

### 3.3 Hay-Davies (1980)

Introduces the **anisotropy index** $A_I$:

$$A_I = \frac{\text{DNI}}{I_0}$$

Diffuse radiation is split into two parts: circumsolar radiation (fraction $A_I$, in the direction of the sun) + isotropic background (fraction $1 - A_I$).

$$\text{POA}_{diffuse} = \text{DHI} \left[A_I \cdot R_b + (1 - A_I) \cdot \frac{1 + \cos\beta}{2}\right]$$

$R_b = \cos(\text{AOI})/\cos(\theta_z)$ is the geometric transposition factor for beam radiation.

### 3.4 Perez (1987/1990)

The most complex and most accurate model. Sky diffuse radiation is divided into **three parts**:

$$\text{POA}_{diffuse} = \text{DHI} \left[(1 - F_1)\frac{1 + \cos\beta}{2} + F_1\frac{a}{b} + F_2\sin\beta\right]$$

- $(1-F_1)$: isotropic background
- $F_1 \cdot a/b$: circumsolar radiation ($a = \max(0, \cos\text{AOI})$, $b = \max(\cos 85°, \cos\theta_z)$)
- $F_2 \cdot \sin\beta$: horizon brightening

$F_1$ and $F_2$ are determined from two sky brightness parameters ($\varepsilon$ and $\Delta$) via a lookup table — 8 sky categories × 6 coefficients = 48 empirical coefficients.

**Perez-Driesse (2024)** improvement: replaces the lookup table with quadratic splines, eliminating discontinuities at sky-category transitions.

### 3.5 Model Selection Guide

| Scenario | Recommended Model | Reason |
|----------|------------------|--------|
| Quick estimate / teaching | Isotropic | Simplest; builds physical intuition |
| General engineering design | Hay-Davies | Good balance of accuracy and complexity |
| Precise energy yield estimation | Perez 1990 | Industry standard; used by PVsyst and other commercial software |
| Optimization / automatic differentiation | Perez-Driesse | Smooth and differentiable; compatible with PyTorch/JAX |
| Very limited data | Erbs + Isotropic | Lowest input requirements |

---

## IV. Complete Code Example

```python
import pvlib
import pandas as pd
import numpy as np
from pvlib.location import Location

# Define location: Beijing
site = Location(39.9, 116.4, tz='Asia/Shanghai', altitude=50)

# Generate a one-day time series
times = pd.date_range('2025-06-21 04:00', '2025-06-21 20:00',
                       freq='1min', tz='Asia/Shanghai')
solpos = site.get_solarposition(times)

# Clear-sky GHI (Ineichen-Perez model)
cs = site.get_clearsky(times, model='ineichen')
ghi = cs['ghi']

# === Step 1: Decomposition (GHI → DNI + DHI) ===
# Method A: Erbs (simple, default)
erbs_result = pvlib.irradiance.erbs(ghi, solpos['zenith'], times)

# Method B: DIRINT (accurate, requires additional inputs)
dirint_dni = pvlib.irradiance.dirint(
    ghi, solpos['zenith'], times,
    pressure=101325, temp_dew=15
)

# === Step 2: Transposition (DNI + DHI → POA) ===
surface_tilt = 30
surface_azimuth = 180  # facing south

# Method A: Isotropic (simplest)
poa_iso = pvlib.irradiance.get_total_irradiance(
    surface_tilt, surface_azimuth,
    solpos['apparent_zenith'], solpos['azimuth'],
    erbs_result['dni'], ghi, erbs_result['dhi'],
    model='isotropic'
)

# Method B: Perez (most accurate)
poa_perez = pvlib.irradiance.get_total_irradiance(
    surface_tilt, surface_azimuth,
    solpos['apparent_zenith'], solpos['azimuth'],
    erbs_result['dni'], ghi, erbs_result['dhi'],
    model='perez', airmass=site.get_airmass(times)['airmass_relative']
)

# Compare the difference
diff_pct = (poa_perez['poa_global'] - poa_iso['poa_global']) / poa_iso['poa_global'] * 100
print(f"Perez vs Isotropic daily mean difference: {diff_pct.mean():.1f}%")
print(f"Perez POA daily total irradiation: {poa_perez['poa_global'].sum() / 60 / 1000:.2f} kWh/m²")
```

---

## V. Error Propagation Analysis

Errors in decomposition and transposition propagate **multiplicatively**:

$$\sigma_{\text{POA}}^2 \approx \sigma_{\text{decomp}}^2 + \sigma_{\text{trans}}^2 + 2\rho\sigma_{\text{decomp}}\sigma_{\text{trans}}$$

Yang (2016), published in *Solar Energy* (Q1), found that:
- Typical MBE for decomposition models: ±2–5% (depending on climate zone)
- Typical MBE for transposition models: ±1–3%
- **Combined error**: up to ±8% in worst-case scenarios

**Most dangerous scenario**: high-latitude winter low-sun-angle + overcast conditions → decomposition models have maximum uncertainty in the low-$k_t$ regime, while large AOI amplifies transposition error simultaneously.

---

## VI. Connection to Warner's Textbook

Warner Ch. 4 covers radiation parameterization schemes — NWP models compute radiative transfer at each grid point, and the outputs are GHI/DNI/DHI. However, NWP resolution is 3–25 km, while PV plants require irradiance **at the module surface**.

pvlib's decomposition + transposition models are precisely the bridge connecting NWP output to PV modeling:
- NWP outputs GHI → pvlib decomposes to DNI + DHI → transposes to POA → power model
- Warner Ch. 13 MOS post-processing can be applied to GHI forecasts (removing systematic bias)
- Decomposition model error is a **non-negligible error source** in the NWP → PV forecast chain

---

## References

1. Erbs, D.G., Klein, S.A. & Duffie, J.A. (1982). Estimation of the diffuse radiation fraction for hourly, daily and monthly-average global radiation. *Solar Energy*, 28(4), 293-302.
2. Perez, R. et al. (1990). Modeling daylight availability and irradiance components from direct and global irradiance. *Solar Energy*, 44(5), 271-289.
3. Maxwell, E.L. (1987). A quasi-physical model for converting hourly GHI to DNI. *SERI/TR-215-3087*.
4. Perez, R. et al. (1992). Dynamic global-to-direct irradiance conversion models (DIRINT). *ASHRAE Trans.*, 98, 354-369.
5. Boland, J. et al. (2008). Modelling the diffuse fraction of global solar radiation on a horizontal surface. *Environmetrics*, 19, 120-136.
6. Gueymard, C.A. & Ruiz-Arias, J.A. (2016). Extensive worldwide validation and climate sensitivity analysis of direct irradiance predictions from 1-min global irradiance. *Solar Energy*, 128, 1-30.
7. Yang, D. (2016). Solar radiation on inclined surfaces: Corrections and benchmarks. *Solar Energy*, 136, 288-302.
8. Driesse, A. & Stein, J.S. (2024). Reformulation of the Erbs and Perez diffuse irradiance models for improved continuity. *pvlib documentation*.
