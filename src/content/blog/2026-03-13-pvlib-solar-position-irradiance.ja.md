---
title: 'pvlib 太陽位置と日射量分解 — 太陽光発電予測の物理的基盤'
description: 'pvlib の太陽位置計算（SPA）と日射量分解（GHI→DNI/DHI→POA）を深く理解する。完全なコードデモ付き。'
category: solar
pubDate: '2026-03-13'
lang: ja
tags: ["pvlib", "光伏", "辐照度", "技術干货"]
---

## なぜ太陽位置と日射量が太陽光発電予測の基盤なのか？

太陽光パネルの発電量は2つの物理量に依存します：**太陽からの日射がパネルにどれだけ届くか**（POA 日射量）と、**その条件下でのモジュールの電気的応答**です。

チェーン全体の最初のステップは、太陽が空のどこにいて、どれだけの放射エネルギーがパネルに到達するかを正確に計算することです。

---

## I. 太陽位置の計算

### 基本概念

- **天頂角（zenith）**：太陽と真上方向との角度。0° = 真上、90° = 地平線
- **方位角（azimuth）**：太陽の水平方向。0° = 真北、90° = 真東、180° = 真南
- **高度角（elevation）**：= 90° - 天頂角
- **視天頂角（apparent_zenith）**：大気屈折を補正した天頂角

### pvlib の実装

pvlib はデフォルトで **NREL SPA アルゴリズム**（Solar Position Algorithm）を使用し、精度は ±0.0003° — これは業界のゴールドスタンダードです。

```python
import pvlib
import pandas as pd

# 地点を定義
location = pvlib.location.Location(
    latitude=31.23, longitude=121.47,
    tz="Asia/Shanghai", altitude=5, name="上海"
)

# 時系列
times = pd.date_range(
    "2024-06-21 04:00", periods=48,
    freq="30min", tz="Asia/Shanghai"
)

# 太陽位置を計算
solpos = location.get_solarposition(times)
print(solpos[["zenith", "azimuth", "apparent_elevation"]].head(10))
```

**主要な出力列：**
| 列名 | 意味 | 単位 |
|------|------|------|
| `zenith` | 天頂角 | ° |
| `apparent_zenith` | 視天頂角（屈折補正あり） | ° |
| `azimuth` | 方位角 | ° |
| `apparent_elevation` | 視高度角 | ° |
| `equation_of_time` | 均時差 | 分 |

### 日出・日没の判定

```python
# zenith > 90° が夜間
is_daytime = solpos["zenith"] < 90
sunrise = solpos[is_daytime].index[0]
sunset = solpos[is_daytime].index[-1]
print(f"日出: {sunrise}, 日没: {sunset}")
```

---

## II. 日射量の基礎概念

太陽放射が地表に到達する際、3つの成分に分けられます：

| 成分 | 英語略称 | 意味 |
|------|---------|------|
| **全天日射量** | GHI | 水平面が受ける総放射量 |
| **法線面直達日射量** | DNI | 太陽方向に垂直な面が受ける直達放射 |
| **散乱日射量** | DHI | 水平面が受ける散乱放射（天空散乱） |

**基本関係式：**
```
GHI = DNI × cos(zenith) + DHI
```

気象観測所は通常 GHI のみを測定するため、モデルを使って DNI と DHI を分離する必要があります。

---

## III. 日射量分解モデル

GHI データのみがある場合、DNI + DHI に分解する必要があります：

### DISC モデル
```python
# GHI → DNI
dni_disc = pvlib.irradiance.disc(
    ghi=clearsky["ghi"],
    solar_zenith=solpos["zenith"],
    datetime_or_doy=times
)
print(dni_disc.head())
```

### DIRINT モデル（より高精度）
```python
# GHI → DNI（より多くの大気変数を考慮）
dni_dirint = pvlib.irradiance.dirint(
    ghi=clearsky["ghi"],
    solar_zenith=solpos["zenith"],
    times=times
)
```

### Erbs 分解
```python
# GHI → DNI + DHI（古典的モデル）
from pvlib.irradiance import clearness_index

# まず晴天指数 kt を計算
kt = clearness_index(
    ghi=measured_ghi,
    solar_zenith=solpos["zenith"],
    extra_radiation=pvlib.irradiance.get_extra_radiation(times)
)
```

---

## IV. 水平面日射量 → パネル日射量（POA）

パネルは水平に設置されていないため、GHI/DNI/DHI をパネルの傾斜面上の日射量（POA = Plane of Array）に変換する必要があります。

### 変換プロセス

```python
# 1. 大気外放射（Perez モデルに必要）
dni_extra = pvlib.irradiance.get_extra_radiation(times)

# 2. パネルパラメータ
surface_tilt = 31.23    # 傾斜角（通常 ≈ 緯度）
surface_azimuth = 180   # 南向き

# 3. POA を計算
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"],
    dni=clearsky["dni"],
    ghi=clearsky["ghi"],
    dhi=clearsky["dhi"],
    dni_extra=dni_extra,
    model="perez"  # Perez 散乱モデルを推奨
)
print(poa[["poa_global", "poa_direct", "poa_diffuse"]].head())
```

