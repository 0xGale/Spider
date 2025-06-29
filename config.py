"""
配置模块 - 包含数据库配置、爬虫设置等
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'zhihu_hot'),
    'username': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# 爬虫配置
SPIDER_CONFIG = {
    # 使用知乎热榜页面而不是API
    'zhihu_hot_url': 'https://www.zhihu.com/hot',
    'zhihu_api_url': 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'Connection': 'keep-alive',
        # 'Upgrade-Insecure-Requests': '1',
        # 'Sec-Fetch-Dest': 'document',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-Site': 'none',
        # 'Sec-Fetch-User': '?1',
        # 'Cache-Control': 'max-age=0',
        'cookie': os.getenv('ZH_COOKIE', ''),  # 从环境变量获取Cookie
    },
    'api_headers': {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # 'Accept': 'application/json, text/plain, */*',
        # 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        # 'Connection': 'keep-alive',
        # 'Referer': 'https://www.zhihu.com/hot',
        # 'Sec-Fetch-Dest': 'empty',
        # 'Sec-Fetch-Mode': 'cors',
        # 'Sec-Fetch-Site': 'same-origin',
        # 'X-Requested-With': 'XMLHttpRequest',
        # 'Cookie': os.getenv('ZH_COOKIE', ''),  # 从环境变量获取Cookie
    },
    'timeout': 30,
    'retry_times': 3,
    'retry_delay': 5,
    'use_api': os.getenv('USE_API')  # 默认使用HTML解析，如果需要API则设为True
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'spider.log'
}
