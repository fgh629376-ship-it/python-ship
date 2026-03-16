---
title: "MIT Probability & Statistics Core: From Bayesian Inference to MLE — The Statistical Foundation of Solar Power Forecasting"
description: "Integrating MIT 18.05/18.650 curriculum: probability foundations, parameter estimation (MLE/method of moments/Bayesian), hypothesis testing, regression, PCA, GLM — how statistics serves solar PV power forecasting"
pubDate: 2026-03-16
lang: en
series: mit-courses
category: algorithm
tags: ["Probability & Statistics", "MIT", "MLE", "Bayesian", "Hypothesis Testing", "Regression", "Textbook Notes"]
---

# MIT Probability & Statistics Core: From Bayesian Inference to MLE

> **Course System**: MIT 18.05 (Intro to Probability & Statistics, Spring 2022) + MIT 18.650 (Statistics for Applications, Fall 2016)
> **Reference Texts**: Grinstead & Snell *Introduction to Probability*; Murphy *Probabilistic Machine Learning* Book 1

## Why Is Probability & Statistics Critical for Solar PV Forecasting?

The essence of solar PV forecasting is **uncertainty quantification**:

- "Solar power output at noon tomorrow will be 500kW" → deterministic forecast (not enough)
- "Power output at noon tomorrow will be between 400–600kW with 90% probability" → **probabilistic forecast** (the core of Yang Ch11)

Probability & statistics provides:
1. **Modeling tools**: probability distributions, likelihood functions, Bayesian inference
2. **Estimation methods**: MLE, method of moments, least squares
3. **Validation framework**: hypothesis testing, confidence intervals, p-values
4. **Dimensionality reduction**: PCA (statistical perspective)

---

## Part 1: Probability Foundations (18.05 First Half)

### The Probability Space Triple

$$(\Omega, \mathcal{F}, P)$$

- $\Omega$: sample space (all possible outcomes)
- $\mathcal{F}$: event collection ($\sigma$-algebra)
- $P$: probability measure ($P(\Omega) = 1$, countably additive)

### Conditional Probability and Bayes' Theorem

$$P(A|B) = \frac{P(B|A)P(A)}{P(B)}$$

**Three interpretations**:
- **Frequentist**: $P(A)$ = long-run frequency
- **Bayesian**: $P(A)$ = degree of belief, updatable
- **Box's stance**: Ch7 discusses both, leaning toward likelihoodism — "let the data speak"

### Key Distribution Families

**Discrete**:
- Bernoulli($p$): binary outcome (sunny/cloudy)
- Binomial($n, p$): number of successes in $n$ trials
- Poisson($\lambda$): rare event counts (equipment failure count)

**Continuous**:
- Normal($\mu, \sigma^2$): **king of the Central Limit Theorem** — Box ARIMA assumes $a_t \sim N(0, \sigma_a^2)$
- Exponential($\lambda$): waiting times (time between failures)
- Beta($\alpha, \beta$): prior for proportions/probabilities (clearness index $k_t \in [0,1]$)
- Gamma($\alpha, \beta$): positive continuous quantities (irradiance, power)

### Law of Large Numbers and Central Limit Theorem

**Law of Large Numbers**: $\bar{X}_n \xrightarrow{P} \mu$ (sample mean converges to population mean)

**Central Limit Theorem**: $\sqrt{n}(\bar{X}_n - \mu) \xrightarrow{d} N(0, \sigma^2)$

**CLT is the cornerstone of statistical inference** — even if the raw data is not normally distributed, the distribution of the sample mean approaches normal. This is why Box's assumption of normally distributed residuals is generally reasonable.

---

## Part 2: Parameter Estimation (18.650 Lec 1–4)

### Maximum Likelihood Estimation (MLE)

$$\hat{\theta}_{MLE} = \arg\max_\theta \mathcal{L}(\theta) = \arg\max_\theta \prod_{i=1}^n f(x_i|\theta)$$

In practice, take the log: $\hat{\theta}_{MLE} = \arg\max_\theta \ell(\theta) = \arg\max_\theta \sum_{i=1}^n \ln f(x_i|\theta)$

**Desirable properties of MLE**:
- **Consistency**: $\hat{\theta}_n \xrightarrow{P} \theta_0$
- **Asymptotic normality**: $\sqrt{n}(\hat{\theta}_n - \theta_0) \xrightarrow{d} N(0, I(\theta_0)^{-1})$
- **Asymptotic efficiency**: achieves the Cramér-Rao lower bound

**Fisher Information**: $I(\theta) = -E\left[\frac{\partial^2 \ell}{\partial \theta^2}\right]$ → theoretical limit of parameter estimation precision

