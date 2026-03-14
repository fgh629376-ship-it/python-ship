---
title: 'Chronos：用大语言模型的方式做时序预测，光伏功率预测的新范式？'
description: 'Amazon 的 Chronos 把时间序列当语言处理——分词、T5 架构、概率输出。零样本预测能力对光伏场景意味着什么？'
pubDate: 2026-03-14
lang: zh
category: algorithm
series: cross-industry
tags: ['Chronos', 'Foundation Model', '时序预测', '光伏功率预测', 'Transformer', '跨行业算法']
---

> 论文：Chronos: Learning the Language of Time Series (Ansari et al., 2024)
> 来源：Amazon Science, arXiv 2403.07815
> 会议：Transactions on Machine Learning Research (TMLR)

## 核心思想：时间序列 = 语言

Chronos 的核心洞察很简单：**时间序列就是一种语言**。既然 GPT 能预测下一个 token，为什么不能预测下一个时间步的值？

做法：
1. 把连续的数值**分桶离散化**（tokenize）
2. 喂进 **T5 语言模型**架构
3. 输出**概率分布**，不是单点预测

```python
import numpy as np
import matplotlib
matplotlib.use('Agg')

# 模拟 Chronos 的分桶思路
def tokenize_time_series(
    values: np.ndarray,
    n_bins: int = 4096,
    context_length: int = 512,
) -> np.ndarray:
    """
    Chronos 核心：把连续值映射到离散 token。
    
    步骤：
    1. 缩放到 [0, 1] 范围（基于上下文窗口的均值和标准差）
    2. 均匀分桶
    3. 每个值变成一个整数 token ID
    """
    # 归一化（Chronos 用 mean scaling）
    ctx = values[-context_length:]
    mean_val = np.abs(ctx).mean() + 1e-9
    scaled = ctx / mean_val
    
    # 分桶：[-15, 15] 范围均匀划分
    bin_edges = np.linspace(-15, 15, n_bins + 1)
    tokens = np.digitize(scaled, bin_edges) - 1
    tokens = np.clip(tokens, 0, n_bins - 1)
    
    return tokens

# 示例：光伏功率序列
np.random.seed(42)
hours = np.arange(72)
# 模拟三天光伏出力（日周期 + 噪声）
solar_power = np.maximum(0, 300 * np.sin(np.pi * (hours % 24) / 24) + 
                          np.random.normal(0, 20, 72))

tokens = tokenize_time_series(solar_power, n_bins=4096)
print(f"原始功率范围: {solar_power.min():.1f} ~ {solar_power.max():.1f} kW")
print(f"Token ID 范围: {tokens.min()} ~ {tokens.max()}")
print(f"Token 序列长度: {len(tokens)}")
print(f"\n前12小时 Token IDs: {tokens[:12]}")
# 基于模型计算，非实测
```

## 为什么不直接回归？

传统 ML 预测（XGBoost/LSTM）是**回归思路**——输入特征，输出一个数。Chronos 换了个玩法：

| 对比维度 | 传统回归 | Chronos |
|---------|---------|---------|
| 输出 | 单个数值 | **概率分布**（多个分位数） |
| 训练数据 | 需要目标领域数据 | **跨领域预训练**，零样本迁移 |
| 特征工程 | 需要手动构造 | **纯时序输入**，无需外部特征 |
| 不确定性 | 需要额外建模 | **天然输出**置信区间 |

这对光伏预测的意义巨大——教材 Chapter 1 反复强调：**好的预测必须是概率性的**。Chronos 天然输出概率分布。

## 架构细节

