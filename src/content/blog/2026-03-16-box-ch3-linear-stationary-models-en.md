---
title: "Box Time Series Analysis Ch3: A Complete Dissection of AR, MA, and ARMA Models"
description: "A close reading of Chapter 3 of Box's Time Series Analysis: from the Wold decomposition to AR/MA duality, mastering PACF cutoff for order identification, the Yule-Walker equations, and invertibility conditions"
pubDate: 2026-03-16
lang: en
series: box-timeseries
category: timeseries
tags: ["time series", "ARIMA", "AR model", "MA model", "PACF", "Yule-Walker", "textbook notes"]
---

# Box Time Series Analysis Ch3: A Complete Dissection of AR, MA, and ARMA Models

> **Textbook**: Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 3

## Chapter Overview

Ch2 provided descriptive tools (ACF/spectrum); Ch3 gives us **actionable parametric models**. This is the most theoretically central chapter in the book — all subsequent modeling, forecasting, and control builds on the AR/MA/ARMA framework established here.

---

## 3.1 The General Linear Process

### The Wold Decomposition Theorem

**Any** zero-mean purely non-deterministic stationary process can be written as:

$$\tilde{z}_t = \sum_{j=0}^{\infty} \psi_j a_{t-j}, \quad \psi_0 = 1, \quad \sum_{j=0}^{\infty} \psi_j^2 < \infty$$

This is the fundamental result of Wold (1938). The significance: **linear models are not an "assumption" but a universal representation of stationary processes**.

### Duality Between ψ-Weights and π-Weights

- **ψ form** (MA representation): $\tilde{z}_t = \psi(B)a_t$ (current value = weighted sum of past shocks)
- **π form** (AR representation): $\pi(B)\tilde{z}_t = a_t$ (current shock = linear combination of current and past values)

Relationship: $\psi(B)\pi(B) = 1$, i.e., $\pi(B) = \psi^{-1}(B)$

### Autocovariance Generating Function

$$\gamma(B) = \sigma_a^2 \psi(B)\psi(B^{-1})$$

**Spectrum and filter gain**: $p(f) = 2\sigma_a^2 |\psi(e^{-i2\pi f})|^2$

Output spectrum = white noise spectrum × squared filter gain.

### Stationarity and Invertibility

- **Stationary**: requires $\sum|\psi_j| < \infty$; equivalent to $\psi(B)$ converges for $|B| \leq 1$
- **Invertible**: requires $\sum|\pi_j| < \infty$; equivalent to $\pi(B)$ converges for $|B| \leq 1$

**Physical meaning of invertibility**: the current value can be expressed using past values (not future values). If $|\theta| \geq 1$, the π-weights of the MA model diverge — the current value depends on the infinitely distant past with ever-increasing weights, which is physically unreasonable.

---

## 3.2 Autoregressive Processes AR(p)

### Stationarity Condition

All roots of $\phi(B) = 0$ lie **outside the unit circle**. Equivalently, the roots of the characteristic equation $m^p - \phi_1 m^{p-1} - \cdots - \phi_p = 0$ lie **inside the unit circle**.

### Difference Equation for the ACF

$$\rho_k = \phi_1\rho_{k-1} + \phi_2\rho_{k-2} + \cdots + \phi_p\rho_{k-p}, \quad k > 0$$

General solution: $\rho_k = A_1 G_1^k + A_2 G_2^k + \cdots + A_p G_p^k$

- **Real roots** → exponential decay
- **Complex conjugate roots** → damped sinusoids (pseudo-periodic behavior)

### AR(1): The Markov Process

$$\tilde{z}_t = \phi_1 \tilde{z}_{t-1} + a_t, \quad |\phi_1| < 1$$

- ACF: $\rho_k = \phi_1^k$ (exponential decay)
- Variance: $\sigma_z^2 = \sigma_a^2 / (1 - \phi_1^2)$
- Spectrum: $p(f) = 2\sigma_a^2 / (1 + \phi_1^2 - 2\phi_1\cos 2\pi f)$
- $\phi_1 > 0$ → smooth trends, low-frequency dominance
- $\phi_1 < 0$ → sawtooth oscillations, high-frequency dominance

### AR(2): Pseudo-Periodic Behavior

Stationarity conditions (triangular region): $\phi_2 + \phi_1 < 1$, $\phi_2 - \phi_1 < 1$, $-1 < \phi_2 < 1$

ACF with complex roots: $\rho_k = D^k \sin(2\pi f_0 k + F) / \sin F$

where the damping factor $D = \sqrt{-\phi_2}$, frequency $f_0 = \cos^{-1}(\phi_1 / 2\sqrt{-\phi_2}) / (2\pi)$

**Implication for solar PV**: irradiance series often exhibit pseudo-periodic behavior (weather system cycles of 3–7 days); AR(2) can capture this behavior.

### Yule-Walker Equations

$$\boldsymbol{P}_p \boldsymbol{\phi} = \boldsymbol{\rho}_p$$

A system of linear equations — substitute estimated ACF values $r_k$ to solve for AR parameters.

### PACF (Partial Autocorrelation Function)

$$\phi_{kk} = \text{corr}[z_t - \hat{z}_t, z_{t-k} - \hat{z}_{t-k}]$$

**Key property: the PACF of an AR(p) process cuts off to zero after lag $p$.**

