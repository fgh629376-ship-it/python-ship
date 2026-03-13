---
title: 'pvlib 温度モデルと DC 電力計算 — 日射量からワットへ'
description: 'pvlib のセル温度モデル（SAPM/PVsyst/Faiman）と DC 電力モデル（SAPM/CEC/PVWatts）を深く理解する。完全なコード比較付き。'
category: solar
pubDate: '2026-03-13'
lang: ja
tags: ["pvlib", "光伏", "温度模型", "DC功率", "技術干货"]
---

## 日射量がパネルに届いた後、次は何をするのか？

前回の記事では POA 日射量を計算しました。しかし日射量はそのままでは電力ではありません。中間には2つの重要なステップがあります：**セル温度計算**と**電気モデル変換**です。

温度が高いほどモジュール効率は低下します。これは無視できません——夏の高温によって発電量が10%以上低下することがあります。

---

## I. なぜ温度がそれほど重要なのか？

シリコン系太陽光発電モジュールの温度係数は一般的に **-0.3% ～ -0.5% /°C** です。

- STC（標準試験条件）：セル温度 25°C
- 実際の運転：夏の正午にはセル温度が **60-70°C** に達することがある
- 温度上昇 40°C × (-0.4%/°C) = **発電量16%低下**

これが pvlib に4種類の温度モデルがある理由です——温度を正確に計算することで、予測が正確になります。

---

## II. 4種類の温度モデルの比較

### SAPM モデル（Sandia）

業界で最も広く使われている経験的モデルです：

```python
import pvlib

# パラメータセット
params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]
print("利用可能なパラメータセット:", list(params.keys()))
# open_rack_glass_glass, close_mount_glass_glass,
# open_rack_glass_polymer, insulated_back_glass_polymer

# セル温度を計算
temp_params = params["open_rack_glass_glass"]
t_cell = pvlib.temperature.sapm_cell(
    poa_global=1000,   # W/m²
    temp_air=32,       # °C
    wind_speed=1.5,    # m/s
    **temp_params       # a, b, deltaT
)
print(f"SAPM セル温度: {t_cell:.1f}°C")  # ≈63.6°C
```

**パラメータの意味：**
- `a`, `b`：POA と風速がモジュール背面温度に与える影響を表す経験係数
- `deltaT`：セルと背面の温度差

### PVsyst モデル

熱収支に基づく物理モデルです：

```python
t_pvsyst = pvlib.temperature.pvsyst_cell(
    poa_global=1000,
    temp_air=32,
    wind_speed=1.5,
    u_c=29.0,   # 定常熱損失係数 W/(m²·K)
    u_v=0.0     # 風速依存熱損失係数
)
print(f"PVsyst セル温度: {t_pvsyst:.1f}°C")  # ≈60.1°C
```

### Faiman モデル

2パラメータの簡略熱収支モデルです：

```python
t_faiman = pvlib.temperature.faiman(
    poa_global=1000,
    temp_air=32,
    wind_speed=1.5,
    u0=25.0,    # 定常放熱係数
    u1=6.84     # 風速放熱係数
)
print(f"Faiman セル温度: {t_faiman:.1f}°C")  # ≈60.5°C
```

### Ross モデル

最もシンプルな線形モデルです：

```python
t_ross = pvlib.temperature.ross(
    poa_global=1000,
    temp_air=32,
    noct=45      # 公称動作セル温度（NOCT）
)
print(f"Ross セル温度: {t_ross:.1f}°C")  # ≈63.4°C
```

### モデル比較まとめ

| モデル | パラメータ数 | 精度 | 計算量 | 適用場面 |
|--------|-----------|------|--------|---------|
| **SAPM** | 3 | ⭐⭐⭐⭐ | 低 | 汎用最初の選択 |
| **PVsyst** | 2 | ⭐⭐⭐⭐ | 低 | PVsyst ユーザー |
| **Faiman** | 2 | ⭐⭐⭐⭐ | 最低 | 簡易推定 |
| **Ross** | 1 | ⭐⭐⭐ | 最低 | NOCT が既知の場合 |
| **Fuentes** | 複数 | ⭐⭐⭐⭐⭐ | 高 | 高精度が必要な場合 |

