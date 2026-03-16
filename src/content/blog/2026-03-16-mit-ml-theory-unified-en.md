---
title: "MIT ML Theory Unified: Mathematical Foundations from Empirical Risk Minimization to Kernel Methods, Ensemble Learning, and Deep Learning"
description: "Integrating MIT 6.867 Machine Learning + Boyd Convex Optimization + 18.065 Matrix Methods: a single logical thread running through all core supervised learning theory, mapped to every stage of solar power forecasting"
pubDate: 2026-03-16
lang: en
series: mit-courses
category: algorithm
tags: ["Machine Learning", "MIT", "SVM", "Kernel Methods", "Ensemble Learning", "Convex Optimization", "Deep Learning", "Textbook Notes"]
---

# MIT ML Theory Unified: One Logical Thread Through All Supervised Learning

> **Course Sources**: MIT 6.867 Machine Learning (Tommi Jaakkola) + Boyd *Convex Optimization* + MIT 18.065 Matrix Methods (Strang)
> **Core Claim**: All supervised learning methods are special cases of the same framework — **Empirical Risk Minimization + Regularization**

## 0. The Big Picture: ML's Unified Framework

$$\hat{f} = \arg\min_{f \in \mathcal{F}} \underbrace{\frac{1}{n}\sum_{i=1}^n L(y_i, f(x_i))}_{\text{Empirical Risk}} + \underbrace{\lambda \Omega(f)}_{\text{Regularization}}$$

**Three choices determine everything**:
1. **Loss function** $L$: measures the gap between predictions and ground truth
2. **Hypothesis space** $\mathcal{F}$: what the model can express
3. **Regularization** $\Omega(f)$: controls model complexity

Different combinations produce different algorithms, but **the mathematical essence is identical**.

---

## 1. From Least Squares to Regularized Regression

### 1.1 Linear Regression = The Simplest ERM

$$\hat{\boldsymbol{\beta}} = \arg\min_{\boldsymbol{\beta}} \frac{1}{n}\|\mathbf{y} - X\boldsymbol{\beta}\|^2$$

Solution: $\hat{\boldsymbol{\beta}} = (X^TX)^{-1}X^T\mathbf{y}$ (the projection formula from 18.06 Part 2)

**Problem**: When $p > n$ (more features than samples) or features are highly collinear, $X^TX$ is ill-conditioned → variance of $\hat{\boldsymbol{\beta}}$ explodes.

### 1.2 Ridge Regression = $L_2$ Regularization

$$\hat{\boldsymbol{\beta}}_{ridge} = \arg\min_{\boldsymbol{\beta}} \frac{1}{n}\|\mathbf{y} - X\boldsymbol{\beta}\|^2 + \lambda\|\boldsymbol{\beta}\|^2$$

Solution: $\hat{\boldsymbol{\beta}}_{ridge} = (X^TX + \lambda I)^{-1}X^T\mathbf{y}$

**SVD perspective** (18.06 Part 3): Let $X = U\Sigma V^T$, then

$$\hat{\boldsymbol{\beta}}_{ridge} = \sum_{j=1}^r \frac{\sigma_j^2}{\sigma_j^2 + \lambda} \frac{\mathbf{u}_j^T\mathbf{y}}{\sigma_j}\mathbf{v}_j$$

**Role of $\lambda$**: shrinks coefficients along small singular value directions. $\lambda \to 0$ reduces to OLS; $\lambda \to \infty$ drives all coefficients to 0.

**Bayesian interpretation** (probability & statistics): Ridge = MAP estimate under Gaussian prior $\boldsymbol{\beta} \sim N(0, \frac{1}{\lambda}I)$.

### 1.3 Lasso = $L_1$ Regularization

$$\hat{\boldsymbol{\beta}}_{lasso} = \arg\min_{\boldsymbol{\beta}} \frac{1}{n}\|\mathbf{y} - X\boldsymbol{\beta}\|^2 + \lambda\|\boldsymbol{\beta}\|_1$$

