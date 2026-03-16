---
title: "Box 時系列分析 Ch3：AR・MA・ARMAモデルの完全解剖"
description: "Box『Time Series Analysis』第3章を精読：Wold分解からAR/MAの双対性まで、PACF打ち切りによる次数同定・Yule-Walker方程式・可逆性条件をマスターする"
pubDate: 2026-03-16
lang: ja
series: box-timeseries
category: timeseries
tags: ["時系列", "ARIMA", "ARモデル", "MAモデル", "PACF", "Yule-Walker", "教科書ノート"]
---

# Box 時系列分析 Ch3：AR・MA・ARMAモデルの完全解剖

> **教科書**：Box, Jenkins & Reinsel — *Time Series Analysis*, 4th Ed, Chapter 3

## 章の位置づけ

Ch2 は記述的ツール（ACF・スペクトル）を提供し、Ch3 では**実際に使えるパラメトリックモデル**を示す。本書の理論的中核となる章であり、以降のすべてのモデリング・予測・制御はここで確立される AR/MA/ARMA の枠組みの上に構築される。

---

## 3.1 一般線形過程

### Wold 分解定理

**任意の**ゼロ平均の純非確定的定常過程は次のように表せる：

$$\tilde{z}_t = \sum_{j=0}^{\infty} \psi_j a_{t-j}, \quad \psi_0 = 1, \quad \sum_{j=0}^{\infty} \psi_j^2 < \infty$$

これは Wold (1938) の基本的な結果である。意義：**線形モデルは「仮定」ではなく、定常過程の普遍的な表現である**。

### ψ 重みと π 重みの双対性

- **ψ 形式**（MA 表現）：$\tilde{z}_t = \psi(B)a_t$（現在値 = 過去のショックの加重和）
- **π 形式**（AR 表現）：$\pi(B)\tilde{z}_t = a_t$（現在のショック = 現在値と過去値の線形結合）

関係式：$\psi(B)\pi(B) = 1$、すなわち $\pi(B) = \psi^{-1}(B)$

### 自己共分散母関数

$$\gamma(B) = \sigma_a^2 \psi(B)\psi(B^{-1})$$

**スペクトルとフィルタゲイン**：$p(f) = 2\sigma_a^2 |\psi(e^{-i2\pi f})|^2$

出力スペクトル = 白色雑音スペクトル × フィルタゲインの二乗。

### 定常性と可逆性

- **定常**：要件 $\sum|\psi_j| < \infty$；同値な表述：$\psi(B)$ が $|B| \leq 1$ で収束
- **可逆**：要件 $\sum|\pi_j| < \infty$；同値な表述：$\pi(B)$ が $|B| \leq 1$ で収束

**可逆性の物理的意味**：現在値を（未来値ではなく）過去値で表現できる。$|\theta| \geq 1$ の場合、MA モデルの π 重みが発散し、現在値が無限の過去に対してますます大きな重みで依存することになり、物理的に不合理である。

---

## 3.2 自己回帰過程 AR(p)

### 定常条件

$\phi(B) = 0$ のすべての根が**単位円の外**にある。等価的に、特性方程式 $m^p - \phi_1 m^{p-1} - \cdots - \phi_p = 0$ の根が**単位円の内**にある。

### ACF の差分方程式

$$\rho_k = \phi_1\rho_{k-1} + \phi_2\rho_{k-2} + \cdots + \phi_p\rho_{k-p}, \quad k > 0$$

一般解：$\rho_k = A_1 G_1^k + A_2 G_2^k + \cdots + A_p G_p^k$

- **実数根** → 指数減衰
- **複素共役根** → 減衰正弦波（擬似周期的挙動）

### AR(1)：マルコフ過程

$$\tilde{z}_t = \phi_1 \tilde{z}_{t-1} + a_t, \quad |\phi_1| < 1$$

- ACF：$\rho_k = \phi_1^k$（指数減衰）
- 分散：$\sigma_z^2 = \sigma_a^2 / (1 - \phi_1^2)$
- スペクトル：$p(f) = 2\sigma_a^2 / (1 + \phi_1^2 - 2\phi_1\cos 2\pi f)$
- $\phi_1 > 0$ → 滑らかなトレンド、低周波支配
- $\phi_1 < 0$ → のこぎり歯振動、高周波支配

### AR(2)：擬似周期的挙動

定常条件（三角形領域）：$\phi_2 + \phi_1 < 1$、$\phi_2 - \phi_1 < 1$、$-1 < \phi_2 < 1$

複素根をもつ場合の ACF：$\rho_k = D^k \sin(2\pi f_0 k + F) / \sin F$

ここで減衰因子 $D = \sqrt{-\phi_2}$、周波数 $f_0 = \cos^{-1}(\phi_1 / 2\sqrt{-\phi_2}) / (2\pi)$

**太陽光発電への示唆**：日射量系列はしばしば擬似周期的挙動（天気システムの3〜7日周期）を示し、AR(2) でこの挙動を捉えられる。

### Yule-Walker 方程式

$$\boldsymbol{P}_p \boldsymbol{\phi} = \boldsymbol{\rho}_p$$

線形方程式系で、ACF の推定値 $r_k$ を代入して AR パラメータを求める。

### PACF（偏自己相関関数）

$$\phi_{kk} = \text{corr}[z_t - \hat{z}_t, z_{t-k} - \hat{z}_{t-k}]$$

**核心的性質：AR(p) の PACF はラグ $p$ 以降でゼロに打ち切られる。**

