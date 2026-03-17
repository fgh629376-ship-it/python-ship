---
title: "🔬 異業種アルゴリズム移転：コンフォーマル予測（Conformal Prediction）——太陽光発電予測における不確実性定量化の新パラダイム"
description: "統計学理論に基づき、金融リスク管理や医学診断で実績を上げたコンフォーマル予測が、再生可能エネルギー分野に移転しつつある。本記事ではCPの数学的基礎、分布非依存性の優位性、太陽光発電予測への具体的応用——カバレッジ保証、適応的区間幅、オンライン更新戦略を、完全なPython実装付きで詳細に解説する。"
pubDate: 2026-03-17
lang: ja
category: solar
series: cross-industry
tags: ['異業種アルゴリズム', 'コンフォーマル予測', '不確実性定量化', '太陽光予測', '確率的予測', '予測区間']
---

## はじめに：なぜ太陽光発電予測に不確実性定量化が必要か？

太陽光発電予測モデルは「明日14:00の出力は850 kW」という数値を出す。しかし系統運用者が本当に知りたいのは：**この数値はどれくらい信頼できるのか？** 実際の範囲は800〜900 kWなのか、500〜1200 kWなのか？

不確実性定量化（Uncertainty Quantification, UQ）は電力システムにとって極めて重要である：

- **系統運用**：予備容量の確保量は予測区間幅に依存する
- **電力市場**：入札戦略には予測の確率分布の知識が必要
- **蓄電池最適化**：充放電判断は予測信頼区間に依存する
- **リスク管理**：極端な偏差の確率がシステム安全性に直接影響する

従来の手法（分位点回帰、ベイジアンニューラルネットワーク、ガウス過程）にはそれぞれ限界がある。**コンフォーマル予測（Conformal Prediction, CP）** は、分布に依存しない不確実性定量化フレームワークとして、統計学・金融分野から再生可能エネルギー予測へ急速に移転している。

---

## 1. コンフォーマル予測の核心的アイデア

### 1.1 起源と発展

コンフォーマル予測は、Vladimir Vovk、Alexander Gammerman、Glenn Shaferにより2005年に体系的に提唱された（Vovk et al., 2005, *Algorithmic Learning in a Random World*, Springer）。その知的ルーツは1950年代の許容区間（tolerance intervals）と非パラメトリック統計に遡る。

2019年以降、CPは爆発的に成長した。Romano et al. (2019) がNeurIPSで発表した**Conformalized Quantile Regression (CQR)** が重要な転換点となった——CPと深層学習をシームレスに統合し、あらゆる点予測モデルに理論的保証付き予測区間を生成させることが可能になった。

### 1.2 数学的フレームワーク

訓練集合 $\{(X_i, Y_i)\}_{i=1}^{n}$ と新しいテスト点 $(X_{n+1}, Y_{n+1})$ が与えられ、データの交換可能性（exchangeability）を仮定する。

**ステップ1：基本モデルの訓練**

訓練集合で任意の予測モデル $\hat{f}$ を訓練する（線形回帰、ランダムフォレスト、ニューラルネットワーク、何でもよい）。

**ステップ2：非適合性スコアの計算**

校正集合（calibration set）で各サンプルの非適合性スコアを計算する：

$$s_i = |Y_i - \hat{f}(X_i)|$$

これは最も単純な絶対残差形式である。より一般的に、非適合性スコアは「モデル予測と真値の不一致度」を測る任意の関数として定義できる。

**ステップ3：分位点閾値の計算**

目標カバレッジ率 $1 - \alpha$（例：90%）に対し、校正スコアの $\lceil (1-\alpha)(1+1/n_{\text{cal}}) \rceil$ 分位点を計算する：

$$\hat{q} = \text{Quantile}\left(\{s_i\}_{i=1}^{n_{\text{cal}}}, \frac{\lceil (1-\alpha)(n_{\text{cal}}+1) \rceil}{n_{\text{cal}}}\right)$$

**ステップ4：予測区間の構築**

新しいサンプル $X_{n+1}$ に対し：

$$C(X_{n+1}) = [\hat{f}(X_{n+1}) - \hat{q}, \; \hat{f}(X_{n+1}) + \hat{q}]$$

### 1.3 主要な保証

**有限標本カバレッジ保証（Finite-Sample Coverage Guarantee）：**

$$P(Y_{n+1} \in C(X_{n+1})) \geq 1 - \alpha$$

この保証は以下の条件で成立する：
1. **交換可能性**（Exchangeability）：$(X_1, Y_1), \ldots, (X_{n+1}, Y_{n+1})$ が共同交換可能（i.i.d.より弱い条件）
2. **分布仮定なし**：正規分布や特定の分布を仮定する必要がない
3. **モデル非依存**：$\hat{f}$ はブラックボックスモデルで構わない

