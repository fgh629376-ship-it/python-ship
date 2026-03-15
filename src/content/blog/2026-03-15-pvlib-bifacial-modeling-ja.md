---
title: 'pvlib 両面モジュールモデリング実践 — 裏面で10-20%多く発電する物理的ロジック'
description: 'pvlib.bifacialモジュールで両面太陽光パネルをモデリング：infinite_sheds日射量計算、視野係数分析、ミスマッチ損失の定量化'
category: solar
series: pvlib
lang: ja
pubDate: '2026-03-15'
tags: ["pvlib", "両面モジュール", "bifacial", "太陽光モデリング", "視野係数"]
---

## 両面モジュール：太陽光発電業界の「新標準」

2024年の世界の太陽光発電新規導入量のうち、**両面モジュールのシェアは70%を超えました**（ITRPV 2024 Roadmap）。理由は単純で、裏面も発電できるため、同じ地面面積で10-20%多くの電力を得られます。

しかし「どれだけ多く」は単純な数字ではありません。地面のアルベド、設置高さ、列間距離、傾斜角、さらにはアレイ内のモジュール位置にまで依存します。**pvlibの`bifacial`モジュールは完全な物理モデリングツールを提供**し、各要因の影響を正確に定量化できます。

> ⚠️ 本記事のデータはすべて晴天モデルシミュレーションに基づいており、実測データではありません

---

## 1. 両面発電の物理原理

両面モジュールの裏面が受ける日射量は3つの成分から構成されます：

1. **地面反射日射量**：GHIが地面に当たり、アルベドρで反射して裏面に到達 — 主要な源
2. **天空散乱日射量**：天空半球からの散乱光
3. **直達成分**：太陽高度角が低い時（朝夕）、直達光が裏面に到達する場合

基本方程式：

```
$$E_{\text{back}} = \rho \times \text{GHI} \times VF_{\text{back→ground}} + \text{DHI} \times VF_{\text{back→sky}}$$
```

**VF（視野係数）** は幾何学的関係を定量的に記述し、裏面がどれだけの地面と空を「見る」かを決定します。

---

## 2. infinite_shedsモデル

pvlibは`infinite_sheds`モデルを提供しています — モジュールアレイが無限に長いと仮定し（端部効果を排除）、表面と裏面の日射量を計算します。

### 基本的な使い方

```python
import pvlib
import pandas as pd

loc = pvlib.location.Location(31.23, 121.47, tz='Asia/Shanghai', altitude=5)
times = pd.date_range('2024-06-21 05:00', '2024-06-21 19:00',
                       freq='10min', tz='Asia/Shanghai')
solpos = loc.get_solarposition(times)
cs = loc.get_clearsky(times)

result = pvlib.bifacial.infinite_sheds.get_irradiance(
    surface_tilt=30,
    surface_azimuth=180,
    solar_zenith=solpos['apparent_zenith'],
    solar_azimuth=solpos['azimuth'],
    gcr=0.4,
    height=1.5,
    pitch=2.5,
    ghi=cs['ghi'], dhi=cs['dhi'], dni=cs['dni'],
    albedo=0.25,
    iam_front=1.0, iam_back=1.0,
)
```

---

## 3. 主要パラメータの感度分析

### 3.1 アルベド — 最も影響が大きい単一要因

上海の夏至（6月21日）、GCR=0.4、傾斜角=30°：

| 地面タイプ | アルベド | 裏面日射量 | 両面ゲイン |
|-----------|---------|-----------|-----------|
| 暗色アスファルト | 0.15 | $0.77 \text{kWh/m}^2$ | **11.3%** |
| 明色土壌 | 0.25 | $1.22 \text{kWh/m}^2$ | **18.0%** |
| 明色コンクリート | 0.35 | $1.67 \text{kWh/m}^2$ | **24.5%** |
| 白色砕石 | 0.50 | $2.35 \text{kWh/m}^2$ | **34.3%** |
| 新雪 | 0.70 | $3.25 \text{kWh/m}^2$ | **47.2%** |

