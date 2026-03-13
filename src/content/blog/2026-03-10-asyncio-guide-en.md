---
title: 'The Complete Guide to Python asyncio: From Basics to Real-World Use'
description: 'Master Python async programming — event loop, coroutines, Tasks, gather, and more, with real-world examples'
pubDate: '2026-03-10'
category: python
series: python-basics
lang: en
tags: ['asyncio', 'Python', '教程型']
---

## Why Use asyncio?

The biggest problem with synchronous code is **waiting**. Send an HTTP request, and your program just sits there — CPU doing nothing.

```python
# Synchronous — slow as a turtle
import time
import requests

def fetch(url):
    return requests.get(url).text

start = time.time()
for url in ["https://httpbin.org/delay/1"] * 5:
    fetch(url)
print(f"Elapsed: {time.time() - start:.1f}s")  # ~5 seconds
```

With `asyncio`, 5 requests run concurrently and finish in about 1 second.

---

## Core Concepts

### 1. Coroutines

Defined with `async def`, paused with `await`:

```python
import asyncio

async def say_hello(name: str, delay: float):
    await asyncio.sleep(delay)  # non-blocking wait
    print(f"Hello, {name}!")

# Run the coroutine
asyncio.run(say_hello("BOSS", 1.0))
```

> **Key point:** `await` can only be used inside `async def` functions.

### 2. Event Loop

The heart of asyncio is the **event loop**, which schedules and runs all coroutines. `asyncio.run()` automatically creates and runs one for you.

### 3. Tasks — Concurrent Execution

```python
import asyncio

async def fetch_data(id: int):
    print(f"Start fetching {id}")
    await asyncio.sleep(1)  # simulate IO
    print(f"Done fetching {id}")
    return f"data_{id}"

async def main():
    # Create multiple Tasks — run concurrently
    tasks = [asyncio.create_task(fetch_data(i)) for i in range(5)]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
# Total time: ~1 second, not 5!
```

---

## Real-World Example: Concurrent HTTP Requests

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
            print(f"❌ Error: {r}")
        else:
            print(f"✅ {r['name']}: {r['followers']} followers")

asyncio.run(main())
```

---

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `RuntimeError: no running event loop` | Calling a coroutine directly from sync code | Use `asyncio.run()` |
| No speedup with concurrency | Using `time.sleep()` instead of `asyncio.sleep()` | Replace all blocking calls with async equivalents |
| One failure in `gather` fails everything | Default behavior | Pass `return_exceptions=True` |

---

## Quick Reference Card 📌

```
asyncio essentials:
  async def      →  define a coroutine
  await          →  pause, yield control
  asyncio.run()  →  start the event loop

Concurrency tools:
  asyncio.gather()      →  wait for multiple coroutines, collect results
  asyncio.create_task() →  schedule immediately, run in background
  asyncio.wait()        →  finer-grained control
```

Master asyncio and you can realistically achieve 5–10x performance gains on IO-bound tasks.
