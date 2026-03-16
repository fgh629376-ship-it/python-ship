---
title: "Box Time Series Analysis Ch7: Parameter Estimation — Maximum Likelihood and Nonlinear Least Squares"
description: "A close reading of Box's Time Series Analysis Chapter 7: conditional/unconditional likelihood, nonlinear iterative estimation, parameter standard errors and confidence intervals"
pubDate: 2026-03-16
lang: en
series: box-timeseries
category: timeseries
tags: ["time series", "parameter estimation", "MLE", "least squares", "ARIMA", "textbook notes"]
---

# Box Time Series Analysis Ch7: Parameter Estimation — Maximum Likelihood and Nonlinear Least Squares

> **Textbook**: Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 7

## Chapter Overview

Ch6 provided candidate models and rough estimates. Ch7 performs **precise estimation** — using MLE or equivalent nonlinear least squares to obtain statistically efficient parameter values and standard errors.

---

## 7.1 Likelihood Function

### Conditional Likelihood

Given the model $\phi(B)\nabla^d z_t = \theta(B)a_t$ with $a_t \sim N(0, \sigma_a^2)$ i.i.d.:

$$l^*(\phi, \theta, \sigma_a^2) = -\frac{n}{2}\ln(\sigma_a^2) - \frac{S^*(\phi, \theta)}{2\sigma_a^2}$$

where the conditional residual sum of squares is:

$$S^*(\phi, \theta) = \sum_{t=1}^{n} a_t^2(\phi, \theta | w^*, a^*, w)$$

**Conditional MLE = Conditional Least Squares** — minimizing $S^*(\phi, \theta)$ is sufficient.

### Conditional vs. Unconditional

- **Conditional likelihood**: Set $a^* = 0$, $w^*$ = actual values; for long series ($n > 50$), simple and fast
- **Unconditional likelihood**: Integrate over/backcast initial values; for short series or AR roots near unit circle

Box recommends: **conditional likelihood is usually sufficient**, but seasonal models (Ch9) must use unconditional likelihood.

---

## 7.2 Nonlinear Iterative Estimation

The likelihood function for ARIMA is **nonlinear** in $\theta$ (MA parameters enter the residual recursion nonlinearly). Iterative methods are needed:

### Marquardt Algorithm

Combines the advantages of Newton's method and steepest descent:

$$(\mathbf{H} + \lambda \mathbf{I})\boldsymbol{\delta} = -\mathbf{g}$$

- Large $\lambda$ → steepest descent (safe but slow)
- Small $\lambda$ → Newton's method (fast but may diverge)
- Adaptively adjusts $\lambda$ at each step

### Parameter Standard Errors

$$\hat{V}(\hat{\xi}) \approx 2\hat{\sigma}_a^2 \mathbf{H}^{-1}$$

where $\mathbf{H}$ is the Hessian of $S(\phi, \theta)$ evaluated at the MLE.

**Confidence intervals**: $\hat{\xi}_j \pm z_{\alpha/2} \hat{\sigma}(\hat{\xi}_j)$

---

## 7.3 Special Properties of AR Parameters

**Yule-Walker estimates for AR are already approximately efficient** — because the likelihood function for AR models is approximately linear in $\phi$.

$$\hat{\boldsymbol{\phi}}_{YW} \approx \hat{\boldsymbol{\phi}}_{MLE}$$

### MA Parameters Are Different

Moment estimates for MA are **not efficient** — they may be much worse than MLE. Iterative MLE from Ch7 is necessary.

---

## 7.4 Geometry of the Likelihood Surface

### Single Parameter (e.g., IMA(0,1,1))

$S(\theta)$ as a function of $\theta$ forms a U-shaped curve; the minimum corresponds to the MLE.

### Multiple Parameters

Contours of $S(\phi, \theta)$ may be ellipses (low parameter correlation) or elongated "valleys" (high parameter correlation).

**Parameter correlation**: When $\phi$ and $\theta$ are close (e.g., $\phi_1 \approx \theta_1$ in ARMA(1,1)), the likelihood surface has a long ridge → the two parameters are nearly indistinguishable → very large standard errors.

---

## 7.5 Bayesian Perspective

Likelihood × prior = posterior distribution. With a flat (non-informative) prior, posterior ∝ likelihood.

Box leans toward **likelihoodism** — let the data speak, without subjective priors. But acknowledges the Bayesian framework has advantages with small samples.

---

## Deep Thinking

### 1. Asymptotic Properties of MLE

In large samples, MLE is:
- **Consistent**: $\hat{\theta} \to \theta_0$
- **Asymptotically normal**: $\sqrt{n}(\hat{\theta} - \theta_0) \to N(0, I^{-1})$
- **Asymptotically efficient**: achieves the Cramér-Rao lower bound

Whittle (1953) extended these properties from independent observations to stationary time series.

### 2. Likelihood Surface Characteristics of Over-parameterized Models

When $\phi_1 \approx \theta_1$ in ARMA(1,1), AR and MA almost cancel → model degenerates to white noise. The "ridge" in the likelihood surface means **parameters are not identifiable** — this is an inherent problem with ARMA models, and is why parsimony is so important.

### 3. Guidance for Solar Power Forecasting

- **Use `statsmodels.tsa.arima.model.ARIMA`**: internally implements conditional and unconditional MLE
- Pay attention to parameter standard errors — if $\hat{\sigma}(\hat{\phi})$ is on the same order as $\hat{\phi}$, the parameter is not significant
- The $\phi \approx \theta$ problem in ARMA(1,1) is common in real data → possibly AR(1) or MA(1) alone is sufficient

---

## Summary

Ch7 = From rough estimates to precise estimates:

$$\text{Ch6 initial estimates} \xrightarrow{\text{Marquardt iteration}} \hat{\phi}_{MLE}, \hat{\theta}_{MLE} \xrightarrow{\text{Hessian}} \text{Standard errors}$$

Core conclusions:
- **MLE = Minimizing residual sum of squares** (under normality)
- Yule-Walker for AR is already approximately efficient
- MA requires iterative MLE
- Parameter standard errors = inverse of Hessian
- Parsimony prevents over-parameterization

---

*📖 [Ch6 Notes](/blog/2026-03-16-box-ch6-model-identification) | [Back to Textbook Index](/textbook/) | 📝 [Box Time Series Series](/blog/)*
