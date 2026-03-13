---
title: 'Python 生成器与迭代器：懒加载的艺术'
description: '深入理解 yield、生成器表达式、迭代器协议 — 处理大数据不爆内存的核心技巧'
category: python
series: python-basics
lang: zh
pubDate: '2026-03-13'
tags: ['生成器', '迭代器', 'Python进阶', '技术干货']
---

## 为什么需要生成器？

一个问题：读一个 10GB 的日志文件，你会怎么做？

```python
# ❌ 内存炸了
lines = open("huge.log").readlines()  # 全部读入内存

# ✅ 生成器：一行一行读，内存恒定
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line  # 每次只产出一行

for line in read_lines("huge.log"):
    process(line)
```

**生成器的核心价值：按需计算，不提前占内存。**

---

## yield 到底干了什么？

```python
def countdown(n):
    while n > 0:
        yield n      # 暂停，返回 n
        n -= 1       # 下次 next() 从这里继续

gen = countdown(3)
print(next(gen))  # 3  — 执行到 yield，暂停
print(next(gen))  # 2  — 从上次暂停处继续
print(next(gen))  # 1
print(next(gen))  # StopIteration!
```

**`yield` = 暂停 + 返回**。函数状态被冻结，下次调用 `next()` 时解冻继续。

---

## 生成器表达式

列表推导式的惰性版本：

```python
# 列表推导 — 立刻计算，全部存内存
squares_list = [x**2 for x in range(10_000_000)]  # ~80MB

# 生成器表达式 — 惰性计算，几乎不占内存
squares_gen = (x**2 for x in range(10_000_000))   # ~120B

# 用法完全一样
for s in squares_gen:
    ...
```

把 `[]` 换成 `()`，就从列表变成了生成器。

---

## 迭代器协议

Python 的 for 循环背后就是迭代器协议：

```python
class Range:
    """自己实现一个 range"""
    def __init__(self, start, end):
        self.current = start
        self.end = end

    def __iter__(self):
        return self  # 返回自身作为迭代器

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

for i in Range(1, 4):
    print(i)  # 1, 2, 3
```

**`__iter__` + `__next__` = 迭代器协议。** 生成器函数自动帮你实现了这两个方法。

---

## yield from — 委托生成器

```python
def chain(*iterables):
    for it in iterables:
        yield from it  # 把子迭代器的值直接产出

list(chain([1, 2], [3, 4], [5]))
# [1, 2, 3, 4, 5]

# 等价于（但 yield from 更简洁高效）：
def chain_manual(*iterables):
    for it in iterables:
        for item in it:
            yield item
```

---

## 双向通信：send() 方法

生成器不只能产出值，还能接收值：

```python
def accumulator():
    total = 0
    while True:
        value = yield total  # 产出 total，接收 send 的值
        if value is None:
            break
        total += value

acc = accumulator()
next(acc)          # 初始化，启动生成器 → 0
acc.send(10)       # → 10
acc.send(20)       # → 30
acc.send(5)        # → 35
```

`send()` 在协程（async/await 的前身）中大量使用。

---

## 实战场景

### 1. 流式处理管道

```python
def read_csv(path):
    with open(path) as f:
        next(f)  # 跳过表头
        for line in f:
            yield line.strip().split(',')

def filter_active(rows):
    for row in rows:
        if row[3] == 'active':
            yield row

def extract_emails(rows):
    for row in rows:
        yield row[2]

# 管道组合 — 每一步都是惰性的，内存占用极低
pipeline = extract_emails(filter_active(read_csv("users.csv")))
for email in pipeline:
    send_notification(email)
```

### 2. 无限序列

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

from itertools import islice
# 取前 10 个斐波那契数
list(islice(fibonacci(), 10))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 3. 滑动窗口

```python
from collections import deque

def sliding_window(iterable, size):
    it = iter(iterable)
    window = deque(islice(it, size), maxlen=size)
    if len(window) == size:
        yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)

list(sliding_window([1,2,3,4,5], 3))
# [(1,2,3), (2,3,4), (3,4,5)]
```

### 4. 分批处理

```python
from itertools import islice

def batched(iterable, n):
    """Python 3.12 内置了 itertools.batched"""
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch

for batch in batched(range(10), 3):
    print(batch)
# [0, 1, 2]
# [3, 4, 5]
# [6, 7, 8]
# [9]
```

---

## itertools 常用武器

```python
import itertools

# 无限计数
itertools.count(10, 2)       # 10, 12, 14, 16, ...

# 循环重复
itertools.cycle([1, 2, 3])   # 1, 2, 3, 1, 2, 3, ...

# 笛卡尔积
itertools.product('AB', '12')  # A1, A2, B1, B2

# 排列组合
itertools.permutations('ABC', 2)   # AB, AC, BA, BC, CA, CB
itertools.combinations('ABC', 2)   # AB, AC, BC

# 分组
for key, group in itertools.groupby('AAABBCCCC'):
    print(key, list(group))
# A ['A','A','A']
# B ['B','B']
# C ['C','C','C','C']

# 累积
list(itertools.accumulate([1,2,3,4]))  # [1, 3, 6, 10]
```

---

## 知识卡片 📌

```
生成器核心：
  yield = 暂停 + 返回值
  惰性求值，按需计算，省内存

生成器表达式：
  (x for x in iterable)  ← 用圆括号

迭代器协议：
  __iter__() + __next__() + StopIteration

实战口诀：
  大文件 → 生成器逐行读
  管道处理 → 生成器串联
  无限序列 → while True + yield
  批量操作 → itertools.islice / batched
```
