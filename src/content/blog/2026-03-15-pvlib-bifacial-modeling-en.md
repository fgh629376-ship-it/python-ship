---
title: 'pvlib Bifacial Module Modeling — The Physics Behind 10-20% Extra Energy'
description: 'Model bifacial PV modules with pvlib.bifacial: infinite_sheds irradiance calculation, view factor analysis, mismatch loss quantification, with complete code examples'
category: solar
series: pvlib
lang: en
pubDate: '2026-03-15'
tags: ["pvlib", "bifacial", "solar modeling", "view factor", "photovoltaics"]
---

## Bifacial Modules: The New Standard in Solar

In 2024, **bifacial modules accounted for over 70% of global PV installations** (ITRPV 2024 Roadmap). The logic is simple — the backside also generates electricity, yielding 10-20% more energy from the same ground area.

But "how much more" isn't a simple number. It depends on ground albedo, mounting height, row spacing, tilt angle, and even the position along the module. **pvlib's `bifacial` module provides complete physical modeling tools** to precisely quantify each factor's impact.

> ⚠️ All data in this article is based on clear-sky model simulations, not field measurements

---

## 1. Physics of Bifacial Energy Generation

The backside of a bifacial module receives three irradiance components:

1. **Ground-reflected irradiance**: GHI hits the ground, reflects at albedo ρ to the backside — the primary source
2. **Sky diffuse irradiance**: Diffuse light from the sky hemisphere reaching the backside
3. **Direct component**: At low solar elevation (morning/evening), direct beam may reach the backside

Core equation:

```
$$E_{\text{back}} = \rho \times \text{GHI} \times VF_{\text{back→ground}} + \text{DHI} \times VF_{\text{back→sky}}$$
```

Where **VF (View Factor)** quantitatively describes geometric relationships, determining how much ground and sky the backside "sees."

---

## 2. The infinite_sheds Model

pvlib provides the `infinite_sheds` model — assuming infinitely long module arrays (eliminating edge effects) to calculate front and rear irradiance.

### Basic Usage

```python
import pvlib
import pandas as pd

loc = pvlib.location.Location(31.23, 121.47, tz='Asia/Shanghai', altitude=5)
times = pd.date_range('2024-06-21 05:00', '2024-06-21 19:00',
                       freq='10min', tz='Asia/Shanghai')
solpos = loc.get_solarposition(times)
cs = loc.get_clearsky(times)

result = pvlib.bifacial.infinite_sheds.get_irradiance(
    surface_tilt=30,
    surface_azimuth=180,
    solar_zenith=solpos['apparent_zenith'],
    solar_azimuth=solpos['azimuth'],
    gcr=0.4,
    height=1.5,
    pitch=2.5,
    ghi=cs['ghi'], dhi=cs['dhi'], dni=cs['dni'],
    albedo=0.25,
    iam_front=1.0, iam_back=1.0,
)
```

### Return Values

`get_irradiance` returns a 13-column DataFrame including `poa_front`, `poa_back`, `poa_global`, and detailed component breakdowns for both sides.

---

## 3. Key Parameter Sensitivity Analysis

### 3.1 Albedo — The Single Most Impactful Factor

Shanghai summer solstice (June 21), GCR=0.4, tilt=30°:

| Ground Type | Albedo | Rear Daily Irrad. | Bifacial Gain |
|-------------|--------|-------------------|---------------|
| Dark asphalt | 0.15 | 0.77 kWh/m² | **11.3%** |
| Light soil | 0.25 | 1.22 kWh/m² | **18.0%** |
| Light concrete | 0.35 | 1.67 kWh/m² | **24.5%** |
| White gravel | 0.50 | 2.35 kWh/m² | **34.3%** |
| Fresh snow | 0.70 | 3.25 kWh/m² | **47.2%** |

**Takeaway**: Increasing albedo from 0.15→0.50 triples bifacial gain. This is why many plants install white ground covers — **investing a few thousand in ground treatment yields 10-15% more energy, paying back in 2-3 years**.

> Reference: Deline et al. (2020) "Bifacial PV System Performance: Separating Fact from Fiction", IEEE JPVSC. Q1 journal.

### 3.2 GCR — Density vs. Gain Tradeoff

| GCR | Row Spacing(m) | Bifacial Gain |
|-----|----------------|---------------|
| 0.25 | 4.0 | **21.7%** |
| 0.30 | 3.3 | **20.4%** |
| 0.40 | 2.5 | **18.0%** |
| 0.50 | 2.0 | **15.5%** |
| 0.60 | 1.7 | **13.1%** |

