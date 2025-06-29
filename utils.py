"""
工具模块 - 包含通用的工具函数
"""
import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from config import LOG_CONFIG

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG['level']),
        format=LOG_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOG_CONFIG['file'], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def save_to_json(data: Any, filename: str):
    """
    保存数据到JSON文件
    
    Args:
        data: 要保存的数据
        filename: 文件名
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        logging.info(f"数据已保存到 {filename}")
    except Exception as e:
        logging.error(f"保存JSON文件失败: {e}")

def load_from_json(filename: str) -> Any:
    """
    从JSON文件加载数据
    
    Args:
        filename: 文件名
        
    Returns:
        加载的数据
    """
    try:
        if not os.path.exists(filename):
            return None
            
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"从 {filename} 加载数据成功")
        return data
    except Exception as e:
        logging.error(f"加载JSON文件失败: {e}")
        return None

def format_timestamp(timestamp: datetime = None) -> str:
    """
    格式化时间戳
    
    Args:
        timestamp: 时间戳，默认为当前时间
        
    Returns:
        格式化的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def create_backup_filename(base_name: str) -> str:
    """
    创建备份文件名
    
    Args:
        base_name: 基础文件名
        
    Returns:
        带时间戳的备份文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(base_name)
    return f"{name}_{timestamp}{ext}"

def ensure_directory(directory: str):
    """
    确保目录存在
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"创建目录: {directory}")

def get_file_size(filename: str) -> int:
    """
    获取文件大小
    
    Args:
        filename: 文件名
        
    Returns:
        文件大小（字节）
    """
    try:
        return os.path.getsize(filename)
    except OSError:
        return 0

def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """
    重试装饰器
    
    Args:
        func: 要重试的函数
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
        
    Returns:
        装饰后的函数
    """
    import time
    
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    logging.error(f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败: {e}")
                    raise
                logging.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}")
                time.sleep(delay)
    
    return wrapper

def validate_config(config: Dict) -> bool:
    """
    验证配置的有效性
    
    Args:
        config: 配置字典
        
    Returns:
        是否有效
    """
    required_keys = ['host', 'port', 'database', 'username', 'password']
    
    for key in required_keys:
        if key not in config or not config[key]:
            logging.error(f"配置缺少必要的键: {key}")
            return False
    
    return True

def print_banner():
    """打印程序横幅"""
    banner = """
    ╔══════════════════════════════════════╗
    ║          知乎热榜爬虫程序              ║
    ║         Zhihu Hot List Spider        ║
    ╚══════════════════════════════════════╝
    """
    print(banner)
