---
title: '光伏预测的五大独特特征：为什么它不能照搬风力/负荷预测方法'
description: '晴空模型、κ分布双峰、云增强1.5倍、时空依赖性、Model Chain——光伏预测与其他能源预测的本质区别。'
pubDate: 2026-03-14
lang: zh
category: solar
series: solar-book
tags: ['光伏预测', '晴空模型', '时空依赖', 'Model Chain', '教材笔记']
---

> 核心参考：《Solar Irradiance and PV Power Forecasting》Chapter 4 (Yang & Kleissl, 2024, CRC Press)
> GEFCom2014 竞赛结果 (Hong et al., 2016)

光伏预测是能源预测家族中最年轻的成员——2010 年代才正式起步。但"年轻"不是借口。教材用整整一章分析了光伏与负荷、风力、电价预测的异同，核心结论是：**光伏有五个独特的物理特征，必须利用它们，否则你的模型还不如 Smart Persistence。**

## 特征 1：晴空模型——最大的武器

这是光伏预测与所有其他预测最根本的区别：**我们能精确计算"没有云时应该有多少辐照度"。**

```python
import numpy as np

def rest2_simplified(
    zenith_deg: float,
    e0n: float = 1361.1,
    aod: float = 0.1,
    water_vapor_cm: float = 1.5,
) -> dict[str, float]:
    """
    REST2 晴空模型的简化版（展示透射率乘积原理）。
    
    完整版：Bnc = E₀ₙ × T_R × T_g × T_o × T_n × T_w × T_a
    六种大气衰减过程的透射率相乘。
    """
    cos_z = np.cos(np.radians(zenith_deg))
    if cos_z <= 0:
        return {"bni_clear": 0, "dhi_clear": 0, "ghi_clear": 0}
    
    # 大气质量
    am = 1 / (cos_z + 0.50572 * (96.07995 - zenith_deg)**(-1.6364))
    
    # 简化透射率
    t_rayleigh = np.exp(-0.0903 * am**0.84)
    t_aerosol = np.exp(-aod * am**0.873)
    t_water = np.exp(-0.2385 * water_vapor_cm * am / 
                     (1 + 20.07 * water_vapor_cm * am)**0.45)
    t_ozone = 0.99  # 简化
    
    bni_clear = e0n * t_rayleigh * t_aerosol * t_water * t_ozone
    dhi_clear = 0.3 * e0n * cos_z * (1 - t_rayleigh * t_aerosol)
    ghi_clear = bni_clear * cos_z + dhi_clear
    
    return {
        "bni_clear": float(bni_clear),
        "dhi_clear": float(dhi_clear),
        "ghi_clear": float(ghi_clear),
        "transmittance_total": float(t_rayleigh * t_aerosol * t_water * t_ozone),
    }

# 正午晴空
result = rest2_simplified(30)
print(f"天顶角 30° 时的晴空辐照度：")
print(f"  BNI_clear = {result['bni_clear']:.0f} W/m²")
print(f"  DHI_clear = {result['dhi_clear']:.0f} W/m²")  
print(f"  GHI_clear = {result['ghi_clear']:.0f} W/m²")
print(f"  总透射率 = {result['transmittance_total']:.3f}")
print(f"\n⚡ GEFCom2014 中唯一使用晴空模型的团队 = 冠军")
# 基于模型计算，非实测
```

**GEFCom2014 竞赛事实**：581 名参赛者，来自 61 个国家。唯一使用了晴空模型的团队获得了冠军——其他所有团队的预测在它面前"黯然失色"（"pale in comparison"）。

## 特征 2：晴空指数 $\kappa$ 的双峰分布

```python
def explain_bimodal_distribution():
    """
    晴空指数 κ 的分布通常是双峰的。
    
    峰 1: κ ≈ 1.0 → 晴天状态
    峰 2: κ ≈ 0.3-0.5 → 阴天/多云状态
    
    干旱地区（如沙漠）可能单峰（几乎总是晴天）。
    """
    regions = {
        "Desert Rock (沙漠)": {"peak1": 1.0, "peak2": None, "形态": "单峰"},
        "Goodwin Creek (温带)": {"peak1": 0.4, "peak2": 1.0, "形态": "双峰"},
        "Penn State (多云)": {"peak1": 0.3, "peak2": 0.95, "形态": "双峰"},
    }
    
    print("晴空指数 κ 的分布特征：\n")
    for loc, info in regions.items():
        peaks = f"κ≈{info['peak1']}"
        if info['peak2']:
            peaks += f" 和 κ≈{info['peak2']}"
        print(f"  📍 {loc}: {info['形态']} ({peaks})")
    
    print("\n⚠️ 常见错误：")
    print("  1. 假设 GHI 服从 Beta 分布——物理上不合理")
    print("     (GHI 可以超过晴空值，不是 [0,1] 区间)")
    print("  2. 直接对 GHI 时序计算相关性——夸大季节性虚假相关")
    print("     (上海和洛杉矶的 GHI 相关性很高，但没有因果关系)")

explain_bimodal_distribution()
```

