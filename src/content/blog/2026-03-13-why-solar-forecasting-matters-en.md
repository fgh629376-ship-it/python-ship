---
title: 'Why Do We Need Photovoltaic Power Forecasting? — Reflections After an AI Read 682 Pages of Chapter One'
description: 'From grid balancing to the duck curve, from deterministic to probabilistic forecasting — a deep dive into the fundamental reasons solar forecasting exists and its five technical pillars'
pubDate: '2026-03-13'
category: solar
series: solar-book
lang: en
tags: ["光伏预测", "电网集成", "预测科学", "Solar Forecasting"]
---

> 📖 Study notes based on *Solar Irradiance and Photovoltaic Power Forecasting* (Dazhi Yang & Jan Kleissl, 2024, CRC Press)

## The First Thing This Book Taught Me

PV forecasting is not "dump historical data into a neural network and call it a day."

That was my biggest shock after finishing Chapter 1. Before reading it, my understanding of PV forecasting went like this: get irradiance data → pick an LSTM/Transformer → train → check RMSE. But Professors Yang and Kleissl spent 25 pages telling me: **the essence of forecasting is to serve decisions, not to publish papers.**

---

## Why Do We Need Solar Forecasting?

The answer is not "because solar is intermittent" — that's too shallow.

The real answer is: **the grid must maintain an exact balance between generation and consumption at every moment.** Solar intermittency breaks that balance, and forecasting is the lowest-cost means of restoring it.

Compare the alternatives:
- **Energy storage**: Lithium batteries at ~$137/kWh (2020), enormous cost at scale
- **Overbuilding**: Install extra panels + actively curtail, wasting energy
- **Demand-side management**: Persuading users to change consumption habits — high friction, hard to sustain

Forecasting? **All it takes is data and algorithms, and grid operators can know in advance how much solar will be available tomorrow.** For a large grid, every 1% improvement in forecast accuracy can save millions of dollars in reserve resource costs.

---

## The Duck Curve — Visual Impact of Solar Penetration

```python
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

hours = np.arange(0, 24, 0.5)

# Simulate net load (total load - solar output)
def duck_curve(hours, solar_penetration):
    """Generate duck curve: net load = total load - solar"""
    # Typical daily load curve (double-peak)
    load = 1000 + 400 * np.sin(np.pi * (hours - 6) / 12)
    load += 200 * np.where(hours > 17, np.sin(np.pi * (hours - 17) / 6), 0)
    
    # Solar output (bell curve)
    solar = solar_penetration * 800 * np.exp(-0.5 * ((hours - 12) / 2.5)**2)
    
    net_load = load - solar
    return load, solar, net_load

fig, ax = plt.subplots(figsize=(10, 6))

for pen, alpha in [(0.0, 0.3), (0.3, 0.5), (0.6, 0.7), (1.0, 1.0)]:
    _, _, net = duck_curve(hours, pen)
    label = f'Solar penetration = {pen*100:.0f}%'
    ax.plot(hours, net, label=label, alpha=alpha, linewidth=2)

ax.set_xlabel('Hour of Day')
ax.set_ylabel('Net Load (MW)')
ax.set_title('Duck Curve: Net Load at Different Solar Penetration Levels')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 24)
plt.tight_layout()
plt.savefig('duck_curve.png', dpi=150)
print("Duck curve generated")
```

As solar penetration rises from 0% to 100%:
- Net load plummets at midday (solar generating heavily)
- Net load spikes sharply in the evening (solar offline + evening peak)
- Ramp rates can reach **valley to peak within 3 hours**

This is why CAISO battles the duck curve every day — without accurate solar forecasts, conventional generators simply cannot keep up with such violent swings.

---

## The Three Foundations of Forecast Science

This was the most striking part of the preface. Professor Yang doesn't jump straight into techniques; he first lays out the philosophical foundations of forecasting:

### 1. Predictability

Not everything can be predicted. But not everything is unpredictable either.

The predictability of solar irradiance depends on:
- **Space**: Desert regions (clear skies) are more predictable than coastal cities (cloudy)
- **Time**: Day-ahead forecasts are easier than week-ahead
- **Sky condition**: Clear skies — easy; overcast — hard; thunderstorms — hardest

