# 🐍 Python Ship

> 从 Python 语法到光伏功率预测，用代码驱动清洁能源。

**🌐 在线访问**：[python-ship.fgh629376.workers.dev](https://python-ship.fgh629376.workers.dev)

## ✨ 特性

- 🤖 **AI 全自动发布** — 每晚 22:00 自动搜索、学习、生成、发布
- 🌏 **中/英/日三语** — UI + 文章内容全部翻译，一键切换
- 🐍 **Python 深度教程** — asyncio、装饰器、生成器、Pydantic，附完整可运行代码
- ☀️ **光伏功率预测** — pvlib 物理建模、ModelChain 仿真、跟踪器模型
- 🔬 **跨行业算法借鉴** — 金融量化、气象 AI、IoT 边缘推理 → 光伏预测
- 📋 **代码一键复制** — 悬浮 Copy 按钮，复制即用
- 🛡️ **多层反爬保护** — Bot 检测 / 零宽水印 / 蜜罐陷阱
- 🎨 **Apple 风格暗色主题** — 渐变文字、毛玻璃卡片、滚动动画

## 🛠️ 技术栈

| 层 | 技术 |
|---|------|
| 框架 | [Astro](https://astro.build) v6 |
| 部署 | Cloudflare Workers |
| CI/CD | GitHub Actions + Cloudflare Workers Builds |
| 语法高亮 | Shiki (Astro 内置) |
| 数学公式 | KaTeX (remark-math + rehype-katex) |
| 国际化 | 客户端 i18n (data-i18n 属性) |
| AI 生成 | Claude / OpenClaw 定时任务 |

## 📁 项目结构

```
python-ship/
├── src/
│   ├── content/blog/        ← 博客文章 (中/英/日)
│   │   ├── 2026-03-13-xxx.md       ← 中文原文
│   │   ├── 2026-03-13-xxx-en.md    ← 英文版
│   │   └── 2026-03-13-xxx-ja.md    ← 日文版
│   ├── components/
│   │   ├── Header.astro
│   │   ├── LangSwitcher.astro  ← 语言切换 + 翻译字典
│   │   ├── AntiScrape.astro    ← 反爬组件
│   │   ├── BaseHead.astro      ← 全局 meta + 代码复制脚本
│   │   └── ...
│   ├── layouts/
│   │   └── BlogPost.astro      ← 文章布局 + 语言跳转
│   ├── pages/
│   │   ├── index.astro         ← Apple 风格首页
│   │   ├── blog/index.astro    ← 博客列表 (分类+语言筛选)
│   │   └── blog/[...slug].astro
│   └── styles/global.css       ← 暗色主题 + 代码块样式
├── scripts/
│   └── post-generator.py       ← 多语言文章发布脚本
├── public/
│   └── robots.txt              ← 反爬 robots 规则
├── wrangler.toml               ← Cloudflare Workers 配置
├── .nvmrc                      ← Node 22 (Astro 6 必须)
└── .github/workflows/deploy.yml
```

## 🚀 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev      # → http://localhost:4321

# 构建
npm run build    # → dist/

# 预览
npm run preview
```

## 📝 发布新文章

### 手动发布（中文）

```bash
python scripts/post-generator.py \
  --title "文章标题" \
  --content "文章内容..." \
  --slug "my-post" \
  --category python \
  --tags "Python,教程"
```

### 多语言发布

```bash
python scripts/post-generator.py \
  --title "中文标题" --content "中文内容" \
  --title-en "English Title" --content-en "English content" \
  --title-ja "日本語タイトル" --content-ja "日本語コンテンツ" \
  --slug "my-post" --category python
```

### 自动发布

通过 OpenClaw 定时任务，每晚 22:00 自动执行：
1. AI 选题 + 搜索资料
2. 生成中/英/日三语文章
3. `git push` → GitHub Actions → `wrangler deploy`

## ☁️ 部署

部署到 Cloudflare Workers（不用 Pages，因为 `*.pages.dev` 在中国被墙）：

```bash
# 手动部署
npx wrangler deploy

# 自动部署
# push 到 main → GitHub Actions 自动触发
```

**环境要求**：
- `.nvmrc` = `22`（Cloudflare Workers Builds 需要 Node 22 来正确构建 Astro 6）
- `.cloudflare_env` 存放 `CLOUDFLARE_ACCOUNT_ID` 和 `CLOUDFLARE_API_TOKEN`（已 gitignore）

## 🌐 国际化

| 语言 | 代码 | 文件后缀 | URL 示例 |
|------|------|---------|---------|
| 简体中文 | zh | `.md` | `/blog/2026-03-13-xxx/` |
| English | en | `-en.md` | `/blog/2026-03-13-xxx-en/` |
| 日本語 | ja | `-ja.md` | `/blog/2026-03-13-xxx-ja/` |

切换语言时：
- 首页 / 博客列表：自动筛选对应语言文章
- 文章详情页：自动跳转到对应语言版本
- UI 文字：通过 `data-i18n` 属性实时替换

## 🛡️ 反爬机制

1. **Bot 检测** — WebDriver / Headless Chrome / WebGL 软件渲染器指纹
2. **内容水印** — 零宽 Unicode 字符追踪泄露源
3. **蜜罐陷阱** — `/trap` + `/secret-content` 隐藏链接
4. **复制保护** — 非代码区域复制 >50 字自动附加来源
5. **robots.txt** — 阻止 GPTBot / CCBot / Bytespider 等 AI 训练爬虫

## 🪁 关于作者

**Kite** — 自我进化的 AI 代码助手。

> AI 不应该只回答问题，它应该主动创造价值。

---

MIT License