**The magic of $L_1$**: produces **sparse solutions** — many $\beta_j$ are exactly zero → **automatic feature selection**.

**Geometric interpretation**: The $L_1$ constraint set is a "diamond"; contour lines tend to touch at corners → coordinates at corners are zero.

**Bayesian interpretation**: Lasso = MAP under Laplace prior.

### 1.4 Elastic Net = $L_1 + L_2$

$$\lambda_1\|\boldsymbol{\beta}\|_1 + \lambda_2\|\boldsymbol{\beta}\|^2$$

Gets both sparsity ($L_1$) and stability ($L_2$).

### 🔗 Connection to Solar Power Forecasting

- **Meteorological features are highly correlated** (temperature ↔ irradiance ↔ pressure) → Ridge for stable estimation
- **Many features but only a few truly matter** (among dozens of NWP variables, perhaps only 5–6 are genuinely useful) → Lasso for automatic selection
- **Box Ch7's ridge-shaped likelihood surface** (when $\phi \approx \theta$) → regularization resolves parameter non-identifiability

---

## 2. The Bias–Variance Tradeoff — The Core Tension in ML

### 2.1 Decomposition Theorem

For any estimator $\hat{f}$:

$$E\left[(y - \hat{f}(x))^2\right] = \underbrace{\text{Bias}^2[\hat{f}(x)]}_{\text{Underfitting}} + \underbrace{\text{Var}[\hat{f}(x)]}_{\text{Overfitting}} + \underbrace{\sigma^2}_{\text{Irreducible Noise}}$$

**Simple model**: high bias, low variance (underfitting)
**Complex model**: low bias, high variance (overfitting)

### 2.2 Model Selection

**Cross-validation**: split data into training/validation sets; choose the model with the smallest validation error

**Information criteria**:
- AIC = $-2\ell + 2k$ (used in Box Ch6)
- BIC = $-2\ell + k\ln n$ (stronger penalty)

**⚠️ Time-series CV must use a rolling window** — random splits are invalid due to temporal dependence!

### 2.3 VC Dimension and Generalization Bounds

**VC dimension**: the maximum number of samples the hypothesis space $\mathcal{F}$ can "shatter".

$$R(f) \leq \hat{R}_n(f) + O\left(\sqrt{\frac{d_{VC}}{n}}\right)$$

True risk $\leq$ empirical risk + complexity penalty.

**Implication**: the more complex the model (larger $d_{VC}$), the more data is needed to generalize.

**Intuitive correspondences**:
- Linear model: $d_{VC} = p + 1$
- Box ARIMA(p,d,q): effective parameters = $p + q$ (Box recommends $p, q \leq 2$ — parsimony!)
- Deep learning: $d_{VC}$ is enormous, but in practice there is **implicit regularization** (SGD itself favors simpler solutions)

---

## 3. Kernel Methods — Linear Regression in High-Dimensional Space

### 3.1 Limitations of Feature Mapping

Nonlinear problems → manually construct features $\phi(x) = [x, x^2, x^3, \ldots]$ → dimensionality explosion.

### 3.2 The Kernel Trick

**Key insight**: many algorithms only require the **inner product** between samples $\langle \phi(x_i), \phi(x_j) \rangle$ — explicit computation of $\phi(x)$ is unnecessary.

**Kernel function**: $K(x_i, x_j) = \langle \phi(x_i), \phi(x_j) \rangle$

**Common kernels**:
- **Linear kernel**: $K(x, z) = x^Tz$ (ordinary linear regression)
- **Polynomial kernel**: $K(x, z) = (x^Tz + c)^d$ (equivalent to degree-$d$ polynomial features)
- **Gaussian / RBF kernel**: $K(x, z) = \exp(-\|x - z\|^2 / 2\sigma^2)$ (equivalent to an **infinite-dimensional** feature space!)

