---
title: "日射量から電力へ：Model Chain 完全ガイド + Firm Power の最終目標"
description: "教科書完結編 — Ch11 物理Model Chain（分離/転置/反射/温度/PVモデル/損失）+ Ch12 階層的予測とFirm Power"
category: solar
series: solar-book
lang: ja
pubDate: '2026-03-15'
tags: ["Model Chain", "pvlib", "階層的予測", "Firm Power", "太陽光予測"]
---

## 🎉 教科書完読！全12章完了

*Solar Irradiance and Photovoltaic Power Forecasting* (Yang & Kleissl, 2024) の最後の2章。Ch11は「日射量をどう電力に変換するか」、Ch12は「予測をどう系統運用に活かすか」。

---

## Ch11：日射量→電力変換

### 核心：2段階 > 1段階

- **1段階**（ML直接電力予測）：大量の履歴データが必要 + 各プラントで再訓練 → スケーラブルでない
- **2段階**（日射量予測 → Model Chain → 電力）：新規プラントでも使用可能 → 系統規模の唯一の選択肢

### Model Chain の7つのステージ

| ステージ | 現在のベストモデル | pvlib関数 |
|---------|-----------------|----------|
| 太陽位置 | SPA (±0.0003°) | `get_solarposition` |
| 分離 | YANG4 | `erbs` / カスタム |
| 転置 | Perez 1990 | `perez` |
| 反射損失 | Physical/Martin | `iam.physical` |
| 温度 | KING (Sandia) | `sapm_cell` |
| PVモデル | CEC単一ダイオード | `singlediode` |
| 損失 | インバータ+ケーブル+汚れ | `inverter.sandia` |

### 確率的Model Chain

最適ワークフロー：**確率的気象入力 + アンサンブルModel Chain + P2P後処理** → 確定的予測だけが必要でも、確率モデルを経由した方が良い結果。

---

## Ch12：階層的予測とFirm Power

### 階層的予測

電力系統は階層構造。最適調和法：**MinT-shrink**（収縮推定量付き最小トレース）

### Firm Power：究極の目標

| 概念 | 目標 | コスト乗数 |
|------|------|----------|
| Firm Forecasting | 発電が予測に完全一致 | ~2x |
| Firm Generation | 発電が負荷に完全一致 | ~3x |

**4つのFirm Power実現技術**：
1. **蓄電池** — 直感的だが単独では高コスト
2. **地理的平滑化** — 分散配置で変動低減
3. **負荷整形** — デマンドレスポンス
4. **過剰建設+能動的カーテイルメント** — **直感に反するが全実証研究で必要と確認**

> 蓄電池だけに頼ることはできない。最適 = 1.5x過剰建設 + 適度な蓄電池 + 地理的平滑化。

### 最重要メッセージ

**予測精度が高い → firmingコストが低い。** 予測研究は学術的な遊びではなく、数十億ドルのコストに直結する。

---

## 参考文献

- Yang, D. & Kleissl, J. (2024). CRC Press. Ch. 11-12.
- Mayer, M.J. & Yang, D. (2022, 2023b). *Solar Energy*. (Q1)
- Perez, R. et al. (2020, 2021). *Solar Energy*. (Q1)
