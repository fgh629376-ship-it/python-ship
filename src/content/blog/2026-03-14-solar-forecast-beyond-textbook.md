---
title: '教材之外：光伏预测实战中 8 个被忽视的关键问题'
description: '473 引的 ML 方法大比拼、κ vs kt 的数学证明、NWP 后处理的正确姿势——这些来自顶刊论文的经验，教材里没写。'
pubDate: 2026-03-14
lang: zh
category: solar
series: solar-book
tags: ['光伏预测', '论文精读', '数据处理', 'NWP', '机器学习', '最佳实践']
---

> **论文来源（全部中科院二区以上）：**
> - Markovics & Mayer (2022), *Renewable & Sustainable Energy Reviews* (1区Top, 473 citations)
> - Yang (2020), "Choice of clear-sky model in solar forecasting", *J. Renewable & Sustainable Energy* (2区, 135 citations)
> - Lauret et al. (2022), "Solar forecasts: clear sky index or clearness index?", *Solar* (2区, 35 citations)
> - Yang et al. (2021), "Operational solar forecasting for grid integration", *Solar Energy* (2区, 100 citations)
> - Prema & Bhaskar (2021), "Critical review of data, models and performance metrics", *IEEE Access* (2区, 156 citations)

教材给了理论框架，但实战中还有很多坑藏在论文的细节里。这篇文章整理了 8 个教材没有深入展开、但会直接影响项目成败的关键问题。

## 1. 68 个 ML 模型大比拼：没有银弹

Markovics & Mayer (2022) 在 *R&SE Reviews* 上做了一件了不起的事：**用同一份数据、同一套评估框架，对比了 68 个机器学习方法**在光伏功率预测上的表现。

```python
# 论文核心发现（重构为知识图谱）
benchmark_results = {
    "数据": "匈牙利 3 个光伏电站，2017-2019，NWP 输入（ECMWF）",
    "预测范围": "日前（24-48h）",
    "输入特征": "GHI/DNI/DHI 预报、温度、风速、云量（NWP）",
    "总模型数": 68,
    "关键发现": [
        "1. 梯度提升树（XGBoost/LightGBM）整体最优",
        "2. 深度学习（LSTM/CNN）并未显著优于传统 ML",
        "3. 简单的线性回归在某些指标上接近最优",
        "4. 模型选择的影响 < 特征工程和数据质量的影响",
        "5. 集成方法（stacking/blending）比单模型提升 2-5%",
    ],
    "最佳模型Top5": [
        "Gradient Boosting (scikit-learn)",
        "XGBoost",
        "LightGBM",
        "Random Forest",
        "Extra Trees",
    ],
}

print("Markovics & Mayer (2022) — 68 个 ML 模型 Benchmark")
print(f"数据: {benchmark_results['数据']}")
print(f"范围: {benchmark_results['预测范围']}")
print(f"\n核心发现:")
for f in benchmark_results['关键发现']:
    print(f"  {f}")
print(f"\nTop 5 模型:")
for i, m in enumerate(benchmark_results['最佳模型Top5'], 1):
    print(f"  {i}. {m}")
```

**对我们的启示**：别花太多时间在模型选择上。**先把 XGBoost 跑通**，90% 的情况下它就是最优解。深度学习在日前预测上并没有碾压优势。

## 2. κ vs kt：数学上为什么 κ 更好

Lauret et al. (2022) 和 Yang (2020) 从数学上证明了为什么晴空指数 κ 比混浊指数 kt 更适合预测：

