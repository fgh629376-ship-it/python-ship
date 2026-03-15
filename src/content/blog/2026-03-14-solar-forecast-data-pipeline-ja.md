---
title: '太陽光発電点予測の実戦：データ処理からモデル構築までの10の致命的ポイント'
description: 'データ品質が予測の上限を決め、モデルはそれに近づくだけ。日射量成分からk-index正規化、QCから訓練/テスト分割まで——一つ間違えばモデルは使い物にならない。'
pubDate: 2026-03-14
lang: ja
category: solar
series: solar-book
tags: ['太陽光発電予測', 'データ処理', '点予測', 'Python', '機械学習', 'テキストノート']
---

> 参考文献：
> - 『Solar Irradiance and PV Power Forecasting』第5・7章 (Yang & Kleissl, 2024)
> - Pedro & Coimbra, *Renewable & Sustainable Energy Reviews* (Q1 Top)
> - Yagli et al., *Renewable & Sustainable Energy Reviews* (Q1 Top)

太陽光発電予測は「モデルを選んで実行する」だけではない。**データ処理が予測の上限を決め、モデルはそれに近づくだけ。**

## 1. 日射量成分を理解する — GHI ≠ POA

PV出力は**パネル面日射量 (POA/GTI)** に比例する。GHIではない。

```python
import numpy as np

def closure_equation(ghi: float, dhi: float, zenith_deg: float) -> float:
    """閉合方程式：GHIとDHIからBNIを導出。"""
    cos_z = np.cos(np.radians(zenith_deg))
    if cos_z <= 0:
        return 0.0
    return max(0.0, (ghi - dhi) / cos_z)

bni = closure_equation(800, 150, 30)
print(f"GHI=800, DHI=150, Z=30° → BNI={bni:.1f} W/m²")
# モデル計算に基づく、実測データではない
```

## 2. k-index正規化 — 天文周期の除去

```python
def clear_sky_index(ghi: np.ndarray, ghi_clear: np.ndarray) -> np.ndarray:
    """κ = GHI / GHI_clear — 日変化・季節変化を除去。"""
    valid = ghi_clear > 10
    kappa = np.ones_like(ghi) * np.nan
    kappa[valid] = ghi[valid] / ghi_clear[valid]
    return kappa
```

**罠**: 多くの論文がclear-sky index ($\kappa$) とclearness index (kt = GHI/E₀) を混同。ktの正規化は不完全——κを使うべき。

## 3-10. 要約

| ステップ | 致命的ミス | 正しいアプローチ |
|---------|-----------|----------------|
| 日射量入力 | GHI直接使用 | POAに変換（Perezモデル） |
| 正規化 | Clearness index kt | Clear-sky index $\kappa$ |
| 品質管理 | 省略 | BSRN PPLテスト + 目視検査 |
| 欠損値 | 0や平均値で埋める | κ補間（短欠損）/ 使用不可マーク（長欠損） |
| データ分割 | ランダム分割 | 厳密な時間順序 |
| 特徴量 | 50変数を積み上げ | 物理的因果関係が必要 |
| ベースライン | 省略 | 持続性モデルは必須 |
| 評価 | RMSEのみ | MBE + RMSE + Skill Score + 日中のみ |

## 5大よくある建模ミス

1. **データ漏洩**: shuffle=True → 未来データが訓練に混入 → RMSE虚偽低下
2. **夜間データ**: 評価に含めると nRMSE が偽って低くなる
3. **過剰チューニング**: 検証セットで繰り返し調整 = 間接的に検証セットで訓練
4. **予測範囲無視**: 時間内と日前で同じモデル → ホライズン別に構築すべき
5. **晴天正規化なし**: モデルが天気ではなく季節変化を学習

---

## 📋 知識カード

> **核心原則**：データ処理に70%の時間、モデル選択に20%、チューニングに10%。多くの人は逆にしている。