これがCPの核心的魅力である：**モデルがどれほど複雑でも、データ分布がどれほど特殊でも、交換可能性が成立する限り、カバレッジ保証は成立する。**

---

## 2. 基礎からフロンティアへ：CPの重要な変種

### 2.1 適合化分位点回帰（CQR）

基本CPの問題：予測区間幅が固定される。晴天時の予測は容易で曇天時は困難だが、区間は同じ幅——明らかに最適ではない。

Romano et al. (2019, NeurIPS) がCQRを提案した：

**ステップ1**：分位点回帰モデルを訓練し、下側分位点 $\hat{q}_{\alpha_{\text{lo}}}(X)$ と上側分位点 $\hat{q}_{\alpha_{\text{hi}}}(X)$ を同時に予測

**ステップ2**：校正集合で適応的非適合性スコアを計算：

$$s_i = \max\left(\hat{q}_{\alpha_{\text{lo}}}(X_i) - Y_i, \; Y_i - \hat{q}_{\alpha_{\text{hi}}}(X_i)\right)$$

**ステップ3**：基本CPと同様に $\hat{q}$ を計算

**ステップ4**：適応的区間を構築：

$$C(X_{n+1}) = [\hat{q}_{\alpha_{\text{lo}}}(X_{n+1}) - \hat{q}, \; \hat{q}_{\alpha_{\text{hi}}}(X_{n+1}) + \hat{q}]$$

主な利点：**区間幅が入力条件に応じて適応的に変化する**。モデルが確信を持つ入力には狭い区間、不確かな入力には広い区間を与え、全体のカバレッジ保証は維持される。

### 2.2 適応的コンフォーマル推論（ACI）

時系列データの課題：交換可能性仮定が成立しない（時系列には自己相関がある）。

Gibbs & Candès (2021, NeurIPS) がACIを提案した：分布シフトに適応するため $\alpha_t$ を動的に調整する：

$$\alpha_{t+1} = \alpha_t + \gamma(\alpha - \text{err}_t)$$

ここで $\text{err}_t = \mathbb{1}(Y_t \notin C_t(X_t))$ は時刻 $t$ のカバレッジエラー指標、$\gamma > 0$ は学習率である。

直感的理解：最近のカバレッジが低すぎれば（モデルがアンダーカバー）、$\alpha_t$ が減少 → 区間が拡大する。逆も同様。これは**オンラインフィードバック制御ループ**を形成する。

ACIは太陽光発電予測に特に重要である：日射量の統計的特性は季節や気象パターンによって大きく変化するため、固定校正のCPでは失敗する。

### 2.3 EnbPI：時系列CPのアンサンブル手法

Xu & Xie (2021, ICML) がEnbPI（Ensemble Batch Prediction Intervals）を提案した：

- $B$ 個のブートストラップ集約モデルを訓練
- Leave-one-out残差でデータ分割を回避
- スライディングウィンドウで残差集合を更新

太陽光予測への利点：専用の校正集合が不要（データ利用効率が高い）で、時系列依存性を自然に処理する。

---

## 3. 太陽光発電予測におけるCPの具体的応用

### 3.1 なぜCPは太陽光予測に適しているか

| 特性 | CPの優位性 | 太陽光予測への意義 |
|------|-----------|-----------------|
| 分布非依存 | 分布仮定不要 | 日射量誤差分布は強い非正規性（右偏、多峰） |
| モデル非依存 | 任意モデルをラップ | 既存のXGBoost/LSTM/Transformerを直接強化 |
| 有限標本保証 | 漸近仮定不要 | 新規発電所はデータが少なく漸近理論は不信頼 |
| 適応的幅 | CQR等の変種 | 晴天は狭区間、曇天は広区間——物理的直感に合致 |
| オンライン更新 | ACI等の変種 | 季節変化やモデル劣化に適応 |

### 3.2 実践シナリオ：日前確率的予測区間

以下は、pvlibシミュレーションデータ（晴天モデルに基づく、実測データではない）を使い、CQRで予測区間を構築する完全な例である：

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

# ============================================================
# 1. シミュレーションPVデータの生成（晴天モデル、実測データではない）
# ============================================================
np.random.seed(42)
n_days = 365
hours = np.arange(6, 19)  # 日中時間帯

