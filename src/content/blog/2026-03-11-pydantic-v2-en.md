---
title: 'Pydantic v2: The Ultimate Weapon for Python Data Validation'
description: 'Deep dive into Pydantic v2 — 5–50x faster than v1, covering type validation, serialization, and custom validators'
pubDate: '2026-03-11'
category: python
lang: en
tags: ['Pydantic', 'Python', '技术干货']
---

## What Is Pydantic v2?

Pydantic is Python's most popular data validation library and a core dependency of FastAPI. v2 rewrote the engine in Rust, making it **5–50x faster than v1**.

```bash
pip install pydantic  # v2 is now the default
```

---

## Basic Usage

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

# Create instance — validation happens automatically
user = User(id=1, name="BOSS", email="boss@example.com", age=25)
print(user.model_dump())
# {'id': 1, 'name': 'BOSS', 'email': 'boss@example.com', 'age': 25, ...}

# Invalid data raises ValidationError
try:
    bad_user = User(id="not-a-number", name="X", email="invalid")
except Exception as e:
    print(e)  # detailed error info
```

---

## v2 New Features at a Glance

### 1. `model_validator` — Model-Level Validation

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode='after')
    def check_dates(self) -> 'DateRange':
        if self.end <= self.start:
            raise ValueError('end must be after start')
        return self

# ✅ Valid
DateRange(start=datetime(2026,1,1), end=datetime(2026,12,31))

# ❌ Raises ValidationError
DateRange(start=datetime(2026,12,31), end=datetime(2026,1,1))
```

### 2. `field_validator` — Field-Level Validation

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
            raise ValueError('Price must be greater than 0')
        return round(v, 2)  # auto-round to cents

    @field_validator('sku')
    @classmethod
    def sku_format(cls, v: str) -> str:
        v = v.upper().strip()
        if not v.startswith('SKU-'):
            raise ValueError('SKU must start with SKU-')
        return v
```

### 3. Serialization Control

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

# JSON serialization
print(post.model_dump_json())
```

---

## Working with FastAPI

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
    # body is already validated — use it directly
    return UserResponse(id=1, name=body.name, email=body.email)
```

FastAPI automatically validates request bodies with Pydantic and filters response fields based on `response_model`.

---

## Quick Reference Card 📌

```
Pydantic v2 at a glance:

Input            Validation      Output
dict/JSON  →  BaseModel  →  model_dump()
str        →  type coercion →  model_dump_json()
                  ↓
          ValidationError (on failure)

Common Field parameters:
  gt / ge / lt / le        →  numeric range
  min_length / max_length  →  string length
  pattern                  →  regex
  default / default_factory →  default values
```

Pydantic v2 is the standard for modern Python projects — FastAPI + Pydantic is the ultimate backend combination.
