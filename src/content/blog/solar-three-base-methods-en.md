---
title: 'NWP vs Satellite vs Ground Data: The Physics Behind Solar Forecasting''s Three Base Methods'
description: 'From primitive equations to cloud motion vectors — a deep dive into the physics, scope, and engineering strategy for the three fundamental solar forecasting methods'
pubDate: 2026-03-14
category: 'solar'
tags: ['solar-forecasting', 'NWP', 'satellite', 'CMV', 'pvlib']
lang: 'en'
series: 'solar-book'
---

# NWP vs Satellite vs Ground Data: The Physics Behind the Three Base Methods

> 📖 Based on Chapter 7 of *Solar Irradiance and Photovoltaic Power Forecasting* (Yang & Kleissl, 2024), with practical engineering perspectives.

"Base methods" in solar forecasting are those that generate **raw forecasts** — before any post-processing refinement. They are the foundation of the entire forecasting pipeline.

The three base methods, ranked by importance:

| Method | Effective Range | Core Physics | Irreplaceability |
|--------|----------------|-------------|------------------|
| **NWP** | Day-ahead ~ multi-day | Solving atmospheric dynamics | ⭐⭐⭐ Only option |
| **Satellite** | 15min ~ 4h | Cloud motion vector advection | ⭐⭐ Critical intra-day supplement |
| **Ground data** | 1min ~ 1h | Time series / spatial correlation | ⭐ Ultra-short-term refinement |

---

## 1. NWP: The Only Method That "Solves" the Atmosphere

### 1.1 Seven Equations, Five Physical Laws

At the core of Numerical Weather Prediction lie the **Primitive Equations** — 7 equations solving for 7 variables (u, v, w, T, q, ρ, p):

① Newton's 2nd Law → 3 momentum equations (predicting 3D wind)

$$\frac{Du}{Dt} = -\frac{\nabla p}{\rho} + f \times u + F_{\text{friction}}$$

② 1st Law of Thermodynamics → Temperature prediction ($\theta$ = potential temperature, $Q$ = heating rate)

$$\frac{D\theta}{Dt} = \frac{\theta}{T} \cdot \frac{Q}{c_p}$$

③ Water vapor conservation → Moisture prediction ($E$ = evaporation, $C$ = condensation)

$$\frac{Dq}{Dt} = E - C$$

④ Mass conservation → Continuity equation

⑤ Ideal gas law → Diagnostic relation (no time derivative)

$$p = \rho R T$$

The first 6 are **prognostic equations** (containing D/Dt, the Lagrangian total derivative); the 7th is **diagnostic**.

### 1.2 Parameterization: NWP's Achilles' Heel

The primitive equations only describe grid-scale (>10km) processes. Sub-grid processes must be approximated through parameterization schemes.

Six key parameterizations ranked by impact on solar forecasting:

| Scheme | Role | Impact on Irradiance |
|--------|------|---------------------|
| **Cloud microphysics** | Condensation, coalescence, precipitation | ⭐⭐⭐ Determines cloud amount |
| **Convection** | Sub-grid vertical heat/moisture transport | ⭐⭐⭐ Cumulus lifecycle → GHI |
| **PBL** | Boundary layer vertical mixing | ⭐⭐ Low-level moisture → cloud base |
| **Land-atmosphere** | Surface energy balance | ⭐⭐ Soil moisture → evaporation → clouds |
| **Radiation** | Radiative transfer computation | ⭐ Mature physics, NOT the bottleneck |
| **Aerosol** | Atmospheric chemistry | ⭐ Only matters in extreme events |

> ⚠️ **Counter-intuitive finding**: The radiation scheme seems most relevant but is NOT the bottleneck. Radiative transfer physics is mature — it just converts cloud water content to surface irradiance. The real bottleneck is **cloud microphysics**: clouds form at micrometer scales (CCN + supersaturation → condensation → coalescence → precipitation), while NWP grids are kilometer-scale. This scale gap is the primary source of NWP irradiance forecast errors.

### 1.3 Discretization and Data Assimilation

**Discretization**: Converting continuous PDEs into solvable algebraic equations.
- Finite differences: Du/Dt ≈ Δu/Δt, staggered grids for accuracy
- Spectral methods: Spherical harmonic decomposition (ECMWF IFS uses Tco1279 ≈ 31.4km)
- CFL condition: Δt ≤ Δx/c — 10km grid → Δt < 100 seconds

**Data Assimilation (4D-Var)**: Using observations to correct the model's initial conditions. The NWP forecast provides a physically consistent prior; observations provide evidence; 4D-Var finds the optimal compromise.

---

## 2. Satellite Forecasting: The 4-Hour Window

### 2.1 Satellite-to-Irradiance Conversion

Three approaches:

**Physical (FARMS/NSRDB)**: `Gh = η·Gho + (1-η)·Ghc` — cloud fraction weighted combination of overcast and clear-sky GHI. Requires cloud properties (GOES), atmospheric profiles (MERRA-2), aerosols (MODIS). FARMS achieves 1000× speedup via lookup tables.

**Semi-empirical (Heliosat-2/SolarGIS/SolarAnywhere)**: `Gh = g(ν)·Ghc` — maps cloud index ν to clear-sky index κ via a simple piecewise function. Uses only the visible channel, achieving 0.5km resolution. The workhorse of commercial solar resource assessment.

**Pure ML**: Random Forest/CNN directly regressing satellite channels to GHI. Lower accuracy but valuable for new satellites lacking mature cloud property products.

### 2.2 Cloud Motion Vectors: The Core

Satellite forecasting extracts current cloud motion, assumes clouds remain "frozen" short-term, and advects the irradiance field forward.

**Lucas-Kanade optical flow**: Brightness constancy $I(x,y,t) = I(x+\Delta x, y+\Delta y, t+\Delta t)$ → optical flow equation $I_x U + I_y V = -I_t$ → solve $(U,V)$ via neighborhood least squares.

**Block matching (three-step search)**: Find maximum cross-correlation blocks between consecutive frames.

> ⚠️ **The 4-hour limit**: The "frozen cloud field" assumption degrades after 15-30 min and fails completely by 4h. Satellite methods **cannot generate new clouds** — only NWP can simulate the full cloud lifecycle.

---

## 3. Ground-Based Forecasting: The Limits of Time Series

### 3.1 Reference Forecasts (Must-Beat Baselines)

```
Persistence: $\hat{\kappa}(t+h) = \kappa(t)$

Smart Persistence: $\widehat{\text{GHI}}(t+h) = \kappa(t) \times G_{hc}(t+h)$
Climatology:      κ̂(t+h) = mean(κ_historical)
CLIPER: $\hat{\kappa}(t+h) = \gamma_h \cdot \kappa(t) + (1 - \gamma_h) \cdot \bar{\kappa}$
```

CLIPER is the strongest simple baseline — it optimally blends persistence (short-term) and climatology (long-term) based on the autocorrelation $\gamma_h$.

### 3.2 The Information-Theoretic Limit

No matter how sophisticated the model (LSTM, Transformer), single-site methods hit a fundamental wall: **as forecast horizon $h$ increases, the autocorrelation $\gamma_h$ between $\kappa(t)$ and $\kappa(t+h)$ approaches zero.** No model can extract information from an input that contains none.

### 3.3 Spatiotemporal Methods

STAR (Space-Time AR), Kriging, and Graph Neural Networks exploit multi-site spatial correlations, but these also decay rapidly with distance and time. Beyond 4h, only NWP brings new information.

---

## 4. Engineering Strategy: Blend All Three

```
Optimal Pipeline:
  Ultra-short (0-30min) → Ground data (real-time correction)
  Intra-day   (30min-4h) → Satellite CMV (cloud motion)
  Day-ahead   (4h-3 days) → NWP (only option)
  Multi-day   (3+ days)   → NWP ensemble forecasts

All horizons need:
  → Clear-sky normalization (κ = GHI/Ghc)
  → Post-processing (MOS/ML)
  → Probabilistic calibration (quantile regression / ensembles)
```

It's not about choosing one method — it's about knowing **which method for which horizon**.

---

## References

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press.
- Xie, Y. et al. (2016). A Fast All-sky Radiation Model for Solar applications (FARMS). *Solar Energy*, 135.
- Rigollier, C. et al. (2004). Heliosat-2 for deriving shortwave solar radiation. *Solar Energy*, 77(2).
- Lucas, B. & Kanade, T. (1981). An iterative image registration technique. *IJCAI*.
- Sengupta, M. et al. (2018). The National Solar Radiation Data Base (NSRDB). *RSER*, 89.
