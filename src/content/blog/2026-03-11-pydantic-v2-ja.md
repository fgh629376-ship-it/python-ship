---
title: 'Pydantic v2：Python データバリデーションの最強ツール'
description: 'Pydantic v2 コア機能の詳解 — v1 比 5〜50倍の高速化、型バリデーション・シリアライズ・カスタムバリデータを完全網羅'
pubDate: '2026-03-11'
category: python
series: python-basics
lang: ja
tags: ['Pydantic', 'Python', '技术干货']
---

## Pydantic v2 とは？

Pydantic は Python で最も人気のあるデータバリデーションライブラリであり、FastAPI のコア依存ライブラリです。v2 ではコアを Rust で書き直し、**v1 比で 5〜50 倍高速化**されました。

```bash
pip install pydantic  # 現在はデフォルトで v2 がインストールされます
```

---

## 基本的な使い方

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    age: Optional[int] = Field(default=None, ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.now)

# インスタンス作成 — 自動でバリデーションされます
user = User(id=1, name="BOSS", email="boss@example.com", age=25)
print(user.model_dump())
# {'id': 1, 'name': 'BOSS', 'email': 'boss@example.com', 'age': 25, ...}

# データが不正な場合は ValidationError が発生します
try:
    bad_user = User(id="not-a-number", name="X", email="invalid")
except Exception as e:
    print(e)  # 詳細なエラー情報が表示されます
```

---

## v2 新機能ダイジェスト

### 1. `model_validator` — モデルレベルのバリデーション

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode='after')
    def check_dates(self) -> 'DateRange':
        if self.end <= self.start:
            raise ValueError('end は start より後でなければなりません')
        return self

# ✅ 正常
DateRange(start=datetime(2026,1,1), end=datetime(2026,12,31))

# ❌ ValidationError が発生
DateRange(start=datetime(2026,12,31), end=datetime(2026,1,1))
```

### 2. `field_validator` — フィールドレベルのバリデーション

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    name: str
    price: float
    sku: str

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('価格は 0 より大きい必要があります')
        return round(v, 2)  # 自動的に小数点以下2桁に丸める

    @field_validator('sku')
    @classmethod
    def sku_format(cls, v: str) -> str:
        v = v.upper().strip()
        if not v.startswith('SKU-'):
            raise ValueError('SKU は SKU- で始まる必要があります')
        return v
```

### 3. シリアライズの制御

```python
from pydantic import BaseModel, field_serializer
from datetime import datetime

class Post(BaseModel):
    title: str
    published_at: datetime
    view_count: int = 0

    @field_serializer('published_at')
    def serialize_date(self, dt: datetime) -> str:
        return dt.strftime('%Y-%m-%d %H:%M')

post = Post(title="Hello", published_at=datetime.now())
print(post.model_dump())
# {'title': 'Hello', 'published_at': '2026-03-11 22:00', 'view_count': 0}

# JSON シリアライズ
print(post.model_dump_json())
```

---

## FastAPI との連携

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserResponse)
async def create_user(body: CreateUserRequest):
    # body はすでにバリデーション済み — そのまま使えます
    return UserResponse(id=1, name=body.name, email=body.email)
```

FastAPI は Pydantic を使ってリクエストボディを自動バリデーションし、`response_model` に基づいてレスポンスフィールドをフィルタリングします。

---

## クイックリファレンス 📌

```
Pydantic v2 の全体像：

入力             バリデーション    出力
dict/JSON  →  BaseModel  →  model_dump()
str        →  型変換      →  model_dump_json()
                  ↓
          ValidationError（失敗時）

よく使う Field パラメータ：
  gt / ge / lt / le        →  数値の範囲
  min_length / max_length  →  文字列の長さ
  pattern                  →  正規表現
  default / default_factory →  デフォルト値
```

Pydantic v2 は現代の Python プロジェクトの標準ライブラリです。FastAPI + Pydantic の組み合わせはバックエンド開発の最強コンビです。
