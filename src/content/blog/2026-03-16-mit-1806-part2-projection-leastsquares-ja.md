---
title: "MIT 18.06 線形代数 Part 2：射影・最小二乗法・QR分解"
description: "MIT 18.06 講義8-14を精読：四つの基本部分空間の全体像、正射影の公式、最小二乗法、Gram-SchmidtとQR分解、擬似逆行列"
pubDate: 2026-03-16
lang: ja
series: mit-courses
category: algorithm
tags: ["線形代数", "MIT", "最小二乗法", "QR分解", "射影", "擬似逆行列", "教科書ノート"]
---

# MIT 18.06 線形代数 Part 2：射影・最小二乗法・QR分解

> **コース**：MIT 18.06 Linear Algebra, Spring 2025
> **範囲**：講義8-14（四つの基本部分空間・射影・最小二乗法・QR・擬似逆行列）

## 講義8-9：四つの基本部分空間——線形代数の全体像

### 行列の四つの基本部分空間

$m \times n$ 行列 $A$ について、RREF $R = GA$ を用いると：

- **列空間** $C(A) = G^{-1}C(R)$、$\subseteq \mathbb{R}^m$、次元 $r$
- **零空間** $N(A) = N(R)$、$\subseteq \mathbb{R}^n$、次元 $n - r$
- **行空間** $C(A^T) = C(R^T)$、$\subseteq \mathbb{R}^n$、次元 $r$
- **左零空間** $N(A^T) = G^T N(R^T)$、$\subseteq \mathbb{R}^m$、次元 $m - r$

### 直交補空間の関係

$$\mathbb{R}^n = C(A^T) \oplus N(A), \quad \mathbb{R}^m = C(A) \oplus N(A^T)$$

行空間と零空間は $\mathbb{R}^n$ における直交補空間であり、列空間と左零空間は $\mathbb{R}^m$ における直交補空間である。

**これは線形代数の最も深い構造定理である。** その示唆：
- $A\mathbf{x} = \mathbf{b}$ において、$\mathbf{b}$ は列空間成分と左零空間成分に一意に分解できる
- 列空間成分は「$A$ が説明できる部分」、左零空間成分は「残差」

**太陽光予測における四つの部分空間**：

$A$ を気象特徴行列（$m$ 個の時間ステップ × $n$ 個の特徴量）とすると：
- $C(A)$：特徴の組み合わせで説明できる発電量変動の空間
- $N(A^T)$：特徴では説明できない発電量変動（「純粋なノイズ」方向）
- $C(A^T)$：有効な特徴方向
- $N(A)$：冗長な特徴の組み合わせ（多重共線性！）

$N(A)$ の次元が大きいとき、特徴間に高い共線性がある——正則化または次元削減（PCA/Ridge）が必要。

---

## 講義10-11：正射影

### 射影の幾何的意味

$$\mathbf{v} = \text{proj}_V(\mathbf{x}) = V \text{ の中で } \mathbf{x} \text{ に最も近い点}$$

同値条件：$(\mathbf{x} - \mathbf{v}) \perp V$

### 射影行列の公式

$V = C(A)$、$A$ は $n \times r$ かつ $\text{rank}(A) = r$ とすると：

$$P_V = A(A^T A)^{-1}A^T$$

**性質**：
- $P_V^2 = P_V$（冪等：2回射影 = 1回射影）
- $P_V^T = P_V$（対称）
- $\text{rank}(P_V) = r$（列空間 = $V$）

### なぜ $A^T A$ は可逆か？

$A$ が列フルランクのとき、$A^T A$ は $r \times r$ の正定値行列である。直感：$A^T A$ の零空間 = $A$ の零空間 = $\{\mathbf{0}\}$。

**Box との関連**：Box 第7章の正規方程式 $A^T A \hat{\boldsymbol{\phi}} = A^T \mathbf{z}$ は正射影を行っている——データ $\mathbf{z}$ を計画行列の列空間に射影する操作である。Yule-Walker 方程式 $\mathbf{P}_p \boldsymbol{\phi} = \boldsymbol{\rho}_p$ の $\mathbf{P}_p$ は Toeplitz 構造を持つ $A^T A$ に他ならない。

---

## 講義12：最小二乗法

### コア公式

$$\hat{\mathbf{x}} = (A^T A)^{-1} A^T \mathbf{b}$$

$\|A\mathbf{x} - \mathbf{b}\|^2 = \sum_i [(A\mathbf{x})_i - b_i]^2$ を最小化する。

### 実際の応用

**原点を通る直線フィット**：$b = xa$
- 計画行列 $A = \mathbf{a}$（1列）、$\hat{x} = \frac{\mathbf{a}^T \mathbf{b}}{\mathbf{a}^T \mathbf{a}}$

**切片付き直線フィット**：$b = x_0 + x_1 a$
- 計画行列 $A = [\mathbf{1} | \mathbf{a}]$（2列）

**多項式フィット**：$b = x_0 + x_1 a + x_2 a^2 + x_3 a^3$
- 計画行列 $A = [\mathbf{1} | \mathbf{a} | \mathbf{a}^2 | \mathbf{a}^3]$（Vandermonde行列）

