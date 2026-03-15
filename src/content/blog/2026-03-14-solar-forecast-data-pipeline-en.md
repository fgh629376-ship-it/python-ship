---
title: 'Solar Power Point Forecasting: 10 Make-or-Break Details from Data to Model'
description: 'Data quality determines the forecasting ceiling; models just approach it. From irradiance components to k-index normalization, QC to train/test splits — get one wrong, your model is useless.'
pubDate: 2026-03-14
lang: en
category: solar
series: solar-book
tags: ['Solar Forecasting', 'Data Processing', 'Point Forecast', 'Python', 'Machine Learning', 'Textbook Notes']
---

> Core references:
> - *Solar Irradiance and PV Power Forecasting* Ch5 & 7 (Yang & Kleissl, 2024, CRC Press)
> - Pedro & Coimbra, *Renewable & Sustainable Energy Reviews* (Q1 Top)
> - Yagli et al., *Renewable & Sustainable Energy Reviews* (Q1 Top)

Solar power forecasting isn't "pick a model and run it." **Data processing determines the ceiling; models just approach it.** Here are 10 critical details — get any one wrong, and your model falls apart.

## 1. Know Your Irradiance Components — GHI ≠ POA

PV output is proportional to **plane-of-array irradiance (POA/GTI)**, not GHI.

```python
import numpy as np

def closure_equation(ghi: float, dhi: float, zenith_deg: float) -> float:
    """Closure equation: derive BNI from GHI and DHI."""
    cos_z = np.cos(np.radians(zenith_deg))
    if cos_z <= 0:
        return 0.0
    bni = (ghi - dhi) / cos_z
    return max(0.0, bni)

bni = closure_equation(800, 150, 30)
print(f"GHI=800, DHI=150, Z=30° → BNI={bni:.1f} W/m²")
# Based on model calculations, not real measurements
```

**Textbook rule**: If data permits GTI modeling, there is NO reason to use GHI as direct input for power forecasting.

## 2. k-index Normalization — Remove Astronomical Cycles

```python
def clear_sky_index(ghi: np.ndarray, ghi_clear: np.ndarray) -> np.ndarray:
    """κ = GHI / GHI_clear — removes diurnal/seasonal cycles."""
    valid = ghi_clear > 10
    kappa = np.ones_like(ghi) * np.nan
    kappa[valid] = ghi[valid] / ghi_clear[valid]
    return kappa
```

**Trap**: Many papers confuse clear-sky index ($\kappa$) with clearness index (kt = GHI/E₀). kt's normalization is incomplete — use κ.

## 3-10. (See Chinese version for full details)

Key rules summarized:
- **QC**: Use BSRN PPL tests (Long & Shi, 2008)
- **Gap filling**: $\kappa$ interpolation for short gaps, mark long gaps as unavailable. NEVER fill 0
- **Train/test split**: Strictly chronological. NEVER shuffle time series data
- **Features**: Every variable needs physical causal justification
- **Baseline**: Persistence model is mandatory benchmark
- **Evaluation**: MBE + RMSE + Skill Score, daytime only (zenith < 85°)
- **Common mistakes**: Data leakage, nighttime inflation, over-tuning, ignoring forecast horizon

---

## 📋 Cheat Sheet

| Step | Fatal Mistake | Correct Approach |
|------|--------------|-----------------|
| Irradiance | Use GHI directly | Convert to POA (Perez model) |
| Normalization | Clearness index kt | Clear-sky index $\kappa$ |
| QC | Skip it | BSRN PPL tests + visual inspection |
| Missing data | Fill with 0 or mean | $\kappa$ interpolation / mark unavailable |
| Data split | Random split | Strict temporal order |
| Features | Stack 50 variables | Physical causality required |
| Baseline | Skip | Persistence is mandatory |
| Evaluation | RMSE only | MBE + RMSE + Skill Score |

> **Core principle**: Spend 70% of time on data, 20% on model selection, 10% on tuning. Most people do it backwards.
