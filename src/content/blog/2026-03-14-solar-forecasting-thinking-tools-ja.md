---
title: '太陽光発電予測のための哲学的武器庫：遠回りを防ぐ6つの思考ツール'
description: 'オッカムの剃刀からスモークグレネード検出まで — これらの思考ツールが太陽光発電予測研究の成否を分ける。'
pubDate: 2026-03-14
lang: ja
category: solar
series: solar-book
tags: ['太陽光発電予測', '研究方法論', '批判的思考', 'Solar Forecasting', 'テキストノート']
---

> 『Solar Irradiance and PV Power Forecasting』(Dazhi Yang & Jan Kleissl, 2024) 第2章 学習ノート

太陽光発電予測の分野では毎年数百本の論文が出るが、本当に進歩に貢献するものはどれほどあるだろうか？第2章は**哲学的思考ツール**を提供し、真のイノベーションとアカデミックノイズを見分ける力を与えてくれる。

## 1. オッカムの剃刀 — シンプルな説明がより正しい

```python
import numpy as np

np.random.seed(42)
x = np.linspace(0, 10, 50)
y_true = 2 * x + 1 + np.random.normal(0, 2, 50)

from numpy.polynomial import polynomial as P
coef_a = P.polyfit(x, y_true, 1)   # 線形: 2パラメータ
y_a = P.polyval(x, coef_a)

coef_b = P.polyfit(x, y_true, 20)  # 20次: 21パラメータ
y_b = P.polyval(x, coef_b)

rmse_a = np.sqrt(np.mean((y_true - y_a)**2))
rmse_b = np.sqrt(np.mean((y_true - y_b)**2))

print(f"線形モデル RMSE: {rmse_a:.3f}（2パラメータ）")
print(f"20次多項式 RMSE: {rmse_b:.3f}（21パラメータ）")
print(f"\nオッカムの剃刀：訓練データではBが良いが、Aの方が汎化する")
# モデル計算に基づく、実測データではない
```

2つのモデルの精度が同程度なら、**パラメータが少ない方を選ぶ**。太陽光予測では、シンプルな持続性モデル（明日＝今日）が過学習した深層学習モデルに勝つことがよくある。

## 2. オッカムのほうき — 隠された不都合な真実

**アンチツール** — 他者が意図的に隠す不利な事実に注意：

**典型例**：カルマンフィルターでWRF日前予測を「後処理」し好結果を報告。しかし隠された事実は、カルマンフィルターは t-1 の観測値が必要で、**日前予測を時間前予測に変えてしまっている**。

```python
def fake_day_ahead_with_kalman(forecast_24h, actual_hourly):
    """
    日前予測の後処理に見えるが、
    実は前時間の実測値を覗き見している
    """
    filtered = []
    for t in range(len(forecast_24h)):
        if t == 0:
            filtered.append(forecast_24h[t])
        else:
            correction = actual_hourly[t-1] - forecast_24h[t-1]
            filtered.append(forecast_24h[t] + 0.5 * correction)
    return filtered

print("⚠️ 後処理手法が予測ホライズンを変えていないか必ず確認")
# モデル計算に基づく、実測データではない
```

## 3. "Novel" オペレーター — 自称「新規性」は疑わしい

タイトルに "novel"、"innovative"、"intelligent" がある論文は、**車輪の再発明**の可能性が高い。

```python
BUZZWORDS = {
    'novel', 'innovative', 'intelligent', 'smart',
    'advanced', 'state-of-the-art', 'effective',
    'efficient', 'superior', 'cutting-edge'
}

def novel_alarm(title: str) -> str:
    found = [w for w in BUZZWORDS if w.lower() in title.lower()]
    if found:
        return f"🚨 {found} を検出 — 文献レビューを要確認"
    return "✅ 控えめなタイトル、内容も要検証"

papers = [
    "A Novel Deep Learning Method for Solar Forecasting",
    "Analog Ensemble Post-processing of Day-ahead Solar Forecasts",
    "An Intelligent Hybrid Model for Efficient PV Prediction",
]
for p in papers:
    print(f"{novel_alarm(p)}\n  → {p}\n")
```

## 4. スモークグレネード — 数式が多いほど疑わしい

Armstrongの実験：**論文の難読度とジャーナルの権威に正の相関**（r=0.7）。

```python
def strip_smoke(abstract: str) -> str:
    """修飾語を除去し、核心的貢献を露出させる"""
    smoke_words = [
        'effective', 'innovative', 'novel', 'intelligent',
        'advanced', 'optimal', 'superior', 'remarkable',
        'significantly', 'dramatically', 'substantially',
    ]
    result = abstract
    for w in smoke_words:
        result = result.replace(w, '___').replace(w.capitalize(), '___')
    return result

original = ("An effective and innovative optimization model based on "
            "nonlinear support vector machine is proposed to forecast "
            "solar radiation with superior accuracy")

print("原文:", original)
print("除煙:", strip_smoke(original))
# → 正則化SVMで太陽放射を予測。それだけ？
```

## 5. 素人の読者 — 初心者向けに書く

一年生の大学院生が再現できない論文は、著者側の問題。

再現不可能な3大理由：
1. **説明不足**：「専門家なら分かるはず」→ 重要ステップ省略
2. **データの秘匿**：BSRN/NSRDB/MERRA-2は全て公開データ
3. **ミスへの恐怖**：コード公開 = バグ露出 → 公開しない

```python
checklist = {
    "データ公開": True,
    "コードオープンソース": False,
    "ハイパーパラメータ全記載": False,
    "ランダムシード固定": False,
    "標準評価指標使用": True,
    "データ分割明確": False,
}

score = sum(checklist.values()) / len(checklist) * 100
print(f"再現性スコア: {score:.0f}%")
for k, v in checklist.items():
    print(f"  {'✅' if v else '❌'} {k}")
```

## 6. レンガと梯子 — レンガだけでなく梯子を作れ

Forscher (1963)：科学者はレンガ製造の流れ作業員と化し、**建物を建てる**という目的を忘れた。

Russellの階層観：ガリレオ → ニュートン → アインシュタイン、各レベルが下位を一般化。**梯子** = 帰納（上へ）+ 演繹（下へ）。

太陽光予測の研究者はレンガ作りが得意だが、梯子を作る人が不足 — 方法を負荷予測・風力予測・金融予測に**一般化して検証する**人材が必要。

---

## 📋 知識カード

| ツール | 種類 | 一言まとめ |
|--------|------|-----------|
| オッカムの剃刀 | ✅ 思考 | 複雑さが**顕著に**改善しない限りシンプルなモデルを優先 |
| オッカムのほうき | ⚠️ アンチ | 隠された不都合な事実に注意 |
| "Novel" オペレーター | ⚠️ アンチ | 自称新規性？まず参考文献を確認 |
| スモークグレネード | ⚠️ アンチ | 数式が多い→骨格を抽出し本質を確認 |
| 素人の読者 | ✅ 思考 | 初心者が再現できるように書く |
| レンガと梯子 | ✅ 思考 | 論文を書くだけでなく、一般化して検証せよ |

> **PVプロジェクトへの教訓**：予測モデルにモジュールを追加するたびに問うべき —「これを外したらどれだけ悪化する？」答えが「ほぼ同じ」なら、オッカムの剃刀で削るべき。
