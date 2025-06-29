"""
数据处理模块 - 负责数据清洗、验证和转换
"""
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理器"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        清洗文本数据
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()（）【】""''—-]', '', text)
        
        return text
    
    @staticmethod
    def validate_item(item: Dict) -> bool:
        """
        验证数据项的有效性
        
        Args:
            item: 数据项字典
            
        Returns:
            是否有效
        """
        required_fields = ['question_id', 'title']
        
        # 检查必填字段
        for field in required_fields:
            if not item.get(field):
                logger.warning(f"缺少必填字段: {field}")
                return False
        
        # 验证question_id格式
        question_id = str(item.get('question_id', ''))
        if not question_id.isdigit():
            logger.warning(f"question_id格式错误: {question_id}")
            return False
        
        # 验证标题长度
        title = item.get('title', '')
        if len(title) > 500:
            logger.warning(f"标题过长: {len(title)} 字符")
            return False
        
        return True
    
    @staticmethod
    def process_hot_items(raw_items: List[Dict]) -> List[Dict]:
        """
        处理热榜数据
        
        Args:
            raw_items: 原始数据列表
            
        Returns:
            处理后的数据列表
        """
        if not raw_items:
            return []
        
        processed_items = []
        
        for item in raw_items:
            try:
                # 数据清洗
                processed_item = DataProcessor._clean_item(item)
                
                # 数据验证
                if not DataProcessor.validate_item(processed_item):
                    continue
                
                processed_items.append(processed_item)
                
            except Exception as e:
                logger.error(f"处理数据项失败: {e}")
                continue
        
        logger.info(f"数据处理完成: {len(processed_items)}/{len(raw_items)} 条有效数据")
        return processed_items
    
    @staticmethod
    def _clean_item(item: Dict) -> Dict:
        """
        清洗单个数据项
        
        Args:
            item: 原始数据项
            
        Returns:
            清洗后的数据项
        """
        cleaned_item = {}
        
        # 处理文本字段
        text_fields = ['title', 'excerpt']
        for field in text_fields:
            if field in item:
                cleaned_item[field] = DataProcessor.clean_text(str(item[field]))
        
        # 处理数字字段
        numeric_fields = ['hot_index', 'answer_count', 'follower_count']
        for field in numeric_fields:
            if field in item:
                try:
                    value = item[field]
                    if value is None:
                        cleaned_item[field] = 0
                    else:
                        cleaned_item[field] = float(value) if field == 'hot_index' else int(value)
                except (ValueError, TypeError):
                    cleaned_item[field] = 0
        
        # 处理其他字段
        other_fields = ['question_id', 'url']
        for field in other_fields:
            if field in item:
                cleaned_item[field] = str(item[field]).strip()
        
        return cleaned_item
    
    @staticmethod
    def deduplicate_items(items: List[Dict]) -> List[Dict]:
        """
        去重数据
        
        Args:
            items: 数据列表
            
        Returns:
            去重后的数据列表
        """
        if not items:
            return []
        
        seen_ids = set()
        unique_items = []
        
        for item in items:
            question_id = item.get('question_id')
            if question_id and question_id not in seen_ids:
                seen_ids.add(question_id)
                unique_items.append(item)
        
        if len(unique_items) != len(items):
            logger.info(f"去重完成: {len(items)} -> {len(unique_items)} 条数据")
        
        return unique_items
    
    @staticmethod
    def sort_by_hot_index(items: List[Dict], reverse: bool = True) -> List[Dict]:
        """
        按热度指数排序
        
        Args:
            items: 数据列表
            reverse: 是否降序排列
            
        Returns:
            排序后的数据列表
        """
        try:
            return sorted(items, key=lambda x: x.get('hot_index', 0), reverse=reverse)
        except Exception as e:
            logger.error(f"排序失败: {e}")
            return items
    
    @staticmethod
    def generate_summary(items: List[Dict]) -> Dict:
        """
        生成数据摘要
        
        Args:
            items: 数据列表
            
        Returns:
            数据摘要字典
        """
        if not items:
            return {
                'total_count': 0,
                'avg_hot_index': 0,
                'max_hot_index': 0,
                'min_hot_index': 0,
                'timestamp': datetime.now().isoformat()
            }
        
        hot_indices = [item.get('hot_index', 0) for item in items]
        
        return {
            'total_count': len(items),
            'avg_hot_index': sum(hot_indices) / len(hot_indices),
            'max_hot_index': max(hot_indices),
            'min_hot_index': min(hot_indices),
            'timestamp': datetime.now().isoformat()
        }
