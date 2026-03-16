---
title: "🔬 Cross-Industry Algorithm Transfer: How Time Series Foundation Models Are Transforming Solar Power Forecasting?"
description: "From NLP's GPT to time series' Chronos/Timer-S1/SPIRIT, foundation models are upending traditional forecasting paradigms. This article deeply analyzes the latest advances from 2024–2026, exploring how they transfer to solar irradiance and power forecasting—zero-shot generalization, multimodal fusion, causal graph attention, and their fundamental limitations."
pubDate: 2026-03-16
lang: en
category: solar
series: cross-industry
tags: ['cross-industry algorithms', 'foundation models', 'Transformer', 'time series forecasting', 'solar forecasting', 'zero-shot learning']
---

## Introduction: Why Should Solar Forecasting Care About "Foundation Models"?

The traditional solar forecasting workflow is: collect 3–5 years of historical data from a target plant → train LSTM/XGBoost/ARIMA → deploy. **What if a new plant has no historical data?** This is the core pain point in the rapid expansion of the solar industry.

Time Series Foundation Models (TSFM) are fundamentally changing this paradigm: pre-train on massive cross-domain time series data → zero-shot transfer to new scenarios. Just as GPT doesn't need to be retrained for every task, the goal of TSFMs is to **forecast without any historical data from the target plant**.

This article, based on the latest papers from 2024–2026, deeply analyzes the progress, methodology, and specific implications for solar forecasting.

---

## 1. The Core Idea of Time Series Foundation Models

### 1.1 Learning from the Success of NLP

The GPT/BERT success formula:
1. **Large-scale pre-training**: Learn universal patterns of language from internet text
2. **General representations**: Learned embeddings encode semantics, syntax, and world knowledge
3. **Downstream fine-tuning / zero-shot**: Transfer to specific tasks

Time series foundation models try to replicate this pattern:
1. **Pre-train on massive time series data**: Stocks, weather, traffic, energy, healthcare...
2. **Learn universal time series patterns**: Trends, seasonality, abrupt changes, autocorrelation, cross-variable dependencies
3. **Zero-shot or few-shot transfer**: Directly forecast time series never seen before

### 1.2 Key Technical Approaches

Current TSFMs fall into three main technical approaches:

| Approach | Representative Model | Core Idea | Pre-training Data |
|----------|---------------------|-----------|-------------------|
| **Tokenization + Transformer** | Chronos (Amazon, 2024) | Quantize time series values into tokens, use T5 architecture for next-token prediction | Multi-domain public datasets |
| **Patch + MoE** | Timer-S1 (Tsinghua, 2026) | Slice time series into patches, 8.3B-parameter MoE, Serial-Token Prediction | TimeBench (1 trillion time points) |
| **Domain-specialized** | SPIRIT (2025) | Target solar irradiance, zero-shot transfer using general models like Lag-Llama/TimesFM | Multi-site irradiance data |

---

## 2. In-Depth Analysis of Key Papers

### 2.1 Timer-S1: A Billion-Scale Time Series Foundation Model

**Source**: Liu et al. (2026), Tsinghua University, GIFT-Eval Leaderboard SOTA

Three core innovations of Timer-S1:

**① Serial-Token Prediction (STP)**

The problem with traditional next-token prediction: forecasting long time series requires autoregressive rolling, with errors accumulating progressively. Timer-S1 proposes STP—serializing prediction targets into multiple token sequences, where each token contains information from a time slice, avoiding rolling inference through serialized computation.

This resolves a fundamental tension: **forecasting accuracy vs. efficiency**. Autoregressive models (GPT-style) are accurate but slow with cumulative errors; direct multi-step output is fast but ignores inter-step dependencies. STP finds a balance between the two.

**② Mixture-of-Experts (MoE)**

8.3B total parameters, but only 0.75B are activated per token. This means:
- The model has sufficient capacity to memorize diverse time series patterns
- Inference-time computation is manageable (only 1/11 of parameters used)
- Different experts may have learned specialized knowledge for different types of time series

