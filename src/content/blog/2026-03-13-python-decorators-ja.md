---
title: 'Python デコレータ：シンタックスシュガーから実務レベルの活用まで'
description: 'Python decorator を完全理解 — 原理、関数デコレータ、クラスデコレータ、引数付きデコレータ、@functools.wraps、実践10パターン'
category: python
series: python-basics
lang: ja
pubDate: '2026-03-13'
tags: ['装饰器', 'Python进阶', '技术干货']
---

## デコレータとは？

デコレータの本質は一言で言えます：**関数を受け取り、別の関数を返す関数**です。

```python
# この2つは完全に同じ意味です
@my_decorator
def hello():
    print("hello")

# これと同等：
def hello():
    print("hello")
hello = my_decorator(hello)
```

`@` はシンタックスシュガーに過ぎません。特別なものではありません。

---

## 最もシンプルなデコレータ

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("before")
        result = func(*args, **kwargs)  # 元の関数を呼び出す
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

**`*args, **kwargs`** は定番パターンです。wrapper が任意の引数を受け取り、元の関数に透過的に渡せるようにします。

---

## `@functools.wraps` は必須です

付けないと、デコレートされた関数が「アイデンティティ」を失います：

```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # ← 必ずこれを付けましょう！
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def hello():
    """これは hello 関数です"""
    pass

print(hello.__name__)  # hello（wraps があるので正しい）
print(hello.__doc__)   # これは hello 関数です
```

---

## 引数付きデコレータ

もう一層ネストが必要です：

```python
import functools

def repeat(n):           # 最外層：引数を受け取る
    def decorator(func): # 中間層：関数を受け取る
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # 最内層：実行ロジック
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

## 実務で使える10のデコレータパターン

### 1. タイマー

```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} の実行時間: {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_func():
    time.sleep(0.1)
```

### 2. リトライ機構

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
                    print(f"第{attempt+1}回失敗、リトライ中...")
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def call_api():
    # 失敗する可能性のあるネットワークリクエスト
    ...
```

### 3. キャッシュ（組み込み版）

```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Python 3.9+、無制限キャッシュ
@cache
def expensive(n):
    return n ** 2
```

### 4. 型チェック

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
                    raise TypeError(f"{arg_name} は {expected.__name__} 型が必要ですが、{type(arg_val).__name__} が渡されました")
        return func(*args, **kwargs)
    return wrapper

@type_check
def add(a: int, b: int) -> int:
    return a + b
```

### 5. アクセス制御

```python
from functools import wraps

def require_auth(role="user"):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not getattr(request, 'user', None):
                raise PermissionError("未認証です")
            if request.user.role != role:
                raise PermissionError(f"{role} 権限が必要です")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

@require_auth(role="admin")
def delete_user(request, user_id):
    ...
```

### 6. ログ記録

```python
import logging
import functools

def log_calls(logger=None):
    def decorator(func):
        _logger = logger or logging.getLogger(func.__module__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger.info(f"{func.__name__}({args}, {kwargs}) を呼び出し")
            result = func(*args, **kwargs)
            _logger.info(f"{func.__name__} の戻り値: {result}")
            return result
        return wrapper
    return decorator
```

### 7. シングルトンパターン

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

## クラスデコレータ

状態を保持する必要がある場合、クラスでデコレータを実装します：

```python
import functools

class Counter:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"呼び出し回数：{self.count}")
        return self.func(*args, **kwargs)

@Counter
def say_hello():
    print("Hello!")

say_hello()  # 呼び出し回数：1
say_hello()  # 呼び出し回数：2
print(say_hello.count)  # 2
```

---

## デコレータの適用順序

複数のデコレータを重ねた場合、**下から上の順**で実行されます：

```python
@decorator_A   # 最後に実行（最外層）
@decorator_B   # 最初に実行（最内層）
def func():
    pass

# これと同等：
func = decorator_A(decorator_B(func))
```

---

## チートシート 📌

```
デコレータ三種の神器：
  1. *args, **kwargs — 透過的な引数パッシング
  2. @functools.wraps — 関数メタ情報の保持
  3. return result — 戻り値を忘れずに

引数付きデコレータ = 3層のネスト関数
  引数層 → デコレータ層 → wrapper 層

よく使う組み込みデコレータ：
  @property      — プロパティアクセス
  @staticmethod  — 静的メソッド
  @classmethod   — クラスメソッド
  @functools.lru_cache — キャッシュ
  @dataclasses.dataclass — データクラス
```