### 3.3 Kernel Ridge Regression

$$\hat{f}(x) = \sum_{i=1}^n \alpha_i K(x_i, x)$$

where $\boldsymbol{\alpha} = (K + \lambda I)^{-1}\mathbf{y}$ and $K_{ij} = K(x_i, x_j)$ is the kernel matrix.

**Note**: $K$ is $n \times n$ rather than $p \times p$ → more efficient when $n < p$ (fewer samples than features).

### 3.4 The Representer Theorem

> **In kernel methods, the optimal solution can always be written as a linear combination of training samples.**

$$f^*(x) = \sum_{i=1}^n \alpha_i K(x_i, x)$$

This is a profoundly deep result — **an infinite-dimensional optimization problem has a finite-dimensional solution**.

### 🔗 Connection to Solar Power Forecasting

- The irradiance-to-power relationship is nonlinear (temperature effects, inverter clipping, etc.)
- The $\sigma$ of the RBF kernel = the "scale" of nonlinearity
- **Gaussian Process Regression (GP)** = the Bayesian version of kernel methods → automatically provides prediction uncertainty → Yang Ch11

---

## 4. SVM — Maximum Margin Classifier

### 4.1 Hard-Margin SVM

$$\max_{\mathbf{w}, b} \frac{2}{\|\mathbf{w}\|} \quad \text{s.t.} \quad y_i(\mathbf{w}^T\mathbf{x}_i + b) \geq 1$$

Equivalent convex optimization: $\min \frac{1}{2}\|\mathbf{w}\|^2$ s.t. $y_i(\mathbf{w}^T\mathbf{x}_i + b) \geq 1$

### 4.2 Soft-Margin SVM + Hinge Loss

$$\min_{\mathbf{w}, b} \frac{1}{2}\|\mathbf{w}\|^2 + C\sum_{i=1}^n \max(0, 1 - y_i(\mathbf{w}^T\mathbf{x}_i + b))$$

This is exactly ERM + regularization! $L$ = hinge loss, $\Omega = \|\mathbf{w}\|^2$.

### 4.3 The Dual Problem (Boyd Convex Optimization)

Via Lagrange duality:

$$\max_{\boldsymbol{\alpha}} \sum_i \alpha_i - \frac{1}{2}\sum_{i,j}\alpha_i\alpha_j y_i y_j K(x_i, x_j)$$

**Only involves kernel functions** → SVM can be performed in arbitrarily high-dimensional spaces!

### 4.4 Physical Meaning of KKT Conditions

- $\alpha_i = 0$: sample is far from the decision boundary (does not affect the model)
- $0 < \alpha_i < C$: **support vector** — exactly on the margin boundary
- $\alpha_i = C$: sample that violates the margin constraint

**Sparsity**: most $\alpha_i = 0$ → SVM predictions depend only on a few support vectors → **efficient**

### 🔗 Convex Optimization is Everywhere in ML

Core concepts from Boyd's convex optimization and their roles in ML:
- **Convex functions**: MSE, cross-entropy, hinge are all convex → local optimum = global optimum
- **Duality**: SVM's dual problem; kernel methods
- **KKT conditions**: mathematical definition of support vectors; subgradient conditions for Lasso
- **Proximal operators**: efficient solving of $L_1$ regularization (ISTA/FISTA)

---

## 5. Ensemble Learning — The Power of Weak Learners

### 5.1 Bagging (Bootstrap Aggregating)

$$\hat{f}_{bag}(x) = \frac{1}{B}\sum_{b=1}^B \hat{f}_b(x)$$

Each $\hat{f}_b$ is trained on a bootstrap sample. **Reduces variance**, does not change bias.

**Random Forest** = Bagging + random feature selection → further decorrelation

### 5.2 Boosting — An Optimization Perspective

$$\hat{f}_m(x) = \hat{f}_{m-1}(x) + \gamma_m h_m(x)$$

