---
title: "MIT 18.063 Matrix Calculus: From the Linear Operator Nature of Derivatives to Backpropagation"
description: "A deep dive into MIT 18.063 Matrix Calculus (Jan 2026): derivatives as linear operators, differentials of matrix functions, forward/reverse mode chain rules, automatic differentiation, calculus of variations, and the Hessian"
pubDate: 2026-03-16
lang: en
series: mit-courses
category: algorithm
tags: ["matrix calculus", "MIT", "automatic differentiation", "backpropagation", "chain rule", "gradient", "textbook notes"]
---

# MIT 18.063 Matrix Calculus: From the Linear Operator Nature of Derivatives to Backpropagation

> **Course**: MIT 18.063 Matrix Calculus for ML and Beyond, IAP January 2026
> **Instructors**: Alan Edelman & Steven G. Johnson
> **Prerequisites**: 18.06 Linear Algebra + 18.02 Multivariable Calculus

## Core Idea: A Derivative Is Not a "Number" — It Is a Linear Operator

### Limitations of Traditional Calculus

18.01 tells us $f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$ — the derivative is a "number."

18.02 generalizes this to vectors: the gradient $\nabla f$ is a vector, and the Jacobian $J$ is a matrix.

**But what about when both input and output are matrices?** What is the "derivative" of $f(X) = X^{-1}$?

### A Unified View: Derivative = Linear Operator

$$f(x + dx) - f(x) = df = f'(x)[dx] + o(\|dx\|)$$

$f'(x)$ is a **linear operator** that takes $dx$ (a small perturbation) as input and returns $df$ (the small change) as output.

**Examples**:
- $f(X) = X^2 \Rightarrow f'(X)[dX] = X \cdot dX + dX \cdot X$
- $f(X) = X^{-1} \Rightarrow f'(X)[dX] = -X^{-1} dX \, X^{-1}$
- $f(X) = \det(X) \Rightarrow f'(X)[dX] = \det(X) \cdot \text{tr}(X^{-1}dX)$

**All of these are linear operations on the matrix $dX$** — no need to "flatten" matrices into vectors and multiply by a Jacobian!

**Significance for deep learning**: Neural network weights are matrices. Matrix calculus handles matrix-to-matrix derivatives directly, without the inefficient vectorization step.

---

## Lec 1-2: Basic Rules

### Product Rule (Matrix Version)

$$d(AB) = (dA)B + A(dB)$$

Note: **order cannot be swapped** (matrix multiplication is not commutative)!

### Gradient of a Scalar Function

For a scalar function $f(X)$, using the **Frobenius inner product** $\langle A, B \rangle = \text{tr}(A^T B)$:

$$df = f'(X)[dX] = \langle \nabla f, dX \rangle = \text{tr}((\nabla f)^T \, dX)$$

$\nabla f$ has the **same shape** as $X$ — this is why PyTorch's `.grad` has the same shape as the parameter tensor.

**Key gradient formulas**:

- $f(A) = \text{tr}(A) \Rightarrow \nabla f = I$
- $f(A) = \|A\|_F \Rightarrow \nabla f = A / \|A\|_F$
- $f(A) = \mathbf{x}^T A \mathbf{y} \Rightarrow \nabla f = \mathbf{x}\mathbf{y}^T$
- $f(A) = \det(A) \Rightarrow \nabla f = \det(A)(A^{-1})^T = \text{adj}(A)^T$
- $f(\mathbf{x}) = \mathbf{x}^T A\mathbf{x} \Rightarrow \nabla f = (A + A^T)\mathbf{x}$ (if $A$ is symmetric, $= 2A\mathbf{x}$)

### Kronecker Product and Vectorization

Flattening an $m \times n$ matrix into an $mn \times 1$ vector: $\text{vec}(X)$

$$\text{vec}(AXB) = (B^T \otimes A)\text{vec}(X)$$

$\otimes$ is the Kronecker product. This turns the Jacobian of a matrix function into an ordinary matrix — but the dimensionality explodes, so it is mainly useful for theoretical analysis.

---

## Lec 3: Chain Rule — Forward vs. Reverse

### Multidimensional Chain Rule

$$\frac{d}{dx}[g(f(x))] = g'(f(x)) \circ f'(x)$$

