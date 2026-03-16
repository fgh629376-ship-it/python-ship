---
title: "Box 時系列分析 Ch10：非線形モデルと長期記憶——GARCH、TAR、ARFIMA"
description: "Box『Time Series Analysis』第10章の精読：ARCH/GARCH条件付き異分散、閾値自己回帰TAR、長期記憶ARFIMA"
pubDate: 2026-03-16
lang: ja
series: box-timeseries
category: timeseries
tags: ["時系列", "GARCH", "非線形", "長期記憶", "ARFIMA", "教材ノート"]
---

# Box 時系列分析 Ch10：非線形モデルと長期記憶

> **教材**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 10

## 核心テーマ

Ch3-9のARIMAは**線形＋等分散**だった。Ch10はこの2つの仮定を破る。

---

## 10.1 ARCH/GARCH：条件付き異分散

### 問題

金融データの「ボラティリティクラスタリング」：大きな動きの後に大きな動きが続く（方向はランダム）、静穏期の後に静穏期が続く。ARMAは $\text{var}(a_t) = \sigma_a^2$ が一定と仮定し、この現象を捉えることができない。

### ARCH(s)モデル

$$h_t = \text{var}[a_t | a_{t-1}, \ldots] = \omega_0 + \sum_{i=1}^{s} \omega_i a_{t-i}^2$$

条件付き分散は過去の**ショックの二乗**に依存する。

### GARCH(s,r)モデル

$$h_t = \omega_0 + \sum_{i=1}^{s} \omega_i a_{t-i}^2 + \sum_{i=1}^{r} \beta_i h_{t-i}$$

GARCH(1,1) = 金融分野で最も広く使われるボラティリティモデル。

### 重要な性質

- $a_t$ は依然としてゼロ平均で無相関——しかし**独立ではない**
- 条件付き分散 $h_t$ は時間とともに変化するが、無条件分散 $\sigma_a^2 = \omega_0/(1 - \omega_1 - \beta_1)$ は一定（弱定常）
- 予測誤差分散が過去のボラティリティに合わせて調整 → **適応的予測区間**

---

## 10.2 非線形モデル

### TAR（閾値自己回帰）

$$z_t = \begin{cases} \phi_1^{(1)} z_{t-1} + \cdots + a_t & \text{if } z_{t-d} \leq r \\ \phi_1^{(2)} z_{t-1} + \cdots + a_t & \text{if } z_{t-d} > r \end{cases}$$

異なる「状態」（レジーム）で異なるARモデルを使用。**リミットサイクル**（極限閉軌道）挙動を生成できる。

### 双線形モデル

$$z_t = \sum \phi_i z_{t-i} + \sum \theta_j a_{t-j} + \sum \beta_{ij} z_{t-i} a_{t-j} + a_t$$

過去の値と過去のショックが交互に作用する。

---

## 10.3 長期記憶ARFIMA

### 問題

一部の系列はACFが非常にゆっくりと減衰する（べき乗則減衰 $\rho_k \sim k^{2d-1}$）が、1回差分すると過剰差分になる → **分数次差分**が必要。

### ARFIMA(p,d,q)

$$\phi(B)(1-B)^d z_t = \theta(B) a_t, \quad -0.5 < d < 0.5$$

$d$ が非整数のとき、$(1-B)^d = \sum_{k=0}^{\infty} \binom{d}{k}(-B)^k$

- $0 < d < 0.5$：長期記憶、ACFのべき乗則減衰（可和！）
- $d = 0$：短期記憶ARMA
- $-0.5 < d < 0$：反持続性

---

## 深掘り思考

### 太陽光発電予測への示唆

1. **日射量へのGARCH**：雲による遮蔽が引き起こすボラティリティクラスタリング → 日射量残差にARCH効果がある可能性 → GARCHを使って適応的予測区間を構築
2. **天気レジームへのTAR**：晴天と曇天では異なるARモデルが必要な可能性 → 閾値モデルやマルコフ切り替えモデル
3. **長期記憶へのARFIMA**：日射量の年際変動は長期記憶特性を示す可能性がある（気候変動の緩やかなダイナミクス）

---

*📖 [Ch9ノート](/blog/2026-03-16-box-ch9-seasonal) | [教材目次に戻る](/textbook/) | 📝 [Box時系列シリーズ](/blog/tags/時系列)*
