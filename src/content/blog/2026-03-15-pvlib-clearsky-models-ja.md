---
title: 'pvlib 実践：快晴モデル — 太陽光発電予測の礎石'
description: '快晴モデルは太陽光発電予測における最も重要な単一ツールです。本記事では pvlib を使って Ineichen、Haurwitz、Simplified Solis の三大モデルを実践比較し、快晴指数 κ の物理的意味とエンジニアリング応用を解説します。'
pubDate: 2026-03-15
lang: ja
category: solar
series: pvlib
tags: ['pvlib', '快晴モデル', '太陽光発電予測', 'Clear Sky', 'Ineichen', '快晴指数']
---

## 快晴モデルがなぜ太陽光発電予測の礎石なのか？

GEFCom2014（グローバルエネルギー予測コンペ）での重要な事実：**快晴モデルを使用した唯一のチーム = 優勝チーム**。他のすべてのチームの予測は「影が薄く」なりました。

快晴モデルが教えてくれること：**今日が一面の快晴であれば、地表はどれだけの太陽放射照度を受けるべきか**。このベースラインがあれば、予測問題は「明日の GHI はいくつか」から「明日は雲がどれだけ遮るか」へと単純化されます——後者はより小さく、モデル化しやすい問題です。

核心となる式：

$$\kappa = \frac{\text{GHI}}{\text{GHI}_{\text{clear}}}$$

快晴指数 $\kappa$ は太陽位置による季節変動と日周期変動を除去し、予測モデルが天気の変化だけに集中できるようにします。

---

## pvlib の三大快晴モデル

pvlib は複雑さと精度が段階的に上がる三つの快晴モデルを提供しています：

| モデル | 入力パラメータ | 精度 | 適用場面 |
|--------|---------------|------|----------|
| **Haurwitz** | 天頂角のみ | ⭐⭐ | 簡易推定・教育用 |
| **Simplified Solis** | 天頂角 + エアロゾル + 水蒸気 + 気圧 | ⭐⭐⭐ | 中程度の精度が必要な場合 |
| **Ineichen-Perez** | 天頂角 + Linke 混濁度 | ⭐⭐⭐⭐ | 運用予測（推奨） |

---

## 完全なコード実践

### 1. 基本セットアップ

```python
import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 上海サイト
latitude, longitude = 31.23, 121.47
altitude = 4  # 標高(m)

# 2024年夏至
times = pd.date_range(
    '2024-06-21 00:00', '2024-06-21 23:59',
    freq='1min', tz='Asia/Shanghai'
)

# 太陽位置を計算
location = pvlib.location.Location(latitude, longitude, altitude=altitude)
solar_position = location.get_solarposition(times)
```

### 2. 三つの快晴モデルの比較

```python
# === Haurwitz（最もシンプル — 天頂角のみ必要）===
cs_haurwitz = location.get_clearsky(times, model='haurwitz')

# === Ineichen-Perez（推奨 — Linke 混濁度が必要）===
# pvlib は SoDa データベースから月平均 Linke 混濁度を自動取得
cs_ineichen = location.get_clearsky(times, model='ineichen')

# === Simplified Solis（エアロゾル光学的厚さが必要）===
cs_solis = location.get_clearsky(
    times, model='simplified_solis',
    aod700=0.1,          # 700nm におけるエアロゾル光学的厚さ
    precipitable_water=2.0,  # 可降水量(cm)
    pressure=101325      # 気圧(Pa)
)
```

### 3. 可視化比較

```python
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

components = ['ghi', 'dni', 'dhi']
titles = ['GHI (全天日射量)', 'DNI (直達法線面日射量)', 'DHI (散乱日射量)']

for ax, comp, title in zip(axes, components, titles):
    ax.plot(cs_haurwitz.index, cs_haurwitz[comp],
            label='Haurwitz', linewidth=1.5, linestyle='--')
    ax.plot(cs_ineichen.index, cs_ineichen[comp],
            label='Ineichen-Perez', linewidth=2)
    ax.plot(cs_solis.index, cs_solis[comp],
            label='Simplified Solis', linewidth=1.5, linestyle='-.')
    ax.set_ylabel(f'{title} (W/m²)')
    ax.legend()
    ax.grid(alpha=0.3)

axes[-1].set_xlabel('時刻 (上海, 2024-06-21)')
plt.suptitle('三大快晴モデルの比較 — 上海・夏至', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('clearsky_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 4. 快晴指数 κ の計算と応用

```python
# 1日分の実際の放射照度をシミュレート（雲の影響を追加）
np.random.seed(42)
cloud_factor = np.ones(len(times))

# シナリオをシミュレート：午前は晴れ、午後は曇り
for i, t in enumerate(times):
    hour = t.hour + t.minute / 60
    if 12 < hour < 16:
        # 午後の雲による遮蔽
        cloud_factor[i] = 0.3 + 0.4 * np.random.random()
    elif 10 < hour < 12:
        # 午前中の断続的な雲
        cloud_factor[i] = 0.7 + 0.3 * np.random.random()

# 実際の GHI = 快晴 GHI × 雲係数
ghi_actual = cs_ineichen['ghi'] * cloud_factor

