---
title: "🔬 pvlib 深掘り：日射分解と傾斜面変換——GHI から傾斜面までの完全モデリングチェーン"
description: "光発電モデリングチェーンの中で最もエラーが生じやすいステップ。GHI → DNI + DHI（分解）→ POA（変換）：各ステップに複数のモデルが存在する。本記事では pvlib に実装された 8 種の分解モデルと 7 種の変換モデルについて、数学的原理・物理的仮定・適用場面・選択戦略を徹底解説する。"
pubDate: 2026-03-16
lang: ja
category: solar
series: pvlib
tags: ['pvlib', '日射量', '分解モデル', '変換モデル', 'Perez', 'Erbs', 'DISC']
---

## はじめに：日射分解と傾斜面変換が必要な理由

太陽光パネルは水平に設置されていない——北半球では通常、南向きに 20°〜40° 傾けて設置される。しかし、世界の地上日射観測点の大多数は**水平面全天日射量 GHI**（Global Horizontal Irradiance）しか計測していない。GHI からパネル面上の日射量 POA（Plane of Array）を求めるには、2 段階の変換が必要である：

$$\text{GHI} \xrightarrow{\text{分解}} \text{DNI} + \text{DHI} \xrightarrow{\text{変換}} \text{POA}$$

この 2 ステップは単純に見えるが、それぞれで無視できない誤差が生じる。Gueymard & Ruiz-Arias (2016) が *Solar Energy*（中国科学院 Q1）に発表した研究によれば、分解モデルの選択だけで年間発電量推定値に 2〜5% の差が生じる可能性がある。100 MW の発電所であれば、これは数百万ドル規模の誤差に相当する。

---

## I. 基本概念

### 日射の 3 成分

| 成分 | 記号 | 物理的意味 | 測定機器 |
|------|------|-----------|---------|
| 水平面全天日射量 | GHI | 水平面が受ける太陽放射の合計 | 熱電堆型日射計（パイラノメータ） |
| 法線面直達日射量 | DNI | 太陽円盤方向からの放射 | 直達日射計（パイルへリオメータ）＋追尾装置 |
| 水平面散乱日射量 | DHI | 大気で散乱されて水平面に到達する放射 | シェーディングバンド／ボール型日射計 |

3 成分の関係式：

$$\text{GHI} = \text{DNI} \cdot \cos(\theta_z) + \text{DHI}$$

ここで $\theta_z$ は太陽天頂角。このクロージャー関係式がすべての分解モデルの数学的基盤となっている。

### 晴天度指数 $k_t$

$$k_t = \frac{\text{GHI}}{I_0 \cdot \cos(\theta_z)}$$

$k_t$ は GHI と大気圏外水平面日射量の比であり、範囲は [0, 1]。大気の透明度を総合的に表す指標である：
- $k_t \approx 0.7$〜$0.8$：晴天
- $k_t \approx 0.3$〜$0.5$：薄曇り
- $k_t < 0.2$：曇天／荒天

**ほぼすべての分解モデルは $k_t$ の関数として定式化されている**——経験的関係式を通じて $k_t$ から散乱比 $k_d = \text{DHI}/\text{GHI}$ を推定する。

---

## II. 分解モデルの詳細解析

### 2.1 第 1 世代：単純な経験的関係式

#### Orgill & Hollands (1977)

最初期の分解モデルの一つ。トロントの 4 年分の時間データに基づく。区分線形関係式を用いる：

$$k_d = \begin{cases} 1 - 0.249k_t & k_t < 0.35 \\ 1.557 - 1.84k_t & 0.35 \leq k_t \leq 0.75 \\ 0.177 & k_t > 0.75 \end{cases}$$

**物理的意味**：
- $k_t$ が低い（曇天）：ほぼすべて散乱光、$k_d \approx 1$
- $k_t$ が高い（晴天）：散乱比が〜18% まで低下
- 中間領域：線形遷移

**限界**：単一観測点のデータのみを使用しており、熱帯・乾燥地域では精度が低下する。

#### Erbs et al. (1982)

pvlib のデフォルト分解モデル。Orgill & Hollands を改良し、より多くの観測点データを使用した 4 次多項式で中間域を近似する：

$$k_d = \begin{cases} 1 - 0.09k_t & k_t \leq 0.22 \\ 0.9511 - 0.1604k_t + 4.388k_t^2 - 16.638k_t^3 + 12.336k_t^4 & 0.22 < k_t \leq 0.80 \\ 0.165 & k_t > 0.80 \end{cases}$$