### Perfect Alignment with Box

Box Ch7's parameter estimation **is** MLE:
- Conditional MLE = conditional least squares (minimizing residual sum of squares $S^*(\phi, \theta)$)
- Fisher information matrix = Hessian → parameter standard errors $\hat{V}(\hat{\xi}) \approx 2\hat{\sigma}_a^2 H^{-1}$
- Marquardt algorithm = regularized Newton's method (Matrix Calculus Lec 9!)

### Method of Moments

$$\hat{\mu}_k = \frac{1}{n}\sum_{i=1}^n X_i^k \quad \text{(sample moments = population moments)}$$

Solve the system of equations to obtain parameter estimates.

**Box Ch6's Yule-Walker estimation is a special case of the method of moments**: use sample ACF (moments) to match theoretical ACF (moments) to estimate AR parameters.

Method of moments is simple but less efficient than MLE — Box emphasizes that moment estimates of MA parameters are **not efficient** and iterative MLE must be used.

### Bayesian Estimation

$$p(\theta|x) = \frac{p(x|\theta)p(\theta)}{p(x)} \propto \text{likelihood} \times \text{prior}$$

- **Prior** $p(\theta)$: belief before estimation
- **Likelihood** $p(x|\theta)$: evidence from the data
- **Posterior** $p(\theta|x)$: updated belief

**MAP estimation**: $\hat{\theta}_{MAP} = \arg\max_\theta p(\theta|x)$

**With non-informative priors, MAP = MLE** (confirmed in Box Ch7)

**Implications for solar PV forecasting**:
- **Prior knowledge**: physical constraints (power $\geq 0$, $\leq$ installed capacity) can be encoded as priors
- **Online updating**: new data arrives each day → Bayesian update of posterior → model adaptation
- **Uncertainty quantification**: the posterior distribution directly yields prediction intervals (more flexible than the constant-width intervals in Box Ch5)

---

## Part 3: Hypothesis Testing (18.650 Lec 5–6)

### Basic Framework

$$H_0: \theta = \theta_0 \quad \text{vs} \quad H_1: \theta \neq \theta_0$$

- **Type I error** ($\alpha$): reject $H_0$ when it is true (false alarm)
- **Type II error** ($\beta$): fail to reject when $H_1$ is true (missed detection)
- **Power** = $1 - \beta$

### Likelihood Ratio Test

$$\Lambda = 2(\ell(\hat{\theta}_{MLE}) - \ell(\theta_0)) \xrightarrow{d} \chi^2(k)$$

**Box Ch8's Ljung-Box Q test is a variant of the likelihood ratio test**:
- $H_0$: residuals are white noise (model is adequate)
- $\tilde{Q}(K) = n(n+2)\sum_{k=1}^K \frac{r_k^2}{n-k} \sim \chi^2(K-p-q)$

### Goodness-of-Fit Test

**Kolmogorov-Smirnov test**: compares the maximum discrepancy between the empirical CDF and the theoretical CDF

**Box Ch8's cumulative periodogram test** is the frequency-domain version of the KS test — checking whether the residual spectrum is uniform (a characteristic of white noise).

### Information Criteria

$$AIC = -2\ell(\hat{\theta}) + 2k, \quad BIC = -2\ell(\hat{\theta}) + k\ln n$$

**Box Ch6** uses AIC/BIC to select $p, q$ — trading off goodness of fit against model complexity.

---

## Part 4: Regression Analysis (18.650 Lec 7)

### Probabilistic View of Linear Regression

$$Y_i = \mathbf{x}_i^T\boldsymbol{\beta} + \epsilon_i, \quad \epsilon_i \sim N(0, \sigma^2)$$

**MLE = least squares** (when errors are normal):

$$\hat{\boldsymbol{\beta}} = (X^TX)^{-1}X^T\mathbf{y}$$

This is exactly the orthogonal projection formula from MIT 18.06 Part 2!

### Statistical Inference

- **Distribution of $\hat{\beta}_j$**: $\hat{\beta}_j \sim N(\beta_j, \sigma^2(X^TX)^{-1}_{jj})$
- **t-test**: $t = \hat{\beta}_j / \text{se}(\hat{\beta}_j) \sim t(n-p)$
- **F-test**: overall model significance

### Multicollinearity

When $X^TX$ is nearly singular (large condition number), the variance of $\hat{\boldsymbol{\beta}}$ explodes.

**Solutions**:
- Ridge regression: $\hat{\boldsymbol{\beta}}_{ridge} = (X^TX + \lambda I)^{-1}X^T\mathbf{y}$ (Bayesian interpretation: normal prior)
- Lasso: $L_1$ regularization → sparse solution (feature selection)
- PCA regression: dimensionality reduction before regression

