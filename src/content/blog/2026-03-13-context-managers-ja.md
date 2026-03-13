---
title: 'Python コンテキストマネージャ：with 文の真の力'
description: 'with 文を完全理解 — __enter__/__exit__・contextlib・実践シナリオ：ファイル・データベース・ロック・一時的な状態変更'
pubDate: '2026-03-13'
category: python
series: python-basics
lang: ja
tags: ['上下文管理器', 'Python进阶', '技术干货']
---

## `with` 文は何をしているのか？

```python
with open("file.txt") as f:
    data = f.read()
# 途中でエラーが発生しても、ファイルは必ずクローズされます
```

`with` は魔法ではありません。たった2つのことをするだけです：
1. **入るとき：** `__enter__()` を呼び出す — リソースを取得する
2. **出るとき：** `__exit__()` を呼び出す — リソースを解放する（例外発生の有無に関わらず）

---

## 自作のコンテキストマネージャ

```python
class Timer:
    def __enter__(self):
        import time
        self.start = time.perf_counter()
        return self  # as の後の変数

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.perf_counter() - self.start
        print(f"経過時間 {self.elapsed:.4f}s")
        return False  # 例外を飲み込まない

with Timer() as t:
    sum(range(1_000_000))
# 経過時間 0.0234s
```

`__exit__` の3つの引数：
- `exc_type` — 例外の型（例外がなければ None）
- `exc_val` — 例外のインスタンス
- `exc_tb` — トレースバック
- `True` を返す = 例外を飲み込む、`False` を返す = 例外を再送出する

---

## contextlib — ジェネレータでコンテキストマネージャを書く

クラスを書きたくない？`@contextmanager` を使うとよりシンプルに書けます：

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label=""):
    start = time.perf_counter()
    try:
        yield  # ここで一時停止し、with ブロックのコードが実行される
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label} 経過時間 {elapsed:.4f}s")

with timer("計算"):
    sum(range(1_000_000))
# 計算 経過時間 0.0234s
```

**`yield` より前 = `__enter__`、`yield` より後 = `__exit__`**

---

## 10 の実践シナリオ

### 1. データベース接続

```python
@contextmanager
def db_connection(url):
    conn = create_connection(url)
    try:
        yield conn
        conn.commit()  # 正常終了時はコミット
    except Exception:
        conn.rollback()  # 例外発生時はロールバック
        raise
    finally:
        conn.close()  # 必ずクローズ

with db_connection("postgres://...") as conn:
    conn.execute("INSERT INTO ...")
```

### 2. 作業ディレクトリの一時変更

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
print(os.getcwd())  # 元のディレクトリに戻る
```

### 3. 環境変数の一時変更

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
# 自動的に元に戻る
```

### 4. スレッドロック

```python
import threading

lock = threading.Lock()

# with が自動的にロックの取得と解放を行う
with lock:
    # スレッドセーフなコード
    shared_resource.update()
```

### 5. 出力の一時リダイレクト

```python
from contextlib import redirect_stdout
import io

buffer = io.StringIO()
with redirect_stdout(buffer):
    print("captured!")

print(buffer.getvalue())  # "captured!\n"
```

### 6. 特定の例外を無視する

```python
from contextlib import suppress

# ファイルが存在しなくても気にしない
with suppress(FileNotFoundError):
    os.remove("maybe_exists.txt")

# 以下と同等：
# try:
#     os.remove("maybe_exists.txt")
# except FileNotFoundError:
#     pass
```

### 7. 一時ファイル / ディレクトリ

```python
import tempfile

with tempfile.NamedTemporaryFile(suffix=".csv") as f:
    f.write(b"data")
    f.flush()
    process(f.name)
# 自動的に削除される

with tempfile.TemporaryDirectory() as tmpdir:
    # 一時ディレクトリ内で作業
    save_files(tmpdir)
# ディレクトリ全体が自動的にクリーンアップされる
```

### 8. 複数リソースの同時管理

```python
# Python 3.1+
with open("input.txt") as fin, open("output.txt", "w") as fout:
    for line in fin:
        fout.write(line.upper())

# Python 3.10+ — 括弧を使って複数行に書ける
with (
    open("a.txt") as a,
    open("b.txt") as b,
    open("c.txt", "w") as c,
):
    ...
```

### 9. 非同期コンテキストマネージャ

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

### 10. ExitStack — 複数コンテキストの動的管理

```python
from contextlib import ExitStack

def process_files(file_list):
    with ExitStack() as stack:
        files = [stack.enter_context(open(f)) for f in file_list]
        # すべてのファイルは終了時にクローズされる
        for f in files:
            process(f)
```

---

## クイックリファレンス 📌

```
コンテキストマネージャ = リソースの自動取得と解放

クラスを使った書き方：
  __enter__()  →  リソースを取得
  __exit__()   →  リソースを解放

ジェネレータを使った書き方（推奨）：
  @contextmanager
  yield より前 = enter
  yield より後 = exit

便利な組み込みユーティリティ：
  suppress()        — 特定の例外を無視
  redirect_stdout() — 出力をリダイレクト
  ExitStack()       — 複数コンテキストを動的に管理
  tempfile.*        — 一時ファイル / ディレクトリ

覚えておくこと：
  with は単なる try/finally の糖衣構文ではない
  「リソースのライフサイクル管理」のための Python パラダイムだ
```
