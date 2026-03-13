---
title: 'Python 上下文管理器：with 语句的真正力量'
description: '彻底搞懂 with 语句 — __enter__/__exit__、contextlib、实战场景：文件、数据库、锁、临时修改'
category: python
pubDate: '2026-03-13'
tags: ['上下文管理器', 'Python进阶', '技术干货']
---

## with 语句在干什么？

```python
with open("file.txt") as f:
    data = f.read()
# 文件一定会被关闭，即使中间报错
```

`with` 不是魔法，它只做两件事：
1. **进入**时调用 `__enter__()` — 获取资源
2. **退出**时调用 `__exit__()` — 释放资源（无论是否异常）

---

## 自己写一个上下文管理器

```python
class Timer:
    def __enter__(self):
        import time
        self.start = time.perf_counter()
        return self  # as 后面的变量

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.perf_counter() - self.start
        print(f"耗时 {self.elapsed:.4f}s")
        return False  # 不吞异常

with Timer() as t:
    sum(range(1_000_000))
# 耗时 0.0234s
```

`__exit__` 的三个参数：
- `exc_type` — 异常类型（无异常时为 None）
- `exc_val` — 异常实例
- `exc_tb` — traceback
- 返回 `True` = 吞掉异常，返回 `False` = 继续抛出

---

## contextlib — 用生成器写上下文管理器

不想写类？用 `@contextmanager` 更简洁：

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label=""):
    start = time.perf_counter()
    try:
        yield  # 这里暂停，执行 with 块的代码
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label} 耗时 {elapsed:.4f}s")

with timer("计算"):
    sum(range(1_000_000))
# 计算 耗时 0.0234s
```

**`yield` 之前 = `__enter__`，`yield` 之后 = `__exit__`**

---

## 10 个实战场景

### 1. 数据库连接

```python
@contextmanager
def db_connection(url):
    conn = create_connection(url)
    try:
        yield conn
        conn.commit()  # 正常退出则提交
    except Exception:
        conn.rollback()  # 异常则回滚
        raise
    finally:
        conn.close()  # 一定关闭

with db_connection("postgres://...") as conn:
    conn.execute("INSERT INTO ...")
```

### 2. 临时改变工作目录

```python
import os
from contextlib import contextmanager

@contextmanager
def cd(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)

with cd("/tmp"):
    print(os.getcwd())  # /tmp
print(os.getcwd())  # 回到原来的目录
```

### 3. 临时修改环境变量

```python
@contextmanager
def env_var(key, value):
    old = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if old is None:
            del os.environ[key]
        else:
            os.environ[key] = old

with env_var("DEBUG", "1"):
    assert os.environ["DEBUG"] == "1"
# 自动恢复
```

### 4. 线程锁

```python
import threading

lock = threading.Lock()

# with 自动获取和释放锁
with lock:
    # 线程安全的代码
    shared_resource.update()
```

### 5. 临时重定向输出

```python
from contextlib import redirect_stdout
import io

buffer = io.StringIO()
with redirect_stdout(buffer):
    print("captured!")

print(buffer.getvalue())  # "captured!\n"
```

### 6. 忽略特定异常

```python
from contextlib import suppress

# 不 care 文件不存在
with suppress(FileNotFoundError):
    os.remove("maybe_exists.txt")

# 等价于：
# try:
#     os.remove("maybe_exists.txt")
# except FileNotFoundError:
#     pass
```

### 7. 临时文件/目录

```python
import tempfile

with tempfile.NamedTemporaryFile(suffix=".csv") as f:
    f.write(b"data")
    f.flush()
    process(f.name)
# 自动删除

with tempfile.TemporaryDirectory() as tmpdir:
    # 在临时目录里工作
    save_files(tmpdir)
# 自动清理整个目录
```

### 8. 多资源同时管理

```python
# Python 3.1+
with open("input.txt") as fin, open("output.txt", "w") as fout:
    for line in fin:
        fout.write(line.upper())

# Python 3.10+ 可以用括号换行
with (
    open("a.txt") as a,
    open("b.txt") as b,
    open("c.txt", "w") as c,
):
    ...
```

### 9. 异步上下文管理器

```python
class AsyncDB:
    async def __aenter__(self):
        self.conn = await create_async_connection()
        return self.conn

    async def __aexit__(self, *exc):
        await self.conn.close()

async with AsyncDB() as conn:
    await conn.execute("SELECT 1")
```

### 10. ExitStack — 动态管理多个上下文

```python
from contextlib import ExitStack

def process_files(file_list):
    with ExitStack() as stack:
        files = [stack.enter_context(open(f)) for f in file_list]
        # 所有文件都会在退出时关闭
        for f in files:
            process(f)
```

---

## 知识卡片 📌

```
上下文管理器 = 资源的自动获取与释放

类写法：
  __enter__()  →  获取资源
  __exit__()   →  释放资源

生成器写法（推荐）：
  @contextmanager
  yield 之前 = enter
  yield 之后 = exit

常用内置：
  suppress()        — 忽略异常
  redirect_stdout() — 重定向输出
  ExitStack()       — 动态管理多个上下文
  tempfile.*        — 临时文件/目录

记住：
  with 不只是 try/finally 的语法糖
  它是"资源生命周期管理"的 Python 范式
```
