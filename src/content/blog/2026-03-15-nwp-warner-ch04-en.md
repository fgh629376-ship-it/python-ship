---
title: "📖 NWP Textbook Reflections Ch4: Parameterization — The Certain Uncertainty of NWP"
description: "Reflections on Chapter 4 of Warner's NWP textbook. Cloud microphysics, convection, boundary layer, and radiation — the four major parameterization schemes are not independent modules but a deeply coupled system. Cloud is the biggest bottleneck in irradiance forecasting, and cloud quality depends on the coordination of all parameterization schemes."
pubDate: 2026-03-15
lang: en
category: solar
series: nwp-warner
tags: ["Textbook Reflections", "NWP", "Parameterization", "Cloud Microphysics", "Radiative Transfer"]
---

> 📖 This post is a reflection on [Warner NWP Textbook](/textbook/nwp-warner/) Ch4 | [Back to Textbook Index](/textbook/)

## 1. Why Does This Chapter Matter?

Yang's textbook Ch7.1.2 sums it up in one sentence: "Parameterization is the most controversial topic in NWP." Warner uses 52 pages to explain why — not because parameterization theory is immature, but because the **interactions between parameterization schemes** are extraordinarily complex, harder to handle than any single scheme in isolation.

This chapter directly answers the question I was left with after Ch2: **Why does Yang say "cloud microphysics is the bottleneck of irradiance forecasting"?**

---

## 2. The Logical Relationships Among the Four Parameterizations

Parameterizations are not independent modules — they form a **deeply coupled feedback loop**:

```
Solar radiation → Surface heating
    ↓
Surface parameterization → Sensible/latent heat flux
    ↓
Boundary layer parameterization → Turbulent mixing (heat + moisture transported upward)
    ↓
Convection parameterization → Moisture condensation (trigger: CAPE > 0, CIN overcome)
    ↓
Cloud microphysics parameterization → Cloud liquid water / ice content (determines cloud optical properties)
    ↓
Radiation parameterization → Cloud attenuation of radiation (reflection + absorption) → Surface irradiance
    ↓
Loop back to: reduced surface irradiance → reduced surface heating → shallower boundary layer → ...
```

