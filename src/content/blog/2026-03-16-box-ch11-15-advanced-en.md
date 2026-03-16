---
title: "Box Time Series Analysis Ch11-15: Transfer Functions, Intervention Analysis, Multivariate, Process Control"
description: "A close reading of Box's Time Series Analysis Chapters 11-15: transfer function models, cross-correlation, intervention analysis, outlier detection, VAR models, feedback control"
pubDate: 2026-03-16
lang: en
series: box-timeseries
category: timeseries
tags: ["time series", "transfer function", "intervention analysis", "VAR", "process control", "textbook notes"]
---

# Box Time Series Analysis Ch11-15: Advanced Topics

> **Textbook**: Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapters 11-15

---

## Ch11: Transfer Function Models

### Core Concept

When we have an **input $X_t$** (e.g., temperature, irradiance) and an **output $Y_t$** (e.g., power):

$$Y_t = v(B)X_t + N_t = \frac{\omega(B)}{\delta(B)} B^b X_t + N_t$$

- $v(B) = \sum v_j B^j$: transfer function (impulse response)
- $b$: pure delay (lag before input affects output)
- $\omega(B)/\delta(B)$: rational function parameterization (parsimony!)
- $N_t$: noise (its own ARMA process)

### Stability

Transfer function is stable ⟺ roots of $\delta(B) = 0$ lie outside the unit circle ⟺ $v_j$ is absolutely summable.

### Significance for Solar Power

The physical relationship irradiance → power is a transfer function! The pvlib Model Chain is essentially a deterministic transfer function, but in practice there is also stochastic noise $N_t$.

---

## Ch12: Identification, Estimation, and Testing of Transfer Functions

### Prewhitening + Cross-Correlation (CCF)

1. "Prewhiten" input $X_t$ with an ARIMA model → $\alpha_t$
2. Apply the same ARIMA transformation to $Y_t$ → $\beta_t$
3. $\hat{v}_k = r_{\alpha\beta}(k) \cdot \hat{\sigma}_\beta / \hat{\sigma}_\alpha$
4. Infer $b, s, r$ from the estimated impulse response → rational transfer function parameters

### Joint Estimation

Joint MLE of $\phi(B), \theta(B)$ (noise) and $\omega(B), \delta(B)$ (transfer function).

---

## Ch13: Intervention Analysis and Outlier Detection

### Intervention Analysis

When a series is affected by **known external events** (e.g., policy changes, equipment failures):

$$Y_t = \frac{\omega(B)}{\delta(B)} B^b \xi_t + N_t$$

where $\xi_t$ is the intervention variable:
- **Step function**: $S_t^{(T)} = 0$ ($t < T$), $= 1$ ($t \geq T$)
- **Pulse function**: $P_t^{(T)} = 0$ ($t \neq T$), $= 1$ ($t = T$)

### Outlier Detection

- **AO (Additive Outlier)**: affects a single observation
- **IO (Innovative Outlier)**: affects all subsequent observations
- Chen & Liu (1993) iterative detection algorithm

### Significance for Solar Power

**Equipment failures, panel shading, inverter power curtailment** are all intervention events → automatically detect and correct.

---

## Ch14: Multivariate Time Series

### VAR(p) Model

$$\mathbf{z}_t = \boldsymbol{\Phi}_1 \mathbf{z}_{t-1} + \cdots + \boldsymbol{\Phi}_p \mathbf{z}_{t-p} + \mathbf{a}_t$$

- $\mathbf{z}_t$ is an $m \times 1$ vector (multiple series)
- $\boldsymbol{\Phi}_i$ are $m \times m$ parameter matrices
- $\mathbf{a}_t \sim N(\mathbf{0}, \boldsymbol{\Sigma})$

### Granger Causality

$X$ **Granger causes** $Y$ ⟺ Past values of $X$ help predict $Y$ (conditioning on the past of $Y$).

### Cointegration

A linear combination of multiple non-stationary series is stationary → VECM (Vector Error Correction Model).

### Significance for Solar Power

**Multi-site forecasting** is a multivariate time series problem — irradiance at adjacent stations is correlated → VAR can capture spatial-temporal dependencies.

---

## Ch15: Process Control

### Feedback Control

$$X_t = g(e_t, e_{t-1}, \ldots)$$

Control variable $X_t$ is a function of the deviation $e_t = Y_t - T_t$ (output minus target).

### Minimum Variance Control

$$X_t = -\frac{\psi(B) - \theta(B)}{v(B)\theta(B)} Y_t$$

Equivalent to minimizing the variance of the output.

### Box-Jenkins Control vs. Classical PID

Box-Jenkins approach: build the model first (transfer function + noise model) → then design the controller. Better than blindly tuning PID.

### Significance for Solar Power

**Energy storage scheduling** and **inverter power control** are both feedback control problems — forecast deviation → adjust battery charge/discharge strategy.

---

## Complete Book Summary

| Part | Chapters | Theme |
|------|---------|-------|
| I | Ch1-5 | Linear models and forecasting |
| II | Ch6-9 | Model building (identification/estimation/diagnostics/seasonal) |
| III | Ch10-15 | Advanced topics (nonlinear/transfer function/multivariate/control) |

**The enduring contributions of the Box-Jenkins framework**:
1. Iterative modeling methodology (identification → estimation → diagnostics → modification)
2. Statistical proof of the parsimony principle
3. ARIMA foundation for exponential smoothing
4. Understanding forecast error as information increment

---

*📖 [Ch10 Notes](/blog/2026-03-16-box-ch10-nonlinear) | [Back to Textbook Index](/textbook/) | 📝 [Box Time Series Series](/blog/)*
