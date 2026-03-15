---
title: "📖 NWP Textbook Notes Ch1-2: From Primitive Equations to NWP"
description: "Close reading of Warner's Numerical Weather and Climate Prediction Ch1-2. Primitive equations, Reynolds averaging, turbulence parameterization, approximate equations."
pubDate: 2026-03-15
lang: en
category: solar
series: nwp-warner
tags: ['Textbook Notes', 'NWP', 'Primitive Equations', 'Reynolds Averaging', 'Numerical Weather Prediction']
---

> 📖 [Back to Textbook Index](/textbook/)

## Why Study This Book?

Yang & Kleissl's PV forecasting textbook devotes 4 pages in Ch7.1 to introducing the NWP primitive equations — Warner uses an entire book (560 pages) to cover the same system.

**The core pipeline of PV forecasting**: NWP outputs irradiance forecasts → clear-sky normalization → ML post-processing → Model Chain → power. NWP is the starting point of this pipeline. Understanding its internal mechanics is what lets you understand where forecast errors come from and how to correct them.

---

## Ch1: Introduction — The Big Picture of NWP

### The Complete Spectrum of Time Scales

NWP is not a single tool; it is a complete prediction system spanning from seconds to centuries:

| Time Scale | Application | PV Context |
|------------|-------------|------------|
| Seconds | CFD, building wind fields | Inverter-level power fluctuation |
| Minutes | Nowcast (1–2 h) | Sky camera + very-short-term forecasting |
| Hours–Days | Deterministic weather forecast | **Day-Ahead Market (DAM), Real-Time Market (RTM)** |
| Week | Ensemble forecast | Weekly dispatch planning |
| Season | Coupled ocean–atmosphere model | Annual energy yield assessment |
| Century | Climate model | Long-term PV plant planning |

### Warner's Core Philosophy

> **Analyze observations and theory first; run models second.**

This aligns perfectly with Yang's textbook Ch2 — don't jump straight into running an LSTM. Warner's own words: "Using models prematurely only extends the time required to complete a research project."

### The Trend Toward Unified Modeling

- Before: mesoscale and global models developed separately
- Now: a single framework serves all scales (e.g., ECMWF IFS)
- Before: weather forecast models and climate models developed separately
- Now: unified models (e.g., UKMO Unified Model)

**Implication for PV**: WRF-Solar is a product of this trend — physical schemes for solar irradiance optimized on top of a general-purpose NWP framework.

---

## Ch2: Governing Equations — The Mathematical Foundation of NWP

### The Primitive Equations: 7 Equations, 7 Unknowns

At the heart of NWP is a system of 7 partial differential equations describing atmospheric motion:

**① Three momentum equations** (forecast wind components $u, v, w$):

$$\frac{Du}{Dt} = -\frac{1}{\rho}\frac{\partial p}{\partial x} + fv + Fr_x$$

$$\frac{Dv}{Dt} = -\frac{1}{\rho}\frac{\partial p}{\partial y} - fu + Fr_y$$

$$\frac{Dw}{Dt} = -\frac{1}{\rho}\frac{\partial p}{\partial z} - g + Fr_z$$

Physical meaning of the three terms on the right:
- **Pressure gradient force**: drives wind from high pressure toward low pressure
- **Coriolis force** ($f = 2\Omega\sin\phi$): Earth's rotation deflects the wind
- **Friction** ($Fr$): surface drag + turbulent stress

**② Thermodynamic equation** (forecast temperature $T$):

$$\frac{DT}{Dt} = -(T_d - T)\frac{Dz}{Dt} + \frac{1}{c_p}\frac{DH}{Dt}$$

$H$ is the heating rate — this is precisely the central quantity computed by radiation parameterization schemes. **Much of the error in irradiance forecasts stems from the accuracy with which this $H$ is computed.**

**③ Mass continuity equation** (forecast density $\rho$):

$$\frac{D\rho}{Dt} + \rho\left(\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} + \frac{\partial w}{\partial z}\right) = 0$$

**④ Water vapor equation** (forecast specific humidity $q_v$):

$$\frac{Dq_v}{Dt} = Q_v$$

