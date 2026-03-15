---
title: "From Irradiance to Power: Complete Model Chain + Firm Power Delivery"
description: "Textbook finale — Ch11 physical Model Chain (separation/transposition/reflection/temperature/PV/losses) + Ch12 hierarchical forecasting and firm power delivery"
category: solar
series: solar-book
lang: en
pubDate: '2026-03-15'
tags: ["Model Chain", "pvlib", "hierarchical forecasting", "Firm Power", "solar forecasting"]
---

## 🎉 Textbook Complete! All 12 Chapters Done

Final two chapters of *Solar Irradiance and Photovoltaic Power Forecasting* (Yang & Kleissl, 2024). Ch11: how irradiance becomes electricity. Ch12: how forecasting serves the grid.

---

## Ch11: Irradiance-to-Power Conversion

### Core Argument: Two-Stage > One-Stage

- **One-stage** (ML directly predicts power): needs extensive historical data + retraining per plant → not scalable
- **Two-stage** (forecast irradiance → Model Chain → power): works for new plants → only viable option for grid-scale
- GEFCom2014 winning team was the **only one using clear-sky model** → clear-sky information is always the most important feature

### The Seven Stages of Model Chain

| Stage | Input → Output | Current Best | pvlib Function |
|-------|---------------|-------------|---------------|
| Solar positioning | Time+location → Z, θ | SPA (±0.0003°) | `get_solarposition` |
| Separation | GHI → DHI + BNI | YANG4 | `erbs` / custom |
| Transposition | Horizontal → tilted | Perez 1990 | `perez` |
| Reflection | AOI → effective irrad. | Physical/Martin | `iam.physical` |
| Temperature | Gc+Tamb+W → Tcell | KING (Sandia) | `sapm_cell` |
| PV modeling | Gc+Tcell → Pdc | CEC single-diode | `singlediode` |
| Losses | Pdc → Pac | Inverter+cables+soiling | `inverter.sandia` |

### Separation Modeling Evolution

150+ models exist. YANG4 is current best (confirmed by DM tests at 126 stations):

> ERBS (1982) → BRL (2010) → ENGERER2 (2015, cloud enhancement) → YANG4 (2021, temporal resolution cascade)

**Key insight**: The kt→k mapping is non-injective. Auxiliary variables (Z, AST, clear-sky index) are essential.

### Probabilistic Model Chain

Best workflow (Mayer & Yang, 2023b): **probabilistic weather + ensemble Model Chain + P2P post-processing**. Even for deterministic forecasts, going through probabilistic models yields better results.

---

## Ch12: Hierarchical Forecasting & Firm Power

### Hierarchical Forecasting

Power systems are naturally hierarchical (interconnection → transmission zone → plant → inverter). Independent forecasts at each level → aggregation inconsistency.

**Optimal reconciliation: MinT-shrink**
- Minimizes trace of reconciled error covariance with shrinkage estimator
- CAISO case study: 34 substations, 405 plants → MinT-shrink best in both deterministic and probabilistic verification

### Firm Power: The Ultimate Goal

| Concept | Target | Cost Multiplier |
|---------|--------|----------------|
| Firm Forecasting | Generation matches forecast exactly | ~2x |
| Firm Generation | Generation matches load exactly | ~3x |

**Four Firm Power Enablers:**
1. **Energy storage** — intuitive but expensive alone
2. **Geographical smoothing** — distributed layout reduces total variability
3. **Load shaping** — demand response, adapt consumption to generation
4. **Overbuilding + proactive curtailment** — **counterintuitive but all empirical studies confirm it's necessary**

> You cannot rely on storage alone. Optimal = 1.5x overbuilding + moderate storage + geographical smoothing. California case: firm forecasting premium $100/kW/yr, firm generation premium $205/kW/yr.

### The Bottom Line

**Better forecasts → lower firming costs.** This is why the first 10 chapters spend so much time on forecasting methods and verification — it's not academic exercise, it directly impacts billions of dollars.

---

## Complete Book Summary

| Ch | Topic | One-Line Summary |
|----|-------|-----------------|
| 1-2 | Why forecast + thinking tools | Murphy's three dimensions + Occam's razor |
| 3 | Probabilistic forecasting | Chaos → uncertainty → must quantify |
| 4 | Solar-specific features | Clear-sky model is the greatest weapon |
| 5 | Data handling | QC + normalization + time alignment |
| 6 | Data sources | NWP > satellite > ground, complementary |
| 7 | Base methods | NWP irreplaceable for day-ahead |
| 8 | Post-processing | D2D/P2D/D2P/P2P four quadrants |
| 9 | Deterministic verification | Skill Score + Murphy-Winkler |
| 10 | Probabilistic verification | CRPS + calibration-sharpness paradigm |
| 11 | Model Chain | Seven stages + probabilistic chain |
| 12 | Hierarchical + Firm Power | MinT-shrink + overbuilding + storage |

---

## References

- Yang, D. & Kleissl, J. (2024). CRC Press. Ch. 11-12.
- Mayer, M.J. & Yang, D. (2022, 2023b). *Solar Energy*. (Q1)
- Yang, D. (2022b). *RSER*. (Q1)
- Perez, R. et al. (2020, 2021). *Solar Energy*. (Q1)
- Wickramasuriya, S.L. et al. (2019). *JASA*. (Q1)
