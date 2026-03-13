---
title: 'Python Generators and Iterators: The Art of Lazy Loading'
description: 'Deep dive into yield, generator expressions, and the iterator protocol — the core technique for processing large data without blowing up memory'
pubDate: '2026-03-13'
category: python
series: python-basics
lang: en
tags: ['生成器', '迭代器', 'Python进阶', '技术干货']
---

## Why Do We Need Generators?

A question: how would you read a 10GB log file?

```python
# ❌ Memory explodes
lines = open("huge.log").readlines()  # Reads everything into memory

# ✅ Generator: reads line by line, constant memory usage
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line  # Yields one line at a time

for line in read_lines("huge.log"):
    process(line)
```

**The core value of generators: compute on demand, no upfront memory allocation.**

---

## What Does yield Actually Do?

```python
def countdown(n):
    while n > 0:
        yield n      # Pause, return n
        n -= 1       # Next next() call resumes here

gen = countdown(3)
print(next(gen))  # 3  — executes until yield, then pauses
print(next(gen))  # 2  — resumes from the last pause point
print(next(gen))  # 1
print(next(gen))  # StopIteration!
```

**`yield` = pause + return**. The function state is frozen and thawed when `next()` is called again.

---

## Generator Expressions

The lazy version of list comprehensions:

```python
# List comprehension — computes immediately, stores everything in memory
squares_list = [x**2 for x in range(10_000_000)]  # ~80MB

# Generator expression — lazy evaluation, almost no memory
squares_gen = (x**2 for x in range(10_000_000))   # ~120B

# Usage is identical
for s in squares_gen:
    ...
```

Just replace `[]` with `()` to turn a list into a generator.

---

## The Iterator Protocol

Python's `for` loop is powered by the iterator protocol under the hood:

```python
class Range:
    """A custom implementation of range"""
    def __init__(self, start, end):
        self.current = start
        self.end = end

    def __iter__(self):
        return self  # Return self as the iterator

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

for i in Range(1, 4):
    print(i)  # 1, 2, 3
```

**`__iter__` + `__next__` = the iterator protocol.** Generator functions automatically implement both methods for you.

---

## yield from — Delegating to Sub-Generators

```python
def chain(*iterables):
    for it in iterables:
        yield from it  # Directly yields values from the sub-iterator

list(chain([1, 2], [3, 4], [5]))
# [1, 2, 3, 4, 5]

# Equivalent to (but yield from is more concise and efficient):
def chain_manual(*iterables):
    for it in iterables:
        for item in it:
            yield item
```

---

## Two-Way Communication: The send() Method

Generators can not only yield values, they can also receive them:

```python
def accumulator():
    total = 0
    while True:
        value = yield total  # Yield total, receive the sent value
        if value is None:
            break
        total += value

acc = accumulator()
next(acc)          # Initialize, start the generator → 0
acc.send(10)       # → 10
acc.send(20)       # → 30
acc.send(5)        # → 35
```

`send()` is heavily used in coroutines (the predecessor of async/await).

---

## Real-World Use Cases

### 1. Streaming Processing Pipeline

```python
def read_csv(path):
    with open(path) as f:
        next(f)  # Skip header
        for line in f:
            yield line.strip().split(',')

def filter_active(rows):
    for row in rows:
        if row[3] == 'active':
            yield row

def extract_emails(rows):
    for row in rows:
        yield row[2]

# Pipeline composition — every step is lazy, extremely low memory usage
pipeline = extract_emails(filter_active(read_csv("users.csv")))
for email in pipeline:
    send_notification(email)
```

### 2. Infinite Sequences

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

from itertools import islice
# Get the first 10 Fibonacci numbers
list(islice(fibonacci(), 10))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 3. Sliding Window

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

### 4. Batch Processing

```python
from itertools import islice

def batched(iterable, n):
    """Python 3.12 has itertools.batched built-in"""
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

## Essential itertools Arsenal

```python
import itertools

# Infinite counting
itertools.count(10, 2)       # 10, 12, 14, 16, ...

# Cycling repetition
itertools.cycle([1, 2, 3])   # 1, 2, 3, 1, 2, 3, ...

# Cartesian product
itertools.product('AB', '12')  # A1, A2, B1, B2

# Permutations and combinations
itertools.permutations('ABC', 2)   # AB, AC, BA, BC, CA, CB
itertools.combinations('ABC', 2)   # AB, AC, BC

# Grouping
for key, group in itertools.groupby('AAABBCCCC'):
    print(key, list(group))
# A ['A','A','A']
# B ['B','B']
# C ['C','C','C','C']

# Accumulation
list(itertools.accumulate([1,2,3,4]))  # [1, 3, 6, 10]
```

---

## Quick Reference Card 📌

```
Generator fundamentals:
  yield = pause + return value
  Lazy evaluation, on-demand computation, memory efficient

Generator expression:
  (x for x in iterable)  ← use parentheses

Iterator protocol:
  __iter__() + __next__() + StopIteration

Practical rules:
  Large files → generator line-by-line reading
  Pipeline processing → chaining generators
  Infinite sequences → while True + yield
  Batch operations → itertools.islice / batched
```