$Q_v$ is the water vapor source/sink term — evaporation and condensation. **Cloud formation depends on this equation**, and clouds determine surface irradiance.

**⑤ Equation of state** (diagnostic equation):

$$p = \rho R T$$

### Connecting to the Yang Textbook

The "7 primitive equations (3 momentum + thermodynamics + water vapor + mass + state equation)" mentioned in Yang Ch7.1.1 correspond exactly to Eq. 2.1–2.7 here. Warner's contribution is to work through the physical meaning, mathematical derivation, and approximation assumptions of each equation in full.

---

### Reynolds Averaging: From the Real Atmosphere to Computable Equations

Turbulent scales in the atmosphere are far smaller than NWP grid spacing (a 10 km grid cannot resolve 10 m eddies). The solution:

**Decompose each variable into a mean part plus a turbulent fluctuation**:

$$u = \bar{u} + u', \quad T = \bar{T} + T', \quad p = \bar{p} + p'$$

Substituting into the primitive equations and taking the average yields the **Reynolds-averaged equations**. The key result is the appearance of **Reynolds stress terms**:

$$\tau_{zx}^{turb} = -\rho \overline{u'w'}$$

These terms represent the effect of turbulence on the mean flow — **they must be represented through parameterization schemes**, which is the mathematical origin of "boundary-layer parameterization" in NWP.

**Connection to PV forecasting**:
- Boundary-layer turbulence affects surface sensible/latent heat fluxes → affects atmospheric water vapor content → affects cloud formation → affects irradiance
- The choice of PBL (planetary boundary layer) scheme is one of the most sensitive settings in WRF-Solar

---

### Three Families of Approximate Equations

| Approximation | Core Idea | Waves Filtered | Applicable Models |
|---------------|-----------|----------------|-------------------|
| **Hydrostatic** | $\frac{\partial p}{\partial z} = -\rho g$ | Sound waves | Global models ($\Delta x > 10$ km) |
| **Boussinesq / Anelastic** | Volume conservation replaces mass conservation | Sound waves | Meso- and small-scale models |
| **Shallow-water** | Uniform, incompressible, hydrostatic | Sound waves | Pedagogical "toy model" |

**Physical meaning of the hydrostatic approximation**: When $\frac{Dw}{Dt} \ll g$, the vertical direction reduces to a balance between gravity and the pressure gradient force alone. This means density is tied to the vertical pressure gradient — sound waves cannot propagate (they require density to vary independently of pressure).

**Enormous impact on computational efficiency**: Filtering out sound waves allows the time step to increase substantially (sound wave speed ~330 m/s vs. weather system movement speed ~30 m/s), reducing the computational cost by roughly an order of magnitude.

**However**: When $\Delta x < 10$ km (high-resolution regional models), the hydrostatic approximation no longer holds — the full non-hydrostatic equations must be used. This is why HRRR (3 km) uses non-hydrostatic equations while GFS (13 km) can use the hydrostatic approximation.

---

## Cross-Textbook Knowledge Map

| Warner Ch2 Concept | Yang Textbook Counterpart | Practical Application |
|--------------------|---------------------------|-----------------------|
| 7 primitive equations | Ch7.1.1 (exact match) | Dynamical core of NWP |
| Reynolds stress | Ch7.1.2 physical parameterization | PBL scheme choice affects irradiance |
| Hydrostatic approximation | Ch6.6 GFS vs. HRRR | GFS (hydrostatic) vs. HRRR (non-hydrostatic) |
| Water vapor equation | Ch7.1.2 cloud microphysics | Cloud = largest uncertainty source in irradiance forecasting |
| $H$ in thermodynamic equation | Ch11 radiation parameterization | Heating rate computation → irradiance output |

---

## References

- Warner, T.T. (2011). *Numerical Weather and Climate Prediction*. Cambridge University Press. Ch1–2.
- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and PV Power Forecasting*. CRC Press. Ch7.1.
- Holton, J.R. (2004). *An Introduction to Dynamic Meteorology* (4th ed.). Academic Press.
- Dutton, J.A. (1976). *The Ceaseless Wind: An Introduction to the Theory of Atmospheric Motion*. McGraw-Hill.
