#!/usr/bin/env python3
"""
调试脚本 - 查看知乎热榜页面的实际HTML结构
"""
import sys
import os
import requests
from bs4 import BeautifulSoup
import json
import re

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SPIDER_CONFIG

def debug_zhihu_page():
    """调试知乎热榜页面结构"""
    print("🔍 调试知乎热榜页面结构...")
    
    try:
        # 创建会话
        session = requests.Session()
        headers = SPIDER_CONFIG['headers'].copy()
        session.headers.update(headers)
        
        # 获取页面
        print("正在获取知乎热榜页面...")
        response = session.get(SPIDER_CONFIG['zhihu_hot_url'], timeout=30)
        response.raise_for_status()
        
        print(f"✅ 页面获取成功，状态码: {response.status_code}")
        print(f"页面大小: {len(response.text)} 字符")
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 保存页面内容到文件
        with open('zhihu_hot_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("✅ 页面内容已保存到 zhihu_hot_debug.html")
        
        # 查找可能的容器
        print("\n🔍 查找可能的热榜容器...")
        
        # 1. 查找所有div元素的class属性
        divs_with_class = soup.find_all('div', class_=True)
        class_names = set()
        for div in divs_with_class:
            classes = div.get('class', [])
            for cls in classes:
                if any(keyword in cls.lower() for keyword in ['hot', 'list', 'item', 'question']):
                    class_names.add(cls)
        
        if class_names:
            print("找到可能相关的CSS类名:")
            for cls in sorted(class_names):
                print(f"  - {cls}")
        
        # 2. 查找所有问题链接
        print("\n🔍 查找知乎问题链接...")
        links = soup.find_all('a', href=True)
        question_links = []
        
        for link in links:
            href = link.get('href', '')
            if '/question/' in href:
                title = link.get_text(strip=True)
                if title and len(title) > 5:  # 过滤短标题
                    question_links.append({
                        'href': href,
                        'title': title[:50] + '...' if len(title) > 50 else title
                    })
        
        print(f"找到 {len(question_links)} 个问题链接:")
        for i, link in enumerate(question_links[:10], 1):  # 只显示前10个
            print(f"  {i}. {link['title']}")
            print(f"     {link['href']}")
        
        if len(question_links) > 10:
            print(f"  ... 还有 {len(question_links) - 10} 个链接")
        
        # 3. 查找脚本标签中的数据
        print("\n🔍 查找JavaScript数据...")
        script_tags = soup.find_all('script')
        
        data_patterns = [
            'hotList', 'hot_list', 'topstory', 'initialState', 
            'INITIAL_STATE', 'window.__', 'data'
        ]
        
        found_data = False
        for i, script in enumerate(script_tags):
            if script.string:
                content = script.string[:200]  # 只看前200字符
                for pattern in data_patterns:
                    if pattern in script.string:
                        print(f"脚本 {i+1} 包含 '{pattern}': {content}...")
                        found_data = True
                        break
                if found_data:
                    break
        
        if not found_data:
            print("未在JavaScript中找到明显的数据模式")
        
        # 4. 查找特定的结构模式
        print("\n🔍 查找特定的HTML结构模式...")
        
        # 查找所有可能的列表结构
        list_elements = []
        
        # 查找ul/ol列表
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            if len(items) > 5:  # 可能是热榜列表
                list_elements.append(f"{'ul' if lst.name == 'ul' else 'ol'} with {len(items)} li items")
        
        # 查找section容器
        sections = soup.find_all('section')
        for section in sections:
            articles = section.find_all('article')
            if len(articles) > 5:
                list_elements.append(f"section with {len(articles)} article items")
        
        if list_elements:
            print("找到可能的列表结构:")
            for elem in list_elements:
                print(f"  - {elem}")
        else:
            print("未找到明显的列表结构")
        
        return len(question_links) > 0
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🛠️  知乎热榜页面结构调试")
    print("=" * 50)
    
    success = debug_zhihu_page()
    
    if success:
        print(f"\n✅ 调试完成！请检查生成的 zhihu_hot_debug.html 文件")
        print("可以据此优化爬虫的HTML解析逻辑")
    else:
        print(f"\n❌ 调试失败，请检查网络连接")

if __name__ == '__main__':
    main()
