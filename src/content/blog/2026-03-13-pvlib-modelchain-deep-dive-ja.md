---
title: 'pvlib ModelChain 徹底解説：10ステップ損失チェーンとカスタム拡張の実践'
description: 'pvlib ModelChain の内部呼び出しチェーンを深く理解し、9つの置き換え可能なモデルノードを分解。カスタム losses_model による汚損/ミスマッチ/配線損失の適用実践と、インバーター容量不足によるクリッピングの落とし穴を解説します。'
category: solar
series: pvlib
pubDate: '2026-03-13'
lang: ja
tags: ["pvlib", "光伏", "ModelChain", "仿真", "技術干货"]
---

## はじめに

pvlib の `ModelChain` はシミュレーションフレームワーク全体のオーケストレーションエンジンです。十数個の独立したモデルを一本のパイプラインに繋ぎ合わせ、`run_model()` を一行呼び出すだけで気象データから AC 出力まで全工程を処理します。

しかし多くの方は「サンプルを動かす」だけで、内部で何が行われているか、どうカスタマイズするかを理解していません。本記事では ModelChain を分解して詳しく見ていきます。

---

## 呼び出しチェーン全体像（pvlib 0.15）

`_run_from_effective_irrad` のソースコードから抽出した ModelChain 内部の実行順序：

```
transposition → aoi → spectral → effective_irradiance
    → temperature → dc → dc_ohmic → losses → ac
```

**9つの置き換え可能なモデルノード**（ModelChain の属性に対応）：

| 属性名 | デフォルト値 | 役割 |
|---|---|---|
| `transposition_model` | `haydavies` | GHI/DNI/DHI → POA |
| `aoi_model` | `sapm_aoi_loss` | 入射角補正 |
| `spectral_model` | `sapm_spectral_loss` | スペクトル補正 |
| `temperature_model` | `sapm_temp` | セル温度 |
| `dc_model` | `sapm` | DC 電力（I-V 曲線） |
| `dc_ohmic_model` | `no_dc_ohmic_loss` | DC オーム損失 |
| `losses_model` | `no_extra_losses` | カスタム追加損失 |
| `ac_model` | `sandia_inverter` | インバーター DC$\rightarrow$AC |

各ノードは置き換え可能です。文字列を渡すと組み込みモデルを使用し、関数を渡すと完全なカスタマイズが可能です。

---

## 標準シミュレーションのクイックセットアップ

```python
import pvlib
import pandas as pd
import numpy as np

# 場所：上海
location = pvlib.location.Location(
    latitude=31.2, longitude=121.5,
    tz='Asia/Shanghai', altitude=5, name='Shanghai'
)

# モジュール（Sandia データベース）
module_db = pvlib.pvsystem.retrieve_sam('SandiaMod')
module = module_db['Canadian_Solar_CS5P_220M___2009_']

# インバーター（容量の一致を確認！）
inverter_db = pvlib.pvsystem.retrieve_sam('SandiaInverter')
inverter = inverter_db['ABB__PVI_4_2_OUTD_S_US__208V_']  # 4.2kW

# モジュール温度パラメータ
temp_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
    'sapm']['open_rack_glass_glass']

# システム構築（10直列×2並列 = 4.39kWp）
array = pvlib.pvsystem.Array(
    mount=pvlib.pvsystem.FixedMount(surface_tilt=30, surface_azimuth=180),
    module_parameters=module,
    temperature_model_parameters=temp_params,
    modules_per_string=10,
    strings=2
)
system = pvlib.pvsystem.PVSystem(arrays=[array], inverter_parameters=inverter)

# ModelChain
mc = pvlib.modelchain.ModelChain(
    system=system, location=location,
    aoi_model='sapm', spectral_model='sapm'
)

# 気象データのシミュレーション（上海夏至）
times = pd.date_range('2025-06-21', periods=24, freq='1h', tz='Asia/Shanghai')
weather = pd.DataFrame({
    'ghi': [0,0,0,0,0,0,20,120,350,580,780,920,950,890,750,560,350,150,30,0,0,0,0,0],
    'dhi': [0,0,0,0,0,0,15,80,180,250,290,310,300,280,250,200,140,80,20,0,0,0,0,0],
    'dni': [0,0,0,0,0,0,30,180,480,720,880,980,1000,950,820,650,450,200,40,0,0,0,0,0],
    'temp_air': [28.0]*24,
    'wind_speed': [2.5]*24,
}, index=times)

mc.run_model(weather)
print(f'日間発電量: {mc.results.ac.clip(0).sum()/1000:.3f} kWh')
# → 日間発電量: 27.072 kWh
```

---

## 中間結果：損失チェーンのデータ

ModelChain は最終 AC 出力だけでなく、すべての中間ステップを `results` に記録します：

```python
poa    = mc.results.total_irrad['poa_global']  # 傾斜面日射量
eff    = mc.results.effective_irradiance        # 有効日射量（AOI+スペクトル補正後）
t_cell = mc.results.cell_temperature           # セル温度
dc     = mc.results.dc                         # DC 電力 DataFrame
ac     = mc.results.ac                         # AC 出力

daytime = poa > 50
print(f'POA 平均:          {poa[daytime].mean():.1f} W/m²')   # 700.2
print(f'有効日射量平均:    {eff[daytime].mean():.1f} W/m²')   # 689.9
print(f'透過率:            {(eff[daytime]/poa[daytime]).mean():.4f}')  # 0.9727
print(f'セル温度平均:      {t_cell[daytime].mean():.1f}°C')   # 48.9°C
print(f'インバーター効率:  {(ac[daytime]/dc["p_mp"][daytime]).mean():.4f}')  # 0.9514
```

夏至日の実測損失チェーン（28°C 環境、POA 平均 $700 \text{W/m}^2$）：

