---
title: 'Chronos: Forecasting Time Series Like Language — A New Paradigm for Solar Power Prediction?'
description: "Amazon's Chronos tokenizes time series into discrete bins and uses T5 architecture for probabilistic forecasting. What does zero-shot capability mean for solar?"
pubDate: 2026-03-14
lang: en
category: algorithm
series: cross-industry
tags: ['Chronos', 'Foundation Model', 'Time Series', 'Solar Forecasting', 'Transformer', 'Cross-industry']
---

> Paper: Chronos: Learning the Language of Time Series (Ansari et al., 2024)
> Source: Amazon Science, arXiv 2403.07815
> Venue: Transactions on Machine Learning Research (TMLR)

## Core Idea: Time Series = Language

Chronos' insight is simple: **time series is a language**. If GPT can predict the next token, why can't it predict the next timestep's value?

The approach:
1. **Bin** continuous values into discrete tokens
2. Feed into a **T5 language model** architecture
3. Output a **probability distribution**, not a point forecast

```python
import numpy as np

def tokenize_time_series(
    values: np.ndarray,
    n_bins: int = 4096,
    context_length: int = 512,
) -> np.ndarray:
    """
    Chronos core: map continuous values to discrete tokens.
    1. Scale to normalized range (mean scaling)
    2. Uniform binning
    3. Each value becomes an integer token ID
    """
    ctx = values[-context_length:]
    mean_val = np.abs(ctx).mean() + 1e-9
    scaled = ctx / mean_val
    
    bin_edges = np.linspace(-15, 15, n_bins + 1)
    tokens = np.digitize(scaled, bin_edges) - 1
    tokens = np.clip(tokens, 0, n_bins - 1)
    return tokens

# Example: solar power series
np.random.seed(42)
hours = np.arange(72)
solar_power = np.maximum(0, 300 * np.sin(np.pi * (hours % 24) / 24) + 
                          np.random.normal(0, 20, 72))

tokens = tokenize_time_series(solar_power, n_bins=4096)
print(f"Power range: {solar_power.min():.1f} ~ {solar_power.max():.1f} kW")
print(f"Token ID range: {tokens.min()} ~ {tokens.max()}")
# Based on model calculations, not real measurements
```

## Why Not Just Regression?

| Dimension | Traditional ML | Chronos |
|-----------|---------------|---------|
| Output | Single value | **Probability distribution** |
| Training data | Needs domain data | **Cross-domain pretrained**, zero-shot |
| Features | Manual engineering | **Pure time series**, no external features |
| Uncertainty | Needs extra modeling | **Naturally outputs** confidence intervals |

This is huge for solar — Chapter 1 of the textbook repeatedly emphasizes: **good forecasts must be probabilistic**. Chronos naturally outputs probability distributions.

## Architecture

```
Input [x₁, x₂, ..., xₜ]
    ↓ Mean Scaling
    ↓ Binning (4096 discrete tokens)
    ↓ Token Embedding
    ↓ T5 Encoder-Decoder
    ↓ Softmax over bins
    ↓ Sample N trajectories
    ↓ Compute quantiles → probabilistic forecast
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ChronosConfig:
    """Simplified Chronos model config."""
    n_tokens: int = 4096
    context_length: int = 512
    prediction_length: int = 64
    n_samples: int = 20
    model_size: str = "base"

    @property
    def t5_params(self) -> dict[str, int]:
        sizes = {
            "tiny":  {"d_model": 64,  "n_heads": 4,  "n_layers": 2},
            "mini":  {"d_model": 128, "n_heads": 4,  "n_layers": 4},
            "small": {"d_model": 256, "n_heads": 8,  "n_layers": 6},
            "base":  {"d_model": 512, "n_heads": 8,  "n_layers": 8},
            "large": {"d_model": 1024,"n_heads": 16, "n_layers": 12},
        }
        return sizes[self.model_size]

config = ChronosConfig(model_size="small")
print(f"Model: chronos-t5-{config.model_size}")
print(f"Context: {config.context_length} steps ≈ {config.context_length//24} days (hourly)")
```

## Zero-Shot: No Solar Data Needed

Chronos pretrains on **27 public time series datasets** (electricity, traffic, weather, economics), then **zero-shot transfers** to unseen domains — including solar power.

```python
def simulate_chronos_forecast(
    history: np.ndarray,
    horizon: int = 24,
    n_samples: int = 20,
) -> dict[str, np.ndarray]:
    """
    Simulates Chronos probabilistic output format.
    
    Real usage:
    >>> from chronos import ChronosPipeline
    >>> pipeline = ChronosPipeline.from_pretrained("amazon/chronos-t5-small")
    >>> forecast = pipeline.predict(torch.tensor(history), prediction_length=24)
    """
    daily_pattern = np.array([history[i::24].mean() for i in range(24)])
    trajectories = np.zeros((n_samples, horizon))
    for s in range(n_samples):
        noise_scale = history.std() * 0.15
        for h in range(horizon):
            trajectories[s, h] = max(0, daily_pattern[h % 24] + 
                                     np.random.normal(0, noise_scale))
    return {
        "median": np.median(trajectories, axis=0),
        "q10": np.quantile(trajectories, 0.1, axis=0),
        "q90": np.quantile(trajectories, 0.9, axis=0),
        "mean": trajectories.mean(axis=0),
    }

np.random.seed(42)
history = np.maximum(0, 300 * np.sin(np.pi * (np.arange(168) % 24) / 24) + 
                     np.random.normal(0, 30, 168))
forecast = simulate_chronos_forecast(history)

print("24h Probabilistic Forecast:")
for h in [6, 9, 12, 15, 18]:
    print(f"  {h:2d}:00 → {forecast['median'][h]:.0f} kW "
          f"[{forecast['q10'][h]:.0f}, {forecast['q90'][h]:.0f}]")
# Based on model calculations, not real measurements
```

## Best Use: Hybrid with Physics Models

```python
def hybrid_forecast(
    pvlib_forecast: np.ndarray,
    chronos_forecast: dict,
    alpha: float = 0.3,
) -> dict[str, np.ndarray]:
    """Combine physics model (point) + Chronos (uncertainty)."""
    combined = (1 - alpha) * pvlib_forecast + alpha * chronos_forecast["median"]
    relative_width = (chronos_forecast["q90"] - chronos_forecast["q10"]) / (
        chronos_forecast["median"] + 1e-9)
    return {
        "point": combined,
        "q10": combined * (1 - relative_width / 2),
        "q90": combined * (1 + relative_width / 2),
    }
```

---

## 📋 Cheat Sheet

| Dimension | Assessment |
|-----------|-----------|
| 📄 **Paper** | Chronos: Learning the Language of Time Series (Amazon, 2024) |
| 🏢 **Source industry** | NLP / Large Language Models |
| 💡 **Core innovation** | Bin time series → T5 language model → probabilistic output |
| 🎯 **Solar fit** | Strong zero-shot, but lacks weather feature input |
| ⭐ **Transfer value** | ⭐⭐⭐⭐ (4/5) |
| 🔧 **Best use** | Complement pvlib physics model with uncertainty quantification |
| 📦 **Open source** | github.com/amazon-science/chronos-forecasting |

> **Takeaway**: Chronos' biggest value isn't replacing traditional methods — it's providing **cold-start forecasting for new stations** and **uncertainty quantification for physics models**.