**教材原话**：假设 GHI 服从 Beta 分布的做法是"不恰当的"（inappropriate）。正确做法是对 $\kappa$ 建模，使用混合高斯分布。

## 特征 3：云增强——上界不是晴空值

```python
CLOUD_ENHANCEMENT = {
    "机制": "太阳直射 + 周围云层散射额外漫射辐射",
    "上界规则": {
        "1秒分辨率": "GHI 可达 ~1900 W/m²（~1.4×太阳常数）",
        "1分钟分辨率": "GHI 可达 ~1600 W/m²",
        "5分钟+": "云增强事件趋于平均化",
        "实用上界": "~1.5 × 晴空值",
    },
    "对预测的影响": [
        "不能用晴空值做 clip 上界——会截掉真实事件",
        "Gaussian 分布不适合辐照度（有物理上下界）",
        "QC 时上界要设为 1.5×晴空值，不能设为晴空值",
    ],
}

print("☁️ 云增强事件（Over-irradiance）：\n")
print(f"机制: {CLOUD_ENHANCEMENT['机制']}")
print("\n各时间分辨率的上界：")
for res, val in CLOUD_ENHANCEMENT['上界规则'].items():
    print(f"  {res}: {val}")
print("\n对预测的影响：")
for impact in CLOUD_ENHANCEMENT['对预测的影响']:
    print(f"  → {impact}")
```

## 特征 4：时空依赖性——云的运动是信息源

```python
FORECAST_HORIZONS = {
    "天空相机 (ASI)": {
        "有效范围": "<30 分钟",
        "原理": "鱼眼镜头拍云，光流法追踪云运动",
        "局限": "视野有限，云形变快",
    },
    "卫星 (Satellite)": {
        "有效范围": "<4 小时",
        "原理": "红外/可见光通道，云运动矢量(CMV)",
        "局限": "分辨率有限，时间 lag",
    },
    "NWP (数值天气预报)": {
        "有效范围": "4h → 15天",
        "原理": "求解大气运动方程（7个原始方程）",
        "局限": "计算昂贵，初始条件敏感",
    },
    "传感器网络": {
        "有效范围": "取决于站间距和风速",
        "原理": "上游站数据 = 下游站预测信号",
        "局限": ">数公里后相关性急剧衰减，不可扩展",
    },
}

print("光伏预测方法 vs 有效预测范围：\n")
for method, info in FORECAST_HORIZONS.items():
    print(f"📡 {method}")
    print(f"   有效范围: {info['有效范围']}")
    print(f"   原理: {info['原理']}")
    print(f"   局限: {info['局限']}")
    print()

print("🔑 核心结论（教材推导）：")
print("  前提1: 电网需要 >4h(RTM) 和 >36h(DAM) 的预测")
print("  前提2: 相机(<30min)/卫星(<4h)/传感器网络 都达不到")
print("  结论: NWP 是日前/日内电网调度的唯一可靠来源")
```

## 特征 5：Model Chain——光伏功率曲线

