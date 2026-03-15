---
title: '🧠 Thinking Training — NWP Textbook Logic Chains'
description: 'Logical reasoning exercises for the Warner NWP Textbook. From primitive equations to forecast error sources, linking NWP knowledge into causal networks and connecting to solar power forecasting practice. Continuously updated.'
pubDate: 2026-03-15
updatedDate: 2026-03-15
lang: en
category: solar
series: nwp-warner
tags: ['thinking training', 'logical reasoning', 'NWP', 'numerical weather prediction', 'knowledge synthesis']
---

> 📖 This article is part of the [Warner NWP Textbook](/textbook/nwp-warner/) thinking training series | [Back to Textbook Index](/textbook/)

Knowing something is not the same as being able to use it. This page contains **logical reasoning exercises** from studying the Warner NWP Textbook — connecting isolated knowledge points into causal chains, training the "why" and "therefore" way of thinking.

**⚡ Continuously updated as study progresses.**

---

## I. Current Knowledge Map

Warner's 16 chapters can be grouped into **six major modules**:

```
Module 1: Mathematical Foundations (Ch2-3)          ✅ Complete
  Ch2 Governing Equations ✅ → Ch3 Numerical Methods ✅
      ↓
Module 2: Physical Representations (Ch4-5)           ✅ Complete
  Ch4 Parameterization Schemes ✅ → Ch5 Surface Processes ✅
      ↓
Module 3: Initialization & Uncertainty (Ch6-8)       ✅ Complete
  Ch6 Data Assimilation ✅ → Ch7 Ensemble Methods ✅ → Ch8 Predictability ✅
      ↓
Module 4: Evaluation (Ch9-11)                        ✅ Complete
  Ch9 Verification Methods ✅ → Ch10 Experimental Design ✅ → Ch11 Output Analysis ✅
      ↓
Module 5: Operations (Ch12-13)                       ✅ Complete
  Ch12 Operational NWP ✅ → Ch13 Post-processing ✅
      ↓
Module 6: Extensions (Ch14-16)                       ✅ Complete
  Ch14 Coupled Applications ✅ → Ch15 CFD ✅ → Ch16 Climate Modeling ✅
```

**🎉 All 16/16 chapters complete!** Next up: Box time series analysis.

---

## II. Causal Reasoning Chains

### Chain 1: Why is NWP the only reliable source for day-ahead solar forecasting?

```
Premise 1 (Yang Ch4.5.4): Irradiance's spatiotemporal dependence comes entirely from moving clouds
    ↓
Premise 2 (Yang Ch4.5.4): Sky cameras assume clouds are "frozen" → fails after <30 min
Premise 3 (Yang Ch4.5.4): Satellite CMV assumes uniform linear cloud motion → fails after <4 h
    ↓
Premise 4 (Warner Ch2): Only primitive equations can solve cloud dynamical evolution
    ↓
Premise 5 (Yang Ch5.6.2): Grid DAM requires >36 h lead time
    ↓
Conclusion: NWP is the only reliable source for day-ahead forecasting
```

This reasoning chain starts from the primitive equations in Warner Ch2 and explains why cameras and satellites fail at the day-ahead scale — because their physical assumptions (frozen field / uniform advection) break down over long time horizons, and only NWP's primitive equations can simulate cloud formation, development, and dissipation.

### Chain 2: Where do NWP forecast errors come from?

```
Warner Ch2 primitive equations → 7 variables need to be solved
    ↓
Problem 1: Equations are nonlinearly coupled → no analytical solution → must discretize (Ch3)
    → Discretization introduces truncation errors
    ↓
Problem 2: Sub-grid processes (turbulence, cloud microphysics) cannot be explicitly resolved
    → Must be parameterized (Ch4-5)
    → Parameterization is an approximation to real physics → introduces parameterization errors
    ↓
Problem 3: Initial conditions come from limited observations
    → Observations have measurement errors + insufficient spatial coverage
    → Imperfect initial conditions → chaotic amplification (Ch8)
    ↓
Total error = truncation error + parameterization error + initial condition error
```

**Connection to Yang's textbook**: Yang Ch3.1 says "forecast errors have two sources: imperfect initial conditions + imperfect dynamical laws." Warner Ch2 elaborates on what "imperfect dynamical laws" specifically means — it's not that the equations themselves are wrong (the primitive equations are exact), but that the **solution method** introduces errors (discretization + parameterization).

### Chain 3: How does Reynolds averaging connect to irradiance forecasting?

