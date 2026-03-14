---
title: "5 Unique Features of Solar Forecasting: Why You Can't Copy-Paste Wind/Load Methods"
description: 'Clear-sky models, bimodal κ distribution, 1.5× cloud enhancement, spatio-temporal dependence, Model Chain — what separates solar from other energy forecasting.'
pubDate: 2026-03-14
lang: en
category: solar
series: solar-book
tags: ['Solar Forecasting', 'Clear-sky Model', 'Spatio-temporal', 'Model Chain', 'Textbook Notes']
---

> Reference: *Solar Irradiance and PV Power Forecasting* Ch4 (Yang & Kleissl, 2024)

Solar forecasting is the youngest member of the energy forecasting family. The textbook dedicates an entire chapter to analyzing what makes it unique. **Five physical features must be leveraged — ignore them, and your model loses to Smart Persistence.**

## Feature 1: Clear-sky Models — The Biggest Weapon

We can precisely calculate "how much irradiance there should be without clouds." No other energy domain has this advantage.

**GEFCom2014 fact**: 581 participants, 61 countries. The ONLY team that used a clear-sky model won the championship.

## Feature 2: Bimodal κ Distribution

Clear-sky index distribution is typically bimodal (clear peak ~1.0, cloudy peak ~0.3-0.5). Model with Gaussian mixture, NOT Beta distribution.

## Feature 3: Cloud Enhancement — Upper Bound ≠ Clear-sky Value

GHI can reach ~1.5× clear-sky value due to cloud enhancement. At 1-second resolution, up to ~1900 W/m². Don't clip at clear-sky value.

## Feature 4: Spatio-temporal Dependence

| Method | Effective Range | Grid Requirement |
|--------|----------------|-----------------|
| Sky camera | <30 min | ❌ |
| Satellite | <4 hours | ❌ |
| NWP | 4h → 15 days | ✅ (RTM + DAM) |
| Sensor network | Limited by spacing | ❌ (not scalable) |

**Conclusion**: NWP is the ONLY reliable source for grid-integration forecasting (>4h).

## Feature 5: Model Chain — The Solar Power Curve

5-step physical chain: Solar position → Separation model → Transposition → Temperature → Power.

**Key insight**: Best individual models ≠ best Model Chain. Error propagation is complex; optimize the chain as a whole.

## Lessons from Other Domains

- **Load**: Two-stage modeling (non-black-box + black-box on residuals) → Solar: clear-sky model + ML on κ
- **Wind**: >3h requires NWP, no substitute → Solar: same rule applies
- **Price**: Late start on probabilistic → Solar: do probabilistic from day one

---

> **Core principle**: Solar forecasting's unique advantage is leverageable physics (clear-sky model + Model Chain). Abandoning physics for pure data-driven methods is a massive waste.

---

## Appendix: Ch4 Full Supplement

### Price Forecasting Tricks (Transferable to Solar)

1. **Variance Stabilizing Transform (VST)**: Use `np.arcsinh()` instead of `np.log()` (handles negative values). Solar: useful for cloud-enhancement outliers.
2. **Seasonal decomposition**: Decompose into trend + stochastic, model separately, combine. Solar: residuals after clear-sky removal can be further decomposed.
3. **Calibration window averaging**: Combine predictions from multiple training window lengths instead of picking one "optimal" length. Works for solar too.

### Hierarchical Forecasting

Individual → regional → grid-level forecasts must be **aggregation consistent**. Modern approach: Optimal Reconciliation (Hyndman et al., 2011) uses all hierarchy levels simultaneously, improving both consistency and accuracy.

### Industry Reality

- Probabilistic forecast adoption remains low — grid operators prefer worst-case planning
- **Textbook verdict**: "Purely data-driven single-location methods are seriously handicapped, regardless of complexity"
- **Best path**: Forecast irradiance → post-process → Model Chain → PV power
- Minimum verification: one full calendar year of hourly data, Diebold-Mariano test for significance

### Five Publication Recommendations

1. Literature review: focus on logical flow, not "who did what"
2. Precise terminology: not "short-term" — specify "horizon=24h, resolution=1h"
3. Provide code + data (ostensive > verbal reproducibility)
4. Choose journals with domain expertise, not just impact factor
5. Be persistent — understanding is proportional to time spent
