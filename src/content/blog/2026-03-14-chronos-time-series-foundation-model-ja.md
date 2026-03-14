---
title: 'Chronos：大規模言語モデルの手法で時系列予測 — 太陽光発電予測の新パラダイム？'
description: 'Amazonの Chronos は時系列を離散トークンに変換し、T5アーキテクチャで確率的予測を実現。ゼロショット能力は太陽光にとって何を意味するか？'
pubDate: 2026-03-14
lang: ja
category: algorithm
series: cross-industry
tags: ['Chronos', 'Foundation Model', '時系列予測', '太陽光発電予測', 'Transformer', '異業種アルゴリズム']
---

> 論文：Chronos: Learning the Language of Time Series (Ansari et al., 2024)
> 出典：Amazon Science, arXiv 2403.07815
> 掲載：Transactions on Machine Learning Research (TMLR)

## 核心思想：時系列 = 言語

Chronosの洞察はシンプル：**時系列は一種の言語**である。GPTが次のトークンを予測できるなら、次の時間ステップの値も予測できるはず。

手順：
1. 連続値を**ビン分割して離散化**（トークン化）
2. **T5言語モデル**アーキテクチャに入力
3. **確率分布**を出力（点予測ではない）

```python
import numpy as np

def tokenize_time_series(
    values: np.ndarray,
    n_bins: int = 4096,
    context_length: int = 512,
) -> np.ndarray:
    """
    Chronos コア：連続値を離散トークンにマッピング。
    1. 正規化（平均スケーリング）
    2. 均一ビン分割
    3. 各値が整数トークンIDに変換
    """
    ctx = values[-context_length:]
    mean_val = np.abs(ctx).mean() + 1e-9
    scaled = ctx / mean_val
    
    bin_edges = np.linspace(-15, 15, n_bins + 1)
    tokens = np.digitize(scaled, bin_edges) - 1
    return np.clip(tokens, 0, n_bins - 1)

# 例：太陽光発電出力系列
np.random.seed(42)
hours = np.arange(72)
solar_power = np.maximum(0, 300 * np.sin(np.pi * (hours % 24) / 24) + 
                          np.random.normal(0, 20, 72))

tokens = tokenize_time_series(solar_power, n_bins=4096)
print(f"出力範囲: {solar_power.min():.1f} ~ {solar_power.max():.1f} kW")
print(f"Token ID範囲: {tokens.min()} ~ {tokens.max()}")
# モデル計算に基づく、実測データではない
```

## なぜ回帰ではないのか？

| 比較 | 従来の回帰 | Chronos |
|------|-----------|---------|
| 出力 | 単一数値 | **確率分布** |
| 訓練データ | ドメインデータ必須 | **クロスドメイン事前学習**、ゼロショット |
| 特徴量 | 手動設計 | **純時系列**、外部特徴不要 |
| 不確実性 | 追加モデリング必要 | **自然に出力** |

教科書の第1章が繰り返し強調：**良い予測は確率的でなければならない**。Chronosは自然に確率分布を出力する。

## アーキテクチャ

```
入力 [x₁, x₂, ..., xₜ]
    ↓ 平均スケーリング
    ↓ ビン分割（4096離散トークン）
    ↓ トークン埋め込み
    ↓ T5 エンコーダ・デコーダ
    ↓ ビン上のSoftmax
    ↓ N回サンプリング → N本の未来軌跡
    ↓ 分位数計算 → 確率的予測区間
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ChronosConfig:
    """簡略版Chronosモデル設定。"""
    n_tokens: int = 4096
    context_length: int = 512
    prediction_length: int = 64
    n_samples: int = 20
    model_size: str = "base"

    @property
    def t5_params(self) -> dict[str, int]:
        sizes = {
            "tiny":  {"d_model": 64,  "n_heads": 4,  "n_layers": 2},
            "small": {"d_model": 256, "n_heads": 8,  "n_layers": 6},
            "base":  {"d_model": 512, "n_heads": 8,  "n_layers": 8},
            "large": {"d_model": 1024,"n_heads": 16, "n_layers": 12},
        }
        return sizes[self.model_size]

config = ChronosConfig(model_size="small")
print(f"コンテキスト: {config.context_length}ステップ ≈ {config.context_length//24}日")
```

## ゼロショット予測

Chronosは**27の公開時系列データセット**で事前学習し、太陽光発電を含む未知のドメインに**ゼロショット転移**する。

```python
def simulate_chronos_forecast(
    history: np.ndarray,
    horizon: int = 24,
    n_samples: int = 20,
) -> dict[str, np.ndarray]:
    """Chronosの確率的予測出力をシミュレーション。"""
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
    }

np.random.seed(42)
history = np.maximum(0, 300 * np.sin(np.pi * (np.arange(168) % 24) / 24) + 
                     np.random.normal(0, 30, 168))
forecast = simulate_chronos_forecast(history)

print("24時間確率的予測：")
for h in [6, 9, 12, 15, 18]:
    print(f"  {h:2d}:00 → {forecast['median'][h]:.0f} kW "
          f"[{forecast['q10'][h]:.0f}, {forecast['q90'][h]:.0f}]")
# モデル計算に基づく、実測データではない
```

## 最適な使い方：物理モデルとの融合

```python
def hybrid_forecast(
    pvlib_forecast: np.ndarray,
    chronos_forecast: dict,
    alpha: float = 0.3,
) -> dict[str, np.ndarray]:
    """物理モデル（点予測）+ Chronos（不確実性）の融合。"""
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

## 📋 知識カード

| 次元 | 評価 |
|------|------|
| 📄 **論文** | Chronos (Amazon, 2024, TMLR) |
| 🏢 **出身業界** | NLP / 大規模言語モデル |
| 💡 **核心革新** | 時系列のビン分割 → T5言語モデル → 確率的予測 |
| ⭐ **借鑑価値** | ⭐⭐⭐⭐（4/5） |
| 🔧 **最適用途** | pvlib物理モデルに不確実性定量化を補完 |
| 📦 **オープンソース** | github.com/amazon-science/chronos-forecasting |

> **PVプロジェクトへの教訓**：Chronosの最大価値は既存手法の代替ではなく、**新設発電所のコールドスタート予測**と**物理モデルへの不確実性定量化の補完**にある。