**Implications for solar**: Irradiance time series has unique characteristics—strong diurnal periodicity, abrupt changes caused by cloud occlusion, slow seasonal drift. In the MoE architecture, dedicated experts may learn to handle "strong diurnal variation + superimposed abrupt changes"—which is precisely the signature of irradiance.

**③ TimeBench Dataset**

1 trillion time points of pre-training data. A key question: data mixture ratio. If energy/weather data occupies too small a fraction of pre-training data, the model's zero-shot capability for irradiance will be limited.

### 2.2 The Internal Mechanism of Chronos: SAE Dissection

**Source**: Mishra (2026), ICLR 2026 Workshop (TSALM)

This paper uses Sparse Autoencoder (SAE) to dissect the internal representations of Chronos-T5-Large (710M parameters), revealing what TSFMs actually learn:

**Depth-dependent hierarchical structure**:
- **Early encoder layers**: Encode low-level frequency features (periodicity, trends)
- **Middle encoder layers**: Concentrate causally critical **abrupt-change detection features** (max single-feature ΔCRPS = 38.61)
- **Final encoder layers**: Rich but causally unimportant time series concept classification

**The most surprising finding**: Chronos relies on **abrupt-dynamics detection** rather than periodic pattern recognition. Progressively ablating features from the final encoder layer actually **improves** prediction quality.

**Deep implications for solar**:
- The core difficulty of irradiance forecasting is precisely **abrupt changes caused by cloud occlusion** (ramp events)
- If TSFMs are naturally good at detecting abrupt changes, they may be especially suited for irradiance nowcasting
- Periodic patterns (diurnal variation, seasonality) are also important—TSFMs place these in early layers, suggesting they're treated as "simple features"
- Practical implication: When fine-tuning TSFMs, **freezing early layers (preserving periodic detection) + fine-tuning middle layers (adapting to irradiance-specific abrupt change patterns)** may be the optimal strategy

### 2.3 SPIRIT: Zero-Shot Transfer for Solar Irradiance

**Source**: Mishra et al. (2025)

SPIRIT directly validates the zero-shot capability of TSFMs in the solar domain:
- Uses general TSFMs (Lag-Llama, TimesFM, etc.)
- **Zero-shot transfer to new sites, reducing error by approximately 70%** (compared to traditional methods with no historical data)
- Further improvement after fine-tuning

A 70% improvement is very significant, but requires careful interpretation:
- The baseline is the scenario with "absolutely no historical data"—if 1–2 years of data is available, traditional methods may catch up
- Zero-shot performance is highly dependent on the coverage of solar irradiance in pre-training data
- The paper does not compare against physics-based clear-sky + satellite cloud image methods—the latter also requires no historical data

### 2.4 SolarCAST: Spatiotemporal Forecasting with Causal Graphs + Transformer

**Source**: Niu et al. (2025), CIKM 2025

SolarCAST's innovation is achieving spatiotemporal forecasting **using only ground station GHI data** (no sky cameras or satellite imagery needed). Core design:

**Explicit modeling of three types of confounders**:
1. **Observable synchronous variables** (time, site identity) → Embedding module
2. **Hidden synchronous confounders** (regional weather patterns) → Spatiotemporal graph neural network (GNN)
3. **Lagged effects** (cloud clusters moving across stations) → Gated Transformer learning temporal offsets

Reduces error by 25.9% compared to Solcast (a leading commercial service).

**Key insights for solar**:
- **Multi-site collaborative forecasting >> single-site independent forecasting**—irradiance changes at neighboring sites contain cloud motion information
- No expensive sky cameras or high-resolution satellites needed—**public weather station networks suffice**
- Causal graph structure lets the model know "cloud at station A → affects station B in 30 minutes," rather than pure correlation

### 2.5 FusionSF: A Vector Quantization Framework for Multimodal Fusion

**Source**: Ma et al. (2024), Alibaba DAMO Academy

