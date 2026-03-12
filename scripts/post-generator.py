#!/usr/bin/env python3
"""
Python Ship — 每日博客自动生成器
每晚 22:00 运行，搜索 Python 热点 → 生成博文 → 提交到 GitHub

用法:
  python scripts/post-generator.py
  python scripts/post-generator.py --topic "Python decorators"
  python scripts/post-generator.py --dry-run  # 只生成不提交
"""

import os
import sys
import re
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic  # pip install anthropic
import httpx      # pip install httpx

# ─── 配置 ────────────────────────────────────────────────────
BLOG_DIR = Path(__file__).parent.parent / "src" / "content" / "blog"
MODEL = "claude-3-5-haiku-20241022"
CST = timezone(timedelta(hours=8))  # 北京时间

TOPIC_POOL = [
    "Python dataclasses advanced tips",
    "Python context managers and `with` statement deep dive",
    "Python type hints generics and protocols",
    "Python performance optimization techniques",
    "Python pathlib vs os.path complete guide",
    "Python logging best practices",
    "Python unittest and pytest comparison",
    "Python itertools and functools practical guide",
    "Python walrus operator use cases",
    "Python match statement (structural pattern matching)",
    "Python virtual environments: venv vs conda vs poetry",
    "Python slots and memory optimization",
    "Python descriptors and property decorator",
    "Python metaclasses explained simply",
    "Python multiprocessing vs threading vs asyncio",
    "Python comprehensions: list dict set generator",
    "Python decorators: from simple to advanced",
    "Python f-strings advanced formatting tricks",
    "Python error handling best practices",
    "Python packaging: pyproject.toml guide",
]

# ─── 搜索热点话题 ────────────────────────────────────────────
def search_python_topics() -> list[str]:
    """用 DuckDuckGo 搜索近期 Python 热点，返回话题列表。"""
    topics = []
    try:
        resp = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": "Python programming tutorial 2026 site:dev.to OR site:realpython.com OR site:towardsdatascience.com"},
            headers={"User-Agent": "Mozilla/5.0 (compatible; PythonShipBot/1.0)"},
            timeout=10,
            follow_redirects=True,
        )
        # 简单提取标题
        titles = re.findall(r'class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>', resp.text, re.DOTALL)
        for t in titles[:5]:
            clean = re.sub(r'<[^>]+>', '', t).strip()
            if clean and len(clean) > 10:
                topics.append(clean)
    except Exception as e:
        print(f"[search] 搜索失败，使用预设话题: {e}")
    
    return topics

# ─── 选择今日话题 ────────────────────────────────────────────
def pick_topic(override: str | None = None) -> str:
    if override:
        return override
    
    # 尝试从搜索获取
    trending = search_python_topics()
    if trending:
        # 用日期做稳定随机，同一天不会变
        day_idx = datetime.now(CST).timetuple().tm_yday
        topic = trending[day_idx % len(trending)]
        print(f"[topic] 搜索到话题: {topic}")
        return topic
    
    # 回退到预设池
    day_idx = datetime.now(CST).timetuple().tm_yday
    topic = TOPIC_POOL[day_idx % len(TOPIC_POOL)]
    print(f"[topic] 使用预设话题: {topic}")
    return topic

# ─── 生成博客内容 ────────────────────────────────────────────
def generate_post(topic: str) -> tuple[str, str, str, list[str]]:
    """
    返回 (title, description, content, tags)
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now(CST).strftime("%Y年%m月%d日")
    
    prompt = f"""你是 Python Ship 博客的作者，写高质量的 Python 技术文章。

今天是 {today}，请写一篇关于「{topic}」的博客文章。

要求：
1. 语言：中文为主，技术术语保留英文
2. 风格：技术干货，实用，有代码示例
3. 长度：800-1500字
4. 结构：
   - 开篇直接切入问题/价值（不要废话）
   - 核心概念解释（配代码）
   - 实战示例（真实可运行的代码）
   - 常见坑或最佳实践
   - 结尾「知识卡片」用代码块总结要点