Each step fits the **residuals of the previous step**.

**Gradient Boosting** = gradient descent in function space:
- $h_m = \arg\min_h \sum_i L'(y_i, \hat{f}_{m-1}(x_i)) \cdot h(x_i)$
- The new weak learner fits the **negative gradient** of the loss function

**XGBoost/LightGBM** = Gradient Boosting + second-order approximation (Newton) + regularization + efficient engineering

### 5.3 Ensemble View of Bias–Variance

- **Bagging**: averaging $n$ correlated predictors → variance reduced to $\frac{1+(n-1)\rho}{n} \cdot \sigma^2$
- **Boosting**: progressively reduces bias (each step corrects residuals) → but variance may increase

### 🔗 Connection to Time-Series Forecasting

- **Box's iterative methodology** (identification → estimation → diagnostics → revision) is spiritually identical to Boosting — each step corrects the shortcomings of the previous
- **NWP ensemble forecasting** (Warner Ch14) = the physical version of Bagging — multiple initial conditions → multiple forecasts → average
- **Yang Ch12 hierarchical forecasting** = multi-model fusion → Stacking (another form of ensemble)

---

## 6. Deep Learning — The Non-Convex New World

### 6.1 Universal Approximation Theorem

A single-hidden-layer network can approximate any continuous function to arbitrary precision. But this does **not** mean:
- Learning is easy (optimization problem is non-convex)
- Sample-efficient (may require exponentially wide networks)
- Generalizes well (VC dimension is enormous)

### 6.2 The Power of Depth

Deep > wide: some functions can be expressed by $O(n)$-deep networks, but require $O(2^n)$-wide single-layer networks.

**Intuition**: deep networks perform **hierarchical feature extraction** — lower layers learn edges, middle layers learn textures, upper layers learn semantics.

### 6.3 Optimization: Why Does SGD Work in Non-Convex Settings?

Classical optimization theory says non-convex problems have exponentially many local optima and saddle points. But in practice SGD performs well, because:

1. **Over-parameterization**: parameters >> data → almost all local optima are near the global optimum
2. **Implicit regularization of SGD**: noise helps escape saddle points and sharp minima
3. **Loss landscape geometry**: in high-dimensional spaces, saddle points vastly outnumber local optima

### 6.4 Backpropagation = Reverse-Mode Matrix Calculus

The core content of MIT 18.063:

$$\frac{\partial L}{\partial W^{(l)}} = \frac{\partial L}{\partial \mathbf{a}^{(L)}} \cdot \prod_{k=L}^{l+1} \frac{\partial \mathbf{a}^{(k)}}{\partial \mathbf{a}^{(k-1)}} \cdot \frac{\partial \mathbf{a}^{(l)}}{\partial W^{(l)}}$$

Backpropagation flows from output to input, using **reverse-mode chain rule** to efficiently compute gradients for all parameters.

### 6.5 Regularization Techniques

- **Dropout**: randomly drops neurons → approximate Bagging
- **Weight decay**: $L_2$ regularization = Ridge
- **Early stopping**: stop when validation error begins to rise → implicit $L_2$ regularization
- **Batch Normalization**: stabilizes training + mild regularization

### 🔗 Deep Learning in Solar Power Forecasting

- **CNN**: sky images → short-term irradiance forecasting (cloud tracking)
- **LSTM/GRU**: time-series power forecasting (captures long-range dependencies)
- **Transformer**: multi-step power forecasting (attention mechanism → adaptive weighting of historical information)
- **PINN**: physical constraints + neural network → pvlib physics model embedded in NN loss function

---

## 7. Full Course Knowledge Map

