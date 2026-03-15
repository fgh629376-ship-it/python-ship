---
title: 'pvlib in Practice: Clear-Sky Models — The Cornerstone of PV Forecasting'
description: 'The clear-sky model is the single most important tool in PV forecasting. This article uses pvlib to compare Ineichen, Haurwitz, and Simplified Solis models hands-on, exploring the physical meaning and engineering applications of the clear-sky index κ.'
pubDate: 2026-03-15
lang: en
category: solar
series: pvlib
tags: ['pvlib', 'clear-sky model', 'PV forecasting', 'Clear Sky', 'Ineichen', 'clear-sky index']
---

## Why Are Clear-Sky Models the Cornerstone of PV Forecasting?

A key fact from GEFCom2014 (the Global Energy Forecasting Competition): **the only team that used a clear-sky model = the champion**. Every other team's forecasts "paled in comparison."

A clear-sky model tells you: **if the sky were completely cloudless today, how much solar irradiance should the ground receive?** With this baseline, the forecasting problem simplifies from "what will GHI be tomorrow?" to "how much will clouds attenuate tomorrow?"—the latter is a much smaller, easier-to-model problem.

Core formula:

$$\kappa = \frac{\text{GHI}}{\text{GHI}_{\text{clear}}}$$

The clear-sky index $\kappa$ removes the seasonal and diurnal cycles driven by solar position, letting the forecasting model focus solely on weather variability.

---

## The Three Major Clear-Sky Models in pvlib

pvlib provides three clear-sky models with increasing complexity and accuracy:

| Model | Input Parameters | Accuracy | Use Case |
|-------|-----------------|----------|----------|
| **Haurwitz** | Zenith angle only | ⭐⭐ | Quick estimation, education |
| **Simplified Solis** | Zenith angle + aerosol + water vapor + pressure | ⭐⭐⭐ | Moderate accuracy needs |
| **Ineichen-Perez** | Zenith angle + Linke turbidity | ⭐⭐⭐⭐ | Operational forecasting (recommended) |

---

## Full Code Walkthrough

### 1. Basic Setup

```python
import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Shanghai site
latitude, longitude = 31.23, 121.47
altitude = 4  # elevation (m)

# Summer solstice 2024
times = pd.date_range(
    '2024-06-21 00:00', '2024-06-21 23:59',
    freq='1min', tz='Asia/Shanghai'
)

# Calculate solar position
location = pvlib.location.Location(latitude, longitude, altitude=altitude)
solar_position = location.get_solarposition(times)
```

### 2. Comparing Three Clear-Sky Models

```python
# === Haurwitz (simplest — only needs zenith angle) ===
cs_haurwitz = location.get_clearsky(times, model='haurwitz')

# === Ineichen-Perez (recommended — needs Linke turbidity) ===
# pvlib automatically retrieves monthly mean Linke turbidity from the SoDa database
cs_ineichen = location.get_clearsky(times, model='ineichen')

# === Simplified Solis (needs aerosol optical depth) ===
cs_solis = location.get_clearsky(
    times, model='simplified_solis',
    aod700=0.1,          # aerosol optical depth at 700 nm
    precipitable_water=2.0,  # precipitable water (cm)
    pressure=101325      # pressure (Pa)
)
```

### 3. Visualization Comparison

```python
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

components = ['ghi', 'dni', 'dhi']
titles = ['GHI (Global Horizontal Irradiance)', 'DNI (Direct Normal Irradiance)', 'DHI (Diffuse Horizontal Irradiance)']

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

axes[-1].set_xlabel('Time (Shanghai, 2024-06-21)')
plt.suptitle('Comparison of Three Clear-Sky Models — Shanghai Summer Solstice', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('clearsky_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 4. Calculating and Applying the Clear-Sky Index κ

```python
# Simulate actual irradiance for a day (with cloud effects added)
np.random.seed(42)
cloud_factor = np.ones(len(times))

# Simulate a scenario: clear morning, cloudy afternoon
for i, t in enumerate(times):
    hour = t.hour + t.minute / 60
    if 12 < hour < 16:
        # Afternoon cloud obstruction
        cloud_factor[i] = 0.3 + 0.4 * np.random.random()
    elif 10 < hour < 12:
        # Intermittent morning clouds
        cloud_factor[i] = 0.7 + 0.3 * np.random.random()

# Actual GHI = clear-sky GHI × cloud factor
ghi_actual = cs_ineichen['ghi'] * cloud_factor

# Calculate clear-sky index κ
kappa = ghi_actual / cs_ineichen['ghi'].replace(0, np.nan)

# Visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

ax1.plot(times, cs_ineichen['ghi'], label='Clear-Sky GHI', color='orange', linewidth=2)
ax1.plot(times, ghi_actual, label='Actual GHI', color='steelblue', alpha=0.8)
ax1.fill_between(times, ghi_actual, cs_ineichen['ghi'],
                  alpha=0.2, color='red', label='Cloud Attenuation Loss')
ax1.set_ylabel('GHI (W/m²)')
ax1.legend()
ax1.set_title('Clear-Sky Model vs Actual Irradiance')

ax2.plot(times, kappa, color='green', linewidth=1)
ax2.axhline(y=1.0, color='orange', linestyle='--', alpha=0.5, label='κ=1 (perfect clear sky)')
ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='κ=0.5 (partly cloudy)')
ax2.set_ylabel('Clear-Sky Index κ')
ax2.set_xlabel('Time')
ax2.set_ylim(0, 1.3)
ax2.legend()
ax2.set_title('Clear-Sky Index κ = GHI / GHI_clear')

plt.tight_layout()
plt.savefig('clearsky_index.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 5. Effect of Linke Turbidity

```python
# Linke turbidity: an atmospheric transparency indicator
# Higher value → more turbid atmosphere → lower clear-sky irradiance
linke_values = [2.0, 3.5, 5.0, 7.0]
labels = ['Very clean (TL=2)', 'Typical (TL=3.5)', 'Polluted (TL=5)', 'Heavily polluted (TL=7)']

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
ax.set_xlabel('Time')
ax.set_title('Effect of Linke Turbidity on Clear-Sky GHI')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('linke_turbidity.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 6. Multi-Site Clear-Sky Comparison

```python
# Clear-sky model differences across climate zones
sites = {
    'Shanghai (Humid Subtropical)': (31.23, 121.47, 4),
    'Dunhuang (Arid Desert)': (40.14, 94.68, 1139),
    'Lhasa (High Plateau)': (29.65, 91.10, 3650),
}

fig, ax = plt.subplots(figsize=(12, 5))

for name, (lat, lon, alt) in sites.items():
    loc = pvlib.location.Location(lat, lon, altitude=alt)
    cs = loc.get_clearsky(times, model='ineichen')
    ax.plot(times, cs['ghi'], label=name, linewidth=2)

ax.set_ylabel('GHI (W/m²)')
ax.set_xlabel('Time (2024-06-21)')
ax.set_title('Clear-Sky GHI Comparison Across Different Sites')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('multi_site_clearsky.png', dpi=150, bbox_inches='tight')
plt.show()
```

---

## Clear-Sky Model Selection Guide

> **Textbook conclusion (Yang & Kleissl, Ch5.4)**: The performance differences between clear-sky models are **far smaller** than the differences between sites. The choice of clear-sky model is only marginally important.

Practical recommendations:

1. **Operational forecasting** → **Ineichen-Perez** (no time restrictions, just a few lines of code)
2. **Research validation** → **REST2** (requires MERRA-2 aerosol data, highest accuracy)
3. **Rapid prototyping** → **Haurwitz** (zero exogenous parameters, but does not output DNI/DHI)

---

## Key Takeaways

- The $\kappa$ distribution is typically **bimodal**: a clear-sky peak at $\approx 1.0$ and a cloudy-sky peak at $\approx 0.3$–$0.5$
- **Multiplicative decomposition** ($\kappa = \text{GHI}/\text{GHI}_{\text{clear}}$) is superior to additive decomposition
- $\kappa > 1$ is physically valid! **Cloud enhancement** can cause instantaneous GHI to exceed the clear-sky value by ~50%
- The clear-sky index is not exclusive to GHI — you can define $\kappa_{\text{BNI}}, \kappa_{\text{POA}}, \kappa_{\text{PV}}$
- When forecasting with $\kappa$, **clear-sky normalization must be applied first**; otherwise the model learns sunrise/sunset patterns rather than weather variability

---

## References

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and PV Power Forecasting*, Ch4.5 & Ch5.4. CRC Press.
- Ineichen, P. & Perez, R. (2002). A new airmass independent formulation for the Linke turbidity coefficient. *Solar Energy*, 73(3), 151-157.
- Sun, X. et al. (2019). Worldwide performance assessment of 75 global clear-sky irradiance models. *Solar Energy*, 187, 392-404.
- Gueymard, C.A. (2008). REST2: High-performance solar radiation model. *Solar Energy*, 82(3), 272-285.
