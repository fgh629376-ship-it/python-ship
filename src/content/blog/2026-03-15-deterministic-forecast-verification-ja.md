---
title: '太陽光発電予測の検証完全ガイド — あなたのモデルは本当に良いのか？Murphyの三次元が答える'
description: '確定的予測検証の深掘り：Skill ScoreとCLIPER参照方法、Murphy-Winkler分布指向フレームワーク、MSE分解、品質-一貫性-価値の三次元評価'
category: solar
series: solar-book
lang: ja
pubDate: '2026-03-15'
tags: ["予測検証", "skill score", "Murphy-Winkler", "MSE分解", "太陽光予測"]
---

## あなたの予測モデルは良いのか？その質問は想像の100倍難しい

太陽光予測をする人なら誰でもRMSEを計算できます。しかし知らないかもしれません：**RMSEが最低の予測が必ずしも最良ではない**のです。古典的なシミュレーション実験（Yang & Kleissl, 2024）では、3人の予測者がそれぞれ異なる指標で「最優秀」になりました。

> 本記事は *Solar Irradiance and Photovoltaic Power Forecasting* (CRC Press, 2024) Chapter 9 に基づく

---

## 1. Skill Score — 誤差ではなく「どれだけ基準を超えたか」

### 1.1 なぜSkill Scoreが必要か

生のRMSEには致命的な欠点があります：**場所や期間によって予測難易度が異なる**。砂漠でRMSE=50 W/m²は悪い結果かもしれませんが（ほぼ常に晴天）、曇りの多い地域でRMSE=100 W/m²は優秀かもしれません。

$$S^* = 1 - \frac{S_{\text{fcst}}}{S_{\text{ref}}}$$

### 1.2 三つの参照方法

| 方法 | 原理 | 適用 |
|------|------|------|
| **Persistence** | 最新の観測値を予測に | 短時間（<3h） |
| **Climatology** | 長期平均値を予測に | 長時間（>6h） |
| **CLIPER** | 両者の最適凸結合 | **全時間帯（推奨）** |

CLIPERの最適重み：$\alpha_{\text{optimal}} = \gamma_h$（ラグh自己相関係数）

数学的証明：**CLIPERはpersistenceとclimatologyの両方以下にならないことが保証される。**

> Yang (2019) が太陽予測コミュニティに導入したが、2024年時点でもほとんどの論文はsmart persistenceを使用。

### 1.3 必ずκ（晴天指数）上で操作

$\kappa$ = 観測値 / 晴天モデル出力。GHI上で直接適用すると**skill scoreが過大評価**される（日変化パターンは「無料の」予測可能性）。

---

## 2. 指標ベース検証の致命的限界

### 2.1 古典実験：3人の予測者、3人の「チャンピオン」

| 予測者 | 戦略 | MBE | MAE | RMSE |
|--------|------|-----|-----|------|
| Novice | 持続性 | **-2.85** ✓ | 79.63 | 142.36 |
| Optimist | 定数0.95 | 36.19 | **57.68** ✓ | 119.81 |
| Statistician | 条件付き平均 | 8.72 | 63.02 | **111.77** ✓ |

**各予測者が1つの指標で「勝者」。** どの指標を選ぶかで結論が完全に変わります。

### 2.2 解決策

**予測-観測ペアを報告**する。要約統計量だけでなく、読者が自分で検証できるように。

---

## 3. Murphy-Winkler 分布指向検証フレームワーク

同時分布 $f(x,y)$ は検証に必要な**すべての情報**を含む。

### 3.1 二つの分解

**Calibration-Refinement分解**: $f(x,y) = f(y|x) \cdot f(x)$
- $f(y|x)$ → **校正性**: $E(Y|X=x) = x$ が完全校正
- $f(x)$ → **分解能**: 予測値の多様性が高いほど良い

**Likelihood-Base Rate分解**: $f(x,y) = f(x|y) \cdot f(y)$
- $f(x|y)$ → **一貫性**: $E(X|Y=y) = y$ が完全一貫
- $f(y)$ → **基準率**: 観測の周辺分布

### 3.2 MSE分解

**COF分解**：

$$\text{MSE} = V(Y) + E_X[X - E(Y|X)]^2 - E_X[E(Y|X) - E(Y)]^2$$

即ち：$\text{MSE} = \text{観測分散} + \text{Type 1 条件バイアス（最小化）} - \text{分解能（最大化）}$

**COX分解**：

$$\text{MSE} = V(X) + E_Y[Y - E(X|Y)]^2 - E_Y[E(X|Y) - E(X)]^2$$

即ち：$\text{MSE} = \text{予測分散} + \text{Type 2 条件バイアス（最小化）} - \text{識別力（最大化）}$

4つの次元、4つの目標 — 単一の指標ではすべてを捉えられない。

---

## 4. ケーススタディ：ECMWF HRES vs NCEP NAM

SURFRAD 3地点、2020年、日前GHI予測。

### 主要発見

1. **どちらのモデルもすべての品質次元で優位ではない** — 多次元評価が不可欠
2. **訓練目標は評価指標と一致する必要がある**（一貫性）
3. **品質と価値の対応は非線形**：MAE 9%の差 → 罰金5倍の差
4. **MAPE最適の予測が最高の罰金を受ける** → MAPEは太陽光予測に使ってはいけない

---

## 5. 実践チェックリスト

1. 参照方法：CLIPERを使用（smart persistenceではなく）
2. κ上で操作：すべてを晴天指数空間で計算
3. 散布図を描く：整合性、外れ値、全体バイアスを確認
4. 予測-観測ペアを報告：再現可能な検証を実現
5. Murphy-Winkler分解：校正/分解能/Type 2バイアス/識別力
6. 一貫性を確保：訓練目標 = 評価指標 = 系統罰則ルール
7. 価値を定量化：実際の罰則スキームで経済損失を算出

---

## 参考文献

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press. Ch. 9.
- Murphy, A.H. & Winkler, R.L. (1987). *Monthly Weather Review*, 115, 1330-1338. (Q1)
- Murphy, A.H. (1993). *Weather and Forecasting*, 8(2), 281-293. (Q1)
- Yang, D. et al. (2020). *Solar Energy*, 210, 20-37. (Q1)
- Kolassa, S. (2020). *International Journal of Forecasting*, 36(1), 208-211. (Q1)