**結論**：アルベドを0.15→0.50にすると、両面ゲインは3倍に。白い砕石やシートを敷設する投資は、2-3年で回収できます。

> 参考：Deline et al. (2020) "Bifacial PV System Performance", IEEE JPVSC. Q1ジャーナル.

### 3.2 GCR — 密度vsゲインのトレードオフ

| GCR | 列間距離(m) | 両面ゲイン |
|-----|-----------|-----------|
| 0.25 | 4.0 | **21.7%** |
| 0.40 | 2.5 | **18.0%** |
| 0.60 | 1.7 | **13.1%** |

GCRが0.1増加するごとに、両面ゲインは約2-3ポイント低下します。

### 3.3 月別変動 — 夏高冬低

上海の年間晴天モデル（GCR=0.4、albedo=0.25）：

**年間両面ゲイン：11.9%**。6月がピーク（17.9%）、12月が最低（5.4%）。

---

## 4. 視野係数（View Factor）

```python
from pvlib.bifacial import utils

vf_sky = utils.vf_row_sky_2d(surface_tilt=30, gcr=0.4, x=0.5)
vf_gnd = utils.vf_row_ground_2d(surface_tilt=30, gcr=0.4, x=0.5)
```

### 傾斜角と視野係数

| 傾斜角 | VF(→空) | VF(→地面) |
|-------|---------|----------|
| 0° | 1.0000 | 0.0000 |
| 30° | 0.8999 | 0.0473 |
| 60° | 0.6637 | 0.1857 |
| 90° | 0.4019 | 0.4019 |

90°（垂直）では両面が対称 — 東西向き両面ファサードの物理的基盤です。

### モジュール位置による不均一性

傾斜角30°、GCR=0.4の場合、下端は上端より91%多くの地面を「見ます」（VF_gnd: 0.0670 vs 0.0350）。これが裏面日射量の不均一性を引き起こし、ミスマッチ損失に直接影響します。

---

## 5. Deline電力ミスマッチモデル

```python
loss = pvlib.bifacial.power_mismatch_deline(rmad=0.10, fill_factor=0.79)
# 戻り値: 0.0462 (4.62%の電力損失)
```

| RMAD | 電力損失 |
|------|---------|
| 2% | 0.41% |
| 5% | 1.51% |
| 10% | **4.62%** |
| 15% | **9.33%** |
| 20% | **15.64%** |

RMAD 5%以下では損失は無視できます。10%を超えると急激に上昇（ほぼ二次関数）。

> 参考：Deline et al. (2020) "Assessment of Bifacial PV Mismatch Losses", NREL Technical Report.

---

## 6. エンジニアリング設計ガイドライン

### セル技術別の両面係数

| 技術 | 両面係数 |
|-----|---------|
| p-PERC | 0.65-0.70 |
| n-TOPCon | 0.80-0.85 |
| HJT | 0.85-0.95 |

### 最適GCR

- **片面モジュール**: GCR=0.40-0.50
- **両面モジュール**: GCR=0.30-0.40（低密度で両面ゲインを解放）
- **垂直両面**: GCR=0.15-0.25（営農型太陽光、東西向き）

---

## 7. 主要な発見

1. **アルベドが最重要因子**: 0.15→0.50でゲインが11%→34%に
2. **年間両面ゲイン≈10-12%**（上海、albedo=0.25）、夏季最大18%、冬季最低5%
3. **GCR 0.1増加ごとに両面ゲイン2-3%低下** — 両面発電所は低密度が必要
4. **RMAD<5%でミスマッチ損失は無視可能**、10%超で急増
5. **FF高のモジュールはミスマッチに敏感** — HJT（FF≈0.83）は列間距離設計に注意

---

## 参考文献

- Deline, C. et al. (2020). *IEEE Journal of Photovoltaics*, 10(4), 1090-1098. (Q1)
- Stein, J.S. et al. (2021). *Solar Energy*, 225, 310-326. (Q1)
- ITRPV (2024). *International Technology Roadmap for Photovoltaic*, 14th Edition.
- pvlib docs: [bifacial module](https://pvlib-python.readthedocs.io/en/stable/reference/bifacial.html)
