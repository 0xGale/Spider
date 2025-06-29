"""
测试脚本 - 用于测试各个模块的功能
"""
import sys
import logging
from utils import setup_logging
from processor import DataProcessor
from scraper import ZhihuSpider

def test_processor():
    """测试数据处理模块"""
    print("测试数据处理模块...")
    
    # 模拟数据
    test_data = [
        {
            'question_id': '123456',
            'title': '这是一个测试标题   ',
            'excerpt': '<p>这是测试内容</p>',
            'hot_index': '100.5',
            'answer_count': '50',
            'follower_count': '200'
        },
        {
            'question_id': '123457',
            'title': '另一个测试标题',
            'excerpt': '正常内容',
            'hot_index': 85.2,
            'answer_count': 30,
            'follower_count': 150
        }
    ]
    
    processor = DataProcessor()
    
    # 测试数据处理
    processed = processor.process_hot_items(test_data)
    print(f"处理后数据条数: {len(processed)}")
    
    # 测试排序
    sorted_data = processor.sort_by_hot_index(processed)
    print("热度排序:", [item['hot_index'] for item in sorted_data])
    
    # 测试摘要
    summary = processor.generate_summary(processed)
    print("数据摘要:", summary)
    
    print("✅ 数据处理模块测试通过\n")

def test_scraper():
    """测试爬虫模块（不实际请求）"""
    print("测试爬虫模块...")
    
    spider = ZhihuSpider()
    
    # 测试数据提取
    test_item = {
        'target': {
            'id': 123456,
            'title': '测试问题标题',
            'excerpt': '这是一个测试问题的描述',
            'answer_count': 100,
            'follower_count': 500
        },
        'detail_text': '热度 1234 讨论'
    }
    
    extracted = spider._extract_item_info(test_item)
    print("提取的数据:", extracted)
    
    spider.close()
    print("✅ 爬虫模块测试通过\n")

def main():
    """主测试函数"""
    setup_logging()
    
    print("🧪 开始模块测试")
    print("=" * 40)
    
    try:
        test_processor()
        test_scraper()
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
