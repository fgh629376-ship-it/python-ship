---
title: 'Textbook Notes Ch3: Deterministic and Probabilistic Forecasts'
description: "Chaos ≠ randomness. From Laplace's Demon to ensemble learning — the complete mathematical framework for deterministic and probabilistic forecasting."
pubDate: 2026-03-14
lang: en
category: solar
series: solar-book
tags: ['Textbook Notes', 'Ch3', 'Probabilistic Forecasting', 'Ensemble Learning', 'Mathematical Foundations']
---

> 📖 [Back to Index](/textbook/solar/)
> 📚 《Solar Irradiance and PV Power Forecasting》Chapter 3, p50-82

---

## 3.1 The Deterministic Nature of the Physical World

**The core chain of reasoning**:
1. All chaotic systems are deterministic (premise 1)
2. Weather is a chaotic system (premise 2)
3. Therefore, weather is deterministic (conclusion)

This is the thought experiment of Laplace's Demon — if we knew the exact initial state of a system and all physical laws, the future would be completely determined.

But **determinism ≠ predictability**. Chaotic systems are extraordinarily sensitive to initial conditions; errors grow exponentially. This is the source of the theoretical limit of weather forecasting.

Two sources of forecast error:
1. **Imperfect initial conditions** (observations always carry error)
2. **Imperfect dynamical laws** (parameterization schemes are approximations)

## 3.2 Uncertainty and Distributional Forecasting

### 3.2.1 Basics of Probability Distributions

- CDF: $F_X(x) = P(X \leq x)$, range $[0,1]$
- PDF: $f_X(x) = F'_X(x)$, **value can be > 1** (a common misconception)
- Irradiance has physical upper and lower bounds; Gaussian distributions (extending to $\pm\infty$) are not appropriate

### 3.2.2 Predictive Distribution

The central form of probabilistic forecasting. Nature selects the true distribution $G_i$; the forecaster issues $F_i$.

Quantile definition:
- The $\tau$-quantile $= F^{-1}(\tau) = \inf\{x : F(x) > \tau\}$
- $\tau$ is the probability level (0–1); the quantile value is a specific irradiance number
- ⚠️ When $X$'s range is also $[0,1]$ (e.g., the clear-sky index $\kappa$), $\tau$ and the quantile value are extremely easy to confuse

### 3.2.3 The Ideal Predictive Distribution (Gneiting et al., 2007)

A foundational paper for probabilistic forecast verification. The core paradigm:

> **Maximize sharpness subject to calibration**

- **Calibration**: statistical consistency between the predictive distribution and observations (if you say 80% interval, it should actually cover 80% of the time)
- **Sharpness**: the concentration of the predictive distribution (the narrower the interval, the better — as long as calibration holds)

Common mistakes:
- Chasing sharpness only → intervals are too narrow; actual coverage rate falls far below the nominal level
- Chasing calibration only → even climatological forecasts can be calibrated, but they have no skill

### 3.2.4 Four Types of Predictive Distributions

| Type | Example | Characteristics | Solar Application |
|------|---------|----------------|-------------------|
| Parametric | Gaussian $N(\mu,\sigma)$ | Described by fixed parameters | Simple, but truncation required (irradiance ≥ 0) |
| Semi-parametric | Mixture Gaussian (2–3 components) | Captures multimodality | Irradiance is naturally bimodal (sunny/cloudy) |
| Non-parametric | KDE kernel density estimation | No shape assumption | Flexible, but bandwidth selection required |
| Empirical | ECDF | Fully non-parametric | Simplest, requires large samples |

### 3.2.5 Other Representations of Distributional Forecasts

- **Quantile forecasts**: report quantile values at specific $\tau$ levels (e.g., $q_{0.1}, q_{0.5}, q_{0.9}$)
- **Interval forecasts**: $(1-\alpha)\times100\%$ central interval = $[\alpha/2, 1-\alpha/2]$ quantiles
- **Ensemble forecasts**: a collection of multiple deterministic forecasts

## 3.3 Ensemble Forecasting

### 3.3.1 Types of Meteorological Ensembles

Three types, categorized by source of uncertainty:

| Type | Principle | Example | Corresponding Uncertainty |
|------|-----------|---------|--------------------------|
| Dynamic ensemble | Perturb initial conditions | ECMWF EPS (50+1 members) | Data uncertainty |
| Poor man's ensemble | Different models | ECMWF + GFS + NAM | Process uncertainty |
| Stochastic parameterization | Different physics schemes | Different cloud microphysics schemes | Parameter uncertainty |

### 3.3.2 Statistical Ensemble Forecasting

Three statistical strategies for generating ensembles:

**Data ensemble**:
- Time-series length perturbation (train on different historical lengths)
- Bootstrap aggregation (the statistical basis of bagging)
- Multiple data sources (different versions of the same variable from stations, satellites, and reanalysis)
- Spatial ensemble (include forecasts from nearby pixels/stations)

**Process ensemble**:
- Wide variety of time-series models to choose from: ARIMA family, ETS family
- Various decomposition methods: STL / X11 / SEATS / Fourier / Wavelet
- Decompose → forecast → reconstruct is the classical workflow
- TBATS = Trigonometric (Fourier) + Box-Cox + ARMA errors + Trend + Seasonality

**Parameter ensemble**:
- Adjust ARIMA's $(p,d,q)$ or ETS state parameters
- Contradicts optimal parameterization? — But non-optimal parameterizations are valuable for uncertainty quantification
- Analogy: NWP ensemble members are not the best guess either, but they are useful for quantifying uncertainty

### 3.3.3 Ensemble Learning

The distinction between statistical ensembles and ensemble learning: fundamentally the same thing, but the terminology comes from different fields. The key insight is that different communities independently invented the same concept.

#### 3.3.3.1 Bagging (Bootstrap Aggregating)

- Create multiple bootstrap samples → train a base learner on each → average the predictions
- **Reduces variance** (well-suited for high-variance models like decision trees)
- Base learners can be **trained in parallel** (embarrassingly parallel)
- Guarantee: ensemble MSE ≤ average base learner MSE, but **not guaranteed ≤ the best base learner**
- Diversity is critical — the more different the base learners, the better the ensemble
- Out-of-bag samples can be used for internal evaluation

#### 3.3.3.2 Boosting

- Built sequentially; each round focuses on the samples that were misclassified in the previous round
- AdaBoost.M1 core steps:
  1. Initialize equal weights $w_i = 1/n$
  2. Train a weak classifier → compute error rate $\eta_j$
  3. Compute $\alpha_j = \log[(1-\eta_j)/\eta_j]$
  4. Multiply the weights of misclassified samples by $\exp(\alpha_j)$
- **Reduces bias** (well-suited for high-bias models like shallow trees)
- For regression: replace exponential loss with squared / absolute / Huber loss
- XGBoost is a modern implementation of boosting

#### 3.3.3.3 Stacking

- Two-layer structure: base learners (Level 0) + super learner (Level 1)
- The super learner is trained via **cross-validation** (no additional hold-out set needed)
- Regularized regression is commonly used as the super learner
- Differs from simple post-processing: stacking does not require a two-stage data split

## 3.4 Afterthought

- The core distinction between statistical ensembles and ensemble learning toolboxes: whether you can access the **component forecasts**
  - Statistical ensemble: external combination — you can see each component
  - Ensemble learning toolbox: typically outputs only the final combined result
- Converting probability to deterministic forecasts is **not trivial**:
  - Use the mean or the median? This affects the choice of evaluation metric
  - If using the mean for a deterministic forecast, evaluate with MSE
  - If using the median for a deterministic forecast, evaluate with MAE
  - Most solar forecasters have never asked these questions

---

## 📋 Key Takeaways

| Concept | Definition | Significance for Solar Forecasting |
|---------|-----------|-----------------------------------|
| Chaotic system | Deterministic but sensitive to initial conditions | The theoretical limit of weather forecasting |
| Predictive distribution | Probabilistic forecast in CDF/PDF form | Four types for different scenarios |
| Gneiting paradigm | Maximize sharpness subject to calibration | The gold standard for probabilistic forecast verification |
| Bagging | Bootstrap + averaging | Reduces variance; Random Forest |
| Boosting | Sequential + focus on errors | Reduces bias; XGBoost |
| Stacking | Base learners + super learner | Optimal combination |

> 📖 [← Previous Chapter](/blog/textbook-ch02/) | [Back to Index](/textbook/solar/) | [Next Chapter →](/blog/textbook-ch04/)
