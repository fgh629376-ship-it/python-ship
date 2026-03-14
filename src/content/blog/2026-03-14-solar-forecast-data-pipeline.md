---
title: '光伏功率点预测实战：数据处理到建模的 10 个生死细节'
description: '数据质量决定预测上限，模型只是逼近它。从辐照度分量到 k-index 归一化，从 QC 流程到训练集划分——这些细节做错一个，模型全废。'
pubDate: 2026-03-14
lang: zh
category: solar
series: solar-book
tags: ['光伏预测', '数据处理', '点预测', 'Python', '机器学习', '教材笔记']
---

> 核心参考：
> - 《Solar Irradiance and PV Power Forecasting》Chapter 5 & 7 (Yang & Kleissl, 2024, CRC Press)
> - Pedro & Coimbra, "Assessment of forecasting techniques for solar power production", *Renewable & Sustainable Energy Reviews* (1区Top)
> - Yagli et al., "Automatic hourly solar forecasting using machine learning models", *Renewable & Sustainable Energy Reviews* (1区Top)

光伏功率预测不是"找个模型跑一下"这么简单。**数据处理决定了预测的上限，模型只是逼近它。** 本文整理了从数据到模型的 10 个生死细节，做错任何一个，模型效果都会崩。

## 1. 搞清辐照度分量——GHI ≠ POA

光伏组件输出功率与**面板平面辐照度 (POA/GTI)** 成正比，不是 GHI。

```python
import numpy as np

def closure_equation(ghi: float, dhi: float, zenith_deg: float) -> float:
    """闭合方程：从 GHI 和 DHI 反推 BNI。"""
    zenith_rad = np.radians(zenith_deg)
    cos_z = np.cos(zenith_rad)
    if cos_z <= 0:
        return 0.0
    # GHI = DHI + BNI * cos(Z)
    bni = (ghi - dhi) / cos_z
    return max(0.0, bni)

# 正午：GHI=800, DHI=150, 天顶角=30°
bni = closure_equation(800, 150, 30)
print(f"GHI=800, DHI=150, Z=30° → BNI={bni:.1f} W/m²")

# POA 转置方程（简化版，Perez 模型更准）
def gti_simple(
    bni: float, dhi: float, ghi: float,
    incidence_angle_deg: float, tilt_deg: float,
    albedo: float = 0.2,
) -> float:
    """GTI = beam + diffuse + reflected（简化各向同性模型）。"""
    cos_theta = np.cos(np.radians(incidence_angle_deg))
    tilt_rad = np.radians(tilt_deg)
    beam = bni * max(0, cos_theta)
    diffuse = dhi * (1 + np.cos(tilt_rad)) / 2  # 各向同性假设
    reflected = ghi * albedo * (1 - np.cos(tilt_rad)) / 2
    return beam + diffuse + reflected

poa = gti_simple(bni, 150, 800, incidence_angle_deg=5, tilt_deg=30)
print(f"POA (GTI) = {poa:.1f} W/m²")
print(f"\n⚠️ GHI=800 但 POA={poa:.0f}，差 {abs(poa-800)/800*100:.1f}%")
print("结论：用 GHI 直接预测功率 = 引入系统性偏差")
# 基于模型计算，非实测
```

**教材核心观点**：如果数据允许建模 GTI，就没有理由用 GHI 作为功率预测的直接输入。Perez 转置模型已达到渐近优化水平，不用它就是浪费。

## 2. k-index 归一化——消除天文周期

原始辐照度有强烈的日/季周期，直接喂模型会让模型花大量容量去学"太阳会升起"这种废话。