```python
def simplified_model_chain(
    ghi: float,
    zenith_deg: float,
    temp_amb: float,
    p_dc_ref: float = 5000,  # 5kW 系统
    noct: float = 45,
    gamma: float = -0.004,  # 温度系数 -0.4%/°C
    tilt: float = 30,
    albedo: float = 0.2,
) -> dict[str, float]:
    """
    最简 Model Chain（教材公式 4.10-4.12）。
    
    步骤：
    1. 太阳位置 → Z, θ
    2. 分离模型 → Bn, Dh (从 GHI 和 kt)
    3. 转置方程 → GTI (Bn·cosθ + Rd·Dh + ρg·Rr·Gh)
    4. 温度模型 → T_cell
    5. 功率方程 → P
    """
    cos_z = np.cos(np.radians(zenith_deg))
    if cos_z <= 0 or ghi <= 0:
        return {"gti": 0, "t_cell": temp_amb, "power_w": 0}
    
    # 分离模型（简化 Erbs 模型）
    e0 = 1361 * cos_z
    kt = min(ghi / e0, 1.0) if e0 > 0 else 0
    
    if kt <= 0.22:
        dhi = ghi * (1 - 0.09 * kt)
    elif kt <= 0.80:
        dhi = ghi * (0.9511 - 0.1604*kt + 4.388*kt**2 - 
                     16.638*kt**3 + 12.336*kt**4)
    else:
        dhi = ghi * 0.165
    
    bni = (ghi - dhi) / cos_z if cos_z > 0.05 else 0
    
    # 转置方程（简化各向同性）
    tilt_rad = np.radians(tilt)
    cos_theta = max(0, cos_z)  # 简化入射角
    gti = (bni * cos_theta + 
           dhi * (1 + np.cos(tilt_rad)) / 2 + 
           ghi * albedo * (1 - np.cos(tilt_rad)) / 2)
    
    # 温度模型
    t_cell = temp_amb + (noct - 20) / 800 * gti
    
    # 功率方程
    power = p_dc_ref * (gti / 1000) * (1 + gamma * (t_cell - 25))
    
    return {
        "kt": float(kt),
        "bni": float(bni),
        "dhi": float(dhi),
        "gti": float(gti),
        "t_cell": float(t_cell),
        "power_w": float(max(0, power)),
    }

# 示例
result = simplified_model_chain(ghi=800, zenith_deg=30, temp_amb=25)
print("Model Chain 示例（GHI=800, Z=30°, Tamb=25°C）：")
print(f"  kt = {result['kt']:.3f}")
print(f"  BNI = {result['bni']:.0f} W/m²")
print(f"  DHI = {result['dhi']:.0f} W/m²")
print(f"  GTI = {result['gti']:.0f} W/m²")
print(f"  T_cell = {result['t_cell']:.1f}°C")
print(f"  Power = {result['power_w']:.0f} W ({result['power_w']/5000*100:.1f}%)")

# 高温示例
result_hot = simplified_model_chain(ghi=800, zenith_deg=30, temp_amb=40)
print(f"\n高温情况（Tamb=40°C）：")
print(f"  T_cell = {result_hot['t_cell']:.1f}°C")
print(f"  Power = {result_hot['power_w']:.0f} W ({result_hot['power_w']/5000*100:.1f}%)")
print(f"  温度损失 = {(result['power_w']-result_hot['power_w'])/result['power_w']*100:.1f}%")
# 基于模型计算，非实测
```

**教材核心观点**：最佳个体模型组合 ≠ 最佳 Model Chain。误差传播机制复杂，分离模型+转置模型+温度模型的最优组合需要整体优化。

## 从其他领域学到的教训

```python
LESSONS_FROM_OTHER_DOMAINS = {
    "负荷预测": {
        "经验": "两阶段法 = 非黑盒捕主特征 + 黑盒处理残差",
        "启示": "光伏也应该：晴空模型捕主特征 + ML 处理残差(κ)",
        "注意": "1% MAPE ≈ 几十万美元/GW，tiny differences matter",
    },
    "风力预测": {
        "经验": ">3h 必须用 NWP，统计方法无法替代物理",
        "启示": "光伏同理，日前预测必须基于 NWP",
        "注意": "NWP 验证要考虑局部暴露和尺度不匹配",
    },
    "电价预测": {
        "经验": "计量经济学模型主导，概率预测起步晚",
        "启示": "不要重蹈覆辙，光伏预测从一开始就要做概率",
        "注意": "博弈论因素在未来电力市场中会越来越重要",
    },
}

print("从其他能源预测领域学到的教训：\n")
for domain, info in LESSONS_FROM_OTHER_DOMAINS.items():
    print(f"📚 {domain}")
    for k, v in info.items():
        print(f"   {k}: {v}")
    print()
```

---

## 📋 知识卡片

| 特征 | 核心要点 | 实践意义 |
|------|---------|---------|
| 晴空模型 | 能精确算出无云辐照度 | GEFCom2014 冠军的秘密武器 |
| $\kappa$ 双峰分布 | 晴天+阴天两个峰 | 用混合高斯建模，不用 Beta |
| 云增强 | 上界 ≈ 1.5×晴空值 | QC 和 clip 不能用晴空值做上界 |
| 时空依赖 | 云运动是核心信息 | >4h 必须用 NWP |
| Model Chain | 5 步物理链 | 整体优化，不是拼接最优个体模型 |

> **核心原则**：光伏预测的独特优势在于可利用物理知识（晴空模型+Model Chain），放弃这个优势而纯粹依赖数据驱动，是极大的浪费。

---

## 附录：教材 Ch4 完整补遗

### 电价预测的三大建模技巧（光伏可借鉴）

电价预测看似和光伏无关，但其中的建模技巧值得跨领域借鉴：

