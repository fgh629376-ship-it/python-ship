---
title: 'Textbook Notes Ch4：Solar Forecasting — The New Member of the Band'
description: 'PV forecasting is the youngest member of the energy forecasting family. From lessons learned in load/wind/price forecasting to the five defining characteristics of solar irradiance.'
pubDate: 2026-03-14
lang: en
category: solar
series: solar-book
tags: ['Textbook Notes', 'Ch4', 'Energy Forecasting', 'Clear-Sky Model', 'Model Chain']
---

> 📖 [Back to Index](/textbook/)
> 📚 *Solar Irradiance and PV Power Forecasting* Chapter 4, p83–128

---

## 4.1 Maturity Across Energy Forecasting Domains

GEFCom2014 (Global Energy Forecasting Competition) was the first large-scale cross-domain benchmark — 581 participants, 61 countries, four tracks: load / wind / price / solar PV.

The four-quadrant maturity framework proposed by Hong et al. (2016) (deterministic × probabilistic):
- **Short-Term Load Forecasting (STLF)**: most mature on the deterministic side, fairly mature on the probabilistic side (since the 1980s)
- **Wind**: most mature on the probabilistic side (strong meteorological tradition), fairly mature on the deterministic side
- **Price**: fairly mature on the deterministic side (economist-led), immature on the probabilistic side
- **Solar PV**: **least mature on both axes** (only took off in the 2010s)

Why? Sparse literature + an insular community (Yang 2019a: "living in a bubble").

## 4.2 Load Forecasting: Small Differences Matter

### 4.2.1 A Bird's-Eye View of Load Forecasting

- Purpose: support supply–demand balance (from decade-long planning down to minute-level frequency regulation)
- The regression nature of the problem doesn't change, regardless of the model used
- **Best practice (Hong & Fan 2016)**: two-stage approach
  - Stage 1: non-black-box multivariate model → captures prominent features (calendar / temperature / load patterns)
  - Stage 2: black-box univariate model → explains small-scale variation in residuals
  - Combined > single-stage
- Key features: day of week, calendar events, weather conditions (temperature most important), hierarchical structure

### 4.2.2 Evaluating Load Forecast Quality

- MAPE is the most widely used metric in load forecasting
- Typical error is only **3%** (mid-size US utility, day-ahead)
- 1% MAPE ≈ hundreds of thousands of dollars per GW of peak load
- ⚠️ Sampling uncertainty: model differences can be as small as 0.002%, requiring statistical tests
- **Diebold–Mariano test**: tests whether the difference in forecast errors between two models is statistically significant

### 4.2.3 Recent Innovations

- Simply applying new ML methods is no longer novel — you must answer "why and how"
- Big data / IoT enables finer-grained load monitoring
- Peak load forecasting (Amara-Ouali et al., 2023)
- Robust forecasting under cybersecurity attacks

## 4.3 Wind Forecasting: It's All About the Weather

### 4.3.1 NWP and Wind Speed Forecasting

- < 3h: statistical / ML methods are sufficient
- > 3h: **NWP is essential**
- Wind speed is a prognostic variable in NWP (solved through the momentum equation)
- 10 m wind speed is diagnosed via boundary-layer parameterization
- Caveats when validating NWP:
  - Local exposure (surroundings of the measurement site)
  - Scale mismatch (NWP grid average vs. local observation)
  - Complex terrain is inherently difficult
  - **All of the above apply equally to solar PV forecasting!**

### 4.3.2 Wind Power Curve Modeling

- Wind speed → wind power: a non-injective mapping (the same wind speed can yield multiple power values)
- $P = \frac{1}{2} C_p \rho \pi R^2 W^3$ (theoretical power curve)
- Four regions: below cut-in (0) / cubic growth / rated power / cut-out (0)
- S-shaped curve fitting or learned via regression

### 4.3.3 Statistical and Machine Learning Methods

Three uses: (1) NWP post-processing (2) wind power curve modeling (3) direct forecast generation

Pinson (2013) identifies four key challenges:
1. Information extraction and utilization (high-dimensional spatiotemporal data → deep learning / CNN)
2. Operational integration (forecasts must interface with existing decision-making systems)
3. Verification of probabilistic forecasts in high dimensions
4. Correspondence between forecast quality and economic value

## 4.4 Electricity Price Forecasting: Causality Matters

### 4.4.1 Markets and Forecast Horizons

- **Terminology gap**: "spot" in Europe = day-ahead price; "spot" in Australia/North America = real-time price
- Trading timeline: annual contracts → seasonal/monthly/weekly contracts → day-ahead auction → intraday/real-time → balancing market
- Day-ahead price is most important: > 90% of papers focus here
- Balancing market: extreme volatility + delayed settlement price publication