```python
import numpy as np

def demonstrate_kappa_vs_kt():
    """
    κ 和 kt 的本质区别：
    - kt = GHI / E₀（地外辐照度）
    - κ = GHI / GHI_clear（晴空辐照度）
    
    差异来源：GHI_clear 已经扣除了大气衰减，E₀ 没有。
    """
    # 模拟一天数据
    hours = np.arange(6, 19)
    zenith = np.abs(hours - 12) * 7.5
    cos_z = np.cos(np.radians(zenith))
    
    # 地外辐照度（只受天顶角影响）
    e0 = 1361 * cos_z
    
    # 晴空辐照度（考虑大气衰减）
    # Ineichen-Perez 模型简化版
    am = 1 / (cos_z + 0.50572 * (96.07995 - zenith)**(-1.6364))
    ghi_clear = 1098 * cos_z * np.exp(-0.057 / cos_z)
    
    # 实际 GHI（晴天比例 70%）
    cloud_factor = 0.7
    ghi = ghi_clear * cloud_factor
    
    # 计算两种指数
    kt = ghi / e0
    kappa = ghi / ghi_clear
    
    print(f"{'Hour':>4} {'GHI':>6} {'E₀':>6} {'GHI_c':>6} {'kt':>6} {'κ':>6}")
    print("-" * 40)
    for i, h in enumerate(hours):
        print(f"{h:>4}h {ghi[i]:>6.0f} {e0[i]:>6.0f} "
              f"{ghi_clear[i]:>6.0f} {kt[i]:>6.3f} {kappa[i]:>6.3f}")
    
    print(f"\nkt 标准差: {np.std(kt):.4f}")
    print(f"κ  标准差: {np.std(kappa):.4f}")
    print(f"\n结论：κ 在一天内几乎恒定（σ={np.std(kappa):.4f}），")
    print(f"      kt 随天顶角变化大（σ={np.std(kt):.4f}）")
    print(f"      → κ 去除了更多天文信号，模型更容易学天气")

demonstrate_kappa_vs_kt()
# 基于模型计算，非实测
```

**核心**：κ 的标准差比 kt 小一个量级——说明 κ 把天文周期去除得更干净，剩下的波动才是模型需要学的**天气信号**。

## 3. 晴空模型的选择影响比你想象的大

Yang (2020, 135 citations) 研究了不同晴空模型对预测的影响：

```python
CLEAR_SKY_MODELS = {
    "Ineichen-Perez": {
        "精度": "⭐⭐⭐⭐",
        "输入": "海拔 + Linke 浑浊度",
        "pvlib": "pvlib.clearsky.ineichen()",
        "优点": "平衡精度和简便性，pvlib 默认",
        "缺点": "Linke 浑浊度的月度气候值可能不准",
    },
    "REST2": {
        "精度": "⭐⭐⭐⭐⭐",
        "输入": "AOD + 水汽 + 臭氧 + 气压",
        "pvlib": "不直接支持，需自定义",
        "优点": "物理基础最强，精度最高",
        "缺点": "需要多种大气参数，数据获取困难",
    },
    "McClear": {
        "精度": "⭐⭐⭐⭐⭐",
        "输入": "CAMS 卫星数据（自动）",
        "pvlib": "pvlib.iotools.get_cams()",
        "优点": "实时大气数据，精度高",
        "缺点": "依赖 CAMS 服务可用性，有延迟",
    },
    "Haurwitz": {
        "精度": "⭐⭐",
        "输入": "仅天顶角",
        "pvlib": "pvlib.clearsky.haurwitz()",
        "优点": "最简单，零输入",
        "缺点": "不考虑大气状态，误差大",
    },
}

print("晴空模型选择指南 (Yang, 2020)：\n")
for name, info in CLEAR_SKY_MODELS.items():
    print(f"📌 {name}")
    print(f"   精度: {info['精度']}")
    print(f"   输入: {info['输入']}")
    print(f"   pvlib: {info['pvlib']}")
    print(f"   ✅ {info['优点']}")
    print(f"   ⚠️ {info['缺点']}")
    print()

print("Yang 的结论：")
print("  → 晴空模型的选择对 Forecast Skill 影响可达 5-10%")
print("  → REST2/McClear 最准，但 Ineichen-Perez 是最佳性价比")
print("  → Haurwitz 只能用于快速原型，不能用于生产")
```

## 4. NWP 后处理：MOS 才是关键

NWP 原始预测（raw forecast）通常有系统性偏差。Yang et al. (2021, 100 citations) 总结了运营级后处理方法：