```python
def clear_sky_index(ghi: np.ndarray, ghi_clear: np.ndarray) -> np.ndarray:
    """
    晴空指数 κ = GHI / GHI_clear
    
    κ ≈ 1.0 → 晴天
    κ < 0.5 → 多云/阴天
    κ > 1.0 → 云增强（短暂超过晴空值）
    """
    # 避免除零（夜间 GHI_clear ≈ 0）
    valid = ghi_clear > 10  # 只处理白天
    kappa = np.ones_like(ghi) * np.nan
    kappa[valid] = ghi[valid] / ghi_clear[valid]
    return kappa

# 模拟一天数据
hours = np.arange(24)
zenith = np.abs(hours - 12) * 7.5  # 简化天顶角

ghi_clear = np.maximum(0, 1000 * np.cos(np.radians(zenith)))
# 加入云层影响
cloud_factor = np.ones(24)
cloud_factor[9:14] = 0.4   # 上午多云
cloud_factor[14:16] = 1.15  # 午后云增强
ghi_actual = ghi_clear * cloud_factor

kappa = clear_sky_index(ghi_actual, ghi_clear)

print(f"{'Hour':>4} {'GHI':>6} {'Clear':>6} {'κ':>6}")
print("-" * 28)
for h in range(6, 19):
    k = f"{kappa[h]:.2f}" if not np.isnan(kappa[h]) else "  N/A"
    print(f"{h:>4}h {ghi_actual[h]:>6.0f} {ghi_clear[h]:>6.0f} {k:>6}")
# 基于模型计算，非实测
```

**坑**：很多论文混淆 clear-sky index (κ) 和 clearness index (kt = GHI/E₀)。kt 的归一化不够彻底——地外辐照度 E₀ 不考虑大气衰减。**用 κ，别用 kt。**

## 3. 数据质量控制 (QC)——垃圾进垃圾出

BSRN（全球最大辐射观测网）的 QC 标准：

```python
from dataclasses import dataclass

@dataclass
class QCResult:
    """单条辐照度数据的 QC 结果。"""
    timestamp: str
    ghi: float
    dhi: float
    bni: float
    zenith: float
    passed: bool
    failed_tests: list[str]

def bsrn_quality_control(
    ghi: float, dhi: float, bni: float,
    zenith_deg: float, e0: float,
) -> QCResult:
    """
    BSRN 物理可能极限 (PPL) 测试。
    
    参考：Long & Shi (2008), J. Atmos. Oceanic Technol.
    """
    cos_z = np.cos(np.radians(zenith_deg))
    failed = []
    
    # Test 1: GHI 范围
    ghi_max = 1.5 * e0 * cos_z**1.2 + 100
    if not (-4 <= ghi <= ghi_max):
        failed.append(f"GHI={ghi:.0f} 超出 [-4, {ghi_max:.0f}]")
    
    # Test 2: DHI 范围
    dhi_max = 0.95 * e0 * cos_z**1.2 + 50
    if not (-4 <= dhi <= dhi_max):
        failed.append(f"DHI={dhi:.0f} 超出 [-4, {dhi_max:.0f}]")
    
    # Test 3: BNI 范围
    if not (-4 <= bni <= e0):
        failed.append(f"BNI={bni:.0f} 超出 [-4, {e0:.0f}]")
    
    # Test 4: 闭合方程一致性
    ghi_calc = dhi + bni * max(cos_z, 0)
    residual = abs(ghi - ghi_calc)
    if residual > 50:
        failed.append(f"闭合残差 {residual:.0f} > 50 W/m²")
    
    # Test 5: 散射比合理性
    if ghi > 50 and dhi / ghi > 1.05:
        failed.append(f"散射比 {dhi/ghi:.2f} > 1.05")
    
    return QCResult(
        timestamp="", ghi=ghi, dhi=dhi, bni=bni,
        zenith=zenith_deg, passed=len(failed) == 0,
        failed_tests=failed,
    )

# 测试
e0 = 1361  # 太阳常数
cases = [
    ("正常晴天", 800, 150, 900, 30),
    ("传感器故障", 1800, 150, 900, 30),  # GHI 异常高
    ("闭合不一致", 800, 500, 900, 30),  # DHI 过高
    ("夜间异常", 50, 10, 0, 95),         # 夜间有值
]

for name, ghi, dhi, bni, z in cases:
    result = bsrn_quality_control(ghi, dhi, bni, z, e0)
    status = "✅" if result.passed else "❌"
    print(f"{status} {name}: GHI={ghi}, DHI={dhi}, BNI={bni}, Z={z}°")
    for f in result.failed_tests:
        print(f"   → {f}")
# 基于模型计算，非实测
```

## 4. 缺失值处理——不能简单填 0

