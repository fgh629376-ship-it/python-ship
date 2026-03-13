---
title: 'pvlib-python 太陽光発電量予測完全ガイド'
description: 'Python で太陽光発電量を予測する — pvlib ライブラリの入門から実践まで、物理モデリングチェーン・ModelChain・気象データ連携・ML ハイブリッド手法を網羅'
pubDate: '2026-03-12'
category: solar
lang: ja
tags: ['pvlib', '光伏', '能源', '技术干货']
---

## pvlib とは？

**pvlib** は太陽光発電業界における Python の物理ベース標準モデリングライブラリです。注意：ML 予測ライブラリでは**ありません** — 物理メカニズムに基づく決定論的な発電量予測ツールです。

基本コンセプトはシンプルです：**地点 + 時刻 + 気象データ → その瞬間の発電所出力を精確に計算**。

```bash
pip install pvlib
# 最新版 v0.15.1（2026年3月）
```

---

## 太陽光発電量予測の物理チェーン

pvlib は発電量予測を 6 つの物理ステップに分解しており、各ステップに対応するモデルが用意されています：

```
太陽位置（高度角 / 方位角）
  ↓
快晴時日射量（GHI / DNI / DHI）
  ↓
傾斜面日射量（POA — 傾斜パネルが実際に受ける日射）
  ↓
有効日射量（AOI 損失 + スペクトル補正を考慮）
  ↓
モジュール温度（発電効率に 5〜10% 影響）
  ↓
DC 電力 → AC 電力（インバータ経由）→ 最終出力
```

このチェーンを理解することが、pvlib を使いこなすための鍵です。

---

## コアモジュール早見表

| モジュール | 役割 | 主な関数 |
|-----------|------|---------|
| `solarposition` | 太陽高度角 / 方位角 | `get_solarposition()` |
| `clearsky` | 快晴時日射量モデル | `ineichen()`, `haurwitz()` |
| `irradiance` | 日射量の分解 / 変換 | `get_total_irradiance()`, `perez()` |
| `temperature` | モジュール / セル温度 | `sapm_cell()`, `faiman()` |
| `pvsystem` | DC / AC 電力計算 | `pvwatts_dc()`, `singlediode()` |
| `modelchain` | **全チェーンのラッパー** | `ModelChain.run_model()` |
| `iotools` | 気象データ取得 | Solcast / ERA5 / NASA Power |

---

## ModelChain — ワンストップ発電量予測

ModelChain は最高レベルの抽象化で、6 ステップをすべて繋げてくれます。地点・システムパラメータを定義して気象データを渡すだけです：

```python
import pvlib
import pandas as pd

# 1. 地点を定義（上海）
location = pvlib.location.Location(
    latitude=31.2,
    longitude=121.5,
    altitude=10,
    tz='Asia/Shanghai'
)

# 2. 太陽光システムを定義
module_params = dict(pdc0=10000, gamma_pdc=-0.004)  # 10kW、温度係数 -0.4%/℃
inverter_params = dict(pdc0=9500)
temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
    'sapm']['open_rack_glass_glass'
]

system = pvlib.pvsystem.PVSystem(
    surface_tilt=30,        # 傾斜角 30°
    surface_azimuth=180,    # 真南向き
    module_parameters=module_params,
    inverter_parameters=inverter_params,
    temperature_model_parameters=temp_params,
    modules_per_string=20,
    strings_per_inverter=2,
)

# 3. ModelChain を構築
mc = pvlib.modelchain.ModelChain(
    system, location,
    dc_model='pvwatts',
    ac_model='pvwatts',
    aoi_model='physical',
    spectral_model='no_loss',
    temperature_model='sapm',
)

# 4. 気象データを準備（ghi/dhi/dni が必須）
times = pd.date_range('2026-06-01', '2026-06-07', freq='1h', tz='Asia/Shanghai')
weather = location.get_clearsky(times)  # 快晴を仮定
weather['temp_air'] = 25
weather['wind_speed'] = 2

# 5. 実行！
mc.run_model(weather)

# 6. 結果を取得
ac_power = mc.results.ac  # W、交流電力の時系列
dc_power = mc.results.dc  # W、直流電力
```

