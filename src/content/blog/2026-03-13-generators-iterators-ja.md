---
title: 'Python ジェネレータとイテレータ：遅延読み込みの技術'
description: 'yield、ジェネレータ式、イテレータプロトコルを深掘り — 大量データをメモリ不足なく処理するコアテクニック'
pubDate: '2026-03-13'
category: python
series: python-basics
lang: ja
tags: ['生成器', '迭代器', 'Python进阶', '技术干货']
---

## なぜジェネレータが必要なのか？

質問です：10GBのログファイルを読み込むとしたら、どうしますか？

```python
# ❌ メモリが爆発する
lines = open("huge.log").readlines()  # すべてをメモリに読み込む

# ✅ ジェネレータ：1行ずつ読み込み、メモリ使用量は一定
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line  # 毎回1行だけ生成する

for line in read_lines("huge.log"):
    process(line)
```

**ジェネレータのコアバリュー：必要に応じて計算し、事前にメモリを消費しない。**

---

## yield は実際に何をするのか？

```python
def countdown(n):
    while n > 0:
        yield n      # 一時停止し、n を返す
        n -= 1       # 次の next() 呼び出しはここから再開

gen = countdown(3)
print(next(gen))  # 3  — yield まで実行して一時停止
print(next(gen))  # 2  — 前回の一時停止箇所から再開
print(next(gen))  # 1
print(next(gen))  # StopIteration!
```

**`yield` = 一時停止 + 戻り値**。関数の状態が凍結され、`next()` が呼び出されると解凍・再開されます。

---

## ジェネレータ式

リスト内包表記の遅延評価版です：

```python
# リスト内包表記 — 即座に計算し、すべてメモリに格納
squares_list = [x**2 for x in range(10_000_000)]  # ~80MB

# ジェネレータ式 — 遅延評価、ほぼメモリを使わない
squares_gen = (x**2 for x in range(10_000_000))   # ~120B

# 使い方はまったく同じ
for s in squares_gen:
    ...
```

`[]` を `()` に変えるだけで、リストがジェネレータになります。

---

## イテレータプロトコル

Python の for ループはイテレータプロトコルで動いています：

```python
class Range:
    """range の自作実装"""
    def __init__(self, start, end):
        self.current = start
        self.end = end

    def __iter__(self):
        return self  # 自分自身をイテレータとして返す

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

for i in Range(1, 4):
    print(i)  # 1, 2, 3
```

**`__iter__` + `__next__` = イテレータプロトコル。** ジェネレータ関数はこの2つのメソッドを自動的に実装してくれます。

---

## yield from — サブジェネレータへの委譲

```python
def chain(*iterables):
    for it in iterables:
        yield from it  # サブイテレータの値を直接生成する

list(chain([1, 2], [3, 4], [5]))
# [1, 2, 3, 4, 5]

# 以下と同等（ただし yield from の方がより簡潔で効率的）：
def chain_manual(*iterables):
    for it in iterables:
        for item in it:
            yield item
```

---

## 双方向通信：send() メソッド

ジェネレータは値を生成するだけでなく、値を受け取ることもできます：

```python
def accumulator():
    total = 0
    while True:
        value = yield total  # total を生成し、send された値を受け取る
        if value is None:
            break
        total += value

acc = accumulator()
next(acc)          # 初期化、ジェネレータを開始 → 0
acc.send(10)       # → 10
acc.send(20)       # → 30
acc.send(5)        # → 35
```

`send()` はコルーチン（async/await の前身）で多く使われています。

---

## 実践的なユースケース

### 1. ストリーム処理パイプライン

```python
def read_csv(path):
    with open(path) as f:
        next(f)  # ヘッダーをスキップ
        for line in f:
            yield line.strip().split(',')

def filter_active(rows):
    for row in rows:
        if row[3] == 'active':
            yield row

def extract_emails(rows):
    for row in rows:
        yield row[2]

# パイプラインの組み合わせ — 各ステップが遅延評価、メモリ使用量が非常に少ない
pipeline = extract_emails(filter_active(read_csv("users.csv")))
for email in pipeline:
    send_notification(email)
```

### 2. 無限シーケンス

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

from itertools import islice
# 最初の10個のフィボナッチ数を取得
list(islice(fibonacci(), 10))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 3. スライディングウィンドウ

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

### 4. バッチ処理

```python
from itertools import islice

def batched(iterable, n):
    """Python 3.12 では itertools.batched が組み込まれています"""
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

## itertools の頼れる道具たち

```python
import itertools

# 無限カウント
itertools.count(10, 2)       # 10, 12, 14, 16, ...

# 循環繰り返し
itertools.cycle([1, 2, 3])   # 1, 2, 3, 1, 2, 3, ...

# デカルト積
itertools.product('AB', '12')  # A1, A2, B1, B2

# 順列と組み合わせ
itertools.permutations('ABC', 2)   # AB, AC, BA, BC, CA, CB
itertools.combinations('ABC', 2)   # AB, AC, BC

# グループ化
for key, group in itertools.groupby('AAABBCCCC'):
    print(key, list(group))
# A ['A','A','A']
# B ['B','B']
# C ['C','C','C','C']

# 累積
list(itertools.accumulate([1,2,3,4]))  # [1, 3, 6, 10]
```

---

## クイックリファレンスカード 📌

```
ジェネレータの基本：
  yield = 一時停止 + 戻り値
  遅延評価、オンデマンド計算、メモリ効率的

ジェネレータ式：
  (x for x in iterable)  ← 丸括弧を使う

イテレータプロトコル：
  __iter__() + __next__() + StopIteration

実践的なルール：
  大きなファイル → ジェネレータで1行ずつ読む
  パイプライン処理 → ジェネレータを連鎖させる
  無限シーケンス → while True + yield
  バッチ操作 → itertools.islice / batched
```