```
Warner Ch2: Atmosphere has sub-grid turbulence → cannot be directly resolved
    ↓
Reynolds decomposition: u = ū + u' → averaging produces covariance term -ρ(u'w')
    ↓
Covariance term = Reynolds stress = turbulence effect on mean flow
    ↓
Must be parameterized (Ch4) → Planetary Boundary Layer (PBL) parameterization scheme
    ↓
PBL scheme determines vertical mixing intensity
    ↓
Branch A: Strong mixing → moisture rises → cloud formation → GHI decreases
Branch B: Weak mixing → stable stratification → fewer clouds → GHI increases
    ↓
Yang Ch7.1.2: PBL scheme is one of the most sensitive choices in WRF-Solar
```

**Core insight**: Starting from Reynolds averaging — a purely mathematical operation — four steps of reasoning lead directly to the accuracy of solar irradiance forecasting. This is what "knowledge is not an island" looks like: a turbulence decomposition method from 1895 determines the quality of solar power forecasting in 2024.

### Chain 4: How does the hydrostatic approximation choice affect solar forecasting?

```
Warner Ch2.3.1: Hydrostatic approximation filters sound waves → allows larger time steps → faster computation
    ↓
But: Hydrostatic approximation breaks down when Δx < 10 km
    ↓
GFS (global model, ~13 km) → can use hydrostatic approximation → coarse but global coverage
HRRR (regional model, 3 km) → must use non-hydrostatic equations → high-res but limited to CONUS
    ↓
Yang Ch6.6 comparison: HRRR irradiance forecasts better than GFS
    ↓
One reason: Non-hydrostatic equations resolve convective cells → more accurate cloud simulation
    ↓
But HRRR only covers the US → other regions must use GFS or ECMWF
    ↓
Value of WRF-Solar: Users can run their own non-hydrostatic regional model
    But requires meteorological expertise (the cross-disciplinary challenge of Yang Ch4.6.1)
```

**Practical decision significance**: For solar forecasting in the US, use HRRR (3 km non-hydrostatic); in China, only GFS/ECMWF (>10 km hydrostatic) or self-run WRF-Solar is available. The theoretical foundation for this decision is the hydrostatic approximation in Warner Ch2.3.

### Chain 5: Why does doubling resolution cost ×8? (New from Ch3)

```
CFL condition: U·Δt/Δx < 1
    ↓
Halving Δx → Δt must also halve (or CFL is violated)
    ↓
2D grid points ×4 (same area, ×2 in each dimension)
    ↓
Total computation = grid points × time steps = 4 × 2 = 8
    ↓
In practice even more: vertical levels may also be refined → ×16 or more
```

**Decision significance for solar forecasting**: Running WRF-Solar on a RTX 4050, going from 9 km → 3 km requires ~27× more computation. Must weigh whether the accuracy gain is worth it.

### Chain 6: How does truncation error propagate all the way to irradiance? (New from Ch3)

```
Finite difference computes derivatives → truncation error (short wave 6Δx error ~17%)
    ↓
Inaccurate pressure gradient force → geostrophic wind bias
    ↓
Inaccurate divergence → vertical motion bias
    ↓
Vertical motion drives condensation/evaporation → cloud liquid water content bias
    ↓
Radiation scheme uses cloud water to compute irradiance → GHI output bias
```

**Core insight**: Irradiance forecast error doesn't only come from radiation parameterization — it accumulates from the most fundamental level of derivative approximation. This is why Yang says "cloud microphysics is the bottleneck" while Warner emphasizes "numerical methods also matter" — they have a multiplicative relationship, not additive.

### Chain 7: Why is "cloud the biggest bottleneck in irradiance forecasting"? (New from Ch4)

```
Radiation parameterization physics is mature (Beer's Law + Planck function)
    ↓
Input to radiation scheme = 3D distribution and optical properties of clouds
    ↓
Cloud optical properties ← cloud microphysics (droplet size distribution)
    ↓
Cloud existence ← convection parameterization (when and where condensation is triggered)
    ↓
Moisture supply for convection ← boundary layer parameterization (vertical mixing intensity)
    ↓
Thermodynamic forcing of boundary layer ← surface energy balance (function of irradiance!)
    ↓
Conclusion: The root cause of irradiance forecast error is not the radiation scheme itself,
but the entire cycle: radiation → surface → PBL → convection → microphysics → cloud → radiation
```

**Core insight**: Yang says "cloud microphysics is the bottleneck," Warner adds "all parameterization schemes are a coupled system" — there is no single-point fix.

### Chain 8: How do aerosols affect solar power forecasting? (New from Ch4)

