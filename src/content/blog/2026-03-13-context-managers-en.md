---
title: 'Python Context Managers: The Real Power of the with Statement'
description: 'Master the with statement — __enter__/__exit__, contextlib, and real-world use cases: files, databases, locks, and temporary state changes'
pubDate: '2026-03-13'
category: python
series: python-basics
lang: en
tags: ['上下文管理器', 'Python进阶', '技术干货']
---

## What Does the `with` Statement Actually Do?

```python
with open("file.txt") as f:
    data = f.read()
# file is guaranteed to close, even if an exception occurs
```

`with` isn't magic — it does exactly two things:
1. **On entry:** calls `__enter__()` — acquire the resource
2. **On exit:** calls `__exit__()` — release the resource (regardless of exceptions)

---

## Writing Your Own Context Manager

```python
class Timer:
    def __enter__(self):
        import time
        self.start = time.perf_counter()
        return self  # the variable after `as`

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.perf_counter() - self.start
        print(f"Elapsed: {self.elapsed:.4f}s")
        return False  # don't suppress exceptions

with Timer() as t:
    sum(range(1_000_000))
# Elapsed: 0.0234s
```

The three parameters of `__exit__`:
- `exc_type` — exception type (None if no exception)
- `exc_val` — exception instance
- `exc_tb` — traceback
- Return `True` = suppress the exception; return `False` = re-raise it

---

## contextlib — Context Managers via Generators

Don't want to write a class? Use `@contextmanager` for something cleaner:

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label=""):
    start = time.perf_counter()
    try:
        yield  # pause here; the with-block runs at this point
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label} elapsed: {elapsed:.4f}s")

with timer("Calculation"):
    sum(range(1_000_000))
# Calculation elapsed: 0.0234s
```

**Everything before `yield` = `__enter__`; everything after `yield` = `__exit__`**

---

## 10 Real-World Use Cases

### 1. Database Connections

```python
@contextmanager
def db_connection(url):
    conn = create_connection(url)
    try:
        yield conn
        conn.commit()  # commit on normal exit
    except Exception:
        conn.rollback()  # rollback on exception
        raise
    finally:
        conn.close()  # always close

with db_connection("postgres://...") as conn:
    conn.execute("INSERT INTO ...")
```

### 2. Temporarily Change Working Directory

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
print(os.getcwd())  # back to original directory
```

### 3. Temporarily Set Environment Variables

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
# automatically restored
```

### 4. Thread Locks

```python
import threading

lock = threading.Lock()

# with automatically acquires and releases the lock
with lock:
    # thread-safe code
    shared_resource.update()
```

### 5. Redirect Output Temporarily

```python
from contextlib import redirect_stdout
import io

buffer = io.StringIO()
with redirect_stdout(buffer):
    print("captured!")

print(buffer.getvalue())  # "captured!\n"
```

### 6. Suppress Specific Exceptions

```python
from contextlib import suppress

# don't care if the file doesn't exist
with suppress(FileNotFoundError):
    os.remove("maybe_exists.txt")

# equivalent to:
# try:
#     os.remove("maybe_exists.txt")
# except FileNotFoundError:
#     pass
```

### 7. Temporary Files and Directories

```python
import tempfile

with tempfile.NamedTemporaryFile(suffix=".csv") as f:
    f.write(b"data")
    f.flush()
    process(f.name)
# automatically deleted

with tempfile.TemporaryDirectory() as tmpdir:
    # work inside the temp directory
    save_files(tmpdir)
# automatically cleaned up
```

### 8. Managing Multiple Resources at Once

```python
# Python 3.1+
with open("input.txt") as fin, open("output.txt", "w") as fout:
    for line in fin:
        fout.write(line.upper())

# Python 3.10+ — parenthesized form for multi-line
with (
    open("a.txt") as a,
    open("b.txt") as b,
    open("c.txt", "w") as c,
):
    ...
```

### 9. Async Context Managers

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

### 10. ExitStack — Dynamic Multi-Context Management

```python
from contextlib import ExitStack

def process_files(file_list):
    with ExitStack() as stack:
        files = [stack.enter_context(open(f)) for f in file_list]
        # all files will be closed on exit
        for f in files:
            process(f)
```

---

## Quick Reference Card 📌

```
Context manager = automatic resource acquisition and release

Class-based approach:
  __enter__()  →  acquire resource
  __exit__()   →  release resource

Generator-based approach (recommended):
  @contextmanager
  before yield = enter
  after yield  = exit

Useful built-ins:
  suppress()        — ignore specific exceptions
  redirect_stdout() — redirect output
  ExitStack()       — dynamically manage multiple contexts
  tempfile.*        — temporary files/directories

Remember:
  with is not just syntactic sugar for try/finally
  it's the Python paradigm for "resource lifecycle management"
```