**太陽光予測における最小二乗法**：
- 温度モデルパラメータのフィッティング：$T_{cell} = T_{amb} + \alpha \cdot GHI + \beta \cdot WS + \gamma$
- Box 第7章の条件付きMLE = 条件付き最小二乗法
- Yang 第7章のMOS（モデル出力統計）後処理 = 重回帰分析

### ⚠️ 最小二乗法 vs PCA

**最小二乗法**は**垂直距離**（$y$ 方向の残差）を最小化する：$y = f(x)$ 回帰に適する

**PCA**は部分空間への**直交距離**の二乗和を最小化する（「垂直最小二乗法」）：データ圧縮・次元削減に適する

教科書はPCAを「perpendicular least squares」と呼んでいる——両者は同じものではない！

---

## 講義13：Gram-SchmidtとQR分解

### Gram-Schmidt直交化

入力：基底 $(v_1, \ldots, v_r)$
出力：正規直交基底 $(u_1, \ldots, u_r)$

$$u_k = \frac{v_k - \sum_{j=1}^{k-1}(v_k \cdot u_j)u_j}{\|v_k - \sum_{j=1}^{k-1}(v_k \cdot u_j)u_j\|}$$

### QR分解

$$A = QR$$

- $Q$：$n \times r$、正規直交な列
- $R$：$r \times r$、上三角行列

**QRの数値的優位性**：
- 正規方程式 $(A^T A)\hat{\mathbf{x}} = A^T\mathbf{b}$ を直接用いると数値的に不安定（条件数が二乗される）
- QRを使えば：$\hat{\mathbf{x}} = R^{-1}Q^T\mathbf{b}$、条件数は変わらない

**実用メモ**：NumPy の `np.linalg.lstsq()` は内部でQR分解を使用しており、正規方程式は使っていない。

---

## 講義14：擬似逆行列

### 最小ノルム解

$A$ が $r \times n$（$r < n$、劣決定系）のとき：解が無限に存在する。**最小ノルム解** = 行空間成分 $\mathbf{x}^\perp$。

### 行列の擬似逆行列 $A^+$

任意の $m \times n$ 行列 $A$ に対して：
1. $\mathbf{y}$ を $C(A)$ に射影して $\mathbf{b}$ を得る
2. $A\mathbf{x} = \mathbf{b}$ の最小ノルム解を求める

$$A^+ : \mathbb{R}^m \to \mathbb{R}^n$$

**二つの特殊ケース**：
- $A$ が列フルランク（$m \geq n = r$）：$A^+ = (A^T A)^{-1} A^T$（左逆、最小二乗）
- $A$ が行フルランク（$n \geq m = r$）：$A^+ = A^T(AA^T)^{-1}$（右逆、最小ノルム）

**SVDによる計算**（講義26）：$A = U\Sigma V^T \Rightarrow A^+ = V\Sigma^{-1}U^T$

**太陽光予測における擬似逆行列**：
- 気象特徴数が観測数を超える（$n > m$）場合、直接最小二乗法では一意解がない → 擬似逆行列が最小ノルム解を与える
- Ridge回帰で $\lambda \to 0$ の極限と等価
- NWPデータ同化では観測演算子 $H$ が通常「横長行列」（観測数 < 状態変数数）であり、擬似逆行列が必要

---

## 深掘り：最小二乗法の統一的な視点

以下のすべての問題は同じ数学的本質を持つ——列空間の中で $\mathbf{b}$ に最も近い点を見つけること：

- **線形回帰**：方程式 $A\mathbf{x} = \mathbf{b}$ — $A$ は計画行列（特徴量）、$\mathbf{b}$ は目的変数
- **Box ARIMA**：方程式 $\Phi\hat{\boldsymbol{\phi}} = \boldsymbol{\rho}$ — $\Phi$ はToeplitz ACF行列、$\boldsymbol{\rho}$ はACFベクトル
- **NWP同化**：方程式 $H\mathbf{x} = \mathbf{y}_{obs}$ — $H$ は観測演算子、$\mathbf{y}_{obs}$ は観測値
- **pvlib温度**：方程式 $A\boldsymbol{\beta} = T_{cell}$ — $A$ は気象特徴行列、$T_{cell}$ はセル温度
- **画像圧縮**：近似 $\approx U_k\Sigma_k V_k^T$ — 左特異ベクトルによる

---

## モジュールまとめ

講義8-14は18.06の精髄——射影と最小二乗法はすべての回帰手法を理解するための幾何学的基盤である。

**コア公式チェーン**：
1. 四つの基本部分空間の直交補関係 → 任意のベクトルが一意に分解される
2. 正射影 $P = A(A^TA)^{-1}A^T$ → 最良近似
3. 最小二乗法 $\hat{\mathbf{x}} = (A^TA)^{-1}A^T\mathbf{b}$ → パラメータ推定
4. QR分解 → 数値安定な実装
5. 擬似逆行列 → 過決定/劣決定系の統一処理

**次回予告**：講義15-19の行列式 + 講義20-23の固有値——ARIMA特性方程式の数学的基盤。

---

*📖 [MITコースシリーズ](/blog/tags/MIT) | [Part 1: ベクトル空間](/blog/2026-03-16-mit-1806-part1-foundations) | 🧠 MIT 18.06 Spring 2025*