```
Anthropogenic/natural aerosols → changes in CCN concentration
    ↓
More CCN → more but smaller cloud droplets → higher optical depth → higher albedo → lower GHI
Fewer CCN → fewer but larger cloud droplets → lower optical depth → higher precipitation efficiency → shorter-lived clouds → higher GHI
    ↓
Operational NWP typically does not simulate aerosols (too expensive)
But ECMWF assimilates CAMS aerosols → better irradiance forecasts
    ↓
Yang Ch5.4 REST2 requires AOD (τ₅₅₀) as input
Yang Ch4.5.1 clear-sky model multiplies 6 transmittances, including Tₐ = aerosol attenuation
    ↓
Conclusion: Aerosol uncertainty → clear-sky model uncertainty + NWP cloud simulation uncertainty
```

### Chain 9: How does surface energy partitioning affect solar forecasting? (New from Ch5)

```
Solar radiation reaches surface: R = (Q+q)(1-α) - I↑ + I↓
    ↓
R is partitioned into three parts: LE (latent heat) + H (sensible heat) + G (ground heat flux)
    ↓
Bowen ratio β = H/LE determines where energy goes:
  - Moist land (small β) → most energy evaporates → cool, moist boundary layer
  - Arid land (large β) → most energy heats atmosphere → hot, deep boundary layer
    ↓
Arid: deeper PBL → stronger convection → more afternoon cumulus → GHI ramp down
Moist: shallower PBL → weaker convection → fewer cumulus → more stable GHI
    ↓
Conclusion: soil moisture → Bowen ratio → PBL depth → convection triggering → cloud → irradiance
```

**Practical significance for solar**: Irrigated vs non-irrigated seasons show systematic differences in solar power output curves — irrigation lowers Bowen ratio → fewer afternoon ramp events.

### Chain 10: Why did PILPS find that more complex LSMs aren't necessarily better? (New from Ch5)

```
Complex LSMs have more parameters (vegetation, root systems, soil hydraulics...)
    ↓
Each parameter needs observational data to be defined — but most cannot be directly observed
    ↓
Uncertain parameters × many = expanded error space
    ↓
Simple LSM has fewer parameters → can be calibrated → may have higher actual accuracy
    ↓
Analogy: Yang Ch3 bias-variance tradeoff
  - Complex model = low bias, high variance
  - Simple model = high bias, low variance
```

**Lesson**: This is completely isomorphic to the overfitting problem in machine learning — model complexity should match the information content of the available data.

---

## III. Cross-Textbook Knowledge Network

| Warner Concept | Yang Textbook Equivalent | Practical Application |
|----------------|--------------------------|----------------------|
| 7 primitive equations (Ch2) | Ch7.1.1 identical | NWP dynamical core |
| Reynolds stress (Ch2) | Ch7.1.2 physical parameterization | PBL scheme choice affects irradiance |
| Hydrostatic approximation (Ch2) | Ch6.6 GFS vs HRRR | Model resolution decision |
| Water vapor equation (Ch2) | Ch7.1.2 cloud microphysics | Cloud = largest irradiance uncertainty source |
| CFL condition (Ch3) | Ch7.1.3 | Resolution ×2 → cost ×8 |
| Truncation error (Ch3) | Ch7.1.1 | Mathematical root of imperfect NWP irradiance |
| Spectral method Tco1279 (Ch3) | Ch6.6 ECMWF IFS | Exact derivatives but nonlinear aliasing |
| LBC six error sources (Ch3) | Ch4.6.1 WRF-Solar | Domain size and boundary scheme choices |
| Numerical dispersion (Ch3) | — | Short waves move too slowly, frontal gradients smoothed |
| Parameterization cycle (Ch4) | Ch7.1.2 | Radiation → surface → PBL → convection → microphysics → cloud → radiation |
| 5 cloud microphysics hydrometeor equations (Ch4) | Ch7.1.2 "cloud is bottleneck" | Cloud liquid water → optical depth → irradiance |
| Gray zone (Ch4) | Ch4.6.1 WRF-Solar | Convection scheme choice at 3–9 km |
| Aerosol → CCN → cloud → irradiance (Ch4) | Ch5.4 REST2 AOD input | Why ECMWF assimilates CAMS |
| Stochastic parameterization (Ch4) | Ch3.3.1 ensemble type ③ | Sub-grid uncertainty quantification |
| Surface energy balance R=LE+H+G (Ch5) | Ch4.2 surface reflection / Ch5.4 clear-sky GHI | Starting point of irradiance → surface → PBL |
| Bowen ratio → PBL → convection → cloud (Ch5) | — | Soil moisture indirectly affects irradiance |
| PILPS: complex ≠ better (Ch5) | Ch3 bias-variance | Parameter uncertainty vs model complexity |
| LDAS spin-up (Ch5) | Ch6 data assimilation (upcoming) | Soil state initialization requires months |

