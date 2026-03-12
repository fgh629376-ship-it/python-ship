#!/usr/bin/env python3
"""
Python Ship — 博客发布脚本
接收生成好的内容，写入 markdown 文件并推送 GitHub。

用法:
  python scripts/post-generator.py --title "标题" --content "内容" --tags "Python,教程型" --slug "my-post"
  python scripts/post-generator.py --dry-run  # 只写文件不推送
"""

import argparse
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BLOG_DIR = Path(__file__).parent.parent / "src" / "content" / "blog"
CST = timezone(timedelta(hours=8))


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


def git_push(filepath: Path, title: str):
    repo_root = Path(__file__).parent.parent
    token = (repo_root / ".gh_token").read_text().strip()
    remote = f"https://{token}@github.com/fgh629376-ship-it/python-ship.git"

    cmds = [
        ["git", "add", str(filepath)],
        ["git", "commit", "-m", f"feat: 每日博客 — {title}"],
        ["git", "push", remote, "main"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[git] 错误: {result.stderr}")
            sys.exit(1)
        print(f"[git] ✅ {' '.join(cmd[:2])}")
    print("[git] 🚀 推送完成，Cloudflare 自动部署中！")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", default="")
    parser.add_argument("--content", required=True)
    parser.add_argument("--tags", default="Python,技术干货")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",")]
    description = args.description or args.title

    filepath = write_post(args.title, description, args.content, tags, args.slug)

    if not args.dry_run:
        git_push(filepath, args.title)
        print(f"✅ 「{args.title}」已发布！")
    else:
        print(f"✅ Dry run — 文件：{filepath}")


if __name__ == "__main__":
    main()
