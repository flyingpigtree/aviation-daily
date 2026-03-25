# Aviation Daily

每日国际航空新闻精选

## 项目结构

```
aviation-daily/
├── .github/workflows/daily.yml    # 自动化工作流
├── scripts/
│   ├── fetch.py                   # 抓取新闻
│   ├── summarize.py               # AI生成摘要
│   └── build.py                   # 构建网站
├── docs/                          # GitHub Pages目录
│   ├── index.html                 # 今日日报
│   ├── archive/                   # 历史归档
│   └── static/
│       └── style.css              # 样式文件
├── config.json                    # 数据源配置
├── requirements.txt               # Python依赖
├── run.py                         # 本地运行入口
├── README.md                      # 项目说明
└── DEPLOY.md                      # 部署指南
```

## 快速开始

1. Fork/Clone 本仓库
2. 配置 `KIMI_API_KEY` 到 GitHub Secrets
3. 启用 GitHub Pages
4. 完成！

详细步骤请查看 [DEPLOY.md](./DEPLOY.md)

## 数据源

- FlightGlobal
- Aviation Week
- Simple Flying
- AirLive
- ATW Online
- Reuters Aerospace

## 技术栈

- Python + feedparser
- Kimi AI (kimi-k2p5)
- GitHub Actions
- GitHub Pages

## 许可证

MIT