**Rule**: Each 0.1 increase in GCR reduces bifacial gain by ~2-3 percentage points.

### 3.3 Monthly Variation — Summer High, Winter Low

Annual clear-sky model for Shanghai (GCR=0.4, albedo=0.25):

**Annual bifacial gain: 11.9%**, with June peak at 17.9% and December minimum at 5.4%.

**Why?** Higher solar elevation in summer means stronger GHI on the ground, thus more reflection to the backside. In winter, low sun angles cause severe inter-row shading.

---

## 4. View Factors — The Power of Geometry

View factors describe the fraction of one surface "visible" to another. pvlib provides 2D analytical solutions:

```python
from pvlib.bifacial import utils

vf_sky = utils.vf_row_sky_2d(surface_tilt=30, gcr=0.4, x=0.5)
vf_gnd = utils.vf_row_ground_2d(surface_tilt=30, gcr=0.4, x=0.5)
```

### Tilt vs. View Factor

| Tilt | VF(→sky) | VF(→ground) |
|------|----------|-------------|
| 0° | 1.0000 | 0.0000 |
| 30° | 0.8999 | 0.0473 |
| 60° | 0.6637 | 0.1857 |
| 90° | 0.4019 | 0.4019 |

At 90° (vertical), both sides see equal amounts of sky and ground — the physical basis for east-west bifacial facades.

### Non-uniformity Along Module Position

At tilt=30°, GCR=0.4, the bottom edge sees 91% more ground than the top edge (VF_gnd: 0.0670 vs 0.0350). This causes **non-uniform backside irradiance** — directly impacting mismatch losses.

---

## 5. Deline Power Mismatch Model

Non-uniform backside irradiance causes current mismatch between cell strings:

```python
loss = pvlib.bifacial.power_mismatch_deline(rmad=0.10, fill_factor=0.79)
# Returns: 0.0462 (4.62% power loss)
```

| RMAD | Power Loss |
|------|-----------|
| 2% | 0.41% |
| 5% | 1.51% |
| 10% | **4.62%** |
| 15% | **9.33%** |
| 20% | **15.64%** |

Below 5% RMAD, losses are negligible. Above 10%, they escalate rapidly (approximately quadratic).

Higher fill factor modules are more sensitive — HJT modules (FF≈0.83) need more careful row spacing design.

> Reference: Deline et al. (2020) "Assessment of Bifacial PV Mismatch Losses", NREL Technical Report.

---

## 6. Engineering Design Guidelines

### Albedo Enhancement Options

| Method | Albedo | Cost | Maintenance |
|--------|--------|------|-------------|
| Natural ground | 0.15-0.25 | Zero | Needs weeding |
| White gravel | 0.40-0.50 | $1-2/m² | Very low |
| White membrane | 0.55-0.70 | $3-5/m² | Needs cleaning |

### Optimal GCR

- **Single-face**: GCR=0.40-0.50
- **Bifacial**: GCR=0.30-0.40 (lower density to unlock bifacial gain)
- **Vertical bifacial**: GCR=0.15-0.25 (agrivoltaics, east-west orientation)

### Bifaciality Factor by Cell Technology

| Technology | Bifaciality |
|-----------|-------------|
| p-PERC | 0.65-0.70 |
| n-TOPCon | 0.80-0.85 |
| HJT | 0.85-0.95 |

> Reference: ITRPV (2024) "International Technology Roadmap for Photovoltaic", 14th Edition.

---

## 7. Key Findings

1. **Albedo is the #1 determinant**: 0.15→0.50, gain jumps from 11% to 34%
2. **Annual bifacial gain ≈ 10-12%** (Shanghai, albedo=0.25), summer max 18%, winter min 5%
3. **Each 0.1 GCR increase costs 2-3% bifacial gain** — bifacial plants need lower density
4. **Mismatch losses negligible at RMAD<5%**, escalate rapidly above 10%
5. **View factors vary along module position**: bottom edge sees 90% more ground than top
6. **Higher FF modules are more mismatch-sensitive**

---

## References

- Deline, C. et al. (2020). "Bifacial PV System Performance." *IEEE Journal of Photovoltaics*, 10(4), 1090-1098. (Q1)
- Stein, J.S. et al. (2021). "Bifacial PV Performance Models." *Solar Energy*, 225, 310-326. (Q1)
- ITRPV (2024). *International Technology Roadmap for Photovoltaic*, 14th Edition.
- pvlib docs: [bifacial module](https://pvlib-python.readthedocs.io/en/stable/reference/bifacial.html)