- AR(1): $\phi_{11} = \rho_1$, $\phi_{kk} = 0$ ($k \geq 2$)
- AR(2): $\phi_{22} = (\rho_2 - \rho_1^2)/(1 - \rho_1^2)$, $\phi_{kk} = 0$ ($k \geq 3$)

Standard error of estimated PACF: $\text{SE}[\hat{\phi}_{kk}] \approx 1/\sqrt{n}$ ($k \geq p+1$)

---

## 3.3 Moving Average Processes MA(q)

### Invertibility Condition

The roots of $\theta(B) = 0$ lie outside the unit circle.

### Cutoff Property of the ACF

$$\rho_k = \begin{cases} \frac{-\theta_k + \theta_1\theta_{k+1} + \cdots + \theta_{q-k}\theta_q}{1 + \theta_1^2 + \cdots + \theta_q^2} & k = 1, \ldots, q \\ 0 & k > q \end{cases}$$

**Key property: the ACF of an MA(q) process cuts off to zero after lag $q$.**

### MA(1) in Detail

- ACF: $\rho_1 = -\theta_1 / (1 + \theta_1^2)$, $\rho_k = 0$ ($k > 1$)
- $|\rho_1| \leq 0.5$ (theoretical upper bound for MA(1)!)
- Given $\rho_1$, there are two solutions for $\theta_1$ ($\theta_1$ and $\theta_1^{-1}$); take the invertible solution with $|\theta_1| < 1$

### The Perfect Duality of AR ↔ MA

- **ACF**: AR(p) tails off (exponential decay / damped sinusoid); MA(q) **cuts off after lag $q$**
- **PACF**: AR(p) **cuts off after lag $p$**; MA(q) tails off (exponential decay / damped sinusoid)
- **Stationarity**: AR(p) requires roots of $\phi(B) = 0$ outside circle; MA(q) always stationary
- **Invertibility**: AR(p) always invertible; MA(q) requires roots of $\theta(B) = 0$ outside circle
- **Spectrum**: AR(p) $p(f) \propto 1/|\phi(e^{-i2\pi f})|^2$; MA(q) $p(f) \propto |\theta(e^{-i2\pi f})|^2$

This duality is the core tool for model identification (Ch6):
- **ACF cuts off → MA model**
- **PACF cuts off → AR model**
- **Both tail off → ARMA mixed model**

---

## 3.4 ARMA(p,q) Mixed Processes

$$\phi(B)\tilde{z}_t = \theta(B)a_t$$

- Stationary: roots of $\phi(B) = 0$ outside the circle
- Invertible: roots of $\theta(B) = 0$ outside the circle
- ACF: the first $q-p+1$ values are directly influenced by θ parameters; thereafter satisfies the difference equation $\phi(B)\rho_k = 0$ → exponential decay / damped sinusoid
- PACF: the first $p-q+1$ values are influenced by φ; thereafter similar to MA PACF → exponential decay
- Spectrum: $p(f) = 2\sigma_a^2 |\theta(e^{-i2\pi f})|^2 / |\phi(e^{-i2\pi f})|^2$

### ARMA(1,1) in Detail

$$(1 - \phi_1 B)\tilde{z}_t = (1 - \theta_1 B)a_t$$

- $\psi_j = (\phi_1 - \theta_1)\phi_1^{j-1}$ ($j \geq 1$)
- $\rho_1 = (1 - \phi_1\theta_1)(\phi_1 - \theta_1)/(1 + \theta_1^2 - 2\phi_1\theta_1)$
- $\rho_k = \phi_1 \rho_{k-1}$ ($k \geq 2$) — exponential decay starting from $\rho_1$

---

## Deep Dives

### 1. The Mathematical Implementation of Parsimony

Ch3 answers "why is ARMA sufficient":
- The Wold theorem guarantees every stationary process has a $\psi(B)$ representation
- $\psi(B) = \phi^{-1}(B)\theta(B)$ is a **rational function approximation** (Padé approximation)
- Low-order rational functions ($p, q \leq 2$) can approximate infinite series with high accuracy
- This is the mathematical foundation of the parsimony principle

### 2. ACF/PACF Cutoff = Model Identification Fingerprints

- ACF cuts off at lag $q$, PACF tails off → **MA(q)**
- ACF tails off, PACF cuts off at lag $p$ → **AR(p)**
- Both tail off → **ARMA(p,q)**
- Both cut off → Impossible (contradiction)

### 3. Specific Guidance for Solar PV Forecasting

- **Residuals after removing the diurnal cycle**: typically ACF tails off but decays quickly → AR(1) or AR(2) candidate
- **Cloud shading events**: cause abrupt changes; AR model ψ-weights are too smooth → may need MA terms
- **Multi-site spatial correlation**: Ch14's VAR model is the multivariate extension of AR

---

## Summary

Ch3 establishes the complete theory for the ARMA model family:

**Three model types** = AR (regression on past values) + MA (weighted sum of shocks) + ARMA (mixed)

**Two identification tools** = ACF (cutoff → MA) + PACF (cutoff → AR)

**Two validity conditions** = Stationarity (roots of $\phi(B)=0$ outside circle) + Invertibility (roots of $\theta(B)=0$ outside circle)

**Preview of next chapter**: Ch4 introduces non-stationarity — the difference operator $\nabla^d$ extends ARMA to ARIMA.

---

*📖 [Ch2 Notes](/blog/2026-03-16-box-ch2-acf-spectrum) | [Back to Textbook Index](/textbook/) | 📝 [Box Time Series Series](/blog/tags/time-series)*