5. 代码块必须指定语言（```python）
6. 最后输出以下格式的元数据（在文章最后）：

---META---
TITLE: （文章标题，中文，20字以内）
DESCRIPTION: （一句话描述，40字以内）
TAGS: （2-3个标签，从这些选：Python, asyncio, Pydantic, FastAPI, 教程型, 技术干货, 知识卡片, 性能优化, 类型注解, 测试）
SLUG: （英文slug，用连字符，如：python-decorators-guide）

请直接开始写文章，不要有任何前言。"""

    print(f"[ai] 正在生成文章：{topic}")
    message = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    full_text = message.content[0].text
    
    # 解析元数据
    meta_match = re.search(r'---META---\n(.*?)$', full_text, re.DOTALL)
    content = full_text[:meta_match.start()].strip() if meta_match else full_text
    
    title = topic
    description = f"关于 {topic} 的深度解析"
    tags = ["Python", "技术干货"]
    slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')[:50]
    
    if meta_match:
        meta = meta_match.group(1)
        if m := re.search(r'TITLE:\s*(.+)', meta):
            title = m.group(1).strip()
        if m := re.search(r'DESCRIPTION:\s*(.+)', meta):
            description = m.group(1).strip()
        if m := re.search(r'TAGS:\s*(.+)', meta):
            tags = [t.strip() for t in m.group(1).split(',')]
        if m := re.search(r'SLUG:\s*(.+)', meta):
            slug = re.sub(r'[^a-z0-9-]', '', m.group(1).strip().lower())
    
    return title, description, content, tags, slug

# ─── 写入文件 ────────────────────────────────────────────────
def write_post(title: str, description: str, content: str, tags: list[str], slug: str) -> Path:
    today = datetime.now(CST).strftime("%Y-%m-%d")
    filename = f"{today}-{slug}.md"
    filepath = BLOG_DIR / filename
    
    tags_yaml = ", ".join(f'"{t}"' for t in tags)
    frontmatter = f"""---
title: '{title}'
description: '{description}'
pubDate: '{today}'
tags: [{tags_yaml}]
---

"""
    
    filepath.write_text(frontmatter + content, encoding="utf-8")
    print(f"[write] 写入：{filepath}")
    return filepath

# ─── Git 提交推送 ────────────────────────────────────────────
def git_push(filepath: Path, title: str):
    repo_root = Path(__file__).parent.parent
    
    cmds = [
        ["git", "add", str(filepath)],
        ["git", "commit", "-m", f"feat: 每日博客 — {title}"],
        ["git", "push", "origin", "main"],
    ]
    
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[git] 错误: {' '.join(cmd)}\n{result.stderr}")
            raise RuntimeError(f"Git 命令失败: {' '.join(cmd)}")
        print(f"[git] ✅ {' '.join(cmd[:2])}")
    
    print("[git] 🚀 已推送，Cloudflare Pages 将自动部署！")

# ─── 主流程 ──────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Python Ship 每日博客生成器")
    parser.add_argument("--topic", help="指定话题（不指定则自动搜索）")
    parser.add_argument("--dry-run", action="store_true", help="只生成文件，不推送 GitHub")
    args = parser.parse_args()
    
    # 检查 API Key
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("❌ 请设置环境变量 ANTHROPIC_API_KEY")
        sys.exit(1)
    
    print(f"\n🐍 Python Ship 每日博客生成器")
    print(f"📅 {datetime.now(CST).strftime('%Y-%m-%d %H:%M')} (北京时间)\n")
    
    # 1. 选话题
    topic = pick_topic(args.topic)
    
    # 2. 生成内容
    title, description, content, tags, slug = generate_post(topic)
    print(f"[meta] 标题：{title}")
    print(f"[meta] 标签：{tags}")
    
    # 3. 写文件
    filepath = write_post(title, description, content, tags, slug)
    
    # 4. 推送
    if not args.dry_run:
        git_push(filepath, title)
        print(f"\n✅ 完成！文章「{title}」已发布。")
    else:
        print(f"\n✅ Dry run 完成！文件已生成：{filepath}")

if __name__ == "__main__":
    main()