---

## III. DC 電力モデル

温度が計算できたら、次は日射量と温度を DC 電力に変換します。

### SAPM モデル（最も高精度）

Sandia データベースの 14 以上のパラメータが必要です。523 モジュールが選択可能です。

### CEC / 単ダイオードモデル（エンジニアリング標準）

5つの電気パラメータを用いて単ダイオード方程式を解きます：

```python
cec_modules = pvlib.pvsystem.retrieve_sam("CECMod")
module = cec_modules["Canadian_Solar_Inc__CS5P_220M"]

# 5パラメータを計算（運転条件によって変化）
IL, I0, Rs, Rsh, nNsVt = pvlib.pvsystem.calcparams_cec(
    effective_irradiance=1000,
    temp_cell=50,
    alpha_sc=module["alpha_sc"],
    a_ref=module["a_ref"],
    I_L_ref=module["I_L_ref"],
    I_o_ref=module["I_o_ref"],
    R_sh_ref=module["R_sh_ref"],
    R_s=module["R_s"],
    Adjust=module["Adjust"]
)

# I-V 特性を解く
result = pvlib.pvsystem.singlediode(IL, I0, Rs, Rsh, nNsVt)
print(f"Pmpp: {result['p_mp']:.1f} W")
print(f"Voc:  {result['v_oc']:.2f} V")
print(f"Isc:  {result['i_sc']:.3f} A")
```

### PVWatts モデル（簡易推定）

2つのパラメータのみ必要です：

```python
dc_power = pvlib.pvsystem.pvwatts_dc(
    g_poa_effective=1000,   # 有効 POA W/m²
    temp_cell=50,           # セル温度 °C
    pdc0=220,               # STC 定格電力 W
    gamma_pdc=-0.004        # 温度係数 1/°C
)
print(f"PVWatts DC 電力: {dc_power:.1f} W")
# 220 * (1000/1000) * (1 + (-0.004) * (50-25)) = 198 W
```

### 異なる運転条件での実測比較

| 条件 | POA | Tc | Pmpp | FF |
|------|-----|-----|------|-----|
| STC 標準 | 1000 | 25°C | 220.0W | 0.726 |
| 曇り | 800 | 25°C | 177.6W | 0.740 |
| 高温 | 1000 | 50°C | 193.0W | 0.695 |
| 冬季低日射 | 500 | 15°C | 117.0W | 0.770 |
| 夜明け/夕暮れ | 200 | 10°C | 47.2W | 0.792 |

---

## IV. 重要な洞察

1. **充填率（FF）は温度上昇とともに低下する**：高温時は内部抵抗が増大し、FF が 0.77 から 0.70 に低下する
2. **低日射下では FF がむしろ高い**：電流が小さいため、抵抗損失の割合が小さい
3. **PVWatts と CEC の年間発電量差は約10-15%**：CEC の方が高精度のため、エンジニアリングプロジェクトでは CEC を推奨

---

## クイックリファレンスカード 📋

| ポイント | 内容 |
|---------|------|
| **温度の影響** | -0.4%/°C；夏季は発電量を10-16%低下させることがある |
| **温度モデル** | SAPM が汎用最初の選択；PVsyst/Faiman は簡略代替 |
| **DC モデル** | SAPM（14パラメータ）> CEC（6パラメータ）> PVWatts（2パラメータ） |
| **単ダイオード** | IL/I0/Rs/Rsh/nNsVt の5パラメータが運転条件によって動的に変化 |
| **充填率** | 0.70-0.79；温度上昇により FF が低下し効率が落ちる |
| **CEC データベース** | 21,535 モジュールのパラメータセット；エンジニアリング用途に最適 |

> **次回予告：** pvlib インバーターモデル — Sandia/ADR/PVWatts 3大モデルの比較実践