```
输入时序 [x₁, x₂, ..., xₜ]
    ↓ Mean Scaling（均值归一化）
    ↓ Binning（分桶离散化，4096 bins）
    ↓ Token Embedding
    ↓ T5 Encoder-Decoder
    ↓ Softmax over bins（输出每个桶的概率）
    ↓ 采样 N 次 → N 条未来轨迹
    ↓ 统计分位数 → 概率预测区间
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ChronosConfig:
    """Chronos 模型配置（简化版）。"""
    n_tokens: int = 4096           # 分桶数（离散化精度）
    context_length: int = 512      # 上下文窗口（输入长度上限）
    prediction_length: int = 64    # 预测步长上限
    n_samples: int = 20            # 采样轨迹数（越多越准）
    model_size: str = "base"       # tiny/mini/small/base/large

    @property
    def t5_params(self) -> dict[str, int]:
        """T5 架构参数。"""
        sizes = {
            "tiny":  {"d_model": 64,  "n_heads": 4,  "n_layers": 2},
            "mini":  {"d_model": 128, "n_heads": 4,  "n_layers": 4},
            "small": {"d_model": 256, "n_heads": 8,  "n_layers": 6},
            "base":  {"d_model": 512, "n_heads": 8,  "n_layers": 8},
            "large": {"d_model": 1024,"n_heads": 16, "n_layers": 12},
        }
        return sizes[self.model_size]

config = ChronosConfig(model_size="small")
print(f"模型: chronos-t5-{config.model_size}")
print(f"参数: d_model={config.t5_params['d_model']}, "
      f"heads={config.t5_params['n_heads']}, "
      f"layers={config.t5_params['n_layers']}")
print(f"分桶数: {config.n_tokens} (精度: {30/config.n_tokens:.4f})")
print(f"上下文: {config.context_length} 步 ≈ {config.context_length/24:.0f} 天（小时级数据）")
```

## 零样本预测：没见过光伏数据也能预测

Chronos 在 **27 个公开时序数据集**上预训练（电力、交通、天气、经济等），然后**零样本迁移**到未见过的领域。

这意味着：**不需要任何光伏训练数据，直接预测光伏功率**。

```python
def simulate_chronos_forecast(
    history: np.ndarray,
    horizon: int = 24,
    n_samples: int = 20,
) -> dict[str, np.ndarray]:
    """
    模拟 Chronos 的概率预测输出。
    
    真实使用时只需：
    >>> from chronos import ChronosPipeline
    >>> pipeline = ChronosPipeline.from_pretrained("amazon/chronos-t5-small")
    >>> forecast = pipeline.predict(torch.tensor(history), prediction_length=24)
    
    这里用统计方法近似模拟其输出格式。
    """
    # 提取日周期模式
    daily_pattern = np.array([
        history[i::24].mean() for i in range(24)
    ])
    
    # 生成 n_samples 条采样轨迹
    trajectories = np.zeros((n_samples, horizon))
    for s in range(n_samples):
        noise_scale = history.std() * 0.15  # 不确定性
        for h in range(horizon):
            hour_of_day = h % 24
            base = daily_pattern[hour_of_day]
            trajectories[s, h] = max(0, base + np.random.normal(0, noise_scale))
    
    # 计算分位数
    return {
        "median": np.median(trajectories, axis=0),
        "q10": np.quantile(trajectories, 0.1, axis=0),
        "q90": np.quantile(trajectories, 0.9, axis=0),
        "mean": trajectories.mean(axis=0),
        "samples": trajectories,
    }

# 用 7 天历史预测未来 24 小时
np.random.seed(42)
hours = np.arange(168)
history = np.maximum(0, 300 * np.sin(np.pi * (hours % 24) / 24) + 
                     np.random.normal(0, 30, 168))

forecast = simulate_chronos_forecast(history, horizon=24, n_samples=20)

print("未来 24 小时预测（概率）：")
print(f"{'Hour':>4} {'Median':>8} {'P10':>8} {'P90':>8} {'区间宽':>8}")
print("-" * 40)
for h in range(0, 24, 3):
    width = forecast['q90'][h] - forecast['q10'][h]
    print(f"{h:>4}h {forecast['median'][h]:>8.1f} {forecast['q10'][h]:>8.1f} "
          f"{forecast['q90'][h]:>8.1f} {width:>8.1f}")
# 基于模型计算，非实测
```

## 光伏场景借鉴分析

### ✅ 优势
1. **零样本能力**：新电站上线当天就能预测，不需要历史数据积累
2. **概率输出**：天然给出不确定性区间，电网调度直接可用
3. **多尺度**：15 分钟/小时/日级数据都能处理
4. **开源可用**：`pip install chronos-forecasting`，模型在 HuggingFace

