---
title: 'Python Project Architecture: 7 Key Designs from Script to Production Code'
description: 'Stop writing spaghetti code. Type hints, config separation, logging, error handling, modular design — demonstrated with a real solar forecasting scenario.'
pubDate: 2026-03-14
lang: en
category: python
series: python-basics
tags: ['Python', 'Architecture', 'Code Quality', 'Engineering', 'Solar Forecasting']
---

Anyone can write a script. But when code exceeds 500 lines, involves more than one person, or needs to be maintained for over a month — you need **production-grade architecture**.

This article uses a mini "solar power forecasting" project to demonstrate 7 key designs that separate clean code from spaghetti.

## 1. Project Structure — Skeleton First, Flesh Later

```
solar-forecast/
├── pyproject.toml
├── src/
│   └── solar_forecast/
│       ├── __init__.py
│       ├── config.py       # Configuration management
│       ├── models/         # Forecasting models
│       │   ├── __init__.py
│       │   ├── base.py     # Abstract base
│       │   ├── persistence.py
│       │   └── linear.py
│       ├── data/           # Data loading & preprocessing
│       │   ├── __init__.py
│       │   └── loader.py
│       ├── evaluation/     # Metrics
│       │   ├── __init__.py
│       │   └── metrics.py
│       └── utils/
│           ├── __init__.py
│           └── logging.py
├── tests/
│   ├── test_models.py
│   └── test_metrics.py
└── scripts/
    └── train.py            # Entry point
```

**Rules**: `src/` layout prevents import confusion. One directory = one responsibility. `scripts/` for entry points, `src/` for logic — never mix them.

## 2. Type Annotations — Code as Documentation

```python
# ❌ Spaghetti: guess types forever
def predict(data, params, steps):
    result = []
    for i in range(steps):
        val = sum(d * p for d, p in zip(data[-len(params):], params))
        result.append(val)
        data.append(val)
    return result

# ✅ Production: types ARE documentation
from typing import Protocol
import numpy as np
from numpy.typing import NDArray

class Forecaster(Protocol):
    """All forecasting models must implement this interface."""
    def fit(self, X: NDArray[np.float64], y: NDArray[np.float64]) -> None: ...
    def predict(self, X: NDArray[np.float64], horizon: int) -> NDArray[np.float64]: ...

def evaluate_model(
    model: Forecaster,
    X_test: NDArray[np.float64],
    y_test: NDArray[np.float64],
    horizon: int = 24,
) -> dict[str, float]:
    """Evaluate a forecasting model's performance."""
    y_pred = model.predict(X_test, horizon)
    return {
        "rmse": float(np.sqrt(np.mean((y_test - y_pred) ** 2))),
        "mae": float(np.mean(np.abs(y_test - y_pred))),
        "mbe": float(np.mean(y_pred - y_test)),
    }
```

**Key**: `Protocol` is more flexible than ABC — no inheritance needed, just implement the methods. Duck typing + static checking, best of both worlds.

## 3. Configuration Management — Hardcoding is Original Sin

```python
from dataclasses import dataclass, field
from pathlib import Path
import tomllib

@dataclass(frozen=True)
class DataConfig:
    """Immutable data configuration."""
    station_id: str = "BSRN_CAB"
    train_start: str = "2020-01-01"
    train_end: str = "2023-12-31"
    features: tuple[str, ...] = ("ghi", "temp_air", "wind_speed", "humidity")

@dataclass(frozen=True)
class ModelConfig:
    """Model configuration."""
    name: str = "linear"
    horizon_hours: int = 24
    learning_rate: float = 0.001
    max_epochs: int = 100
    batch_size: int = 64
    num_workers: int = 8

@dataclass(frozen=True)
class AppConfig:
    """Top-level config aggregating all sub-configs."""
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    output_dir: Path = Path("outputs")
    log_level: str = "INFO"
    seed: int = 42

    @classmethod
    def from_toml(cls, path: str | Path) -> "AppConfig":
        with open(path, "rb") as f:
            raw = tomllib.load(f)
        return cls(
            data=DataConfig(**raw.get("data", {})),
            model=ModelConfig(**raw.get("model", {})),
            output_dir=Path(raw.get("output_dir", "outputs")),
            log_level=raw.get("log_level", "INFO"),
            seed=raw.get("seed", 42),
        )
```

**Rules**: `frozen=True` prevents runtime mutation. TOML is Python 3.11+'s standard config format (`tomllib` built-in). Nested dataclasses are 10x more readable than flat dicts.

## 4. Logging — print is Debugging, logging is Engineering

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

**Rule**: Always use `%s` placeholders, not f-strings — log aggregation tools can group by template.

## 5. Error Handling — Custom Exceptions Have More Soul Than ValueError

```python
class SolarForecastError(Exception):
    """Project base exception."""

class DataNotFoundError(SolarForecastError):
    def __init__(self, station: str, date: str) -> None:
        self.station = station
        self.date = date
        super().__init__(f"Data not found: station={station}, date={date}")

class ModelNotFittedError(SolarForecastError):
    """Model predict() called before fit()."""

class InvalidHorizonError(SolarForecastError):
    def __init__(self, horizon: int) -> None:
        super().__init__(f"Horizon must be 1-168h, got {horizon}")
```

**Rules**: One project = one base exception. Exceptions carry context (station, date), not just strings. `except Exception` is lazy — production code catches precisely.

## 6. Vectorization — NumPy is 100x Faster Than For Loops

```python
import numpy as np
from numpy.typing import NDArray
import time

n = 8760  # One year of hourly data
np.random.seed(42)
actual = np.random.uniform(0, 500, n)
predicted = np.random.uniform(0, 500, n)

# ❌ Loop
def rmse_loop(a: list, p: list) -> float:
    return (sum((ai - pi)**2 for ai, pi in zip(a, p)) / len(a)) ** 0.5

# ✅ Vectorized
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

print(f"Loop:       {t_loop:.3f}s")
print(f"Vectorized: {t_vec:.3f}s")
print(f"Speedup:    {t_loop / t_vec:.0f}x")
# Based on model calculations, not real measurements
```

## 7. Entry Script — Tie Everything Together

```python
#!/usr/bin/env python3
"""Solar forecast training entry point."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
from solar_forecast.config import AppConfig
from solar_forecast.utils.logging import setup_logger

def main() -> int:
    parser = argparse.ArgumentParser(description="Train solar forecast model")
    parser.add_argument("--config", type=Path, default="config.toml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = AppConfig.from_toml(args.config)
    logger = setup_logger(level=config.log_level, log_file=config.output_dir / "train.log")
    np.random.seed(config.seed)

    if args.dry_run:
        logger.info("Dry-run: config validated ✅")
        return 0

    logger.info("Training: model=%s horizon=%dh", config.model.name, config.model.horizon_hours)
    # ... training logic
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 📋 Cheat Sheet

| Design | Spaghetti | Production |
|--------|-----------|------------|
| Structure | Everything in one file | `src/` layout + single responsibility |
| Types | No annotations | `Protocol` + `NDArray` + type hints |
| Config | Hardcoded `lr=0.001` | `frozen dataclass` + TOML |
| Logging | `print("debug...")` | `logging` + dual output |
| Errors | `raise ValueError` | Custom exception hierarchy |
| Compute | `for` loops | NumPy vectorization (100x speedup) |
| Entry | 300 lines in `__main__` | `main() → int` + argparse |

> **Next step**: When the solar forecasting project starts, use this architecture directly. Design the skeleton before writing code — get the bones right, and the flesh won't become spaghetti.
