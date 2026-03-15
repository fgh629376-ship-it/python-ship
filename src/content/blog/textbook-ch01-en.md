---
title: 'Textbook Notes Ch1: Why We Do Solar Forecasting'
description: 'Forecasting serves decision-making, not academic publishing. PV intermittency disrupts grid balance; forecasting is the lowest-cost means to restore it.'
pubDate: 2026-03-14
lang: en
category: solar
series: solar-book
tags: ['Textbook Notes', 'Ch1', 'Solar Forecasting', 'Grid Integration']
---

> 📖 [Back to Index](/textbook/solar/)
> 📚 《Solar Irradiance and PV Power Forecasting》Chapter 1, p1-25

---

## 1.1 Five Dimensions of Solar Forecasting

The textbook opens with a clear statement: **forecasting exists to serve decision-making**, not to produce publications. The intermittency of solar PV disrupts the generation-load balance of power grids, and forecasting is the **lowest-cost means** to restore that balance.

The economic value of accuracy is enormous — every 1% improvement in forecast accuracy can save millions of dollars across a large grid.

### 1.1.1 Base Methods

The five foundational methods for solar forecasting, ordered by forecast horizon:

| Method | Forecast Horizon | Data Source |
|--------|-----------------|-------------|
| Sky Camera (ASI) | Minutes (~30 min) | Ground-level fisheye camera |
| Satellite | Intra-day (~4h) | Meteorological satellite imagery |
| NWP (Numerical Weather Prediction) | Day-ahead (1–15 days) | Atmospheric motion equations |
| Statistical Methods | Flexible | Historical time-series data |
| Machine Learning | Flexible | Multi-source data fusion |

### 1.1.2 Post-processing

Post-processing is the bridge between raw forecasts and final products. The textbook defines 10 categories of post-processing techniques, organized into four quadrants by input/output type — deterministic (D) or probabilistic (P):

```
Input \ Output | Deterministic (D)              | Probabilistic (P)
Deterministic (D) | D2D: regression/filtering/downscaling | D2P: ensemble simulation/dressing/probabilistic regression
Probabilistic (P) | P2D: aggregate distribution/combining | P2P: calibration/combining probabilities
```

### 1.1.3 Verification

Murphy (1993) proposed three dimensions of forecast quality:
1. **Consistency**: Does the forecaster believe their own forecasts?
2. **Quality**: How well do forecasts match observations?
3. **Value**: How much do forecasts help decision-making?

### 1.1.4 Irradiance-to-Power Conversion

Converting irradiance forecasts to power forecasts is not a simple multiplication — it requires a Model Chain:
- Solar position → Decomposition model → Transposition model → Temperature model → PV model

### 1.1.5 Grid Integration

Forecasting ultimately serves grid operations:
- **Day-Ahead Market (DAM)**: requires 36h+ forecasts
- **Real-Time Market (RTM)**: requires 4h+ forecasts
- **Frequency regulation**: requires minute-level forecasts

---

## 1.2 Book Outline

### 1.2.1 Understanding Before Acting

The textbook's philosophy: **don't rush to run models**. First understand the physical foundations, statistical theory, and practical standards of forecasting.

### 1.2.2 Grid Integration and Firm Power Delivery

The textbook's ultimate goal is not merely improving forecast accuracy, but achieving **Dispatchable Solar Power** — using forecasting + storage + dispatch to make solar PV deliver power as reliably as a conventional power plant.

---

## 📋 Key Takeaways

| Point | Content |
|-------|---------|
| Purpose of forecasting | Serves grid decision-making, not publishing |
| Economic value | 1% accuracy gain = millions of dollars per large grid |
| Five base methods | ASI / Satellite / NWP / Statistical / ML |
| 10 post-processing types | D2D / D2P / P2D / P2P quadrants |
| Three quality dimensions | Consistency / Quality / Value |
| Ultimate goal | Dispatchable Solar Power |

> 📖 [Back to Index](/textbook/solar/) | [Next Chapter →](/blog/textbook-ch02/)
