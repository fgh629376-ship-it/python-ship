---
title: 'Python dataclass：告别样板代码'
description: '用 @dataclass 替代手写 __init__/__repr__/__eq__ — 字段默认值、frozen、slots、继承、与 Pydantic 对比'
category: python
lang: zh
pubDate: '2026-03-13'
tags: ['dataclass', 'Python进阶', '知识卡片']
---

## 痛点：写一个简单的数据类要多少行？

```python
# 传统写法 — 样板代码地狱
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
# dataclass — 一行搞定
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# 自动生成 __init__, __repr__, __eq__
p = Point(1.0, 2.0)
print(p)  # Point(x=1.0, y=2.0)
```

---

## 常用参数

```python
@dataclass(
    frozen=True,    # 不可变（生成 __hash__，禁止赋值）
    order=True,     # 支持 < > <= >= 比较
    slots=True,     # 使用 __slots__（省内存，Python 3.10+）
    kw_only=True,   # 所有字段必须用关键字传参（3.10+）
)
class Config:
    host: str
    port: int = 8080
```

---

## 字段默认值

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    age: int = 18                                  # 简单默认值
    tags: list[str] = field(default_factory=list)  # 可变对象必须用 field

    # ❌ 错误写法：
    # tags: list[str] = []  # 所有实例会共享同一个列表！
```

---

## field() 高级用法

```python
from dataclasses import dataclass, field

@dataclass
class Employee:
    name: str
    _salary: float = field(repr=False)          # 不显示在 repr 中
    id: int = field(init=False)                  # 不参与 __init__
    metadata: dict = field(default_factory=dict, compare=False)  # 不参与比较

    def __post_init__(self):
        # __init__ 之后自动调用
        self.id = hash(self.name) % 10000
```

---

## `__post_init__` — 初始化后处理

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        self.area = self.width * self.height
        if self.width < 0 or self.height < 0:
            raise ValueError("长宽不能为负")

r = Rectangle(3, 4)
print(r.area)  # 12.0
```

---

## frozen=True — 不可变数据类

```python
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

red = Color(255, 0, 0)
# red.r = 100  # ❌ FrozenInstanceError

# frozen 自动支持 hash，可以当 dict key 或放进 set
colors = {Color(255, 0, 0): "red", Color(0, 0, 255): "blue"}
```

---

## slots=True — 省内存（3.10+）

```python
@dataclass(slots=True)
class Sensor:
    id: int
    value: float
    timestamp: float

# 比普通 dataclass 省 ~30% 内存
# 适合创建大量实例的场景
```

---

## 继承

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

⚠️ 注意：父类有默认值的字段，子类的字段也必须有默认值（否则报错）。

---

## 与 dict/tuple 互转

```python
from dataclasses import asdict, astuple

@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
asdict(p)    # {'x': 1.0, 'y': 2.0}
astuple(p)   # (1.0, 2.0)

# 从 dict 创建
Point(**{'x': 3.0, 'y': 4.0})
```

---

## dataclass vs Pydantic vs NamedTuple

| 特性 | dataclass | Pydantic | NamedTuple |
|------|-----------|----------|------------|
| 运行时验证 | ❌ | ✅ | ❌ |
| JSON 序列化 | 手动 | ✅ 内置 | 手动 |
| 性能 | 快 | 稍慢 | 最快 |
| 不可变 | frozen=True | 可选 | 默认不可变 |
| 使用场景 | 内部数据结构 | API/配置 | 轻量元组替代 |

**选择建议：**
- 内部数据传递 → `dataclass`
- API 入参/配置文件 → `Pydantic`
- 简单的命名元组 → `NamedTuple`

---

## 知识卡片 📌

```
@dataclass 自动生成：
  __init__  __repr__  __eq__

必记参数：
  frozen=True  → 不可变 + 可 hash
  slots=True   → 省内存（3.10+）
  order=True   → 支持比较排序

可变默认值：
  ❌ tags: list = []
  ✅ tags: list = field(default_factory=list)

后处理：
  __post_init__() — 计算派生字段、校验

互转：
  asdict(obj)  astuple(obj)
```
