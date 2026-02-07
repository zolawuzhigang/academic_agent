"""
适配器抽象基类模块

定义所有API适配器的统一接口规范
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from academic_agent.models import Paper, Author, Journal
from academic_agent.exceptions import APIRequestError, RateLimitExceededError


class BaseAcademicAdapter(ABC):
    """
    所有API适配器的抽象基类，定义统一接口
    
    该类定义了与学术API交互的标准接口，所有具体的适配器（如OpenAlex、
    Scopus等）都必须继承并实现这些抽象方法。
    
    Attributes:
        api_key: API密钥
        base_url: API基础URL
        rate_limit: 每秒请求数限制
        retry_times: 请求失败时的重试次数
        retry_delay: 重试间隔（秒）
        timeout: 请求超时时间（秒）
        logger: 日志记录器实例
    
    Example:
        >>> class OpenAlexAdapter(BaseAcademicAdapter):
        ...     def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        ...         # 实现获取论文逻辑
        ...         pass
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化适配器
        
        Args:
            config: 配置字典，包含以下键：
                - api_key: API密钥（可选）
                - base_url: API基础URL
                - rate_limit: 每秒请求数限制，默认10
                - retry_times: 重试次数，默认3
                - retry_delay: 重试延迟（秒），默认1
                - timeout: 请求超时时间（秒），默认30
        """
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "")
        self.rate_limit = config.get("rate_limit", 10)
        self.retry_times = config.get("retry_times", 3)
        self.retry_delay = config.get("retry_delay", 1)
        self.timeout = config.get("timeout", 30)
        self._last_request_time = 0
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _rate_limit_wait(self) -> None:
        """
        频率限制等待
        
        根据配置的rate_limit确保请求间隔符合限制。
        如果距离上次请求时间过短，则等待相应时间。
        """
        min_interval = 1.0 / self.rate_limit
        elapsed = time.time() - self._last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, method: str, url: str, **kwargs) -> Any:
        """
        执行HTTP请求（带重试机制）
        
        Args:
            method: HTTP方法（GET, POST等）
            url: 请求URL
            **kwargs: 传递给requests的请求参数
            
        Returns:
            响应对象
            
        Raises:
            APIRequestError: 请求失败时抛出
            RateLimitExceededError: 频率限制时抛出
        """
        import requests
        
        for attempt in range(self.retry_times):
            try:
                self._rate_limit_wait()
                response = requests.request(
                    method, 
                    url, 
                    timeout=self.timeout,
                    **kwargs
                )
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitExceededError(retry_after=retry_after)
                
                response.raise_for_status()
                return response
                
            except RateLimitExceededError:
                raise
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"请求失败（尝试 {attempt + 1}/{self.retry_times}）: {e}"
                )
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise APIRequestError(
                        message=f"请求失败: {str(e)}",
                        status_code=getattr(e.response, 'status_code', None)
                    )
    
    @abstractmethod
    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        根据论文ID获取单篇论文信息
        
        Args:
            paper_id: 论文ID
            
        Returns:
            Paper对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
            RateLimitExceededError: 频率限制时抛出
        """
        pass
    
    @abstractmethod
    def get_author_papers(
        self, 
        author_id: str, 
        start_year: Optional[int] = None,
        end_year: Optional[int] = None, 
        limit: int = 100
    ) -> List[Paper]:
        """
        根据作者ID获取其发表的论文列表
        
        Args:
            author_id: 作者ID
            start_year: 开始年份（可选）
            end_year: 结束年份（可选）
            limit: 返回数量限制，默认100
            
        Returns:
            Paper对象列表
            
        Raises:
            APIRequestError: API请求失败时抛出
            RateLimitExceededError: 频率限制时抛出
        """
        pass
    
    @abstractmethod
    def search_papers(
        self, 
        keyword: str, 
        start_year: Optional[int] = None,
        end_year: Optional[int] = None, 
        page: int = 1,
        page_size: int = 20
    ) -> List[Paper]:
        """
        根据关键词搜索论文
        
        Args:
            keyword: 搜索关键词
            start_year: 开始年份（可选）
            end_year: 结束年份（可选）
            page: 页码，默认1
            page_size: 每页数量，默认20
            
        Returns:
            Paper对象列表
            
        Raises:
            APIRequestError: API请求失败时抛出
            RateLimitExceededError: 频率限制时抛出
        """
        pass
    
    @abstractmethod
    def get_citation_relations(
        self, 
        paper_id: str, 
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        获取论文的引证关系
        
        Args:
            paper_id: 论文ID
            depth: 引证关系深度（1=直接引证，2=间接引证），默认1
            
        Returns:
            包含以下键的字典：
                - references: 该论文引用的论文列表
                - citations: 引用该论文的论文列表
                - metadata: 引证关系元数据
            
        Raises:
            APIRequestError: API请求失败时抛出
            RateLimitExceededError: 频率限制时抛出
        """
        pass
    
    @abstractmethod
    def get_author_info(self, author_id: str) -> Optional[Author]:
        """
        根据作者ID获取作者基础信息
        
        Args:
            author_id: 作者ID
            
        Returns:
            Author对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
            RateLimitExceededError: 频率限制时抛出
        """
        pass
    
    @abstractmethod
    def get_journal_info(self, journal_id: str) -> Optional[Journal]:
        """
        根据期刊ID获取期刊信息
        
        Args:
            journal_id: 期刊ID
            
        Returns:
            Journal对象，不存在则返回None
            
        Raises:
            APIRequestError: API请求失败时抛出
            RateLimitExceededError: 频率限制时抛出
        """
        pass
    
    @abstractmethod
    def parse_paper(self, raw_data: Dict[str, Any]) -> Paper:
        """
        将原始API响应数据解析为Paper对象
        
        Args:
            raw_data: API返回的原始数据
            
        Returns:
            解析后的Paper对象
            
        Raises:
            DataValidationError: 数据解析失败时抛出
        """
        pass
