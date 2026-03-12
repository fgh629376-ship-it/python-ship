---
title: 'Python 3.12 新特性：你必须知道的6个改进'
description: 'Python 3.12 最重要的新特性详解 — f-string 升级、type 语句、性能提升、更清晰的错误信息'
pubDate: '2026-03-12'
tags: ['Python3.12', '技术干货', '知识卡片']
---

## Python 3.12 值得升级吗？

一句话：**值得**。3.12 是近几年变化最大的版本之一。

```bash
# 检查版本
python --version

# 用 pyenv 安装
pyenv install 3.12.0
pyenv global 3.12.0
```

---

## 1. f-string 全面升级

以前 f-string 里不能用同种引号，不能跨行，不能嵌套表达式。3.12 全解禁：

```python
# ✅ 3.12 — 现在可以在 f-string 里用同种引号
name = "Python"
print(f"Hello, {"world".upper()}!")  # Hello, WORLD!

# ✅ f-string 嵌套，以前只能用 \
data = {"key": "value"}
print(f"Result: {data["key"]}")  # Result: value

# ✅ 多行 f-string 表达式
result = f"""
Numbers: {
    ", ".join(str(i) for i in range(5))
}
"""
```

---

## 2. `type` 语句 — 类型别名

```python
# 旧写法（3.11及以前）
from typing import TypeAlias
Vector = list[float]  # 不够明确

# 新写法（3.12）
type Vector = list[float]
type Matrix = list[Vector]
type Callback[T] = Callable[[T], None]  # 支持泛型！

# 使用
def dot_product(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))
```

---

## 3. 泛型语法简化

```python
# 旧写法
from typing import TypeVar, Generic
T = TypeVar('T')

class Stack(Generic[T]):
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# 新写法（3.12）— 简洁多了！
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()

# 泛型函数也一样
def first[T](lst: list[T]) -> T:
    return lst[0]
```

---

## 4. 更清晰的错误信息

```python
# 3.11 之前
>>> import collections.abc
>>> collections.abc.Mapping[str, int][str, int]
TypeError: ...

# 3.12 — 精准指出问题
class Point:
    x: int
    y: int

p = Point()
print(p.z)
# AttributeError: 'Point' object has no attribute 'z'
# Did you mean: 'x' or 'y'?  ← 3.12 会给建议！
```

---

## 5. 性能提升

| 基准测试 | 3.11 vs 3.10 | 3.12 vs 3.11 |
|---------|-------------|-------------|
| 综合速度 | +25% | +5% |
| 内存使用 | 基线 | -10% |
| 启动时间 | 基线 | 更快 |

3.12 重点优化了**子解释器**（支持真正的多线程，实验性），未来潜力巨大。

---

## 6. `@override` 装饰器

```python
from typing import override

class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    @override  # 告诉类型检查器：这是有意重写父类方法
    def speak(self) -> str:
        return "Woof!"
    
    @override
    def fly(self) -> None:  # ❌ 类型检查器会报错！Animal 没有 fly 方法
        pass
```

---

## 知识卡片 📌

```
Python 3.12 六大亮点：

1. f-string  →  支持同种引号、嵌套、多行表达式
2. type 语句  →  清晰的类型别名定义
3. 泛型语法   →  class Foo[T] 代替 Generic[T]
4. 错误提示   →  更人性化，甚至会给出建议
5. 性能       →  内存降低，速度微升
6. @override  →  方法重写安全检查

升级命令：
  pyenv install 3.12.x
  poetry env use 3.12
```

现在还在用 3.10？可以升了，3.12 向后兼容性很好。
