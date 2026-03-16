---
title: "Box Time Series Analysis Ch4: ARIMA — Differencing Turns Non-Stationarity into Stationarity"
description: "A close reading of Chapter 4 of Box's Time Series Analysis: the physical meaning of the difference operator, the three explicit forms of ARIMA(p,d,q), the IMA process and its equivalence to exponential smoothing"
pubDate: 2026-03-16
lang: en
series: box-timeseries
category: timeseries
tags: ["time series", "ARIMA", "differencing", "non-stationarity", "IMA", "exponential smoothing", "textbook notes"]
---

# Box Time Series Analysis Ch4: ARIMA — Differencing Turns Non-Stationarity into Stationarity

> **Textbook**: Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 4

## Core Idea

The ARMA models of Ch3 only handle stationary series. But many real-world series (stock prices, sales volumes, temperatures) **have no fixed mean**. The key insight of Ch4:

> **Differencing $d$ times can transform a "homogeneously non-stationary" series into a stationary one.**

$$\phi(B)\nabla^d z_t = \theta(B)a_t$$

This is the ARIMA(p,d,q) model, where $\nabla = 1 - B$ is the difference operator.

---

## 4.1 Definition of the ARIMA Process

### Why Not Non-Stationarity with "Roots Inside the Circle"?

Box first rules out the case where roots of $\phi(B) = 0$ lie **inside** the unit circle — this produces **explosive processes** (e.g., $z_t = 2z_{t-1} + a_t$, where the series grows exponentially). This is not the type we wish to model.

The non-stationarity we want is **homogeneous** — no fixed level, but local behavior is similar everywhere. Mathematically, this corresponds to $\phi(B) = 0$ having $d$ roots **exactly on the unit circle** (equal to 1).

### Two Ways to Understand ARIMA

1. **Differencing perspective**: $w_t = \nabla^d z_t$ is a stationary ARMA process; $z_t$ is obtained by $d$-fold cumulative summation ("integration") of $w_t$
2. **Homogeneity perspective**:
   - $d = 1$: the level of $z_t$ can drift freely, but $\nabla z_t$ is stationary → **stochastic level**
   - $d = 2$: both the level and slope of $z_t$ can vary freely, but $\nabla^2 z_t$ is stationary → **stochastic level + stochastic trend**

### The Meaning of the Constant Term $\theta_0$

$$\phi(B)\nabla^d z_t = \theta_0 + \theta(B)a_t$$

When $d \geq 1$, $\theta_0 \neq 0$ implies a **deterministic trend**:
- $d = 1, \theta_0 \neq 0$: $z_t$ has a linear deterministic trend with slope $\mu_w = \theta_0/(1 - \phi_1 - \cdots - \phi_p)$

**Box's recommendation**: unless the data or physical reasoning clearly supports it, assume $\theta_0 = 0$ (stochastic trends are more flexible than deterministic ones).

---

## 4.2 Three Explicit Forms

### Form 1: Difference Equation Form

$$z_t = \varphi_1 z_{t-1} + \cdots + \varphi_{p+d} z_{t-p-d} + a_t - \theta_1 a_{t-1} - \cdots - \theta_q a_{t-q}$$

where $\varphi(B) = \phi(B)(1-B)^d$. **Most convenient for computing forecasts.**

### Form 2: Random Shock Form

$$z_t = a_t + \psi_1 a_{t-1} + \psi_2 a_{t-2} + \cdots$$

The ψ-weights are solved recursively from $\varphi(B)\psi(B) = \theta(B)$. **Required for computing forecast error variances.**

### Form 3: Inverted Form (π-weights)

$$z_t = \pi_1 z_{t-1} + \pi_2 z_{t-2} + \cdots + a_t$$

The π-weights are solved recursively from $\theta(B)\pi(B) = \varphi(B)$. **Represents the process as an infinite AR; the exponentially weighted moving average (EWMA) is a special case.**

---

## 4.3 IMA Processes — The Theoretical Foundation of Exponential Smoothing

### IMA(0,1,1)

$$\nabla z_t = (1 - \theta_1 B)a_t$$

Inverted form: $z_t = (1-\theta_1) z_{t-1} + \theta_1(1-\theta_1) z_{t-2} + \cdots + a_t$

Setting $\lambda = 1 - \theta_1$, this is precisely the **Exponentially Weighted Moving Average (EWMA)**! The weights decay exponentially at rate $\theta_1^j$.

**Historical significance**: The exponential smoothing methods of Holt/Brown/Winters were widely used before Box-Jenkins. Box demonstrated that these methods are **exactly the optimal forecasts for IMA(0,1,1)** — providing rigorous statistical foundations for empirical methods.

### IMA(0,2,2)

$$\nabla^2 z_t = (1 - \theta_1 B - \theta_2 B^2)a_t$$

The optimal forecast evolves along a **straight line** (level + slope continuously updated). Corresponds to **Holt's two-parameter exponential smoothing**.

---

## Deep Dives

### 1. Differencing vs. Detrending

- **Differencing $\nabla^d$**: Removes degree-$d$ polynomial trend; assumes trend is stochastic; applies to most economic/industrial series
- **Regression detrending**: $z_t = f(t) + \epsilon_t$; assumes trend is deterministic; applies to series with physical trends
- **Physical model detrending**: $z_t - \text{clearsky}_t$; assumes physical model is known; applies to solar PV irradiance

**For solar PV**: first detrend physically with a clear-sky model (Yang Ch7); if residuals are still non-stationary, difference once more.

### 2. Practical Choice of d

Box repeatedly emphasizes: $d$ is typically 0, 1, or at most 2.
- $d = 0$: stationary series
- $d = 1$: level drift (most common)
- $d = 2$: trend drift (less common)
- $d \geq 3$: almost never needed

### 3. Modern Tests for Unit Roots and Non-Stationarity

In Box's era, the ACF was the primary tool for deciding whether to difference (slowly decaying ACF → may need differencing). Modern methods include:
- **ADF test** (Augmented Dickey-Fuller)
- **KPSS test**
- **Phillips-Perron test**

These will be touched on indirectly in Ch6 (model identification).

### 4. The Danger of Over-Differencing

If the series is already stationary and you difference $d$ times, you **introduce unnecessary MA unit roots**, leading to unstable parameter estimation. Box's advice: err on the side of under-differencing; use ACF/PACF to judge.

---

## Summary

Ch4 = the non-stationary extension of Ch3. There is only one core formula:

$$\phi(B)(1-B)^d z_t = \theta_0 + \theta(B)a_t$$

But its power is immense — almost all non-seasonal time series can be described by ARIMA with $p, d, q \leq 2$.

**Preview of next chapter**: Ch5 will show how to use ARIMA models for optimal forecasting (minimum MSE forecast functions).

---

*📖 [Ch3 Notes](/blog/2026-03-16-box-ch3-linear-stationary-models) | [Back to Textbook Index](/textbook/) | 📝 [Box Time Series Series](/blog/)*
