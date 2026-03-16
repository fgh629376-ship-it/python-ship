---
title: "Box Time Series Analysis Ch10: Nonlinear Models and Long Memory — GARCH, TAR, ARFIMA"
description: "A close reading of Box's Time Series Analysis Chapter 10: ARCH/GARCH conditional heteroscedasticity, threshold autoregression TAR, long-memory ARFIMA"
pubDate: 2026-03-16
lang: en
series: box-timeseries
category: timeseries
tags: ["time series", "GARCH", "nonlinear", "long memory", "ARFIMA", "textbook notes"]
---

# Box Time Series Analysis Ch10: Nonlinear Models and Long Memory

> **Textbook**: Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 10

## Core Themes

ARIMA in Ch3-9 is **linear + homoscedastic**. Ch10 breaks both of these assumptions.

---

## 10.1 ARCH/GARCH: Conditional Heteroscedasticity

### The Problem

"Volatility clustering" in financial data: large movements are followed by large movements (random direction), quiet periods are followed by quiet periods. ARMA assumes $\text{var}(a_t) = \sigma_a^2$ is constant and cannot capture this phenomenon.

### ARCH(s) Model

$$h_t = \text{var}[a_t | a_{t-1}, \ldots] = \omega_0 + \sum_{i=1}^{s} \omega_i a_{t-i}^2$$

The conditional variance depends on past **squared shocks**.

### GARCH(s,r) Model

$$h_t = \omega_0 + \sum_{i=1}^{s} \omega_i a_{t-i}^2 + \sum_{i=1}^{r} \beta_i h_{t-i}$$

GARCH(1,1) = the most widely used volatility model in finance.

### Key Properties

- $a_t$ is still zero-mean and uncorrelated — but **not independent**
- Conditional variance $h_t$ varies over time, but unconditional variance $\sigma_a^2 = \omega_0/(1 - \omega_1 - \beta_1)$ is constant (weakly stationary)
- Forecast error variance adjusts with past volatility → **adaptive forecast intervals**

---

## 10.2 Nonlinear Models

### TAR (Threshold Autoregression)

$$z_t = \begin{cases} \phi_1^{(1)} z_{t-1} + \cdots + a_t & \text{if } z_{t-d} \leq r \\ \phi_1^{(2)} z_{t-1} + \cdots + a_t & \text{if } z_{t-d} > r \end{cases}$$

Different AR models are used in different "regimes." Can produce **limit cycle** behavior.

### Bilinear Models

$$z_t = \sum \phi_i z_{t-i} + \sum \theta_j a_{t-j} + \sum \beta_{ij} z_{t-i} a_{t-j} + a_t$$

Past values and past shocks interact with each other.

---

## 10.3 Long-Memory ARFIMA

### The Problem

Some series have ACF that decays very slowly (power-law decay $\rho_k \sim k^{2d-1}$), yet differencing once is too much → **fractional differencing** is needed.

### ARFIMA(p,d,q)

$$\phi(B)(1-B)^d z_t = \theta(B) a_t, \quad -0.5 < d < 0.5$$

When $d$ is non-integer, $(1-B)^d = \sum_{k=0}^{\infty} \binom{d}{k}(-B)^k$

- $0 < d < 0.5$: long memory, power-law ACF decay (summable!)
- $d = 0$: short-memory ARMA
- $-0.5 < d < 0$: antipersistence

---

## Deep Thinking

### Implications for Solar Power Forecasting

1. **GARCH for irradiance**: Volatility clustering caused by cloud cover → irradiance residuals may have ARCH effects → use GARCH for adaptive forecast intervals
2. **TAR for weather regimes**: Sunny vs. cloudy days may need different AR models → threshold model or Markov switching
3. **ARFIMA for long-term memory**: Interannual variation in irradiance may exhibit long-memory characteristics (slow dynamics of climate change)

---

*📖 [Ch9 Notes](/blog/2026-03-16-box-ch9-seasonal) | [Back to Textbook Index](/textbook/) | 📝 [Box Time Series Series](/blog/)*