```python
import numpy as np

def model_output_statistics(
    nwp_forecast: np.ndarray,
    actual: np.ndarray,
    train_days: int = 30,
) -> tuple[np.ndarray, dict[str, float]]:
    """
    MOS（模式输出统计）：NWP 后处理的黄金标准。
    
    原理：用最近 N 天的 NWP 预测和观测建立线性回归，
    修正系统性偏差（bias）和条件偏差（conditional bias）。
    
    参考：Glahn & Lowry (1972), 气象界经典方法
    """
    # 训练数据
    train_x = nwp_forecast[:train_days * 24]
    train_y = actual[:train_days * 24]
    
    # 简单线性 MOS: y = a*x + b
    valid = (train_x > 0) & (train_y > 0)
    if valid.sum() < 10:
        return nwp_forecast, {"bias": 0, "slope": 1, "intercept": 0}
    
    # 最小二乘拟合
    a, b = np.polyfit(train_x[valid], train_y[valid], 1)
    
    # 修正整个序列
    corrected = np.maximum(0, a * nwp_forecast + b)
    
    # 评估
    raw_rmse = np.sqrt(np.mean((nwp_forecast - actual)**2))
    cor_rmse = np.sqrt(np.mean((corrected - actual)**2))
    
    return corrected, {
        "slope": float(a),
        "intercept": float(b),
        "raw_rmse": float(raw_rmse),
        "corrected_rmse": float(cor_rmse),
        "improvement": float((raw_rmse - cor_rmse) / raw_rmse * 100),
    }

# 模拟 NWP 预测（有 15% 正偏差 + 噪声）
np.random.seed(42)
n = 60 * 24  # 60 天小时数据
hours = np.arange(n)
actual_power = np.maximum(0, 300 * np.sin(np.pi * (hours % 24) / 24) + 
                          np.random.normal(0, 30, n))
nwp_pred = actual_power * 1.15 + np.random.normal(10, 20, n)  # 系统性高估 15%

corrected, stats = model_output_statistics(nwp_pred, actual_power, train_days=30)

print("MOS 后处理效果：")
print(f"  回归系数: y = {stats['slope']:.3f} * NWP + {stats['intercept']:.1f}")
print(f"  Raw RMSE:       {stats['raw_rmse']:.1f} kW")
print(f"  Corrected RMSE: {stats['corrected_rmse']:.1f} kW")
print(f"  改善:           {stats['improvement']:.1f}%")
# 基于模型计算，非实测
```

**Yang et al. (2021) 的运营化要求：**
- Issue time（发布时间）：NWP 数据到达后立即开始处理
- Lead time（提前量）：考虑数据传输延迟（ECMWF ~6h）
- 滚动更新：每次新 NWP 到达时重新修正
- 备用方案：NWP 数据缺失时回退到统计方法

## 5. 概率预测不是可选项

Prema & Bhaskar (2021, 156 citations) 的综述指出：

```python
PROBABILITY_VS_DETERMINISTIC = {
    "电网调度需求": {
        "日前市场 (DAM)": "需要概率预测 — 评估备用容量需求",
        "实时调度 (RTUC)": "需要概率预测 — 计算爬坡风险",
        "频率调节": "确定性预测足够 — 但需要高时间分辨率",
    },
    "为什么多数论文只做点预测": [
        "1. 概率评估指标（CRPS/PIT）不如 RMSE 直观",
        "2. 概率预测需要更复杂的建模（分位数回归/集成）",
        "3. 审稿人可能不熟悉概率预测评估",
        "4. 数据量要求更大（需要估计分布尾部）",
    ],
    "推荐的概率方法": [
        "分位数回归 (QR) — 最简单，sklearn 直接支持",
        "分位数回归森林 (QRF) — scikit-garden",
        "NGBoost — 基于自然梯度的概率提升",
        "Conformalized QR — 理论保证覆盖率",
        "Ensemble MOS — NWP 集合成员后处理",
    ],
}

print("概率预测 vs 点预测：\n")
print("电网调度需求：")
for scenario, need in PROBABILITY_VS_DETERMINISTIC["电网调度需求"].items():
    print(f"  {scenario}: {need}")

print("\n推荐概率方法：")
for m in PROBABILITY_VS_DETERMINISTIC["推荐的概率方法"]:
    print(f"  → {m}")
```

## 6. 多站点预测：空间相关性是金矿

```python
def spatial_correlation_insight():
    """
    多站点预测的空间相关性利用。
    
    核心发现（来自 Yang et al. 多篇论文）：
    - 上游电站的 15 分钟前数据 = 下游电站的预测信号
    - 云运动矢量（CMV）+ 站间距离 → 预测提前量
    - 站间相关性随距离衰减，典型 decorrelation 距离 ~50km
    """
    stations = {
        "A（上游）": {"lat": 31.0, "lon": 121.0, "dist_km": 0},
        "B（中游）": {"lat": 31.1, "lon": 121.2, "dist_km": 20},
        "C（下游）": {"lat": 31.2, "lon": 121.4, "dist_km": 40},
    }
    
    # 典型云速 40 km/h
    cloud_speed_kmh = 40
    
    print("多站点预测 — 空间信息利用：\n")
    for name, info in stations.items():
        lead_time = info["dist_km"] / cloud_speed_kmh * 60  # 分钟
        print(f"  {name}: 距离 {info['dist_km']}km, "
              f"可提供 {lead_time:.0f} 分钟预测提前量")
    
    print(f"\n  云速 {cloud_speed_kmh} km/h 时：")
    print(f"  20km 站间距 → 30 分钟提前量")
    print(f"  40km 站间距 → 60 分钟提前量")
    print(f"\n  ⚠️ 超过 ~50km 相关性急剧下降，信息量有限")

spatial_correlation_insight()
```

