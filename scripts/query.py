#!/usr/bin/env python3
"""
数据查询工具
方便查询历史新闻和统计数据
"""
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import query_news, get_stats, init_db

def print_help():
    print("""
Aviation Daily 数据查询工具

用法:
  python query.py stats              查看统计信息
  python query.py today              查看今天的新闻
  python query.py week               查看本周的新闻
  python query.py search <关键词>     搜索新闻
  python query.py export <日期>       导出某天数据为JSON
  
示例:
  python query.py stats
  python query.py today
  python query.py export 2026-03-31
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'stats':
        init_db()
        stats = get_stats(days=30)
        print("\n📊 数据统计")
        print("=" * 40)
        print(f"总新闻数: {stats['total_news']}")
        print(f"已摘要数: {stats['summarized']}")
        print(f"摘要完成率: {stats['summarized']/stats['total_news']*100:.1f}%" if stats['total_news'] > 0 else "N/A")
        
        print(f"\n📅 最近30天统计:")
        for date, fetched, summarized in stats['daily_stats'][:10]:
            print(f"  {date}: 抓取{fetched}条 / 摘要{summarized}条")
        
        print(f"\n📰 来源分布:")
        for source, count in stats['source_stats'][:10]:
            print(f"  {source}: {count}条")
    
    elif cmd == 'today':
        init_db()
        today = datetime.now().strftime('%Y-%m-%d')
        news = query_news(start_date=today, limit=20)
        print(f"\n📰 {today} 的新闻 ({len(news)}条)")
        print("=" * 60)
        for item in news:
            status = "✓" if item['is_summarized'] else "○"
            print(f"{status} [{item['source']}] {item['title'][:50]}...")
    
    elif cmd == 'week':
        init_db()
        end = datetime.now()
        start = end - timedelta(days=7)
        news = query_news(start_date=start.strftime('%Y-%m-%d'), 
                         end_date=end.strftime('%Y-%m-%d'), 
                         limit=50)
        print(f"\n📰 最近7天新闻 ({len(news)}条)")
        print("=" * 60)
        for item in news[:20]:
            status = "✓" if item['is_summarized'] else "○"
            pub = item['published_at'][:10] if item['published_at'] else 'unknown'
            print(f"{status} [{pub}] [{item['source']}] {item['title'][:40]}...")
    
    elif cmd == 'search' and len(sys.argv) >= 3:
        init_db()
        keyword = sys.argv[2]
        news = query_news(limit=100)
        filtered = [n for n in news if keyword.lower() in n['title'].lower() or 
                   (n['summary'] and keyword.lower() in n['summary'].lower())]
        print(f"\n🔍 搜索 '{keyword}' 找到 {len(filtered)} 条")
        print("=" * 60)
        for item in filtered[:20]:
            print(f"[{item['source']}] {item['title'][:50]}...")
            if item['summary']:
                print(f"  摘要: {item['summary'][:80]}...")
    
    elif cmd == 'export' and len(sys.argv) >= 3:
        init_db()
        date_str = sys.argv[2]
        data = export_to_json(date_str)
        filename = f'data/export_{date_str}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 已导出: {filename}")
        print(f"  共 {data['news_count']} 条新闻")
    
    else:
        print_help()

if __name__ == '__main__':
    main()
