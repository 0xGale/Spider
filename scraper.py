"""
爬虫模块 - 负责从知乎获取热榜数据
"""
import requests
import json
import time
import logging
import re
from typing import List, Dict, Optional
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from config import SPIDER_CONFIG

logger = logging.getLogger(__name__)

class ZhihuSpider:
    """知乎热榜爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self._setup_session()
    
    def _setup_session(self):
        """设置会话"""
        # 设置请求头
        headers = SPIDER_CONFIG['headers'].copy()
        headers['User-Agent'] = self.ua.random
        self.session.headers.update(headers)
        
        # 设置超时
        self.session.timeout = SPIDER_CONFIG['timeout']
        
        logger.info("爬虫会话初始化完成")
    
    def _make_request(self, url: str, max_retries: int = None) -> Optional[requests.Response]:
        """
        发送HTTP请求
        
        Args:
            url: 请求URL
            max_retries: 最大重试次数
            
        Returns:
            响应对象或None
        """
        if max_retries is None:
            max_retries = SPIDER_CONFIG['retry_times']
        
        headers = SPIDER_CONFIG['headers'].copy()
        
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"正在请求URL: {url} (尝试 {attempt + 1}/{max_retries + 1})")
                
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                
                logger.debug(f"请求成功: {url}")
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                
                if attempt < max_retries:
                    time.sleep(SPIDER_CONFIG['retry_delay'])
                else:
                    logger.error(f"请求最终失败: {url}")
                    return None
        
        return None
    

    
    def fetch_hot_list(self) -> List[Dict]:
        """
        获取知乎热榜数据
        
        Returns:
            热榜数据列表
        """
        logger.info("开始获取知乎热榜数据")
        
        # 使用HTML解析方法获取数据
        return self._fetch_from_html()
    
    def _fetch_from_html(self) -> List[Dict]:
        """
        从HTML页面解析数据
        
        Returns:
            热榜数据列表
        """
        logger.info("从HTML页面解析数据")
        
        try:
            response = self._make_request(SPIDER_CONFIG['zhihu_hot_url'])
            if not response:
                logger.error("获取知乎热榜页面失败")
                return []
            
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应内容长度: {len(response.text)} 字符")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            hot_items = []
            
            # 方法3: 如果前两种方法都失败，使用更通用的解析方法
            if not hot_items:
                logger.info("HTML结构解析失败，尝试通用解析方法")
                hot_items = self._parse_generic_structure(soup)
            
            # 方法4: 如果所有解析都失败，返回空列表
            if not hot_items:
                logger.warning("所有HTML解析方法都失败，返回空列表")
                hot_items = []
            
            logger.info(f"从HTML成功获取 {len(hot_items)} 条热榜数据")
            return hot_items
            
        except Exception as e:
            logger.error(f"HTML解析获取热榜数据异常: {e}")
            return []
    
    def _extract_from_data_object(self, data: dict) -> List[Dict]:
        """
        从数据对象中查找热榜数据
        
        Args:
            data: 数据对象
            
        Returns:
            热榜数据列表
        """
        hot_items = []
        
        try:
            # 优先查找topstory相关的热榜数据
            if 'topstory' in data:
                topstory = data['topstory']
                if isinstance(topstory, dict):
                    # 查找热榜数据
                    for key in ['hotList', 'data', 'list']:
                        if key in topstory and isinstance(topstory[key], list):
                            logger.debug(f"在topstory中找到热榜数据: {key}")
                            for item in topstory[key]:
                                hot_item = self._extract_html_item_info(item)
                                if hot_item:
                                    hot_items.append(hot_item)
                            if hot_items:
                                return hot_items
            
            # 如果没有找到topstory，查找其他可能的热榜数据键
            for key in ['hotList', 'hot']:
                if key in data and isinstance(data[key], list):
                    logger.debug(f"找到热榜数据: {key}")
                    for item in data[key]:
                        hot_item = self._extract_html_item_info(item)
                        if hot_item:
                            hot_items.append(hot_item)
                    if hot_items:
                        break
                        
        except Exception as e:
            logger.warning(f"查找数据异常: {e}")
        
        return hot_items
    
    def _parse_html_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """
        解析HTML结构获取热榜数据
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            热榜数据列表
        """
        hot_items = []
        
        try:
            # 首先尝试找到热榜容器
            hot_container_selectors = [
                'div[class*="HotList"]',  # 知乎热榜容器
                'div[class*="Topstory"]',  # 热榜容器
                'section[class*="Hot"]',  # 热榜区域
            ]
            
            hot_container = None
            for selector in hot_container_selectors:
                container = soup.select_one(selector)
                if container:
                    hot_container = container
                    logger.info(f"找到热榜容器: {selector}")
                    break
            
            # 如果没有找到热榜容器，使用整个页面
            if not hot_container:
                hot_container = soup
                logger.info("未找到热榜容器，使用整个页面")
            
            # 在热榜容器中查找热榜条目
            item_selectors = [
                'div[class*="HotItem"]',  # 知乎热榜条目
                'div[class*="Card"]',     # 卡片式条目
                'article',               # 文章条目
                'div[data-za-module="HotItem"]',  # 知乎特定属性
            ]
            
            for selector in item_selectors:
                items = hot_container.select(selector)
                if items:
                    logger.info(f"在热榜容器中找到条目: {selector}, 数量: {len(items)}")
                    
                    for i, item in enumerate(items):
                        try:
                            hot_item = self._extract_from_html_element(item, i + 1)
                            if hot_item:
                                hot_items.append(hot_item)
                        except Exception as e:
                            logger.warning(f"解析HTML元素失败: {e}")
                            continue
                    
                    if hot_items:
                        break
            
        except Exception as e:
            logger.error(f"解析HTML结构失败: {e}")
        
        return hot_items
    
    def _parse_generic_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """
        通用的HTML解析方法，当特定结构解析失败时使用
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            热榜数据列表
        """
        hot_items = []
        
        try:
            # 首先尝试在热榜相关区域查找
            hot_sections = soup.find_all(['div', 'section'], class_=re.compile(r'(?i)hot|topstory'))
            
            if not hot_sections:
                # 如果没有找到热榜区域，查找整个页面，但过滤掉明显的非热榜区域
                excluded_sections = soup.find_all(['div', 'section'], class_=re.compile(r'(?i)rumor|辟谣|footer|header|nav|sidebar'))
                for section in excluded_sections:
                    section.decompose()  # 移除这些区域
                hot_sections = [soup]
            
            seen_questions = set()
            
            for section in hot_sections:
                links = section.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    if '/question/' not in href:
                        continue
                    
                    # 提取问题ID
                    question_match = re.search(r'/question/(\d+)', href)
                    if not question_match:
                        continue
                    
                    question_id = question_match.group(1)
                    if question_id in seen_questions:
                        continue
                    
                    seen_questions.add(question_id)
                    
                    # 获取标题
                    title = link.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # 过滤明显不是热榜的标题（比如包含"辟谣"等关键词）
                    if any(keyword in title for keyword in ['辟谣', '谣言', '假消息']):
                        continue
                    
                    # 构建URL
                    url = f"https://www.zhihu.com{href}" if href.startswith('/') else href
                    
                    hot_item = {
                        'question_id': question_id,
                        'title': title,
                        'excerpt': '',
                        'url': url,
                        'hot_index': float(len(hot_items) + 1) * 10,
                        'answer_count': 0,
                        'follower_count': 0
                    }
                    
                    hot_items.append(hot_item)
                    
                    # 限制数量
                    if len(hot_items) >= 50:
                        break
                
                if len(hot_items) >= 50:
                    break
            
            logger.info(f"通用解析获取 {len(hot_items)} 条数据")
            
        except Exception as e:
            logger.error(f"通用解析失败: {e}")
        
        return hot_items
    
    def _extract_from_html_element(self, element, index: int) -> Optional[Dict]:
        """
        从HTML元素中提取热榜条目信息
        
        Args:
            element: HTML元素
            index: 排序索引
            
        Returns:
            处理后的数据字典
        """
        try:
            # 查找标题
            title = ""
            title_selectors = [
                'h2', 'h3', 'h4',
                '[class*="title"]',
                '[class*="Title"]',
                'a[href*="/question/"]'
            ]
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title:
                        break
            
            if not title:
                return None
            
            # 查找链接
            link_elem = element.find('a', href=True)
            url = ""
            question_id = ""
            
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    url = f"https://www.zhihu.com{href}"
                else:
                    url = href
                
                # 提取问题ID
                question_match = re.search(r'/question/(\d+)', href)
                if question_match:
                    question_id = question_match.group(1)
            
            if not question_id:
                return None
            
            # 提取摘要
            excerpt = ""
            excerpt_selectors = [
                'p', 'div[class*="excerpt"]',
                'div[class*="Excerpt"]',
                'div[class*="description"]'
            ]
            
            for selector in excerpt_selectors:
                excerpt_elem = element.select_one(selector)
                if excerpt_elem:
                    excerpt = excerpt_elem.get_text(strip=True)
                    if excerpt:
                        break
            
            # 提取数字信息（回答数、关注数等）
            numbers = re.findall(r'(\d+)', element.get_text())
            answer_count = 0
            follower_count = 0
            
            if numbers:
                # 简单的数字分配逻辑
                if len(numbers) >= 2:
                    answer_count = int(numbers[0])
                    follower_count = int(numbers[1])
                elif len(numbers) == 1:
                    answer_count = int(numbers[0])
            
            # 计算热度
            hot_index = float(index) * 100
            
            return {
                'question_id': question_id,
                'title': title,
                'excerpt': excerpt,
                'url': url,
                'hot_index': hot_index,
                'answer_count': answer_count,
                'follower_count': follower_count
            }
            
        except Exception as e:
            logger.error(f"提取HTML元素信息失败: {e}")
            return None
    

    
    def _extract_html_item_info(self, item: Dict) -> Optional[Dict]:
        """
        提取HTML热榜条目信息
        
        Args:
            item: HTML解析的原始数据项
            
        Returns:
            处理后的数据字典
        """
        try:
            # 适配不同的数据结构
            target = item.get('target', item)
            
            question_id = str(target.get('id', target.get('questionId', '')))
            title = target.get('title', target.get('titleArea', {}).get('text', '')).strip()
            excerpt = target.get('excerpt', target.get('excerptArea', {}).get('text', '')).strip()
            
            url = f"https://www.zhihu.com/question/{question_id}" if question_id else ''
            
            # 统计信息
            answer_count = target.get('answerCount', target.get('answer_count', 0))
            follower_count = target.get('followerCount', target.get('follower_count', 0))
            
            # 热度信息
            hot_index = target.get('hotIndex', target.get('hot_index', 0))
            if not hot_index:
                detail_text = target.get('metricsArea', {}).get('text', '')
                hot_index = self._extract_hot_index(detail_text)
            
            if not title or not question_id:
                return None
            
            return {
                'question_id': question_id,
                'title': title,
                'excerpt': excerpt,
                'url': url,
                'hot_index': float(hot_index) if hot_index else 0.0,
                'answer_count': int(answer_count) if answer_count else 0,
                'follower_count': int(follower_count) if follower_count else 0
            }
            
        except Exception as e:
            logger.error(f"提取HTML条目信息失败: {e}")
            return None
    
    def _extract_hot_index(self, detail_text: str) -> float:
        """
        从详情文本中提取热度指数
        
        Args:
            detail_text: 详情文本
            
        Returns:
            热度指数
        """
        try:
            if not detail_text:
                return 0.0
            
            # 移除非数字字符，提取数字
            import re
            numbers = re.findall(r'(\d+(?:\.\d+)?)', detail_text)
            
            if numbers:
                # 取最大的数字作为热度指数
                return float(max(numbers, key=float))
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"提取热度指数失败: {e}")
            return 0.0
    

    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
            logger.info("爬虫会话已关闭")
