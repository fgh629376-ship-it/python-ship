---
title: 'pvlib 単軸トラッカー モデリング実践：年間15%増益の物理的根拠'
description: 'pvlib.tracking.singleaxis を使って固定架台と単軸トラッカーを比較し、上海地区での年間+15.3%増益の原因と、冬季にトラッカーがかえって損をする本当の理由を解明します。バックトラッキングと GCR パラメータの詳細解説付き。'
category: solar
series: pvlib
pubDate: '2026-03-13'
lang: ja
tags: ["pvlib", "光伏", "单轴跟踪器", "跟踪增益", "技術干货"]
---

## なぜトラッカーを使うのか？

大規模地上型太陽光発電所には一つのこだわりがあります：**パネルを常に太陽の方向に向ける**ことです。固定架台は設置後に特定の静的角度にしか向けられませんが、単軸トラッカーは一日中回転することで直達日射の利用率を最大化します。

では、トラッカーの費用対効果は？増益はどの程度？どの月に効果的で、どの月に効果がないのか？今日は pvlib を使ってこれらを定量的に分析します。

---

## コア関数：pvlib.tracking.singleaxis

```python
import pvlib
import pvlib.tracking
import pvlib.irradiance
import pvlib.location
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

lat, lon = 31.23, 121.47  # 上海
tz = 'Asia/Shanghai'

times = pd.date_range('2025-01-01', '2025-12-31 23:00', freq='1h', tz=tz)
loc = pvlib.location.Location(lat, lon, tz=tz, altitude=5)
cs = loc.get_clearsky(times)
solar_pos = loc.get_solarposition(times)

tracker_data = pvlib.tracking.singleaxis(
    apparent_zenith=solar_pos['apparent_zenith'],
    apparent_azimuth=solar_pos['azimuth'],
    axis_tilt=0,      # 水平軸
    axis_azimuth=180, # 南北方向
    max_angle=55,     # 最大回転角 ±55°
    backtrack=True,   # バックトラッキング有効
    gcr=0.35          # 地表カバー率 35%
)
```

`singleaxis` は各時刻の surface_tilt、surface_azimuth、aoi（入射角）、tracker_theta（回転角）を含む DataFrame を返します。

---

## 重要パラメータの詳細

### max_angle：最大回転角

トラッカーは無制限に回転できません。通常 ±45°～±60° に制限されます。この角度を超えると風荷重が急増し、構造的な安全リスクが上昇します。**推奨値：±55°**

### gcr：地表カバー率（Ground Coverage Ratio）

GCR = モジュール幅 / 列間距離。GCR が高いほど土地利用率は上がりますが、隣接列間の遮蔽も増えます。地上型発電所の典型値：0.3～0.4。

### backtrack：バックトラッキング

朝夕の太陽高度角が低い時間帯、前列が後列を遮蔽することがあります。バックトラッキングの戦略は：潜在的な遮蔽を検出した際に、**パネルを太陽と反対方向に回転させ**、入射角を若干犠牲にすることでアレイ全体を無遮蔽状態に保ちます。

```python
# GCR 別、夏至日早朝のバックトラッキング角度比較
june21 = pd.date_range('2025-06-21 06:00', '2025-06-21 09:00', freq='30min', tz=tz)
sp21 = loc.get_solarposition(june21)

for gcr_val in [0.35, 0.50, 0.70]:
    td = pvlib.tracking.singleaxis(
        sp21['apparent_zenith'], sp21['azimuth'],
        axis_tilt=0, axis_azimuth=180,
        max_angle=55, backtrack=True, gcr=gcr_val
    )
    print(f'GCR={gcr_val}: 06:00 角度={td.surface_tilt.iloc[0]:.1f}°')
```

結果：GCR=0.35 では 06:30 に 54°まで回転可能（理想に近い）。GCR=0.70 では同じ時刻で 9° しか回転できません——高密度設置は大幅な妥協を強いられます。

---

## 年間発電増益シミュレーション

```python
# 固定架台 POA（30°南向き）
fixed_poa = pvlib.irradiance.get_total_irradiance(
    30, 180,
    solar_pos['apparent_zenith'], solar_pos['azimuth'],
    cs['dni'], cs['ghi'], cs['dhi']
)

# トラッカー POA（fillna で夜間 NaN を処理）
tracker_poa = pvlib.irradiance.get_total_irradiance(
    tracker_data['surface_tilt'].fillna(0),
    tracker_data['surface_azimuth'].fillna(180),
    solar_pos['apparent_zenith'], solar_pos['azimuth'],
    cs['dni'], cs['ghi'], cs['dhi']
)

fixed_annual   = fixed_poa['poa_global'].clip(0).sum() / 1000
tracker_annual = tracker_poa['poa_global'].clip(0).sum() / 1000
gain = (tracker_annual / fixed_annual - 1) * 100

print(f'固定架台: {fixed_annual:.1f} kWh/m²')
print(f'トラッカー: {tracker_annual:.1f} kWh/m²')
print(f'増益: +{gain:.1f}%')
# 出力：固定架台: 2469.2  トラッカー: 2847.5  増益: +15.3%
```

