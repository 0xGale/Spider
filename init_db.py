"""
数据库初始化脚本
"""
import sys
import logging
from utils import setup_logging
from database import db_manager

def init_database():
    """初始化数据库"""
    try:
        # 设置日志
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("开始初始化数据库...")
        
        # 创建表
        db_manager.create_tables()
        
        logger.info("数据库初始化完成！")
        return True
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
