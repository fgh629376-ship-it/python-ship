---
title: "Box Time Series Analysis Ch2: ACF and Spectrum — Two Keys to Time Series Analysis"
description: "A close reading of Box's Time Series Analysis Chapter 2: from stationarity to ACF positive definiteness, from the periodogram to spectral density — understanding the perfect duality of time and frequency domains"
pubDate: 2026-03-16
lang: en
series: box-timeseries
category: timeseries
tags: ["time series", "autocorrelation function", "spectral analysis", "stationarity", "Bartlett", "textbook notes"]
---

# Box Time Series Analysis Ch2: ACF and Spectrum — Two Keys to Time Series Analysis

> **Textbook**: Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 2

## Chapter Positioning

Ch1 gave us the "what to do" blueprint; Ch2 answers "how to look" — how to describe the statistical characteristics of a stationary time series. Box provides two equivalent keys:
1. **Autocorrelation Function (ACF)**: time-domain perspective, measuring linear dependence at different lags
2. **Spectral Density Function**: frequency-domain perspective, decomposing variance across different frequencies

The two are Fourier transform pairs — mathematically equivalent but providing different intuitions.

---

## 2.1 Autocorrelation Properties of Stationary Processes

### 2.1.1 Time Series and Stochastic Processes

Box distinguishes two ways discrete time series are generated:
1. **Sampling a continuous process**: e.g., measuring a chemical furnace every 9 seconds (discretization)
2. **Cumulative variables**: e.g., daily rainfall, batch yields (aggregation)

**Key definition**: A time series $z_1, z_2, \ldots, z_N$ is a **single realization** of the underlying stochastic process. Statistical inference = inferring the properties of the stochastic process from this single realization.

### 2.1.2 Stationary Stochastic Processes

**Strictly Stationary**: The joint distribution of any $m$ time points depends only on the time differences, not on absolute time.

$$p(z_{t_1}, z_{t_2}, \ldots, z_{t_m}) = p(z_{t_1+k}, z_{t_2+k}, \ldots, z_{t_m+k}) \quad \forall k$$

This implies:
- **Constant mean**: $\mu = E[z_t]$
- **Constant variance**: $\sigma_z^2 = E[(z_t - \mu)^2]$

**Autocovariance coefficient** (lag $k$):
$$\gamma_k = \text{cov}[z_t, z_{t+k}] = E[(z_t - \mu)(z_{t+k} - \mu)]$$

**Autocorrelation coefficient**:
$$\rho_k = \frac{\gamma_k}{\gamma_0}$$

Note that $\rho_0 = 1$ and $\rho_k = \rho_{-k}$ (ACF is symmetric about zero).

### 2.1.3 Positive Definiteness and the Autocovariance Matrix (Key Point!)

The covariance matrix of $n$ consecutive observations is a **Toeplitz matrix** (elements along each diagonal are identical):

$$\boldsymbol{\Gamma}_n = \sigma_z^2 \begin{pmatrix} 1 & \rho_1 & \rho_2 & \cdots & \rho_{n-1} \\ \rho_1 & 1 & \rho_1 & \cdots & \rho_{n-2} \\ \vdots & & & \ddots & \vdots \\ \rho_{n-1} & \rho_{n-2} & \cdots & & 1 \end{pmatrix}$$

**Key property**: The autocovariance matrix must be **positive definite** (all eigenvalues > 0).

This means autocorrelation coefficients cannot take arbitrary values! For example:
- $n=2$: $|\rho_1| < 1$
- $n=3$: $-1 < \frac{\rho_2 - \rho_1^2}{1 - \rho_1^2} < 1$ (this is actually the constraint on partial autocorrelation $\phi_{22}$!)

**Significance for PV forecasting**: When estimating ACF with numpy in Python, direct truncation may yield a non-positive-definite covariance matrix, causing issues in subsequent MLE estimation. Ensuring positive definiteness is an important practical programming detail.

**Linear operations preserve stationarity**: If $z_t$ is stationary, then $y_t = \sum_{i=0}^{\infty} \psi_i z_{t-i}$ ($\sum|\psi_i| < \infty$) is also stationary. This is **the foundation for ARMA model validity** — white noise is stationary, and the output through a stable filter is also stationary.

**Gaussian processes**: If the joint distribution is multivariate normal, then weak stationarity → strict stationarity. Because the normal distribution is completely determined by its first moment (mean) and second moment (covariance).

### 2.1.4 Autocovariance Function and Autocorrelation Function