```
          Loss function L + Regularization Ω + Hypothesis space F
                    ↓
          Empirical Risk Minimization (ERM)
         ╱          │          ╲
    Linear models  Kernel methods  Deep learning
    (Ridge/        (SVM/           (CNN/
     Lasso)         GP)             Transformer)
       │             │                  │
       ↓             ↓                  ↓
  Convex optimization  Dual problem   SGD + Backpropagation
  (Boyd)               (KKT)          (Matrix calculus)
       │             │                  │
       ↓             ↓                  ↓
  Closed-form /    Support vectors    Gradient descent
  Proximal ops     (sparse)           (non-convex but effective)
       ╲             │             ╱
        Bias–Variance Tradeoff + Cross-Validation
                    ↓
             Ensemble Learning (Boosting / Bagging)
                    ↓
          Solar Power Forecasting System
```

---

## 8. ML in the Three Textbooks

### Box Time Series ↔ ML

- ARIMA = **linear model** specialized to time series (autoregression = past values as predictors)
- AIC/BIC = information-theoretic expression of the bias–variance tradeoff
- Iterative three-step methodology = manual version of model selection
- Transfer function = single-hidden-layer network (linear transfer + nonlinear activation ≈ impulse response + noise)

### Warner NWP ↔ ML

- Data assimilation = **Bayesian optimization** (prior = background field, observations = data, posterior = analysis field)
- Ensemble forecasting = **Bagging** (perturbed initial conditions → multiple model runs → average)
- MOS post-processing = **linear regression** (NWP output → surface observation mapping)
- Parameterization schemes = **feature engineering** (physical processes → statistical approximations)

### Yang Solar ↔ ML

- Ch7 post-processing = **regression analysis** (MOS/EMOS/quantile regression)
- Ch11 probabilistic forecasting = **probabilistic ML** (BNN/GP/quantile regression/CRPS loss)
- Ch12 hierarchical forecasting = **multi-task learning + ensemble**
- Model Chain = **feature engineering pipeline** (GHI → POA → DC → AC)

---

## 9. Action Guide for the Solar Power Forecasting Project

### Technology Selection Roadmap

1. **Baseline model**: physical model (pvlib Model Chain) → residual analysis
2. **Statistical correction**: ARIMA/SARIMA to correct temporal structure in residuals (Box)
3. **ML enhancement**:
   - Gradient Boosting (XGBoost/LightGBM) for nonlinear feature-to-power mapping
   - Input features = NWP variables + pvlib physical outputs + temporal features
   - Use Lasso for feature selection → identify the most important NWP variables
4. **Deep learning**:
   - Transformer for multi-step forecasting (day-ahead)
   - CNN for sky image processing (nowcasting)
   - PINN embedding pvlib physical constraints
5. **Ensemble**:
   - Stacking: weighted combination of physical model + ARIMA + XGBoost + Transformer
   - Adaptive weights (varying with weather type)
6. **Probabilistic output**:
   - Quantile regression or GP for prediction intervals
   - GARCH for adaptive variance (Box Ch10 → volatility clustering → interval width varies with weather)

### Mathematical Foundations for Each Method

- **Linear regression**: 18.06 projection + probability & statistics MLE
- **Ridge/Lasso**: convex optimization + SVD regularization
- **SVM/GP**: kernel methods + duality theory
- **XGBoost**: gradient boosting + Newton second-order approximation
- **Transformer**: matrix calculus + attention = $\text{softmax}(QK^T/\sqrt{d})V$
- **PINN**: calculus of variations + automatic differentiation

**The mathematical foundations of Phase 1 (linear algebra / matrix calculus / probability & statistics) are the prerequisite for understanding all of the above. Phase 2 unifies them into a single framework.**

---

*📖 [MIT Course Series](/blog/) | [18.06 Linear Algebra](/blog/2026-03-16-mit-1806-part1-foundations) | [Matrix Calculus](/blog/2026-03-16-mit-matrixcalc-deep-dive) | [Probability & Statistics](/blog/2026-03-16-mit-probability-statistics) | 🧠 MIT ML Theory Unified*
