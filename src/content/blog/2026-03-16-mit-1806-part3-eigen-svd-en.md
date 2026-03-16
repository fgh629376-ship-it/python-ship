---
title: "MIT 18.06 Linear Algebra Part 3: Eigenvalues, SVD, and Data Science"
description: "A close reading of MIT 18.06 Lectures 15-27: determinants, eigenvalue decomposition, spectral theorem, SVD, low-rank approximation, image compression — the bridge from pure mathematics to solar forecasting"
pubDate: 2026-03-16
lang: en
series: mit-courses
category: algorithm
tags: ["Linear Algebra", "MIT", "Eigenvalues", "SVD", "PCA", "Low-Rank Approximation", "Textbook Notes"]
---

# MIT 18.06 Linear Algebra Part 3: Eigenvalues, SVD, and Data Science

> **Course**: MIT 18.06 Linear Algebra, Spring 2025
> **Scope**: Lecture 15-27 (Determinants, Eigenvalues, SVD, Low-Rank Approximation)

## Lec 15-19: Determinants

### Determinant = Signed Scaling Factor of Volume

$$\det A = \text{the signed scaling factor applied by the linear transformation } A \text{ to } n\text{-dimensional volume}$$

**Key properties**:
- Product formula: $\det(AB) = (\det A)(\det B)$
- $\det A \neq 0 \Leftrightarrow A$ is invertible
- Upper triangular matrix: $\det =$ product of diagonal entries

### The Big Formula (Lec 16)

$$\det A = \sum_{\sigma} (\text{sgn}\,\sigma) \prod_{i=1}^n a_{i,\sigma(i)}$$

Summing over all $n!$ permutations — theoretically beautiful, but Gaussian elimination is far more efficient for computation.

### Laplace Expansion and the Adjugate (Lec 17, 19)

Cofactor $C_{ij} = (-1)^{i+j}\det M_{ij}$ (where $M_{ij}$ is the submatrix with row $i$ and column $j$ removed)

$$A^{-1} = \frac{1}{\det A}C^T$$

**Cramer's Rule**: $x_j = \frac{\det A_j}{\det A}$ (where $A_j$ is $A$ with its $j$-th column replaced by $\mathbf{b}$)

**Practical value**: Determinants are elegant in theoretical derivations (characteristic equation $\det(A - \lambda I) = 0$), but are almost never used directly in large-scale numerical computation.

---

## Lec 20-22: Eigenvalues and Diagonalization

### The Eigenvalue Problem

$$A\mathbf{v} = \lambda\mathbf{v}, \quad \mathbf{v} \neq \mathbf{0}$$

The matrix $A$ only scales in an eigendirection (by $\lambda$) — it does not change the direction.

### The Characteristic Polynomial

$$p_A(\lambda) = \det(A - \lambda I) = (-1)^n\lambda^n + (-1)^{n-1}\alpha\lambda^{n-1} + \cdots + \det A$$

where $\alpha = \text{tr}(A)$. The $n$ roots (including complex and repeated roots) give the $n$ eigenvalues.

### Diagonalization

$$A = EDE^{-1}$$

Columns of $E$ = eigenvectors; diagonal of $D$ = eigenvalues.

**Condition for diagonalization**: if and only if the geometric multiplicity of every eigenvalue equals its algebraic multiplicity.

- All eigenvalues distinct → always diagonalizable
- Repeated roots → not necessarily (e.g., Jordan blocks)

### Deep Connection to Box ARIMA

The AR(p) characteristic equation $\phi(B) = 0$ in Box Ch3 is essentially computing eigenvalues of the $\phi$ operator:

- Roots outside the unit circle → $|\lambda| < 1$ → stationary (decaying)
- Roots on the unit circle → $|\lambda| = 1$ → non-stationary ($d$ unit roots in ARIMA)
- Roots inside the unit circle → $|\lambda| > 1$ → explosive

Complex eigenvalues of AR(2) produce **quasi-periodic behavior** (damped sinusoids) — sunspot data is the classic AR(2) example.

The acoustic/gravity wave analysis in Warner NWP Ch5 is also an eigenvalue problem: the eigenvalues of the linearized atmospheric equation system determine wave propagation speed and stability.

---

## Lec 23: Complex Eigenvalues and the Spectral Theorem

### Complex Eigenvalues of Real Matrices Appear in Conjugate Pairs

If $\lambda = a + bi$ is an eigenvalue, then $\bar{\lambda} = a - bi$ is also one.

### Spectral Theorem (Symmetric Matrices)

> **If $A$ is a real symmetric matrix ($A = A^T$), then:**
> 1. All eigenvalues are **real**
> 2. Eigenvectors form an **orthonormal basis**
> 3. $A = E D E^T$ ($E$ is orthogonal)

**This is one of the most beautiful theorems in linear algebra.** The eigendecomposition of a symmetric matrix = rotation + scaling + reverse rotation.

**Application in solar forecasting**: The covariance matrix $\Sigma = \frac{1}{n}X^TX$ is always symmetric positive semidefinite → it always has an orthogonal eigendecomposition → this is the mathematical foundation of PCA.

---

## Lec 24: Positive Definite Matrices and Introduction to SVD