**pvlib 実装における重要点**：
- `min_cos_zenith=0.065`（天頂角 > 86.3° で打ち切り、ゼロ除算を回避）
- `max_zenith=87`（太陽が地平線付近のとき DNI を 0 に設定）
- クロージャー関係式 $\text{DNI} = (\text{GHI} - \text{DHI})/\cos(\theta_z)$ を使って DNI を逆算

**重要な問題点**：$k_t = 0.22$ および $k_t = 0.80$ で導関数が不連続（関数値は連続だが 1 階微分は不連続）。最適化アルゴリズムで問題となる可能性がある。

#### Erbs-Driesse（2024 改良版）

Driesse が Erbs モデルを再パラメータ化し、区分関数を滑らかな関数で置き換えた。**変曲点において関数値と 1 階微分の両方が連続**であることを保証する。これは勾配法による最適化や自動微分（PyTorch/JAX）において極めて重要である。

```python
import pvlib
# 従来の Erbs（区分関数、微分不連続）
result_erbs = pvlib.irradiance.erbs(ghi, zenith, doy)

# Erbs-Driesse（滑らか、微分可能）
result_driesse = pvlib.irradiance.erbs_driesse(ghi, zenith, doy)
```

### 2.2 第 2 世代：物理増強型

#### DISC (Maxwell 1987)

Direct Insolation Simulation Code。散乱比を直接推定するのではなく、**直達晴天度指数 $k_n$** を通じて DNI を推定する：

$$k_n = \frac{\text{DNI}}{I_0}$$

その後、クロージャー関係式から DHI を逆算する。DISC モデルは $k_t$ と大気光路長 AM の 2 次元関係を使用し、純粋な $k_t$ モデルより物理的な次元を一つ加えている——大気光学的経路長の影響を考慮する。

#### DIRINT (Perez et al. 1992)

DISC の改良版で、2 つの追加入力を取り込む：
1. **GHI の時系列変動**：前後時刻の $k_t$ 変化率（雲の動的情報）
2. **露点温度**：大気水蒸気量の代理変数

この 2 つの情報により、「薄い雲による均一散乱」と「厚い雲の破砕チャンネル効果」を区別できる——同じ瞬間的な $k_t$ を示しながら、DNI/DHI の比率が全く異なる 2 つの状況を識別する。

**pvlib 実装**：
```python
# DIRINT はより多くの入力を必要とするが精度が高い
dni = pvlib.irradiance.dirint(
    ghi, zenith, times,
    pressure=101325,           # 気圧
    use_delta_kt_prime=True,   # 時系列安定性指標を使用
    temp_dew=10                # 露点温度
)
```

#### DIRINDEX (Perez 2002)

DIRINT に**晴天モデル情報**を追加したモデル。Ineichen 晴天 GHI を使って晴天晴天度指数を計算し、実際の $k_t$ と比較する——大きな偏差は雲の存在を示し、小さな偏差はエアロゾルや水蒸気による減衰を示す。

**これが重要な理由**：雲とエアロゾルはどちらも GHI を低下させるが、DNI/DHI の比率への影響は全く異なる——雲は主に散乱を増加させ、エアロゾルは散乱と吸収を同時に増加させる。

### 2.3 第 3 世代：ロジスティック回帰

#### Boland (2008/2013)

区分関数をロジスティック回帰で置き換える：

$$k_d = \frac{1}{1 + e^{-a(k_t - b)}}$$

パラメータは $a$ と $b$ の 2 つだけで、関数は自然に滑らかかつ連続である。Boland モデルの優雅さは次の点にある：
- 物理的制約 $k_d \in [0, 1]$ を自動的に満たす
- 異なる気候帯向けにパラメータを再フィッティング可能
- 至るところで微分可能であり、最適化に適している

---

## III. 変換モデルの詳細解析

分解が完了すると、DNI・DHI・GHI が得られる。次のステップは傾斜面上の日射量 POA を計算することである：

$$\text{POA} = \text{POA}_{beam} + \text{POA}_{diffuse} + \text{POA}_{ground}$$

