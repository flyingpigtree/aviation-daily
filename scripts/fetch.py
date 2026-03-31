#!/usr/bin/env python3
"""
抓取国际航空新闻
"""
import json
import feedparser
import hashlib
from datetime import datetime, timedelta
from urllib.parse import urlparse
import os
import sys

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(__file__))
from database import init_db, save_raw_news

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


def get_domain(url):
    """从URL获取域名"""
    return urlparse(url).netloc.replace('www.', '')


def get_time_window():
    """获取抓取时间窗口：昨日8点至当日8点"""
    now = datetime.now()
    # 当日8点
    today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    # 昨日8点
    yesterday_8am = today_8am - timedelta(days=1)
    
    # 如果当前时间早于8点，则调整窗口
    if now.hour < 8:
        today_8am = today_8am - timedelta(days=1)
        yesterday_8am = yesterday_8am - timedelta(days=1)
    
    return yesterday_8am, today_8am


def parse_datetime(entry):
    """解析RSS条目的发布时间，返回datetime对象"""
    try:
        # 优先使用解析好的时间元组
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        
        # 尝试解析字符串格式
        import time
        for field in ['published', 'updated']:
            if hasattr(entry, field):
                date_str = getattr(entry, field)
                if date_str:
                    # 尝试RFC 2822格式
                    try:
                        parsed = time.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                        return datetime.fromtimestamp(time.mktime(parsed))
                    except:
                        pass
                    # 尝试ISO格式
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        pass
    except Exception:
        pass
    return None


def fetch_rss(source_id, source_config):
    """抓取RSS源"""
    if not source_config.get('enabled', True):
        return []

    try:
        feed = feedparser.parse(source_config['url'])
        items = []
        
        # 获取24小时时间窗口
        window_start, window_end = get_time_window()

        for entry in feed.entries[:config['settings']['max_news_per_source'] * 3]:
            # 解析发布时间
            news_datetime = parse_datetime(entry)
            
            # 如果没有解析到时间，跳过
            if not news_datetime:
                continue
            
            # 只保留在昨日8点至当日8点之间的新闻
            if not (window_start <= news_datetime <= window_end):
                continue

            # 生成唯一ID
            unique_str = f"{entry.title}{entry.link}"
            news_id = hashlib.md5(unique_str.encode()).hexdigest()[:12]

            items.append({
                'id': news_id,
                'title': entry.title,
                'link': entry.link,
                'summary': entry.get('summary', '')[:500],
                'published': entry.get('published', entry.get('updated', '')),
                'published_datetime': news_datetime.isoformat(),
                'source': source_config['name'],
                'domain': get_domain(entry.link)
            })

            if len(items) >= config['settings']['max_news_per_source']:
                break

        print(f"✓ {source_config['name']}: {len(items)}条 ({window_start.strftime('%Y-%m-%d %H:%M')} ~ {window_end.strftime('%Y-%m-%d %H:%M')})")
        return items

    except Exception as e:
        print(f"✗ {source_config['name']}: {str(e)}")
        return []


def fetch_all_news():
    """抓取所有源的新闻"""
    all_news = []
    
    # 获取时间窗口
    window_start, window_end = get_time_window()
    
    print("开始抓取新闻...")
    print(f"时间窗口: {window_start.strftime('%Y-%m-%d %H:%M')} ~ {window_end.strftime('%Y-%m-%d %H:%M')}")
    print("-" * 40)
    
    for source_id, source_config in config['sources'].items():
        news = fetch_rss(source_id, source_config)
        all_news.extend(news)
    
    print("-" * 40)
    print(f"总计抓取: {len(all_news)}条")
    
    # 按发布时间排序
    all_news.sort(key=lambda x: x.get('published_datetime', ''), reverse=True)
    
    # 去重（基于ID）
    seen_ids = set()
    unique_news = []
    for news in all_news:
        if news['id'] not in seen_ids:
            seen_ids.add(news['id'])
            unique_news.append(news)
    
    print(f"去重后: {len(unique_news)}条")
    
    # 限制数量用于后续处理
    return unique_news[:config['settings']['max_news_for_summary']]


def save_raw_news_file(news_list):
    """保存原始新闻到文件（备用）"""
    today = datetime.now().strftime('%Y-%m-%d')
    os.makedirs('data', exist_ok=True)
    
    filename = f'data/raw_news_{today}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    
    print(f"已保存JSON: {filename}")
    return filename


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 抓取新闻
    news = fetch_all_news()
    if news:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 保存到数据库
        inserted = save_raw_news(news, today)
        print(f"✓ 数据库新增: {inserted}条")
        
        # 同时保存JSON（备用）
        save_raw_news_file(news)
        
        print("\n新闻抓取完成，准备生成摘要...")
    else:
        print("\n未获取到新闻，请检查数据源配置")