Composition of linear operators = matrix multiplication.

### Forward Mode

From input to output, compute $f'(x)[dx]$ layer by layer:

$$dx \to df_1 = f_1'[dx] \to df_2 = f_2'[df_1] \to \cdots \to df_n$$

**Each pass differentiates along only one input direction.** If there are $n$ inputs, $n$ forward passes are needed.

### Reverse Mode = Backpropagation

From output to input, compute the "adjoint" at each layer:

$$\bar{f}_n = 1 \gets \bar{f}_{n-1} = f_n'^T[\bar{f}_n] \gets \cdots \gets \bar{f}_0 = \nabla f$$

**One pass computes gradients with respect to all inputs simultaneously!** A single backward pass yields the complete gradient.

### Key Insight

- **Many inputs, few outputs** (e.g., a loss function $\mathbb{R}^{10^6} \to \mathbb{R}$) → **reverse mode is efficient**
- **Few inputs, many outputs** (e.g., forward simulations) → **forward mode is efficient**

**This is why deep learning uses backpropagation**: $10^6+$ parameters, scalar loss.

**Significance for solar forecasting**:
- Training neural network prediction models → backpropagation (done automatically by PyTorch/JAX)
- Sensitivity analysis (how does a change in one parameter affect predictions) → forward mode
- Physics-constrained optimization (PINN) → requires mixed mode

---

## Lec 5-6: Automatic Differentiation

### Dual Numbers — Forward AD

Define $a + b\epsilon$ where $\epsilon^2 = 0$ (not zero, but "infinitesimal"):

$$f(a + b\epsilon) = f(a) + f'(a) \cdot b\epsilon$$

**Simply replace floating-point numbers with dual numbers in your program, and you automatically get derivatives!**

```python
# Conceptual illustration (Python)
class Dual:
    def __init__(self, val, deriv=0):
        self.val = val
        self.deriv = deriv
    def __mul__(self, other):
        return Dual(self.val * other.val,
                     self.val * other.deriv + self.deriv * other.val)
```

### Reverse AD on a Computation Graph

A neural network = a directed acyclic graph (DAG). Each node is an operation.

**Forward pass**: From input to output, compute the value at each node
**Backward pass**: From output to input, compute the "adjoint" at each node (vJP = vector-Jacobian product)

**Key point**: Modern AD is **compiler technology** — not symbolic differentiation, not finite differences. Both JAX's `jax.grad()` and PyTorch's `loss.backward()` are built on this.

---

## Lec 4: Generalized Gradient and Inner Products

### A Gradient Requires an Inner Product to Be Defined

On an arbitrary vector space $V$, the derivative $f'(x)$ of a scalar function $f: V \to \mathbb{R}$ is a linear functional.

By the **Riesz representation theorem**: any linear functional can be written as an inner product with some vector:

$$f'(x)[dx] = \langle \nabla f, dx \rangle$$

$\nabla f \in V$ — the gradient has the same "shape" as the input.

### Gradient = Direction of Steepest Ascent

$$\nabla f = \arg\max_{\|v\|=1} f'(x)[v]$$

**But "steepest ascent" depends on the choice of norm!** Different inner products yield different gradient directions.

This is why **preconditioning** and **natural gradient** methods work — they correspond to defining the gradient with a better inner product.

**Example from solar forecasting**: If feature magnitudes differ greatly (temperature ~300 K vs. irradiance ~1000 W/m²), standard gradient descent converges at different rates in different directions. Feature normalization = changing the inner product to weight all directions equally.

---

## Lec 6: Calculus of Variations

### Calculus on Function Spaces

When the "variable" is a function $u(x)$, derivatives become **variational derivatives**:

$$\delta f[u] = f(u + \delta u) - f(u) = f'(u)[\delta u]$$

The stationarity condition $\nabla f = 0$ → **Euler-Lagrange equations**

**Classic examples**:
- Shortest path → geodesic equations
- Principle of least action → Lagrangian mechanics
- Optimal control → Hamilton-Jacobi-Bellman equations

**Significance for solar forecasting**:
- Optimal control theory (Box Ch15) is the discrete version of the calculus of variations
- The loss function of PINNs (Physics-Informed Neural Networks) = integral of PDE residuals → a variational problem
- Optimal energy storage scheduling = discrete-time optimal control