### 4.4.2 Short-Term Price Forecasting Models

- Fundamentally a regression problem: $Y_{d,h} = \mathbf{x}^T_{d,h} \boldsymbol{\beta}_h + \varepsilon_{d,h}$
- Regularized regression (Lasso / Elastic Net) for automatic variable selection
  - Lasso: $\lambda \sum |\beta|$ → irrelevant variable coefficients shrink to zero
  - Elastic Net: $\lambda_1 \sum |\beta| + \lambda_2 \sum \beta^2$ → balances selection and stability
  - Extendable to quantile regression (pinball loss)
- ANN / LSTM / GRU can model nonlinearity and temporal dynamics
- VAR model: jointly estimates the 24-hour price vector

### 4.4.3 Modeling Tricks

1. **Variance-Stabilizing Transformation (VST)**:
   - Electricity prices have spikes and can be negative → log transform is inapplicable
   - Fix: asinh or probability integral transform
   - First standardize (subtract median, divide by median absolute deviation), then apply VST

2. **Seasonal decomposition**:
   - Decompose into long-term trend + stochastic component
   - Model independently then recombine > modeling prices directly
   - Works equally well for ANNs and probabilistic forecasting

3. **Calibration window averaging**:
   - Hubicka et al. (2019): combining forecasts from multiple windows > choosing a single "optimal" window
   - Essentially a form of data ensemble (Section 3.3.2.1)

## 4.5 Distinctive Characteristics of Solar Irradiance

### 4.5.1 The Clear-Sky Expectation

**This is the most fundamental distinction between solar PV forecasting and everything else.**

The core equations of the REST2 clear-sky model:
- $B_{nc} = E_{0n} \times T_R \times T_g \times T_o \times T_n \times T_w \times T_a$
- Transmittances of six atmospheric attenuation processes multiplied together
- $\text{GHI}_\text{clear} = \text{BNI}_\text{clear} \times \cos(Z) + \text{DHI}_\text{clear}$

Clear-sky model taxonomy:
- Ranges from simple empirical formulas to the full radiative transfer parameterization of REST2
- Sun et al. (2021a, 2019): the most comprehensive comparison to date (75 GHI models, 95 BNI/DHI models)
- REST2v9.1 achieves the highest quality

> ⚡ **GEFCom2014 fact**: the only team to use a clear-sky model = the winner. All other teams' forecasts were "put to shame."

### 4.5.2 Clear-Sky Index Distribution

