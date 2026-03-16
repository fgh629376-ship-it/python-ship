---
title: "MIT 18.06 Linear Algebra Part 2: Projection, Least Squares, and QR Decomposition"
description: "A close reading of MIT 18.06 Lectures 8-14: the complete picture of the four fundamental subspaces, orthogonal projection formulas, least squares, Gram-Schmidt and QR, and the pseudoinverse"
pubDate: 2026-03-16
lang: en
series: mit-courses
category: algorithm
tags: ["Linear Algebra", "MIT", "Least Squares", "QR Decomposition", "Projection", "Pseudoinverse", "Textbook Notes"]
---

# MIT 18.06 Linear Algebra Part 2: Projection, Least Squares, and QR Decomposition

> **Course**: MIT 18.06 Linear Algebra, Spring 2025
> **Scope**: Lecture 8-14 (Four Fundamental Subspaces, Projection, Least Squares, QR, Pseudoinverse)

## Lec 8-9: The Four Fundamental Subspaces — The Complete Picture of Linear Algebra

### The Four Fundamental Subspaces of a Matrix

For an $m \times n$ matrix $A$, using the RREF $R = GA$:

- **Column space** $C(A) = G^{-1}C(R)$, $\subseteq \mathbb{R}^m$, dimension $r$
- **Null space** $N(A) = N(R)$, $\subseteq \mathbb{R}^n$, dimension $n - r$
- **Row space** $C(A^T) = C(R^T)$, $\subseteq \mathbb{R}^n$, dimension $r$
- **Left null space** $N(A^T) = G^T N(R^T)$, $\subseteq \mathbb{R}^m$, dimension $m - r$

### Orthogonal Complement Relationships

$$\mathbb{R}^n = C(A^T) \oplus N(A), \quad \mathbb{R}^m = C(A) \oplus N(A^T)$$

The row space and null space are orthogonal complements in $\mathbb{R}^n$; the column space and left null space are orthogonal complements in $\mathbb{R}^m$.

**This is the deepest structural theorem of linear algebra.** It tells us:
- For $A\mathbf{x} = \mathbf{b}$, $\mathbf{b}$ can be uniquely decomposed into a column-space component + a left-null-space component
- The column-space component is "what $A$ can explain," and the left-null-space component is the "residual"

**The four subspaces in solar forecasting**:

Let $A$ be the meteorological feature matrix ($m$ time steps × $n$ features):
- $C(A)$: the space of power variations that feature combinations can explain
- $N(A^T)$: power variations that features cannot explain ("pure noise" direction)
- $C(A^T)$: effective feature directions
- $N(A)$: redundant feature combinations (multicollinearity!)

When the dimension of $N(A)$ is large, features are highly collinear — regularization or dimensionality reduction (PCA/Ridge) is needed.

---

## Lec 10-11: Orthogonal Projection

### Geometric Meaning of Projection

$$\mathbf{v} = \text{proj}_V(\mathbf{x}) = \text{the point in } V \text{ closest to } \mathbf{x}$$

Equivalent condition: $(\mathbf{x} - \mathbf{v}) \perp V$

### Projection Matrix Formula

Let $V = C(A)$, where $A$ is $n \times r$ with $\text{rank}(A) = r$:

$$P_V = A(A^T A)^{-1}A^T$$

**Properties**:
- $P_V^2 = P_V$ (idempotent: projecting twice = projecting once)
- $P_V^T = P_V$ (symmetric)
- $\text{rank}(P_V) = r$ (column space = $V$)

### Why Is $A^T A$ Invertible?

When $A$ has full column rank, $A^T A$ is an $r \times r$ positive definite matrix. Intuition: the null space of $A^T A$ = the null space of $A$ = $\{\mathbf{0}\}$.

**Connection to Box**: The normal equations in Box Ch7, $A^T A \hat{\boldsymbol{\phi}} = A^T \mathbf{z}$, are doing exactly orthogonal projection — projecting data $\mathbf{z}$ onto the column space of the design matrix. The $\mathbf{P}_p$ in the Yule-Walker equations $\mathbf{P}_p \boldsymbol{\phi} = \boldsymbol{\rho}_p$ is precisely $A^T A$ with Toeplitz structure.

---

## Lec 12: Least Squares

### Core Formula

$$\hat{\mathbf{x}} = (A^T A)^{-1} A^T \mathbf{b}$$

Minimizes $\|A\mathbf{x} - \mathbf{b}\|^2 = \sum_i [(A\mathbf{x})_i - b_i]^2$.

### Practical Applications

**Line fit through origin**: $b = xa$
- Design matrix $A = \mathbf{a}$ (single column), $\hat{x} = \frac{\mathbf{a}^T \mathbf{b}}{\mathbf{a}^T \mathbf{a}}$

**Line fit with intercept**: $b = x_0 + x_1 a$
- Design matrix $A = [\mathbf{1} | \mathbf{a}]$ (two columns)

**Polynomial fit**: $b = x_0 + x_1 a + x_2 a^2 + x_3 a^3$
- Design matrix $A = [\mathbf{1} | \mathbf{a} | \mathbf{a}^2 | \mathbf{a}^3]$ (Vandermonde matrix)

