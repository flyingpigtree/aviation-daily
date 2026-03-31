# Aviation Daily Report

每日国际航空产业情报，自动抓取、AI深度分析、精准筛选。

🌐 **在线访问**: https://[your-github-username].github.io/aviation-daily/

---

## 功能特性

- 📰 每天8点自动抓取国际航空新闻
- 🤖 AI深度分析生成结构化摘要（100-200字）
- 🎯 智能筛选：聚焦产业竞争、供应链、安全事件、地缘政治
- 🚫 自动剔除：军机/直升机、商飞COMAC内部信息
- 🔗 每条新闻保留原文链接
- 📱 极简风格，移动端友好
- 📅 历史归档，支持日期跳转

---

## 内容筛选标准

### ✅ 优先报道

| 类别 | 示例 |
|------|------|
| **竞争动态** | 波音、空客订单交付、产品策略、市场份额 |
| **供应链情报** | 发动机、航电、复合材料、零部件供应、产能变化 |
| **安全事件** | 事故调查、适航指令、安全法规变化 |
| **地缘政治** | 制裁、贸易争端、航空外交、航权谈判 |
| **近期重点** | 伊朗战争对航空业影响、后疫情供应链复苏、俄罗斯国产客机/进口替代 |

### ❌ 自动剔除

- 军机/军用直升机项目（战斗机、轰炸机、国防合同）
- 中国商飞COMAC自身动作、交付、订单等
- 航空公司纯财务报告、人事变动

---

## 技术栈

- **数据抓取**: Python + feedparser + requests
- **AI分析**: Kimi API (moonshot-v1-8k)
- **网站生成**: 纯静态HTML + Jinja2
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
python scripts/fetch.py      # 抓取新闻
python scripts/summarize.py  # AI生成摘要
python scripts/build.py      # 构建网站

# 或一键运行
python run.py

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
- Reuters Aerospace & Defense
- Air Transport World (ATW)
- AIN Online
- CH-Aviation
- Boeing Newsroom
- Airbus Newsroom

---

## 目录结构

```
aviation-daily/
├── scripts/
│   ├── fetch.py          # 抓取新闻
│   ├── summarize.py      # AI生成深度摘要
│   └── build.py          # 生成网站
├── docs/                 # GitHub Pages目录
│   ├── index.html        # 今日日报
│   ├── archive/          # 历史归档
│   └── static/
│       └── style.css     # 样式文件
├── data/                 # 原始数据与摘要
├── .github/workflows/
│   └── daily.yml         # 定时任务
├── config.json           # 数据源与筛选配置
├── run.py                # 一键运行入口
└── requirements.txt      # Python依赖
```

---

## 更新日志

### 2025-03-30 内容优化

- **摘要增强**: 从20-30字扩展至100-200字结构化摘要
- **筛选优化**: 明确包含/剔除规则，聚焦产业情报
- **近期重点**: 新增伊朗战争、供应链复苏、俄罗斯客机追踪
- **样式升级**: 优化长摘要阅读体验

---

## 许可证

MIT License