```python
PRICE_FORECASTING_TRICKS = {
    "方差稳定化 (VST)": {
        "问题": "电价有剧烈尖峰（含负电价），线性模型对异常值敏感",
        "做法": "对数变换不可用（电价可为负）→ 用 asinh 或概率积分变换",
        "光伏借鉴": "辐照度也有异常值（云增强），VST 可用于稳健建模",
        "代码": "np.arcsinh(price)  # 代替 np.log(price)",
    },
    "季节分解": {
        "问题": "电价有日/周/年三重季节性",
        "做法": "分解为长期趋势+随机成分，分别建模再组合",
        "光伏借鉴": "光伏的双季节性(日+年)用晴空模型处理，但残差可进一步分解",
        "代码": "Hodrick-Prescott filter / wavelet decomposition",
    },
    "校准窗口平均": {
        "问题": "训练窗口长度选多少？2周还是5年？",
        "做法": "不选'最优'窗口，而是多窗口预测取平均",
        "光伏借鉴": "光伏模型也面临同样问题，集成不同窗口 > 选单一窗口",
        "代码": "forecast = mean([model.fit(window_n).predict() for n in windows])",
    },
}

print("电价预测三大技巧 → 光伏借鉴：\n")
for name, info in PRICE_FORECASTING_TRICKS.items():
    print(f"🔧 {name}")
    print(f"   问题: {info['问题']}")
    print(f"   做法: {info['做法']}")
    print(f"   光伏借鉴: {info['光伏借鉴']}")
    print(f"   代码: {info['代码']}")
    print()
```

### 层次预测：个体→区域→全网的一致性

```python
def hierarchical_forecasting_explained():
    """
    层次预测（Hierarchical Forecasting）：
    光伏电站的预测必须满足聚合一致性。
    
    传统方法                 现代方法
    ─────────              ─────────
    自上而下 (top-down)     最优调和法 (Hyndman et al., 2011)
    自下而上 (bottom-up)    → 利用所有层级信息
    中间输出 (middle-out)   → 调和后精度通常更高
    ↑ 只用单层信息          ↑ 用全部信息
    """
    hierarchy = {
        "Level 3 全网": "区域A + 区域B + 区域C（净负荷）",
        "Level 2 区域": "电站1 + 电站2 + ... + 电站N",
        "Level 1 电站": "逆变器1 + 逆变器2 + ... + 逆变器M",
        "Level 0 组串": "单个光伏组串的功率预测",
    }
    
    print("光伏功率预测的层级结构：\n")
    for level, desc in hierarchy.items():
        print(f"  {level}: {desc}")
    
    print("\n问题: 各层级独立预测后，加总不一致")
    print("  电站1预测 + 电站2预测 ≠ 区域预测")
    print("\n解决: 最优调和法")
    print("  1. 各层级独立预测（base forecasts）")
    print("  2. 用 MinT/WLS 等方法调和所有层级")
    print("  3. 调和后的预测既一致又更准确")
    print("\n⚡ 电网法规要求: 系统所有者必须提交功率预测")
    print("   动机: 合规 + 减少罚款")

hierarchical_forecasting_explained()
```

### 工业界的残酷现实

```python
INDUSTRY_REALITY = {
    "概率预测接受度低": {
        "原因": "电力系统运营极其保守，流程已演化几十年",
        "表现": "运营者宁可按最坏情况调度，也不完全信任概率模型",
        "教材原话": "与运营标准脱节的预测研究没有内在价值",
    },
    "论文验证标准": {
        "最低要求": "至少一整年小时级验证数据",
        "禁止做法": [
            "只和自家弱版本比（浅网络 vs 深网络）",
            "对接近零的值用 MAPE",
            "验证集只有几十个点",
        ],
        "统计检验": "Diebold-Mariano test 检验模型差异是否显著",
    },
    "教材终极结论": {
        "原话": "纯数据驱动的单站方法 seriously handicapped，无论多复杂",
        "最佳路径": "先预测辐照度 → 后处理 → Model Chain → 光伏功率",
        "核心": "物理知识 + 数据驱动 = 唯一正确道路",
    },
}

print("工业界现实 & 教材终极结论：\n")
for topic, info in INDUSTRY_REALITY.items():
    print(f"📌 {topic}")
    if isinstance(info, dict):
        for k, v in info.items():
            if isinstance(v, list):
                print(f"   {k}:")
                for item in v:
                    print(f"     ❌ {item}")
            else:
                print(f"   {k}: {v}")
    print()
```

### 论文发表的五条黄金建议

```python
PUBLICATION_RECOMMENDATIONS = [
    "1. 文献综述注重逻辑流，不是 roster-like 的 'who did what'",
    "2. 术语精确：不说'短期'，说 'horizon = 24h, resolution = 1h'",
    "3. 提供代码+数据（ostensive reproducibility > verbal）",
    "4. 选有领域专家的期刊，不是只看影响因子",
    "5. 坚持不懈——理解与时间成正比，没有捷径",
]

print("论文发表五条黄金建议（教材作者的编辑经验）：\n")
for r in PUBLICATION_RECOMMENDATIONS:
    print(f"  📝 {r}")
print("\n教材作者背景：300+ 论文 / 数百篇审稿 / 数千篇编辑处理")
```