# 快晴指数 κ を計算
kappa = ghi_actual / cs_ineichen['ghi'].replace(0, np.nan)

# 可視化
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

ax1.plot(times, cs_ineichen['ghi'], label='快晴 GHI', color='orange', linewidth=2)
ax1.plot(times, ghi_actual, label='実際の GHI', color='steelblue', alpha=0.8)
ax1.fill_between(times, ghi_actual, cs_ineichen['ghi'],
                  alpha=0.2, color='red', label='雲による損失')
ax1.set_ylabel('GHI (W/m²)')
ax1.legend()
ax1.set_title('快晴モデル vs 実際の放射照度')

ax2.plot(times, kappa, color='green', linewidth=1)
ax2.axhline(y=1.0, color='orange', linestyle='--', alpha=0.5, label='κ=1 (完全な快晴)')
ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='κ=0.5 (薄曇り)')
ax2.set_ylabel('快晴指数 κ')
ax2.set_xlabel('時刻')
ax2.set_ylim(0, 1.3)
ax2.legend()
ax2.set_title('快晴指数 κ = GHI / GHI_clear')

plt.tight_layout()
plt.savefig('clearsky_index.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 5. Linke 混濁度の影響

```python
# Linke 混濁度：大気透明度の指標
# 値が大きいほど → 大気が混濁 → 快晴放射照度が低下
linke_values = [2.0, 3.5, 5.0, 7.0]
labels = ['非常にクリーン (TL=2)', '標準的 (TL=3.5)', '汚染あり (TL=5)', '高度汚染 (TL=7)']

fig, ax = plt.subplots(figsize=(12, 5))

for tl, label in zip(linke_values, labels):
    cs = pvlib.clearsky.ineichen(
        solar_position['apparent_zenith'],
        airmass_absolute=location.get_airmass(times)['airmass_absolute'],
        linke_turbidity=tl,
        altitude=altitude
    )
    ax.plot(times, cs['ghi'], label=label, linewidth=2)

ax.set_ylabel('GHI (W/m²)')
ax.set_xlabel('時刻')
ax.set_title('Linke 混濁度が快晴 GHI に与える影響')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('linke_turbidity.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 6. 複数サイトでの快晴比較

```python
# 異なる気候帯における快晴モデルの違い
sites = {
    '上海 (湿潤亜熱帯)': (31.23, 121.47, 4),
    '敦煌 (乾燥砂漠)': (40.14, 94.68, 1139),
    'ラサ (高原)': (29.65, 91.10, 3650),
}

fig, ax = plt.subplots(figsize=(12, 5))

for name, (lat, lon, alt) in sites.items():
    loc = pvlib.location.Location(lat, lon, altitude=alt)
    cs = loc.get_clearsky(times, model='ineichen')
    ax.plot(times, cs['ghi'], label=name, linewidth=2)

ax.set_ylabel('GHI (W/m²)')
ax.set_xlabel('時刻 (2024-06-21)')
ax.set_title('異なるサイトの快晴 GHI 比較')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('multi_site_clearsky.png', dpi=150, bbox_inches='tight')
plt.show()
```

---

## 快晴モデル選択ガイド

> **教科書的結論（Yang & Kleissl, Ch5.4）**：快晴モデル間の性能差は、サイト間の差異と比べると**はるかに小さい**。快晴モデルの選択は限界的な重要性しか持たない。

実践的な推奨：

1. **運用予測** → **Ineichen-Perez**（時間的制約なし、数行のコードで完結）
2. **研究・検証** → **REST2**（MERRA-2 エアロゾルデータが必要、最高精度）
3. **迅速なプロトタイプ** → **Haurwitz**（外生パラメータ不要だが、DNI/DHI は出力されない）

---

## 重要な知見

- $\kappa$ の分布は通常**二峰性**：快晴ピーク $\approx 1.0$、曇天ピーク $\approx 0.3$–$0.5$
- **乗法的分解**（$\kappa = \text{GHI}/\text{GHI}_{\text{clear}}$）は加法的分解より優れている
- $\kappa > 1$ は物理的に正当！**雲増強効果**により瞬時 GHI が快晴値を約 50% 超えることがある
- 快晴指数は GHI 専用ではない——$\kappa_{\text{BNI}}, \kappa_{\text{POA}}, \kappa_{\text{PV}}$ も定義できる
- $\kappa$ を使って予測する際は**必ず快晴正規化を先に行うこと**。そうしないとモデルは天気の変化ではなく日の出・日の入りを学習してしまう

---

## 参考文献

- Yang, D. & Kleissl, J. (2024). *Solar Irradiance and PV Power Forecasting*, Ch4.5 & Ch5.4. CRC Press.
- Ineichen, P. & Perez, R. (2002). A new airmass independent formulation for the Linke turbidity coefficient. *Solar Energy*, 73(3), 151-157.
- Sun, X. et al. (2019). Worldwide performance assessment of 75 global clear-sky irradiance models. *Solar Energy*, 187, 392-404.
- Gueymard, C.A. (2008). REST2: High-performance solar radiation model. *Solar Energy*, 82(3), 272-285.