---

## Lec 7: Complex Calculus (CR Calculus)

### Problem: Is $f(z) = |z|^2 = z\bar{z}$ Not Differentiable?

Traditional complex analysis requires the Cauchy-Riemann conditions (holomorphic functions); $|z|^2$ does not satisfy them.

### Wirtinger Derivatives

Define $\frac{\partial}{\partial z} = \frac{1}{2}\left(\frac{\partial}{\partial x} - i\frac{\partial}{\partial y}\right)$ and $\frac{\partial}{\partial \bar{z}} = \frac{1}{2}\left(\frac{\partial}{\partial x} + i\frac{\partial}{\partial y}\right)$

This allows us to **define a "gradient" even for non-holomorphic functions**.

**Significance for ML**: Gradients for complex-valued neural networks (used in signal processing / quantum ML) require CR calculus. JAX's complex AD is based on Wirtinger derivatives.

---

## Lec 7+9: Constrained Derivatives and Eigenvalue Differentiation

### Derivative of Eigenvalues

Let $A(t)$ be a parameterized family of matrices, $\lambda(t)$ an eigenvalue, $\mathbf{v}(t)$ the corresponding eigenvector:

$$\frac{d\lambda}{dt} = \frac{\mathbf{v}^T \frac{dA}{dt} \mathbf{v}}{\mathbf{v}^T \mathbf{v}}$$

(For symmetric matrices — the **Hellmann-Feynman theorem**)

**Note**: When eigenvalues coincide, the derivative may not exist! This is a key difficulty in optimization.

### The Hessian and Second-Order Approximation

$$f(x + \delta x) \approx f(x) + \nabla f^T \delta x + \frac{1}{2}\delta x^T H \delta x$$

$H$ positive definite → local minimum; $H$ indefinite → saddle point

**Newton's method**: $\delta x = -H^{-1}\nabla f$ (second-order convergence, but requires the Hessian)

**Quasi-Newton methods (BFGS)**: Gradually approximate $H^{-1}$ without computing the full Hessian

---

## Grand Unification: The Knowledge Map of Matrix Calculus

```
Derivative = linear operator f'(x)[dx]
    ↓
Scalar function → gradient ∇f (requires inner product)
Matrix function → Jacobian (requires Kronecker product / vectorization)
    ↓
Chain rule = composition of linear operators
    ↓
Forward mode (few inputs)  ←→  Reverse mode (few outputs)
    ↓                               ↓
Dual number AD               Backprop / vJP
    ↓                               ↓
Forward AD libraries         PyTorch / JAX
    ↓
Second-order derivatives → Hessian → Newton's method / BFGS
    ↓
Calculus of variations → Euler-Lagrange → optimal control / PINN
```

---

## Cross-References with Three Textbooks

- **Box Ch7**: MLE for ARIMA parameters = minimizing $S(\phi, \theta)$; Marquardt algorithm = gradient descent with Hessian approximation
- **Warner Ch12**: Variational methods in data assimilation (4D-Var) = calculus of variations applied to NWP; loss = observation residuals + background constraint
- **Yang Ch7**: Parameter optimization for post-processing models = gradient descent
- **PINN framework**: Physics constraints + data fitting → combined loss function → requires efficient automatic differentiation

## Action Guide for the Solar Forecasting Project

1. **Use JAX instead of pure NumPy**: JAX = NumPy + automatic differentiation + JIT compilation, perfect for gradient computation
2. **Understand `loss.backward()`**: Backpropagation is not magic — it's the reverse mode of the chain rule
3. **Sensitivity analysis**: Use forward AD to compute the effect of individual meteorological parameters on predictions
4. **Feature normalization = modifying the inner product**: Ensures gradient descent converges at a consistent rate in all directions
5. **Hessian diagnostics**: Large condition number → use Adam/BFGS; small condition number → SGD is sufficient
6. **The math behind PINN is right here**: PDE constraints + data fitting = variational problem + automatic differentiation

---

*📖 [MIT Course Series](/blog/tags/MIT) | [18.06 Linear Algebra](/blog/2026-03-16-mit-1806-part1-foundations) | 🧠 MIT 18.063 Matrix Calculus — Full Course Complete*