---

## 3 つの予測シナリオ

### シナリオ 1：快晴ベースライン予測

快晴 = 雲がない場合の理論的最大日射量。ベースラインとしてよく使われます：

```python
clearsky = location.get_clearsky(times, model='ineichen')
# ghi/dni/dhi を出力
# 実際の発電量 / 快晴時発電量 = 快晴指数（0〜1）
```

### シナリオ 2：NWP 気象予報の組み込み

短期予測で最もよく使われる方法 — サードパーティから予報データを取得してモデルに直接渡します：

```python
from pvlib.iotools import get_solcast_forecast

df, meta = get_solcast_forecast(
    latitude=31.2,
    longitude=121.5,
    api_key='your_key',
    hours=48,
)
# df には ghi/dni/dhi/temp_air/wind_speed が含まれます
mc.run_model(df)
```

### シナリオ 3：傾斜面日射計センサーの活用

現地にセンサーがある場合はデータがより正確 — 直接使いましょう：

```python
mc.run_model_from_poa(poa_data)
# poa_data には poa_global / poa_direct / poa_diffuse が必要
```

---

## モデル選択ガイド

### 日射量変換（GHI → 傾斜面 POA）

- **`perez`** — 精度最高、デフォルト推奨
- **`haydavies`** — ほとんどの場合で十分
- **`isotropic`** — 簡易推定用

### DC 電力モデル

- **`pvwatts`** — `pdc0 + gamma_pdc` だけで動作、データが少ない場合の第一選択
- **`sapm`** — 完全な Sandia パラメータが必要、精密シミュレーション向け
- **`singlediode`** — 5 パラメータが必要、最も高精度

### 温度モデル

```python
# SAPM（最もよく使われる）
pvlib.temperature.sapm_cell(poa_global, temp_air, wind_speed, a, b, deltaT)

# Faiman（シンプルな線形モデル、効果的）
pvlib.temperature.faiman(poa_global, temp_air, wind_speed, u0=25, u1=6.84)
```

---

## 損失モデル（PVWatts）

実際の発電量は常に理論値より低くなります。pvlib はあらゆる損失要因を考慮しています：

```python
losses = pvlib.pvsystem.pvwatts_losses(
    soiling=2,          # 汚れ 2%
    shading=3,          # 遮影 3%
    mismatch=2,         # ミスマッチ 2%
    wiring=2,           # 配線損失 2%
    connections=0.5,    # 接続部 0.5%
    lid=1.5,            # LID 1.5%
    nameplate_rating=1, # 銘板誤差 1%
    availability=3,     # 稼働率 3%
)
# 合計損失：約 14.1%
```

---

## pvlib + ML = 業界のベストプラクティス

純粋な物理モデルには限界があり、純粋な ML は物理的制約に欠けます。両者を組み合わせるのが主流のアプローチです：

```
手順：
1. pvlib で物理ベースの基準予測値 P_phys を算出
2. 残差を計算：residual = P_actual - P_phys
3. XGBoost / LSTM で残差を学習
   入力特徴：雲量指数、NWP バイアス、過去の残差
4. 最終予測：P_final = P_phys + residual_pred
```

物理制約により予測値が物理的に妥当な範囲に保たれ、ML が気象予報の誤差を補正します。

---

## 気象データソース

| データソース | 特徴 | 費用 |
|------------|------|------|
| **Solcast** | 最高精度、予報対応 | 商用 |
| **ERA5** | ECMWF 再解析、グローバル | 無料 |
| **NASA Power** | グローバルカバレッジ | 無料 |
| **PVGIS** | EU 管理 | 無料 |

---

## クイックリファレンス 📌

```
pvlib のコアポジション：
  物理モデリングエンジン — ブラックボックス ML ではない

6 ステップ予測チェーン：
  太陽位置 → 快晴時日射 → 傾斜面日射
  → 有効日射 → モジュール温度 → 電力

最速の始め方：
  ModelChain.run_model(weather_dataframe)

実践公式：
  pvlib 物理ベースライン + ML 残差補正 = 最適解
```
