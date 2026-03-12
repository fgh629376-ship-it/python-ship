# 🐍 Python Ship

每日 Python 知识库 — 技术干货 · 教程 · 知识卡片

**自动发布**：每晚 22:00 (北京时间) 自动生成并推送新博文，Cloudflare Pages 自动部署。

## 本地开发

```bash
npm install
npm run dev      # 启动开发服务器 http://localhost:4321
npm run build    # 构建静态文件
npm run preview  # 预览构建结果
```

## 自动发布脚本

```bash
# 安装 Python 依赖
pip install -r scripts/requirements.txt

# 设置 API Key
export ANTHROPIC_API_KEY=sk-ant-...

# 手动触发（测试用）
python scripts/post-generator.py

# 指定话题
python scripts/post-generator.py --topic "Python decorators"

# 只生成不推送
python scripts/post-generator.py --dry-run
```

## Cloudflare Pages 部署

1. 在 [Cloudflare Pages](https://pages.cloudflare.com/) 创建项目
2. 连接 GitHub 仓库 `fgh629376-ship-it/python-ship`
3. 构建配置：
   - **Framework preset**: Astro
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
4. 部署完成后，每次 push 自动触发重新部署

## 项目结构

```
python-ship/
├── src/
│   ├── content/blog/   ← 博客文章（Markdown）
│   ├── components/     ← Astro 组件
│   ├── layouts/        ← 页面布局
│   └── pages/          ← 路由页面
├── scripts/
│   └── post-generator.py  ← 每日自动发布脚本
└── public/             ← 静态资源
```