FusionSF fuses three modalities: historical power data + NWP + satellite imagery. The core challenge is **information density mismatch**:
- Historical power: dense, 1-dimensional
- NWP: sparse, multivariate, with systematic biases
- Satellite imagery: high-dimensional, spatially rich

A Vector Quantization (VQ) framework aligns different modalities into a unified discrete representation space—similar in spirit to VQ-VAE.

**Deployed at scale**: 300+ solar plants, total capacity 15GW+. This is not a purely academic paper, but a system validated in production environments.

---

## 3. The Deep Logic of Cross-Industry Transfer

### 3.1 Why May "Universal Time Series Patterns" Exist?

Although time series from different domains have completely different physical mechanisms, they share common **mathematical structure**:
- **Trend + Seasonality + Residual** decomposition (the universality of STL decomposition)
- **Autocorrelation structure** (the core assumption of ARIMA)
- **Abrupt change / changepoint detection** (regime switching)
- **Multi-scale features** (minute-level noise → hourly fluctuations → diurnal variation → seasonal changes)

Foundation model pre-training learns these **domain-independent mathematical structures**.

### 3.2 The Uniqueness of Irradiance Time Series

But irradiance has features rare in other domains:
1. **Hard upper bound constraint**: GHI ≤ extraterrestrial irradiance × clearness index—this physical limit cannot be exceeded
2. **Deterministic component of diurnal variation**: Solar angle is precisely known (astronomical calculation)
3. **Bimodal distribution**: Clear sky vs. overcast, not a continuous Gaussian distribution
4. **Directional spatial correlation**: Cloud clusters move along wind direction, not isotropic

These characteristics mean: **the zero-shot capability of general TSFMs has a ceiling**. The optimal approach may be:
$$\text{Forecast} = \underbrace{\text{Clear-sky model}}_{\text{Physical determinism}} + \underbrace{\text{TSFM}}_{\text{Data-driven residual}}$$

That is, first use pvlib's clear-sky models (Ineichen/Perez) to calculate a deterministic baseline, then use TSFM to predict deviations (clearness index or cloud modification factor). This is completely consistent with the MOS post-processing idea in Warner's textbook Ch13—the physical model provides the baseline, while statistical methods correct the residuals.

### 3.3 Insights from the FutureBoosting Paradigm

The FutureBoosting paper on electricity price forecasting (Qiu et al. 2026) proposes an elegant hybrid framework:
1. A frozen TSFM generates "forecasted features"
2. These are injected into a downstream regression model (XGBoost/LightGBM) as additional input
3. MAE reduction of 30%+

**Transferred to solar**: Use Chronos/Timer-S1 to "enhance" NWP irradiance forecasts—TSFM extracts temporal patterns not captured by NWP, serving as features input to a post-processing regression model. This is more practical, more interpretable, and easier to deploy than end-to-end replacement of NWP.

---

## 4. 2D State Space Models: Mamba's Multivariate Extension

### 4.1 Theoretical Necessity of Permutation Equivariance

VI 2D SSM (Jeong & Suk 2026) points out a widely overlooked problem: **In multivariate time series, there is no natural ordering among variables**.

Traditional methods (including Mamba) arrange multiple variables in a sequence for sequential modeling, implicitly assuming a variable order—but swapping variable order changes prediction results. This is physically unreasonable.

Mathematically, they prove that **any linear 2D state space system satisfying permutation equivariance** naturally decomposes as:
$$\mathbf{x}_{t+1}^{(i)} = \mathbf{A}\mathbf{x}_t^{(i)} + \mathbf{B}\bar{\mathbf{x}}_t$$

where $\mathbf{x}_t^{(i)}$ is the local state of the $i$-th variable, and $\bar{\mathbf{x}}_t$ is the global pooling of all variables. **Local autonomous dynamics + global pooled interaction**—no need for ordered recurrence among variables.

### 4.2 Implications for Multi-Site Solar Forecasting

