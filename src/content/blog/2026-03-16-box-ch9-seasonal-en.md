---
title: "Box Time Series Analysis Ch9: Seasonal Models — The Multiplicative Structure of SARIMA"
description: "A close reading of Box's Time Series Analysis Chapter 9: multiplicative seasonal models SARIMA, seasonal differencing, airline passengers example, Box-Cox transformation"
pubDate: 2026-03-16
lang: en
series: box-timeseries
category: timeseries
tags: ["time series", "SARIMA", "seasonality", "airline passengers", "Box-Cox", "textbook notes"]
---

# Box Time Series Analysis Ch9: Seasonal Models — The Multiplicative Structure of SARIMA

> **Textbook**: Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 9

## Core Idea

Ch3-8 only handled non-seasonal series. But a large amount of real data has **periodic patterns** (monthly sales, quarterly GDP, hourly irradiance). Ch9's solution:

> **Multiplicative SARIMA models** — model separately at both the $B$ and $B^s$ scales.

---

## 9.1 Why Do We Need Dedicated Seasonal Models?

### The Fitting vs. Forecasting Trap

Box first warns: it's easy to "fit" seasonal patterns with Fourier series or deterministic functions, but forecasting may be poor. IBM stock prices look like they have a trend, but the optimal forecast is just today's price — deterministic fitting is misleading.

### Intuition Behind the Multiplicative Model

Monthly data has **two types of temporal relationships**:
1. **Adjacent months** ($B$): the connection between March and April
2. **Same month, different years** ($B^{12}$): the connection between this April and last April

A natural approach: model each scale separately, then **multiply them together**.

---

## 9.2 General Multiplicative Seasonal Model

$$\phi_p(B) \Phi_P(B^s) \nabla^d \nabla_s^D z_t = \theta_q(B) \Theta_Q(B^s) a_t$$

- $\phi_p(B)$: Non-seasonal AR(p), e.g. $(1 - \phi_1 B)$
- $\Phi_P(B^s)$: Seasonal AR(P), e.g. $(1 - \Phi_1 B^{12})$
- $\nabla^d = (1-B)^d$: Non-seasonal differencing, e.g. $d = 1$
- $\nabla_s^D = (1-B^s)^D$: Seasonal differencing, e.g. $D = 1, s = 12$
- $\theta_q(B)$: Non-seasonal MA(q), e.g. $(1 - \theta_1 B)$
- $\Theta_Q(B^s)$: Seasonal MA(Q), e.g. $(1 - \Theta_1 B^{12})$

Denoted **ARIMA$(p,d,q) \times (P,D,Q)_s$**.

### Classic Airline Passengers Example

Series G: Monthly international airline passengers (1949-1960), $s = 12$

Final model: $(0,1,1) \times (0,1,1)_{12}$

$$(1 - B)(1 - B^{12}) \ln z_t = (1 - \theta B)(1 - \Theta B^{12}) a_t$$

$\hat{\theta} = 0.40, \hat{\Theta} = 0.60$

**The meaning of the multiplicative structure**: The MA part of the model expands to $a_t - \theta a_{t-1} - \Theta a_{t-12} + \theta\Theta a_{t-13}$, describing the complex within-year and between-year dependence structure with only 3 parameters.

---

## 9.3 Identification, Estimation, and Diagnostics for Seasonal Models

### Identification Procedure

1. **Check non-stationarity**: ACF of original and seasonally differenced series
2. **Seasonal differencing**: $\nabla_{12} z_t = z_t - z_{t-12}$ (or take log/Box-Cox first)
3. **Check non-seasonal non-stationarity**: see if $\nabla$ differencing is also needed
4. **ACF/PACF at lags $s, 2s, 3s, \ldots$** → seasonal $P, Q$
5. **ACF/PACF at lags $1, 2, 3, \ldots$** → non-seasonal $p, q$

### Box-Cox Transformation

$$z_t^{(\lambda)} = \begin{cases} (z_t^\lambda - 1)/\lambda & \lambda \neq 0 \\ \ln z_t & \lambda = 0 \end{cases}$$

Airline passengers data uses $\lambda = 0$ (log transformation), because variability increases proportionally with the level.

---

## Deep Thinking

### 1. Reasonableness of the Multiplicative Assumption

The multiplicative seasonal model assumes: seasonal effects and non-seasonal dynamics are **separable**. This is equivalent to saying "the relationship between April and March" does not depend on "the overall level this year."

For much data this is reasonable, but not always — for example, the temporal structure of cloud effects on solar irradiance may differ between summer and winter.

### 2. Key Insights for Solar Power Forecasting

**Irradiance has two types of periodicities**:
- **Daily cycle** ($s = 24$, or $s = 48$ for 30-minute data)
- **Annual cycle** ($s = 365$, or $s = 12$ for monthly data)

SARIMA can directly handle the daily cycle:
$$\text{ARIMA}(p,d,q) \times (P,D,Q)_{24}$$

But with $s = 24$, the multiplicative model has 24 seasonal roots; in practice one typically uses:
1. **Physical de-seasonalization** (clearsky model) → fit ARMA to residuals
2. **Fourier terms + ARMA residuals**
3. **STL decomposition + ARMA residuals**

### 3. Parsimony Is Even More Important in Seasonal Models

$(0,1,1) \times (0,1,1)_{12}$ with only 3 parameters ($\theta, \Theta, \sigma_a^2$) describes the complete dynamics of 144 months of data. This is the ultimate embodiment of the parsimony principle.

---

## Summary

Ch9 = Seasonal extension of ARIMA. Core formula:

$$\phi(B)\Phi(B^s)\nabla^d\nabla_s^D z_t = \theta(B)\Theta(B^s) a_t$$

The **multiplicative structure** allows a small number of parameters to describe complex multi-scale temporal dependence.

---

*📖 [Ch8 Notes](/blog/2026-03-16-box-ch8-diagnostics) | [Back to Textbook Index](/textbook/) | 📝 [Box Time Series Series](/blog/)*