---

## IV. Hypotheses to Verify

As study continues into later chapters, the following hypotheses need verification:

1. ~~**Ch5 Surface Processes**~~ → **Verified — see "Resolved Puzzles"**

2. **Ch6 Data Assimilation** — How much better is ECMWF's 4D-Var compared to 3D-Var? What is the marginal improvement in irradiance forecasting? The quality of cloud field assimilation in initial conditions directly determines short-term forecasts — what does Warner say?

3. **Ch7 Ensemble Methods** — Does Warner's meteorological ensemble fully correspond to Yang Ch3.3's statistical ensemble? Ch4 mentions stochastic parameterization (adding noise to parameters) — is this the same thing as "model uncertainty perturbation" in ensemble methods?

4. **Ch9 Verification Methods** — How much overlap exists between Warner's NWP verification methods and Yang Ch9-10's forecast verification framework? What is special about irradiance forecast verification?

5. **"Optimal combination" of parameterization schemes** — Ch4 says parameterization schemes are tightly coupled, so does any particular combination of schemes suit solar forecasting scenarios especially well? Which schemes did WRF-Solar choose, and why?

6. **Practical impact of the gray zone** — Ch4 says 3–9 km is the gray zone for convection parameterization. In practice, how is this handled? Fully turning off convection parameterization vs using a scale-aware scheme vs using coarser resolution — which strategy works best for solar forecasting?

---

## V. Resolved Puzzles

### ❓ Yang Ch7.1.1 says "7 primitive equations," but the equations look very abstract — what is the physical meaning of each term?

✅ **Warner Ch2 completely resolved this puzzle.** Every term in every equation has a clear physical interpretation: pressure gradient force drives wind, Coriolis force deflects wind, heating rate $H$ includes radiation + latent heat + sensible heat, water vapor source/sink term $Q_v$ includes evaporation and condensation.

### ❓ Yang Ch7.1.2 says "parameterization is the most controversial topic in NWP," but why?

✅ **Warner Ch2's Reynolds averaging provides the answer.** The mathematical origin of parameterization is the Reynolds stress term — it is fundamentally a **closure problem** (fewer equations than unknowns). Any parameterization scheme is one approximation to this closure problem, and there is no "single correct answer." This is why controversy always persists.

### ❓ What is the specific derivation of the CFL condition? How does the time step constraint affect NWP real-time performance?

✅ **Warner Ch3 provides the detailed derivation.** CFL condition: $\Delta t \leq \Delta x / c$, where $c$ is the fastest signal propagation speed (sound waves ~340 m/s). This means at $\Delta x = 1$ km, $\Delta t \leq 3$ s, requiring 28,800 steps to simulate one day — this is the fundamental reason high-resolution NWP computation explodes. Semi-implicit methods can relax the CFL constraint but introduce accuracy loss.

### ❓ Is cloud microphysics parameterization the largest source of irradiance forecast error?

✅ **Warner Ch4 confirms and deepens this.** Not only is cloud microphysics itself a bottleneck, but the entire parameterization cycle (radiation → surface → PBL → convection → microphysics → cloud → radiation) is coupled. The physics of radiation schemes is mature; the bottleneck is their **input** — the three-dimensional distribution of clouds. Cloud quality depends on the coordination of all upstream parameterization schemes. Aerosol (CCN concentration) uncertainty further amplifies errors by affecting droplet size distributions.

### ❓ How large is the error contribution from surface parameterization? Is vegetation/soil parameter uncertainty underestimated?

✅ **Warner Ch5 partially verified.** The PILPS comparison of 23 LSMs shows complex LSMs aren't necessarily better than simple ones — because parameter uncertainty expands. Soil moisture affects thermal conductivity by two orders of magnitude (dry vs wet soil), and moisture errors are amplified. LDAS requiring months of spin-up shows soil state initial errors decay very slowly. **Conclusion**: The surface is indeed an underestimated error source, but less critical than clouds — surface process time scales (hours to days) are slower than clouds (minutes to hours), so error propagation is slower.

---

## References

- Warner, T.T. (2011). *Numerical Weather and Climate Prediction*. Cambridge University Press.
- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and PV Power Forecasting*. CRC Press.
- Reynolds, O. (1895). On the dynamical theory of incompressible viscous fluids and the determination of the criterion. *Phil. Trans. R. Soc.*

---

*This article is continuously updated with progress through the Warner textbook. Each new chapter adds new reasoning chains and cross-textbook connections.*
