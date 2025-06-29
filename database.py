"""
数据库操作模块 - 处理数据库连接、创建表、数据插入等操作
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import List, Optional
from models import Base, ZhihuHotItem
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._init_database()
    
    def _init_database(self):
        """初始化数据库连接"""
        try:
            # 构建数据库连接字符串
            db_url = (
                f"postgresql://{DATABASE_CONFIG['username']}:"
                f"{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:"
                f"{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
            )
            
            self.engine = create_engine(
                db_url,
                echo=False,  # 设置为True可以看到SQL语句
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600
            )
            
            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("数据库连接初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    def create_tables(self):
        """创建数据表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据表创建成功")
        except SQLAlchemyError as e:
            logger.error(f"创建数据表失败: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """获取数据库会话上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def save_hot_items(self, items: List[dict]) -> int:
        """
        保存热榜数据到数据库
        
        Args:
            items: 热榜数据列表
            
        Returns:
            成功保存的条目数量
        """
        if not items:
            return 0
            
        saved_count = 0
        
        with self.get_session() as session:
            for item_data in items:
                try:
                    # 检查是否已存在
                    existing_item = session.query(ZhihuHotItem).filter_by(
                        question_id=item_data.get('question_id')
                    ).first()
                    
                    if existing_item:
                        # 更新现有记录
                        for key, value in item_data.items():
                            if hasattr(existing_item, key) and key != 'id':
                                setattr(existing_item, key, value)
                        logger.debug(f"更新热榜条目: {item_data.get('title', '')[:20]}...")
                    else:
                        # 创建新记录
                        new_item = ZhihuHotItem(**item_data)
                        session.add(new_item)
                        logger.debug(f"添加新热榜条目: {item_data.get('title', '')[:20]}...")
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"保存热榜条目失败: {e}, 数据: {item_data}")
                    continue
        
        logger.info(f"成功保存 {saved_count} 条热榜数据")
        return saved_count
    
    def get_hot_items(self, limit: Optional[int] = None) -> List[ZhihuHotItem]:
        """
        获取热榜数据
        
        Args:
            limit: 限制返回数量
            
        Returns:
            热榜数据列表
        """
        with self.get_session() as session:
            query = session.query(ZhihuHotItem).order_by(ZhihuHotItem.created_time.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
    
    def clear_old_data(self, days: int = 7):
        """
        清理旧数据
        
        Args:
            days: 保留最近几天的数据
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_session() as session:
            deleted_count = session.query(ZhihuHotItem).filter(
                ZhihuHotItem.created_time < cutoff_date
            ).delete()
            
        logger.info(f"清理了 {deleted_count} 条旧数据")
        return deleted_count

# 创建全局数据库管理器实例
db_manager = DatabaseManager()
