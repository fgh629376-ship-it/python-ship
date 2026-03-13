---
title: 'pvlib 年間発電量評価と PR 計算 — 公式から全年シミュレーションまで'
description: 'pvlib を使って上海の 5kWp システムで 8760 時間シミュレーションを実施。PR・比発電量・設備利用率の計算方法と、なぜ夏の PR が最も低くなるのかを体系的に解説'
pubDate: '2026-03-13'
category: solar
lang: ja
tags: ["pvlib", "光伏", "PR计算", "发电量评估", "技术干货"]
---

> ⚠️ **データに関する注意**：本記事のすべてのシミュレーションデータは **pvlib のクリアスカイモデル（clearsky）** に基づいて計算されたものであり、実際の発電所の実測データではありません。クリアスカイモデルは年間を通じて雲や霞がないことを前提としているため、GHI、発電量、PR などの数値は実際よりも高くなります。実際のデータは実測値をご参照ください。

## なぜあなたの太陽光発電システムは常に予想より少ない発電量しか出ないのか？

5kWp の太陽光発電システムを設置しました。理論上、年間どれくらいの電力を発電できるのでしょうか？メーカーのマニュアルを読むと、ある言葉が繰り返し登場します：**PR**（Performance Ratio、システム効率比）。

PR は太陽光発電業界でシステムの「健全性」を測る核心指標です。PR = 92% のシステムと PR = 78% のシステムは同じ設備容量でも、年間発電量が 15% 異なる場合があります。

本記事では pvlib を使って上海のある住宅用 5kWp 太陽光発電システムの全年時間別シミュレーションを行い、PR・比発電量・設備利用率の計算方法と、なぜ夏の PR が最も低くなるのかを丁寧に解説します。

---

## 第1章：核心指標の公式

コードを書く前に、次の3つの公式をしっかり覚えましょう：

### PR（Performance Ratio）

$$PR = \frac{E_{ac}}{P_{peak} \times H_{POA}}$$

- $E_{ac}$：年間 AC 発電量（kWh）
- $P_{peak}$：設備容量（kWp）
- $H_{POA}$：パネル面（POA）年間日射量（kWh/m²）

**重要**：分母は POA 日射量であって、水平面 GHI ではありません！

### 比発電量（Specific Yield）

$$SY = \frac{E_{ac}}{P_{peak}} \quad \text{[kWh/kWp]}$$

「設置した 1kW のピーク容量あたり、年間何 kWh 発電できるか」と理解してください。

### 設備利用率（Capacity Factor）

$$CF = \frac{E_{ac}}{P_{peak} \times 8760} \times 100\%$$

---

## 第2章：全年時間別シミュレーション

### 環境準備

```bash
pip install pvlib pandas numpy
```

### ステップ 1：全年模擬気象データの生成

```python
import pvlib
import pandas as pd
import numpy as np
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import warnings
warnings.filterwarnings('ignore')

# 上海：北緯 31.2°、東経 121.5°
site = Location(31.2, 121.5, tz='Asia/Shanghai', altitude=10, name='上海')

# 全年 8760 時間
times = pd.date_range('2025-01-01', '2025-12-31 23:00', freq='h', tz='Asia/Shanghai')

# 快晴時日射量をベースラインとして使用
cs = site.get_clearsky(times, model='ineichen')

# ランダムな雲量の擾乱を加えて実際の天気を模擬
np.random.seed(42)
cloud_factor = np.clip(np.random.beta(3, 1, len(times)), 0.1, 1.0)
day_mask = cs['ghi'] > 0

ghi = cs['ghi'].copy() * np.where(day_mask, cloud_factor, 1.0)
dni = cs['dni'].copy() * np.where(day_mask, cloud_factor, 1.0)
dhi = cs['dhi'].copy() * np.where(day_mask, cloud_factor, 1.0)

weather = pd.DataFrame({
    'ghi': ghi, 'dni': dni, 'dhi': dhi,
    # 気温：年平均 15°C、夏は暑く冬は寒い
    'temp_air': 15 + 10*np.sin(2*np.pi*(times.dayofyear-80)/365)
                   + np.random.normal(0, 3, len(times)),
    'wind_speed': np.clip(3 + np.random.exponential(2, len(times)), 0, 20),
}, index=times)

print(f"年間 GHI: {weather['ghi'].sum()/1000:.0f} kWh/m²")
# 年間 GHI: 1640 kWh/m²
```