**Core insight**: The radiation scheme itself is not the bottleneck — radiative transfer physics is well established (Beer's Law, Planck function, etc.). The bottleneck lies in the **inputs to the radiation scheme** — the three-dimensional distribution and optical properties of clouds. And cloud quality depends on every upstream parameterization scheme.

---

## 3. Cloud Microphysics: The Smallest Scale Drives the Largest Uncertainty

### Cross-Scale Challenges from Micrometers to Kilometers

Cloud microphysical processes occur at scales from $\mu m$ to $mm$ — 6–9 orders of magnitude smaller than NWP grid cells. Processes that must be parameterized:

- **Condensation**: Water vapor + CCN (cloud condensation nuclei) → cloud droplets (10 μm)
- **Collision-coalescence**: Small droplets hitting large droplets → raindrops (100–1000 μm)
- **Bergeron-Findeisen process**: Ice crystals grow preferentially in supercooled water (saturation vapor pressure over ice < over liquid water)
- **Aggregation / deposition / melting / evaporation**: Phase transitions among solid, liquid, and gas

### Bulk Microphysics Schemes

Operational models use Bulk schemes (rather than the more accurate but expensive Bin schemes):

- **Single-moment**: Predicts only mixing ratio (mass)
- **Double-moment**: Predicts mixing ratio + particle number concentration
- **Triple-moment**: Adds radar reflectivity → gamma distribution shape parameter becomes variable

Five hydrometeor prognostic equations (water vapor $q_v$, cloud water $q_{cw}$, cloud ice $q_{ci}$, snow $q_s$, rain $q_r$), coupled through approximately 20 source/sink terms.

### The "Butterfly Effect" of Aerosols

The number of CCN determines the size distribution of cloud droplets:
- More CCN → more but smaller droplets → greater optical depth (higher albedo ↑) → reduced precipitation efficiency → longer-lived clouds
- Fewer CCN → fewer but larger droplets → smaller optical depth → higher precipitation efficiency → shorter-lived clouds

**Impact on solar PV**: Uncertainty in aerosol concentration propagates directly into uncertainty in irradiance forecasting — this is exactly why ECMWF IFS assimilates CAMS aerosol data.

---

## 4. Convection Parameterization: When and Where Does It Rain?

### Key Concepts

- **CAPE** (Convective Available Potential Energy): Buoyant energy that determines convective intensity
- **CIN** (Convective Inhibition): An energy barrier that prevents convection from initiating
- Convection occurs when there is sufficient CAPE + a mechanism to overcome CIN

### The "Gray Zone" of Resolution

- $\Delta x > 10$ km: Convection must be fully parameterized (traditional global/regional models)
- $\Delta x \approx 1–10$ km: **Gray zone** — convection is partly resolved and partly parameterized, risking "double counting"
- $\Delta x < 1$ km: Convection can be explicitly resolved (cloud-resolving models)

**Direct impact on solar PV**: WRF-Solar commonly uses 3–9 km resolution — squarely in the gray zone! The choice of whether to switch convection parameterization on or off, and which scheme to use, has a huge impact on the simulation of cumulus clouds (which block irradiance).

---

## 5. Boundary Layer Parameterization: The "Invisible Driver" of Irradiance

### Two Classes of Closure Methods

| Method | Principle | Applicable Regime | Representative Scheme |
|--------|-----------|-------------------|-----------------------|
| Local closure | K-theory: flux ∝ local gradient | Stable / neutral stratification | MYJ |
| Non-local closure | Large-eddy driven: flux depends on the thermodynamic structure of the entire boundary layer depth | Convective boundary layer (daytime) | YSU, ACM2 |

**The fatal flaw of K-theory**: In a convective boundary layer, the local gradient may suggest a downward heat flux (because temperature increases slightly with height in the mixed layer), but the actual heat flux is upward (large eddies transport surface heat upward). Local closure can give the **wrong flux direction**.

### A Mathematical View of Reynolds-Averaged Closure

The Reynolds stress term $-\rho\overline{u'w'}$ from Ch2 requires closure — Ch4 provides the specific approaches:
- Zeroth-order closure: $u', v', w'$ are directly parameterized
- First-order closure: $\overline{u'w'}$ is parameterized using K-theory → number of equations equals number of unknowns
- 1.5-order closure: Predicts TKE (turbulent kinetic energy), uses TKE to diagnose K
- Second-order closure: Predicts all second-order moments ($\overline{u'u'}, \overline{u'v'}, \overline{u'w'}, ...$), parameterizes third-order moments

**Higher closure order → more accurate but more expensive**. Operational models mostly use 1.5-order (TKE schemes).

---

## 6. Radiation Parameterization: Most Mature Physics but Most Expensive to Call

### Shortwave vs. Longwave

- **Shortwave** (0.15–3 μm): Solar radiation; requires computing scattering + absorption + reflection
- **Longwave** (3–100 μm): Earth-atmosphere radiation; requires layer-by-layer computation of absorption + emission

### The 100-20-49 Rule

Global annual mean energy budget:
- 100 units of incoming solar radiation
- 31 units reflected back to space (clouds 17 + atmosphere 8 + surface 6)
- 20 units absorbed by atmosphere + clouds
- **49 units absorbed by the surface** → this is the energy source that drives all weather processes

### Computational Bottleneck

Radiative transfer requires integrating Beer's Law over every wavelength — computationally intensive. Solutions:
- **Not called at every time step** (may be computed every 15–30 minutes)
- **Correlated-k method**: A small number of representative wavelengths substitute for full spectral integration
- **Look-up tables (LUT)**: Models such as McClear use this approach to achieve a 5-order-of-magnitude speedup

**Key insight for solar PV**: NWP radiation schemes are not the same as clear-sky models! NWP radiation schemes compute **all-sky** (including clouds) irradiance, whereas clear-sky models only handle cloud-free conditions. Clear-sky models such as REST2 in Yang's textbook achieve much higher accuracy than NWP radiation schemes because they do not need to handle clouds.

---

## 7. Stochastic Parameterization and Cloud Fraction

### Stochastic Parameterization

Traditional parameterization is deterministic — given grid-scale inputs, the output is uniquely determined. In reality, however, the same grid-scale state can correspond to multiple sub-grid states.

Stochastic parameterization adds noise to parameters (e.g., random perturbations to CAPE), more faithfully reflecting sub-grid uncertainty. The scheme of Grell & Devenyi (2002) is already used operationally in the NCEP RUC model.

### Cloud Fraction Parameterization

In a model with $\Delta x = 10–100$ km, a single grid cell may contain both cloudy and clear portions.

Sundqvist et al. (1989): $C = 1 - \sqrt{(1 - RH)/(1 - RH_{crit})}$

Cloud fraction determines the degree of irradiance attenuation computed by the radiation scheme — the difference between 50% cloud fraction and 100% cloud fraction is enormous.

---

## 8. Cross-Textbook Connections

| Warner Ch4 Concept | Yang Textbook Counterpart | Practical Significance |
|--------------------|--------------------------|------------------------|
| Interaction among parameterization schemes | Ch7.1.2 overview | "Holism" matters more than "reductionism" |
| 5 hydrometeor equations in cloud microphysics | Ch7.1.2 "cloud is the bottleneck" | Cloud liquid water → optical depth → irradiance |
| CAPE/CIN and convective triggering | — | Appearance/dissipation of cumulus determines ramp events |
| The gray-zone problem | Ch4.6.1 WRF-Solar | Must choose convection scheme carefully at 3–9 km resolution |
| Flaw of K-theory | — | Daytime PBL must use non-local scheme |
| Radiation ≠ clear-sky model | Ch5.4 REST2/McClear | NWP radiation = all-sky; clear-sky model = cloud-free |
| Aerosol → cloud → irradiance | Ch7.1.2 | Why ECMWF assimilates CAMS aerosol data |
| Stochastic parameterization | Ch3.3.1 ensemble type ③ | Corresponds to "stochastic parameterization ensemble" |

---

## References

- Warner, T.T. (2011). *Numerical Weather and Climate Prediction*. Cambridge University Press. Ch4.
- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and PV Power Forecasting*. CRC Press. Ch7.1.
- Stensrud, D.J. (2007). *Parameterization Schemes: Keys to Understanding Numerical Weather Prediction Models*. Cambridge University Press.
- Grell, G.A. & Devenyi, D. (2002). A generalized approach to parameterizing convection combining ensemble and data assimilation techniques. *Geophys. Res. Lett.*, 29(14).
