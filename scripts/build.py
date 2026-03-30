#!/usr/bin/env python3
"""
生成静态网站
"""
import json
import os
from datetime import datetime, timedelta
from jinja2 import Template

# HTML模板
INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aviation Daily - {{ date }}</title>
    <link rel="stylesheet" href="static/style.css">
    <link rel="alternate" type="application/rss+xml" title="Aviation Daily RSS" href="feed.xml">
</head>
<body>
    <div class="container">
        <header>
            <h1>Aviation Daily</h1>
            <p class="subtitle">每日国际航空新闻精选</p>
            <p class="date">{{ date }} · {{ weekday }}</p>
        </header>
        
        <main>
            {% for item in news %}
            <article class="news-item">
                <span class="news-num">{{ loop.index }}</span>
                <div class="news-content">
                    <h2 class="news-title">
                        <a href="{{ item.url }}" target="_blank" rel="noopener">{{ item.cn_title }}</a>
                    </h2>
                    <p class="news-summary">{{ item.summary }}</p>
                    <div class="news-meta">
                        <span class="source">{{ item.source }}</span>
                        <a href="{{ item.url }}" class="original-link" target="_blank" rel="noopener">原文 →</a>
                    </div>
                </div>
            </article>
            {% endfor %}
        </main>
        
        <footer>
            <div class="nav">
                {% if prev_date %}<a href="./archive/{{ prev_date }}.html" class="nav-link">← {{ prev_date }}</a>{% endif %}
                <a href="./archive/" class="nav-link">历史归档</a>
            </div>
            <p class="footer-info">
                每日8:00自动更新 · 
                <a href="https://github.com/{{ github_user }}/aviation-daily">GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>'''

ARCHIVE_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                {% for date in dates %}
                <div class="archive-item">
                    <a href="./{{ date }}.html" class="archive-link">{{ date }}</a>
                </div>
                {% endfor %}
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


def load_summarized_news(date_str=None):
    """加载摘要新闻"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    filename = f'data/summarized_news_{date_str}.json'

    if not os.path.exists(filename):
        print(f"❌ 错误：找不到当天数据文件 {filename}")
        print("可能原因：")
        print("  1. fetch.py 没有抓取到新闻")
        print("  2. summarize.py 生成摘要失败（检查 KIMI_API_KEY）")
        print("  3. 今天是周末/节假日，新闻源没有更新")
        return None, date_str

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 验证数据日期匹配
    if data.get('date') != date_str:
        print(f"⚠️ 警告：数据文件日期 ({data.get('date')}) 与预期 ({date_str}) 不匹配")
        return None, date_str

    return data, date_str


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
    if not os.path.exists(prev_file):
        prev_date = None
    
    template = Template(INDEX_TEMPLATE)
    html = template.render(
        date=date_str,
        weekday=weekday,
        news=data['news'],
        prev_date=prev_date,
        github_user=os.getenv('GITHUB_REPOSITORY', 'user').split('/')[0]
    )
    
    return html


def generate_archive_page():
    """生成归档页面"""
    # 获取所有历史日期
    archive_files = []
    if os.path.exists('docs/archive'):
        archive_files = [f for f in os.listdir('docs/archive') if f.endswith('.html') and f != 'index.html']
    
    dates = sorted([f.replace('.html', '') for f in archive_files], reverse=True)
    
    template = Template(ARCHIVE_TEMPLATE)
    html = template.render(dates=dates)
    
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