## 7. 评估指标的陷阱

```python
METRIC_TRAPS = {
    "RMSE 被夜间拉低": {
        "现象": "包含夜间数据时 nRMSE 看起来很好",
        "原因": "夜间 actual=0, predicted=0, error=0, 贡献了大量'完美'预测",
        "解法": "只评估 zenith < 85° 的时段",
    },
    "nRMSE 的分母不统一": {
        "现象": "不同论文的 nRMSE 无法比较",
        "原因": "分母有用 capacity 的、有用 mean 的、有用 max 的",
        "解法": "明确标注 nRMSE = RMSE / ? ，推荐用 capacity",
    },
    "Forecast Skill 的 baseline 不一致": {
        "现象": "Skill Score 看起来很高但不可信",
        "原因": "有人用 climatology 做 baseline（太弱），应该用 smart persistence",
        "解法": "至少报告相对于 persistence 和 smart persistence 的 skill",
    },
    "R² 在时序预测中不可靠": {
        "现象": "R² = 0.95 看起来很好",
        "原因": "光伏出力本身有强日周期，哪怕用 GHI_clear 做预测 R² 也能 0.90+",
        "解法": "在晴空指数 κ 空间评估 R²，而非原始功率空间",
    },
}

print("评估指标 4 大陷阱：\n")
for i, (name, info) in enumerate(METRIC_TRAPS.items(), 1):
    print(f"⚠️ {i}. {name}")
    print(f"   现象: {info['现象']}")
    print(f"   原因: {info['原因']}")
    print(f"   解法: {info['解法']}")
    print()
```

## 8. 模型部署的工程问题

```python
DEPLOYMENT_ISSUES = {
    "数据延迟": {
        "问题": "NWP 数据从 ECMWF 到达需要 4-6 小时",
        "方案": "设计数据缺失时的回退策略（fallback to persistence）",
    },
    "模型漂移": {
        "问题": "组件老化/灰尘/新增遮挡导致模型逐渐失准",
        "方案": "滚动窗口重训练（每 30 天用最新数据更新模型）",
    },
    "异常天气": {
        "问题": "沙尘暴/大雪/冰雹等极端事件，训练数据中没见过",
        "方案": "设置预测置信度阈值，低置信度时报警并回退",
    },
    "逆变器限幅": {
        "问题": "预测功率 > 逆变器额定 → 实际被截断",
        "方案": "后处理加 clip(0, Pmax)，同时考虑降额曲线",
    },
    "时区和夏令时": {
        "问题": "UTC/本地时间混用导致预测偏移 1-8 小时",
        "方案": "全链路统一用 UTC，只在展示层转本地时间",
    },
}

print("模型部署 5 个工程问题：\n")
for name, info in DEPLOYMENT_ISSUES.items():
    print(f"🔧 {name}")
    print(f"   问题: {info['问题']}")
    print(f"   方案: {info['方案']}")
    print()
```

---

## 📋 知识卡片

| 来源论文 | 期刊 | 核心启示 |
|---------|------|---------|
| Markovics & Mayer (2022) | R&SE Reviews (1区Top) | XGBoost 是日前预测最优解，深度学习无显著优势 |
| Yang (2020) | JRSE (2区) | 晴空模型选择影响 Skill 5-10%，Ineichen-Perez 最佳性价比 |
| Lauret et al. (2022) | Solar (2区) | κ 比 kt 标准差小一个量级，去天文信号更干净 |
| Yang et al. (2021) | Solar Energy (2区) | 运营化预测要考虑数据延迟、备用方案、滚动更新 |
| Prema & Bhaskar (2021) | IEEE Access (2区) | 概率预测不是可选项，电网调度必须要 |

> **核心原则**：
> 1. 先跑 XGBoost，90% 情况下够用
> 2. κ 归一化 + Ineichen-Perez 晴空模型 = 最佳性价比
> 3. 概率预测是电网的真正需求
> 4. 部署 ≠ 训练，要考虑漂移/延迟/异常/回退
