---
title: 'Python dataclass：ボイラープレートコードとおさらば'
description: '@dataclass で手書きの __init__/__repr__/__eq__ を置き換える — フィールドのデフォルト値、frozen、slots、継承、Pydantic との比較'
pubDate: '2026-03-13'
category: python
series: python-basics
lang: ja
tags: ['dataclass', 'Python進化', '知識カード']
---

## 痛点：シンプルなデータクラスを書くのに何行必要？

```python
# 従来の書き方 — ボイラープレート地獄
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))
```

```python
# dataclass — 一発で解決
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# __init__, __repr__, __eq__ を自動生成
p = Point(1.0, 2.0)
print(p)  # Point(x=1.0, y=2.0)
```

---

## よく使うパラメータ

```python
@dataclass(
    frozen=True,    # イミュータブル（__hash__ を生成し、代入を禁止）
    order=True,     # < > <= >= の比較をサポート
    slots=True,     # __slots__ を使用（メモリ節約、Python 3.10+）
    kw_only=True,   # すべてのフィールドをキーワード引数で渡す必要あり（3.10+）
)
class Config:
    host: str
    port: int = 8080
```

---

## フィールドのデフォルト値

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    age: int = 18                                  # シンプルなデフォルト値
    tags: list[str] = field(default_factory=list)  # ミュータブルなオブジェクトは field を使う必要あり

    # ❌ 間違った書き方：
    # tags: list[str] = []  # すべてのインスタンスが同じリストを共有してしまう！
```

---

## field() の高度な使い方

```python
from dataclasses import dataclass, field

@dataclass
class Employee:
    name: str
    _salary: float = field(repr=False)          # repr に表示しない
    id: int = field(init=False)                  # __init__ に含めない
    metadata: dict = field(default_factory=dict, compare=False)  # 比較に使用しない

    def __post_init__(self):
        # __init__ の後に自動的に呼び出される
        self.id = hash(self.name) % 10000
```

---

## `__post_init__` — 初期化後の処理

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        self.area = self.width * self.height
        if self.width < 0 or self.height < 0:
            raise ValueError("幅と高さは負の値にできません")

r = Rectangle(3, 4)
print(r.area)  # 12.0
```

---

## frozen=True — イミュータブルなデータクラス

```python
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

red = Color(255, 0, 0)
# red.r = 100  # ❌ FrozenInstanceError

# frozen は自動的に hash をサポート — dict のキーや set に入れられる
colors = {Color(255, 0, 0): "red", Color(0, 0, 255): "blue"}
```

---

## slots=True — メモリ節約（3.10+）

```python
@dataclass(slots=True)
class Sensor:
    id: int
    value: float
    timestamp: float

# 通常の dataclass より約 30% 少ないメモリ使用量
# 大量のインスタンスを作成するシナリオに最適
```

---

## 継承

```python
@dataclass
class Animal:
    name: str
    sound: str = "..."

@dataclass
class Dog(Animal):
    breed: str = "unknown"

d = Dog(name="Rex", sound="Woof", breed="Husky")
print(d)  # Dog(name='Rex', sound='Woof', breed='Husky')
```

⚠️ 注意：親クラスにデフォルト値を持つフィールドがある場合、子クラスのフィールドもデフォルト値を持つ必要があります（そうしないとエラーが発生します）。

---

## dict/tuple との相互変換

```python
from dataclasses import asdict, astuple

@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
asdict(p)    # {'x': 1.0, 'y': 2.0}
astuple(p)   # (1.0, 2.0)

# dict から作成
Point(**{'x': 3.0, 'y': 4.0})
```

---

## dataclass vs Pydantic vs NamedTuple

| 特性 | dataclass | Pydantic | NamedTuple |
|------|-----------|----------|------------|
| 実行時バリデーション | ❌ | ✅ | ❌ |
| JSON シリアライズ | 手動 | ✅ 組み込み | 手動 |
| パフォーマンス | 速い | やや遅い | 最速 |
| イミュータブル | frozen=True | オプション | デフォルトでイミュータブル |
| ユースケース | 内部データ構造 | API/設定 | 軽量タプルの代替 |

**選択のヒント：**
- 内部データの受け渡し → `dataclass`
- API 入力/設定ファイル → `Pydantic`
- シンプルな名前付きタプル → `NamedTuple`

---

## クイックリファレンスカード 📌

```
@dataclass が自動生成するもの：
  __init__  __repr__  __eq__

覚えるべき重要パラメータ：
  frozen=True  → イミュータブル + ハッシュ可能
  slots=True   → メモリ節約（3.10+）
  order=True   → 比較・ソートをサポート

ミュータブルなデフォルト値：
  ❌ tags: list = []
  ✅ tags: list = field(default_factory=list)

後処理：
  __post_init__() — 派生フィールドの計算、バリデーション

変換：
  asdict(obj)  astuple(obj)
```
