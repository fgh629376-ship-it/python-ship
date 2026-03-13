---
title: 'Python Decorators: From Syntactic Sugar to Industrial-Grade Patterns'
description: 'Master Python decorators — principles, function decorators, class decorators, parameterized decorators, @functools.wraps, and 10 real-world use cases'
category: python
lang: en
pubDate: '2026-03-13'
tags: ['装饰器', 'Python进阶', '技术干货']
---

## What Is a Decorator?

A decorator boils down to one sentence: **a function that takes a function and returns another function**.

```python
# These two are exactly equivalent
@my_decorator
def hello():
    print("hello")

# Same as:
def hello():
    print("hello")
hello = my_decorator(hello)
```

`@` is just syntactic sugar — nothing magical.

---

## The Simplest Decorator

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("before")
        result = func(*args, **kwargs)  # call the original
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

**`*args, **kwargs`** is the standard pattern — it lets the wrapper accept any arguments and pass them through transparently.

---

## Always Use `@functools.wraps`

Without it, the decorated function loses its identity:

```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # ← always add this!
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def hello():
    """This is the hello function"""
    pass

print(hello.__name__)  # hello (correct with wraps)
print(hello.__doc__)   # This is the hello function
```

---

## Parameterized Decorators

You need one extra layer of nesting:

```python
import functools

def repeat(n):           # outer: receives parameters
    def decorator(func): # middle: receives the function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # inner: execution logic
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

## 10 Industrial-Grade Decorator Patterns

### 1. Timer

```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_func():
    time.sleep(0.1)
```

### 2. Retry Mechanism

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
                    print(f"Attempt {attempt+1} failed, retrying...")
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def call_api():
    # potentially failing network request
    ...
```

### 3. Caching (Built-in)

```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Python 3.9+, unlimited cache
@cache
def expensive(n):
    return n ** 2
```

### 4. Type Checking

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
                    raise TypeError(f"{arg_name} expects {expected.__name__}, got {type(arg_val).__name__}")
        return func(*args, **kwargs)
    return wrapper

@type_check
def add(a: int, b: int) -> int:
    return a + b
```

### 5. Access Control

```python
from functools import wraps

def require_auth(role="user"):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not getattr(request, 'user', None):
                raise PermissionError("Not authenticated")
            if request.user.role != role:
                raise PermissionError(f"Requires {role} privileges")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

@require_auth(role="admin")
def delete_user(request, user_id):
    ...
```

### 6. Logging

```python
import logging
import functools

def log_calls(logger=None):
    def decorator(func):
        _logger = logger or logging.getLogger(func.__module__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger.info(f"Calling {func.__name__}({args}, {kwargs})")
            result = func(*args, **kwargs)
            _logger.info(f"{func.__name__} returned {result}")
            return result
        return wrapper
    return decorator
```

### 7. Singleton Pattern

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

## Class-Based Decorators

Implement decorators as classes when you need to maintain state:

```python
import functools

class Counter:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call count: {self.count}")
        return self.func(*args, **kwargs)

@Counter
def say_hello():
    print("Hello!")

say_hello()  # Call count: 1
say_hello()  # Call count: 2
print(say_hello.count)  # 2
```

---

## Stacking Order

When multiple decorators are stacked, they execute **bottom to top**:

```python
@decorator_A   # executes last (outermost)
@decorator_B   # executes first (innermost)
def func():
    pass

# Equivalent to:
func = decorator_A(decorator_B(func))
```

---

## Cheat Sheet 📌

```
The Decorator Trifecta:
  1. *args, **kwargs — transparent argument passing
  2. @functools.wraps — preserve function metadata
  3. return result — don't forget the return value

Parameterized decorator = 3 nested functions
  param layer → decorator layer → wrapper layer

Common built-in decorators:
  @property      — property access
  @staticmethod  — static method
  @classmethod   — class method
  @functools.lru_cache — caching
  @dataclasses.dataclass — data classes
```