- Multiplicative decomposition ($\kappa = \text{GHI} / \text{GHI}_\text{clear}$) > additive decomposition ($\kappa' = \text{GHI} - \text{GHI}_\text{clear}$)
- The additive residual still has time-varying amplitude (fails)
- The $\kappa$ distribution is typically **bimodal** (a clear-sky peak near ~1.0 + an overcast peak near ~0.3–0.5)
- Arid regions (e.g., Desert Rock) may show a unimodal distribution

⚠️ Common mistakes:
1. Assuming GHI follows a Beta distribution — physically unreasonable (GHI can exceed the clear-sky value)
2. Computing correlations directly on GHI — inflates spurious seasonal correlation (GHI in Shanghai and Los Angeles looks highly correlated, but there is no causal link)

### 4.5.3 Physical Bounds

- **Lower bound**: theoretically 0 (thermocouple offset can produce slightly negative readings; ignored in practice)
- **Upper bound**: ≈ 1.5 × clear-sky value (cloud enhancement + albedo enhancement)
  - 1-second resolution: ~$1900 \text{W/m}^2$
  - 1-minute resolution: ~$1600 \text{W/m}^2$
  - > 5 minutes: cloud enhancement tends to average out
  - 100 kW PV plant: peak can reach ~$1400 \text{W/m}^2$ (~1.5 × clear-sky)
- **AC power ceiling**: inverter rated capacity (clipping occurs when DC:AC > 2 in over-paneled systems)
- **Gaussian distribution is inappropriate for irradiance**: physical bounds exist, whereas Gaussian extends to ±∞

### 4.5.4 Spatiotemporal Dependence

After removing seasonality, the correlations in irradiance data **arise entirely from moving clouds**.

Effective range for each forecasting approach:
- Sky cameras: < 30 minutes (the "frozen cloud field" assumption, valid for only a few minutes)
- Satellite: < 4 hours (cloud motion vector advection assumption, valid for several hours)
- NWP: 4h → 15 days (the only approach that solves cloud dynamics)
- Sensor networks: effective only within a few kilometers; not scalable

**The textbook's key logical chain**:
- Premise 1: The grid needs forecasts for > 4h (real-time market) and > 36h (day-ahead market)
- Premise 2: Sky cameras / satellite / sensor networks all fall short
- **Conclusion: NWP is the only reliable source for day-ahead and intraday grid dispatch**

### 4.5.5 PV Power Curve (Model Chain)

The minimal four-step Model Chain:
1. Decomposition model: $k_t = G_h / E_0$ → estimate $B_n$ and $D_h$
2. Transposition equation: $G_c = B_n \cdot \cos(\theta) + R_d \cdot D_h + \rho_g \cdot R_r \cdot G_h$
3. Temperature model: $T_\text{cell} = T_\text{amb} + \frac{\text{NOCT} - 20}{800} \times G_c$
4. Power equation: $P = P_\text{dc,ref} \times \frac{G_c}{1000} \times [1 + \gamma (T_\text{cell} - 25)]$

⚠️ **The best combination of individual sub-models ≠ the best Model Chain** — error propagation is complex.

## 4.6 Shared Research Frontiers

### 4.6.1 Advanced Physical Forecasting

- Energy forecasters ≠ meteorologists; the knowledge gap is real
- Most papers rely only on **off-the-shelf NWP products**, without engaging with the underlying physics
- Opportunity: use global NWP as boundary conditions to run high-resolution regional models (e.g., WRF-Solar)

### 4.6.2 Machine Learning

- ML has over 30 years of history in energy forecasting
- Deep learning requires **large volumes of training data** — a few years of single-station hourly data is simply not enough
- Current literature **prioritizes form over substance** — pages spent on network architectures, little attention to application fit
- Physical features must be engineered into ML models; you can't expect algorithms to discover physics on their own
- "Those who believe in deep learning will object, but there is currently no decisive evidence to end the debate"

### 4.6.3 Ensemble and Probabilistic Forecasting

- Probabilistic forecasting is the **most important conceptual shift**
- Energy forecasters are **users** of weather forecasts; their primary work is post-processing
- Industrial adoption remains low — power system operations are extremely conservative
- Yang et al. (2021a): forecasting research disconnected from operational standards **has no intrinsic value**

### 4.6.4 Hierarchical Forecasting

- Individual → regional → system-wide must satisfy **aggregation coherence**
- Traditional approaches (top-down / bottom-up / middle-out) exploit only a single level
- Modern approach: **optimal reconciliation (Hyndman et al., 2011)** — leverages information from all levels simultaneously
- Grid regulations require system owners to submit power forecasts (compliance + penalty reduction)
- Hierarchical forecasting can unify load + wind + solar into a **net load forecast**

## 4.7 Common Pitfalls and Recommendations

### 4.7.1 Common Pitfalls

1. **Limited datasets**: proprietary or context-specific datasets → conclusions don't generalize
2. **Insufficient validation**:
   - Wrong metrics (using MAPE when values are near zero)
   - Weak baselines (only comparing against a weaker version of your own method)
   - Test sets too small (Rob Hyndman: "That is just silly")
   - At minimum, **a full year of hourly data** is required
3. **Inconsistent terminology**: reinventing jargon causes literature bloat

### 4.7.2 Recommendations

1. Structure literature reviews around **logical flow**, not a "who did what" roster
2. Be precise with terminology: don't say "short-term" — say "horizon = 24h, resolution = 1h"
3. Share code + data to enhance reproducibility (ostensive > verbal reproducibility)
4. Choose journals with domain experts as reviewers, not just high impact factors
5. **Persist** — understanding is proportional to time invested; there are no shortcuts

## 4.8 Chapter Summary

The textbook's ultimate conclusions:

> 1. The clear-sky model is the **most important consideration** in solar PV forecasting
> 2. Purely data-driven, single-station approaches are **seriously handicapped**, no matter how complex
> 3. Best path: forecast irradiance first → post-process → Model Chain → power output
> 4. Methods that require very specialized data are not worth generalizing

---

## 📋 Key Takeaways from This Chapter

| Topic | Core Point |
|-------|-----------|
| Status of PV forecasting | Least mature in energy forecasting, but fastest-growing |
| Lesson from load forecasting | Two-stage method = main features + residuals → PV analog: clear-sky model + ML |
| Lesson from wind forecasting | NWP required for > 3h → same applies to solar |
| Tricks from price forecasting | VST / decomposition / window averaging → all transferable |
| Clear-sky model | The most powerful weapon; the secret behind GEFCom2014 champion |
| $\kappa$ distribution | Bimodal; use mixture Gaussian, not Beta |
| Cloud enhancement | Upper bound ≈ 1.5 × clear-sky value |
| Necessity of NWP | The only reliable source for forecasts beyond 4h |
| Model Chain | Holistic optimization > stitching together individually optimal sub-models |

> 📖 [← Previous Chapter](/blog/textbook-ch03/) | [Back to Index](/textbook/) | [Next Chapter →](/blog/textbook-ch05/)