### ステップ 2：PV システムモデルの構築

```python
# CEC モジュールデータベースを読み込む（組み込み、ダウンロード不要）
cec_mods = pvlib.pvsystem.retrieve_sam('CECMod')
module = cec_mods['Canadian_Solar_Inc__CS6P_250P']

print(f"モジュール STC 出力: {module['STC']:.0f}W")
print(f"温度係数(Pmax): {module['gamma_r']:.3f}%/°C")
# モジュール STC 出力: 250W
# 温度係数(Pmax): -0.424%/°C

# SAPM 温度モデルパラメータ（開放型架台、ガラス-ガラス封止）
temp_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

N_MOD = 20          # モジュール数
KWP = N_MOD * module['STC'] / 1000  # = 5.0 kWp

# pvlib 0.15.0 では Array + FixedMount を使って架台パラメータを渡す必要があります
array = Array(
    mount=FixedMount(surface_tilt=30, surface_azimuth=180),  # 南向き 30° 固定傾斜角
    module_parameters=module,
    temperature_model_parameters=temp_params,
    modules_per_string=N_MOD,
    strings=1,
)

system = PVSystem(
    arrays=[array],
    inverter_parameters={'pdc0': KWP * 1000, 'eta_inv_nom': 0.96},  # PVWatts パワーコンディショナー
)
```

### ステップ 3：ModelChain を実行して結果を抽出

```python
mc = ModelChain(system, site, aoi_model='physical', spectral_model='no_loss')
mc.run_model(weather)

# ⚠️ pvlib 0.15.0 の落とし穴：results.ac は DataFrame で、出力は p_mp 列にあります！
ac_power = mc.results.ac['p_mp'].clip(0)   # AC 出力（W）
dc_power = mc.results.dc['p_mp'].clip(0)   # DC 出力（W）
poa = mc.results.total_irrad['poa_global'] # パネル面日射強度（W/m²）
cell_temp = mc.results.cell_temperature    # セル温度（°C）

# 年間合計に変換
ann_ac_kwh = float(ac_power.sum() / 1000)
ann_dc_kwh = float(dc_power.sum() / 1000)
poa_kwh_m2 = float(poa.sum() / 1000)

print(f"年間 POA（南向き 30°）: {poa_kwh_m2:.0f} kWh/m²")
print(f"DC 発電量: {ann_dc_kwh:.0f} kWh/年")
print(f"AC 発電量: {ann_ac_kwh:.0f} kWh/年")
# 年間 POA（南向き 30°）: 1883 kWh/m²
# DC 発電量: 9069 kWh/年
# AC 発電量: 8694 kWh/年
```

### ステップ 4：主要指標の計算

```python
# PR：分母は KWP × poa_kwh_m2 で単位はすでに合っています
pr = ann_ac_kwh / (KWP * poa_kwh_m2)
sy = ann_ac_kwh / KWP               # 比発電量
cf = ann_ac_kwh / (KWP * 8760)      # 設備利用率

print(f"PR: {pr:.3f} ({pr*100:.1f}%)")
print(f"比発電量: {sy:.0f} kWh/kWp")
print(f"設備利用率: {cf*100:.1f}%")
# PR: 0.923 (92.3%)
# 比発電量: 1739 kWh/kWp
# 設備利用率: 19.8%
```

---

## 第3章：月別 PR 分析 — なぜ夏の PR が最も低いのか？

```python
m_ac  = (ac_power.resample('ME').sum() / 1000).values
m_poa = (poa.resample('ME').sum() / 1000).values
m_ct  = cell_temp.resample('ME').mean().values
m_pr  = m_ac / (KWP * m_poa)

months = ['1月','2月','3月','4月','5月','6月',
          '7月','8月','9月','10月','11月','12月']
for i, mo in enumerate(months):
    print(f"{mo}: AC={m_ac[i]:.0f}kWh | セル温度={m_ct[i]:.1f}°C | PR={m_pr[i]:.3f}")
```

出力結果：