```
POA 700.2 W/m²
  → AOI+スペクトル: ×0.9727 → 有効日射量 689.9 W/m²  (-2.73%)
  → 温度効果:       48.9°C  → DC Pmpp 2567 W
  → インバーター:   ×0.9514 → AC 出力 2458 W           (-4.86%)
  → システム PR ≈ 79.7%
```

---

## 3つの実行エントリーポイント

ModelChain は異なるステージをスキップする3つのエントリーポイントを提供します：

```python
# エントリー1：GHI/DNI/DHI 気象データから（最も一般的、完全なパイプライン）
mc.run_model(weather)

# エントリー2：傾斜面 POA データから（転置ステップをスキップ）
# 用途：傾斜面日射計があり、実測 POA 値が既知の場合
poa_weather = pd.DataFrame({
    'poa_global': ..., 'poa_direct': ..., 'poa_diffuse': ...,
    'temp_air': ..., 'wind_speed': ...
}, index=times)
mc.run_model_from_poa(poa_weather)

# エントリー3：有効日射量から（転置+AOI+スペクトルをスキップ）
# 用途：AOI とスペクトル補正が外部で計算済みの場合
eff_weather = pd.DataFrame({
    'effective_irradiance': ...,
    'temp_air': ..., 'wind_speed': ...
}, index=times)
mc.run_model_from_effective_irradiance(eff_weather)
```

同一データでの3つのエントリーポイントの結果差異は <0.05% です。選択の基準は**データがどのステップから始まるか**です。

---

## カスタム losses_model：汚損/ミスマッチ/配線損失の適用

losses_model の呼び出しタイミング：**dc_model の後、ac_model の前**——これが DC 側のシステム損失を挿入する正しい位置です。

### 正しい実装方法

```python
def custom_dc_losses(mc_obj):
    """カスタム損失：汚損3% + ミスマッチ2% + 配線1%"""
    factor = (1 - 0.03) * (1 - 0.02) * (1 - 0.01)  # = 0.9412
    mc_obj.results.dc['p_mp'] *= factor
    mc_obj.results.dc['i_mp'] *= np.sqrt(factor)
    mc_obj.results.dc['v_mp'] *= np.sqrt(factor)

# ✅ 正しい：直接代入、pvlib が自動的に functools.partial としてラップ
mc.losses_model = custom_dc_losses
mc.run_model(weather)

kWh_loss = mc.results.ac.clip(0).sum() / 1000
# 結果：25.484 kWh（実際の損失 5.87%、理論値 5.89% — 完璧に一致）
```

### ⚠️ 3つの落とし穴

**落とし穴1：losses_model が変更するのは results.dc であり、results.ac ではない**

損失は AC 計算の前に適用されます。`mc_obj.results.ac` を変更しようとすると、その時点ではまだ `None` です。

**落とし穴2：インバーター容量不足により損失が「消える」ことがある**

システムが 4.39 kWp でインバーターが 250W（DC/AC 比 17.6:1）の場合、AC 出力は常に Paco でクリッピングされます。5.89% の DC 損失を適用しても AC 出力はほとんど変わりません（差異わずか 0.18%）——クリッピングされた電力はどちらにせよ捨てられるからです。**必ず DC/AC 比を先に確認してください！**

```python
# DC/AC 比の確認
stc_power = module['Impo'] * module['Vmpo'] * n_modules
ratio = stc_power / inverter['Paco']
print(f'DC/AC 比: {ratio:.2f}x')  # 適切な範囲：1.0~1.3
```

**落とし穴3：haydavies 転置モデルには dni_extra が必要**

```python
# ❌ エラー
poa = pvlib.irradiance.get_total_irradiance(..., model='haydavies')

# ✅ 正しい
from pvlib.irradiance import get_extra_radiation
dni_extra = get_extra_radiation(times)
poa = pvlib.irradiance.get_total_irradiance(..., model='haydavies', dni_extra=dni_extra)
```

---

## 温度モデルの比較

同一条件下での SAPM と PVsyst 温度モデルの差異：

```python
# SAPM 温度パラメータ（開放架台、ガラス-ガラス封止）
temp_sapm = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
# PVsyst 温度パラメータ（自立設置）
temp_pvs  = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['pvsyst']['freestanding']
```

28°C 環境での夏至日比較：

| 温度モデル | 平均セル温度 | 日間発電量 | 差異 |
|---|---|---|---|
| SAPM | 48.9°C | 27.072 kWh | 基準 |
| PVsyst | 47.6°C | 27.336 kWh | +0.97% |

PVsyst モデルはセル温度がやや低く、発電量がわずかに高くなります。どちらも妥当であり、選択は設置方法とメーカーデータの出典によります。

---

## クイックリファレンスカード

> **ModelChain = レゴブロック**
> 各ノードは独立して置き換え可能で、他はデフォルトのまま使えます。1つカスタマイズすれば、残り8つは無料で継承されます。

**完全な呼び出しチェーン**：
```
transposition → aoi → spectral → effective_irradiance
  → temperature → dc → dc_ohmic → losses → ac
```

**カスタマイズクイックリファレンス**：

| カスタマイズ目標 | 方法 |
|---|---|
| システム損失（汚損/ミスマッチ/配線） | `mc.losses_model = my_func` |
| 温度モデル | Array の `temperature_model_parameters` を変更 |
| インバーターモデル | `ModelChain(ac_model='pvwatts')` |
| 転置モデル | `ModelChain(transposition_model='perez')` |
| カスタム DC | `mc.dc_model = my_dc_func` |

**losses_model の関数シグネチャ**：`mc_obj` を受け取り、`mc_obj.results.dc` を変更し、戻り値は不要です。このパイプラインを覚えれば、カスタムコードをどこに挿入すべきかが常に分かります。
