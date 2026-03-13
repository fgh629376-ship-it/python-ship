---
title: 'Python asyncio 完全ガイド：基礎から実践まで'
description: 'Python 非同期プログラミングを完全理解 — イベントループ・コルーチン・Task・gather を網羅、実用サンプル付き'
pubDate: '2026-03-10'
category: python
lang: ja
tags: ['asyncio', 'Python', '教程型']
---

## なぜ asyncio を使うのか？

同期コードの最大の問題は**待機**です。HTTP リクエストを送ると、プログラムはただ待つだけ — CPU は何もしません。

```python
# 同期 — カメのように遅い
import time
import requests

def fetch(url):
    return requests.get(url).text

start = time.time()
for url in ["https://httpbin.org/delay/1"] * 5:
    fetch(url)
print(f"経過時間：{time.time() - start:.1f}s")  # 約5秒
```

`asyncio` を使えば、5つのリクエストを並行実行して約1秒で完了します。

---

## コアコンセプト

### 1. コルーチン（Coroutine）

`async def` で定義し、`await` で一時停止します：

```python
import asyncio

async def say_hello(name: str, delay: float):
    await asyncio.sleep(delay)  # ノンブロッキング待機
    print(f"Hello, {name}!")

# コルーチンを実行
asyncio.run(say_hello("BOSS", 1.0))
```

> **重要：** `await` は `async def` 関数の中でしか使えません。

### 2. イベントループ（Event Loop）

asyncio の核心は**イベントループ**です。すべてのコルーチンのスケジューリングを担います。`asyncio.run()` を呼ぶと、イベントループが自動的に作成・実行されます。

### 3. Task — 並行実行

```python
import asyncio

async def fetch_data(id: int):
    print(f"取得開始 {id}")
    await asyncio.sleep(1)  # IO 操作をシミュレート
    print(f"取得完了 {id}")
    return f"data_{id}"

async def main():
    # 複数の Task を作成して並行実行
    tasks = [asyncio.create_task(fetch_data(i)) for i in range(5)]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
# 合計時間：約1秒（5秒ではなく）
```

---

## 実践：並行 HTTP リクエスト

```python
import asyncio
import httpx  # pip install httpx

URLS = [
    "https://api.github.com/users/python",
    "https://api.github.com/users/django",
    "https://api.github.com/users/flask",
]

async def fetch(client: httpx.AsyncClient, url: str) -> dict:
    resp = await client.get(url)
    resp.raise_for_status()
    data = resp.json()
    return {"name": data["login"], "followers": data["followers"]}

async def main():
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [fetch(client, url) for url in URLS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for r in results:
        if isinstance(r, Exception):
            print(f"❌ エラー：{r}")
        else:
            print(f"✅ {r['name']}: {r['followers']} followers")

asyncio.run(main())
```

---

## よくあるハマりどころ

| 問題 | 原因 | 対処法 |
|------|------|--------|
| `RuntimeError: no running event loop` | 同期コードからコルーチンを直接呼び出している | `asyncio.run()` を使う |
| 並行化しても速くならない | `asyncio.sleep()` の代わりに `time.sleep()` を使っている | すべてのブロッキング処理を async バージョンに切り替える |
| `gather` で1つ失敗すると全部失敗する | デフォルトの挙動 | `return_exceptions=True` を渡す |

---

## クイックリファレンス 📌

```
asyncio の三種の神器：
  async def      →  コルーチンを定義
  await          →  一時停止して制御を手放す
  asyncio.run()  →  イベントループを起動

並行処理ツール：
  asyncio.gather()      →  複数コルーチンを待機して結果を収集
  asyncio.create_task() →  即座にスケジュールしてバックグラウンドで実行
  asyncio.wait()        →  より細かい制御
```

asyncio をマスターすれば、IO バウンドなタスクで5〜10倍のパフォーマンス向上も夢ではありません。
