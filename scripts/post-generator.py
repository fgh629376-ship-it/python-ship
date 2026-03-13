#!/usr/bin/env python3
"""
Python Ship — 博客发布脚本
支持多语言版本生成（zh/en/ja）。

用法:
  # 单语发布（中文）
  python scripts/post-generator.py --title "标题" --content "内容" --tags "Python,教程" --slug "my-post" --category python

  # 多语发布（同时写入 en/ja 版本）
  python scripts/post-generator.py --title "标题" --content "内容" --tags "Python,教程" --slug "my-post" --category python \
    --title-en "Title" --content-en "English content" \
    --title-ja "タイトル" --content-ja "Japanese content"

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
               slug: str, category: str, lang: str = "zh") -> Path:
    today = datetime.now(CST).strftime("%Y-%m-%d")

    # 文件名：中文版无后缀，其他语言加 .en / .ja
    if lang == "zh":
        filename = f"{today}-{slug}.md"
    else:
        filename = f"{today}-{slug}.{lang}.md"

    filepath = BLOG_DIR / filename

    tags_yaml = ", ".join(f'"{t}"' for t in tags)
    # 转义标题中的单引号
    safe_title = title.replace("'", "''")
    safe_desc = description.replace("'", "''")

    frontmatter = f"""---
title: '{safe_title}'
description: '{safe_desc}'
pubDate: '{today}'
category: {category}
lang: {lang}
tags: [{tags_yaml}]
---

"""
    filepath.write_text(frontmatter + content, encoding="utf-8")
    print(f"[write] [{lang}] 写入：{filepath}")
    return filepath


def git_push(filepaths: list[Path], title: str):
    token_file = REPO_ROOT / ".gh_token"
    token = token_file.read_text().strip()
    remote = f"https://{token}@github.com/fgh629376-ship-it/python-ship.git"

    # Add all files
    for fp in filepaths:
        subprocess.run(["git", "add", str(fp)], cwd=REPO_ROOT,
                       capture_output=True, text=True)

    cmds = [
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

    for line in deploy.stdout.splitlines():
        if "workers.dev" in line:
            print(f"[deploy] ✅ 上线：{line.strip()}")
            break
    else:
        print("[deploy] ✅ 部署成功")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="中文标题")
    parser.add_argument("--description", default="", help="中文描述")
    parser.add_argument("--content", required=True, help="中文内容")
    parser.add_argument("--tags", default="Python,技术干货")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--category", default="python",
                        choices=["python", "solar"])
    # 英文版
    parser.add_argument("--title-en", default="", help="英文标题")
    parser.add_argument("--description-en", default="", help="英文描述")
    parser.add_argument("--content-en", default="", help="英文内容")
    # 日文版
    parser.add_argument("--title-ja", default="", help="日文标题")
    parser.add_argument("--description-ja", default="", help="日文描述")
    parser.add_argument("--content-ja", default="", help="日文内容")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",")]
    description = args.description or args.title

    filepaths = []

    # 中文版（必须）
    fp_zh = write_post(args.title, description, args.content,
                       tags, args.slug, args.category, "zh")
    filepaths.append(fp_zh)

    # 英文版（可选）
    if args.title_en and args.content_en:
        desc_en = args.description_en or args.title_en
        fp_en = write_post(args.title_en, desc_en, args.content_en,
                           tags, args.slug, args.category, "en")
        filepaths.append(fp_en)

    # 日文版（可选）
    if args.title_ja and args.content_ja:
        desc_ja = args.description_ja or args.title_ja
        fp_ja = write_post(args.title_ja, desc_ja, args.content_ja,
                           tags, args.slug, args.category, "ja")
        filepaths.append(fp_ja)

    if not args.dry_run:
        git_push(filepaths, args.title)
        deploy_workers()
        langs = [fp.stem.split(".")[-1] if "." in fp.stem else "zh" for fp in filepaths]
        print(f"\n✅ 「{args.title}」已发布 [{'/'.join(langs)}] 到 https://python-ship.fgh629376.workers.dev")
    else:
        print(f"✅ Dry run — 文件：{[str(fp) for fp in filepaths]}")


if __name__ == "__main__":
    main()