```python
def gap_fill_irradiance(
    series: np.ndarray,
    clear_sky: np.ndarray,
    max_gap_hours: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """
    辐照度缺失值填充策略。
    
    短缺失（≤3h）：用晴空指数插值
    长缺失（>3h）：标记为不可用，不填充
    
    ⚠️ 绝对不能用 0 填充白天缺失值——会引入虚假的"阴天"信号
    """
    filled = series.copy()
    is_filled = np.zeros(len(series), dtype=bool)
    
    # 计算晴空指数
    kappa = np.where(clear_sky > 10, series / clear_sky, np.nan)
    
    # 找缺失段
    is_nan = np.isnan(series)
    gap_start = None
    
    for i in range(len(series)):
        if is_nan[i] and gap_start is None:
            gap_start = i
        elif not is_nan[i] and gap_start is not None:
            gap_len = i - gap_start
            if gap_len <= max_gap_hours:
                # 短缺失：插值 κ 再乘回晴空值
                k_start = kappa[gap_start - 1] if gap_start > 0 else 1.0
                k_end = kappa[i] if not np.isnan(kappa[i]) else k_start
                for j in range(gap_start, i):
                    frac = (j - gap_start + 1) / (gap_len + 1)
                    k_interp = k_start + (k_end - k_start) * frac
                    filled[j] = k_interp * clear_sky[j]
                    is_filled[j] = True
            gap_start = None
    
    return filled, is_filled

print("缺失值处理规则：")
print("  ✅ 短缺失（≤3h）：晴空指数线性插值")
print("  ❌ 长缺失（>3h）：不填充，标记不可用")
print("  🚫 绝对禁止：用 0 填充白天数据")
print("  🚫 绝对禁止：用均值填充（破坏时序结构）")
```

## 5. 训练/测试集划分——时序数据不能 random split

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TimeSeriesSplit:
    """时序数据正确的划分方式。"""
    train_start: str
    train_end: str
    val_start: str
    val_end: str
    test_start: str
    test_end: str

# ✅ 正确：按时间顺序划分
correct = TimeSeriesSplit(
    train_start="2020-01-01", train_end="2022-12-31",
    val_start="2023-01-01",   val_end="2023-06-30",
    test_start="2023-07-01",  test_end="2023-12-31",
)

print("✅ 正确划分（时间顺序）：")
print(f"   训练: {correct.train_start} → {correct.train_end} (3年)")
print(f"   验证: {correct.val_start} → {correct.val_end} (6个月)")
print(f"   测试: {correct.test_start} → {correct.test_end} (6个月)")

print("\n❌ 错误划分（随机打乱）：")
print("   sklearn.model_selection.train_test_split(shuffle=True)")
print("   → 未来数据泄露到训练集，RMSE 虚低 30-50%")
print("   → 这是光伏预测论文最常见的错误之一")

