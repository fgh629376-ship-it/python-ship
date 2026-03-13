---
title: 'Python asyncio 完全指南：从入门到实战'
description: '彻底搞懂 Python 异步编程 — event loop、协程、Task、gather 一网打尽，附真实案例'
category: python
pubDate: '2026-03-10'
tags: ['asyncio', 'Python', '教程型']
---

## 为什么要用 asyncio？

同步代码最大的问题是**等待**。发一个 HTTP 请求，程序就傻等着，CPU 什么都不干。

```python
# 同步 — 慢得像乌龟
import time
import requests

def fetch(url):
    return requests.get(url).text

start = time.time()
for url in ["https://httpbin.org/delay/1"] * 5:
    fetch(url)
print(f"耗时：{time.time() - start:.1f}s")  # 约 5 秒
```

用 `asyncio`，5 个请求并发跑，1 秒搞定。

---

## 核心概念

### 1. 协程（Coroutine）

用 `async def` 定义，用 `await` 暂停：

```python
import asyncio

async def say_hello(name: str, delay: float):
    await asyncio.sleep(delay)  # 非阻塞等待
    print(f"Hello, {name}!")

# 运行协程
asyncio.run(say_hello("BOSS", 1.0))
```

> **关键：** `await` 只能用在 `async def` 函数内部。

### 2. Event Loop

asyncio 的核心是**事件循环**，它调度所有协程的执行。`asyncio.run()` 会自动创建并运行一个事件循环。

### 3. Task — 并发执行

```python
import asyncio

async def fetch_data(id: int):
    print(f"开始获取 {id}")
    await asyncio.sleep(1)  # 模拟 IO 操作
    print(f"完成获取 {id}")
    return f"data_{id}"

async def main():
    # 创建多个 Task，并发执行
    tasks = [asyncio.create_task(fetch_data(i)) for i in range(5)]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
# 总耗时约 1 秒，而不是 5 秒！
```

---

## 实战：并发 HTTP 请求

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
            print(f"❌ 错误：{r}")
        else:
            print(f"✅ {r['name']}: {r['followers']} followers")

asyncio.run(main())
```

---

## 常见坑

| 问题 | 原因 | 解决 |
|------|------|------|
| `RuntimeError: no running event loop` | 在同步代码里直接调用协程 | 用 `asyncio.run()` |
| 并发没有加速 | 用了 `time.sleep()` 而不是 `asyncio.sleep()` | 所有阻塞操作换成 async 版本 |
| `gather` 里一个失败全失败 | 默认行为 | 传入 `return_exceptions=True` |

---

## 知识卡片 📌

```
asyncio 三件套：
  async def  →  定义协程
  await      →  暂停，让出控制权
  asyncio.run()  →  启动事件循环

并发工具：
  asyncio.gather()     →  等待多个协程，收集结果
  asyncio.create_task() →  立即调度，后台运行
  asyncio.wait()        →  更细粒度的控制
```

掌握 asyncio，IO 密集型任务性能提升 5-10x 不是梦。
