---
title: 'Python プロジェクト設計：スクリプトから本番コードへの7つの鍵'
description: 'スパゲッティコードはもう卒業。型ヒント、設定分離、ログ、エラー処理、モジュール分割 — 太陽光発電予測の実例で解説。'
pubDate: 2026-03-14
lang: ja
category: python
series: python-basics
tags: ['Python', 'アーキテクチャ', 'コード品質', 'エンジニアリング', '太陽光発電予測']
---

スクリプトなら誰でも書ける。しかしコードが500行を超え、関わる人が1人以上、メンテ期間が1ヶ月を超えたら——**本番品質のアーキテクチャ**が必要だ。

本記事では「太陽光発電予測」ミニプロジェクトを題材に、スパゲッティから本番品質への7つの鍵を紹介する。

## 1. プロジェクト構造 — 骨格を先に、肉は後から

```
solar-forecast/
├── pyproject.toml
├── src/
│   └── solar_forecast/
│       ├── __init__.py
│       ├── config.py       # 設定管理
│       ├── models/         # 予測モデル
│       │   ├── __init__.py
│       │   ├── base.py     # 抽象基底
│       │   ├── persistence.py
│       │   └── linear.py
│       ├── data/           # データ読込・前処理
│       │   ├── __init__.py
│       │   └── loader.py
│       ├── evaluation/     # 評価指標
│       │   ├── __init__.py
│       │   └── metrics.py
│       └── utils/
│           ├── __init__.py
│           └── logging.py
├── tests/
│   ├── test_models.py
│   └── test_metrics.py
└── scripts/
    └── train.py            # エントリポイント
```

**ルール**：`src/` レイアウトでインポート混乱を防止。1ディレクトリ＝1責務。

## 2. 型アノテーション — コードがドキュメントになる

```python
# ❌ スパゲッティ：型を永遠に推測
def predict(data, params, steps):
    result = []
    for i in range(steps):
        val = sum(d * p for d, p in zip(data[-len(params):], params))
        result.append(val)
        data.append(val)
    return result

# ✅ 本番：型＝ドキュメント
from typing import Protocol
import numpy as np
from numpy.typing import NDArray

class Forecaster(Protocol):
    """全予測モデルが実装すべきインターフェース。"""
    def fit(self, X: NDArray[np.float64], y: NDArray[np.float64]) -> None: ...
    def predict(self, X: NDArray[np.float64], horizon: int) -> NDArray[np.float64]: ...

def evaluate_model(
    model: Forecaster,
    X_test: NDArray[np.float64],
    y_test: NDArray[np.float64],
    horizon: int = 24,
) -> dict[str, float]:
    """予測モデルの性能を評価する。"""
    y_pred = model.predict(X_test, horizon)
    return {
        "rmse": float(np.sqrt(np.mean((y_test - y_pred) ** 2))),
        "mae": float(np.mean(np.abs(y_test - y_pred))),
        "mbe": float(np.mean(y_pred - y_test)),
    }
```

**ポイント**：`Protocol` はABCより柔軟——継承不要、メソッドを実装するだけ。ダックタイピング＋静的チェックの両立。

## 3. 設定管理 — ハードコーディングは原罪

```python
from dataclasses import dataclass, field
from pathlib import Path
import tomllib

@dataclass(frozen=True)
class DataConfig:
    station_id: str = "BSRN_CAB"
    train_start: str = "2020-01-01"
    train_end: str = "2023-12-31"
    features: tuple[str, ...] = ("ghi", "temp_air", "wind_speed", "humidity")

@dataclass(frozen=True)
class ModelConfig:
    name: str = "linear"
    horizon_hours: int = 24
    learning_rate: float = 0.001
    max_epochs: int = 100
    num_workers: int = 8

@dataclass(frozen=True)
class AppConfig:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    output_dir: Path = Path("outputs")
    seed: int = 42

    @classmethod
    def from_toml(cls, path: str | Path) -> "AppConfig":
        with open(path, "rb") as f:
            raw = tomllib.load(f)
        return cls(
            data=DataConfig(**raw.get("data", {})),
            model=ModelConfig(**raw.get("model", {})),
            output_dir=Path(raw.get("output_dir", "outputs")),
            seed=raw.get("seed", 42),
        )
```

