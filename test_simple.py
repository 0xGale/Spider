#!/usr/bin/env python3
"""
简单测试脚本 - 测试知乎热榜爬虫是否能正常工作
"""
import sys
import os
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_scraper_only():
    """仅测试爬虫功能，不涉及数据库"""
    print("🕷️  测试知乎热榜爬虫...")
    
    try:
        # 简单的日志设置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        from scraper import ZhihuSpider
        
        # 创建爬虫实例
        spider = ZhihuSpider()
        
        # 获取热榜数据
        print("正在获取热榜数据...")
        raw_data = spider.fetch_hot_list()
        
        if not raw_data:
            print("❌ 未能获取到热榜数据")
            return False
        
        print(f"✅ 成功获取 {len(raw_data)} 条原始数据")
        
        # 显示前5条数据
        print("\n📊 热榜前5条:")
        print("-" * 60)
        
        for i, item in enumerate(raw_data[:5], 1):
            print(f"{i}. {item.get('title', 'N/A')}")
            print(f"   问题ID: {item.get('question_id', 'N/A')}")
            print(f"   热度: {item.get('hot_index', 'N/A')}")
            print(f"   URL: {item.get('url', 'N/A')}")
            print()
        
        # 清理资源
        spider.close()
        
        print("✅ 爬虫测试成功完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_processing():
    """测试爬虫和数据处理"""
    print("🔄 测试数据处理...")
    
    try:
        from processor import DataProcessor
        from scraper import ZhihuSpider
        
        logging.basicConfig(level=logging.WARNING)  # 减少日志输出
        
        spider = ZhihuSpider()
        processor = DataProcessor()
        
        # 获取数据
        raw_data = spider.fetch_hot_list()
        if not raw_data:
            print("❌ 无法获取数据")
            return False
        
        # 处理数据
        processed_data = processor.process_hot_items(raw_data)
        if not processed_data:
            print("❌ 数据处理失败")
            return False
        
        print(f"✅ 成功处理 {len(processed_data)} 条数据")
        
        # 去重和排序
        unique_data = processor.deduplicate_items(processed_data)
        sorted_data = processor.sort_by_hot_index(unique_data)
        
        print(f"✅ 去重后剩余 {len(unique_data)} 条数据")
        
        # 生成摘要
        summary = processor.generate_summary(sorted_data)
        print(f"✅ 数据摘要: 平均热度 {summary['avg_hot_index']:.2f}")
        
        spider.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据处理测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 知乎热榜爬虫测试")
    print("=" * 40)
    
    # 先测试基本爬虫功能
    success1 = test_scraper_only()
    
    if success1:
        print("\n" + "="*40)
        # 再测试数据处理
        success2 = test_with_processing()
        
        if success2:
            print("\n🎉 所有测试通过！现在可以运行完整的爬虫程序了。")
            print("运行命令: python main.py --mode once")
        else:
            print("\n⚠️  爬虫工作正常，但数据处理有问题。")
    else:
        print("\n💡 如果遇到问题，请检查网络连接。")
        print("建议:")
        print("1. 检查网络连接是否正常")
        print("2. 检查是否能访问 https://www.zhihu.com/hot")
        print("3. 尝试使用代理或VPN")
    
    return 0 if success1 else 1

if __name__ == '__main__':
    sys.exit(main())
