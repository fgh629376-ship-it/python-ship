---
title: 'Python 项目架构：从脚本到工程级代码的 7 个关键设计'
description: '别再写屎山了。类型注解、配置分离、日志系统、错误处理、模块拆分——用真实光伏预测场景演示工程级 Python 代码。'
pubDate: 2026-03-14
lang: zh
category: python
series: python-basics
tags: ['Python', '项目架构', '代码质量', '工程化', '光伏预测']
---

写脚本谁都会，但当代码超过 500 行、参与者超过 1 人、需要维护超过 1 个月——你就需要**工程级架构**。

本文用一个「光伏功率预测」迷你项目，演示从屎山到工程的 7 个关键设计。

## 1. 项目结构 —— 先画骨架再填肉

```
solar-forecast/
├── pyproject.toml          # 项目元数据 + 依赖
├── src/
│   └── solar_forecast/
│       ├── __init__.py
│       ├── config.py       # 配置管理
│       ├── models/         # 预测模型
│       │   ├── __init__.py
│       │   ├── base.py     # 抽象基类
│       │   ├── persistence.py
│       │   └── linear.py
│       ├── data/           # 数据加载与预处理
│       │   ├── __init__.py
│       │   └── loader.py
│       ├── evaluation/     # 评估指标
│       │   ├── __init__.py
│       │   └── metrics.py
│       └── utils/          # 工具函数
│           ├── __init__.py
│           └── logging.py
├── tests/
│   ├── test_models.py
│   └── test_metrics.py
└── scripts/
    └── train.py            # 入口脚本
```

**规则**：
- `src/` layout 防止导入混乱
- 每个目录一个职责
- `scripts/` 放入口，`src/` 放逻辑——永远不混

## 2. 类型注解 —— 代码即文档

屎山代码：
```python
# ❌ 猜参数类型，猜返回值，猜一辈子
def predict(data, params, steps):
    result = []
    for i in range(steps):
        val = sum(d * p for d, p in zip(data[-len(params):], params))
        result.append(val)
        data.append(val)
    return result
```

工程级代码：
```python
# ✅ 类型即文档，IDE 自动补全，重构不怕
from typing import Protocol
import numpy as np
from numpy.typing import NDArray

# 定义预测器协议——任何实现 predict 方法的类都是合法预测器
class Forecaster(Protocol):
    """所有预测模型必须实现此接口。"""

    def fit(self, X: NDArray[np.float64], y: NDArray[np.float64]) -> None: ...
    def predict(self, X: NDArray[np.float64], horizon: int) -> NDArray[np.float64]: ...

def evaluate_model(
    model: Forecaster,
    X_test: NDArray[np.float64],
    y_test: NDArray[np.float64],
    horizon: int = 24,
) -> dict[str, float]:
    """
    评估预测模型性能。

    Args:
        model: 已训练的预测器（满足 Forecaster 协议）
        X_test: 测试特征, shape (n_samples, n_features)
        y_test: 真实值, shape (n_samples,)
        horizon: 预测步长（小时）

    Returns:
        包含 RMSE、MAE、MBE 的字典
    """
    y_pred = model.predict(X_test, horizon)
    return {
        "rmse": float(np.sqrt(np.mean((y_test - y_pred) ** 2))),
        "mae": float(np.mean(np.abs(y_test - y_pred))),
        "mbe": float(np.mean(y_pred - y_test)),
    }
```

**关键**：`Protocol` 比 ABC 更灵活——不需要继承，只需实现方法。鸭子类型 + 静态检查，两全其美。

## 3. 配置管理 —— 硬编码是原罪