**Least squares in solar forecasting**:
- Temperature model parameter fitting: $T_{cell} = T_{amb} + \alpha \cdot GHI + \beta \cdot WS + \gamma$
- Conditional MLE in Box Ch7 = conditional least squares
- MOS (Model Output Statistics) post-processing in Yang Ch7 = multiple linear regression

### ⚠️ Least Squares vs. PCA

**Least squares** minimizes **vertical distance** (residuals in the $y$ direction): suitable for $y = f(x)$ regression

**PCA** minimizes **orthogonal distance** (shortest distance to the subspace): suitable for data compression/dimensionality reduction

The textbook calls PCA "perpendicular least squares" — the two are not the same!

---

## Lec 13: Gram-Schmidt and QR Decomposition

### Gram-Schmidt Orthogonalization

Input: basis $(v_1, \ldots, v_r)$
Output: orthonormal basis $(u_1, \ldots, u_r)$

$$u_k = \frac{v_k - \sum_{j=1}^{k-1}(v_k \cdot u_j)u_j}{\|v_k - \sum_{j=1}^{k-1}(v_k \cdot u_j)u_j\|}$$

### QR Decomposition

$$A = QR$$

- $Q$: $n \times r$, orthonormal columns
- $R$: $r \times r$, upper triangular

**Numerical advantages of QR**:
- Using the normal equations $(A^T A)\hat{\mathbf{x}} = A^T\mathbf{b}$ directly is numerically unstable (condition number is squared)
- With QR: $\hat{\mathbf{x}} = R^{-1}Q^T\mathbf{b}$, condition number unchanged

**Practical note**: NumPy's `np.linalg.lstsq()` uses QR decomposition internally, not the normal equations.

---

## Lec 14: The Pseudoinverse

### Minimum-Norm Solution

When $A$ is $r \times n$ ($r < n$, underdetermined system): infinitely many solutions exist. The **minimum-norm solution** = the row-space component $\mathbf{x}^\perp$.

### Matrix Pseudoinverse $A^+$

For an arbitrary $m \times n$ matrix $A$:
1. Project $\mathbf{y}$ onto $C(A)$ to get $\mathbf{b}$
2. Solve $A\mathbf{x} = \mathbf{b}$ for the minimum-norm solution

$$A^+ : \mathbb{R}^m \to \mathbb{R}^n$$

**Two special cases**:
- $A$ has full column rank ($m \geq n = r$): $A^+ = (A^T A)^{-1} A^T$ (left inverse, least squares)
- $A$ has full row rank ($n \geq m = r$): $A^+ = A^T(AA^T)^{-1}$ (right inverse, minimum norm)

**Computed via SVD** (Lec 26): $A = U\Sigma V^T \Rightarrow A^+ = V\Sigma^{-1}U^T$

**Pseudoinverse in solar forecasting**:
- When meteorological features outnumber observations ($n > m$), direct least squares has no unique solution → pseudoinverse gives the minimum-norm solution
- Equivalent to the limit of Ridge regression as $\lambda \to 0$
- In NWP data assimilation, the observation operator $H$ is typically a "wide matrix" (fewer observations than state variables), requiring the pseudoinverse

---

## Deep Dive: A Unified View of Least Squares

All of the following problems share the same mathematical essence — finding the point in the column space closest to $\mathbf{b}$:

- **Linear Regression**: equation $A\mathbf{x} = \mathbf{b}$ — $A$ is the design matrix (features), $\mathbf{b}$ is the response variable
- **Box ARIMA**: equation $\Phi\hat{\boldsymbol{\phi}} = \boldsymbol{\rho}$ — $\Phi$ is the Toeplitz ACF matrix, $\boldsymbol{\rho}$ is the ACF vector
- **NWP Assimilation**: equation $H\mathbf{x} = \mathbf{y}_{obs}$ — $H$ is the observation operator, $\mathbf{y}_{obs}$ is the observed values
- **pvlib Temperature**: equation $A\boldsymbol{\beta} = T_{cell}$ — $A$ is the meteorological feature matrix, $T_{cell}$ is the cell temperature
- **Image Compression**: approximation $\approx U_k\Sigma_k V_k^T$ — via left singular vectors

---

## Module Summary

Lectures 8-14 are the heart of 18.06 — projection and least squares are the geometric foundation for understanding all regression methods.

**Core formula chain**:
1. Orthogonal complements of the four fundamental subspaces → any vector decomposes uniquely
2. Orthogonal projection $P = A(A^TA)^{-1}A^T$ → best approximation
3. Least squares $\hat{\mathbf{x}} = (A^TA)^{-1}A^T\mathbf{b}$ → parameter estimation
4. QR decomposition → numerically stable implementation
5. Pseudoinverse → unified handling of overdetermined/underdetermined systems

**Preview of next post**: Lec 15-19 determinants + Lec 20-23 eigenvalues — the mathematical foundation for the ARIMA characteristic equation.

---

*📖 [MIT Course Series](/blog/tags/MIT) | [Part 1: Vector Spaces](/blog/2026-03-16-mit-1806-part1-foundations) | 🧠 MIT 18.06 Spring 2025*