直達成分 $\text{POA}_{beam} = \text{DNI} \cdot \cos(\text{AOI})$ は純粋な幾何計算である。地面反射 $\text{POA}_{ground} = \text{GHI} \cdot \rho \cdot (1 - \cos\beta)/2$ も比較的単純である。**核心的な課題は天空散乱放射の角度分布モデルにある。**

### 3.1 等方性モデル（Liu-Jordan 1963）

最も単純な仮定：天空の散乱放射は一様に分布している。

$$\text{POA}_{diffuse} = \text{DHI} \cdot \frac{1 + \cos\beta}{2}$$

**物理的限界**：実際の天空散乱放射は一様ではない——太陽周辺には周日輝（circumsolar radiation）が存在し、地平線付近には増輝（horizon brightening）がある。等方性モデルは POA を系統的に 5〜10% 過小評価する。

### 3.2 Klucher (1979)

等方性モデルに周日輝と地平線増輝の変調因子を加える：

$$\text{POA}_{diffuse} = \text{DHI} \cdot \frac{1 + \cos\beta}{2} \cdot \left[1 + F\sin^3\left(\frac{\beta}{2}\right)\right] \cdot \left[1 + F\cos^2(\theta)\sin^3(\theta_z)\right]$$

ここで $F = 1 - (k_d)^2$ は非等方性強度因子。晴天では $F$ が大きく（非等方性が強い）、曇天では $F$ が小さく（等方性に近づく）なる。

### 3.3 Hay-Davies (1980)

**非等方性指数** $A_I$ を導入する：

$$A_I = \frac{\text{DNI}}{I_0}$$

散乱放射を 2 つの成分に分ける：周日輝（$A_I$ の割合、太陽方向）＋等方性背景（$1 - A_I$ の割合）。

$$\text{POA}_{diffuse} = \text{DHI} \left[A_I \cdot R_b + (1 - A_I) \cdot \frac{1 + \cos\beta}{2}\right]$$

$R_b = \cos(\text{AOI})/\cos(\theta_z)$ は直達放射の幾何変換係数。

### 3.4 Perez (1987/1990)

最も複雑で最も高精度のモデル。天空散乱放射を**3 成分**に分割する：

$$\text{POA}_{diffuse} = \text{DHI} \left[(1 - F_1)\frac{1 + \cos\beta}{2} + F_1\frac{a}{b} + F_2\sin\beta\right]$$

- $(1-F_1)$：等方性背景
- $F_1 \cdot a/b$：周日輝（$a = \max(0, \cos\text{AOI})$、$b = \max(\cos 85°, \cos\theta_z)$）
- $F_2 \cdot \sin\beta$：地平線増輝

$F_1$ と $F_2$ は 2 つの天空輝度パラメータ（$\varepsilon$ と $\Delta$）をルックアップテーブルから参照して決定される——8 天空区分 × 6 係数 = 48 個の経験係数。

**Perez-Driesse（2024）** の改良：ルックアップテーブルを 2 次スプラインで置き換え、天空区分の切り替え時の不連続性を解消した。

### 3.5 モデル選択ガイド

| シナリオ | 推奨モデル | 理由 |
|---------|-----------|------|
| 概算／教育目的 | Isotropic | 最も単純；物理的直感を養う |
| 一般的な工学設計 | Hay-Davies | 精度と複雑さのバランスが良い |
| 精密な発電量推定 | Perez 1990 | 業界標準；PVsyst などの商用ソフトで採用 |
| 最適化／自動微分 | Perez-Driesse | 滑らかで微分可能；PyTorch/JAX に対応 |
| 入力データが極めて少ない | Erbs + Isotropic | 最小限の入力で動作 |

---

## IV. 完全なコード例