The ACF plot $\{\rho_k\}$ reveals the **dependence structure** of the time series:
- **Positive correlation**: adjacent values tend to have the same sign (smooth series)
- **Negative correlation**: adjacent values tend to have opposite signs (sawtooth series)
- **Decay rate**: exponential decay, sinusoidal decay, truncation — corresponding to different models

**A normal stationary process is completely characterized by $\mu$, $\sigma_z^2$, and $\{\rho_k\}$.**

### 2.1.5 Estimation of the ACF

Sample autocorrelation function:

$$r_k = \frac{c_k}{c_0}, \quad c_k = \frac{1}{N}\sum_{t=1}^{N-k}(z_t - \bar{z})(z_{t+k} - \bar{z})$$

Box demonstrates the computation using chemical batch data (70 observations). The result $r_1 = -0.39$ indicates that adjacent batch yields are **negatively correlated** — a high-yield batch leaves tar residue that affects the next batch.

**Practical guidelines**:
- At least 50 observations needed
- Compute up to lag $K \leq N/4$ at most
- Two decimal places of precision suffice

### 2.1.6 Standard Error of ACF Estimates (Bartlett's Formula)

Bartlett (1946) provided the approximate variance of $r_k$ under a stationary normal process:

$$\text{var}[r_k] \approx \frac{1}{N} \sum_{v=-\infty}^{\infty} (\rho_v^2 + \rho_{v+k}\rho_{v-k} - 4\rho_k\rho_v\rho_{v-k} + 2\rho_v^2\rho_k^2)$$

**Simplification for large lags**: If $\rho_v = 0$ for all $v > q$, then for $k > q$:

$$\text{var}[r_k] \approx \frac{1}{N}\left(1 + 2\sum_{v=1}^{q} \rho_v^2\right)$$

**White noise special case** ($q=0$): $\text{se}[r_k] \approx 1/\sqrt{N}$

This is the origin of the "significance bands" ($\pm 2/\sqrt{N}$) drawn on ACF plots! Values of $r_k$ exceeding this band are considered significantly non-zero.

**Bartlett's important caveat**: Adjacent $r_k$ values may be highly correlated, which can distort the visual appearance of the ACF. **Don't look at individual $r_k$ values — judge the overall pattern**.

---

## 2.2 Spectral Properties of Stationary Processes

### 2.2.1 The Periodogram

Decomposing the time series into sine and cosine components:

$$z_t = \alpha_0 + \sum_{i=1}^{q} (\alpha_i \cos 2\pi f_i t + \beta_i \sin 2\pi f_i t) + e_t$$

**Periodogram intensity**: $I(f_i) = \frac{N}{2}(a_i^2 + b_i^2)$

Box demonstrates using 1964 monthly mean temperatures for England — the main component is at $f = 1/12$ (annual cycle), consistent with intuition.

### 2.2.2 Analysis of Variance Perspective

$$\sum_{t=1}^{N}(z_t - \bar{z})^2 = \sum_{i=1}^{q} I(f_i)$$

Total variance = sum of contributions from each frequency component. Each $I(f_i)$ accounts for 2 degrees of freedom.

If the series is white noise, each $I(f_i) \sim \sigma^2 \chi^2(2)$. If periodic components exist, the corresponding $I(f_i)$ will be significantly amplified.

### 2.2.3 The Spectral Density Function

The **sample spectrum** $I(f)$ and autocovariance estimates are connected via the Fourier transform:

$$I(f) = 2\left(c_0 + 2\sum_{k=1}^{N-1} c_k \cos 2\pi fk\right)$$

**Theoretical power spectrum**:

$$p(f) = 2\left(\gamma_0 + 2\sum_{k=1}^{\infty} \gamma_k \cos 2\pi fk\right), \quad 0 \leq f \leq \frac{1}{2}$$

**Spectral density function** (normalized):

$$g(f) = \frac{p(f)}{\sigma_z^2} = 2\left(1 + 2\sum_{k=1}^{\infty} \rho_k \cos 2\pi fk\right)$$

Satisfying $\int_0^{1/2} g(f)\,df = 1$ (analogous to a probability density).

### Key Properties

1. **$p(f) \geq 0$** for all $f$ (the frequency-domain equivalent of positive definiteness!)
2. **$\gamma_0 = \int_0^{1/2} p(f)\,df$** (total variance = integral of the spectrum over all frequencies)
3. **ACF ↔ spectrum** are Fourier transform pairs: knowing one determines the other

### 2.2.4 Two Simple Examples