### ⚠️ 局限
1. **纯时序输入**：不接受外部特征（温度、辐照度预报），而光伏功率高度依赖气象
2. **分桶精度**：4096 bins，对光伏功率的绝对值精度约 ±0.7%
3. **上下文长度**：512 步 = 21 天（小时级），可能不够捕捉季节模式
4. **计算开销**：T5-large 参数量 ~710M，推理需要 GPU

### 🎯 最佳使用方式

不要拿 Chronos **替代**物理模型，而是**互补**：

```python
def hybrid_forecast(
    pvlib_forecast: np.ndarray,    # 物理模型预测
    chronos_forecast: dict,        # Chronos 概率预测
    alpha: float = 0.3,           # Chronos 权重
) -> dict[str, np.ndarray]:
    """
    混合预测：物理模型提供基线，Chronos 提供不确定性。
    
    思路：
    - 确定性预测用物理模型（有气象输入，更准）
    - 不确定性区间用 Chronos（天然概率输出）
    - 加权组合 median
    """
    combined_median = (1 - alpha) * pvlib_forecast + alpha * chronos_forecast["median"]
    
    # 不确定性区间：用 Chronos 的相对宽度叠加到物理预测上
    relative_width = (chronos_forecast["q90"] - chronos_forecast["q10"]) / (
        chronos_forecast["median"] + 1e-9
    )
    
    return {
        "point": combined_median,
        "q10": combined_median * (1 - relative_width / 2),
        "q90": combined_median * (1 + relative_width / 2),
    }

# 示例
pvlib_pred = np.maximum(0, 280 * np.sin(np.pi * np.arange(24) / 24))
hybrid = hybrid_forecast(pvlib_pred, forecast, alpha=0.3)
print("混合预测结果：")
for h in [6, 9, 12, 15, 18]:
    print(f"  {h:2d}:00 → {hybrid['point'][h]:.0f} kW "
          f"[{hybrid['q10'][h]:.0f}, {hybrid['q90'][h]:.0f}]")
# 基于模型计算，非实测
```

## 与其他时序基础模型对比

| 模型 | 来源 | 架构 | 概率输出 | 零样本 | 开源 |
|------|------|------|---------|-------|------|
| **Chronos** | Amazon | T5 (Enc-Dec) | ✅ | ✅ | ✅ |
| TimesFM | Google | Decoder-only | ❌ | ✅ | ✅ |
| MOIRAI | Salesforce | Masked Enc | ✅ | ✅ | ✅ |
| Lag-Llama | 学术 | Llama | ✅ | ✅ | ✅ |
| iTransformer | 清华 | Inverted Attn | ❌ | ❌ | ✅ |

Chronos 的独特优势：**唯一一个把连续值分桶成离散 token 的方法**，把时序预测完全转化为语言建模问题。

---

## 📋 知识卡片

| 维度 | 评估 |
|------|------|
| 📄 **论文** | Chronos: Learning the Language of Time Series (Amazon, 2024) |
| 🏢 **来源行业** | NLP / 大语言模型 |
| 💡 **核心创新** | 时间序列分桶离散化 → T5 语言模型 → 概率预测 |
| 🎯 **光伏适配** | 零样本能力强，但缺乏气象特征输入 |
| ⭐ **借鉴价值** | ⭐⭐⭐⭐（4/5）|
| 🔧 **最佳用法** | 与 pvlib 物理模型互补，Chronos 提供不确定性量化 |
| 📦 **开源地址** | github.com/amazon-science/chronos-forecasting |
| 🚀 **一句话** | 把时间序列当语言，用 GPT 的方式做预测 |

> **对光伏项目的启示**：Chronos 最大的价值不是替代传统方法，而是**为新电站提供冷启动预测**和**为物理模型补充不确定性量化**。当 BOSS 的项目启动时，可以用 pvlib 做点预测 + Chronos 做概率区间，两者结合形成完整的概率预测方案。