print("\n⚠️ 进阶：滚动窗口验证")
print("   每次用前 N 天训练，预测第 N+1 天")
print("   最接近真实运行场景")
```

## 6. 特征工程——物理知识 > 盲目堆变量

```python
def engineer_solar_features(
    ghi: np.ndarray,
    ghi_clear: np.ndarray,
    temp_air: np.ndarray,
    humidity: np.ndarray,
    hour: np.ndarray,
    day_of_year: np.ndarray,
) -> dict[str, np.ndarray]:
    """
    基于物理因果关系的特征工程。
    
    原则（教材 Ch5）：
    - 每个特征要有物理解释
    - 变量选择要有因果支撑，不是"扔进去看效果"
    - 风速影响温度→影响功率（间接有用）
    - 风速不影响辐射传输→对辐照度预测无用
    """
    features = {}
    
    # 核心特征：晴空指数（消除天文周期）
    valid = ghi_clear > 10
    kappa = np.where(valid, ghi / ghi_clear, 0)
    features["kappa"] = kappa
    
    # 滞后特征（自回归项）
    features["kappa_lag1"] = np.roll(kappa, 1)
    features["kappa_lag2"] = np.roll(kappa, 2)
    features["kappa_lag24"] = np.roll(kappa, 24)  # 昨天同时刻
    
    # 变化率（云的动态信息）
    features["kappa_diff1"] = np.diff(kappa, prepend=kappa[0])
    
    # 日变化位置（编码为周期特征）
    features["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    features["hour_cos"] = np.cos(2 * np.pi * hour / 24)
    
    # 季节位置
    features["doy_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    features["doy_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)
    
    # 气象特征（有物理因果的）
    features["temp_air"] = temp_air        # 影响组件温度→功率
    features["humidity"] = humidity         # 影响大气透过率
    
    return features

print("特征工程规则：")
print("  1. 晴空指数 κ 是最核心特征")
print("  2. 滞后项 κ(t-1), κ(t-24) 提供自回归信息")
print("  3. 时间特征用 sin/cos 编码，不用 raw hour")
print("  4. 每个气象变量要说清物理因果链")
print("  5. Occam's Razor：特征不是越多越好")
```

## 7. Baseline 模型——先跑持续性模型再说

```python
def persistence_forecast(
    kappa_history: np.ndarray,
    horizon_hours: int = 24,
) -> np.ndarray:
    """
    持续性模型：最简单的 baseline。
    
    κ̂(t+h) = κ(t)（晴空指数不变）
    
    实际功率 = κ̂ × P_clear(t+h)
    
    ⚠️ 如果你的"先进"模型打不过持续性模型，
    你的模型大概率有 bug 或者数据有问题。
    """
    return np.full(horizon_hours, kappa_history[-1])

def smart_persistence(
    kappa_history: np.ndarray,
    horizon_hours: int = 24,
    window: int = 3,
) -> np.ndarray:
    """
    Smart persistence：用最近几小时的均值。
    比简单持续性更稳健。
    """
    return np.full(horizon_hours, kappa_history[-window:].mean())

print("Baseline 模型的意义：")
print("  - 持续性模型是所有预测论文的必须 benchmark")
print("  - Forecast Skill = 1 - RMSE_model / RMSE_persistence")
print("  - Skill > 0 才说明模型学到了东西")
print("  - 教材强调：很多'先进'模型在日前尺度打不过持续性")
```

## 8. 评估指标——RMSE 只是开始

```python
def comprehensive_evaluation(
    actual: np.ndarray,
    predicted: np.ndarray,
    persistence: np.ndarray,
    capacity_kw: float,
) -> dict[str, float]:
    """
    完整的预测评估指标集。
    
    参考：Murphy (1993) 三维度
    - 一致性（Consistency）：预测者是否相信自己的预测
    - 质量（Quality）：预测与观测的符合程度
    - 价值（Value）：预测对决策的帮助
    """
    n = len(actual)
    errors = predicted - actual
    
    metrics: dict[str, float] = {}
    
    # 偏差（系统误差方向）
    metrics["mbe"] = float(np.mean(errors))
    metrics["mbe_pct"] = metrics["mbe"] / capacity_kw * 100
    
    # 精度
    metrics["rmse"] = float(np.sqrt(np.mean(errors**2)))
    metrics["mae"] = float(np.mean(np.abs(errors)))
    metrics["nrmse_pct"] = metrics["rmse"] / capacity_kw * 100
    
    # 技巧评分（相对于持续性）
    rmse_pers = float(np.sqrt(np.mean((persistence - actual)**2)))
    metrics["skill"] = 1 - metrics["rmse"] / rmse_pers
    
    # 相关性
    metrics["correlation"] = float(np.corrcoef(actual, predicted)[0, 1])
    
    return metrics

# 示例
np.random.seed(42)
actual = np.maximum(0, 300 * np.sin(np.pi * np.arange(24) / 24) + 
                    np.random.normal(0, 30, 24))
predicted = actual + np.random.normal(5, 25, 24)  # 有偏+有噪声
pers = np.roll(actual, 1)  # 简单持续性

m = comprehensive_evaluation(actual, predicted, pers, capacity_kw=500)
print(f"MBE:   {m['mbe']:+.1f} kW ({m['mbe_pct']:+.1f}%)")
print(f"RMSE:  {m['rmse']:.1f} kW (nRMSE: {m['nrmse_pct']:.1f}%)")
print(f"MAE:   {m['mae']:.1f} kW")
print(f"Skill: {m['skill']:.3f}")
print(f"R:     {m['correlation']:.3f}")
print(f"\n{'Skill > 0 → 比持续性好 ✅' if m['skill'] > 0 else 'Skill ≤ 0 → 不如持续性 ❌'}")
# 基于模型计算，非实测
```

## 9. 常见建模错误与解决方案

```python
COMMON_MISTAKES = {
    "数据泄露": {
        "症状": "测试集 RMSE 异常低（低于持续性 50%+）",
        "原因": "shuffle=True / 未来数据混入训练集 / 特征包含未来信息",
        "解决": "严格按时间划分，检查每个特征的可用时间点",
    },
    "夜间数据处理不当": {
        "症状": "nRMSE 极低（因为夜间全是0=0的'正确'预测）",
        "原因": "评估时包含了夜间数据（GHI=0 预测 0，RMSE=0）",
        "解决": "评估时只用白天数据（zenith < 85°），或用 nRMSE",
    },
    "过度调参": {
        "症状": "验证集效果好，但部署后效果差",
        "原因": "在验证集上反复调参 = 间接在验证集上训练",
        "解决": "验证集只用一次，或用嵌套交叉验证",
    },
    "不考虑预测范围": {
        "症状": "小时级和日前级用同一个模型",
        "原因": "不同 horizon 的可预测性完全不同",
        "解决": "分 horizon 建模：0-6h / 6-24h / 24-72h",
    },
    "忽略晴空归一化": {
        "症状": "模型在夏季好，冬季差（或反之）",
        "原因": "模型在学季节变化而非天气变化",
        "解决": "使用晴空指数 κ 作为输入/输出变量",
    },
}

print("光伏预测建模 5 大常见错误：\n")
for i, (name, info) in enumerate(COMMON_MISTAKES.items(), 1):
    print(f"❌ {i}. {name}")
    print(f"   症状：{info['症状']}")
    print(f"   原因：{info['原因']}")
    print(f"   解决：{info['解决']}")
    print()
```

## 10. 完整 Pipeline 模板

```python
from pathlib import Path
from typing import Any

def solar_forecast_pipeline(
    data_path: Path,
    config: dict[str, Any],
) -> dict[str, float]:
    """
    光伏点预测完整流程模板。
    
    Steps:
    1. 数据加载
    2. QC（质量控制）
    3. 缺失值处理
    4. 晴空指数归一化
    5. 特征工程
    6. 时序划分（train/val/test）
    7. Baseline（持续性模型）
    8. 模型训练
    9. 预测
    10. 评估（含 Skill Score）
    """
    # 伪代码，展示正确的流程顺序
    steps = [
        "1. load_data(path, freq='1h')",
        "2. quality_control(data, method='bsrn_ppl')",
        "3. gap_fill(data, max_gap='3h', method='kappa_interp')",
        "4. compute_clear_sky_index(ghi, ghi_clear)",
        "5. engineer_features(kappa, temp, humidity, wind)",
        "6. temporal_split(train='3y', val='6m', test='6m')",
        "7. baseline = persistence(kappa_test)",
        "8. model.fit(X_train, y_train)",
        "9. predictions = model.predict(X_test)",
        "10. evaluate(actual, predictions, baseline)",
    ]
    
    print("光伏点预测 Pipeline：")
    for step in steps:
        print(f"  → {step}")
    
    return {"status": "template"}

solar_forecast_pipeline(Path("data/"), {})
```

---

## 📋 知识卡片

| 环节 | 致命错误 | 正确做法 |
|------|---------|---------|
| 辐照度输入 | 直接用 GHI | 转为 POA（Perez 转置模型） |
| 归一化 | 用 clearness index kt | 用 clear-sky index κ |
| 质量控制 | 不做 QC | BSRN PPL 测试 + 人工目视 |
| 缺失值 | 填 0 或均值 | κ 插值（短缺失）/ 标记不可用（长缺失） |
| 数据划分 | random split | 严格时间顺序 |
| 特征 | 堆 50 个变量 | 每个变量要有物理因果 |
| Baseline | 不跑 | 持续性模型是必须 benchmark |
| 评估 | 只看 RMSE | MBE + RMSE + Skill Score + 分时段 |
| 时间周期 | raw hour 做特征 | sin/cos 编码 |
| 夜间 | 包含在评估中 | 只评估白天（zenith < 85°） |

> **核心原则**：数据处理花 70% 的时间，模型选择花 20%，调参花 10%。大多数人反过来了。