```python
# config.py
from dataclasses import dataclass, field
from pathlib import Path
import tomllib

@dataclass(frozen=True)
class DataConfig:
    """数据相关配置（不可变）。"""
    station_id: str = "BSRN_CAB"
    train_start: str = "2020-01-01"
    train_end: str = "2023-12-31"
    test_start: str = "2024-01-01"
    test_end: str = "2024-12-31"
    features: tuple[str, ...] = ("ghi", "temp_air", "wind_speed", "humidity")

@dataclass(frozen=True)
class ModelConfig:
    """模型相关配置。"""
    name: str = "linear"
    horizon_hours: int = 24
    learning_rate: float = 0.001
    max_epochs: int = 100
    batch_size: int = 64
    num_workers: int = 8  # i7-14650HX 24线程，8 workers 合理

@dataclass(frozen=True)
class AppConfig:
    """顶层配置，聚合所有子配置。"""
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    output_dir: Path = Path("outputs")
    log_level: str = "INFO"
    seed: int = 42

    @classmethod
    def from_toml(cls, path: str | Path) -> "AppConfig":
        """从 TOML 文件加载配置。"""
        with open(path, "rb") as f:
            raw = tomllib.load(f)
        return cls(
            data=DataConfig(**raw.get("data", {})),
            model=ModelConfig(**raw.get("model", {})),
            output_dir=Path(raw.get("output_dir", "outputs")),
            log_level=raw.get("log_level", "INFO"),
            seed=raw.get("seed", 42),
        )

# 使用
config = AppConfig.from_toml("config.toml")
print(config.model.horizon_hours)  # 24
# config.model.horizon_hours = 48  # ❌ frozen=True，不可变
```

**规则**：
- `frozen=True` 防止运行时意外修改配置
- TOML 是 Python 3.11+ 的标准配置格式（`tomllib` 内置）
- 嵌套 dataclass 比扁平 dict 可读性高 10 倍

## 4. 日志系统 —— print 是调试，logging 是工程

```python
# utils/logging.py
import logging
import sys
from pathlib import Path

def setup_logger(
    name: str = "solar_forecast",
    level: str = "INFO",
    log_file: Path | None = None,
) -> logging.Logger:
    """
    配置结构化日志。

    生产环境用文件 + 控制台双输出，
    开发环境只用控制台。
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # 文件输出（可选）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger

# 使用
logger = setup_logger("solar_forecast", level="DEBUG", log_file=Path("logs/train.log"))
logger.info("开始训练: model=%s, horizon=%dh", "linear", 24)
logger.warning("GPU 内存不足，回退到 CPU")
logger.error("数据文件缺失: %s", "2024-06-15.csv")
```

**输出**：
```
2026-03-14 22:00:01 | INFO     | solar_forecast | 开始训练: model=linear, horizon=24h
2026-03-14 22:00:03 | WARNING  | solar_forecast | GPU 内存不足，回退到 CPU
```

**规则**：永远用 `%s` 占位符而非 f-string——日志聚合工具能按模板分组。

## 5. 错误处理 —— 自定义异常比 ValueError 有灵魂

```python
# exceptions.py
class SolarForecastError(Exception):
    """项目基类异常，所有自定义异常继承它。"""

class DataNotFoundError(SolarForecastError):
    """数据文件不存在或无法读取。"""
    def __init__(self, station: str, date: str) -> None:
        self.station = station
        self.date = date
        super().__init__(f"找不到数据: station={station}, date={date}")

class ModelNotFittedError(SolarForecastError):
    """模型未训练就调用 predict。"""

class InvalidHorizonError(SolarForecastError):
    """预测步长不合法。"""
    def __init__(self, horizon: int) -> None:
        super().__init__(f"预测步长必须在 1-168h 之间，收到 {horizon}")

# 使用——调用方可以精准捕获
from pathlib import Path

def load_station_data(station: str, date: str) -> "pd.DataFrame":
    path = Path(f"data/{station}/{date}.csv")
    if not path.exists():
        raise DataNotFoundError(station, date)
    # ... 加载逻辑

# 调用方
try:
    df = load_station_data("BSRN_CAB", "2024-06-15")
except DataNotFoundError as e:
    logger.error("数据缺失: %s", e)
    # 精准处理：跳过这一天 or 用插值填充
except SolarForecastError as e:
    logger.error("未知项目错误: %s", e)
    raise
```