**Model 1:** $z_t = 10 + a_t + a_{t-1}$
- ACF: $\rho_1 = 0.5$, $\rho_k = 0$ ($k \geq 2$)
- Spectrum: $g(f) = 2[1 + \cos(2\pi f)]$ (low-frequency dominant)
- Series appearance: Smooth

**Model 2:** $z_t = 10 + a_t - a_{t-1}$
- ACF: $\rho_1 = -0.5$, $\rho_k = 0$ ($k \geq 2$)
- Spectrum: $g(f) = 2[1 - \cos(2\pi f)]$ (high-frequency dominant)
- Series appearance: Sawtooth

These two MA(1) models perfectly demonstrate:
- **Positive autocorrelation → energy concentrated at low frequencies → smooth series**
- **Negative autocorrelation → energy concentrated at high frequencies → sawtooth series**

### 2.2.5 ACF vs Spectrum: Which to Choose

Box's view is pragmatic:
- The two are mathematically equivalent — "allies, not adversaries"
- Both are **nonparametric methods** (unstructured), similar to histograms
- The subsequent goal is selecting parametric models (ARMA)
- Box primarily uses ACF in this book (because the ACF forms of ARMA models are more intuitive)

---

## Deep Reflections: Implications of Ch2 for PV Power Forecasting

### 1. Programming Implications of ACF Positive Definiteness

When computing sample ACF using `statsmodels.tsa.acf()` in Python, a truncated ACF does not guarantee a positive definite matrix. If you need to construct a covariance matrix from the ACF (e.g., for Kriging, GP regression), you must additionally ensure positive definiteness — common methods include spectral truncation or Toeplitz matrix positive-definite correction.

### 2. Role of Bartlett Standard Errors in Model Diagnostics

After fitting an ARIMA model, residuals should be white noise. The diagnostic method: plot the residual ACF and check if all values fall within the $\pm 2/\sqrt{N}$ band. This is the foundation of Ch8 diagnostic tests, but the standard comes from Ch2.

### 3. Spectral Analysis Applications in PV

The spectral structure of solar irradiance has distinctive features:
- **Diurnal cycle**: $f = 1/24h$ (strongest signal)
- **Annual cycle**: $f = 1/365d$
- **Weather systems**: $f \approx 1/(3\text{-}7d)$
- **Cloud high-frequency disturbances**: $f > 1/1h$

Understanding spectral structure helps with:
- Choosing appropriate sampling frequency (Nyquist)
- Designing filters to remove specific frequency interference
- Judging whether an ARIMA model adequately captures the main frequency components

### 4. Practical Impact of Weak vs Strict Stationarity

Box points out that under Gaussian processes, weak stationarity = strict stationarity. PV data is typically **not normal** (truncated: nighttime power is 0; skewed: cloud occlusion), so weak stationarity ≠ strict stationarity. This means ACF description alone may be insufficient — higher-order moments may need consideration (e.g., GARCH models for conditional heteroscedasticity).

### 5. Connection to Warner NWP

The numerical filters in Warner Ch4 spectral analysis (Robert-Asselin filter, implicit diffusion) and Box's linear filter $y_t = \psi(B)z_t$ are essentially the same. The 2Δt computational noise in NWP (computational mode from the leapfrog scheme) corresponds to the sawtooth pattern where $\rho_1 < 0$ in ACF — this is a physical example of negative MA(1) coefficients.

---

## Summary

Ch2 establishes the descriptive tools for time series analysis:

- **Theory**: Time domain — Autocovariance $\gamma_k$ / Autocorrelation $\rho_k$; Frequency domain — Power spectrum $p(f)$ / Spectral density $g(f)$
- **Estimation**: Time domain — Sample ACF $r_k$; Frequency domain — Sample spectrum $I(f)$ / Smoothed spectrum $\hat{p}(f)$
- **Precision**: Time domain — Bartlett standard error; Frequency domain — Spectral window width
- **Relationship**: Fourier transform pair

**Core theorem**: Autocovariance sequence $\{\gamma_k\}$ is positive definite $\Leftrightarrow$ spectrum $p(f) \geq 0$

**Next chapter preview**: Ch3 will use these tools to analyze specific AR, MA, and ARMA models — given $\phi$ and $\theta$ parameters, derive the analytical forms of ACF and spectrum.

---

*📖 [Ch1 Notes](/blog/2026-03-16-box-ch1-introduction) | [Back to Textbook Index](/textbook/) | 📝 [Box Time Series Series](/blog/)*