### POA 出力成分

| 成分 | 意味 |
|------|------|
| `poa_global` | パネル総日射量 |
| `poa_direct` | パネル上の直達成分 |
| `poa_diffuse` | パネル上の散乱成分（天空＋地面反射） |
| `poa_sky_diffuse` | 天空散乱 |
| `poa_ground_diffuse` | 地面反射散乱 |

### 散乱モデルの比較

pvlib は複数の散乱モデルを提供します：

| モデル | 関数 | 精度 | 適用場面 |
|--------|------|------|---------|
| **Perez** | `pvlib.irradiance.perez()` | ⭐⭐⭐⭐⭐ | 汎用最初の選択 |
| **Hay-Davies** | `pvlib.irradiance.haydavies()` | ⭐⭐⭐⭐ | 計算量が少ない |
| **Reindl** | `pvlib.irradiance.reindl()` | ⭐⭐⭐⭐ | 折衷案 |
| **Klucher** | `pvlib.irradiance.klucher()` | ⭐⭐⭐ | 曇り環境 |
| **Isotropic** | `pvlib.irradiance.isotropic()` | ⭐⭐ | 最もシンプル |

**業界では Perez モデルが第一選択**です。精度が最も高く、追加入力として `dni_extra`（大気外放射）が必要です。

---

## V. 入射角（AOI）の計算

太陽光はパネルに垂直には当たらず、入射角が反射損失に影響します：

```python
aoi = pvlib.irradiance.aoi(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"]
)
print(f"正午の入射角: {aoi.iloc[len(aoi)//2]:.1f}°")
```

AOI が大きいほど反射損失も大きくなります。pvlib は複数の IAM（入射角修正係数）モデルを提供します：

```python
# 物理 IAM モデル
iam_loss = pvlib.iam.physical(aoi, n=1.526, K=4.0, L=0.002)
# 0～1 の透過率係数を返す
```

---

## VI. 晴天モデル

実測データがない場合、晴天モデルを使って理想的な日射量を推定します：

```python
# Ineichen 晴天モデル（デフォルト）
clearsky = location.get_clearsky(times, model="ineichen")

# GHI、DNI、DHI を出力
print(clearsky.columns)  # ghi, dni, dhi
```

pvlib がサポートする晴天モデル：
- **Ineichen-Perez**（デフォルト）— 最も広く使われている
- **Haurwitz** — シンプル、GHI のみ出力
- **Simplified Solis** — エアロゾル光学的厚さをサポート

---

## VII. 完全な例：地点から POA までの全パイプライン

```python
import pvlib
import pandas as pd

# 地点：上海
loc = pvlib.location.Location(31.23, 121.47, "Asia/Shanghai", 5)
times = pd.date_range("2024-06-21", periods=48, freq="30min", tz="Asia/Shanghai")

# 太陽位置
solpos = loc.get_solarposition(times)

# 晴天日射量
cs = loc.get_clearsky(times)

# 大気外放射
dni_extra = pvlib.irradiance.get_extra_radiation(times)

# パネル POA（傾斜角=緯度、南向き）
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=31.23, surface_azimuth=180,
    solar_zenith=solpos["apparent_zenith"],
    solar_azimuth=solpos["azimuth"],
    dni=cs["dni"], ghi=cs["ghi"], dhi=cs["dhi"],
    dni_extra=dni_extra, model="perez"
)

# 正午の結果を出力
noon = poa.between_time("11:30", "12:30")
print("正午の POA 日射量 (W/m²):")
print(noon[["poa_global", "poa_direct", "poa_diffuse"]].round(1))

# 日積算日射量 (kWh/m²)
daily_irradiation = poa["poa_global"].sum() * 0.5 / 1000  # 30分間隔
print(f"\n日積算日射量: {daily_irradiation:.2f} kWh/m²")
```

---

## クイックリファレンスカード 📋

| ポイント | 内容 |
|---------|------|
| **太陽位置** | pvlib は SPA アルゴリズムを使用、精度 ±0.0003°、zenith/azimuth を出力 |
| **日射量の三要素** | GHI = DNI×cos(z) + DHI；気象観測所は GHI を測定、モデルで分解 |
| **分解モデル** | DISC、DIRINT — GHI から DNI を抽出 |
| **POA 変換** | 水平面日射量 → パネル傾斜面日射量；Perez モデルを推奨 |
| **入射角 AOI** | 反射損失に影響、IAM モデルで補正 |
| **晴天モデル** | 実測データがない場合の理想日射量推定 |

> **次回予告：** pvlib モジュール温度モデルと DC 電力計算 — 日射量からワットへの変換