---

## 驚き！冬季はトラッカーが負の増益に

月次データが直感に反する現象を明らかにします：

| 月 | 固定架台 $\text{kWh/m}^2$ | トラッカー $\text{kWh/m}^2$ | 増益 |
|----|----------------|------------------|------|
| 1月 | 194.4 | 176.1 | **-9.4%** |
| 3月 | 226.2 | 257.9 | +14.0% |
| 6月 | 207.8 | 290.1 | **+39.6%** |
| 9月 | 205.4 | 238.6 | +16.2% |
| 11月 | 184.9 | 172.6 | -6.7% |
| 12月 | 185.3 | 161.6 | **-12.8%** |

**なぜ冬季にトラッカーが損をするのか？**

冬は太陽の軌道が低く短くなります。上海（北緯31°）では：
1. **固定30°傾斜が冬季最適に近い**：冬至の正午太陽高度角 ≈ 35°、30°傾斜で直達日射を十分に受けられる
2. **散乱日射の利用率が低下**：散乱日射は全方向から来るため、トラッカーが大角度に回転すると散乱光を受ける立体角が減少する
3. **バックトラッキングが回転角を抑制**：朝夕の太陽高度角が極めて低い時間帯に、バックトラッキングが強制的に角度を制限し、追尾効果が低下する

**エンジニアリング上の結論**：単軸トラッカーの価値は主に春夏秋の3シーズンから生まれます。高緯度地域（>40°N）では冬季の負の増益がより顕著になるため、年間を通じた ROI 評価が必要です。

---

## 完全な実行可能コード

```python
import pvlib
import pvlib.tracking, pvlib.irradiance, pvlib.location
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

lat, lon, tz = 31.23, 121.47, 'Asia/Shanghai'
times = pd.date_range('2025-01-01', '2025-12-31 23:00', freq='1h', tz=tz)
loc = pvlib.location.Location(lat, lon, tz=tz, altitude=5)
cs = loc.get_clearsky(times)
solar_pos = loc.get_solarposition(times)

# 固定架台
fixed_poa = pvlib.irradiance.get_total_irradiance(
    30, 180, solar_pos['apparent_zenith'], solar_pos['azimuth'],
    cs['dni'], cs['ghi'], cs['dhi']
)

# 単軸トラッカー
tracker = pvlib.tracking.singleaxis(
    solar_pos['apparent_zenith'], solar_pos['azimuth'],
    axis_tilt=0, axis_azimuth=180, max_angle=55, backtrack=True, gcr=0.35
)
tracker_poa = pvlib.irradiance.get_total_irradiance(
    tracker['surface_tilt'].fillna(0), tracker['surface_azimuth'].fillna(180),
    solar_pos['apparent_zenith'], solar_pos['azimuth'],
    cs['dni'], cs['ghi'], cs['dhi']
)

# 月次比較
fixed_m   = fixed_poa['poa_global'].clip(0).resample('ME').sum() / 1000
tracker_m = tracker_poa['poa_global'].clip(0).resample('ME').sum() / 1000
gain_m = (tracker_m / fixed_m - 1) * 100
print(gain_m.round(1).rename('月次増益(%)'))
```

---

## クイックリファレンスカード 🗂️

| ポイント | 内容 |
|---------|------|
| singleaxis コアパラメータ | axis_tilt / max_angle / gcr / backtrack |
| 年間平均増益（上海） | **+15.3%**（晴天モデル、実測値 約12-18%） |
| 最高増益月 | 6月 **+39.6%**、直達日射比率が高い |
| 負の増益月 | 12月 **-12.8%**、固定傾斜が既に冬季最適に近い |
| バックトラッキングの本質 | GCR が大きいほど朝の回転が抑制される；GCR=0.7 では朝の角度が<10° |
| API の注意点 | 夜間 NaN に fillna(0)/fillna(180) を適用しないと get_total_irradiance がエラー |
| pvlib バージョン | 0.15.0 では pvlib.mounting は存在せず、pvlib.tracking を直接使用 |
