---
title: "📖 NWP Textbook Reflections Ch9-11: Verification, Experimental Design, and Output Analysis — How to Scientifically Evaluate a Model?"
description: "Reflections on Warner NWP Chapters 9 to 11. Representativeness error is unavoidable, effective resolution > 2Δx, the double-penalty problem — these concepts changed my understanding of model verification. OSSE, factor separation, and EOF are the core tools of research design."
pubDate: 2026-03-16
lang: en
category: solar
series: nwp-warner
tags: ["Textbook Reflections", "NWP", "Model Verification", "OSSE", "EOF"]
---

> 📖 This post is a reflection on [Warner NWP Textbook](/textbook/nwp-warner/) Ch9-11 | [Back to Textbook Index](/textbook/)

## 1. Representativeness Error: The Ultimate Dilemma of Verification

The biggest shock from Ch9: **Even if both the model and the instrument are perfect, the verification statistics are not zero.**

Observations = instantaneous point values at a specific time. Model = spatiotemporal average over a grid box volume (possibly 10 km × 10 km × 100 m). These are physically different quantities.

Representativeness error ∝ sub-grid variability within the grid box. Under convective conditions, GHI within 1 km² can range from 200 to 900 W/m² — the representativeness error is larger than the model error.

**Effective resolution > 2Δx**: Skamarock (2004) showed that numerical dissipation and explicit diffusion further smooth the solution; the minimum resolvable scale is approximately 6–8Δx.

---

## 2. Choosing Verification Metrics

### Continuous Variables
- **MAE**: More intuitively understandable (mean absolute error)
- **RMSE**: More sensitive to large errors (errors are squared)
- **Bias**: Systematic error, $\bar{x} - \bar{o}$
- **AC** (Anomaly Correlation): Standard for 500 hPa height field — AC > 0.6 = useful forecast. Global model AC = 0.6 limit has extended from ~5 days to ~8 days (40 years of progress)

### Categorical Variables (Yes/No Events)
- **POD** = hits/(hits+misses)
- **FAR** = false alarms/(hits+false alarms)
- **CSI** = hits/(hits+misses+false alarms)
- **HSS** (Heidke Skill Score): improvement relative to random forecasts

### The Pitfall of Skill Scores

$$SS = 1 - \frac{MSE}{MSE_{ref}}$$

The choice of reference forecast is critical. For irradiance: do not use simple persistence ("tomorrow will be the same as today"); use **diurnal persistence** ("tomorrow will be the same as today at the same time of day") — because the diurnal variation of the solar angle is deterministic.

---

## 3. The Double-Penalty Problem and Object-Based Verification

The fatal flaw of traditional point-by-point verification: if a model correctly predicts a storm but the position is shifted by 20 km, point-by-point verification gives one penalty at each location — rain was forecast but not observed (false alarm), rain was observed but not forecast (miss). In reality, the model only had a position error, not a complete failure.

**Object-based verification (MODE/SAL)**: identifies precipitation areas (or cloud areas) as objects, comparing the position, size, intensity, and shape of objects. This approach may be more valuable for irradiance forecasting than point-by-point verification.

---

## 4. Core Tools for Experimental Design (Ch10)

- **OSSE** (Observing System Simulation Experiment): evaluating the value of new observing systems — testing "if we add this type of observation, by how much would the forecast improve?" in a virtual world
- **Factor separation** (Stein & Alpert 1993): isolates the individual contributions and interaction effects of multiple factors
- **Adjoint sensitivity**: gradient of the cost function with respect to initial conditions/parameters → defines "the regions with the greatest influence on the forecast"
- **Reforecasts**: running historical cases with the current model → obtaining large-sample verification statistics

### Warner's Warning

> "Thoroughly analyze the observations first, then run the model. Failing to analyze observations before running the model is a very common mistake (modelers love to model!)"

---

## 5. Model Output Analysis Tools (Ch11)

- **SOM** (Self-Organizing Map): automatic classification of weather regimes → can be used for automatic classification of irradiance fields
- **EOF/PCA**: dimensionality reduction, extracting major variability modes → the first EOF of irradiance spatiotemporal variability typically corresponds to large-scale cloud cover
- **CCA/SVD**: finding coupled modes → coupling between large-scale circulation and local irradiance
- **Spectral/wavelet analysis**: frequency characteristics, spatial distribution of diurnal variation power

---

## 6. Implications for Solar Power Forecasting

1. **Representativeness error must be considered when verifying irradiance forecasts** — ground station verification has a natural lower bound
2. **Object-based verification may be more appropriate for evaluating cloud field forecasts** — a position shift is much better than complete absence
3. **Diurnal persistence is a more reasonable reference forecast** — simple persistence should not be used
4. **EOF can be directly applied to spatiotemporal analysis of irradiance** — extracting major variability modes

---

## References

- Warner, T.T. (2011). *Numerical Weather and Climate Prediction*. Cambridge University Press. Ch9-11.
- Skamarock, W.C. (2004). Evaluating mesoscale NWP models using kinetic energy spectra. *Mon. Wea. Rev.*, 132, 3019-3032.
- Wilks, D.S. (2006). *Statistical Methods in the Atmospheric Sciences*. Academic Press.
