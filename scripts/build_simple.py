#!/usr/bin/env python3
"""
生成静态网站 (无外部依赖版本)
"""
import json
import os
from datetime import datetime, timedelta


def load_summarized_news(date_str=None):
    """加载摘要新闻"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    filename = f'data/summarized_news_{date_str}.json'

    if not os.path.exists(filename):
        print(f"❌ 错误：找不到当天数据文件 {filename}")
        return None, date_str

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data, date_str


def generate_news_html(news_list):
    """生成新闻列表HTML"""
    html = []
    for i, item in enumerate(news_list, 1):
        html.append(f'''
            <article class="news-item">
                <div class="news-header">
                    <span class="news-num">{i}</span>
                    <h2 class="news-title">
                        <a href="{item['url']}" target="_blank" rel="noopener">{item['cn_title']}</a>
                    </h2>
                </div>
                <div class="news-content">
                    <p class="news-summary">{item['summary']}</p>
                    <div class="news-meta">
                        <span class="source">{item['source']}</span>
                        <a href="{item['url']}" class="original-link" target="_blank" rel="noopener">阅读原文 →</a>
                    </div>
                </div>
            </article>''')
    return '\n'.join(html)


def generate_daily_page(data, date_str):
    """生成每日页面"""
    # 获取星期几
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekdays[date_obj.weekday()]
    
    # 获取上一天日期
    prev_date_obj = date_obj - timedelta(days=1)
    prev_date = prev_date_obj.strftime('%Y-%m-%d')
    
    # 检查前一天文件是否存在
    prev_file = f'docs/archive/{prev_date}.html'
    prev_link = f'<a href="./archive/{prev_date}.html" class="nav-link">← {prev_date}</a>' if os.path.exists(prev_file) else ''
    
    news_html = generate_news_html(data['news'])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Aviation Daily - {date_str}</title>
    <link rel="stylesheet" href="static/style.css?v={date_str}">
</head>
<body>
    <div class="container">
        <header>
            <h1>Aviation Daily</h1>
            <p class="subtitle">每日国际航空产业情报</p>
            <p class="date">{date_str} · {weekday}</p>
            <div class="filter-info">
                <span class="filter-tag">✈️ 波音空客动态</span>
                <span class="filter-tag">📦 供应链情报</span>
                <span class="filter-tag">⚠️ 安全事件</span>
                <span class="filter-tag">🌍 地缘政治</span>
            </div>
        </header>
        
        <main>
            {news_html}
        </main>
        
        <footer>
            <div class="nav">
                {prev_link}
                <a href="./archive/" class="nav-link">历史归档</a>
            </div>
            <p class="footer-info">
                每日8:00自动更新 · 已剔除军机/直升机/商飞相关新闻 ·
                <a href="https://github.com/user/aviation-daily">GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>'''
    
    return html


def generate_archive_page():
    """生成归档页面"""
    # 获取所有历史日期
    archive_files = []
    if os.path.exists('docs/archive'):
        archive_files = [f for f in os.listdir('docs/archive') if f.endswith('.html') and f != 'index.html']
    
    dates = sorted([f.replace('.html', '') for f in archive_files], reverse=True)
    
    dates_html = '\n'.join([f'<div class="archive-item"><a href="./{d}.html" class="archive-link">{d}</a></div>' for d in dates])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>历史归档 - Aviation Daily</title>
    <link rel="stylesheet" href="../static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Aviation Daily</h1>
            <p class="subtitle">历史归档</p>
        </header>
        
        <main>
            <div class="archive-list">
                {dates_html}
            </div>
        </main>
        
        <footer>
            <div class="nav">
                <a href="../" class="nav-link">← 返回今日</a>
            </div>
        </footer>
    </div>
</body>
</html>'''
    
    return html


def build_site():
    """构建完整网站"""
    print("开始构建网站...")
    print("-" * 40)
    
    # 加载新闻数据
    data, date_str = load_summarized_news()
    if not data:
        print("找不到新闻数据")
        return False
    
    print(f"加载数据: {date_str}, 共{data['news_count']}条")
    
    # 确保目录存在
    os.makedirs('docs/archive', exist_ok=True)
    
    # 1. 生成今日首页 (index.html)
    index_html = generate_daily_page(data, date_str)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("✓ docs/index.html")
    
    # 2. 生成历史归档页面
    archive_html = generate_daily_page(data, date_str)
    archive_file = f'docs/archive/{date_str}.html'
    with open(archive_file, 'w', encoding='utf-8') as f:
        f.write(archive_html)
    print(f"✓ {archive_file}")
    
    # 3. 更新归档列表页
    archive_index = generate_archive_page()
    with open('docs/archive/index.html', 'w', encoding='utf-8') as f:
        f.write(archive_index)
    print("✓ docs/archive/index.html")
    
    print("-" * 40)
    print("网站构建完成!")
    return True


if __name__ == '__main__':
    build_site()
