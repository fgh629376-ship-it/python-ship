---
title: "Probabilistic Forecast Verification — Calibration, Sharpness, and Proper Scoring Rules"
description: "Deep dive into probabilistic forecast verification: PIT/Rank histograms, Reliability Diagrams, CRPS/Brier Score/IGN scoring rules, and the calibration-sharpness paradigm"
category: solar
series: solar-book
lang: en
pubDate: '2026-03-15'
tags: ["probabilistic forecasting", "CRPS", "Brier Score", "calibration", "solar forecasting"]
---

## From "Predicting a Number" to "Predicting a Distribution"

Deterministic forecasts tell you "tomorrow's GHI is 500 W/m²." Probabilistic forecasts tell you "there's a 90% chance GHI will be between 350-650 W/m²." The latter is far more useful for grid operations — dispatchers need to know **how uncertain things are** to decide on reserve capacity.

But verifying probabilistic forecasts is much harder than deterministic ones. You can't simply compute RMSE when the forecast is a distribution, not a number. Based on Chapter 10 of Yang & Kleissl (2024).

> Based on *Solar Irradiance and Photovoltaic Power Forecasting* (CRC Press, 2024) Chapter 10

---

## 1. The Core Paradigm: Maximize Sharpness Subject to Calibration

### 1.1 Calibration

**Definition**: Statistical consistency between predictive distributions and observations.

Intuition: If you issue 100 forecasts saying "70% chance of rain," it should actually rain about 70 times.

Mathematically, perfect calibration means PIT follows a uniform distribution:
$$p_t = F_t(y_t) \sim U(0,1)$$

### 1.2 Sharpness

**Definition**: Concentration of predictive distributions — narrower is sharper.

Key distinction: Sharpness is a property of **forecasts only**, not involving observations.

### 1.3 Why Both Matter

- **Calibration alone**: Always issue climatology → perfectly calibrated but zero information
- **Sharpness alone**: Issue a spike distribution → sharp but may completely miss observations

> **Gneiting's paradigm**: Maximize sharpness **subject to calibration**. The overarching principle of probabilistic forecasting.

---

## 2. Strictly Proper Scoring Rules

A scoring rule assigns a numerical value based on a probabilistic forecast and an observation. **Strictly proper** means: the forecaster achieves the best expected score by reporting their true belief. No incentive to hedge.

### 2.1 CRPS — The Core Score for Continuous Variables

$$\text{crps}(F, y) = \int_{-\infty}^{\infty} [F(x) - \mathbb{1}(x \geq y)]^2 \, dx$$

Key properties:
- Strictly proper
- Reduces to MAE for deterministic (point) forecasts
- CRPS = integral of Brier Score over all thresholds
- Simultaneously assesses calibration and sharpness
- Decomposable: **CRPS = Reliability - Resolution + Uncertainty**

### 2.2 Brier Score (Binary Events)

$$\text{bs}(p, y) = (p - y)^2$$

Decomposable into reliability + resolution + uncertainty (Murphy, 1973).

### 2.3 IGN (Ignorance Score / Log Score)

$$\text{ign}(f, y) = -\log f(y)$$

Local property: only evaluates the PDF at the observation point. Complements CRPS's global assessment.

### 2.4 Quantile Score (Pinball Loss)

Evaluates individual quantiles. CRPS = 2 × ∫ QS_τ dτ.

### 2.5 Consistency Principle

- Evaluate with CRPS → train by minimizing CRPS
- Evaluate with IGN → train by maximizing log-likelihood
- **Mixing objectives leads to suboptimal results**

---

## 3. Visual Assessment Tools

### 3.1 Rank Histogram (Ensemble Forecasts)

Insert observation into sorted ensemble members, count the rank.

- **Flat** → well calibrated
- **U-shaped** → under-dispersed (most common NWP deficiency)
- **Inverted U** → over-dispersed
- **Skewed** → biased

### 3.2 PIT Histogram (Distributional Forecasts)

PIT = F_t(y_t). Should be U(0,1) for calibrated forecasts. Continuous analog of rank histogram.

### 3.3 Reliability Diagram (Recommended)

The "go-to" visual tool (Lauret et al., 2019):
- x-axis: nominal probability τ
- y-axis: observed proportion z̄_τ
- Perfect calibration → points on diagonal
- Add **consistency bands** to quantify sampling uncertainty

### 3.4 Sharpness Diagram

Box plots of prediction interval width at various nominal coverage rates. A property of forecasts only.

---

## 4. Case Study: ECMWF 50-Member Ensemble Post-Processing

### Key Findings

1. **Raw ensemble → U-shaped rank histogram** → under-dispersed → P2P post-processing needed
2. **NGR1 best under CRPS, NGR2 best under IGN** → empirical validation of propriety theory
3. **QR produces flattest PIT histogram** → nonparametric calibration advantage
4. **No single method dominates all aspects** — the recurring theme

### CRPS Results (W/m²)

| Method | BON | DRA | PSU |
|--------|-----|-----|-----|
| Raw EPS | 55.5 | 34.2 | 60.0 |
| NGR1 (CRPS-opt) | **50.6** | **24.2** | **54.4** |
| QR | 49.1 | 25.0 | 54.6 |
| BMA | 56.3 | 28.5 | 59.9 |

---

## 5. Practical Checklist

1. **Primary score**: Use CRPS (strictly proper, decomposable, reduces to MAE for deterministic)
2. **Check calibration**: PIT/Rank histogram + Reliability Diagram with consistency bands
3. **Check sharpness**: Sharpness diagram conditioned on coverage rate
4. **Consistency**: Match training objective to evaluation metric
5. **Always post-process**: Raw NWP ensembles are almost always under-dispersed
6. **Never use non-proper scores** (e.g., CWC) — they incentivize hedging

---

## References

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press. Ch. 10.
- Gneiting, T. et al. (2007). *JRSS-B*, 69(2), 243-268. (Q1)
- Gneiting, T. & Raftery, A.E. (2007). *JASA*, 102(477), 359-378. (Q1)
- Hersbach, H. (2000). *Weather and Forecasting*, 15, 559-570. (Q1)
- Lauret, P. et al. (2019). *Solar Energy*, 194, 254-271. (Q1)
