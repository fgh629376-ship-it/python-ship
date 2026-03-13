---
title: 'Python 3.12 新機能：必ず知っておくべき6つの改善点'
description: 'Python 3.12 の重要な新機能を詳しく解説 — f-string の強化・type 文・パフォーマンス向上・より明確なエラーメッセージ'
pubDate: '2026-03-12'
category: python
lang: ja
tags: ['Python3.12', '技术干货', '知识卡片']
---

## Python 3.12 はアップグレードする価値があるか？

一言で言えば：**あります**。3.12 はここ数年で最も変化の大きいバージョンの一つです。

```bash
# バージョンを確認
python --version

# pyenv でインストール
pyenv install 3.12.0
pyenv global 3.12.0
```

---

## 1. f-string の全面強化

これまでの f-string では、同じ種類の引用符を使えず、複数行にまたがることもできず、式のネストも制限されていました。3.12 ではこれらすべての制限が解除されました：

```python
# ✅ 3.12 — f-string 内で同じ引用符が使えるようになった
name = "Python"
print(f"Hello, {"world".upper()}!")  # Hello, WORLD!

# ✅ f-string のネスト — バックスラッシュ不要に
data = {"key": "value"}
print(f"Result: {data["key"]}")  # Result: value

# ✅ 複数行の f-string 式
result = f"""
Numbers: {
    ", ".join(str(i) for i in range(5))
}
"""
```

---

## 2. `type` 文 — 型エイリアス

```python
# 旧書き方（3.11 以前）
from typing import TypeAlias
Vector = list[float]  # 明確さに欠ける

# 新書き方（3.12）
type Vector = list[float]
type Matrix = list[Vector]
type Callback[T] = Callable[[T], None]  # ジェネリクスもサポート！

# 使用例
def dot_product(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))
```

---

## 3. ジェネリクス構文の簡略化

```python
# 旧書き方
from typing import TypeVar, Generic
T = TypeVar('T')

class Stack(Generic[T]):
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# 新書き方（3.12）— はるかにシンプル！
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()

# ジェネリック関数も同様
def first[T](lst: list[T]) -> T:
    return lst[0]
```

---

## 4. より明確なエラーメッセージ

```python
# 3.11 以前
>>> import collections.abc
>>> collections.abc.Mapping[str, int][str, int]
TypeError: ...

# 3.12 — 問題を正確に指摘してくれる
class Point:
    x: int
    y: int

p = Point()
print(p.z)
# AttributeError: 'Point' object has no attribute 'z'
# Did you mean: 'x' or 'y'?  ← 3.12 は候補まで提示してくれる！
```

---

## 5. パフォーマンスの向上

| ベンチマーク | 3.11 vs 3.10 | 3.12 vs 3.11 |
|------------|-------------|-------------|
| 総合速度 | +25% | +5% |
| メモリ使用量 | ベースライン | -10% |
| 起動時間 | ベースライン | より速い |

Python 3.12 は**サブインタープリタ**（実験的な真のマルチスレッド）に重点を置いており、将来性が非常に高いです。

---

## 6. `@override` デコレータ

```python
from typing import override

class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    @override  # 型チェッカーに「これは意図的な親クラスメソッドのオーバーライドだ」と伝える
    def speak(self) -> str:
        return "Woof!"
    
    @override
    def fly(self) -> None:  # ❌ 型チェッカーがエラーを報告！Animal に fly メソッドはない
        pass
```

---

## クイックリファレンス 📌

```
Python 3.12 の 6 大ハイライト：

1. f-string   →  同じ引用符・ネスト・複数行式が使える
2. type 文    →  明確な型エイリアス定義
3. ジェネリクス →  class Foo[T] が Generic[T] を置き換える
4. エラー表示  →  より人間に優しく、提案付き
5. パフォーマンス →  メモリ削減、速度微向上
6. @override  →  メソッドオーバーライドの安全チェック

アップグレードコマンド：
  pyenv install 3.12.x
  poetry env use 3.12
```

まだ 3.10 を使っていますか？そろそろアップグレードしましょう — Python 3.12 は後方互換性に優れています。