records = []
for day in range(n_days):
    for hour in hours:
        solar_elevation = np.sin(np.pi * (hour - 6) / 12)
        ghi_clear = 1000 * max(0, solar_elevation)
        
        cloud_factor = np.random.beta(2, 5)
        ghi = ghi_clear * (1 - cloud_factor * 0.8)
        
        temp = 25 + 10 * solar_elevation + np.random.normal(0, 3)
        
        power = max(0, ghi * 0.85 * (1 - 0.004 * (temp - 25)) 
                     + np.random.normal(0, 20))
        
        records.append({
            'day': day, 'hour': hour,
            'ghi': ghi, 'temp': temp, 
            'solar_elevation': solar_elevation,
            'power': power
        })

df = pd.DataFrame(records)
X = df[['ghi', 'temp', 'solar_elevation']].values
y = df['power'].values

# ============================================================
# 2. データ分割：訓練 / 校正 / テスト
# ============================================================
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.4, random_state=42
)
X_cal, X_test, y_cal, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42
)

# ============================================================
# 3. CQR 実装
# ============================================================
alpha = 0.1  # 目標カバレッジ率 90%

model_lo = GradientBoostingRegressor(
    loss='quantile', alpha=alpha/2, n_estimators=200, max_depth=5
)
model_hi = GradientBoostingRegressor(
    loss='quantile', alpha=1-alpha/2, n_estimators=200, max_depth=5
)
model_lo.fit(X_train, y_train)
model_hi.fit(X_train, y_train)

q_lo_cal = model_lo.predict(X_cal)
q_hi_cal = model_hi.predict(X_cal)
scores = np.maximum(q_lo_cal - y_cal, y_cal - q_hi_cal)

n_cal = len(y_cal)
q_level = np.ceil((1 - alpha) * (n_cal + 1)) / n_cal
q_hat = np.quantile(scores, min(q_level, 1.0))

q_lo_test = model_lo.predict(X_test) - q_hat
q_hi_test = model_hi.predict(X_test) + q_hat

# ============================================================
# 4. 評価
# ============================================================
coverage = np.mean((y_test >= q_lo_test) & (y_test <= q_hi_test))
avg_width = np.mean(q_hi_test - q_lo_test)

print(f"目標カバレッジ率: {1-alpha:.0%}")
print(f"実際カバレッジ率: {coverage:.1%}")
print(f"平均区間幅: {avg_width:.1f} kW")
print(f"区間幅標準偏差: {np.std(q_hi_test - q_lo_test):.1f} kW")
```

### 3.3 晴天 vs 曇天の区間適応

CQRの核心的利点はコードに現れている：GBR分位点モデルが「曇天は不確実性が大きい」ことを学習するため：

- **晴天**（高GHI、低変動）：$\hat{q}_{0.95}(X) - \hat{q}_{0.05}(X)$ が小 → 狭い区間
- **曇天**（低GHI、高変動）：$\hat{q}_{0.95}(X) - \hat{q}_{0.05}(X)$ が大 → 広い区間

CPの補正項 $\hat{q}$ を加えることで、最終的な区間は適応的でありながらカバレッジ保証を持つ。

### 3.4 オンライン更新：季節ドリフトへの対応

太陽光予測の重要な課題は**概念ドリフト**（concept drift）である：夏季と冬季の日射量分布は完全に異なる。ACIのオンライン更新戦略はこのシナリオに最適である：

```python
# ACI オンライン更新の例
gamma = 0.005  # 学習率
alpha_t = alpha  # 初期化

coverages = []
for t in range(len(y_test)):
    interval = [
        model_lo.predict(X_test[t:t+1])[0] - q_hat,
        model_hi.predict(X_test[t:t+1])[0] + q_hat
    ]
    
    err_t = 1 if (y_test[t] < interval[0] or y_test[t] > interval[1]) else 0
    
    alpha_t = alpha_t + gamma * (alpha - err_t)
    alpha_t = np.clip(alpha_t, 0.01, 0.5)
    
    q_level = np.ceil((1 - alpha_t) * (n_cal + 1)) / n_cal
    q_hat = np.quantile(scores, min(q_level, 1.0))
    
    coverages.append(1 - err_t)