**Connection to 18.06**: condition number $\kappa(X^TX) = \sigma_1^2/\sigma_r^2$ → Ridge is equivalent to truncating small singular values

---

## Part 5: Bayesian Statistics (18.650 Lec 8)

### Conjugate Priors

When the product of prior and likelihood still belongs to the same distribution family:

- Normal likelihood + Normal prior → Normal posterior
- Bernoulli likelihood + Beta prior → Beta posterior
- Poisson likelihood + Gamma prior → Gamma posterior

### MCMC Sampling

When the posterior cannot be computed analytically (most cases):
- **Metropolis-Hastings**: propose-accept/reject
- **Gibbs sampling**: coordinate-wise conditional sampling
- **Hamiltonian MC**: efficient exploration using gradient information (PyMC/Stan)

### Bayesian Prediction

$$p(y_{new}|x_{new}, \text{data}) = \int p(y_{new}|x_{new}, \theta) p(\theta|\text{data}) d\theta$$

Not just a point prediction, but a **complete predictive distribution**!

**This is the mathematical foundation of probabilistic forecasting in Yang Ch11.**

---

## Part 6: PCA and GLM (18.650 Lec 9–10)

### Statistical Perspective on PCA

- PCA in 18.06 = geometric view via SVD
- PCA in 18.650 = **eigendecomposition of the sample covariance matrix**

$$\hat{\Sigma} = \frac{1}{n-1}X^TX, \quad \hat{\Sigma}\mathbf{v}_k = \lambda_k\mathbf{v}_k$$

Selecting the top $k$ eigenvectors retains $\frac{\sum_{i=1}^k \lambda_i}{\sum_{i=1}^p \lambda_i}$ of the total variance.

### Generalized Linear Models (GLM)

$$g(E[Y]) = \mathbf{x}^T\boldsymbol{\beta}$$

- **Linear regression**: $g$ = identity function, $Y$ normal
- **Logistic regression**: $g$ = logit, $Y$ binary
- **Poisson regression**: $g$ = log, $Y$ count

**Implications for solar PV**:
- Weather type classification (sunny/partly cloudy/overcast) → multinomial logistic regression
- Equipment failure counts → Poisson regression
- Power output truncated at capacity → Tobit model (censored regression)

---

## Grand Unification: The Knowledge Network of Probability & Statistics and the Three Textbooks

### Box Time Series

| Statistical Concept | Application in Box |
|---------------------|-------------------|
| MLE | Ch7 parameter estimation |
| Fisher information | Parameter standard errors |
| Likelihood ratio test | Ch8 model diagnostics |
| AIC/BIC | Ch6 model selection |
| Normality assumption | White noise $a_t \sim N(0, \sigma_a^2)$ |
| Conditional expectation | Ch5 optimal forecasting |

### Warner NWP

| Statistical Concept | Application in Warner |
|---------------------|-----------------------|
| Bayesian inference | Ch12 data assimilation (prior = background field, likelihood = observations, posterior = analysis field) |
| Covariance matrix | Background error covariance $B$ + observation error covariance $R$ |
| PCA (EOF) | Principal mode analysis of meteorological fields |
| Ensemble statistics | Ch14 ensemble forecast mean/spread |

### Yang Solar

| Statistical Concept | Application in Yang |
|---------------------|---------------------|
| Probabilistic forecasting | Ch11 forecast intervals, reliability diagrams |
| Regression | Ch7 MOS post-processing |
| Cross-validation | Ch9 forecast verification |
| Quantile regression | Quantiles for probabilistic forecasting |

---

## Action Guide for the Solar PV Forecasting Project

1. **MLE is the default**: MLE is the first choice for model parameter estimation — simple and effective
2. **Bayesian inference for uncertainty quantification**: the posterior distribution directly yields prediction intervals
3. **AIC/BIC for model selection**: applies not only to ARIMA $p,d,q$ but also to hyperparameters of ML models
4. **Ljung-Box is mandatory**: test residuals for white noise for every model
5. **PCA for dimensionality reduction**: apply PCA when the meteorological feature matrix has a large condition number
6. **GLM framework**: choose a different link function for different forecasting objectives
7. **Cross-validation**: use rolling-window CV for time series — not random splits

---

*📖 [MIT Course Series](/blog/) | [18.06 Linear Algebra](/blog/2026-03-16-mit-1806-part1-foundations) | [Matrix Calculus](/blog/2026-03-16-mit-matrixcalc-deep-dive) | 🧠 MIT Probability & Statistics Complete*