### Positive Definiteness

A symmetric matrix $A$ is **positive definite (PD)** $\Leftrightarrow$ all eigenvalues $> 0$ $\Leftrightarrow$ $\mathbf{x}^T A\mathbf{x} > 0, \forall \mathbf{x} \neq 0$

**Positive semidefinite (PSD)**: all eigenvalues $\geq 0$

Key fact: **For any matrix $M$, both $M^TM$ and $MM^T$ are positive semidefinite.**

### SVD: Singular Value Decomposition

For any $n \times p$ matrix $M$ (no requirement to be square!):

$$M = U\Sigma V^T$$

- $U$: $n \times r$, left singular vectors (orthonormal basis for the column space of $M$)
- $\Sigma$: $r \times r$, diagonal matrix of singular values ($\sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_r > 0$)
- $V$: $p \times r$, right singular vectors (orthonormal basis for the row space of $M$)

**SVD simultaneously reveals orthonormal bases for all four fundamental subspaces!**

---

## Lec 25-26: Computing SVD and Geometric Interpretation

### Computation Steps

1. Eigendecomposition of $A = M^TM$: $A = EDE^T$
2. $V$ = first $r$ columns of $E$ (eigenvectors corresponding to $d_i > 0$)
3. $\sigma_i = \sqrt{d_i}$
4. $U = MV\Sigma^{-1}$

### Geometric Meaning

- **Operator norm** $\|M\|_{op} = \sigma_1$: maximum factor by which $M$ can stretch the unit ball
- **Pseudoinverse via SVD**: $M^+ = V\Sigma^{-1}U^T$
- **Condition number** $\kappa = \sigma_1/\sigma_r$: larger means more ill-conditioned

---

## Lec 27: Low-Rank Approximation and Image Compression

### The Eckart-Young Theorem

$$M_k = U_k\Sigma_k V_k^T = \text{best rank-}k\text{ approximation}$$

Optimal under the spectral norm, Frobenius norm, and nuclear norm.

### Image Compression

Original image $M$: $n \times p$ pixels (stores $np$ values)
Compressed $M_k$: stores $(n + p)k + k$ values

When $k \ll \min(n,p)$, the **compression ratio is enormous**.

### Implications for Solar Forecasting

**Multi-site power data matrix** ($m$ time steps × $n$ stations):

If rank $r \ll n$ (because neighboring stations are highly correlated), then:
- Low-rank approximation $M_k$ denoises the data
- Columns of $U_k$ = "typical power patterns" (clear-sky, partly cloudy, overcast, etc.)
- Columns of $V_k$ = "spatial patterns" (which stations behave similarly)
- $\Sigma_k$ = "energy" of each pattern

Yang Ch12's hierarchical forecasting essentially exploits the low-rank structure of the multi-site power matrix.

**Dimensionality reduction of meteorological features**:
- Raw features: temperature, humidity, pressure, wind speed, wind direction, cloud cover, irradiance… ($p$ dimensions)
- SVD/PCA reduces to $k$ dimensions → removes redundancy → reduces overfitting

---

## Deep Connection: SVD Unifies Everything

SVD is the "ultimate weapon" of linear algebra — almost every important concept can be understood through SVD:

- **Four fundamental subspaces**: columns of $U$ = basis of $C(M)$, columns of $V$ = basis of $C(M^T)$
- **Rank**: number of $\sigma_i > 0$
- **Least squares**: $\hat{\mathbf{x}} = M^+\mathbf{b} = V\Sigma^{-1}U^T\mathbf{b}$
- **PCA**: right singular vectors of data matrix = principal component directions
- **Low-rank approximation**: Eckart-Young → data compression/denoising
- **Condition number**: $\sigma_1/\sigma_r$ → numerical stability diagnosis
- **Regularization**: Tikhonov regularization = truncating small singular values

### SVD in Three Textbooks

| Textbook | Role of SVD |
|----------|-------------|
| **Box** | Eigendecomposition of residual covariance matrix → principal component residual analysis |
| **Warner** | EOF (Empirical Orthogonal Functions) = PCA of meteorological fields = SVD applied to climate data matrices |
| **Yang** | Extraction of spatial patterns for multi-site forecasting |

---

## Module Summary

Lectures 15-27 trace the path from determinants → eigenvalues → SVD, progressively revealing the internal structure of matrices.

**Core conceptual chain**:

$$\underbrace{\det(A-\lambda I) = 0}_{\text{characteristic equation}} \to \underbrace{A = EDE^{-1}}_{\text{diagonalization}} \to \underbrace{A = EDE^T}_{\text{spectral theorem (symmetric)}} \to \underbrace{M = U\Sigma V^T}_{\text{SVD (any matrix)}}$$

Each step generalizes the previous. SVD is the final form — applicable to any matrix while simultaneously providing the best approximation.

**Preview of next post**: Lec 28-36 moves into PCA, DFT, and circulant matrices — the mathematical core of signal processing and time series analysis.

---

*📖 [MIT Course Series](/blog/) | [Part 2: Projection and Least Squares](/blog/2026-03-16-mit-1806-part2-projection-leastsquares) | 🧠 MIT 18.06 Spring 2025*