- In multi-site irradiance forecasting, there is no natural ordering among stations
- SolarCAST uses graph structure (GNN) to handle inter-station relationships; VI 2D SSM uses permutation-invariant aggregation
- The philosophy is consistent: **inter-station interactions should be symmetric** (unless there is an explicit causal direction, such as time lags caused by wind direction)

---

## 5. Practical Roadmap: From Papers to Deployment

Based on the above analysis, solar forecasting projects can introduce cross-industry methods via the following stages:

### Stage 1: Quick Wins (1–2 weeks)
- Use Chronos-T5-Small (8M parameters) as a zero-shot irradiance forecasting baseline
- Compare against traditional persistence forecasting and clear-sky models
- Evaluate: Can zero-shot TSFM outperform clear-sky + persistence when no historical data is available?

### Stage 2: Physics-Enhanced (2–4 weeks)
- Hybrid architecture: clear-sky model + TSFM residual prediction
- FutureBoosting style: TSFM extracts enhanced features from NWP irradiance forecasts → LightGBM post-processing
- Requires paired historical NWP forecasts and ground observation data

### Stage 3: Multi-Site Spatiotemporal (1–2 months)
- SolarCAST-style causal graph Transformer
- Or VI 2D SSM's permutation-equivariant architecture
- Requires synchronized multi-site data

### Stage 4: Fine-Tune TSFM (Long-term)
- Fine-tune Timer-S1 or Chronos on Chinese irradiance data
- Freeze early layers (retain general time series features) + fine-tune middle layers (adapt to irradiance abrupt changes)

---

## 6. Limitations and Sober Reflection

1. **TSFMs don't understand physics**: They don't know solar angles, aerosol optical depth, or cloud microphysics—these must be provided by physical models or NWP
2. **Data bias**: Pre-training data is dominated by finance/traffic/healthcare; irradiance occupies an extremely small fraction—the ceiling on zero-shot capability is real
3. **Computational cost**: Timer-S1 has 8.3B parameters; even with MoE, it requires A100-class GPUs. An RTX 4050 6GB can only run small models (Chronos-Small/Tiny)
4. **Poor interpretability**: The Chronos SAE dissection is an important advance, but far from "understanding what the model is doing"
5. **Not a replacement for NWP**: TSFMs complement NWP (post-processing / residual correction), not replace it

---

## References

1. Liu, Y. et al. (2026). Timer-S1: A Billion-Scale Time Series Foundation Model with Serial Scaling. *arXiv:2603.04791*.
2. Mishra, A. (2026). Dissecting Chronos: Sparse Autoencoders Reveal Causal Feature Hierarchies in Time Series Foundation Models. *ICLR 2026 Workshop (TSALM)*. arXiv:2603.10071.
3. Mishra, A. et al. (2025). SPIRIT: Short-term Prediction of solar IRradIance for zero-shot Transfer learning. *arXiv:2502.10307*.
4. Niu, Y. et al. (2025). Solar Forecasting with Causality: A Graph-Transformer Approach. *CIKM 2025*. arXiv:2509.15481.
5. Ma, Z. et al. (2024). FusionSF: Fuse Heterogeneous Modalities in a Vector Quantized Framework for Robust Solar Power Forecasting. *arXiv:2402.05823*.
6. Qiu, Y. et al. (2026). Regression Models Meet Foundation Models: A Hybrid-AI Approach to Practical Electricity Price Forecasting. *arXiv:2603.06726*.
7. Jeong, S. & Suk, H.-I. (2026). Permutation-Equivariant 2D State Space Models for Multivariate Time Series. *arXiv:2603.08753*.
8. Niu, Y. et al. (2025). Solar Multimodal Transformer: Intraday Solar Irradiance Predictor using Public Cameras and Time Series. *WACV 2025*. arXiv:2503.00250.
9. Lanzilao, L. & Meyer, A. (2026). Intraday spatiotemporal PV power prediction at national scale. *arXiv:2601.04751*.
