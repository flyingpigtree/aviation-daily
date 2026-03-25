# Aviation Daily Report

每日国际航空新闻精选，自动抓取、AI翻译摘要、极简呈现。

🌐 **在线访问**: https://[your-github-username].github.io/aviation-daily/

---

## 功能特性

- 📰 每天8点自动抓取国际航空新闻
- 🌍 英文新闻AI翻译为中文摘要
- 🔗 每条新闻保留原文链接
- 📱 极简风格，移动端友好
- 📅 历史归档，支持日期跳转

---

## 技术栈

- **数据抓取**: Python + feedparser + requests
- **AI摘要**: Kimi API (kimi-k2p5)
- **网站生成**: 纯静态HTML
- **定时任务**: GitHub Actions
- **托管部署**: GitHub Pages

---

## 本地开发

```bash
# 克隆仓库
git clone https://github.com/[your-username]/aviation-daily.git
cd aviation-daily

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置API Key
export KIMI_API_KEY="your-api-key"

# 手动运行生成
python scripts/fetch.py
python scripts/summarize.py
python scripts/build.py

# 本地预览
cd docs && python -m http.server 8000
```

---

## 配置说明

### 1. 设置 GitHub Secrets

在仓库 Settings -> Secrets and variables -> Actions 中添加:

- `KIMI_API_KEY`: 你的Kimi API密钥
- `GITHUB_TOKEN`: 自动生成，无需手动设置

### 2. 启用 GitHub Pages

Settings -> Pages -> Source 选择 "Deploy from a branch" -> Branch: `gh-pages`

### 3. 自定义域名（可选）

在 `docs/CNAME` 文件中添加你的域名。

---

## 数据源

- FlightGlobal
- Aviation Week
- Reuters Aerospace
- SimpleFlying
- Airbus Newsroom
- Boeing Newsroom
- ...

---

## 目录结构

```
aviation-daily/
├── scripts/
│   ├── fetch.py          # 抓取新闻
│   ├── summarize.py      # AI生成摘要
│   └── build.py          # 生成网站
├── docs/                 # GitHub Pages目录
│   ├── index.html        # 今日日报
│   ├── archive/          # 历史归档
│   └── static/
│       └── style.css     # 样式文件
├── .github/workflows/
│   └── daily.yml         # 定时任务
├── config.json           # 数据源配置
└── requirements.txt      # Python依赖
```

---

## 许可证

MIT License
