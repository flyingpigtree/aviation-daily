#!/usr/bin/env python3
"""
数据库管理模块
使用SQLite存储新闻数据，方便历史查询和积累
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path('data/aviation_daily.db')

def init_db():
    """初始化数据库"""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            cn_title TEXT,
            summary TEXT,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            published_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category TEXT,
            is_summarized BOOLEAN DEFAULT 0,
            UNIQUE(url)
        )
    ''')
    
    # 每日统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            total_fetched INTEGER DEFAULT 0,
            total_summarized INTEGER DEFAULT 0,
            categories TEXT,
            generated_at TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_published ON news(published_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON news(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON news(source)')
    
    conn.commit()
    conn.close()
    print("✓ 数据库初始化完成")


def save_raw_news(news_list, date_str):
    """保存原始新闻到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    for news in news_list:
        try:
            # 解析发布时间
            pub_time = news.get('published_datetime', '')
            if pub_time:
                try:
                    pub_dt = datetime.fromisoformat(pub_time.replace('Z', '+00:00').replace('+00:00', ''))
                except:
                    pub_dt = None
            else:
                pub_dt = None
            
            cursor.execute('''
                INSERT OR IGNORE INTO news 
                (id, title, url, source, published_at, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                news['id'],
                news['title'],
                news['link'],
                news['source'],
                pub_dt,
                datetime.now()
            ))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"保存失败: {news.get('title', 'unknown')[:30]}... - {e}")
    
    # 更新每日统计
    cursor.execute('''
        INSERT OR REPLACE INTO daily_stats (date, total_fetched, generated_at)
        VALUES (?, ?, ?)
    ''', (date_str, inserted, datetime.now()))
    
    conn.commit()
    conn.close()
    return inserted


def update_summaries(summarized_news, date_str):
    """更新AI生成的摘要"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updated = 0
    for news in summarized_news:
        try:
            cursor.execute('''
                UPDATE news 
                SET cn_title = ?, summary = ?, is_summarized = 1
                WHERE url = ?
            ''', (
                news['cn_title'],
                news['summary'],
                news['url']
            ))
            if cursor.rowcount > 0:
                updated += 1
        except Exception as e:
            print(f"更新失败: {news.get('cn_title', 'unknown')[:30]}... - {e}")
    
    # 更新统计
    cursor.execute('''
        UPDATE daily_stats 
        SET total_summarized = ?
        WHERE date = ?
    ''', (updated, date_str))
    
    conn.commit()
    conn.close()
    return updated


def query_news(start_date=None, end_date=None, category=None, source=None, limit=100):
    """查询新闻"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM news WHERE 1=1'
    params = []
    
    if start_date:
        query += ' AND published_at >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND published_at <= ?'
        params.append(end_date)
    if category:
        query += ' AND category = ?'
        params.append(category)
    if source:
        query += ' AND source = ?'
        params.append(source)
    
    query += ' ORDER BY published_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_stats(days=30):
    """获取统计信息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总新闻数
    cursor.execute('SELECT COUNT(*) FROM news')
    total_news = cursor.fetchone()[0]
    
    # 已摘要数
    cursor.execute('SELECT COUNT(*) FROM news WHERE is_summarized = 1')
    summarized = cursor.fetchone()[0]
    
    # 最近30天统计
    cursor.execute('''
        SELECT date, total_fetched, total_summarized 
        FROM daily_stats 
        ORDER BY date DESC LIMIT ?
    ''', (days,))
    daily = cursor.fetchall()
    
    # 来源统计
    cursor.execute('''
        SELECT source, COUNT(*) as count 
        FROM news 
        GROUP BY source 
        ORDER BY count DESC
    ''')
    sources = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_news': total_news,
        'summarized': summarized,
        'daily_stats': daily,
        'source_stats': sources
    }


def export_to_json(date_str):
    """导出某天的数据为JSON（用于生成网页）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT cn_title, summary, url, source, published_at
        FROM news
        WHERE date(published_at) = ? AND is_summarized = 1
        ORDER BY published_at DESC
    ''', (date_str,))
    
    rows = cursor.fetchall()
    conn.close()
    
    news_list = []
    for row in rows:
        news_list.append({
            'cn_title': row['cn_title'],
            'summary': row['summary'],
            'url': row['url'],
            'source': row['source']
        })
    
    return {
        'date': date_str,
        'generated_at': datetime.now().isoformat(),
        'news_count': len(news_list),
        'news': news_list
    }


if __name__ == '__main__':
    init_db()
    stats = get_stats()
    print(f"\n数据库统计:")
    print(f"- 总新闻数: {stats['total_news']}")
    print(f"- 已摘要: {stats['summarized']}")
    print(f"- 最近30天: {len(stats['daily_stats'])} 天有数据")
    print(f"\n来源分布:")
    for source, count in stats['source_stats'][:5]:
        print(f"  - {source}: {count}条")
