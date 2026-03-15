---
title: "📖 NWP Textbook Reflections Ch5: Land Surface Processes — The Underestimated Link in the Irradiance Forecast Chain"
description: "Reflections on Chapter 5 of Warner's NWP textbook. The surface energy balance equation R=LE+H+G is the starting point of the Ch4 parameterization cycle. Soil thermal conduction, evapotranspiration, and albedo — these seemingly 'non-atmospheric' processes directly determine boundary layer structure and convection initiation, which in turn affect clouds and irradiance."
pubDate: 2026-03-16
lang: en
category: solar
series: nwp-warner
tags: ["Textbook Reflections", "NWP", "Land Surface Processes", "Energy Balance", "LSM"]
---

> 📖 This post contains reflections on Ch5 of the [Warner NWP Textbook](/textbook/nwp-warner/) | [Back to Textbook Index](/textbook/)

## 1. Why Does This Chapter Matter?

Ch4 established the parameterization cycle: **Radiation → Surface → PBL → Convection → Microphysics → Clouds → Radiation**.

Ch5 focuses on the **starting point** of this cycle — land surface processes. The surface energy balance determines how much energy enters the atmosphere (sensible heat H), how much water vapor enters the atmosphere (latent heat LE), and how much heat is stored in the soil (G). The ratio of these three components directly controls boundary layer development and convection initiation.

**Direct relevance to PV forecasting**: One of the inputs pvlib requires is albedo, and albedo is not a constant — it depends on soil moisture, vegetation type, and solar angle. If the NWP land surface model uses an incorrect albedo, there will be a systematic bias in irradiance predictions.

---

## 2. Surface Energy Balance: The Starting Point of Everything

### Core Equation

$$R = LE + H + G \quad (5.1)$$

- $R$ = Net radiation (sum of all radiation fluxes)
- $LE$ = Latent heat flux (energy consumed by evaporation/transpiration)
- $H$ = Sensible heat flux (energy heating the atmosphere)
- $G$ = Ground heat flux (energy conducted into the soil)

### Decomposition of Net Radiation

$$R = (Q + q)(1 - \alpha) - I_{\uparrow} + I_{\downarrow} \quad (5.2)$$

- $Q$ = Direct solar radiation, $q$ = Diffuse solar radiation
- $\alpha$ = Surface albedo
- $I_{\uparrow}$ = Longwave radiation emitted by the surface ($= \varepsilon\sigma T_g^4$)
- $I_{\downarrow}$ = Downward longwave radiation from the atmosphere

**Key insight**: This equation connects the radiation parameterization from Ch4 (which provides $Q, q, I_{\downarrow}$) with the surface parameterization. The output of the radiation scheme is the input to the land surface model.

### Water Balance Equation

$$\frac{\partial\theta}{\partial t} = P - ET - RO - D \quad (5.3)$$

$\theta$ is volumetric water content, $P$ is precipitation input, $ET$ is evapotranspiration loss, $RO$ is runoff, and $D$ is deep drainage.

---

## 3. Soil Thermal Conduction: Propagation of Temperature Waves

### Heat Diffusion Equation

$$\frac{\partial T_s}{\partial t} = \frac{k_s}{C_s}\frac{\partial^2 T_s}{\partial z^2} \quad (5.6)$$

Thermal diffusivity $\kappa = k_s/C_s$ determines the speed of temperature wave propagation:
- $k_s$ = Thermal conductivity (wet soil >> dry soil >> air)
- $C_s$ = Heat capacity (wet soil > dry soil)

### Temperature Wave Attenuation with Depth

$$(\Delta T)_z = (\Delta T)_0 \exp\left(-z\sqrt{\frac{\pi}{\kappa P}}\right) \quad (5.7)$$

- The diurnal variation wave penetrates approximately 0.5 m
- The annual variation wave penetrates approximately 7 m ($\sqrt{365} \approx 19$ times deeper)

**Relevance to PV**: Soil thermal admittance ($\mu_s = \sqrt{k_s C_s}$) determines the amplitude of the diurnal surface temperature cycle. High thermal admittance (wet soil) → small surface temperature variation → small sensible heat flux → weak boundary layer development → convection less easily triggered. This is why clouds differ significantly between irrigated and arid regions.

---

## 4. Evapotranspiration: Linking the Water Cycle and Energy Cycle

### Two Surface Flux Expressions

Sensible heat: $H = \rho C_p D_H (T_g - T_a) \quad (5.14)$

Latent heat: $LE = \rho L D_W (q_{sat}(T_g) - q_a) \quad (5.15)$

$D_H, D_W$ are transfer coefficients that depend on:
- **Surface roughness** (forest >> grassland >> water surface)
- **Wind shear** (higher wind speed → stronger turbulence → faster transport)
- **Stability** (unstable → buoyancy-driven turbulence → enhanced transport)

