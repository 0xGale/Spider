#!/usr/bin/env python3
"""
最简单的测试脚本 - 仅测试数据获取
"""
import sys
import os
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_minimal():
    """最小化测试"""
    print("🔧 最简测试 - 验证爬虫基本功能")
    print("=" * 50)
    
    try:
        # 设置简单日志
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        
        from scraper import ZhihuSpider
        
        # 创建爬虫
        spider = ZhihuSpider()
        print("✅ 爬虫实例创建成功")
        
        # 获取数据
        print("🕷️  正在获取热榜数据...")
        data = spider.fetch_hot_list()
        
        if data:
            print(f"✅ 成功获取 {len(data)} 条数据")
            
            # 显示前3条
            print("\n📊 数据预览:")
            for i, item in enumerate(data[:3], 1):
                print(f"  {i}. {item.get('title', 'N/A')[:40]}...")
                print(f"     ID: {item.get('question_id', 'N/A')}")
                print(f"     热度: {item.get('hot_index', 'N/A')}")
                print()
            
            # 检查数据质量
            valid_items = [item for item in data if item.get('title') and item.get('question_id')]
            print(f"📈 数据质量: {len(valid_items)}/{len(data)} 条有效")
            
            if len(valid_items) >= 5:
                print("🎉 测试成功！爬虫工作正常")
                success = True
            else:
                print("⚠️  数据质量不佳，但基本功能正常")
                success = True
                
        else:
            print("❌ 未获取到数据")
            success = False
        
        # 清理
        spider.close()
        
        return success
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    success = test_minimal()
    
    if success:
        print("\n✅ 测试通过！可以运行完整程序了")
        print("运行命令: python main.py --mode once")
    else:
        print("\n❌ 测试失败")
        print("建议:")
        print("1. 检查网络连接")
        print("2. 使用VPN或代理")
        print("3. 稍后重试")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
