# 部署指南

## 快速开始

### 1. 创建 GitHub 仓库

1. 登录 GitHub
2. 创建新仓库，命名为 `aviation-daily`
3. **不要**初始化 README（我们已经有现成的）

### 2. 上传代码

```bash
# 在本项目目录下执行
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/aviation-daily.git
git push -u origin main
```

### 3. 配置 Secrets

在 GitHub 仓库页面：

**Settings → Secrets and variables → Actions → New repository secret**

添加以下 secret：

| Name | Value |
|------|-------|
| `KIMI_API_KEY` | 你的 Kimi API 密钥 |

**获取 Kimi API Key：**
1. 访问 https://platform.moonshot.cn/
2. 登录并创建 API Key
3. 复制并粘贴到 Secrets 中

### 4. 启用 GitHub Pages

**Settings → Pages**

- **Source**: Deploy from a branch
- **Branch**: `gh-pages` / `root`
- 点击 Save

等待几分钟，访问 `https://YOUR_USERNAME.github.io/aviation-daily/`

### 5. 测试运行

在 GitHub 仓库页面：

**Actions → Daily Aviation Report → Run workflow**

手动触发一次测试运行。

---

## 自定义配置

### 修改数据源

编辑 `config.json` 文件：

```json
{
  "sources": {
    "flightglobal": {
      "name": "FlightGlobal",
      "url": "https://www.flightglobal.com/rss",
      "enabled": true
    },
    // 添加更多源...
  }
}
```

### 自定义域名（可选）

**Settings → Secrets → New repository secret**

添加 `CUSTOM_DOMAIN`，值为你的域名（如 `aviation.yourdomain.com`）

然后在你的 DNS 服务商添加 CNAME 记录：

```
CNAME  aviation  YOUR_USERNAME.github.io
```

### 修改定时时间

编辑 `.github/workflows/daily.yml`：

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # UTC时间，北京时间 = UTC+8
```

常用时间：
- `0 0 * * *` = 北京时间 8:00
- `0 22 * * *` = 北京时间 6:00
- `30 23 * * *` = 北京时间 7:30

---

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export KIMI_API_KEY="your-api-key"

# 运行完整流程
python run.py

# 或分步运行
python scripts/fetch.py
python scripts/summarize.py
python scripts/build.py

# 本地预览
cd docs
python -m http.server 8000
# 访问 http://localhost:8000
```

---

## 故障排查

### Action 运行失败

1. **检查 Secrets 是否配置正确**
   - Settings → Secrets and variables → Actions

2. **查看运行日志**
   - Actions → 选择失败的运行 → 查看日志

3. **常见问题**
   - `KIMI_API_KEY` 未设置或错误
   - RSS 源失效（检查 config.json）
   - API 调用超时（网络问题）

### 网站未更新

1. **检查 gh-pages 分支**
   - 确认 Actions 成功运行
   - 查看 gh-pages 分支是否有新提交

2. **清除浏览器缓存**
   - GitHub Pages 有 CDN 缓存
   - 添加 `?nocache=1` 强制刷新

3. **检查 Pages 设置**
   - Settings → Pages → Source 是否正确

---

## 高级功能

### 添加邮件订阅

使用 Buttondown 或 Mailchimp API，在 workflow 中添加发送步骤。

### 添加 Telegram 推送

添加 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID` secrets，
在 workflow 中添加发送脚本。

### 多语言支持

修改 `summarize.py` 中的 prompt，要求输出多语言版本。

---

有问题？在 GitHub Issues 中提问。