| 月 | AC 発電量（kWh） | セル温度（°C） | 月間 PR |
|----|---------------|-------------|--------|
| 1月 | 739          | 11.7        | 0.962  |
| 3月 | 819          | 20.2        | 0.924  |
| 6月 | 687          | 30.6        | **0.881** |
| 9月 | 730          | 21.2        | 0.925  |
| 12月 | 691         | 10.2        | **0.971** |

**結論**：6月のセル温度は 30.6°C で PR は 88.1% まで低下し、12月のセル温度は 10.2°C で PR は 97.1% に達します。

温度係数 -0.424%/°C の影響：25°C から 30.6°C になると効率は約 2.4% 低下します。一見少なく見えますが、夏全体で積み上がると相当な損失になります。

---

## 第4章：最適傾斜角のスキャン

```python
def simulate_tilt(tilt):
    arr = Array(
        mount=FixedMount(tilt, 180),
        module_parameters=module,
        temperature_model_parameters=temp_params,
        modules_per_string=N_MOD, strings=1,
    )
    sys = PVSystem(arrays=[arr], inverter_parameters={'pdc0': KWP*1000, 'eta_inv_nom': 0.96})
    mc = ModelChain(sys, site, aoi_model='physical', spectral_model='no_loss')
    mc.run_model(weather)
    return float(mc.results.ac['p_mp'].clip(0).sum() / 1000)

base = simulate_tilt(30)
for tilt in [0, 15, 20, 25, 30, 35, 40, 45]:
    y = simulate_tilt(tilt)
    print(f"傾斜角 {tilt:2d}°: {y:.1f} kWh ({(y-base)/base*100:+.1f}%)")
```

```
傾斜角  0°: 7477.6 kWh (-14.0%)
傾斜角 15°: 8341.9 kWh  (-4.0%)
傾斜角 20°: 8516.2 kWh  (-2.0%)
傾斜角 25°: 8633.5 kWh  (-0.7%)
傾斜角 30°: 8694.0 kWh  (+0.0%)
傾斜角 35°: 8698.0 kWh  (+0.0%) ← 最適
傾斜角 40°: 8645.3 kWh  (-0.6%)
傾斜角 45°: 8535.7 kWh  (-1.8%)
```

上海（北緯 31.2°）の最適傾斜角は約 33-35° ですが、25° から 40° の間の差異は 1% 未満です。実際の工事では屋根の構造に合わせて 30° を選んでも全く問題ありません。正確な角度にこだわる必要はありません。

---

## 第5章：完全な損失チェーン

```
設備容量:          5.0 kWp
理論最大発電量:    8760h × 5kW = 43800 kWh（達成不可能）
基準発電量:        9415 kWh  （POA 日射に基づく理論満発）
DC 発電量:         9069 kWh  ← 温度損失（-3.8%）、AOI 損失など
AC 発電量:         8694 kWh  ← パワーコンディショナー損失（-4.1%）
総損失率:          7.7%（PR = 92.3%）
```

---

## ⚠️ pvlib 0.15.0 のよくある落とし穴

1. **`results.ac` は DataFrame です** — `.sum()` を直接呼ばず、`['p_mp'].clip(0).sum()` を使ってください
2. **PR 公式の分母**：`KWP × poa_kwh_m2` — さらに 1000 で割る必要はありません（単位はすでに合っています）
3. **PVSystem の新しい API**：架台パラメータの渡し方は `Array(mount=FixedMount(...))` を使う必要があります
4. **POA ≠ GHI**：PR の分母には必ず POA（パネル傾斜面）の日射量を使ってください。そうしないと結果が過大評価されます

---

## クイックリファレンスカード 🗂️

| 指標 | 公式 | 上海 5kWp ケース |
|------|------|----------------|
| **PR** | E_ac / (P_peak × H_POA) | **92.3%** |
| **比発電量** | E_ac / P_peak | **1739 kWh/kWp** |
| **設備利用率** | E_ac / (P_peak × 8760) | **19.8%** |
| 最適傾斜角 | ≈ 当地緯度 | **~35°**（差異 <1%、30° で十分）|
| 夏の PR が最低 | 高温 -0.424%/°C | 6月 88.1% |
| 冬の PR が最高 | 低温高効率 | 12月 97.1% |

**経験値（上海）**：5kWp システムの年間発電量 ≈ **8500〜9000 kWh**、比発電量 ≈ **1700〜1800 kWh/kWp**。
