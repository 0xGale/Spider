"""
主程序入口 - 知乎热榜爬虫
"""
import logging
import argparse
import sys
from datetime import datetime, timedelta
from typing import Optional

from utils import setup_logging, print_banner, save_to_json, format_timestamp
from scraper import ZhihuSpider
from processor import DataProcessor
from database import db_manager

logger = logging.getLogger(__name__)

class ZhihuHotSpider:
    """知乎热榜爬虫主类"""
    
    def __init__(self):
        self.spider = None
        self.processor = DataProcessor()
        
    def setup(self):
        """初始化设置"""
        try:
            # 设置日志
            setup_logging()
            logger.info("程序启动")
            
            # 初始化爬虫
            self.spider = ZhihuSpider()
            
            # 创建数据库表
            db_manager.create_tables()
            
            logger.info("初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False
    
    def run_once(self, save_json: bool = False) -> bool:
        """
        执行一次爬取
        
        Args:
            save_json: 是否保存为JSON文件
            
        Returns:
            是否成功
        """
        try:
            logger.info("开始执行爬取任务")
            
            # 获取热榜数据
            raw_data = self.spider.fetch_hot_list()
            if not raw_data:
                logger.warning("未获取到热榜数据")
                return False
            
            # 数据处理
            processed_data = self.processor.process_hot_items(raw_data)
            if not processed_data:
                logger.warning("数据处理后无有效数据")
                return False
            
            # 去重和排序
            unique_data = self.processor.deduplicate_items(processed_data)
            # sorted_data = self.processor.sort_by_hot_index(unique_data)
            
            # 保存到数据库
            saved_count = db_manager.save_hot_items(unique_data)
            logger.info(f"成功保存 {saved_count} 条数据到数据库")
            
            # 可选：保存为JSON文件
            if save_json:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"zhihu_hot_{timestamp}.json"
                save_to_json(unique_data, json_filename)
            
            # 生成并显示摘要
            summary = self.processor.generate_summary(unique_data)
            self._print_summary(summary, unique_data[:5])  # 显示前5条
            
            logger.info("爬取任务执行完成")
            return True
            
        except Exception as e:
            logger.error(f"执行爬取任务失败: {e}")
            return False
    
    def run_scheduled(self, interval: int = 3600):
        """
        定时执行爬取
        
        Args:
            interval: 间隔时间（秒）
        """
        import time
        
        logger.info(f"开始定时爬取，间隔 {interval} 秒")
        
        try:
            while True:
                success = self.run_once()
                if success:
                    logger.info(f"下次执行时间: {format_timestamp(datetime.now().replace(second=0, microsecond=0).replace(minute=0) + timedelta(hours=1))}")
                else:
                    logger.warning("本次爬取失败")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("收到停止信号，程序退出")
        except Exception as e:
            logger.error(f"定时爬取异常: {e}")
    
    def cleanup_old_data(self, days: int = 7):
        """
        清理旧数据
        
        Args:
            days: 保留天数
        """
        try:
            deleted_count = db_manager.clear_old_data(days)
            logger.info(f"清理了 {deleted_count} 条超过 {days} 天的旧数据")
        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")
    
    def show_recent_data(self, limit: int = 20):
        """
        显示最近的数据
        
        Args:
            limit: 显示条数
        """
        try:
            items = db_manager.get_hot_items(limit)
            if not items:
                print("数据库中暂无数据")
                return
            
            print(f"\n最近 {len(items)} 条热榜数据:")
            print("-" * 80)
            
            for i, item in enumerate(items, 1):
                print(f"{i:2d}. {item.title}")
                print(f"    热度: {item.hot_index} | 回答: {item.answer_count} | 关注: {item.follower_count}")
                print(f"    时间: {format_timestamp(item.created_time)} | URL: {item.url}")
                print()
                
        except Exception as e:
            logger.error(f"显示数据失败: {e}")
    
    def _print_summary(self, summary: dict, top_items: list):
        """打印摘要信息"""
        print("\n" + "="*50)
        print("📊 爬取摘要")
        print("="*50)
        print(f"总条数: {summary['total_count']}")
        print(f"平均热度: {summary['avg_hot_index']:.2f}")
        print(f"最高热度: {summary['max_hot_index']:.2f}")
        print(f"最低热度: {summary['min_hot_index']:.2f}")
        print(f"爬取时间: {summary['timestamp']}")
        
        if top_items:
            print("\n🔥 热度排行榜 TOP 5:")
            print("-" * 50)
            for i, item in enumerate(top_items, 1):
                print(f"{i}. {item['title'][:30]}...")
                print(f"   热度: {item['hot_index']} | 回答: {item['answer_count']}")
        
        print("="*50)
    
    def cleanup(self):
        """清理资源"""
        if self.spider:
            self.spider.close()
        logger.info("资源清理完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='知乎热榜爬虫程序')
    parser.add_argument('--mode', choices=['once', 'schedule', 'show', 'cleanup'], 
                       default='once', help='运行模式')
    parser.add_argument('--interval', type=int, default=3600, 
                       help='定时模式的间隔时间（秒）')
    parser.add_argument('--json', action='store_true', 
                       help='是否保存为JSON文件')
    parser.add_argument('--limit', type=int, default=20, 
                       help='显示数据的条数')
    parser.add_argument('--days', type=int, default=7, 
                       help='清理超过指定天数的旧数据')
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 创建爬虫实例
    spider_app = ZhihuHotSpider()
    
    try:
        # 初始化
        if not spider_app.setup():
            sys.exit(1)
        
        # 根据模式执行
        if args.mode == 'once':
            success = spider_app.run_once(save_json=args.json)
            sys.exit(0 if success else 1)
            
        elif args.mode == 'schedule':
            spider_app.run_scheduled(interval=args.interval)
            
        elif args.mode == 'show':
            spider_app.show_recent_data(limit=args.limit)
            
        elif args.mode == 'cleanup':
            spider_app.cleanup_old_data(days=args.days)
            
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        sys.exit(1)
    finally:
        spider_app.cleanup()

if __name__ == '__main__':
    main()