**ルール**：`frozen=True` で実行時の変更を防止。TOML は Python 3.11+ の標準設定フォーマット。

## 4. ログシステム — print はデバッグ、logging はエンジニアリング

```python
import logging
import sys
from pathlib import Path

def setup_logger(
    name: str = "solar_forecast",
    level: str = "INFO",
    log_file: Path | None = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger
```

**ルール**：f-stringではなく `%s` プレースホルダーを使う——ログ集約ツールがテンプレート別にグループ化できる。

## 5. エラー処理 — カスタム例外は ValueError より魂がある

```python
class SolarForecastError(Exception):
    """プロジェクト基底例外。"""

class DataNotFoundError(SolarForecastError):
    def __init__(self, station: str, date: str) -> None:
        self.station = station
        self.date = date
        super().__init__(f"データ未発見: station={station}, date={date}")

class ModelNotFittedError(SolarForecastError):
    """fit()前にpredict()を呼んだ。"""

class InvalidHorizonError(SolarForecastError):
    def __init__(self, horizon: int) -> None:
        super().__init__(f"ホライズンは1-168hの範囲、受け取り値: {horizon}")
```

## 6. ベクトル化 — NumPy は for ループより100倍速い

```python
import numpy as np
from numpy.typing import NDArray
import time

n = 8760
np.random.seed(42)
actual = np.random.uniform(0, 500, n)
predicted = np.random.uniform(0, 500, n)

# ❌ ループ
def rmse_loop(a: list, p: list) -> float:
    return (sum((ai - pi)**2 for ai, pi in zip(a, p)) / len(a)) ** 0.5

# ✅ ベクトル化
def rmse_vec(a: NDArray[np.float64], p: NDArray[np.float64]) -> float:
    return float(np.sqrt(np.mean((a - p) ** 2)))

t0 = time.perf_counter()
for _ in range(1000):
    rmse_loop(actual.tolist(), predicted.tolist())
t_loop = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(1000):
    rmse_vec(actual, predicted)
t_vec = time.perf_counter() - t0

print(f"ループ:       {t_loop:.3f}s")
print(f"ベクトル化:   {t_vec:.3f}s")
print(f"高速化倍率:   {t_loop / t_vec:.0f}x")
# モデル計算に基づく、実測データではない
```

## 7. エントリスクリプト — すべてを繋げる

```python
#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
from solar_forecast.config import AppConfig
from solar_forecast.utils.logging import setup_logger

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default="config.toml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = AppConfig.from_toml(args.config)
    logger = setup_logger(level=config.log_level, log_file=config.output_dir / "train.log")
    np.random.seed(config.seed)

    if args.dry_run:
        logger.info("Dry-run: 設定検証完了 ✅")
        return 0

    logger.info("訓練開始: model=%s horizon=%dh", config.model.name, config.model.horizon_hours)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 📋 知識カード

| 設計 | スパゲッティ | 本番品質 |
|------|-------------|----------|
| 構造 | 全部1ファイル | `src/` レイアウト + 単一責務 |
| 型 | アノテーションなし | `Protocol` + `NDArray` + 型ヒント |
| 設定 | ハードコード | `frozen dataclass` + TOML |
| ログ | `print("debug...")` | `logging` + デュアル出力 |
| エラー | `raise ValueError` | カスタム例外階層 |
| 計算 | `for` ループ | NumPy ベクトル化（100倍高速） |
| エントリ | `__main__` に300行 | `main() → int` + argparse |

> **次のステップ**：太陽光発電予測プロジェクト開始時、このアーキテクチャをそのまま使う。コードを書く前に骨格を設計 — 骨が正しければ、肉はスパゲッティにならない。