### The Special Nature of Vegetation Transpiration

Vegetation draws water from deep soil through roots → transports it to leaves via xylem → releases water vapor through stomata. This process:
- Consumes latent heat at the **leaf surface** (not the soil surface)
- Is controlled by soil water content (below wilting point → transpiration stops)
- Is controlled by stomatal opening/closing (drought/high temperature → stomata close → transpiration decreases → sensible heat increases)

**Chain reaction for PV**: Drought → stomata close → transpiration ↓ → sensible heat ↑ → deeper boundary layer → stronger convection → more afternoon cumulus clouds → more severe afternoon GHI ramp-down

---

## 5. Land Surface Models (LSM): Engineering Implementation

### Hierarchical Structure

23 LSMs participated in PILPS (Project for Intercomparison of Land-surface Parameterization Schemes). Key finding: **complex LSMs are not always better than simple ones** — because complex models require large numbers of parameters that are difficult to accurately obtain.

### Noah LSM (WRF Default)

- 4 soil layers (10 cm, 30 cm, 60 cm, 100 cm)
- Solves equations: 5.1 (energy balance) + 5.3 (water balance) + 5.6 (thermal diffusion) + 5.9 (moisture diffusion) + 5.14/5.15 (surface fluxes)
- Skin temperature $T_g$ solved iteratively

### Land Data Assimilation System (LDAS)

Runs the LSM independently, driven by observational data (rather than model output), to "spin up" the soil temperature and moisture fields. Requires months to years of spin-up to reach equilibrium.

**Engineering lesson**: LDAS and the atmospheric model must use the **same LSM**. Converting soil state between different LSMs is nearly impossible to do accurately — different assumptions, different parameterizations, different grids.

---

## 6. Other Surface Processes

### Ocean Processes
- Short-term forecasts (<1–2 weeks): SST can be assumed constant
- Exception: Hurricanes — strong winds mix and rapidly cool SST; ocean model coupling is required
- Long-term/climate prediction: must couple ocean circulation + sea ice models

### Topographic Forcing
- Smoothed terrain lowers mountain heights → underestimates mountain blocking and gravity wave drag
- Envelope topography: uses "peak height" rather than "grid-averaged height"
- Resolution impact is dramatic: the terrain differences between 30 km vs 3.3 km grids are striking

### Urban Canopy Model (UCM)
- Simple approach: adjust LSM parameters (roughness ↑, albedo ↓, heat capacity ↑, permeable area ↓)
- Complex approach: UCM parameterizes building geometry (street canyon radiation trapping, shadow effects)
- Urban heat island effect on PV: deeper boundary layer above cities → stronger convection → different cloud patterns

---

## 7. Cross-Textbook Connections

| Warner Ch5 Concept | Ch4 Counterpart | Yang Textbook Counterpart | Practical Significance |
|---|---|---|---|
| $R = LE + H + G$ | Radiation parameterization provides R | Ch5.4 clear-sky model provides GHI | Starting point of surface energy partitioning |
| Albedo $\alpha$ | — | Ch4.2 ground reflection | pvlib input parameter, not a constant |
| Soil thermal admittance | Lower boundary condition for PBL parameterization | — | Convective differences between wet and dry surfaces |
| ET-to-sensible heat ratio (Bowen ratio) | Moisture source for convection initiation | — | Indirect driver of afternoon ramp events |
| LDAS spin-up | Initial condition impact (→ Ch6) | — | Months of warm-up needed before use |
| Topographic forcing | — | — | Constraint for WRF resolution selection |

---

## 8. Validating Ch4's Hypotheses

In Ch4, I proposed Hypothesis 1: **"How large is the error contribution from surface parameterization?"**

Warner's answer (partial validation):
- The PILPS comparison of 23 LSMs shows that **complex models are not necessarily better** — parameter uncertainty may be more important than model complexity
- The effect of soil moisture on thermal conductivity spans **two orders of magnitude** (dry vs wet soil) — moisture errors are amplified
- LDAS requires months of spin-up, indicating that initial soil state errors **decay very slowly**

Conclusion: The land surface is indeed an underestimated error source, but not as critical as clouds. Because land surface processes operate on much longer timescales (hours to days) than clouds (minutes to hours), errors propagate more slowly.

---

## References

- Warner, T.T. (2011). *Numerical Weather and Climate Prediction*. Cambridge University Press. Ch5.
- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and PV Power Forecasting*. CRC Press.
- Chen, F. & Dudhia, J. (2001). Coupling an advanced land surface–hydrology model with the Penn State–NCAR MM5 modeling system. *Mon. Wea. Rev.*, 129(4), 569-585.
- Henderson-Sellers, A. et al. (1995). The Project for Intercomparison of Land-surface Parameterization Schemes. *Bull. Amer. Meteor. Soc.*, 76(4), 489-503.
