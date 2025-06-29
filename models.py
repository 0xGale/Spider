"""
数据模型定义模块
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class ZhihuHotItem(Base):
    """知乎热榜条目模型"""
    __tablename__ = 'zhihu_hot_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(50), unique=True, nullable=False, comment='问题ID')
    title = Column(String(500), nullable=False, comment='标题')
    excerpt = Column(Text, comment='摘要')
    url = Column(String(500), comment='链接')
    hot_index = Column(Float, comment='热度指数')
    answer_count = Column(Integer, default=0, comment='回答数')
    follower_count = Column(Integer, default=0, comment='关注数')
    created_time = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f"<ZhihuHotItem(id={self.id}, title='{self.title[:20]}...')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'title': self.title,
            'excerpt': self.excerpt,
            'url': self.url,
            'hot_index': self.hot_index,
            'answer_count': self.answer_count,
            'follower_count': self.follower_count,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }
