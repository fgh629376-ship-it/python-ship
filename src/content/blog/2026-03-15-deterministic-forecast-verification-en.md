---
title: "Complete Guide to Solar Forecast Verification — Is Your Model Actually Good?"
description: 'Deep dive into deterministic forecast verification: Skill Score with CLIPER reference, Murphy-Winkler distribution-oriented framework, MSE decomposition, and the quality-consistency-value trinity'
category: solar
series: solar-book
lang: en
pubDate: '2026-03-15'
tags: ["forecast verification", "skill score", "Murphy-Winkler", "MSE decomposition", "solar forecasting"]
---

## Is Your Forecast Model Any Good? That Question Is 100x Harder Than You Think

Everyone doing solar forecasting can compute RMSE. But you might not know: **the forecast with the lowest RMSE isn't necessarily the best one**. In a classic simulation experiment (Yang & Kleissl, 2024), three forecasters each rank "best" under different metrics — everyone can claim to be the winner.

This is why forecast verification deserves an entire chapter. Based on Chapter 9 of Yang & Kleissl (2024), this article builds a systematic verification mindset.

> Based on *Solar Irradiance and Photovoltaic Power Forecasting* (CRC Press, 2024) Chapter 9

---

## 1. Skill Score — Not About Error, But About How Much You Beat the Baseline

### 1.1 Why Skill Score?

Raw RMSE has a fatal flaw: **different locations and periods have different forecasting difficulty**. An RMSE of $50 \text{W/m}^2$ in a desert might be terrible (nearly always clear), while $100 \text{W/m}^2$ in a cloudy region might be excellent.

Skill Score compares your forecast against a "naïve" reference:

$$S^* = 1 - \frac{S_{\text{fcst}}}{S_{\text{ref}}}$$

### 1.2 Three Reference Methods

| Method | Principle | Best For |
|--------|-----------|----------|
| **Persistence** | Use latest observation | Short horizons (<3h) |
| **Climatology** | Use historical mean | Long horizons (>6h) |
| **CLIPER** | Optimal convex combination | **All horizons (recommended)** |

CLIPER's optimal weight: $\alpha_{\text{optimal}} = \gamma_h$ (lag-h autocorrelation). Mathematically proven:

$$\text{MSE}_{\text{CLIPER}} = (1 - \gamma_h^2) \cdot \sigma_K^2$$

$$\text{MSE}_{\text{CLIPER}} \leq \min(\text{MSE}_{\text{CLIM}},\; \text{MSE}_{\text{PERS}}) \quad \forall \; \gamma_h$$

**CLIPER is guaranteed to be no worse than either persistence or climatology.** Yang (2019) introduced this to the solar community, but as of 2024, most papers still use smart persistence.

### 1.3 Always Operate on $\kappa$ (Clear-Sky Index)

- $\kappa$ = observation / clear-sky model output
- Apply persistence/climatology/CLIPER to $\kappa$, then back-transform
- Direct application to GHI **inflates skill scores** (diurnal cycle is "free" predictability)

---

## 2. The Fatal Limitation of Measure-Oriented Verification

### 2.1 Classic Experiment: Three Forecasters, Three "Champions"

| Forecaster | Strategy | MBE | MAE | RMSE |
|-----------|----------|-----|-----|------|
| Novice | Persistence | **-2.85** ✓ | 79.63 | 142.36 |
| Optimist | Constant 0.95 | 36.19 | **57.68** ✓ | 119.81 |
| Statistician | Conditional mean | 8.72 | 63.02 | **111.77** ✓ |

**Each forecaster "wins" under one metric.** The conclusion depends entirely on which metric you choose.

### 2.2 The Fix

**Report forecast-observation pairs**, not just summary statistics. Let readers conduct their own verification.

---

## 3. Murphy-Winkler Distribution-Oriented Framework

The joint distribution $f(x,y)$ contains **all information** needed for verification.

### 3.1 Two Factorizations

**Calibration-Refinement**: $f(x,y) = f(y|x) \cdot f(x)$
- $f(y|x)$ → **Calibration**: $E(Y|X=x) = x$ is perfectly calibrated
- $f(x)$ → **Resolution**: Higher forecast diversity = better

**Likelihood-Base Rate**: $f(x,y) = f(x|y) \cdot f(y)$
- $f(x|y)$ → **Consistency/Type 2 bias**: $E(X|Y=y) = y$ is perfectly consistent
- $f(y)$ → **Base rate**: Marginal distribution of observations

### 3.2 MSE Decompositions

**COF decomposition**:

$$\text{MSE} = V(Y) + E_X[X - E(Y|X)]^2 - E_X[E(Y|X) - E(Y)]^2$$

i.e., $\text{MSE} = \text{Obs. variance} + \text{Type 1 bias (minimize)} - \text{Resolution (maximize)}$

**COX decomposition**:

$$\text{MSE} = V(X) + E_Y[Y - E(X|Y)]^2 - E_Y[E(X|Y) - E(X)]^2$$

i.e., $\text{MSE} = \text{Fcst. variance} + \text{Type 2 bias (minimize)} - \text{Discrimination (maximize)}$

Four dimensions, four targets — no single metric captures all.

---

## 4. Case Study: ECMWF HRES vs NCEP NAM

Three SURFRAD stations (BON/DRA/PSU), 2020, day-ahead GHI forecasts.

### 4.1 Quality Assessment

| Metric | HRES Wins | NAM Wins |
|--------|-----------|----------|
| MAE/RMSE (accuracy) | ✅ | |
| Marginal distribution similarity | | ✅ |
| Calibration | ✅ | |
| Type 2 conditional bias | | ✅ |
| Resolution | ✅ | |
| Discrimination | | ✅ |

**Neither model dominates across all quality dimensions.** This is the norm, not the exception.

### 4.2 Consistency

Linear correction with three objective functions (MAE/MSE/MAPE minimization) + cross-evaluation confirms: **training objective must match evaluation metric**.

> If the grid operator penalizes by RMSE, train with MSE. Mismatched training and evaluation is wasted compute.

### 4.3 Value Assessment

The most striking finding: **quality-value correspondence is nonlinear**.

- 9% MAE difference → **5× penalty difference**
- MAPE-optimal forecasts receive the **highest** penalty

**Conclusion**: Better quality ≠ higher value. Forecasting serves decision-making, not paper-publishing.

---

## 5. Practical Checklist

1. **Reference method**: Use CLIPER, not smart persistence
2. **Operate on κ**: All computations in clear-sky index space
3. **Plot scatter diagrams**: Check alignment, outliers, overall bias
4. **Report f-o pairs**: Enable reproducible verification
5. **Murphy-Winkler decomposition**: Calibration / Resolution / Type 2 bias / Discrimination
6. **Ensure consistency**: Training objective = evaluation metric = grid penalty rule
7. **Quantify value**: Use actual penalty schemes for economic assessment

---

## References

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press. Ch. 9.
- Murphy, A.H. & Winkler, R.L. (1987). *Monthly Weather Review*, 115, 1330-1338. (Q1)
- Murphy, A.H. (1993). *Weather and Forecasting*, 8(2), 281-293. (Q1)
- Yang, D. et al. (2020). *Solar Energy*, 210, 20-37. (Q1)
- Kolassa, S. (2020). *International Journal of Forecasting*, 36(1), 208-211. (Q1)
