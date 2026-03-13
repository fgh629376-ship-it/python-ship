---
title: 'pvlib パワーコンディショナーモデル徹底比較：Sandia vs ADR vs PVWatts'
description: '3大パワーコンディショナーモデルのパラメータ体系・効率曲線・電圧感度を全面比較。実際のデータベース呼び出しコードも含め、太陽光シミュレーションで適切なモデルを選ぶ方法を解説'
pubDate: '2026-03-13'
category: solar
lang: ja
tags: ["pvlib", "光伏", "逆变器", "技术干货", "仿真"]
---

pvlib は3つの主要なパワーコンディショナー（インバーター）モデルを提供しています：**Sandia**、**ADR（Anton Driesse）**、**PVWatts**。モデルを誤って選択すると年間発電量の予測が2%以上ずれる可能性があります — この記事では実際のコードを使ってすべてを徹底的に解説します。

## なぜパワーコンディショナーモデルが重要なのか？

パワーコンディショナーの効率は定数ではなく、出力と電圧によって変化します。公称効率 96% のパワーコンディショナーでも、10% 負荷では 92% しか達成できないことがあり、過負荷時にはさらに急落します。モデルを誤るとシステムシミュレーションに系統的な誤差が生じます。

## 3モデルの概要

| 特性 | Sandia | ADR | PVWatts |
|------|--------|-----|---------|
| パラメータ出所 | 実測フィッティング | 物理 + フィッティング | 簡略経験則 |
| 電圧感度 | ✅ あり | ✅ あり | ❌ なし |
| データベース | `SandiaInverter` | `ADRInverter` | データベース不要 |
| 精度 | 高い | 高い | 中程度 |
| 用途 | 詳細シミュレーション | 研究用途 | 簡易推算 |

## コード実践

### データベースの読み込み

```python
import pvlib
import numpy as np

# Sandia データベース（世界の主要パワーコンディショナーを網羅）
inv_db = pvlib.pvsystem.retrieve_sam('SandiaInverter')
sandia_params = inv_db['SMA_America__SB5000TL_US_22__208V_']

# ADR データベース
adr_db = pvlib.pvsystem.retrieve_sam('ADRInverter')
adr_params = adr_db['Ablerex_Electronics_Co___Ltd___ES_5000_US_240__240_Vac__240V__CEC_2011_']

print("Sandia 定格出力:", sandia_params['Paco'], "W")
print("ADR 定格出力:", adr_params['Pacmax'], "W")
# 出力:
# Sandia 定格出力: 4580.0 W
# ADR 定格出力: 5240.0 W
```

### Sandia モデルの呼び出し

```python
# パラメータ：v_dc（直流電圧）, p_dc（直流出力）, パラメータ辞書
pdc_arr = np.linspace(50, 5500, 200)
v_nom = 400.0  # 動作電圧

ac_sandia = pvlib.inverter.sandia(v_nom, pdc_arr, sandia_params)
# Paco を超えると自動的にクリップ、NaN または Paco を返す
```

**主要パラメータの解説：**
- `Paco`：AC 定格上限（クリップポイント）
- `Pdco`：定格 AC 出力に対応する DC 出力
- `Vdco`：最高効率に対応する DC 電圧
- `C0~C3`：効率曲線の 4 つのフィッティング係数
- `Pso`：自己消費閾値（この DC 出力以下では AC 出力がゼロ）

### PVWatts モデルの呼び出し

```python
# 最もシンプル：定格出力と効率だけが必要
pdc0 = 5000  # 定格 DC 出力 [W]
eta_nom = 0.96  # 定格効率

ac_pvwatts = pvlib.inverter.pvwatts(pdc_arr, pdc0, eta_nom)
# pdc0 * 1.1 を超えるとクリップ
```

PVWatts は内部で区分多項式の効率曲線を使用し、**電圧に依存しません** — 1つのパラメータで完結します。

### ADR モデルの呼び出し

```python
# ADR パラメータは ADRInverter データベースから
# 注意：v0.15.0 では ADR は配列入力に対応していないため、スカラーでループする必要あり
ac_adr = np.array([
    pvlib.inverter.adr(v_nom, float(p), adr_params)
    for p in pdc_arr
])
```

ADR は 9 つの係数を持つ 2 次元多項式を使用し、出力と電圧の両方が効率に与える影響を同時に記述します。3つのモデルの中で最も物理的な意味が明確です。

## 効率曲線の実測比較

```python
eff_sandia  = ac_sandia  / pdc_arr * 100
eff_pvwatts = ac_pvwatts / pdc_arr * 100
eff_adr     = ac_adr     / pdc_arr * 100
```

