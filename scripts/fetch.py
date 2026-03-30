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

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


def get_domain(url):
    """从URL获取域名"""
    return urlparse(url).netloc.replace('www.', '')


def fetch_rss(source_id, source_config):
    """抓取RSS源"""
    if not source_config.get('enabled', True):
        return []

    try:
        feed = feedparser.parse(source_config['url'])
        items = []

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        for entry in feed.entries[:config['settings']['max_news_per_source'] * 2]:  # 多抓一些用于过滤
            # 提取日期
            published = entry.get('published', entry.get('updated', ''))

            # 尝试解析日期
            news_date = None
            try:
                # 尝试常见日期格式
                for date_field in ['published_parsed', 'updated_parsed', 'published', 'updated']:
                    if hasattr(entry, date_field):
                        date_val = getattr(entry, date_field)
                        if date_val:
                            if isinstance(date_val, tuple):
                                news_date = datetime(*date_val[:6]).date()
                            break
            except Exception:
                pass

            # 如果没有解析到日期或日期不是今天/昨天，跳过
            if news_date and news_date not in [today, yesterday]:
                continue

            # 生成唯一ID
            unique_str = f"{entry.title}{entry.link}"
            news_id = hashlib.md5(unique_str.encode()).hexdigest()[:12]

            items.append({
                'id': news_id,
                'title': entry.title,
                'link': entry.link,
                'summary': entry.get('summary', '')[:300],
                'published': published,
                'source': source_config['name'],
                'domain': get_domain(entry.link)
            })

            if len(items) >= config['settings']['max_news_per_source']:
                break

        print(f"✓ {source_config['name']}: {len(items)}条")
        return items

    except Exception as e:
        print(f"✗ {source_config['name']}: {str(e)}")
        return []


def fetch_all_news():
    """抓取所有源的新闻"""
    all_news = []
    
    print("开始抓取新闻...")
    print("-" * 40)
    
    for source_id, source_config in config['sources'].items():
        news = fetch_rss(source_id, source_config)
        all_news.extend(news)
    
    print("-" * 40)
    print(f"总计抓取: {len(all_news)}条")
    
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


def save_raw_news(news_list):
    """保存原始新闻"""
    today = datetime.now().strftime('%Y-%m-%d')
    os.makedirs('data', exist_ok=True)
    
    filename = f'data/raw_news_{today}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    
    print(f"已保存: {filename}")
    return filename


if __name__ == '__main__':
    news = fetch_all_news()
    if news:
        save_raw_news(news)
        print("\n新闻抓取完成，准备生成摘要...")
    else:
        print("\n未获取到新闻，请检查数据源配置")
