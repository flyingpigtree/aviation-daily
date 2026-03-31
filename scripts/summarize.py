#!/usr/bin/env python3
"""
使用Kimi API生成中文摘要
"""
import json
import os
import sys
from datetime import datetime

# 尝试导入Kimi SDK，如果没有则使用requests
try:
    from openai import OpenAI
    USE_SDK = True
except ImportError:
    import requests
    USE_SDK = False


def get_kimi_client():
    """获取Kimi客户端"""
    api_key = os.getenv('KIMI_API_KEY')
    if not api_key:
        raise ValueError("请设置环境变量 KIMI_API_KEY")
    
    if USE_SDK:
        return OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
    else:
        return api_key


def summarize_with_kimi(news_list):
    """使用Kimi生成摘要"""
    client = get_kimi_client()

    # 构建新闻内容
    news_content = []
    for i, news in enumerate(news_list, 1):
        content = f"{i}. 标题: {news['title']}\n   来源: {news['source']}\n   链接: {news['link']}\n   摘要: {news['summary'][:500]}"
        news_content.append(content)

    news_text = "\n\n".join(news_content)

    prompt = f"""你是航空行业分析师。请从以下国际航空新闻中，选出最重要的8条。

【信息筛选标准 - 严格遵循】

✅ 优先选择以下类型的新闻：
1. 波音、空客等竞争对手的竞争动态（订单、交付、产品策略、市场份额变化）
2. 航空产业链供应链动态（发动机、航电、复合材料、零部件供应、产能变化）
3. 航空领域重大安全事件（事故、调查、适航指令、安全法规变化）
4. 国家竞争与地缘政治涉及航空领域的事件（制裁、贸易争端、航空外交、航权谈判）
5. 近期重点关注主题：
   - 伊朗战争/中东冲突对航空业的影响（航线改道、保险费用、油价、航空公司损失）
   - 疫情后航空供应链复苏情况（产能恢复、零部件短缺、交付延迟）
   - 俄罗斯国产客机进展、进口替代计划（SSJ-New、MC-21、PD-发动机等）

❌ 必须剔除的新闻：
1. 军机/军用直升机项目相关（战斗机、轰炸机、军用旋翼机、国防合同）
2. 中国商飞COMAC自身的动作、交付、订单等内部信息
3. 航空公司单纯的财务报告、人事变动、营销新闻
4. 通用航空/私人飞机的非产业影响新闻

【输出格式要求】

对每条新闻：
1. 标题翻译为简洁中文（15字以内）
2. 生成结构化摘要（100-200字），必须包含：
   - 核心事实：发生了什么（时间、地点、主体、事件）
   - 影响/意义：对航空产业链、市场竞争格局、或地缘政治的潜在影响
   - 如有涉及数据，保留关键数字
3. 保留原文链接

新闻内容：
{news_text}

请严格按照以下JSON格式输出，不要添加其他说明：
[
  {{
    "cn_title": "中文标题",
    "summary": "100-200字的结构化摘要，包含核心事实和影响分析",
    "url": "原文链接",
    "source": "来源名称"
  }}
]

只输出JSON数组，共8条。确保摘要信息完整、有深度，不仅仅是表面描述。"""

    try:
        if USE_SDK:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "你是一个专业的航空行业分析师，擅长将英文航空新闻翻译并摘要成简洁中文。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content
        else:
            # 使用requests直接调用API
            api_key = client
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "moonshot-v1-8k",
                "messages": [
                    {"role": "system", "content": "你是一个专业的航空行业分析师，擅长将英文航空新闻翻译并摘要成简洁中文。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            resp = requests.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            resp.raise_for_status()
            content = resp.json()['choices'][0]['message']['content']
        
        # 解析JSON
        # 清理可能的markdown代码块标记
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        return result
        
    except Exception as e:
        print(f"Kimi API调用失败: {str(e)}")
        print(f"响应内容: {content if 'content' in locals() else 'N/A'}")
        return None


def load_raw_news():
    """加载原始新闻"""
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'data/raw_news_{today}.json'

    if not os.path.exists(filename):
        raise FileNotFoundError(f"找不到当天新闻数据文件: {filename}")

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✓ 加载当天新闻: {filename}, 共 {len(data)} 条")
    return data


def save_summarized_news(news_list):
    """保存摘要后的新闻"""
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'data/summarized_news_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'generated_at': datetime.now().isoformat(),
            'news_count': len(news_list),
            'news': news_list
        }, f, ensure_ascii=False, indent=2)
    
    print(f"已保存摘要: {filename}")
    return filename


if __name__ == '__main__':
    print("开始生成中文摘要...")
    print("-" * 40)
    
    try:
        raw_news = load_raw_news()
        print(f"加载了 {len(raw_news)} 条原始新闻")
        
        if not raw_news:
            print("没有新闻数据，退出")
            sys.exit(1)
        
        summarized = summarize_with_kimi(raw_news)
        
        if summarized:
            print(f"生成了 {len(summarized)} 条摘要")
            save_summarized_news(summarized)
            print("\n摘要生成完成，准备构建网站...")
        else:
            print("摘要生成失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