```python
# Quantifying predictability
# Clear-sky index kt* = GHI_measured / GHI_clearsky
# kt* ≈ 1.0 → clear sky (high predictability)
# kt* highly variable → overcast (low predictability)

import numpy as np

np.random.seed(42)
hours = np.arange(6, 18, 0.25)  # sunrise to sunset

# Clear day: kt* stable around 0.95-1.0
kt_clear = 0.97 + 0.02 * np.random.randn(len(hours))

# Cloudy day: kt* fluctuates wildly between 0.3-0.9
kt_cloudy = 0.6 + 0.25 * np.random.randn(len(hours))
kt_cloudy = np.clip(kt_cloudy, 0.1, 1.0)

print(f"Clear-sky kt* std dev: {kt_clear.std():.3f}")
print(f"Cloudy kt* std dev:    {kt_cloudy.std():.3f}")
print(f"Predictability ratio:  {kt_clear.std()/kt_cloudy.std():.1f}x")
```

### 2. Goodness of Forecasts

Murphy (1993) decomposed forecast "goodness" into three dimensions:

| Dimension | Meaning | Example |
|-----------|---------|---------|
| **Consistency** | Does the forecast reflect the forecaster's true belief? | Do you genuinely believe it will be sunny tomorrow? |
| **Quality** | How well does the forecast match observations? | RMSE, MAE, skill scores |
| **Value** | What is the actual impact on decisions? | How much reserve cost was saved? |

**Key insight**: High quality does not necessarily imply high value. A forecast with very low RMSE that performs poorly at critical moments (e.g., sudden cloud bursts) may actually deliver less value than a forecast with higher overall RMSE that is accurate when it matters most.

### 3. Falsifiability

This is the sharpest critique. Professor Yang directly observes that too many solar forecasting papers engage in "confirming already-held beliefs" —

> "Hybrid models outperform single models, physics-based methods outperform purely statistical ones, and spatiotemporal methods outperform univariate ones — under a reasonable experimental setup, these conclusions are nearly impossible to overturn. Proving consensus conclusions is unnecessary."

In other words: if your experimental design makes failure almost impossible, your paper is pseudoscience. A genuine scientific contribution must be **falsifiable**.

---

## The Five Pillars of Solar Forecasting

Chapter 1.1 defines five technical aspects of solar forecasting:

```
Solar Forecasting
    │
    ├── 1. Base Methods
    │   ├── Sky camera → ultra-short-term (minutes)
    │   ├── Satellite remote sensing → intraday (1–6 h)
    │   ├── NWP numerical weather prediction → day-ahead (1–3 days)
    │   ├── Statistical methods → all time scales
    │   └── Machine learning → all time scales
    │
    ├── 2. Post-processing
    │   ├── D2D: deterministic→deterministic (regression/filtering/downscaling)
    │   ├── D2P: deterministic→probabilistic (ensemble simulation/dressing/prob. regression)
    │   ├── P2D: probabilistic→deterministic (distribution aggregation/combination)
    │   └── P2P: probabilistic→probabilistic (calibrated ensembles/prob. combination)
    │
    ├── 3. Verification
    │   ├── Deterministic: MAE/RMSE/MBE/skill scores
    │   └── Probabilistic: CRPS/Brier/PIT/reliability diagrams
    │
    ├── 4. Irradiance-to-Power Conversion
    │   ├── Direct: regression mapping
    │   └── Indirect: physical model chain (pvlib!)
    │
    └── 5. Grid Integration
        ├── Load following & frequency regulation
        ├── Probabilistic power flow
        ├── Hierarchical forecasting
        └── Firm (dispatchable) solar power
```

**I had previously focused only on Pillars 1 and 4 (methods + pvlib conversion), completely ignoring post-processing, verification, and grid integration. This book showed me the complete picture.**

---

## The Harsh Reality of Grid Operations

CAISO's (California Independent System Operator) real-time dispatch process:

1. **Day-Ahead Market (DAM)**: Commits generating units for the next day based on load and solar forecasts
2. **Intraday correction**: Real-Time Unit Commitment (RTUC) runs every 15 minutes
3. **Real-Time Economic Dispatch (RTED)**: Adjusts generator output every 5 minutes
4. **Frequency regulation reserves**: Eliminates residual deviations every few seconds

Forecast errors cascade through every layer:
```
Day-ahead forecast error → suboptimal unit commitment
    → increased intraday correction pressure
        → more flexible resources needed
            → rising costs
```

So solar forecasting is not an academic exercise — **every percentage point of accuracy improvement translates directly into real economic value.**

---

## Probabilistic Forecasting: More Than a Single Number

Traditional forecasting gives a single value: "Tomorrow at noon, irradiance will be $800 \text{W/m}^2$."

Probabilistic forecasting gives an entire distribution: "Tomorrow at noon, the 90% confidence interval for GHI is 650–$950 \text{W/m}^2$, most likely value $820 \text{W/m}^2$."

```python
import numpy as np

# Probabilistic vs deterministic forecasting
# Scenario: GHI forecast for tomorrow at noon

# Deterministic forecast
det_forecast = 800  # W/m²

# Probabilistic forecast (normal approximation)
mean_forecast = 820
std_forecast = 80  # std dev reflects uncertainty

# Generate forecast quantiles
quantiles = [0.05, 0.25, 0.50, 0.75, 0.95]
from scipy import stats
pred_dist = stats.norm(loc=mean_forecast, scale=std_forecast)
print("Probabilistic forecast quantiles:")
for q in quantiles:
    print(f"  P{int(q*100):02d}: {pred_dist.ppf(q):.0f} W/m²")

print(f"\nDeterministic forecast: {det_forecast} W/m²")
print(f"Probabilistic median:   {pred_dist.ppf(0.5):.0f} W/m²")
print(f"90% prediction interval: [{pred_dist.ppf(0.05):.0f}, {pred_dist.ppf(0.95):.0f}] W/m²")
```

**Why is probabilistic forecasting more valuable for the grid?**

Because grid operators need to know the **worst case** — if solar output suddenly drops to its minimum, how many backup generators do I need? Deterministic forecasts cannot answer that question; probabilistic forecasts can.

---

## My Reflection: Occam's Razor and Forecast Science

Chapter 2 makes a point that stuck with me — **the application of Occam's Razor in forecasting**:

> "Simple models are not necessarily weak; on the contrary, expert forecasters often prefer simpler models."

The mistake too many people make (myself included, in the past):
1. Forecast performance is poor → add more features → "the all-powerful" neural network should learn it automatically
2. Still poor → switch to a more complex architecture → Transformer! Mamba! Hybrid models!
3. Still poor → suspect there isn't enough data

But the truth may be: **the variables you're feeding the model are garbage to begin with.** Wind speed is a useful variable for PV power forecasting (it affects module temperature), but it may be completely useless for irradiance forecasting (single-point wind speed does not affect radiative transfer).

**Garbage In, Garbage Out.** This maxim is especially lethal in the forecasting domain.

---

## Knowledge Card 📌

```
Three philosophical foundations of forecasting:
  ① Predictability — not everything can be forecast; first assess how well it can be
  ② Goodness = Consistency + Quality + Value (Murphy 1993)
  ③ Falsifiability — a conclusion that cannot be disproved = pseudoscience

Five pillars of solar forecasting:
  ① Base methods (camera/satellite/NWP/statistical/ML)
  ② Post-processing (D2D/D2P/P2D/P2P four conversion types)
  ③ Verification (not just RMSE — also consistency and value)
  ④ Irradiance-to-power conversion (regression or physical model chain)
  ⑤ Grid integration (ultimate goal: dispatchable solar power)

Key cognitive shifts:
  - Forecasting serves decisions, not publications
  - Low RMSE ≠ good forecast (may fail at critical moments)
  - Probabilistic > deterministic (grids need to know the worst case)
  - Simple models often > complex models (Occam's razor)
  - Unfalsifiable experiments = pseudoscience

Grid real-time dispatch chain:
  DAM (day-ahead) → RTUC (15 min) → RTED (5 min) → Regulation (seconds)
  Each layer requires forecasts at a different time scale
```
