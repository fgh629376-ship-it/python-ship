---
title: 'Python dataclass: Say Goodbye to Boilerplate Code'
description: 'Replace hand-written __init__/__repr__/__eq__ with @dataclass — field defaults, frozen, slots, inheritance, and comparison with Pydantic'
pubDate: '2026-03-13'
category: python
lang: en
tags: ['dataclass', 'Python进阶', '知识卡片']
---

## The Pain: How Many Lines Does a Simple Data Class Take?

```python
# Traditional approach — boilerplate hell
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
# dataclass — done in one line
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# Automatically generates __init__, __repr__, __eq__
p = Point(1.0, 2.0)
print(p)  # Point(x=1.0, y=2.0)
```

---

## Common Parameters

```python
@dataclass(
    frozen=True,    # Immutable (generates __hash__, disables assignment)
    order=True,     # Supports < > <= >= comparisons
    slots=True,     # Uses __slots__ (saves memory, Python 3.10+)
    kw_only=True,   # All fields must be passed as keyword arguments (3.10+)
)
class Config:
    host: str
    port: int = 8080
```

---

## Field Default Values

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    age: int = 18                                  # Simple default value
    tags: list[str] = field(default_factory=list)  # Mutable objects must use field

    # ❌ Wrong approach:
    # tags: list[str] = []  # All instances would share the same list!
```

---

## Advanced field() Usage

```python
from dataclasses import dataclass, field

@dataclass
class Employee:
    name: str
    _salary: float = field(repr=False)          # Not shown in repr
    id: int = field(init=False)                  # Not included in __init__
    metadata: dict = field(default_factory=dict, compare=False)  # Not used in comparison

    def __post_init__(self):
        # Automatically called after __init__
        self.id = hash(self.name) % 10000
```

---

## `__post_init__` — Post-Initialization Processing

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        self.area = self.width * self.height
        if self.width < 0 or self.height < 0:
            raise ValueError("Width and height cannot be negative")

r = Rectangle(3, 4)
print(r.area)  # 12.0
```

---

## frozen=True — Immutable Dataclass

```python
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

red = Color(255, 0, 0)
# red.r = 100  # ❌ FrozenInstanceError

# frozen automatically supports hash — can be used as dict key or in a set
colors = {Color(255, 0, 0): "red", Color(0, 0, 255): "blue"}
```

---

## slots=True — Save Memory (3.10+)

```python
@dataclass(slots=True)
class Sensor:
    id: int
    value: float
    timestamp: float

# ~30% less memory than a regular dataclass
# Ideal for scenarios with large numbers of instances
```

---

## Inheritance

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

⚠️ Note: If the parent class has fields with default values, child class fields must also have default values (otherwise an error is raised).

---

## Converting to dict/tuple

```python
from dataclasses import asdict, astuple

@dataclass
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
asdict(p)    # {'x': 1.0, 'y': 2.0}
astuple(p)   # (1.0, 2.0)

# Create from dict
Point(**{'x': 3.0, 'y': 4.0})
```

---

## dataclass vs Pydantic vs NamedTuple

| Feature | dataclass | Pydantic | NamedTuple |
|---------|-----------|----------|------------|
| Runtime validation | ❌ | ✅ | ❌ |
| JSON serialization | Manual | ✅ Built-in | Manual |
| Performance | Fast | Slightly slower | Fastest |
| Immutability | frozen=True | Optional | Immutable by default |
| Use case | Internal data structures | API/config | Lightweight tuple replacement |

**Recommendations:**
- Internal data passing → `dataclass`
- API inputs/config files → `Pydantic`
- Simple named tuples → `NamedTuple`

---

## Quick Reference Card 📌

```
@dataclass auto-generates:
  __init__  __repr__  __eq__

Key parameters to remember:
  frozen=True  → Immutable + hashable
  slots=True   → Saves memory (3.10+)
  order=True   → Supports comparison and sorting

Mutable defaults:
  ❌ tags: list = []
  ✅ tags: list = field(default_factory=list)

Post-processing:
  __post_init__() — compute derived fields, validate

Conversion:
  asdict(obj)  astuple(obj)
```