print(f"ACI ローリングカバレッジ: {np.mean(coverages):.1%}")
```

---

## 4. CP vs 従来の確率的予測手法

### 4.1 分位点回帰（QR）との比較

分位点回帰はpinball lossを直接最適化して分位点を出力するが、**有限標本カバレッジ保証がない**。実際にはQRのカバレッジ率が目標から大きく外れることがある。

CQR = QR + CP補正で、QRの上に**安全装置を追加**したものである。

### 4.2 ベイジアン手法との比較

ベイジアンニューラルネットワーク（BNN）とガウス過程（GP）は完全な事後分布を提供するが：

- **計算コストが高い**：BNNはMCMCまたは変分推論が必要、GPは $O(n^3)$
- **事前分布に敏感**：不適切な事前分布は信頼区間の信頼性を損なう
- **分布仮定**：GPはガウスノイズを仮定、BNNの変分事後分布も近似である

CPの利点：**計算が軽量**（校正集合でソートして分位点を取るだけ）+ **分布仮定不要**。

### 4.3 アンサンブル手法との比較

ランダムフォレスト/深層アンサンブルの予測区間はメンバーモデルの分散から導かれるが：

- アンサンブルの分散 ≠ 真の不確実性
- メンバーモデルが高度に相関すると区間が過度に狭くなる
- 理論的カバレッジ保証がない

CPはアンサンブル手法を**外側からラップ**し、その区間に補正を加えることができる。

---

## 5. フロンティアの進展と将来の方向性

### 5.1 多段階コンフォーマル予測

太陽光予測は通常、多段階予測（例：今後24時間の毎時予測）を必要とする。Stankevičiūtė et al. (2021, ICML) は、共同カバレッジを制御するCopulaベースの多段階コンフォーマル予測を提案した。

### 5.2 空間コンフォーマル予測

PV発電所ネットワークでは、複数の発電所に同時に予測区間を提供する必要がある。Feldman et al. (2023, *Journal of the American Statistical Association*) が空間コンフォーマル予測の理論的フレームワークを探究した。

### 5.3 深層学習との深い統合

Angelopoulos & Bates (2023, *Foundations and Trends in Machine Learning*) のサーベイは、CPとTransformer、グラフニューラルネットワーク等の深層モデルとの統合が活発な研究方向であると指摘している。PV分野では、CPとiTransformerやPatchTSTの組み合わせは自然な次のステップである。

### 5.4 因果コンフォーマル予測

Cauchois et al. (2024) が因果推論フレームワークにおけるコンフォーマル予測を探究した。太陽光への意義は：予測モデルの入力（天気予報など）自体にバイアスがある場合に、予測区間をどう補正するかという問題への対処である。

---

## 6. 実践的な推奨事項

### 6.1 太陽光予測エンジニアへの提言

1. **CQRから始める**：最も実用的なCP変種——コードが簡潔で効果が高い
2. **校正集合は代表的に**：異なる天候タイプと季節をカバーすること
3. **オンラインシナリオにはACIを使用**：デプロイ後のモデルには分布ドリフトへの適応が必要
4. **評価指標**：カバレッジ率 + 区間幅（sharpness）+ Winklerスコア
5. **既存モデルとの組み合わせ**：CPは後処理ステップ、モデルの再訓練は不要

### 6.2 推奨ライブラリ

- **MAPIE**：scikit-learn互換のCPライブラリ（[mapie.readthedocs.io](https://mapie.readthedocs.io)）
- **crepes**：軽量コンフォーマル予測ライブラリ
- **fortuna**：AWSオープンソースの不確実性定量化ライブラリ

---

## 7. まとめ

コンフォーマル予測は、太陽光発電予測の不確実性定量化に対して**理論的に優雅で実践的に強力な**フレームワークを提供する：

- **分布非依存**：誤差分布の形式を仮定しない
- **モデル非依存**：任意の既存モデルを強化
- **有限標本保証**：カバレッジ保証に漸近仮定が不要
- **適応的**：CQR + ACIで条件適応 + オンライン更新を実現
- **計算軽量**：校正ステップはソートと分位点計算のみ

統計学理論から金融リスク管理、そして再生可能エネルギー予測へ——コンフォーマル予測の異業種移転は、太陽光発電予測の確率化アップグレードに重要なツールを提供している。

---

## 参考文献

1. Vovk, V., Gammerman, A., & Shafer, G. (2005). *Algorithmic Learning in a Random World*. Springer.
2. Romano, Y., Patterson, E., & Candès, E. (2019). Conformalized Quantile Regression. *NeurIPS 2019*.
3. Gibbs, I., & Candès, E. (2021). Adaptive Conformal Inference Under Distribution Shift. *NeurIPS 2021*.
4. Xu, C., & Xie, Y. (2021). Conformal Prediction Interval for Dynamic Time-Series. *ICML 2021*.
5. Angelopoulos, A. N., & Bates, S. (2023). Conformal Prediction: A Gentle Introduction. *Foundations and Trends in Machine Learning*, 16(4), 494–591.
6. Stankevičiūtė, K., Alaa, A. M., & van der Schaar, M. (2021). Conformal Time-Series Forecasting. *NeurIPS 2021*.
7. Yang, D., & Kleissl, J. (2024). *Solar Irradiance and Photovoltaic Power Forecasting*. CRC Press.
8. Feldman, S., Bates, S., & Romano, Y. (2023). Achieving Risk Control in Online Learning Settings. *Journal of the American Statistical Association*.
