---
title: "MIT 18.06 Linear Algebra Part 1: The Four Pillars of Vector Spaces"
description: "A close reading of MIT 18.06 Spring 2025 Lectures 1-7: from Gaussian elimination to the four fundamental subspaces, the core framework of linear algebra applied to solar forecasting"
pubDate: 2026-03-16
lang: en
series: mit-courses
category: algorithm
tags: ["Linear Algebra", "MIT", "Vector Spaces", "Gaussian Elimination", "Rank-Nullity Theorem", "Textbook Notes"]
---

# MIT 18.06 Linear Algebra Part 1: The Four Pillars of Vector Spaces

> **Course**: MIT 18.06 Linear Algebra, Spring 2025 — Prof. Nike Sun
> **Textbook**: Gilbert Strang, *Introduction to Linear Algebra*, 6th Ed.
> **Scope**: Lecture 1-7 (Foundations of Vector Spaces)

## Why Study Linear Algebra?

Linear algebra is the **mathematical language of all data science, machine learning, and signal processing**. For solar power forecasting:

- **Least Squares Fitting** (Lec 12) = parameter estimation for pvlib temperature models
- **SVD/PCA** (Lec 24-28) = dimensionality reduction of meteorological features, multi-site data compression
- **Eigenvalue Decomposition** (Lec 20-23) = characteristic equation analysis for Box ARIMA
- **Matrix Operations** = the essence of forward/backward propagation in deep learning

Strang's famous quote: "**The heart of linear algebra is the four fundamental subspaces.**"

---

## Lec 1-2: Vectors and Matrix Operations

### Linear Combinations — The Starting Point of Everything

Vectors in $\mathbb{R}^n$ can do two things: **addition** and **scalar multiplication**. Combining both gives a **linear combination**:

$$c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + \cdots + c_k\mathbf{v}_k$$

The **span** of a set of vectors = the set of all possible linear combinations.

### Matrix Times Vector = Linear Combination of Columns

$$A\mathbf{x} = x_1\mathbf{a}_1 + x_2\mathbf{a}_2 + \cdots + x_n\mathbf{a}_n$$

**This is the most important perspective for understanding matrices**: $A\mathbf{x}$ is not a mechanical "row × column" computation — it is a linear combination of the column vectors of $A$, with coefficients given by $\mathbf{x}$.

### Gaussian Elimination = Matrix Multiplication

Each elimination step can be written as left-multiplication by an elementary matrix $G_i$:

$$G_k \cdots G_2 G_1 A\mathbf{x} = G_k \cdots G_2 G_1 \mathbf{b}$$

**This is more than a computational trick — it reveals the essence of matrix factorization**. LU decomposition is just collecting all the $G_i$.

**Connection to solar forecasting**: The implicit time integration in numerical weather prediction (NWP) requires solving large sparse linear systems; Gaussian elimination (LU factorization) is the core solver. The finite-difference equations in Warner NWP Ch3 all reduce to $A\mathbf{x} = \mathbf{b}$.

---

## Lec 3-4: Inverses and Linear Independence

### Gauss-Jordan Elimination for the Inverse

Transform $(A|I)$ to $(I|A^{-1})$ via row operations. Key insight:

> **Not every square matrix is invertible.** Invertible $\Leftrightarrow$ columns are linearly independent $\Leftrightarrow$ null space contains only the zero vector.

### Column Space $C(A)$

An $m \times n$ matrix $A$ defines a map $\mathbb{R}^n \to \mathbb{R}^m$. The **column space** $C(A) = \{A\mathbf{x} : \mathbf{x} \in \mathbb{R}^n\}$ is the image of this map.

$$A\mathbf{x} = \mathbf{b} \text{ has a solution} \Leftrightarrow \mathbf{b} \in C(A)$$

### Null Space $N(A)$

$$N(A) = \{\mathbf{x} : A\mathbf{x} = \mathbf{0}\}$$

Invertible row operations do not change the null space: $N(A) = N(R)$ ($R$ is the RREF).

**Practical meaning**: The dimension of the null space = the "degrees of freedom" in the system. In solar system modeling, if the parameter matrix has a nontrivial null space, the model is **over-parameterized** — some parameter combinations cannot be distinguished by data (analogous to the ridge-shaped likelihood surface in Box Ch7 when $\phi \approx \theta$ for ARMA(1,1)).

---

## Lec 5-6: Structure of the General Solution

### Homogeneous + Particular = General Solution

For $A\mathbf{x} = \mathbf{b}$:

1. If $\mathbf{b} \notin C(A)$, no solution exists
2. If a solution exists, find one **particular solution** $\mathbf{x}_0$ (set free variables = 0)
3. **General solution** = $\mathbf{x}_0 + N(A)$

This is exactly the same structure as the general solution of a differential equation: particular solution + homogeneous solution. The ARIMA forecast function in Box Ch5 has the same structure — the final forecast = particular solution (anchored by the MA part) + homogeneous solution (decay/oscillation determined by AR characteristic roots).

---

## Lec 7: Basis, Dimension, and the Rank-Nullity Theorem

### Basis

A basis of a vector space $V$ = a set of vectors that are **linearly independent** and **span** $V$.

### Rank-Nullity Theorem

$$n = \dim C(A) + \dim N(A) = \text{rank}(A) + \text{nullity}(A)$$

> **$n$ columns = number of pivot columns + number of free columns**

This is the most fundamental "conservation law" of linear algebra — information is neither created nor destroyed, it is only distributed between the column space and the null space.

**Deep connections**:
- **Box Ch3**: The invertibility/stationarity of ARMA(p,q) depends on the roots of the characteristic equation — essentially the "null space structure" of the operators $\phi(B)$ and $\theta(B)$
- **PCA dimensionality reduction**: Data matrix rank $r \ll \min(m,n)$ → $n-r$ dimensional null space corresponds to redundant features → only $r$ principal components need to be retained
- **NWP data assimilation**: Column space of observation matrix $H$ = observable states; null space = unobservable states

---

## Module Summary: Geometric Intuition for Vector Spaces

Lectures 1-7 establish the core framework of linear algebra. Below is a summary using bullet lists (avoiding LaTeX-in-table formatting):

- **Linear Combination** — Geometric meaning: the "way of moving" in vector space — Role in solar forecasting: models are linear combinations of basis functions
- **Column Space $C(A)$** — Geometric meaning: the space the matrix can "reach" — Role in solar forecasting: the range of predictions the model can express
- **Null Space $N(A)$** — Geometric meaning: the space the matrix "cannot see" — Role in solar forecasting: parameter combinations the model cannot distinguish
- **Rank $r$** — Geometric meaning: the dimension of effective information — Role in solar forecasting: intrinsic dimension of the data
- **RREF** — Geometric meaning: the simplest equivalent form — Role in solar forecasting: the streamlined model after feature selection

**Preview of next post**: Lec 8-14 moves into projections and least squares — linear regression, QR decomposition, and the pseudoinverse. These are the direct mathematical tools for parameter estimation in solar forecasting.

---

*📖 [MIT Course Series](/blog/) | [Back to Textbook Index](/textbook/) | 🧠 MIT 18.06 Spring 2025*