| DC 出力 | 定格比 | Sandia | PVWatts | ADR |
|---------|--------|--------|---------|-----|
| 296 W | 5% | 92.25% | 88.19% | 87.36% |
| 543 W | 10% | 94.99% | 92.61% | 92.27% |
| 1036 W | 20% | 96.43% | 95.03% | 94.91% |
| 2515 W | 50% | **96.92%** | 96.22% | 96.07% |
| 3747 W | 75% | 96.70% | 96.21% | 95.91% |
| 4980 W | 100% | 91.97% | 96.00% | 95.54% |

**重要な発見：**

1. **Sandia は 100% 負荷時に効率が急落します**：テスト機器の Pdco=4747W < Pac=4580W のため、定格に近い時点で AC 出力がすでにクリップされており、効率の数値が歪んでいます。これはデータベースのパラメータと実際のパワーコンディショナーが一致しない場合によく見られる問題です。

2. **PVWatts は楽観的すぎます**：100% 負荷でも 96% を示しますが、実際のパワーコンディショナーは満負荷に近づくと効率が低下します。

3. **ADR が最も滑らかです**：110% 過負荷でも合理的な 95.27% を示し、モデルの外挿性能が優れています。

## 電圧感度：見落とされがちな重要要因

```python
# PDC=3000W 時に DC 電圧を変化させる
for v in [300, 350, 384, 400, 450]:
    ac_s = pvlib.inverter.sandia(v, 3000.0, sandia_params)
    ac_a = pvlib.inverter.adr(v, 3000.0, adr_params)
    ac_p = pvlib.inverter.pvwatts(3000.0, pdc0, eta_nom)  # 変化なし
    print(f"V={v}V: Sandia={ac_s:.1f}W, ADR={ac_a:.1f}W, PVWatts={ac_p:.1f}W")

# V=300V: Sandia=2897.6W, ADR=2866.0W, PVWatts=2887.6W（固定）
# V=450V: Sandia=2912.0W, ADR=2893.8W, PVWatts=2887.6W（固定）
```

300V から 450V の範囲で、Sandia の出力変化は約 **14W**、ADR は約 **28W** 変化します。冬と夏で直流電圧が 100V 異なるシステムでは、この差が累積して有意な誤差になります。**PVWatts は電圧を完全に無視しており、これが主な欠点です。**

## CEC 加重効率の計算

CEC（カリフォルニアエネルギー委員会）は 6 つの出力ポイントの加重平均でパワーコンディショナーを評価します。これを「CEC 効率」とも呼びます：

```python
weights = [0.04, 0.05, 0.12, 0.21, 0.53, 0.05]  # 10/20/30/50/75/100%
pcts = [10, 20, 30, 50, 75, 100]

cec_sandia  = sum(w * eff_sandia[int(p/110*199)]  for w, p in zip(weights, pcts))
cec_pvwatts = sum(w * eff_pvwatts[int(p/110*199)] for w, p in zip(weights, pcts))
cec_adr     = sum(w * eff_adr[int(p/110*199)]     for w, p in zip(weights, pcts))

# 結果：
# Sandia CEC 効率:  96.44%
# PVWatts CEC 効率: 95.95%
# ADR CEC 効率:     95.71%
```

## モデル選択ガイド

**Sandia を使う場合：**
- 対象パワーコンディショナーの Sandia データベースレコードが見つかる
- 最高のシミュレーション精度が必要（実測データとの一致）
- エネルギー監査や性能保証分析を行っている

**ADR を使う場合：**
- 研究目的、または複数のパワーコンディショナーの特性を比較したい
- Sandia データベースにないが ADR データベースにある
- 良好な電圧外挿能力が必要

**PVWatts を使う場合：**
- 簡易推算、正確なパワーコンディショナーデータが不要
- 初期フィージビリティスタディ
- データベースに対応機器が見つからない

## 実践的な使用上のヒント

```python
# ModelChain でパワーコンディショナーモデルを指定
system = pvlib.pvsystem.PVSystem(
    ...,
    inverter_parameters=sandia_params,
    inverter='sandia'  # または 'pvwatts', 'adr'
)
mc = pvlib.modelchain.ModelChain(system, location)
```

データベースにパワーコンディショナーが見つからない場合、メーカーが提供する効率曲線から Sandia パラメータを逆算できます（pvlib には `pvlib.inverter.fit_sandia` 関数があります）。

---

📋 **クイックリファレンスカード**

| 要点 | 結論 |
|------|------|
| 最高精度 | Sandia（実測フィッティング、クリップ処理あり） |
| 研究に最適 | ADR（物理的意味が明確、外挿性能が良い） |
| 最もシンプルで速い | PVWatts（1パラメータ、電圧依存なし） |
| 電圧感度 | Sandia > ADR >> PVWatts（= 0） |
| 低負荷精度 | モデル間の差が最大 — Sandia が最優秀 |
| 推奨データベース | `pvlib.pvsystem.retrieve_sam('SandiaInverter')` |
| ADR の注意点 | pvlib 0.15 は配列入力に非対応、逐点計算が必要 |
