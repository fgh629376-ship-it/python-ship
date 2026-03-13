---
title: 'Python 装饰器：从语法糖到工业级用法'
description: '彻底搞懂 Python decorator — 原理、函数装饰器、类装饰器、带参数装饰器、@functools.wraps、实战10个常用场景'
category: python
pubDate: '2026-03-13'
tags: ['装饰器', 'Python进阶', '技术干货']
---

## 装饰器是什么？

装饰器的本质就一句话：**接收一个函数，返回另一个函数的函数**。

```python
# 这两种写法完全等价
@my_decorator
def hello():
    print("hello")

# 等价于：
def hello():
    print("hello")
hello = my_decorator(hello)
```

`@` 只是语法糖，不神秘。

---

## 最简装饰器

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("before")
        result = func(*args, **kwargs)  # 调用原函数
        print("after")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}!")

greet("Python")
# before
# Hello, Python!
# after
```

**`*args, **kwargs`** 是标配 — 让 wrapper 能接受任意参数，透明传给原函数。

---

## 必须加 `@functools.wraps`

不加的话，被装饰的函数会"失去身份"：

```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # ← 必须加这个！
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def hello():
    """这是 hello 函数"""
    pass

print(hello.__name__)  # hello（加了 wraps 才正确）
print(hello.__doc__)   # 这是 hello 函数
```

---

## 带参数的装饰器

需要多套一层函数：

```python
import functools

def repeat(n):           # 最外层：接收参数
    def decorator(func): # 中间层：接收函数
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # 最内层：执行逻辑
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say(msg):
    print(msg)

say("hi")
# hi
# hi
# hi
```

---

## 10 个工业级装饰器场景

### 1. 计时器

```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} 耗时 {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_func():
    time.sleep(0.1)
```

### 2. 重试机制

```python
import functools, time

def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
                    print(f"第 {attempt+1} 次失败，重试...")
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def call_api():
    # 可能失败的网络请求
    ...
```

### 3. 缓存（内置版）

```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Python 3.9+，无限缓存
@cache
def expensive(n):
    return n ** 2
```

### 4. 类型检查

```python
import functools
from typing import get_type_hints

def type_check(func):
    hints = get_type_hints(func)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for arg_name, arg_val in zip(func.__code__.co_varnames, args):
            if arg_name in hints:
                expected = hints[arg_name]
                if not isinstance(arg_val, expected):
                    raise TypeError(f"{arg_name} 需要 {expected.__name__}，got {type(arg_val).__name__}")
        return func(*args, **kwargs)
    return wrapper

@type_check
def add(a: int, b: int) -> int:
    return a + b
```

### 5. 权限控制

```python
from functools import wraps

def require_auth(role="user"):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not getattr(request, 'user', None):
                raise PermissionError("未登录")
            if request.user.role != role:
                raise PermissionError(f"需要 {role} 权限")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

@require_auth(role="admin")
def delete_user(request, user_id):
    ...
```

### 6. 日志记录

```python
import logging
import functools

def log_calls(logger=None):
    def decorator(func):
        _logger = logger or logging.getLogger(func.__module__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger.info(f"调用 {func.__name__}({args}, {kwargs})")
            result = func(*args, **kwargs)
            _logger.info(f"{func.__name__} 返回 {result}")
            return result
        return wrapper
    return decorator
```

### 7. 单例模式

```python
def singleton(cls):
    instances = {}
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Config:
    def __init__(self):
        self.debug = False
```

---

## 类装饰器

用类实现装饰器，适合需要保存状态的场景：

```python
import functools

class Counter:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"调用次数：{self.count}")
        return self.func(*args, **kwargs)

@Counter
def say_hello():
    print("Hello!")

say_hello()  # 调用次数：1
say_hello()  # 调用次数：2
print(say_hello.count)  # 2
```

---

## 装饰器叠加顺序

多个装饰器叠加时，**从下往上执行**：

```python
@decorator_A   # 最后执行（最外层）
@decorator_B   # 先执行（最内层）
def func():
    pass

# 等价于：
func = decorator_A(decorator_B(func))
```

---

## 知识卡片 📌

```
装饰器三件套：
  1. *args, **kwargs — 透明传参
  2. @functools.wraps — 保留函数元信息
  3. return result — 别忘了返回值

带参数装饰器 = 3层嵌套函数
  参数层 → 装饰器层 → wrapper 层

常用内置装饰器：
  @property      — 属性访问
  @staticmethod  — 静态方法
  @classmethod   — 类方法
  @functools.lru_cache — 缓存
  @dataclasses.dataclass — 数据类
```