**规则**：
- 一个项目一个基类异常，所有子异常继承它
- 异常带上下文信息（station、date），不只是字符串
- `except Exception` 是懒人写法，生产代码要精准捕获

## 6. 向量化 —— NumPy 比 for 循环快 100 倍

```python
import numpy as np
import time

# 模拟一年的小时级光伏数据（8760 小时）
np.random.seed(42)
n = 8760
ghi = np.random.uniform(0, 1000, n)      # W/m²
temp = np.random.uniform(-10, 40, n)      # °C
power_actual = np.random.uniform(0, 500, n)  # kW

# ❌ 屎山写法：for 循环逐小时计算 RMSE
def rmse_loop(actual: list, predicted: list) -> float:
    total = 0.0
    for a, p in zip(actual, predicted):
        total += (a - p) ** 2
    return (total / len(actual)) ** 0.5

# ✅ 工程写法：NumPy 向量化
def rmse_vectorized(
    actual: NDArray[np.float64],
    predicted: NDArray[np.float64],
) -> float:
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))

# 性能对比
predicted = ghi * 0.18 - temp * 0.5  # 简单线性模型

t0 = time.perf_counter()
for _ in range(1000):
    rmse_loop(power_actual.tolist(), predicted.tolist())
t_loop = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(1000):
    rmse_vectorized(power_actual, predicted)
t_vec = time.perf_counter() - t0

print(f"for 循环: {t_loop:.3f}s")
print(f"向量化:   {t_vec:.3f}s")
print(f"加速比:   {t_loop / t_vec:.0f}x")
# 基于模型计算，非实测
```

**规则**：
- 任何涉及数组运算的逻辑，先想 NumPy 能不能做
- `np.mean`、`np.sqrt`、广播机制——这三样够解决 90% 的场景
- 实在需要循环？用 `numba.jit` 加速

## 7. 入口脚本 —— 把一切串起来

```python
#!/usr/bin/env python3
"""solar-forecast 训练入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from solar_forecast.config import AppConfig
from solar_forecast.utils.logging import setup_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="训练光伏功率预测模型")
    parser.add_argument(
        "--config", type=Path, default="config.toml",
        help="配置文件路径 (default: config.toml)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只验证配置，不实际训练",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # 1. 加载配置
    config = AppConfig.from_toml(args.config)

    # 2. 初始化日志
    logger = setup_logger(
        level=config.log_level,
        log_file=config.output_dir / "train.log",
    )
    logger.info("配置加载完成: %s", args.config)
    logger.info("模型: %s | 步长: %dh | seed: %d",
                config.model.name, config.model.horizon_hours, config.seed)

    # 3. 固定随机种子（可复现）
    np.random.seed(config.seed)

    if args.dry_run:
        logger.info("dry-run 模式，配置验证通过 ✅")
        return 0

    # 4. 加载数据 → 训练 → 评估 → 保存
    logger.info("开始训练...")
    # ... 实际训练逻辑
    logger.info("训练完成 ✅")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**规则**：
- `main()` 返回 int（退出码），方便脚本编排
- `argparse` 处理 CLI 参数，不在代码里硬编码路径
- 固定 seed 保证可复现——每次跑出一样的结果

---

## 📋 知识卡片

| 设计 | 屎山写法 | 工程写法 |
|------|---------|---------|
| 项目结构 | 全塞一个文件 | `src/` layout + 单一职责 |
| 类型 | 不写注解 | `Protocol` + `NDArray` + type hints |
| 配置 | 硬编码 `lr=0.001` | `frozen dataclass` + TOML 文件 |
| 日志 | `print("debug...")` | `logging` + 文件/控制台双输出 |
| 错误 | `raise ValueError` | 自定义异常层次 + 上下文信息 |
| 计算 | `for` 循环 | NumPy 向量化（100x 加速）|
| 入口 | `if __name__` 里写 300 行 | `main()` → `return int` + argparse |

> **下一步**：光伏预测项目启动时，直接用这套架构。写代码前先搭骨架，骨架对了，填肉才不会变成屎山。