- AR(1)：$\phi_{11} = \rho_1$、$\phi_{kk} = 0$（$k \geq 2$）
- AR(2)：$\phi_{22} = (\rho_2 - \rho_1^2)/(1 - \rho_1^2)$、$\phi_{kk} = 0$（$k \geq 3$）

推定 PACF の標準誤差：$\text{SE}[\hat{\phi}_{kk}] \approx 1/\sqrt{n}$（$k \geq p+1$）

---

## 3.3 移動平均過程 MA(q)

### 可逆性条件

$\theta(B) = 0$ の根が単位円の外にある。

### ACF の打ち切り性

$$\rho_k = \begin{cases} \frac{-\theta_k + \theta_1\theta_{k+1} + \cdots + \theta_{q-k}\theta_q}{1 + \theta_1^2 + \cdots + \theta_q^2} & k = 1, \ldots, q \\ 0 & k > q \end{cases}$$

**核心的性質：MA(q) の ACF はラグ $q$ 以降でゼロに打ち切られる。**

### MA(1) の詳解

- ACF：$\rho_1 = -\theta_1 / (1 + \theta_1^2)$、$\rho_k = 0$（$k > 1$）
- $|\rho_1| \leq 0.5$（MA(1) の理論上限！）
- $\rho_1$ が与えられると $\theta_1$ の解が2つあり（$\theta_1$ と $\theta_1^{-1}$）、$|\theta_1| < 1$ の可逆解を選ぶ

### AR ↔ MA の完全な双対性

- **ACF**：AR(p) 無限に続く（指数減衰／減衰正弦）；MA(q) **ラグ $q$ 後に打ち切り**
- **PACF**：AR(p) **ラグ $p$ 後に打ち切り**；MA(q) 無限に続く（指数減衰／減衰正弦）
- **定常条件**：AR(p) $\phi(B) = 0$ の根が円外；MA(q) 常に定常
- **可逆条件**：AR(p) 常に可逆；MA(q) $\theta(B) = 0$ の根が円外
- **スペクトル**：AR(p) $p(f) \propto 1/|\phi(e^{-i2\pi f})|^2$；MA(q) $p(f) \propto |\theta(e^{-i2\pi f})|^2$

この双対性がモデル同定（Ch6）の核心ツールである：
- **ACF の打ち切り → MA モデル**
- **PACF の打ち切り → AR モデル**
- **両方が裾を引く → ARMA 混合モデル**

---

## 3.4 ARMA(p,q) 混合過程

$$\phi(B)\tilde{z}_t = \theta(B)a_t$$

- 定常：$\phi(B) = 0$ の根が円外
- 可逆：$\theta(B) = 0$ の根が円外
- ACF：最初の $q-p+1$ 個の値は θ パラメータに直接影響され、その後は差分方程式 $\phi(B)\rho_k = 0$ を満たす → 指数減衰／減衰正弦
- PACF：最初の $p-q+1$ 個の値は φ の影響を受け、その後は MA の PACF に類似 → 指数減衰
- スペクトル：$p(f) = 2\sigma_a^2 |\theta(e^{-i2\pi f})|^2 / |\phi(e^{-i2\pi f})|^2$

### ARMA(1,1) の詳解

$$(1 - \phi_1 B)\tilde{z}_t = (1 - \theta_1 B)a_t$$

- $\psi_j = (\phi_1 - \theta_1)\phi_1^{j-1}$（$j \geq 1$）
- $\rho_1 = (1 - \phi_1\theta_1)(\phi_1 - \theta_1)/(1 + \theta_1^2 - 2\phi_1\theta_1)$
- $\rho_k = \phi_1 \rho_{k-1}$（$k \geq 2$）— $\rho_1$ から始まる指数減衰

---

## 深い考察

### 1. 簡約原理の数学的実装

Ch3 は「なぜ ARMA で十分か」に答える：
- Wold 定理は任意の定常過程が $\psi(B)$ 表現をもつことを保証する
- $\psi(B) = \phi^{-1}(B)\theta(B)$ は**有理関数近似**（Padé 近似）
- 低次有理関数（$p, q \leq 2$）は無限級数を高精度で近似できる
- これが簡約原理の数学的根拠である

### 2. ACF/PACF の打ち切り = モデル同定の指紋

- ACF がラグ $q$ で打ち切り、PACF が裾を引く → **MA(q)**
- ACF が裾を引く、PACF がラグ $p$ で打ち切り → **AR(p)**
- 両方が裾を引く → **ARMA(p,q)**
- 両方が打ち切り → 不可能（矛盾）

### 3. 太陽光発電予測への具体的指針

- **日変動除去後の残差**：通常 ACF は裾を引くが急速に減衰 → AR(1) または AR(2) の候補
- **雲遮蔽イベント**：急変を引き起こし、AR モデルの ψ 重みでは滑らかすぎる → MA 項が必要かも
- **複数地点の空間相関**：Ch14 の VAR モデルは AR の多変量拡張

---

## まとめ

Ch3 は ARMA モデル族の完全な理論を確立した：

**三大モデル** = AR（過去値への回帰）+ MA（ショックの加重和）+ ARMA（混合）

**二大同定ツール** = ACF（打ち切り→MA）+ PACF（打ち切り→AR）

**二大妥当性条件** = 定常性（$\phi(B)=0$ の根が円外）+ 可逆性（$\theta(B)=0$ の根が円外）

**次章の予告**：Ch4 では非定常を導入 — 差分演算子 $\nabla^d$ が ARMA を ARIMA に拡張する。

---

*📖 [Ch2 ノート](/blog/2026-03-16-box-ch2-acf-spectrum) | [教科書目次に戻る](/textbook/) | 📝 [Box 時系列シリーズ](/blog/)*
