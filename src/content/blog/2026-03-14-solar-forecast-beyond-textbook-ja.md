---
title: '教科書の先へ：太陽光発電予測で見落とされがちな8つの重要問題'
description: '473引用のML比較、κ vs ktの数学的証明、NWP後処理のベストプラクティス——トップジャーナルの知見を整理。'
pubDate: 2026-03-14
lang: ja
category: solar
series: solar-book
tags: ['太陽光発電予測', '論文精読', 'データ処理', 'NWP', '機械学習', 'ベストプラクティス']
---

> **全参考文献はCAS Q1/Q2ジャーナル：**
> - Markovics & Mayer (2022), *R&SE Reviews* (Q1 Top, 473引用)
> - Yang (2020), *JRSE* (Q2, 135引用)
> - Lauret et al. (2022), *Solar* (Q2, 35引用)
> - Yang et al. (2021), *Solar Energy* (Q2, 100引用)

## 1. 68のMLモデルベンチマーク：銀の弾丸はない

Markovics & Mayer (2022) の核心発見：
- 勾配ブースティング（XGBoost/LightGBM）が総合最優
- 深層学習は日前予測で従来MLに対し有意な優位性なし
- モデル選択 < 特徴エンジニアリングとデータ品質

## 2. κ vs kt：数学的に κ が優れる理由

κ（clear-sky index）はkt（clearness index）より一桁小さい標準偏差 → 天文信号の除去がより徹底的。

## 3. 晴天モデルの選択：Skillに5-10%の影響

Ineichen-Perez = 最適コストパフォーマンス。

## 4. NWP後処理：MOSがゴールドスタンダード

## 5. 確率的予測は選択肢ではない

電力系統運用者は確率分布を必要とする。推奨：分位点回帰 → QRF → NGBoost。

## 6-8. 空間相関、評価指標の罠、デプロイメント問題

（中国語版に詳細なコード例あり）

---

## 📋 知識カード

| 論文 | ジャーナル | 核心的洞察 |
|------|----------|-----------|
| Markovics & Mayer (2022) | R&SE Reviews (Q1 Top) | XGBoostが日前予測で最適 |
| Yang (2020) | JRSE (Q2) | 晴天モデル選択がSkillに5-10%影響 |
| Lauret et al. (2022) | Solar (Q2) | κはktより天文信号除去が徹底 |
| Yang et al. (2021) | Solar Energy (Q2) | 運用予測にはフォールバック計画必要 |

> **核心原則**：(1) まずXGBoost、(2) κ + Ineichen-Perez = 最適、(3) 確率出力が真の需要、(4) デプロイ ≠ 訓練