```python
import pvlib
import pandas as pd
import numpy as np
from pvlib.location import Location

# 地点の定義：北京
site = Location(39.9, 116.4, tz='Asia/Shanghai', altitude=50)

# 1 日分の時系列を生成
times = pd.date_range('2025-06-21 04:00', '2025-06-21 20:00',
                       freq='1min', tz='Asia/Shanghai')
solpos = site.get_solarposition(times)

# 晴天 GHI（Ineichen-Perez モデル）
cs = site.get_clearsky(times, model='ineichen')
ghi = cs['ghi']

# === ステップ 1：分解（GHI → DNI + DHI）===
# 方法 A：Erbs（シンプル、デフォルト）
erbs_result = pvlib.irradiance.erbs(ghi, solpos['zenith'], times)

# 方法 B：DIRINT（高精度、追加入力が必要）
dirint_dni = pvlib.irradiance.dirint(
    ghi, solpos['zenith'], times,
    pressure=101325, temp_dew=15
)

# === ステップ 2：変換（DNI + DHI → POA）===
surface_tilt = 30
surface_azimuth = 180  # 南向き

# 方法 A：等方性（最もシンプル）
poa_iso = pvlib.irradiance.get_total_irradiance(
    surface_tilt, surface_azimuth,
    solpos['apparent_zenith'], solpos['azimuth'],
    erbs_result['dni'], ghi, erbs_result['dhi'],
    model='isotropic'
)

# 方法 B：Perez（最も高精度）
poa_perez = pvlib.irradiance.get_total_irradiance(
    surface_tilt, surface_azimuth,
    solpos['apparent_zenith'], solpos['azimuth'],
    erbs_result['dni'], ghi, erbs_result['dhi'],
    model='perez', airmass=site.get_airmass(times)['airmass_relative']
)

# 差異を比較
diff_pct = (poa_perez['poa_global'] - poa_iso['poa_global']) / poa_iso['poa_global'] * 100
print(f"Perez vs Isotropic 日平均差異: {diff_pct.mean():.1f}%")
print(f"Perez POA 日積算日射量: {poa_perez['poa_global'].sum() / 60 / 1000:.2f} kWh/m²")
```

---

## V. 誤差伝播解析

分解と変換の誤差は**乗法的に伝播する**：

$$\sigma_{\text{POA}}^2 \approx \sigma_{\text{decomp}}^2 + \sigma_{\text{trans}}^2 + 2\rho\sigma_{\text{decomp}}\sigma_{\text{trans}}$$

Yang (2016) が *Solar Energy*（Q1）に発表した分析によれば：
- 分解モデルの典型的な MBE：±2〜5%（気候帯に依存）
- 変換モデルの典型的な MBE：±1〜3%
- **組み合わせ誤差**：最悪の場合 ±8% に達する

**最も危険なシナリオ**：高緯度の冬季・低太陽高度角＋曇天 → 分解モデルが低 $k_t$ 域で最大の不確実性を示し、同時に大きな入射角が変換誤差を増幅させる。

---

## VI. Warner 教科書との関連

Warner 第 4 章では放射パラメータ化スキームを扱っている——NWP モデルは各グリッド点で放射輸送を計算し、その出力が GHI/DNI/DHI となる。しかし NWP の解像度は 3〜25 km であるのに対し、太陽光発電所が必要とするのは**パネル面上**の日射量である。

pvlib の分解＋変換モデルは、まさに NWP 出力と光発電モデリングを繋ぐ橋渡し役を担っている：
- NWP が GHI を出力 → pvlib が DNI + DHI に分解 → POA に変換 → 発電量モデル
- Warner 第 13 章の MOS 後処理は GHI 予報に適用可能（系統的バイアスの除去）
- 分解モデルの誤差は NWP → PV 予測チェーンにおける**無視できない誤差源**の一つである

---

## 参考文献

1. Erbs, D.G., Klein, S.A. & Duffie, J.A. (1982). Estimation of the diffuse radiation fraction for hourly, daily and monthly-average global radiation. *Solar Energy*, 28(4), 293-302.
2. Perez, R. et al. (1990). Modeling daylight availability and irradiance components from direct and global irradiance. *Solar Energy*, 44(5), 271-289.
3. Maxwell, E.L. (1987). A quasi-physical model for converting hourly GHI to DNI. *SERI/TR-215-3087*.
4. Perez, R. et al. (1992). Dynamic global-to-direct irradiance conversion models (DIRINT). *ASHRAE Trans.*, 98, 354-369.
5. Boland, J. et al. (2008). Modelling the diffuse fraction of global solar radiation on a horizontal surface. *Environmetrics*, 19, 120-136.
6. Gueymard, C.A. & Ruiz-Arias, J.A. (2016). Extensive worldwide validation and climate sensitivity analysis of direct irradiance predictions from 1-min global irradiance. *Solar Energy*, 128, 1-30.
7. Yang, D. (2016). Solar radiation on inclined surfaces: Corrections and benchmarks. *Solar Energy*, 136, 288-302.
8. Driesse, A. & Stein, J.S. (2024). Reformulation of the Erbs and Perez diffuse irradiance models for improved continuity. *pvlib documentation*.
