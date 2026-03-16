---
title: "MIT 18.06 Linear Algebra Part 4: PCA, Fourier Transform, and Circulant Matrices"
description: "A close reading of MIT 18.06 Lectures 28-36: PCA for data analysis, DFT for signal processing, circulant matrices and convolution — the ultimate applications of linear algebra to time series and solar forecasting"
pubDate: 2026-03-16
lang: en
series: mit-courses
category: algorithm
tags: ["Linear Algebra", "MIT", "PCA", "Fourier Transform", "DFT", "Circulant Matrices", "Textbook Notes"]
---

# MIT 18.06 Linear Algebra Part 4: PCA, Fourier Transform, and Circulant Matrices

> **Course**: MIT 18.06 Linear Algebra, Spring 2025
> **Scope**: Lecture 28-36 (PCA, Complex Spaces, DFT, Circulant Matrices)

## Lec 28: PCA — The First Tool of Data Science

### What Is PCA?

**Principal Component Analysis (PCA) = apply SVD to the data matrix and take the first $k$ right singular vectors as the new coordinate axes.**

Let $X$ be an $n \times p$ data matrix ($n$ samples, $p$ features, centered and standardized):

$$X = U\Sigma V^T$$

- **Principal component directions**: columns of $V$ (directions in $\mathbb{R}^p$)
- **Principal component scores**: columns of $U\Sigma$ (each sample's projection onto the principal components)
- **Variance explained**: $\sigma_i^2 / \sum \sigma_j^2$

### 2D PCA

Choose the 2D projection that captures maximum data variability: take the first two columns $\mathbf{u}, \mathbf{v}$ of $V$, and plot the scatter diagram $(\mathbf{x}_i \cdot \mathbf{u}, \mathbf{x}_i \cdot \mathbf{v})$.

### PCA ≠ Least Squares

- **Least squares**: minimizes the sum of squared residuals in the $y$ direction (perpendicular to the $x$-axis)
- **PCA**: minimizes the sum of squared **orthogonal distances** to the subspace ("perpendicular least squares")

**PCA in solar forecasting**:
- **Meteorological feature reduction**: temperature/humidity/pressure/wind speed are highly correlated → PCA reduces to 3-5 dimensions retaining 95% of variance
- **Multi-site power patterns**: PCA on the power matrix of $n$ stations → extract "clear-sky mode," "cloud-passage mode," "overcast mode"
- **NWP ensemble analysis**: EOF analysis in Warner Ch14 = PCA applied to the NWP ensemble forecast matrix

---

## Lec 29-30: Complex Vector Spaces

### From Real to Complex

- **Conjugate transpose** $\bar{A}^T$ (Hermitian transpose) replaces $A^T$
- **Inner product** $\langle \mathbf{v}, \mathbf{w} \rangle = \bar{\mathbf{v}}^T \mathbf{w}$ → ensures $\|\mathbf{v}\|^2 = \langle \mathbf{v}, \mathbf{v} \rangle \geq 0$

### Three Special Types of Complex Matrices

- **Unitary**: $U\bar{U}^T = I$ → length-preserving transformation (generalization of orthogonal matrices)
- **Hermitian**: $A = \bar{A}^T$ → all real eigenvalues (generalization of symmetric matrices)
- **Normal**: $A\bar{A}^T = \bar{A}^T A$ → has an orthogonal eigenbasis

### Generalized Spectral Theorem

Stated as bullet points to avoid LaTeX in table cells:

- **Real symmetric**: $A = EDE^T$, $E$ orthogonal, $D$ real diagonal
- **Hermitian**: $A = UDU^*$, $U$ unitary, $D$ real diagonal
- **Normal**: $A = UDU^*$, $U$ unitary, $D$ complex diagonal

---

## Lec 31-33: Circulant Matrices and the Fourier Basis

### Circulant Matrices

The cyclic permutation matrix $P$ ($1 \to 2 \to 3 \to \cdots \to n \to 1$) has eigenvalues equal to the $n$-th roots of unity:

$$\omega_k = e^{2\pi i k/n}, \quad k = 0, 1, \ldots, n-1$$

**Circulant matrix** = linear combination of powers of $P$ = $c_0 I + c_1 P + c_2 P^2 + \cdots$

### The Fourier Basis

The eigenvectors of $P$ form the **Fourier matrix** $F$ — this is the **matrix of the Discrete Fourier Transform (DFT)**!

$$F_{jk} = \frac{1}{\sqrt{n}} \omega_n^{jk}$$

**Key property**: the Fourier basis is the **common eigenbasis of all circulant matrices**.

### Circular Convolution

The circular convolution of two vectors = the product of the corresponding circulant matrices.

**Key theorem**: the DFT converts convolution to pointwise multiplication.

$$\text{DFT}(\mathbf{a} * \mathbf{b}) = \text{DFT}(\mathbf{a}) \odot \text{DFT}(\mathbf{b})$$

---

## Lec 34-36: Applications of DFT

### DFT = Change of Basis

Coordinate transformation from the standard basis to the Fourier basis:

$$\hat{\mathbf{f}} = F^* \mathbf{f}$$

Inverse transform: $\mathbf{f} = F\hat{\mathbf{f}}$

### Applications

- **Signal compression**: keep only large coefficients after DFT → the mathematical foundation of JPEG/MP3
- **Denoising**: DFT → filter out high-frequency components → inverse DFT
- **Convolution acceleration**: direct convolution $O(n^2)$, pointwise multiplication after DFT $O(n \log n)$ (FFT)

### Deep Connection to Box Time Series

The power spectrum in Box Ch2 = DFT of the autocovariance function:

$$p(f) = 2\left(\gamma_0 + 2\sum_{k=1}^{\infty} \gamma_k \cos 2\pi f k\right)$$

This **is** the Fourier transform! The ACF $\gamma_k$ and spectrum $p(f)$ are Fourier duals.

**Frequency-domain view of linear filters**:

The spectral density of the ARMA model $\phi(B)\tilde{z}_t = \theta(B)a_t$:

$$g(f) = \sigma_a^2 \frac{|\theta(e^{-2\pi if})|^2}{|\phi(e^{-2\pi if})|^2}$$

MA → numerator (zeros) → suppresses energy at specific frequencies
AR → denominator (poles) → amplifies energy at specific frequencies

**Spectral peak of AR(2)** (sunspot ~11-year cycle) = frequency corresponding to the argument of the complex eigenvalues. This is perfectly consistent with the eigenvalue structure of circulant matrices!

### DFT in Solar Forecasting

- **Extracting the daily cycle**: DFT of the power series → peak at frequency $1/24\text{h}$ = daily variation; peak at $1/8760\text{h}$ = annual variation
- **Denoising**: high-frequency noise (sensor jitter) removed via low-pass filtering
- **Feature engineering**: DFT coefficients can serve as frequency-domain features for ML models
- **Frequency-domain interpretation of SARIMA**: seasonal differencing $\nabla_{24}$ is equivalent to placing zeros at frequencies $k/24$

---

## Grand Unification: The Knowledge Network of Linear Algebra

```
Vector Spaces → Basis → Dimension → Rank-Nullity Theorem
    ↓                                         ↓
Linear Maps → Matrices → Four Subspaces → Orthogonal Complements
    ↓              ↓                          ↓
Eigenvalues → Diagonalization → Spectral Theorem → Positive Definiteness
    ↓                                              ↓
SVD ← Singular Values = √(eigenvalues of M^TM)
 ↓           ↓                      ↓
PCA    Low-Rank Approx    Pseudoinverse / Least Squares
 ↓                                   ↓
DFT  =  Eigendecomposition of Circulant Matrices  =  Box Power Spectrum
```

**The core message of MIT 18.06**:

> Linear algebra is not just "a tool for solving systems of equations" — it is the **language for understanding the structure of data**.
> The four fundamental subspaces tell you "what can be explained";
> SVD tells you "in what order things matter";
> the Fourier transform tells you "which frequencies dominate."

---

## Action Plan for the Solar Forecasting Project

Based on the full MIT 18.06 course, concrete recommendations for the future solar forecasting framework:

1. **First step of data exploration**: apply SVD to the meteorological feature matrix, examine rank and condition number
2. **Feature selection**: PCA dimensionality reduction, or inspect which original features contribute most via the $V$ matrix
3. **Multi-site modeling**: low-rank decomposition of the power matrix → spatial pattern extraction
4. **Frequency-domain analysis**: DFT to examine periodic structure → determine $s$ for SARIMA
5. **Numerical stability**: use QR decomposition for regression, do not solve the normal equations directly
6. **Regularization decision**: condition number $\kappa > 100$ → Ridge/Lasso needed
7. **Residual diagnostics**: eigenvalue distribution of the residual covariance matrix → verify model adequacy

---

*📖 [MIT Course Series](/blog/tags/MIT) | [Part 3: Eigenvalues and SVD](/blog/2026-03-16-mit-1806-part3-eigen-svd) | 🧠 MIT 18.06 Spring 2025 — Full Course Complete*
