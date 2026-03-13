#!/usr/bin/env python3
"""
Python Ship — 博客发布脚本
接收生成好的内容，写入 markdown 文件并推送 GitHub + 部署到 Cloudflare Workers。

用法:
  python scripts/post-generator.py --title "标题" --content "内容" --tags "Python,教程型" --slug "my-post" --category python
  python scripts/post-generator.py --dry-run  # 只写文件不推送
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BLOG_DIR = Path(__file__).parent.parent / "src" / "content" / "blog"
REPO_ROOT = Path(__file__).parent.parent
CST = timezone(timedelta(hours=8))


def load_cloudflare_env():
    """从 .cloudflare_env 文件加载凭证到环境变量"""
    env_file = REPO_ROOT / ".cloudflare_env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def write_post(title: str, description: str, content: str, tags: list[str],
               slug: str, category: str) -> Path:
    today = datetime.now(CST).strftime("%Y-%m-%d")
    filename = f"{today}-{slug}.md"
    filepath = BLOG_DIR / filename

    tags_yaml = ", ".join(f'"{t}"' for t in tags)
    frontmatter = f"""---
title: '{title}'
description: '{description}'
pubDate: '{today}'
category: {category}
tags: [{tags_yaml}]
---

"""
    filepath.write_text(frontmatter + content, encoding="utf-8")
    print(f"[write] 写入：{filepath}")
    return filepath


def git_push(filepath: Path, title: str):
    token_file = REPO_ROOT / ".gh_token"
    token = token_file.read_text().strip()
    remote = f"https://{token}@github.com/fgh629376-ship-it/python-ship.git"

    cmds = [
        ["git", "add", str(filepath)],
        ["git", "commit", "-m", f"feat: 每日博客 — {title}"],
        ["git", "push", remote, "main"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[git] 错误: {result.stderr}")
            sys.exit(1)
        print(f"[git] ✅ {' '.join(cmd[:2])}")
    print("[git] 推送完成")


def deploy_workers():
    """构建 + 部署到 Cloudflare Workers"""
    load_cloudflare_env()

    print("[deploy] 构建 Astro...")
    build = subprocess.run(["npm", "run", "build"], cwd=REPO_ROOT,
                           capture_output=True, text=True)
    if build.returncode != 0:
        print(f"[deploy] 构建失败:\n{build.stderr}")
        sys.exit(1)
    print("[deploy] ✅ 构建成功")

    print("[deploy] 部署到 Cloudflare Workers...")
    deploy = subprocess.run(["npx", "wrangler", "deploy"], cwd=REPO_ROOT,
                            capture_output=True, text=True,
                            env={**os.environ})
    if deploy.returncode != 0:
        print(f"[deploy] 部署失败:\n{deploy.stderr}")
        sys.exit(1)

    # 从输出里提取部署 URL
    for line in deploy.stdout.splitlines():
        if "workers.dev" in line:
            print(f"[deploy] ✅ 上线：{line.strip()}")
            break
    else:
        print("[deploy] ✅ 部署成功")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", default="")
    parser.add_argument("--content", required=True)
    parser.add_argument("--tags", default="Python,技术干货")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--category", default="python",
                        choices=["python", "solar"],
                        help="文章分类: python 或 solar")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",")]
    description = args.description or args.title

    filepath = write_post(args.title, description, args.content,
                          tags, args.slug, args.category)

    if not args.dry_run:
        git_push(filepath, args.title)
        deploy_workers()
        print(f"\n✅ 「{args.title}」已发布到 https://python-ship.fgh629376.workers.dev")
    else:
        print(f"✅ Dry run — 文件：{filepath}")


if __name__ == "__main__":
    main()
